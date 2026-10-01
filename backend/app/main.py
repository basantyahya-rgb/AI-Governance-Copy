"""FastAPI entry point for the AI Governance Platform."""

import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)


from app.governance.injection_detector import (
    detect_prompt_injection,
)

from app.governance.pii_detector import (
    detect_pii,
)

from app.governance.prompt_filter import (
    filter_prompt,
)

from app.governance.risk_engine import (
    calculate_risk,
)

from app.services.nemo_service import (
    check_prompt,
)

from app.services.qwen_service import (
    ask_qwen,
)


load_dotenv()


GOVERNANCE_VERSION = "2.0"


app = FastAPI(

    title="AI Governance Platform",

    description=(
        "Enterprise AI Governance Platform "
        "for Prompt Validation and Risk Assessment"
    ),

    version="2.0.0",
)


class PromptRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


@app.get("/")
def root():

    return {

        "application":
            "AI Governance Platform",

        "version":
            "2.0.0",

        "status":
            "Running",

        "decision_policy": [
            "ALLOW",
            "BLOCK",
        ],
    }


@app.get("/health")
def health():

    return {

        "status":
            "Healthy",

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


@app.post("/validate")
def validate_prompt(
    request: PromptRequest
):

    started = time.perf_counter()

    request_id = str(
        uuid.uuid4()
    )

    try:

        prompt = request.prompt

        # =================================================
        # 1. Prompt Security Filter
        # =================================================

        (
            allowed,
            filter_reason,
            filter_category,
        ) = filter_prompt(
            prompt
        )

        # =================================================
        # 2. Prompt Injection
        # =================================================

        injection = (
            detect_prompt_injection(
                prompt
            )
        )

        # =================================================
        # 3. PII / Secrets
        # =================================================

        pii_findings = detect_pii(
            prompt
        )

        # =================================================
        # 4. NeMo Secondary Layer
        # =================================================

        nemo_result = {

            "available": False,

            "flagged": False,

            "response": None,

            "error": None,

            "message": None,
        }

        # Don't waste local compute if the prompt
        # is already deterministically blocked.

        if (
            not allowed
            or injection.get("detected")
        ):

            nemo_result["message"] = (
                "Skipped because a "
                "deterministic security control "
                "already blocked the prompt."
            )

        else:

            try:

                nemo_result = {

                    "available": True,

                    **check_prompt(
                        prompt
                    ),

                    "error": None,

                    "message":
                        "Executed successfully",
                }

            except Exception as exc:

                nemo_result = {

                    "available": False,

                    "flagged": False,

                    "response": None,

                    "error": str(exc),

                    "message": (
                        "NeMo execution failed; "
                        "deterministic controls "
                        "remain authoritative."
                    ),
                }

        # =================================================
        # 5. Unified Risk Engine
        # =================================================

        risk = calculate_risk(

            prompt_filter={

                "allowed":
                    allowed,

                "category":
                    filter_category,

                "reason":
                    filter_reason,
            },

            injection=
                injection,

            pii_findings=
                pii_findings,

            nemo=
                nemo_result,
        )

        # =================================================
        # 6. FINAL DECISION
        # =================================================

        decision = risk["action"]

        # Absolute API guarantee:
        # only ALLOW / BLOCK can leave this endpoint.

        if decision not in {
            "ALLOW",
            "BLOCK",
        }:

            decision = "BLOCK"

        # =================================================
        # 7. Qwen
        # =================================================

        llm_response = None

        output_findings = []

        if decision == "ALLOW":

            try:

                llm_response = ask_qwen(
                    prompt
                )

                # =================================================
                # Output Security Guard
                # =================================================

                output_findings = detect_pii(
                    llm_response or ""
                )

                if output_findings:

                    llm_response = (
                        "Response blocked by "
                        "output security policy."
                    )

                    decision = "BLOCK"

                    risk["reasons"].append(
                        "Output security guard "
                        "detected sensitive content."
                    )

            except Exception as exc:

                llm_response = None

                risk["reasons"].append(
                    f"LLM unavailable: {exc}"
                )

        # =================================================
        # 8. Processing Time
        # =================================================

        processing_time = round(

            (
                time.perf_counter()
                - started
            )
            * 1000,

            2,
        )

        # =================================================
        # 9. Response
        # =================================================

        return {

            "request_id":
                request_id,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "governance_version":
                GOVERNANCE_VERSION,

            "decision":
                decision,

            "risk": {

                "score":
                    risk["score"],

                "level":
                    risk["level"],

                "reasons":
                    risk["reasons"],

                "breakdown":
                    risk["breakdown"],
            },

            "governance": {

                "prompt_filter": {

                    "allowed":
                        allowed,

                    "reason":
                        filter_reason,

                    "category":
                        filter_category,
                },

                "prompt_injection":
                    injection,

                "pii_detection": {

                    "count":
                        len(pii_findings),

                    "findings":
                        pii_findings,
                },

                "nemo_guardrails":
                    nemo_result,

                "output_guard": {

                    "blocked":
                        bool(output_findings),

                    "findings_count":
                        len(output_findings),
                },
            },

            "audit": {

                "engine":
                    "AI Governance Platform",

                "version":
                    "2.0.0",

                "processing_time_ms":
                    processing_time,
            },

            "llm": {

                "model":
                    "qwen3:8b",

                "response":
                    llm_response,
            },
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail={

                "request_id":
                    request_id,

                "message":
                    "Validation Error",

                "error":
                    str(exc),
            },

        ) from exc