import numpy as np
import pydub
import base64


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
