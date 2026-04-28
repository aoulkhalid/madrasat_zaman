"""
pages/logo_page.py — Logo Game (présentateur valide bonne/mauvaise réponse)
"""
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QPixmap
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, LOGOS_DIR


class LogoPage(BasePage):

    def _build_page(self):
        hdr = self._add_header(show_back=True)
        hdr.set_center("LOGO GAME")

        self._team_banner = self._add_team_banner()
        self._timer       = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes       = self._build_scoreboard(self._timer)

        # Section label
        self._section_lbl = QLabel("Logo 1 / 20")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Arial", 12))
        self._section_lbl.setStyleSheet(f"color: {C['text_light']}; padding: 2px;")
        self._root_layout.addWidget(self._section_lbl)

        # ── Carte logo ──
        self._card = self._make_card()
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(28, 20, 28, 20)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)

        self._logo_lbl = QLabel()
        self._logo_lbl.setAlignment(Qt.AlignCenter)
        self._logo_lbl.setFixedHeight(170)
        self._logo_lbl.setStyleSheet(
            f"background: {C['bg_card']}; border-radius: 12px;"
            f" border: 1px solid {C['border']};")
        card_layout.addWidget(self._logo_lbl)

        self._hint_lbl = QLabel("")
        self._hint_lbl.setAlignment(Qt.AlignCenter)
        self._hint_lbl.setFont(QFont("Arial", 12))
        self._hint_lbl.setStyleSheet(f"color: {C['text_light']};")
        card_layout.addWidget(self._hint_lbl)

        # Feedback
        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setAlignment(Qt.AlignCenter)
        self._feedback_lbl.setFont(QFont("Arial", 14, QFont.Bold))
        card_layout.addWidget(self._feedback_lbl)

        # ── Boutons Bonne / Mauvaise réponse ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)
        btn_row.setAlignment(Qt.AlignCenter)

        self._correct_btn = QPushButton("  ✓  BONNE RÉPONSE  ")
        self._correct_btn.setObjectName("success_btn")
        self._correct_btn.setFixedSize(240, 54)
        self._correct_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self._correct_btn.clicked.connect(lambda: self._validate(True))

        self._wrong_btn = QPushButton("  ✗  MAUVAISE RÉPONSE  ")
        self._wrong_btn.setObjectName("danger_btn")
        self._wrong_btn.setFixedSize(240, 54)
        self._wrong_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self._wrong_btn.clicked.connect(lambda: self._validate(False))

        btn_row.addWidget(self._correct_btn)
        btn_row.addWidget(self._wrong_btn)
        card_layout.addLayout(btn_row)

        wrap = QHBoxLayout()
        wrap.setContentsMargins(36, 0, 36, 14)
        wrap.addWidget(self._card)
        self._root_layout.addLayout(wrap)
        self._root_layout.addStretch()

        # État
        self._logos    = []
        self._l_idx    = 0
        self._answered = False
        self._auto_timer = QTimer()
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._next_logo)

    # ── Logique ───────────────────────────────────────────────────────────────

    def on_show(self, **kwargs):
        self._logos  = self.mw.tc.get_logo_slice()
        self._l_idx  = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        self._update_scores(self._boxes)
        self._load_logo()

    def _load_logo(self):
        if self._l_idx >= len(self._logos):
            self.mw.show_page("menu")
            return

        self._answered = False
        logo  = self._logos[self._l_idx]
        team  = self.mw.tc.current_team

        self._refresh_team_banner()
        self._update_scores(self._boxes)
        self._section_lbl.setText(
            f"Logo {self._l_idx + 1} / {len(self._logos)}  ·  Tour : {team.name}")
        self._hint_lbl.setText(logo.get("hint", ""))
        self._feedback_lbl.setText("")

        # Charger image
        path = os.path.join(LOGOS_DIR, logo["image"])
        pix  = QPixmap(path)
        if pix.isNull():
            self._logo_lbl.setText(f"[ {logo['name']} ]")
            self._logo_lbl.setStyleSheet(
                f"background: {C['bg_card']}; border-radius:12px;"
                f" border: 1px solid {C['border']};"
                f" font-size:22px; font-weight:bold; color:{C['text_light']};")
        else:
            scaled = pix.scaled(320, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._logo_lbl.setPixmap(scaled)
            self._logo_lbl.setText("")

        self._correct_btn.setEnabled(True)
        self._wrong_btn.setEnabled(True)
        self._timer.reset(TIMER_DURATION)
        self._timer.start()

    def _validate(self, correct: bool):
        if self._answered:
            return
        self._answered = True
        self._timer.stop()
        self._correct_btn.setEnabled(False)
        self._wrong_btn.setEnabled(False)

        pts = self.mw.tc.answer("logo", correct)
        self._update_scores(self._boxes)

        logo = self._logos[self._l_idx]
        if correct:
            self._feedback_lbl.setText(f"✓  +{pts} pts — {logo['name']}")
            self._feedback_lbl.setStyleSheet(
                f"color: {C['success']}; font-weight:bold;")
        else:
            self._feedback_lbl.setText(f"✗  0 pts — {logo['name']}")
            self._feedback_lbl.setStyleSheet(
                f"color: {C['error']}; font-weight:bold;")

        self._auto_timer.start(1400)

    def _on_timeout(self):
        if not self._answered:
            self._validate(False)

    def _next_logo(self):
        self.mw.tc.next_turn()
        self._l_idx += 1
        self._load_logo()
