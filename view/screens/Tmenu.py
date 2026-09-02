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
from view.widgets.botao_navegacao import CaixaApp


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

        box_camera = CaixaApp(titulo="CAMERA", icone="📷", subtitulo="Visualizar transmissao",
                             cor=Palette.NEON_CYAN)
        box_camera.clicked.connect(self.open_camera.emit)

        box_nav = CaixaApp(titulo="NAVEGACAO", icone="🧭", subtitulo="Mapa e rota",
                          cor=Palette.NEON_GREEN)
        box_nav.clicked.connect(self.open_navigation.emit)

        box_settings = CaixaApp(titulo="CONFIGURACOES", icone="⚙", subtitulo="Usuario, tema, audio",
                               cor=Palette.NEON_PURPLE)
        box_settings.clicked.connect(self.open_settings.emit)

        box_system = CaixaApp(titulo="SISTEMA", icone="🖥", subtitulo="Sensores / ESP32 / Arduino",
                             cor=Palette.NEON_MAGENTA)
        box_system.clicked.connect(self.open_system.emit)

        grid.addWidget(box_camera, 0, 0)
        grid.addWidget(box_nav, 0, 1)
        grid.addWidget(box_settings, 1, 0)
        grid.addWidget(box_system, 1, 1)

        self.body_layout.addLayout(grid)
