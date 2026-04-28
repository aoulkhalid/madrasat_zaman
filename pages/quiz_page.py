"""
pages/quiz_page.py — Quiz Game (mode 2 équipes, 20 questions par match)
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QGridLayout,
                              QProgressBar, QSizePolicy)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, POINTS_CORRECT


class QuizPage(BasePage):

    LETTERS = ["A", "B", "C", "D"]
    BTN_COLORS = ["#2980b9", "#8e44ad", "#27ae60", "#e67e22"]

    def _build_page(self):
        hdr = self._add_header(show_back=True)
        hdr.set_center("QUIZ GAME")

        # ── Bandeau équipe + scores ──
        self._team_banner = self._add_team_banner()
        self._timer = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Progression
        self._progress = QProgressBar()
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(8)
        self._progress.setStyleSheet(
            f"QProgressBar {{ background: {C['border']}; border-radius: 4px; border:none; }}"
            f"QProgressBar::chunk {{ background: {C['primary']}; border-radius: 4px; }}")
        prog_wrap = QFrame()
        prog_wrap.setStyleSheet("background: transparent;")
        pw = QHBoxLayout(prog_wrap)
        pw.setContentsMargins(40, 0, 40, 0)
        pw.addWidget(self._progress)
        self._root_layout.addWidget(prog_wrap)

        # Section label
        self._section_lbl = QLabel("Question 1 / 20")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Arial", 12))
        self._section_lbl.setStyleSheet(f"color: {C['text_light']}; padding: 2px;")
        self._root_layout.addWidget(self._section_lbl)

        # ── Carte de question ──
        self._card = self._make_card()
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(28, 20, 28, 16)
        card_layout.setSpacing(14)

        self._q_lbl = QLabel("")
        self._q_lbl.setAlignment(Qt.AlignCenter)
        self._q_lbl.setFont(QFont("Arial", 15, QFont.Bold))
        self._q_lbl.setWordWrap(True)
        self._q_lbl.setStyleSheet(f"color: {C['text_dark']};")
        card_layout.addWidget(self._q_lbl)

        # Grille 2×2 de boutons réponse
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(10)
        self._ans_btns = []
        for i in range(4):
            btn = self._make_answer_button(i)
            grid.addWidget(btn, i // 2, i % 2)
            self._ans_btns.append(btn)
        card_layout.addWidget(grid_frame)

        wrap = QHBoxLayout()
        wrap.setContentsMargins(36, 0, 36, 14)
        wrap.addWidget(self._card)
        self._root_layout.addLayout(wrap)
        self._root_layout.addStretch()

        # État
        self._questions  = []
        self._q_idx      = 0
        self._answered   = False
        self._auto_timer = QTimer()
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._next_question)

    def _make_answer_button(self, idx: int) -> QPushButton:
        btn = QPushButton(f"  {self.LETTERS[idx]}   ")
        btn.setObjectName("answer_btn")
        btn.setFont(QFont("Arial", 13))
        btn.setMinimumHeight(52)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            f"QPushButton#answer_btn {{ background: white; border: 2px solid {C['border']};"
            f" border-radius: 10px; text-align: left; padding: 10px 14px; }}"
            f"QPushButton#answer_btn:hover:enabled {{ background: #edf4fb;"
            f" border-color: {C['primary_light']}; }}")
        btn.clicked.connect(lambda checked, i=idx: self._on_answer(i))
        btn._idx = idx
        return btn

    # ── Logique ───────────────────────────────────────────────────────────────

    def on_show(self, **kwargs):
        self._questions = self.mw.tc.get_quiz_slice()
        self._q_idx     = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        self._update_scores(self._boxes)
        self._load_question()

    def _load_question(self):
        if self._q_idx >= len(self._questions):
            self.mw.show_page("menu")
            return

        self._answered = False
        q = self._questions[self._q_idx]
        team = self.mw.tc.current_team

        self._refresh_team_banner()
        self._update_scores(self._boxes)

        n   = len(self._questions)
        self._section_lbl.setText(
            f"Question {self._q_idx + 1} / {n}  ·  Tour : {team.name}")
        self._progress.setMaximum(n)
        self._progress.setValue(self._q_idx)

        self._q_lbl.setText(q["q"])

        for i, btn in enumerate(self._ans_btns):
            txt = q["choices"][i] if i < len(q["choices"]) else ""
            btn.setText(f"  {self.LETTERS[i]}   {txt}")
            btn.setEnabled(True)
            btn.setStyleSheet(
                f"QPushButton#answer_btn {{ background: white;"
                f" border: 2px solid {C['border']}; border-radius: 10px;"
                f" text-align: left; padding: 10px 14px; font-size: 13px;"
                f" color: {C['text_dark']}; }}"
                f"QPushButton#answer_btn:hover {{ background: #edf4fb;"
                f" border-color: {C['primary_light']}; }}")

        self._timer.reset(TIMER_DURATION)
        self._timer.start()

    def _on_answer(self, idx: int):
        if self._answered:
            return
        self._answered = True
        self._timer.stop()
        for btn in self._ans_btns:
            btn.setEnabled(False)

        correct_idx = self._questions[self._q_idx]["answer"]
        is_correct  = (idx == correct_idx)

        # Highlights
        self._highlight_btn(idx, correct=is_correct)
        if not is_correct:
            self._highlight_btn(correct_idx, correct=True)

        # Score
        pts = self.mw.tc.answer("quiz", is_correct)
        self._update_scores(self._boxes)

        self._auto_timer.start(1300)

    def _on_timeout(self):
        if not self._answered:
            self._answered = True
            for btn in self._ans_btns:
                btn.setEnabled(False)
            correct = self._questions[self._q_idx]["answer"]
            self._highlight_btn(correct, correct=True)
            self.mw.tc.answer("quiz", False)
            self._update_scores(self._boxes)
            self._auto_timer.start(1100)

    def _highlight_btn(self, idx: int, correct: bool):
        btn = self._ans_btns[idx]
        if correct:
            btn.setStyleSheet(
                f"QPushButton {{ background: {C['success_bg']};"
                f" border: 2px solid {C['success']}; border-radius: 10px;"
                f" text-align: left; padding: 10px 14px; font-size: 13px;"
                f" color: {C['success']}; font-weight: bold; }}")
        else:
            btn.setStyleSheet(
                f"QPushButton {{ background: {C['error_bg']};"
                f" border: 2px solid {C['error']}; border-radius: 10px;"
                f" text-align: left; padding: 10px 14px; font-size: 13px;"
                f" color: {C['error']}; font-weight: bold; }}")

    def _next_question(self):
        self.mw.tc.next_turn()
        self._q_idx += 1
        self._load_question()
