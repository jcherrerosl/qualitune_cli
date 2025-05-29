from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, tempfile
import yt_dlp
import pandas as pd
import numpy as np
from analyze_song import analyze_song
from fastapi.responses import FileResponse
from uuid import uuid4

app = FastAPI()

REFERENCE_CSV = "reference_dataset.csv"
Z_THRESHOLD = 1.5
CSV_OUTPUT_DIR = "exports"
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

class PlaylistRequest(BaseModel):
    playlist_url: str

def load_reference_stats():
    df = pd.read_csv(REFERENCE_CSV)
    stats = {}
    for col in df.columns:
        if col != "url":
            stats[col] = {"mean": df[col].mean(), "std": df[col].std()}
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

def compute_rating_and_issues(features, stats):
    z_scores = {k: abs(v - stats[k]["mean"]) / stats[k]["std"]
                for k, v in features.items() if k in stats and stats[k]["std"] != 0}
    avg_z = np.mean(list(z_scores.values())) if z_scores else 0
    rating = max(1, 5 - avg_z)
    issues = [k for k, z in z_scores.items() if z > Z_THRESHOLD]
    return round(rating, 2), issues

@app.post("/rate_playlist")
def rate_playlist(req: PlaylistRequest):
    urls = get_playlist_urls(req.playlist_url)
    stats = load_reference_stats()
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for url in urls:
            try:
                mp3_path, title = download_audio_mp3(url, tmpdir)
                features = analyze_song(mp3_path)
                rating, issues = compute_rating_and_issues(features, stats)
                results.append({
                    "title": title,
                    "rating": rating,
                    "issues": issues,
                    "features": features,
                    "source": url
                })
            except Exception as e:
                results.append({
                    "title": "ERROR",
                    "rating": 0,
                    "issues": [str(e)],
                    "features": {},
                    "source": url
                })

    session_id = str(uuid4())[:8]
    csv_path = os.path.join(CSV_OUTPUT_DIR, f"rating_session_{session_id}.csv")
    df = pd.DataFrame([{
        "title": r["title"],
        "rating": r["rating"],
        "issues": ", ".join(r["issues"]),
        "source": r["source"]
    } for r in results])
    df.to_csv(csv_path, index=False)

    return {
        "session_id": session_id,
        "result_count": len(results),
        "results": results,
        "csv_download_url": f"/csv/{session_id}"
    }

@app.get("/csv/{session_id}")
def download_csv(session_id: str):
    path = os.path.join(CSV_OUTPUT_DIR, f"rating_session_{session_id}.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo CSV no encontrado.")
    return FileResponse(path, media_type="text/csv", filename=f"rating_{session_id}.csv")
