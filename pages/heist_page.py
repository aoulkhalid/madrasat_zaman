"""
pages/heist_page.py — Braquage de Banque (version 1 PC, sans téléphones)

Chaque équipe tente, à son tour, d'ouvrir le coffre en résolvant 4 missions
dans le temps imparti. L'équipe répond à l'oral, le/la responsable clique
✅ Correct ou ❌ Incorrect pour valider chaque mission.

4/4 clés avant la fin du chrono -> coffre ouvert (+40 pts)
Sinon (temps écoulé ou mission ratée en fin de tentative) -> alarme (-10 pts)
"""

import os

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QPixmap, QColor

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (
    C,
    HEIST_DURATION,
    HEIST_MISSIONS_PER_ATTEMPT,
    HEIST_POINTS_SUCCESS,
    HEIST_POINTS_FAIL
)

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


class _KeyBadge(QFrame):
    """Un badge clé : verrouillé (gris) / réussi (vert) / raté (rouge)."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 100)
        self._title = title
        self._state = "locked"

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(4)

        self._icon_lbl = QLabel("🔒")
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setFont(QFont("Segoe UI", 30))
        self._icon_lbl.setStyleSheet("background: transparent;")

        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._title_lbl.setStyleSheet(
            f"color: {C['text_light']}; background: transparent;"
        )

        self._layout.addWidget(self._icon_lbl)
        self._layout.addWidget(self._title_lbl)

        self.setGraphicsEffect(_make_shadow(blur=20, dy=5, alpha=70))
        self.set_state("locked")

    def set_state(self, state: str):
        """state: 'locked' | 'success' | 'fail'"""
        self._state = state
        if state == "success":
            self._icon_lbl.setText("🔑")
            bg, border = C["success_bg"], C["success"]
        elif state == "fail":
            self._icon_lbl.setText("❌")
            bg, border = C["error_bg"], C["error"]
        else:
            self._icon_lbl.setText("🔒")
            bg, border = "white", C["border"]

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 22px;
            }}
        """)

    def is_success(self) -> bool:
        return self._state == "success"


