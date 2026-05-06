# Data Flow

**Status:** Defined  
**Stage:** 0

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
│   SESSION SUMMARY    │  │       PREPARED GUIDANCE          │
│                      │  │                                  │
│  what-did-you-learn  │  │  Gap analysis → weak concepts    │
│  work session brief  │  │  Quiz generation (local LLM)     │
│                      │  │  Exercise generation (cloud LLM) │
└──────────────────────┘  │  Session briefing formatter      │
                          └──────────────┬───────────────────┘
                                         │
                                         ▼
                          ┌──────────────────────────────────┐
                          │      DELIVERED TO USER           │
                          │                                  │
                          │  CLI output on session start     │
                          │  stareha prep tomorrow           │
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
| Learning profile summary | Cloud LLM call | Goals + weak concepts + level (no raw data) |
| Exercise request | Cloud LLM call | Topic + level + style (no personal data) |
| Talking mode context | Cloud LLM call | Session summaries (no raw data) |
| Memories (optional) | Cloud sync Stage 8 | Encrypted, summary-only, user opt-in |

---

## Related Files
- [System Architecture](system-architecture.md)
- [Intelligence Policy Flow](../_flows/intelligence-policy-flow.md)
- [Learning Ledger Flow](../_flows/learning-ledger-flow.md)
