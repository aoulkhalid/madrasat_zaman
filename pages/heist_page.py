# -*- coding: utf-8 -*-
"""
pages/heist_page.py — Braquage de Banque

Règles :
    - 2 équipes
    - 20 questions par équipe
    - 20 secondes par question
    - Bonne réponse : +5 points
    - Mauvaise réponse : +0
    - Temps écoulé : +0
    - 5 questions = 1 clé
    - 20/20 bonnes réponses = Banque braquée +10 points bonus
"""

import os

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QGraphicsDropShadowEffect,
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QPixmap, QColor

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer

from config import C

from games.heist_data import ALL_MISSIONS


# ============================================================
# CONFIGURATION DU JEU
# ============================================================

HEIST_QUESTION_DURATION = 20
HEIST_QUESTIONS_PER_TEAM = 20
HEIST_QUESTIONS_PER_KEY = 5

HEIST_POINTS_CORRECT = 5
HEIST_POINTS_BANK = 10

HEIST_TOTAL_MISSIONS = 40


# ============================================================
# BACKGROUND
# ============================================================

BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png"
    )
).replace("\\", "/")


# ============================================================
# SHADOW
# ============================================================

def _make_shadow(blur=28, dx=0, dy=8, alpha=90):
    """Petit utilitaire pour les ombres."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    return shadow


# ============================================================
# KEY BADGE
# ============================================================

class _KeyBadge(QFrame):
    """
    Badge d'une clé :

        locked  -> 🔒
        success -> 🔑
        fail    -> ❌
    """

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setFixedSize(150, 100)

        self._title = title
        self._state = "locked"

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(4)

        self._icon_lbl = QLabel("🔒")
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setFont(QFont("Segoe UI", 30))
        self._icon_lbl.setStyleSheet(
            "background: transparent;"
        )

        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        self._title_lbl.setStyleSheet(
            f"color: {C['text_light']}; "
            "background: transparent;"
        )

        self._layout.addWidget(self._icon_lbl)
        self._layout.addWidget(self._title_lbl)

        self.setGraphicsEffect(
            _make_shadow(
                blur=20,
                dy=5,
                alpha=70
            )
        )

        self.set_state("locked")

    def set_state(self, state: str):
        """
        state :
            locked
            success
            fail
        """

        self._state = state

        if state == "success":

            self._icon_lbl.setText("🔑")

            bg = C["success_bg"]
            border = C["success"]

        elif state == "fail":

            self._icon_lbl.setText("❌")

            bg = C["error_bg"]
            border = C["error"]

        else:

            self._icon_lbl.setText("🔒")

            bg = "white"
            border = C["border"]

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 22px;
            }}
            """
        )

    def is_success(self) -> bool:
        return self._state == "success"


# ============================================================
# MAIN PAGE
# ============================================================

