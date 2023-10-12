import numpy as np
import pydub
import base64
import os
import whisper

class RestApiAudioConverter:
    def __init__(self, dtype= np.int64, frame_rate= 16000, sample_width= 2, channels= 1):
        self.dtype = dtype
        self.frame_rate = frame_rate
        self.sample_width = sample_width
        self.channels = channels

    def convert_bytes_to_audio_segment(self, audio_bytes):
        audio_binary = np.frombuffer(base64.b64decode(audio_bytes), dtype=self.dtype)
        audio_segment = pydub.AudioSegment(
            audio_binary.tobytes(),
            frame_rate=16000,
            sample_width=2,
            channels=1
        )
        return audio_segment
    
class Whisper2Text:
    def __init__(self, model_art: str):
        
        print(f"Loading Whisper Model: {model_art}")
        self.model = whisper.load_model(model_art)

    def get_text(self, audio_segment: pydub.AudioSegment, remove_audio_file: bool = False):
        audio_segment.export(f"audio.wav", format="wav")
        result = self.model.transcribe("audio.wav", fp16=False)
        dict_text = {
            "text": result["text"],
            "language": result["language"]
        }
        if remove_audio_file:
            if os.path.exists("audio.wav"):
                 os.remove("audio.wav")
        return dict_text
    