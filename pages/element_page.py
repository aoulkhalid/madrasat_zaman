"""
pages/element_page.py — Jeu des Éléments
QCM : deviner le résultat de la combinaison de deux éléments.
Même logique que le Quiz : alternance par équipe, +5 pts / 0 pt, chrono 35s.
Bonne réponse -> vert, mauvaise réponse cliquée -> rouge.
"""

import os

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QGridLayout
)

from PyQt5.QtCore import (
    Qt,
    QTimer
)

from PyQt5.QtGui import (
    QFont,
    QPainter,
    QPixmap
)

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION

# Charger directement les 30 questions
from games.element_data import ALL_COMBOS


# ═════════════════════════════════════════════════════════════════════════════
# BACKGROUND IMAGE
# ═════════════════════════════════════════════════════════════════════════════

BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png"
    )
).replace("\\", "/")


LETTERS = [
    "A",
    "B",
    "C",
    "D"
]


LETTER_COLORS = [
    "#4f8ef7",
    "#a855f7",
    "#06b6d4",
    "#f59e0b"
]


class _ChoiceButton(QPushButton):
    """
    Bouton de réponse — peut passer en état neutre /
    correct (vert) / faux (rouge).
    """

    def __init__(
        self,
        letter,
        color,
        parent=None
    ):

        super().__init__(
            parent
        )

        self._letter = letter

        self._color = color

        self.setFixedHeight(
            64
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold
            )
        )

        self.reset_style()

    def _style(
        self,
        bg,
        fg,
        border
    ):

        return f"""

            QPushButton {{

                background-color: {bg};

                color: {fg};

                border: 2px solid {border};

                border-radius: 14px;

                text-align: left;

                padding-left: 18px;

            }}

        """

    def reset_style(
        self
    ):

        """
        État neutre avant réponse.
        """

        self.setStyleSheet(

            self._style(

                "white",

                C['text_dark'],

                self._color

            )

            + f"""

                QPushButton:hover {{

                    background-color: {self._color};

                    color: white;

                }}

            """

        )

    def set_correct(
        self
    ):

        """
        Bonne réponse -> vert.
        """

        self.setStyleSheet(

            self._style(

                C['success'],

                "white",

                C['success']

            )

        )

    def set_wrong(
        self
    ):

        """
        Mauvaise réponse choisie -> rouge.
        """

        self.setStyleSheet(

            self._style(

                C['error'],

                "white",

                C['error']

            )

        )

    def set_faded(
        self
    ):

        """
        Ni correcte ni choisie -> grisée, désactivée.
        """

        self.setStyleSheet(

            self._style(

                "#eeeeee",

                "#999999",

                "#cccccc"

            )

        )


