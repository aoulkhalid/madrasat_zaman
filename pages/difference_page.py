"""
pages/difference_page.py — Difference Game
Timer synchronisé — gestion propre QTimer — auto-avance après résultats
"""
import os, math, re
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QPoint, QTimer
from PyQt5.QtGui     import (QFont, QPixmap, QPainter, QPen, QColor,
                              QBrush, QLinearGradient, QPainterPath)
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, DIFF_DIR

BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")

ACCENT_BLUE  = "#4f8ef7"
BLUE_NAME    = "#4f8ef7"
TEXT_MUTED   = "rgba(255,255,255,180)"
_TRANSPARENT = "background: transparent; border: none; background-color: transparent;"

# Délai (ms) avant de passer automatiquement à l'image suivante
AUTO_ADVANCE_MS = 2000


# ── Helpers ───────────────────────────────────────────────────────────────────
def _make_transparent(widget):
    widget.setStyleSheet(_TRANSPARENT)
    widget.setAttribute(Qt.WA_TranslucentBackground, True)
    for child in widget.findChildren(QWidget):
        if isinstance(child, QLabel):
            old   = child.styleSheet()
            clean = re.sub(r'background(-color)?\s*:[^;]+;?', '', old)
            child.setStyleSheet(clean + " background: transparent;")
        else:
            child.setStyleSheet(_TRANSPARENT)
            child.setAttribute(Qt.WA_TranslucentBackground, True)


def _force_labels_blue(widget):
    for child in widget.findChildren(QLabel):
        child.setStyleSheet(
            child.styleSheet()
            + f" color: {BLUE_NAME}; font-weight: bold; background: transparent;"
        )


