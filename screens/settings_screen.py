# -*- coding: utf-8 -*-
"""
screens/settings_screen.py

SettingsScreen: configuracoes gerais do app (apenas UI - sem logica).
Campos: nome do usuario, tema de cores, volume, tamanho da fonte.

Sinais emitidos (para quem for plugar a logica depois):
    settings_screen.save_requested.connect(handler)
    # handler recebe um dict: {"username": str, "theme": str,
    #                            "volume": int, "font_size": int}
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QSlider, QSpinBox,
    QLabel, QHBoxLayout
)

from LoLa.core.config import Palette, Fonts
from LoLa.screens.base_screen import BaseScreen
from LoLa.widgets.panel import NeonPanel
from LoLa.widgets.nav_button import IconButton


class SettingsScreen(BaseScreen):

    save_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(title="CONFIGURACOES", show_back=True, parent=parent)
        self.setObjectName("SettingsScreen")

        panel = NeonPanel(glow_color=Palette.NEON_PURPLE, glow_strength=18)
        form_layout = QFormLayout(panel)
        form_layout.setSpacing(18)
        form_layout.setContentsMargins(28, 24, 28, 24)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # -- nome do usuario -----------------------------------------
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Digite o nome do usuario")
        form_layout.addRow(self._field_label("NOME DO USUARIO"), self.username_edit)

        # -- tema de cores -----------------------------------------
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Neon Cyan/Magenta (padrao)",
            "Neon Verde/Roxo",
            "Neon Vermelho/Azul",
            "Monocromatico Ambar",
        ])
        form_layout.addRow(self._field_label("TEMA DE CORES"), self.theme_combo)

        # -- volume -----------------------------------------
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_value_label = QLabel("70%")
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_value_label.setText(f"{v}%")
        )
        form_layout.addRow(self._field_label("VOLUME"), self._with_value(self.volume_slider, self.volume_value_label))

        # -- tamanho da fonte -----------------------------------------
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        self.font_size_spin.setValue(14)
        self.font_size_spin.setSuffix(" pt")
        form_layout.addRow(self._field_label("TAMANHO DA FONTE"), self.font_size_spin)

        self.body_layout.addWidget(panel)

        # -- botao salvar -----------------------------------------
        save_row = QHBoxLayout()
        save_row.addStretch(1)
        self.save_btn = IconButton(text="SALVAR", icon="✔", color=Palette.NEON_GREEN)
        self.save_btn.clicked.connect(self._emit_save)
        save_row.addWidget(self.save_btn)
        self.body_layout.addLayout(save_row)
        self.body_layout.addStretch(1)

    def _field_label(self, text):
        label = QLabel(text)
        label.setFont(QFont(Fonts.DISPLAY[0], 10, QFont.DemiBold))
        label.setObjectName("SettingsFieldLabel")
        return label

    def _with_value(self, slider, value_label):
        from PySide6.QtWidgets import QWidget
        wrapper = QWidget()
        h = QHBoxLayout(wrapper)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(slider, 1)
        h.addWidget(value_label)
        return wrapper

    def _emit_save(self):
        data = {
            "username": self.username_edit.text(),
            "theme": self.theme_combo.currentText(),
            "volume": self.volume_slider.value(),
            "font_size": self.font_size_spin.value(),
        }
        self.save_requested.emit(data)
