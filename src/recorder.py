import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from datetime import datetime
from pathlib import Path


class Recorder:
    """
    Class for recording audio from the microphone
    """
    
    def __init__(self, sample_rate=16000, channels=1):
        """
        Initialize the recorder with the specified parameters.
        
        Args:
            sample_rate (int): The sample rate to record at
            channels (int): The number of audio channels
        """
        self.sample_rate = sample_rate
        self.channels = channels
        
    def record(self, duration=None, output_dir=None, filename=None, save=True):
        """
        Record audio from the microphone.
        
        Args:
            duration (float, optional): Duration in seconds to record. If None, will record until stopped.
            output_dir (str, optional): Directory to save the recording to
            filename (str, optional): Filename for the recording
            save (bool): Whether to save the recording to a file
            
        Returns:
            tuple: (audio_array, file_path or None)
        """
        if duration is None:
            print("Press Ctrl+C to stop recording...")
            
        try:
            if duration is None:
                # For manual stopping, we need a different approach
                print("Recording... Press Ctrl+C to stop.")
                
                # Use a list to collect chunks of audio
                audio_chunks = []
                
                def callback(indata, frames, time, status):
                    if status:
                        print(f"Error: {status}")
                    audio_chunks.append(indata.copy())
                
                # Start the stream
                with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, 
                                callback=callback, dtype='float32'):
                    try:
                        # Wait indefinitely until KeyboardInterrupt
                        import time
                        while True:
                            time.sleep(0.1)
                    except KeyboardInterrupt:
                        print("\nRecording stopped by user")
                
                # Concatenate all audio chunks
                if audio_chunks:
                    audio_data = np.concatenate(audio_chunks, axis=0)
                else:
                    print("No audio recorded")
                    return None, None
            else:
                print(f"Recording for {duration} seconds...")
                # Record for the specified duration
                audio_data = sd.rec(
                    int(duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype='float32'
                )
                
                # Wait for the recording to finish
                sd.wait()
                
            print("Recording finished")
            
            if save:
                # Save the recording to a file
                if output_dir is None:
                    output_dir = os.getenv("OUTPUT_DIRECTORY", "./output")
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"recording_{timestamp}.wav"
                
                file_path = os.path.join(output_dir, filename)
                
                # Convert to int16 for WAV file
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav.write(file_path, self.sample_rate, audio_int16)
                
                print(f"Recording saved to: {file_path}")
                return audio_data, file_path
            else:
                return audio_data, None
                
        except Exception as e:
            print(f"Error during recording: {str(e)}")
            raise