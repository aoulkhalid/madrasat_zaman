"""
pages/menu_page.py — Menu principal (VERSION MODERNE + BACKGROUND + SCROLL)
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QPixmap, QColor, QLinearGradient, QBrush
import os
from pages.base_page import BasePage
from config import C, TEAMS


# ─────────────────────────────────────────────
#  Chemin background
# ─────────────────────────────────────────────
BG2_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")


# ─────────────────────────────────────────────
#  Widget de fond
# ─────────────────────────────────────────────
class _Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = QPixmap(BG2_PATH)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()

        if not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            p.drawPixmap(0, 0, scaled)
        else:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#dde6ed"))
            grad.setColorAt(1.0, QColor("#d6e3ec"))
            p.fillRect(self.rect(), QBrush(grad))


# ─────────────────────────────────────────────
#  Page Menu
# ─────────────────────────────────────────────
class MenuPage(BasePage):

    _GAMES = [
        ("❓", "#1565C0", "#1E88E5", "QUIZ GAME",
         "20 questions QCM — alternance équipes — +5 pts / bonne réponse", "quiz"),
        ("🌿", "#00695C", "#00897B", "LOGO GAME",
         "20 logos — réponse orale — +5 pts", "logo"),
        ("🧩", "#E65100", "#FB8C00", "DIFFERENCE GAME",
         "10 images — trouvez les différences — +5 pts", "difference"),
        ("🔐", "#6b3fa0", "#9b6fd0", "LE CODE SECRET",
         "Devinez le code de l'équipe adverse — jusqu'à +40 pts", "secret_code"),
        ("🌪️", "#0e7c86", "#14a3b0", "JEU DES ÉLÉMENTS",
         "Devinez la combinaison — +5 pts", "element"),
        ("🏦", "#8a5a1a", "#c98a3a", "BRAQUAGE DE BANQUE",
         "4 missions, 3 minutes — +40 pts", "heist"),
        ("🕵️", "#2c3e50", "#4a637a", "CYBER INVESTIGATION",
         "Résolvez l'enquête en 5 minutes — +40 pts", "cyber"),
        ("🎵", "#7a1f7a", "#a83fa8", "BLIND TEST",
         "Le premier qui trouve gagne — +10 pts", "blindtest"),
        ("💼", "#1a5f3a", "#2f8a58", "LE BON INVESTISSEMENT",
         "Répartissez votre capital — jusqu'à +45 pts", "investment"),
         ("📡", "#c0392b", "#e57373", "TRANSMISSION",
        "Relais oral en 4 joueurs — +5 pts", "transmission"),
        ("🧠", "#5b2c8a", "#8e5fc4", "MEMORY CHALLENGE",
        "3 manches, 5→10 paires — jusqu'à +450 pts", "memory"),
    ]

    def _build_page(self):
        layout = self._root_layout
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Fond plein écran ──────────────────────────────────────
        self._bg = _Background(self)
        self._bg.setGeometry(self.rect())
        self._bg.lower()

        # ── Conteneur principal transparent ──────────────────────
        container = QWidget(self)
        container.setAttribute(Qt.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(40, 20, 40, 12)
        c_layout.setSpacing(0)
        layout.addWidget(container)

        # ── Header (fixe) ─────────────────────────────────────────
        hdr = self._add_header(show_back=True, show_audio=True)
        hdr.back_clicked.disconnect()
        hdr.back_clicked.connect(lambda: self.mw.show_page("home"))

        # ── Banner match (fixe) ────────────────────────────────────
        self._match_banner = QFrame()
        self._match_banner.setFixedHeight(60)
        self._match_banner.setStyleSheet("""
            QFrame {
                border-radius: 16px;
            }
        """)
        banner_shadow = QGraphicsDropShadowEffect()
        banner_shadow.setBlurRadius(20)
        banner_shadow.setOffset(0, 4)
        banner_shadow.setColor(QColor(0, 0, 0, 60))
        self._match_banner.setGraphicsEffect(banner_shadow)

        banner_layout = QHBoxLayout(self._match_banner)
        banner_layout.setContentsMargins(24, 0, 24, 0)

        self._match_lbl = QLabel("")
        self._match_lbl.setAlignment(Qt.AlignCenter)
        self._match_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._match_lbl.setStyleSheet("color: white; background: transparent;")
        banner_layout.addWidget(self._match_lbl)

        c_layout.addSpacing(10)
        c_layout.addWidget(self._match_banner)
        c_layout.addSpacing(10)

        # ── Zone défilante : titre + cartes + bouton + footer ─────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 40);
                width: 10px;
                border-radius: 5px;
                margin: 2px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(42, 127, 165, 190);
                border-radius: 5px;
                min-height: 32px;
            }
            QScrollBar::handle:vertical:hover { background: rgba(42, 127, 165, 240); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        s_layout = QVBoxLayout(scroll_content)
        s_layout.setContentsMargins(0, 0, 10, 0)
        s_layout.setSpacing(0)

        # ── Titre ─────────────────────────────────────────────────
        title = QLabel("CHOISISSEZ UN JEU")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 19, QFont.Bold))
        title.setStyleSheet("color: #1a3a5c; background: transparent; margin-bottom: 4px;")
        s_layout.addWidget(title)
        s_layout.addSpacing(8)

        # ── Cartes jeux ───────────────────────────────────────────
        for icon, color_dark, color_light, name, desc, page in self._GAMES:
            card = self._make_game_card(icon, color_dark, color_light, name, desc, page)
            s_layout.addWidget(card)
            s_layout.addSpacing(10)

        s_layout.addSpacing(4)

        # ── Bouton TERMINER ───────────────────────────────────────
        self._end_btn = QPushButton("🏁  TERMINER CE MATCH")
        self._end_btn.setFixedSize(340, 54)
        self._end_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self._end_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a7fa5;
                color: white;
                border: none;
                border-radius: 16px;
                letter-spacing: 1px;
            }
            QPushButton:hover  { background-color: #3a9abf; }
            QPushButton:pressed { background-color: #1a5f80; }
            QPushButton:disabled { background-color: #bdc3c7; color: #888; }
        """)
        end_shadow = QGraphicsDropShadowEffect()
        end_shadow.setBlurRadius(22)
        end_shadow.setOffset(0, 6)
        end_shadow.setColor(QColor(42, 127, 165, 130))
        self._end_btn.setGraphicsEffect(end_shadow)
        self._end_btn.clicked.connect(self._end_match)

        end_row = QHBoxLayout()
        end_row.setAlignment(Qt.AlignCenter)
        end_row.addWidget(self._end_btn)
        s_layout.addLayout(end_row)
        s_layout.addSpacing(10)

        # ── Footer ────────────────────────────────────────────────
        footer = QLabel("Propulsé par CS Club")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "color: #5a7a9a; font-size: 11px; background: transparent; margin-top: 4px;"
        )
        s_layout.addWidget(footer)
        s_layout.addStretch()

        scroll.setWidget(scroll_content)
        c_layout.addWidget(scroll, stretch=1)

    # ─────────────────────────────────────────────
    #  Carte jeu moderne (dimensions réduites et cohérentes)
    # ─────────────────────────────────────────────
    def _make_game_card(self, icon, color_dark, color_light, name, desc, page):
        card = QFrame()
        card.setFixedHeight(78)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 220);
                border-radius: 16px;
                border-left: 5px solid {color_dark};
            }}
            QFrame:hover {{
                background-color: rgba(255, 255, 255, 255);
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)

        row = QHBoxLayout(card)
        row.setContentsMargins(16, 10, 16, 10)
        row.setSpacing(14)

        # Icône colorée
        icon_box = QFrame()
        icon_box.setFixedSize(52, 52)
        icon_box.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {color_light}, stop:1 {color_dark});
            border-radius: 13px;
            border: none;
        """)
        icon_layout = QVBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Noto Color Emoji", 22))
        icon_lbl.setStyleSheet("background: transparent; color: white;")
        icon_layout.addWidget(icon_lbl)
        row.addWidget(icon_box)

        # Texte
        txt = QVBoxLayout()
        txt.setSpacing(2)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {color_dark}; background: transparent;")

        desc_lbl = QLabel(desc)
        desc_lbl.setFont(QFont("Segoe UI", 9))
        desc_lbl.setStyleSheet("color: #5a7a9a; background: transparent;")
        desc_lbl.setWordWrap(True)

        txt.addWidget(name_lbl)
        txt.addWidget(desc_lbl)
        row.addLayout(txt, 1)

        # Flèche
        arrow = QLabel("›")
        arrow.setFont(QFont("Segoe UI", 26, QFont.Bold))
        arrow.setStyleSheet(f"color: {color_light}; background: transparent;")
        row.addWidget(arrow)

        # Clic
        card.mousePressEvent      = lambda e, p=page: self.mw.show_page(p)
        icon_box.mousePressEvent  = lambda e, p=page: self.mw.show_page(p)

        return card

    # ─────────────────────────────────────────────
    #  Logique
    # ─────────────────────────────────────────────
    def _end_match(self):
        done = self.mw.tc.end_match()
        self.mw.show_page("result", tournament_over=done)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())

    def on_show(self, **kwargs):
        m  = self.mw.tc.current_match
        t1 = TEAMS[m.team1.key]
        t2 = TEAMS[m.team2.key]

        self._match_banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {t1['color']}, stop:1 {t2['color']});
                border-radius: 16px;
            }}
        """)
        self._match_lbl.setText(
            f"⚔️  {m.label.upper()} — {t1['emoji']} {t1['name']}  vs  {t2['emoji']} {t2['name']}"
        )

        if self.mw.tc.current_match.finished:
            self._end_btn.setEnabled(False)
        else:
            self._end_btn.setEnabled(True)