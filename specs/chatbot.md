# Chatbot spec

## Goal
A chatbot that remembers the conversation within a session.

## Endpoints
- `GET /health`
- `POST /sessions` returns `session_id`
- `POST /chat` takes `session_id`, `message` (1-4000 chars) and an optional `model` (a `provider:model` id from `GET /models`; default is `LAB_MODEL`). Returns `reply`, `input_tokens`, `output_tokens`, `seconds`, `cost`, `turns_in_memory`, `guardrail` (null, or the reason)
- `GET /models` returns the model choices from `backend/models.json`, and the default model
- `GET /sessions/{session_id}` returns the messages so far
- `DELETE /sessions/{session_id}`
- `GET /guardrails` reads the guardrail settings
- `PUT /guardrails` changes the guardrail settings

## Rules
- Sessions live in memory.
- Only the last `MAX_HISTORY_TURNS` turns are sent to the model.
- Guardrails run before and after the model call.
- Blocked messages are not saved.

## Errors
- 404: unknown session
- 422: bad input, or a `model` that is not in `GET /models`
- 502: LLM failure

## UI
- Plain HTML chat page served on port 5500.
- A model dropdown in the top bar lists the models from `GET /models`, grouped by provider. The selected model is sent with each message. Changing it keeps the chat history.
