# main.py
# QueueStorm Ticket Classifier — FastAPI Application
# SUST CSE Carnival 2026 | Codex Community Hackathon
#
# Endpoints:
#   GET  /health       → Service health check
#   POST /sort-ticket  → Classify a customer support ticket
# ─────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from classifier import classify_ticket

# ══════════════════════════════════════════════════════
# APP INITIALIZATION
# ══════════════════════════════════════════════════════

app = FastAPI(
    title="QueueStorm — Ticket Classifier API",
    description=(
        "Classifies bKash customer support tickets by case type, "
        "severity, and routing department. "
        "Built for SUST CSE Carnival 2026 — Codex Community Hackathon."
    ),
    version="1.0.0",
)


# ══════════════════════════════════════════════════════
# REQUEST MODEL
# ══════════════════════════════════════════════════════

class TicketRequest(BaseModel):
    ticket_id: str = Field(
        ...,
        description="Unique ticket identifier. Will be echoed back in the response.",
        example="T-001"
    )
    channel: Optional[str] = Field(
        None,
        description="Source channel of the message.",
        example="app"
    )
    locale: Optional[str] = Field(
        None,
        description="Language locale of the message.",
        example="en"
    )
    message: str = Field(
        ...,
        description="Free-text customer complaint message.",
        example="I sent 5000 taka to a wrong number this morning, please help me get it back"
    )


# ══════════════════════════════════════════════════════
# RESPONSE MODEL
# ══════════════════════════════════════════════════════

class TicketResponse(BaseModel):
    ticket_id: str = Field(..., description="Echoed from the request.")
    case_type: str = Field(..., description="Classified type of issue.")
    severity: str = Field(..., description="Severity level: low, medium, high, or critical.")
    department: str = Field(..., description="Department to route this ticket to.")
    agent_summary: str = Field(..., description="One or two neutral sentences for the agent.")
    human_review_required: bool = Field(..., description="True for critical or phishing cases.")
    confidence: float = Field(..., description="Classification confidence between 0.0 and 1.0.")


# ══════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════

@app.get(
    "/health",
    summary="Health Check",
    description="Returns the current health status of the service. Must respond within 10 seconds.",
    tags=["Health"]
)
def health_check():
    """
    Simple health check endpoint.
    Returns: { "status": "ok" }
    """
    return {"status": "ok"}


@app.post(
    "/sort-ticket",
    response_model=TicketResponse,
    summary="Classify a Ticket",
    description="Accepts one CRM ticket and returns a structured classification result.",
    tags=["Classification"]
)
def sort_ticket(ticket: TicketRequest):
    """
    Classifies a customer support ticket.

    - Echoes back the ticket_id exactly as received.
    - Determines case_type, severity, department.
    - Generates a safe, neutral agent_summary (never asks for PIN/OTP/password).
    - Sets human_review_required=True for critical or phishing cases.
    - Must respond within 30 seconds.
    """

    # Validate that message is not blank
    if not ticket.message or not ticket.message.strip():
        raise HTTPException(
            status_code=422,
            detail="The 'message' field must not be empty."
        )

    # Run classification
    result = classify_ticket(ticket.message)

    # Build and return the response
    return TicketResponse(
        ticket_id=ticket.ticket_id,  # ← Always echo back exactly!
        case_type=result["case_type"],
        severity=result["severity"],
        department=result["department"],
        agent_summary=result["agent_summary"],
        human_review_required=result["human_review_required"],
        confidence=result["confidence"],
    )
