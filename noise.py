import numpy as np
from scipy.signal import find_peaks
import librosa

def calculate_noise_ratio(y, sr, n_fft=16384, min_peak_height=0.05, freq_range=(50, 16000)):
    # Aplicar ventana de Hann para reducir fugas espectrales
    window = np.hanning(len(y))
    y_windowed = y * window
    
    # Calcular FFT de toda la señal
    spectrum = np.abs(np.fft.rfft(y_windowed, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1/sr)
    
    # Limitar al rango de frecuencias relevante
    freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    spectrum = spectrum[freq_mask]
    freqs = freqs[freq_mask]
    
    # Detectar picos armónicos
    peaks, _ = find_peaks(spectrum, height=np.max(spectrum)*min_peak_height, distance=10)
    
    # Crear máscara para componentes armónicos (picos + vecindario)
    harmonic_mask = np.zeros_like(spectrum, dtype=bool)
    peak_width = 8  # bins de frecuencia a cada lado del pico
    for p in peaks:
        start = max(0, p - peak_width)
        end = min(len(spectrum), p + peak_width)
        harmonic_mask[start:end] = True
    
    # Calcular energías
    harmonic_energy = np.sum(spectrum[harmonic_mask])
    noise_energy = np.sum(spectrum[~harmonic_mask])
    total_energy = harmonic_energy + noise_energy
    
    # Evitar división por cero
    if total_energy == 0:
        return 0.0
    
    return noise_energy / total_energy