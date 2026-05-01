"""
pages/base_page.py
Page de base PyQt5 — header, bandeau équipe, scoreboard
Même style moderne : fond transparent, noms bleus, ligne lumineuse
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                              QLabel, QPushButton, QSizePolicy, QSpacerItem)
from PyQt5.QtCore    import Qt, pyqtSignal, QRect
from PyQt5.QtGui     import (QFont, QColor, QPainter, QPen, QBrush,
                              QLinearGradient, QPainterPath)
from config          import C, TEAMS

# ── Palette ────────────────────────────────────────────────────────────────────
ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"
BLUE_NAME     = "#4f8ef7"
TEXT_MUTED    = "rgba(255,255,255,180)"


class HeaderWidget(QFrame):
    """Bandeau supérieur transparent avec ligne lumineuse."""
    back_clicked = pyqtSignal()

    def __init__(self, show_back=True, show_audio_btn=False, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self.setStyleSheet("background: transparent; border: none;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        # Bouton retour
        if show_back:
            self._back = QPushButton("←")
            self._back.setObjectName("back_btn")
            self._back.setFont(QFont("Segoe UI", 14))
            self._back.setFixedSize(36, 36)
            self._back.setStyleSheet(
                "QPushButton { background: rgba(79,142,247,25);"
                " border: 1.5px solid #4f8ef7;"
                " border-radius: 18px; color: #4f8ef7; font-weight: bold; }"
                "QPushButton:hover { background: rgba(79,142,247,80); }"
            )
            self._back.clicked.connect(self.back_clicked.emit)
            layout.addWidget(self._back)

        # Logo texte — bleu gras
        brand = QLabel("CS CLUB")
        brand.setObjectName("header_brand")
        brand.setFont(QFont("Georgia", 11, QFont.Bold))
        brand.setStyleSheet(
            f"color: {BLUE_NAME}; background: transparent; font-weight: bold;"
        )
        layout.addWidget(brand)

        layout.addStretch()

        # Titre central
        self._center_lbl = QLabel("")
        self._center_lbl.setObjectName("header_center")
        self._center_lbl.setAlignment(Qt.AlignCenter)
        self._center_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._center_lbl.setStyleSheet(
            f"color: {BLUE_NAME}; background: transparent; letter-spacing: 2px;"
        )
        layout.addWidget(self._center_lbl)

        layout.addStretch()

        # Bouton audio
        if show_audio_btn:
            self._audio_btn = QPushButton("🔊")
            self._audio_btn.setObjectName("audio_btn")
            self._audio_btn.setFixedSize(40, 40)
            self._audio_btn.setStyleSheet(
                "QPushButton { background: rgba(255,255,255,30);"
                " border: 1px solid rgba(255,255,255,60);"
                " border-radius: 20px; font-size: 16px; }"
                "QPushButton:hover { background: rgba(79,142,247,80); }"
            )
            layout.addWidget(self._audio_btn)
        else:
            self._audio_btn = None

        # Icône déco
        deco = QLabel("💡")
        deco.setStyleSheet("font-size: 20px; background: transparent;")
        layout.addWidget(deco)

    def set_center(self, text: str):
        self._center_lbl.setText(text)

    def connect_audio(self, slot):
        if self._audio_btn:
            self._audio_btn.clicked.connect(slot)

    def paintEvent(self, event):
        """Ligne lumineuse bleu→violet en bas du header."""
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        lg = QLinearGradient(0, 0, w, 0)
        lg.setColorAt(0.0,  QColor(79, 142, 247, 0))
        lg.setColorAt(0.25, QColor(79, 142, 247, 140))
        lg.setColorAt(0.75, QColor(168, 85, 247, 140))
        lg.setColorAt(1.0,  QColor(168, 85, 247, 0))
        p.setPen(QPen(QBrush(lg), 1.5))
        p.drawLine(0, h - 1, w, h - 1)


class TeamBannerWidget(QFrame):
    """Bandeau équipe — semi-transparent avec couleur d'équipe."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("team_banner")
        self.setFixedHeight(38)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._color = QColor(79, 142, 247)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._lbl = QLabel("")
        self._lbl.setObjectName("team_label")
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self._lbl.setStyleSheet(
            f"color: {BLUE_NAME}; background: transparent; letter-spacing: 1px;"
        )
        layout.addWidget(self._lbl)

    def set_team(self, team_key: str):
        t = TEAMS[team_key]
        self._color = QColor(t["color"])
        self._lbl.setText(
            f"{t['emoji']}  {t['name'].upper()}  —  À VOUS DE JOUER !"
        )
        self._lbl.setStyleSheet(
            f"color: {BLUE_NAME}; background: transparent;"
            f" letter-spacing: 1px; font-weight: bold;"
        )
        self.update()

    def paintEvent(self, event):
        """Fond dégradé semi-transparent couleur équipe."""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(self._color); c.setAlpha(45)
        p.fillRect(self.rect(), QBrush(c))
        # Bordure basse
        border_c = QColor(self._color); border_c.setAlpha(100)
        p.setPen(QPen(border_c, 1))
        p.drawLine(0, self.height()-1, self.width(), self.height()-1)


