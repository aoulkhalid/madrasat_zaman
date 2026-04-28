"""
pages/base_page.py
Page de base PyQt5 — header, bandeau équipe, scoreboard
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                              QLabel, QPushButton, QSizePolicy, QSpacerItem)
from PyQt5.QtCore    import Qt, pyqtSignal
from PyQt5.QtGui     import QFont, QColor
from config          import C, TEAMS


class HeaderWidget(QFrame):
    """Bandeau supérieur bleu foncé."""
    back_clicked = pyqtSignal()

    def __init__(self, show_back=True, show_audio_btn=False, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        # Bouton retour
        if show_back:
            self._back = QPushButton("←")
            self._back.setObjectName("back_btn")
            self._back.clicked.connect(self.back_clicked.emit)
            layout.addWidget(self._back)

        # Logo texte
        brand = QLabel("🌿 MADRSAT\n    ZAMAN")
        brand.setObjectName("header_brand")
        brand.setFont(QFont("Georgia", 12, QFont.Bold))
        layout.addWidget(brand)

        layout.addStretch()

        # Titre central (facultatif)
        self._center_lbl = QLabel("")
        self._center_lbl.setObjectName("header_brand")
        self._center_lbl.setAlignment(Qt.AlignCenter)
        self._center_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(self._center_lbl)

        layout.addStretch()

        # Bouton audio
        if show_audio_btn:
            self._audio_btn = QPushButton("🔊")
            self._audio_btn.setObjectName("audio_btn")
            self._audio_btn.setFixedSize(40, 40)
            layout.addWidget(self._audio_btn)
        else:
            self._audio_btn = None

        # Icône décorative
        deco = QLabel("💡")
        deco.setStyleSheet("color: white; font-size: 20px;")
        layout.addWidget(deco)

    def set_center(self, text: str):
        self._center_lbl.setText(text)

    def connect_audio(self, slot):
        if self._audio_btn:
            self._audio_btn.clicked.connect(slot)


class TeamBannerWidget(QFrame):
    """Bandeau coloré indiquant l'équipe active."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("team_banner")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._lbl = QLabel("")
        self._lbl.setObjectName("team_label")
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setFont(QFont("Arial", 14, QFont.Bold))
        self._lbl.setStyleSheet("color: white;")
        layout.addWidget(self._lbl)

    def set_team(self, team_key: str):
        t = TEAMS[team_key]
        self.setStyleSheet(
            f"QFrame#team_banner {{ background-color: {t['color']}; }}")
        self._lbl.setText(
            f"{t['emoji']}  {t['name'].upper()}  —  À VOUS DE JOUER !")


class ScoreBoxWidget(QFrame):
    """Boîte d'affichage du score d'une équipe."""
    def __init__(self, team_key: str, parent=None):
        super().__init__(parent)
        self.setObjectName("score_box")
        self._team = TEAMS[team_key]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        name_lbl = QLabel(self._team["name"])
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setFont(QFont("Arial", 10, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {self._team['color']};")

        self._score_lbl = QLabel("0")
        self._score_lbl.setAlignment(Qt.AlignCenter)
        self._score_lbl.setFont(QFont("Arial", 20, QFont.Bold))
        self._score_lbl.setStyleSheet(f"color: {self._team['color']};")

        layout.addWidget(name_lbl)
        layout.addWidget(self._score_lbl)

    def set_score(self, val: int):
        self._score_lbl.setText(str(val))


class BasePage(QWidget):
    """Classe mère de toutes les pages."""

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window    # référence à MainWindow
        self.setStyleSheet(f"background-color: {C['bg']};")
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)
        self._build_page()

    # ── API à surcharger ──────────────────────────────────────────────────────

    def _build_page(self):
        pass

    def on_show(self, **kwargs):
        pass

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _add_header(self, show_back=True, show_audio=False) -> HeaderWidget:
        hdr = HeaderWidget(show_back=show_back,
                           show_audio_btn=show_audio)
        hdr.back_clicked.connect(lambda: self.mw.show_page("menu"))
        if show_audio:
            hdr.connect_audio(self._toggle_audio)
        self._root_layout.addWidget(hdr)
        return hdr

    def _toggle_audio(self):
        muted = self.mw.audio.toggle_mute()
        # Retrouver le bouton et changer l'icône
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
        """
        Ligne : [timer] ── [score E1] VS [score E2]
        Retourne {"s1": ScoreBoxWidget, "s2": ScoreBoxWidget}
        """
        bar = QWidget()
        bar.setFixedHeight(90)
        bar.setStyleSheet(f"background-color: {C['bg']};")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 4, 20, 4)
        h.setSpacing(10)

        if timer_widget:
            h.addWidget(timer_widget)

        h.addStretch()

        m   = self.mw.tc.current_match
        s1  = ScoreBoxWidget(m.team1.key)
        vs  = QLabel("VS")
        vs.setFont(QFont("Arial", 13, QFont.Bold))
        vs.setStyleSheet(f"color: {C['text_light']};")
        s2  = ScoreBoxWidget(m.team2.key)

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
        card = QFrame(parent)
        card.setObjectName("card")
        card.setStyleSheet(
            f"QFrame#card {{ background-color: {C['white']};"
            f" border-radius: 16px; border: 1px solid {C['border']}; }}")
        return card

    def _primary_button(self, text: str, parent=None,
                         name="primary", width=200, height=46) -> QPushButton:
        btn = QPushButton(text, parent)
        btn.setObjectName(name)
        btn.setFixedHeight(height)
        btn.setMinimumWidth(width)
        btn.setFont(QFont("Arial", 13, QFont.Bold))
        return btn
