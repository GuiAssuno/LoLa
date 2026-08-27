# -*- coding: utf-8 -*-
"""
widgets/gauge.py

GaugeWidget: mostrador circular estilo "retro neon" para velocidade,
nivel de combustivel/bateria, RPM, etc. Desenho 100% via QPainter
(nao depende de imagens), o que fica leve no RPi5 e escala perfeitamente
em qualquer resolucao.

Interface publica pensada para quem for plugar os dados reais depois:
    gauge = GaugeWidget(title="VELOCIDADE", unit="km/h", min_value=0, max_value=220)
    gauge.setValue(87)          # atualiza o ponteiro
    gauge.setDangerZone(180)    # opcional: a partir desse valor pinta em vermelho
"""

import math

from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient, QRadialGradient
from PySide6.QtWidgets import QWidget, QSizePolicy

from view.core.config import Palette, Fonts

# Angulo inicial/final do arco (estilo velocimetro automotivo classico)
START_ANGLE = 225   # graus, sentido anti-horario a partir do eixo 3h (convencao Qt)
SPAN_ANGLE = -270    # varre 270 graus no sentido horario


class GaugeWidget(QWidget):

    def __init__(self, title="GAUGE", unit="", min_value=0, max_value=100,
                 color: QColor = None, parent=None):
        super().__init__(parent)
        self._title = title
        self._unit = unit
        self._min = min_value
        self._max = max_value
        self._value = min_value
        self._danger_zone = None
        self._danger_mode = "above"
        self._color = QColor(color or Palette.NEON_CYAN)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(140, 140)

        # precisa existir ANTES de criar o QPropertyAnimation, pois o Qt
        # pode ler a propriedade "animatedValue" assim que ela e registrada
        self._animated_value = self._value

        self._anim = QPropertyAnimation(self, b"animatedValue")
        self._anim.setDuration(350)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    # -- API publica -------------------------------------------------
    def setValue(self, value: float):
        """Atualiza o valor exibido (anima suavemente ate o novo valor)."""
        value = max(self._min, min(self._max, value))
        self._value = value
        self._anim.stop()
        self._anim.setStartValue(self._animated_value)
        self._anim.setEndValue(value)
        self._anim.start()

    def value(self):
        return self._value

    def setDangerZone(self, value_from: float, mode: str = "above"):
        """Define a partir de que valor o gauge fica vermelho.

        mode="above" (padrao): perigo quando o valor >= value_from
                                (ex.: velocidade, RPM, temperatura altos)
        mode="below": perigo quando o valor <= value_from
                                (ex.: nivel de bateria/combustivel baixo)
        """
        self._danger_zone = value_from
        self._danger_mode = mode
        self.update()

    def setUnit(self, unit: str):
        self._unit = unit
        self.update()

    def setRange(self, min_value: float, max_value: float):
        self._min, self._max = min_value, max_value
        self.update()

    # -- propriedade animavel (Qt Property) ---------------------------
    def _get_animated_value(self):
        return self._animated_value

    def _set_animated_value(self, v):
        self._animated_value = v
        self.update()

    animatedValue = Property(float, _get_animated_value, _set_animated_value)

    def _is_danger(self, value: float) -> bool:
        if self._danger_zone is None:
            return False
        if self._danger_mode == "below":
            return value <= self._danger_zone
        return value >= self._danger_zone

    # -- pintura --------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)  # canvas logico 200x200

        self._draw_background(painter)
        self._draw_ticks(painter)
        self._draw_arc_progress(painter)
        self._draw_needle(painter)
        self._draw_center_text(painter)

    def _draw_background(self, p: QPainter):
        rect = QRectF(-90, -90, 180, 180)
        grad = QRadialGradient(0, 0, 95)
        grad.setColorAt(0.0, Palette.BG_PANEL_LIGHT)
        grad.setColorAt(1.0, Palette.BG_DARK)
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawEllipse(rect)

        # anel externo neon (trilho)
        pen = QPen(QColor(self._color.red(), self._color.green(), self._color.blue(), 60))
        pen.setWidth(10)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawArc(rect, START_ANGLE * 16, SPAN_ANGLE * 16)

    def _draw_ticks(self, p: QPainter):
        p.save()
        steps = 11
        for i in range(steps):
            frac = i / (steps - 1)
            angle_deg = START_ANGLE + SPAN_ANGLE * frac
            angle_rad = math.radians(angle_deg)
            is_danger = self._is_danger(self._min + frac * (self._max - self._min))
            color = Palette.NEON_RED if is_danger else Palette.TEXT_DIM
            pen = QPen(color)
            pen.setWidth(2)
            p.setPen(pen)
            x1, y1 = 80 * math.cos(angle_rad), -80 * math.sin(angle_rad)
            x2, y2 = 72 * math.cos(angle_rad), -72 * math.sin(angle_rad)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))
        p.restore()

    def _draw_arc_progress(self, p: QPainter):
        if self._max == self._min:
            return
        frac = (self._animated_value - self._min) / (self._max - self._min)
        frac = max(0.0, min(1.0, frac))
        span = SPAN_ANGLE * frac

        color = self._color
        if self._is_danger(self._animated_value):
            color = Palette.NEON_RED

        rect = QRectF(-90, -90, 180, 180)
        pen = QPen(color)
        pen.setWidth(8)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawArc(rect, START_ANGLE * 16, int(span * 16))

    def _draw_needle(self, p: QPainter):
        if self._max == self._min:
            return
        frac = (self._animated_value - self._min) / (self._max - self._min)
        frac = max(0.0, min(1.0, frac))
        angle_deg = START_ANGLE + SPAN_ANGLE * frac
        angle_rad = math.radians(angle_deg)

        p.save()
        pen = QPen(Palette.TEXT_PRIMARY)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        x, y = 62 * math.cos(angle_rad), -62 * math.sin(angle_rad)
        p.drawLine(0, 0, int(x), int(y))

        p.setPen(Qt.NoPen)
        p.setBrush(self._color)
        p.drawEllipse(QRectF(-5, -5, 10, 10))
        p.restore()

    def _draw_center_text(self, p: QPainter):
        p.save()
        value_font = QFont(Fonts.MONO[0], 22, QFont.Bold)
        p.setFont(value_font)
        p.setPen(Palette.TEXT_PRIMARY)
        p.drawText(QRectF(-70, -14, 140, 30), Qt.AlignCenter, f"{self._animated_value:.0f}")

        unit_font = QFont(Fonts.DISPLAY[0], 8)
        p.setFont(unit_font)
        p.setPen(Palette.TEXT_DIM)
        p.drawText(QRectF(-70, 14, 140, 16), Qt.AlignCenter, self._unit)

        title_font = QFont(Fonts.DISPLAY[0], 8, QFont.DemiBold)
        p.setFont(title_font)
        p.setPen(self._color)
        p.drawText(QRectF(-70, 42, 140, 16), Qt.AlignCenter, self._title)
        p.restore()
