"""
pages/transmission_page.py — 📡 Transmission

Étape 1 (VIEW)   : l'image s'affiche, seul le Joueur 1 de l'équipe regarde l'écran.
Étape 2 (RELAY)  : l'écran masque l'image, les 4 joueurs se relaient l'info à l'oral.
Étape 3 (SELECT) : 4 images s'affichent, le Joueur 4 choisit la bonne, le/la
                    responsable valide le clic.
Étape 4 (BREAK)  : pause de 10 secondes avant le round suivant.
"""
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget, QGridLayout,
                              QGraphicsDropShadowEffect)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor, QPainter, QPixmap

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, TRANSMISSION_VIEW_DURATION, TRANSMISSION_RELAY_DURATION,
                     TRANSMISSION_SELECT_DURATION, TRANSMISSION_BREAK_DURATION,
                     TRANSMISSION_POINTS_CORRECT)

# NOTE : adapte le nom de fichier si ton image de fond "transmission" porte un
# autre nom dans assets/images (ex. background2.png pour réutiliser celle du
# braquage). Le paintEvent ci-dessous ne fait rien si le fichier est
# introuvable (pixmap.isNull()), donc aucun risque de crash — juste pas de
# fond affiché tant que le chemin n'est pas correct.
BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png"
    )
).replace("\\", "/")


# ── Petits utilitaires de teinte : dérivent des couleurs de C, n'en ajoutent
#    aucune nouvelle. C'est ce qui permet un thème "salle de contrôle" sombre
#    tout en restant 100% dans la palette existante. ─────────────────────────
def _shade(hex_color, factor=150):
    """Version plus sombre d'une couleur existante."""
    return QColor(hex_color).darker(factor).name()


def _tint(hex_color, factor=140):
    """Version plus claire d'une couleur existante."""
    return QColor(hex_color).lighter(factor).name()


def _rgba(hex_color, alpha):
    """Version translucide d'une couleur existante (alpha 0-255)."""
    c = QColor(hex_color)
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {alpha})"


