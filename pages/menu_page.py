"""pages/menu_page.py — Menu principal avec sélection du jeu"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QFont
from pages.base_page import BasePage
from config          import C, TEAMS


class MenuPage(BasePage):

    _GAMES = [
        ("❓", "#1a5c8a", "QUIZ GAME",
         "20 questions QCM — alternance équipes — +5 pts / bonne réponse", "quiz"),
        ("🌿", "#17a589", "LOGO GAME",
         "20 logos — le présentateur valide la réponse orale — +5 pts", "logo"),
        ("🧩", "#e67e22", "DIFFERENCE GAME",
         "10 images — cliquez sur les différences — +5 pts chacune", "difference"),
    ]

    def _build_page(self):
        hdr = self._add_header(show_back=True, show_audio=True)
        hdr.back_clicked.disconnect()
        hdr.back_clicked.connect(lambda: self.mw.show_page("home"))

        # ── Bandeau match actuel ──
        self._match_banner = QFrame()
        self._match_banner.setFixedHeight(50)
        banner_layout = QHBoxLayout(self._match_banner)
        banner_layout.setContentsMargins(24, 0, 24, 0)
        self._match_lbl = QLabel("")
        self._match_lbl.setAlignment(Qt.AlignCenter)
        self._match_lbl.setFont(QFont("Arial", 15, QFont.Bold))
        self._match_lbl.setStyleSheet("color: white;")
        banner_layout.addWidget(self._match_lbl)
        self._root_layout.addWidget(self._match_banner)

        # Titre
        title = QLabel("CHOISISSEZ UN JEU")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {C['text_dark']}; padding: 16px 0 8px 0;")
        self._root_layout.addWidget(title)

        # Cartes de jeux
        cards_widget = QFrame()
        cards_widget.setStyleSheet("background: transparent;")
        cards_layout = QVBoxLayout(cards_widget)
        cards_layout.setContentsMargins(60, 0, 60, 0)
        cards_layout.setSpacing(12)

        for icon, color, name, desc, page in self._GAMES:
            self._make_game_card(cards_layout, icon, color, name, desc, page)

        self._root_layout.addWidget(cards_widget)
        self._root_layout.addStretch()

        # ── Bouton terminer le match ──
        end_row = QHBoxLayout()
        end_row.setAlignment(Qt.AlignCenter)
        self._end_btn = QPushButton("  🏁  TERMINER CE MATCH  ")
        self._end_btn.setObjectName("danger_btn")
        self._end_btn.setFixedSize(280, 48)
        self._end_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self._end_btn.clicked.connect(self._end_match)
        end_row.addWidget(self._end_btn)
        self._root_layout.addLayout(end_row)

        # Pied de page
        footer = QLabel("Propulsé par CS Club")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {C['text_light']}; font-size: 11px; padding: 10px;")
        self._root_layout.addWidget(footer)

    def _make_game_card(self, parent_layout, icon, color, name, desc, page):
        # Shadow effect via frame
        shadow = QFrame()
        shadow.setStyleSheet(
            f"background-color: {C['shadow']}; border-radius: 14px;")
        shadow.setFixedHeight(76)
        shadow_layout = QVBoxLayout(shadow)
        shadow_layout.setContentsMargins(0, 0, 0, 3)

        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: {C['white']}; border-radius: 13px; }}"
            f"QFrame:hover {{ background-color: #edf4fb; }}")
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedHeight(72)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 10, 16, 10)
        card_layout.setSpacing(16)

        # Icône
        icon_box = QFrame()
        icon_box.setFixedSize(52, 52)
        icon_box.setStyleSheet(
            f"background-color: {color}; border-radius: 10px;")
        icon_layout = QVBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Arial", 22))
        icon_lbl.setStyleSheet("background: transparent; color: white;")
        icon_layout.addWidget(icon_lbl)

        # Textes
        txt_frame = QFrame()
        txt_frame.setStyleSheet("background: transparent;")
        txt_layout = QVBoxLayout(txt_frame)
        txt_layout.setContentsMargins(0, 0, 0, 0)
        txt_layout.setSpacing(2)
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Arial", 13, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")
        desc_lbl = QLabel(desc)
        desc_lbl.setFont(QFont("Arial", 10))
        desc_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")
        txt_layout.addWidget(name_lbl)
        txt_layout.addWidget(desc_lbl)

        arrow = QLabel("›")
        arrow.setFont(QFont("Arial", 26, QFont.Bold))
        arrow.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        card_layout.addWidget(icon_box)
        card_layout.addWidget(txt_frame, 1)
        card_layout.addWidget(arrow)

        shadow_layout.addWidget(card)
        parent_layout.addWidget(shadow)

        # Clic sur la carte
        card.mousePressEvent = lambda e, p=page: self.mw.show_page(p)
        icon_box.mousePressEvent = lambda e, p=page: self.mw.show_page(p)

    def _end_match(self):
        done = self.mw.tc.end_match()
        self.mw.show_page("result", tournament_over=done)

    def on_show(self, **kwargs):
        m = self.mw.tc.current_match
        t1 = TEAMS[m.team1.key]
        t2 = TEAMS[m.team2.key]
        color = t1["color"]
        self._match_banner.setStyleSheet(
            f"background-color: {color}; border-radius: 0;")
        self._match_lbl.setText(
            f"⚔️  {m.label.upper()}  —  "
            f"{t1['emoji']} {t1['name']} vs {t2['emoji']} {t2['name']}")
        # Désactiver terminer match sur finale si déjà terminée
        if self.mw.tc.current_match.finished:
            self._end_btn.setEnabled(False)
