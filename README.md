# 🎬 YouTube Timestamp Generator

Generate automatic chapter titles for YouTube videos using AI (FLAN-T5 or TinyLLaMA).  
This app helps convert transcript chunks into short, catchy chapter headings that can enhance your YouTube viewer experience or help with content organization.

---

## 🔧 How It Works

- 📥 You paste a YouTube video URL.
- 📝 The app fetches the English **auto-generated transcript** (if available).
- ✂️ It chunks the transcript and feeds each part into a language model.
- 📌 The model returns engaging chapter titles for each timestamp.

---

## 📂 App Versions

- `app.py` → Uses **FLAN-T5-Base** via `transformers` (better accuracy, slower).
- `app2.py` → Uses **TinyLLaMA** via **Ollama API** (lighter, local, faster — but results may vary).

---

## ⚠️ Limitations

- ❌ **Does not work** with videos that:
  - Don’t have auto-captions.
  - Use **translated** captions (e.g., from German to English) — results are usually gibberish.
- 💡 **TinyLLaMA (app2.py)** might return lower-quality titles compared to FLAN-T5 (app.py).

---

## ▶️ Run Locally

### Requirements

Install dependencies:

```bash
pip install -r requirements.txt
