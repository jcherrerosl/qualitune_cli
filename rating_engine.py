import pandas as pd
import numpy as np
import os
import sys
import tempfile
import yt_dlp
from analyze_song import analyze_song

REFERENCE_CSV = "reference_dataset.csv"
RATED_LOG_CSV = "rated_songs.csv"
Z_THRESHOLD = 1.5  # Consideramos “desviación” a partir de z > 1.5

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
        title = info.get("title", "Unknown")
        output_path = os.path.join(out_dir, f"{video_id}.mp3")
    return output_path, title

def compute_rating_and_issues(features, stats):
    z_scores = {}
    for metric, value in features.items():
        if metric not in stats:
            continue
        mean = stats[metric]["mean"]
        std = stats[metric]["std"]
        if std == 0:
            continue
        z = abs(value - mean) / std
        z_scores[metric] = z

    avg_z = np.mean(list(z_scores.values())) if z_scores else 0
    rating = max(1, 5 - avg_z)
    issues = [k for k, z in z_scores.items() if z > Z_THRESHOLD]

    return round(rating, 2), issues

def append_to_log(title, rating, issues, source):
    row = {
        "title": title,
        "rating": rating,
        "issues": ", ".join(issues) if issues else "✓ OK",
        "source": source
    }

    df = pd.DataFrame([row])
    if os.path.exists(RATED_LOG_CSV):
        df.to_csv(RATED_LOG_CSV, mode='a', header=False, index=False)
    else:
        df.to_csv(RATED_LOG_CSV, index=False)

def rate_song_from_file(filepath):
    stats = load_reference_stats()
    features = analyze_song(filepath)
    rating, issues = compute_rating_and_issues(features, stats)

    print("🎧 Características técnicas:")
    for k, v in features.items():
        print(f"- {k}: {v}")
    print(f"\n🧠 Rating técnico: {rating} / 5")
    print(f"🧪 Desviaciones: {', '.join(issues) if issues else '✓ Ninguna'}")

    append_to_log(os.path.basename(filepath), rating, issues, filepath)

def rate_song_from_youtube(url):
    with tempfile.TemporaryDirectory() as tmpdir:
        mp3_path, title = download_audio_mp3(url, tmpdir)
        stats = load_reference_stats()
        features = analyze_song(mp3_path)
        rating, issues = compute_rating_and_issues(features, stats)

        print("🎧 Características técnicas:")
        for k, v in features.items():
            print(f"- {k}: {v}")
        print(f"\n🧠 Rating técnico: {rating} / 5")
        print(f"🧪 Desviaciones: {', '.join(issues) if issues else '✓ Ninguna'}")

        append_to_log(title, rating, issues, url)

def get_playlist_urls(playlist_url):
    ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if 'entries' in info:
            return [entry['url'] for entry in info['entries']]
        else:
            return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📥 Introduce una URL de YouTube (video o playlist) o ruta a un MP3:")
        user_input = input("> ").strip()
    else:
        user_input = sys.argv[1].strip()

    if "playlist" in user_input or "list=" in user_input:
        print("📃 Detectada playlist, extrayendo canciones...")
        urls = get_playlist_urls(user_input)
        print(f"🎶 {len(urls)} canciones encontradas.")
        for idx, url in enumerate(urls, 1):
            print(f"\n🔄 ({idx}/{len(urls)}) Analizando {url}")
            try:
                rate_song_from_youtube(url)
            except Exception as e:
                print(f"❌ Error con {url}: {e}")
    elif user_input.startswith("http"):
        rate_song_from_youtube(user_input)
    else:
        if not os.path.exists(user_input):
            print("❌ Archivo no encontrado.")
        else:
            rate_song_from_file(user_input)
