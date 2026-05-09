# Prepared Guidance Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Updated
**Stage:** 4–5.5

---

## What This Covers

How Stareha prepares personalized next-session guidance before the user asks.

---

## Core Idea

Stareha does not wait to be asked.

When the user ends a session with `stareha done`, Stareha:
1. Analyzes what happened
2. Identifies gaps and weaknesses
3. Prepares relevant guidance
4. Delivers a briefing at the next session start

---

## Full Flow

```
Session ends (stareha done)
  ↓
Learning run triggered
  (see Learning Flow)
  ↓
Learning profile loaded
  {
    goals: ["learn web development"],
    strong_concepts: ["HTML forms", "basic CSS"],
    weak_concepts: ["DOM selectors", "Flexbox alignment"],
    recent_sessions: [...],
    preferred_style: "project-based"
  }
  ↓
Gap analysis
  - What did the user struggle with today?
  - What concepts were repeatedly searched?
  - What exercises were not completed?
  - What errors were repeated?
  ↓
Guidance plan generated
  (scripts/templates by default; local LLM if available; cloud only when explicitly allowed)
  ↓
For Learning Goals:
  - Quizzes on weak concepts
  - Exercises matched to level
  - Recap of today's topic
  - Next concept to study
  - Recommended resources

For Work Goals:
  - Task summary (what was completed)
  - Open issues or blockers
  - Suggested next task
  - Relevant docs or commands
  ↓
Guidance stored locally
  ↓
Next `stareha learn "<goal>"` → briefing delivered
  (CLI output now, tray notification later)
```

---

## Briefing Format (Learning)

```
Good morning. I prepared today's learning plan.

Yesterday you:
- Practiced HTML forms (completed)
- Struggled with Flexbox alignment (6 searches)
- Did not finish DOM selector exercises

Today's plan:

1. 10-minute Flexbox recap
   Focus: justify-content, align-items, flex-direction

2. 5-question quiz
   Topic: Flexbox properties

3. Project exercise
   Build a responsive pricing card using Flexbox

4. DOM selector tasks
   Complete the 3 tasks from yesterday
```

---

## Briefing Format (Work)

```
Good morning. Here's where you left off.

AgentOS Continuum — last active: yesterday at 18:45

Completed:
- SQLite event store schema
- Terminal history scanner (basic)

In progress:
- Memory candidate generator (partial)

Next suggested task:
- Wire up memory_candidates table to the inbox CLI command

Relevant:
- See: features/06-memory-governance/memory-commands.md
```

---

## Guidance Types

| Type | When generated | Requires |
|------|---------------|----------|
| Quiz | After learning session | Learning profile + weak concepts; script/local by default |
| Exercise | After repeated struggle | Weak concept detected; cloud only when explicitly allowed |
| Recap | Always | Session summary |
| Next concept | When current concept understood | Learning profile |
| Work task | After work session | Work session memory |
| Bug investigation | After repeated error | Error pattern memory |

---

## Intelligence Used

| Task | Layer |
|------|-------|
| Gap analysis | Deterministic scripts |
| Recap generation | Local LLM |
| Quiz generation | Scripts → Local LLM; Cloud only for explicit cloud-enabled command |
| Exercise generation | Scripts/templates first; Cloud only for explicit cloud-enabled command |
| Resource recommendation | Local lookup → Cloud for new topics |

---

## Trigger Rules

Guidance is prepared:
- Automatically after `stareha done`
- Automatically after advanced `stareha session stop`
- Nightly at 23:00 if user was active that day
- Manually via `stareha prep`

Guidance is delivered:
- On next `stareha learn "<goal>"`
- On advanced `stareha session start`
- On terminal open (if desktop integration enabled)
- Via tray notification (Stage 6)

---

## Related Files
- [Learning Flow](learning-flow.md)
- [Weak Concept Detection](../features/04-prepared-guidance/weak-concept-detection.md)
- [Quiz Generation](../features/04-prepared-guidance/quiz-generation.md)
- [Exercise Generation](../features/04-prepared-guidance/exercise-generation.md)
- [Session Briefing](../features/04-prepared-guidance/session-briefing.md)
