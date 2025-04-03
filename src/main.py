import os
import argparse
import datetime
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import subprocess

from recorder import Recorder
from transcriber import Transcriber
from summarizer import Summarizer

def convert_to_wav(input_file):
    """Convert MP4/M4A to WAV for processing."""
    output_file = os.path.splitext(input_file)[0] + ".wav"

    ext = os.path.splitext(input_file)[1].lower()

    if ext == ".wav":
        print(f"{input_file} is already a WAV file. No conversion needed.")
        return input_file

    elif ext in [".mp4", ".m4a"]:
        print(f"Converting {input_file} to {output_file}...")
        command = ["ffmpeg", "-i", input_file, "-ac", "1", "-ar", "16000", output_file]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_file

    else:
        print(f"Unsupported file format: {input_file}")
        return None

def send_to_slack(summary, slack_channel):
    """Send the summarized text to a Slack channel."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("Error: SLACK_BOT_TOKEN is missing.")
        return

    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=slack_channel,
            text=f"{summary}"
        )
        print(f"Summary successfully posted to Slack: {response['ts']}")
    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")

def main():
    """Main function to run the standup summarizer"""
    load_dotenv()

    parser = argparse.ArgumentParser(description="Standup Meeting Summarizer")
    parser.add_argument("--audio_file", type=str, help="Path to an existing audio file to process")
    parser.add_argument("--record", action="store_true", help="Record audio from microphone")
    parser.add_argument("--duration", type=float, default=None, help="Duration in seconds to record")
    
    args = parser.parse_args()
    transcriber = Transcriber()
    summarizer = Summarizer()
    
    audio_file_path = None
    session_dir = None
    
    if args.record:
        print("Recording mode activated")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"standup_{timestamp}"

        base_output_dir = os.getenv("OUTPUT_DIRECTORY", "./output")
        session_dir = os.path.join(base_output_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        print(f"Session ID: {session_id}")
        print(f"Output directory: {session_dir}")

        recorder = Recorder()
        _, audio_file_path = recorder.record(duration=args.duration, output_dir=session_dir, filename=f"{session_id}_recording.wav")
    
    elif args.audio_file:
        audio_file_path = convert_to_wav(args.audio_file)  # Convert if necessary
        if not audio_file_path or not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found or conversion failed at {audio_file_path}")
            return
        
        session_dir = os.path.dirname(audio_file_path)

    else:
        print("Error: Please specify either --record to record audio or --audio_file to use an existing file")
        return
    
    base_filename = os.path.splitext(os.path.basename(audio_file_path))[0]

    transcript_path = os.path.join(session_dir, f"{base_filename}_transcript.txt")
    result = transcriber.transcribe_file(audio_file_path, output_file=transcript_path)
    transcript_text = result["text"]
    
    print("\nTranscription:")
    print("-" * 50)
    print(transcript_text)
    print("-" * 50)
    
    summary_path = os.path.join(session_dir, f"{base_filename}_summary.md")
    summary = summarizer.summarize(transcript_text, output_file=summary_path)
    
    print("\nSummary:")
    print("-" * 50)
    print(summary)
    print("-" * 50)
    
    # Send summary to Slack
    slack_channel = os.getenv("SLACK_CHANNEL_ID")
    send_to_slack(summary, slack_channel)
    
    print(f"\nAll files saved to: {session_dir}")
    print("\nProcess completed successfully!")
    print("Summary has been sent to Slack!")


if __name__ == "__main__":
    main()
