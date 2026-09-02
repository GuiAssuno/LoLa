""" medidor = Medidor(titulo="VELOCIDADE", unidade="km/h", valor_min=0, valor_max=220)
    medidor.set_Valor(87)
    medidor.set_ZonaPerigo(180) # opcional
"""

import math

from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient, QRadialGradient
from PySide6.QtWidgets import QWidget, QSizePolicy

from view.core.config import Palette, Fonts

# Angulo inicial/final do arco (estilo velocimetro automotivo classico)
START_ANGLE = 225   # graus, sentido anti-horario a partir do eixo 3h (convencao Qt)
SPAN_ANGLE = -270    # varre 270 graus no sentido horario

#=================================================================================================================
#======================================== Classe Medidor =========================================================
#=================================================================================================================
class Medidor(QWidget):
    def __init__(self, titulo="MEDIDOR", unidade="", valor_min=0, valor_max=100,
                 cor: QColor = None, parent=None):
        super().__init__(parent)
        self._titulo = titulo
        self._unidade = unidade
        self._min = valor_min
        self._max = valor_max
        self._valor = valor_min
        self._zona_de_perigo = None
        self._modo_de_perigo = "acima"
        self._color = QColor(cor or Palette.NEON_CYAN)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(140, 140)

        # precisa existir ANTES de criar o QPropertyAnimation, 
        # assim o Qt pode ler a propriedade "valorAnimado" assim que ela é registrada
        self._valor_animado = self._valor 

        self._animacao = QPropertyAnimation(self, b"valorAnimado")
        self._animacao.setDuration(350)
        self._animacao.setEasingCurve(QEasingCurve.OutCubic)

#________________________________________________________________________________________________________set_Valor
    def set_Valor(self, valor: float):
        """Atualiza o valor exibido no medidor até o novo valor."""
        valor = max(self._min, min(self._max, valor))
        self._valor = valor
        self._animacao.stop()
        self._animacao.setStartValue(self._valor_animado)
        self._animacao.setEndValue(valor)
        self._animacao.start()

    def valor(self):
        return self._valor
#___________________________________________________________________________________________________set_ZonaPerigo
    def set_ZonaPerigo(self, valor_perigo: float, modo: str = "acima"):
        """Define a partir de que valor o medidor fica vermelho.
        modo="acima" : perigo quando o valor >= valor_perigo
        modo="abaixo": perigo quando o valor <= valor_perigo
        """
        self._zona_de_perigo = valor_perigo
        self._modo_de_perigo = modo
        self.update()

    def set_Unidade(self, unidade: str):
        self._unidade = unidade
        self.update()

    def set_Intervalo(self, valor_min: float, valor_max: float):
        self._min, self._max = valor_min, valor_max
        self.update()

    def _get_valor_animado(self):
        return self._valor_animado

    def _set_valor_animado(self, vlr):
        self._valor_animado = vlr
        self.update()

    valorAnimado = Property(float, _get_valor_animado, _set_valor_animado)

    def _is_danger(self, value: float) -> bool:
        if self._zona_de_perigo is None:
            return False
        if self._modo_de_perigo == "abaixo":
            return value <= self._zona_de_perigo
        return value >= self._zona_de_perigo

    # -- pintura --------------------------------------------------------
    def paintEvent(self, event):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        lado = min(self.width(), self.height())
        pintor.translate(self.width() / 2, self.height() / 2)
        pintor.scale(lado / 200.0, lado / 200.0)  # canvas logico 200x200

        self._desenha_fundo(pintor)
        self._desenha_ticks(pintor)
        self._desenha_arco_progresso(pintor)
        self._desenha_agulha(pintor)
        self._desenha_texto_centro  (pintor)
