from .transcriber import Transcriber
from .summarizer import Summarizer
from db.session import get_db
from db.models.summary import Summary
from .transcribe_summarizer import send_to_slack


class SummaryProcessor:
    def __init__(self):
        self.transcriber = Transcriber()
        self.summarizer = Summarizer()

    async def process_audio(self, audio_file_path: str, channel_id: int):
        """Process audio and store results in database"""
        db = next(get_db())

        transcription = self.transcriber.transcribe_file(audio_file_path)

        summary_text = self.summarizer.summarize(transcription["text"])

        db_summary = Summary(
            channel_id=channel_id,
            audio_file_path=audio_file_path,
            transcript=transcription["text"],
            summary=summary_text,
        )
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)

        slack_sent = send_to_slack(summary_text)

        return {"db_id": db_summary.id, "slack_notification_sent": slack_sent}
