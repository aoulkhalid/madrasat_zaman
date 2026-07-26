"""
pages/memory_page.py — 🧠 Memory Challenge (cartes plein écran)

3 manches jouées à la suite dans la même confrontation :
  Manche 1 : 10 cartes (5 paires) — aperçu 5s, puis 60s  — +10 pts / paire
  Manche 2 : 16 cartes (8 paires) — 90s  — +15 pts / paire
  Manche 3 : 20 cartes (10 paires) — 120s — +20 pts / paire
             + une erreur donne un bonus à l'équipe adverse

Les cartes calculent automatiquement leur taille pour occuper le maximum
d'espace écran disponible (largeur ET hauteur), quelle que soit la résolution.

IMPORTANT : une paire TROUVÉE (set_matched) reste affichée face visible
pour le reste de la manche — seule une paire FAUSSE se recache
(_hide_pair). Rien dans le code ne re-cache jamais une paire trouvée.

Les images des cartes sont chargées depuis assets/images/memory/ (voir
games/memory_data.py). Si un fichier est introuvable, un repli visuel (🖼️)
s'affiche automatiquement à la place — l'app ne plante jamais.
"""
import os
import random
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget, QGridLayout)
from PyQt5.QtCore    import Qt, QTimer, QSize
from PyQt5.QtGui     import QFont, QIcon, QPixmap

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, MEMORY_ROUNDS, MEMORY_BONUS_WRONG, MEMORY_ROUND_BREAK,
                     MEMORY_IMAGES_DIR)

CARD_MATCH_PAUSE = 650   # ms avant de vérifier la paire
CARD_HIDE_PAUSE  = 900   # ms avant de recacher une paire fausse

COLUMNS = {5: 5, 8: 4, 10: 5}   # colonnes de la grille selon le nombre de paires

CARD_MIN_SIZE = 100
CARD_MAX_SIZE = 280
CARD_SPACING  = 16

# Espace réservé en hauteur pour header + bandeau équipe + scoreboard/timer
# + label de manche + marges — ajusté au plus juste pour maximiser les cartes.
RESERVED_HEIGHT = 250
RESERVED_WIDTH  = 40


class _CardButton(QPushButton):
    """Une carte du Memory : cachée (numéro) / retournée (image) / trouvée (image, permanente)."""

    def __init__(self, size, number, parent=None):
        super().__init__(parent)
        self._size = size
        self._number = number
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(QSize(int(size * 0.72), int(size * 0.72)))
        self.value = None
        self.set_hidden()

    def _style(self, bg, border):
        return f"""
            QPushButton {{
                background-color: {bg};
                border: 3px solid {border};
                border-radius: 16px;
            }}
        """

    def set_hidden(self):
        """Dos de carte : affiche son numéro (1, 2, 3...) au lieu d'un symbole générique."""
        self.setIcon(QIcon())
        self.setText(str(self._number))
        self.setFont(QFont("Segoe UI", int(self._size * 0.38), QFont.Bold))
        self.setStyleSheet(self._style(C['primary'], C['primary_light']) + """
            QPushButton { color: white; }
        """)

    def _set_face(self, image_path, bg, border):
        pixmap = None
        if image_path and os.path.exists(image_path):
            candidate = QPixmap(image_path)
            if not candidate.isNull():
                pixmap = candidate

        if pixmap:
            self.setText("")
            self.setIcon(QIcon(pixmap))
        else:
            # Repli si le fichier est introuvable ou invalide : jamais de plantage
            self.setIcon(QIcon())
            self.setText("🖼️")
            self.setFont(QFont("Segoe UI Emoji", int(self._size * 0.4)))

        self.setStyleSheet(self._style(bg, border))

    def set_revealed(self, image_path):
        self._set_face(image_path, "white", C['border'])

    def set_matched(self, image_path):
        """Paire trouvée — reste affichée ainsi jusqu'à la fin de la manche."""
        self._set_face(image_path, C['success_bg'], C['success'])


