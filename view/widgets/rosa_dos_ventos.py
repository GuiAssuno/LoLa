"""
CompassRose: rosa dos ventos compacta (N/S/E/W) desenhada com QPainter,
usada como overlay no canto do mapa. So estetico/HUD - se quiser refletir
o rumo real do veiculo, chame set_heading(graus).
"""
import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget

from view.core.config import Palette, Fonts


class RosaVentos(QWidget):
    def __init__(self, parent=None, diametro=64):
        super().__init__(parent)
        self._diametro = diametro
        self.setFixedSize(diametro, diametro)
        self._direcao = 0.0
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_heading(self, graus: float):
        self._direcao = graus
        self.update()

    def paintEvent(self, event):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        diametro = self._diametro
        raio = diametro / 2 - 3
        centro_x, centro_y = diametro / 2, diametro / 2

        # fundo circular semi-transparente
        pintor.setPen(QPen(QColor(0, 255, 240, 160), 1.5))
        pintor.setBrush(QColor(5, 1, 15, 190))
        pintor.drawEllipse(QRectF(centro_x - raio, centro_y - raio, raio * 2, raio * 2))

        # ticks menores
        pen = QPen(QColor(0, 255, 240, 90))
        pen.setWidth(1)
        pintor.setPen(pen)
        for i in range(12):
            angulo = math.radians(i * 30)
            x1, y1 = centro_x + (raio - 4) * math.sin(angulo), centro_y - (raio - 4) * math.cos(angulo)
            x2, y2 = centro_x + raio * math.sin(angulo), centro_y - raio * math.cos(angulo)
            pintor.drawLine(int(x1), int(y1), int(x2), int(y2))

        # letras cardeais
        pintor.setFont(QFont(Fonts.DISPLAY[0], 7, QFont.Bold))
        coordenadas = {"N": (0, -1), "S": (0, 1), "L": (1, 0), "O": (-1, 0)}

        for coordenada, (dx, dy) in coordenadas.items():
            cor = Palette.NEON_MAGENTA if coordenada == "N" else Palette.TEXT_DIM
            pintor.setPen(cor)
            tx = centro_x + dx * (raio - 11) - 5
            ty = centro_y + dy * (raio - 11) + 4
            pintor.drawText(QRectF(tx, ty - 8, 10, 12), Qt.AlignCenter, coordenada)

        # agulha aponta para a direcao
        pintor.save()
        pintor.translate(centro_x, centro_y)
        pintor.rotate(self._direcao)
        agulha = QPen(Palette.NEON_CYAN)
        agulha.setWidth(2)
        pintor.setPen(agulha)
        pintor.drawLine(0, 0, 0, -int(raio - 14))
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(Palette.NEON_CYAN)
        pintor.drawEllipse(QRectF(-3, -3, 6, 6))
        pintor.restore()
