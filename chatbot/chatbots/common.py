import numpy as np
import pydub
import base64
import os
import whisper
from gtts import gTTS

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
    
class TextToSpeech:
    def __init__(self, slow: False):
        self.slow = slow
        self.counter = 0

    def text_audio(self, text, language):
        filename = f"response{self.counter}"
        # Increment counter since this can run in parallel
        self.counter += 1
        myobj = gTTS(text=text, lang=language)
        myobj.save(f"{filename}.mp3")
        sound = pydub.AudioSegment.from_mp3(f"{filename}.mp3")
        # Set the frame_rate/sample_rate to 16000 since that's the value we used for all audio transmitions so far
        sound = sound.set_frame_rate(16000)
        sound.export(f"{filename}.wav", format="wav")
        buffer_reader = open(f'{filename}.wav', 'rb')
        if os.path.exists(f"{filename}.wav"):
            os.remove(f"{filename}.wav")
        if os.path.exists(f"{filename}.mp3"):
            os.remove(f"{filename}.mp3")
        buffer_reader.seek(0)
        buffer_reader.read(44)
        byte_array = buffer_reader.read()
        byte_string = base64.b64encode(byte_array).decode('ascii')
        self.counter += 1
        return byte_string