"""
pages/result_page.py — Résultats du match + état du tournoi (VERSION MODERNE)
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from pages.base_page import BasePage
from config import C, TEAMS


class ResultPage(BasePage):

    def _build_page(self):
        self._root_layout.setSpacing(18)
        self._root_layout.setContentsMargins(30, 20, 30, 20)

        hdr = self._add_header(show_back=False, show_audio=False)
        hdr.set_center("")

        # 🎊 Confettis
        self._confetti_lbl = QLabel("🎊 🎉 🏆 🎉 🎊")
        self._confetti_lbl.setAlignment(Qt.AlignCenter)
        self._confetti_lbl.setFont(QFont("Segoe UI Emoji", 28))
        self._confetti_lbl.setStyleSheet("padding: 12px; letter-spacing: 6px;")
        self._root_layout.addWidget(self._confetti_lbl)

        # 🏆 Titre
        self._title_lbl = QLabel("FÉLICITATIONS !")
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self._title_lbl.setStyleSheet(f"color: {C['primary']}; margin-top: 10px;")
        self._root_layout.addWidget(self._title_lbl)

        # 🥇 Gagnant
        self._winner_lbl = QLabel("")
        self._winner_lbl.setAlignment(Qt.AlignCenter)
        self._winner_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self._winner_lbl.setStyleSheet("margin-bottom: 15px;")
        self._root_layout.addWidget(self._winner_lbl)

        # ── Scorecard ──
        self._scores_row = QHBoxLayout()
        self._scores_row.setAlignment(Qt.AlignCenter)
        self._scores_row.setSpacing(25)

        score_wrap = QWidget()
        score_wrap.setLayout(self._scores_row)
        self._root_layout.addWidget(score_wrap)

        # 🧩 Bracket
        bracket_lbl = QLabel("ÉTAT DU TOURNOI")
        bracket_lbl.setAlignment(Qt.AlignCenter)
        bracket_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        bracket_lbl.setStyleSheet(f"color: {C['text_light']}; padding-top:10px;")
        self._root_layout.addWidget(bracket_lbl)

        self._bracket_frame = QFrame()
        bracket_layout = QHBoxLayout(self._bracket_frame)
        bracket_layout.setAlignment(Qt.AlignCenter)
        bracket_layout.setSpacing(20)
        self._root_layout.addWidget(self._bracket_frame)

        self._root_layout.addStretch()

        # 🎮 Boutons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)

        self._next_btn = QPushButton("▶ MATCH SUIVANT")
        self._menu_btn = QPushButton("↩ MENU")
        self._restart_btn = QPushButton("🔄 NOUVEAU TOURNOI")

        for btn in [self._next_btn, self._menu_btn, self._restart_btn]:
            btn.setFixedHeight(48)
            btn.setMinimumWidth(200)
            btn.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # 🎨 Styles modernes
        self._next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {C['primary']};
            color: white;
            border-radius: 12px;
        }}
        QPushButton:hover {{
            background-color: #2e86de;
        }}
        """)

        self._menu_btn.setStyleSheet("""
        QPushButton {
            background-color: #ecf0f1;
            border-radius: 12px;
        }
        QPushButton:hover {
            background-color: #dcdde1;
        }
        """)

        self._restart_btn.setStyleSheet("""
        QPushButton {
            background-color: #f1f2f6;
            border-radius: 12px;
        }
        QPushButton:hover {
            background-color: #dfe4ea;
        }
        """)

        self._next_btn.clicked.connect(self._go_next)
        self._menu_btn.clicked.connect(lambda: self.mw.show_page("menu"))
        self._restart_btn.clicked.connect(self._restart)

        btn_row.addWidget(self._next_btn)
        btn_row.addWidget(self._menu_btn)
        btn_row.addWidget(self._restart_btn)

        self._root_layout.addLayout(btn_row)

        footer = QLabel("Propulsé par CS Club — Madrasat Zaman v3")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {C['text_light']}; font-size: 11px;")
        self._root_layout.addWidget(footer)

        self._tournament_over = False

    # ── LOGIQUE (INCHANGÉE) ──

    def on_show(self, tournament_over=False, **kwargs):
        self._tournament_over = tournament_over
        tourn = self.mw.tc.tournament

        finished_idx = tourn.current_match_idx - 1
        if tournament_over:
            finished_idx = 2
        if finished_idx < 0:
            finished_idx = 0

        finished_match = tourn.matches[finished_idx]

        if tournament_over:
            champ = tourn.champion
            self._title_lbl.setText("🏆 CHAMPION DU TOURNOI !")
            self._winner_lbl.setText(f"{champ.emoji} {champ.name} remporte la victoire !")
            self._winner_lbl.setStyleSheet(f"color: {champ.color};")
            self._next_btn.setVisible(False)
        else:
            winner = finished_match.winner
            self._title_lbl.setText(f"{finished_match.label}")
            self._winner_lbl.setText(f"{winner.emoji} {winner.name} gagne !")
            self._winner_lbl.setStyleSheet(f"color: {winner.color};")
            self._next_btn.setVisible(True)

        self._clear_layout(self._scores_row)
        if finished_match:
            self._add_score_box(finished_match.team1, finished_match.winner)
            vs = QLabel("VS")
            vs.setFont(QFont("Segoe UI", 18, QFont.Bold))
            self._scores_row.addWidget(vs)
            self._add_score_box(finished_match.team2, finished_match.winner)

        self._update_bracket()
        self._animate_confetti()

    def _add_score_box(self, team, winner):
        t = TEAMS[team.key]
        is_winner = winner and winner.key == team.key

        box = QFrame()
        box.setFixedSize(170, 140)

        border_w = 5 if is_winner else 2
        box.setStyleSheet(f"""
            background: {t['light']};
            border-radius: 18px;
            border: {border_w}px solid {t['color']};
        """)

        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        box.setGraphicsEffect(shadow)

        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignCenter)

        
        name = QLabel(f"{t['emoji']} {t['name']}")
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name.setStyleSheet(f"color: {t['color']};")

        score = QLabel(str(team.score))
        score.setAlignment(Qt.AlignCenter)
        score.setFont(QFont("Segoe UI", 42, QFont.Bold))
        score.setStyleSheet(f"color: {t['color']};")

        pts = QLabel("pts")
        pts.setAlignment(Qt.AlignCenter)
        pts.setStyleSheet(f"color: {t['color']}; opacity:0.7;")

        layout.addWidget(name)
        layout.addWidget(score)
        layout.addWidget(pts)

        self._scores_row.addWidget(box)

    def _update_bracket(self):
        self._clear_layout(self._bracket_frame.layout())
        tourn = self.mw.tc.tournament

        for match in tourn.matches:
            if match is None:
                card = self._bracket_card("Finale", "? vs ?", None)
            else:
                teams = f"{match.team1.name} vs {match.team2.name}"
                card = self._bracket_card(match.label, teams, match.winner)
            self._bracket_frame.layout().addWidget(card)

    def _bracket_card(self, label, teams, winner):
        card = QFrame()
        card.setFixedSize(220, 100)
        card.setStyleSheet(f"""
            background: white;
            border-radius: 14px;
            border: 1px solid {C['border']};
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))

        teams_lbl = QLabel(teams)
        teams_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl)
        layout.addWidget(teams_lbl)

        if winner:
            win = QLabel(f"🏆 {winner.name}")
            win.setAlignment(Qt.AlignCenter)
            layout.addWidget(win)

        return card

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _go_next(self):
        self.mw.show_page("menu")

    def _restart(self):
        self.mw.tc.reset()
        self.mw.show_page("home")

    def _animate_confetti(self, step=0):
        import random
        icons = ["🎊","🎉","✨","🌟","🎈","🏆","🥇","💫"]
        self._confetti_lbl.setText(" ".join(random.choices(icons, k=6)))
        if step < 15:
            QTimer.singleShot(120, lambda: self._animate_confetti(step + 1))