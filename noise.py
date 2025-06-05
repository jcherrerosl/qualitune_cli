from scipy.signal import find_peaks
import numpy as np
import librosa

def analyze_noise(y, sr):
    # FFT con ventana grande para resolución frecuencial fina
    n_fft = 16384
    spectrum = np.abs(np.fft.rfft(y, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1/sr)

    # Detección de picos (armónicos esperados)
    peaks, _ = find_peaks(spectrum, height=np.max(spectrum)*0.1, distance=20)

    # Crear máscara de picos (zonas que se consideran armónicas)
    harmonic_mask = np.zeros_like(spectrum, dtype=bool)
    peak_width = 5  # rango de tolerancia en bins
    for p in peaks:
        harmonic_mask[max(0, p - peak_width):p + peak_width] = True

    # Separar energía tonal y ruido
    harmonic_energy = np.sum(spectrum[harmonic_mask])
    noise_energy = np.sum(spectrum[~harmonic_mask])

    noise_ratio = noise_energy / (harmonic_energy + noise_energy)

    return f"Noise ratio: {noise_ratio:.3f} ({noise_ratio*100:.1f}% del contenido es no armónico)"
