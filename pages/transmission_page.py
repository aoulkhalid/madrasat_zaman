"""
pages/transmission_page.py — 📡 Transmission

Étape 1 (VIEW)   : l'image s'affiche, seul le Joueur 1 de l'équipe regarde l'écran.
Étape 2 (RELAY)  : l'écran masque l'image, les 4 joueurs se relaient l'info à l'oral.
Étape 3 (SELECT) : 4 images s'affichent, le Joueur 4 choisit la bonne, le/la
                    responsable valide le clic.
Étape 4 (BREAK)  : pause de 10 secondes avant le round suivant.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget, QGridLayout)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, TRANSMISSION_VIEW_DURATION, TRANSMISSION_RELAY_DURATION,
                     TRANSMISSION_SELECT_DURATION, TRANSMISSION_BREAK_DURATION,
                     TRANSMISSION_POINTS_CORRECT)


class _ImageChoiceButton(QPushButton):
    """Bouton affichant une grande image (emoji) — neutre / correct (vert) / faux (rouge)."""

    def __init__(self, emoji, parent=None):
        super().__init__(emoji, parent)
        self.setFixedSize(140, 140)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI Emoji", 48))
        self.reset_style()

    def _style(self, bg, border):
        return f"""
            QPushButton {{
                background-color: {bg};
                border: 3px solid {border};
                border-radius: 20px;
            }}
        """

    def reset_style(self):
        self.setStyleSheet(self._style("white", C['border']) + f"""
            QPushButton:hover {{ border: 3px solid {C['primary']}; }}
        """)

    def set_correct(self):
        self.setStyleSheet(self._style(C['success_bg'], C['success']))

    def set_wrong(self):
        self.setStyleSheet(self._style(C['error_bg'], C['error']))


class TransmissionPage(BasePage):

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
        hdr.set_center("📡 TRANSMISSION")

        self._team_banner = self._add_team_banner()

        self._timer = CircularTimer(duration=TRANSMISSION_VIEW_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        self._section_lbl = QLabel("Round 1 / 6")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Segoe UI", 11))
        self._section_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")
        self._root_layout.addWidget(self._section_lbl)

        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setSpacing(20)
        self._root_layout.addWidget(self._content, stretch=1)

    def _clear_content(self):
        """Point d'entrée public : vide entièrement _content_layout."""
        self._clear_layout(self._content_layout)

    def _clear_layout(self, layout):
        """Vide un layout RÉCURSIVEMENT : widgets directs ET sous-layouts
        (ex. la QGridLayout des 4 images de sélection)."""
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
        self._rounds = self.mw.tc.get_transmission_slice()
        self._idx = 0
        self.mw.tc.current_match._turn_index = 0
        self._update_scores(self._boxes)
        self._refresh_team_banner()
        self._load_round()

    def _load_round(self):
        if self._idx >= len(self._rounds):
            self.mw.show_page("menu")
            return

        self._round = self._rounds[self._idx]
        self._team  = self.mw.tc.current_team
        self._stage = "view"
        self._refresh_team_banner()
        self._update_scores(self._boxes)
        self._section_lbl.setText(
            f"Round {self._idx + 1} / {len(self._rounds)}  ·  Tour : {self._team.name}"
        )
        self._show_image()

    def _show_image(self):
        self._clear_content()
        self._stage = "view"

        warn = QLabel("👁️ Seul·e le Joueur 1 regarde l'écran — les autres se retournent !")
        warn.setAlignment(Qt.AlignCenter)
        warn.setWordWrap(True)
        warn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        warn.setStyleSheet(f"color: {C['error']}; background: transparent;")

        img = QLabel(self._round["correct"])
        img.setAlignment(Qt.AlignCenter)
        img.setFont(QFont("Segoe UI Emoji", 90))
        img.setStyleSheet("background: transparent;")

        hint = QLabel("Mémorisez cette image, elle va disparaître.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Segoe UI", 11))
        hint.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        self._content_layout.addWidget(warn)
        self._content_layout.addWidget(img)
        self._content_layout.addWidget(hint)

        self._timer.reset(TRANSMISSION_VIEW_DURATION)
        self._timer.start()

    def _start_relay(self):
        self._clear_content()
        self._stage = "relay"

        title = QLabel("📡 Transmission orale en cours...")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        chain = QLabel("Joueur 1  →  Joueur 2  →  Joueur 3  →  Joueur 4")
        chain.setAlignment(Qt.AlignCenter)
        chain.setFont(QFont("Segoe UI", 15, QFont.Bold))
        chain.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        hint = QLabel("Décrivez l'image à voix basse, de joueur en joueur — à l'abri des autres équipes.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setFont(QFont("Segoe UI", 11))
        hint.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        skip_btn = QPushButton("✅ L'équipe a terminé — passer à la sélection")
        skip_btn.setFixedHeight(50)
        skip_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        skip_btn.setCursor(Qt.PointingHandCursor)
        skip_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {C['success']}; color: white; border-radius: 14px; padding: 0 20px; }}
            QPushButton:hover {{ background-color: #219150; }}
        """)
        skip_btn.clicked.connect(self._start_selection)

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(chain)
        self._content_layout.addWidget(hint)
        self._content_layout.addWidget(skip_btn, alignment=Qt.AlignCenter)

        self._timer.reset(TRANSMISSION_RELAY_DURATION)
        self._timer.start()

    def _start_selection(self):
        self._timer.stop()
        self._clear_content()
        self._stage = "select"

        title = QLabel(f"🎯 Joueur 4 de {self._team.name}, quelle image avez-vous reçue ?")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        grid = QGridLayout()
        grid.setSpacing(20)
        self._choice_btns = []
        for i, emoji in enumerate(self._round["choices"]):
            btn = _ImageChoiceButton(emoji)
            btn.clicked.connect(lambda _c, idx=i: self._resolve(idx))
            self._choice_btns.append(btn)
            grid.addWidget(btn, i // 2, i % 2)

        self._content_layout.addWidget(title)
        self._content_layout.addLayout(grid)

        self._timer.reset(TRANSMISSION_SELECT_DURATION)
        self._timer.start()

    def _resolve(self, choice_idx):
        if self._stage != "select":
            return
        self._timer.stop()
        self._apply_feedback(choice_idx)

        correct = (choice_idx == self._round["answer"])
        self.mw.tc.answer("transmission", correct)
        self._update_scores(self._boxes)
        self.mw.tc.next_turn()

        # Laisse voir le résultat (vert/rouge) 1.6s, puis lance la pause de 10s
        self._stage = "result"
        QTimer.singleShot(1600, self._start_break)

    def _apply_feedback(self, chosen_idx):
        for i, btn in enumerate(self._choice_btns):
            btn.setEnabled(False)
            if i == self._round["answer"]:
                btn.set_correct()
            elif i == chosen_idx:
                btn.set_wrong()

    def _start_break(self):
        """Pause de 10 secondes entre la fin d'un round et le début du suivant."""
        self._clear_content()
        self._stage = "break"

        title = QLabel("⏸️  Pause avant le round suivant")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        hint = QLabel("Préparez-vous, le prochain relais arrive bientôt...")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Segoe UI", 12))
        hint.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(hint)

        self._timer.reset(TRANSMISSION_BREAK_DURATION)
        self._timer.start()

    def _on_timeout(self):
        if self._stage == "view":
            self._start_relay()
        elif self._stage == "relay":
            self._start_selection()
        elif self._stage == "select":
            self._resolve(-1)   # personne n'a choisi à temps
        elif self._stage == "break":
            self._next_round()

    def _next_round(self):
        self._idx += 1
        self._load_round()