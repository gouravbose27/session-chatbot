---
name: fastapi-backend
description: Use when building, extending or fixing anything in backend/ - FastAPI endpoints, Pydantic request/response models, JSON file storage, settings from .env, LLM calls through llm_client.ask_llm, error handling, CORS and pytest tests. Read the spec in specs/ before writing code.
---

# FastAPI backend skill

Before anything else, start your reply with one line: `🧩 Using skill: fastapi-backend`
so the developer can see this skill is active.

The people reading this code are Python beginners. Clarity beats cleverness.

## Before writing code
1. Read the spec in `specs/` completely. It is the source of truth. Build exactly the endpoints
   it lists: same method, path, inputs, outputs and error codes.
2. If something is unclear, pick the simplest option and note it in `docs/DECISIONS.md`.
3. `backend/llm_client.py` is given. Use `ask_llm()` and `MODEL`. Never edit `ask_llm()`.

## Layout
```
backend/
├── main.py          ← FastAPI app: endpoints only, kept thin
├── models.py        ← Pydantic request and response models
├── services.py      ← the logic
├── settings.py      ← reads .env once (python-dotenv), exposes plain constants
├── llm_client.py    ← given, do not change
├── *.json           ← prompts and config files the spec names
├── data/            ← runtime data, created at start-up, git-ignored
└── tests/test_api.py
```

## Rules
- One short function per endpoint: validate, call `services.py`, return. `response_model=` on every route.
- Every body and response is a Pydantic model with `Field(...)` limits that match the spec.
- `GET /health` returns `{"status": "ok"}`.
- Errors use `HTTPException` with a human message: 404 unknown id, 409 not allowed now,
  422 bad input (automatic from Pydantic), 502 when the LLM call fails (include the provider's message).
- Every LLM call goes through `ask_llm(prompt, model=MODEL, system=...)`. Never import openai or
  anthropic anywhere else. Return input_tokens, output_tokens, seconds and cost to the caller.
- Prompt text lives in a JSON file, never in Python. Fill `{variables}` with `str.format()`.
- Config that a non-developer may change (limits, rules, phrases) lives in a JSON file whose
  path comes from `.env`, with GET and PUT endpoints to read and change it.
- CORS: allow only the origin in `FRONTEND_ORIGIN` from `.env`.
- JSON files are written whole with `indent=2`, via a temp file + rename. New ids: `uuid.uuid4().hex[:8]`.
- Never print, log or return API keys.

## Style
Small functions with one-line docstrings, type hints, plain loops and ifs, descriptive names,
comments that explain why.

## Tests
- `backend/tests/test_api.py` with FastAPI's `TestClient`.
- Replace `ask_llm` with a fake (pytest `monkeypatch`): tests never call a real model or cost money.
- Point every data/config file at `tmp_path`.
- At least one test per endpoint and per error code, plus one per acceptance test in the spec.
- Run with `.venv/bin/python -m pytest -q` from `backend/` (see the python-venv skill). All must pass.

## Done means
- [ ] Every endpoint in the spec exists with the right models and errors
- [ ] No prompt text or keys in Python files; `llm_client.py` unchanged
- [ ] All tests pass with the fake LLM
- [ ] You told the developer: `uvicorn main:app --reload` from `backend/`, Swagger at `/docs`