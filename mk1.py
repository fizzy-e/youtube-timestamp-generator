import re
import requests
import torch
from yt_dlp import YoutubeDL
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# === Get transcript with timestamps ===
def fetch_transcript(url):
    with YoutubeDL({'skip_download': True, 'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
    captions = info.get('automatic_captions', {}).get('en', [])
    duration = info.get('duration', 0)  # in seconds
    for fmt in captions:
        if 'json3' in fmt.get('url', ''):
            resp = requests.get(fmt['url'])
            data = resp.json()
            transcript = []
            for event in data.get('events', []):
                t_ms = event.get('tStartMs')
                segs = event.get('segs')
                if t_ms and segs:
                    text = "".join(seg.get('utf8', '') for seg in segs).strip()
                    if text:
                        m, s = divmod(int(t_ms // 1000), 60)
                        timestamp = f"{m}:{s:02d}"
                        transcript.append(f"{timestamp} {text}")
            return transcript, duration
    raise RuntimeError("No usable English auto-captions found.")

# === Merge chunk lines into one paragraph per chunk ===
def merge_chunk_lines(chunk_lines):
    if not chunk_lines:
        return ""
    current_paragraph = ""
    base_timestamp = ""
    for line in chunk_lines:
        match = re.match(r"^(\d{1,2}:\d{2}) (.+)", line)
        if match:
            timestamp, text = match.groups()
            if not base_timestamp:
                base_timestamp = timestamp
            current_paragraph += text + " "
    return f"{base_timestamp} {current_paragraph.strip()}"

# === Generate chapter title from chunk ===
def generate_chapters_chunk(merged_chunk, tokenizer, model, retries=2):
    timestamp = merged_chunk.split(' ', 1)[0]
    paragraph = merged_chunk[len(timestamp):].strip()
    
    prompt = (
        "Below is an excerpt from a YouTube video transcript.\n"
        "Please generate a short, engaging chapter title that summarizes the main idea of the excerpt. "
        "Return only the title.\n\nTranscript:\n"
        f"{paragraph}\n\nTitle:"
    )

    device = model.device
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=768).to(device)

    for _ in range(retries):
        outputs = model.generate(
            **inputs,
            max_new_tokens=30,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            do_sample=True
        )
        result = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        if len(result.split()) >= 2:
            return f"{timestamp} {result}"

    return f"{timestamp} {paragraph[:40]}..."  # fallback

# === Generate chapters for full transcript ===
def generate_chapters(transcript_lines, duration_secs):
    model_id = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # === Decide number of chunks linearly based on duration (scale to 5–10 chapters) ===
    min_chunks = 5
    max_chunks = 10
    max_duration = 3600  # scale up to 1 hour
    target_chunks = round(min_chunks + (max_chunks - min_chunks) * min(duration_secs, max_duration) / max_duration)

    # === Estimate total word count of transcript ===
    all_text = " ".join(line.split(' ', 1)[-1] for line in transcript_lines)
    words = all_text.split()
    words_per_chunk = max(40, len(words) // target_chunks)

    # === Divide transcript lines into chunks by word count ===
    chunks = []
    current_chunk = []
    word_count = 0
    for line in transcript_lines:
        wc = len(line.split())
        current_chunk.append(line)
        word_count += wc
        if word_count >= words_per_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            word_count = 0
    if current_chunk:
        chunks.append(current_chunk)

    # === Generate chapter titles ===
    all_chapters = []
    for chunk in chunks:
        merged = merge_chunk_lines(chunk)
        result = generate_chapters_chunk(merged, tokenizer, model)
        all_chapters.append(result)

    return "\n".join(all_chapters)

# === Main ===
if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=CmrjSe01LMA" # input("Paste YouTube video URL: ").strip()
    try:
        transcript, duration = fetch_transcript(video_url)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

    chapters = generate_chapters(transcript, duration)
    print(chapters)
