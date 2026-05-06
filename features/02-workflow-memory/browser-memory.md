# Browser/Research Memory

**Status:** Concept  
**Stage:** 7 (automatic) / 2 (manual tagging)

---

## What It Is

Browser memory stores what topics the user researches and what resources they rely on — extracted from browsing sessions via the browser extension or manual session tagging.

---

## Why It Matters

Research patterns reveal:
- What topics the user is learning
- What docs they rely on
- What they struggle to find answers to
- What resources are most useful to them

---

## Memory Categories

### Research Topics
What subjects the user researches frequently.

Example:
```
Memory: "Frequently researches: CSS Flexbox alignment, DOM selectors, React useEffect."
Source: browser extension
Evidence: 12 research sessions
Confidence: 0.88
```

### Trusted Resources
Sites the user consistently returns to.

Example:
```
Memory: "Primary references: developer.mozilla.org (CSS), react.dev (React), sqlite.org (SQLite)."
Source: browser extension
Evidence: 40+ visits
Confidence: 0.94
```

### Repeated Searches
Topics searched multiple times, indicating struggle.

Example:
```
Memory: "Searched 'flexbox align center' 6 times — likely struggling with alignment."
Source: browser extension
Evidence: 6 search events
Confidence: 0.79
```

---

## MVP Alternative (Stage 2, before browser extension)

Users can manually tag research sessions:

```bash
stareha note "researching Flexbox alignment — struggling with justify-content vs align-items"
stareha note "read React useEffect docs — understood cleanup functions"
```

These notes become browser-type memories with lower confidence (no behavioral evidence).

---

## Example Memories

```
When working on web dev projects, Ayush uses MDN as primary reference.
Source: manual note | Confidence: 0.65
```

```
Ayush has searched CSS Flexbox alignment 6 times this week — a weak concept.
Source: browser | Evidence: 6 searches | Confidence: 0.87
```

---

## Related Files
- [Workflow Memory](README.md)
- [Browser Connector](../01-learning/connectors/browser.md)
- [Weak Concept Detection](../04-prepared-guidance/weak-concept-detection.md)
