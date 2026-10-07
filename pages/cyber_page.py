"""
pages/cyber_page.py — Cyber Investigation

Une seule histoire, deux équipes qui s'affrontent en même temps.
Pour chaque question, le/la modérateur·rice clique sur l'équipe qui a
donné la bonne réponse en premier -> cette équipe gagne +5 points.
Si personne ne trouve : "Personne n'a trouvé" (0 point) et on passe à la suite.

8 questions, un chrono global (CircularTimer) pour toute la partie.
"""
import os

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QFrame, QWidget, QScrollArea, QSizePolicy,
                              QGraphicsDropShadowEffect)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor, QPainter, QPixmap

from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C

BG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "images",
        "background2.png"
    )
).replace("\\", "/")

POINTS_PER_CORRECT_ANSWER = 5
TOTAL_CLUES               = 8
GAME_DURATION             = 180   # secondes pour toute la partie
NEXT_DELAY_MS             = 1400  # pause avant la question suivante
END_DELAY_MS              = 2600  # pause avant de revenir au menu

# ── Tailles pour projecteur (augmente/diminue ici si besoin) ────────────────
FS_COUNTER  = 20    # "Question 3 / 8"
FS_ICON     = 52    # icône de l'indice
FS_TITLE    = 30    # titre de l'indice
FS_CLUE     = 22    # texte de la mise en situation
FS_QUESTION = 34    # la question
FS_BUTTON   = 24    # texte des boutons
FS_ANSWER   = 26    # réponse révélée
FS_SCORE_NAME  = 17 # nom d'équipe dans le scoreboard
FS_SCORE_VALUE = 38 # score dans le scoreboard
BTN_HEIGHT  = 100   # hauteur des boutons
BADGE_SIZE  = 42    # taille des pastilles 1..8
SCOREBAR_HEIGHT = 120  # hauteur de la barre timer + scores


def _make_shadow(blur=28, dx=0, dy=8, alpha=90):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    shadow.setColor(QColor(0, 0, 0, alpha))
    return shadow


def _button_style(color):
    hover = QColor(color).darker(115).name()
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border-radius: 24px;
            border: none;
            padding: 0 22px;
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
    """


class _ClueBadge(QLabel):
    """Pastille numérotée : à venir / en cours / résolue / ratée."""

    def __init__(self, number, px=BADGE_SIZE, parent=None):
        super().__init__(str(number), parent)
        self._px    = px
        self._state = "pending"
        self.setAlignment(Qt.AlignCenter)
        self.set_size(px)

    def set_size(self, px):
        self._px = px
        self.setFixedSize(px, px)
        self.setFont(QFont("Segoe UI", max(9, int(px * 0.34)), QFont.Bold))
        self.set_state(self._state)

    def set_state(self, state: str):
        """state: 'pending' | 'current' | 'solved' | 'skipped'"""
        self._state = state
        if state == "current":
            bg, border, fg = C['primary'], C['primary'], "white"
        elif state == "solved":
            bg, border, fg = C['success'], C['success'], "white"
        elif state == "skipped":
            bg, border, fg = C['error_bg'], C['error'], C['error']
        else:
            bg, border, fg = "white", C['border'], C['text_light']
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border: 3px solid {border};
            border-radius: {self._px // 2}px;
        """)


