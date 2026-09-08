# Deployment

Each module ships its own Dockerfile and can be built and run independently.
There is no single compose file covering the whole monorepo, because a given
deployment normally needs only a subset.

## A minimal deployment

Two services:

```bash
# Ubiq room server
cd Ubiq-server && docker build -t ubiq .
docker run -d --restart unless-stopped -p 8009:8009 -p 8011:8011 ubiq

# Database API
cd ../database-api && docker build -t vasili/database-api .
docker run -d --restart unless-stopped -p 5000:5000 \
    -e DB_SERVER=mongo.example.org \
    -e DB_USERNAME=<user> -e DB_PASSWORD=<password> \
    -e X_API_KEY=<secret> \
    vasili/database-api
```

Plus a MongoDB instance - see [Data Model](data_model.md#mongodb-deployment).

!!! tip "For a full VR interview deployment, use InterView"
    [InterView](https://texttechnologylab.github.io/InterView/) provides a Docker
    Compose stack that brings up the Ubiq server and the Database API together
    with a Janus WebRTC gateway, an optional TURN relay and a web client, with
    versioned configuration and restart policies. Its
    [setup guide](https://texttechnologylab.github.io/InterView/setup/) is the
    fastest route to a working deployment.

## Base images

`docker-images/` holds shared base images used by the other modules.

| Image | Contents |
|---|---|
| `vasili/python` | NVIDIA cuDNN base with Python and ffmpeg preinstalled |

[Speech](services/speech.md) builds on it.

## Secrets

No module reads a secrets file; all take credentials from the environment.

| Secret | Used by |
|---|---|
| `X_API_KEY` | [Database API](database_api.md), and every client that logs to it |
| `DB_PASSWORD` | Database API |
| `SOCKET_SECRET` | [Chatbot](services/chatbot.md) |
| TURN credentials | [Ubiq](ubiq_server.md) - in `config/local.json` |

!!! danger "Two committed defaults must be overridden"
    `X_API_KEY` defaults to the **empty string**, which accepts unauthenticated
    requests. `SOCKET_SECRET` has a committed default value. Set both explicitly
    in any deployment that is reachable by anything other than localhost.

## Ports

Defaults. Several modules default to `5000`, so they cannot run on the same host
without remapping.

| Module | Port |
|---|---|
| [Database API](database_api.md) | 5000 (`PORT`) |
| [Ubiq](ubiq_server.md) | 8009 / 8010 / 8011 |
| [Chatbot](services/chatbot.md) | 5000 (`PORT`) |
| [speech2text](services/speech.md#speech2text) | 5000 |