class HeistPage(BasePage):

    # ========================================================
    # BACKGROUND
    # ========================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        pixmap = QPixmap(BG_PATH)

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

        super().paintEvent(event)

    # ========================================================
    # BUILD PAGE
    # ========================================================

    def _build_page(self):

        layout = self._root_layout

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(0)

        container = QWidget(self)

        container.setStyleSheet(
            "background: transparent;"
        )

        c_layout = QVBoxLayout(container)

        c_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        c_layout.setSpacing(0)

        layout.addWidget(container)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        hdr = self._add_header(
            show_back=True
        )

        hdr.set_center(
            "🏦 BRAQUAGE DE BANQUE"
        )

        # ----------------------------------------------------
        # TEAM BANNER
        # ----------------------------------------------------

        self._team_banner = (
            self._add_team_banner()
        )

        # ----------------------------------------------------
        # TIMER + SCOREBOARD
        # ----------------------------------------------------

        self._timer = CircularTimer(
            duration=HEIST_QUESTION_DURATION,
            size=110
        )

        self._timer.timeout.connect(
            self._on_timeout
        )

        self._boxes = (
            self._build_scoreboard(
                self._timer
            )
        )

        # ----------------------------------------------------
        # KEYS ROW
        # ----------------------------------------------------

        keys_row = QHBoxLayout()

        keys_row.setAlignment(
            Qt.AlignCenter
        )

        keys_row.setSpacing(22)

        keys_row.setContentsMargins(
            0,
            14,
            0,
            14
        )

        self._key_badges = []

        self._keys_wrap = QWidget()

        self._keys_wrap.setStyleSheet(
            "background: transparent;"
        )

        self._keys_wrap.setLayout(
            keys_row
        )

        self._keys_row_layout = keys_row

        self._root_layout.addWidget(
            self._keys_wrap
        )

        # ----------------------------------------------------
        # CONTENT CARD
        # ----------------------------------------------------

        self._content_card = QFrame()

        self._content_card.setObjectName(
            "heistCard"
        )

        self._content_card.setStyleSheet(
            """
            QFrame#heistCard {
                background-color:
                    rgba(255, 255, 255, 0.90);
                border-radius: 28px;
            }
            """
        )

        self._content_card.setGraphicsEffect(
            _make_shadow(
                blur=36,
                dy=10,
                alpha=80
            )
        )

        card_outer = QVBoxLayout()

        card_outer.setContentsMargins(
            24,
            20,
            24,
            32
        )

        card_outer.addWidget(
            self._content_card
        )

        self._root_layout.addLayout(
            card_outer,
            stretch=1
        )

        self._content_layout = QVBoxLayout(
            self._content_card
        )

        self._content_layout.setAlignment(
            Qt.AlignCenter
        )

        self._content_layout.setContentsMargins(
            36,
            32,
            36,
            32
        )

        self._content_layout.setSpacing(22)

    # ========================================================
    # CLEAR LAYOUT
    # ========================================================

    @staticmethod
    def _clear_layout(layout):

        while layout.count():

            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:

                widget.hide()
                widget.deleteLater()

                continue

            child_layout = item.layout()

            if child_layout is not None:

                HeistPage._clear_layout(
                    child_layout
                )

                child_layout.setParent(None)

    # ========================================================
    # CLEAR CONTENT
    # ========================================================

    def _clear_content(self):

        self._clear_layout(
            self._content_layout
        )

    # ========================================================
    # REBUILD KEYS
    # ========================================================

    def _rebuild_keys_row(self):

        while self._keys_row_layout.count():

            item = (
                self._keys_row_layout.takeAt(0)
            )

            widget = item.widget()

            if widget:

                widget.hide()
                widget.deleteLater()

        self._key_badges = []

        for i in range(4):

            badge = _KeyBadge(
                f"Clé {i + 1}"
            )

            self._key_badges.append(
                badge
            )

            self._keys_row_layout.addWidget(
                badge
            )

    # ========================================================
    # LIFECYCLE
    # ========================================================

    def on_show(self, **kwargs):

        self._match = (
            self.mw.tc.current_match
        )

        # Team 1 commence
        self._match._turn_index = 0

        self._start_attempt(
            self._match.team1,
            team_number=1
        )

    # ========================================================
    # START TEAM ATTEMPT
    # ========================================================

    def _start_attempt(
        self,
        team,
        team_number
    ):

        self._current_attempt_team = team
        self._team_number = team_number

        # ----------------------------------------------------
        # Sélection des 20 questions
        # ----------------------------------------------------

        if team_number == 1:

            start = 0
            end = 20

        else:

            start = 20
            end = 40

        self._missions = (
            ALL_MISSIONS[start:end]
        )

        # Sécurité
        if len(self._missions) != 20:

            raise ValueError(
                "heist_data.py doit contenir "
                "exactement 40 questions."
            )

        # ----------------------------------------------------
        # État
        # ----------------------------------------------------

        self._m_idx = 0

        self._finished = False

        self._mission_locked = False

        # Nombre de bonnes réponses
        self._correct_answers = 0

        # Nombre de questions par clé
        self._key_correct = [
            0,
            0,
            0,
            0
        ]

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self._rebuild_keys_row()

        self._refresh_team_banner()

        self._update_scores(
            self._boxes
        )

        # ----------------------------------------------------
        # Timer
        # ----------------------------------------------------

        self._timer.reset(
            HEIST_QUESTION_DURATION
        )

        self._timer.start()

        # ----------------------------------------------------
        # Première question
        # ----------------------------------------------------

        self._load_mission()

    # ========================================================
    # LOAD QUESTION
    # ========================================================

    def _load_mission(self):

        self._clear_content()

        self._mission_locked = False

        mission = (
            self._missions[self._m_idx]
        )

        # ----------------------------------------------------
        # Numéro
        # ----------------------------------------------------

        counter = QLabel(
            f"Question {self._m_idx + 1} / "
            f"{len(self._missions)}"
        )

        counter.setAlignment(
            Qt.AlignCenter
        )

        counter.setFont(
            QFont(
                "Segoe UI",
                13,
                QFont.DemiBold
            )
        )

        counter.setStyleSheet(
            f"""
            color: {C['text_med']};
            background: transparent;
            letter-spacing: 1px;
            """
        )

        # ----------------------------------------------------
        # Key actuelle
        # ----------------------------------------------------

        key_number = (
            self._m_idx //
            HEIST_QUESTIONS_PER_KEY
        ) + 1

        key_label = QLabel(
            f"🔐 Clé {key_number}"
        )

        key_label.setAlignment(
            Qt.AlignCenter
        )

        key_label.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Bold
            )
        )

        key_label.setStyleSheet(
            f"""
            color: {C['text_med']};
            background: transparent;
            """
        )

        # ----------------------------------------------------
        # Icon
        # ----------------------------------------------------

        icon = QLabel(
            mission["icon"]
        )

        icon.setAlignment(
            Qt.AlignCenter
        )

        icon.setFont(
            QFont(
                "Segoe UI",
                58
            )
        )

        icon.setStyleSheet(
            "background: transparent;"
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = QLabel(
            mission["title"]
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Bold
            )
        )

        title.setStyleSheet(
            f"""
            color: {C['text_light']};
            background: transparent;
            """
        )

        # ----------------------------------------------------
        # Question
        # ----------------------------------------------------

        question = QLabel(
            mission["question"]
        )

        question.setAlignment(
            Qt.AlignCenter
        )

        question.setWordWrap(True)

        question.setFont(
            QFont(
                "Segoe UI",
                29,
                QFont.Bold
            )
        )

        question.setStyleSheet(
            f"""
            color: {C['primary']};
            background: transparent;
            """
        )

        # ----------------------------------------------------
        # Answer
        # ----------------------------------------------------

        self._answer_lbl = QLabel("")

        self._answer_lbl.setAlignment(
            Qt.AlignCenter
        )

        self._answer_lbl.setFont(
            QFont(
                "Segoe UI",
                15,
                QFont.Bold
            )
        )

        self._answer_lbl.setStyleSheet(
            f"""
            color: {C['text_med']};
            background: transparent;
            """
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        btn_row = QHBoxLayout()

        btn_row.setAlignment(
            Qt.AlignCenter
        )

        btn_row.setSpacing(26)

        # ====================================================
        # CORRECT
        # ====================================================

        self._ok_btn = QPushButton(
            "✅  Correct"
        )

        self._ok_btn.setFixedSize(
            220,
            70
        )

        self._ok_btn.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Bold
            )
        )

        self._ok_btn.setCursor(
            Qt.PointingHandCursor
        )

        self._ok_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color:
                    {C['success']};
                color: white;
                border-radius: 20px;
                border: none;
            }}

            QPushButton:hover {{
                background-color:
                    #219150;
            }}

            QPushButton:pressed {{
                padding-top: 3px;
            }}

            QPushButton:disabled {{
                background-color:
                    #a9dcc1;
            }}
            """
        )

        self._ok_btn.setGraphicsEffect(
            _make_shadow(
                blur=18,
                dy=6,
                alpha=60
            )
        )

        self._ok_btn.clicked.connect(
            lambda:
                self._validate(True)
        )

        # ====================================================
        # INCORRECT
        # ====================================================

        self._no_btn = QPushButton(
            "❌  Incorrect"
        )

        self._no_btn.setFixedSize(
            220,
            70
        )

        self._no_btn.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Bold
            )
        )

        self._no_btn.setCursor(
            Qt.PointingHandCursor
        )

        self._no_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color:
                    {C['error']};
                color: white;
                border-radius: 20px;
                border: none;
            }}

            QPushButton:hover {{
                background-color:
                    #c0392b;
            }}

            QPushButton:pressed {{
                padding-top: 3px;
            }}

            QPushButton:disabled {{
                background-color:
                    #eab2ac;
            }}
            """
        )

        self._no_btn.setGraphicsEffect(
            _make_shadow(
                blur=18,
                dy=6,
                alpha=60
            )
        )

        self._no_btn.clicked.connect(
            lambda:
                self._validate(False)
        )

        btn_row.addWidget(
            self._ok_btn
        )

        btn_row.addWidget(
            self._no_btn
        )

        # ----------------------------------------------------
        # ADD TO CONTENT
        # ----------------------------------------------------

        self._content_layout.addWidget(
            counter
        )

        self._content_layout.addWidget(
            key_label
        )

        self._content_layout.addWidget(
            icon
        )

        self._content_layout.addWidget(
            title
        )

        self._content_layout.addWidget(
            question
        )

        self._content_layout.addLayout(
            btn_row
        )

        self._content_layout.addWidget(
            self._answer_lbl
        )

        # ----------------------------------------------------
        # Restart timer for THIS question
        # ----------------------------------------------------

        self._timer.reset(
            HEIST_QUESTION_DURATION
        )

        self._timer.start()

    # ========================================================
    # VALIDATE ANSWER
    # ========================================================

    def _validate(
        self,
        is_correct: bool
    ):

        if self._finished:
            return

        if self._mission_locked:
            return

        self._mission_locked = True

        # ----------------------------------------------------
        # Stop timer for current question
        # ----------------------------------------------------

        self._timer.stop()

        # ----------------------------------------------------
        # Disable buttons
        # ----------------------------------------------------

        self._ok_btn.setEnabled(
            False
        )

        self._no_btn.setEnabled(
            False
        )

        # ----------------------------------------------------
        # Current mission
        # ----------------------------------------------------

        mission = (
            self._missions[self._m_idx]
        )

        # ----------------------------------------------------
        # Current key
        # ----------------------------------------------------

        key_index = (
            self._m_idx //
            HEIST_QUESTIONS_PER_KEY
        )

        # ----------------------------------------------------
        # CORRECT
        # ----------------------------------------------------

        if is_correct:

            self._correct_answers += 1

            self._key_correct[
                key_index
            ] += 1

            # +5 immédiatement
            self.mw.tc.award_points_to(
                self._current_attempt_team,
                "heist",
                HEIST_POINTS_CORRECT
            )

            self._answer_lbl.setText(
                f"✅ Correct ! "
                f"+{HEIST_POINTS_CORRECT} points"
                f"<br>"
                f"Réponse : "
                f"{mission['answer']}"
            )

        # ----------------------------------------------------
        # INCORRECT
        # ----------------------------------------------------

        else:

            self._answer_lbl.setText(
                f"❌ Incorrect"
                f"<br>"
                f"Réponse : "
                f"{mission['answer']}"
            )

        # ----------------------------------------------------
        # Update score
        # ----------------------------------------------------

        self._update_scores(
            self._boxes
        )

        # ----------------------------------------------------
        # Check key completion
        #
        # Une clé est verte uniquement si ses 5 questions
        # sont toutes correctes.
        # ----------------------------------------------------

        questions_in_key = (
            (
                self._m_idx %
                HEIST_QUESTIONS_PER_KEY
            ) + 1
        )

        if (
            questions_in_key ==
            HEIST_QUESTIONS_PER_KEY
        ):

            if (
                self._key_correct[key_index]
                ==
                HEIST_QUESTIONS_PER_KEY
            ):

                self._key_badges[
                    key_index
                ].set_state(
                    "success"
                )

            else:

                self._key_badges[
                    key_index
                ].set_state(
                    "fail"
                )

        # ----------------------------------------------------
        # Next question
        # ----------------------------------------------------

        QTimer.singleShot(
            1100,
            self._next_mission
        )

    # ========================================================
    # TIMEOUT
    # ========================================================

    def _on_timeout(self):

        if self._finished:
            return

        if self._mission_locked:
            return

        # ----------------------------------------------------
        # Temps écoulé = mauvaise réponse
        # ----------------------------------------------------

        self._validate(False)

    # ========================================================
    # NEXT QUESTION
    # ========================================================

    def _next_mission(self):

        if self._finished:
            return

        self._m_idx += 1

        # ----------------------------------------------------
        # End of 20 questions
        # ----------------------------------------------------

        if (
            self._m_idx >=
            len(self._missions)
        ):

            self._finish_attempt()

        else:

            self._load_mission()

    # ========================================================
    # FINISH TEAM ATTEMPT
    # ========================================================

    def _finish_attempt(self):

        if self._finished:
            return

        self._finished = True

        self._mission_locked = True

        self._timer.stop()

        self._clear_content()

        team = (
            self._current_attempt_team
        )

        # ----------------------------------------------------
        # BANK BRAQUÉE ?
        #
        # 20/20 correct
        # ----------------------------------------------------

        bank_braqued = (
            self._correct_answers ==
            HEIST_QUESTIONS_PER_TEAM
        )

        bonus = 0

        if bank_braqued:

            bonus = HEIST_POINTS_BANK

            self.mw.tc.award_points_to(
                team,
                "heist",
                HEIST_POINTS_BANK
            )

        # ----------------------------------------------------
        # Update score
        # ----------------------------------------------------

        self._update_scores(
            self._boxes
        )

        # ----------------------------------------------------
        # Message
        # ----------------------------------------------------

        if bank_braqued:

            msg = QLabel(
                f"💰 COFFRE BRAQUÉ !\n"
                f"{team.name}\n\n"
                f"20 / 20 bonnes réponses\n"
                f"+{bonus} pts bonus"
            )

            msg.setStyleSheet(
                f"""
                color: {C['success']};
                background: transparent;
                """
            )

        else:

            msg = QLabel(
                f"🚨 ALARME !\n"
                f"{team.name}\n\n"
                f"{self._correct_answers} / "
                f"{HEIST_QUESTIONS_PER_TEAM} "
                f"bonnes réponses\n"
                f"Banque non braquée"
            )

            msg.setStyleSheet(
                f"""
                color: {C['error']};
                background: transparent;
                """
            )

        msg.setAlignment(
            Qt.AlignCenter
        )

        msg.setFont(
            QFont(
                "Segoe UI",
                27,
                QFont.Bold
            )
        )

        self._content_layout.addWidget(
            msg
        )

        # ----------------------------------------------------
        # Go to next team
        # ----------------------------------------------------

        QTimer.singleShot(
            2600,
            self._after_attempt
        )

    # ========================================================
    # AFTER TEAM
    # ========================================================

    def _after_attempt(self):

        # ----------------------------------------------------
        # Team 1 finished
        # → Team 2
        # ----------------------------------------------------

        if self._team_number == 1:

            self._match._turn_index = 1

            self._start_attempt(
                self._match.team2,
                team_number=2
            )

        # ----------------------------------------------------
        # Team 2 finished
        # → Menu
        # ----------------------------------------------------

        else:

            self.mw.show_page(
                "menu"
            )