"""
pages/quiz_page.py — Quiz Game (mode 2 équipes, 20 questions par match)
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QGridLayout,
                              QProgressBar, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QPainter, QPixmap, QColor, QLinearGradient, QBrush
import os, re
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, POINTS_CORRECT


BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background.png")
_TRANSPARENT = "background: transparent; border: none; background-color: transparent;"


def _make_transparent(widget):
    widget.setStyleSheet(_TRANSPARENT)
    widget.setAttribute(Qt.WA_TranslucentBackground, True)
    for child in widget.findChildren(QWidget):
        if isinstance(child, QLabel):
            old   = child.styleSheet()
            clean = re.sub(r'background(-color)?\s*:[^;]+;?', '', old)
            child.setStyleSheet(clean + " background: transparent;")
        else:
            child.setStyleSheet(_TRANSPARENT)
            child.setAttribute(Qt.WA_TranslucentBackground, True)


class _Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = QPixmap(BG_PATH)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        if not self._bg_pixmap.isNull():
            p.drawPixmap(0, 0,
                self._bg_pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#dde6ed"))
            grad.setColorAt(1.0, QColor("#d6e3ec"))
            p.fillRect(self.rect(), QBrush(grad))


class QuizPage(BasePage):

    LETTERS = ["A", "B", "C", "D"]

    def _build_page(self):
        layout = self._root_layout
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Fond
        self._bg = _Background(self)
        self._bg.setGeometry(self.rect())
        self._bg.lower()

        container = QWidget(self)
        container.setAttribute(Qt.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)
        layout.addWidget(container)

        # ── Header ────────────────────────────────────────────────
        hdr = self._add_header(show_back=True)
        hdr.set_center("QUIZ GAME")
        _make_transparent(hdr)

        # ── Bandeau équipe ────────────────────────────────────────
        self._team_banner = self._add_team_banner()
        _make_transparent(self._team_banner)

        # ── Timer + Scoreboard ────────────────────────────────────
        self._timer = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)
        for i in range(self._root_layout.count()):
            item = self._root_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, (QFrame, QWidget)):
                    _make_transparent(w)

        # ── Barre de progression + label (juste sous le scoreboard)
        prog_container = QFrame()
        prog_container.setStyleSheet("background: transparent;")
        prog_container.setFixedHeight(30)
        prog_v = QVBoxLayout(prog_container)
        prog_v.setContentsMargins(50, 2, 50, 2)
        prog_v.setSpacing(3)

        self._section_lbl = QLabel("Question 1 / 20")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Segoe UI", 11))
        self._section_lbl.setStyleSheet(
            f"color: {C['text_light']}; background: transparent;"
        )
        prog_v.addWidget(self._section_lbl)

        self._progress = QProgressBar()
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(7)
        self._progress.setStyleSheet(
            f"QProgressBar {{ background: {C['border']}; border-radius: 4px; border:none; }}"
            f"QProgressBar::chunk {{ background: {C['primary']}; border-radius: 4px; }}"
        )
        prog_v.addWidget(self._progress)
        self._root_layout.addWidget(prog_container)

        # ── Carte de question — prend tout l'espace restant ───────
        self._card = self._make_card()
        self._card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 215);
                border-radius: 22px;
            }
        """)
        # La carte s'étire verticalement pour remplir jusqu'aux symboles
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(44, 10, 44, 10)
        card_layout.setSpacing(0)

        # Stretch haut — centre verticalement le contenu dans la carte
        card_layout.addStretch(1)

        # Texte de la question
        self._q_lbl = QLabel("")
        self._q_lbl.setAlignment(Qt.AlignCenter)
        self._q_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._q_lbl.setWordWrap(True)
        self._q_lbl.setStyleSheet(
            f"color: {C['text_dark']}; background: transparent;"
        )
        card_layout.addWidget(self._q_lbl)

        card_layout.addSpacing(18)

        # Grille 2×2
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(16)
        self._ans_btns = []
        for i in range(4):
            btn = self._make_answer_button(i)
            grid.addWidget(btn, i // 2, i % 2)
            self._ans_btns.append(btn)
        card_layout.addWidget(grid_frame)

        # Stretch bas
        card_layout.addStretch(1)

        # Marges horizontales de la carte = identiques au screenshot
        wrap = QHBoxLayout()
        wrap.setContentsMargins(36, 2, 36, 2)
        wrap.addWidget(self._card)

        # Ce layout prend tout l'espace disponible
        self._root_layout.addLayout(wrap, stretch=1)

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
        btn.setFont(QFont("Segoe UI", 16))
        btn.setMinimumHeight(76)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            f"QPushButton#answer_btn {{"
            f"  background: rgba(255,255,255,210);"
            f"  border: 2px solid {C['border']};"
            f"  border-radius: 14px;"
            f"  text-align: left;"
            f"  padding: 14px 20px;"
            f"  color: {C['text_dark']};"
            f"}}"
            f"QPushButton#answer_btn:hover:enabled {{"
            f"  background: #edf4fb;"
            f"  border-color: {C['primary_light']};"
            f"}}"
        )
        btn.clicked.connect(lambda checked, i=idx: self._on_answer(i))
        btn._idx = idx
        return btn

    # ── Logique ───────────────────────────────────────────────────

    def on_show(self, **kwargs):
        self._questions = self.mw.tc.get_quiz_slice()
        self._q_idx     = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        self._update_scores(self._boxes)
        self._load_question()

    def _load_question(self):
        if self._q_idx >= len(self._questions):
            self.mw.show_page("menu")
            return

        self._answered = False
        q    = self._questions[self._q_idx]
        team = self.mw.tc.current_team

        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        self._update_scores(self._boxes)

        n = len(self._questions)
        self._section_lbl.setText(
            f"Question {self._q_idx + 1} / {n}   ·   Tour : {team.name}"
        )
        self._progress.setMaximum(n)
        self._progress.setValue(self._q_idx + 1)
        self._q_lbl.setText(q["q"])

        for i, btn in enumerate(self._ans_btns):
            txt = q["choices"][i] if i < len(q["choices"]) else ""
            btn.setText(f"  {self.LETTERS[i]}   {txt}")
            btn.setEnabled(True)
            btn.setStyleSheet(
                f"QPushButton#answer_btn {{"
                f"  background: rgba(255,255,255,210);"
                f"  border: 2px solid {C['border']};"
                f"  border-radius: 14px;"
                f"  text-align: left;"
                f"  padding: 14px 20px;"
                f"  font-size: 16px;"
                f"  color: {C['text_dark']};"
                f"}}"
                f"QPushButton#answer_btn:hover {{"
                f"  background: #edf4fb;"
                f"  border-color: {C['primary_light']};"
                f"}}"
            )

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
        self._highlight_btn(idx, correct=is_correct)
        if not is_correct:
            self._highlight_btn(correct_idx, correct=True)

        self.mw.tc.answer("quiz", is_correct)
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
                f" border: 2px solid {C['success']}; border-radius: 14px;"
                f" text-align: left; padding: 14px 20px; font-size: 16px;"
                f" color: {C['success']}; font-weight: bold; }}"
            )
        else:
            btn.setStyleSheet(
                f"QPushButton {{ background: {C['error_bg']};"
                f" border: 2px solid {C['error']}; border-radius: 14px;"
                f" text-align: left; padding: 14px 20px; font-size: 16px;"
                f" color: {C['error']}; font-weight: bold; }}"
            )

    def _next_question(self):
        self.mw.tc.next_turn()
        self._q_idx += 1
        self._load_question()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())