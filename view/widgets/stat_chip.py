# -*- coding: utf-8 -*-
"""
widgets/stat_chip.py

CompactStat: mini painel circular/quadrado com icone + valor + legenda,
usado para leituras que nao precisam de um arco/ponteiro (ex.: Tempo de
Viagem, com um relogio). Combina bem ao lado dos GaugeWidget na fileira
de indicadores compactos.

    chip = CompactStat(icon="🕐", value="00:14", caption="TEMPO DE VIAGEM")
    chip.set_value("01:32")
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel, QSizePolicy

from view.core.config import Palette, Fonts
from view.widgets.base_do_painel import NeonPanel


class CompactStat(NeonPanel):

    def __init__(self, icon="◇", value="--", caption="STAT", color=None, parent=None):
        color = color or Palette.NEON_CYAN
        super().__init__(parent, glow_color=color, glow_strength=14)
        self.setObjectName("CompactStat")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(80, 80)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont(Fonts.DISPLAY[0], 14))
        icon_label.setStyleSheet(f"color: {color.name()};")
        layout.addWidget(icon_label)

        self._value_label = QLabel(value)
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setFont(QFont(Fonts.MONO[0], 15, QFont.Bold))
        layout.addWidget(self._value_label)

        caption_label = QLabel(caption)
        caption_label.setAlignment(Qt.AlignCenter)
        caption_label.setFont(QFont(Fonts.DISPLAY[0], 7))
        caption_label.setObjectName("InfoCardCaption")
        layout.addWidget(caption_label)

    def set_value(self, value: str):
        self._value_label.setText(value)
