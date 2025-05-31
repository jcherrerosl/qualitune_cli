import csv
import os
import yt_dlp
import tempfile
import pandas as pd
from analyze_song import analyze_song

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

    if not os.path.isfile(output_path):
        raise FileNotFoundError(f"MP3 file not generated for {url}")

    return output_path


def process_csv(input_csv, output_csv):
    output_data = []

    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            url = row['url']

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    mp3_path = download_audio_mp3(url, tmpdir)
                    features = analyze_song(mp3_path)
                    features['url'] = url
                    output_data.append(features)
            except Exception as e:
                print(f"Error processing {url}: {e}")

    df = pd.DataFrame(output_data)

    if os.path.exists(output_csv):
        df.to_csv(output_csv, mode='a', header=False, index=False)
    else:
        df.to_csv(output_csv, index=False)

    print(f"Features added to: {output_csv}")


if __name__ == "__main__":
    process_csv(INPUT_CSV, OUTPUT_CSV)
