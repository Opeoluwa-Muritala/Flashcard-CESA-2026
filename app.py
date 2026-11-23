import os
import json
from flask import Flask, request, jsonify, render_template
from groq import Groq, APIConnectionError, APIStatusError
from pypdf import PdfReader

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

API_KEY = os.environ.get("API_KEY")
MODEL = os.environ.get("MODEL", "openai/gpt-oss-20b")
client = Groq(api_key=API_KEY) if API_KEY else None

MAX_CHARS = 6000  # keeps requests small and fast on the free tier


def error(message, status):
    return jsonify({"error": message}), status


@app.errorhandler(413)
def too_large(_):
    return error("That file is larger than 5 MB.", 413)


@app.route("/")
def home():
    return render_template("index.html")


def build_prompt(mode, text):
    format_hint = '[{"question": "...", "answer": "..."}]'
    if mode == "questions":
        return (
            "Turn each question below into one study flashcard. Keep the question "
            "exactly as written on the front, and give a short, correct answer on the "
            "back. Use at most 10 cards. Reply ONLY with a JSON list like "
            f"{format_hint}. No extra text.\n\n" + text[:MAX_CHARS]
        )
    source = "the topic below" if mode == "topic" else "the notes below"
    return (
        f"Create 5 study flashcards about {source}. Reply ONLY with a JSON list like "
        f"{format_hint}. No extra text.\n\n" + text[:MAX_CHARS]
    )


@app.route("/generate", methods=["POST"])
def generate():
    if client is None:
        return error("API_KEY is not set. See the README, Step 2.", 500)

    mode = request.form.get("mode", "topic")

    if mode == "pdf":
        upload = request.files.get("pdf")
        if not upload:
            return error("Choose a PDF first.", 400)
        try:
            reader = PdfReader(upload.stream)
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except Exception:  # pypdf raises several error types for bad files
            return error("Could not open this PDF. Try another file.", 400)
        if not text:
            return error("No text found in this PDF. It may be a scanned image.", 400)
    else:
        text = request.form.get("text", "").strip()
        if not text:
            return error("Please enter some text first.", 400)

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": build_prompt(mode, text)}],
            timeout=30,
        )
    except APIConnectionError:
        return error("Could not reach Groq. Check your internet connection.", 502)
    except APIStatusError as e:
        return error(f"Groq returned status {e.status_code}: {e.message}", 502)

    reply = completion.choices[0].message.content or ""
    try:
        cards = json.loads(reply[reply.index("["): reply.rindex("]") + 1])
    except ValueError:
        return error("Could not read the cards. Generate again.", 500)

    valid = [c for c in cards if isinstance(c, dict) and "question" in c and "answer" in c]
    if not valid:
        return error("No usable cards came back. Generate again.", 500)

    return jsonify(valid[:10])


if __name__ == "__main__":
    app.run(debug=True)
