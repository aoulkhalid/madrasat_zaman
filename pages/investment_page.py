# -*- coding: utf-8 -*-
"""
pages/investment_page.py — Le Bon Investissement

Version simulation business réaliste.

Le design original est conservé.

La logique :
1. Chaque équipe reçoit 100 000 DH.
2. Elle répartit son capital entre 4 postes.
3. Les conséquences sont calculées selon le scénario.
4. Un événement économique survient.
5. Les indicateurs de l'entreprise sont mis à jour.
6. Un score final est calculé.
7. Le meilleur score gagne la manche.

Score :
    30% Santé
    25% Réputation
    20% Croissance
    15% Clients
    10% Trésorerie
"""

import os

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QFrame,
    QWidget,
    QGraphicsDropShadowEffect,
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer

from config import (
    C,
    INVESTMENT_ROUNDS_PER_MATCH,
    INVESTMENT_ALLOCATION_DURATION,
    INVESTMENT_POINTS_WIN,
    INVESTMENT_POINTS_LOSE_POSITIVE,
    INVESTMENT_POINTS_TIE,
)


BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png",
    )
).replace("\\", "/")


POSTS = [
    ("marketing", "📢", "Marketing"),
    ("rnd", "🔬", "R&D"),
    ("recrutement", "👥", "Recrutement"),
    ("dev", "💻", "Dev"),
]


# ============================================================
# OUTILS
# ============================================================

def _make_shadow(blur=28, dx=0, dy=8, alpha=90):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    return shadow


def _accent_for(key):
    return {
        "marketing": C["primary"],
        "rnd": C["success"],
        "recrutement": C["error"],
        "dev": C["text_dark"],
    }.get(key, C["primary"])


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


# ============================================================
# SLIDER
# ============================================================