class HeistPage(BasePage):

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
        hdr.set_center("🏦 BRAQUAGE DE BANQUE")

        # Bandeau équipe
        self._team_banner = self._add_team_banner()

        # Timer + scoreboard
        self._timer = CircularTimer(duration=HEIST_DURATION, size=110)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Rangée des clés
        keys_row = QHBoxLayout()
        keys_row.setAlignment(Qt.AlignCenter)
        keys_row.setSpacing(22)
        keys_row.setContentsMargins(0, 14, 0, 14)

        self._key_badges = []
        self._keys_wrap = QWidget()
        self._keys_wrap.setStyleSheet("background: transparent;")
        self._keys_wrap.setLayout(keys_row)
        self._keys_row_layout = keys_row
        self._root_layout.addWidget(self._keys_wrap)

        # Zone de contenu dynamique — carte "verre dépoli" pour la lisibilité
        # sur le fond illustré, sans toucher à la palette de couleurs (C).
        self._content_card = QFrame()
        self._content_card.setObjectName("heistCard")
        self._content_card.setStyleSheet("""
            QFrame#heistCard {
                background-color: rgba(255, 255, 255, 0.90);
                border-radius: 28px;
            }
        """)
        self._content_card.setGraphicsEffect(_make_shadow(blur=36, dy=10, alpha=80))

        card_outer = QVBoxLayout()
        card_outer.setContentsMargins(24, 20, 24, 32)
        card_outer.addWidget(self._content_card)
        self._root_layout.addLayout(card_outer, stretch=1)

        self._content_layout = QVBoxLayout(self._content_card)
        self._content_layout.setAlignment(Qt.AlignCenter)
        self._content_layout.setContentsMargins(36, 32, 36, 32)
        self._content_layout.setSpacing(22)

    @staticmethod
    def _clear_layout(layout):
        """Vide récursivement un layout : widgets ET sous-layouts.

        item.widget() renvoie None quand l'item contient un layout imbriqué
        (ex. le QHBoxLayout des boutons ✅/❌ ajouté via addLayout()). Ne
        traiter que les widgets directs laissait les boutons de la mission
        précédente vivants et affichés sous les nouveaux -> effet "dupliqué".
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
                HeistPage._clear_layout(child_layout)
                child_layout.setParent(None)

    def _clear_content(self):
        self._clear_layout(self._content_layout)

    def _rebuild_keys_row(self):
        while self._keys_row_layout.count():
            item = self._keys_row_layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
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
        # Verrou anti double-clic / double-validation pour CETTE mission.
        self._mission_locked = False
        mission = self._missions[self._m_idx]

        counter = QLabel(f"Mission {self._m_idx + 1} / {len(self._missions)}")
        counter.setAlignment(Qt.AlignCenter)
        counter.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        counter.setStyleSheet(
            f"color: {C['text_med']}; background: transparent; letter-spacing: 1px;"
        )

        icon = QLabel(mission["icon"])
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI", 58))
        icon.setStyleSheet("background: transparent;")

        title = QLabel(mission["title"])
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {C['text_light']}; background: transparent;")

        question = QLabel(mission["question"])
        question.setAlignment(Qt.AlignCenter)
        question.setWordWrap(True)
        question.setFont(QFont("Segoe UI", 29, QFont.Bold))
        question.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        self._answer_lbl = QLabel("")
        self._answer_lbl.setAlignment(Qt.AlignCenter)
        self._answer_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self._answer_lbl.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(26)

        self._ok_btn = QPushButton("✅  Correct")
        self._ok_btn.setFixedSize(220, 70)
        self._ok_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._ok_btn.setCursor(Qt.PointingHandCursor)
        self._ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['success']};
                color: white;
                border-radius: 20px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #219150;
            }}
            QPushButton:pressed {{
                padding-top: 3px;
            }}
            QPushButton:disabled {{
                background-color: #a9dcc1;
            }}
        """)
        self._ok_btn.setGraphicsEffect(_make_shadow(blur=18, dy=6, alpha=60))
        self._ok_btn.clicked.connect(lambda: self._validate(True))

        self._no_btn = QPushButton("❌  Incorrect")
        self._no_btn.setFixedSize(220, 70)
        self._no_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._no_btn.setCursor(Qt.PointingHandCursor)
        self._no_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['error']};
                color: white;
                border-radius: 20px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            QPushButton:pressed {{
                padding-top: 3px;
            }}
            QPushButton:disabled {{
                background-color: #eab2ac;
            }}
        """)
        self._no_btn.setGraphicsEffect(_make_shadow(blur=18, dy=6, alpha=60))
        self._no_btn.clicked.connect(lambda: self._validate(False))

        btn_row.addWidget(self._ok_btn)
        btn_row.addWidget(self._no_btn)

        self._content_layout.addWidget(counter)
        self._content_layout.addWidget(icon)
        self._content_layout.addWidget(title)
        self._content_layout.addWidget(question)
        self._content_layout.addLayout(btn_row)
        self._content_layout.addWidget(self._answer_lbl)

    def _validate(self, is_correct: bool):
        # Double garde : l'attempt entière est-elle finie ? cette mission
        # a-t-elle déjà été validée ? Empêche un double-clic (ou un clic sur
        # les deux boutons avant la transition) de faire avancer deux fois
        # l'index de mission, ce qui "sautait" une mission / dupliquait l'état.
        if self._finished or self._mission_locked:
            return
        self._mission_locked = True

        self._ok_btn.setEnabled(False)
        self._no_btn.setEnabled(False)

        mission = self._missions[self._m_idx]
        self._key_badges[self._m_idx].set_state("success" if is_correct else "fail")
        self._answer_lbl.setText(f"Réponse : {mission['answer']}")

        QTimer.singleShot(1100, self._next_mission)

    def _next_mission(self):
        if self._finished:
            return
        self._m_idx += 1
        if self._m_idx >= len(self._missions):
            self._finish_attempt()
        else:
            self._load_mission()

    def _on_timeout(self):
        if self._finished:
            return
        self._finish_attempt(timed_out=True)

    def _finish_attempt(self, timed_out=False):
        if self._finished:
            return

        self._finished = True
        self._mission_locked = True
        self._timer.stop()
        self._clear_content()

        success = all(b.is_success() for b in self._key_badges) and not timed_out
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
        msg.setFont(QFont("Segoe UI", 27, QFont.Bold))
        self._content_layout.addWidget(msg)

        QTimer.singleShot(2600, self._after_attempt)

    def _after_attempt(self):
        if self._attempt_offset == 0:
            self._match._turn_index = 1
            self._start_attempt(self._match.team2, attempt_offset=4)
        else:
            self.mw.show_page("menu")