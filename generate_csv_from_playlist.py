from yt_dlp import YoutubeDL
import csv

def extract_urls_from_youtube(input_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    urls = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=False)

        if '_type' in info and info['_type'] == 'playlist':
            print(f"Playlist detected: {info.get('title', 'Untitled')} ({len(info['entries'])} videos)")
            for entry in info['entries']:
                urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
        else:
            print("Single song detected")
            urls.append(info['webpage_url'])

    return urls

def save_urls_to_csv(urls, filename="songs.csv"):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['url'])
        for url in urls:
            writer.writerow([url])
    print(f"CSV saved as {filename}")

if __name__ == "__main__":
    input_url = input("Enter a YouTube URL (playlist or song): ").strip()
    urls = extract_urls_from_youtube(input_url)
    save_urls_to_csv(urls)