def _make_shadow(blur=28, dx=0, dy=8, color=None, alpha=90):
    """Ombre/halo portée réutilisable ; `color` permet un halo coloré
    (utilisé pour la lueur verte/rouge de bonne/mauvaise réponse)."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    qc = QColor(color) if color is not None else QColor(0, 0, 0)
    qc.setAlpha(alpha)
    shadow.setColor(qc)
    return shadow


GLASS_BG     = "rgba(255, 255, 255, 0.85)"   # panneau "verre" translucide
ACCENT       = C['primary']
ACCENT_LIGHT = _tint(C['primary'], 135)


class _StageStepper(QFrame):
    """Indicateur d'étapes VOIR → RELAIS → CHOIX → PAUSE, affiché sur le fond
    clair de l'app (donc contrasté clair, pas sombre) — remplace l'ancien
    texte plat "Round X / N"."""

    STEPS = [("view", "👁️ VOIR"), ("relay", "📡 RELAIS"),
             ("select", "🎯 CHOIX"), ("break", "⏸️ PAUSE")]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._pills = {}
        for key, label in self.STEPS:
            pill = QLabel(label)
            pill.setAlignment(Qt.AlignCenter)
            pill.setFixedHeight(42)
            pill.setFont(QFont("Segoe UI", 13, QFont.Bold))
            self._pills[key] = pill
            row.addWidget(pill)

        self.set_stage("view")

    def set_stage(self, stage):
        order = [k for k, _ in self.STEPS]
        current_i = order.index(stage) if stage in order else 0
        for i, (key, _label) in enumerate(self.STEPS):
            pill = self._pills[key]
            if key == stage:
                pill.setStyleSheet(f"""
                    color: white;
                    background-color: {ACCENT};
                    border-radius: 21px;
                    padding: 0 22px;
                """)
            elif i < current_i:
                pill.setStyleSheet(f"""
                    color: {ACCENT};
                    background-color: white;
                    border: 2px solid {ACCENT};
                    border-radius: 21px;
                    padding: 0 22px;
                """)
            else:
                pill.setStyleSheet(f"""
                    color: {C['text_med']};
                    background-color: white;
                    border: 2px solid {C['border']};
                    border-radius: 21px;
                    padding: 0 22px;
                """)


class _ImageChoiceButton(QPushButton):
    """Tuile "écran" affichant une image (emoji) — neutre / correcte (halo
    vert) / fausse (halo rouge). Look "moniteur" au lieu d'un simple carré
    blanc, cohérent avec le panneau sombre de la page."""

    def __init__(self, emoji, parent=None):
        super().__init__(emoji, parent)
        self.setFixedSize(230, 230)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI Emoji", 76))
        self.reset_style()

    def _style(self, bg, border):
        return f"""
            QPushButton {{
                background-color: {bg};
                border: 4px solid {border};
                border-radius: 30px;
            }}
        """

    def reset_style(self):
        self.setGraphicsEffect(None)
        self.setStyleSheet(self._style("white", ACCENT) + f"""
            QPushButton:hover {{
                border: 3px solid {ACCENT_LIGHT};
                background-color: {_rgba(ACCENT, 25)};
            }}
        """)

    def set_correct(self):
        self.setStyleSheet(self._style(_rgba(C['success'], 60), C['success']))
        self.setGraphicsEffect(_make_shadow(blur=30, dy=0, color=C['success'], alpha=170))

    def set_wrong(self):
        self.setStyleSheet(self._style(_rgba(C['error'], 60), C['error']))
        self.setGraphicsEffect(_make_shadow(blur=30, dy=0, color=C['error'], alpha=170))


class TransmissionPage(BasePage):

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        pixmap = QPixmap(BG_PATH)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        painter.end()
        super().paintEvent(event)

    def _build_page(self):
        layout = self._root_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QWidget(self)
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)
        layout.addWidget(container)

        hdr = self._add_header(show_back=True)
        hdr.set_center("📡 TRANSMISSION")

        self._team_banner = self._add_team_banner()

        self._timer = CircularTimer(duration=TRANSMISSION_VIEW_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Indicateur d'étapes, remplace l'ancien "Round X / N" en texte plat.
        self._stepper = _StageStepper()
        self._root_layout.addSpacing(4)
        self._root_layout.addWidget(self._stepper, 0, Qt.AlignHCenter)
        self._root_layout.addSpacing(10)

        # Panneau "salle de contrôle" : fond sombre + bordure lumineuse,
        # volontairement à l'opposé du verre dépoli clair des autres pages.
        self._content_card = QFrame()
        self._content_card.setObjectName("transCard")
        self._content_card.setStyleSheet(f"""
            QFrame#transCard {{
                background-color: {GLASS_BG};
                border: 2px solid {ACCENT};
                border-radius: 26px;
            }}
        """)
        self._content_card.setGraphicsEffect(
            _make_shadow(blur=36, dy=10, color=ACCENT, alpha=70)
        )

        card_outer = QVBoxLayout()
        card_outer.setContentsMargins(28, 4, 28, 28)
        card_outer.addWidget(self._content_card)
        self._root_layout.addLayout(card_outer, stretch=1)

        card_v = QVBoxLayout(self._content_card)
        card_v.setContentsMargins(32, 24, 32, 30)
        card_v.setSpacing(18)

        # En-tête persistant du panneau (round + équipe), non affecté par
        # _clear_content : seul _content_layout (imbriqué) est vidé à chaque
        # changement d'étape.
        self._section_lbl = QLabel("Round 1 / 6")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        self._section_lbl.setStyleSheet(
            f"color: {C['primary']}; background: transparent; letter-spacing: 1px;"
        )
        card_v.addWidget(self._section_lbl)

        self._content_layout = QVBoxLayout()
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setSpacing(28)
        card_v.addLayout(self._content_layout, stretch=1)

    def _clear_content(self):
        """Point d'entrée public : vide entièrement _content_layout."""
        self._clear_layout(self._content_layout)

    def _clear_layout(self, layout):
        """Vide un layout RÉCURSIVEMENT : widgets directs ET sous-layouts
        (ex. la QGridLayout des 4 images de sélection, ou la ligne de la
        chaîne de relais). hide() immédiat en plus de deleteLater() pour
        éviter tout résidu visible pendant le court délai de destruction."""
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.deleteLater()
                continue

            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout)
                child_layout.setParent(None)

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._rounds = self.mw.tc.get_transmission_slice()
        self._idx = 0
        self.mw.tc.current_match._turn_index = 0
        self._update_scores(self._boxes)
        self._refresh_team_banner()
        self._load_round()

    def _load_round(self):
        if self._idx >= len(self._rounds):
            self.mw.show_page("menu")
            return

        self._round = self._rounds[self._idx]
        self._team  = self.mw.tc.current_team
        self._stage = "view"
        self._refresh_team_banner()
        self._update_scores(self._boxes)
        self._section_lbl.setText(
            f"Round {self._idx + 1} / {len(self._rounds)}  ·  Tour : {self._team.name}"
        )
        self._show_image()

    def _show_image(self):
        self._clear_content()
        self._stage = "view"
        self._stepper.set_stage("view")

        warn = QLabel("👁️ Seul·e le Joueur 1 regarde l'écran — les autres se retournent !")
        warn.setAlignment(Qt.AlignCenter)
        warn.setWordWrap(True)
        warn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        warn.setStyleSheet(f"""
            color: {C['error']};
            background-color: {_rgba(C['error'], 45)};
            border-radius: 14px;
            padding: 10px 20px;
        """)

        screen = QFrame()
        screen.setFixedSize(280, 280)
        screen.setStyleSheet(f"""
            background-color: white;
            border: 4px solid {ACCENT};
            border-radius: 32px;
        """)
        screen_layout = QVBoxLayout(screen)
        img = QLabel(self._round["correct"])
        img.setAlignment(Qt.AlignCenter)
        img.setFont(QFont("Segoe UI Emoji", 120))
        img.setStyleSheet("background: transparent;")
        screen_layout.addWidget(img)

        hint = QLabel("Mémorisez cette image, elle va disparaître.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Segoe UI", 14))
        hint.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        self._content_layout.addWidget(warn)
        self._content_layout.addWidget(screen, alignment=Qt.AlignCenter)
        self._content_layout.addWidget(hint)

        self._timer.reset(TRANSMISSION_VIEW_DURATION)
        self._timer.start()

    def _start_relay(self):
        self._clear_content()
        self._stage = "relay"
        self._stepper.set_stage("relay")

        title = QLabel("📡 Transmission orale en cours...")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        chain = self._build_relay_chain()

        hint = QLabel("Décrivez l'image à voix basse, de joueur en joueur — à l'abri des autres équipes.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setFont(QFont("Segoe UI", 14))
        hint.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        skip_btn = QPushButton("✅  L'équipe a terminé — passer à la sélection")
        skip_btn.setFixedHeight(64)
        skip_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        skip_btn.setCursor(Qt.PointingHandCursor)
        skip_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['success']};
                color: white;
                border-radius: 20px;
                border: none;
                padding: 0 28px;
            }}
            QPushButton:hover {{
                background-color: #219150;
            }}
            QPushButton:pressed {{
                padding-top: 3px;
            }}
        """)
        skip_btn.setGraphicsEffect(_make_shadow(blur=18, dy=5, color=C['success'], alpha=90))
        skip_btn.clicked.connect(self._start_selection)

        self._content_layout.addWidget(title)
        self._content_layout.addLayout(chain)
        self._content_layout.addWidget(hint)
        self._content_layout.addWidget(skip_btn, alignment=Qt.AlignCenter)

        self._timer.reset(TRANSMISSION_RELAY_DURATION)
        self._timer.start()

    def _build_relay_chain(self):
        """Chaîne des 4 joueurs reliés par un "câble" lumineux — remplace
        l'ancien texte "Joueur 1 → Joueur 2 → ..." par un vrai visuel."""
        row = QHBoxLayout()
        row.setSpacing(6)
        row.setAlignment(Qt.AlignCenter)

        for i in range(4):
            circle = QLabel(f"J{i + 1}")
            circle.setFixedSize(72, 72)
            circle.setAlignment(Qt.AlignCenter)
            circle.setFont(QFont("Segoe UI", 17, QFont.Bold))
            circle.setStyleSheet(f"""
                color: white;
                background-color: {ACCENT};
                border-radius: 36px;
            """)
            row.addWidget(circle)
            if i < 3:
                line = QFrame()
                line.setFixedSize(46, 4)
                line.setStyleSheet(f"background-color: {ACCENT_LIGHT}; border-radius: 2px;")
                row.addWidget(line)

        return row

    def _start_selection(self):
        self._timer.stop()
        self._clear_content()
        self._stage = "select"
        self._stepper.set_stage("select")

        title = QLabel(f"🎯 Joueur 4 de {self._team.name}, quelle image avez-vous reçue ?")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 19, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        grid = QGridLayout()
        grid.setSpacing(30)
        self._choice_btns = []
        for i, emoji in enumerate(self._round["choices"]):
            btn = _ImageChoiceButton(emoji)
            btn.clicked.connect(lambda _c, idx=i: self._resolve(idx))
            self._choice_btns.append(btn)
            grid.addWidget(btn, i // 2, i % 2)

        self._content_layout.addWidget(title)
        self._content_layout.addLayout(grid)

        self._timer.reset(TRANSMISSION_SELECT_DURATION)
        self._timer.start()

    def _resolve(self, choice_idx):
        if self._stage != "select":
            return
        self._timer.stop()
        self._apply_feedback(choice_idx)

        correct = (choice_idx == self._round["answer"])
        self.mw.tc.answer("transmission", correct)
        self._update_scores(self._boxes)
        self.mw.tc.next_turn()

        # Laisse voir le résultat (halo vert/rouge) 1.6s, puis lance la pause de 10s
        self._stage = "result"
        QTimer.singleShot(1600, self._start_break)

    def _apply_feedback(self, chosen_idx):
        for i, btn in enumerate(self._choice_btns):
            btn.setEnabled(False)
            if i == self._round["answer"]:
                btn.set_correct()
            elif i == chosen_idx:
                btn.set_wrong()

    def _start_break(self):
        """Pause de 10 secondes entre la fin d'un round et le début du suivant."""
        self._clear_content()
        self._stage = "break"
        self._stepper.set_stage("break")

        icon = QLabel("📡")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 62))
        icon.setStyleSheet(f"color: {_rgba(ACCENT, 140)}; background: transparent;")

        title = QLabel("Pause avant le round suivant")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        hint = QLabel("Préparez-vous, le prochain relais arrive bientôt...")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Segoe UI", 14))
        hint.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        self._content_layout.addWidget(icon)
        self._content_layout.addWidget(title)
        self._content_layout.addWidget(hint)

        self._timer.reset(TRANSMISSION_BREAK_DURATION)
        self._timer.start()

    def _on_timeout(self):
        if self._stage == "view":
            self._start_relay()
        elif self._stage == "relay":
            self._start_selection()
        elif self._stage == "select":
            self._resolve(-1)   # personne n'a choisi à temps
        elif self._stage == "break":
            self._next_round()

    def _next_round(self):
        self._idx += 1
        self._load_round()