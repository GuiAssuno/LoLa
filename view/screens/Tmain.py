# -*- coding: utf-8 -*-
"""
screens/main_screen.py

TelaPrincipal: tela principal / tela em que o app sempre inicia.

Layout (inspirado em paineis automotivos modernos):

    [ TopStatusBar: menu | conectividade | selo CONECTADO ]  <- topo, full width
    -------------------------------------------------------------------
    [ MAPA + bussola  ]  [                          ]  [ CARRO + radares  ]
    [ (col. esquerda)  ]  [   VIDEO DA CAMERA        ]  [  de proximidade  ]
    [ gauges compactos ]  [   (coluna central)       ]  [  + TPMS (col. dir)]
    -------------------------------------------------------------------
    [ ---------------- MediaPlayerBar (rodape) ---------------------- ]

Os stretch factors garantem responsividade em qualquer resolucao.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

from view.core.config import Palette
from view.widgets.barra_de_status import TopStatusBar
from view.widgets.medidor import GaugeWidget
from view.widgets.stat_chip import CompactStat
from view.widgets.area_mapa import MapPanel
from view.widgets.area_video import VideoPanel
from view.widgets.sensores_proximacao import CarSensorsPanel
from view.widgets.barra_de_media import MediaPlayerBar


class TelaPrincipal(QWidget):

    menu_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelaPrincipal")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 10, 16, 0)
        root.setSpacing(10)

        # ---- barra superior ----
        self.top_bar = TopStatusBar()
        self.top_bar.menu_requested.connect(self.menu_requested.emit)
        root.addWidget(self.top_bar)

        # ---- corpo: 3 colunas ----
        body = QHBoxLayout()
        body.setSpacing(14)

        body.addLayout(self._build_left_column(), stretch=28)
        body.addWidget(self._build_video_column(), stretch=42)
        body.addWidget(self._build_right_column(), stretch=28)

        root.addLayout(body, stretch=1)

        # ---- rodape: media player ----
        self.media_bar = MediaPlayerBar()
        root.addWidget(self.media_bar)

    # -----------------------------------------------------------------
    def _build_left_column(self):
        col = QVBoxLayout()
        col.setSpacing(10)

        self.map_panel = MapPanel()
        col.addWidget(self.map_panel, stretch=3)

        col.addLayout(self._build_gauges_row(), stretch=0)
        return col

    def _build_video_column(self):
        self.video_panel = VideoPanel()
        return self.video_panel

    def _build_right_column(self):
        self.car_panel = CarSensorsPanel()
        # valores de exemplo so para deixar a interface com boa aparencia
        self.car_panel.set_tire_pressure("fl", 35)
        self.car_panel.set_tire_pressure("fr", 35)
        self.car_panel.set_tire_pressure("rl", 35)
        self.car_panel.set_tire_pressure("rr", 35)
        return self.car_panel

    def _build_gauges_row(self):
        grid = QGridLayout()
        grid.setSpacing(8)

        self.speed_gauge = GaugeWidget(title="VELOC.", unit="km/h", min_value=0,
                                        max_value=220, color=Palette.NEON_CYAN)
        self.speed_gauge.setDangerZone(160)

        self.rpm_gauge = GaugeWidget(title="RPM", unit="x1000", min_value=0,
                                      max_value=8, color=Palette.NEON_GREEN)
        self.rpm_gauge.setDangerZone(6)

        self.temp_gauge = GaugeWidget(title="TEMP.", unit="°C", min_value=0,
                                       max_value=140, color=Palette.NEON_YELLOW)
        self.temp_gauge.setDangerZone(110)

        self.trip_chip = CompactStat(icon="🕐", value="00:00", caption="TEMPO",
                                      color=Palette.NEON_CYAN)

        self.gforce_gauge = GaugeWidget(title="G-FORCE", unit="G", min_value=0,
                                         max_value=2, color=Palette.NEON_PURPLE)

        self.energy_gauge = GaugeWidget(title="ENERGIA", unit="%", min_value=0,
                                         max_value=100, color=Palette.NEON_GREEN)
        self.energy_gauge.setDangerZone(15, mode="below")

        self.incline_gauge = GaugeWidget(title="INCLIN.", unit="°", min_value=-45,
                                          max_value=45, color=Palette.NEON_MAGENTA)

        widgets = [
            self.speed_gauge, self.rpm_gauge, self.temp_gauge, self.trip_chip,
            self.gforce_gauge, self.energy_gauge, self.incline_gauge,
        ]
        cols = 4
        for i, w in enumerate(widgets):
            w.setFixedSize(84, 84)
            row, col = divmod(i, cols)
            grid.addWidget(w, row, col)

        return grid