# ── Fond ──────────────────────────────────────────────────────────────────────
class _Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_pixmap = QPixmap(BG_PATH)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        if not self._bg_pixmap.isNull():
            p.drawPixmap(0, 0,
                self._bg_pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#dde6ed"))
            grad.setColorAt(1.0, QColor("#d6e3ec"))
            p.fillRect(self.rect(), QBrush(grad))
        p.fillRect(self.rect(), QColor(0, 0, 0, 30))
        lg = QLinearGradient(0, 0, w, 0)
        lg.setColorAt(0.0,  QColor(79, 142, 247, 0))
        lg.setColorAt(0.35, QColor(79, 142, 247, 160))
        lg.setColorAt(0.65, QColor(168, 85, 247, 160))
        lg.setColorAt(1.0,  QColor(168, 85, 247, 0))
        p.setPen(QPen(QBrush(lg), 2))
        p.drawLine(0, 2, w, 2)


# ── Canvas image ──────────────────────────────────────────────────────────────
class ImageCanvas(QLabel):
    """QLabel avec superposition de cercles, coordonnées scalées automatiquement."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._circles       = []      # [(orig_x, orig_y, r, color), ...]
        self._original_size = None    # QSize de l'image source
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(400, 300)
        self.setStyleSheet(
            "background: rgba(255,255,255,215);"
            "border-radius: 18px;"
            "border: 2px solid rgba(79,142,247,80);"
        )

    def set_image(self, path: str):
        """Charge une image et mémorise sa taille originale pour le scaling."""
        pix = QPixmap(path)
        if pix.isNull():
            self.setPixmap(QPixmap())
            self.setText("Image manquante")
            self._original_size = None
        else:
            self.setPixmap(pix)
            self.setText("")
            self._original_size = pix.size()

    def set_circles(self, circles):
        """circles = [(orig_x, orig_y, r, color), ...]"""
        self._circles = list(circles)
        self.update()

    def clear_circles(self):
        self._circles = []
        self.update()

    def _to_widget_coords(self, ox, oy):
        """Coordonnées image originale → coordonnées widget affiché."""
        if self._original_size and self._original_size.width() > 0:
            sx = self.width()  / self._original_size.width()
            sy = self.height() / self._original_size.height()
            return int(ox * sx), int(oy * sy)
        return int(ox), int(oy)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._circles:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for ox, oy, r, color in self._circles:
            wx, wy = self._to_widget_coords(ox, oy)
            c = QColor(color)
            halo = QColor(c); halo.setAlpha(40)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(QPoint(wx, wy), r + 18, r + 18)
            painter.setPen(QPen(c, 3))
            fill = QColor(c); fill.setAlpha(35)
            painter.setBrush(QBrush(fill))
            painter.drawEllipse(QPoint(wx, wy), r + 12, r + 12)
        painter.end()


# ── Bouton action ─────────────────────────────────────────────────────────────
class _ActionButton(QPushButton):
    def __init__(self, label: str, icon: str, color: str, bg_color: str):
        super().__init__()
        self._label    = label
        self._icon     = icon
        self._color    = QColor(color)
        self._bg_color = QColor(bg_color)
        self.setFixedHeight(52)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        alpha = 255 if (self.underMouse() and self.isEnabled()) else 220
        if not self.isEnabled():
            alpha = 90
        fill = QColor(self._bg_color); fill.setAlpha(alpha)
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), 14, 14)
        p.fillPath(path, QBrush(fill))
        bc = QColor(self._color)
        if not self.isEnabled(): bc.setAlpha(80)
        p.setPen(QPen(bc, 2)); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width()-2, r.height()-2, 14, 14)
        tc = QColor("#ffffff") if self.isEnabled() else QColor(180, 180, 180, 100)
        p.setPen(QPen(tc))
        p.setFont(QFont("Segoe UI", 14, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{self._icon}  {self._label}")

    def enterEvent(self, e): super().enterEvent(e); self.update()
    def leaveEvent(self, e): super().leaveEvent(e); self.update()


# ── Page principale ───────────────────────────────────────────────────────────
class DifferencePage(BasePage):

    def _build_page(self):
        layout = self._root_layout
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Fond
        self._bg = _Background(self)
        self._bg.setGeometry(self.rect())
        self._bg.lower()

        container = QWidget(self)
        container.setAttribute(Qt.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")
        layout.addWidget(container)

        # Header
        hdr = self._add_header(show_back=True)
        hdr.set_center("DIFFERENCE GAME")
        _make_transparent(hdr)
        _force_labels_blue(hdr)

        # Bandeau équipe
        self._team_banner = self._add_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)

        # Timer circulaire + scoreboard
        self._timer = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_countdown_finished)
        self._boxes = self._build_scoreboard(self._timer)
        for i in range(self._root_layout.count()):
            item = self._root_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, (QFrame, QWidget)):
                    _make_transparent(w)
                    _force_labels_blue(w)

        # Infos
        info_row = QHBoxLayout()
        info_row.setAlignment(Qt.AlignCenter)
        info_row.setSpacing(30)
        info_row.setContentsMargins(0, 2, 0, 2)

        self._section_lbl = QLabel("Image 1 / 10")
        self._section_lbl.setFont(QFont("Segoe UI", 11))
        self._section_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        self._count_lbl = QLabel("0 / 5 essais")
        self._count_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._count_lbl.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")

        info_row.addWidget(self._section_lbl)
        info_row.addWidget(self._count_lbl)
        self._root_layout.addLayout(info_row)

        # Zone images
        images_wrap = QFrame()
        images_wrap.setStyleSheet("background: transparent; border: none;")
        images_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        images_v = QVBoxLayout(images_wrap)
        images_v.setContentsMargins(28, 2, 28, 2)
        images_v.setSpacing(6)

        lbl_row = QHBoxLayout()
        lbl_row.setSpacing(16)
        for txt in ("Image originale", "Image modifiée  —  cliquez pour trouver"):
            lbl = QLabel(txt)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
            lbl_row.addWidget(lbl, 1)
        images_v.addLayout(lbl_row)

        canvas_row = QHBoxLayout()
        canvas_row.setSpacing(16)
        self._cv_left  = ImageCanvas()
        self._cv_right = ImageCanvas()
        self._cv_right.setCursor(Qt.CrossCursor)
        self._cv_right.mousePressEvent = self._on_image_click
        canvas_row.addWidget(self._cv_left,  1)
        canvas_row.addWidget(self._cv_right, 1)
        images_v.addLayout(canvas_row, stretch=1)
        self._root_layout.addWidget(images_wrap, stretch=1)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(28, 4, 28, 8)
        btn_row.setSpacing(16)

        self._reveal_btn = _ActionButton(
            "VOIR TOUTES LES RÉPONSES", "👁",
            color="#6b7280", bg_color="#6b7280"
        )
        self._reveal_btn.clicked.connect(self._on_reveal_clicked)

        self._next_btn = _ActionButton(
            "IMAGE SUIVANTE", "→",
            color=C["success"], bg_color=C["success"]
        )
        self._next_btn.clicked.connect(self._on_next_clicked)

        btn_row.addWidget(self._reveal_btn)
        btn_row.addWidget(self._next_btn)
        self._root_layout.addLayout(btn_row)

        # ── Timer d'auto-avance ───────────────────────────────────────────────
        # Un seul QTimer partagé pour toute la durée de vie de la page.
        # Toujours stoppé avant d'être relancé → zéro doublon possible.
        self._advance_timer = QTimer(self)
        self._advance_timer.setSingleShot(True)
        self._advance_timer.timeout.connect(self._advance_to_next)

        # État interne
        self._diffs        = []
        self._d_idx        = 0
        self._blue_circles = []    # [(orig_x, orig_y)] — clics joueur
        self._tries        = 0
        self._round_over   = False  # verrou : True dès que les résultats sont affichés

    # =========================================================================
    # CYCLE DE VIE D'UNE IMAGE
    # =========================================================================

    def on_show(self, **kwargs):
        self._diffs = self.mw.tc.get_diff_slice()
        self._d_idx = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._load_image()

    def _load_image(self):
        """
        Charge l'image courante et démarre un chrono propre.
        Séquence garantie :
          1. Stopper TOUS les timers
          2. Réinitialiser l'état
          3. Mettre à jour l'UI
          4. reset() + start() du CircularTimer
        """
        if self._d_idx >= len(self._diffs):
            self.mw.show_page("menu")
            return

        # 1. Stopper tous les timers sans exception
        self._stop_all_timers()

        # 2. Réinitialiser l'état de la manche
        self._blue_circles = []
        self._tries        = 0
        self._round_over   = False

        diff = self._diffs[self._d_idx]
        team = self.mw.tc.current_team

        # 3. Mettre à jour l'UI
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)

        self._section_lbl.setText(
            f"Image {self._d_idx + 1} / {len(self._diffs)}  ·  Tour : {team.name}"
        )
        self._count_lbl.setText("0 / 5 essais")
        self._count_lbl.setStyleSheet(
            f"color: {ACCENT_BLUE}; background: transparent;"
        )

        # Charger les images et effacer les cercles
        self._cv_left.set_image(os.path.join(DIFF_DIR, diff["left"]))
        self._cv_right.set_image(os.path.join(DIFF_DIR, diff["right"]))
        self._cv_left.clear_circles()
        self._cv_right.clear_circles()

        # Réactiver les boutons
        self._reveal_btn.setEnabled(True)
        self._next_btn.setEnabled(True)

        # 4. Démarrer le chronomètre — reset() PUIS start(), jamais l'inverse
        self._timer.reset(TIMER_DURATION)
        self._timer.start()

        self.mw.audio.play("tension")

    # =========================================================================
    # GESTION DES CLICS
    # =========================================================================

    def _on_image_click(self, event):
        """Enregistre un clic joueur. Au 5ᵉ essai, déclenche l'évaluation."""
        if self._round_over or self._tries >= 5:
            return

        x, y = event.pos().x(), event.pos().y()
        orig_x, orig_y = self._widget_to_orig(self._cv_right, x, y)

        self._blue_circles.append((orig_x, orig_y))
        self._tries += 1
        self._count_lbl.setText(f"{self._tries} / 5 essais")

        # Affichage provisoire des clics en bleu
        self._cv_right.set_circles(
            [(bx, by, 10, "#4f8ef7") for bx, by in self._blue_circles]
        )

        if self._tries >= 5:
            self._show_results()

    # =========================================================================
    # AFFICHAGE DES RÉSULTATS (point d'entrée unique)
    # =========================================================================

    def _show_results(self):
        """
        Stoppe le chrono, évalue les clics, affiche vert/rouge,
        crédite les points, puis planifie l'auto-avance dans AUTO_ADVANCE_MS.

        Le verrou _round_over garantit qu'on n'entre jamais deux fois ici
        pour la même image, quelle que soit la source du déclenchement
        (5 clics, timeout, bouton Révéler).
        """
        if self._round_over:
            return
        self._round_over = True

        # Stopper le décompte et l'audio
        self._stop_all_timers()
        self.mw.audio.stop()

        diff      = self._diffs[self._d_idx]
        true_diffs = diff["diffs"]  # [(cx, cy, r), ...]

        # Évaluer chaque clic
        evaluated   = []
        hits        = 0
        matched_ids = set()

        for bx, by in self._blue_circles:
            hit = False
            for i, (cx, cy, r) in enumerate(true_diffs):
                if i not in matched_ids and math.hypot(bx - cx, by - cy) <= r + 22:
                    hit = True
                    hits += 1
                    matched_ids.add(i)
                    break
            color = C["success"] if hit else C["error"]
            evaluated.append((bx, by, 10, color))

        # Afficher résultats
        self._cv_right.set_circles(evaluated)
        self._cv_left.set_circles(
            [(cx, cy, r, C["success"]) for cx, cy, r in true_diffs]
        )

        # Compteur final
        found = len(matched_ids)
        self._count_lbl.setText(f"{found} / {len(true_diffs)} trouvées")
        self._count_lbl.setStyleSheet(
            f"color: {C['success'] if found == len(true_diffs) else ACCENT_BLUE};"
            " background: transparent;"
        )

        # Créditer les points (5 pts par différence trouvée)
        for _ in range(hits):
            self.mw.tc.answer("diff", True)
        self._update_scores(self._boxes)

        # Changer de tour
        self.mw.tc.next_turn()
        self._refresh_team_banner()
        _force_labels_blue(self._team_banner)

        # Désactiver les boutons pendant la phase de résultats
        self._reveal_btn.setEnabled(False)
        self._next_btn.setEnabled(False)

        # Planifier l'auto-avance (stop() avant start() : règle PyQt5)
        self._advance_timer.stop()
        self._advance_timer.start(AUTO_ADVANCE_MS)

    # =========================================================================
    # CALLBACKS TIMERS
    # =========================================================================

    def _on_countdown_finished(self):
        """Signal CircularTimer.timeout — le temps est écoulé."""
        self._show_results()

    def _advance_to_next(self):
        """
        Déclenché par _advance_timer après AUTO_ADVANCE_MS.
        Passe à l'image suivante (ou retourne au menu si terminé).
        """
        self._d_idx += 1
        self._load_image()

    # =========================================================================
    # CALLBACKS BOUTONS
    # =========================================================================

    def _on_reveal_clicked(self):
        """Bouton 'Voir toutes les réponses' → évaluation immédiate."""
        self._show_results()

    def _on_next_clicked(self):
        """
        Bouton 'Image suivante' → annule l'auto-avance si elle était planifiée,
        puis charge l'image suivante immédiatement.
        """
        self._advance_timer.stop()   # annuler le passage auto en cours
        self._d_idx += 1
        self._load_image()

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def _stop_all_timers(self):
        """
        Arrête proprement TOUS les timers de la page.
        Règle PyQt5 fondamentale : toujours stop() avant tout reset() ou start().
        Sans ça, deux instances du même timer peuvent tourner en parallèle.
        """
        self._timer.stop()           # décompte visuel (CircularTimer)
        self._advance_timer.stop()   # délai d'auto-avance (QTimer)

    def _widget_to_orig(self, canvas: ImageCanvas, wx: int, wy: int):
        """Convertit des coordonnées widget affichées → coordonnées image originale."""
        if canvas._original_size and canvas._original_size.width() > 0:
            sx = canvas._original_size.width()  / canvas.width()
            sy = canvas._original_size.height() / canvas.height()
            return wx * sx, wy * sy
        return float(wx), float(wy)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())