import os
import argparse
import datetime
from dotenv import load_dotenv

from recorder import Recorder
from transcriber import Transcriber
from summarizer import Summarizer


def main():
    """Main function to run the standup summarizer"""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Standup Meeting Summarizer")
    parser.add_argument("--audio_file", type=str, help="Path to an existing audio file to process")
    parser.add_argument("--record", action="store_true", help="Record audio from microphone")
    parser.add_argument("--duration", type=float, default=None, help="Duration in seconds to record")
    parser.add_argument("--model", type=str, default=os.getenv("WHISPER_MODEL", "base"), 
                        help="Whisper model to use (tiny, base, small, medium, large)")
    args = parser.parse_args()

    # Create a unique session ID for this run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"standup_{timestamp}"
    
    # Create session directory
    base_output_dir = os.getenv("OUTPUT_DIRECTORY", "./output")
    session_dir = os.path.join(base_output_dir, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    print(f"Session ID: {session_id}")
    print(f"Output directory: {session_dir}")

    # Initialize components
    transcriber = Transcriber(model_name=args.model)
    summarizer = Summarizer()
    
    audio_file_path = None
    
    # Record audio or use existing file
    if args.record:
        print("Recording mode activated")
        recorder = Recorder()
        _, audio_file_path = recorder.record(duration=args.duration, output_dir=session_dir, filename=f"{session_id}_recording.wav")
    elif args.audio_file:
        audio_file_path = args.audio_file
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return
            
        # If using existing file, copy it to the session directory
        if not audio_file_path.startswith(session_dir):
            from shutil import copy2
            filename = os.path.basename(audio_file_path)
            new_path = os.path.join(session_dir, f"{session_id}_recording{os.path.splitext(filename)[1]}")
            copy2(audio_file_path, new_path)
            print(f"Copied audio file to session directory: {new_path}")
            audio_file_path = new_path
    else:
        print("Error: Please specify either --record to record audio or --audio_file to use an existing file")
        return
    
    # Transcribe audio
    transcript_path = os.path.join(session_dir, f"{session_id}_transcript.txt")
    result = transcriber.transcribe_file(audio_file_path, output_file=transcript_path)
    transcript_text = result["text"]
    
    print("\nTranscription:")
    print("-" * 50)
    print(transcript_text)
    print("-" * 50)
    
    # Summarize transcript
    summary_path = os.path.join(session_dir, f"{session_id}_summary.md")
    summary = summarizer.summarize(transcript_text, output_file=summary_path)
    
    print("\nSummary:")
    print("-" * 50)
    print(summary)
    print("-" * 50)
    
    # Create a metadata file with information about the session
    metadata = {
        "session_id": session_id,
        "timestamp": timestamp,
        "audio_file": os.path.basename(audio_file_path),
        "transcript_file": os.path.basename(transcript_path),
        "summary_file": os.path.basename(summary_path),
        "whisper_model": args.model
    }
    
    metadata_path = os.path.join(session_dir, f"{session_id}_metadata.json")
    with open(metadata_path, "w") as f:
        import json
        json.dump(metadata, f, indent=2)
    
    print(f"\nAll files saved to session directory: {session_dir}")
    print("\nProcess completed successfully!")
    print("Next step would be to implement Slack integration to post the summary.")


if __name__ == "__main__":
    main()