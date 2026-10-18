# Sequence diagrams

How requests flow through the chatbot, as built. Source: [backend/main.py](../backend/main.py), [backend/services.py](../backend/services.py), [backend/guardrails.py](../backend/guardrails.py), [frontend/app.js](../frontend/app.js).

## 1. Start a session

```mermaid
sequenceDiagram
autonumber
actor User
participant UI as Browser app
participant API as FastAPI main.py
participant Svc as services.py
participant Mem as sessions in memory

User->>API: GET /health (optional check from a terminal)
API-->>User: 200 status ok
User->>UI: Open chat page
UI->>UI: Read session_id from sessionStorage
alt Saved session_id exists
  UI->>API: GET /sessions/session_id
  API->>Svc: get_session(session_id)
  Svc->>Mem: Look up session_id
  Svc-->>API: messages
  API-->>UI: 200 session_id, messages
  UI->>UI: Render previous messages
else No saved session_id
  UI->>API: POST /sessions
  API->>Svc: create_session()
  Svc->>Mem: sessions[new id] = empty list
  Svc-->>API: new 8-character session_id
  API-->>UI: 200 session_id
  UI->>UI: Save session_id in sessionStorage
end
Note over Mem: Sessions are lost when uvicorn stops
```

## 2. Send a message: input side

The last `2 * MAX_HISTORY_TURNS` messages are added to the prompt in part 2.

```mermaid
sequenceDiagram
autonumber
actor User
participant UI as Browser app
participant API as FastAPI main.py
participant Svc as services.py
participant Mem as sessions in memory
participant Guard as guardrails.py
participant Cfg as guardrails.json
participant Client as llm_client.py

User->>UI: Type message and press Enter
UI->>API: POST /chat session_id, message
API->>Svc: chat(session_id, message)
Svc->>Mem: get_session(session_id)
Svc->>Cfg: load_config()
Cfg-->>Svc: guardrail settings
Svc->>Guard: check_input(message, config)
Note over Guard: Checks length, injection phrases, then masks email and phone
opt topic_check is on (off by default)
  Guard->>Client: ask_llm(message, topic-judge system)
  Client-->>Guard: YES or NO
end
alt Input blocked
  Guard-->>Svc: not allowed, reason
  Svc-->>API: blocked_message as reply, nothing saved
  API-->>UI: 200 reply, guardrail reason
else Input allowed
  Guard-->>Svc: cleaned message, masked reason or null
  Note over Svc: Continues in part 2
end
```

## 3. Send a message: prompt, LLM call and output side

```mermaid
sequenceDiagram
autonumber
actor User
participant UI as Browser app
participant API as FastAPI main.py
participant Svc as services.py
participant Mem as sessions in memory
participant Guard as guardrails.py
participant Prompts as prompts.json
participant Client as llm_client.py
participant LLM as LLM provider

Svc->>Svc: Keep last 2 * MAX_HISTORY_TURNS messages
Svc->>Svc: build_prompt(recent messages, cleaned message)
Svc->>Prompts: Read chat-assistant system prompt
Prompts-->>Svc: system text
Svc->>Client: ask_llm(prompt, model, system)
Client->>LLM: Chat request
LLM-->>Client: Reply text and token counts
Client-->>Svc: text, tokens, seconds, cost
Svc->>Guard: check_output(reply, config)
alt Output blocked
  Guard-->>Svc: not allowed, reason
  Svc-->>API: blocked_message as reply, nothing saved
else Output allowed
  Guard-->>Svc: allowed
  Svc->>Mem: Append user and assistant messages
  Svc-->>API: reply, metrics, turns_in_memory, guardrail
end
API-->>UI: 200 ChatResponse
UI-->>User: Show reply and metrics
```

## 4. Change the guardrails with PUT /guardrails

The frontend does not call this endpoint. An admin client such as curl or the FastAPI docs page sends it. The endpoint has no authentication.

```mermaid
sequenceDiagram
autonumber
actor Admin as Admin client
participant API as FastAPI main.py
participant Models as models.py
participant Guard as guardrails.py
participant Cfg as guardrails.json

Admin->>API: PUT /guardrails with full JSON body
API->>Models: Validate GuardrailConfig
alt Invalid body, for example max_input_chars <= 0
  Models-->>API: Validation error
  API-->>Admin: 422 detail, file unchanged
else Valid body
  Models-->>API: GuardrailConfig
  API->>Guard: save_config(config)
  Guard->>Cfg: Write guardrails.json.tmp
  Guard->>Cfg: Replace guardrails.json with the temp file
  Guard-->>API: Saved
  API-->>Admin: 200 GuardrailConfig
end
Note over Cfg: The next /chat reads the new file, no restart needed
```

## 5. Error paths

```mermaid
sequenceDiagram
autonumber
actor User
participant UI as Browser app
participant API as FastAPI main.py
participant Svc as services.py
participant Client as llm_client.py
participant LLM as LLM provider

alt Backend is not running
  Note over UI: fetch fails before any response
  UI-->>User: Can't reach the server. Is the backend running?
else Unknown session id, for example after a restart
  UI->>API: POST /chat session_id, message
  API->>Svc: chat(session_id, message)
  Svc-->>API: 404 Unknown session id
  API-->>UI: 404 detail
  UI->>API: POST /sessions
  API-->>UI: 200 new session_id
  UI->>API: POST /chat with new session_id
  API-->>UI: 200 reply
  UI-->>User: Note that a new chat was started
else LLM call fails
  UI->>API: POST /chat session_id, message
  API->>Svc: chat(session_id, message)
  Svc->>Client: ask_llm(prompt, model, system)
  Client->>LLM: Chat request
  LLM-->>Client: Error
  Client-->>Svc: Exception
  Svc-->>API: 502 LLM call failed
  API-->>UI: 502 detail, nothing saved
  UI-->>User: Show error and restore the typed text
end
```
