"""
pages/menu_page.py — Menu principal (VERSION MODERNE + BACKGROUND)
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QWidget
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
        c_layout.setContentsMargins(40, 20, 40, 20)
        c_layout.setSpacing(0)
        layout.addWidget(container)

        # ── Header ────────────────────────────────────────────────
        hdr = self._add_header(show_back=True, show_audio=True)
        hdr.back_clicked.disconnect()
        hdr.back_clicked.connect(lambda: self.mw.show_page("home"))

        # ── Banner match ──────────────────────────────────────────
        self._match_banner = QFrame()
        self._match_banner.setFixedHeight(64)
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
        self._match_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self._match_lbl.setStyleSheet("color: white; background: transparent;")
        banner_layout.addWidget(self._match_lbl)
        c_layout.addSpacing(12)
        c_layout.addWidget(self._match_banner)
        c_layout.addSpacing(16)

        # ── Titre ─────────────────────────────────────────────────
        title = QLabel("CHOISISSEZ UN JEU")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #1a3a5c; background: transparent; margin-bottom: 8px;")
        c_layout.addWidget(title)
        c_layout.addSpacing(10)

        # ── Cartes jeux ───────────────────────────────────────────
        for icon, color_dark, color_light, name, desc, page in self._GAMES:
            card = self._make_game_card(icon, color_dark, color_light, name, desc, page)
            c_layout.addWidget(card)
            c_layout.addSpacing(14)

        c_layout.addStretch()

        # ── Bouton TERMINER ───────────────────────────────────────
        self._end_btn = QPushButton("🏁  TERMINER CE MATCH")
        self._end_btn.setFixedSize(340, 58)
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
        c_layout.addLayout(end_row)
        c_layout.addSpacing(6)

        # ── Footer ────────────────────────────────────────────────
        footer = QLabel("Propulsé par CS Club")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "color: #5a7a9a; font-size: 11px; background: transparent; margin-top: 6px;"
        )
        c_layout.addWidget(footer)

    # ─────────────────────────────────────────────
    #  Carte jeu moderne
    # ─────────────────────────────────────────────
    def _make_game_card(self, icon, color_dark, color_light, name, desc, page):
        card = QFrame()
        card.setFixedHeight(100)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 220);
                border-radius: 20px;
                border-left: 6px solid {color_dark};
            }}
            QFrame:hover {{
                background-color: rgba(255, 255, 255, 255);
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 45))
        card.setGraphicsEffect(shadow)

        row = QHBoxLayout(card)
        row.setContentsMargins(20, 14, 20, 14)
        row.setSpacing(18)

        # Icône colorée
        icon_box = QFrame()
        icon_box.setFixedSize(66, 66)
        icon_box.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {color_light}, stop:1 {color_dark});
            border-radius: 16px;
            border: none;
        """)
        icon_layout = QVBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 28))
        icon_lbl.setStyleSheet("background: transparent; color: white;")
        icon_layout.addWidget(icon_lbl)
        row.addWidget(icon_box)

        # Texte
        txt = QVBoxLayout()
        txt.setSpacing(4)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {color_dark}; background: transparent;")

        desc_lbl = QLabel(desc)
        desc_lbl.setFont(QFont("Segoe UI", 10))
        desc_lbl.setStyleSheet("color: #5a7a9a; background: transparent;")
        desc_lbl.setWordWrap(True)

        txt.addWidget(name_lbl)
        txt.addWidget(desc_lbl)
        row.addLayout(txt, 1)

        # Flèche
        arrow = QLabel("›")
        arrow.setFont(QFont("Segoe UI", 32, QFont.Bold))
        arrow.setStyleSheet(f"color: {color_light}; background: transparent;")
        row.addWidget(arrow)

        # Clic
        card.mousePressEvent  = lambda e, p=page: self.mw.show_page(p)
        icon_box.mousePressEvent = lambda e, p=page: self.mw.show_page(p)

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