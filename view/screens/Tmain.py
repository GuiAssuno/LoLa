
#   Top →   [  menu |                     conectividade   |  selo CONECTADO ]
#           [===============================================================]
#           [  MAPA + bussola  ]  [                   ]  [ CARRO + radares  ]
#   Mid  →  [                  ]  [  VIDEO DA CAMERA  ]  [  de proximidade  ]
#           [     Medidores    ]  [                   ]  [      + TPMS      ]
#           [===============================================================]
#   Bot  →  [                        MediaPlayerBar                         ]


from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

from view.core.config import Palette
from view.widgets.barra_de_status import BarraStatus
from view.widgets.medidor import Medidor
from view.widgets.medidor_estatico import CompactStat
from view.widgets.area_mapa import MapPanel
from view.widgets.area_video import VideoPanel
from view.widgets.sensores_proximacao import PainelSensorCarro
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
        self.top_bar = BarraStatus()
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
        self.car_panel = PainelSensorCarro()
        # valores de exemplo so para deixar a interface com boa aparencia
        self.car_panel.set_pressao_pneu("fe", 35)
        self.car_panel.set_pressao_pneu("fd", 35)
        self.car_panel.set_pressao_pneu("te", 35)
        self.car_panel.set_pressao_pneu("td", 35)
        return self.car_panel

    def _build_gauges_row(self):
        grid = QGridLayout()
        grid.setSpacing(8)

        self.speed_gauge = Medidor(titulo="VELOC.", unidade="km/h", valor_min=0,
                                        valor_max=220, cor=Palette.NEON_CYAN)
        self.speed_gauge.set_ZonaPerigo(160)

        self.rpm_gauge = Medidor(titulo="RPM", unidade="x1000", valor_min=0,
                                      valor_max=8, cor=Palette.NEON_GREEN)
        self.rpm_gauge.set_ZonaPerigo(6)

        self.temp_gauge = Medidor(titulo="TEMP.", unidade="°C", valor_min=0,
                                       valor_max=140, cor=Palette.NEON_YELLOW)
        self.temp_gauge.set_ZonaPerigo(110)

        self.trip_chip = CompactStat(icon="🕐", value="00:00", caption="TEMPO",
                                      cor=Palette.NEON_CYAN)

        self.gforce_gauge = Medidor(titulo="G-FORCE", unidade="G", valor_min=0,
                                         valor_max=2, cor=Palette.NEON_PURPLE)

        self.energy_gauge = Medidor(titulo="ENERGIA", unidade="%", valor_min=0,
                                         valor_max=100, cor=Palette.NEON_GREEN)
        self.energy_gauge.set_ZonaPerigo(15, modo="abaixo")

        self.incline_gauge = Medidor(titulo="INCLIN.", unidade="°", valor_min=-45,
                                          valor_max=45, cor=Palette.NEON_MAGENTA)

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
