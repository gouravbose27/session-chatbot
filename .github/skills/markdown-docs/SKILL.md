---
name: markdown-docs
description: Use when writing or updating project documentation in Markdown - README.md, docs/API.md, docs/DECISIONS.md, docs/PROMPT_LOG.md.
---

# Markdown documentation skill

Before anything else, start your reply with one line: `🧩 Using skill: markdown-docs`
so the developer can see this skill is active.

## Files
| File | Contents |
|---|---|
| `README.md` | What it is (2 lines) · screenshot placeholder · Quick start · Configuration · Project layout · Running tests · Links to docs/ |
| `docs/API.md` | One section per endpoint: method + path, purpose, request JSON example, response JSON example, errors |
| `docs/DECISIONS.md` | One entry per decision: date, decision, why, alternatives considered |
| `docs/PROMPT_LOG.md` | Kept by the developer: each prompt given to the agent and what happened (do not rewrite it) |

## Rules
1. **Quick start must work word for word** on a fresh clone: create `.venv`, install, copy
   `.env.example` to `.env`, add a key, start backend, open Swagger, start frontend, open the URL.
   Every command in its own fenced ```bash block.
2. Configuration section: a table of every `.env` variable and every JSON config file, with
   default and meaning. Never include real keys.
3. API examples are copied from real responses (run the endpoint or the tests), not invented.
4. Link the diagrams: `docs/architecture.drawio` and `docs/sequence.md`.
5. Plain words, short sentences, second person ("you"). Headings in sentence case.
6. Relative links only, so they work on GitHub.

## Check before you say "done"
- [ ] Every endpoint in the spec is in API.md
- [ ] Every `.env` variable is in the README's configuration table
- [ ] No broken relative links (check each path exists)