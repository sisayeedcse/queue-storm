# QueueStorm — Ticket Classifier API

> **SUST CSE Carnival 2026 | Codex Community Hackathon | Mock Preliminary Round**
> Organized by SUST CSE Society | Hackathon Sponsor: Poridhi.io | Title Sponsor: bKash

---

## What This Does

**QueueStorm** is a lightweight REST API that classifies customer support tickets for a digital finance platform (bKash).

Given a free-text customer complaint, the service instantly answers:

| Question | Answer |
|----------|--------|
| What kind of problem? | `wrong_transfer`, `payment_failed`, `refund_request`, `phishing_or_social_engineering`, `other` |
| How serious? | `low`, `medium`, `high`, `critical` |
| Which team handles it? | `customer_support`, `dispute_resolution`, `payments_ops`, `fraud_risk` |
| One-line summary? | A neutral sentence for the agent to read in 2 seconds |

It also raises a `human_review_required` flag automatically for phishing and critical cases.

---

## Architecture

```
POST /sort-ticket
      │
      ▼
 TicketRequest (Pydantic validation)
      │
      ▼
 classify_ticket()   ← keyword-based engine (classifier.py)
      │
      ▼
 TicketResponse (JSON)
```

**Stack:** Python 3.11 · FastAPI · Uvicorn · Pydantic · Docker

**Classification method:** Rule-based keyword matching — no GPU, no LLM required.

---

## Project Structure

```
queue-storm/
├── main.py            ← FastAPI app (routes & models)
├── classifier.py      ← Keyword-based classification engine
├── requirements.txt   ← Python dependencies
├── Dockerfile         ← Container build instructions
├── .gitignore         ← Excludes secrets & cache
└── README.md          ← This file
```

---

## Local Setup (Without Docker)

### Prerequisites
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sisayeedcse/queue-storm.git
cd queue-storm

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000

# 5. Test it
curl http://localhost:8000/health
```

---

## Local Setup (With Docker)

### Prerequisites
- Docker Desktop installed and running

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sisayeedcse/queue-storm.git
cd queue-storm

# 2. Build the Docker image
docker build -t queue-storm .

# 3. Run the container
docker run -d -p 8000:8000 queue-storm

# 4. Test it
curl http://localhost:8000/health
```

---

## Environment Variables

This project currently requires **no environment variables** to run.

If you add an LLM API key in a future version, create a `.env` file (never commit it):

```bash
# .env  ← this file is in .gitignore
OPENAI_API_KEY=your_key_here
```

---

## API Reference

### `GET /health`

Returns the current health status of the service.

**Response:**
```json
{
  "status": "ok"
}
```

---

### `POST /sort-ticket`

Classifies a customer support ticket.

**Request body:**

```json
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number this morning, please help me get it back"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ticket_id` | string | ✅ Yes | Echoed back in the response |
| `channel` | string | Optional | `app`, `sms`, `call_center`, `merchant_portal` |
| `locale` | string | Optional | `bn`, `en`, `mixed` |
| `message` | string | ✅ Yes | Free-text customer complaint |

**Response:**

```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending funds to an unintended recipient and is requesting assistance to recover the transferred amount.",
  "human_review_required": true,
  "confidence": 0.90
}
```

| Field | Type | Notes |
|-------|------|-------|
| `ticket_id` | string | Always matches the request `ticket_id` |
| `case_type` | enum | Classification result |
| `severity` | enum | `low`, `medium`, `high`, `critical` |
| `department` | enum | Routing destination |
| `agent_summary` | string | Neutral one or two sentence summary |
| `human_review_required` | boolean | `true` for `critical` or `phishing` cases |
| `confidence` | float | Between `0.0` and `1.0` |

**Interactive API Docs:** Available at `/docs` on any running instance (Swagger UI).

---

## Public Test Cases

| # | Message | Expected `case_type` | Severity |
|---|---------|---------------------|----------|
| 1 | I sent 3000 to wrong number | `wrong_transfer` | `high` |
| 2 | Payment failed but balance deducted | `payment_failed` | `high` |
| 3 | Someone called asking my OTP, is that bKash? | `phishing_or_social_engineering` | `critical` |
| 4 | Please refund my last transaction, I changed my mind | `refund_request` | `low` |
| 5 | App crashed when I opened it | `other` | `low` |

---

## Deployment Guide (Render.com)

This app is deployed on **Render** — a free cloud platform that provides HTTPS automatically.

### Steps to Redeploy

1. **Fork or clone** this repository to your GitHub account (must be Public).

2. **Go to [render.com](https://render.com)** → Sign in with GitHub.

3. Click **New +** → **Web Service** → Connect this repository.

4. Configure the service:

   | Setting | Value |
   |---------|-------|
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | `Free` |

5. Click **Create Web Service** and wait ~3–5 minutes.

6. Render provides a free HTTPS URL automatically — no manual SSL setup needed.

### Credentials
No cloud credentials are required for this deployment. No secrets are stored in this repository.

---

## Live Deployment

| Resource | URL |
|----------|-----|
| 🌐 Live API | *(to be added after deployment)* |
| 📁 GitHub Repo | https://github.com/sisayeedcse/queue-storm |
| 📋 Swagger Docs | `<live-url>/docs` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: fastapi` | Run `pip install -r requirements.txt` |
| Port already in use | Change port: `uvicorn main:app --port 8001` |
| Render deploy times out | Free instances sleep after 15 min — first request wakes it up, wait ~30s |
| `422 Unprocessable Entity` | Check your JSON body — `ticket_id` and `message` are required |
| Wrong `ticket_id` in response | This should not happen — open an issue on GitHub |

---

## Classification Rules (How It Works)

The classifier uses priority-ordered keyword matching:

| Priority | Case Type | Trigger Keywords (examples) |
|----------|-----------|-----------------------------|
| 1st | `phishing_or_social_engineering` | otp, pin, password, someone called, asked for my |
| 2nd | `wrong_transfer` | wrong number, sent to wrong, wrong account |
| 3rd | `payment_failed` | payment failed, balance deducted, failed but |
| 4th | `refund_request` | refund, cancel, changed my mind, money back |
| 5th | `other` | everything else |

**Safety rule enforced:** The `agent_summary` field never asks the customer to share any PIN, OTP, password, or card number.

---

## LLM Usage

**No LLM was used.** Classification is entirely rule-based keyword matching.

---

*Built for SUST CSE Carnival 2026 — Codex Community Hackathon Mock Preliminary Round.*
