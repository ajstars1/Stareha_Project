# Feature: Learning

**Status:** Concept  
**Stage:** 2  
**Why it matters:** This is what makes Stareha different — it learns from actual work, not just what the user tells it.

---

## What It Is

The learning system observes approved user activity and extracts useful patterns, habits, decisions, and knowledge gaps.

It is the input layer of Stareha. Everything downstream — workflow memory, learning ledger, prepared guidance — depends on what the learning system captures.

---

## Why It Matters

Without learning, Stareha is just another chatbot that forgets everything.

With learning, Stareha becomes a companion that accumulates context over time and uses it to help proactively.

---

## How It Works

See: [Learning Flow](../../_flows/learning-flow.md)

Short version:
1. Connectors collect approved events from user activity
2. Events are processed by pattern extractors (scripts first)
3. Interesting patterns become memory candidates
4. Candidates go to the Memory Inbox for user review
5. Approved memories update the learning profile
6. Learning profile feeds into Prepared Guidance

---

## Sub-Features

| Sub-feature | File | What it covers |
|-------------|------|---------------|
| Learning from work | [learning-from-work.md](learning-from-work.md) | How work sessions are observed and learned from |
| Learning profile | [learning-profile.md](learning-profile.md) | What the profile contains, how it's built |
| Connectors | [connectors/README.md](connectors/README.md) | All data connectors overview |
| Claude Code connector | [connectors/claude-code.md](connectors/claude-code.md) | Chat history, CLAUDE.md, session import |
| Terminal connector | [connectors/terminal.md](connectors/terminal.md) | Shell history, command watching |
| Browser connector | [connectors/browser.md](connectors/browser.md) | Research and learning sessions |
| File watcher connector | [connectors/file-watcher.md](connectors/file-watcher.md) | Project file activity |

---

## What Stareha Learns

| Source | What is learned |
|--------|----------------|
| Terminal | Command patterns, errors, fixes, project habits |
| Claude Code | Decisions, bugs, plans, open tasks |
| Browser | Research topics, docs used, learning focus |
| Files | Active project, structure, common files |
| App usage | Work environment, time-of-day habits |
| User input | Explicit goals, corrections, feedback |

---

## What Stareha Does NOT Learn

- Private messages or conversations not in approved sources
- Financial or personal data
- Full file contents (project-level summaries only)
- Browser history outside learning/research context
- Any source without explicit permission

---

## Related Flows
- [Learning Flow](../../_flows/learning-flow.md)
- [Workflow Memory Flow](../../_flows/workflow-memory-flow.md)
- [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)
