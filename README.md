# YouTube Timestamp Generator ⏯️

This tool takes a YouTube video and generates **chapter timestamps** with **engaging titles** using an AI model (FLAN-T5). It fetches the video transcript and summarizes it into key chapters automatically.

## 🚀 Features

- 📼 Takes YouTube video URL as input
- ✂️ Dynamically segments transcript based on video duration
- 🧠 Uses FLAN-T5 to generate chapter titles
- 📜 Outputs timestamps + chapter names in human-readable format
- 🔧 Built for local use — no API required

## 📦 Requirements

Install the dependencies:

```
pip install -r requirements.txt
```

## 🧪 Example

Input:

```
https://www.youtube.com/watch?v=EXAMPLE123
```

Output:

```
0:00 The Rescue
0:48 Reuniting With The Seal
1:45 Building Trust
...
```

## 🖥️ Usage (CLI version coming soon)

For now, just run:

```bash
python mk1.py
```

Then manually paste the video URL inside the script. (CLI flags like `--url` coming soon.)

## 📁 Project Structure

```
.
├── mk1.py               # Main script
├── requirements.txt     # Python dependencies
├── README.md            # You're here
└── .gitignore
```
