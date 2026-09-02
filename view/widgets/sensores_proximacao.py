import math
# bibliotecas Qt
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

# bibliotecas internas do projeto
from view.core.config import Palette, Fonts
from view.widgets.base_do_painel import NeonPanel
 
CORNERS = ("fe", # frente-esquerda
           "fd", # frente-direita
           "te", # traseira-esquerda
           "td"  # traseira-direita
)

#========================================== Nivel de Cor ========================================================
def _NivelCor(nivel: float) -> QColor:
    """Intercala verde(0.0) → amarelo(0.5) → vermelho(1.0) em uma escala de 0.0 a 1.0"""
    nivel = max(0.0, min(1.0, nivel))
#_________________________________________verde -> amarelo_______________________________________________________
    if nivel < 0.5: 
        t = nivel / 0.5
        r = int(Palette.NEON_GREEN.red()   + t * (Palette.NEON_YELLOW.red()   - Palette.NEON_GREEN.red()))
        g = int(Palette.NEON_GREEN.green() + t * (Palette.NEON_YELLOW.green() - Palette.NEON_GREEN.green()))
        b = int(Palette.NEON_GREEN.blue()  + t * (Palette.NEON_YELLOW.blue()  - Palette.NEON_GREEN.blue()))
#_________________________________________amarelo -> vermelho____________________________________________________
    else: 
        t = (nivel - 0.5) / 0.5
        r = int(Palette.NEON_YELLOW.red()   + t * (Palette.NEON_RED.red()   - Palette.NEON_YELLOW.red()))
        g = int(Palette.NEON_YELLOW.green() + t * (Palette.NEON_RED.green() - Palette.NEON_YELLOW.green()))
        b = int(Palette.NEON_YELLOW.blue()  + t * (Palette.NEON_RED.blue()  - Palette.NEON_YELLOW.blue()))
    return QColor(r, g, b)

