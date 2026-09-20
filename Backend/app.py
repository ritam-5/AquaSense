import os

from flask import Flask, jsonify
from flask_cors import CORS

from routes.entries import entries_bp
from routes.stats import stats_bp

# Optional: `pip install python-dotenv` and uncomment the next two lines
# to load variables from a .env file automatically.
# from dotenv import load_dotenv
# load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False  # avoid 308 redirects between /api/entries and /api/entries/
CORS(app, origins=os.environ.get("CORS_ORIGIN", "*"))


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "aquasense-backend-python"})


app.register_blueprint(entries_bp, url_prefix="/api/entries")
app.register_blueprint(stats_bp, url_prefix="/api")  # exposes /api/stats, /api/tips, /api/seed


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
