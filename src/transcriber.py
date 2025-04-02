import os
import whisper
from pathlib import Path


class Transcriber:
    """
    Class for transcribing audio to text using Whisper
    """
    
    def __init__(self, model_name="base"):
        """
        Initialize the transcriber with the specified Whisper model.
        
        Args:
            model_name (str): The Whisper model to use - tiny, base, small, medium, or large
        """
        self.model_name = model_name
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        print("Model loaded successfully")
        
    def transcribe_file(self, audio_file_path, output_file=None):
        """
        Transcribe an audio file to text.
        
        Args:
            audio_file_path (str): Path to the audio file
            output_file (str, optional): Path to save the transcript
            
        Returns:
            dict: The transcription result containing text and segments
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
        print(f"Transcribing file: {audio_file_path}")
        result = self.model.transcribe(audio_file_path)
        
        # Save the transcript to a file
        if output_file is None:
            output_dir = os.path.dirname(audio_file_path)
            if not output_dir:
                output_dir = os.getenv("OUTPUT_DIRECTORY", "./transcripts")
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
            # Get the base filename without extension
            base_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
            if base_filename.startswith("recording_"):
                base_filename = base_filename[10:]  # Remove "recording_" prefix
                
            transcript_file = os.path.join(output_dir, f"{base_filename}_transcript.txt")
        else:
            transcript_file = output_file
            
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(transcript_file), exist_ok=True)
        
        with open(transcript_file, "w") as f:
            f.write(result["text"])
        
        print(f"Transcript saved to: {transcript_file}")
        return result
    
    def transcribe_audio_array(self, audio_array, sample_rate=16000, output_file=None):
        """
        Transcribe audio from a numpy array.
        
        Args:
            audio_array (numpy.ndarray): Audio data
            sample_rate (int): Sample rate of the audio data
            output_file (str, optional): Path to save the transcript
            
        Returns:
            dict: The transcription result containing text and segments
        """
        print("Transcribing audio array")
        result = self.model.transcribe(audio_array, sr=sample_rate)
        
        # Save the transcript to a file if specified
        if output_file:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, "w") as f:
                f.write(result["text"])
            
            print(f"Transcript saved to: {output_file}")
            
        return result