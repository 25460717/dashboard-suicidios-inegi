import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. GENERAR LA SENAL SINTETICA
# ---------------------------------------------------------
fs = 1000          # Frecuencia de muestreo (1000 Hz)
t_lim = 1.0        # Duracion de 1 segundo
t = np.linspace(0, t_lim, int(fs * t_lim), endpoint=False)

# Tonos senoidales de prueba
f1 = 50   # Hz
f2 = 120  # Hz

# Senal pura + Ruido Gaussiano
seno1 = 2.0 * np.sin(2 * np.pi * f1 * t)
seno2 = 1.5 * np.sin(2 * np.pi * f2 * t)
ruido = np.random.normal(0, 1.5, size=t.shape)

signal = seno1 + seno2 + ruido

# ---------------------------------------------------------
# 2. CALCULAR FFT Y EJE DE FRECUENCIAS
# ---------------------------------------------------------
N = len(signal)
fft_vals = np.fft.fft(signal)
freqs = np.fft.fftfreq(N, d=1/fs)

# ---------------------------------------------------------
# 3. QUEDARSE SOLO CON FRECUENCIAS POSITIVAS Y PERIODOGRAMA
# ---------------------------------------------------------
pos_mask = freqs >= 0
freqs_pos = freqs[pos_mask]

# Periodograma (Espectro de Potencia): |FFT|^2 / N
power_spectrum = (np.abs(fft_vals[pos_mask]) ** 2) / N

# ---------------------------------------------------------
# 4. IDENTIFICAR PICOS DOMINANTES CON np.argmax
# ---------------------------------------------------------
# Copiamos el espectro para buscar los dos picos mas altos
ps_copy = power_spectrum.copy()

# Primer pico mas dominante
idx1 = np.argmax(ps_copy)
freq_pico1 = freqs_pos[idx1]

# Enmascaramos la zona alrededor del primer pico para encontrar el segundo
ventana = 5
idx_min = max(0, idx1 - ventana)
idx_max = min(len(ps_copy), idx1 + ventana)
ps_copy[idx_min:idx_max] = 0

# Segundo pico mas dominante
idx2 = np.argmax(ps_copy)
freq_pico2 = freqs_pos[idx2]

print(f"Frecuencias originales usadas: {f1} Hz y {f2} Hz")
print(f"Frecuencias detectadas con np.argmax: {freq_pico1:.1f} Hz y {freq_pico2:.1f} Hz")

# ---------------------------------------------------------
# GRAFICAR
# ---------------------------------------------------------
plt.figure(figsize=(12, 5))

# Grafica del Periodograma
plt.plot(freqs_pos, power_spectrum, color='b', label='Periodograma')
plt.axvline(freq_pico1, color='r', linestyle='--', label=f'Pico 1: {freq_pico1:.1f} Hz')
plt.axvline(freq_pico2, color='g', linestyle='--', label=f'Pico 2: {freq_pico2:.1f} Hz')

plt.title("Periodograma de la Senal Sintetica (Frecuencias Positivas)")
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Potencia")
plt.xlim(0, 200)  # Enfocar en el rango de interés
plt.legend()
plt.grid(True)
plt.show()