"""
pages/investment_page.py — Le Bon Investissement

Chaque équipe répartit un capital fictif entre 4 postes (Marketing, R&D,
Recrutement, Dev) sans connaître les rendements cachés du scénario.
Une fois les deux équipes validées, les rendements sont révélés et le
ROI de chaque équipe est calculé et comparé.

ROI = somme(allocation_poste × multiplicateur_poste) / somme(allocations)
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                              QPushButton, QFrame, QWidget, QGridLayout)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, INVESTMENT_ROUNDS_PER_MATCH, INVESTMENT_ALLOCATION_DURATION,
                     INVESTMENT_POINTS_WIN, INVESTMENT_POINTS_LOSE_POSITIVE,
                     INVESTMENT_POINTS_TIE)

POSTS = [
    ("marketing",    "📢 Marketing"),
    ("rnd",          "🔬 R&D"),
    ("recrutement",  "👥 Recrutement"),
    ("dev",          "💻 Dev"),
]


class _PostSlider(QFrame):
    """Un poste d'investissement : label + slider 0-100 + valeur affichée."""

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        top = QHBoxLayout()
        self._label = QLabel(label)
        self._label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._label.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        self._value_lbl = QLabel("25%")
        self._value_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._value_lbl.setAlignment(Qt.AlignRight)
        self._value_lbl.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        top.addWidget(self._label)
        top.addStretch()
        top.addWidget(self._value_lbl)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setSingleStep(5)
        self.slider.setPageStep(5)
        self.slider.setValue(25)
        self.slider.setTickInterval(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(lambda v: self._value_lbl.setText(f"{v}%"))

        layout.addLayout(top)
        layout.addWidget(self.slider)

    def value(self) -> int:
        return self.slider.value()

    def reset(self):
        self.slider.setValue(25)


class InvestmentPage(BasePage):

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

        hdr = self._add_header(show_back=True)
        hdr.set_center("💼 LE BON INVESTISSEMENT")

        self._team_banner = self._add_team_banner()

        self._timer = CircularTimer(duration=INVESTMENT_ALLOCATION_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        self._round_lbl = QLabel("Trimestre 1 / 3")
        self._round_lbl.setAlignment(Qt.AlignCenter)
        self._round_lbl.setFont(QFont("Segoe UI", 11))
        self._round_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")
        self._root_layout.addWidget(self._round_lbl)

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

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._match = self.mw.tc.current_match
        self._match._turn_index = 0
        self._scenarios = self.mw.tc.get_investment_slice()
        self._round_idx = 0
        self._cumulative = {self._match.team1.key: 0, self._match.team2.key: 0}
        self._update_scores(self._boxes)
        self._start_round()

    def _start_round(self):
        self._scenario = self._scenarios[self._round_idx]
        self._allocations = {}
        self._round_lbl.setText(f"Trimestre {self._round_idx + 1} / {len(self._scenarios)}")
        self._start_allocation(self._match.team1)

    def _start_allocation(self, team):
        self._alloc_team = team
        self._clear_content()
        self._timer.stop()
        self._refresh_team_banner()

        title = QLabel(f"{team.name} — Répartissez votre capital")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        warn = QLabel("⚠️ L'équipe adverse ne doit pas voir votre répartition !")
        warn.setAlignment(Qt.AlignCenter)
        warn.setFont(QFont("Segoe UI", 12))
        warn.setStyleSheet(f"color: {C['error']}; background: transparent;")

        scenario_box = QFrame()
        scenario_box.setStyleSheet(f"""
            QFrame {{ background-color: white; border: 1px solid {C['border']};
                      border-radius: 14px; }}
        """)
        sb_layout = QVBoxLayout(scenario_box)
        sb_layout.setContentsMargins(20, 14, 20, 14)

        s_title = QLabel(self._scenario["title"])
        s_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        s_title.setWordWrap(True)
        s_title.setAlignment(Qt.AlignCenter)
        s_title.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        s_desc = QLabel(self._scenario["description"])
        s_desc.setFont(QFont("Segoe UI", 11))
        s_desc.setWordWrap(True)
        s_desc.setAlignment(Qt.AlignCenter)
        s_desc.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        sb_layout.addWidget(s_title)
        sb_layout.addWidget(s_desc)

        self._sliders = {}
        grid = QGridLayout()
        grid.setSpacing(14)
        for i, (key, label) in enumerate(POSTS):
            s = _PostSlider(label)
            s.reset()
            s.slider.valueChanged.connect(self._update_total)
            self._sliders[key] = s
            grid.addWidget(s, i // 2, i % 2)

        self._total_lbl = QLabel("Total : 100%")
        self._total_lbl.setAlignment(Qt.AlignCenter)
        self._total_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._total_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        submit = QPushButton("VALIDER LA RÉPARTITION")
        submit.setFixedSize(280, 52)
        submit.setFont(QFont("Segoe UI", 13, QFont.Bold))
        submit.setCursor(Qt.PointingHandCursor)
        submit.setStyleSheet(f"""
            QPushButton {{ background-color: {C['primary']}; color: white; border-radius: 14px; }}
            QPushButton:hover {{ background-color: {C['primary_light']}; }}
        """)
        submit.clicked.connect(self._submit_allocation)

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(warn)
        self._content_layout.addWidget(scenario_box)
        self._content_layout.addLayout(grid)
        self._content_layout.addWidget(self._total_lbl)
        self._content_layout.addWidget(submit, alignment=Qt.AlignCenter)

        self._timer.reset(INVESTMENT_ALLOCATION_DURATION)
        self._timer.start()

    def _update_total(self):
        total = sum(s.value() for s in self._sliders.values())
        self._total_lbl.setText(f"Total : {total}%")
        if total == 100:
            self._total_lbl.setStyleSheet(f"color: {C['success']}; background: transparent;")
        else:
            self._total_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

    def _submit_allocation(self):
        self._timer.stop()
        self._allocations[self._alloc_team.key] = {
            key: s.value() for key, s in self._sliders.items()
        }
        if self._alloc_team.key == self._match.team1.key:
            self._start_allocation(self._match.team2)
        else:
            self._reveal_results()

    def _on_timeout(self):
        # Temps écoulé -> on valide la répartition actuelle telle quelle
        self._submit_allocation()

    def _compute_roi(self, allocation: dict) -> float:
        total = sum(allocation.values())
        if total == 0:
            return 0.0
        weighted = sum(allocation[k] * self._scenario["multipliers"][k] for k in allocation)
        return weighted / total

    def _reveal_results(self):
        self._clear_content()
        self._timer.stop()

        team1, team2 = self._match.team1, self._match.team2
        alloc1 = self._allocations[team1.key]
        alloc2 = self._allocations[team2.key]
        roi1 = self._compute_roi(alloc1)
        roi2 = self._compute_roi(alloc2)

        title = QLabel("📊 Rendements révélés !")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        mult_lines = "   ".join(
            f"{label} ×{self._scenario['multipliers'][key]:.1f}" for key, label in POSTS
        )
        mult_lbl = QLabel(mult_lines)
        mult_lbl.setAlignment(Qt.AlignCenter)
        mult_lbl.setWordWrap(True)
        mult_lbl.setFont(QFont("Segoe UI", 12))
        mult_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        row = QHBoxLayout()
        row.setSpacing(30)
        row.setAlignment(Qt.AlignCenter)
        row.addWidget(self._make_result_card(team1, alloc1, roi1))
        row.addWidget(self._make_result_card(team2, alloc2, roi2))

        # Points
        if roi1 > roi2:
            winner, loser, roi_w, roi_l = team1, team2, roi1, roi2
        elif roi2 > roi1:
            winner, loser, roi_w, roi_l = team2, team1, roi2, roi1
        else:
            winner = loser = None

        if winner is None:
            self.mw.tc.award_points_to(team1, "investment", INVESTMENT_POINTS_TIE)
            self.mw.tc.award_points_to(team2, "investment", INVESTMENT_POINTS_TIE)
            self._cumulative[team1.key] += INVESTMENT_POINTS_TIE
            self._cumulative[team2.key] += INVESTMENT_POINTS_TIE
            result_msg = f"Égalité ! +{INVESTMENT_POINTS_TIE} pts chacune"
        else:
            self.mw.tc.award_points_to(winner, "investment", INVESTMENT_POINTS_WIN)
            self._cumulative[winner.key] += INVESTMENT_POINTS_WIN
            loser_pts = INVESTMENT_POINTS_LOSE_POSITIVE if roi_l >= 1.0 else 0
            if loser_pts:
                self.mw.tc.award_points_to(loser, "investment", loser_pts)
                self._cumulative[loser.key] += loser_pts
            result_msg = (f"🏆 {winner.name} a le meilleur ROI ce trimestre "
                          f"(+{INVESTMENT_POINTS_WIN} pts)")

        self._update_scores(self._boxes)

        result_lbl = QLabel(result_msg)
        result_lbl.setAlignment(Qt.AlignCenter)
        result_lbl.setWordWrap(True)
        result_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        result_lbl.setStyleSheet(f"color: {C['success']}; background: transparent;")

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(mult_lbl)
        self._content_layout.addLayout(row)
        self._content_layout.addWidget(result_lbl)

        QTimer.singleShot(3200, self._next_round)

    def _make_result_card(self, team, allocation, roi):
        card = QFrame()
        card.setFixedWidth(260)
        card.setStyleSheet(f"""
            QFrame {{ background-color: white; border: 2px solid {C['border']};
                      border-radius: 14px; }}
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(6)

        name = QLabel(team.name)
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        for key, label in POSTS:
            line = QLabel(f"{label} : {allocation[key]}%")
            line.setFont(QFont("Segoe UI", 10))
            line.setStyleSheet(f"color: {C['text_med']}; background: transparent;")
            v.addWidget(line)

        roi_lbl = QLabel(f"ROI : {roi*100:.0f}%")
        roi_lbl.setAlignment(Qt.AlignCenter)
        roi_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        color = C['success'] if roi >= 1.0 else C['error']
        roi_lbl.setStyleSheet(f"color: {color}; background: transparent;")

        v.addWidget(name)
        v.addWidget(roi_lbl)
        return card

    def _next_round(self):
        self._round_idx += 1
        if self._round_idx >= len(self._scenarios):
            self._finish_match()
        else:
            self._start_round()

    def _finish_match(self):
        self._clear_content()
        team1, team2 = self._match.team1, self._match.team2
        c1, c2 = self._cumulative[team1.key], self._cumulative[team2.key]

        if c1 > c2:
            msg_text = f"🏆 {team1.name} remporte le duel d'investissement !"
        elif c2 > c1:
            msg_text = f"🏆 {team2.name} remporte le duel d'investissement !"
        else:
            msg_text = "🤝 Égalité parfaite sur l'ensemble des trimestres !"

        msg = QLabel(msg_text)
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setFont(QFont("Segoe UI", 20, QFont.Bold))
        msg.setStyleSheet(f"color: {C['success']}; background: transparent;")
        self._content_layout.addWidget(msg)

        QTimer.singleShot(3000, lambda: self.mw.show_page("menu"))