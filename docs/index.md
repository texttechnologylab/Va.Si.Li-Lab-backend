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

</div>

!!! note "Not every backend module is in this checkout"
    The `main` branch of this repository also has a `vr-agent/` module
    (LLM-backed conversational agents) and a `tts-stt/` module (WhisperX STT +
    TTS). Neither is present here yet - pull them in and extend this site when
    you do.

## Which services do I need?

| Scenario | Required | Optional |
|---|---|---|
| Any Va.Si.Li-Lab deployment | Database API, Ubiq | - |
| Recording an experiment | Database API, Ubiq | - |
| Scenarios with a chatbot | Database API, Ubiq | Chatbot |
| Voice-driven interaction | Database API, Ubiq | Speech |

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
| `docker-images/` | Shared base images - see [Deployment](deployment.md#base-images) |

## Related documentation

| Site | Covers |
|---|---|
| [Va.Si.Li-Lab](https://texttechnologylab.github.io/Va.Si.Li-Lab/) | The VR client and Unity framework |
| [InterView](https://texttechnologylab.github.io/InterView/) | The VR interview platform and its deployment |
