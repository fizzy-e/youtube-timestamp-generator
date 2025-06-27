import streamlit as st

import re
import requests
from tqdm import tqdm

import re
import requests
from tqdm import tqdm
from yt_dlp import YoutubeDL
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM # needed for ai

def fetch_transcript(video):
    with YoutubeDL({'skip_download':True, 'quiet':True}) as ydl:
        info = ydl.extract_info(video, download=False)
        # now we have a dictionary with the video's meta data stored in 'info' dictionary, need english transcript

    captions = info.get('automatic_captions',{}).get('en',[])
    # now we have a dictionary with the link to all engilsh transcript formats, still need the format

    transcript = []

    for fmt in captions:
        # going through all the formats, each a dictionary
        if 'json3' in fmt.get('url', ''):
            # looking for string 'json3', the format, in the url key
            response = requests.get(fmt['url'])
            # get the transcript, in json3 format, from the link
            data = response.json()
            # convert the info json into a dictionary

            for event in data.get('events', []):
                # event is a key in a dict, which is list of dicts, that has our relevant info
                start = event.get('tStartMs')
                # start time in milliseconds
                segs = event.get('segs')
                # seg is a key in event, a list of dicts, each containing a word

                if start and segs:
                    # this is needed cause some segs dont' exist
                    text = "".join(seg.get('utf8', '') for seg in segs).strip()
                    # take the word and keep appending it, to make a sentence

                    if text: # this is needed since some text is just a blank
                        m, s = divmod(start // 1000, 60)
                        # getting minutes and seconds
                        timestamp = f"{int(m)}:{int(s):02d}"
                        # turning to string, formatting it
                        transcript.append(f"{timestamp} {text}")
                        # now we have created one line in the timestamps
    
    return transcript, info.get("duration") # need the duration for dynamic chunking

def generate_timestamps(transcript, video_duration):
    UNWANTED_PHRASES = ["[Music]", "[Applause]", "[Laughter]", "[Noise]"]
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "tinyllama"  # Change this to match any model you've pulled (e.g. "gemma:2b"), gemma3:1b

    if not transcript:
        return [], 0

    prompts = []
    timestamps = []
    results = []
    this_chunk = ""

    target_chunks = max(5, min(10, int(video_duration // 360)))
    interval = max(1, len(transcript) // target_chunks)

    for idx, i in enumerate(transcript):
        this_chunk += " " + i.split(' ', 1)[1] if ' ' in i else i

        line = i
        for phrase in UNWANTED_PHRASES:
            line = line.replace(phrase, "")
        line = re.sub(r"[!?.,]{2,}", ".", line)
        line = re.sub(r"[^\x00-\x7F]+", "", line)
        line = line.strip()
        if not line:
            continue

        if idx % interval == 0:
            start = i.split(' ', 1)[0]
            start_parts = start.split(':')
            minutes = int(start_parts[0])
            if minutes >= 60:
                total_seconds = minutes * 60 + int(start_parts[1])
                h, rem = divmod(total_seconds, 3600)
                m, s = divmod(rem, 60)
                start = f"{h}:{m:02d}:{s:02d}"

            prompt = (
                f"One short, catchy YouTube chapter title (max 6 words) for this transcript chunk:\n\n{this_chunk}"
            )
            prompts.append(prompt)
            timestamps.append(start)
            this_chunk = ""

    BATCH_SIZE = 4

    for i in tqdm(range(0, len(prompts), BATCH_SIZE), desc="🧠 AI Generating", unit="batch"):
        batch_prompts = prompts[i:i + BATCH_SIZE]
        batch_timestamps = timestamps[i:i + BATCH_SIZE]
        batch_results = []

        for prompt in batch_prompts:
            try:
                response = requests.post(
                    OLLAMA_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    title = response.json().get("response", "").strip().title()
                else:
                    title = "Untitled"
            except Exception as e:
                title = "Error"

            batch_results.append(title)

        results.extend([f"{ts} {title}" for ts, title in zip(batch_timestamps, batch_results)])

    return results


st.set_page_config(page_title="YouTube Chapter Generator", layout="centered")

st.title("📽️ YouTube Timestamp Generator")
st.markdown("Generate automatic chapter titles for YouTube videos using AI (tinyllama).")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Generate Chapters") or video_url:
    if video_url:
        transcript = duration = None  # define defaults to avoid scope issues

        with st.spinner("Fetching transcript..."):
            transcript, duration = fetch_transcript(video_url)

        if not transcript or not duration:
            st.error("Could not extract transcript. Try another video.")
        else:
            with st.spinner("Generating chapter titles..."):
                results = generate_timestamps(transcript, duration)

            st.success("Chapters generated!")
            st.subheader("📌 Chapters:")
            st.code("\n".join(results), language="text")

    else:
        st.warning("Please enter a video URL.")
