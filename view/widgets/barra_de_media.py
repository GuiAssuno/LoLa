
"""
MediaPlayerBar: rodape de ponta a ponta estilo "media player" (album art,
titulo/artista, controles, waveform animada, barra de progresso e a
proxima faixa) — inspirado em paineis automotivos modernos.

So INTERFACE. A waveform e uma animacao decorativa simulada (QTimer +
QPainter), leve para o RPi5. Para tocar audio de verdade, conecte sua
logica aos sinais/metodos publicos:

    bar.play_pause_clicked   (Signal)
    bar.next_clicked         (Signal)
    bar.previous_clicked     (Signal)
    bar.set_track("Titulo", "Artista")
    bar.set_next_track("Titulo", "Artista")
    bar.set_progress(current_seconds, total_seconds)
    bar.set_playing(True/False)   # troca o icone play/pause
"""
import random

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QLinearGradient
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QPushButton, QSizePolicy
)

from view.core.config import Palette, Fonts

def _format_time(seconds: int) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"

class _WaveformVisualizer(QWidget):
    def __init__(self, bars=64, parent=None):
        super().__init__(parent)
        self._n_bars = bars
        self._levels = [random.uniform(0.15, 0.9) for _ in range(bars)]
        self._playing = True
        self.setMinimumHeight(34)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._timer = QTimer(self)
        self._timer.setInterval(160)  # baixo custo de CPU no RPi5
        self._timer.timeout.connect(self._animate)
        self._timer.start()

    def set_playing(self, playing: bool):
        self._playing = playing

    def _animate(self):
        if not self._playing:
            return
        # variacao suave dos niveis (nao aleatorio "puro", parece mais organico)
        for i in range(self._n_bars):
            delta = random.uniform(-0.18, 0.18)
            self._levels[i] = min(1.0, max(0.08, self._levels[i] + delta))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        n = self._n_bars
        gap = 2
        bar_w = max(1.5, (w - gap * (n - 1)) / n)

        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, Palette.NEON_CYAN)
        grad.setColorAt(0.5, Palette.NEON_MAGENTA)
        grad.setColorAt(1.0, Palette.NEON_YELLOW)

        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        for i, level in enumerate(self._levels):
            bar_h = level * h
            x = i * (bar_w + gap)
            y = (h - bar_h) / 2
            p.drawRoundedRect(x, y, bar_w, bar_h, 1.5, 1.5)


class _TransportButton(QPushButton):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setObjectName("TransportButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 36)
        self.setFont(QFont(Fonts.DISPLAY[0], 13))


class MediaPlayerBar(QWidget):

    play_pause_clicked = Signal()
    next_clicked = Signal()
    previous_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MediaPlayerBar")
        self.setFixedHeight(92)
        self._is_playing = True
        self._total_seconds = 225  # 3:45 placeholder

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 10, 18, 10)
        root.setSpacing(18)

        # ---- bloco esquerdo: capa + titulo/artista + controles ----
        left = QHBoxLayout()
        left.setSpacing(10)

        self._album_art = QLabel("♪")
        self._album_art.setObjectName("AlbumArt")
        self._album_art.setFixedSize(56, 56)
        self._album_art.setAlignment(Qt.AlignCenter)
        self._album_art.setFont(QFont(Fonts.DISPLAY[0], 20))
        left.addWidget(self._album_art)

        track_box = QVBoxLayout()
        track_box.setSpacing(2)
        self._title_label = QLabel("The Tite Mon")
        self._title_label.setObjectName("TrackTitle")
        self._title_label.setFont(QFont(Fonts.DISPLAY[0], 12, QFont.Bold))
        self._artist_label = QLabel("Artist Lanon")
        self._artist_label.setObjectName("TrackArtist")
        self._artist_label.setFont(QFont(Fonts.MONO[0], 10))
        track_box.addWidget(self._title_label)
        track_box.addWidget(self._artist_label)
        left.addLayout(track_box)

        controls = QHBoxLayout()
        controls.setSpacing(4)
        self._prev_btn = _TransportButton("⏮")
        self._play_btn = _TransportButton("⏸")
        self._next_btn = _TransportButton("⏭")
        self._prev_btn.clicked.connect(self.previous_clicked.emit)
        self._next_btn.clicked.connect(self.next_clicked.emit)
        self._play_btn.clicked.connect(self._on_play_clicked)
        for b in (self._prev_btn, self._play_btn, self._next_btn):
            controls.addWidget(b)
        left.addLayout(controls)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(360)
        root.addWidget(left_widget)

        # ---- bloco central: waveform + progresso ----
        center = QVBoxLayout()
        center.setSpacing(4)

        self._waveform = _WaveformVisualizer()
        center.addWidget(self._waveform)

        progress_row = QHBoxLayout()
        self._time_current = QLabel("1:24")
        self._time_current.setObjectName("TimeLabel")
        self._time_total = QLabel("3:45")
        self._time_total.setObjectName("TimeLabel")
        self._progress_slider = QSlider(Qt.Horizontal)
        self._progress_slider.setRange(0, self._total_seconds)
        self._progress_slider.setValue(84)
        self._progress_slider.setFont(QFont(Fonts.MONO[0], 9))

        progress_row.addWidget(self._time_current)
        progress_row.addWidget(self._progress_slider, 1)
        progress_row.addWidget(self._time_total)
        center.addLayout(progress_row)

        root.addLayout(center, 1)

        # ---- bloco direito: proxima faixa ----
        right = QHBoxLayout()
        right.setSpacing(10)

        next_box = QVBoxLayout()
        next_box.setSpacing(2)
        next_caption = QLabel("PRÓXIMA")
        next_caption.setObjectName("NextCaption")
        next_caption.setFont(QFont(Fonts.DISPLAY[0], 8, QFont.DemiBold))
        self._next_title_label = QLabel("The Tite Mon")
        self._next_title_label.setFont(QFont(Fonts.DISPLAY[0], 11, QFont.Bold))
        self._next_artist_label = QLabel("Artist Lanon")
        self._next_artist_label.setFont(QFont(Fonts.MONO[0], 9))
        self._next_artist_label.setObjectName("TrackArtist")
        next_box.addWidget(next_caption)
        next_box.addWidget(self._next_title_label)
        next_box.addWidget(self._next_artist_label)
        right.addLayout(next_box)

        self._next_album_art = QLabel("♪")
        self._next_album_art.setObjectName("AlbumArt")
        self._next_album_art.setFixedSize(48, 48)
        self._next_album_art.setAlignment(Qt.AlignCenter)
        self._next_album_art.setFont(QFont(Fonts.DISPLAY[0], 16))
        right.addWidget(self._next_album_art)

        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setFixedWidth(240)
        root.addWidget(right_widget)

    # -- API publica -----------------------------------------------------
    def set_track(self, title: str, artist: str):
        self._title_label.setText(title)
        self._artist_label.setText(artist)

    def set_next_track(self, title: str, artist: str):
        self._next_title_label.setText(title)
        self._next_artist_label.setText(artist)

    def set_progress(self, current_seconds: int, total_seconds: int):
        self._total_seconds = total_seconds
        self._progress_slider.setRange(0, total_seconds)
        self._progress_slider.setValue(current_seconds)
        self._time_current.setText(_format_time(current_seconds))
        self._time_total.setText(_format_time(total_seconds))

    def set_playing(self, playing: bool):
        self._is_playing = playing
        self._play_btn.setText("⏸" if playing else "▶")
        self._waveform.set_playing(playing)

    def _on_play_clicked(self):
        self.set_playing(not self._is_playing)
        self.play_pause_clicked.emit()
