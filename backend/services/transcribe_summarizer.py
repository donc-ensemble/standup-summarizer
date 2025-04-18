import os
from db.models.channel import Channel
from db.session import get_db
from db.models.summary import Summary
from .transcriber import Transcriber
from .summarizer import Summarizer


def send_to_slack(summary, channel_id=None):
    """
    Send summary to Slack channel

    Args:
        summary: Summary text to send
        channel_id: ID of the channel in our database (not Slack channel ID)
    """
    import os
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print(
            "SLACK_BOT_TOKEN not found in environment variables. Skipping Slack notification."
        )
        return False

    db = next(get_db())
    try:
        # Get the Slack channel ID from our database
        channel = db.query(Channel).get(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found in database. Skipping Slack notification.")
            return False

        slack_channel_id = channel.channel_id  # This is the actual Slack channel ID
        client = WebClient(token=slack_token)

        client.chat_postMessage(
            channel=slack_channel_id,
            text="Standup Meeting Summary",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Standup Meeting Summary",
                    },
                },
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": summary}},
            ],
        )
        print(f"Message successfully sent to Slack channel {slack_channel_id}")
        return True

    except SlackApiError as e:
        print(f"Error sending message to Slack: {e.response['error']}")
        return False
    except Exception as e:
        print(f"Unexpected error sending to Slack: {e}")
        return False
    finally:
        db.close()

def transcribe_summarize_api(
    audio_file_path: str, 
    channel_id: int, 
    original_filename: str, 
    job_id: str, 
    send_to_slack_bool: bool  # Changed parameter name to be more descriptive
):
    db = next(get_db())
    try:
        channel = db.query(Channel).get(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")

        print(f"Starting processing for {original_filename}...")
        db.query(Summary).filter(Summary.job_id == job_id).update(
            {"status": "processing"}
        )
        db.commit()

        transcriber = Transcriber()
        transcription = transcriber.transcribe_file(audio_file_path)

        summarizer = Summarizer()
        summary_text = summarizer.summarize(transcription["text"])

        # Initialize variables with default values
        slack_success = False
        slack_error = None
        
        # Only try to send to Slack if requested
        if send_to_slack_bool:
            slack_success = send_to_slack(summary_text, channel_id)
            if not slack_success:
                slack_error = "Failed to send to Slack (channel not found or other error)"
            
        db.query(Summary).filter(Summary.job_id == job_id).update(
            {
                "status": "completed",
                "transcript": transcription["text"],
                "summary": summary_text,
                "slack_notification_sent": slack_success,
                "slack_error": slack_error,
            }
        )
        db.commit()
        print(f"✅ Updated database status to 'completed' for job {job_id}")

    except Exception as e:
        db.rollback()
        db.query(Summary).filter(Summary.job_id == job_id).update(
            {"status": "failed", "slack_error": str(e)}
        )
        db.commit()
        raise
    finally:
        db.close()
        temp_dir = os.path.dirname(audio_file_path)
        base_name = os.path.basename(audio_file_path).split("_")[0]
        for filename in os.listdir(temp_dir):
            if filename.startswith(base_name):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete temp file {file_path}: {str(e)}")