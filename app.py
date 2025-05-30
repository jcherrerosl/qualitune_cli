import streamlit as st
import pandas as pd
import tempfile
from yt_dlp import YoutubeDL
from rating_engine import load_reference_stats, download_audio_mp3, analyze_and_rate

st.set_page_config(page_title="Qualitune Demo", layout="centered")
st.title("🎧 Qualitune Demo")
st.caption("Análisis técnico automatizado para filtrado editorial")

# Input de usuario
input_url = st.text_input("Introduce una URL de YouTube (playlist o canción):", "")

if input_url:
    with st.spinner("Analizando playlist..."):
        try:
            # Extraer URLs
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': True,
            }

            urls = []
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(input_url, download=False)

                if '_type' in info and info['_type'] == 'playlist':
                    st.success(f"Playlist detectada: {info.get('title', 'Sin título')} ({len(info['entries'])} pistas)")
                    for entry in info['entries']:
                        urls.append(entry['url'] if 'url' in entry else f"https://www.youtube.com/watch?v={entry['id']}")
                else:
                    st.success("Canción individual detectada")
                    urls.append(info['webpage_url'])

            # Cargar estadísticas de referencia
            stats = load_reference_stats()
            results = []

            with tempfile.TemporaryDirectory() as tmpdir:
                for i, url in enumerate(urls):
                    st.write(f"🔄 ({i+1}/{len(urls)}) Analizando {url}")
                    try:
                        mp3_path, title = download_audio_mp3(url, tmpdir)
                        features, rating, issues = analyze_and_rate(mp3_path, stats)
                        results.append({
                            "title": title,
                            "rating": rating,
                            "issues": ", ".join(issues),
                            "url": url
                        })
                    except Exception as e:
                        results.append({
                            "title": "ERROR",
                            "rating": 0,
                            "issues": str(e),
                            "url": url
                        })

            # Mostrar resultados
            df = pd.DataFrame(results)
            st.subheader("📊 Resultados")
            st.dataframe(df[["title", "rating", "issues"]], use_container_width=True)

            # Exportar CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar resultados en CSV",
                data=csv,
                file_name="results.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error al analizar: {e}")
