# Learning Profile

**Status:** Concept  
**Stage:** 2–4

---

## What It Is

The learning profile is a structured summary of everything Stareha knows about the user's goals, skill level, strengths, weaknesses, and preferred learning style.

It is built incrementally over time from approved memories.

---

## Why It Matters

The learning profile is the input to Prepared Guidance. Without a profile, Stareha cannot generate personalized quizzes, exercises, or next steps.

---

## Profile Structure

```json
{
  "user_id": "local",
  "created_at": "2026-04-01",
  "updated_at": "2026-05-06",

  "goals": [
    {
      "id": "goal_001",
      "description": "Learn web development",
      "type": "learning",
      "status": "active",
      "added_at": "2026-04-15"
    }
  ],

  "skills": {
    "html_forms": { "level": "practiced", "last_seen": "2026-05-05" },
    "css_basics": { "level": "understood", "last_seen": "2026-05-05" },
    "flexbox": { "level": "struggling", "search_count": 6, "last_seen": "2026-05-05" },
    "dom_selectors": { "level": "weak", "error_count": 4, "last_seen": "2026-05-04" },
    "react_components": { "level": "novice", "last_seen": "2026-05-03" }
  },

  "learning_style": {
    "preferred": "project-based",
    "evidence": "user responded positively to exercise prompts",
    "confidence": 0.72
  },

  "recent_sessions": [
    {
      "date": "2026-05-05",
      "goal": "CSS Flexbox",
      "duration_minutes": 95,
      "completed": ["HTML form exercise"],
      "struggled_with": ["Flexbox alignment", "DOM selectors"]
    }
  ],

  "projects": {
    "agent-os": {
      "last_active": "2026-05-06",
      "stack": ["TypeScript", "Node.js", "SQLite"],
      "typical_commands": ["npm run build", "npm test", "tsc"],
      "active_focus": "memory system"
    }
  }
}
```

---

## Skill Levels

| Level | What it means |
|-------|--------------|
| `unknown` | No data yet |
| `novice` | Just started, 1–2 exposures |
| `struggling` | Repeatedly failing or searching |
| `practicing` | Working with it, occasional errors |
| `understood` | Can use without help |
| `strong` | Rarely needs to look it up |

Level is inferred from:
- Search frequency (high = struggling)
- Error count (high = struggling)
- Completion rate (high = understood)
- User correction of Stareha assumptions (direct feedback)

---

## How the Profile Is Updated

1. After each learning run, new memories are merged into the profile
2. Skill levels are updated based on new evidence
3. Goals are marked complete when user confirms
4. Projects are updated from file watcher and terminal data

---

## How the Profile Is Used

| Consumer | Uses |
|----------|------|
| Prepared Guidance | Weak concepts → quiz/exercise targets |
| Session Briefing | Goals + recent sessions → daily plan |
| Cloud LLM context | Summary sent as context (no raw data) |
| `stareha profile` CLI | User can view/edit their profile |

---

## Related Files
- [Learning Feature](README.md)
- [Weak Concept Detection](../04-prepared-guidance/weak-concept-detection.md)
- [Prepared Guidance Flow](../../_flows/prepared-guidance-flow.md)