#================================================================================================================
#========================================== Classe DesenhoCarro =================================================
#================================================================================================================
class _DesenhoCarro(QWidget):
    """Desenho do carro com radares de proximidade e os chips de sensores de peneus (TPMS). 
    So INTERFACE, sem logica de sensores - use os metodos publicos set_aproximidade() e set_pressao_pneu()"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(180, 260)

        self.sensor_de_aproximidade = {"fe": 0.2, "fd": 0.5, "te": 0.75, "td": 0.3} # DADO MOCK
        self.sensor_do_pneu = {"fe": None, "fd": None, "te": None, "td": None} # DADO MOCK
#________________________________________________________________________________________________set_aproximidade
    def set_aproximidade(self, sensor, level):
        """Atualiza o nivel de aproximidade do sensor do carro"""
        if sensor in self.sensor_de_aproximidade:
            self.sensor_de_aproximidade[sensor] = max(0.0, min(1.0, level))
            self.update()
#________________________________________________________________________________________________set_pressao_pneu
    def set_pressao_pneu(self, pneu, psi):
        """Atualiza a pressao do pneu"""
        if pneu in self.sensor_do_pneu:
            self.sensor_do_pneu[pneu] = psi
            self.update()
#________________________________________________________________________________________________set_pressao_pneu

    def paintEvent(self, event):
        """Desenha o carro, os radares de aproximação e os chips de pressao dos pneus"""

        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        largura, altura = self.width(), self.height()
        centro_x, centro_y = largura / 2, altura / 2

        car_largura = min(largura * 0.34, 110)
        car_altura  = min(altura  * 0.62, 320)
        
        self._DesenhaSensores(pintor, centro_x, centro_y, car_largura, car_altura)      # Desenho as ondas de aproximidade
        self._DesenhaCorpoCarro(pintor, centro_x, centro_y, car_largura, car_altura)    # Desenho o corpo do carro visto de cima
        self._DesenhaSensorPressao(pintor, centro_x, centro_y, car_largura, car_altura) # Desenho os sensores de pressao dos pneus

    def _DesenhaCorpoCarro(self, p: QPainter, centro_x, centro_y, car_largura, car_altura):
        """Desenha o corpo do carro visto de cima
        com para-brisa e rodas no formato de retangulo arredondado"""

        corpo_retangulo = QRectF(centro_x - car_largura / 2, centro_y - car_altura / 2, car_largura, car_altura)

        pen = QPen(Palette.NEON_CYAN)
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QColor(10, 20, 35, 140))
        p.drawRoundedRect(corpo_retangulo, car_largura * 0.28, car_largura * 0.28)

        # para-brisa
        para_brisa = QRectF(centro_x - car_largura * 0.32, centro_y - car_altura * 0.36, car_largura * 0.64, car_altura * 0.16)
        p.setPen(QPen(QColor(0, 255, 240, 120), 1))
        p.setBrush(QColor(0, 255, 240, 25))
        p.drawRoundedRect(para_brisa, 6, 6)

        # rodas
        pneu_largura, pneu_altura = car_largura * 0.16, car_altura * 0.14
        offsets = {
            "fe": (-car_largura / 2 - pneu_largura * 0.3, -car_altura * 0.30),
            "fd": ( car_largura / 2 - pneu_largura * 0.7, -car_altura * 0.30),
            "te": (-car_largura / 2 - pneu_largura * 0.3,  car_altura * 0.16),
            "td": ( car_largura / 2 - pneu_largura * 0.7,  car_altura * 0.16),
        }

        p.setPen(QPen(Palette.TEXT_DIM, 1))
        p.setBrush(QColor(20, 20, 28))

        for delta_x, delta_y in offsets.values():
            p.drawRoundedRect(
                QRectF(centro_x + delta_x, # Left
                       centro_y + delta_y, # Top
                       pneu_largura,       # Weidth
                       pneu_altura),       # Height       

                3, # Radius X
                3 # Radius Y
            )
#________________________________________________________________________________________________DesenhaSensores
    def _DesenhaSensores(self, p: QPainter, centro_x, centro_y, car_largura, car_altura):
        """Desenha os radares de aproximação 
            direcao_sensor aponta a direção: 
            0°    →  Direita 
            90°   ↑  Cima
            180°  ←  Esquerda 
            270°  ↓  Baixo"""

        posicao_sensores = { # Lado: (x, y, angulo_base_graus)
            "fe": (centro_x - car_largura / 2, centro_y - car_altura / 2, 135), 
            "fd": (centro_x + car_largura / 2, centro_y - car_altura / 2, 45),
            "te": (centro_x - car_largura / 2, centro_y + car_altura / 2, 225),
            "td": (centro_x + car_largura / 2, centro_y + car_altura / 2, 315),
        }

        # Desenha cada sensor de aproximidade
        for sensor, (x, y, direcao_sensor) in posicao_sensores.items(): 
            nivel = self.sensor_de_aproximidade.get(sensor, 0.0) 
            cor = _NivelCor(nivel)
            numero_de_arcos = 3
            maximo_radianos = 34

            # para cada sensor, desenha 3 arcos
            for i in range(1, numero_de_arcos + 1): 
                radianos = maximo_radianos * i / numero_de_arcos
                transparencia = int(60 + 130 * (i / numero_de_arcos)) if nivel > 0.02 else 40 # transparencia do arco (quanto mais proximo, mais opaco)
                pen = QPen(QColor(cor.red(),   # Red
                                  cor.green(), # Green
                                  cor.blue(),  # Blue
                                  transparencia))      # Tranparencia
            
                pen.setWidth(4)                          # largura da linha do arco
                pen.setCapStyle(Qt.PenCapStyle.RoundCap) # Ponta da linha do arco SquareCap=Quadrado | RoundCap=Arredondas
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                retangulo = QRectF(x - radianos, y - radianos, radianos * 2, radianos * 2)
                # arco de 70 graus centrado no angulo-base (aponta pra fora do carro)
                p.drawArc(retangulo, int((direcao_sensor - 35) * 16), int(70 * 16))

#________________________________________________________________________________________________DesenhaSensorPressao
    def _DesenhaSensorPressao(self, pintor: QPainter, centro_x, centro_y, car_largura, car_altura):
        """Desenha os chips de pressao dos pneus"""

        positions = { # Lado: (x, y, alinhamento)
            "fe": (centro_x - car_largura / 2 - 46, centro_y - car_altura * 0.30, Qt.AlignRight),
            "fd": (centro_x + car_largura / 2 + 4,  centro_y - car_altura * 0.30, Qt.AlignLeft),
            "te": (centro_x - car_largura / 2 - 46, centro_y + car_altura * 0.16, Qt.AlignRight),
            "td": (centro_x + car_largura / 2 + 4,  centro_y + car_altura * 0.16, Qt.AlignLeft),
        }

        pintor.setFont(QFont(Fonts.MONO[0], 8, QFont.DemiBold))

        for pneu, (x, y, alinhamento) in positions.items():
            psi = self.sensor_do_pneu.get(pneu)
            text = f"{psi} PSI" if psi is not None else "-- PSI"
            retangulo = QRectF(x, y, 42, 26)
            pintor.setPen(QPen(Palette.NEON_GREEN, 1))
            pintor.setBrush(QColor(5, 1, 15, 200))
            pintor.drawRoundedRect(retangulo, 5, 5)
            pintor.setPen(Palette.TEXT_PRIMARY)
            pintor.drawText(retangulo, alinhamento, text)

#================================================================================================================
#======================================== Classe PainelSensorCarro ==============================================
#================================================================================================================
class PainelSensorCarro(NeonPanel):
    """Painel de sensores de proximidade e pressao dos pneus"""
    def __init__(self, parent=None):
        super().__init__(parent, glow_color=Palette.NEON_MAGENTA, glow_strength=20)
        self.setObjectName("PainelSensorCarro")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        titulo = QLabel("◈ SENSORES DE APROXIMIDADE")
        titulo.setObjectName("TituloPainel")
        layout.addWidget(titulo)

        self._desenho = _DesenhoCarro()
        layout.addWidget(self._desenho, stretch=1)

    def set_aproximidade(self, sensor: str, level: float):
        self._desenho.set_aproximidade(sensor, level)

    def set_pressao_pneu(self, pneu: str, psi):
        self._desenho.set_pressao_pneu(pneu, psi)
