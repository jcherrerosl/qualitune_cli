import streamlit as st
import pandas as pd
import tempfile
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs
from rating_engine import load_reference_stats, download_audio_mp3, analyze_and_rate
import os

def sanitize_youtube_url(input_url):
    parsed = urlparse(input_url)
    query = parse_qs(parsed.query)
    if 'list' in query:
        playlist_id = query['list'][0]
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    else:
        return input_url

def fetch_metadata(url):
    last_exc = None
    cookie_path = 'cookies.txt' if os.path.exists('cookies.txt') else None
    for flat in (True, False):
        ydl_opts = {
            'quiet': True,
            'extract_flat': flat,
            'noplaylist': False,
            'skip_download': True,
            'nocheckcertificate': True,
        }
        if cookie_path:
            ydl_opts['cookiefile'] = cookie_path
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return info
        except Exception as exc:
            last_exc = exc
    raise RuntimeError(last_exc or "yt-dlp returned no data")

st.set_page_config(page_title="Qualitune Demo", layout="centered")
st.title("Qualitune - demo")
st.caption("Automated technical analysis for editorial filtering")

input_url = st.text_input("Enter a YouTube URL (playlist or song):", "")

if input_url:
    url = sanitize_youtube_url(input_url)

    with st.spinner("Analyzing…"):
        try:
            info = fetch_metadata(url)

            urls = []
            if info.get('_type') == 'playlist':
                st.success(f"Playlist detected: {info.get('title', 'Untitled')} ({len(info['entries'])} tracks)")
                for entry in info['entries']:
                    if entry and 'id' in entry:
                        urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
            else:
                st.success("Single song detected")
                urls.append(info['webpage_url'])

            stats = load_reference_stats()
            results = []

            with tempfile.TemporaryDirectory() as tmpdir:
                for i, url in enumerate(urls):
                    st.write(f"Analyzing {url} ({i+1}/{len(urls)})")
                    try:
                        mp3_path, title = download_audio_mp3(url, tmpdir)
                        result = analyze_and_rate(mp3_path, stats)
                        results.append({
                            "title": title,
                            "rating": result["rating"],
                            "issues": ", ".join(result["issues"]),
                            "url": url
                        })
                    except Exception as e:
                        st.warning(f"Skipping: {url}\nReason: {str(e)}")
                        results.append({
                            "title": "Cannot analyze",
                            "rating": 0,
                            "issues": "Not playable or extractable",
                            "url": url
                        })

            df = pd.DataFrame(results)
            st.subheader("Results")
            st.dataframe(df[["title", "rating", "issues"]], use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="results.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"Error during analysis: {e}")