import queue
import sys
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel


q = queue.Queue()

SetLogLevel(1) 

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


model = Model(r"e:\VsCode\LoLa\voice\model")
recognizer = KaldiRecognizer(model, 16000)


try:
    with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            
            if recognizer.AcceptWaveform(data):
                resultado = json.loads(recognizer.Result())
                texto = resultado.get("text", "")
                if texto:
                    print(f"Você disse: {texto}")
            else:
                pass

except KeyboardInterrupt:
    print("\n\nCaptura encerrada.")
except Exception as e:
    print(f"\nerro: {e}")
    