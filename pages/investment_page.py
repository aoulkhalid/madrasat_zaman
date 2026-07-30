"""
pages/investment_page.py — Le Bon Investissement

Chaque équipe répartit un capital fictif entre 4 postes (Marketing, R&D,
Recrutement, Dev) sans connaître les rendements cachés du scénario.
Une fois les deux équipes validées, les rendements sont révélés et le
ROI de chaque équipe est calculé et comparé.

ROI = somme(allocation_poste × multiplicateur_poste) / somme(allocations)
"""
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                              QPushButton, QFrame, QWidget, QGridLayout,
                              QGraphicsDropShadowEffect)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor, QPainter, QPixmap

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import (C, INVESTMENT_ROUNDS_PER_MATCH, INVESTMENT_ALLOCATION_DURATION,
                     INVESTMENT_POINTS_WIN, INVESTMENT_POINTS_LOSE_POSITIVE,
                     INVESTMENT_POINTS_TIE)

# NOTE : adapte le nom de fichier si ton image de fond "investissement" porte
# un autre nom dans assets/images. Le paintEvent ci-dessous ne fait rien si
# le fichier est introuvable (pixmap.isNull()), donc aucun risque de crash —
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

POSTS = [
    ("marketing",    "📢", "Marketing"),
    ("rnd",          "🔬", "R&D"),
    ("recrutement",  "👥", "Recrutement"),
    ("dev",          "💻", "Dev"),
]


