# Quiz Generation

**Status:** Built
**Stage:** 4–5

---

## What It Is

Stareha generates personalized quizzes targeting the user's current weak concepts, at the right difficulty level for their current skill.

---

## Why It Matters

Quizzes are the fastest way to check and reinforce understanding. A personalized quiz on exactly what the user struggled with is far more effective than any generic exercise.

---

## Quiz Format

```
CSS Flexbox Quiz — 5 questions
Prepared because: you searched Flexbox alignment 6 times this week.

Q1: What property controls horizontal alignment of flex items?
   A) align-items
   B) justify-content
   C) flex-direction
   D) align-content

Q2: Which value centers flex items both horizontally and vertically?
   (type your answer)

Q3: True or False: flex-direction: row is the default.

Q4: What's the difference between align-items and align-content?

Q5: Fix this CSS to center the card horizontally:
   .container { display: flex; align-items: center; }
```

---

## Generation Process

```
Weak concepts list (from detection)
  ↓
For each concept to quiz:
  - Select concept (highest score first)
  - Determine difficulty from learning profile skill level
  - Generate 5 questions
    (template/scripts always work; local LLM improves quality if available)
  - Use cloud LLM only for an explicit cloud-enabled command such as `stareha quiz --cloud <topic>`
  - Format as CLI-friendly or markdown output
  - Store quiz in prepared_guidance table
  ↓
Quiz available in `stareha quiz` or next-session guidance
```

---

## Question Types

| Type | When used |
|------|-----------|
| Multiple choice | Concept identification, vocabulary |
| Short answer | Applied understanding |
| True/False | Quick checks |
| Code completion | Applied syntax |
| Debugging | Error-pattern concepts |

---

## Difficulty Calibration

| Skill level | Quiz style |
|------------|-----------|
| `novice` | Multiple choice only, conceptual |
| `struggling` | Mixed, applied, with hints |
| `practicing` | Code completion, debugging |
| `understood` | Edge cases, comparison questions |

---

## Scoring

After the user answers:
- Score calculated
- Wrong answers tagged as weak signals
- Score >= 70% → concept moves toward `practicing`
- Score < 50% → concept flagged for more exercises

---

## Intelligence Layer

| Task | Layer |
|------|-------|
| Question selection | Scripts (concept + difficulty rules) |
| Question generation | Template/scripts by default; local LLM if available |
| Cloud fallback | Only when the user passes an explicit cloud-enabled command such as `stareha quiz --cloud <topic>` |

---

## Related Files
- [Prepared Guidance](README.md)
- [Weak Concept Detection](weak-concept-detection.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
