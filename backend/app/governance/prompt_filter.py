"""Context-aware deterministic prompt security filter."""

import re

from rapidfuzz import fuzz


FUZZY_THRESHOLD = 94


BLOCKED_PATTERNS = {

    "SYSTEM_COMMAND": [

        r"\b(?:rm\s+-rf|format|shutdown|reboot|poweroff|halt|killall|taskkill)\b",

        r"\b(?:drop|delete|truncate)\s+(?:the\s+)?(?:database|table|schema)\b",

        r"\b(?:erase|wipe|destroy)\s+(?:the\s+)?(?:system|disk|database|data|files?)\b",
    ],

    "MALWARE": [

        r"\b(?:create|write|build|develop|deploy|install|execute|run)\s+(?:a\s+)?(?:malware|virus|worm|trojan|ransomware|spyware|rootkit|keylogger|backdoor|botnet)\b",

        r"\b(?:install|deploy|execute|run)\s+(?:this|the)\s+(?:malware|virus|ransomware|trojan)\b",

        r"\b(?:steal|exfiltrate)\s+(?:credentials?|passwords?|tokens?|data)\b",
    ],

    "DATA_EXFILTRATION": [

        r"\b(?:steal|exfiltrate|leak|dump|export)\s+(?:the\s+)?(?:database|data|credentials?|passwords?|tokens?)\b",

        r"\b(?:download|copy)\s+(?:the\s+)?(?:entire\s+)?database\b",
    ],

    "SOCIAL_ENGINEERING": [

        r"\b(?:create|write|send|build)\s+(?:a\s+)?phishing\s+(?:email|page|message|campaign)\b",

        r"\b(?:impersonate|spoof)\s+(?:a\s+)?(?:person|employee|admin|company|user)\b",

        r"\bcredential\s+harvesting\b",
    ],

    "HARMFUL": [

        r"\b(?:bypass|circumvent)\s+(?:authentication|authorization|security|access\s+control)\b",

        r"\b(?:perform|launch|execute)\s+(?:a\s+)?(?:ddos|denial\s+of\s+service)\b",

        r"\b(?:exploit|attack)\s+(?:this|the)\s+(?:server|website|system|target)\b",
    ],
}


FUZZY_PHRASES = {

    "SYSTEM_COMMAND": (
        "delete database",
        "drop database",
        "wipe system",
    ),

    "MALWARE": (
        "install malware",
        "create malware",
        "deploy ransomware",
        "write a virus",
    ),

    "DATA_EXFILTRATION": (
        "steal data",
        "dump database",
        "exfiltrate credentials",
    ),

    "SOCIAL_ENGINEERING": (
        "credential harvesting",
        "phishing campaign",
        "impersonate admin",
    ),

    "HARMFUL": (
        "bypass authentication",
        "attack the server",
        "launch ddos",
    ),
}


def normalize(text: str) -> str:

    text = str(text or "").lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"[\u200b-\u200f\u202a-\u202e\ufeff]",
        "",
        text,
    )

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE,
    )

    text = re.sub(
        r"(.)\1{2,}",
        r"\1",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def filter_prompt(prompt: str):

    normalized = normalize(prompt)

    # =================================================
    # Deterministic rules
    # =================================================

    for category, patterns in BLOCKED_PATTERNS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                normalized,
                re.IGNORECASE,
            ):

                return (
                    False,
                    f"Regex matched: {pattern}",
                    category,
                )

    # =================================================
    # Fuzzy rules
    # =================================================

    for category, phrases in FUZZY_PHRASES.items():

        for phrase in phrases:

            if (
                fuzz.partial_ratio(
                    normalized,
                    phrase,
                )
                >= FUZZY_THRESHOLD
            ):

                return (
                    False,
                    f"Fuzzy matched dangerous action: '{phrase}'",
                    category,
                )

    # =================================================
    # Safe
    # =================================================

    return (
        True,
        "Prompt passed security filter.",
        "SAFE",
    )