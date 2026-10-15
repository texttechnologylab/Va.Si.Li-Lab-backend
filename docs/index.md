# Va.Si.Li-Lab Backend

Monorepo for the backend services used by
[Va.Si.Li-Lab](https://github.com/texttechnologylab/Va.Si.Li-Lab).

The modules are independent. A minimal deployment needs only two of them - the
Database API and the Ubiq server. Everything else is optional and exists to
support particular scenarios.

## Modules

<div class="grid cards" markdown>

-   :material-database: **[Database API](database_api.md)** - *required*

    Scene, level and role definitions, plus the logging endpoints that every
    tracking sample and event is written through. Backed by MongoDB.

-   :material-lan-connect: **[Ubiq Server](ubiq_server.md)** - *required*

    Room and session server. Keeps avatars, transforms and object ownership in
    sync between connected clients.

-   :material-robot: **[Chatbot](services/chatbot.md)** - *optional*

    Host process that dynamically loads chatbot clients over a socket connection
    and exposes them as a single queryable endpoint.

-   :material-microphone-message: **[Speech](services/speech.md)** - *optional*

    Speech-to-text based on Whisper.

-   :material-account-voice: **[VR Agent](services/vr_agent.md)** - *optional*

    LLM-backed conversational agents that answer users and call tools in the
    VR scene.

-   :material-waveform: **[TTS/STT](services/tts_stt.md)** - *optional*

    WhisperX speech-to-text and text-to-speech in one service, used by the VR
    agents.

</div>

## Which services do I need?

| Scenario | Required | Optional |
|---|---|---|
| Any Va.Si.Li-Lab deployment | Database API, Ubiq | - |
| Recording an experiment | Database API, Ubiq | - |
| Scenarios with a chatbot | Database API, Ubiq | Chatbot |
| Voice-driven interaction | Database API, Ubiq | Speech |
| Talking to LLM agents | Database API, Ubiq | VR Agent, TTS/STT |

!!! info "InterView deploys a subset of these"
    The [InterView](https://texttechnologylab.github.io/InterView/) platform runs
    the Database API and the Ubiq server from this repository, alongside a Janus
    WebRTC gateway and a web client. Its
    [setup guide](https://texttechnologylab.github.io/InterView/setup/) covers
    deploying them together with Docker Compose.

## Repository layout

| Path | Module |
|---|---|
| `database-api/` | [Database API](database_api.md) |
| `Ubiq-server/` | [Ubiq Server](ubiq_server.md) |
| `chatbot/` | [Chatbot host and clients](services/chatbot.md) |
| `speech2text/` | [Whisper speech-to-text](services/speech.md#speech2text) |
| `vr-agent/` | [VR Agent](services/vr_agent.md) |
| `tts-stt/` | [TTS/STT](services/tts_stt.md) |
| `docker-images/` | Shared base images - see [Deployment](deployment.md#base-images) |

## Related documentation

| Site | Covers |
|---|---|
| [Va.Si.Li-Lab](https://texttechnologylab.github.io/Va.Si.Li-Lab/) | The VR client and Unity framework |
| [InterView](https://texttechnologylab.github.io/InterView/) | The VR interview platform and its deployment |
