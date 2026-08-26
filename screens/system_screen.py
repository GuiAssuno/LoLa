# -*- coding: utf-8 -*-
"""
screens/system_screen.py

SystemScreen: exibe informacoes recebidas de sensores e dos modulos
ESP32/Arduino. Aqui e so a INTERFACE - cada "cartao" tem um metodo
publico set_value() para ser alimentado pela camada de dados depois.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QLabel

from LoLa.core.config import Palette, Fonts
from LoLa.screens.base_screen import BaseScreen
from LoLa.widgets.panel import NeonPanel


class _SensorCard(NeonPanel):
    def __init__(self, title, value="--", unit="", color=None, icon="◇"):
        color = color or Palette.NEON_CYAN
        super().__init__(glow_color=color, glow_strength=16)
        self.setObjectName("SensorCard")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont(Fonts.DISPLAY[0], 22))
        icon_label.setStyleSheet(f"color: {color.name()};")
        layout.addWidget(icon_label)

        self._value_label = QLabel(f"{value} {unit}".strip())
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setFont(QFont(Fonts.MONO[0], 18, QFont.Bold))
        layout.addWidget(self._value_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(Fonts.DISPLAY[0], 9))
        title_label.setObjectName("SensorCardTitle")
        layout.addWidget(title_label)

        self._unit = unit

    def set_value(self, value):
        self._value_label.setText(f"{value} {self._unit}".strip())


class SystemScreen(BaseScreen):

    def __init__(self, parent=None):
        super().__init__(title="SISTEMA — SENSORES / ESP32 / ARDUINO", show_back=True, parent=parent)
        self.setObjectName("SystemScreen")

        grid = QGridLayout()
        grid.setSpacing(18)

        self.temp_card = _SensorCard("TEMPERATURA", "--", "°C", Palette.NEON_RED, "🌡")
        self.voltage_card = _SensorCard("TENSAO BATERIA", "--", "V", Palette.NEON_YELLOW, "⚡")
        self.rpm_card = _SensorCard("RPM MOTOR", "--", "rpm", Palette.NEON_CYAN, "◎")
        self.humidity_card = _SensorCard("UMIDADE", "--", "%", Palette.NEON_GREEN, "💧")
        self.esp32_card = _SensorCard("ESP32", "OFFLINE", "", Palette.NEON_PURPLE, "◈")
        self.arduino_card = _SensorCard("ARDUINO", "OFFLINE", "", Palette.NEON_MAGENTA, "◈")
        self.cpu_card = _SensorCard("CPU / TEMP RPi5", "--", "°C", Palette.NEON_CYAN, "🖥")
        self.storage_card = _SensorCard("ARMAZENAMENTO", "--", "% usado", Palette.NEON_GREEN, "💾")

        cards = [
            self.temp_card, self.voltage_card, self.rpm_card, self.humidity_card,
            self.esp32_card, self.arduino_card, self.cpu_card, self.storage_card,
        ]
        for i, card in enumerate(cards):
            row, col = divmod(i, 4)
            grid.addWidget(card, row, col)

        self.body_layout.addLayout(grid)
        self.body_layout.addStretch(1)
