"""PII and secret detection with safe redaction in API results."""

import re

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
)


analyzer = AnalyzerEngine()


def _register(
    name: str,
    entity: str,
    regex: str,
    score: float,
):

    recognizer = PatternRecognizer(

        supported_entity=entity,

        patterns=[
            Pattern(
                name=name,
                regex=regex,
                score=score,
            )
        ],
    )

    analyzer.registry.add_recognizer(
        recognizer
    )


_register(
    "egypt_national_id",
    "EGYPT_NATIONAL_ID",
    r"\b[23]\d{13}\b",
    0.9,
)


_register(
    "egypt_phone",
    "EGYPT_PHONE",
    r"(?:\+20|0020|0)1[0125]\d{8}\b",
    0.85,
)


_register(
    "egypt_landline",
    "EGYPT_LANDLINE",
    r"(?:\+20|0020|0)[2-9]\d{7,8}\b",
    0.75,
)


_register(
    "passport",
    "PASSPORT_NUMBER",
    r"\b[A-Z]{1,2}\d{7,8}\b",
    0.75,
)


# =====================================================
# Secrets
# =====================================================

SECRET_PATTERNS = {

    "JWT":
        r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",

    "Bearer_Token":
        r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*",

    "AWS_Access_Key":
        r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",

    "Google_API_Key":
        r"\bAIza[0-9A-Za-z\-_]{35}\b",

    "GitHub_PAT":
        r"\bgh[pousr]_[A-Za-z0-9]{36}\b",

    "Slack_Token":
        r"\bxox[baprs]-[A-Za-z0-9-]+\b",

    "Stripe_Live_Key":
        r"\bsk_live_[A-Za-z0-9]+\b",

    "OpenAI_Key":
        r"\bsk-[A-Za-z0-9]{20,}\b",

    "Private_Key":
        r"-----BEGIN(?: [A-Z0-9]+)? PRIVATE KEY-----",

    "SSH_Public_Key":
        r"\bssh-(?:rsa|ed25519|ecdsa)\s+[A-Za-z0-9+/=]+",

    "API_Key_Assignment":
        r"\b(?:api[_ -]?key|secret[_ -]?key)\s*[:=]\s*[A-Za-z0-9_\-]{12,}\b",
}


def _masked(value: str) -> str:

    if not value:

        return "[REDACTED]"

    if len(value) <= 8:

        return "[REDACTED]"

    return (
        f"{value[:3]}…{value[-3:]}"
    )


def detect_pii(text: str):

    text = str(text or "")

    findings = []

    # =================================================
    # Presidio
    # =================================================

    try:

        presidio_results = analyzer.analyze(
            text=text,
            language="en",
        )

    except Exception:

        presidio_results = []

    for result in presidio_results:

        value = text[
            result.start:result.end
        ]

        findings.append({

            "type": result.entity_type,

            "start": result.start,

            "end": result.end,

            "text": _masked(value),

            "confidence": round(
                result.score,
                3,
            ),

            "severity": (
                "High"
                if result.score >= 0.85
                else "Medium"
            ),
        })

    # =================================================
    # Secrets
    # =================================================

    for entity, pattern in SECRET_PATTERNS.items():

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE,
        ):

            findings.append({

                "type": entity,

                "start": match.start(),

                "end": match.end(),

                "text": _masked(
                    match.group()
                ),

                "confidence": 1.0,

                "severity": "High",
            })

    # =================================================
    # Deduplication
    # =================================================

    unique = []

    seen = set()

    for item in findings:

        key = (
            item["type"],
            item["start"],
            item["end"],
        )

        if key not in seen:

            seen.add(key)

            unique.append(item)

    return sorted(
        unique,
        key=lambda item: (
            item["start"],
            item["end"],
        ),
    )