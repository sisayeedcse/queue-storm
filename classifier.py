# classifier.py
# QueueStorm Ticket Classifier — Classification Engine
# SUST CSE Carnival 2026 | Codex Community Hackathon
#
# Rule-based keyword classification.
# No GPU, no LLM, no heavy dependencies required.
# ─────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════
# KEYWORD DICTIONARIES
# Each list covers common phrasings a real customer might type.
# ══════════════════════════════════════════════════════

PHISHING_KEYWORDS = [
    "otp", "pin", "password", "account number", "card number",
    "someone called", "called asking", "sms asking", "called me",
    "asking for my", "asked for my", "share your", "send your otp",
    "confirm your pin", "verify your", "fake bkash", "fake agent",
    "scam", "fraud call", "suspicious call", "suspicious sms",
    "they asked", "he asked", "she asked", "told me to share",
    "told me to send", "phishing", "social engineering"
]

WRONG_TRANSFER_KEYWORDS = [
    "wrong number", "wrong person", "sent to wrong", "wrong account",
    "mistaken transfer", "wrong recipient", "transferred to wrong",
    "wrong bkash", "sent by mistake", "accidentally sent",
    "sent to the wrong", "send to wrong", "wrong mobile",
    "wrong destination", "by mistake sent", "wrong name"
]

PAYMENT_FAILED_KEYWORDS = [
    "payment failed", "transaction failed", "balance deducted",
    "not received", "money deducted", "deducted but", "failed but",
    "unsuccessful payment", "could not complete", "did not go through",
    "payment did not", "transfer failed", "failed payment",
    "charge but", "debited but", "deducted without", "failed transaction",
    "deducted and not"
]

REFUND_KEYWORDS = [
    "refund", "return my money", "cancel", "changed my mind",
    "want my money back", "reverse the transaction", "money back",
    "undo", "revert", "get my money back", "send it back",
    "please return", "please reverse", "i want back",
    "take it back", "i dont want"
]


# ══════════════════════════════════════════════════════
# MAIN CLASSIFIER FUNCTION
# ══════════════════════════════════════════════════════

def classify_ticket(message: str) -> dict:
    """
    Classifies a customer support ticket using keyword matching.

    Priority order (most critical first):
        1. Phishing / Social Engineering  → critical
        2. Wrong Transfer                 → high
        3. Payment Failed                 → high
        4. Refund Request                 → low
        5. Other (catch-all)              → low

    Parameters:
        message (str): Raw free-text customer complaint.

    Returns:
        dict: Classification result containing:
            - case_type (str)
            - severity (str)
            - department (str)
            - agent_summary (str)
            - human_review_required (bool)
            - confidence (float)
    """

    msg = message.lower()

    # ── PRIORITY 1: PHISHING / SOCIAL ENGINEERING ──────────────
    if any(kw in msg for kw in PHISHING_KEYWORDS):
        return {
            "case_type": "phishing_or_social_engineering",
            "severity": "critical",
            "department": "fraud_risk",
            "agent_summary": (
                "Customer has reported a suspicious contact or activity "
                "that may indicate a phishing or social engineering attempt. "
                "Immediate escalation to the fraud risk team is required."
            ),
            "human_review_required": True,
            "confidence": 0.93,
        }

    # ── PRIORITY 2: WRONG TRANSFER ─────────────────────────────
    if any(kw in msg for kw in WRONG_TRANSFER_KEYWORDS):
        return {
            "case_type": "wrong_transfer",
            "severity": "high",
            "department": "dispute_resolution",
            "agent_summary": (
                "Customer reports sending funds to an unintended recipient "
                "and is requesting assistance to recover the transferred amount."
            ),
            "human_review_required": True,
            "confidence": 0.90,
        }

    # ── PRIORITY 3: PAYMENT FAILED ─────────────────────────────
    if any(kw in msg for kw in PAYMENT_FAILED_KEYWORDS):
        return {
            "case_type": "payment_failed",
            "severity": "high",
            "department": "payments_ops",
            "agent_summary": (
                "Customer reports a failed or incomplete transaction "
                "where the account balance may have been deducted without successful completion."
            ),
            "human_review_required": False,
            "confidence": 0.87,
        }

    # ── PRIORITY 4: REFUND REQUEST ─────────────────────────────
    if any(kw in msg for kw in REFUND_KEYWORDS):
        return {
            "case_type": "refund_request",
            "severity": "low",
            "department": "customer_support",
            "agent_summary": (
                "Customer is requesting a refund or reversal "
                "for a recent transaction."
            ),
            "human_review_required": False,
            "confidence": 0.82,
        }

    # ── PRIORITY 5: OTHER (catch-all) ──────────────────────────
    return {
        "case_type": "other",
        "severity": "low",
        "department": "customer_support",
        "agent_summary": (
            "Customer has submitted a general inquiry or reported "
            "a miscellaneous issue that does not match standard categories."
        ),
        "human_review_required": False,
        "confidence": 0.70,
    }
