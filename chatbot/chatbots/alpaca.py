import numpy as np
from common import RestApiAudioConverter
from models.AlpacaBot import AlpacaBot
from common import Whisper2Text
from common import TextToSpeech
import os
import socketio
import torch
sio = socketio.Client()

audio_converter = RestApiAudioConverter(np.int64, 16000, 2, 1)

whisper_model = None
alpaca_bot = None
text_2_speech = TextToSpeech(False)

chatbot_host = os.environ.get("HOST", "localhost")
chatbot_port = os.environ.get("PORT", 5000)
chatbot_url = f"http://{chatbot_host}:{chatbot_port}/"

port = os.environ.get("PORT", 5001)

alpaca_model = os.environ.get("ALPACA_MODEL", "declare-lab/flan-alpaca-base")

whisper_model = os.environ.get("WHISPER_MODEL", "small")


load_on_start = os.environ.get("LOAD_ON_START", True)


@sio.on("load")
def load(data):
    print("Loading model")
    global whisper_model
    global alpaca_bot
    if whisper_model is None:
        whisper_model = Whisper2Text(whisper_model)
    if alpaca_bot is None:
        alpaca_bot = AlpacaBot(alpaca_model)
    print("Loaded models")
    return {"status": "success"}, 200


@sio.on("unload")
def unload(data):
    print("Unloading model")
    global whisper_model
    global alpaca_bot
    if whisper_model is not None:
        del whisper_model
        whisper_model = None
    if alpaca_bot is not None:
        del alpaca_bot
        alpaca_bot = None
        torch.cuda.empty_cache()
    print("Unloaded models")
    return {"status": "success"}, 200


@sio.on("query")
def chatbot_query(data):
    if isinstance(data, dict):
        data_request = data
        try:
            # Load the model in case it has been unloaded
            load(data)
            audio_bytes = data_request["audioData"]["base64"]
            audio_seg = audio_converter.convert_bytes_to_audio_segment(
                audio_bytes)
            print("Convert Audio")
            whisper_text = whisper_model.get_text(audio_seg, True)
            print("Get Text")
            response = alpaca_bot.get_response(whisper_text["text"])
            print("Text2Speech")
            audio_response = text_2_speech.text_audio(
                response, whisper_text["language"])
            print("Completed")
            return {
                "status": "success",
                "audio": {
                    "base64": audio_response
                },
                "text_in": whisper_text["text"],
                "text_out": response,
                "lang": whisper_text["language"]
            }, 202
        except Exception as ex:
            return {"error": f"{ex}"}, 412
    return {"error": "Request must be JSON-like"}, 415


@sio.on("close")
def close(data):
    sio.disconnect()
    print("Forcibly disconnected")


@sio.on("connect")
def init():
    sio.emit("init", {"name": "alpaca"})


if __name__ == '__main__':
    sio.connect(chatbot_url)
    if load_on_start:
        load({})
    sio.wait()
