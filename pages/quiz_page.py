"""
pages/quiz_page.py — Quiz Game (mode 2 équipes, 20 questions par match)
Style : carte originale (make_card) + boutons modernes (badge lettre coloré)
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QGridLayout,
                              QProgressBar, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QTimer, QRect
from PyQt5.QtGui     import (QFont, QPainter, QPixmap, QColor,
                              QLinearGradient, QBrush, QPen, QPainterPath)
import os, re
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, POINTS_CORRECT


BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")

# ── Palette ────────────────────────────────────────────────────────────────────
ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"
SUCCESS_COLOR = "#22d3a5"
ERROR_COLOR   = "#f43f5e"
TEXT_WHITE    = "#ffffff"
TEXT_MUTED    = "rgba(255,255,255,180)"
BLUE_NAME     = "#4f8ef7"
_TRANSPARENT  = "background: transparent; border: none; background-color: transparent;"

LETTER_COLORS = ["#4f8ef7", "#a855f7", "#06b6d4", "#f59e0b"]


# ── Helpers ────────────────────────────────────────────────────────────────────
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


def _force_labels_blue(widget):
    for child in widget.findChildren(QLabel):
        child.setStyleSheet(
            child.styleSheet()
            + f" color: {BLUE_NAME}; font-weight: bold; background: transparent;"
        )


# ── Fond : image plein écran + overlay minimal ────────────────────────────────
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
                self._bg_pixmap.scaled(w, h,
                    Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#dde6ed"))
            grad.setColorAt(1.0, QColor("#d6e3ec"))
            p.fillRect(self.rect(), QBrush(grad))

        # Overlay ultra-léger
        p.fillRect(self.rect(), QColor(0, 0, 0, 30))

        # Ligne lumineuse en haut
        lg = QLinearGradient(0, 0, w, 0)
        lg.setColorAt(0.0,  QColor(79, 142, 247, 0))
        lg.setColorAt(0.35, QColor(79, 142, 247, 160))
        lg.setColorAt(0.65, QColor(168, 85, 247, 160))
        lg.setColorAt(1.0,  QColor(168, 85, 247, 0))
        p.setPen(QPen(QBrush(lg), 2))
        p.drawLine(0, 2, w, 2)


# ── Bouton réponse moderne : badge lettre coloré + paintEvent custom ───────────
class _AnswerButton(QPushButton):

    def __init__(self, idx: int, letter: str):
        super().__init__()
        self._idx    = idx
        self._letter = letter
        self._color  = LETTER_COLORS[idx]
        self._state  = "default"
        self._text   = ""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(120)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")

    def set_answer_text(self, txt: str):
        self._text = txt
        self.update()

    def set_state(self, state: str):
        self._state = state
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        radius = 14

        # ── Couleurs selon état ────────────────────────────────────
        if self._state == "correct":
            fill     = QColor(C["success_bg"])
            border_c = QColor(C["success"])
            text_c   = QColor(C["success"])
            badge_c  = QColor(C["success"])
            glow_c   = QColor(34, 211, 165, 50)
        elif self._state == "wrong":
            fill     = QColor(C["error_bg"])
            border_c = QColor(C["error"])
            text_c   = QColor(C["error"])
            badge_c  = QColor(C["error"])
            glow_c   = QColor(244, 63, 94, 45)
        elif self._state == "disabled":
            fill     = QColor(255, 255, 255, 130)
            border_c = QColor(C["border"])
            text_c   = QColor(150, 150, 150)
            badge_c  = QColor(150, 150, 150)
            glow_c   = QColor(0, 0, 0, 0)
        else:
            if self.underMouse() and self.isEnabled():
                fill     = QColor("#edf4fb")
                border_c = QColor(C["primary_light"])
                glow_c   = QColor(79, 142, 247, 30)
            else:
                fill     = QColor(255, 255, 255, 210)
                border_c = QColor(C["border"])
                glow_c   = QColor(0, 0, 0, 0)
            text_c  = QColor(C["text_dark"])
            badge_c = QColor(self._color)

        # Halo
        if glow_c.alpha() > 0:
            glow_path = QPainterPath()
            glow_path.addRoundedRect(-3, -3, r.width()+6, r.height()+6, radius+3, radius+3)
            p.fillPath(glow_path, QBrush(glow_c))

        # Fond bouton
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), radius, radius)
        p.fillPath(path, QBrush(fill))

        # Bordure
        p.setPen(QPen(border_c, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width()-2, r.height()-2, radius, radius)

        # Badge lettre (cercle coloré)
        badge_size = 56
        badge_x    = 22
        badge_y    = (r.height() - badge_size) // 2
        badge_rect = QRect(badge_x, badge_y, badge_size, badge_size)
        badge_fill = QColor(badge_c); badge_fill.setAlpha(28)
        p.setBrush(QBrush(badge_fill))
        p.setPen(QPen(badge_c, 1.5))
        p.drawEllipse(badge_rect)
        p.setPen(QPen(badge_c))
        p.setFont(QFont("Segoe UI", 20, QFont.Bold))
        p.drawText(badge_rect, Qt.AlignCenter, self._letter)

        # Texte réponse
        tx = badge_x + badge_size + 20
        p.setPen(QPen(text_c))
        p.setFont(QFont("Segoe UI", 22))
        p.drawText(QRect(tx, 0, r.width()-tx-12, r.height()),
                   Qt.AlignVCenter | Qt.TextWordWrap, self._text)

    def enterEvent(self, e):
        super().enterEvent(e); self.update()
    def leaveEvent(self, e):
        super().leaveEvent(e); self.update()


# ── Page principale ────────────────────────────────────────────────────────────
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
        _force_labels_blue(hdr)

        # ── Bandeau équipe ────────────────────────────────────────
        self._team_banner = self._add_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)

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
                    _force_labels_blue(w)

        # ── Barre de progression ──────────────────────────────────
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
            f"QProgressBar {{ background: {C['border']}; border-radius:4px; border:none; }}"
            f"QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {ACCENT_BLUE}, stop:1 {ACCENT_PURPLE}); border-radius:4px; }}"
        )
        prog_v.addWidget(self._progress)
        self._root_layout.addWidget(prog_container)

        # ── Carte ORIGINALE (make_card) ───────────────────────────
        self._card = self._make_card()
        self._card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 215);
                border-radius: 22px;
            }
        """)
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(44, 10, 44, 10)
        card_layout.setSpacing(0)

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

        # Grille 2×2 — boutons MODERNES
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(18)
        self._ans_btns: list[_AnswerButton] = []
        for i in range(4):
            btn = _AnswerButton(i, self.LETTERS[i])
            btn.clicked.connect(lambda checked, idx=i: self._on_answer(idx))
            grid.addWidget(btn, i // 2, i % 2)
            self._ans_btns.append(btn)
        card_layout.addWidget(grid_frame)

        card_layout.addStretch(1)

        wrap = QHBoxLayout()
        wrap.setContentsMargins(36, 2, 36, 2)
        wrap.addWidget(self._card)
        self._root_layout.addLayout(wrap, stretch=1)

        # État
        self._questions  = []
        self._q_idx      = 0
        self._answered   = False
        self._auto_timer = QTimer()
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._next_question)

    # ── Logique ───────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._questions = self.mw.tc.get_quiz_slice()
        self._q_idx     = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
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
        _force_labels_blue(self._team_banner)
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
            btn.set_answer_text(txt)
            btn.set_state("default")
            btn.setEnabled(True)

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

        for i, btn in enumerate(self._ans_btns):
            if i == correct_idx:
                btn.set_state("correct")
            elif i == idx and not is_correct:
                btn.set_state("wrong")
            else:
                btn.set_state("disabled")

        self.mw.tc.answer("quiz", is_correct)
        self._update_scores(self._boxes)
        self._auto_timer.start(1300)

    def _on_timeout(self):
        if not self._answered:
            self._answered = True
            for i, btn in enumerate(self._ans_btns):
                btn.setEnabled(False)
            correct = self._questions[self._q_idx]["answer"]
            for i, btn in enumerate(self._ans_btns):
                btn.set_state("correct" if i == correct else "disabled")
            self.mw.tc.answer("quiz", False)
            self._update_scores(self._boxes)
            self._auto_timer.start(1100)

    def _next_question(self):
        self.mw.tc.next_turn()
        self._q_idx += 1
        self._load_question()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())