from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os, tempfile
import pandas as pd
import uuid
from rating_engine import download_audio_mp3, analyze_and_rate, load_reference_stats
import yt_dlp

app = FastAPI()

REFERENCE_CSV = "reference_dataset.csv"
CSV_OUTPUT_DIR = "exports"
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

class PlaylistRequest(BaseModel):
    playlist_url: str

def get_playlist_urls(input_url):
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=False)

        # Si es playlist
        if info.get('_type') == 'playlist' and 'entries' in info:
            return [f"https://www.youtube.com/watch?v={entry['id']}" for entry in info['entries']]

        # Si es canción suelta
        return [info.get('webpage_url', input_url)]

@app.post("/rate_playlist")
def rate_playlist(req: PlaylistRequest):
    try:
        urls = get_playlist_urls(req.playlist_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando la URL: {e}")

    stats = load_reference_stats()
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for url in urls:
            try:
                mp3_path, title = download_audio_mp3(url, tmpdir)
                features, rating, issues = analyze_and_rate(mp3_path, stats)
                results.append({
                    "title": title,
                    "rating": rating,
                    "issues": ", ".join(issues) if issues else "✓ OK",
                    "source": url
                })
            except Exception as e:
                results.append({
                    "title": "ERROR",
                    "rating": 0,
                    "issues": f"ERROR: {e}",
                    "source": url
                })
                continue

    session_id = str(uuid.uuid4())[:8]
    csv_path = os.path.join(CSV_OUTPUT_DIR, f"rating_session_{session_id}.csv")
    pd.DataFrame(results).to_csv(csv_path, index=False)

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
