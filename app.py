from flask import Flask, request, redirect, render_template, jsonify
import string, random
from urllib.parse import urlparse

app = Flask(__name__)

# In-memory storage: short_code -> long_url
url_map = {}
# Optional: keep a small recent list for UX (code, url)
recent = []

ALPHABET = string.ascii_letters + string.digits

def generate_short_code(length: int = 4) -> str:
    # generate a unique short code
    while True:
        code = ''.join(random.choice(ALPHABET) for _ in range(length))
        if code not in url_map:
            return code

def normalize_url(u: str) -> str:
    """Ensure the URL has a scheme; if missing, default to https://"""
    if not u:
        return u
    parsed = urlparse(u)
    if not parsed.scheme:
        return "https://" + u
    return u

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True) or {}
    long_url = (data.get("long_url") or "").strip()

    # Basic validation
    if not long_url:
        return jsonify({"error": "Please provide a URL."}), 400

    long_url = normalize_url(long_url)
    parsed = urlparse(long_url)
    if not parsed.netloc:
        return jsonify({"error": "Invalid URL."}), 400

    # Create short code and store
    code = generate_short_code(length=4)
    url_map[code] = long_url

    # Update recent list (cap at 20)
    recent.insert(0, (code, long_url))
    if len(recent) > 20:
        recent.pop()

    short_url = request.host_url + code
    return jsonify({"short_url": short_url})

@app.route("/<code>", methods=["GET"])
def redirect_to_original(code):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url, code=302)
    return "Short URL not found.", 404

if __name__ == "__main__":
    # Run locally
    app.run(host="0.0.0.0", port=5000, debug=True)
