"""
pages/difference_page.py — Difference Game + HELP / JOKER system
Logique originale (5 essais, évaluation groupée, scaling coordonnées)
+ Timer synchronisé + auto-avance 2s + HELP/JOKER
"""
import os, math, re
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui     import (QFont, QPixmap, QPainter, QPen, QColor,
                              QBrush, QLinearGradient, QPainterPath)
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from widgets.help_popup import HelpPopup, DIFF_HELP_OPTIONS, MAX_HELP_USES
from config import C, TIMER_DURATION, POINTS_CORRECT, DIFF_DIR


BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")

ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"
BLUE_NAME     = "#4f8ef7"
TEXT_MUTED    = "rgba(255,255,255,180)"
_TRANSPARENT  = "background: transparent; border: none; background-color: transparent;"

AUTO_ADVANCE_MS = 2000


# ── Helpers ────────────────────────────────────────────────────────────────────
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


# ── Canvas image avec cercles superposés ──────────────────────────────────────
class ImageCanvas(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._circles = []
        self._original_size = None
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(400, 300)
        self.setStyleSheet(
            "background: rgba(255,255,255,215);"
            "border-radius: 18px;"
            "border: 2px solid rgba(79,142,247,80);"
            "padding: 0px;"
        )

    def set_circles(self, circles):
        self._circles = circles; self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._circles:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for cx, cy, r, color in self._circles:
            c = QColor(color)
            rx, ry = int(r), int(r)
            if self._original_size and self._original_size.width() and self._original_size.height():
                if 0 <= cx <= 1 and 0 <= cy <= 1:
                    cx = cx * self.width()
                    cy = cy * self.height()
                else:
                    scale_x = self.width() / self._original_size.width()
                    scale_y = self.height() / self._original_size.height()
                    cx = cx * scale_x
                    cy = cy * scale_y
                rx = int(r * self.width() / self._original_size.width())
                ry = int(r * self.height() / self._original_size.height())
            halo = QColor(c); halo.setAlpha(40)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(QPoint(int(cx), int(cy)), rx + 18, ry + 18)
            painter.setPen(QPen(c, 3))
            fill = QColor(c); fill.setAlpha(35)
            painter.setBrush(QBrush(fill))
            painter.drawEllipse(QPoint(int(cx), int(cy)), rx + 12, ry + 12)
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


# ── Page Difference ────────────────────────────────────────────────────────────
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

        # ── Header ────────────────────────────────────────────────
        hdr = self._add_header(show_back=True)
        hdr.set_center("DIFFERENCE GAME")
        _make_transparent(hdr)
        _force_labels_blue(hdr)

        # Injecter le bouton HELP dans le header
        self._help_btn = self._make_help_button()
        hdr.layout().insertWidget(hdr.layout().count() - 1, self._help_btn)

        # ── Bandeau équipe ────────────────────────────────────────
        self._team_banner = self._add_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)

        # ── Timer + Scoreboard ────────────────────────────────────
        self._timer = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes = self._build_scoreboard(self._timer)
        for i in range(self._root_layout.count()):
            item = self._root_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, (QFrame, QWidget)):
                    _make_transparent(w)
                    _force_labels_blue(w)

        # ── Infos section + compteur ──────────────────────────────
        info_row = QHBoxLayout()
        info_row.setAlignment(Qt.AlignCenter)
        info_row.setSpacing(30)
        info_row.setContentsMargins(0, 2, 0, 2)

        self._section_lbl = QLabel("Image 1 / 10")
        self._section_lbl.setFont(QFont("Segoe UI", 11))
        self._section_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        self._count_lbl = QLabel("0 / 5 tries")
        self._count_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._count_lbl.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")

        info_row.addWidget(self._section_lbl)
        info_row.addWidget(self._count_lbl)
        self._root_layout.addLayout(info_row)

        # Label info HELP — caché par défaut
        self._help_info_lbl = QLabel("")
        self._help_info_lbl.setAlignment(Qt.AlignCenter)
        self._help_info_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._help_info_lbl.setWordWrap(True)
        self._help_info_lbl.setFixedHeight(32)
        self._help_info_lbl.setStyleSheet(
            "background: rgba(255,255,255,220); border-radius: 10px;"
            " padding: 4px 14px; color: #27ae60; font-weight: bold;"
        )
        self._help_info_lbl.setVisible(False)
        self._root_layout.addWidget(self._help_info_lbl)

        # ── Zone images ───────────────────────────────────────────
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

        # ── Bouton centré ─────────────────────────────────────────
        self._reveal_btn = _ActionButton(
            "VOIR TOUTES LES RÉPONSES", "👁",
            color="#6b7280", bg_color="#6b7280"
        )
        self._reveal_btn.clicked.connect(self._reveal_all)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(80, 4, 80, 8)   # marges larges = centré visuellement
        btn_row.addWidget(self._reveal_btn)
        self._root_layout.addLayout(btn_row)

        # ── Timer d'auto-avance (singleShot, partagé) ─────────────
        self._advance_timer = QTimer(self)
        self._advance_timer.setSingleShot(True)
        self._advance_timer.timeout.connect(self._advance_to_next)

        # ── État ──────────────────────────────────────────────────
        self._diffs          = []
        self._d_idx          = 0
        self._found_set      = set()
        self._answered       = False
        self._circles_right  = []
        self._blue_circles   = []
        self._tries          = 0

    # =========================================================================
    # HELP BUTTON — fabrique
    # =========================================================================
    def _make_help_button(self) -> QPushButton:
        btn = QPushButton("🎯  JOKER")
        btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn.setFixedHeight(44)
        btn.setMinimumWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton {"
            f" background: rgba(79,142,247,35); color: {ACCENT_BLUE};"
            f" border: 2px solid {ACCENT_BLUE};"
            "  border-radius: 12px; padding: 0 14px; font-weight: bold; }"
            "QPushButton:hover { background: rgba(79,142,247,70); }"
            "QPushButton:disabled { background: rgba(150,150,150,20);"
            " color: #aaaaaa; border-color: #aaaaaa; }"
        )
        btn.clicked.connect(self._open_help)
        return btn

    def _update_help_btn(self):
        self._help_btn.setEnabled(not self._answered)

    # =========================================================================
    # LOGIQUE PRINCIPALE
    # =========================================================================
    def on_show(self, **kwargs):
        self._diffs          = self.mw.tc.get_diff_slice()
        self._d_idx          = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._update_help_btn()
        self._load_diff()

    def _load_diff(self):
        if self._d_idx >= len(self._diffs):
            self.mw.show_page("menu")
            return

        # 1. Stopper tous les timers
        self._stop_all_timers()

        # 2. Réinitialiser l'état
        self._found_set     = set()
        self._circles_right = []
        self._answered      = False
        self._blue_circles  = []
        self._tries         = 0
        self._help_info_lbl.setVisible(False)

        diff = self._diffs[self._d_idx]
        team = self.mw.tc.current_team
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._update_help_btn()

        self._section_lbl.setText(
            f"Image {self._d_idx + 1} / {len(self._diffs)}  ·  Tour : {team.name}"
        )
        self._count_lbl.setText("0 / 5 tries")
        self._count_lbl.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")

        def load_img(fname, widget):
            path = os.path.join(DIFF_DIR, fname)
            pix  = QPixmap(path)
            if pix.isNull():
                widget.setPixmap(QPixmap())
                widget.setText("Image manquante")
                widget._original_size = None
            else:
                widget.setPixmap(pix)
                widget.setText("")
                widget._original_size = pix.size()

        load_img(diff["left"],  self._cv_left)
        load_img(diff["right"], self._cv_right)
        self._cv_left.set_circles([])
        self._cv_right.set_circles([])

        # 3. Réactiver le bouton
        self._reveal_btn.setEnabled(True)

        # 4. Démarrer le chronomètre (reset PUIS start)
        self._timer.reset(TIMER_DURATION)
        self._timer.start()
        self.mw.audio.play("tension")

    def _on_image_click(self, event):
        if self._tries >= 5 or self._answered:
            return
        x, y = event.pos().x(), event.pos().y()

        if self._cv_right._original_size:
            scale_x = self._cv_right.width() / self._cv_right._original_size.width()
            scale_y = self._cv_right.height() / self._cv_right._original_size.height()
            orig_x = x / scale_x
            orig_y = y / scale_y
        else:
            orig_x, orig_y = x, y

        self._blue_circles.append((orig_x, orig_y))
        self._tries += 1
        self._count_lbl.setText(f"{self._tries} / 5 tries")

        if self._tries == 5:
            self._evaluate_tries()
        else:
            self._update_blue_circles()

    def _update_blue_circles(self):
        self._cv_right.set_circles(
            [(bx, by, 0, "#4f8ef7") for bx, by in self._blue_circles]
        )

    def _evaluate_tries(self):
        """Point d'entrée unique pour les résultats. Verrou _answered."""
        if self._answered:
            return
        self._answered = True
        self._stop_all_timers()
        self.mw.audio.stop()
        self._help_btn.setEnabled(False)

        diff = self._diffs[self._d_idx]
        evaluated = []
        hits = 0
        hit_diffs = set()

        for bx, by in self._blue_circles:
            hit = False
            for i, (cx, cy, r) in enumerate(diff["diffs"]):
                if self._cv_right._original_size and 0 <= cx <= 1 and 0 <= cy <= 1:
                    cx = cx * self._cv_right._original_size.width()
                    cy = cy * self._cv_right._original_size.height()
                if i not in hit_diffs and math.hypot(bx - cx, by - cy) <= r + 22:
                    hit = True; hits += 1; hit_diffs.add(i); break
            evaluated.append((bx, by, 0, C["success"] if hit else C["error"]))

        self._cv_right.set_circles(evaluated)
        self._cv_left.set_circles(
            [(cx, cy, r, C["success"]) for cx, cy, r in diff["diffs"]]
        )

        for _ in range(hits):
            self.mw.tc.answer("diff", True)
        self._update_scores(self._boxes)

        self.mw.tc.next_turn()
        self._refresh_team_banner()
        _force_labels_blue(self._team_banner)

        self._reveal_btn.setEnabled(False)

        # Auto-avance — next_turn() déjà appelé donc l'autre équipe joue ensuite
        self._advance_timer.stop()
        self._advance_timer.start(AUTO_ADVANCE_MS)

    def _reveal_all(self):
        if not self._answered:
            self._evaluate_tries()

    def _on_timeout(self):
        if not self._answered:
            self._evaluate_tries()

    def _advance_to_next(self):
        self._d_idx += 1
        self._load_diff()

    def _next_diff(self):
        self._advance_timer.stop()
        self._d_idx += 1
        self._load_diff()

    # =========================================================================
    # HELP SYSTEM
    # =========================================================================
    def _open_help(self):
        if self._answered:
            return
        # Pause complète
        self._stop_all_timers()
        self.mw.audio.stop()
        self._help_btn.setEnabled(False)

        popup = HelpPopup(self, DIFF_HELP_OPTIONS, 0)
        popup.option_chosen.connect(self._apply_help)
        popup.cancelled.connect(self._resume_after_help)

    def _apply_help(self, option_id: str):
        self._update_help_btn()

        if   option_id == "skip":     self._help_skip()
        elif option_id == "teammate": self._help_teammate()

    def _resume_after_help(self):
        """Reprend le jeu si le joueur annule le popup."""
        if not self._answered:
            self._timer.start()
            self.mw.audio.play("tension")
            self._update_help_btn()

    # ── Actions spécifiques ───────────────────────────────────────
    def _help_skip(self):
        """
        Passe l'image sans changer d'équipe.
        next_turn() n'est PAS appelé → la même équipe continue sur l'image suivante.
        """
        self._d_idx += 1
        self._load_diff()

    def _help_teammate(self):
        self._show_help_info("🤝 Discussion autorisée ! Concertez-vous...", "#27ae60")
        self._timer.start()
        self.mw.audio.play("tension")

    # ── Feedback visuel ───────────────────────────────────────────
    def _show_help_info(self, msg: str, color: str = "#27ae60"):
        self._help_info_lbl.setText(msg)
        self._help_info_lbl.setStyleSheet(
            f"background: rgba(255,255,255,220); border-radius: 10px;"
            f" padding: 4px 14px; color: {color}; font-weight: bold;"
        )
        self._help_info_lbl.setVisible(True)
        QTimer.singleShot(4000, lambda: self._help_info_lbl.setVisible(False))

    # ── Utilitaires ───────────────────────────────────────────────
    def _stop_all_timers(self):
        """Stoppe les deux timers de la page — toujours avant reset/start."""
        self._timer.stop()
        self._advance_timer.stop()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())