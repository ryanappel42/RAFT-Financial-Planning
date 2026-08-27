"""
FastAPI backend for the financial planning platform.

Wraps the existing tool-use loop (api/client.py) behind HTTP endpoints,
manages conversation state per session, and provides a lightweight access
gate since this will be deployed publicly and calls the Anthropic API.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.client import chat
from backend.mock_clients import list_clients, get_client_context

app = FastAPI(title="Financial Planning Platform API")

# Allow the frontend to call this API. Set ALLOWED_ORIGIN in Railway once the
# frontend has a real URL (e.g. https://your-frontend.up.railway.app) to lock
# this down; "*" is fine for local development only.
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCESS_CODE = os.environ.get("ACCESS_CODE")  # set in Railway env vars; None disables the gate locally

# In-memory session store: session_id -> message history.
# Fine for a portfolio demo; a real deployment would use a database or Redis,
# since this resets on every server restart/redeploy and doesn't scale across instances.
SESSIONS: dict = {}


def check_access(x_access_code: str | None):
    if ACCESS_CODE and x_access_code != ACCESS_CODE:
        raise HTTPException(status_code=401, detail="Invalid or missing access code")


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    mode: str = "consumer"       # "consumer" or "advisor"
    client_id: str | None = None  # required for advisor mode


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tool_calls: list = []  # [{"tool_name": str, "result": dict}, ...] for this turn, used to render visuals


def _extract_text(content) -> str:
    """Pulls the plain-text portion out of a Claude response's content blocks."""
    return "".join(block.text for block in content if getattr(block, "type", None) == "text")


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/clients")
def get_clients(x_access_code: str | None = Header(default=None)):
    """Lists mock clients for the advisor-mode client picker."""
    check_access(x_access_code)
    return list_clients()


@app.post("/chat", response_model=ChatResponse)
def post_chat(req: ChatRequest, x_access_code: str | None = Header(default=None)):
    check_access(x_access_code)

    if req.mode == "advisor" and not req.client_id:
        raise HTTPException(status_code=400, detail="client_id is required in advisor mode")

    session_id = req.session_id or str(uuid.uuid4())
    messages = SESSIONS.get(session_id, [])
    messages.append({"role": "user", "content": req.message})

    client_context = get_client_context(req.client_id) if req.mode == "advisor" else None

    try:
        updated_messages, tool_calls = chat(messages, mode=req.mode, client_context=client_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Claude: {e}")

    SESSIONS[session_id] = updated_messages

    last_assistant_message = next(
        (m for m in reversed(updated_messages) if m["role"] == "assistant"), None
    )
    reply = _extract_text(last_assistant_message["content"]) if last_assistant_message else ""

    return ChatResponse(session_id=session_id, reply=reply, tool_calls=tool_calls)
