# TTS/STT

Optional. Speech-to-text (WhisperX) and text-to-speech (Coqui TTS) in one service. The Unity client uses it to let
users talk to [VR agents](vr_agent.md) and to speak their answers.

Source: `tts-stt/` · Python, Flask

| Direction | Model | Language |
|---|---|---|
| Speech to text | WhisperX `large-v2` | German |
| Text to speech | Coqui `tts_models/de/thorsten/tacotron2-DDC` | German |

GPU-accelerated when a CUDA GPU is available (the image is based on CUDA 12.1); falls back to CPU, where both
directions are much slower.

## Endpoints

All `POST`, JSON bodies.

| Endpoint | Body | Returns |
|---|---|---|
| `/load` | - | Loads the WhisperX model |
| `/unload` | - | Releases the WhisperX model |
| `/whisperx` | `{"audioBase64": "<WAV, base64>"}` | `{"status", "transcription"}` (HTTP 202) |
| `/tts` | `{"prompt": "<text>"}` | `{"status", "base64Audio"}`: WAV, 16-bit PCM, 22050 Hz (HTTP 202) |

Errors return `{"status": "error", "error": "..."}` with HTTP 412 (or 415 for a non-JSON body). `/whisperx` loads the
model itself if needed, so `/load` only avoids the delay on the first request.

!!! note "`/load` and `/unload` exist to share a GPU"
    As with [speech2text](speech.md#speech2text), unload the STT model when idle on a shared GPU host. The TTS model
    is loaded at start-up and stays in memory.

!!! warning "No authentication"
    The endpoints are not authenticated. Don't expose the service beyond the network the clients run in.

## Running

```bash
cd tts-stt
docker build -t vasili/tts-stt .
docker run -d --restart unless-stopped --gpus all -p 5012:5012 vasili/tts-stt
```

The service listens on port 5012. The models are downloaded on first start, which takes a while.

## Unity client

Set `speechSynthesis` in the client's endpoints configuration (`VasiliEndpoints`) to this service's URL. It is used by
`ChatAPI` for the [agents](https://texttechnologylab.github.io/Va.Si.Li-Lab/modules/bots/).

!!! info "TTS/STT vs. speech2text"
    [speech2text](speech.md) is the older, Whisper-only service. It serves `/whisper` for the client's
    `MicrophoneListener` (`speech` in the endpoints). TTS/STT is what the agents use.
