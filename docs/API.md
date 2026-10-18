# API reference

The backend runs on http://localhost:8000. Interactive docs are at http://localhost:8000/docs.

The examples below were copied from real responses. The `/chat` success and 502 examples use the fake model from the test suite, so the reply text is `reply 1`. The other examples come from the running server.

## GET /health

Checks that the server is running.

Response, 200:

```json
{
  "status": "ok"
}
```

## POST /sessions

Starts a new chat session. Sessions are kept in memory and are lost when the server stops.

Request: no body.

Response, 200:

```json
{
  "session_id": "c31a201d"
}
```

## POST /chat

Sends a message in a session and returns the reply with its metrics.

Request:

```json
{
  "session_id": "cccafc4f",
  "message": "hello"
}
```

`message` must be 1 to 4000 characters. Messages over `max_input_chars` (2000 by default) are blocked with a 200 response. See [DECISIONS.md](DECISIONS.md).

Response, 200, normal reply (fake model):

```json
{
  "reply": "reply 1",
  "input_tokens": 10,
  "output_tokens": 5,
  "seconds": 0.5,
  "cost": null,
  "turns_in_memory": 1,
  "guardrail": null
}
```

Response, 200, blocked input. No model call is made and nothing is saved:

```json
{
  "reply": "Sorry, I can't help with that. Please try asking something else.",
  "input_tokens": 0,
  "output_tokens": 0,
  "seconds": 0.0,
  "cost": null,
  "turns_in_memory": 0,
  "guardrail": "blocked: injection"
}
```

`guardrail` is `null`, a blocked reason such as `blocked: injection`, `blocked: too long`, `blocked: off topic`, `blocked: banned word`, or `blocked: reply too long`, or a masking note such as `masked: email, phone`.

Errors:

| Status | When | Example body |
|---|---|---|
| 404 | Unknown `session_id` | `{"detail": "Unknown session id"}` |
| 422 | Empty message or message over 4000 characters | See below |
| 502 | The model call fails, or the topic check fails | `{"detail": "LLM call failed: provider is down"}` |

422 example, for an empty `message`:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": [
        "body",
        "message"
      ],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {
        "min_length": 1
      }
    }
  ]
}
```

A 502 leaves the session unchanged, so the user can retry.

## GET /sessions/{session_id}

Returns the messages of a session so far, oldest first.

Response, 200:

```json
{
  "session_id": "cccafc4f",
  "messages": [
    {
      "role": "user",
      "content": "hello"
    },
    {
      "role": "assistant",
      "content": "reply 1"
    }
  ]
}
```

A blocked message is not saved, so after a blocked message the list is empty:

```json
{
  "session_id": "c31a201d",
  "messages": []
}
```

Errors:

| Status | When | Example body |
|---|---|---|
| 404 | Unknown `session_id` | `{"detail": "Unknown session id"}` |

## DELETE /sessions/{session_id}

Deletes a session and its messages.

Response, 200:

```json
{
  "deleted": true
}
```

Errors:

| Status | When | Example body |
|---|---|---|
| 404 | Unknown `session_id` | `{"detail": "Unknown session id"}` |

## GET /guardrails

Returns the guardrail settings from `backend/guardrails.json`.

Response, 200:

```json
{
  "enabled": true,
  "max_input_chars": 2000,
  "block_injection": true,
  "injection_phrases": [
    "ignore previous instructions",
    "reveal your system prompt",
    "you are now",
    "developer mode"
  ],
  "mask_pii": true,
  "topic_check": false,
  "allowed_topic": "general questions and everyday conversation",
  "max_output_words": 300,
  "banned_output_words": [],
  "blocked_message": "Sorry, I can't help with that. Please try asking something else."
}
```

## PUT /guardrails

Replaces all guardrail settings and writes them to `backend/guardrails.json`. The body must contain every field shown in `GET /guardrails`. Numeric limits must be greater than 0.

Request: the same JSON as the `GET /guardrails` response, with the values you want to change.

Response, 200: the saved settings, in the same shape as `GET /guardrails`.

Errors:

| Status | When | Example body |
|---|---|---|
| 422 | A field is missing or invalid, for example `max_input_chars` is `-1` | Pydantic error list, in the same format as the 422 example under `POST /chat`. The file is not changed. |

This endpoint has no authentication. Anyone who can reach the server can change the guardrails.
