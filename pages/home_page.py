"""
pages/home_page.py — Page d'accueil (VERSION CS CLUB DESIGN)
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGraphicsDropShadowEffect, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QFont, QPainter, QColor, QLinearGradient,
    QBrush, QPixmap, QFontDatabase
)
import os
from pages.base_page import BasePage
from config import C


# ─────────────────────────────────────────────
#  Chemin background
# ─────────────────────────────────────────────
BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background.png")

# ─────────────────────────────────────────────
#  Chemin police personnalisée
# ─────────────────────────────────────────────
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "Quivert.ttf")


class _Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = QPixmap(BG_PATH)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()

        if not self._bg_pixmap.isNull():
            scaled_bg = self._bg_pixmap.scaled(
                w, h,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            p.drawPixmap(0, 0, scaled_bg)
        else:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#dde6ed"))
            grad.setColorAt(1.0, QColor("#d6e3ec"))
            p.fillRect(self.rect(), QBrush(grad))


class HomePage(BasePage):
    def _build_page(self):
        layout = self._root_layout
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Background
        self._bg = _Background(self)
        self._bg.setGeometry(self.rect())
        self._bg.lower()

        container = QWidget(self)
        container.setAttribute(Qt.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")

        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(30, 20, 30, 20)
        c_layout.setSpacing(0)

        layout.addWidget(container)

        # Header
        hdr = self._add_header(show_back=False, show_audio=True)
        hdr.set_center("")

        # ───────────── CHARGER POLICE QUIVERT
        font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # ───────────── ESPACE HAUT
        c_layout.addStretch()

        # ───────────── TITRE CENTRÉ
        t2 = QLabel("MADRASAT ZAMAN")
        t2.setAlignment(Qt.AlignCenter)
        t2.setFont(QFont(font_family, 70, QFont.Bold))
        t2.setStyleSheet("""
            color: #1a4a6b;
            background: transparent;
        """)
        c_layout.addWidget(t2)

        # ───────────── ESPACE MILIEU
        c_layout.addStretch()

        # ───────────── BOUTON
        self._start_btn = QPushButton("COMMENCER")
        self._start_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._start_btn.setFixedSize(280, 64)
        self._start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 14px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(30, 80, 150, 120))
        self._start_btn.setGraphicsEffect(shadow)

        self._start_btn.clicked.connect(lambda: self.mw.show_page("menu"))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._start_btn)
        btn_row.addStretch()

        c_layout.addLayout(btn_row)

        # ───────────── FOOTER
        footer = QLabel("Propulsé par CS Club")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "color: #5a7a9a; font-size: 11px; margin-top: 10px;"
        )
        c_layout.addWidget(footer)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())

    def on_show(self, **kwargs):
        pass