# Session chatbot

A chatbot that remembers the conversation within a browser session. It has a FastAPI backend, a plain HTML/CSS/JavaScript frontend, and input and output guardrails.

![Screenshot placeholder: chat page](docs/screenshot.png)

## Quick start

1. Create the virtual environment in the project root.

```bash
python -m venv .venv
```

2. Activate it. On Windows PowerShell, use `.venv\Scripts\Activate.ps1`.

```bash
source .venv/bin/activate
```

3. Install the backend packages.

```bash
pip install -r backend/requirements.txt
```

4. Copy the example settings file.

```bash
cp backend/.env.example backend/.env
```

5. Open `backend/.env` and add a key for the provider in `LAB_MODEL`. For example, `GROQ_API_KEY` for the default `groq:llama-3.3-70b-versatile`.

6. Start the backend from the `backend` folder.

```bash
cd backend
uvicorn main:app --port 8000
```

7. In a second terminal, open the API docs at http://localhost:8000/docs to check that the server is up.

8. In a third terminal, serve the frontend from the `frontend` folder.

```bash
cd frontend
python -m http.server 5500
```

9. Open http://localhost:5500 in your browser and send a message.

## Configuration

Settings come from `backend/.env`. Copy `backend/.env.example` to start. Never commit real keys.

| Name | Where | Default | Meaning |
|---|---|---|---|
| `OPENAI_API_KEY` | `.env` | none | Key for `openai:` models |
| `ANTHROPIC_API_KEY` | `.env` | none | Key for `anthropic:` models |
| `GEMINI_API_KEY` | `.env` | none | Key for `gemini:` models |
| `GROQ_API_KEY` | `.env` | none | Key for `groq:` models |
| `MISTRAL_API_KEY` | `.env` | none | Key for `mistral:` models |
| `OPENROUTER_API_KEY` | `.env` | none | Key for `openrouter:` models |
| `LAB_MODEL` | `.env` | `mistral:ministral-3b-2512` | Model in `provider:model` form. The example file sets `groq:llama-3.3-70b-versatile`. |
| `MAX_HISTORY_TURNS` | `.env` | `6` | Number of earlier turns sent to the model. The example file sets `10`. |
| `FRONTEND_ORIGIN` | `.env` | `http://localhost:5500` | The only origin allowed by CORS |
| `GUARDRAILS_FILE` | `.env` | `guardrails.json` | Guardrail settings file, relative to `backend/` |
| `PROMPTS_FILE` | `.env` | `backend/prompts.json` | Prompt file. Not in the example file. A relative path is read from the folder you start the server in. |
| `enabled` | `backend/guardrails.json` | `true` | Turns all guardrails on or off |
| `max_input_chars` | `backend/guardrails.json` | `2000` | Longer user messages are blocked |
| `block_injection` | `backend/guardrails.json` | `true` | Blocks messages that contain an injection phrase |
| `injection_phrases` | `backend/guardrails.json` | 4 phrases | Phrases that trigger the injection block, matched without case |
| `mask_pii` | `backend/guardrails.json` | `true` | Replaces emails with `[EMAIL]` and phone numbers with `[PHONE]` |
| `topic_check` | `backend/guardrails.json` | `false` | Asks the model whether the message fits `allowed_topic` |
| `allowed_topic` | `backend/guardrails.json` | `general questions and everyday conversation` | Topic used by the topic check |
| `max_output_words` | `backend/guardrails.json` | `300` | Replies longer than this are blocked |
| `banned_output_words` | `backend/guardrails.json` | `[]` | Replies that contain any of these words are blocked |
| `blocked_message` | `backend/guardrails.json` | `Sorry, I can't help with that. Please try asking something else.` | Reply shown when a message or reply is blocked |

`guardrails.json` is read on every request, so edits take effect without a restart. `PUT /guardrails` rewrites the whole file.

`backend/prompts.json` holds the `chat-assistant` and `topic-judge` prompts.

## Project layout

```
AGENTS.md                  Project rules for the coding agent
backend/
  main.py                  FastAPI endpoints and CORS
  services.py              Sessions, prompt building, chat logic
  guardrails.py            Input and output checks
  guardrails.json          Guardrail settings
  llm_client.py            ask_llm() for every provider
  models.py                Pydantic request and response models
  settings.py              Settings read from .env
  prompts.json             System and topic-judge prompts
  requirements.txt         Python packages
  pytest.ini               Test settings
  tests/test_api.py        API tests with a fake LLM
  .env.example             Example settings file
docs/
  API.md                   Endpoint reference
  DECISIONS.md             Design decisions
  PROMPT_LOG.md            Prompts given to the agent
  sequence.md              Request flow diagrams
  architecture.drawio      Architecture diagrams
frontend/
  index.html               Chat page
  app.js                   Calls the backend with fetch()
  style.css                Styles
specs/
  chatbot.md               Specification
```

## Running tests

The tests replace the model with a fake, so no key or network access is needed.

```bash
cd backend
pytest
```

## Documentation

- [API reference](docs/API.md)
- [Design decisions](docs/DECISIONS.md)
- [Sequence diagrams](docs/sequence.md)
- [Architecture diagrams](docs/architecture.drawio)
- [Specification](specs/chatbot.md)
