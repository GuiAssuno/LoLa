# -*- coding: utf-8 -*-
"""
widgets/nav_button.py

Botoes de navegacao reutilizaveis:
  - IconButton: botao redondo compacto (ex.: botao de MENU flutuante, VOLTAR)
  - AppBox: caixa clicavel usada na tela de Menu (camera, navegacao, config, sistema)
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy

from LoLa.core.config import Palette, Fonts
from LoLa.widgets.panel import NeonPanel


class IconButton(QPushButton):
    """Botao circular/pill compacto, ex: botao MENU ou VOLTAR."""

    def __init__(self, text="MENU", icon="☰", parent=None, color=None):
        super().__init__(parent)
        self.setObjectName("IconButton")
        self._color = color or Palette.NEON_MAGENTA
        self.setText(f"{icon}  {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont(Fonts.DISPLAY[0], 11, QFont.DemiBold))
        self.setMinimumHeight(44)
        self.setStyleSheet(self._build_style())

    def _build_style(self):
        c = self._color.name()
        return f"""
            QPushButton#IconButton {{
                color: {c};
                border: 2px solid {c};
                border-radius: 22px;
                background-color: rgba(255,255,255,10);
                padding: 6px 18px;
            }}
            QPushButton#IconButton:hover {{
                background-color: rgba(255,255,255,25);
            }}
            QPushButton#IconButton:pressed {{
                background-color: rgba(255,255,255,45);
            }}
        """


class AppBox(NeonPanel):
    """Caixa clicavel do menu de aplicativos (camera / navegacao / config / sistema)."""

    clicked = Signal()

    def __init__(self, title="APP", icon="◆", subtitle="", color=None, parent=None):
        color = color or Palette.NEON_CYAN
        super().__init__(parent, glow_color=color, glow_strength=18)
        self.setObjectName("AppBox")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(180, 180)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont(Fonts.DISPLAY[0], 42))
        icon_label.setStyleSheet(f"color: {color.name()};")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("AppBoxTitle")
        title_label.setFont(QFont(Fonts.DISPLAY[0], 13, QFont.Bold))
        layout.addWidget(title_label)

        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setAlignment(Qt.AlignCenter)
            sub_label.setObjectName("AppBoxSubtitle")
            sub_label.setFont(QFont(Fonts.MONO[0], 9))
            layout.addWidget(sub_label)

        self._color = color

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
