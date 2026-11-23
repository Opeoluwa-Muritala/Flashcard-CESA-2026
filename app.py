import os
import json
from flask import Flask, request, jsonify, render_template
from groq import Groq, APIConnectionError, APIStatusError

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
MODEL = os.environ.get("MODEL", "openai/gpt-oss-20b")

client = Groq(api_key=API_KEY) if API_KEY else None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if client is None:
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
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            timeout=30,
        )
    except APIConnectionError:
        return jsonify({"error": "Could not reach Groq. Check your internet connection."}), 502
    except APIStatusError as e:
        return jsonify({"error": f"Groq returned status {e.status_code}: {e.message}"}), 502

    text = completion.choices[0].message.content or ""
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
