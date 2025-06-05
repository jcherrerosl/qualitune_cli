from frequencies import analyze_bands
from dynamics import analyze_dynamics
from noise import analyze_noise
from tuning import separate_audio, check_tune
import librosa

def rate_song(filepath):
    y, sr = librosa.load(filepath, sr=44100, mono=True)

    bands = analyze_bands(filepath)
    dynamics = analyze_dynamics(filepath)
    noise = analyze_noise(y, sr)
    vocals, sr_vocals = separate_audio(filepath)
    tuning_result = check_tune(vocals, sr_vocals)

    score = 0

    if dynamics["lufs"] >= -14:
        score += 1
    if dynamics["crest_factor"] >= 2 and dynamics["crest_factor"] <= 4:
        score += 1
    if dynamics["clipping_ratio"] < 0.01:
        score += 1