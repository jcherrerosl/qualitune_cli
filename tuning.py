from spleeter.separator import Separator
import librosa
import numpy as np
import librosa.display
import soundfile as sf
import tempfile
import os

def separate_audio(y, sr):
    try:
        # Baja a 22050 Hz
        y_resampled = librosa.resample(y, orig_sr=sr, target_sr=22050)

        # Archivo temporal .wav
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
            temp_path = tmpfile.name
            sf.write(temp_path, y_resampled, 22050)

        output_dir = os.path.dirname(temp_path)
        separator = Separator('spleeter:2stems')
        separator.separate_to_file(temp_path, output_dir)

        vocal_path = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(temp_path))[0],
            'vocals.wav'
        )

        vocals, _ = librosa.load(vocal_path, sr=22050)

        # Limpieza
        os.remove(temp_path)
        os.remove(vocal_path)
        os.rmdir(os.path.dirname(vocal_path))

        return vocals, 22050

    except Exception as e:
        print(f"[ERROR] Error al separar audio: {e}")
        return None, sr



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

