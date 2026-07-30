# pages/secret_code_page.py

import os

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QWidget,
    QSizePolicy,
    QGraphicsDropShadowEffect
)

from PyQt5.QtCore import (
    Qt,
    QRegExp,
    QTimer
)

from PyQt5.QtGui import (
    QFont,
    QRegExpValidator,
    QPainter,
    QPixmap,
    QColor
)

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer

from config import (
    C,
    SECRET_CODE_LENGTH,
    SECRET_CODE_MAX_TRIES,
    SECRET_CODE_TURN_DURATION,
    SECRET_CODE_POINTS_WIN,
    SECRET_CODE_BONUS_FAST,
    SECRET_CODE_BONUS_PER_TRY
)


# ═════════════════════════════════════════════════════════════════════════════
# BACKGROUND
# ═════════════════════════════════════════════════════════════════════════════

BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png"
    )
)

BG_PATH = BG_PATH.replace("\\", "/")


# ═════════════════════════════════════════════════════════════════════════════
# COLORS
# ═════════════════════════════════════════════════════════════════════════════

CYAN = "#00D9FF"
CYAN_DARK = "#009BB8"
CYAN_LIGHT = "#66ECFF"

WHITE = "#FFFFFF"
LIGHT_GREY = "#F4F7FA"
GREY = "#B7C0CC"
DARK_GREY = "#5F6B78"
DARK = "#18232F"

GREEN = "#19C98B"
YELLOW = "#F4B942"
RED = "#FF5C6C"


# ═════════════════════════════════════════════════════════════════════════════
# SHADOW
# ═════════════════════════════════════════════════════════════════════════════

def _add_shadow(
    widget,
    blur=35,
    y_offset=10,
    opacity=90
):

    shadow = QGraphicsDropShadowEffect(
        widget
    )

    shadow.setBlurRadius(
        blur
    )

    shadow.setOffset(
        0,
        y_offset
    )

    shadow.setColor(
        QColor(
            0,
            0,
            0,
            opacity
        )
    )

    widget.setGraphicsEffect(
        shadow
    )


# ═════════════════════════════════════════════════════════════════════════════
# DIGIT BOX
# ═════════════════════════════════════════════════════════════════════════════

class _DigitBox(QLineEdit):

    def __init__(
        self,
        masked=False,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setMaxLength(
            1
        )

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setFixedSize(
            110,
            120
        )

        self.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed
        )

        self.setFont(
            QFont(
                "Segoe UI",
                48,
                QFont.Bold
            )
        )

        self.setValidator(
            QRegExpValidator(
                QRegExp(
                    r"[0-9]"
                )
            )
        )

        if masked:

            self.setEchoMode(
                QLineEdit.Password
            )

        self.setStyleSheet(
            f"""

            QLineEdit {{

                background-color: rgba(255, 255, 255, 235);

                border: 3px solid #D9E1E8;

                border-radius: 24px;

                color: {DARK};

                padding: 0px;

                selection-background-color: {CYAN};

            }}

            QLineEdit:hover {{

                background-color: rgba(255, 255, 255, 250);

                border: 3px solid {CYAN_LIGHT};

            }}

            QLineEdit:focus {{

                background-color: rgba(244, 253, 255, 245);

                border: 4px solid {CYAN};

                color: {DARK};

            }}

        """
        )


# ═════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ═════════════════════════════════════════════════════════════════════════════

