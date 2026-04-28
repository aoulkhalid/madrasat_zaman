"""
pages/result_page.py — Résultats du match + état du tournoi
Gère : fin de demi-finale → affichage bracket  |  fin de finale → champion
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy,
                              QScrollArea, QWidget)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont
from pages.base_page import BasePage
from config          import C, TEAMS


class ResultPage(BasePage):

    def _build_page(self):
        hdr = self._add_header(show_back=False, show_audio=False)
        hdr.set_center("")

        # ── Trophée + confettis ──
        self._confetti_lbl = QLabel("🎊 🎉 🏆 🎉 🎊")
        self._confetti_lbl.setAlignment(Qt.AlignCenter)
        self._confetti_lbl.setFont(QFont("Arial", 32))
        self._confetti_lbl.setStyleSheet("padding: 10px;")
        self._root_layout.addWidget(self._confetti_lbl)

        # Titre
        self._title_lbl = QLabel("FÉLICITATIONS !")
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(QFont("Georgia", 30, QFont.Bold))
        self._title_lbl.setStyleSheet(f"color: {C['primary']};")
        self._root_layout.addWidget(self._title_lbl)

        # Gagnant
        self._winner_lbl = QLabel("")
        self._winner_lbl.setAlignment(Qt.AlignCenter)
        self._winner_lbl.setFont(QFont("Arial", 18, QFont.Bold))
        self._winner_lbl.setStyleSheet(f"color: {C['warning']};")
        self._root_layout.addWidget(self._winner_lbl)

        # ── Scorecard ──
        self._scores_row = QHBoxLayout()
        self._scores_row.setAlignment(Qt.AlignCenter)
        self._scores_row.setSpacing(20)
        score_wrap = QWidget()
        score_wrap.setStyleSheet("background: transparent;")
        score_wrap.setLayout(self._scores_row)
        self._root_layout.addWidget(score_wrap)

        # Bracket tournoi
        bracket_lbl = QLabel("ÉTAT DU TOURNOI")
        bracket_lbl.setAlignment(Qt.AlignCenter)
        bracket_lbl.setFont(QFont("Arial", 14, QFont.Bold))
        bracket_lbl.setStyleSheet(f"color: {C['text_light']}; padding-top:10px;")
        self._root_layout.addWidget(bracket_lbl)

        self._bracket_frame = QFrame()
        self._bracket_frame.setStyleSheet("background: transparent;")
        bracket_layout = QHBoxLayout(self._bracket_frame)
        bracket_layout.setAlignment(Qt.AlignCenter)
        bracket_layout.setSpacing(16)
        self._root_layout.addWidget(self._bracket_frame)

        self._root_layout.addStretch()

        # ── Boutons ──
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)

        self._next_btn = QPushButton("  ▶  MATCH SUIVANT  ")
        self._next_btn.setObjectName("primary")
        self._next_btn.setFixedHeight(48)
        self._next_btn.setMinimumWidth(220)
        self._next_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self._next_btn.clicked.connect(self._go_next)

        self._menu_btn = QPushButton("  ↩  RETOUR AU MENU  ")
        self._menu_btn.setObjectName("secondary")
        self._menu_btn.setFixedHeight(48)
        self._menu_btn.setMinimumWidth(220)
        self._menu_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self._menu_btn.clicked.connect(lambda: self.mw.show_page("menu"))

        self._restart_btn = QPushButton("  🔄  NOUVEAU TOURNOI  ")
        self._restart_btn.setObjectName("secondary")
        self._restart_btn.setFixedHeight(48)
        self._restart_btn.setMinimumWidth(220)
        self._restart_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self._restart_btn.clicked.connect(self._restart)

        btn_row.addWidget(self._next_btn)
        btn_row.addWidget(self._menu_btn)
        btn_row.addWidget(self._restart_btn)
        self._root_layout.addLayout(btn_row)

        footer = QLabel("Propulsé par CS Club  —  Madrasat Zaman v3")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {C['text_light']}; font-size: 11px; padding:8px;")
        self._root_layout.addWidget(footer)

        self._tournament_over = False

    # ── Logique ───────────────────────────────────────────────────────────────

    def on_show(self, tournament_over=False, **kwargs):
        self._tournament_over = tournament_over
        tourn = self.mw.tc.tournament

        # Déterminer quel match vient de finir
        finished_idx = tourn.current_match_idx - 1
        if tournament_over:
            finished_idx = 2  # c'est la finale

        if finished_idx < 0:
            finished_idx = 0

        finished_match = tourn.matches[finished_idx]

        # ── Titre ──
        if tournament_over:
            champ = tourn.champion
            self._title_lbl.setText(f"🏆  CHAMPION DU TOURNOI !")
            self._winner_lbl.setText(
                f"{champ.emoji}  {champ.name}  remporte la victoire !")
            self._winner_lbl.setStyleSheet(f"color: {champ.color};")
            self._next_btn.setVisible(False)
        else:
            winner = finished_match.winner
            self._title_lbl.setText(
                f"FÉLICITATIONS — {finished_match.label} !")
            self._winner_lbl.setText(
                f"{winner.emoji}  {winner.name}  remporte ce match !")
            self._winner_lbl.setStyleSheet(f"color: {winner.color};")
            self._next_btn.setVisible(True)
            # Libellé du bouton suivant
            if tourn.current_match_idx == 2 and tourn.matches[2]:
                m = tourn.matches[2]
                self._next_btn.setText(
                    f"  ▶  FINALE : {m.team1.name} vs {m.team2.name}  ")

        # ── Scorecard du match terminé ──
        self._clear_layout(self._scores_row)
        if finished_match:
            self._add_score_box(finished_match.team1, finished_match.winner)
            vs = QLabel("VS")
            vs.setFont(QFont("Arial", 20, QFont.Bold))
            vs.setStyleSheet(f"color: {C['text_light']};")
            self._scores_row.addWidget(vs)
            self._add_score_box(finished_match.team2, finished_match.winner)

        # ── Bracket ──
        self._update_bracket()

        # Confettis animés
        self._animate_confetti()

    def _add_score_box(self, team, winner):
        t  = TEAMS[team.key]
        is_winner = (winner and winner.key == team.key)
        box = QFrame()
        box.setFixedSize(160, 130)
        border_w = 5 if is_winner else 2
        box.setStyleSheet(
            f"background: {t['light']}; border-radius: 16px;"
            f" border: {border_w}px solid {t['color']};")
        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignCenter)

        name_lbl = QLabel(f"{t['emoji']} {t['name']}")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setFont(QFont("Arial", 12, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {t['color']}; background: transparent;")

        score_lbl = QLabel(str(team.score))
        score_lbl.setAlignment(Qt.AlignCenter)
        score_lbl.setFont(QFont("Arial", 40, QFont.Bold))
        score_lbl.setStyleSheet(f"color: {t['color']}; background: transparent;")

        pts_lbl = QLabel("pts")
        pts_lbl.setAlignment(Qt.AlignCenter)
        pts_lbl.setFont(QFont("Arial", 11))
        pts_lbl.setStyleSheet(f"color: {t['color']}; background: transparent;")

        if is_winner:
            crown = QLabel("🏆")
            crown.setAlignment(Qt.AlignCenter)
            crown.setFont(QFont("Arial", 18))
            crown.setStyleSheet("background: transparent;")
            layout.addWidget(crown)

        layout.addWidget(name_lbl)
        layout.addWidget(score_lbl)
        layout.addWidget(pts_lbl)
        self._scores_row.addWidget(box)

    def _update_bracket(self):
        self._clear_layout(self._bracket_frame.layout())
        tourn = self.mw.tc.tournament

        for i, match in enumerate(tourn.matches):
            if match is None:
                # Finale pas encore créée
                card = self._bracket_card("Finale", "? vs ?", None, C["text_light"])
            else:
                label = match.label
                teams = f"{match.team1.emoji}{match.team1.name} vs {match.team2.emoji}{match.team2.name}"
                winner = match.winner
                card = self._bracket_card(label, teams, winner, C["primary"])
            self._bracket_frame.layout().addWidget(card)

    def _bracket_card(self, label, teams_str, winner, color) -> QFrame:
        card = QFrame()
        card.setFixedSize(220, 90)
        card.setStyleSheet(
            f"background: white; border-radius: 12px;"
            f" border: 2px solid {C['border']};")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(3)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        lbl.setStyleSheet(f"color: {color}; background: transparent;")

        teams_lbl = QLabel(teams_str)
        teams_lbl.setAlignment(Qt.AlignCenter)
        teams_lbl.setFont(QFont("Arial", 10))
        teams_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")
        teams_lbl.setWordWrap(True)

        layout.addWidget(lbl)
        layout.addWidget(teams_lbl)

        if winner:
            win_lbl = QLabel(f"🏆 {winner.name}")
            win_lbl.setAlignment(Qt.AlignCenter)
            win_lbl.setFont(QFont("Arial", 10, QFont.Bold))
            win_lbl.setStyleSheet(
                f"color: {TEAMS[winner.key]['color']}; background: transparent;")
            layout.addWidget(win_lbl)
        return card

    def _clear_layout(self, layout):
        if layout is None:
            return
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
        icons = ["🎊","🎉","✨","🌟","🎈","🏅","🥇"]
        import random
        row = " ".join(random.choices(icons, k=6))
        self._confetti_lbl.setText(row)
        if step < 15:
            QTimer.singleShot(150, lambda: self._animate_confetti(step + 1))
