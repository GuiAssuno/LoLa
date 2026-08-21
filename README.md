# LoLa

**Central de Controle Embarcada de Alta Performance para monitoramento e operação de maquinário crítico.**

---

## Objetivo do Projeto

O sistema **Kiosk** é um Hub IoT desenhado para operar como uma central de controle embarcada de alta performance. Ele foi projetado para o monitoramento e operação de maquinário crítico, como motores a combustão e geradores elétricos. 

O sistema exige e garante:
- **Latência zero na interface gráfica (60 FPS).**
- **Isolamento de falhas de rede (Sandboxing).**
- **Inteligência artificial rodando localmente (Edge AI).**
- **Controle físico de injeção em tempo real estrito (Hard Real-Time).**

---

## Módulos e Funcionalidades Principais

### Estrutura Visual e Interface
- **Modo Kiosk:** Aplicação em tela cheia usando `QMainWindow`, com responsividade garantida por `QGridLayout` e `QVBoxLayout`.
- **Gestão de Memória:** Navegação em camadas com `QStackedWidget` (Home, Mapas, Player) evitando a sobrecarga de múltiplas janelas.
- **Visual Retrô Neon:** Estilização via arquivos **QSS** focada em cores escuras e bordas brilhantes, incrementada com `QGraphicsDropShadowEffect` para um efeito "glow" tridimensional.

### Navegação e GPS Offline
- **Mapa Base:** Renderização offline utilizando `QWebEngineView`, executando HTML local com **Leaflet.js** e tiles de mapa armazenados no disco.
- **Telemetria de Localização:** Leitura de coordenadas do módulo **NEO-6M** via interface serial (`pyserial`) atualizando dinamicamente a posição do veículo.
- **Traçado de Rotas:** Servidor **OSRM** rodando localmente em background, eliminando a necessidade de serviços em nuvem.

### Multimídia e Conectividade
- **Player de Música Automotivo:** Protocolos **A2DP** e **AVRCP** nativos para streaming de áudio, metadados (artista, música) e controles físicos.
- **Telefone Automotivo Integrado:** Protocolo **HFP** (Hands-Free Profile) convertendo o Hub em um viva-voz autêntico com identificador de chamadas.

### Interação por Voz e WhatsApp (Ponte)
- **Assistente Offline:** Integração com `pyttsx3` (Text-to-Speech) e `Vosk` (Speech-to-Text).
- **WhatsApp Bridge:** Aplicativo Android auxiliar no smartphone do usuário para espelhar notificações no Kiosk e injetar áudio convertido em texto como resposta no WhatsApp, contornando limitações do Bluetooth padrão.

---

## Arquitetura do Sistema (Camadas)

A arquitetura foi dividida rigorosamente em 4 camadas para isolar falhas externas e proteger as rotinas críticas de hardware.

### Camada 0: Controle Crítico e Reflexo (Hard Real-Time)
Interação direta com hardware físico sob intenso ruído eletromagnético (EMI).
- **Módulo de Injeção/Ignição (Arduino / STM32):** Bare-metal (sem SO), execução puramente determinística para leitura da roda fônica e acionamento de injetores em nanossegundos.
- **Módulo de Telemetria (ESP32):** Leitura de sensores (temperatura, pressão de óleo, bateria) enviando pacotes de dados consolidados via UART (TX/RX).

### Camada 1: Firewall e Rede Externa (Telemetria Remota)
A zona de *Sandboxing* para blindagem de falhas.
- **Hardware:** Raspberry Pi Zero 2 W.
- **Função:** Gerenciamento Bluetooth e pareamento. Em caso de envio de pacotes corrompidos ou travamentos no app, isola o problema da interface principal. Transmite dados filtrados para a Camada 2.

### Camada 2: O Cérebro Lógico e Visual (Application Layer)
O "Cockpit" ultrafluido do sistema.
- **Hardware:** Raspberry Pi 5 (Offline).
- **SO:** Raspberry Pi OS Lite (64-bit) (com opção de patch `PREEMPT_RT`).
- **Interface Gráfica:** **Labwc (Wayland)** em Modo Kiosk rodando **Python com PyQt6** (ou PySide6).
- **Otimização Extrema:** Divisão de processamento via `multiprocessing`: GUI blindada no Núcleo 1, Sensores no Núcleo 2, Áudio no Núcleo 3.

### Camada 3: Aceleração Matemática (IA e Áudio)
Processamento pesado delegado para coprocessadores, resfriando a CPU principal.
- **Visão Computacional:** **Raspberry Pi AI Kit (Hailo-8L NPU)** via PCIe rodando YOLO (INT8) para identificação a 60 FPS com câmeras MIPI (via CSI-HDMI).
- **Processamento de Áudio (Offline):** **whisper.cpp** para STT e **Piper TTS** para conversão de texto. Ferramentas compiladas em C/C++ importadas via `ctypes`.

---

## Tecnologias e Protocolos

| Categoria | Tecnologia | Detalhe |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python 3 | Orquestração, `multiprocessing` e controle lógico (`pathlib`). |
| **Linguagem de Baixo Nível** | C / C++ | Otimização (`-O3`) e integração de dados seriais/áudio usando `ctypes`. |
| **Deploy de Código** | WinSCP / FileZilla | SFTP via Wi-Fi local; sem necessidade de remover o MicroSD do Hub. |
| **Ambiente Isolado** | `.venv` | Isolamento das libs (PyQt6, pyserial, OpenCV) na arquitetura ARM64 (Pi 5). |
| **Comunicação Interna** | UART / I2C | Utilização das 5 portas UART nativas do Pi 5 para comunicação sem lag. |

---

## Configurações Críticas de Sistema

1. **Boot Direto (Kiosk):** Autologin no console onde `~/.bash_profile` dispara o gerenciador de janelas `exec labwc`. Por sua vez, o `~/.config/labwc/autostart` chama a aplicação principal via `.venv/bin/python main.py &`.
2. **Caminhos de Arquivos (Paths Absolutos):** Proibido o uso de caminhos relativos em string. Utilização obrigatória da biblioteca `pathlib` (ex: `Path(__file__).parent / "assets/logo.png"`) para prevenir "File Not Found" no script de boot.
3. **Liberação de Hardware:** Uso obrigatório do `sudo raspi-config` para desabilitar o terminal do console na serial e liberar os pinos físicos TX/RX para hardware nativo.
4. **Isolamento de Voltagem:** OBRIGATÓRIO o uso de Conversores de Nível Lógico (*Logic Level Converters*) entre redes de 5V (Arduino) e 3.3V (Raspberry/ESP32) para proteção elétrica dos CIs.