class SecretCodePage(
    BasePage
):

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

        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        container = QWidget(
            self
        )

        container.setStyleSheet(
            "background: transparent;"
        )

        container_layout = QVBoxLayout(
            container
        )

        container_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        container_layout.setSpacing(
            0
        )

        layout.addWidget(
            container
        )

        # ═════════════════════════════════════════════════════════════════════
        # HEADER
        # ═════════════════════════════════════════════════════════════════════

        header = self._add_header(
            show_back=True
        )

        header.set_center(
            "🔐  LE CODE SECRET"
        )

        # ═════════════════════════════════════════════════════════════════════
        # TEAM BANNER
        # ═════════════════════════════════════════════════════════════════════

        self._team_banner = self._add_team_banner()

        # ═════════════════════════════════════════════════════════════════════
        # TIMER
        # ═════════════════════════════════════════════════════════════════════

        self._timer = CircularTimer(
            duration=SECRET_CODE_TURN_DURATION,
            size=110
        )

        self._timer.timeout.connect(
            self._on_timeout
        )

        # ═════════════════════════════════════════════════════════════════════
        # SCOREBOARD
        # ═════════════════════════════════════════════════════════════════════

        self._boxes = self._build_scoreboard(
            self._timer
        )

        # ═════════════════════════════════════════════════════════════════════
        # MAIN CARD
        # ═════════════════════════════════════════════════════════════════════

        self._content = QFrame()

        self._content.setMinimumWidth(
            750
        )

        self._content.setMaximumWidth(
            1250
        )

        self._content.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self._content.setStyleSheet(
            """

            QFrame {

                background-color: rgba(255, 255, 255, 215);

                border: 1px solid rgba(255, 255, 255, 220);

                border-radius: 32px;

            }

        """
        )

        _add_shadow(
            self._content,
            blur=45,
            y_offset=16,
            opacity=100
        )

        # ═════════════════════════════════════════════════════════════════════
        # IMPORTANT : CONTENEUR CENTRAL
        # ═════════════════════════════════════════════════════════════════════

        content_outer_layout = QHBoxLayout(
            self._content
        )

        content_outer_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        content_outer_layout.setSpacing(
            0
        )

        # Espace gauche
        content_outer_layout.addStretch(
            1
        )

        # Conteneur central
        self._content_center = QWidget()

        self._content_center.setMinimumWidth(
            650
        )

        self._content_center.setMaximumWidth(
            700
        )

        self._content_center.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self._content_center.setStyleSheet(
            """

            QWidget {

                background: transparent;

            }

        """
        )

        # Layout réel du contenu
        self._content_layout = QVBoxLayout(
            self._content_center
        )

        self._content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self._content_layout.setSpacing(
            18
        )

        self._content_layout.setAlignment(
            Qt.AlignCenter
        )

        content_outer_layout.addWidget(
            self._content_center
        )

        # Espace droit
        content_outer_layout.addStretch(
            1
        )

        # Ajout de la grande carte — CENTRÉE horizontalement dans la page.
        # Sans "alignment=Qt.AlignHCenter", un QVBoxLayout ancre par défaut
        # un widget à largeur plafonnée (maximumWidth) sur la GAUCHE plutôt
        # que de le centrer — c'est ce qui causait la carte collée à gauche.
        self._root_layout.addWidget(
            self._content,
            stretch=1,
            alignment=Qt.AlignHCenter
        )

    # ═════════════════════════════════════════════════════════════════════════
    # BACKGROUND
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
    # SHOW PAGE
    # ═════════════════════════════════════════════════════════════════════════

    def on_show(
        self,
        **kwargs
    ):

        self._match = self.mw.tc.current_match

        self._match._turn_index = 0

        self._match.secret_codes = {}

        self._attempts = {

            self._match.team1.key: 0,

            self._match.team2.key: 0

        }

        self._finished = False

        self._team_banner.setVisible(
            False
        )

        self._update_scores(
            self._boxes
        )

        self._timer.stop()

        self._start_setup(
            self._match.team1
        )

    # ═════════════════════════════════════════════════════════════════════════
    # CLEAR CONTENT
    # ═════════════════════════════════════════════════════════════════════════

    def _clear_content(
        self
    ):

        while self._content_layout.count():

            item = self._content_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

    # ═════════════════════════════════════════════════════════════════════════
    # TITLE
    # ═════════════════════════════════════════════════════════════════════════

    def _create_title(
        self,
        text
    ):

        title = QLabel(
            text
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                28,
                QFont.Bold
            )
        )

        title.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK};

                background: transparent;

                padding: 6px;

            }}

        """
        )

        return title

    # ═════════════════════════════════════════════════════════════════════════
    # SUBTITLE
    # ═════════════════════════════════════════════════════════════════════════

    def _create_subtitle(
        self,
        text
    ):

        subtitle = QLabel(
            text
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setFont(
            QFont(
                "Segoe UI",
                14
            )
        )

        subtitle.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK_GREY};

                background: transparent;

                padding: 5px;

            }}

        """
        )

        return subtitle

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION LABEL
    # ═════════════════════════════════════════════════════════════════════════

    def _create_section_label(
        self,
        text
    ):

        label = QLabel(
            text
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Bold
            )
        )

        label.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK_GREY};

                background: transparent;

                letter-spacing: 1px;

                padding: 4px;

            }}

        """
        )

        return label

    # ═════════════════════════════════════════════════════════════════════════
    # BUTTON
    # ═════════════════════════════════════════════════════════════════════════

    def _create_button(
        self,
        text,
        background,
        width=320
    ):

        button = QPushButton(
            text
        )

        button.setFixedSize(
            width,
            64
        )

        button.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold
            )
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setStyleSheet(
            f"""

            QPushButton {{

                background-color: {background};

                color: white;

                border: none;

                border-radius: 20px;

                padding: 12px 25px;

            }}

            QPushButton:hover {{

                background-color: {CYAN_LIGHT};

                color: {DARK};

            }}

            QPushButton:pressed {{

                background-color: {CYAN_DARK};

            }}

        """
        )

        _add_shadow(
            button,
            blur=25,
            y_offset=7,
            opacity=95
        )

        return button

    # ═════════════════════════════════════════════════════════════════════════
    # INFO BADGE
    # ═════════════════════════════════════════════════════════════════════════

    def _create_info_badge(
        self,
        text,
        accent=CYAN
    ):

        badge = QLabel(
            text
        )

        badge.setAlignment(
            Qt.AlignCenter
        )

        badge.setFont(
            QFont(
                "Segoe UI",
                13,
                QFont.Bold
            )
        )

        badge.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK};

                background-color: rgba(243, 247, 249, 210);

                border: 2px solid {accent};

                border-radius: 16px;

                padding: 12px 25px;

            }}

        """
        )

        return badge

    # ═════════════════════════════════════════════════════════════════════════
    # FEEDBACK
    # ═════════════════════════════════════════════════════════════════════════

    def _create_feedback_card(
        self,
        text
    ):

        feedback = QLabel(
            text
        )

        feedback.setAlignment(
            Qt.AlignCenter
        )

        feedback.setWordWrap(
            True
        )

        feedback.setMinimumHeight(
            65
        )

        feedback.setFont(
            QFont(
                "Segoe UI",
                13,
                QFont.Bold
            )
        )

        feedback.setStyleSheet(
            """

            QLabel {

                color: #18232F;

                background-color: rgba(245, 248, 250, 210);

                border: 1px solid #DCE5EA;

                border-radius: 18px;

                padding: 14px 22px;

            }

        """
        )

        return feedback

    # ═════════════════════════════════════════════════════════════════════════
    # CREATE BOXES CONTAINER
    # ═════════════════════════════════════════════════════════════════════════

    def _create_boxes_container(
        self,
        masked=False
    ):

        boxes_container = QWidget()

        boxes_container.setFixedHeight(
            140
        )

        boxes_container.setMinimumWidth(
            600
        )

        boxes_container.setStyleSheet(
            "background: transparent;"
        )

        boxes_layout = QHBoxLayout(
            boxes_container
        )

        boxes_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        boxes_layout.setSpacing(
            18
        )

        boxes_layout.setAlignment(
            Qt.AlignCenter
        )

        boxes = []

        for i in range(
            SECRET_CODE_LENGTH
        ):

            box = _DigitBox(
                masked=masked
            )

            box.textChanged.connect(

                lambda _text, idx=i:

                self._auto_advance(
                    boxes,
                    idx
                )

            )

            boxes.append(
                box
            )

            boxes_layout.addWidget(
                box
            )

        return boxes_container, boxes

    # ═════════════════════════════════════════════════════════════════════════
    # SECRET CODE CREATION
    # ═════════════════════════════════════════════════════════════════════════

    def _start_setup(
        self,
        team
    ):

        self._clear_content()

        self._timer.stop()

        self._setup_team = team

        title = self._create_title(
            f"🔒  {team.name}"
        )

        subtitle = self._create_subtitle(
            "Créez votre code secret composé de 4 chiffres"
        )

        security = QLabel(
            "🔐  CODE CONFIDENTIEL  •  NE LE MONTREZ PAS À L'ÉQUIPE ADVERSE"
        )

        security.setAlignment(
            Qt.AlignCenter
        )

        security.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold
            )
        )

        security.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK};

                background-color: rgba(234, 251, 255, 200);

                border: 2px solid {CYAN};

                border-radius: 15px;

                padding: 13px 20px;

            }}

        """
        )

        section_label = self._create_section_label(
            "CHOISISSEZ VOTRE CODE"
        )

        boxes_container, self._setup_boxes = self._create_boxes_container(
            masked=True
        )

        confirm = self._create_button(

            "🔐  VALIDER LE CODE",

            CYAN_DARK,

            340

        )

        confirm.clicked.connect(
            self._validate_setup
        )

        self._setup_error = QLabel(
            ""
        )

        self._setup_error.setAlignment(
            Qt.AlignCenter
        )

        self._setup_error.setStyleSheet(
            f"""

            QLabel {{

                color: {RED};

                background: transparent;

                font-weight: bold;

                padding: 8px;

            }}

        """
        )

        self._content_layout.addWidget(
            title,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addWidget(
            subtitle,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            10
        )

        self._content_layout.addWidget(
            security,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            18
        )

        self._content_layout.addWidget(
            section_label,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addWidget(
            boxes_container,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            24
        )

        self._content_layout.addWidget(
            confirm,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addWidget(
            self._setup_error,
            0,
            Qt.AlignCenter
        )

        self._setup_boxes[0].setFocus()

    # ═════════════════════════════════════════════════════════════════════════
    # AUTO ADVANCE
    # ═════════════════════════════════════════════════════════════════════════

    def _auto_advance(
        self,
        boxes,
        idx
    ):

        if (

            boxes[idx].text()

            and idx + 1 < len(boxes)

        ):

            boxes[idx + 1].setFocus()

    # ═════════════════════════════════════════════════════════════════════════
    # VALIDATE SECRET CODE
    # ═════════════════════════════════════════════════════════════════════════

    def _validate_setup(
        self
    ):

        digits = "".join(

            box.text()

            for box in self._setup_boxes

        )

        if (

            len(digits) != SECRET_CODE_LENGTH

            or not digits.isdigit()

        ):

            self._setup_error.setText(

                "⚠️ Veuillez saisir 4 chiffres."

            )

            return

        self._match.secret_codes[

            self._setup_team.key

        ] = digits

        if (

            self._setup_team.key

            == self._match.team1.key

        ):

            self._start_setup(

                self._match.team2

            )

        else:

            self._start_guessing()

    # ═════════════════════════════════════════════════════════════════════════
    # START GUESSING
    # ═════════════════════════════════════════════════════════════════════════

    def _start_guessing(
        self
    ):

        self._team_banner.setVisible(
            True
        )

        self._refresh_team_banner()

        self._load_turn(
            feedback=""
        )

    # ═════════════════════════════════════════════════════════════════════════
    # LOAD TURN
    # ═════════════════════════════════════════════════════════════════════════

    def _load_turn(
        self,
        feedback=""
    ):

        self._clear_content()

        self._refresh_team_banner()

        self._update_scores(
            self._boxes
        )

        team = self.mw.tc.current_team

        remaining = (

            SECRET_CODE_MAX_TRIES

            - self._attempts[team.key]

        )

        title = self._create_title(
            f"🎯  {team.name}"
        )

        subtitle = self._create_subtitle(
            "Déchiffrez le code secret de l'équipe adverse"
        )

        turn_badge = self._create_info_badge(
            "⚡  TOUR ACTUEL — À VOUS DE JOUER",
            CYAN
        )

        tries_lbl = self._create_info_badge(
            f"🧩  ESSAIS RESTANTS : {remaining}",
            CYAN_DARK
        )

        section_label = self._create_section_label(
            "ENTREZ VOTRE PROPOSITION"
        )

        boxes_container, self._guess_boxes = self._create_boxes_container(
            masked=False
        )

        submit = self._create_button(

            "🎯  VALIDER LA PROPOSITION",

            CYAN_DARK,

            360

        )

        submit.clicked.connect(
            self._submit_guess
        )

        self._feedback_lbl = self._create_feedback_card(
            feedback
        )

        self._content_layout.addWidget(
            title,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addWidget(
            subtitle,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            8
        )

        self._content_layout.addWidget(
            turn_badge,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            8
        )

        self._content_layout.addWidget(
            tries_lbl,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            20
        )

        self._content_layout.addWidget(
            section_label,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addWidget(
            boxes_container,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addSpacing(
            24
        )

        self._content_layout.addWidget(
            submit,
            0,
            Qt.AlignCenter
        )

        self._content_layout.addWidget(
            self._feedback_lbl,
            0,
            Qt.AlignCenter
        )

        self._guess_boxes[0].setFocus()

        self._timer.reset(
            SECRET_CODE_TURN_DURATION
        )

        self._timer.start()

    # ═════════════════════════════════════════════════════════════════════════
    # BULLS & COWS
    # ═════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _bulls_cows(
        secret: str,
        guess: str
    ):

        bulls = sum(

            1

            for a, b in zip(

                secret,

                guess

            )

            if a == b

        )

        common = sum(

            min(

                secret.count(d),

                guess.count(d)

            )

            for d in set(
                guess
            )

        )

        cows = common - bulls

        return bulls, cows

    # ═════════════════════════════════════════════════════════════════════════
    # SUBMIT GUESS
    # ═════════════════════════════════════════════════════════════════════════

    def _submit_guess(
        self
    ):

        if self._finished:

            return

        guess = "".join(

            box.text()

            for box in self._guess_boxes

        )

        if (

            len(guess) != SECRET_CODE_LENGTH

            or not guess.isdigit()

        ):

            self._feedback_lbl.setText(

                "⚠️ Entrez exactement 4 chiffres."

            )

            return

        self._timer.stop()

        self._resolve_guess(
            guess
        )

    # ═════════════════════════════════════════════════════════════════════════
    # TIMEOUT
    # ═════════════════════════════════════════════════════════════════════════

    def _on_timeout(
        self
    ):

        if self._finished:

            return

        self._resolve_guess(
            ""
        )

    # ═════════════════════════════════════════════════════════════════════════
    # RESOLVE GUESS
    # ═════════════════════════════════════════════════════════════════════════

    def _resolve_guess(
        self,
        guess: str
    ):

        team = self.mw.tc.current_team

        opponent = self._match.other_team

        secret = self._match.secret_codes[
            opponent.key
        ]

        self._attempts[
            team.key
        ] += 1

        if (

            guess

            and len(guess) == SECRET_CODE_LENGTH

        ):

            bulls, cows = self._bulls_cows(

                secret,

                guess

            )

        else:

            bulls, cows = 0, 0

        if bulls == SECRET_CODE_LENGTH:

            self._win(

                team,

                self._attempts[team.key]

            )

            return

        remaining_mine = (

            SECRET_CODE_MAX_TRIES

            - self._attempts[team.key]

        )

        remaining_other = (

            SECRET_CODE_MAX_TRIES

            - self._attempts[opponent.key]

        )

        if (

            remaining_mine <= 0

            and remaining_other <= 0

        ):

            self._draw()

            return

        self.mw.tc.next_turn()

        self._load_turn(

            feedback=(

                f"🟢  Bonne position : {bulls}    "

                f"🟡  Bon chiffre mal placé : {cows}"

            )

        )

    # ═════════════════════════════════════════════════════════════════════════
    # WIN
    # ═════════════════════════════════════════════════════════════════════════

    def _win(
        self,
        team,
        attempts_used
    ):

        self._finished = True

        self._timer.stop()

        pts = SECRET_CODE_POINTS_WIN

        if attempts_used < 3:

            pts += SECRET_CODE_BONUS_FAST

        pts += (

            SECRET_CODE_MAX_TRIES

            - attempts_used

        ) * SECRET_CODE_BONUS_PER_TRY

        self.mw.tc.award_points_to(

            team,

            "secret_code",

            pts

        )

        self._update_scores(
            self._boxes
        )

        self._clear_content()

        victory_card = QFrame()

        victory_card.setStyleSheet(
            f"""

            QFrame {{

                background-color: rgba(242, 255, 251, 225);

                border: 3px solid {GREEN};

                border-radius: 28px;

            }}

        """
        )

        _add_shadow(
            victory_card,
            blur=40,
            y_offset=12,
            opacity=110
        )

        victory_layout = QVBoxLayout(
            victory_card
        )

        victory_layout.setContentsMargins(
            60,
            45,
            60,
            45
        )

        victory_layout.setSpacing(
            16
        )

        title = QLabel(
            "🏆  CODE DÉCHIFFRÉ !"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                32,
                QFont.Bold
            )
        )

        title.setStyleSheet(
            f"""

            QLabel {{

                color: {GREEN};

                background: transparent;

            }}

        """
        )

        winner = QLabel(
            f"{team.name} REMPORTE LA MANCHE"
        )

        winner.setAlignment(
            Qt.AlignCenter
        )

        winner.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Bold
            )
        )

        winner.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK};

                background: transparent;

            }}

        """
        )

        points = QLabel(
            f"+{pts} POINTS"
        )

        points.setAlignment(
            Qt.AlignCenter
        )

        points.setFont(
            QFont(
                "Segoe UI",
                26,
                QFont.Bold
            )
        )

        points.setStyleSheet(
            f"""

            QLabel {{

                color: {CYAN_DARK};

                background: transparent;

            }}

        """
        )

        victory_layout.addWidget(
            title
        )

        victory_layout.addWidget(
            winner
        )

        victory_layout.addWidget(
            points
        )

        self._content_layout.addWidget(
            victory_card,
            0,
            Qt.AlignCenter
        )

        QTimer.singleShot(

            3000,

            lambda:

            self.mw.show_page(
                "menu"
            )

        )

    # ═════════════════════════════════════════════════════════════════════════
    # DRAW
    # ═════════════════════════════════════════════════════════════════════════

    def _draw(
        self
    ):

        self._finished = True

        self._timer.stop()

        self._clear_content()

        draw_card = QFrame()

        draw_card.setStyleSheet(
            f"""

            QFrame {{

                background-color: rgba(255, 253, 245, 225);

                border: 3px solid {YELLOW};

                border-radius: 28px;

            }}

        """
        )

        _add_shadow(
            draw_card,
            blur=40,
            y_offset=12,
            opacity=110
        )

        draw_layout = QVBoxLayout(
            draw_card
        )

        draw_layout.setContentsMargins(
            60,
            45,
            60,
            45
        )

        draw_layout.setSpacing(
            16
        )

        title = QLabel(
            "⏱️  MISSION NON RÉSOLUE"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                29,
                QFont.Bold
            )
        )

        title.setStyleSheet(
            f"""

            QLabel {{

                color: {YELLOW};

                background: transparent;

            }}

        """
        )

        description = QLabel(
            "Les deux équipes ont épuisé leurs essais."
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        description.setFont(
            QFont(
                "Segoe UI",
                15
            )
        )

        description.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK_GREY};

                background: transparent;

            }}

        """
        )

        result = QLabel(
            "🤝  MATCH NUL"
        )

        result.setAlignment(
            Qt.AlignCenter
        )

        result.setFont(
            QFont(
                "Segoe UI",
                24,
                QFont.Bold
            )
        )

        result.setStyleSheet(
            f"""

            QLabel {{

                color: {DARK};

                background: transparent;

            }}

        """
        )

        draw_layout.addWidget(
            title
        )

        draw_layout.addWidget(
            description
        )

        draw_layout.addWidget(
            result
        )

        self._content_layout.addWidget(
            draw_card,
            0,
            Qt.AlignCenter
        )

        QTimer.singleShot(

            3000,

            lambda:

            self.mw.show_page(
                "menu"
            )

        )