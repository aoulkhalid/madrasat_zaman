"""
pages/result_page.py — Résultats du match + état du tournoi
Même style moderne : fond image, tout transparent, noms bleus, glassmorphism
"""
import re, random
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QFrame, QWidget, QGraphicsDropShadowEffect,
                              QSizePolicy)
from PyQt5.QtCore    import Qt, QTimer, QRect
from PyQt5.QtGui     import (QFont, QColor, QPainter, QPen, QBrush,
                              QLinearGradient, QPainterPath, QPixmap,
                              QRadialGradient)
from pages.base_page import BasePage
from config import C, TEAMS
import os

BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background.png")

ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"
BLUE_NAME     = "#4f8ef7"
TEXT_MUTED    = "rgba(255,255,255,180)"
SUCCESS_COLOR = "#22d3a5"
_TRANSPARENT  = "background: transparent; border: none; background-color: transparent;"


def _make_transparent(widget):
    widget.setStyleSheet(_TRANSPARENT)
    widget.setAttribute(Qt.WA_TranslucentBackground, True)
    for child in widget.findChildren(QWidget):
        if isinstance(child, QLabel):
            old   = child.styleSheet()
            clean = re.sub(r'background(-color)?\s*:[^;]+;?', '', old)
            child.setStyleSheet(clean + " background: transparent;")
        else:
            child.setStyleSheet(_TRANSPARENT)
            child.setAttribute(Qt.WA_TranslucentBackground, True)

def _force_labels_blue(widget):
    for child in widget.findChildren(QLabel):
        child.setStyleSheet(
            child.styleSheet()
            + f" color: {BLUE_NAME}; font-weight: bold; background: transparent;"
        )


