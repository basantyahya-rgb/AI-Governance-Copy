"""Optional NeMo Guardrails integration.

NeMo is a secondary security signal.
Deterministic governance remains authoritative.
"""

import os
from functools import lru_cache

from nemoguardrails import (
    LLMRails,
    RailsConfig,
)


CONFIG_PATH = os.getenv(
    "NEMO_CONFIG_PATH",
    "config/guardrails",
)


@lru_cache(maxsize=1)
def _get_rails():

    config = RailsConfig.from_path(
        CONFIG_PATH
    )

    return LLMRails(config)


def check_prompt(prompt: str) -> dict:

    rails = _get_rails()

    # Preferred API.

    if hasattr(
        rails,
        "check",
    ):

        result = rails.check(

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        return {

            "flagged": bool(result),

            "result": result,
        }

    return {

        "flagged": False,

        "result": None,

        "message": (
            "NeMo check() is unavailable "
            "in this installation."
        ),
    }