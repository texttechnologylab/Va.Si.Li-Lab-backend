from flask import Flask, request
from flask_socketio import SocketIO, call
import os


max_buffer = os.environ.get("MAX_HTTP_BUFFER_SIZE", 20_000_000)
port = os.environ.get("PORT", 5000)
socket_secret = os.environ.get("SOCKET_SECRET", 'reallyGoodSecret!')
debug = os.environ.get("DEBUG", False)
host = os.environ.get("HOST", "0.0.0.0")

app = Flask(__name__)
app.config['SECRET_KEY'] = socket_secret
socketio = SocketIO(app, max_http_buffer_size=max_buffer)


# Dictionary of currently available chatbots
chatbots = {}


def get_chatbot_names():
    return map(lambda x: x["name"], chatbots.values())


def get_sid_by_name(name):
    for sid, chatbot in chatbots.items():
        if chatbot["name"] == name:
            return sid


@socketio.on('init')
def handle_connect(data):
    chatbots[request.sid] = data
    print("Initialized chatbot", data)


@socketio.on('disconnect')
def test_disconnect():
    if request.sid in chatbots:
        del chatbots[request.sid]
    print('Client disconnected')


@app.get("/chatbots")
def get_chatbots():
    return {"status": "success", "result": list(get_chatbot_names())}, 200


@app.post("/query")
def chatbot_query():
    chatbot_name = request.json["chatBotName"]
    if chatbot_name in get_chatbot_names():
        sid = get_sid_by_name(chatbot_name)
        res = call("query", request.json, to=sid, namespace="/", timeout=200)
        return res
    else:
        return {"status": "Chatbot not found"}, 404


@app.post("/unload")
def unload():
    chatbot_name = request.json["chatBotName"]
    if chatbot_name in get_chatbot_names():
        sid = get_sid_by_name(chatbot_name)
        res = call("unload", request.json, to=sid, namespace="/")
        return res
    else:
        return {"status": "Chatbot not found"}, 404


@app.post("/close")
def close():
    chatbot_name = request.json["chatBotName"]
    if chatbot_name in get_chatbot_names():
        sid = get_sid_by_name(chatbot_name)
        res = call("close", request.json, to=sid, namespace="/")
        return res, 200
    return {"status": "Chatbot not found"}, 404


if __name__ == '__main__':
    socketio.run(app, host=host, debug=debug, allow_unsafe_werkzeug=True, port=port)
