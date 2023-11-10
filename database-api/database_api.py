from common import app
import rest_logging
import rest_scene
import os

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    app.run(threaded=True, host="0.0.0.0", port=port)