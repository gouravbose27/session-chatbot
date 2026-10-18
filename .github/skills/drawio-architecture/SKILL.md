---
name: drawio-architecture
description: Use when creating or updating the solution architecture diagram docs/architecture.drawio (draw.io / diagrams.net XML) - components, data flow, files and external services.
---

# draw.io architecture skill

Before anything else, start your reply with one line: `🧩 Using skill: drawio-architecture`
so the developer can see this skill is active.

## Output
One file: `docs/architecture.drawio`, **uncompressed** draw.io XML
(`<mxfile><diagram name="..."><mxGraphModel>...`), so it is readable in git diffs.

## Pages (one `<diagram>` each)
1. **Context**: the user, the browser app, the FastAPI backend, the LLM provider(s). One box each.
2. **Components**: inside the backend: each Python module, each JSON/config/data file, and
   `llm_client.py`; inside the frontend: index.html / app.js. Arrows labelled with what flows
   (e.g. "POST /chat {session_id, message}", "ask_llm(prompt, system)").
3. **Deployment / run view**: what runs where locally: uvicorn on its port, http.server on its port,
   `.env` read at start-up, files under `backend/data/`.

## Drawing rules
- Read the spec AND the code in backend/ and frontend/. Draw what the code actually does;
  every module, endpoint group and data/config file appears, nothing invented.
- Left-to-right flow: user → frontend → backend → LLM. Grid-aligned, no overlapping boxes.
- Colours: frontend light blue (`#dae8fc`), backend light green (`#d5e8d4`),
  files/config light yellow (`#fff2cc`), external services light grey (`#f5f5f5`).
- Every arrow has a label. Use `edgeStyle=orthogonalEdgeStyle`.
- Unique `id` for every cell; every edge's `source` and `target` point to existing ids.

## Validate before you say "done"
- Parse the file: `python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse('docs/architecture.drawio'); print('valid XML')"`
- Tell the developer how to open it: draw.io desktop app, the VS Code "Draw.io Integration"
  extension, or app.diagrams.net → File → Open from → Device.