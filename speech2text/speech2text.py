from flask import Flask, request
import numpy as np
from common import RestApiAudioConverter, Whisper2Text
import os

app = Flask(__name__)

whisper_model_identifier = os.environ.get("WHISPER_MODEL", "small")

audio_converter = RestApiAudioConverter(np.int64, 16000, 2, 1)
whisper_model = Whisper2Text(whisper_model_identifier)

@app.post("/unload")
def unload():
    global longform_bot
    if whisper_model is not None:
        del whisper_model
        whisper_model = None

@app.post("/load")
def load():
    global whisper_model
    if whisper_model is None:
        whisper_model = Whisper2Text(whisper_model_identifier)

@app.post("/whisper")
def speech_to_text():
    if request.is_json:
        data_request = request.get_json()
        try:
            load()
            audio_bytes = data_request["audioData"]["base64"]
            audio_seg = audio_converter.convert_bytes_to_audio_segment(audio_bytes)
            print("Convert Audio")
            whisper_text = whisper_model.get_text(audio_seg, True)
            print("Completed")
            return {
                "status": "success",
                "text_in": whisper_text["text"],
                "lang": whisper_text["language"]
            }, 202
        except Exception as ex:
            return {"error": f"{ex}"}, 412
    return {"error": "Request must be JSON"}, 415

if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", port=5000)