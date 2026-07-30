"""
pages/blindtest_page.py — Blind Test

Le/la responsable lance un extrait audio. Les équipes lèvent la main /
répondent à l'oral. Le/la responsable clique sur l'équipe qui a buzzé
la première (ou "Personne n'a trouvé"). Pas d'alternance stricte : n'importe
quelle équipe du match peut remporter chaque extrait.
"""
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QWidget,
                              QGraphicsDropShadowEffect)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor, QPainter, QPixmap

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, BLINDTEST_DIR, BLINDTEST_ROUND_DURATION,
                     BLINDTEST_POINTS_CORRECT)

# NOTE : adapte le nom de fichier si ton image de fond "blind test" porte un
# autre nom dans assets/images. Le paintEvent ci-dessous ne fait rien si le
# fichier est introuvable (pixmap.isNull()), donc aucun risque de crash —
# juste pas de fond affiché tant que le chemin n'est pas correct.
BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png"
    )
).replace("\\", "/")


def _make_shadow(blur=28, dx=0, dy=8, alpha=90):
    """Petit utilitaire pour des ombres portées cohérentes dans toute la page."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    return shadow


class BlindTestPage(BasePage):

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        pixmap = QPixmap(BG_PATH)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        painter.end()
        super().paintEvent(event)

    def _build_page(self):
        layout = self._root_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QWidget(self)
        container.setStyleSheet("background: transparent;")
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
        self._section_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._section_lbl.setStyleSheet(
            f"color: {C['text_med']}; background: transparent; letter-spacing: 1px;"
        )
        self._root_layout.addWidget(self._section_lbl)

        # Zone de contenu dynamique — carte "verre dépoli" pour la lisibilité
        # sur le fond illustré, sans toucher à la palette de couleurs (C).
        self._content_card = QFrame()
        self._content_card.setObjectName("blindtestCard")
        self._content_card.setStyleSheet("""
            QFrame#blindtestCard {
                background-color: rgba(255, 255, 255, 0.90);
                border-radius: 28px;
            }
        """)
        self._content_card.setGraphicsEffect(_make_shadow(blur=34, dy=10, alpha=80))

        card_outer = QVBoxLayout()
        card_outer.setContentsMargins(28, 20, 28, 32)
        card_outer.addWidget(self._content_card)
        self._root_layout.addLayout(card_outer, stretch=1)

        self._content_layout = QVBoxLayout(self._content_card)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setContentsMargins(36, 34, 36, 34)
        self._content_layout.setSpacing(24)

    @staticmethod
    def _clear_layout(layout):
        """Vide récursivement un layout : widgets ET sous-layouts.

        item.widget() renvoie None quand l'item contient un layout imbriqué
        (la rangée des boutons de buzz est ajoutée via addLayout()). Ne
        traiter que les widgets directs laissait les boutons de l'extrait
        précédent vivants et affichés sous les nouveaux -> effet "dupliqué".
        """
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                # hide() immédiat : deleteLater() ne détruit le widget qu'au
                # prochain passage de la boucle d'événements, donc sans
                # hide() il resterait visible en superposition entre-temps.
                w.hide()
                w.deleteLater()
                continue

            child_layout = item.layout()
            if child_layout is not None:
                BlindTestPage._clear_layout(child_layout)
                child_layout.setParent(None)

    def _clear_content(self):
        self._clear_layout(self._content_layout)

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
        icon.setFont(QFont("Segoe UI", 72))
        icon.setStyleSheet("background: transparent;")

        self._play_btn = QPushButton("▶️  JOUER L'EXTRAIT")
        self._play_btn.setFixedSize(300, 66)
        self._play_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self._play_btn.setCursor(Qt.PointingHandCursor)
        self._play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['primary']};
                color: white;
                border-radius: 18px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {C['primary_light']};
            }}
            QPushButton:pressed {{
                padding-top: 3px;
            }}
            QPushButton:disabled {{
                background-color: {C['primary_light']};
            }}
        """)
        self._play_btn.setGraphicsEffect(_make_shadow(blur=18, dy=6, alpha=60))
        self._play_btn.clicked.connect(self._play_track)

        self._answer_lbl = QLabel("")
        self._answer_lbl.setAlignment(Qt.AlignCenter)
        self._answer_lbl.setWordWrap(True)
        self._answer_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
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
        row.setSpacing(18)

        btn1 = QPushButton(f"✅  {team1.name} a trouvé")
        btn2 = QPushButton(f"✅  {team2.name} a trouvé")
        none_btn = QPushButton("❌  Personne n'a trouvé")

        # Gardées en attributs pour pouvoir les désactiver une fois la manche
        # résolue (évite tout second clic une fois la réponse déjà validée).
        self._buzz_buttons = (btn1, btn2, none_btn)

        for btn, color, hover in (
            (btn1, C['success'], "#219150"),
            (btn2, C['success'], "#219150"),
            (none_btn, C['error'], "#c0392b"),
        ):
            btn.setFixedHeight(60)
            btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 16px;
                    border: none;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    padding-top: 3px;
                }}
                QPushButton:disabled {{
                    background-color: #cfd8dc;
                    color: white;
                }}
            """)
            btn.setGraphicsEffect(_make_shadow(blur=16, dy=5, alpha=55))

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

        for btn in getattr(self, "_buzz_buttons", ()):
            btn.setEnabled(False)

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