import os
import datetime
import argparse
from dotenv import load_dotenv

from .transcriber import Transcriber
from .summarizer import Summarizer

def convert_to_wav(audio_path):
    """Convert audio file to WAV format if needed"""
    # If already a WAV file, return the path
    if audio_path.lower().endswith('.wav'):
        return audio_path
    
    # Implementation for converting to WAV would go here
    # For now, this is a placeholder
    print(f"Converting {audio_path} to WAV format")
    return audio_path

def send_to_slack(summary, channel_id=None):
    """
    Send summary to Slack channel
    
    Args:
        summary: Summary text to send
        channel_id: ID of the Slack channel to send to
    """
    import os
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    channel = channel_id or os.getenv("SLACK_CHANNEL_ID")
    
    if not slack_token:
        print("SLACK_BOT_TOKEN not found in environment variables. Skipping Slack notification.")
        return False
        
    if not channel:
        print("SLACK_CHANNEL_ID not found in environment variables. Skipping Slack notification.")
        return False
    
    try:
        client = WebClient(token=slack_token)
        
        client.chat_postMessage(
            channel=channel,
            text="Standup Meeting Summary",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Standup Meeting Summary"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary
                    }
                }
            ]
        )
        print(f"Message successfully sent to Slack channel {channel}")
        return True
        
    except SlackApiError as e:
        print(f"Error sending message to Slack: {e.response['error']}")
        return False
    except Exception as e:
        print(f"Unexpected error sending to Slack: {e}")
        return False

def transcribe_summarize_api(audio_file_path):
    """
    API-compatible version of the transcribe_summarize function that accepts a file path
    directly instead of using command line arguments.
    
    Args:
        audio_file_path: Path to the audio file to process
    
    Returns:
        dict: Results dictionary containing paths to transcript and summary files
    """
    load_dotenv()
    
    transcriber = Transcriber()
    summarizer = Summarizer()
    
    if not audio_file_path or not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}")
        return {"error": "Audio file not found"}
    
    audio_file_path = convert_to_wav(audio_file_path)
    
    session_dir = os.path.dirname(audio_file_path)
    base_filename = os.path.splitext(os.path.basename(audio_file_path))[0]

    transcript_path = os.path.join(session_dir, f"{base_filename}_transcript.txt")
    result = transcriber.transcribe_file(audio_file_path, output_file=transcript_path)
    transcript_text = result["text"]
    
    # print("\nTranscription:")
    # print("-" * 50)
    # print(transcript_text)
    # print("-" * 50)
    
    summary_path = os.path.join(session_dir, f"{base_filename}_summary.md")
    summary = summarizer.summarize(transcript_text, output_file=summary_path)
    
    # print("\nSummary:")
    # print("-" * 50)
    # print(summary)
    # print("-" * 50)
    
    slack_channel = os.getenv("SLACK_CHANNEL_ID")
    slack_success = send_to_slack(summary, slack_channel)
    
    status_message = "Summary has been sent to Slack!" if slack_success else "Failed to send summary to Slack. Check logs for details."
    
    print(f"\nAll files saved to: {session_dir}")
    print("\nProcess completed successfully!")
    print(status_message)
    
    return {
        "transcript_path": transcript_path,
        "summary_path": summary_path,
        "transcript_text": transcript_text,
        "summary": summary,
        "slack_notification_sent": slack_success
    }
    
    
# Keep the original function for command-line usage
def transcribe_summarize():
    """Main function to run the standup summarizer from command line"""
    load_dotenv()

    parser = argparse.ArgumentParser(description="Standup Meeting Summarizer")
    parser.add_argument("--audio_file", type=str, help="Path to an existing audio file to process")
    parser.add_argument("--record", action="store_true", help="Record audio instead of using existing file")
    parser.add_argument("--duration", type=int, default=300, help="Recording duration in seconds (default: 300)")
    
    args = parser.parse_args()
    
    audio_file_path = None
    session_dir = None
    
    if args.record:
        print("Recording mode activated")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"standup_{timestamp}"

        base_output_dir = os.getenv("OUTPUT_DIRECTORY", "/app/output")
        session_dir = os.path.join(base_output_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        print(f"Session ID: {session_id}")
        print(f"Output directory: {session_dir}")

    
    elif args.audio_file:
        audio_file_path = convert_to_wav(args.audio_file)  # Convert if necessary
        if not audio_file_path or not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found or conversion failed at {audio_file_path}")
            return
        
        session_dir = os.path.dirname(audio_file_path)

    else:
        print("Error: Please specify either --record to record audio or --audio_file to use an existing file")
        return
    
    # Call the API version to avoid code duplication
    return transcribe_summarize_api(audio_file_path)

if __name__ == "__main__":
    transcribe_summarize()