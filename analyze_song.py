import librosa
import numpy as np
import pyloudnorm as pyln

def analyze_song(filepath):
    try:
        y, sr = librosa.load(filepath, sr=44100, mono=True)
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(y)
        rms_total = np.mean(librosa.feature.rms(y=y))
        peak = np.max(np.abs(y))
        crest_factor = peak / rms_total if rms_total > 0 else 0

        def band_energy(y, sr, fmin, fmax):
            S = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)
            band = np.logical_and(freqs >= fmin, freqs <= fmax)
            if not np.any(band):
                return 0
            return np.mean(S[band, :])

        bass = band_energy(y, sr, 20, 120)
        mids = band_energy(y, sr, 300, 3000)
        highs = band_energy(y, sr, 6000, 12000)
        clipping = np.sum(np.abs(y) >= 0.99) / len(y)

        return {
            "lufs": round(loudness, 2),
            "rms": round(rms_total, 6),
            "crest_factor": round(crest_factor, 2),
            "bass_energy": round(bass, 6),
            "mid_energy": round(mids, 6),
            "high_energy": round(highs, 6),
            "clipping_ratio": round(clipping, 6),
        }

    except Exception as e:
        raise RuntimeError(f"Error analyzing {filepath}: {e}")
