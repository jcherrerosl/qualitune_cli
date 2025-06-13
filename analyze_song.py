from frequencies import analyze_bands
from dynamics import analyze_dynamics
from noise import calculate_noise_ratio
from tuning import separate_audio, check_tune
import librosa
import numpy as np

def analyze_song(filepath, target_sr=44100):
    results = {}

    try:
        y, sr = librosa.load(filepath, sr=target_sr, mono=True)
    except Exception as e:
        return {
            'error': f"Error loading audio: {e}",
            'frequency_bands': None,
            'dynamics': None,
            'noise_ratio': np.nan,
            'tuning': {'pitch': None, 'confidence': np.nan}
        }

    # Frecuencias
    try:
        results['frequency_bands'] = analyze_bands(y, sr)
    except Exception as e:
        results['frequency_bands'] = None

    # Dinámica
    try:
        results['dynamics'] = analyze_dynamics(y, sr)
    except Exception as e:
        results['dynamics'] = None

    # Ruido
    try:
        results['noise_ratio'] = calculate_noise_ratio(y, sr)
    except Exception as e:
        results['noise_ratio'] = np.nan

    # Afinación vocal
    try:
        vocals, sr_vocals = separate_audio(y, sr)
        tuning_results = check_tune(vocals, sr_vocals)

        if isinstance(tuning_results, dict):
            results['tuning'] = tuning_results
        else:
            try:
                results['tuning'] = {
                    'pitch': tuning_results.split("Note: ")[1].split(",")[0],
                    'confidence': float(tuning_results.split("Confidence: ")[1])
                }
            except:
                results['tuning'] = {'pitch': None, 'confidence': np.nan}
    except Exception as e:
        results['tuning'] = {'pitch': None, 'confidence': np.nan}

    results['error'] = None
    return results
