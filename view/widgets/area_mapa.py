# -*- coding: utf-8 -*-
"""
widgets/map_widget.py

MapPanel: area reservada para o mapa/localizacao vinda do modulo NEO-6M.
Aqui e desenhado apenas um "radar/grid" estilo retro-neon como placeholder
visual - quando a logica real existir, basta trocar o conteudo do canvas
por um QWebEngineView (ex.: Leaflet/OSM offline) ou por tiles renderizados,
mantendo o mesmo layout/API publica:

    map_panel.set_coordinates(lat, lon)   # atualiza o texto de status (HUD)
    map_panel.set_heading(deg)            # gira a seta/indicador (placeholder)
"""

import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

from view.core.config import Palette, Fonts
from view.widgets.base_do_painel import NeonPanel
from view.widgets.rosa_dos_ventos import RosaVentos


class _RadarCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._heading = 0.0

        # bussola flutuante no canto inferior direito (overlay, fora do layout)
        self._compass = RosaVentos(self, diametro=60)
        self._compass.raise_()

    def set_heading(self, degrees: float):
        self._heading = degrees
        self._compass.set_heading(degrees)
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        margin = 8
        self._compass.move(
            self.width() - self._compass.width() - margin,
            self.height() - self._compass.height() - margin,
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 6

        # grade de fundo (linhas sutis)
        pen = QPen(Palette.GRID_LINE)
        pen.setWidth(1)
        p.setPen(pen)
        step = max(20, int(radius / 3))
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)

        # aneis concentricos
        ring_pen = QPen(QColor(Palette.NEON_GREEN.red(), Palette.NEON_GREEN.green(),
                                Palette.NEON_GREEN.blue(), 90))
        ring_pen.setWidth(1)
        p.setPen(ring_pen)
        p.setBrush(Qt.NoBrush)
        for i in range(1, 4):
            r = radius * i / 3
            p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # marcador central (posicao atual)
        p.setPen(Qt.NoPen)
        p.setBrush(Palette.NEON_MAGENTA)
        p.drawEllipse(QRectF(cx - 5, cy - 5, 10, 10))

        # indicador de direcao (heading) - seta
        p.save()
        p.translate(cx, cy)
        p.rotate(self._heading)
        pen2 = QPen(Palette.NEON_CYAN)
        pen2.setWidth(2)
        p.setPen(pen2)
        p.drawLine(0, 0, 0, -int(radius * 0.75))
        p.drawLine(0, -int(radius * 0.75), -6, -int(radius * 0.6))
        p.drawLine(0, -int(radius * 0.75), 6, -int(radius * 0.6))
        p.restore()


class MapPanel(NeonPanel):

    def __init__(self, parent=None):
        super().__init__(parent, glow_color=Palette.NEON_GREEN, glow_strength=20)
        self.setObjectName("MapPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        title = QLabel("◈ LOCALIZACAO (GPS)")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)

        self._canvas = _RadarCanvas()
        layout.addWidget(self._canvas, stretch=1)

        self._status_label = QLabel("LAT: --.-----   LON: --.-----")
        self._status_label.setObjectName("MapStatusLabel")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

    # -- API publica ---------------------------------------------------
    def set_coordinates(self, lat: float, lon: float):
        self._status_label.setText(f"LAT: {lat:.5f}   LON: {lon:.5f}")

    def set_heading(self, degrees: float):
        self._canvas.set_heading(degrees)

    def set_no_fix(self):
        self._status_label.setText("SEM FIX GPS")
