import os
import json
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Read the key from the environment (see README, Step 2)
API_KEY = os.environ.get("API_KEY")

# Free-tier chat endpoint and model. If the provider changes these, update them here.

API_URL = os.environ.get("API_URL", "https://api.groq.com/openai/v1/chat/completions")
MODEL = os.environ.get("MODEL", "openai/gpt-oss-20b")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if not API_KEY:
        return jsonify({"error": "API_KEY is not set. See the README, Step 2."}), 500

    topic = (request.get_json(silent=True) or {}).get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Please enter a topic or notes first."}), 400

    prompt = (
        "Create 5 study flashcards about the topic below. "
        "Reply ONLY with a JSON list like "
        '[{"question": "...", "answer": "..."}]. No extra text.\n\n'
        f"Topic: {topic}"
    )

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
    except requests.RequestException:
        return jsonify({"error": "Could not reach the model. Check your internet connection."}), 502

    if response.status_code != 200:
        return jsonify({"error": "The model request failed. Check your API key and model name."}), 502

    text = response.json()["choices"][0]["message"]["content"]
    try:
        cards = json.loads(text[text.index("["): text.rindex("]") + 1])
    except ValueError:
        return jsonify({"error": "Could not read the cards. Click Generate Cards again."}), 500

    valid = [c for c in cards if isinstance(c, dict) and "question" in c and "answer" in c]
    if not valid:
        return jsonify({"error": "No usable cards came back. Click Generate Cards again."}), 500

    return jsonify(valid)


if __name__ == "__main__":
    app.run(debug=True)
