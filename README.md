# InfoScam Prevention

InfoScam Prevention is a generic-purpose web app for checking messages, captions, posts, and claims for common scam or misinformation warning signs.

This app was created for the SIT Hackrift Hackathon as a simple prevention tool that helps users pause, review suspicious online content, and make safer decisions before clicking links, sharing private information, sending money, or forwarding claims.

## Purpose

The goal of this app is to provide a fast first-pass risk check for text-based online content. It is designed for general awareness and education, not as a replacement for professional fact-checking, cybersecurity advice, or official reporting channels.

Users can paste suspicious text into the app, receive a risk assessment, review the warning signs that were detected, and submit feedback to improve future evaluation.

## Features

- Text analysis for scam and misinformation patterns.
- Risk score, confidence value, and readable verdict.
- Explanation of detected warning signs.
- Recommended next steps for safe verification.
- Feedback collection for user-labeled results.
- Lightweight Flask backend with a responsive frontend.

## Project Structure

```text
infoscam-prevention/
├── Hackrift/
│   ├── app.py
│   ├── model.py
│   ├── requirements.txt
│   ├── static/
│   │   ├── script.js
│   │   └── style.css
│   └── templates/
│       └── index.html
├── README.md
└── .gitignore
```

## Requirements

- Python 3.9 or newer.
- pip.

## Run locally

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r Hackrift/requirements.txt
python3 Hackrift/app.py
```

Then open `http://127.0.0.1:5000`.

## How to Use

1. Paste a suspicious message, social media post, caption, or claim into the text box.
2. Select `Analyze`.
3. Review the verdict, risk score, detected signals, and recommended next steps.
4. Use the feedback buttons to mark the result as `Risky` or `Safe`.

Feedback is saved locally to:

```text
Hackrift/feedback.csv
```

## API Endpoints

### `GET /`

Loads the web interface.

### `GET /health`

Returns a simple app health response.

### `POST /analyze-text`

Analyzes submitted text.

Example request:

```json
{
  "text": "URGENT: your account is locked. Click this link to verify your password."
}
```

Example response:

```json
{
  "is_misinformation": true,
  "risk_level": "High risk",
  "risk_score": 86,
  "confidence": 87,
  "message": "This message shows multiple scam or misinformation warning signs.",
  "signals": [],
  "recommendations": []
}
```

### `POST /submit-feedback`

Saves user feedback for a previous analysis.

Example request:

```json
{
  "text": "Example message",
  "user_verdict": true,
  "analysis": {
    "risk_score": 86,
    "confidence": 87,
    "is_misinformation": true
  }
}
```

## Notes

The current analyzer uses local heuristic rules rather than a trained machine learning model. It can help identify warning signs, but users should still verify important claims through trusted sources and official websites.
