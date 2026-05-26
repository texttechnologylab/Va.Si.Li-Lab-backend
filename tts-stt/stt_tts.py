import shutil
import sys
import traceback
import base64
from pydub import AudioSegment
import io

import torch

_original_torch_load = torch.load

def torch_load_unsafe(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)

torch.load = torch_load_unsafe


print("torch.load patched:", torch.load is torch_load_unsafe)


from flask import Flask, request, jsonify
import whisperx
from TTS.api import TTS
import soundfile as sf

device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if torch.cuda.is_available() else "int8"

app = Flask(__name__)

whisper = None
tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False).to(device)


@app.post("/unload")
def unload():
    global whisper
    if whisper is not None:
        del whisper
        whisper = None
    return {"result": "success"}, 200


@app.post("/load")
def load():
    global whisper
    if whisper is None:
        whisper = whisperx.load_model("large-v2", device, compute_type=compute_type, language="de")

    return {"result": "success"}, 200


@app.post("/whisperx")
def speech_to_text():
    if request.is_json:

        data_request = request.get_json()

        try:
            load()

            audioBase64 = data_request["audioBase64"]

            try:
                with open("tempAudio", "wb") as f:
                    f.write(base64.b64decode(audioBase64))
            except Exception as e:
                print(str(e))

            print("Convert audio to text")
            audio = whisperx.load_audio("tempAudio")
            result = whisper.transcribe(audio, batch_size=16)

            transcription = ""

            for segment in result["segments"]:

                text = segment.get("text").strip()

                if transcription:
                    transcription = transcription + " " + text
                else:
                    transcription = text

            print("Done")
            print(transcription)

            return {
                "status": "success",
                "transcription": transcription
            }, 202
        except Exception as ex:
            print("WHISPERX ERROR: ", repr(ex))
            traceback.print_exc()
            return {
                "status": "error",
                "error": f"{ex}"
            }, 412
    return {
        "status": "error",
        "error": "Request must be JSON"
    }, 415


@app.post("/tts")
def text_to_speech():
    if not request.is_json:
        return jsonify({
            "status": "error",
            "error": "Request must be JSON"
        }), 415

    try:
        data_request = request.get_json()
        print(data_request)
        
        prompt = data_request["prompt"]

        global tts

        wav = tts.tts(text=prompt)

        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, wav, samplerate=22050, format="WAV", subtype="PCM_16")
        wav_buffer.seek(0)

        sound = AudioSegment.from_file(wav_buffer, format="wav")
        sound = sound.set_sample_width(2)

        pcm16_buffer = io.BytesIO()
        sound.export(pcm16_buffer, format="wav")
        pcm16_buffer.seek(0)

        audio_base64 = base64.b64encode(pcm16_buffer.read()).decode("utf-8")

        print("Done")

        return jsonify({
            "status": "success",
            "error": "none",
            "base64Audio": audio_base64
        }), 202

    except Exception as ex:
        return jsonify({
            "status": "error",
            "error": str(ex)
        }), 412


if __name__ == '__main__':
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found in PATH. Install it and add it to PATH.")
    app.run(threaded=True, host="0.0.0.0", port=5012)