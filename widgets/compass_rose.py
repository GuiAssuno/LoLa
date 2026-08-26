# -*- coding: utf-8 -*-
"""
widgets/compass_rose.py

CompassRose: rosa dos ventos compacta (N/S/E/W) desenhada com QPainter,
usada como overlay no canto do mapa. So estetico/HUD - se quiser refletir
o rumo real do veiculo, chame set_heading(graus).
"""

import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget

from LoLa.core.config import Palette, Fonts


class CompassRose(QWidget):

    def __init__(self, parent=None, diameter=64):
        super().__init__(parent)
        self._diameter = diameter
        self.setFixedSize(diameter, diameter)
        self._heading = 0.0
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_heading(self, degrees: float):
        self._heading = degrees
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        d = self._diameter
        r = d / 2 - 3
        cx, cy = d / 2, d / 2

        # fundo circular semi-transparente
        p.setPen(QPen(QColor(0, 255, 240, 160), 1.5))
        p.setBrush(QColor(5, 1, 15, 190))
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # ticks menores
        pen = QPen(QColor(0, 255, 240, 90))
        pen.setWidth(1)
        p.setPen(pen)
        for i in range(12):
            angle = math.radians(i * 30)
            x1, y1 = cx + (r - 4) * math.sin(angle), cy - (r - 4) * math.cos(angle)
            x2, y2 = cx + r * math.sin(angle), cy - r * math.cos(angle)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # letras cardeais
        p.setFont(QFont(Fonts.DISPLAY[0], 7, QFont.Bold))
        labels = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        for letter, (dx, dy) in labels.items():
            color = Palette.NEON_MAGENTA if letter == "N" else Palette.TEXT_DIM
            p.setPen(color)
            tx = cx + dx * (r - 11) - 5
            ty = cy + dy * (r - 11) + 4
            p.drawText(QRectF(tx, ty - 8, 10, 12), Qt.AlignCenter, letter)

        # agulha (aponta para o heading)
        p.save()
        p.translate(cx, cy)
        p.rotate(self._heading)
        needle_pen = QPen(Palette.NEON_CYAN)
        needle_pen.setWidth(2)
        p.setPen(needle_pen)
        p.drawLine(0, 0, 0, -int(r - 14))
        p.setPen(Qt.NoPen)
        p.setBrush(Palette.NEON_CYAN)
        p.drawEllipse(QRectF(-3, -3, 6, 6))
        p.restore()
