"""Prompt-injection detection.

Deterministic first, fuzzy second. Explicit instruction-hijacking
phrases are blocked immediately, while fuzzy matching is gated
to reduce false positives.
"""

import csv
import re
from functools import lru_cache
from pathlib import Path

from rapidfuzz import fuzz


FUZZY_THRESHOLD = 92


INJECTION_PATTERNS = [
    r"\bignore\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|earlier)\s+instructions?\b",
    r"\bforget\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|earlier)\s+instructions?\b",
    r"\bdisregard\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|earlier)\s+instructions?\b",

    r"\boverride\s+(?:the\s+)?(?:system|developer|safety|security)\s+(?:instructions?|rules?|policy)\b",

    r"\breveal\s+(?:the\s+)?(?:hidden\s+)?(?:system|developer)\s+prompt\b",

    r"\b(?:show|print|display|output|expose)\s+(?:the\s+)?(?:hidden\s+)?(?:system|developer)\s+(?:prompt|instructions?)\b",

    r"\b(?:reveal|show|expose|print|output)\s+(?:your|the)\s+(?:hidden\s+)?instructions?\b",

    r"\b(?:ignore|disregard|bypass|disable)\s+(?:the\s+)?(?:safety|security|guardrails?|policy|rules?)\b",

    r"\b(?:developer|admin|administrator|system)\s+mode\b",

    r"\b(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be)\b.*\b(?:unrestricted|unfiltered|jailbroken|dan)\b",

    r"\bdo\s+anything\s+now\b",

    r"\b(?:dan|jailbreak|jailbroken)\b",

    r"\bprompt\s+injection\b.*\b(?:ignore|override|bypass)\b",
]


INJECTION_ACTION_CUES = (
    "ignore",
    "disregard",
    "forget",
    "override",
    "bypass",
    "disable",
    "reveal",
    "show",
    "expose",
    "system prompt",
    "developer message",
    "hidden instructions",
    "guardrails",
    "jailbreak",
    "dan",
    "unrestricted",
)


CSV_PATH = Path(__file__).parent / "prompt_injections_benchmark.csv"


def normalize(text: str) -> str:

    text = str(text or "").lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    # Remove zero-width / bidi characters.
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

    # Normalize repeated characters.
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


@lru_cache(maxsize=1)
def _load_jailbreak_prompts() -> tuple[str, ...]:

    if not CSV_PATH.exists():
        return ()

    prompts = []

    try:

        with CSV_PATH.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:

            reader = csv.DictReader(handle)

            for row in reader:

                if (
                    str(row.get("label", ""))
                    .strip()
                    .lower()
                    == "jailbreak"
                ):

                    value = normalize(
                        row.get("text", "")
                    )

                    if value:
                        prompts.append(value)

    except (
        OSError,
        csv.Error,
    ):

        return ()

    return tuple(prompts)


def _fuzzy_detection(prompt: str):

    # Do not run expensive fuzzy comparison against
    # the whole benchmark for normal prompts.

    if not any(
        cue in prompt
        for cue in INJECTION_ACTION_CUES
    ):

        return (
            False,
            None,
            0.0,
        )

    best_score = 0.0
    best_match = None

    for jailbreak in _load_jailbreak_prompts():

        score = fuzz.partial_ratio(
            prompt,
            jailbreak,
        )

        if score > best_score:

            best_score = float(score)
            best_match = jailbreak

    if best_score >= FUZZY_THRESHOLD:

        return (
            True,
            best_match,
            best_score,
        )

    return (
        False,
        None,
        best_score,
    )


def detect_prompt_injection(prompt: str) -> dict:

    normalized = normalize(prompt)

    # =================================================
    # Layer 1: Deterministic regex
    # =================================================

    for pattern in INJECTION_PATTERNS:

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        ):

            return {
                "detected": True,
                "method": "REGEX",
                "matched": pattern,
                "confidence": 100.0,
                "score": 100.0,
            }

    # =================================================
    # Layer 2: Fuzzy benchmark detection
    # =================================================

    detected, match, score = _fuzzy_detection(
        normalized
    )

    if detected:

        return {
            "detected": True,
            "method": "RAPIDFUZZ",
            "matched": match,
            "confidence": round(score, 2),
            "score": round(score, 2),
        }

    return {
        "detected": False,
        "method": None,
        "matched": None,
        "confidence": round(score, 2),
        "score": round(score, 2),
    }