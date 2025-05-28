import pandas as pd
import numpy as np
import os
import tempfile
import yt_dlp
from analyze_song import analyze_song

REFERENCE_CSV = "reference_dataset.csv"

# -----------------------------
# 1. Calcular perfil técnico ideal
# -----------------------------
def load_reference_stats():
    df = pd.read_csv(REFERENCE_CSV)
    stats = {}
    for col in df.columns:
        if col != "url":
            stats[col] = {
                "mean": df[col].mean(),
                "std": df[col].std()
            }
    return stats

# -----------------------------
# 2. Descargar canción de YouTube como .mp3
# -----------------------------
def download_audio_mp3(url, out_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id")
        output_path = os.path.join(out_dir, f"{video_id}.mp3")
    return output_path

# -----------------------------
# 3. Calcular rating técnico 1–5
# -----------------------------
def compute_rating(features, stats):
    z_scores = []
    for metric, value in features.items():
        if metric not in stats:
            continue
        mean = stats[metric]["mean"]
        std = stats[metric]["std"]
        if std == 0:
            continue  # ignorar métricas con varianza cero
        z = abs(value - mean) / std
        z_scores.append(z)

    avg_z = np.mean(z_scores) if z_scores else 0
    # Convertir z-score inverso a rating (cuanto más cercano a 0, mejor)
    rating = max(1, 5 - avg_z)
    return round(rating, 2)

# -----------------------------
# 4. Flujo principal
# -----------------------------
def rate_song_from_file(filepath):
    stats = load_reference_stats()
    features = analyze_song(filepath)
    rating = compute_rating(features, stats)

    print("🎧 Características técnicas:")
    for k, v in features.items():
        print(f"- {k}: {v}")
    print(f"\n🧠 Rating técnico: {rating} / 5")

def rate_song_from_youtube(url):
    with tempfile.TemporaryDirectory() as tmpdir:
        mp3_path = download_audio_mp3(url, tmpdir)
        rate_song_from_file(mp3_path)

# -----------------------------
# 5. CLI
# -----------------------------
if __name__ == "__main__":
    print("📥 Introduce la ruta de un MP3 o una URL de YouTube:")
    user_input = input("> ").strip()
    if user_input.startswith("http"):
        rate_song_from_youtube(user_input)
    else:
        if not os.path.exists(user_input):
            print("❌ Archivo no encontrado.")
        else:
            rate_song_from_file(user_input)
