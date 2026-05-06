# Stareha Project — Claude Rules

## Identity
This is the **Stareha / AgentOS Continuum** product documentation workspace.

Stareha = AI companion. AgentOS Continuum = the system it lives inside.

---

## Documentation Law
> Every time we work on this project, documentation must be updated before the session ends.

1. Add a feature → write or update its report in `features/`
2. Change a flow → update the relevant `_flows/` file
3. Change architecture → update `architecture/`
4. Add any new file → add it to `SITEMAP.md`
5. Never leave this project in an undocumented state.

## Before Working on Anything
1. Read `SITEMAP.md` — understand the full map
2. Read the relevant feature README before touching sub-reports
3. Read the relevant `_flows/` file before changing behavior logic
4. Check `product/roadmap.md` to understand which stage we're in

## Report Format Rules
Every feature report must include:
- **What it is** — one clear definition
- **Why it matters** — the problem it solves
- **How it works** — the flow/mechanism
- **Sub-features** — links if any
- **Stage** — which roadmap stage it belongs to
- **Status** — Concept / In Progress / Built

## Flow Files (`_flows/`)
Single source of truth for how each system works end-to-end.
- Update any time the flow changes
- Read before implementing — must match the actual implementation

## Sitemap (`SITEMAP.md`)
Every new file must appear here. It's the project's table of contents + dependency map.

## Naming Conventions
- Folders/files: `kebab-case`
- Feature folders prefixed: `01-learning/`, `02-workflow-memory/`, etc.

---

## Commit & PR

**Commit format:** `type: short description` — types: `feat` `fix` `docs` `chore`

**Commit discipline:**
- One logical change per commit — independently revertable
- Never `git add -A` or `git add .` — stage specific files by name
- Rename/move in a separate commit from behavior changes

**PR format:**
```
## What changed
[concrete description — what users/devs can now do]

## Why
[motivation, not implementation narrative]

## Test plan
- [ ] specific thing verified
```

**CHANGELOG voice:** Lead with what you can now do, not what was refactored. "You can now..." not "Refactored the...". Real commands, real file names.

---

## Debugging — Iron Law

**No fixes without root cause. No exceptions.**

1. Read the error fully — collect symptoms before touching code
2. Trace the code path from symptom back to cause
3. Check `git log --oneline -20 -- <file>` — is this a regression?
4. Confirm hypothesis before fixing — add a log/assert at suspected cause
5. If 3 hypotheses fail → stop, ask, don't guess further
6. Fix the root cause, not the symptom — smallest diff that eliminates the problem
7. If touching >5 files → something is wrong, reconsider the approach

**Red flags — slow down:**
- "Quick fix for now" → there is no "for now"
- Proposing a fix before tracing the data flow → you're guessing
- Each fix reveals a new bug → wrong layer, not wrong code

---

## Code Review — What to Always Check

**Critical (check every change):**
- SQLite queries — parameterized, no raw string concatenation
- Raw data leaving the device — Principle 2, zero exceptions
- Permission checks — every collector gated by `can_collect()`
- Shell/subprocess calls — no user-controlled input in shell strings
- Redaction runs before any write — no exceptions (see `_flows/intelligence-policy-flow.md`)

**Privacy-specific (Stareha's core trust contract):**
- Cloud LLM receives summaries only — never raw events, never file contents
- Sensitive fields never logged — passwords, tokens, API keys
- Every memory has provenance — no orphan writes to `memories` table

**Auto-fix without asking:**
- Dead code, unused imports, missing validation at boundaries, stale comments, magic numbers → constants

**Always ask before:**
- Security decisions, race conditions, any fix >20 lines, removing existing functionality

---

## Dangerous Commands — Always Confirm First

These require explicit user confirmation before running:
- `rm -rf` anything outside `~/.stareha/` or project directories
- `systemctl` stop/disable/reset on the daemon
- Any SQLite migration that drops or alters columns
- `git reset --hard`, `git push --force`
- `DROP TABLE`, `TRUNCATE`, `DELETE FROM` without `WHERE`

Safe without confirmation: `rm -rf node_modules`, `rm -rf .next`, `rm -rf dist`

---

## Voice & Communication

Write like a builder talking to another builder:
- Lead with the point — what it does, not what you did
- Be concrete — name files, functions, line numbers, real commands
- Tie to outcomes — what the user sees or can now do
- No filler: avoid "robust", "comprehensive", "seamlessly", "delve", "leverage"
- No em dashes in code output or docs

---

## Skills — When to Invoke

For deep/complex work, invoke the relevant skill. For everything else, the rules above are sufficient.

| Skill | When |
|-------|------|
| `/stareha-doc-sync` | End of session — verify docs are updated |
| `/stareha-stage-check` | Before advancing to next roadmap stage |
| `/plan-eng-review` | Before coding a new stage |
| `/investigate` | Any bug that isn't immediately obvious |
| `/ship` | Creating a PR |
| `/careful` | Touching systemd, SQLite migrations, permission files |
| `/office-hours` | Designing a feature before writing its report |
