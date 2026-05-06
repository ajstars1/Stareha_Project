# Provenance

**Status:** Concept  
**Stage:** 3

---

## What It Is

Provenance is the complete trail of evidence behind every memory. It answers: "Why does Stareha know this?"

---

## Core Rule

```
No memory without provenance.
```

If provenance cannot be established, the memory is not stored.

---

## Provenance Data Model

Every approved memory has an attached provenance record:

```typescript
interface MemoryProvenance {
  memoryId: string

  // What caused this memory
  evidenceEventIds: string[]    // ledger_events that support this
  evidenceCount: number         // how many events

  // How it was processed
  modelUsed: string             // 'pattern_extractor' | 'local_llm:llama3.2' | 'cloud_llm:claude-sonnet-4-6'
  learningRunId: string         // which batch produced this

  // Confidence metadata
  confidence: number            // 0.0–1.0
  sensitivity: 'low' | 'normal' | 'high'

  // User action
  userAction: 'approved' | 'edited'
  userEditContent?: string      // if edited, the corrected text
  approvedAt: Date

  // Source summary
  sourceSummary: string         // human-readable: "Observed 8 times in ~/projects/agent-os"
}
```

---

## Provenance for Each Source Type

### Terminal provenance
- Event IDs of commands that supported this pattern
- Count of occurrences
- Date range observed
- Project path

### Claude Code provenance
- Session ID
- Date of session
- Which turn in the conversation referenced this

### Browser provenance (Stage 7)
- Research session IDs
- Domains visited
- Search queries that triggered this

### User input provenance
- Direct input event
- Confidence: 1.0 (user-stated)
- Cannot be rejected by model

---

## Sensitivity Classification

| Level | Examples | Treatment |
|-------|---------|-----------|
| `low` | Command patterns, project stack | Auto-surface, normal review |
| `normal` | Learning goals, work habits | Normal inbox review |
| `high` | Personal patterns, private decisions | Require explicit approval, never sent to cloud |

Sensitivity is determined by:
- Source (terminal: low-normal, claude_code: normal-high)
- Content (mentions of personal info: high)
- User override (user can always escalate sensitivity)

---

## How Provenance Enables Trust

When the user asks `stareha memory why`, provenance allows Stareha to say:

```
I learned this because:
- I saw it happen 8 times
- The last time was yesterday
- I used a local pattern extractor (no cloud)
- You approved this on 2026-05-02
```

This makes every memory auditable.

---

## Related Files
- [Learning Ledger](README.md)
- [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)
- [Memory Why](../06-memory-governance/memory-why.md)
