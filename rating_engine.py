import pandas as pd
import numpy as np
import os
import yt_dlp
from analyze_song import analyze_song

REFERENCE_CSV = "reference_dataset.csv"
Z_THRESHOLD = 1.5

def load_reference_stats():
    df = pd.read_csv(REFERENCE_CSV)
    stats = {}
    for col in df.columns:
        if col not in ["url", "title"]:
            stats[col] = {
                "mean": df[col].mean(),
                "std": df[col].std()
            }
    return stats

def get_playlist_urls(playlist_url):
    ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        return [entry['url'] for entry in info.get('entries', [])]

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
        return os.path.join(out_dir, f"{video_id}.mp3"), title

def analyze_and_rate(features, stats):
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
