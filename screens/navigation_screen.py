# -*- coding: utf-8 -*-
"""
screens/navigation_screen.py

NavigationScreen: tela dedicada a navegacao - mapa grande + paineis de
informacao (velocidade, direcao, distancia) como placeholders de UI.
Logica real deve chamar:
    navigation_screen.map_panel.set_coordinates(lat, lon)
    navigation_screen.map_panel.set_heading(deg)
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel

from LoLa.core.config import Palette, Fonts
from LoLa.screens.base_screen import BaseScreen
from LoLa.widgets.map_widget import MapPanel
from LoLa.widgets.panel import NeonPanel


class _InfoCard(NeonPanel):
    def __init__(self, label_text, value_text="--", color=None):
        super().__init__(glow_color=color or Palette.NEON_GREEN, glow_strength=16)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.value_label = QLabel(value_text)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFont(QFont(Fonts.MONO[0], 22, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {(color or Palette.NEON_GREEN).name()};")

        caption = QLabel(label_text)
        caption.setAlignment(Qt.AlignCenter)
        caption.setFont(QFont(Fonts.DISPLAY[0], 9))
        caption.setObjectName("InfoCardCaption")

        layout.addWidget(self.value_label)
        layout.addWidget(caption)


class NavigationScreen(BaseScreen):

    def __init__(self, parent=None):
        super().__init__(title="NAVEGACAO", show_back=True, parent=parent)
        self.setObjectName("NavigationScreen")

        self.map_panel = MapPanel()
        self.body_layout.addWidget(self.map_panel, stretch=1)

        info_row = QHBoxLayout()
        info_row.setSpacing(16)

        self.speed_card = _InfoCard("VELOCIDADE ATUAL", "-- km/h", Palette.NEON_CYAN)
        self.heading_card = _InfoCard("DIRECAO", "-- °", Palette.NEON_GREEN)
        self.distance_card = _InfoCard("DISTANCIA RESTANTE", "-- km", Palette.NEON_PURPLE)
        self.eta_card = _InfoCard("CHEGADA PREVISTA", "--:--", Palette.NEON_MAGENTA)

        for card in (self.speed_card, self.heading_card, self.distance_card, self.eta_card):
            card.setFixedHeight(90)
            info_row.addWidget(card)

        self.body_layout.addLayout(info_row)
