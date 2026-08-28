from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from view.core.config import Palette, UI


class NeonPanel(QFrame):
    def __init__(self, parent=None, glow_color: QColor = None, glow_strength: int = 22):
        super().__init__(parent)
        self.setObjectName("NeonPanel")
        self._glow_cor = glow_color or Palette.NEON_CYAN
        self._aplicar_glow(glow_strength)

    def _aplicar_glow(self, intensidade: int):
        efeito = QGraphicsDropShadowEffect(self)
        efeito.setBlurRadius(intensidade)
        efeito.setOffset(0, 0)
        cor = QColor(self._glow_cor)
        cor.setAlpha(180)
        efeito.setColor(cor)
        self.setGraphicsEffect(efeito)

    def set_glow_cor(self, cor: QColor):
        self._glow_cor = cor
        self._aplicar_glow(UI.GLOW_BLUR_RADIUS)
