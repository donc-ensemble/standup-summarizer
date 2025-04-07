import os
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic


class Summarizer:
    """
    Class for summarizing transcribed text using Anthropic's Claude
    """

    def __init__(self, api_key=None):
        """
        Initialize the summarizer with Anthropic API key.

        Args:
            api_key (str, optional): Anthropic API key. If None, it will be read from env variables.
        """
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "Anthropic API key is required. Set it in the .env file or pass it directly."
            )

        self.client = Anthropic(api_key=api_key)

    def summarize(self, transcript_text, output_file=None):
        """
        Summarize a transcript using Anthropic's Claude.

        Args:
            transcript_text (str): The transcript text to summarize
            output_file (str, optional): Path to save the summary

        Returns:
            str: The summarized text
        """
        if not transcript_text or len(transcript_text.strip()) == 0:
            raise ValueError("Transcript text is empty")

        print("Generating summary with Anthropic's Claude")

        prompt = f"""
        You are a helpful assistant that summarizes standup meetings. Below is a transcript of a standup meeting.
        Please provide a concise summary that includes:
        
        1. Key updates from each participant
        2. Any blockers or issues mentioned
        3. Action items or next steps
        4. Decisions made during the meeting
        
        Format the summary in a clear, organized way that would be useful for team members who missed the meeting.
        
        Here is the transcript:
        
        {transcript_text}
        """

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                temperature=0.3,
                system="You are a helpful assistant that specializes in summarizing standup meetings in a concise and actionable format.",
                messages=[{"role": "user", "content": prompt}],
            )

            summary = response.content[0].text

            if output_file is None:
                if os.path.exists(transcript_text):
                    output_dir = os.path.dirname(transcript_text)
                    base_filename = os.path.splitext(os.path.basename(transcript_text))[
                        0
                    ]
                    if base_filename.endswith("_transcript"):
                        base_filename = base_filename[:-10]
                    summary_file = os.path.join(
                        output_dir, f"{base_filename}_summary.md"
                    )
                else:
                    output_dir = os.getenv("OUTPUT_DIRECTORY", "./summaries")
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    summary_file = os.path.join(output_dir, f"summary_{timestamp}.md")
            else:
                summary_file = output_file
            # print(f"Summary saved to: {summary_file}")
            return summary

        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            raise
