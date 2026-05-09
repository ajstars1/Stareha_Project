# Session Briefing

**Status:** Built
**Stage:** 4–5.5

---

## What It Is

The session briefing is the daily/next-session summary that Stareha prepares and delivers when the user starts a new session.

It is the primary interface through which Stareha acts as a mentor or work companion.

---

## Why It Matters

The briefing is the "Jarvis moment" — the product's highest-value UX. If the briefing is great, the user feels Stareha is indispensable. If it's off, the user ignores it.

---

## Delivery Points

| When | How |
|------|-----|
| `stareha learn "<goal>"` | CLI output |
| Advanced `stareha session start` | CLI output |
| First terminal open (if daemon integration enabled) | CLI message |
| `stareha what-did-you-learn today` | On demand |
| `stareha prep` | On demand, for next session |
| Desktop tray (Stage 6) | Notification |

---

## Learning Briefing Format

```
Good morning. I prepared today's plan.

Yesterday (2026-05-05):
- You practiced CSS Flexbox for 95 minutes
- Struggled with: alignment, justify-content vs align-items
- Completed: HTML forms exercise
- Searched "flexbox align center" 6 times

Today's plan:

1. 10-minute recap
   → CSS Flexbox: justify-content, align-items, flex-direction
   (file: ~/.stareha/recaps/flexbox-recap.md)

2. 5-question quiz
   → Focus: the properties you struggled with yesterday
   Run: stareha quiz flexbox

3. Exercise (30 min)
   → Build a responsive pricing card (Flexbox only)
   Run: stareha exercise flexbox-pricing-card

4. Stretch goal: DOM selectors
   → 3 debugging tasks
   Run: stareha exercise dom-selectors-debug
```

---

## Work Briefing Format

```
Good morning.

AgentOS Continuum — last session: yesterday at 18:45 (3h 20m)

Completed:
- SQLite event store schema (packages/core/src/db.ts)
- Terminal history scanner (basic implementation)

In progress:
- Memory candidate generator (partial — stopped at evidence_ids logic)

Open tasks:
- Wire up memory_candidates to CLI inbox command
- Add confidence scoring to pattern extractor

Next suggested step:
Complete evidence_ids logic in packages/core/src/memory.ts
(you left off at line ~142)

Relevant:
- Last decision: use SQLite $transaction for candidate writes
- Run: cd ~/projects/agent-os && npm run build
```

---

## Briefing Quality Rules

1. Never show more than 4–5 items — cognitive overload kills it
2. Always explain WHY each item is suggested ("you searched X 6 times")
3. Make every item immediately actionable (run this command)
4. Keep it under 30 lines in CLI
5. Lead with completion from yesterday — celebrate progress first

---

## Briefing Generation Process

```
Session history + memories + learning profile
  ↓
Gap analysis (what was struggled with?)
  ↓
Completion check (what was finished?)
  ↓
Plan construction (recap + quiz + exercise + stretch)
  ↓
Format for CLI
  ↓
Store in prepared_guidance (ready for next `stareha learn "<goal>"`)
```

---

## Related Files
- [Prepared Guidance](README.md)
- [Work Task Prep](work-task-prep.md)
- [Prepared Guidance Flow](../../_flows/prepared-guidance-flow.md)
