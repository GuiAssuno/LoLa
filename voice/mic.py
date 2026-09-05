import queue
import sys
import json
import sounddevice as sd
# Adicione SetLogLevel na importação
from vosk import Model, KaldiRecognizer, SetLogLevel

# Fila para armazenar os blocos de áudio
q = queue.Queue()

# Ativa os logs do motor C++ do Vosk
SetLogLevel(1) 

# Função que o sounddevice chama toda vez que captura um bloco de áudio
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))



print("Carregando modelo...")
# Carrega o modelo da pasta 'model' (certifique-se que ela está no mesmo diretório)
model = Model(r"e:\VsCode\LoLa\voice\model")

# Configura o reconhecedor para a taxa de amostragem de 16000Hz
recognizer = KaldiRecognizer(model, 16000)

print("\nMicrofone aberto! Pode começar a falar. (Pressione Ctrl+C para sair)")

# Abre o microfone usando o sounddevice
try:
    with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, dtype='int16',
                           channels=1, callback=callback):
        while True:
            # Pega o áudio da fila
            data = q.get()
            
            # O Vosk analisa o áudio. Se ele detectar o fim de uma frase, retorna True.
            if recognizer.AcceptWaveform(data):
                resultado = json.loads(recognizer.Result())
                texto = resultado.get("text", "")
                if texto:
                    print(f"Você disse: {texto}")
            else:
                # Se quiser ver o texto sendo formado em tempo real, descomente as duas linhas abaixo:
                parcial = json.loads(recognizer.PartialResult())
                print(parcial.get("partial", ""), end='\r')
                pass

except KeyboardInterrupt:
    print("\n\nCaptura encerrada pelo usuário.")
except Exception as e:
    print(f"\nOcorreu um erro: {e}")