import os
import tempfile
from rating_engine import load_reference_stats, download_audio_mp3, analyze_and_rate
import pandas as pd
from yt_dlp import YoutubeDL

def get_urls_from_youtube(input_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    urls = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=False)

        if '_type' in info and info['_type'] == 'playlist':
            print(f"\n🎧 Playlist detectada: '{info.get('title', 'Sin título')}' ({len(info['entries'])} pistas)")
            for entry in info['entries']:
                urls.append(entry['url'] if 'url' in entry else f"https://www.youtube.com/watch?v={entry['id']}")
        else:
            print("\n🎵 Canción individual detectada")
            urls.append(info['webpage_url'])

    return urls

if __name__ == "__main__":
    input_url = input("🔗 Introduce una URL de YouTube (playlist o canción): ").strip()
    urls = get_urls_from_youtube(input_url)
    stats = load_reference_stats()

    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, url in enumerate(urls):
            print(f"🔄 ({i+1}/{len(urls)}) Analizando {url}")
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
                print(f"❌ Error con {url}: {e}")
                results.append({
                    "title": "ERROR",
                    "rating": 0,
                    "issues": str(e),
                    "url": url
                })

    df = pd.DataFrame(results)
    df.to_csv("results.csv", index=False)
    print("\n✅ Resultados guardados en 'results.csv'")
    print(df[["title", "rating", "issues"]])
