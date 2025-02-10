import yt_dlp
import pandas as pd
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Step 1: Fetch all video URLs and titles from a channel
def get_channel_videos(channel_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True
    }
    video_data = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        if "entries" in info:
            for entry in info["entries"]:
                if "url" in entry and "title" in entry:
                    video_data.append({"title": entry["title"], "url": entry["url"]})
    return video_data

# Step 2: Extract name from first 10 seconds of captions (stopping at "and" & capitalizing words)
def get_video_name(video_url, language='en'):
    try:
        video_id = video_url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        captions_text = []
        for entry in transcript:
            if entry['start'] > 10:  # Stop after 10 seconds
                break
            captions_text.append(entry['text'])
        
        combined_text = " ".join(captions_text)

        # Improved regex: Captures full names and stops at "and"
        match = re.search(r"(?i)(?:my name is|I'm|I am) ([A-Za-z0-9]+(?:\s[A-Za-z0-9]+)*?)(?=\s+(?:And|For|I|On|This|Today)\b|$)", combined_text)        
        if match:
            # Capitalize each word in the name properly
            name = match.group(1)
            return name.title(), video_url  # Converts "john doe" -> "John Doe"
        
        return "Unknown", video_url

    except Exception:
        return "Unknown", video_url

# Step 3: Process all videos and save to CSV
def process_channel_to_csv(channel_url, output_file="names.csv"):
    video_data = get_channel_videos(channel_url)
    results = []

    for video in video_data:
        name, url = get_video_name(video["url"])
        results.append({"Video Title": video["title"], "Video URL": url, "Name": name})
        print(f"Processed: {video['title']} -> {name}")

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"\n✅ Names saved to {output_file}")

# Example Usage
channel_url = "https://www.youtube.com/@MidwestMagicCleaning/videos"
process_channel_to_csv(channel_url, "names.csv")