class MemoryPage(BasePage):

    def _build_page(self):
        layout = self._root_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QWidget(self)
        container.setStyleSheet(f"background-color: {C['bg']};")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)
        layout.addWidget(container)

        hdr = self._add_header(show_back=True)
        hdr.set_center("🧠 MEMORY CHALLENGE")

        self._team_banner = self._add_team_banner()

        self._timer = CircularTimer(duration=60, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        self._section_lbl = QLabel("Manche 1 / 3")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._section_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")
        self._root_layout.addWidget(self._section_lbl)

        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setContentsMargins(10, 4, 10, 8)
        self._content_layout.setSpacing(8)
        self._root_layout.addWidget(self._content, stretch=1)

    def _clear_content(self):
        self._clear_layout(self._content_layout)

    def _clear_layout(self, layout):
        """Vide un layout récursivement (widgets ET sous-layouts comme la grille de cartes)."""
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout:
                    self._clear_layout(child_layout)

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._match = self.mw.tc.current_match
        self._round_idx = 0
        self._cumulative = {self._match.team1.key: 0, self._match.team2.key: 0}
        self._update_scores(self._boxes)
        self._start_round()

    def _round_label_text(self):
        pairs = self._round_cfg["pairs"]
        return (f"Manche {self._round_idx + 1} / 3  —  {pairs} paires  —  "
                f"{self._round_cfg['points_per_pair']} pts/paire")

    def _start_round(self):
        self._round_cfg = MEMORY_ROUNDS[self._round_idx]
        pairs = self._round_cfg["pairs"]
        filenames = self.mw.tc.get_memory_pool(self._round_idx, pairs)
        paths = [os.path.join(MEMORY_IMAGES_DIR, fn) for fn in filenames]

        values = paths * 2
        random.shuffle(values)

        self._cards = [{"value": v, "revealed": False, "matched": False} for v in values]
        self._selected = []
        self._busy = False
        self._preview_mode = False
        self._round_points = {self._match.team1.key: 0, self._match.team2.key: 0}
        self._pairs_found  = {self._match.team1.key: 0, self._match.team2.key: 0}

        self._match._turn_index = 0
        self._render_board()

        preview = self._round_cfg.get("preview_duration", 0)
        if preview > 0:
            self._show_preview(preview)
        else:
            self._section_lbl.setText(self._round_label_text())
            self._timer.reset(self._round_cfg["duration"])
            self._timer.start()

    def _compute_card_size(self, cols, rows):
        """Calcule la taille des cartes pour occuper le maximum d'espace écran
        disponible (largeur ET hauteur), quelle que soit la résolution."""
        avail_w = max(self.width() - RESERVED_WIDTH, 500)
        avail_h = max(self.height() - RESERVED_HEIGHT, 300)

        size_w = (avail_w - CARD_SPACING * (cols - 1)) // cols
        size_h = (avail_h - CARD_SPACING * (rows - 1)) // rows

        size = min(size_w, size_h)
        return max(CARD_MIN_SIZE, min(size, CARD_MAX_SIZE))

    def _render_board(self):
        self._clear_content()
        self._refresh_team_banner()
        self._update_scores(self._boxes)

        pairs = self._round_cfg["pairs"]
        cols  = COLUMNS[pairs]
        total = len(self._cards)
        rows  = -(-total // cols)  # division entière arrondie au supérieur

        size = self._compute_card_size(cols, rows)

        grid = QGridLayout()
        grid.setSpacing(CARD_SPACING)
        self._card_btns = []
        for i, card in enumerate(self._cards):
            btn = _CardButton(size, number=i + 1)
            btn.clicked.connect(lambda _c, idx=i: self._on_card_click(idx))
            self._card_btns.append(btn)
            grid.addWidget(btn, i // cols, i % cols)

        self._content_layout.addLayout(grid)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Recalcule la taille des cartes si l'écran change de taille en plein jeu
        if hasattr(self, "_cards") and hasattr(self, "_card_btns") and self._card_btns:
            pairs = self._round_cfg["pairs"]
            cols  = COLUMNS[pairs]
            rows  = -(-len(self._cards) // cols)
            new_size = self._compute_card_size(cols, rows)
            for btn in self._card_btns:
                if btn.width() != new_size:
                    btn.setFixedSize(new_size, new_size)
                    btn._size = new_size
                    btn.setIconSize(QSize(int(new_size * 0.72), int(new_size * 0.72)))

    # ── Phase d'aperçu (Manche 1 uniquement par défaut) ─────────────────────
    def _show_preview(self, seconds):
        self._busy = True
        self._preview_mode = True
        for i, card in enumerate(self._cards):
            self._card_btns[i].set_revealed(card["value"])
        self._section_lbl.setText(f"👀 Mémorisez les cartes ! ({seconds}s)")
        self._timer.reset(seconds)
        self._timer.start()

    def _end_preview(self):
        self._preview_mode = False
        for i, card in enumerate(self._cards):
            card["revealed"] = False
            self._card_btns[i].set_hidden()
        self._busy = False
        self._section_lbl.setText(self._round_label_text())
        self._timer.reset(self._round_cfg["duration"])
        self._timer.start()

    def _on_card_click(self, idx):
        if self._busy:
            return
        card = self._cards[idx]
        if card["matched"] or card["revealed"]:
            return
        if len(self._selected) == 2:
            return

        card["revealed"] = True
        self._card_btns[idx].set_revealed(card["value"])
        self._selected.append(idx)

        if len(self._selected) == 2:
            self._busy = True
            QTimer.singleShot(CARD_MATCH_PAUSE, self._check_match)

    def _check_match(self):
        i1, i2 = self._selected
        c1, c2 = self._cards[i1], self._cards[i2]
        team = self.mw.tc.current_team

        if c1["value"] == c2["value"]:
            # ✅ Paire trouvée : marquée matched=True, affichage permanent via
            # set_matched(). Rien ne la recachera plus tard.
            c1["matched"] = c2["matched"] = True
            self._card_btns[i1].set_matched(c1["value"])
            self._card_btns[i2].set_matched(c2["value"])

            pts = self._round_cfg["points_per_pair"]
            self.mw.tc.award_points_to(team, "memory", pts)
            self._cumulative[team.key]   += pts
            self._round_points[team.key] += pts
            self._pairs_found[team.key]  += 1
            self._update_scores(self._boxes)

            self._selected = []
            self._busy = False

            if all(c["matched"] for c in self._cards):
                self._end_round()
        else:
            # ❌ Paire fausse : seules CES deux cartes se recachent (_hide_pair)
            if self._round_cfg.get("bonus_on_wrong"):
                opponent = (self._match.team2 if team.key == self._match.team1.key
                            else self._match.team1)
                self.mw.tc.award_points_to(opponent, "memory", MEMORY_BONUS_WRONG)
                self._cumulative[opponent.key]   += MEMORY_BONUS_WRONG
                self._round_points[opponent.key] += MEMORY_BONUS_WRONG
                self._update_scores(self._boxes)

            QTimer.singleShot(CARD_HIDE_PAUSE, lambda: self._hide_pair(i1, i2))

    def _hide_pair(self, i1, i2):
        """Ne recache QUE les deux cartes fausses passées en paramètre —
        jamais une carte déjà 'matched'."""
        for i in (i1, i2):
            if self._cards[i]["matched"]:
                continue
            self._cards[i]["revealed"] = False
            self._card_btns[i].set_hidden()
        self._selected = []
        self._busy = False
        self.mw.tc.next_turn()
        self._refresh_team_banner()

    def _on_timeout(self):
        if self._preview_mode:
            self._end_preview()
        else:
            self._end_round(timed_out=True)

    def _end_round(self, timed_out=False):
        self._timer.stop()
        self._busy = True
        self._clear_content()

        team1, team2 = self._match.team1, self._match.team2
        title = QLabel("⏱️ Temps écoulé !" if timed_out else "🎉 Toutes les paires trouvées !")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        summary = QLabel(
            f"{team1.name} : {self._pairs_found[team1.key]} paires (+{self._round_points[team1.key]} pts)\n"
            f"{team2.name} : {self._pairs_found[team2.key]} paires (+{self._round_points[team2.key]} pts)"
        )
        summary.setAlignment(Qt.AlignCenter)
        summary.setFont(QFont("Segoe UI", 14, QFont.Bold))
        summary.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(summary)

        QTimer.singleShot(MEMORY_ROUND_BREAK, self._next_round)

    def _next_round(self):
        self._round_idx += 1
        if self._round_idx >= len(MEMORY_ROUNDS):
            self._finish_game()
        else:
            self._start_round()

    def _finish_game(self):
        self._clear_content()
        team1, team2 = self._match.team1, self._match.team2
        c1, c2 = self._cumulative[team1.key], self._cumulative[team2.key]

        if c1 > c2:
            msg_text = f"🏆 {team1.name} remporte le Memory Challenge ! ({c1} vs {c2} pts)"
        elif c2 > c1:
            msg_text = f"🏆 {team2.name} remporte le Memory Challenge ! ({c2} vs {c1} pts)"
        else:
            msg_text = f"🤝 Égalité parfaite ! ({c1} pts chacune)"

        msg = QLabel(msg_text)
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setFont(QFont("Segoe UI", 19, QFont.Bold))
        msg.setStyleSheet(f"color: {C['success']}; background: transparent;")
        self._content_layout.addWidget(msg)

        QTimer.singleShot(3200, lambda: self.mw.show_page("menu"))