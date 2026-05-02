"""
pages/difference_page.py — Difference Game
Même style moderne que quiz/logo page — fond image, tout transparent, noms bleus
Images maximisées pour bien voir les différences
"""
import os, math, re
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QWidget)
from PyQt5.QtCore    import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui     import (QFont, QPixmap, QPainter, QPen, QColor,
                              QBrush, QLinearGradient, QPainterPath)
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, POINTS_CORRECT, DIFF_DIR


BG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "background2.png")

# ── Palette ────────────────────────────────────────────────────────────────────
ACCENT_BLUE   = "#4f8ef7"
ACCENT_PURPLE = "#a855f7"
BLUE_NAME     = "#4f8ef7"
TEXT_MUTED    = "rgba(255,255,255,180)"
_TRANSPARENT  = "background: transparent; border: none; background-color: transparent;"


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
                self._bg_pixmap.scaled(w, h,
                    Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
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
    """QLabel avec superposition de cercles de différences — style moderne."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._circles = []
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
        self._circles = circles
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._circles:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for cx, cy, r, color in self._circles:
            c = QColor(color)
            # Halo externe
            halo = QColor(c); halo.setAlpha(40)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(QPoint(cx, cy), r + 18, r + 18)
            # Cercle principal
            painter.setPen(QPen(c, 3))
            fill = QColor(c); fill.setAlpha(35)
            painter.setBrush(QBrush(fill))
            painter.drawEllipse(QPoint(cx, cy), r + 12, r + 12)
        painter.end()


# ── Bouton action moderne ──────────────────────────────────────────────────────
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
        radius = 14
        alpha = 255 if (self.underMouse() and self.isEnabled()) else 220
        if not self.isEnabled():
            alpha = 90
        fill = QColor(self._bg_color); fill.setAlpha(alpha)
        path = QPainterPath()
        path.addRoundedRect(0, 0, r.width(), r.height(), radius, radius)
        p.fillPath(path, QBrush(fill))
        border_c = QColor(self._color)
        if not self.isEnabled(): border_c.setAlpha(80)
        p.setPen(QPen(border_c, 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, r.width()-2, r.height()-2, radius, radius)
        text_c = QColor("#ffffff") if self.isEnabled() else QColor(180, 180, 180, 100)
        p.setPen(QPen(text_c))
        p.setFont(QFont("Segoe UI", 14, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{self._icon}  {self._label}")

    def enterEvent(self, e): super().enterEvent(e); self.update()
    def leaveEvent(self, e): super().leaveEvent(e); self.update()


# ── Page principale ────────────────────────────────────────────────────────────
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

        self._count_lbl = QLabel("0 / 5 trouvées")
        self._count_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._count_lbl.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")

        info_row.addWidget(self._section_lbl)
        info_row.addWidget(self._count_lbl)
        self._root_layout.addLayout(info_row)

        # ── Zone images — prend tout l'espace disponible ──────────
        images_wrap = QFrame()
        images_wrap.setStyleSheet("background: black; border: solid black 5px;")
        images_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        images_v = QVBoxLayout(images_wrap)
        images_v.setContentsMargins(28, 2, 28, 2)
        images_v.setSpacing(6)

        # Labels
        lbl_row = QHBoxLayout()
        lbl_row.setSpacing(16)
        for txt in ("Image originale", "Image modifiée  —  cliquez pour trouver"):
            lbl = QLabel(txt)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
            lbl_row.addWidget(lbl, 1)
        images_v.addLayout(lbl_row)

        # Canvas côte à côte
        canvas_row = QHBoxLayout()
        canvas_row.setSpacing(16)

        self._cv_left  = ImageCanvas()
        self._cv_right = ImageCanvas()
        self._cv_right.setCursor(Qt.CrossCursor)
        self._cv_right.mousePressEvent = self._on_image_click

        w = self._cv_left.width()
        h = self._cv_left.height()

        print(w, h)

        canvas_row.addWidget(self._cv_left,  1)
        canvas_row.addWidget(self._cv_right, 1)
        images_v.addLayout(canvas_row, stretch=1)

        self._root_layout.addWidget(images_wrap, stretch=1)

        # ── Boutons ───────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(28, 4, 28, 8)
        btn_row.setSpacing(16)

        self._reveal_btn = _ActionButton(
            "VOIR TOUTES LES RÉPONSES", "👁",
            color="#6b7280", bg_color="#6b7280"
        )
        self._reveal_btn.clicked.connect(self._reveal_all)

        self._next_btn = _ActionButton(
            "IMAGE SUIVANTE", "→",
            color=C["success"], bg_color=C["success"]
        )
        self._next_btn.clicked.connect(self._next_diff)

        btn_row.addWidget(self._reveal_btn)
        btn_row.addWidget(self._next_btn)
        self._root_layout.addLayout(btn_row)

        # État
        self._diffs         = []
        self._d_idx         = 0
        self._found_set     = set()
        self._answered      = False
        self._circles_right = []

    # ── Logique ───────────────────────────────────────────────────
    def on_show(self, **kwargs):
        self._diffs = self.mw.tc.get_diff_slice()
        self._d_idx = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)
        self._load_diff()

    def _load_diff(self):
        if self._d_idx >= len(self._diffs):
            self.mw.show_page("menu")
            return

        self._found_set     = set()
        self._circles_right = []
        self._answered      = False

        diff = self._diffs[self._d_idx]
        team = self.mw.tc.current_team
        self._refresh_team_banner()
        _make_transparent(self._team_banner)
        _force_labels_blue(self._team_banner)
        self._update_scores(self._boxes)

        self._section_lbl.setText(
            f"Image {self._d_idx + 1} / {len(self._diffs)}  ·  Tour : {team.name}"
        )
        self._count_lbl.setText(f"0 / {len(diff['diffs'])} trouvées")
        self._count_lbl.setStyleSheet(f"color: {ACCENT_BLUE}; background: transparent;")

        def load_img(fname, widget):
            path = os.path.join(DIFF_DIR, fname)
            pix  = QPixmap(path)
            if pix.isNull():
                widget.setPixmap(QPixmap())
                widget.setText("Image manquante")
            else:
                widget.setPixmap(pix)
                widget.setText("")

        load_img(diff["left"],  self._cv_left)
        load_img(diff["right"], self._cv_right)
        self._cv_left.set_circles([])
        self._cv_right.set_circles([])
        self._reveal_btn.setEnabled(True)

        self._timer.reset(TIMER_DURATION)
        self._timer.start()

    def _on_image_click(self, event):
        if self._answered:
            return
        diff = self._diffs[self._d_idx]
        x, y = event.pos().x(), event.pos().y()

        for i, (cx, cy, r) in enumerate(diff["diffs"]):
            if i in self._found_set:
                continue
            if math.hypot(x - cx, y - cy) <= r + 22:
                self._found_set.add(i)
                team  = self.mw.tc.current_team
                color = team.color
                self._circles_right.append((cx, cy, r, color))
                self._cv_left.set_circles(
                    [(cx, cy, r, color) for cx, cy, r, color in self._circles_right])
                self._cv_right.set_circles(self._circles_right)
                pts = self.mw.tc.answer("diff", True)
                self._update_scores(self._boxes)
                n = len(diff["diffs"])
                f = len(self._found_set)
                self._count_lbl.setText(f"{f} / {n} trouvées")
                if f == n:
                    self._count_lbl.setStyleSheet(
                        f"color: {C['success']}; background: transparent;")
                    self._answered = True
                    self._timer.stop()
                self.mw.tc.next_turn()
                self._refresh_team_banner()
                _force_labels_blue(self._team_banner)
                break

    def _reveal_all(self):
        self._timer.stop()
        self._answered = True
        diff = self._diffs[self._d_idx]
        all_circles = []
        for i, (cx, cy, r) in enumerate(diff["diffs"]):
            color = C["success"] if i in self._found_set else C["error"]
            all_circles.append((cx, cy, r, color))
        self._cv_left.set_circles(all_circles)
        self._cv_right.set_circles(all_circles)
        n = len(diff["diffs"])
        self._count_lbl.setText(f"{len(self._found_set)} / {n} trouvées")
        self._reveal_btn.setEnabled(False)

    def _on_timeout(self):
        if not self._answered:
            self._reveal_all()

    def _next_diff(self):
        self._timer.stop()
        self._d_idx += 1
        self._load_diff()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(self.rect())