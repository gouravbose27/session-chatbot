"""The logic: in-memory sessions, prompt building and the LLM call."""
import json
import uuid

from fastapi import HTTPException

import guardrails
import settings
from llm_client import ask_llm

# session_id -> messages, oldest first. Lost when the server stops (the spec says memory only).
sessions: dict[str, list[dict]] = {}


def create_session() -> str:
    """Make a new empty session and return its id."""
    session_id = uuid.uuid4().hex[:8]
    sessions[session_id] = []
    return session_id


def get_session(session_id: str) -> list[dict]:
    """Return the messages of a session, or raise 404 if it is unknown."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Unknown session id")
    return sessions[session_id]


def delete_session(session_id: str) -> None:
    """Remove a session, or raise 404 if it is unknown."""
    get_session(session_id)
    del sessions[session_id]


def load_system_prompt() -> str:
    """Read the chat-assistant system prompt from the prompts file."""
    with open(settings.PROMPTS_FILE, encoding="utf-8") as prompts_file:
        return json.load(prompts_file)["chat-assistant"]


def build_prompt(history: list[dict], message: str) -> str:
    """Put the earlier turns and the new message into one prompt."""
    lines = ["Conversation so far:"]
    if not history:
        lines.append("(none yet)")
    for msg in history:
        label = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{label}: {msg['content']}")
    lines.append("")
    lines.append("New message from the user:")
    lines.append(message)
    return "\n".join(lines)


def chat(session_id: str, message: str) -> dict:
    """Answer one message, remember the turn, and return the reply with its metrics."""
    history = get_session(session_id)
    config = guardrails.load_config()

    try:
        allowed, clean_message, input_reason = guardrails.check_input(message, config)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Topic check failed: {error}")
    if not allowed:
        # Blocked input never reaches the model and is not saved.
        return blocked_reply(config, input_reason, len(history) // 2)

    # One turn is a user message plus an assistant message, so keep 2 items per turn.
    max_messages = 2 * settings.MAX_HISTORY_TURNS
    recent = history[-max_messages:] if max_messages else []
    prompt = build_prompt(recent, clean_message)
    system = load_system_prompt()

    try:
        result = ask_llm(prompt, model=settings.MODEL, system=system)
    except Exception as error:
        # Nothing is saved when the model call fails, so the user can retry.
        raise HTTPException(status_code=502, detail=f"LLM call failed: {error}")

    output_allowed, _, output_reason = guardrails.check_output(result["text"], config)
    if not output_allowed:
        # Blocked replies are not saved either.
        return {
            **blocked_reply(config, output_reason, len(history) // 2),
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "seconds": result["seconds"],
            "cost": result["cost"],
        }

    history.append({"role": "user", "content": clean_message})
    history.append({"role": "assistant", "content": result["text"]})

    return {
        "reply": result["text"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "seconds": result["seconds"],
        "cost": result["cost"],
        "turns_in_memory": len(history) // 2,
        "guardrail": input_reason,
    }


def blocked_reply(config: dict, reason: str | None, turns_in_memory: int) -> dict:
    """Build the friendly reply for a blocked message, with no tokens used."""
    return {
        "reply": config["blocked_message"],
        "input_tokens": 0,
        "output_tokens": 0,
        "seconds": 0.0,
        "cost": None,
        "turns_in_memory": turns_in_memory,
        "guardrail": reason,
    }
