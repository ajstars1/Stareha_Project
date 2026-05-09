# Exercise Generation

**Status:** Concept  
**Stage:** 4

---

## What It Is

Stareha generates coding exercises — mini-projects, debugging tasks, and practice challenges — matched to the user's current level and weak areas.

---

## Why It Matters

Reading about a concept is different from building with it. Exercises create the practice that actually solidifies learning.

A user who struggled with Flexbox doesn't need another article. They need to build something with Flexbox.

---

## Exercise Types

| Type | Description | When used |
|------|-------------|-----------|
| Mini-project | Small self-contained build | Strong concept application |
| Debugging task | Broken code to fix | Error-pattern concepts |
| Code completion | Partial code to finish | Applied syntax |
| Comparison task | Explain difference between two approaches | Conceptual clarity |
| Refactor task | Improve existing code | Advanced practice |

---

## Example Exercise

```
Exercise: Responsive Pricing Card

Topic: CSS Flexbox
Level: beginner-intermediate
Reason: You searched Flexbox alignment 6 times this week.

Task:
Build a responsive pricing card with:
- 3-column layout on desktop
- Single column on mobile
- Centered content in each card
- A highlighted "Pro" tier in the middle

Requirements:
- Use only Flexbox (no Grid)
- Card must center horizontally and vertically
- Works at 320px and 1200px width

Starter file: pricing-card-starter.html (provided)

When done, run: stareha exercise complete flexbox-pricing-card
```

---

## Generation Process

```
Weak concept + skill level + learning style
  ↓
Exercise template selected (based on concept type)
  ↓
Exercise generated (script/template or local LLM by default; cloud only with explicit consent)
  ↓
Starter file created if needed
  ↓
Stored in prepared_guidance table
  ↓
Available in next-session briefing
```

---

## Exercise Storage

Exercises are stored locally as markdown files + optional starter code:

```
~/.stareha/exercises/
  2026-05-06-flexbox-pricing-card.md
  2026-05-06-flexbox-pricing-card-starter.html
```

---

## Completion Tracking

```bash
stareha exercise complete flexbox-pricing-card     # Mark as done
stareha exercise skip flexbox-pricing-card         # Skip this one
stareha exercise list                              # Show pending exercises
```

Completion updates the learning profile skill level.

---

## Intelligence Layer

Cloud LLM may be used for future exercise generation only after explicit user consent:
- Exercises require creativity
- Generic exercises waste the user's time
- No raw data is sent, only a learning profile summary

Context sent to cloud LLM after consent:
```
Topic: CSS Flexbox
User level: struggling (searched 6 times, 2 incomplete exercises)
Preferred style: project-based
Goal: web development
Generate a beginner-appropriate mini-project exercise.
```

---

## Related Files
- [Prepared Guidance](README.md)
- [Weak Concept Detection](weak-concept-detection.md)
- [Quiz Generation](quiz-generation.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
