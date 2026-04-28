"""
pages/difference_page.py — Difference Game
Clic sur les zones interactives, alternance équipes, +5 pts chacune
"""
import os, math
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore    import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui     import QFont, QPixmap, QPainter, QPen, QColor, QBrush
from pages.base_page import BasePage
from widgets.circular_timer import CircularTimer
from config import C, TIMER_DURATION, POINTS_CORRECT, DIFF_DIR


class ImageCanvas(QLabel):
    """QLabel avec superposition de cercles de différences."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._circles = []   # [(cx, cy, r, color)]
        self.setFixedSize(310, 210)
        self.setAlignment(Qt.AlignCenter)

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
            pen = QPen(QColor(color), 3)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(color + "40")))  # transparent fill
            painter.drawEllipse(QPoint(cx, cy), r + 12, r + 12)
        painter.end()


class DifferencePage(BasePage):

    def _build_page(self):
        hdr = self._add_header(show_back=True)
        hdr.set_center("DIFFERENCE GAME")

        self._team_banner = self._add_team_banner()
        self._timer       = CircularTimer(duration=TIMER_DURATION, size=88)
        self._timer.timeout.connect(self._on_timeout)
        self._boxes       = self._build_scoreboard(self._timer)

        # Infos
        info_row = QHBoxLayout()
        info_row.setAlignment(Qt.AlignCenter)
        info_row.setSpacing(30)

        self._section_lbl = QLabel("Image 1 / 10")
        self._section_lbl.setFont(QFont("Arial", 12))
        self._section_lbl.setStyleSheet(f"color: {C['text_light']};")

        self._count_lbl = QLabel("0 / 5 trouvées")
        self._count_lbl.setFont(QFont("Arial", 12, QFont.Bold))
        self._count_lbl.setStyleSheet(f"color: {C['primary']};")

        info_row.addWidget(self._section_lbl)
        info_row.addWidget(self._count_lbl)
        self._root_layout.addLayout(info_row)

        # ── Images côte à côte ──
        img_labels_row = QHBoxLayout()
        img_labels_row.setContentsMargins(36, 0, 36, 0)
        lbl_left = QLabel("Image originale")
        lbl_right = QLabel("Image modifiée — Cliquez pour trouver les différences")
        for l in (lbl_left, lbl_right):
            l.setAlignment(Qt.AlignCenter)
            l.setFont(QFont("Arial", 10))
            l.setStyleSheet(f"color: {C['text_light']};")
            img_labels_row.addWidget(l, 1)
        self._root_layout.addLayout(img_labels_row)

        images_row = QHBoxLayout()
        images_row.setContentsMargins(36, 0, 36, 4)
        images_row.setSpacing(16)

        self._cv_left  = ImageCanvas()
        self._cv_right = ImageCanvas()
        self._cv_right.setCursor(Qt.CrossCursor)
        self._cv_right.mousePressEvent = self._on_image_click

        for cv in (self._cv_left, self._cv_right):
            cv.setStyleSheet(
                f"background: {C['bg_card']}; border: 2px solid {C['border']};"
                f" border-radius: 10px;")

        images_row.addWidget(self._cv_left,  1)
        images_row.addWidget(self._cv_right, 1)
        self._root_layout.addLayout(images_row)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)

        self._reveal_btn = QPushButton("  👁  VOIR TOUTES LES RÉPONSES  ")
        self._reveal_btn.setObjectName("secondary")
        self._reveal_btn.setFixedHeight(42)
        self._reveal_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self._reveal_btn.clicked.connect(self._reveal_all)

        self._next_btn = QPushButton("  → IMAGE SUIVANTE  ")
        self._next_btn.setObjectName("primary")
        self._next_btn.setFixedHeight(42)
        self._next_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self._next_btn.clicked.connect(self._next_diff)

        btn_row.addWidget(self._reveal_btn)
        btn_row.addWidget(self._next_btn)
        self._root_layout.addLayout(btn_row)
        self._root_layout.addStretch()

        # État
        self._diffs          = []
        self._d_idx          = 0
        self._found_set      = set()
        self._answered       = False
        self._circles_right  = []
        self._img_pix_l      = None
        self._img_pix_r      = None

    # ── Logique ───────────────────────────────────────────────────────────────

    def on_show(self, **kwargs):
        self._diffs  = self.mw.tc.get_diff_slice()
        self._d_idx  = 0
        self.mw.tc.current_match._turn_index = 0
        self._refresh_team_banner()
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
        self._update_scores(self._boxes)
        self._section_lbl.setText(
            f"Image {self._d_idx + 1} / {len(self._diffs)}  ·  Tour : {team.name}")
        self._count_lbl.setText(f"0 / {len(diff['diffs'])} trouvées")
        self._count_lbl.setStyleSheet(f"color: {C['primary']};")

        def load_img(fname, widget):
            path = os.path.join(DIFF_DIR, fname)
            pix  = QPixmap(path)
            if pix.isNull():
                widget.setText("Image manquante")
                widget.setPixmap(QPixmap())
            else:
                scaled = pix.scaled(
                    310, 210, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                widget.setPixmap(scaled)
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
                # Miroir sur gauche
                self._cv_left.set_circles(
                    [(cx, cy, r, color) for cx, cy, r, color in self._circles_right])
                self._cv_right.set_circles(self._circles_right)

                pts = self.mw.tc.answer("diff", True)
                self._update_scores(self._boxes)

                n = len(diff["diffs"])
                f = len(self._found_set)
                self._count_lbl.setText(f"{f} / {n} trouvées")
                if f == n:
                    self._count_lbl.setStyleSheet(f"color: {C['success']};")
                    self._answered = True
                    self._timer.stop()

                # Passer au tour suivant
                self.mw.tc.next_turn()
                self._refresh_team_banner()
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
        self._count_lbl.setText(
            f"{len(self._found_set)} / {n} trouvées")
        self._reveal_btn.setEnabled(False)

    def _on_timeout(self):
        if not self._answered:
            self._reveal_all()

    def _next_diff(self):
        self._timer.stop()
        # Reset tour pour que la prochaine image commence à l'équipe correcte
        self._d_idx += 1
        self._load_diff()
