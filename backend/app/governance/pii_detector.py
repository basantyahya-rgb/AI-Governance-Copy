"""
PII Detection Layer

Enterprise PII Detection
- Microsoft Presidio
- Egyptian custom recognizers
- Secret detection
"""

import re

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
)

# -------------------------------------------------------
# Presidio Engine
# -------------------------------------------------------

analyzer = AnalyzerEngine()

# -------------------------------------------------------
# Egyptian National ID
# -------------------------------------------------------

egypt_id_pattern = Pattern(
    name="egypt_national_id",
    regex=r"\b[23]\d{13}\b",
    score=0.9,
)

egypt_id = PatternRecognizer(
    supported_entity="EGYPT_NATIONAL_ID",
    patterns=[egypt_id_pattern],
)

analyzer.registry.add_recognizer(egypt_id)

# -------------------------------------------------------
# Egyptian Mobile Numbers
# -------------------------------------------------------

egypt_phone_pattern = Pattern(
    name="egypt_phone",
    regex=r"(?:\+20|0020|0)?1[0125]\d{8}\b",
    score=0.85,
)

egypt_phone = PatternRecognizer(
    supported_entity="EGYPT_PHONE",
    patterns=[egypt_phone_pattern],
)

analyzer.registry.add_recognizer(egypt_phone)

# -------------------------------------------------------
# Egyptian Landline
# -------------------------------------------------------

landline_pattern = Pattern(
    name="egypt_landline",
    regex=r"(?:\+20|0020|0)[2-9]\d{7,8}\b",
    score=0.75,
)

landline = PatternRecognizer(
    supported_entity="EGYPT_LANDLINE",
    patterns=[landline_pattern],
)

analyzer.registry.add_recognizer(landline)

# -------------------------------------------------------
# Passport
# -------------------------------------------------------

passport_pattern = Pattern(
    name="passport",
    regex=r"\b[A-Z]{1,2}\d{7,8}\b",
    score=0.75,
)

passport = PatternRecognizer(
    supported_entity="PASSPORT_NUMBER",
    patterns=[passport_pattern],
)

analyzer.registry.add_recognizer(passport)

# -------------------------------------------------------
# Driver License
# -------------------------------------------------------

license_pattern = Pattern(
    name="driver_license",
    regex=r"\b\d{8,14}\b",
    score=0.45,
)

driver_license = PatternRecognizer(
    supported_entity="DRIVER_LICENSE",
    patterns=[license_pattern],
)

analyzer.registry.add_recognizer(driver_license)

# -------------------------------------------------------
# Secrets
# -------------------------------------------------------

SECRET_PATTERNS = {

    "API_KEY":
        r"\b(?:sk|pk|api)[-_]?[A-Za-z0-9]{16,}\b",

    "JWT":
        r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",

    "Bearer":
        r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",

    "AWS_ACCESS_KEY":
        r"\b(AKIA|ASIA)[A-Z0-9]{16}\b",

    "AWS_SECRET":
        r"\b[0-9A-Za-z/+]{40}\b",

    "Private_Key":
        r"-----BEGIN.*PRIVATE KEY-----",

    "SSH_Key":
        r"ssh-rsa\s+[A-Za-z0-9+/=]+",

    "Azure_Key":
        r"\b[a-zA-Z0-9]{32}\b",

    "Google_API_Key":
        r"AIza[0-9A-Za-z\-_]{35}",

    "Slack_Token":
        r"xox[baprs]-[A-Za-z0-9-]+",

    "GitHub_PAT":
        r"gh[pousr]_[A-Za-z0-9]{36}",

    "Stripe_Key":
        r"sk_live_[A-Za-z0-9]+",

    "OpenAI_Key":
        r"sk-[A-Za-z0-9]{20,}",

}

# -------------------------------------------------------
# Severity
# -------------------------------------------------------

HIGH = {

    "API_KEY",
    "JWT",
    "Bearer",
    "AWS_ACCESS_KEY",
    "AWS_SECRET",
    "Private_Key",
    "SSH_Key",
    "Azure_Key",
    "Google_API_Key",
    "Slack_Token",
    "GitHub_PAT",
    "Stripe_Key",
    "OpenAI_Key",
}

# -------------------------------------------------------
# Detection
# -------------------------------------------------------

def detect_pii(text: str):

    findings = []

    presidio_results = analyzer.analyze(
        text=text,
        language="en",
    )

    for result in presidio_results:

        findings.append({

            "type": result.entity_type,

            "start": result.start,

            "end": result.end,

            "text": text[result.start:result.end],

            "confidence": round(result.score, 3),

            "severity": (
                "High"
                if result.score > 0.85
                else "Medium"
            )

        })

    for entity, pattern in SECRET_PATTERNS.items():

        for match in re.finditer(pattern, text, re.IGNORECASE):

            findings.append({

                "type": entity,

                "start": match.start(),

                "end": match.end(),

                "text": match.group(),

                "confidence": 1.0,

                "severity": (
                    "High"
                    if entity in HIGH
                    else "Medium"
                )

            })

    # Remove duplicate detections
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

    return sorted(unique, key=lambda x: x["start"])

"""
This implementation combines Presidio's built-in recognizers with your custom ones. It will detect:

- Email addresses
- Person names
- Phone numbers
- Egyptian mobile numbers
- Egyptian landlines
- Egyptian National IDs (14 digits)
- Passport numbers
- Driver license patterns
- Credit card numbers
- IBANs and bank account identifiers (via Presidio where applicable)
- URLs and IP addresses (if enabled by Presidio)
- JWT tokens
- API keys
- Bearer tokens
- AWS access keys and secrets
- OpenAI keys
- GitHub Personal Access Tokens
- Slack tokens
- Google API keys
- Azure keys
- Stripe keys
- SSH public keys
- Private keys (PEM/RSA/OpenSSH)
"""