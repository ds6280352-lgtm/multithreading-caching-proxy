
import threading
from flask import Flask, render_template, jsonify

from proxy_server import start_server, get_server_stats
from http_handler import cache

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    server_stats = get_server_stats()
    cache_stats = cache.get_stats()

    return jsonify({
        "server": server_stats,
        "cache": cache_stats
    })


if __name__ == "__main__":

    proxy_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    proxy_thread.start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
