# -*- coding: utf-8 -*-
"""
screens/base_screen.py

BaseScreen: classe base para todas as telas do QStackedWidget.
Fornece uma barra de topo padrao (titulo + botao voltar opcional) para
manter consistencia visual entre Camera / Navegacao / Config / Sistema.
A tela Principal (MainScreen) NAO herda desta base pois tem layout proprio.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy

from LoLa.core.config import Palette, Fonts
from LoLa.widgets.nav_button import IconButton


class BaseScreen(QWidget):

    back_requested = Signal()

    def __init__(self, title="TELA", show_back=True, parent=None):
        super().__init__(parent)
        self.setObjectName("BaseScreen")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 18, 24, 18)
        root.setSpacing(14)

        header = QHBoxLayout()
        if show_back:
            self._back_btn = IconButton(text="VOLTAR", icon="◄", color=Palette.NEON_MAGENTA)
            self._back_btn.clicked.connect(self.back_requested.emit)
            header.addWidget(self._back_btn, 0, Qt.AlignVCenter)
        else:
            self._back_btn = None

        title_label = QLabel(title)
        title_label.setObjectName("ScreenTitle")
        title_label.setFont(QFont(Fonts.DISPLAY[0], 20, QFont.Bold))
        header.addWidget(title_label, 1, Qt.AlignVCenter | Qt.AlignHCenter)

        # espacador simetrico do lado direito p/ manter o titulo centralizado
        header.addSpacerItem(QSpacerItem(120, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))

        root.addLayout(header)

        self.body_layout = QVBoxLayout()
        self.body_layout.setSpacing(16)
        root.addLayout(self.body_layout, stretch=1)
