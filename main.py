import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QShortcut, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from view.screens.Tmain import TelaPrincipal
from view.screens.Tmenu import TelaMenu
from view.screens.Tcamera import TelaCamera
from view.screens.TGPS import TelaGPS
from view.screens.Tconfig import TelaConfig
from view.screens.Tmonitor_sensores import TelaMonitor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(BASE_DIR, "view", "resources", "style.qss")


class KioskWindow(QMainWindow):
    def __init__(self):
        # Chamando a classe pai QMainWindow
        super().__init__() 
        self.setWindowTitle("Assistente de Bordo - LoLa")

        # Janela sem bordas
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # criando a pilha para gerenciar as telas
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

#===========================================================================================================
#==========================================  instancia as telas ============================================
#===========================================================================================================
        self.tela_home    = TelaPrincipal() # Tela principal
        self.tela_menu    = TelaMenu()      # Tela de menu
        self.tela_camera  = TelaCamera()    # Tela de camera
        self.tela_GPS     = TelaGPS()       # Tela de navegacao
        self.tela_config  = TelaConfig()    # Tela de configurações
        self.tela_monitor = TelaMonitor()   # Tela de sistema

        for screen in (self.tela_home, self.tela_menu, self.tela_camera, self.tela_GPS, self.tela_config, self.tela_monitor):
            self.stack.addWidget(screen)

        # conecta os sinais de navegacao entre as telas
        self._connect_navigation()

        # tela principal e sempre a primeira a aparecer
        self.stack.setCurrentWidget(self.tela_home)

        self._setup_dev_shortcuts()

    def _connect_navigation(self):
        # tela principal -> menu
        self.tela_home.menu_requested.connect(
            lambda: self.stack.setCurrentWidget(self.tela_menu)
        )

        # menu -> cada app
        self.tela_menu.open_camera.connect(
            lambda: self.stack.setCurrentWidget(self.tela_camera)
        )
        self.tela_menu.open_navigation.connect(
            lambda: self.stack.setCurrentWidget(self.tela_GPS)
        )
        self.tela_menu.open_settings.connect(
            lambda: self.stack.setCurrentWidget(self.tela_config)
        )
        self.tela_menu.open_system.connect(
            lambda: self.stack.setCurrentWidget(self.tela_monitor)
        )
        # botao "voltar" do menu leva para a tela principal
        self.tela_menu.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.tela_home)
        )

        # botao "voltar" de cada app leva de volta ao menu
        self.tela_camera.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.tela_menu)
        )
        self.tela_GPS.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.tela_menu)
        )
        self.tela_config.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.tela_menu)
        )
        self.tela_monitor.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.tela_menu)
        )

    def _setup_dev_shortcuts(self):
        QShortcut(QKeySequence("Esc"), self, activated=self.showNormal)
        QShortcut(QKeySequence("F11"), self, activated=self._toggle_fullscreen)
        QShortcut(QKeySequence("F2"), self, activated=self._toggle_cursor)
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.close)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _toggle_cursor(self):
        app = QApplication.instance()
        if app.overrideCursor() is not None:
            app.restoreOverrideCursor()
        else:
            app.setOverrideCursor(Qt.BlankCursor)


def configure_performance(app: QApplication):
    """Ajustes recomendados para rodar com o maximo de desempenho no RPi5."""
    app.setEffectEnabled(Qt.UI_AnimateMenu, False)
    app.setEffectEnabled(Qt.UI_AnimateCombo, False)
    app.setEffectEnabled(Qt.UI_AnimateTooltip, False)


def load_fonts():
    """Carrega fontes customizadas de resources/fonts/*.ttf, se existirem.
    Caso nao existam no sistema, o QSS/QFont cai para os fallbacks
    definidos em core/config.py."""
    fonts_dir = os.path.join(BASE_DIR, "resources", "fonts")
    if os.path.isdir(fonts_dir):
        for filename in os.listdir(fonts_dir):
            if filename.lower().endswith((".ttf", ".otf")):
                QFontDatabase.addApplicationFont(os.path.join(fonts_dir, filename))


def hide_mouse_cursor(app: QApplication):
    """Remove o cursor do mouse da interface.

    O app e controlado por voz + touchscreen, entao nao faz sentido exibir
    uma setinha de mouse. Duas camadas de protecao sao aplicadas:

    1. QT_QPA_EGLFS_HIDECURSOR=1 - flag nativa do plugin de plataforma
       "eglfs" (o modo mais comum de rodar Qt em kiosk no Raspberry Pi,
       sem X11/Wayland, direto sobre KMS/DRM). Precisa ser definida ANTES
       da QApplication ser criada, por isso fica em main(), no topo.
    2. app.setOverrideCursor(Qt.BlankCursor) - esconde o cursor em nivel
       de aplicacao Qt, funcionando em qualquer plataforma (eglfs, X11,
       Wayland, ou mesmo rodando numa janela normal durante os testes).

    Nenhuma das duas interfere no touchscreen: eventos de toque nao usam
    o cursor do mouse, o Qt so exibe (ou nao) o icone dele por cima.
    """
    app.setOverrideCursor(Qt.BlankCursor)


def main():
    # Habilita escalonamento correto em telas com DPI diferente
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    # Precisa ser definido ANTES da QApplication existir. So tem efeito
    # quando QT_QPA_PLATFORM=eglfs (kiosk sem X11/Wayland no RPi5); em
    # outras plataformas essa variavel e simplesmente ignorada.
    os.environ.setdefault("QT_QPA_EGLFS_HIDECURSOR", "1")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # base neutra, o QSS sobrepoe quase tudo

    configure_performance(app)
    load_fonts()
    hide_mouse_cursor(app)

    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = KioskWindow()
    window.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
