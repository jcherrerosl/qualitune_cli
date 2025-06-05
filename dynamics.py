import librosa
import numpy as np
import pyloudnorm as pyln

def analyze_dynamics(filepath):
    try:
        y, sr = librosa.load(filepath, sr=44100, mono=True)
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(y)
        rms_total = np.mean(librosa.feature.rms(y=y))
        peak = np.max(np.abs(y))
        crest_factor = peak / rms_total if rms_total > 0 else 0
        clipping = np.sum(np.abs(y) >= 0.99) / len(y)

        return {
            "lufs": round(loudness, 2),
            "rms": round(rms_total, 6),
            "crest_factor": round(crest_factor, 2),
            "clipping_ratio": round(clipping, 6),
        }

    except Exception as e:
        raise RuntimeError(f"Error analyzing {filepath}: {e}")