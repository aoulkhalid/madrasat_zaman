"""
pages/heist_page.py — Braquage de Banque (version 1 PC, sans téléphones)

Chaque équipe tente, à son tour, d'ouvrir le coffre en résolvant 4 missions
dans le temps imparti. L'équipe répond à l'oral, le/la responsable clique
✅ Correct ou ❌ Incorrect pour valider chaque mission.

4/4 clés avant la fin du chrono -> coffre ouvert (+40 pts)
Sinon (temps écoulé ou mission ratée en fin de tentative) -> alarme (-10 pts)
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, HEIST_DURATION, HEIST_MISSIONS_PER_ATTEMPT,
                     HEIST_POINTS_SUCCESS, HEIST_POINTS_FAIL)


class _KeyBadge(QFrame):
    """Un badge clé : verrouillé (gris) / réussi (vert) / raté (rouge)."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 80)
        self._title = title
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(2)

        self._icon_lbl = QLabel("🔒")
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setFont(QFont("Segoe UI", 22))
        self._icon_lbl.setStyleSheet("background: transparent;")

        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self._title_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        self._layout.addWidget(self._icon_lbl)
        self._layout.addWidget(self._title_lbl)
        self.set_state("locked")

    def set_state(self, state: str):
        """state: 'locked' | 'success' | 'fail'"""
        if state == "success":
            self._icon_lbl.setText("🔑")
            bg, border = C['success_bg'], C['success']
        elif state == "fail":
            self._icon_lbl.setText("❌")
            bg, border = C['error_bg'], C['error']
        else:
            self._icon_lbl.setText("🔒")
            bg, border = "white", C['border']
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 14px;
            }}
        """)


class HeistPage(BasePage):

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
        hdr.set_center("🏦 BRAQUAGE DE BANQUE")

        # Bandeau équipe
        self._team_banner = self._add_team_banner()

        # Timer + scoreboard
        self._timer = CircularTimer(duration=HEIST_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Rangée des clés
        keys_row = QHBoxLayout()
        keys_row.setAlignment(Qt.AlignCenter)
        keys_row.setSpacing(16)
        keys_row.setContentsMargins(0, 10, 0, 10)
        self._key_badges = []  # rempli dans on_show selon les missions
        self._keys_wrap = QWidget()
        self._keys_wrap.setLayout(keys_row)
        self._keys_row_layout = keys_row
        self._root_layout.addWidget(self._keys_wrap)

        # Zone de contenu dynamique (mission courante / écran final)
        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setSpacing(18)
        self._root_layout.addWidget(self._content, stretch=1)

    def _clear_content(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _rebuild_keys_row(self):
        while self._keys_row_layout.count():
            item = self._keys_row_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._key_badges = []
        for m in self._missions:
            badge = _KeyBadge(m["title"])
            self._key_badges.append(badge)
            self._keys_row_layout.addWidget(badge)

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._match = self.mw.tc.current_match
        self._match._turn_index = 0
        self._start_attempt(self._match.team1, attempt_offset=0)

    def _start_attempt(self, team, attempt_offset):
        self._current_attempt_team = team
        self._attempt_offset = attempt_offset
        self._missions = self.mw.tc.get_heist_slice(attempt_offset)
        self._m_idx = 0
        self._finished = False

        self._rebuild_keys_row()
        self._refresh_team_banner()
        self._update_scores(self._boxes)

        self._timer.reset(HEIST_DURATION)
        self._timer.start()
        self._load_mission()

    def _load_mission(self):
        self._clear_content()
        mission = self._missions[self._m_idx]

        counter = QLabel(f"Mission {self._m_idx + 1} / {len(self._missions)}")
        counter.setAlignment(Qt.AlignCenter)
        counter.setFont(QFont("Segoe UI", 11))
        counter.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        icon = QLabel(mission["icon"])
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 40))
        icon.setStyleSheet("background: transparent;")

        title = QLabel(mission["title"])
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        question = QLabel(mission["question"])
        question.setAlignment(Qt.AlignCenter)
        question.setWordWrap(True)
        question.setFont(QFont("Segoe UI", 22, QFont.Bold))
        question.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        self._answer_lbl = QLabel("")
        self._answer_lbl.setAlignment(Qt.AlignCenter)
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
        self._content_layout.addWidget(question)
        self._content_layout.addLayout(btn_row)
        self._content_layout.addWidget(self._answer_lbl)

    def _validate(self, is_correct: bool):
        if self._finished:
            return
        mission = self._missions[self._m_idx]
        self._key_badges[self._m_idx].set_state("success" if is_correct else "fail")
        self._answer_lbl.setText(f"Réponse : {mission['answer']}")

        QTimer.singleShot(1100, self._next_mission)
        # désactive temporairement pour éviter le double-clic
        self._finished_step = True

    def _next_mission(self):
        self._m_idx += 1
        if self._m_idx >= len(self._missions):
            self._finish_attempt()
        else:
            self._load_mission()

    def _on_timeout(self):
        if self._finished:
            return
        # Les clés non encore tentées restent verrouillées -> échec
        self._finish_attempt(timed_out=True)

    def _finish_attempt(self, timed_out=False):
        if self._finished:
            return
        self._finished = True
        self._timer.stop()
        self._clear_content()

        success = all(b._icon_lbl.text() == "🔑" for b in self._key_badges) and not timed_out
        team = self._current_attempt_team
        pts = HEIST_POINTS_SUCCESS if success else HEIST_POINTS_FAIL
        self.mw.tc.award_points_to(team, "heist", pts)
        self._update_scores(self._boxes)

        if success:
            msg = QLabel(f"💰 COFFRE OUVERT !\n{team.name} remporte cette manche (+{pts} pts)")
            msg.setStyleSheet(f"color: {C['success']}; background: transparent;")
        else:
            reason = "⏱️ Temps écoulé" if timed_out else "Mission ratée"
            msg = QLabel(f"💥 ALARME !\n{reason} — {team.name} ({pts} pts)")
            msg.setStyleSheet(f"color: {C['error']}; background: transparent;")

        msg.setAlignment(Qt.AlignCenter)
        msg.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self._content_layout.addWidget(msg)

        QTimer.singleShot(2600, self._after_attempt)

    def _after_attempt(self):
        if self._attempt_offset == 0:
            # Passe au tour de l'équipe 2
            self._match._turn_index = 1
            self._start_attempt(self._match.team2, attempt_offset=4)
        else:
            self.mw.show_page("menu")