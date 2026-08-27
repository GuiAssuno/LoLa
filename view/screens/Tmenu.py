# -*- coding: utf-8 -*-
"""
screens/menu_screen.py

TelaMenu: exibe as caixas de aplicativos que o usuario pode abrir:
  - Camera        -> tela so com a imagem da camera
  - Navegacao     -> tela so com o mapa/GPS
  - Configuracoes -> nome do usuario, tema, volume, tamanho da fonte
  - Sistema       -> dados de sensores / ESP32 / Arduino
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout

from view.core.config import Palette
from view.screens.base import BaseScreen
from view.widgets.botao_navegacao import AppBox


class TelaMenu(BaseScreen):

    open_camera = Signal()
    open_navigation = Signal()
    open_settings = Signal()
    open_system = Signal()

    def __init__(self, parent=None):
        super().__init__(title="MENU DE APLICATIVOS", show_back=True, parent=parent)
        self.setObjectName("TelaMenu")
        # o sinal back_requested (herdado de BaseScreen) e conectado em
        # main.py para levar de volta a tela principal

        grid = QGridLayout()
        grid.setSpacing(20)

        box_camera = AppBox(title="CAMERA", icon="📷", subtitle="Visualizar transmissao",
                             color=Palette.NEON_CYAN)
        box_camera.clicked.connect(self.open_camera.emit)

        box_nav = AppBox(title="NAVEGACAO", icon="🧭", subtitle="Mapa e rota",
                          color=Palette.NEON_GREEN)
        box_nav.clicked.connect(self.open_navigation.emit)

        box_settings = AppBox(title="CONFIGURACOES", icon="⚙", subtitle="Usuario, tema, audio",
                               color=Palette.NEON_PURPLE)
        box_settings.clicked.connect(self.open_settings.emit)

        box_system = AppBox(title="SISTEMA", icon="🖥", subtitle="Sensores / ESP32 / Arduino",
                             color=Palette.NEON_MAGENTA)
        box_system.clicked.connect(self.open_system.emit)

        grid.addWidget(box_camera, 0, 0)
        grid.addWidget(box_nav, 0, 1)
        grid.addWidget(box_settings, 1, 0)
        grid.addWidget(box_system, 1, 1)

        self.body_layout.addLayout(grid)
