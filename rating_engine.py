import os
import yt_dlp
import numpy as np
import pandas as pd
from analyze_song import analyze_song

Z_THRESHOLD = 1.5

def load_reference_stats(reference_csv="reference_dataset.csv"):
    df = pd.read_csv(reference_csv)
    stats = {}
    for col in df.columns:
        if col != "url":
            stats[col] = {
                "mean": df[col].mean(),
                "std": df[col].std() if df[col].std() != 0 else 1  # evitar división por 0
            }
    return stats

def download_audio_mp3(url, out_dir):
    ffmpeg_path = os.path.abspath("bin/ffmpeg")

    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': ffmpeg_path,
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
        mp3_path = os.path.join(out_dir, f"{video_id}.mp3")
        if not os.path.exists(mp3_path):
            raise Exception("No se generó el archivo de audio.")
        return mp3_path, title

def analyze_and_rate(mp3_path, stats):
    features = analyze_song(mp3_path)
    z_scores = {}

    for k, v in features.items():
        if k in stats and stats[k]["std"] != 0:
            z_scores[k] = abs(v - stats[k]["mean"]) / stats[k]["std"]

    avg_z = np.mean(list(z_scores.values())) if z_scores else 0
    rating = round(max(1, 5 - avg_z), 2)
    issues = [k for k, z in z_scores.items() if z > Z_THRESHOLD]

    return features, rating, issues
