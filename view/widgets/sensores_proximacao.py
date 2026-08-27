# -*- coding: utf-8 -*-
"""
widgets/car_sensors.py

CarSensorsPanel: visao superior (top-down) do veiculo com:
  - ondas de radar de proximidade nos 4 cantos (dianteira/traseira, esq/dir)
  - chips TPMS (pressao dos 4 pneus)

Tudo desenhado com QPainter (leve para o RPi5, sem imagens externas).
So INTERFACE - API publica pronta para os dados reais dos sensores:

    car_panel.set_proximity("fl", 0.8)   # 0 = livre (verde) .. 1 = perigo (vermelho)
    car_panel.set_proximity("fr", 0.3)
    car_panel.set_proximity("rl", 0.1)
    car_panel.set_proximity("rr", 0.5)
    car_panel.set_tire_pressure("fl", 34)   # PSI
"""

import math

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

from view.core.config import Palette, Fonts
from view.widgets.base_do_painel import NeonPanel

# ordem: front-left, front-right, rear-left, rear-right
CORNERS = ("fl", "fr", "rl", "rr")


def _level_color(level: float) -> QColor:
    """Interpola verde -> amarelo -> vermelho conforme o nivel (0..1)."""
    level = max(0.0, min(1.0, level))
    if level < 0.5:
        # verde -> amarelo
        t = level / 0.5
        r = int(Palette.NEON_GREEN.red() + t * (Palette.NEON_YELLOW.red() - Palette.NEON_GREEN.red()))
        g = int(Palette.NEON_GREEN.green() + t * (Palette.NEON_YELLOW.green() - Palette.NEON_GREEN.green()))
        b = int(Palette.NEON_GREEN.blue() + t * (Palette.NEON_YELLOW.blue() - Palette.NEON_GREEN.blue()))
    else:
        # amarelo -> vermelho
        t = (level - 0.5) / 0.5
        r = int(Palette.NEON_YELLOW.red() + t * (Palette.NEON_RED.red() - Palette.NEON_YELLOW.red()))
        g = int(Palette.NEON_YELLOW.green() + t * (Palette.NEON_RED.green() - Palette.NEON_YELLOW.green()))
        b = int(Palette.NEON_YELLOW.blue() + t * (Palette.NEON_RED.blue() - Palette.NEON_YELLOW.blue()))
    return QColor(r, g, b)