class ElementPage(
    BasePage
):

    # ═════════════════════════════════════════════════════════════════════════
    # BACKGROUND IMAGE
    # ═════════════════════════════════════════════════════════════════════════

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        pixmap = QPixmap(
            BG_PATH
        )

        if not pixmap.isNull():

            scaled = pixmap.scaled(

                self.size(),

                Qt.KeepAspectRatioByExpanding,

                Qt.SmoothTransformation

            )

            x = (

                self.width()

                - scaled.width()

            ) // 2

            y = (

                self.height()

                - scaled.height()

            ) // 2

            painter.drawPixmap(

                x,

                y,

                scaled

            )

        painter.end()

        super().paintEvent(
            event
        )

    # ═════════════════════════════════════════════════════════════════════════
    # BUILD PAGE
    # ═════════════════════════════════════════════════════════════════════════

    def _build_page(
        self
    ):

        layout = self._root_layout

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )

        container = QWidget(
            self
        )

        # Transparent pour laisser apparaître background2.png
        container.setStyleSheet(
            "background: transparent;"
        )

        c_layout = QVBoxLayout(
            container
        )

        c_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        c_layout.setSpacing(
            0
        )

        layout.addWidget(
            container
        )

        # Header
        hdr = self._add_header(
            show_back=True
        )

        hdr.set_center(
            "JEU DES ÉLÉMENTS"
        )

        # Bandeau équipe
        self._team_banner = self._add_team_banner()

        # Timer + scoreboard
        self._timer = CircularTimer(
            duration=TIMER_DURATION,
            size=88
        )

        self._timer.timeout.connect(
            self._on_timeout
        )

        self._boxes = self._build_scoreboard(
            self._timer
        )

        # Compteur
        self._section_lbl = QLabel(
            "Combinaison 1 / 30"
        )

        self._section_lbl.setAlignment(
            Qt.AlignCenter
        )

        self._section_lbl.setFont(
            QFont(
                "Segoe UI",
                11
            )
        )

        self._section_lbl.setStyleSheet(
            f"""

                color: {C['text_light']};

                background: transparent;

            """
        )

        self._root_layout.addWidget(
            self._section_lbl
        )

        # Carte combinaison
        card = QFrame()

        card.setStyleSheet(
            f"""

                QFrame {{

                    background-color: white;

                    border-radius: 18px;

                    border: 1px solid {C['border']};

                }}

            """
        )

        card_layout = QVBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            30,
            24,
            30,
            24
        )

        card_layout.setSpacing(
            20
        )

        self._combo_lbl = QLabel(
            "🔥 Feu  +  💧 Eau  =  ?"
        )

        self._combo_lbl.setAlignment(
            Qt.AlignCenter
        )

        self._combo_lbl.setFont(
            QFont(
                "Segoe UI",
                26,
                QFont.Bold
            )
        )

        self._combo_lbl.setStyleSheet(
            f"""

                color: {C['primary']};

                background: transparent;

            """
        )

        card_layout.addWidget(
            self._combo_lbl
        )

        grid = QGridLayout()

        grid.setSpacing(
            14
        )

        self._choice_btns = []

        for i in range(
            4
        ):

            btn = _ChoiceButton(

                LETTERS[i],

                LETTER_COLORS[i]

            )

            btn.clicked.connect(

                lambda _c, idx=i:

                self._validate(
                    idx
                )

            )

            self._choice_btns.append(
                btn
            )

            grid.addWidget(

                btn,

                i // 2,

                i % 2

            )

        card_layout.addLayout(
            grid
        )

        wrap = QHBoxLayout()

        wrap.setContentsMargins(
            60,
            10,
            60,
            10
        )

        wrap.addWidget(
            card
        )

        self._root_layout.addLayout(
            wrap,
            stretch=1
        )

    # ═════════════════════════════════════════════════════════════════════════
    # CYCLE DE VIE
    # ═════════════════════════════════════════════════════════════════════════

    def on_show(
        self,
        **kwargs
    ):

        # ================================================================
        # IMPORTANT :
        # Avant : get_element_slice() -> seulement 6 questions
        # Maintenant : ALL_COMBOS -> les 30 questions complètes
        # ================================================================

        self._combos = ALL_COMBOS.copy()

        self._idx = 0

        self.mw.tc.current_match._turn_index = 0

        self._refresh_team_banner()

        self._update_scores(
            self._boxes
        )

        self._load_combo()

    # ═════════════════════════════════════════════════════════════════════════
    # LOAD COMBINATION
    # ═════════════════════════════════════════════════════════════════════════

    def _load_combo(
        self
    ):

        if self._idx >= len(
            self._combos
        ):

            self.mw.show_page(
                "menu"
            )

            return

        self._answered = False

        combo = self._combos[
            self._idx
        ]

        team = self.mw.tc.current_team

        self._refresh_team_banner()

        self._update_scores(
            self._boxes
        )

        self._section_lbl.setText(

            f"Combinaison {self._idx + 1} / "
            f"{len(self._combos)}  ·  "
            f"Tour : {team.name}"

        )

        self._combo_lbl.setText(

            f"{combo['a']}  +  "
            f"{combo['b']}  =  ?"

        )

        for i, btn in enumerate(
            self._choice_btns
        ):

            btn.setText(

                f"  {LETTERS[i]}.  "
                f"{combo['choices'][i]}"

            )

            btn.setEnabled(
                True
            )

            btn.reset_style()

        self._timer.reset(
            TIMER_DURATION
        )

        self._timer.start()

    # ═════════════════════════════════════════════════════════════════════════
    # FEEDBACK
    # ═════════════════════════════════════════════════════════════════════════

    def _apply_feedback(
        self,
        chosen_idx,
        correct_idx
    ):

        """
        Colore les boutons :
        vert = bonne réponse,
        rouge = mauvaise réponse choisie.
        """

        for i, btn in enumerate(
            self._choice_btns
        ):

            btn.setEnabled(
                False
            )

            if i == correct_idx:

                btn.set_correct()

            elif i == chosen_idx:

                btn.set_wrong()

            else:

                btn.set_faded()

    # ═════════════════════════════════════════════════════════════════════════
    # VALIDATE ANSWER
    # ═════════════════════════════════════════════════════════════════════════

    def _validate(
        self,
        choice_idx
    ):

        if self._answered:

            return

        self._answered = True

        self._timer.stop()

        combo = self._combos[
            self._idx
        ]

        correct = (

            choice_idx

            == combo["answer"]

        )

        self._apply_feedback(

            choice_idx,

            combo["answer"]

        )

        self.mw.tc.answer(
            "element",
            correct
        )

        self._update_scores(
            self._boxes
        )

        self.mw.tc.next_turn()

        QTimer.singleShot(

            1400,

            self._next_combo

        )

    # ═════════════════════════════════════════════════════════════════════════
    # TIMEOUT
    # ═════════════════════════════════════════════════════════════════════════

    def _on_timeout(
        self
    ):

        if self._answered:

            return

        self._answered = True

        combo = self._combos[
            self._idx
        ]

        self._apply_feedback(

            chosen_idx=-1,

            correct_idx=combo["answer"]

        )

        self.mw.tc.answer(

            "element",

            False

        )

        self._update_scores(
            self._boxes
        )

        self.mw.tc.next_turn()

        QTimer.singleShot(

            1400,

            self._next_combo

        )

    # ═════════════════════════════════════════════════════════════════════════
    # NEXT COMBINATION
    # ═════════════════════════════════════════════════════════════════════════

    def _next_combo(
        self
    ):

        self._idx += 1

        self._load_combo()