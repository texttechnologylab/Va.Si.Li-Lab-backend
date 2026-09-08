# Va.Si.Li-Lab-backend

Monorepo for the backend modules used by
[Va.Si.Li-Lab](https://github.com/texttechnologylab/Va.Si.Li-Lab).

📖 **[Documentation](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/)**

The modules are independent. A minimal deployment needs only the Database API and
the Ubiq server; everything else is optional.

## Modules

| Module | Purpose | |
|---|---|---|
| [`database-api/`](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/database_api/) | Scene, level and role definitions, plus the logging API that all tracking and event data is written through. Backed by MongoDB. **Scenes can now be created and edited entirely over this API** - see [Scene API](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/database_api/#creating-a-scene). | **required** |
| [`Ubiq-server/`](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/ubiq_server/) | Room and session server - keeps avatars, transforms and ownership in sync. | **required** |
| [`chatbot/`](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/services/chatbot/) | Host process that dynamically loads chatbot clients over a socket and exposes them as one endpoint. | optional |
| [`speech2text/`](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/services/speech/#speech2text) | Speech-to-text based on OpenAI Whisper. | optional |
| [`docker-images/`](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/deployment/#base-images) | Shared base images for the other modules. | - |

## Quick start

A minimal deployment is the Database API, the Ubiq server and a MongoDB instance:

```bash
cd Ubiq-server && docker build -t ubiq . && \
  docker run -d --restart unless-stopped -p 8009:8009 -p 8011:8011 ubiq

cd ../database-api && docker build -t vasili/database-api . && \
  docker run -d --restart unless-stopped -p 5000:5000 \
    -e DB_SERVER=<mongo host> -e DB_USERNAME=<user> -e DB_PASSWORD=<password> \
    -e X_API_KEY=<secret> vasili/database-api
```

> **Set `X_API_KEY` explicitly.** It defaults to the empty string, which accepts
> unauthenticated requests. See
> [Deployment](https://texttechnologylab.github.io/Va.Si.Li-Lab-backend/deployment/#secrets).

For a full VR interview deployment, [InterView](https://github.com/texttechnologylab/InterView)
provides a Docker Compose stack that runs these services together with a Janus
WebRTC gateway, TURN relay and web client.

## Related repositories

| Repository | Contains |
|---|---|
| [Va.Si.Li-Lab](https://github.com/texttechnologylab/Va.Si.Li-Lab) | The VR client and Unity framework |
| [InterView](https://github.com/texttechnologylab/InterView) | VR interview platform and deployment stack |
