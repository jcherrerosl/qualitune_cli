import csv
import os
import yt_dlp
import tempfile
import pandas as pd
from analyze_song import analyze_song
import numpy as np

INPUT_CSV = "songs.csv"
OUTPUT_CSV = "reference_dataset.csv"

def download_audio_mp3(url, out_dir):
    ffmpeg_path = os.path.abspath("bin/ffmpeg")

    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id")
        output_path = os.path.join(out_dir, f"{video_id}.mp3")
        title = info.get("title", "Unknown Title")

    if not os.path.isfile(output_path):
        raise FileNotFoundError(f"MP3 file not generated for {url}")

    return output_path, title

def process_csv(input_csv, output_csv):
    output_data = []

    with open(input_csv, newline='') as csvfile:
        reader = list(csv.DictReader(csvfile))
        total = len(reader)

        for i, row in enumerate(reader):
            url = row['url'].strip()
            if not url:
                print(f"Skipping empty URL at row {i + 1}")
                continue
            print(f"Analyzing {i + 1}/{total}...", end=" ", flush=True)

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    mp3_path, title = download_audio_mp3(url, tmpdir)
                    features = analyze_song(mp3_path)

                    row_data = {
                        'title': title,
                        'url': url,
                        'noise_ratio': features.get('noise_ratio', np.nan),
                        'error': features.get('error')
                    }

                    # Frequency bands
                    freq = features.get('frequency_bands') or {}
                    for key in ['sub_bass', 'bass', 'low_mids', 'mids', 'highs', 'air']:
                        row_data[key] = freq.get(key, np.nan)

                    # Dynamics
                    dyn = features.get('dynamics') or {}
                    for key in ['lufs', 'rms', 'crest_factor', 'clipping_ratio']:
                        row_data[key] = dyn.get(key, np.nan)

                    # Tuning
                    tun = features.get('tuning') or {}
                    row_data['pitch'] = tun.get('pitch')
                    row_data['confidence'] = tun.get('confidence', np.nan)

                    output_data.append(row_data)

            except Exception as e:
                print(f"Error processing {url}: {e}")

    df = pd.DataFrame(output_data)
    df.to_csv(output_csv, index=False)
    print(f"Features saved to: {output_csv}")

if __name__ == "__main__":
    process_csv(INPUT_CSV, OUTPUT_CSV)