# ── Fond identique aux autres pages ───────────────────────────────────────────
class _Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = QPixmap(BG_PATH)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        if not self._bg_pixmap.isNull():
            p.drawPixmap(0, 0,
                self._bg_pixmap.scaled(w, h,
                    Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#dde6ed"))
            grad.setColorAt(1.0, QColor("#d6e3ec"))
            p.fillRect(self.rect(), QBrush(grad))
        p.fillRect(self.rect(), QColor(0, 0, 0, 30))
        lg = QLinearGradient(0, 0, w, 0)
        lg.setColorAt(0.0,  QColor(79, 142, 247, 0))
        lg.setColorAt(0.35, QColor(79, 142, 247, 160))
        lg.setColorAt(0.65, QColor(168, 85, 247, 160))
        lg.setColorAt(1.0,  QColor(168, 85, 247, 0))
        p.setPen(QPen(QBrush(lg), 2))
        p.drawLine(0, 2, w, 2)


# ── Carte glassmorphism (identique quiz_page) ──────────────────────────────────
class _GlassCard(QFrame):
    def __init__(self, radius=22, alpha=60, parent=None):
        super().__init__(parent)
        self._radius = radius
        self._alpha  = alpha

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), self._radius, self._radius)
        p.fillPath(path, QBrush(QColor(255, 255, 255, self._alpha)))
        border_grad = QLinearGradient(0, 0, r.width(), 0)
        border_grad.setColorAt(0.0,  QColor(79, 142, 247, 0))
        border_grad.setColorAt(0.25, QColor(79, 142, 247, 120))
        border_grad.setColorAt(0.75, QColor(168, 85, 247, 120))
        border_grad.setColorAt(1.0,  QColor(168, 85, 247, 0))
        p.setPen(QPen(QBrush(border_grad), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(r.adjusted(1, 1, -1, -1), self._radius, self._radius)


# ── Bouton action premium ──────────────────────────────────────────────────────
class _ActionButton(QPushButton):
    def __init__(self, label, icon, color, bg_color):
        super().__init__()
        self._label    = label
        self._icon     = icon
        self._color    = QColor(color)
        self._bg_color = QColor(bg_color)
        self.setFixedHeight(52)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        alpha = 255 if (self.underMouse() and self.isEnabled()) else 210
        if not self.isEnabled(): alpha = 80
        fill = QColor(self._bg_color); fill.setAlpha(alpha)
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), 14, 14)
        p.fillPath(path, QBrush(fill))
        bc = QColor(self._color)
        if not self.isEnabled(): bc.setAlpha(80)
        p.setPen(QPen(bc, 2)); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width()-2, r.height()-2, 14, 14)
        tc = QColor("#ffffff") if self.isEnabled() else QColor(180,180,180,100)
        p.setPen(QPen(tc))
        p.setFont(QFont("Segoe UI", 13, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{self._icon}  {self._label}")

    def enterEvent(self, e): super().enterEvent(e); self.update()
    def leaveEvent(self, e): super().leaveEvent(e); self.update()


# ── Page résultats ─────────────────────────────────────────────────────────────
class ResultPage(BasePage):

    def _build_page(self):
        layout = self._root_layout
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Fond
        self._bg = _Background(self)
        self._bg.setGeometry(self.rect())
        self._bg.lower()

        container = QWidget(self)
        container.setAttribute(Qt.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")
        layout.addWidget(container)

        # Header
        hdr = self._add_header(show_back=False)
        hdr.set_center("")
        _make_transparent(hdr)
        _force_labels_blue(hdr)

        # Zone centrale scrollable
        center = QVBoxLayout()
        center.setSpacing(14)
        center.setContentsMargins(36, 10, 36, 10)

        # ── Confettis ─────────────────────────────────────────────
        self._confetti_lbl = QLabel("🎊 🎉 🏆 🎉 🎊")
        self._confetti_lbl.setAlignment(Qt.AlignCenter)
        self._confetti_lbl.setFont(QFont("Segoe UI Emoji", 26))
        self._confetti_lbl.setStyleSheet("background: transparent; letter-spacing: 6px;")
        center.addWidget(self._confetti_lbl)

        # ── Titre ─────────────────────────────────────────────────
        self._title_lbl = QLabel("FÉLICITATIONS !")
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self._title_lbl.setStyleSheet(
            f"color: {ACCENT_BLUE}; background: transparent; letter-spacing: 2px;"
        )
        center.addWidget(self._title_lbl)

        # ── Gagnant ───────────────────────────────────────────────
        self._winner_lbl = QLabel("")
        self._winner_lbl.setAlignment(Qt.AlignCenter)
        self._winner_lbl.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self._winner_lbl.setStyleSheet("background: transparent;")
        center.addWidget(self._winner_lbl)

        # ── Scorecard (GlassCard) ─────────────────────────────────
        score_card = _GlassCard(radius=22, alpha=60)
        score_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        score_card.setFixedHeight(380)
        score_card_layout = QHBoxLayout(score_card)
        score_card_layout.setContentsMargins(30, 16, 30, 16)
        score_card_layout.setAlignment(Qt.AlignCenter)
        score_card_layout.setSpacing(50)
        self._scores_row = score_card_layout
        center.addWidget(score_card)

        # ── Bracket ───────────────────────────────────────────────
        bracket_title = QLabel("⬡  ÉTAT DU TOURNOI")
        bracket_title.setAlignment(Qt.AlignCenter)
        bracket_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        bracket_title.setStyleSheet(
            f"color: {ACCENT_BLUE}; background: transparent; letter-spacing: 2px;"
        )
        center.addWidget(bracket_title)

        self._bracket_frame = _GlassCard(radius=18, alpha=50)
        self._bracket_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._bracket_frame.setFixedHeight(120)
        b_layout = QHBoxLayout(self._bracket_frame)
        b_layout.setAlignment(Qt.AlignCenter)
        b_layout.setSpacing(20)
        center.addWidget(self._bracket_frame)

        self._root_layout.addLayout(center)
        self._root_layout.addStretch()

        # ── Boutons ───────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(36, 4, 36, 12)
        btn_row.setSpacing(14)

        self._next_btn = _ActionButton(
            "MATCH SUIVANT", "▶", color=ACCENT_BLUE, bg_color=ACCENT_BLUE)
        self._menu_btn = _ActionButton(
            "MENU", "↩", color="#6b7280", bg_color="#6b7280")
        self._restart_btn = _ActionButton(
            "NOUVEAU TOURNOI", "🔄", color=SUCCESS_COLOR, bg_color=SUCCESS_COLOR)

        self._next_btn.clicked.connect(self._go_next)
        self._menu_btn.clicked.connect(lambda: self.mw.show_page("menu"))
        self._restart_btn.clicked.connect(self._restart)

        btn_row.addWidget(self._next_btn)
        btn_row.addWidget(self._menu_btn)
        btn_row.addWidget(self._restart_btn)
        self._root_layout.addLayout(btn_row)

        # Footer
        footer = QLabel("⬡  CS Club — Madrasat Zaman v3")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            f"color: {ACCENT_BLUE}; font-size: 11px;"
            f" background: transparent; letter-spacing: 1px;"
        )
        footer.setFixedHeight(22)
        self._root_layout.addWidget(footer)

        self._tournament_over = False

    # ── Logique ───────────────────────────────────────────────────
    def on_show(self, tournament_over=False, **kwargs):
        self._tournament_over = tournament_over
        tourn = self.mw.tc.tournament

        finished_idx = tourn.current_match_idx - 1
        if tournament_over:
            finished_idx = 2
        if finished_idx < 0:
            finished_idx = 0

        finished_match = tourn.matches[finished_idx]

        if tournament_over:
            champ = tourn.champion
            self._title_lbl.setText("🏆 CHAMPION DU TOURNOI !")
            self._winner_lbl.setText(f"{champ.emoji}  {champ.name} remporte la victoire !")
            self._winner_lbl.setStyleSheet(f"color: {champ.color}; background: transparent;")
            self._next_btn.setVisible(False)
        else:
            winner = finished_match.winner
            self._title_lbl.setText(finished_match.label)
            self._winner_lbl.setText(f"{winner.emoji}  {winner.name} gagne !")
            self._winner_lbl.setStyleSheet(
                f"color: {winner.color}; background: transparent;")
            self._next_btn.setVisible(True)

        self._clear_layout(self._scores_row)
        if finished_match:
            self._add_score_box(finished_match.team1, finished_match.winner)
            vs = QLabel("VS")
            vs.setFont(QFont("Segoe UI", 34, QFont.Bold))
            vs.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")
            self._scores_row.addWidget(vs)
            self._add_score_box(finished_match.team2, finished_match.winner)

        self._update_bracket()
        self._animate_confetti()

    def _add_score_box(self, team, winner):
        t = TEAMS[team.key]
        is_winner = winner and winner.key == team.key

        box = _GlassCard(radius=18, alpha=80 if is_winner else 50)
        box.setFixedSize(340, 300)

        if is_winner:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(28)
            shadow.setOffset(0, 6)
            c = QColor(t["color"]); c.setAlpha(120)
            shadow.setColor(c)
            box.setGraphicsEffect(shadow)

        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)

        if is_winner:
            crown = QLabel("🏆")
            crown.setAlignment(Qt.AlignCenter)
            crown.setStyleSheet("font-size: 18px; background: transparent;")
            layout.addWidget(crown)

        name = QLabel(f"{t['emoji']}  {t['name']}")
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 22, QFont.Bold))
        name.setStyleSheet("color: #6b7280; background: transparent;")

        score = QLabel(str(team.score))
        score.setAlignment(Qt.AlignCenter)
        score.setFont(QFont("Segoe UI", 110, QFont.Bold))
        score.setStyleSheet(f"color: {t['color']}; background: transparent;")

        pts = QLabel("pts")
        pts.setAlignment(Qt.AlignCenter)
        pts.setStyleSheet("color: #6b7280; background: transparent; font-size: 14px;")

        layout.addWidget(name)
        layout.addWidget(score)
        layout.addWidget(pts)

        self._scores_row.addWidget(box)

    def _update_bracket(self):
        self._clear_layout(self._bracket_frame.layout())
        tourn = self.mw.tc.tournament
        for match in tourn.matches:
            if match is None:
                card = self._bracket_card("Finale", "? vs ?", None)
            else:
                teams = f"{match.team1.name} vs {match.team2.name}"
                card = self._bracket_card(match.label, teams, match.winner)
            self._bracket_frame.layout().addWidget(card)

    def _bracket_card(self, label, teams, winner):
        card = _GlassCard(radius=14, alpha=70)
        card.setFixedSize(210, 88)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent; letter-spacing: 1px;")

        teams_lbl = QLabel(teams)
        teams_lbl.setAlignment(Qt.AlignCenter)
        teams_lbl.setFont(QFont("Segoe UI", 9))
        teams_lbl.setStyleSheet("color: rgba(255,255,255,180); background: transparent;")

        layout.addWidget(lbl)
        layout.addWidget(teams_lbl)

        if winner:
            win = QLabel(f"🏆  {winner.name}")
            win.setAlignment(Qt.AlignCenter)
            win.setFont(QFont("Segoe UI", 9, QFont.Bold))
            win.setStyleSheet(f"color: {SUCCESS_COLOR}; background: transparent;")
            layout.addWidget(win)

        return card

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _go_next(self):
        self.mw.show_page("menu")

    def _restart(self):
        self.mw.tc.reset()
        self.mw.show_page("home")

    def _animate_confetti(self, step=0):
        icons = ["🎊","🎉","✨","🌟","🎈","🏆","🥇","💫","⭐","🎆"]
        self._confetti_lbl.setText("  ".join(random.choices(icons, k=7)))
        if step < 18:
            QTimer.singleShot(110, lambda: self._animate_confetti(step + 1))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())