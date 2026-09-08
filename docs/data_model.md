# Data Model

Everything the [Database API](database_api.md) records goes into MongoDB. This
page documents the collections it writes, the indexes it creates, and the
timestamp semantics - which matter more than they look.

## Collections

Sixteen collections, created and indexed on startup.

### Tracking

Written by `POST /logging/player`, which fans one batched request out across all
of these. See [the fan-out](database_api.md#post-loggingplayer).

| Collection | Contents | Key fields |
|---|---|---|
| `Body` | Body position and rotation | `position`, `rotation`, `counter` |
| `Head` | Headset pose - from the camera fields of the body payload | `position`, `rotation`, `counter` |
| `Hand` | Hand pose, both sides in one collection | `position`, `rotation`, `identifier` (`left`/`right`), `counter` |
| `Finger` | Finger tracking | `rootPose`, `pointerPose`, `identifier`, `counter` |
| `Eye` | Eye tracking | `position`, `orientation` |
| `Facial` | Facial expression | `expressionWeights`, `expressionWeightConfidences` |
| `Audio` | Base64 audio chunks | `audio` |

!!! warning "`Finger`, `Eye` and `Facial` are conditional"
    They are only populated when the client includes a `metaMessage` field in the
    payload. Their absence means the client did not send it - not that tracking
    failed.

### Events and session data

| Collection | Written by | Contents |
|---|---|---|
| `object` | `/logging/object` | Object interaction - `interaction`, `hand`, `playerId` |
| `LogIn` | `/logging/playerLogIn` | Session start - `roomId`, `sceneName` |
| `Role` | `/logging/playerRoleLogIn` | Role assignment per player |
| `Level` | `/logging/levelChange` | Level transitions - `levelID`, `levelStatus` |
| `Log` | `/logging/log` | General log entries - `roomId`, `sceneName` |
| `Special` | `/logging/special` | Free-form structured payloads |
| `Misc` | `/logging/logMisc` | Miscellaneous events |
| `logging` | *(internal)* | |

### Scene definitions

| Collection | Contents |
|---|---|
| `scenarios` | Scene, level and role definitions |
| `globalInfos` | Global information served by `/info` |

## Timestamps

Every logged document carries two independent time values. Confusing them is the
most common analysis error.

| Field | Set by | Meaning |
|---|---|---|
| `localTime` | The **client** | The client's own clock. Sensor-synchronous, high resolution - the right choice for aligning modalities *within* one client |
| `serverTime` | The **API**, at insert | `datetime.now()` on the server when the request arrived |

!!! danger "`serverTime` is arrival time, not sample time"
    It is stamped when the request is *received*, and one request carries a
    **batch** of samples. Every sample in that batch gets the **same**
    `serverTime`, regardless of when it was actually captured. It is therefore
    useless as a per-sample timestamp.

    Use `localTime` for anything within a client. Use `serverTime` only to
    establish a coarse offset *between* clients - each client's clock is its own,
    and nothing synchronises them.

`counter` is the per-sample index within a batch, and is what recovers ordering
inside one request.

## Indexes

The API creates its indexes at startup - no manual step is needed. They cover
`playerId` and `messageId` on every collection, plus per-collection fields:

| Collection | Additional indexed fields |
|---|---|
| `Body`, `Head` | `counter`, `position`, `rotation` |
| `Hand` | `counter`, `identifier`, `position`, `rotation` |
| `Finger` | `counter`, `identifier`, `rootPose`, `pointerPose` |
| `Eye` | `position`, `orientation` |
| `Facial` | `expressionWeights`, `expressionWeightConfidences` |
| `object` | `interaction`, `hand` |
| `Log`, `LogIn` | `roomId`, `sceneName` |
| `Level` | `roomId`, `sceneName`, `levelID`, `levelStatus` |
| `Special` | `roomId` |

!!! note "Index creation is idempotent but not free"
    They are re-declared on every start. On a large existing database the first
    start after adding an index blocks until it is built.

## MongoDB deployment

Any reachable MongoDB instance works. A minimal container:

```yaml
services:
  mongodb:
    image: mongo:latest
    container_name: vasililab_mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: <user>
      MONGO_INITDB_ROOT_PASSWORD: <password>
    ports:
      - "27017:27017"
    volumes:
      - ./data/db:/data/db
      - ./mongod.conf:/etc/mongod.conf
    command: ["-f", "/etc/mongod.conf"]
```

```yaml title="mongod.conf"
storage:
  dbPath: /data/db
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
net:
  port: 27017
  bindIp: 0.0.0.0
security:
  authorization: enabled
```

!!! warning "`bindIp` and authorisation"
    `bindIp: 0.0.0.0` makes the database reachable on every interface. Combined
    with a published port it exposes MongoDB to anything that can route to the
    host. Keep `security.authorization: enabled`, and prefer binding to a private
    interface or leaving the port unpublished when the API runs on the same host.

### Capacity

Tracking data dominates. Continuous body, hand, head, eye and face sampling for
two participants produces a large number of small documents per session - plan
storage and an archival policy before a data collection period, not during one.