class _PostRow(QFrame):

    def __init__(self, emoji, label, accent, parent=None):
        super().__init__(parent)

        self._accent = accent

        self.setStyleSheet(
            "background: transparent; border: none;"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(22)

        badge = QLabel(emoji)
        badge.setFixedSize(62, 62)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFont(QFont("Segoe UI", 26))

        badge.setStyleSheet(
            f"""
            background-color: white;
            border: 3px solid {accent};
            border-radius: 31px;
            """
        )

        text_label = QLabel(label)
        text_label.setFixedWidth(140)
        text_label.setFont(
            QFont("Segoe UI", 15, QFont.Bold)
        )

        text_label.setStyleSheet(
            f"""
            color: {C['text_dark']};
            background: transparent;
            """
        )

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setRange(0, 100)
        self.slider.setSingleStep(5)
        self.slider.setPageStep(5)
        self.slider.setValue(25)
        self.slider.setMinimumHeight(40)

        self.slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                height: 20px;
                border-radius: 10px;
                background: {C['border']};
            }}

            QSlider::sub-page:horizontal {{
                background: {accent};
                border-radius: 10px;
            }}

            QSlider::add-page:horizontal {{
                background: {C['border']};
                border-radius: 10px;
            }}

            QSlider::handle:horizontal {{
                width: 34px;
                height: 34px;
                margin: -8px 0;
                border-radius: 17px;
                background: white;
                border: 4px solid {accent};
            }}
            """
        )

        self._value_lbl = QLabel("25%")

        self._value_lbl.setFixedWidth(66)
        self._value_lbl.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self._value_lbl.setFont(
            QFont("Segoe UI", 17, QFont.Bold)
        )

        self._value_lbl.setStyleSheet(
            f"""
            color: {accent};
            background: transparent;
            """
        )

        self.slider.valueChanged.connect(
            lambda v: self._value_lbl.setText(f"{v}%")
        )

        layout.addWidget(badge)
        layout.addWidget(text_label)
        layout.addWidget(self.slider, stretch=1)
        layout.addWidget(self._value_lbl)

    def value(self):
        return self.slider.value()

    def reset(self):
        self.slider.setValue(25)


# ============================================================
# PAGE
# ============================================================

class InvestmentPage(BasePage):

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        pixmap = QPixmap(BG_PATH)

        if not pixmap.isNull():

            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )

            x = (
                self.width() - scaled.width()
            ) // 2

            y = (
                self.height() - scaled.height()
            ) // 2

            painter.drawPixmap(
                x,
                y,
                scaled,
            )

        painter.end()

        super().paintEvent(event)

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    def _build_page(self):

        layout = self._root_layout

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.setSpacing(0)

        container = QWidget(self)

        container.setStyleSheet(
            "background: transparent;"
        )

        c_layout = QVBoxLayout(container)

        c_layout.setContentsMargins(
            0, 0, 0, 0
        )

        c_layout.setSpacing(0)

        layout.addWidget(container)

        hdr = self._add_header(
            show_back=True
        )

        hdr.set_center(
            "💼 LE BON INVESTISSEMENT"
        )

        self._team_banner = (
            self._add_team_banner()
        )

        self._timer = CircularTimer(
            duration=INVESTMENT_ALLOCATION_DURATION,
            size=88,
        )

        self._timer.timeout.connect(
            self._on_timeout
        )

        self._boxes = (
            self._build_scoreboard(
                self._timer
            )
        )

        # ----------------------------------------------------
        # ROUND LABEL
        # ----------------------------------------------------

        self._round_lbl = QLabel(
            "Trimestre 1 / 3"
        )

        self._round_lbl.setAlignment(
            Qt.AlignCenter
        )

        self._round_lbl.setFixedHeight(30)

        self._round_lbl.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        self._round_lbl.setStyleSheet(
            f"""
            color: {C['primary']};
            background-color: white;
            border: 1px solid {C['border']};
            border-radius: 15px;
            padding: 0 18px;
            """
        )

        self._round_lbl.setGraphicsEffect(
            _make_shadow(
                blur=10,
                dy=2,
                alpha=40,
            )
        )

        self._root_layout.addSpacing(6)

        self._root_layout.addWidget(
            self._round_lbl,
            0,
            Qt.AlignHCenter,
        )

        self._root_layout.addSpacing(6)

        # ----------------------------------------------------
        # CONTENT CARD
        # ----------------------------------------------------

        self._content_card = QFrame()

        self._content_card.setObjectName(
            "investCard"
        )

        self._content_card.setStyleSheet(
            f"""
            QFrame#investCard {{
                background-color:
                    rgba(255, 255, 255, 0.95);

                border-top:
                    6px solid {C['primary']};

                border-radius: 22px;
            }}
            """
        )

        self._content_card.setGraphicsEffect(
            _make_shadow(
                blur=30,
                dy=9,
                alpha=75,
            )
        )

        card_outer = QVBoxLayout()

        card_outer.setContentsMargins(
            28, 10, 28, 28
        )

        card_outer.addWidget(
            self._content_card
        )

        self._root_layout.addLayout(
            card_outer,
            stretch=1,
        )

        self._content_layout = QVBoxLayout(
            self._content_card
        )

        self._content_layout.setAlignment(
            Qt.AlignTop
        )

        self._content_layout.setContentsMargins(
            32, 24, 32, 24
        )

        self._content_layout.setSpacing(14)

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    @staticmethod
    def _clear_layout(layout):

        while layout.count():

            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:

                widget.hide()
                widget.deleteLater()

                continue

            child_layout = item.layout()

            if child_layout is not None:

                InvestmentPage._clear_layout(
                    child_layout
                )

                child_layout.setParent(None)

    def _clear_content(self):

        self._clear_layout(
            self._content_layout
        )

    # ========================================================
    # GAME START
    # ========================================================

    def on_show(self, **kwargs):

        self._match = (
            self.mw.tc.current_match
        )

        self._match._turn_index = 0

        self._scenarios = (
            self.mw.tc.get_investment_slice()
        )

        self._round_idx = 0

        self._cumulative = {
            self._match.team1.key: 0,
            self._match.team2.key: 0,
        }

        self._update_scores(
            self._boxes
        )

        self._start_round()

    # ========================================================
    # ROUND
    # ========================================================

    def _start_round(self):

        self._scenario = (
            self._scenarios[
                self._round_idx
            ]
        )

        self._allocations = {}

        self._round_lbl.setText(
            f"Trimestre "
            f"{self._round_idx + 1} / "
            f"{len(self._scenarios)}"
        )

        self._start_allocation(
            self._match.team1
        )

    # ========================================================
    # ALLOCATION
    # ========================================================

    def _start_allocation(self, team):

        self._alloc_team = team

        self._alloc_submitted = False

        self._clear_content()

        self._timer.stop()

        self._refresh_team_banner()

        title = QLabel(
            f"{team.name} — "
            f"Répartissez votre capital"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Bold,
            )
        )

        title.setStyleSheet(
            f"""
            color: {C['primary']};
            background: transparent;
            """
        )

        warn = QLabel(
            "⚠️ L'équipe adverse ne doit "
            "pas voir votre répartition !"
        )

        warn.setAlignment(
            Qt.AlignCenter
        )

        warn.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold,
            )
        )

        warn.setStyleSheet(
            f"""
            color: {C['error']};
            background-color:
                {C['error_bg']};

            border-radius: 10px;

            padding:
                6px 14px;
            """
        )

        # ----------------------------------------------------
        # SCENARIO
        # ----------------------------------------------------

        scenario_box = QFrame()

        scenario_box.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: none;
                border-left:
                    6px solid {C['primary']};
                border-radius: 14px;
            }}
            """
        )

        scenario_box.setGraphicsEffect(
            _make_shadow(
                blur=16,
                dy=4,
                alpha=35,
            )
        )

        sb_layout = QHBoxLayout(
            scenario_box
        )

        sb_layout.setContentsMargins(
            18, 14, 18, 14
        )

        sb_layout.setSpacing(16)

        s_icon = QLabel("📈")

        s_icon.setFont(
            QFont("Segoe UI", 30)
        )

        s_icon.setAlignment(
            Qt.AlignCenter
        )

        s_icon.setStyleSheet(
            "background: transparent;"
        )

        s_text_col = QVBoxLayout()

        s_text_col.setSpacing(4)

        s_title = QLabel(
            self._scenario["title"]
        )

        s_title.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold,
            )
        )

        s_title.setWordWrap(True)

        s_title.setStyleSheet(
            f"""
            color: {C['text_dark']};
            background: transparent;
            """
        )

        s_desc = QLabel(
            self._scenario["description"]
        )

        s_desc.setFont(
            QFont(
                "Segoe UI",
                11
            )
        )

        s_desc.setWordWrap(True)

        s_desc.setStyleSheet(
            f"""
            color: {C['text_med']};
            background: transparent;
            """
        )

        s_text_col.addWidget(
            s_title
        )

        s_text_col.addWidget(
            s_desc
        )

        sb_layout.addWidget(
            s_icon
        )

        sb_layout.addLayout(
            s_text_col,
            stretch=1,
        )

        # ----------------------------------------------------
        # SLIDERS
        # ----------------------------------------------------

        self._sliders = {}

        posts_col = QVBoxLayout()

        posts_col.setSpacing(10)

        for key, emoji, label in POSTS:

            accent = _accent_for(key)

            row = _PostRow(
                emoji,
                label,
                accent,
            )

            row.reset()

            row.slider.valueChanged.connect(
                self._update_total
            )

            self._sliders[key] = row

            posts_col.addWidget(row)

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        self._total_lbl = QLabel(
            "Total : 100%"
        )

        self._total_lbl.setAlignment(
            Qt.AlignCenter
        )

        self._total_lbl.setFixedSize(
            170,
            34,
        )

        self._total_lbl.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold,
            )
        )

        # ----------------------------------------------------
        # BUTTON
        # ----------------------------------------------------

        submit = QPushButton(
            "VALIDER LA RÉPARTITION"
        )

        submit.setFixedSize(
            300,
            54,
        )

        submit.setFont(
            QFont(
                "Segoe UI",
                13,
                QFont.Bold,
            )
        )

        submit.setCursor(
            Qt.PointingHandCursor
        )

        submit.setStyleSheet(
            f"""
            QPushButton {{
                background-color:
                    {C['primary']};

                color: white;

                border-radius: 27px;

                border: none;

                letter-spacing: 1px;
            }}

            QPushButton:hover {{
                background-color:
                    {C['primary_light']};
            }}

            QPushButton:pressed {{
                padding-top: 3px;
            }}

            QPushButton:disabled {{
                background-color:
                    {C['primary_light']};
            }}
            """
        )

        submit.setGraphicsEffect(
            _make_shadow(
                blur=18,
                dy=6,
                alpha=60,
            )
        )

        self._submit_btn = submit

        submit.clicked.connect(
            self._submit_allocation
        )

        self._content_layout.addWidget(
            title
        )

        self._content_layout.addWidget(
            warn,
            alignment=Qt.AlignCenter,
        )

        self._content_layout.addWidget(
            scenario_box
        )

        self._content_layout.addLayout(
            posts_col
        )

        self._content_layout.addWidget(
            self._total_lbl,
            alignment=Qt.AlignCenter,
        )

        self._content_layout.addWidget(
            submit,
            alignment=Qt.AlignCenter,
        )

        self._update_total()

        self._timer.reset(
            INVESTMENT_ALLOCATION_DURATION
        )

        self._timer.start()

    # ========================================================
    # TOTAL
    # ========================================================

    def _update_total(self):

        total = sum(
            s.value()
            for s in self._sliders.values()
        )

        self._total_lbl.setText(
            f"Total : {total}%"
        )

        if total == 100:

            bg = C["success_bg"]
            border = C["success"]
            fg = C["success"]

        else:

            bg = C["error_bg"]
            border = C["error"]
            fg = C["error"]

        self._total_lbl.setStyleSheet(
            f"""
            color: {fg};

            background-color: {bg};

            border:
                1px solid {border};

            border-radius: 17px;
            """
        )

        # Le bouton ne peut être validé que si
        # l'équipe distribue exactement 100%.
        self._submit_btn.setEnabled(
            total == 100
        )

    # ========================================================
    # SUBMIT
    # ========================================================

    def _submit_allocation(self):

        if self._alloc_submitted:
            return

        total = sum(
            s.value()
            for s in self._sliders.values()
        )

        if total != 100:
            return

        self._alloc_submitted = True

        self._submit_btn.setEnabled(
            False
        )

        self._timer.stop()

        self._allocations[
            self._alloc_team.key
        ] = {
            key: s.value()
            for key, s in self._sliders.items()
        }

        if (
            self._alloc_team.key
            == self._match.team1.key
        ):

            self._start_allocation(
                self._match.team2
            )

        else:

            self._reveal_results()

    # ========================================================
    # TIMEOUT
    # ========================================================

    def _on_timeout(self):

        # Si l'équipe n'a pas exactement 100%,
        # on complète automatiquement la répartition
        # avec le poste ayant actuellement le plus petit
        # investissement.

        if self._alloc_submitted:
            return

        values = {
            key: slider.value()
            for key, slider
            in self._sliders.items()
        }

        total = sum(values.values())

        if total < 100:

            difference = 100 - total

            best_key = min(
                values,
                key=values.get
            )

            current = (
                self._sliders[
                    best_key
                ].value()
            )

            self._sliders[
                best_key
            ].slider.setValue(
                current + difference
            )

        elif total > 100:

            difference = total - 100

            best_key = max(
                values,
                key=values.get
            )

            current = (
                self._sliders[
                    best_key
                ].value()
            )

            self._sliders[
                best_key
            ].slider.setValue(
                max(
                    0,
                    current - difference
                )
            )

        self._submit_allocation()

    # ========================================================
    # BUSINESS SIMULATION
    # ========================================================

    def _simulate_company(
        self,
        allocation,
    ):

        scenario = self._scenario

        initial = scenario["initial"]

        effects = scenario["effects"]

        # -----------------------------------------------
        # Etat initial
        # -----------------------------------------------

        company = {
            "cash": float(
                initial["cash"]
            ),

            "clients": float(
                initial["clients"]
            ),

            "reputation": float(
                initial["reputation"]
            ),

            "health": float(
                initial["health"]
            ),

            "growth": float(
                initial["growth"]
            ),
        }

        # -----------------------------------------------
        # Investissement
        # -----------------------------------------------

        budget = initial["cash"]

        for key, percentage in allocation.items():

            # Montant réel investi
            amount = (
                budget
                * percentage
                / 100
            )

            effect = effects[key]

            # Trésorerie
            company["cash"] += (
                amount
                * effect["cash"]
            )

            # Clients
            company["clients"] += (
                percentage
                * effect["clients"]
            )

            # Réputation
            company["reputation"] += (
                percentage
                * effect["reputation"]
            )

            # Santé
            company["health"] += (
                percentage
                * effect["health"]
            )

            # Croissance
            company["growth"] += (
                percentage
                * effect["growth"]
            )

        # -----------------------------------------------
        # EVENT
        # -----------------------------------------------

        event = scenario.get(
            "event"
        )

        if event:

            event_effects = event[
                "effects"
            ]

            company["clients"] += (
                event_effects.get(
                    "clients",
                    0
                )
            )

            company["reputation"] += (
                event_effects.get(
                    "reputation",
                    0
                )
            )

            company["health"] += (
                event_effects.get(
                    "health",
                    0
                )
            )

            company["growth"] += (
                event_effects.get(
                    "growth",
                    0
                )
            )

        # -----------------------------------------------
        # Limites réalistes
        # -----------------------------------------------

        company["cash"] = max(
            0,
            company["cash"]
        )

        company["clients"] = max(
            0,
            company["clients"]
        )

        company["reputation"] = _clamp(
            company["reputation"],
            0,
            100,
        )

        company["health"] = _clamp(
            company["health"],
            0,
            100,
        )

        # -----------------------------------------------
        # SCORE
        # -----------------------------------------------

        # Trésorerie : 0 → 100
        cash_score = _clamp(
            company["cash"]
            / 100000
            * 100,
            0,
            100,
        )

        # Clients : 0 → 100
        initial_clients = max(
            1,
            initial["clients"]
        )

        client_score = _clamp(
            (
                company["clients"]
                / initial_clients
            )
            * 50,
            0,
            100,
        )

        # Score global
        score = (
            company["health"] * 0.30
            +
            company["reputation"] * 0.25
            +
            _clamp(
                50 + company["growth"] * 5,
                0,
                100,
            ) * 0.20
            +
            client_score * 0.15
            +
            cash_score * 0.10
        )

        company["score"] = round(
            score,
            1,
        )

        company["event"] = event

        return company

    # ========================================================
    # RESULT
    # ========================================================

    def _reveal_results(self):

        self._clear_content()

        self._timer.stop()

        team1 = self._match.team1
        team2 = self._match.team2

        alloc1 = self._allocations[
            team1.key
        ]

        alloc2 = self._allocations[
            team2.key
        ]

        result1 = self._simulate_company(
            alloc1
        )

        result2 = self._simulate_company(
            alloc2
        )

        score1 = result1["score"]
        score2 = result2["score"]

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = QLabel(
            "📊 Résultats de la simulation"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Bold,
            )
        )

        title.setStyleSheet(
            f"""
            color: {C['primary']};
            background: transparent;
            """
        )

        # ----------------------------------------------------
        # EVENT
        # ----------------------------------------------------

        event = self._scenario.get(
            "event"
        )

        event_lbl = QLabel()

        if event:

            event_lbl.setText(
                "🚨 "
                + event["title"]
                + "\n"
                + event["description"]
            )

        event_lbl.setAlignment(
            Qt.AlignCenter
        )

        event_lbl.setWordWrap(True)

        event_lbl.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold,
            )
        )

        event_lbl.setStyleSheet(
            f"""
            color: {C['error']};

            background-color:
                {C['error_bg']};

            border-radius: 12px;

            padding:
                8px 16px;
            """
        )

        # ----------------------------------------------------
        # INVESTMENT EFFECTS
        # ----------------------------------------------------

        mult_row = QHBoxLayout()

        mult_row.setAlignment(
            Qt.AlignCenter
        )

        mult_row.setSpacing(10)

        for key, emoji, label in POSTS:

            accent = _accent_for(key)

            amount1 = (
                alloc1[key]
                * 1000
            )

            amount2 = (
                alloc2[key]
                * 1000
            )

            chip = QLabel(
                f"{emoji} {label}\n"
                f"{amount1:,.0f} DH / "
                f"{amount2:,.0f} DH"
            )

            chip.setFont(
                QFont(
                    "Segoe UI",
                    10,
                    QFont.Bold,
                )
            )

            chip.setAlignment(
                Qt.AlignCenter
            )

            chip.setStyleSheet(
                f"""
                color: {accent};

                background-color:
                    white;

                border:
                    1.5px solid {accent};

                border-radius:
                    13px;

                padding:
                    4px 12px;
                """
            )

            mult_row.addWidget(
                chip
            )

        # ----------------------------------------------------
        # RESULT CARDS
        # ----------------------------------------------------

        row = QHBoxLayout()

        row.setSpacing(30)

        row.setAlignment(
            Qt.AlignCenter
        )

        row.addWidget(
            self._make_result_card(
                team1,
                alloc1,
                result1,
            )
        )

        row.addWidget(
            self._make_result_card(
                team2,
                alloc2,
                result2,
            )
        )

        # ----------------------------------------------------
        # WINNER
        # ----------------------------------------------------

        if score1 > score2:

            winner = team1
            loser = team2

        elif score2 > score1:

            winner = team2
            loser = team1

        else:

            winner = None
            loser = None

        # ----------------------------------------------------
        # POINTS
        # ----------------------------------------------------

        if winner is None:

            self.mw.tc.award_points_to(
                team1,
                "investment",
                INVESTMENT_POINTS_TIE,
            )

            self.mw.tc.award_points_to(
                team2,
                "investment",
                INVESTMENT_POINTS_TIE,
            )

            self._cumulative[
                team1.key
            ] += INVESTMENT_POINTS_TIE

            self._cumulative[
                team2.key
            ] += INVESTMENT_POINTS_TIE

            result_msg = (
                f"🤝 Égalité ! "
                f"+{INVESTMENT_POINTS_TIE} pts chacune"
            )

        else:

            self.mw.tc.award_points_to(
                winner,
                "investment",
                INVESTMENT_POINTS_WIN,
            )

            self._cumulative[
                winner.key
            ] += INVESTMENT_POINTS_WIN

            # Le perdant reçoit des points
            # seulement s'il a réussi à maintenir
            # une entreprise suffisamment saine.
            if result1["health"] >= 70 and result2["health"] >= 70:

                loser_pts = (
                    INVESTMENT_POINTS_LOSE_POSITIVE
                )

                self.mw.tc.award_points_to(
                    loser,
                    "investment",
                    loser_pts,
                )

                self._cumulative[
                    loser.key
                ] += loser_pts

            else:

                loser_pts = 0

            result_msg = (
                f"🏆 {winner.name} "
                f"obtient le meilleur score "
                f"business : "
                f"{max(score1, score2):.1f}/100 "
                f"(+{INVESTMENT_POINTS_WIN} pts)"
            )

        self._update_scores(
            self._boxes
        )

        # ----------------------------------------------------
        # RESULT LABEL
        # ----------------------------------------------------

        result_lbl = QLabel(
            result_msg
        )

        result_lbl.setAlignment(
            Qt.AlignCenter
        )

        result_lbl.setWordWrap(True)

        result_lbl.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold,
            )
        )

        result_lbl.setStyleSheet(
            f"""
            color: {C['success']};

            background-color:
                {C['success_bg']};

            border-radius: 12px;

            padding:
                8px 16px;
            """
        )

        # ----------------------------------------------------
        # ADD
        # ----------------------------------------------------

        self._content_layout.addWidget(
            title
        )

        self._content_layout.addWidget(
            event_lbl
        )

        self._content_layout.addLayout(
            mult_row
        )

        self._content_layout.addLayout(
            row
        )

        self._content_layout.addWidget(
            result_lbl,
            alignment=Qt.AlignCenter,
        )

        # Sauvegarder les résultats
        # pour pouvoir les afficher si nécessaire
        self._last_results = {
            team1.key: result1,
            team2.key: result2,
        }

        QTimer.singleShot(
            4500,
            self._next_round,
        )

    # ========================================================
    # RESULT CARD
    # ========================================================

    def _make_bar_row(
        self,
        emoji,
        value,
        maximum,
        accent,
    ):

        row = QHBoxLayout()

        row.setSpacing(10)

        icon = QLabel(
            emoji
        )

        icon.setFixedWidth(26)

        icon.setFont(
            QFont(
                "Segoe UI",
                14,
            )
        )

        icon.setStyleSheet(
            "background: transparent;"
        )

        track = QFrame()

        track.setFixedSize(
            150,
            14,
        )

        track.setStyleSheet(
            f"""
            background-color:
                {C['border']};

            border-radius:
                7px;
            """
        )

        track_layout = QHBoxLayout(
            track
        )

        track_layout.setContentsMargins(
            0, 0, 0, 0
        )

        track_layout.setSpacing(0)

        ratio = (
            value / maximum
            if maximum
            else 0
        )

        ratio = _clamp(
            ratio,
            0,
            1,
        )

        fill = QFrame()

        fill.setFixedWidth(
            max(
                3,
                int(
                    150 * ratio
                ),
            )
        )

        fill.setStyleSheet(
            f"""
            background-color:
                {accent};

            border-radius:
                7px;
            """
        )

        track_layout.addWidget(
            fill
        )

        track_layout.addStretch()

        val = QLabel(
            f"{value:.0f}"
        )

        val.setFixedWidth(
            60
        )

        val.setAlignment(
            Qt.AlignRight
        )

        val.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Bold,
            )
        )

        val.setStyleSheet(
            f"""
            color: {accent};
            background: transparent;
            """
        )

        row.addWidget(
            icon
        )

        row.addWidget(
            track
        )

        row.addWidget(
            val
        )

        return row

    # ========================================================
    # BUSINESS RESULT CARD
    # ========================================================

    def _make_result_card(
        self,
        team,
        allocation,
        result,
    ):

        card = QFrame()

        card.setFixedWidth(
            320
        )

        card.setStyleSheet(
            f"""
            QFrame {{
                background-color:
                    white;

                border:
                    2px solid
                    {C['border']};

                border-radius:
                    16px;
            }}
            """
        )

        card.setGraphicsEffect(
            _make_shadow(
                blur=18,
                dy=5,
                alpha=45,
            )
        )

        v = QVBoxLayout(card)

        v.setContentsMargins(
            18, 16, 18, 16
        )

        v.setSpacing(8)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QHBoxLayout()

        name = QLabel(
            team.name
        )

        name.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold,
            )
        )

        name.setStyleSheet(
            f"""
            color:
                {C['text_dark']};

            background:
                transparent;
            """
        )

        score = result["score"]

        score_color = (
            C["success"]
            if score >= 60
            else C["error"]
        )

        score_badge = QLabel(
            f"{score:.0f}"
        )

        score_badge.setFixedSize(
            56,
            56,
        )

        score_badge.setAlignment(
            Qt.AlignCenter
        )

        score_badge.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold,
            )
        )

        score_badge.setStyleSheet(
            f"""
            background-color:
                white;

            color:
                {score_color};

            border:
                3px solid
                {score_color};

            border-radius:
                28px;
            """
        )

        header.addWidget(
            name
        )

        header.addStretch()

        header.addWidget(
            score_badge
        )

        v.addLayout(
            header
        )

        # ----------------------------------------------------
        # BUSINESS METRICS
        # ----------------------------------------------------

        cash = result["cash"]

        clients = result["clients"]

        reputation = result["reputation"]

        health = result["health"]

        growth = result["growth"]

        # Trésorerie
        v.addLayout(
            self._make_bar_row(
                "💰",
                cash,
                100000,
                C["primary"],
            )
        )

        # Clients
        initial_clients = (
            self._scenario[
                "initial"
            ]["clients"]
        )

        v.addLayout(
            self._make_bar_row(
                "👥",
                clients,
                max(
                    initial_clients * 2,
                    clients,
                    1,
                ),
                C["success"],
            )
        )

        # Réputation
        v.addLayout(
            self._make_bar_row(
                "⭐",
                reputation,
                100,
                C["primary"],
            )
        )

        # Santé
        v.addLayout(
            self._make_bar_row(
                "❤️",
                health,
                100,
                C["error"],
            )
        )

        # Croissance
        growth_display = (
            50 + growth * 5
        )

        v.addLayout(
            self._make_bar_row(
                "📈",
                growth_display,
                100,
                C["text_dark"],
            )
        )

        # ----------------------------------------------------
        # SCORE TEXT
        # ----------------------------------------------------

        score_lbl = QLabel(
            f"🏆 Score business : "
            f"{score:.1f} / 100"
        )

        score_lbl.setAlignment(
            Qt.AlignCenter
        )

        score_lbl.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold,
            )
        )

        score_lbl.setStyleSheet(
            f"""
            color:
                {score_color};

            background:
                transparent;
            """
        )

        v.addWidget(
            score_lbl
        )

        return card

    # ========================================================
    # NEXT ROUND
    # ========================================================

    def _next_round(self):

        self._round_idx += 1

        if (
            self._round_idx
            >= len(self._scenarios)
        ):

            self._finish_match()

        else:

            self._start_round()

    # ========================================================
    # FINISH
    # ========================================================

    def _finish_match(self):

        self._clear_content()

        team1 = self._match.team1

        team2 = self._match.team2

        c1 = self._cumulative[
            team1.key
        ]

        c2 = self._cumulative[
            team2.key
        ]

        if c1 > c2:

            msg_text = (
                f"🏆 {team1.name} "
                f"remporte le duel "
                f"d'investissement !"
            )

        elif c2 > c1:

            msg_text = (
                f"🏆 {team2.name} "
                f"remporte le duel "
                f"d'investissement !"
            )

        else:

            msg_text = (
                "🤝 Égalité parfaite "
                "sur l'ensemble "
                "des trimestres !"
            )

        msg = QLabel(
            msg_text
        )

        msg.setAlignment(
            Qt.AlignCenter
        )

        msg.setWordWrap(True)

        msg.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Bold,
            )
        )

        msg.setStyleSheet(
            f"""
            color:
                {C['success']};

            background:
                transparent;
            """
        )

        self._content_layout.addWidget(
            msg
        )

        QTimer.singleShot(
            3000,
            lambda:
                self.mw.show_page(
                    "menu"
                ),
        )