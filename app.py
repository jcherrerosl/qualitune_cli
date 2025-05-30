import streamlit as st
import pandas as pd
import tempfile
import os
import uuid
from rating_engine import get_playlist_urls, download_audio_mp3, load_reference_stats, analyze_and_rate
from analyze_song import analyze_song

REFERENCE_CSV = "reference_dataset.csv"

st.set_page_config(page_title="Qualitune", layout="wide")

st.title("🎧 Qualitune")
st.markdown("""
Análisis técnico automático de calidad sonora para filtrado editorial.  
Introduce una **playlist de YouTube** y obtén un análisis técnico de cada canción.  
""")

playlist_url = st.text_input("🔗 URL de la playlist de YouTube", "")

if playlist_url:
    if st.button("🚀 Analizar Playlist"):
        with st.spinner("Descargando y analizando canciones..."):
            urls = get_playlist_urls(playlist_url)
            stats = load_reference_stats()
            results = []
            tempdir = tempfile.TemporaryDirectory()

            for idx, url in enumerate(urls, 1):
                st.write(f"🔄 ({idx}/{len(urls)}) Analizando: {url}")
                try:
                    mp3_path, title = download_audio_mp3(url, tempdir.name)
                    features = analyze_song(mp3_path)
                    rating, issues = analyze_and_rate(features, stats)
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
                        "issues": str(e),
                        "source": url
                    })

            df = pd.DataFrame(results)
            st.success("✅ Análisis completado")
            st.dataframe(df)

            csv_filename = f"qualitune_results_{uuid.uuid4().hex[:6]}.csv"
            df.to_csv(csv_filename, index=False)
            with open(csv_filename, "rb") as f:
                st.download_button("📥 Descargar CSV", data=f, file_name=csv_filename, mime="text/csv")

            tempdir.cleanup()
            os.remove(csv_filename)
