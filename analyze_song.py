from frequencies import analyze_bands
from dynamics import analyze_dynamics
from noise import analyze_noise
from tuning import separate_audio, check_tune
import librosa
import numpy as np

def analyze_song(filepath):
    # Cargar el audio completo para noise
    y, sr = librosa.load(filepath, sr=44100, mono=True)

    # Módulos de análisis
    bands = analyze_bands(filepath)
    dynamics = analyze_dynamics(filepath)
    noise_str = analyze_noise(y, sr)
    vocals, sr_vocals = separate_audio(filepath)
    tuning_str = check_tune(vocals, sr_vocals)

    # Parsear resultado de ruido
    try:
        noise_ratio = float(noise_str.split()[2])
    except:
        noise_ratio = np.nan

    # Parsear resultado de afinación
    try:
        tuning_conf = float(tuning_str.split("Confidence: ")[-1])
    except:
        tuning_conf = np.nan

    # Consolidar y devolver
    return {
        **bands,
        **dynamics,
        "noise_ratio": round(noise_ratio, 4),
        "tuning_conf": round(tuning_conf, 4)
    }
