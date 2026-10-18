---
name: html-frontend
description: Use when building or changing anything in frontend/ - the browser user interface written in plain HTML, CSS and JavaScript that calls the FastAPI backend with fetch().
---

# HTML frontend skill

Before anything else, start your reply with one line: `🧩 Using skill: html-frontend`
so the developer can see this skill is active.

## Stack
Plain HTML, CSS and JavaScript. No framework, no npm, no build step. Three files:
`frontend/index.html`, `frontend/style.css`, `frontend/app.js`.
Served for development with `python3 -m http.server <port>` from `frontend/`.

## Rules
1. The backend URL is ONE constant at the top of `app.js` (e.g. `const API = "http://localhost:8000";`).
2. All calls go through one helper `async function api(method, path, body)` that:
   sets JSON headers, parses JSON, and turns errors into a readable message
   (network down → "Can't reach the server. Is the backend running?"; 4xx/5xx → the `detail` field).
3. Never put API keys or secrets in the frontend. The browser only talks to our backend.
4. Never insert server or model text with `innerHTML`. Use `textContent` or
   `document.createElement` so nothing in a reply can run as code.
5. Every button that calls the backend shows a busy state and is disabled until the call ends.
6. Errors are shown inside the page next to what failed. No `alert()`, no confirm dialogs.
7. Layout with CSS grid/flex, readable at 1280px and 400px wide. System font, one accent colour.
8. Keep page state in a few clearly named variables at the top of `app.js`; use `sessionStorage`
   only for things that should survive a refresh (like a session id).

## Check before you say "done"
- [ ] `grep -n "innerHTML" frontend/app.js` shows no model/server text going in
- [ ] `grep -rn "KEY" frontend` is empty
- [ ] With the backend stopped, the page shows the friendly message, not a blank screen
- [ ] You told the developer how to serve it and which URL to open