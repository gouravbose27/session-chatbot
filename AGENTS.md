# Project rules

## Skills
Skills live in `.github/skills/`. Read the matching SKILL.md before doing the task.

- `fastapi-backend`: use for anything in `backend/`: endpoints, Pydantic models, JSON storage, settings, LLM calls, CORS, pytest.
- `html-frontend`: use for anything in `frontend/`: the plain HTML/CSS/JS chat page that calls the backend with fetch().
- `python-venv`: use when creating or repairing the virtual environment, installing packages, or writing requirements.txt.
- `git-workflow`: use for git init, .gitignore, staging, commits, remotes, and GitHub via gh.
- `markdown-docs`: use when writing README.md, docs/API.md, docs/DECISIONS.md, or docs/PROMPT_LOG.md.
- `mermaid-sequence`: use for sequence diagrams in docs/sequence.md.
- `drawio-architecture`: use for the architecture diagram docs/architecture.drawio.

## Rules
- Keys only in `backend/.env`. Never write a real key anywhere else.
- Prompt text only in `backend/prompts.json`.
- Never edit `backend/llm_client.py`.
- Always plan before changing files. Show the plan and wait for approval.
- The spec in `specs/chatbot.md` is the reference for all app work.
