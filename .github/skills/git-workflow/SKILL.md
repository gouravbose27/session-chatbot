---
name: git-workflow
description: Use for anything involving git or GitHub - git init, .gitignore, staging, commits, commit messages, remotes, and creating or pushing to a GitHub repository with the gh CLI.
---

# Git workflow skill

Before anything else, start your reply with one line: `🧩 Using skill: git-workflow`
so the developer can see this skill is active.

## Rules
1. **Show before you change.** Before any command that changes the repo (add, commit, push,
   remote, repo create), print the exact command and wait for the developer to say yes.
2. **Secrets never enter git.** `.gitignore` always contains: `.env`, `.venv/`, `__pycache__/`,
   `.pytest_cache/`, `backend/data/`, `.DS_Store`. Before every commit run `git status` and
   `git diff --cached --name-only`; if `.env` or anything with a real key is staged, stop and say so.
3. **Small commits, one per step**, message format `type: what changed`
   (types: chore, feat, fix, test, docs). Example: `feat: session memory in /chat`.
4. Never `git push --force`, never rewrite history, never change git config, never commit on
   the developer's behalf without being asked in this step.
5. **GitHub through gh only.** First `gh auth status`. If not logged in, stop and ask the
   developer to run `gh auth login` themselves; never handle tokens or passwords.
   Create repos private by default:
   `gh repo create <name> --private --source=. --remote=origin --push`
6. After a push, show `git remote -v`, `git log --oneline -5` and the repo URL.

## Check before you say "done"
- [ ] `git status` is clean
- [ ] `git ls-files` contains no `.env` and no `.venv`
- [ ] The commit message says what changed, in words