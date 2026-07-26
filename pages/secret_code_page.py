"""
pages/secret_code_page.py — Le Code Secret (Mastermind à 2 équipes)

Phase 1 : chaque équipe entre secrètement son code à 4 chiffres (masqué).
Phase 2 : tours alternés — chaque équipe tente de deviner le code adverse
          et reçoit des indices (bonne position / bon chiffre mal placé).

Dépend de :
  - config.py       → constantes SECRET_CODE_*
  - controllers/tournament_controller.py → méthode award_points_to()
  - models/match.py → méthode record_answer_for()
"""
import re
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QFrame, QWidget)
from PyQt5.QtCore    import Qt, QRegExp, QTimer
from PyQt5.QtGui     import QFont, QRegExpValidator

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, SECRET_CODE_LENGTH, SECRET_CODE_MAX_TRIES,
                     SECRET_CODE_TURN_DURATION, SECRET_CODE_POINTS_WIN,
                     SECRET_CODE_BONUS_FAST, SECRET_CODE_BONUS_PER_TRY)


class _DigitBox(QLineEdit):
    """Case à un seul chiffre (0-9), masquée ou non."""

    def __init__(self, masked=False, parent=None):
        super().__init__(parent)
        self.setMaxLength(1)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(56, 64)
        self.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.setValidator(QRegExpValidator(QRegExp(r"[0-9]")))
        if masked:
            self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 2px solid {C['border']};
                border-radius: 12px;
                color: {C['primary']};
            }}
            QLineEdit:focus {{ border: 2px solid {C['primary_light']}; }}
        """)


class SecretCodePage(BasePage):

    # ── Construction (une seule fois) ───────────────────────────────────────
    def _build_page(self):
        layout = self._root_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QWidget(self)
        container.setStyleSheet(f"background-color: {C['bg']};")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)
        layout.addWidget(container)

        # Header
        hdr = self._add_header(show_back=True)
        hdr.set_center("LE CODE SECRET")

        # Bandeau équipe (masqué pendant la phase de création)
        self._team_banner = self._add_team_banner()

        # Timer + scoreboard
        self._timer = CircularTimer(duration=SECRET_CODE_TURN_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Zone de contenu dynamique (recréée à chaque étape)
        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setSpacing(18)
        self._root_layout.addWidget(self._content, stretch=1)

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._match = self.mw.tc.current_match
        self._match._turn_index = 0
        self._match.secret_codes = {}     # team_key -> "1234"
        self._attempts = {self._match.team1.key: 0, self._match.team2.key: 0}
        self._finished = False

        self._team_banner.setVisible(False)
        self._update_scores(self._boxes)
        self._timer.stop()

        self._start_setup(self._match.team1)

    def _clear_content(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    # ── Phase 1 : création des codes ────────────────────────────────────────
    def _start_setup(self, team):
        self._clear_content()
        self._timer.stop()
        self._setup_team = team

        title = QLabel(f"{team.name}, entrez votre code secret")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        warn = QLabel("⚠️ Les autres équipes doivent regarder ailleurs !")
        warn.setAlignment(Qt.AlignCenter)
        warn.setFont(QFont("Segoe UI", 13))
        warn.setStyleSheet(f"color: {C['error']}; background: transparent;")

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(14)
        self._setup_boxes = []
        for i in range(SECRET_CODE_LENGTH):
            box = _DigitBox(masked=True)
            box.textChanged.connect(lambda _t, idx=i: self._auto_advance(self._setup_boxes, idx))
            self._setup_boxes.append(box)
            row.addWidget(box)

        confirm = QPushButton("VALIDER LE CODE")
        confirm.setFixedSize(260, 52)
        confirm.setFont(QFont("Segoe UI", 13, QFont.Bold))
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['primary']}; color: white;
                border-radius: 14px;
            }}
            QPushButton:hover {{ background-color: {C['primary_light']}; }}
        """)
        confirm.clicked.connect(self._validate_setup)

        self._setup_error = QLabel("")
        self._setup_error.setAlignment(Qt.AlignCenter)
        self._setup_error.setStyleSheet(f"color: {C['error']}; background: transparent;")

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(warn)
        self._content_layout.addLayout(row)
        self._content_layout.addWidget(confirm, alignment=Qt.AlignCenter)
        self._content_layout.addWidget(self._setup_error)

        self._setup_boxes[0].setFocus()

    def _auto_advance(self, boxes, idx):
        if boxes[idx].text() and idx + 1 < len(boxes):
            boxes[idx + 1].setFocus()

    def _validate_setup(self):
        digits = "".join(b.text() for b in self._setup_boxes)
        if len(digits) != SECRET_CODE_LENGTH or not digits.isdigit():
            self._setup_error.setText("Veuillez saisir 4 chiffres.")
            return

        self._match.secret_codes[self._setup_team.key] = digits

        if self._setup_team.key == self._match.team1.key:
            self._start_setup(self._match.team2)
        else:
            self._start_guessing()

    # ── Phase 2 : devinette ──────────────────────────────────────────────────
    def _start_guessing(self):
        self._team_banner.setVisible(True)
        self._refresh_team_banner()
        self._load_turn(feedback="")

    def _load_turn(self, feedback=""):
        self._clear_content()
        self._refresh_team_banner()
        self._update_scores(self._boxes)

        team = self.mw.tc.current_team
        remaining = SECRET_CODE_MAX_TRIES - self._attempts[team.key]

        title = QLabel(f"{team.name} — Devinez le code adverse")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        tries_lbl = QLabel(f"Essais restants : {remaining}")
        tries_lbl.setAlignment(Qt.AlignCenter)
        tries_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        tries_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(14)
        self._guess_boxes = []
        for i in range(SECRET_CODE_LENGTH):
            box = _DigitBox(masked=False)
            box.textChanged.connect(lambda _t, idx=i: self._auto_advance(self._guess_boxes, idx))
            self._guess_boxes.append(box)
            row.addWidget(box)

        submit = QPushButton("VALIDER LA PROPOSITION")
        submit.setFixedSize(280, 52)
        submit.setFont(QFont("Segoe UI", 13, QFont.Bold))
        submit.setCursor(Qt.PointingHandCursor)
        submit.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['accent']}; color: white;
                border-radius: 14px;
            }}
            QPushButton:hover {{ background-color: #1abc9c; }}
        """)
        submit.clicked.connect(self._submit_guess)

        self._feedback_lbl = QLabel(feedback)
        self._feedback_lbl.setAlignment(Qt.AlignCenter)
        self._feedback_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self._feedback_lbl.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(tries_lbl)
        self._content_layout.addLayout(row)
        self._content_layout.addWidget(submit, alignment=Qt.AlignCenter)
        self._content_layout.addWidget(self._feedback_lbl)

        self._guess_boxes[0].setFocus()
        self._timer.reset(SECRET_CODE_TURN_DURATION)
        self._timer.start()

    @staticmethod
    def _bulls_cows(secret: str, guess: str):
        bulls = sum(1 for a, b in zip(secret, guess) if a == b)
        common = sum(min(secret.count(d), guess.count(d)) for d in set(guess))
        cows = common - bulls
        return bulls, cows

    def _submit_guess(self):
        if self._finished:
            return
        guess = "".join(b.text() for b in self._guess_boxes)
        if len(guess) != SECRET_CODE_LENGTH or not guess.isdigit():
            self._feedback_lbl.setText("Entrez 4 chiffres.")
            return
        self._timer.stop()
        self._resolve_guess(guess)

    def _on_timeout(self):
        if self._finished:
            return
        self._resolve_guess("")   # temps écoulé = tentative ratée (0/0)

    def _resolve_guess(self, guess: str):
        team     = self.mw.tc.current_team
        opponent = self._match.other_team
        secret   = self._match.secret_codes[opponent.key]

        self._attempts[team.key] += 1

        if guess and len(guess) == SECRET_CODE_LENGTH:
            bulls, cows = self._bulls_cows(secret, guess)
        else:
            bulls, cows = 0, 0

        if bulls == SECRET_CODE_LENGTH:
            self._win(team, self._attempts[team.key])
            return

        remaining_mine  = SECRET_CODE_MAX_TRIES - self._attempts[team.key]
        remaining_other = SECRET_CODE_MAX_TRIES - self._attempts[opponent.key]
        if remaining_mine <= 0 and remaining_other <= 0:
            self._draw()
            return

        self.mw.tc.next_turn()
        self._load_turn(
            feedback=f"🟢 Bonne position : {bulls}   🟡 Bon chiffre mal placé : {cows}"
        )

    def _win(self, team, attempts_used):
        self._finished = True
        self._timer.stop()

        pts = SECRET_CODE_POINTS_WIN
        if attempts_used < 3:
            pts += SECRET_CODE_BONUS_FAST
        pts += (SECRET_CODE_MAX_TRIES - attempts_used) * SECRET_CODE_BONUS_PER_TRY

        self.mw.tc.award_points_to(team, "secret_code", pts)
        self._update_scores(self._boxes)

        self._clear_content()
        msg = QLabel(f"🎉 Code trouvé !\n{team.name} remporte cette manche (+{pts} pts)")
        msg.setAlignment(Qt.AlignCenter)
        msg.setFont(QFont("Segoe UI", 20, QFont.Bold))
        msg.setStyleSheet(f"color: {C['success']}; background: transparent;")
        self._content_layout.addWidget(msg)

        QTimer.singleShot(3000, lambda: self.mw.show_page("menu"))

    def _draw(self):
        self._finished = True
        self._timer.stop()
        self._clear_content()
        msg = QLabel("⏱️ Essais épuisés pour les deux équipes.\nAucun code trouvé — aucune manche remportée.")
        msg.setAlignment(Qt.AlignCenter)
        msg.setFont(QFont("Segoe UI", 18, QFont.Bold))
        msg.setStyleSheet(f"color: {C['warning']}; background: transparent;")
        self._content_layout.addWidget(msg)

        QTimer.singleShot(3000, lambda: self.mw.show_page("menu"))