class CyberPage(BasePage):

    # ── Fond ─────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        pixmap = self._bg_pix
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

    # ── Construction ─────────────────────────────────────────────────────────
    def _build_page(self):
        # État (initialisé avant tout, car hideEvent peut l'utiliser)
        self._bg_pix      = QPixmap(BG_PATH)
        self._match       = None
        self._clues       = []
        self._c_idx       = 0
        self._locked      = False
        self._finished    = False
        self._session     = 0      # invalide les QTimer.singleShot en retard
        self._clue_badges = []
        self._scale       = 0      # facteur d'échelle (taille d'écran)
        self._badge_px    = BADGE_SIZE

        layout = self._root_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = self._add_header(show_back=True)
        hdr.set_center("🕵️ CYBER INVESTIGATION")

        # Timer global + scoreboard
        self._timer = CircularTimer(duration=GAME_DURATION, size=110)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)
        for box in self._boxes.values():
            box._name_lbl.setFont(QFont("Segoe UI", FS_SCORE_NAME, QFont.Bold))
            box._score_lbl.setFont(QFont("Segoe UI", FS_SCORE_VALUE, QFont.Bold))
        # La barre du scoreboard est fixée à 90px dans BasePage : on l'agrandit
        # ici pour que les gros noms/scores ne soient pas coupés.
        self._boxes["s1"].parentWidget().setFixedHeight(SCOREBAR_HEIGHT)

        # ── Barre de progression (compteur + pastilles) ──────────────────────
        prog = QFrame()
        prog.setObjectName("cyberProgress")
        self._prog = prog
        prog.setFixedHeight(76)
        prog.setStyleSheet("""
            QFrame#cyberProgress {
                background-color: rgba(255, 255, 255, 0.90);
                border-radius: 18px;
            }
        """)
        prog.setGraphicsEffect(_make_shadow(blur=18, dy=4, alpha=50))

        prog_l = QHBoxLayout(prog)
        prog_l.setContentsMargins(26, 8, 26, 8)

        self._counter_lbl = QLabel(f"Question 1 / {TOTAL_CLUES}")
        self._counter_lbl.setFont(QFont("Segoe UI", FS_COUNTER, QFont.Bold))
        self._counter_lbl.setStyleSheet(
            f"color: {C['text_med']}; background: transparent; letter-spacing: 1px;"
        )
        prog_l.addWidget(self._counter_lbl)
        prog_l.addStretch()

        self._badges_layout = QHBoxLayout()
        self._badges_layout.setSpacing(10)
        prog_l.addLayout(self._badges_layout)

        prog_outer = QVBoxLayout()
        prog_outer.setContentsMargins(24, 6, 24, 0)
        prog_outer.addWidget(prog)
        self._root_layout.addLayout(prog_outer)

        # ── Carte de contenu (verre dépoli) + scroll de sécurité ─────────────
        card = QFrame()
        card.setObjectName("cyberCard")
        card.setStyleSheet("""
            QFrame#cyberCard {
                background-color: rgba(255, 255, 255, 0.90);
                border-radius: 26px;
            }
        """)
        card.setGraphicsEffect(_make_shadow(blur=32, dy=9, alpha=80))

        card_outer = QVBoxLayout()
        card_outer.setContentsMargins(24, 12, 24, 24)
        card_outer.addWidget(card)
        self._root_layout.addLayout(card_outer, stretch=1)

        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(6, 6, 6, 6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 15);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(13, 59, 110, 150);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(inner)
        self._content_layout.setAlignment(Qt.AlignVCenter)
        self._content_layout.setContentsMargins(36, 14, 36, 14)
        self._content_layout.setSpacing(14)
        scroll.setWidget(inner)
        card_v.addWidget(scroll)

        # Icône + titre de l'indice
        head = QHBoxLayout()
        head.setAlignment(Qt.AlignCenter)
        head.setSpacing(14)

        self._icon_lbl = QLabel("🕵️")
        self._icon_lbl.setFont(QFont("Segoe UI", FS_ICON))
        self._icon_lbl.setStyleSheet("background: transparent;")

        self._title_lbl = QLabel("")
        self._title_lbl.setFont(QFont("Segoe UI", FS_TITLE, QFont.Bold))
        self._title_lbl.setStyleSheet(
            f"color: {C['text_light']}; background: transparent;"
        )

        head.addWidget(self._icon_lbl)
        head.addWidget(self._title_lbl)

        # Mise en situation
        self._clue_lbl = QLabel("")
        self._clue_lbl.setAlignment(Qt.AlignCenter)
        self._clue_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._clue_lbl.setWordWrap(True)
        self._clue_lbl.setFont(QFont("Consolas", FS_CLUE))
        self._clue_lbl.setStyleSheet(f"""
            color: {C['text_dark']};
            background-color: white;
            border: 1px solid {C['border']};
            border-radius: 22px;
            padding: 16px 28px;
        """)
        self._clue_lbl.setGraphicsEffect(_make_shadow(blur=14, dy=3, alpha=35))

        # Question
        self._question_lbl = QLabel("")
        self._question_lbl.setAlignment(Qt.AlignCenter)
        self._question_lbl.setWordWrap(True)
        self._question_lbl.setFont(QFont("Segoe UI", FS_QUESTION, QFont.Bold))
        self._question_lbl.setStyleSheet(
            f"color: {C['primary']}; background: transparent;"
        )

        # Boutons : équipe 1 / équipe 2 / personne
        btn_row = QHBoxLayout()
        btn_row.setSpacing(24)

        self._team1_btn = QPushButton("")
        self._team2_btn = QPushButton("")
        self._none_btn  = QPushButton("❌  Personne n'a trouvé")

        for btn in (self._team1_btn, self._team2_btn, self._none_btn):
            btn.setFixedHeight(BTN_HEIGHT)
            btn.setFont(QFont("Segoe UI", FS_BUTTON, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setGraphicsEffect(_make_shadow(blur=16, dy=5, alpha=55))
            btn_row.addWidget(btn)

        self._none_btn.setStyleSheet(_button_style(C['error']))

        self._team1_btn.clicked.connect(lambda: self._team_wins(self._match.team1))
        self._team2_btn.clicked.connect(lambda: self._team_wins(self._match.team2))
        self._none_btn.clicked.connect(self._nobody)

        # Réponse révélée
        self._answer_lbl = QLabel("")
        self._answer_lbl.setAlignment(Qt.AlignCenter)
        self._answer_lbl.setWordWrap(True)
        self._answer_lbl.setMinimumHeight(96)
        self._answer_lbl.setFont(QFont("Segoe UI", FS_ANSWER, QFont.Bold))
        self._answer_lbl.setStyleSheet(
            f"color: {C['text_med']}; background: transparent;"
        )

        self._content_layout.addLayout(head)
        self._content_layout.addWidget(self._clue_lbl)
        self._content_layout.addWidget(self._question_lbl)
        self._content_layout.addLayout(btn_row)
        self._content_layout.addWidget(self._answer_lbl)

        self._apply_scale(force=True)

    # ── Taille adaptée à l'écran (projecteur 1080p, 768p, ...) ──────────────
    def _apply_scale(self, force=False):
        """Les tailles FS_* / BTN_HEIGHT sont prévues pour 1080p de haut.
        Sur un écran plus petit, tout rétrécit proportionnellement pour
        que la question et les boutons tiennent sans scroll."""
        h = self.height()
        f = max(0.5, min(1.0, ((h if h > 300 else 1080) / 1080) ** 1.4))
        if not force and abs(f - self._scale) < 0.02:
            return
        self._scale = f

        def fs(v):
            return max(9, int(round(v * f)))

        self._counter_lbl.setFont(QFont("Segoe UI", fs(FS_COUNTER), QFont.Bold))
        self._icon_lbl.setFont(QFont("Segoe UI", fs(FS_ICON)))
        self._title_lbl.setFont(QFont("Segoe UI", fs(FS_TITLE), QFont.Bold))
        self._clue_lbl.setFont(QFont("Consolas", fs(FS_CLUE)))
        self._question_lbl.setFont(QFont("Segoe UI", fs(FS_QUESTION), QFont.Bold))
        self._answer_lbl.setFont(QFont("Segoe UI", fs(FS_ANSWER), QFont.Bold))
        self._answer_lbl.setMinimumHeight(int(80 * f))

        for btn in (self._team1_btn, self._team2_btn, self._none_btn):
            btn.setFixedHeight(int(BTN_HEIGHT * f))
            btn.setFont(QFont("Segoe UI", fs(FS_BUTTON), QFont.Bold))

        for box in self._boxes.values():
            box._name_lbl.setFont(QFont("Segoe UI", fs(FS_SCORE_NAME), QFont.Bold))
            box._score_lbl.setFont(QFont("Segoe UI", fs(FS_SCORE_VALUE), QFont.Bold))
        self._boxes["s1"].parentWidget().setFixedHeight(
            max(100, int(SCOREBAR_HEIGHT * f))
        )

        self._prog.setFixedHeight(max(54, int(76 * f)))
        self._badge_px = max(28, int(BADGE_SIZE * f))
        for badge in self._clue_badges:
            badge.set_size(self._badge_px)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_prog"):
            self._apply_scale()

    # ── Cycle de vie ─────────────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._apply_scale()
        self._match    = self.mw.tc.current_match
        self._session += 1
        self._finished = False
        self._locked   = False
        self._c_idx    = 0

        self._load_all_clues()
        self._build_badges()
        self._style_team_buttons()
        self._update_scores(self._boxes)

        self._timer.reset(GAME_DURATION)
        self._timer.start()

        self._load_clue()

    def hideEvent(self, event):
        """Quitter la page (←, menu...) : on coupe tout ce qui tournait."""
        self._session += 1
        self._finished = True
        self._timer.stop()
        super().hideEvent(event)

    # ── Chargement des questions ─────────────────────────────────────────────
    def _load_all_clues(self):
        """Le contrôleur fournit les indices par blocs de 4 : on prend les
        deux blocs (8 questions), sans doublons, dans l'ordre de l'histoire."""
        try:
            from games.cyber_data import ALL_CLUES
        except Exception:
            ALL_CLUES = []

        # Histoire complète : si les données contiennent exactement les 8
        # indices, on les prend TOUS, dans l'ordre (pas de tirage au hasard).
        if len(ALL_CLUES) == TOTAL_CLUES:
            self._clues = list(ALL_CLUES)
            return

        picked, seen = [], set()

        for offset in (0, 4):
            try:
                chunk = self.mw.tc.get_cyber_slice(offset)
            except Exception:
                chunk = []
            for c in chunk:
                if id(c) not in seen:
                    seen.add(id(c))
                    picked.append(c)

        # Compléter si des doublons ont réduit le total
        for c in ALL_CLUES:
            if len(picked) >= TOTAL_CLUES:
                break
            if id(c) not in seen:
                seen.add(id(c))
                picked.append(c)

        picked = picked[:TOTAL_CLUES]

        # Garder l'ordre logique de l'histoire
        order = {id(c): i for i, c in enumerate(ALL_CLUES)}
        picked.sort(key=lambda c: order.get(id(c), 0))

        if len(picked) >= TOTAL_CLUES:
            self._clues = picked
        else:
            self._clues = self._default_story()

    def _default_story(self):
        """Histoire complète de secours (si les données ne suffisent pas)."""
        return [
            {
                "title": "🚨 Une alerte vient de tomber",
                "story": (
                    "Il est 22h03. Le système de sécurité de l'entreprise "
                    "signale une connexion inhabituelle sur le serveur interne. "
                    "Personne de l'équipe informatique n'était censé travailler "
                    "à cette heure."
                ),
                "question": (
                    "Pour commencer l'enquête, quelle information faut-il "
                    "examiner en priorité ?"
                ),
                "answer": "Les journaux de connexion.",
            },
            {
                "title": "📧 Le témoignage de l'employé",
                "story": (
                    "L'équipe interroge ensuite l'employé dont le compte "
                    "apparaît dans les journaux. Il affirme avoir reçu quelques "
                    "heures plus tôt un e-mail semblant provenir du service IT."
                ),
                "question": (
                    "Un e-mail qui demande à l'employé de vérifier son compte "
                    "avec un lien suspect correspond-il à une attaque de phishing ?"
                ),
                "answer": "Oui, c'est du phishing.",
            },
            {
                "title": "🔗 Le lien piégé",
                "story": (
                    "L'équipe récupère l'e-mail. Le lien mène vers une fausse "
                    "page de connexion qui ressemble exactement au portail "
                    "de l'entreprise."
                ),
                "question": (
                    "Le but principal de cette fausse page était-il de récupérer "
                    "les identifiants de l'employé ?"
                ),
                "answer": "Oui, récupérer les identifiants.",
            },
            {
                "title": "🔐 Le compte compromis",
                "story": (
                    "Quelques minutes après que l'employé a utilisé la fausse "
                    "page, une connexion réussie apparaît dans les journaux. "
                    "La connexion utilise exactement son compte."
                ),
                "question": (
                    "Peut-on considérer que le compte de l'employé a été compromis ?"
                ),
                "answer": "Oui, le compte a été compromis.",
            },
            {
                "title": "💻 L'intrusion",
                "story": (
                    "L'analyse continue. Le compte compromis ouvre ensuite une "
                    "session sur le serveur interne depuis une adresse IP inconnue "
                    "du réseau habituel de l'entreprise."
                ),
                "question": (
                    "Cette connexion inhabituelle peut-elle être considérée "
                    "comme une étape de l'intrusion ?"
                ),
                "answer": "Oui, elle constitue une étape de l'intrusion.",
            },
            {
                "title": "📁 Les fichiers sensibles",
                "story": (
                    "Après cette connexion, plusieurs fichiers sont consultés. "
                    "Les journaux montrent notamment l'accès à un dossier contenant "
                    "des contrats clients et des documents financiers."
                ),
                "question": (
                    "L'attaquant a-t-il ciblé des données sensibles de l'entreprise ?"
                ),
                "answer": "Oui, des données sensibles ont été ciblées.",
            },
            {
                "title": "📤 Le transfert",
                "story": (
                    "À 22h21, un fichier archive de grande taille est créé. "
                    "Quelques secondes plus tard, une connexion sortante apparaît "
                    "vers un serveur externe."
                ),
                "question": (
                    "Cette étape correspond-elle à une exfiltration de données ?"
                ),
                "answer": "Oui, il s'agit d'une exfiltration de données.",
            },
            {
                "title": "🧩 La reconstitution finale",
                "story": (
                    "L'enquête est maintenant terminée. Les éléments retrouvés "
                    "permettent de reconstituer toute l'attaque : l'employé reçoit "
                    "un faux e-mail, ses identifiants sont récupérés, puis le compte "
                    "est utilisé pour accéder aux fichiers sensibles avant leur "
                    "transfert vers l'extérieur."
                ),
                "question": (
                    "La chaîne suivante décrit-elle correctement l'attaque : "
                    "phishing → vol d'identifiants → intrusion → accès aux données "
                    "→ exfiltration ?"
                ),
                "answer": (
                    "Oui : phishing → vol d'identifiants → intrusion → "
                    "accès aux données → exfiltration."
                ),
            },
        ]

    # ── Badges ───────────────────────────────────────────────────────────────
    def _build_badges(self):
        while self._badges_layout.count():
            item = self._badges_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.deleteLater()

        self._clue_badges = []
        for i in range(TOTAL_CLUES):
            badge = _ClueBadge(i + 1, self._badge_px)
            self._clue_badges.append(badge)
            self._badges_layout.addWidget(badge)

    def _set_badge_state(self, index, state):
        if 0 <= index < len(self._clue_badges):
            self._clue_badges[index].set_state(state)

    # ── Boutons équipes ──────────────────────────────────────────────────────
    def _style_team_buttons(self):
        t1, t2 = self._match.team1, self._match.team2
        self._team1_btn.setText(f"{t1.emoji}  {t1.name} — VRAI")
        self._team2_btn.setText(f"{t2.emoji}  {t2.name} — VRAI")
        self._team1_btn.setStyleSheet(_button_style(t1.color))
        self._team2_btn.setStyleSheet(_button_style(t2.color))

    # ── Question courante ────────────────────────────────────────────────────
    def _load_clue(self):
        if self._c_idx >= len(self._clues):
            self._finish_game()
            return

        self._locked = False
        clue = self._clues[self._c_idx]

        self._counter_lbl.setText(f"Question {self._c_idx + 1} / {TOTAL_CLUES}")
        self._icon_lbl.setText(clue.get("icon", "🕵️"))
        self._title_lbl.setText(clue.get("title", f"Indice {self._c_idx + 1}"))
        self._clue_lbl.setText(clue.get("story", clue.get("clue", "")))
        self._question_lbl.setText(clue.get("question", ""))
        self._answer_lbl.setText("")
        self._answer_lbl.setStyleSheet(
            f"color: {C['text_med']}; background: transparent;"
        )

        for btn in (self._team1_btn, self._team2_btn, self._none_btn):
            btn.setVisible(True)
            btn.setEnabled(True)

        self._set_badge_state(self._c_idx, "current")

    def _lock_buttons(self):
        for btn in (self._team1_btn, self._team2_btn, self._none_btn):
            btn.setEnabled(False)

    # ── Réponses ─────────────────────────────────────────────────────────────
    def _team_wins(self, team):
        """L'équipe cliquée a trouvé la bonne réponse en premier : +5 pts."""
        if self._locked or self._finished:
            return
        self._locked = True
        self._lock_buttons()

        self.mw.tc.award_points_to(team, "cyber", POINTS_PER_CORRECT_ANSWER)
        self._update_scores(self._boxes)
        self._set_badge_state(self._c_idx, "solved")

        answer = self._clues[self._c_idx].get("answer", "Réponse correcte.")
        self._answer_lbl.setText(
            f"🎉 {team.name} gagne +{POINTS_PER_CORRECT_ANSWER} points !\n✅ {answer}"
        )
        self._answer_lbl.setStyleSheet(
            f"color: {C['success']}; background: transparent;"
        )

        QTimer.singleShot(
            NEXT_DELAY_MS, lambda s=self._session: self._next_clue(s)
        )

    def _nobody(self):
        """Personne n'a trouvé : 0 point, on révèle la réponse et on avance."""
        if self._locked or self._finished:
            return
        self._locked = True
        self._lock_buttons()

        self._set_badge_state(self._c_idx, "skipped")

        answer = self._clues[self._c_idx].get("answer", "")
        self._answer_lbl.setText(f"❌ Personne n'a trouvé\nRéponse : {answer}")
        self._answer_lbl.setStyleSheet(
            f"color: {C['error']}; background: transparent;"
        )

        QTimer.singleShot(
            NEXT_DELAY_MS, lambda s=self._session: self._next_clue(s)
        )

    def _next_clue(self, session=None):
        if session is not None and session != self._session:
            return
        if self._finished:
            return
        self._c_idx += 1
        if self._c_idx >= TOTAL_CLUES:
            self._finish_game()
        else:
            self._load_clue()

    # ── Chrono ───────────────────────────────────────────────────────────────
    def _on_timeout(self):
        if self._finished:
            return
        self._finish_game(timed_out=True)

    # ── Fin de partie ────────────────────────────────────────────────────────
    def _finish_game(self, timed_out=False):
        if self._finished:
            return
        self._finished = True
        self._session += 1          # annule les singleShot en attente
        self._timer.stop()
        self._update_scores(self._boxes)

        t1, t2 = self._match.team1, self._match.team2
        s1, s2 = t1.score, t2.score

        if s1 > s2:
            result = f"🏆 {t1.name} remporte le duel !"
        elif s2 > s1:
            result = f"🏆 {t2.name} remporte le duel !"
        else:
            result = "🤝 Égalité entre les deux équipes !"

        self._icon_lbl.setText("⏱️" if timed_out else "🏁")
        self._title_lbl.setText(
            "TEMPS ÉCOULÉ" if timed_out else "ENQUÊTE TERMINÉE"
        )
        self._clue_lbl.setText(
            f"{result}\n\n{t1.emoji} {t1.name} : {s1} pts\n"
            f"{t2.emoji} {t2.name} : {s2} pts"
        )
        self._question_lbl.setText("L'enquête cyber est terminée.")
        self._answer_lbl.setText("Bravo aux deux équipes !")
        self._answer_lbl.setStyleSheet(
            f"color: {C['success']}; background: transparent;"
        )
        self._counter_lbl.setText(f"Investigation terminée — {TOTAL_CLUES} questions")

        for btn in (self._team1_btn, self._team2_btn, self._none_btn):
            btn.setVisible(False)

        QTimer.singleShot(
            END_DELAY_MS, lambda s=self._session: self._back_to_menu(s)
        )

    def _back_to_menu(self, session=None):
        if session is not None and session != self._session:
            return
        self._timer.stop()
        self._finished = True
        self.mw.show_page("menu")