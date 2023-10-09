import os
import whisper
import pydub


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
