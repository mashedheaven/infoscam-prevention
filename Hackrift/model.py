from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern


BASE_DIR = Path(__file__).resolve().parent
FEEDBACK_PATH = BASE_DIR / "feedback.csv"


@dataclass(frozen=True)
class Rule:
    label: str
    pattern: Pattern[str]
    weight: int
    detail: str


RULES = [
    Rule(
        "Urgency pressure",
        re.compile(
            r"\b(urgent|immediately|act now|limited time|last warning|final notice|"
            r"within\s+\d+\s+(minutes?|hours?|days?))\b",
            re.IGNORECASE,
        ),
        16,
        "Uses time pressure to push a quick decision.",
    ),
    Rule(
        "Account threat",
        re.compile(
            r"\b(verify|confirm|update|unlock|reactivate|suspend(?:ed)?|blocked|locked)\b"
            r".{0,40}\b(account|bank|wallet|password|identity|profile|subscription)\b|"
            r"\b(account|bank|wallet|password|identity|profile|subscription)\b"
            r".{0,40}\b(verify|confirm|update|unlock|reactivate|suspend(?:ed)?|blocked|locked)\b",
            re.IGNORECASE,
        ),
        18,
        "Mentions account action tied to verification or suspension.",
    ),
    Rule(
        "Credential request",
        re.compile(
            r"\b(password|passcode|pin|otp|one[-\s]?time code|2fa|security code|"
            r"login details|seed phrase|recovery phrase)\b",
            re.IGNORECASE,
        ),
        22,
        "Requests sensitive login or recovery information.",
    ),
    Rule(
        "Payment pressure",
        re.compile(
            r"\b(gift cards?|wire transfer|bank transfer|crypto(?:currency)?|bitcoin|usdt|"
            r"western union|cash app|zelle|venmo|apple pay|deposit|processing fee)\b",
            re.IGNORECASE,
        ),
        18,
        "Pushes payment methods commonly used in scams.",
    ),
    Rule(
        "Prize or refund lure",
        re.compile(
            r"\b(congratulations|winner|you(?:'|')?ve won|you have won|lottery|jackpot|"
            r"prize|claim your reward|refund available|unclaimed funds)\b",
            re.IGNORECASE,
        ),
        15,
        "Promises money, prizes, refunds, or rewards.",
    ),
    Rule(
        "Too-good-to-be-true claim",
        re.compile(
            r"\b(guaranteed|risk[-\s]?free|double your money|passive income|secret method|"
            r"no experience needed|get rich|100x|sure profit)\b",
            re.IGNORECASE,
        ),
        16,
        "Makes an unusually strong financial or outcome guarantee.",
    ),
    Rule(
        "Link or attachment command",
        re.compile(
            r"\b(click|tap|open|visit|download|scan)\b.{0,40}\b(link|url|attachment|"
            r"file|form|qr code|code)\b",
            re.IGNORECASE,
        ),
        13,
        "Asks the reader to open a link, attachment, form, or code.",
    ),
    Rule(
        "Health misinformation marker",
        re.compile(
            r"\b(miracle cure|cures? cancer|doctors hate|natural cure|"
            r"vaccine.{0,24}(dangerous|hoax|poison)|covid.{0,24}(hoax|fake))\b",
            re.IGNORECASE,
        ),
        18,
        "Uses a common unsupported health-claim pattern.",
    ),
    Rule(
        "Conspiracy framing",
        re.compile(
            r"\b(they don'?t want you to know|mainstream media won'?t tell|wake up|"
            r"cover[-\s]?up|deep state|false flag)\b",
            re.IGNORECASE,
        ),
        14,
        "Relies on secrecy or conspiracy framing instead of verifiable evidence.",
    ),
    Rule(
        "Viral sharing pressure",
        re.compile(
            r"\b(share before deleted|forward this to everyone|send this to all|"
            r"confirmed by unnamed sources|100% true)\b",
            re.IGNORECASE,
        ),
        14,
        "Pushes viral sharing without a clear source.",
    ),
    Rule(
        "Impersonation risk",
        re.compile(
            r"\b(irs|social security|police|fbi|customs|delivery|post office|bank|"
            r"netflix|paypal|amazon|microsoft|apple)\b.{0,50}\b(fine|arrest|suspended|"
            r"failed delivery|unpaid|unusual activity|locked|refund)\b",
            re.IGNORECASE,
        ),
        16,
        "References a trusted organization alongside a threat or payment issue.",
    ),
]

