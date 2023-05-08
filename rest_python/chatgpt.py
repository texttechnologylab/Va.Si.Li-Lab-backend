# import base64
import openai
# import json
# import numpy as np
# import ConvertAudio
# from whisper2text import Whisper2Text
# from Text2Speech import TextToSpeech
from pydub import AudioSegment

class ChatGpt:
    def __init__(self, api_key: str, model_engine: str = "text-davinci-003"):
        openai.api_key = api_key
        self.model_engine = model_engine

    def get_response(self, question: str):
        completion = openai.Completion.create(
            engine=self.model_engine,
            prompt=question,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return completion.choices[0].text


# class AudioChatGPT:
#     def __init__(self, api_key: str, model_engine: str, whisper_model: str, dtype= np.int64, frame_rate= 16000, sample_width= 2, channels= 1):
#         self.audio_converter = ConvertAudio.RestApiAudioConverter(dtype, frame_rate, sample_width, channels)
#         self.whisper_model = Whisper2Text(whisper_model)
#         self.chatgpt_class = ChatGpt(api_key, model_engine)
#         self.text_2_speech = TextToSpeech(False)
#
#     def ChatGPTResponse(self, audio_bytes):
#         audio_seg = self.audio_converter.convert_bytes_to_audio_segment(audio_bytes)
#         whisper_text = self.whisper_model.get_text(audio_seg, True)
#         response = self.chatgpt_class.get_response(whisper_text["text"])
#         audio_response = self.text_2_speech.text_audio(response, whisper_text["language"])
#         return whisper_text, response, audio_response


if __name__ == '__main__':
    audio = AudioSegment.from_file('test.m4a')
    # with open("data/config_chatgpt.json", "r", encoding="UTF-8") as json_file:
    #     key_chatgpt = json.load(json_file)
    # audioChatGPT = AudioChatGPT(key_chatgpt["key"], "text-davinci-003", "small", np.int64, 16000, 2, 1)
    # text_in, chatgpt_text, back_audio = audioChatGPT.ChatGPTResponse(audio)
    # audio_back = AudioSegment(
    #         base64.b64decode(back_audio),
    #         frame_rate=16000,
    #         sample_width=2,
    #         channels=1
    #     )
    # audio_back.export("response.mp3")
    # chatgpt_text = ChatGpt(key_chatgpt["key"])
    # print(chatgpt_text.get_response("Beschreibe das Thema Informatik mit weniger als 100 Worten"))
