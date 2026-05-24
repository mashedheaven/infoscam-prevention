from __future__ import annotations

from typing import Any, Optional

from flask import Flask, jsonify, render_template, request

try:
    from .model import analyze_text as analyze_message
    from .model import save_feedback
except ImportError:
    from model import analyze_text as analyze_message
    from model import save_feedback


MAX_TEXT_LENGTH = 5000

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze-text", methods=["POST"])
def analyze_text_route():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify({"error": "Text is required."}), 400

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"Text must be {MAX_TEXT_LENGTH} characters or fewer."}), 400

    return jsonify(analyze_message(text))


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback_route():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    verdict = _normalize_user_verdict(data.get("user_verdict"))

    if not text:
        return jsonify({"error": "Text is required."}), 400

    if verdict is None:
        return jsonify({"error": "Feedback verdict must be risky or safe."}), 400

    analysis = data.get("analysis")
    if not isinstance(analysis, dict):
        analysis = {}

    save_feedback(text=text, user_verdict=verdict, analysis=analysis)
    return jsonify({"status": "saved"})


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found."}), 404


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"error": "Something went wrong."}), 500


def _normalize_user_verdict(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "risky", "misinformation", "scam", "yes"}:
            return True
        if normalized in {"false", "safe", "accurate", "no"}:
            return False

    return None


if __name__ == "__main__":
    app.run(debug=True)
