import os
import re
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz


FUZZY_THRESHOLD = 90

PROMPT_INJECTION_PATTERNS = [

    r"ignore\s+(all\s+)?previous\s+instructions",

    r"ignore\s+(all\s+)?prior\s+instructions",

    r"forget\s+(all\s+)?previous\s+instructions",

    r"forget\s+everything",

    r"system\s+prompt",

    r"reveal\s+system\s+prompt",

    r"show\s+system\s+prompt",

    r"developer\s+mode",

    r"developer\s+message",

    r"hidden\s+instructions",

    r"internal\s+prompt",

    r"override\s+instructions",

    r"bypass\s+safety",

    r"disable\s+safety",

    r"ignore\s+safety",

    r"disable\s+guardrails",

    r"ignore\s+guardrails",

    r"act\s+as",

    r"pretend\s+to\s+be",

    r"you\s+are\s+now",

    r"do\s+anything\s+now",

    r"\bdan\b",

    r"prompt\s+injection",
]

def normalize(text: str):

    text = text.lower()

    text = text.replace("_", " ")

    text = text.replace("-", " ")

    text = re.sub(r"[^\w\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

CSV_PATH = Path(__file__).parent / "prompt_injections_benchmark.csv"
df = pd.read_csv(CSV_PATH)
df["label"] = df["label"].fillna("").astype(str)
df["text"] = df["text"].fillna("").astype(str)

JAILBREAK_PROMPTS = (
    df[df["label"].str.lower() == "jailbreak"]["text"]
    .tolist()
)

def normalize(text: str):

    text = text.lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(r"[^\w\s]", " ", text)

    text = re.sub(r"(.)\1{2,}", r"\1", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

JAILBREAK_PROMPTS = [
    normalize(x)
    for x in JAILBREAK_PROMPTS
]

PROMPT_INJECTION_PATTERNS = [

    r"ignore\s+(all\s+)?previous\s+instructions",

    r"forget\s+(all\s+)?previous\s+instructions",

    r"forget\s+everything",

    r"system\s+prompt",

    r"reveal\s+system\s+prompt",

    r"show\s+system\s+prompt",

    r"developer\s+mode",

    r"developer\s+message",

    r"hidden\s+instructions",

    r"internal\s+prompt",

    r"override",

    r"bypass",

    r"disable\s+safety",

    r"ignore\s+safety",

    r"disable\s+guardrails",

    r"ignore\s+guardrails",

    r"pretend\s+to\s+be",

    r"act\s+as",

    r"you\s+are\s+now",

    r"do\s+anything\s+now",

    r"\bdan\b",

]

def fuzzy_detection(prompt):

    prompt = normalize(prompt)

    best_score = 0
    best_match = None

    for jailbreak in JAILBREAK_PROMPTS:

        jailbreak = normalize(jailbreak)

        score = fuzz.partial_ratio(prompt, jailbreak)

        if score > best_score:
            best_score = score
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



def detect_prompt_injection(prompt):

    prompt = normalize(prompt)

    # Layer 1: Regex
    for pattern in PROMPT_INJECTION_PATTERNS:

        if re.search(pattern, prompt):

            return {
                "detected": True,
                "method": "REGEX",
                "matched": pattern,
                "score": 100,
            }

    # Layer 2: RapidFuzz
    detected, match, score = fuzzy_detection(prompt)

    if detected:

        return {
            "detected": True,
            "method": "RAPIDFUZZ",
            "matched": match,
            "score": score,
        }

    return {
        "detected": False,
        "method": None,
        "matched": None,
        "score": score,
    }