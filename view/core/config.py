from PySide6.QtGui import QColor

# ---------------------------------------------------------------------------
# Paleta "retro neon"
# ---------------------------------------------------------------------------
class Palette:
    BG_DARK = QColor("#05010f")        # fundo geral (quase preto, base do "profundidade")
    BG_PANEL = QColor("#0d0221")       # fundo dos paineis
    BG_PANEL_LIGHT = QColor("#150a30")

    NEON_CYAN = QColor("#00fff0")
    NEON_MAGENTA = QColor("#ff00c8")
    NEON_PURPLE = QColor("#7d12ff")
    NEON_YELLOW = QColor("#f6ff00")
    NEON_GREEN = QColor("#00ff85")
    NEON_RED = QColor("#ff2b4d")

    TEXT_PRIMARY = QColor("#e6faff")
    TEXT_DIM = QColor("#7a90b3")

    GRID_LINE = QColor(0, 255, 240, 35)


class Fonts:
    DISPLAY = ["Orbitron", "Eurostile", "Segoe UI", "sans-serif"]
    MONO = ["Share Tech Mono", "Consolas", "DejaVu Sans Mono", "monospace"]


class UI:
    CORNER_RADIUS = 14
    GLOW_BLUR_RADIUS = 28
    ANIMATION_MS = 260
    FOOTER_ROTATE_MS = 4000
    DESIGN_WIDTH = 1280
    DESIGN_HEIGHT = 800
