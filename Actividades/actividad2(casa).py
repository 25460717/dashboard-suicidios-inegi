import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# 1. CARGAR ARCHIVO DE AUDIO REAL
# (Asegúrate de colocar un archivo .wav en tu carpeta de trabajo)
# fs, data = wavfile.read('tu_audio.wav')

# --- EJEMPLO GENERADO PARA PROBAR EL CÓDIGO DIRECTAMENTE ---
fs = 44100
t = np.linspace(0, 2, 2 * fs, endpoint=False)
audio_dummy = np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 880 * t) # Tono A4 (440Hz) y A5 (880Hz)
wavfile.write("audio_prueba.wav", fs, (audio_dummy * 32767).astype(np.int16))

# Cargar el archivo .wav
fs, data = wavfile.read("audio_prueba.wav")

# Si el audio es estéreo (2 canales), tomar solo un canal
if len(data.shape) > 1:
    data = data[:, 0]

# 2. CALCULAR FFT
N = len(data)
fft_vals = np.fft.fft(data)
freqs = np.fft.fftfreq(N, d=1/fs)

# 3. FILTRAR FRECUENCIAS POSITIVAS Y CALCULAR POTENCIA
pos_mask = freqs >= 0
freqs_pos = freqs[pos_mask]
power_spectrum = (np.abs(fft_vals[pos_mask]) ** 2) / N

# 4. IDENTIFICAR LA FRECUENCIA DOMINANTE
idx_max = np.argmax(power_spectrum)
frecuencia_dominante = freqs_pos[idx_max]

print(f"La frecuencia dominante del audio es: {frecuencia_dominante:.2f} Hz")

# 5. GRAFICAR PERIODOGRAMA DEL AUDIO
plt.figure(figsize=(12, 5))
plt.plot(freqs_pos, power_spectrum, color='purple')
plt.title("Periodograma del Audio Real")
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Potencia")
plt.xlim(0, 2000) # Límite para visualizar mejor el rango audible principal
plt.grid(True)
plt.show()