URL_PATTERN = re.compile(r"\b(https?://|www\.|bit\.ly/|tinyurl\.com/|t\.co/|wa\.me/|telegram\.me/)", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
MONEY_PATTERN = re.compile(r"([$€£]\s?\d+|\b\d+\s?(usd|sgd|eur|gbp|dollars?|bucks)\b)", re.IGNORECASE)
SOURCE_PATTERN = re.compile(
    r"\b(according to|source:|doi:|peer[-\s]?reviewed|reuters|associated press|ap news|"
    r"bbc|cdc\.gov|who\.int|fda\.gov|ftc\.gov|gov\.sg|police\.gov\.sg)\b",
    re.IGNORECASE,
)


def analyze_text(text: str) -> Dict[str, Any]:
    """Score user text for common scam and misinformation warning signs."""
    clean_text = " ".join((text or "").split())
    signals: List[Dict[str, Any]] = []
    score = 5

    for rule in RULES:
        if rule.pattern.search(clean_text):
            score += rule.weight
            signals.append(
                {
                    "label": rule.label,
                    "detail": rule.detail,
                    "weight": rule.weight,
                }
            )

    if URL_PATTERN.search(clean_text):
        score += 12
        signals.append(
            {
                "label": "External link",
                "detail": "Contains a link or shortened URL that should be verified before opening.",
                "weight": 12,
            }
        )

    if PHONE_PATTERN.search(clean_text):
        score += 7
        signals.append(
            {
                "label": "Phone contact",
                "detail": "Includes a phone number or contact route outside normal channels.",
                "weight": 7,
            }
        )

    if MONEY_PATTERN.search(clean_text):
        score += 10
        signals.append(
            {
                "label": "Money mentioned",
                "detail": "Mentions a payment amount, refund, fee, or financial transfer.",
                "weight": 10,
            }
        )

    if _uppercase_ratio(clean_text) > 0.4 and len(clean_text) > 35:
        score += 6
        signals.append(
            {
                "label": "High-emphasis wording",
                "detail": "Uses heavy capitalization, which often appears in manipulative messages.",
                "weight": 6,
            }
        )

    if clean_text.count("!") >= 3 or clean_text.count("?") >= 3:
        score += 5
        signals.append(
            {
                "label": "Excess punctuation",
                "detail": "Uses repeated punctuation to intensify the message.",
                "weight": 5,
            }
        )

    word_count = len(clean_text.split())
    if word_count < 5 and score < 35:
        score = 36
        signals.append(
            {
                "label": "Limited context",
                "detail": "The text is too short for a confident assessment.",
                "weight": 0,
            }
        )

    if SOURCE_PATTERN.search(clean_text) and score < 55:
        score -= 8

    risk_score = _clamp(score)
    verdict, risk_level, message = _verdict_for_score(risk_score)

    return {
        "is_misinformation": verdict,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "confidence": _confidence_for_score(risk_score),
        "message": message,
        "signals": signals[:6],
        "recommendations": _recommendations(verdict),
    }


def save_feedback(text: str, user_verdict: bool, analysis: Optional[Dict[str, Any]] = None) -> None:
    """Append user feedback to a local CSV file for later review."""
    analysis = analysis or {}
    file_has_data = FEEDBACK_PATH.exists() and FEEDBACK_PATH.stat().st_size > 0
    fieldnames = [
        "created_at",
        "user_verdict",
        "model_verdict",
        "risk_score",
        "confidence",
        "text",
    ]

    with FEEDBACK_PATH.open("a", newline="", encoding="utf-8") as feedback_file:
        writer = csv.DictWriter(feedback_file, fieldnames=fieldnames)
        if not file_has_data:
            writer.writeheader()

        writer.writerow(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "user_verdict": "risky" if user_verdict else "safe",
                "model_verdict": analysis.get("is_misinformation", ""),
                "risk_score": analysis.get("risk_score", ""),
                "confidence": analysis.get("confidence", ""),
                "text": _csv_safe(text),
            }
        )


def _verdict_for_score(score: int) -> tuple[Any, str, str]:
    if score >= 65:
        return (
            True,
            "High risk",
            "This message shows multiple scam or misinformation warning signs.",
        )

    if score >= 35:
        return (
            "uncertain",
            "Needs review",
            "There is not enough reliable context to make a strong call.",
        )

    return (
        False,
        "Low risk",
        "No strong scam or misinformation signals were found.",
    )


def _recommendations(verdict: Any) -> List[str]:
    if verdict is True:
        return [
            "Do not click links, send money, or share private codes.",
            "Verify the claim through an official website or known phone number.",
            "Search for the same claim in trusted reporting or government sources.",
        ]

    if verdict == "uncertain":
        return [
            "Check whether the sender, link, and claim can be verified independently.",
            "Look for a primary source before forwarding or acting on the message.",
            "Treat requests for money, passwords, or OTPs as high risk.",
        ]

    return [
        "Keep verifying important decisions through official sources.",
        "Be cautious if the sender later asks for payment, codes, or urgent action.",
    ]


def _confidence_for_score(score: int) -> int:
    if score >= 65:
        return _clamp(round(72 + ((score - 65) * 0.7)))

    if score < 35:
        return _clamp(round(68 + ((35 - score) * 0.6)))

    return _clamp(round(52 + abs(score - 50) * 0.5))


def _uppercase_ratio(text: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    uppercase = [char for char in letters if char.isupper()]
    return len(uppercase) / len(letters)


def _clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, int(round(value))))


def _csv_safe(value: str) -> str:
    clean_value = " ".join((value or "").split())
    if clean_value[:1] in {"=", "+", "-", "@"}:
        return f"'{clean_value}"
    return clean_value
