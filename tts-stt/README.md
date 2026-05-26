

# STT/TTS Backend API

Flask-based backend service providing Speech-to-Text (STT) and Text-to-Speech (TTS) functionality.

## Installation

Use the provided Dockerfile to deploy this backend service.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/load` | Initialize STT model (`whisperx large-v2`) |
| `POST` | `/unload` | Release STT model from memory. |
| `POST` | `/whisperx` | Convert audio to text. Accepts Base64-encoded WAV in JSON body. |
| `POST` | `/tts` | Generate speech from text. Accepts prompt in JSON body. |

## Notes
- Default language: German (DE)
- Audio format: WAV, 16-bit PCM, 22050 Hz
- GPU accelerated when available
- Service runs on `0.0.0.0:5012` by default