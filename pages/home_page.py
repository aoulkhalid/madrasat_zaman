"""pages/home_page.py — Page d'accueil"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QFont, QColor
from pages.base_page import BasePage
from config          import C


class HomePage(BasePage):

    def _build_page(self):
        layout = self._root_layout

        # ── Header sans retour, avec bouton audio ──
        hdr = self._add_header(show_back=False, show_audio=True)
        hdr.set_center("")

        # ── Corps centré ──
        body = QFrame()
        body.setStyleSheet(f"background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setAlignment(Qt.AlignCenter)
        body_layout.setSpacing(20)

        # Décos
        deco_top = QLabel("📚  🧩  ❓  💡  ⭐")
        deco_top.setAlignment(Qt.AlignCenter)
        deco_top.setStyleSheet(f"color: {C['border']}; font-size: 28px; background:transparent;")
        body_layout.addWidget(deco_top)

        # Titre
        title = QLabel("Madrsat\nZaman")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Georgia", 56, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")
        body_layout.addWidget(title)

        # Sous-titre
        sub = QLabel("Application Éducative Interactive")
        sub.setAlignment(Qt.AlignCenter)
        sub.setFont(QFont("Arial", 14))
        sub.setStyleSheet(f"color: {C['text_light']}; background: transparent;")
        body_layout.addWidget(sub)

        sep = QLabel("╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌")
        sep.setAlignment(Qt.AlignCenter)
        sep.setStyleSheet(f"color: {C['border']}; background: transparent;")
        body_layout.addWidget(sep)

        # Bouton COMMENCER
        self._start_btn = QPushButton("  COMMENCER  ")
        self._start_btn.setObjectName("primary")
        self._start_btn.setFont(QFont("Arial", 16, QFont.Bold))
        self._start_btn.setFixedSize(280, 58)
        self._start_btn.clicked.connect(lambda: self.mw.show_page("menu"))
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.addWidget(self._start_btn)
        body_layout.addLayout(btn_row)

        # Décos bas
        deco_bot = QLabel("🏆  Tournoi 4 équipes  ·  3 matchs  ·  Quiz + Logo + Différences")
        deco_bot.setAlignment(Qt.AlignCenter)
        deco_bot.setStyleSheet(
            f"color: {C['text_light']}; font-size: 12px; background: transparent;")
        body_layout.addWidget(deco_bot)

        layout.addStretch()
        layout.addWidget(body)
        layout.addStretch()

        # Pied de page
        footer = QLabel("Propulsé par CS Club  —  Madrasat Zaman v3")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {C['text_light']}; font-size: 11px;")
        layout.addWidget(footer)

    def on_show(self, **kwargs):
        pass
