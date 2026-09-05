from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy

from view.core.config import Palette, Fonts
from view.widgets.base_do_painel import NeonPanel


#===========================================================================================================
#==========================================  Icone Botão Menu  =============================================
#===========================================================================================================
class BotaoMenu(QPushButton):
    """Botao MENU"""
    def __init__(self, texto="MENU", icon="☰", parent=None, color=None):
        super().__init__(parent)
        self.setObjectName("IconButton")

        # cor do botao (pode ser alterada depois com set_color()) 
        self._color = color or Palette.NEON_MAGENTA # se a cor nao for passada, usa a cor padrao (magenta neon)

        self.setText(f"{icon}") # o texto que aparece no botao
        self.setCursor(Qt.PointingHandCursor) # cursor de "maozinha" ao passar por cima
        self.setFont(QFont(Fonts.DISPLAY[0], 11, QFont.DemiBold)) # fonte do botao
        self.setMinimumHeight(44) # tamanho minimo do botao
        self.setStyleSheet(self._build_style()) # aplica o estilo do botao
#___________________________________________________________________________________________estilo do botao
    def _build_style(self):
        c = self._color.name() # pega a cor do botao em formato hexadecimal

        # retorna o estilo do botao em formato CSS, usando a cor definida
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

#===========================================================================================================
#==========================================  Caixa dos aplicativos  ========================================
#===========================================================================================================
class CaixaApp(NeonPanel):
    """Caixa de aplicativos"""
    clicked = Signal()

    def __init__(self, titulo="APP", icone="◆", subtitulo="", cor=None, parent=None):
        cor = cor or Palette.NEON_CYAN
        super().__init__(parent, glow_color=cor, glow_strength=18)
        self.setObjectName("AppBox")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(180, 180)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icone_label = QLabel(icone)
        icone_label.setAlignment(Qt.AlignCenter)
        icone_label.setFont(QFont(Fonts.DISPLAY[0], 42))
        icone_label.setStyleSheet(f"color: {cor.name()};")
        layout.addWidget(icone_label)

        titulo_label = QLabel(titulo)
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setObjectName("AppBoxTitle")
        titulo_label.setFont(QFont(Fonts.DISPLAY[0], 13, QFont.Bold))
        layout.addWidget(titulo_label)

        if subtitulo:
            subtitulo_label = QLabel(subtitulo)
            subtitulo_label.setAlignment(Qt.AlignCenter)
            subtitulo_label.setObjectName("AppBoxSubtitle")
            subtitulo_label.setFont(QFont(Fonts.MONO[0], 9))
            layout.addWidget(subtitulo_label)

        self._cor = cor

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
