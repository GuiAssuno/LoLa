# -*- coding: utf-8 -*-
"""
screens/camera_screen.py

CameraScreen: tela dedicada, exibindo APENAS a imagem da camera em
tamanho grande. A logica de captura deve chamar:
    camera_screen.video_panel.set_frame(pixmap)
"""

from LoLa.screens.base_screen import BaseScreen
from LoLa.widgets.video_widget import VideoPanel


class CameraScreen(BaseScreen):

    def __init__(self, parent=None):
        super().__init__(title="CAMERA", show_back=True, parent=parent)
        self.setObjectName("CameraScreen")

        self.video_panel = VideoPanel()
        self.body_layout.addWidget(self.video_panel, stretch=1)
