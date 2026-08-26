# -*- coding: utf-8 -*-
"""
main.py

Ponto de entrada do app. Monta a janela em modo kiosk (fullscreen, sem
bordas) e gerencia a navegacao entre as telas via QStackedWidget.

Rodar:
    python main.py

Sair do modo kiosk durante desenvolvimento: tecla ESC ou Ctrl+Q
(remova o atalho de ESC em producao se quiser bloquear o usuario 100%).
"""

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QShortcut, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from LoLa.screens.main_screen import MainScreen
from LoLa.screens.menu_screen import MenuScreen
from LoLa.screens.camera_screen import CameraScreen
from LoLa.screens.navigation_screen import NavigationScreen
from LoLa.screens.settings_screen import SettingsScreen
from LoLa.screens.system_screen import SystemScreen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(BASE_DIR, "resources", "style.qss")


class KioskWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painel de Bordo — Kiosk")

        # Janela sem bordas/decoracao, tipica de kiosk
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ---- instancia as telas ----
        self.main_screen = MainScreen()
        self.menu_screen = MenuScreen()
        self.camera_screen = CameraScreen()
        self.navigation_screen = NavigationScreen()
        self.settings_screen = SettingsScreen()
        self.system_screen = SystemScreen()

        for screen in (self.main_screen, self.menu_screen, self.camera_screen,
                       self.navigation_screen, self.settings_screen, self.system_screen):
            self.stack.addWidget(screen)

        self._connect_navigation()

        # tela principal e sempre a primeira a aparecer
        self.stack.setCurrentWidget(self.main_screen)

        self._setup_dev_shortcuts()

    def _connect_navigation(self):
        # tela principal -> menu
        self.main_screen.menu_requested.connect(
            lambda: self.stack.setCurrentWidget(self.menu_screen)
        )

        # menu -> cada app
        self.menu_screen.open_camera.connect(
            lambda: self.stack.setCurrentWidget(self.camera_screen)
        )
        self.menu_screen.open_navigation.connect(
            lambda: self.stack.setCurrentWidget(self.navigation_screen)
        )
        self.menu_screen.open_settings.connect(
            lambda: self.stack.setCurrentWidget(self.settings_screen)
        )
        self.menu_screen.open_system.connect(
            lambda: self.stack.setCurrentWidget(self.system_screen)
        )
        # botao "voltar" do menu leva para a tela principal
        self.menu_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.main_screen)
        )

        # botao "voltar" de cada app leva de volta ao menu
        self.camera_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.menu_screen)
        )
        self.navigation_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.menu_screen)
        )
        self.settings_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.menu_screen)
        )
        self.system_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.menu_screen)
        )

    def _setup_dev_shortcuts(self):
        """Atalhos uteis durante o desenvolvimento/testes.
        Remova ou proteja com senha em producao para um kiosk real."""
        QShortcut(QKeySequence("Esc"), self, activated=self.showNormal)
        QShortcut(QKeySequence("F11"), self, activated=self._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.close)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


def configure_performance(app: QApplication):
    """Ajustes recomendados para rodar com o maximo de desempenho no RPi5."""
    # Desativa efeitos de UI globais pesados (o glow dos paineis continua,
    # pois e feito individualmente e nao por esses efeitos genericos do Qt).
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


def main():
    # Habilita escalonamento correto em telas com DPI diferente
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # base neutra, o QSS sobrepoe quase tudo

    configure_performance(app)
    load_fonts()

    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = KioskWindow()

    # ---- Modo kiosk real: fullscreen, sem cursor do mouse ----
    # Descomente a linha abaixo em producao para esconder o cursor:
    # app.setOverrideCursor(Qt.BlankCursor)
    window.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
