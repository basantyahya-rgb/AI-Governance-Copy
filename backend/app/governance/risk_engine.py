"""
Risk Assessment Layer

Aggregates all governance modules into a deterministic
enterprise risk score.
"""

from typing import Dict, List


# =====================================================
# Prompt Filter Weights
# =====================================================

PROMPT_FILTER_WEIGHTS = {

    "SYSTEM_COMMAND": 45,

    "MALWARE": 45,

    "DATA_EXFILTRATION": 40,

    "SOCIAL_ENGINEERING": 35,

    "SECRETS": 30,

    "HARMFUL": 40,

    "SAFE": 0,
}


# =====================================================
# Injection
# =====================================================

MAX_INJECTION_WEIGHT = 40


# =====================================================
# PII
# =====================================================

PII_SEVERITY = {

    "Critical": 20,

    "High": 15,

    "Medium": 8,

    "Low": 3,
}

MAX_PII_SCORE = 40


# =====================================================
# NeMo
# =====================================================

NEMO_WEIGHT = 20


# =====================================================
# Total
# =====================================================

MAX_SCORE = 100


# =====================================================
# Thresholds
# =====================================================

LOW = 25

MEDIUM = 50

HIGH = 75


# =====================================================
# Risk Calculation
# =====================================================

def calculate_risk(

    prompt_filter: Dict,

    injection: Dict,

    pii_findings: List,

    nemo: Dict,

) -> Dict:

    score = 0

    reasons = []

    breakdown = {}


    # =================================================
    # Prompt Filter
    # =================================================

    category = prompt_filter.get("category", "SAFE")

    if not prompt_filter.get("allowed", True):

        weight = PROMPT_FILTER_WEIGHTS.get(category, 30)

        score += weight

        breakdown["prompt_filter"] = weight

        reasons.append(
            f"Prompt Filter blocked prompt ({category})."
        )

    else:

        breakdown["prompt_filter"] = 0


    # =================================================
    # Prompt Injection
    # =================================================

    if injection.get("detected"):

        confidence = injection.get("confidence", 100)

        if confidence >= 95:

            inj_score = 40

        elif confidence >= 90:

            inj_score = 35

        elif confidence >= 80:

            inj_score = 30

        else:

            inj_score = 20

        score += inj_score

        breakdown["prompt_injection"] = inj_score

        reasons.append(

            f"Prompt Injection detected ({confidence:.1f}% confidence)."

        )

    else:

        breakdown["prompt_injection"] = 0


    # =================================================
    # PII
    # =================================================

    pii_score = 0

    for finding in pii_findings:

        severity = finding.get("severity", "Medium")

        pii_score += PII_SEVERITY.get(severity, 8)

    pii_score = min(pii_score, MAX_PII_SCORE)

    score += pii_score

    breakdown["pii"] = pii_score

    if pii_findings:

        reasons.append(

            f"{len(pii_findings)} sensitive item(s) detected."

        )


    # =================================================
    # NeMo
    # =================================================

    if nemo.get("available"):

        if nemo.get("flagged"):

            score += NEMO_WEIGHT

            breakdown["nemo"] = NEMO_WEIGHT

            reasons.append(

                "NeMo Guardrails flagged unsafe content."

            )

        else:

            breakdown["nemo"] = 0

    else:

        breakdown["nemo"] = 0

        reasons.append(

            "NeMo Guardrails unavailable."

        )


    # =================================================
    # Normalize
    # =================================================

    score = min(score, MAX_SCORE)


    # =================================================
    # Risk Level
    # =================================================

    if score >= HIGH:

        level = "Critical"

        action = "BLOCK"

    elif score >= MEDIUM:

        level = "High"

        action = "BLOCK"

    elif score >= LOW:

        level = "Medium"

        action = "REVIEW"

    else:

        level = "Low"

        action = "ALLOW"


    return {

        "score": score,

        "level": level,

        "action": action,

        "reasons": reasons,

        "breakdown": breakdown,

    }