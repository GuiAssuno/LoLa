# -*- coding: utf-8 -*-
"""
widgets/video_widget.py

VideoPanel: area onde o frame da camera do Raspberry sera exibido.
Aqui e apenas a INTERFACE - um QLabel pronto para receber um QPixmap.
Quem for implementar a captura (picamera2 / OpenCV / GStreamer) so
precisa chamar:

    video_panel.set_frame(pixmap)   # QPixmap
    video_panel.clear_frame()       # volta para o estado "sem sinal"

Dica de performance no RPi5: converta o frame para QImage/QPixmap fora da
thread de UI (ex.: QThread + Signal(QImage)) e chame set_frame() apenas no
slot conectado a esse signal, para nao travar a interface.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout

from LoLa.core.config import Palette, Fonts
from LoLa.widgets.panel import NeonPanel


class VideoPanel(NeonPanel):

    def __init__(self, parent=None, compact=False):
        super().__init__(parent, glow_color=Palette.NEON_CYAN, glow_strength=26)
        self.setObjectName("VideoPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setObjectName("VideoImageLabel")
        self._image_label.setScaledContents(False)
        layout.addWidget(self._image_label)

        self._no_signal_text = "SEM SINAL" if not compact else "CAM"
        self._pixmap = None
        self.clear_frame()

    def set_frame(self, pixmap: QPixmap):
        """Recebe um QPixmap ja pronto (chamado pelo codigo de captura)."""
        self._pixmap = pixmap
        self._rescale()

    def clear_frame(self):
        self._pixmap = None
        font = QFont(Fonts.DISPLAY[0], 14, QFont.Bold)
        self._image_label.setFont(font)
        self._image_label.setText(f"◇ {self._no_signal_text} ◇")
        self._image_label.setStyleSheet(f"color: {Palette.TEXT_DIM.name()};")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()

    def _rescale(self):
        if self._pixmap is None:
            return
        scaled = self._pixmap.scaled(
            self._image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._image_label.setPixmap(scaled)
