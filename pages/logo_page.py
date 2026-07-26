"""
pages/logo_page.py — Logo Game + HELP / JOKER system
"""
import os, re, random
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QTimer, QRect
from PyQt5.QtGui     import (QFont, QPixmap, QPainter, QColor,
                              QLinearGradient, QBrush, QPen, QPainterPath)
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from widgets.help_popup import HelpPopup, LOGO_HELP_OPTIONS, MAX_HELP_USES
from config import C, TIMER_DURATION, LOGOS_DIR


BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")

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


# ── Fond ──────────────────────────────────────────────────────────────────────
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
                self._bg_pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
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


# ── Bouton valider ─────────────────────────────────────────────────────────────
class _ValidateButton(QPushButton):
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
        if self.underMouse() and self.isEnabled():
            fill = QColor(self._bg_color); fill.setAlpha(220)
        else:
            fill = QColor(self._bg_color); fill.setAlpha(180)
        if not self.isEnabled():
            fill.setAlpha(80)
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), radius, radius)
        p.fillPath(path, QBrush(fill))
        border_c = QColor(self._color)
        if not self.isEnabled():
            border_c.setAlpha(80)
        p.setPen(QPen(border_c, 2)); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width()-2, r.height()-2, radius, radius)
        text_c = QColor("#ffffff") if self.isEnabled() else QColor(200, 200, 200, 120)
        p.setPen(QPen(text_c))
        p.setFont(QFont("Segoe UI", 15, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{self._icon}  {self._label}")

    def enterEvent(self, e): super().enterEvent(e); self.update()
    def leaveEvent(self, e): super().leaveEvent(e); self.update()


# ── Page Logo ──────────────────────────────────────────────────────────────────
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

        self._help_btn = self._make_help_button()
        hdr.layout().insertWidget(hdr.layout().count() - 1, self._help_btn)

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

        # ── Carte ─────────────────────────────────────────────────
        self._card = self._make_card()
        self._card.setStyleSheet(
            "QFrame { background-color: rgba(255,255,255,215); border-radius: 22px; }"
        )
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(28, 20, 28, 20)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)

        # Image logo
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

        # Label info HELP — caché par défaut
        self._help_info_lbl = QLabel("")
        self._help_info_lbl.setAlignment(Qt.AlignCenter)
        self._help_info_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._help_info_lbl.setWordWrap(True)
        self._help_info_lbl.setStyleSheet(
            "background: rgba(79,142,247,18); border-radius: 10px;"
            " padding: 6px 14px; color: #1a5c8a;"
        )
        self._help_info_lbl.setVisible(False)
        card_layout.addWidget(self._help_info_lbl)

        # Feedback validation
        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setAlignment(Qt.AlignCenter)
        self._feedback_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._feedback_lbl.setStyleSheet("background: transparent;")
        card_layout.addWidget(self._feedback_lbl)

        # ── Boutons Bonne / Mauvaise réponse UNIQUEMENT ───────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)
        btn_row.setContentsMargins(0, 8, 0, 0)

        self._correct_btn = _ValidateButton(
            "BONNE RÉPONSE", "✓", color=C["success"], bg_color=C["success_bg"]
        )
        self._correct_btn.clicked.connect(lambda: self._validate(True))

        self._wrong_btn = _ValidateButton(
            "MAUVAISE RÉPONSE", "✗", color=C["error"], bg_color=C["error_bg"]
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

    # =========================================================================
    # HELP BUTTON
    # =========================================================================
    def _make_help_button(self) -> QPushButton:
        btn = QPushButton("🎯  JOKER")
        btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn.setFixedHeight(44)
        btn.setMinimumWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton {"
            f" background: rgba(79,142,247,35); color: {ACCENT_BLUE};"
            f" border: 2px solid {ACCENT_BLUE};"
            "  border-radius: 12px; padding: 0 14px; font-weight: bold; }"
            "QPushButton:hover { background: rgba(79,142,247,70); }"
            "QPushButton:disabled { background: rgba(150,150,150,20);"
            " color: #aaaaaa; border-color: #aaaaaa; }"
        )
        btn.clicked.connect(self._open_help)
        return btn

    def _update_help_btn(self):
        self._help_btn.setEnabled(not self._answered)

    # =========================================================================
    # LOGIQUE PRINCIPALE
    # =========================================================================
    def on_show(self, **kwargs):
        self._logos  = self.mw.tc.get_logo_slice()
        self._l_idx  = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._update_help_btn()
        self._load_logo()

    def _load_logo(self):
        if self._l_idx >= len(self._logos):
            self.mw.show_page("menu")
            return

        self._answered = False
        self._help_info_lbl.setVisible(False)
        logo = self._logos[self._l_idx]
        team = self.mw.tc.current_team

        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._update_help_btn()

        self._section_lbl.setText(
            f"Logo {self._l_idx + 1} / {len(self._logos)}  ·  Tour : {team.name}"
        )
        self._hint_lbl.setText(logo.get("hint", ""))
        self._feedback_lbl.setText("")

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
        self._help_btn.setEnabled(False)
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

    # =========================================================================
    # HELP SYSTEM
    # =========================================================================
    def _open_help(self):
        if self._answered:
            return
        self._timer.stop()
        self.mw.audio.stop()
        self._help_btn.setEnabled(False)

        popup = HelpPopup(self, LOGO_HELP_OPTIONS, 0)
        popup.option_chosen.connect(self._apply_help)
        popup.cancelled.connect(self._resume_after_help)

    def _apply_help(self, option_id: str):
        self._update_help_btn()
        if   option_id == "public_vote": self._help_public_vote()
        elif option_id == "skip":        self._help_skip()
        elif option_id == "teammate":    self._help_teammate()

    def _resume_after_help(self):
        if not self._answered:
            self._timer.start()
            self.mw.audio.play("tension")
            self._update_help_btn()

    def _help_public_vote(self):
        logo   = self._logos[self._l_idx]
        name   = logo["name"]
        self._show_help_info(
            f"👥 Le public indique : commence par « {name[0]} » — {len(name)} lettres",
            "#3498db"
        )
        self._timer.start()
        self.mw.audio.play("tension")

    def _help_skip(self):
        """
        Skip via JOKER — même équipe rejoue le logo suivant.
        next_turn() non appelé → tour inchangé.
        """
        if self._answered:
            return
        self._answered = True
        self._timer.stop()
        self._help_btn.setEnabled(False)
        self._correct_btn.setEnabled(False)
        self._wrong_btn.setEnabled(False)
        logo = self._logos[self._l_idx]
        self._feedback_lbl.setText(f"⏭️  Logo passé — {logo['name']}")
        self._feedback_lbl.setStyleSheet(
            "color: #f39c12; font-weight: bold; background: transparent;"
        )
        QTimer.singleShot(900, self._skip_to_next_logo)

    def _skip_to_next_logo(self):
        self._l_idx += 1
        self._load_logo()

    def _help_teammate(self):
        self._show_help_info("🤝 Discussion autorisée ! Concertez-vous...", "#27ae60")
        self._timer.start()
        self.mw.audio.play("tension")

    def _show_help_info(self, msg: str, color: str = "#3498db"):
        self._help_info_lbl.setText(msg)
        self._help_info_lbl.setStyleSheet(
            f"background: rgba(255,255,255,220); border-radius: 10px;"
            f" padding: 6px 14px; color: {color}; font-weight: bold;"
        )
        self._help_info_lbl.setVisible(True)
        QTimer.singleShot(4000, lambda: self._help_info_lbl.setVisible(False))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())