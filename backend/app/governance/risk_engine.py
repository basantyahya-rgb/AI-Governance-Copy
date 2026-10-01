"""Single-source risk engine with binary ALLOW/BLOCK enforcement."""

from typing import Dict, List


PROMPT_FILTER_WEIGHTS = {

    "SYSTEM_COMMAND": 60,

    "MALWARE": 70,

    "DATA_EXFILTRATION": 65,

    "SOCIAL_ENGINEERING": 55,

    "SECRETS": 45,

    "HARMFUL": 65,

    "SAFE": 0,
}


MAX_INJECTION_WEIGHT = 100


PII_SEVERITY = {

    "Critical": 45,

    "High": 35,

    "Medium": 20,

    "Low": 10,
}


MAX_PII_SCORE = 60


NEMO_WEIGHT = 25


MAX_SCORE = 100


BLOCK_THRESHOLD = 30


def calculate_risk(
    prompt_filter: Dict,
    injection: Dict,
    pii_findings: List,
    nemo: Dict,
) -> Dict:

    score = 0

    reasons = []

    breakdown = {

        "prompt_filter": 0,

        "prompt_injection": 0,

        "pii": 0,

        "nemo": 0,
    }

    # =================================================
    # Prompt Filter
    # =================================================

    category = prompt_filter.get(
        "category",
        "SAFE",
    )

    if not prompt_filter.get(
        "allowed",
        True,
    ):

        weight = PROMPT_FILTER_WEIGHTS.get(
            category,
            50,
        )

        score += weight

        breakdown["prompt_filter"] = weight

        reasons.append(
            f"Prompt Filter blocked prompt ({category})."
        )

    # =================================================
    # Prompt Injection
    # =================================================

    if injection.get("detected"):

        score += MAX_INJECTION_WEIGHT

        breakdown["prompt_injection"] = (
            MAX_INJECTION_WEIGHT
        )

        confidence = float(
            injection.get(
                "confidence",
                injection.get(
                    "score",
                    100,
                ),
            )
            or 100
        )

        reasons.append(
            f"Prompt Injection detected "
            f"({confidence:.1f}% confidence)."
        )

    # =================================================
    # PII / Secrets
    # =================================================

    pii_score = 0

    for finding in pii_findings:

        pii_score += PII_SEVERITY.get(
            finding.get(
                "severity",
                "Medium",
            ),
            20,
        )

    pii_score = min(
        pii_score,
        MAX_PII_SCORE,
    )

    score += pii_score

    breakdown["pii"] = pii_score

    if pii_findings:

        reasons.append(
            f"{len(pii_findings)} sensitive "
            f"item(s) detected."
        )

    # =================================================
    # NeMo
    # =================================================

    if (
        nemo.get("available")
        and nemo.get("flagged")
    ):

        score += NEMO_WEIGHT

        breakdown["nemo"] = NEMO_WEIGHT

        reasons.append(
            "NeMo Guardrails flagged unsafe content."
        )

    # =================================================
    # Normalize
    # =================================================

    score = min(
        max(score, 0),
        MAX_SCORE,
    )

    # =================================================
    # Informational Risk Level
    # =================================================

    if score >= 75:

        level = "Critical"

    elif score >= 50:

        level = "High"

    elif score >= BLOCK_THRESHOLD:

        level = "Medium"

    else:

        level = "Low"

    # =================================================
    # Binary Decision
    # =================================================

    action = (
        "BLOCK"
        if score >= BLOCK_THRESHOLD
        else "ALLOW"
    )

    return {

        "score": score,

        "level": level,

        "action": action,

        "reasons": reasons,

        "breakdown": breakdown,
    }