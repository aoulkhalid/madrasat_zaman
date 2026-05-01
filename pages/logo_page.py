"""
pages/logo_page.py — Logo Game (présentateur valide bonne/mauvaise réponse)
Style : même design que quiz_page — fond image, tout transparent, noms bleus
"""
import os, re
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QTimer, QRect
from PyQt5.QtGui     import (QFont, QPixmap, QPainter, QColor,
                              QLinearGradient, QBrush, QPen, QPainterPath)
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, LOGOS_DIR


BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")

# ── Palette (identique quiz_page) ─────────────────────────────────────────────
ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"
SUCCESS_COLOR = "#22d3a5"
ERROR_COLOR   = "#f43f5e"
TEXT_MUTED    = "rgba(255,255,255,180)"
BLUE_NAME     = "#4f8ef7"
_TRANSPARENT  = "background: transparent; border: none; background-color: transparent;"


# ── Helpers ────────────────────────────────────────────────────────────────────
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


# ── Fond : image plein écran + overlay minimal ────────────────────────────────
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

        # Overlay ultra-léger
        p.fillRect(self.rect(), QColor(0, 0, 0, 30))

        # Ligne lumineuse bleu→violet en haut
        lg = QLinearGradient(0, 0, w, 0)
        lg.setColorAt(0.0,  QColor(79, 142, 247, 0))
        lg.setColorAt(0.35, QColor(79, 142, 247, 160))
        lg.setColorAt(0.65, QColor(168, 85, 247, 160))
        lg.setColorAt(1.0,  QColor(168, 85, 247, 0))
        p.setPen(QPen(QBrush(lg), 2))
        p.drawLine(0, 2, w, 2)


