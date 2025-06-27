import argparse
from mk1 import fetch_transcript, generate_timestamps
from colorama import init, Fore, Style

#Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.CYAN, Fore.MAGENTA, Fore.WHITE
#Add Style.BRIGHT, Style.DIM, or Style.NORMAL to control intensity

def main():
    parser = argparse.ArgumentParser(description="Generate YouTube video chapters using AI.")
    parser.add_argument('--url', type=str, required=True, help="YouTube video URL")
    args = parser.parse_args()

    print(Fore.GREEN + "⚠ Fetching transcript...")
    transcript, duration = fetch_transcript(args.url)

    if not transcript or not duration:
        print(Fore.RED + "❌ Failed to fetch transcript or duration.")
        return

    print("✔ Generating chapter titles...")
    results = generate_timestamps(transcript, duration)

    print(Style.RESET_ALL + "\n✔ Chapters:\n")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
    print(Style.RESET_ALL)
