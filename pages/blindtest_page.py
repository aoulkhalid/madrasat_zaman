"""
pages/blindtest_page.py — Blind Test

Le/la responsable lance un extrait audio. Les équipes lèvent la main /
répondent à l'oral. Le/la responsable clique sur l'équipe qui a buzzé
la première (ou "Personne n'a trouvé"). Pas d'alternance stricte : n'importe
quelle équipe du match peut remporter chaque extrait.
"""
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, BLINDTEST_DIR, BLINDTEST_ROUND_DURATION,
                     BLINDTEST_POINTS_CORRECT)


class BlindTestPage(BasePage):

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
        hdr.set_center("🎵 BLIND TEST")

        # Bandeau équipe (affiche juste l'équipe "active" par défaut, non bloquant)
        self._team_banner = self._add_team_banner()

        # Timer + scoreboard
        self._timer = CircularTimer(duration=BLINDTEST_ROUND_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        self._section_lbl = QLabel("Extrait 1 / 8")
        self._section_lbl.setAlignment(Qt.AlignCenter)
        self._section_lbl.setFont(QFont("Segoe UI", 11))
        self._section_lbl.setStyleSheet(f"color: {C['text_light']}; background: transparent;")
        self._root_layout.addWidget(self._section_lbl)

        # Zone de contenu dynamique
        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setSpacing(20)
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
        self._tracks = self.mw.tc.get_blindtest_slice()
        self._idx = 0
        self._channel = None
        self.mw.audio.stop()          # coupe l'ambiance pendant le blind test
        self._update_scores(self._boxes)
        self._refresh_team_banner()
        self._load_track()

    def _load_track(self):
        if self._idx >= len(self._tracks):
            self.mw.show_page("menu")
            return

        self._answered = False
        self._played   = False
        self._clear_content()
        self._timer.stop()
        self._section_lbl.setText(f"Extrait {self._idx + 1} / {len(self._tracks)}")

        icon = QLabel("🎧")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 48))
        icon.setStyleSheet("background: transparent;")

        self._play_btn = QPushButton("▶️  JOUER L'EXTRAIT")
        self._play_btn.setFixedSize(280, 60)
        self._play_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._play_btn.setCursor(Qt.PointingHandCursor)
        self._play_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {C['primary']}; color: white; border-radius: 16px; }}
            QPushButton:hover {{ background-color: {C['primary_light']}; }}
        """)
        self._play_btn.clicked.connect(self._play_track)

        self._answer_lbl = QLabel("")
        self._answer_lbl.setAlignment(Qt.AlignCenter)
        self._answer_lbl.setWordWrap(True)
        self._answer_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._answer_lbl.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        self._content_layout.addWidget(icon)
        self._content_layout.addWidget(self._play_btn, alignment=Qt.AlignCenter)
        self._content_layout.addWidget(self._answer_lbl)

    def _play_track(self):
        track = self._tracks[self._idx]
        path = os.path.join(BLINDTEST_DIR, track["file"])

        if not os.path.exists(path):
            self._answer_lbl.setText(
                f"⚠️ Fichier introuvable : {track['file']}\n"
                f"Ajoute-le dans assets/sounds/blindtest/"
            )
            self._answer_lbl.setStyleSheet(f"color: {C['error']}; background: transparent;")
        else:
            self._channel = self.mw.audio.play_clip(path)

        self._played = True
        self._play_btn.setEnabled(False)
        self._play_btn.setText("🎶  Extrait en cours...")

        self._show_buzz_buttons()
        self._timer.reset(BLINDTEST_ROUND_DURATION)
        self._timer.start()

    def _show_buzz_buttons(self):
        team1 = self._match.team1
        team2 = self._match.team2

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(16)

        btn1 = QPushButton(f"✅  {team1.name} a trouvé")
        btn2 = QPushButton(f"✅  {team2.name} a trouvé")
        none_btn = QPushButton("❌  Personne n'a trouvé")

        for btn, color in ((btn1, C['success']), (btn2, C['success']), (none_btn, C['error'])):
            btn.setFixedHeight(56)
            btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {color}; color: white; border-radius: 14px; padding: 0 16px; }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)

        btn1.clicked.connect(lambda: self._resolve(team1))
        btn2.clicked.connect(lambda: self._resolve(team2))
        none_btn.clicked.connect(lambda: self._resolve(None))

        row.addWidget(btn1)
        row.addWidget(btn2)
        row.addWidget(none_btn)
        self._content_layout.addLayout(row)

    def _resolve(self, team):
        if self._answered:
            return
        self._answered = True
        self._timer.stop()
        if self._channel:
            self.mw.audio.stop_clip(self._channel)
            self._channel = None

        track = self._tracks[self._idx]
        if team is not None:
            self.mw.tc.award_points_to(team, "blindtest", BLINDTEST_POINTS_CORRECT)
            self._answer_lbl.setText(
                f"🎉 {team.name} a trouvé ! (+{BLINDTEST_POINTS_CORRECT} pts)\n"
                f"{track['title']} — {track['artist']}"
            )
            self._answer_lbl.setStyleSheet(f"color: {C['success']}; background: transparent;")
        else:
            self._answer_lbl.setText(
                f"Réponse : {track['title']} — {track['artist']}"
            )
            self._answer_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        self._update_scores(self._boxes)
        QTimer.singleShot(2200, self._next_track)

    def _on_timeout(self):
        if self._answered:
            return
        self._resolve(None)

    def _next_track(self):
        self._idx += 1
        self._load_track()