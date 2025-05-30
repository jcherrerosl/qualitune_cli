
import streamlit as st
import tempfile
import os
import pandas as pd
import numpy as np
from analyze_song import analyze_song
import yt_dlp

REFERENCE_CSV = "reference_dataset.csv"
Z_THRESHOLD = 1.5

def load_reference_stats():
    df = pd.read_csv(REFERENCE_CSV)
    stats = {}
    for col in df.columns:
        if col != "url":
            stats[col] = {"mean": df[col].mean(), "std": df[col].std()}
    return stats

def compute_rating_and_issues(features, stats):
    z_scores = {k: abs(v - stats[k]["mean"]) / stats[k]["std"]
                for k, v in features.items() if k in stats and stats[k]["std"] != 0}
    avg_z = np.mean(list(z_scores.values())) if z_scores else 0
    rating = max(1, 5 - avg_z)
    issues = [k for k, z in z_scores.items() if z > Z_THRESHOLD]
    return round(rating, 2), issues

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

st.set_page_config(page_title="Qualitune", layout="centered")

st.title("Qualitune")
st.markdown("Análisis técnico automático de calidad sonora para filtrado editorial.")

option = st.radio("¿Qué quieres analizar?", ["Canción de YouTube", "Archivo local"])

if option == "Canción de YouTube":
    url = st.text_input("Pega aquí el enlace de YouTube")
    if st.button("Analizar"):
        with tempfile.TemporaryDirectory() as tmpdir:
            with st.spinner("Descargando y analizando..."):
                try:
                    mp3_path, title = download_audio_mp3(url, tmpdir)
                    stats = load_reference_stats()
                    features = analyze_song(mp3_path)
                    rating, issues = compute_rating_and_issues(features, stats)

                    st.success(f"✅ {title}")
                    st.metric("Rating técnico", f"{rating} / 5")
                    st.write("### Problemas detectados:")
                    st.write(issues if issues else "✓ Ninguno")
                    st.write("### Detalles del análisis:")
                    st.json(features)

                except Exception as e:
                    st.error(f"❌ Error al analizar: {e}")

elif option == "Archivo local":
    uploaded_file = st.file_uploader("Sube un archivo MP3", type="mp3")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile.write(uploaded_file.read())
            tmpfile_path = tmpfile.name

        if st.button("Analizar"):
            with st.spinner("Analizando archivo..."):
                try:
                    stats = load_reference_stats()
                    features = analyze_song(tmpfile_path)
                    rating, issues = compute_rating_and_issues(features, stats)

                    st.success(f"✅ {uploaded_file.name}")
                    st.metric("Rating técnico", f"{rating} / 5")
                    st.write("### Problemas detectados:")
                    st.write(issues if issues else "✓ Ninguno")
                    st.write("### Detalles del análisis:")
                    st.json(features)
                except Exception as e:
                    st.error(f"❌ Error al analizar: {e}")
