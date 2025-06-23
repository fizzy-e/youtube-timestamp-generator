import argparse
from mk1 import fetch_transcript, generate_timestamps

def main():
    parser = argparse.ArgumentParser(description="Generate YouTube video chapters using AI.")
    parser.add_argument('--url', type=str, required=True, help="YouTube video URL")
    args = parser.parse_args()

    print("📥 Fetching transcript...")
    transcript, duration = fetch_transcript(args.url)

    if not transcript or not duration:
        print("❌ Failed to fetch transcript or duration.")
        return

    print("🤖 Generating chapter titles...")
    results = generate_timestamps(transcript, duration)

    print("\n✅ Chapters:\n")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
