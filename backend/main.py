"""FastAPI app: endpoints only. The logic lives in services.py."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import guardrails
import services
import settings
from models import (
    ChatRequest,
    ChatResponse,
    DeleteResponse,
    GuardrailConfig,
    HealthResponse,
    SessionCreated,
    SessionHistory,
)

app = FastAPI(title="Session chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Check that the server is running."""
    return HealthResponse(status="ok")


@app.post("/sessions", response_model=SessionCreated)
def create_session() -> SessionCreated:
    """Start a new chat session."""
    return SessionCreated(session_id=services.create_session())


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Send a message in a session and get the reply."""
    return ChatResponse(**services.chat(request.session_id, request.message))


@app.get("/sessions/{session_id}", response_model=SessionHistory)
def get_session(session_id: str) -> SessionHistory:
    """Return the messages of a session so far."""
    messages = services.get_session(session_id)
    return SessionHistory(session_id=session_id, messages=messages)


@app.delete("/sessions/{session_id}", response_model=DeleteResponse)
def delete_session(session_id: str) -> DeleteResponse:
    """Delete a session and its messages."""
    services.delete_session(session_id)
    return DeleteResponse(deleted=True)


@app.get("/guardrails", response_model=GuardrailConfig)
def get_guardrails() -> GuardrailConfig:
    """Return the guardrail settings."""
    return GuardrailConfig(**guardrails.load_config())


@app.put("/guardrails", response_model=GuardrailConfig)
def put_guardrails(config: GuardrailConfig) -> GuardrailConfig:
    """Replace the guardrail settings and save them to the file."""
    guardrails.save_config(config.model_dump())
    return config
