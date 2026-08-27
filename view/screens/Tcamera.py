# -*- coding: utf-8 -*-
"""
screens/camera_screen.py

TelaCamera: tela dedicada, exibindo APENAS a imagem da camera em
tamanho grande. A logica de captura deve chamar:
    camera_screen.video_panel.set_frame(pixmap)
"""

from view.screens.base import BaseScreen
from view.widgets.area_video import VideoPanel


class TelaCamera(BaseScreen):

    def __init__(self, parent=None):
        super().__init__(title="CAMERA", show_back=True, parent=parent)
        self.setObjectName("TelaCamera")

        self.video_panel = VideoPanel()
        self.body_layout.addWidget(self.video_panel, stretch=1)
