# Weak Concept Detection

**Status:** Concept  
**Stage:** 4

---

## What It Is

Weak concept detection identifies topics and skills where the user is struggling, based on behavioral signals from their learning and work sessions.

This is the intelligence that makes quizzes and exercises actually relevant.

---

## Why It Matters

Generic quizzes don't help. Personalized ones do.

Weak concept detection ensures that Stareha only prepares practice on what the user actually needs — not what a generic curriculum says they should know.

---

## Detection Signals

| Signal | Weight | Example |
|--------|--------|---------|
| Repeated searches on same topic | High | Searched "flexbox align" 6 times |
| Repeated errors with same concept | High | DOM selector errors 4 times |
| Incomplete exercises | Medium | Started but didn't finish CSS exercise |
| Low quiz scores (future) | High | Got 2/5 on Flexbox quiz |
| User states struggle explicitly | Highest | `stareha note "struggling with Flexbox"` |
| Long time on same docs page | Medium | 25 min on MDN Flexbox page |

---

## Detection Algorithm (Scripts)

```
For each skill in learning_profile.skills:
  score = 0

  if search_count >= 3:
    score += search_count * 0.15

  if error_count >= 2:
    score += error_count * 0.25

  if incomplete_exercise_count >= 1:
    score += incomplete_exercise_count * 0.20

  if explicit_struggle = true:
    score = max(score, 0.9)

  if score >= 0.5:
    classify as 'weak' or 'struggling'
```

---

## Output

The detection produces a weak concepts list in the learning profile:

```json
{
  "weak_concepts": [
    {
      "concept": "CSS Flexbox alignment",
      "score": 0.82,
      "signals": ["6 searches", "2 incomplete exercises"],
      "last_detected": "2026-05-05"
    },
    {
      "concept": "DOM selectors",
      "score": 0.71,
      "signals": ["4 errors", "1 explicit note"],
      "last_detected": "2026-05-04"
    }
  ]
}
```

This list is the input to quiz and exercise generation.

---

## Resolving Weak Concepts

A concept moves from `weak` to `practicing` when:
- User completes a quiz with score >= 70%
- User completes an exercise on the concept
- User explicitly marks it resolved

---

## Related Files
- [Prepared Guidance](README.md)
- [Learning Profile](../01-learning/learning-profile.md)
- [Quiz Generation](quiz-generation.md)
- [Prepared Guidance Flow](../../_flows/prepared-guidance-flow.md)
