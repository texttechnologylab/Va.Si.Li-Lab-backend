import os

from gtts import gTTS
import base64
import pydub
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


if __name__ == '__main__':
    text_speech = TextToSpeech(False)
    text_speech.text_audio("Hallo, wie geht es dir?", "de")