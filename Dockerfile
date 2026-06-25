# ─────────────────────────────────────────────────────
# Dockerfile — QueueStorm Ticket Classifier
# SUST CSE Carnival 2026 | Codex Community Hackathon
#
# Build:  docker build -t queue-storm .
# Run:    docker run -d -p 8000:8000 queue-storm
# ─────────────────────────────────────────────────────

# ── Base Image ────────────────────────────────────────
# Python 3.11 slim = lightweight, no unnecessary packages
FROM python:3.11-slim

# ── Working Directory ─────────────────────────────────
# All files live inside /app inside the container
WORKDIR /app

# ── Install Dependencies ──────────────────────────────
# Copy requirements FIRST (before source code) so Docker
# can cache this layer — speeds up rebuilds when only
# source code changes, not dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Source Code ──────────────────────────────────
# Copy the rest of the project files into the container
COPY . .

# ── Expose Port ───────────────────────────────────────
# Tells Docker that the container listens on port 8000
EXPOSE 8000

# ── Start Command ─────────────────────────────────────
# Starts the FastAPI app with Uvicorn
# --host 0.0.0.0 makes it accessible outside the container
# --port 8000 matches the exposed port above
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
