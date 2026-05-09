# Data Flow

**Status:** Updated
**Stage:** 5.5

---

## Complete Data Flow: Raw Event → Memory → Suggestion

```
┌─────────────────────────────────────────────────────────────┐
│                        USER ACTIVITY                        │
│  Terminal command  │  File save  │  Claude Code session      │
└─────────┬──────────┴──────┬──────┴───────────┬──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERMISSION CHECK                          │
│  Is this source enabled? Has path been approved?            │
└─────────────────────────┬───────────────────────────────────┘
                          │ (if permitted)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      REDACTION                              │
│  Strip secrets, API keys, passwords, tokens                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   LEDGER_EVENTS TABLE                        │
│  Immutable write. Raw event (redacted) + metadata.          │
│  Never modified after write.                                │
└─────────────────────────┬───────────────────────────────────┘
                          │ (on session end / scheduled)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING RUN                              │
│                                                             │
│  Layer 1 (scripts):                                         │
│    Pattern extractor → command sequences, frequencies       │
│    Importance scorer → skip if score < 0.3                  │
│    Deduplicator → skip if already captured                  │
│                                                             │
│  Layer 2 (local LLM, if available):                         │
│    Summarizer → human-readable memory text                  │
│    Weak concept extractor → gaps in learning                │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 MEMORY_CANDIDATES TABLE                      │
│  content + source + evidence_ids + model + confidence       │
│  Status: 'pending'                                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      MEMORY INBOX                           │
│  User: stareha memory inbox                                 │
│  User approves / rejects / edits each candidate             │
└─────────────────────────┬───────────────────────────────────┘
                          │ (if approved)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    MEMORIES TABLE                            │
│  Approved memory + full provenance record                   │
│  Available for: summaries, guidance, LLM context            │
└────────────────┬────────────────────┬───────────────────────┘
                 │                    │
                 ▼                    ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│    LEARNING CARD     │  │       PREPARED GUIDANCE          │
│                      │  │                                  │
│  goal + project      │  │  Gap analysis → weak concepts    │
│  worked on           │  │  Quiz generation (script/local)  │
│  stuck on            │  │  Session briefing formatter      │
│  next step           │  │                                  │
└──────────┬───────────┘  └──────────────┬───────────────────┘
           │                             │
           └──────────────┬──────────────┘
                          ▼
                          ┌──────────────────────────────────┐
                          │        EXPERIENCE LAYER          │
                          │                                  │
                          │  stareha home                    │
                          │  stareha done                    │
                          │  stareha continue                │
                          │  Save / Ignore / Edit review UX  │
                          └──────────────┬───────────────────┘
                                         │
                                         ▼
                          ┌──────────────────────────────────┐
                          │      DELIVERED TO USER           │
                          │                                  │
                          │  Learning Card at session end    │
                          │  Continue plan on return         │
                          │  CLI briefing on session start   │
                          │  stareha prep                    │
                          │  Desktop tray (Stage 6)          │
                          └──────────────────────────────────┘
```

---

## What Never Leaves the Device

- Raw events (ledger_events table)
- Memory candidates
- Full terminal logs
- File contents
- Raw Claude Code conversations
- Browser history
- Approved memories (unless cloud sync enabled at Stage 8)

## What May Leave the Device

| Data | When | What exactly |
|------|------|-------------|
| Learning profile summary | Explicit cloud-enabled command | Goals + weak concepts + level (no raw data) |
| Quiz/exercise request | Explicit cloud-enabled command | Topic + level + style (no personal data) |
| Talking mode context | `stareha talk --cloud` | Approved memories and summaries (no raw data) |
| Memories (optional) | Cloud sync Stage 8 | Encrypted, summary-only, user opt-in |

---

## Related Files
- [System Architecture](system-architecture.md)
- [Intelligence Policy Flow](../_flows/intelligence-policy-flow.md)
- [Learning Ledger Flow](../_flows/learning-ledger-flow.md)
