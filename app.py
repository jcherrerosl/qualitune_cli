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

st.set_page_config(page_title="Qualitune Demo", layout="centered")
st.title("Qualitune - demo")
st.caption("Automated technical analysis for editorial filtering")

input_url = st.text_input("Enter a YouTube URL (playlist or song):", "")

if input_url:
    input_url = sanitize_youtube_url(input_url)

    with st.spinner("Analyzing playlist..."):
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'noplaylist': False,
                'ignoreerrors': True,
                'skip_download': True,
            }

            urls = []
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(input_url, download=False)

                if '_type' in info and info['_type'] == 'playlist':
                    st.success(f"Playlist detected: {info.get('title', 'Untitled')} ({len(info['entries'])} tracks)")
                    for entry in info['entries']:
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
                        features, rating, issues = analyze_and_rate(mp3_path, stats)
                        results.append({
                            "title": title,
                            "rating": rating,
                            "issues": ", ".join(issues),
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
