import os
import json
import uuid
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path

import pip_system_certs
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from agent_runner import run_agent_stream

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="Log Inspector API")

# Allow both local dev and production Vercel origins
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
# Add production frontend URL from env if set
frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_HISTORY_DIR = Path(__file__).resolve().parent.parent / "user_history"
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

for d in [USER_HISTORY_DIR, UPLOAD_DIR, OUTPUT_DIR]:
    d.mkdir(exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_users_file() -> Path:
    return USER_HISTORY_DIR / "users.json"


def load_users() -> dict:
    f = get_users_file()
    if f.exists():
        return json.loads(f.read_text())
    return {}


def save_users(users: dict):
    get_users_file().write_text(json.dumps(users, indent=2))


def log_login(username: str, success: bool):
    history_file = USER_HISTORY_DIR / f"{username}_history.json"
    history = []
    if history_file.exists():
        history = json.loads(history_file.read_text())
    history.append({
        "timestamp": datetime.now().isoformat(),
        "action": "login",
        "success": success,
    })
    history_file.write_text(json.dumps(history, indent=2))


# ── Auth Models ───────────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ── Auth Endpoints ────────────────────────────────────────────────────────────
@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    users = load_users()
    if req.email in users:
        raise HTTPException(400, "Email already registered")
    users[req.email] = {
        "name": req.name,
        "password": hash_password(req.password),
        "created_at": datetime.now().isoformat(),
    }
    save_users(users)
    log_login(req.email, True)
    return {"message": "Account created", "email": req.email, "name": req.name}


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    users = load_users()
    if req.email not in users:
        raise HTTPException(401, "Invalid credentials")
    if users[req.email]["password"] != hash_password(req.password):
        log_login(req.email, False)
        raise HTTPException(401, "Invalid credentials")
    log_login(req.email, True)
    return {"message": "Login successful", "email": req.email, "name": users[req.email].get("name", "")}


# ── File Upload ───────────────────────────────────────────────────────────────
@app.post("/api/upload/logs")
async def upload_logs(file: UploadFile = File(...)):
    filename = f"logs_{uuid.uuid4().hex[:8]}_{file.filename}"
    filepath = UPLOAD_DIR / filename
    content = await file.read()
    filepath.write_bytes(content)
    return {"filename": filename, "path": str(filepath)}


@app.post("/api/upload/docs")
async def upload_docs(file: UploadFile = File(...)):
    filename = f"docs_{uuid.uuid4().hex[:8]}_{file.filename}"
    filepath = UPLOAD_DIR / filename
    content = await file.read()
    filepath.write_bytes(content)
    return {"filename": filename, "path": str(filepath)}


# ── Agent Analysis (SSE streaming) ───────────────────────────────────────────
@app.get("/api/analyze")
async def analyze(logs_path: str, email: str = "", docs_path: str = None):
    async def event_stream():
        try:
            async for event in run_agent_stream(logs_path, docs_path):
                # Normalize: agent_runner uses 'content', frontend expects 'message'
                normalized = {
                    "type": event.get("type", "status"),
                    "message": event.get("content", event.get("message", "")),
                }
                if event.get("type") == "complete":
                    normalized["report"] = event.get("content", "")
                yield f"data: {json.dumps(normalized)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Report Download ──────────────────────────────────────────────────────────
@app.get("/api/report/download")
async def download_report():
    report_path = OUTPUT_DIR / "incident_report.txt"
    if not report_path.exists():
        raise HTTPException(404, "Report not yet generated")
    return FileResponse(
        report_path,
        media_type="text/plain",
        filename="incident_report.txt",
    )


@app.get("/api/report/content")
async def get_report_content():
    report_path = OUTPUT_DIR / "incident_report.txt"
    if not report_path.exists():
        raise HTTPException(404, "Report not yet generated")
    return {"content": report_path.read_text(encoding="utf-8")}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
