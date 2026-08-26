# -*- coding: utf-8 -*-
"""
widgets/footer.py

RotatingFooter: rodapé de ponta a ponta que roda entre varias informacoes
(hora, clima, avisos, telemetria, etc.) com uma transicao suave de opacidade.
E so a INTERFACE - o conteudo real e alimentado via set_messages().

    footer.set_messages(["18:42  |  22°C", "GPS: 12 satelites", "Bateria: 87%"])
    footer.set_interval_ms(5000)
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsOpacityEffect

from LoLa.core.config import Palette, Fonts, UI


class RotatingFooter(QWidget):

    def __init__(self, parent=None, messages=None, interval_ms=UI.FOOTER_ROTATE_MS):
        super().__init__(parent)
        self.setObjectName("RotatingFooter")
        self.setFixedHeight(46)

        self._messages = messages or ["Aguardando dados..."]
        self._index = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # marcador lateral esquerdo (so estetico, indica "ao vivo")
        self._dot = QLabel("●")
        self._dot.setObjectName("FooterDot")
        layout.addWidget(self._dot, 0, Qt.AlignVCenter)

        self._label = QLabel(self._messages[0])
        self._label.setObjectName("FooterLabel")
        self._label.setFont(QFont(Fonts.MONO[0], 12))
        layout.addWidget(self._label, 1, Qt.AlignVCenter)

        self._page_indicator = QLabel(self._page_text())
        self._page_indicator.setObjectName("FooterPageIndicator")
        layout.addWidget(self._page_indicator, 0, Qt.AlignVCenter)

        self._opacity_fx = QGraphicsOpacityEffect(self._label)
        self._label.setGraphicsEffect(self._opacity_fx)
        self._opacity_fx.setOpacity(1.0)

        self._fade_out = QPropertyAnimation(self._opacity_fx, b"opacity")
        self._fade_out.setDuration(UI.ANIMATION_MS)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        self._fade_out.finished.connect(self._on_fade_out_finished)

        self._fade_in = QPropertyAnimation(self._opacity_fx, b"opacity")
        self._fade_in.setDuration(UI.ANIMATION_MS)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.InOutQuad)

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._rotate)
        self._timer.start()

    # -- API publica -----------------------------------------------------
    def set_messages(self, messages: list):
        if not messages:
            return
        self._messages = messages
        self._index = 0
        self._label.setText(self._messages[0])
        self._page_indicator.setText(self._page_text())

    def set_interval_ms(self, ms: int):
        self._timer.setInterval(ms)

    def pause(self):
        self._timer.stop()

    def resume(self):
        self._timer.start()

    # -- interno -----------------------------------------------------------
    def _page_text(self):
        return f"{self._index + 1:02d}/{len(self._messages):02d}"

    def _rotate(self):
        if len(self._messages) <= 1:
            return
        self._fade_out.start()

    def _on_fade_out_finished(self):
        self._index = (self._index + 1) % len(self._messages)
        self._label.setText(self._messages[self._index])
        self._page_indicator.setText(self._page_text())
        self._fade_in.start()
