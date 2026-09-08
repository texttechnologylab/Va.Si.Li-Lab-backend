# Speech

Optional. Speech-to-text based on OpenAI Whisper.

!!! note "A newer speech service exists upstream"
    The backend's `main` branch also has a `tts-stt/` module (WhisperX-based STT
    plus TTS in one service) that is not yet present in this checkout. If you
    pull it in, document it alongside this page as a second option.

GPU-accelerated when a GPU is available; falls back to CPU, where transcription
is substantially slower.

## speech2text

Whisper-based transcription.

Source: `speech2text/`

### Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/whisper` | Transcribe audio |
| `POST` | `/load` | Load the model into memory |
| `POST` | `/unload` | Release the model |

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `WHISPER_MODEL` | `small` | Which Whisper model to load - see the [model list](https://github.com/openai/whisper#available-models-and-languages) |

!!! note "`/load` and `/unload` exist to share a GPU"
    The model occupies GPU memory for as long as it is loaded. On a host running
    several services, unload it when idle rather than leaving it resident.

    The trade-off is latency: the first request after an unload pays the full
    load cost. Keep it loaded during an active session.

### Running

```bash
cd speech2text
docker build -t vasili/speech2text .
docker run -d --gpus all -p 5000:5000 -e WHISPER_MODEL=small vasili/speech2text
```
