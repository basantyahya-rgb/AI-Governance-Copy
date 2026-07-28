
from datasets import load_dataset
from datetime import datetime
import time
import uuid
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Governance Modules
from app.governance.prompt_filter import filter_prompt
from app.governance.injection_detector import detect_prompt_injection
from app.governance.pii_detector import detect_pii
from app.governance.risk_engine import calculate_risk
from app.governance.decision_engine import make_decision
from app.services.qwen_service import ask_qwen
# NeMo Guardrails
from app.services.nemo_service import check_prompt

from dotenv import load_dotenv
load_dotenv()

nemo_result = {
    "available": False,
    "flagged": False,
    "response": None,
    "error": None,
    "message": None,
}

app = FastAPI(
    title="AI Governance Platform",
    description="Enterprise AI Governance Platform for Prompt Validation and Risk Assessment",
    version="1.0.0",
)

GOVERNANCE_VERSION = "1.0"


class PromptRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User prompt",
    )


@app.get("/")
def root():
    return {
        "application": "AI Governance Platform",
        "version": "1.0.0",
        "status": "Running",
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/validate")
def validate_prompt(request: PromptRequest):

    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    try:

        prompt = request.prompt

        # Step 1
        allowed, filter_reason, filter_category = filter_prompt(prompt)

        # Step 2
        injection = detect_prompt_injection(prompt)

        injection_detected = injection["detected"]

        # Step 3
        pii_findings = detect_pii(prompt)

        # Step 4
        # Step 4 - NeMo Guardrails

        nemo_result = {
            "available": False,
            "flagged": False,
            "response": None,
            "error": None,
            "message": None,
        }

        # Only skip if the prompt was already blocked by the Prompt Filter
        if not allowed:

            nemo_result["message"] = (
                "Skipped because Prompt Filter blocked the prompt."
            )

        else:

            try:
                nemo_output = check_prompt(prompt)

                nemo_result = {
                    "available": True,
                    "flagged": nemo_output.get("flagged", False),
                    "response": nemo_output,
                    "error": None,
                    "message": "Executed successfully",
                }

            except Exception as e:

                nemo_result = {
                    "available": False,
                    "flagged": False,
                    "response": None,
                    "error": str(e),
                    "message": "NeMo execution failed",
                }
                        
                        
    # Step 5

                
        risk = calculate_risk(

        prompt_filter={
            "allowed": allowed,
            "category": filter_category,
            "reason": filter_reason,
        },

        injection=injection,

        pii_findings=pii_findings,

        nemo=nemo_result,

    )
        
        risk_score = risk["score"]
        risk_level = risk["level"]
        reasons = risk["reasons"]

        # Step 6
        decision = make_decision(risk["score"])
        processing_time = round(
    (time.perf_counter() - start_time) * 1000,
    2,
)

        if (decision == "ALLOW" and allowed and not injection_detected and len(pii_findings) == 0 and not nemo_result["flagged"]):
            try:
                llm_response = ask_qwen(prompt)
            except Exception as e:
                llm_response = f"Qwen Error: {e}"
        else:
            llm_response = None

        

        return {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "governance_version": GOVERNANCE_VERSION,
            "decision": decision,
            "risk": {
                "score": risk_score,
                "level": risk_level,
                "reasons": reasons,
                "breakdown": risk["breakdown"]
            },
            "governance": {
              "prompt_filter": {
                "allowed": allowed,
                "reason": filter_reason,
                "category": filter_category
                     },
                "prompt_injection": injection,
                "pii_detection": {
                    "count": len(pii_findings),
                    "findings": pii_findings,
                },
                "nemo_guardrails": nemo_result,
            
            },
            "audit": {
                "engine": "AI Governance Platform",
                "version": "1.0.0",
                "processing_time_ms": processing_time,
            },

            "llm": {

    "model": "qwen3:8b",

    "response": llm_response

},
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "message": "Validation Error",
                "error": str(e),
            },
        )



