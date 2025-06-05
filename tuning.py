from spleeter.separator import Separator
import librosa
import numpy as np
import librosa.display

def separate_audio(filepath):
    separator = Separator('spleeter:2stems')

    y, sr = librosa.load(filepath, sr=44100, mono=True)
    y = np.stack([y, y], axis=1)  # Convert to stereo by duplicating the mono signal

    prediction = separator.separate(y)
    
    vocals = prediction['vocals']
    vocals_mono = np.mean(vocals, axis=1)
    return vocals_mono, sr

def check_tune(vocals_mono, sr):
    
    f0, voice_flag, voice_probs = librosa.pyin(
        vocals_mono, 
        fmin=librosa.note_to_hz('C2'), 
        fmax=librosa.note_to_hz('C7'), 
        sr=sr
    )

    f0_clean = f0[~np.isnan(f0)]
    if len(f0_clean) == 0:
        return "No pitch detected"
    
    avg_pitch = np.mean(f0_clean)
    avg_note = librosa.hz_to_note(avg_pitch)

    return f"Average pitch: {avg_pitch:.2f} Hz, Note: {avg_note}, Confidence: {np.nanmean(voice_probs):.2f}"