# ── Bouton valider moderne (Bonne / Mauvaise réponse) ─────────────────────────
class _ValidateButton(QPushButton):
    """Bouton avec fond coloré, icône et texte — style premium."""

    def __init__(self, label: str, icon: str, color: str, bg_color: str):
        super().__init__()
        self._label    = label
        self._icon     = icon
        self._color    = QColor(color)
        self._bg_color = QColor(bg_color)
        self.setFixedHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        radius = 14

        # Fond coloré semi-transparent
        if self.underMouse() and self.isEnabled():
            fill = QColor(self._bg_color); fill.setAlpha(220)
        else:
            fill = QColor(self._bg_color); fill.setAlpha(180)

        if not self.isEnabled():
            fill.setAlpha(80)

        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), radius, radius)
        p.fillPath(path, QBrush(fill))

        # Bordure colorée
        border_c = QColor(self._color)
        if not self.isEnabled():
            border_c.setAlpha(80)
        p.setPen(QPen(border_c, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width()-2, r.height()-2, radius, radius)

        # Icône + texte
        text_c = QColor("#ffffff") if self.isEnabled() else QColor(200, 200, 200, 120)
        p.setPen(QPen(text_c))
        p.setFont(QFont("Segoe UI", 15, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{self._icon}  {self._label}")

    def enterEvent(self, e):
        super().enterEvent(e); self.update()
    def leaveEvent(self, e):
        super().leaveEvent(e); self.update()


# ── Page Logo ─────────────────────────────────────────────────────────────────
class LogoPage(BasePage):

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

        # ── Header ────────────────────────────────────────────────
        hdr = self._add_header(show_back=True)
        hdr.set_center("LOGO GAME")
        _make_transparent(hdr)
        _force_labels_blue(hdr)

        # ── Bandeau équipe ────────────────────────────────────────
        self._team_banner = self._add_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)

        # ── Timer + Scoreboard ────────────────────────────────────
        self._timer = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)
        for i in range(self._root_layout.count()):
            item = self._root_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, (QFrame, QWidget)):
                    _make_transparent(w)
                    _force_labels_blue(w)

        # ── Label section ─────────────────────────────────────────
        self._section_lbl = QLabel("Logo 1 / 20")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Segoe UI", 11))
        self._section_lbl.setStyleSheet(
            f"color: {TEXT_MUTED}; background: transparent; padding: 2px;"
        )
        self._root_layout.addWidget(self._section_lbl)

        # ── Carte originale (make_card) ───────────────────────────
        self._card = self._make_card()
        self._card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 215);
                border-radius: 22px;
            }
        """)
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(28, 20, 28, 20)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)

        # Image du logo
        self._logo_lbl = QLabel()
        self._logo_lbl.setAlignment(Qt.AlignCenter)
        self._logo_lbl.setFixedHeight(420)
        self._logo_lbl.setStyleSheet(
            f"background: {C['bg_card']}; border-radius: 12px;"
            f" border: 1px solid {C['border']};"
        )
        card_layout.addWidget(self._logo_lbl)

        # Indice
        self._hint_lbl = QLabel("")
        self._hint_lbl.setAlignment(Qt.AlignCenter)
        self._hint_lbl.setFont(QFont("Segoe UI", 12))
        self._hint_lbl.setStyleSheet(
            f"color: {C['text_light']}; background: transparent;"
        )
        card_layout.addWidget(self._hint_lbl)

        # Feedback
        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setAlignment(Qt.AlignCenter)
        self._feedback_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._feedback_lbl.setStyleSheet("background: transparent;")
        card_layout.addWidget(self._feedback_lbl)

        # ── Boutons Bonne / Mauvaise réponse ─────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)
        btn_row.setContentsMargins(0, 8, 0, 0)

        self._correct_btn = _ValidateButton(
            "BONNE RÉPONSE", "✓",
            color=C["success"],
            bg_color=C["success_bg"]
        )
        self._correct_btn.clicked.connect(lambda: self._validate(True))

        self._wrong_btn = _ValidateButton(
            "MAUVAISE RÉPONSE", "✗",
            color=C["error"],
            bg_color=C["error_bg"]
        )
        self._wrong_btn.clicked.connect(lambda: self._validate(False))

        btn_row.addWidget(self._correct_btn)
        btn_row.addWidget(self._wrong_btn)
        card_layout.addLayout(btn_row)

        wrap = QHBoxLayout()
        wrap.setContentsMargins(36, 0, 36, 14)
        wrap.addWidget(self._card)
        self._root_layout.addLayout(wrap, stretch=1)

        # État
        self._logos      = []
        self._l_idx      = 0
        self._answered   = False
        self._auto_timer = QTimer()
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._next_logo)

    # ── Logique ───────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._logos  = self.mw.tc.get_logo_slice()
        self._l_idx  = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._load_logo()

    def _load_logo(self):
        if self._l_idx >= len(self._logos):
            self.mw.show_page("menu")
            return

        self._answered = False
        logo  = self._logos[self._l_idx]
        team  = self.mw.tc.current_team

        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)

        self._section_lbl.setText(
            f"Logo {self._l_idx + 1} / {len(self._logos)}  ·  Tour : {team.name}"
        )
        self._hint_lbl.setText(logo.get("hint", ""))
        self._feedback_lbl.setText("")

        # Charger image
        path = os.path.join(LOGOS_DIR, logo["image"])
        pix  = QPixmap(path)
        if pix.isNull():
            self._logo_lbl.setPixmap(QPixmap())
            self._logo_lbl.setText(f"[ {logo['name']} ]")
            self._logo_lbl.setStyleSheet(
                f"background: {C['bg_card']}; border-radius:12px;"
                f" border: 1px solid {C['border']};"
                f" font-size:22px; font-weight:bold; color:{C['text_light']};"
            )
        else:
            scaled = pix.scaled(780, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._logo_lbl.setPixmap(scaled)
            self._logo_lbl.setText("")

        self._correct_btn.setEnabled(True)
        self._wrong_btn.setEnabled(True)
        self._timer.reset(TIMER_DURATION)
        self._timer.start()

    def _validate(self, correct: bool):
        if self._answered:
            return
        self._answered = True
        self._timer.stop()
        self._correct_btn.setEnabled(False)
        self._wrong_btn.setEnabled(False)

        pts  = self.mw.tc.answer("logo", correct)
        self._update_scores(self._boxes)

        logo = self._logos[self._l_idx]
        if correct:
            self._feedback_lbl.setText(f"✓  +{pts} pts — {logo['name']}")
            self._feedback_lbl.setStyleSheet(
                f"color: {C['success']}; font-weight: bold; background: transparent;"
            )
        else:
            self._feedback_lbl.setText(f"✗  0 pts — {logo['name']}")
            self._feedback_lbl.setStyleSheet(
                f"color: {C['error']}; font-weight: bold; background: transparent;"
            )

        self._auto_timer.start(1400)

    def _on_timeout(self):
        if not self._answered:
            self._validate(False)

    def _next_logo(self):
        self.mw.tc.next_turn()
        self._l_idx += 1
        self._load_logo()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())