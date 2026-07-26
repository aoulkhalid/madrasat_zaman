"""
pages/cyber_page.py — Cyber Investigation (version 1 PC, sans téléphones)

Chaque équipe tente, à son tour, de résoudre l'enquête en élucidant 4 indices
dans le temps imparti. L'équipe déduit la réponse à l'oral, le/la responsable
clique ✅ Correct ou ❌ Incorrect pour valider chaque indice.

4/4 indices résolus avant la fin du chrono -> enquête résolue (+40 pts)
Sinon (temps écoulé ou indice raté en fin de tentative) -> enquête non résolue (-10 pts)
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, CYBER_DURATION, CYBER_CLUES_PER_ATTEMPT,
                     CYBER_POINTS_SUCCESS, CYBER_POINTS_FAIL)


class _ClueBadge(QFrame):
    """Un badge indice : non résolu (gris) / résolu (vert) / raté (rouge)."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 80)
        self._solved = False
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(2)

        self._icon_lbl = QLabel("🔍")
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setFont(QFont("Segoe UI", 22))
        self._icon_lbl.setStyleSheet("background: transparent;")

        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self._title_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        self._layout.addWidget(self._icon_lbl)
        self._layout.addWidget(self._title_lbl)
        self.set_state("pending")

    def set_state(self, state: str):
        """state: 'pending' | 'solved' | 'failed'"""
        if state == "solved":
            self._icon_lbl.setText("✅")
            self._solved = True
            bg, border = C['success_bg'], C['success']
        elif state == "failed":
            self._icon_lbl.setText("❌")
            self._solved = False
            bg, border = C['error_bg'], C['error']
        else:
            self._icon_lbl.setText("🔍")
            self._solved = False
            bg, border = "white", C['border']
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 14px;
            }}
        """)

    def is_solved(self) -> bool:
        return self._solved


class CyberPage(BasePage):

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
        hdr.set_center("🕵️ CYBER INVESTIGATION")

        # Bandeau équipe
        self._team_banner = self._add_team_banner()

        # Timer + scoreboard
        self._timer = CircularTimer(duration=CYBER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Rangée des indices
        clues_row = QHBoxLayout()
        clues_row.setAlignment(Qt.AlignCenter)
        clues_row.setSpacing(16)
        clues_row.setContentsMargins(0, 10, 0, 10)
        self._clue_badges = []
        self._clues_wrap = QWidget()
        self._clues_wrap.setLayout(clues_row)
        self._clues_row_layout = clues_row
        self._root_layout.addWidget(self._clues_wrap)

        # Zone de contenu dynamique
        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setSpacing(16)
        self._root_layout.addWidget(self._content, stretch=1)

    def _clear_content(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _rebuild_clues_row(self):
        while self._clues_row_layout.count():
            item = self._clues_row_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._clue_badges = []
        for c in self._clues:
            badge = _ClueBadge(c["title"])
            self._clue_badges.append(badge)
            self._clues_row_layout.addWidget(badge)

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._match = self.mw.tc.current_match
        self._match._turn_index = 0
        self._start_attempt(self._match.team1, attempt_offset=0)

    def _start_attempt(self, team, attempt_offset):
        self._current_attempt_team = team
        self._attempt_offset = attempt_offset
        self._clues = self.mw.tc.get_cyber_slice(attempt_offset)
        self._c_idx = 0
        self._finished = False

        self._rebuild_clues_row()
        self._refresh_team_banner()
        self._update_scores(self._boxes)

        self._timer.reset(CYBER_DURATION)
        self._timer.start()
        self._load_clue()

    def _load_clue(self):
        self._clear_content()
        clue = self._clues[self._c_idx]

        counter = QLabel(f"Indice {self._c_idx + 1} / {len(self._clues)}")
        counter.setAlignment(Qt.AlignCenter)
        counter.setFont(QFont("Segoe UI", 11))
        counter.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        icon = QLabel(clue["icon"])
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 36))
        icon.setStyleSheet("background: transparent;")

        title = QLabel(clue["title"])
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        situation = QLabel(clue["clue"])
        situation.setAlignment(Qt.AlignCenter)
        situation.setWordWrap(True)
        situation.setFont(QFont("Consolas", 13))
        situation.setStyleSheet(f"""
            color: {C['text_dark']}; background-color: white;
            border: 1px solid {C['border']}; border-radius: 12px;
            padding: 12px 20px;
        """)

        question = QLabel(clue["question"])
        question.setAlignment(Qt.AlignCenter)
        question.setWordWrap(True)
        question.setFont(QFont("Segoe UI", 19, QFont.Bold))
        question.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        self._answer_lbl = QLabel("")
        self._answer_lbl.setAlignment(Qt.AlignCenter)
        self._answer_lbl.setWordWrap(True)
        self._answer_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self._answer_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(20)

        ok_btn = QPushButton("✅  Correct")
        ok_btn.setFixedSize(180, 56)
        ok_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {C['success']}; color: white; border-radius: 14px; }}
            QPushButton:hover {{ background-color: #219150; }}
        """)
        ok_btn.clicked.connect(lambda: self._validate(True))

        no_btn = QPushButton("❌  Incorrect")
        no_btn.setFixedSize(180, 56)
        no_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        no_btn.setCursor(Qt.PointingHandCursor)
        no_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {C['error']}; color: white; border-radius: 14px; }}
            QPushButton:hover {{ background-color: #c0392b; }}
        """)
        no_btn.clicked.connect(lambda: self._validate(False))

        btn_row.addWidget(ok_btn)
        btn_row.addWidget(no_btn)

        self._content_layout.addWidget(counter)
        self._content_layout.addWidget(icon)
        self._content_layout.addWidget(title)
        self._content_layout.addWidget(situation)
        self._content_layout.addWidget(question)
        self._content_layout.addLayout(btn_row)
        self._content_layout.addWidget(self._answer_lbl)

    def _validate(self, is_correct: bool):
        if self._finished:
            return
        clue = self._clues[self._c_idx]
        self._clue_badges[self._c_idx].set_state("solved" if is_correct else "failed")
        self._answer_lbl.setText(f"Réponse : {clue['answer']}")

        QTimer.singleShot(1200, self._next_clue)

    def _next_clue(self):
        self._c_idx += 1
        if self._c_idx >= len(self._clues):
            self._finish_attempt()
        else:
            self._load_clue()

    def _on_timeout(self):
        if self._finished:
            return
        self._finish_attempt(timed_out=True)

    def _finish_attempt(self, timed_out=False):
        if self._finished:
            return
        self._finished = True
        self._timer.stop()
        self._clear_content()

        success = all(b.is_solved() for b in self._clue_badges) and not timed_out
        team = self._current_attempt_team
        pts = CYBER_POINTS_SUCCESS if success else CYBER_POINTS_FAIL
        self.mw.tc.award_points_to(team, "cyber", pts)
        self._update_scores(self._boxes)

        if success:
            msg = QLabel(f"🕵️ ENQUÊTE RÉSOLUE !\n{team.name} identifie le pirate (+{pts} pts)")
            msg.setStyleSheet(f"color: {C['success']}; background: transparent;")
        else:
            reason = "⏱️ Temps écoulé" if timed_out else "Enquête non résolue"
            msg = QLabel(f"🔒 PIRATE INTROUVABLE\n{reason} — {team.name} ({pts} pts)")
            msg.setStyleSheet(f"color: {C['error']}; background: transparent;")

        msg.setAlignment(Qt.AlignCenter)
        msg.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self._content_layout.addWidget(msg)

        QTimer.singleShot(2600, self._after_attempt)

    def _after_attempt(self):
        if self._attempt_offset == 0:
            self._match._turn_index = 1
            self._start_attempt(self._match.team2, attempt_offset=4)
        else:
            self.mw.show_page("menu")