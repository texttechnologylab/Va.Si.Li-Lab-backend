from common import app
import rest_logging
import rest_scene

if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", port=5000)