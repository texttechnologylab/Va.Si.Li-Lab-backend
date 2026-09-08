# Ubiq Server

The room and session server. Keeps shared state - avatars, transforms, object
ownership - synchronised between connected clients.

A modified version of [Ubiq](https://ubiq.online/) (UCL)
([docs](https://ucl-vr.github.io/ubiq/) ·
[GitHub](https://github.com/UCL-VR/ubiq/)), extended with the functionality
Va.Si.Li-Lab needs.

Source: `Ubiq-server/` · Node.js + TypeScript

!!! info "State only"
    Ubiq carries **no audio or video**. In deployments that stream media - such as
    [InterView](https://texttechnologylab.github.io/InterView/) - that is a
    separate service, and the two fail independently. A session can have working
    voice and broken avatars, or the reverse.

## Ports

| Port | Purpose |
|---|---|
| `8009` | TCP room server - what the Unity client connects to |
| `8010` | Secure WebSocket room server |
| `8011` | Status and metrics |

## Configuration

Configuration is layered by [`nconf`](https://github.com/indexzero/nconf) and
resolved **first-wins**:

1. Files passed as command-line arguments
2. `config/local.json` - deployment overrides, **not** in source control
3. `config/default.json` - committed defaults

To change a setting, add it to `config/local.json` rather than editing the
committed defaults.

```json title="config/local.json"
{
    "roomserver": {
        "tcp": { "port": 8009 },
        "wss": { "port": 8010, "cert": "./cert.pem", "key": "./key.pem" }
    },
    "status": { "port": 8011, "cert": "./cert.pem", "key": "./key.pem", "apikeys": [] },
    "iceservers": [
        { "uri": "turn:turn.example.org:3478", "username": "<user>", "password": "<password>" }
    ]
}
```

### `iceservers`

Handed to clients when they connect. The committed default is a public Google
STUN server, which is enough for clients on permissive networks.

!!! warning "Credentials belong in `config/local.json`"
    `config/default.json` is committed. TURN credentials placed there end up in
    the repository. Put them in `config/local.json`, which is not tracked.

### Room types

`roomserver:roomType`, if set, selects the room class the server instantiates.
The class must already be imported by the entry point.

## Running

=== "Docker"

    ```bash
    cd Ubiq-server
    docker build -t ubiq .
    docker run -d --restart unless-stopped -p 8009:8009 -p 8011:8011 ubiq
    ```

=== "Locally"

    ```bash
    cd Ubiq-server
    npm install
    node --loader ts-node/esm app.ts
    ```

The container runs as an unprivileged user (`uid 8877`).

## Unity client

Set the connection definition in `SocialNetworkScene > RoomClient` to this
server's host and TCP port. See the
[Va.Si.Li-Lab documentation](https://texttechnologylab.github.io/Va.Si.Li-Lab/).

## Citation

```bibtex
@inproceedings{friston2021ubiq,
  title={Ubiq: A system to build flexible social virtual reality experiences},
  author={Friston, Sebastian J and Congdon, Ben J and Swapp, David and Izzouzi, Lisa
          and Brandst{\"a}tter, Klara and Archer, Daniel and Olkkonen, Otto
          and Thiel, Felix Johannes and Steed, Anthony},
  booktitle={Proceedings of the 27th ACM symposium on virtual reality software and technology},
  pages={1--11},
  year={2021}
}
```