class ScoreBoxWidget(QFrame):
    """Boîte score — transparente avec texte coloré."""

    def __init__(self, team_key: str, parent=None):
        super().__init__(parent)
        self.setObjectName("score_box")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")
        self._team = TEAMS[team_key]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)

        name_lbl = QLabel(self._team["name"])
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        name_lbl.setStyleSheet(
            f"color: {BLUE_NAME}; background: transparent; font-weight: bold;"
        )

        self._score_lbl = QLabel("0")
        self._score_lbl.setAlignment(Qt.AlignCenter)
        self._score_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._score_lbl.setStyleSheet(
            f"color: {BLUE_NAME}; background: transparent; font-weight: bold;"
        )

        layout.addWidget(name_lbl)
        layout.addWidget(self._score_lbl)

    def set_score(self, val: int):
        self._score_lbl.setText(str(val))


class BasePage(QWidget):
    """Classe mère de toutes les pages."""

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)
        self._build_page()

    # ── API à surcharger ──────────────────────────────────────────
    def _build_page(self):
        pass

    def on_show(self, **kwargs):
        pass

    # ── Helpers ───────────────────────────────────────────────────
    def _add_header(self, show_back=True, show_audio=False) -> HeaderWidget:
        hdr = HeaderWidget(show_back=show_back, show_audio_btn=show_audio)
        hdr.back_clicked.connect(lambda: self.mw.show_page("menu"))
        if show_audio:
            hdr.connect_audio(self._toggle_audio)
        self._root_layout.addWidget(hdr)
        return hdr

    def _toggle_audio(self):
        muted = self.mw.audio.toggle_mute()
        btn = self.sender()
        if btn:
            btn.setText("🔇" if muted else "🔊")

    def _add_team_banner(self) -> TeamBannerWidget:
        banner = TeamBannerWidget()
        self._root_layout.addWidget(banner)
        self._team_banner = banner
        return banner

    def _refresh_team_banner(self):
        if hasattr(self, "_team_banner"):
            self._team_banner.set_team(self.mw.tc.current_team.key)

    def _build_scoreboard(self, timer_widget=None) -> dict:
        bar = QWidget()
        bar.setFixedHeight(90)
        bar.setAttribute(Qt.WA_TranslucentBackground)
        bar.setStyleSheet("background: transparent;")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 4, 20, 4)
        h.setSpacing(10)

        if timer_widget:
            h.addWidget(timer_widget)

        h.addStretch()

        m  = self.mw.tc.current_match
        s1 = ScoreBoxWidget(m.team1.key)
        vs = QLabel("VS")
        vs.setFont(QFont("Segoe UI", 13, QFont.Bold))
        vs.setStyleSheet("color: rgba(255,255,255,160); background: transparent;")
        s2 = ScoreBoxWidget(m.team2.key)

        h.addWidget(s1)
        h.addWidget(vs)
        h.addWidget(s2)

        self._root_layout.addWidget(bar)
        return {"s1": s1, "s2": s2}

    def _update_scores(self, boxes: dict):
        m = self.mw.tc.current_match
        boxes["s1"].set_score(m.team1.score)
        boxes["s2"].set_score(m.team2.score)

    def _make_card(self, parent=None) -> QFrame:
        """Carte originale rgba(255,255,255,215) — utilisée par quiz/logo."""
        card = QFrame(parent)
        card.setObjectName("card")
        card.setStyleSheet(
            "QFrame#card { background-color: rgba(255,255,255,215);"
            " border-radius: 22px; border: none; }"
        )
        return card

    def _primary_button(self, text: str, parent=None,
                         name="primary", width=200, height=46) -> QPushButton:
        btn = QPushButton(text, parent)
        btn.setObjectName(name)
        btn.setFixedHeight(height)
        btn.setMinimumWidth(width)
        btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        btn.setStyleSheet(
            f"QPushButton {{ background: {ACCENT_BLUE}; color: red;"
            f" border-radius: 12px; border: none; }}"
            f"QPushButton:hover {{ background: #3a7de8; }}"
        )
        return btn