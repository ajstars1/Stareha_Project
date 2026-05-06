# Product Principles

**Status:** Defined  
**Stage:** 0

These 7 principles are non-negotiable. Every feature decision must pass through them.

---

## 1. Learn Workflows, Not Private Lives

Stareha learns useful patterns — not surveillance data.

**Good memory:**
```
Ayush often runs npm run build before npm test in AgentOS.
```

**Bad memory:**
```
Ayush visited every URL at every minute of the day.
```

Rule: Learn patterns that help. Ignore everything else.

---

## 2. Raw Data Stays Local by Default

Raw data never leaves the device unless the user explicitly allows it.

Raw data includes:
- Full terminal logs
- Full browser history
- Full file contents
- Screenshots
- Private conversations
- Raw Claude Code histories

Only processed summaries may leave — and only with permission.

---

## 3. No Memory Without Provenance

Every durable memory must know:
- Where it came from
- When it was learned
- Why it was learned
- Which source supported it
- What confidence it has
- Whether the user approved or corrected it

If provenance is unknown, the memory should not be stored.

See: [Learning Ledger](../features/03-learning-ledger/README.md)

---

## 4. Scripts First, Local LLM Second, Cloud LLM Only When Needed

```
Deterministic scripts → Local LLM → Cloud LLM
```

Use the cheapest, safest, most private layer that can do the job.

See: [Intelligence Policy](_flows/intelligence-policy-flow.md)

---

## 5. Suggest Autonomously, Act With Permission

Stareha may:
- Learn on its own
- Prepare guidance on its own
- Surface suggestions on its own

Stareha must NOT:
- Take irreversible actions without approval
- Run commands outside approved scopes
- Modify files without explicit permission

---

## 6. User Control Is Mandatory

The user must always be able to:
- See what Stareha learned
- Understand why it learned it
- Edit memories
- Delete memories
- Pause learning
- Disable sources
- Reject bad suggestions
- Improve behavior over time

No black boxes.

---

## 7. Quiet Until Useful

Stareha should not constantly interrupt.

It appears when:
- It has useful context
- It has a helpful suggestion
- It has prepared guidance ready
- The user opens a new session

It does not appear when:
- It has nothing useful to say
- The user is in deep work
- The user has paused it

---

## How to Use These Principles

Before shipping any feature, ask:
1. Does this learn workflows or private lives? (P1)
2. Is raw data leaving the device? (P2)
3. Do new memories have provenance? (P3)
4. Are we using the cheapest valid intelligence layer? (P4)
5. Are we acting without permission? (P5)
6. Can the user see, edit, and delete this? (P6)
7. Are we interrupting unnecessarily? (P7)

If any answer violates a principle → redesign before shipping.
