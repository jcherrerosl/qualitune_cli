import librosa
import numpy as np

def analyze_bands(filepath):
    try:
        y, sr = librosa.load(filepath, sr=44100, mono=True)

        def band_energy(y, sr, fmin, fmax):
            S = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)
            band = np.logical_and(freqs >= fmin, freqs <= fmax)
            if not np.any(band):
                return 0
            return np.mean(S[band, :])

        sub_bass = band_energy(y, sr, 20, 60)
        bass = band_energy(y, sr, 60, 120)
        low_mids = band_energy(y, sr, 120, 300)
        mids = band_energy(y, sr, 300, 2000)
        highs = band_energy(y, sr, 2000, 7500)
        air = band_energy(y, sr, 7500, 15000)

        return {
            "sub_bass": round(sub_bass, 4),
            "bass": round(bass, 4),
            "low_mids": round(low_mids, 4),
            "mids": round(mids, 4),
            "highs": round(highs, 4),
            "air": round(air, 4),
        }

    except Exception as e:
        raise RuntimeError(f"Error analyzing {filepath}: {e}")