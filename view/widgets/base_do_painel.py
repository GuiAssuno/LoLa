from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from view.core.config import Palette, UI


class NeonPanel(QFrame):
    def __init__(self, parent=None, glow_color: QColor = None, glow_strength: int = 22):
        super().__init__(parent)
        self.setObjectName("NeonPanel")
        self._glow_color = glow_color or Palette.NEON_CYAN
        self._apply_glow(glow_strength)

    def _apply_glow(self, strength: int):
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(strength)
        effect.setOffset(0, 0)
        c = QColor(self._glow_color)
        c.setAlpha(180)
        effect.setColor(c)
        self.setGraphicsEffect(effect)

    def set_glow_color(self, color: QColor):
        self._glow_color = color
        self._apply_glow(UI.GLOW_BLUR_RADIUS)
