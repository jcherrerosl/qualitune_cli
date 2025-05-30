import streamlit as st
import pandas as pd
import tempfile
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs
from rating_engine import load_reference_stats, download_audio_mp3, analyze_and_rate

def sanitize_youtube_url(input_url):
    parsed = urlparse(input_url)
    query = parse_qs(parsed.query)

    if 'list' in query:
        playlist_id = query['list'][0]
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    else:
        return input_url

# --- Configuración de la app ---
st.set_page_config(page_title="Qualitune Demo", layout="centered")
st.title("Qualitune - demo")
st.caption("Análisis técnico automatizado para filtrado editorial")

# --- Input del usuario ---
input_url = st.text_input("Introduce una URL de YouTube (playlist o canción):", "")

if input_url:
    input_url = sanitize_youtube_url(input_url)  # 👈 aplicar limpieza

    with st.spinner("Analizando playlist..."):
        try:
            # --- 🎧 Extraer URLs ---
            ydl_opts = {
                'quiet': True,
                'extract_flat': False,  # ← Necesario para obtener metadatos completos
                'noplaylist': False,    # ← Asegura que procesa toda la playlist
            }

            urls = []
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(input_url, download=False)

                if '_type' in info and info['_type'] == 'playlist':
                    st.success(f"Playlist detectada: {info.get('title', 'Sin título')} ({len(info['entries'])} pistas)")
                    for entry in info['entries']:
                        urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
                else:
                    st.success("Canción individual detectada")
                    urls.append(info['webpage_url'])

            # --- 📊 Cargar stats de referencia ---
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
                        st.warning(f"⚠️ Saltando: {url}\nMotivo: {str(e)}")
                        results.append({
                            "title": "ERROR",
                            "rating": 0,
                            "issues": str(e),
                            "url": url
                        })

            # --- 🧾 Mostrar resultados ---
            df = pd.DataFrame(results)
            st.subheader("📊 Resultados")
            st.dataframe(df[["title", "rating", "issues"]], use_container_width=True)

            # --- 📥 Botón para descargar CSV ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar resultados en CSV",
                data=csv,
                file_name="results.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error al analizar: {e}")
