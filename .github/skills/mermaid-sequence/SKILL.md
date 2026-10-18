---
name: mermaid-sequence
description: Use when creating or updating sequence diagrams of how requests flow through the app - docs/sequence.md written in Mermaid sequenceDiagram syntax.
---

# Mermaid sequence diagram skill

Before anything else, start your reply with one line: `🧩 Using skill: mermaid-sequence`
so the developer can see this skill is active.

## Output
`docs/sequence.md`: a short intro, then one `## heading` + one ```mermaid block per flow.

## What to draw
- One diagram per main user action in the spec (e.g. "send a message", "deploy a version").
- One diagram for the main **error paths** (backend down, unknown id → 404, LLM fails → 502,
  guardrail / rule blocks the request).
- Participants, in this order: `actor User`, `participant UI as Browser (app.js)`,
  `participant API as FastAPI`, then the backend modules that matter, files as
  `participant Store as data file`, and `participant LLM as LLM provider` last.

## Syntax rules
- Start with `sequenceDiagram` and `autonumber`.
- Requests `->>`, responses `-->>`. Label requests with method + path + key fields,
  responses with status + key fields.
- Use `alt` / `else` for branches (blocked vs allowed) and `Note over` to explain a rule.
- Keep each diagram under ~20 messages; split it if it grows.
- No HTML, no `;` at line ends, no parentheses inside participant aliases.

## Validate before you say "done"
- Every endpoint in the spec appears in at least one diagram.
- Tell the developer how to view it: open the file on GitHub (renders automatically),
  VS Code Markdown preview with the "Markdown Preview Mermaid Support" extension,
  or paste a block into https://mermaid.live.