class _CarCanvas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(180, 260)
        # valores de exemplo (placeholder visual ate os dados reais chegarem)
        self._proximity = {"fl": 0.2, "fr": 0.5, "rl": 0.75, "rr": 0.3}
        self._tpms = {"fl": None, "fr": None, "rl": None, "rr": None}

    def set_proximity(self, corner, level):
        if corner in self._proximity:
            self._proximity[corner] = max(0.0, min(1.0, level))
            self.update()

    def set_tire_pressure(self, wheel, psi):
        if wheel in self._tpms:
            self._tpms[wheel] = psi
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        car_w = min(w * 0.34, 110)
        car_h = min(h * 0.62, 320)

        self._draw_radars(p, cx, cy, car_w, car_h)
        self._draw_car_body(p, cx, cy, car_w, car_h)
        self._draw_tpms(p, cx, cy, car_w, car_h)

    # -- carro (silhueta simples, vista de cima) -----------------------
    def _draw_car_body(self, p: QPainter, cx, cy, car_w, car_h):
        body_rect = QRectF(cx - car_w / 2, cy - car_h / 2, car_w, car_h)

        pen = QPen(Palette.NEON_CYAN)
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QColor(10, 20, 35, 140))
        p.drawRoundedRect(body_rect, car_w * 0.28, car_w * 0.28)

        # para-brisa (indicacao da frente)
        wind_rect = QRectF(cx - car_w * 0.32, cy - car_h * 0.36, car_w * 0.64, car_h * 0.16)
        p.setPen(QPen(QColor(0, 255, 240, 120), 1))
        p.setBrush(QColor(0, 255, 240, 25))
        p.drawRoundedRect(wind_rect, 6, 6)

        # rodas (4 retangulos)
        wheel_w, wheel_h = car_w * 0.16, car_h * 0.14
        offsets = {
            "fl": (-car_w / 2 - wheel_w * 0.3, -car_h * 0.30),
            "fr": (car_w / 2 - wheel_w * 0.7, -car_h * 0.30),
            "rl": (-car_w / 2 - wheel_w * 0.3, car_h * 0.16),
            "rr": (car_w / 2 - wheel_w * 0.7, car_h * 0.16),
        }
        p.setPen(QPen(Palette.TEXT_DIM, 1))
        p.setBrush(QColor(20, 20, 28))
        for dx, dy in offsets.values():
            p.drawRoundedRect(QRectF(cx + dx, cy + dy, wheel_w, wheel_h), 3, 3)

    # -- radares de proximidade (arcos tipo 'sinal wifi') ----------------
    def _draw_radars(self, p: QPainter, cx, cy, car_w, car_h):
        corner_pos = {
            "fl": (cx - car_w / 2, cy - car_h / 2, 225),   # (x, y, angulo_base_graus)
            "fr": (cx + car_w / 2, cy - car_h / 2, 315),
            "rl": (cx - car_w / 2, cy + car_h / 2, 135),
            "rr": (cx + car_w / 2, cy + car_h / 2, 45),
        }
        for corner, (x, y, base_angle) in corner_pos.items():
            level = self._proximity.get(corner, 0.0)
            color = _level_color(level)
            n_arcs = 3
            max_radius = 34
            for i in range(1, n_arcs + 1):
                radius = max_radius * i / n_arcs
                alpha = int(60 + 130 * (i / n_arcs)) if level > 0.02 else 40
                pen = QPen(QColor(color.red(), color.green(), color.blue(), alpha))
                pen.setWidth(4)
                pen.setCapStyle(Qt.RoundCap)
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                rect = QRectF(x - radius, y - radius, radius * 2, radius * 2)
                # arco de 70 graus centrado no angulo-base (aponta pra fora do carro)
                p.drawArc(rect, int((base_angle - 35) * 16), int(70 * 16))

    # -- chips TPMS (pressao dos pneus) -----------------------------------
    def _draw_tpms(self, p: QPainter, cx, cy, car_w, car_h):
        positions = {
            "fl": (cx - car_w / 2 - 46, cy - car_h * 0.30, Qt.AlignRight),
            "fr": (cx + car_w / 2 + 4, cy - car_h * 0.30, Qt.AlignLeft),
            "rl": (cx - car_w / 2 - 46, cy + car_h * 0.16, Qt.AlignRight),
            "rr": (cx + car_w / 2 + 4, cy + car_h * 0.16, Qt.AlignLeft),
        }
        p.setFont(QFont(Fonts.MONO[0], 8, QFont.DemiBold))
        for wheel, (x, y, align) in positions.items():
            psi = self._tpms.get(wheel)
            text = f"{psi} PSI" if psi is not None else "-- PSI"
            rect = QRectF(x, y, 42, 26)
            p.setPen(QPen(Palette.NEON_GREEN, 1))
            p.setBrush(QColor(5, 1, 15, 200))
            p.drawRoundedRect(rect, 5, 5)
            p.setPen(Palette.TEXT_PRIMARY)
            p.drawText(rect, Qt.AlignCenter, text)


class CarSensorsPanel(NeonPanel):

    def __init__(self, parent=None):
        super().__init__(parent, glow_color=Palette.NEON_MAGENTA, glow_strength=20)
        self.setObjectName("CarSensorsPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        title = QLabel("◈ SENSORES DE PROXIMIDADE")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)

        self._canvas = _CarCanvas()
        layout.addWidget(self._canvas, stretch=1)

    # -- API publica -----------------------------------------------------
    def set_proximity(self, corner: str, level: float):
        self._canvas.set_proximity(corner, level)

    def set_tire_pressure(self, wheel: str, psi):
        self._canvas.set_tire_pressure(wheel, psi)
