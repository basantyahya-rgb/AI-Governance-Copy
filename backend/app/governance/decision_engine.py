"""Compatibility wrapper for the binary governance policy."""


BLOCK_THRESHOLD = 30


def make_decision(score) -> str:

    try:

        numeric_score = float(score)

    except (
        TypeError,
        ValueError,
    ):

        # Fail closed.

        return "BLOCK"

    return (
        "BLOCK"
        if numeric_score >= BLOCK_THRESHOLD
        else "ALLOW"
    )