#____________________________________________________________________________________________________desenha_fundo
    def _desenha_fundo(self, pintor: QPainter):
        """Desenha o fundo do medidor, incluindo o painel circular e o anel externo neon."""
        retangulo = QRectF(-90, -90, 180, 180)
        grad = QRadialGradient(0, 0, 95)
        grad.setColorAt(0.0, Palette.BG_PANEL_LIGHT)
        grad.setColorAt(1.0, Palette.BG_DARK)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(grad)
        pintor.drawEllipse(retangulo)

        # anel externo neon
        pen = QPen(QColor(self._color.red(), self._color.green(), self._color.blue(), 60))
        pen.setWidth(10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pintor.setPen(pen)
        pintor.setBrush(Qt.NoBrush)
        pintor.drawArc(retangulo, START_ANGLE * 16, SPAN_ANGLE * 16)
#____________________________________________________________________________________________________desenha_ticks
    def _desenha_ticks(self, pintor: QPainter):
        """Desenha os ticks (marcadores) do medidor, incluindo os ticks de perigo em vermelho."""
        pintor.save()
        passos = 11
        for i in range(passos):
            frac = i / (passos - 1)
            angle_deg = START_ANGLE + SPAN_ANGLE * frac
            angle_rad = math.radians(angle_deg)
            is_danger = self._is_danger(self._min + frac * (self._max - self._min))
            color = Palette.NEON_RED if is_danger else Palette.TEXT_DIM
            pen = QPen(color)
            pen.setWidth(2)
            pintor.setPen(pen)
            x1, y1 = 80 * math.cos(angle_rad), -80 * math.sin(angle_rad)
            x2, y2 = 72 * math.cos(angle_rad), -72 * math.sin(angle_rad)
            pintor.drawLine(int(x1), int(y1), int(x2), int(y2))
        pintor.restore()
#___________________________________________________________________________________________desenha_arco_progresso
    def _desenha_arco_progresso(self, pintor: QPainter):
        """Desenha o arco de progresso do medidor, que indica o valor atual."""
        if self._max == self._min:
            return
        frac = (self._valor_animado - self._min) / (self._max - self._min)
        frac = max(0.0, min(1.0, frac))
        span = SPAN_ANGLE * frac

        color = self._color
        if self._is_danger(self._valor_animado):
            color = Palette.NEON_RED

        retangulo = QRectF(-90, -90, 180, 180)
        pen = QPen(color)
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pintor.setPen(pen)
        pintor.setBrush(Qt.NoBrush)
        pintor.drawArc(retangulo, START_ANGLE * 16, int(span * 16))
#___________________________________________________________________________________________________desenha_agulha
    def _desenha_agulha(self, pintor: QPainter):
        """Agulha do medidor é um ponteiro circular que gira em torno do centro do widget."""
        if self._max == self._min:
            return
        frac = (self._valor_animado - self._min) / (self._max - self._min)
        frac = max(0.0, min(1.0, frac))
        angle_deg = START_ANGLE + SPAN_ANGLE * frac
        angle_rad = math.radians(angle_deg)

        pintor.save()
        pen = QPen(Palette.TEXT_PRIMARY)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pintor.setPen(pen)
        x, y = 62 * math.cos(angle_rad), -62 * math.sin(angle_rad)
        pintor.drawLine(0, 0, int(x), int(y))

        pintor.setPen(Qt.NoPen)
        pintor.setBrush(self._color)
        pintor.drawEllipse(QRectF(-5, -5, 10, 10))
        pintor.restore()

    def _desenha_texto_centro(self, pintor: QPainter):
        """Desenha o valor atual, unidade e titulo no centro do medidor."""
        pintor.save()
        fonte_valor = QFont(Fonts.MONO[0], 22, QFont.Bold)
        pintor.setFont(fonte_valor)
        pintor.setPen(Palette.TEXT_PRIMARY)
        pintor.drawText(QRectF(-70, -14, 140, 30), Qt.AlignCenter, f"{self._valor_animado:.0f}")

        fonte_unidade = QFont(Fonts.DISPLAY[0], 8)
        pintor.setFont(fonte_unidade)
        pintor.setPen(Palette.TEXT_DIM)
        pintor.drawText(QRectF(-70, 14, 140, 16), Qt.AlignCenter, self._unidade)

        fonte_do_titulo = QFont(Fonts.DISPLAY[0], 8, QFont.DemiBold)
        pintor.setFont(fonte_do_titulo)
        pintor.setPen(self._color)
        pintor.drawText(QRectF(-70, 42, 140, 16), Qt.AlignCenter, self._titulo)
        pintor.restore()
