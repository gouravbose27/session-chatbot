---
name: python-venv
description: Use whenever you create, activate, repair or install packages into the project's Python virtual environment, or write requirements.txt. Covers python3 -m venv, pip, requirements files and checking which python is in use.
---

# Python virtual environment skill

Before anything else, start your reply with one line: `🧩 Using skill: python-venv`
so the developer can see this skill is active.

## Rules
1. One virtual environment per project, at `.venv/` in the project root. Never install into the system Python.
2. Create it with `python3 -m venv .venv`. Use Python 3.11 or newer; check with `python3 --version` first.
3. Never "activate" inside your own commands: call the venv's tools by path, e.g.
   `.venv/bin/pip install -r backend/requirements.txt` and `.venv/bin/python -m pytest`.
   (On Windows: `.venv\Scripts\pip`.) Tell the developer how to activate it themselves:
   `source .venv/bin/activate`.
4. Dependencies live in `backend/requirements.txt`, one package per line, no versions unless a
   version is needed to make it work. Add a comment line explaining any pinned version.
5. After installing, prove it worked: `.venv/bin/pip list` filtered to the new packages.
6. `.venv/` must be in `.gitignore`. Never commit it.

## Check before you say "done"
- [ ] `.venv/bin/python --version` prints 3.11+
- [ ] Every import in the code is in requirements.txt
- [ ] `.venv/bin/pip install -r backend/requirements.txt` runs cleanly on a fresh venv
- [ ] You told the developer the exact activate command