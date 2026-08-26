# -*- coding: utf-8 -*-
"""
widgets/top_status_bar.py

TopStatusBar: barra fixa no topo da tela principal.
Esquerda: botao de menu.
Direita: icones de conectividade (WiFi/Bluetooth/4G) + selo "CONECTADO".

E so INTERFACE - o estado de conexao real deve ser atualizado via:
    top_bar.set_connected(True/False)
    top_bar.set_signal_bars(0..4)
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy

from LoLa.core.config import Palette, Fonts
from LoLa.widgets.nav_button import IconButton


class _StatusPill(QLabel):
    """Selo arredondado tipo 'CONECTADO' com ponto de status."""

    def __init__(self, text="CONECTADO", connected=True, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusPill")
        self.setFont(QFont(Fonts.DISPLAY[0], 9, QFont.DemiBold))
        self.setAlignment(Qt.AlignCenter)
        self.set_connected(connected, text)

    def set_connected(self, connected: bool, text: str = None):
        color = Palette.NEON_GREEN if connected else Palette.NEON_RED
        label = text or ("CONECTADO" if connected else "DESCONECTADO")
        self.setText(f"●  {label}")
        self.setStyleSheet(f"""
            QLabel#StatusPill {{
                color: {color.name()};
                border: 1px solid {color.name()};
                border-radius: 12px;
                padding: 4px 14px;
                background-color: rgba(0,0,0,60);
            }}
        """)


class TopStatusBar(QWidget):

    menu_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopStatusBar")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(14)

        self._menu_btn = IconButton(text="", icon="☰", color=Palette.NEON_MAGENTA)
        self._menu_btn.setFixedWidth(56)
        self._menu_btn.clicked.connect(self.menu_requested.emit)
        layout.addWidget(self._menu_btn, 0, Qt.AlignVCenter)

        layout.addStretch(1)

        self._signal_label = QLabel("📶 4G")
        self._signal_label.setObjectName("ConnIcon")
        self._wifi_label = QLabel("📡 WiFi")
        self._wifi_label.setObjectName("ConnIcon")
        self._bt_label = QLabel("⚡ BT")
        self._bt_label.setObjectName("ConnIcon")

        for lbl in (self._signal_label, self._wifi_label, self._bt_label):
            lbl.setFont(QFont(Fonts.MONO[0], 10))
            layout.addWidget(lbl, 0, Qt.AlignVCenter)

        self._status_pill = _StatusPill(connected=True)
        layout.addWidget(self._status_pill, 0, Qt.AlignVCenter)

    # -- API publica -----------------------------------------------------
    def set_connected(self, connected: bool):
        self._status_pill.set_connected(connected)

    def set_signal_text(self, text: str):
        self._signal_label.setText(f"📶 {text}")
