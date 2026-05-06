# Stareha Project — Claude Rules

## Identity
This is the **Stareha / AgentOS Continuum** product documentation workspace.

Stareha = AI companion. AgentOS Continuum = the system it lives inside.

## Documentation Law
> Every time we work on this project, documentation must be updated before the session ends.

Rules:
1. If you add a feature → write or update its report in `features/`
2. If you change a flow → update the flow file in `_flows/`
3. If you change system architecture → update `architecture/`
4. If you add a new feature or sub-feature → add it to `SITEMAP.md`
5. If a report exists, update it. If it doesn't, create it.
6. Never leave this project in an undocumented state.

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
- **Sub-features** — links to sub-reports if any
- **Stage** — which roadmap stage it belongs to
- **Status** — Concept / In Progress / Built

## Flow Files (`_flows/`)
Each flow file is the single source of truth for how that system works end-to-end.
- Must be updated any time the flow changes
- Must be reviewed before implementing the feature
- Must match the actual implementation

## Sitemap (`SITEMAP.md`)
- The sitemap is the master navigation for the entire project
- Every new file must be added to it
- Think of it as the project's table of contents + dependency map

## Naming Conventions
- Folders: `kebab-case`
- Files: `kebab-case.md`
- Feature folders are prefixed with numbers for ordering: `01-learning/`

## Commit Convention
- `docs: update [feature] report`
- `docs: add [feature] flow`
- `feat: add [feature] implementation`
- `fix: correct [feature] description`
