
# E so INTERFACE - o estado de conexao real deve ser atualizado via:
#     top_bar.set_connected(True/False)
#     top_bar.set_signal_bars(0..4)


from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy

from view.core.config import Palette, Fonts
from view.widgets.botao_navegacao import BotaoMenu

#===========================================================================================================
#==========================================  Status de Conectado ============================================
#===========================================================================================================
class _StatusConectado(QLabel):
    """Selo arredondado tipo 'CONECTADO' com ponto de status."""

    def __init__(self, texto="CONECTADO", conectado=True, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusPill")
        self.setFont(QFont(Fonts.DISPLAY[0], 9, QFont.DemiBold))
        self.setAlignment(Qt.AlignCenter)
        self.set_connected(conectado, texto)

    def set_connected(self, conectado: bool, texto: str = None):
        color = Palette.NEON_GREEN if conectado else Palette.NEON_RED
        label = texto or ("CONECTADO" if conectado else "DESCONECTADO")
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

#===========================================================================================================
#==========================================  Barra do Topo ============================================
#===========================================================================================================
class BarraStatus(QWidget):

    menu_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopStatusBar")
        self.setFixedHeight(48)
        
        layout = QHBoxLayout(self)            # layout horizontal para a barra
        layout.setContentsMargins(4, 4, 4, 4) # margens internas do layout (esq, cima, dir, baixo)
        layout.setSpacing(14)                 # espaço entre os elementos da barra
#______________________________________________________________________________________________________________________________botao de menu
        self._menu_btn = BotaoMenu(texto="", icon="☰", color=Palette.NEON_MAGENTA)

        self._menu_btn.setFixedWidth(46) # define a largura fixa do botao
        self._menu_btn.clicked.connect(self.menu_solicitado.emit) # conecta o sinal de clique do botao de menu ao sinal menu_solicitado da barra de status
        layout.addWidget(self._menu_btn, 0, Qt.AlignVCenter) # adiciona o botao de menu ao layout da barra de status, alinhado verticalmente ao centro

        layout.addStretch(1) # adiciona um stretch para empurrar os elementos da direita para a borda direita

        self._signal_label = QLabel("4G")
        self._signal_label.setObjectName("ConnIcon") # define o nome do objeto para estilização
        self._wifi_label = QLabel("WiFi")
        self._wifi_label.setObjectName("ConnIcon")
        self._bt_label = QLabel("BT")
        self._bt_label.setObjectName("ConnIcon")

        for lbl in (self._signal_label, self._wifi_label, self._bt_label):
            lbl.setFont(QFont(Fonts.MONO[0], 10))
            layout.addWidget(lbl, 0, Qt.AlignVCenter) # adiciona os icones de conectividade ao layout da barra de status, alinhados verticalmente ao centro

        self._status_conectado = _StatusConectado(conectado=True) 
        layout.addWidget(self._status_conectado, 0, Qt.AlignVCenter) # adiciona o selo de status ao layout da barra de status, alinhado verticalmente ao centro

    # -- API publica -----------------------------------------------------
    def set_connected(self, conectado: bool):
        self._status_conectado.set_connected(conectado)

    def set_signal_text(self, text: str):
        self._signal_label.setText(f"📶 {text}")