def _make_shadow(blur=28, dx=0, dy=8, alpha=90):
    """Petit utilitaire pour des ombres portées cohérentes dans toute la page."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    return shadow


def _accent_for(key):
    """Une couleur d'accent par poste, choisie dans la palette existante (C) —
    aucune nouvelle couleur : juste une réutilisation ciblée pour distinguer
    visuellement les 4 postes d'un coup d'œil."""
    return {
        "marketing":   C['primary'],
        "rnd":         C['success'],
        "recrutement": C['error'],
        "dev":         C['text_dark'],
    }.get(key, C['primary'])


class _PostRow(QFrame):
    """Une ligne d'allocation : badge rond coloré + libellé + slider + valeur.

    Remplace l'ancienne grille 2x2 de sliders "OS par défaut" par une liste
    verticale au look plus dashboard : piste pleine largeur, poignée ronde,
    couleur d'accent par poste au lieu du gris uniforme.
    """

    def __init__(self, emoji, label, accent, parent=None):
        super().__init__(parent)
        self._accent = accent
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(22)

        badge = QLabel(emoji)
        badge.setFixedSize(62, 62)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFont(QFont("Segoe UI", 26))
        badge.setStyleSheet(f"""
            background-color: white;
            border: 3px solid {accent};
            border-radius: 31px;
        """)

        text_label = QLabel(label)
        text_label.setFixedWidth(140)
        text_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        text_label.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setSingleStep(5)
        self.slider.setPageStep(5)
        self.slider.setValue(25)
        self.slider.setMinimumHeight(40)
        self.slider.setStyleSheet(f"""
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
        """)

        self._value_lbl = QLabel("25%")
        self._value_lbl.setFixedWidth(66)
        self._value_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._value_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        self._value_lbl.setStyleSheet(f"color: {accent}; background: transparent;")
        self.slider.valueChanged.connect(lambda v: self._value_lbl.setText(f"{v}%"))

        layout.addWidget(badge)
        layout.addWidget(text_label)
        layout.addWidget(self.slider, stretch=1)
        layout.addWidget(self._value_lbl)

    def value(self) -> int:
        return self.slider.value()

    def reset(self):
        self.slider.setValue(25)


class InvestmentPage(BasePage):

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

        hdr = self._add_header(show_back=True)
        hdr.set_center("💼 LE BON INVESTISSEMENT")

        self._team_banner = self._add_team_banner()

        self._timer = CircularTimer(duration=INVESTMENT_ALLOCATION_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)

        # Pastille "Trimestre X / N" — badge pilule au lieu d'un simple texte.
        self._round_lbl = QLabel("Trimestre 1 / 3")
        self._round_lbl.setAlignment(Qt.AlignCenter)
        self._round_lbl.setFixedHeight(30)
        self._round_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._round_lbl.setStyleSheet(f"""
            color: {C['primary']};
            background-color: white;
            border: 1px solid {C['border']};
            border-radius: 15px;
            padding: 0 18px;
        """)
        self._round_lbl.setGraphicsEffect(_make_shadow(blur=10, dy=2, alpha=40))
        self._root_layout.addSpacing(6)
        self._root_layout.addWidget(self._round_lbl, 0, Qt.AlignHCenter)
        self._root_layout.addSpacing(6)

        # Carte de contenu — style "papier" avec bande d'accent en haut,
        # volontairement différent du verre dépoli des autres mini-jeux.
        self._content_card = QFrame()
        self._content_card.setObjectName("investCard")
        self._content_card.setStyleSheet(f"""
            QFrame#investCard {{
                background-color: rgba(255, 255, 255, 0.95);
                border-top: 6px solid {C['primary']};
                border-radius: 22px;
            }}
        """)
        self._content_card.setGraphicsEffect(_make_shadow(blur=30, dy=9, alpha=75))

        card_outer = QVBoxLayout()
        card_outer.setContentsMargins(28, 10, 28, 28)
        card_outer.addWidget(self._content_card)
        self._root_layout.addLayout(card_outer, stretch=1)

        self._content_layout = QVBoxLayout(self._content_card)
        self._content_layout.setAlignment(Qt.AlignTop)
        self._content_layout.setContentsMargins(32, 24, 32, 24)
        self._content_layout.setSpacing(14)

    @staticmethod
    def _clear_layout(layout):
        """Vide récursivement un layout : widgets ET sous-layouts.

        item.widget() renvoie None quand l'item contient un layout imbriqué
        (la grille des sliders et la ligne des cartes de résultat sont
        ajoutées via addLayout()). Ne traiter que les widgets directs
        laissait ces éléments vivants et affichés sous le contenu suivant.
        """
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.deleteLater()
                continue

            child_layout = item.layout()
            if child_layout is not None:
                InvestmentPage._clear_layout(child_layout)
                child_layout.setParent(None)

    def _clear_content(self):
        self._clear_layout(self._content_layout)

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
        # Verrou anti double-soumission : empêche un clic sur "Valider" et le
        # timeout du chrono de valider deux fois la même répartition (ce qui
        # pouvait faire sauter le tour d'une équipe ou dupliquer les données).
        self._alloc_submitted = False
        self._clear_content()
        self._timer.stop()
        self._refresh_team_banner()

        title = QLabel(f"{team.name} — Répartissez votre capital")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {C['primary']}; background: transparent;")

        warn = QLabel("⚠️ L'équipe adverse ne doit pas voir votre répartition !")
        warn.setAlignment(Qt.AlignCenter)
        warn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        warn.setStyleSheet(f"""
            color: {C['error']};
            background-color: {C['error_bg']};
            border-radius: 10px;
            padding: 6px 14px;
        """)

        # Carte scénario façon "ticket" : bande d'accent à gauche + icône,
        # au lieu du bloc centré simple d'origine.
        scenario_box = QFrame()
        scenario_box.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: none;
                border-left: 6px solid {C['primary']};
                border-radius: 14px;
            }}
        """)
        scenario_box.setGraphicsEffect(_make_shadow(blur=16, dy=4, alpha=35))
        sb_layout = QHBoxLayout(scenario_box)
        sb_layout.setContentsMargins(18, 14, 18, 14)
        sb_layout.setSpacing(16)

        s_icon = QLabel("📈")
        s_icon.setFont(QFont("Segoe UI", 30))
        s_icon.setAlignment(Qt.AlignCenter)
        s_icon.setStyleSheet("background: transparent;")

        s_text_col = QVBoxLayout()
        s_text_col.setSpacing(4)

        s_title = QLabel(self._scenario["title"])
        s_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        s_title.setWordWrap(True)
        s_title.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        s_desc = QLabel(self._scenario["description"])
        s_desc.setFont(QFont("Segoe UI", 11))
        s_desc.setWordWrap(True)
        s_desc.setStyleSheet(f"color: {C['text_med']}; background: transparent;")

        s_text_col.addWidget(s_title)
        s_text_col.addWidget(s_desc)

        sb_layout.addWidget(s_icon)
        sb_layout.addLayout(s_text_col, stretch=1)

        # Liste verticale des postes (remplace la grille 2x2 de sliders bruts)
        self._sliders = {}
        posts_col = QVBoxLayout()
        posts_col.setSpacing(10)
        for key, emoji, label in POSTS:
            accent = _accent_for(key)
            row = _PostRow(emoji, label, accent)
            row.reset()
            row.slider.valueChanged.connect(self._update_total)
            self._sliders[key] = row
            posts_col.addWidget(row)

        # Pastille de total au lieu d'un texte brut
        self._total_lbl = QLabel("Total : 100%")
        self._total_lbl.setAlignment(Qt.AlignCenter)
        self._total_lbl.setFixedSize(170, 34)
        self._total_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))

        submit = QPushButton("VALIDER LA RÉPARTITION")
        submit.setFixedSize(300, 54)
        submit.setFont(QFont("Segoe UI", 13, QFont.Bold))
        submit.setCursor(Qt.PointingHandCursor)
        submit.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['primary']};
                color: white;
                border-radius: 27px;
                border: none;
                letter-spacing: 1px;
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
        submit.setGraphicsEffect(_make_shadow(blur=18, dy=6, alpha=60))
        self._submit_btn = submit
        submit.clicked.connect(self._submit_allocation)

        self._content_layout.addWidget(title)
        self._content_layout.addWidget(warn, alignment=Qt.AlignCenter)
        self._content_layout.addWidget(scenario_box)
        self._content_layout.addLayout(posts_col)
        self._content_layout.addWidget(self._total_lbl, alignment=Qt.AlignCenter)
        self._content_layout.addWidget(submit, alignment=Qt.AlignCenter)

        self._update_total()
        self._timer.reset(INVESTMENT_ALLOCATION_DURATION)
        self._timer.start()

    def _update_total(self):
        total = sum(s.value() for s in self._sliders.values())
        self._total_lbl.setText(f"Total : {total}%")
        if total == 100:
            bg, border, fg = C['success_bg'], C['success'], C['success']
        else:
            bg, border, fg = C['error_bg'], C['error'], C['error']
        self._total_lbl.setStyleSheet(f"""
            color: {fg};
            background-color: {bg};
            border: 1px solid {border};
            border-radius: 17px;
        """)

    def _submit_allocation(self):
        if self._alloc_submitted:
            return
        self._alloc_submitted = True
        self._submit_btn.setEnabled(False)

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

        # Multiplicateurs en chips colorées au lieu d'une ligne de texte plate
        mult_row = QHBoxLayout()
        mult_row.setAlignment(Qt.AlignCenter)
        mult_row.setSpacing(10)
        for key, emoji, label in POSTS:
            accent = _accent_for(key)
            chip = QLabel(f"{emoji} ×{self._scenario['multipliers'][key]:.1f}")
            chip.setFont(QFont("Segoe UI", 11, QFont.Bold))
            chip.setAlignment(Qt.AlignCenter)
            chip.setStyleSheet(f"""
                color: {accent};
                background-color: white;
                border: 1.5px solid {accent};
                border-radius: 13px;
                padding: 4px 12px;
            """)
            mult_row.addWidget(chip)

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
        result_lbl.setStyleSheet(f"""
            color: {C['success']};
            background-color: {C['success_bg']};
            border-radius: 12px;
            padding: 8px 16px;
        """)

        self._content_layout.addWidget(title)
        self._content_layout.addLayout(mult_row)
        self._content_layout.addLayout(row)
        self._content_layout.addWidget(result_lbl, alignment=Qt.AlignCenter)

        QTimer.singleShot(3200, self._next_round)

    def _make_bar_row(self, emoji, pct, accent):
        """Une mini barre de répartition (remplace la ligne de texte brute
        "Marketing : 25%") pour un rendu visuel plus lisible d'un coup d'œil."""
        row = QHBoxLayout()
        row.setSpacing(10)

        icon = QLabel(emoji)
        icon.setFixedWidth(26)
        icon.setFont(QFont("Segoe UI", 14))
        icon.setStyleSheet("background: transparent;")

        track = QFrame()
        track.setFixedSize(150, 14)
        track.setStyleSheet(f"background-color: {C['border']}; border-radius: 7px;")
        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(0)
        fill = QFrame()
        fill.setFixedWidth(max(3, int(150 * pct / 100)))
        fill.setStyleSheet(f"background-color: {accent}; border-radius: 7px;")
        track_layout.addWidget(fill)
        track_layout.addStretch()

        val = QLabel(f"{pct}%")
        val.setFixedWidth(42)
        val.setAlignment(Qt.AlignRight)
        val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        val.setStyleSheet(f"color: {accent}; background: transparent;")

        row.addWidget(icon)
        row.addWidget(track)
        row.addWidget(val)
        return row

    def _make_result_card(self, team, allocation, roi):
        card = QFrame()
        card.setFixedWidth(320)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {C['border']};
                border-radius: 16px;
            }}
        """)
        card.setGraphicsEffect(_make_shadow(blur=18, dy=5, alpha=45))
        v = QVBoxLayout(card)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        header = QHBoxLayout()
        name = QLabel(team.name)
        name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name.setStyleSheet(f"color: {C['text_dark']}; background: transparent;")

        roi_color = C['success'] if roi >= 1.0 else C['error']
        roi_badge = QLabel(f"{roi*100:.0f}%")
        roi_badge.setFixedSize(56, 56)
        roi_badge.setAlignment(Qt.AlignCenter)
        roi_badge.setFont(QFont("Segoe UI", 14, QFont.Bold))
        roi_badge.setStyleSheet(f"""
            background-color: white;
            color: {roi_color};
            border: 3px solid {roi_color};
            border-radius: 28px;
        """)

        header.addWidget(name)
        header.addStretch()
        header.addWidget(roi_badge)

        v.addLayout(header)
        for key, emoji, label in POSTS:
            v.addLayout(self._make_bar_row(emoji, allocation[key], _accent_for(key)))

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