"""
widgets/help_popup.py — Système HELP / JOKER
Popup modal moderne, animations d'entrée, pause timer automatique
Réutilisable dans tous les game screens.

Usage dans une page :
    from widgets.help_popup import HelpPopup, MAX_HELP_USES

    popup = HelpPopup(self, OPTIONS_LIST, self._help_uses_left)
    popup.option_chosen.connect(self._apply_help)
    popup.cancelled.connect(self._resume_after_help)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy,
                              QGraphicsOpacityEffect)
from PyQt5.QtCore    import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui     import (QPainter, QColor, QFont, QBrush,
                              QPainterPath, QPen, QLinearGradient)

# ── Constantes globales ────────────────────────────────────────────────────────
MAX_HELP_USES = 3
ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"

# ── Options prédéfinies par jeu ────────────────────────────────────────────────
QUIZ_HELP_OPTIONS = [
    {"id": "fifty_fifty",  "icon": "❌",
     "label": "Supprimer 2 mauvaises réponses",
     "desc":  "Élimine 2 réponses incorrectes (50/50)",
     "color": "#e74c3c"},
    {"id": "skip",         "icon": "⏭️",
     "label": "Passer la question",
     "desc":  "Aller à la suivante sans perdre de points",
     "color": "#f39c12"},
    {"id": "public_vote",  "icon": "👥",
     "label": "Demander au public",
     "desc":  "Affiche une suggestion populaire pondérée",
     "color": "#3498db"},
    {"id": "teammate",     "icon": "🤝",
     "label": "Demander à un coéquipier",
     "desc":  "Discussion autorisée 30 secondes",
     "color": "#27ae60"},
]

LOGO_HELP_OPTIONS = [
    {"id": "public_vote",  "icon": "👥",
     "label": "Demander au public",
     "desc":  "Indice sur le nom du logo",
     "color": "#3498db"},
    {"id": "skip",         "icon": "⏭️",
     "label": "Passer le logo",
     "desc":  "Skip sans point ni pénalité",
     "color": "#f39c12"},
    {"id": "teammate",     "icon": "🤝",
     "label": "Demander à un coéquipier",
     "desc":  "Discussion autorisée 30 secondes",
     "color": "#27ae60"},
]

DIFF_HELP_OPTIONS = [
    {"id": "skip",         "icon": "⏭️",
     "label": "Passer l'image",
     "desc":  "Passer à l'image suivante",
     "color": "#f39c12"},
    {"id": "teammate",     "icon": "🤝",
     "label": "Demander à un coéquipier",
     "desc":  "Discussion autorisée 30 secondes",
     "color": "#27ae60"},
]


# ── Bouton option ──────────────────────────────────────────────────────────────
class _OptionBtn(QPushButton):
    """Bouton d'aide stylisé avec icône, titre et description."""

    def __init__(self, icon: str, label: str, desc: str, color: str = ACCENT_BLUE):
        super().__init__()
        self._icon  = icon
        self._label = label
        self._desc  = desc
        self._col   = QColor(color)
        self.setFixedHeight(74)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        # Fond coloré semi-transparent
        bg = QColor(self._col)
        bg.setAlpha(35 if self.underMouse() else 14)
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), 14, 14)
        p.fillPath(path, QBrush(bg))

        # Bordure
        p.setPen(QPen(self._col, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width() - 2, r.height() - 2, 14, 14)

        # Icône
        p.setFont(QFont("Segoe UI Emoji", 22))
        p.setPen(QPen(self._col))
        p.drawText(QRect(14, 0, 52, r.height()),
                   Qt.AlignVCenter | Qt.AlignCenter, self._icon)

        # Label principal
        p.setFont(QFont("Segoe UI", 13, QFont.Bold))
        p.setPen(QPen(QColor("#1a2c42")))
        p.drawText(QRect(78, 12, r.width() - 92, 26), Qt.AlignVCenter, self._label)

        # Description
        p.setFont(QFont("Segoe UI", 10))
        p.setPen(QPen(QColor("#7f8c8d")))
        p.drawText(QRect(78, 40, r.width() - 92, 22), Qt.AlignVCenter, self._desc)

    def enterEvent(self, e): super().enterEvent(e); self.update()
    def leaveEvent(self, e): super().leaveEvent(e); self.update()


# ── Popup principal ────────────────────────────────────────────────────────────
class HelpPopup(QWidget):
    """
    Modal overlay HELP/JOKER.

    Signals
    -------
    option_chosen(str) : id de l'option sélectionnée
    cancelled()        : popup fermée sans choix → reprendre le jeu
    """
    option_chosen = pyqtSignal(str)
    cancelled     = pyqtSignal()

    def __init__(self, parent: QWidget, options: list, uses_left: int):
        """
        Parameters
        ----------
        parent     : page parente (la popup couvre tout son espace)
        options    : liste de dicts {"id","icon","label","desc","color"}
        uses_left  : nombre de jokers restants (affiché en en-tête)
        """
        super().__init__(parent)
        self.setGeometry(parent.rect())
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build_ui(options, uses_left)
        self.show()
        self.raise_()
        self._animate_in()

    # ── Construction ──────────────────────────────────────────────
    def _build_ui(self, options: list, uses_left: int):
        self._card = QFrame(self)
        self._card.setFixedWidth(520)
        self._card.setStyleSheet(
            "QFrame { background: white; border-radius: 26px; border: none; }"
        )

        lay = QVBoxLayout(self._card)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(10)

        # ── En-tête ───────────────────────────────────────────────
        hdr = QHBoxLayout()

        title = QLabel("🎯  AIDE / JOKER")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")

        hdr.addWidget(title)
        hdr.addStretch()
        lay.addLayout(hdr)

        # Ligne décorative bleu → violet
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {ACCENT_BLUE}, stop:1 {ACCENT_PURPLE});"
            " border: none; border-radius: 1px;"
        )
        lay.addWidget(sep)
        lay.addSpacing(2)

        # ── Boutons options ───────────────────────────────────────
        for opt in options:
            btn = _OptionBtn(
                opt["icon"], opt["label"],
                opt["desc"], opt.get("color", ACCENT_BLUE)
            )
            btn.clicked.connect(lambda _, oid=opt["id"]: self._choose(oid))
            lay.addWidget(btn)

        lay.addSpacing(4)

        # ── Bouton Annuler ────────────────────────────────────────
        cancel_btn = QPushButton("✕  Annuler — Reprendre le jeu")
        cancel_btn.setFixedHeight(46)
        cancel_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        cancel_btn.setStyleSheet(
            "QPushButton { background: #f1f5f9; color: #64748b;"
            " border: none; border-radius: 13px; }"
            "QPushButton:hover { background: #e2e8f0; }"
        )
        cancel_btn.clicked.connect(self._cancel)
        lay.addWidget(cancel_btn)

        # Centrer la carte
        self._card.adjustSize()
        self._center_card()

    def _center_card(self):
        self._card.adjustSize()
        cx = (self.width()  - self._card.width())  // 2
        cy = (self.height() - self._card.height()) // 2
        self._card.move(cx, cy)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._center_card()

    # ── Animation d'entrée (fade-in) ──────────────────────────────
    def _animate_in(self):
        eff = QGraphicsOpacityEffect(self._card)
        self._card.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(200)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._anim = anim   # garder la référence pour éviter GC

    # ── Callbacks ─────────────────────────────────────────────────
    def _choose(self, option_id: str):
        self.option_chosen.emit(option_id)
        self.close()
        self.deleteLater()

    def _cancel(self):
        self.cancelled.emit()
        self.close()
        self.deleteLater()

    # ── Fond overlay semi-transparent ─────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 158))