"""
widgets/circular_timer.py
Timer circulaire PyQt5 — dessiné avec QPainter
"""
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore    import Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui     import QPainter, QPen, QBrush, QColor, QFont


class CircularTimer(QWidget):
    """Compte à rebours visuel circulaire."""

    timeout = pyqtSignal()
    ticked  = pyqtSignal(int)   # secondes restantes

    def __init__(self, parent=None, duration: int = 35, size: int = 88):
        super().__init__(parent)
        self.duration  = duration
        self.remaining = duration
        self._running  = False
        self._size     = size
        self.setFixedSize(size, size)

        self._qtimer = QTimer(self)
        self._qtimer.setInterval(1000)
        self._qtimer.timeout.connect(self._tick)

    # ── Contrôle ──────────────────────────────────────────────────────────────

    def start(self):
        if not self._running:
            self._running = True
            self._qtimer.start()

    def stop(self):
        self._running = False
        self._qtimer.stop()

    def reset(self, duration: int = None):
        self.stop()
        self.remaining = duration if duration is not None else self.duration
        if duration is not None:
            self.duration = duration
        self.update()

    def _tick(self):
        if self.remaining > 0:
            self.remaining -= 1
            self.ticked.emit(self.remaining)
            self.update()
        else:
            self.stop()
            self.update()
            self.timeout.emit()

    # ── Peinture ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        s = self._size
        p = 9           # padding

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Ombre
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#cdd9e4"))
        painter.drawEllipse(p + 2, p + 2, s - 2*p, s - 2*p)

        # Fond blanc
        painter.setBrush(QColor("white"))
        painter.setPen(QPen(QColor("#cde0ef"), 2))
        painter.drawEllipse(p, p, s - 2*p, s - 2*p)

        # Arc de progression
        if self.remaining > 0 and self.duration > 0:
            fraction = self.remaining / self.duration
            arc_rect = QRect(p + 4, p + 4, s - 2*p - 8, s - 2*p - 8)
            span_deg = int(-fraction * 360 * 16)   # 1/16 de degré
            col = QColor("#0d3b6e") if self.remaining > 10 else QColor("#e74c3c")
            pen = QPen(col, 6)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(arc_rect, 90 * 16, span_deg)

        # Chiffre
        num_color = QColor("#0d3b6e") if self.remaining > 10 else QColor("#e74c3c")
        painter.setPen(num_color)
        painter.setFont(QFont("Arial", 17, QFont.Bold))
        painter.drawText(QRect(0, 0, s, s - 8), Qt.AlignCenter,
                         str(self.remaining))

        # "sec"
        painter.setPen(QColor("#7f8c8d"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(QRect(0, s // 2 + 10, s, 20), Qt.AlignCenter, "sec")
