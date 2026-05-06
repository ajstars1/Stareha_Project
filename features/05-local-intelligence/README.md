# Feature: Local Intelligence

**Status:** Concept  
**Stage:** 1 (scripts), 5 (local LLM), 3 (cloud LLM restricted)

---

## What It Is

The intelligence policy system determines which processing layer handles each task — deterministic scripts, local LLM, or cloud LLM — based on capability, privacy, and cost requirements.

---

## Why It Matters

Processing everything with a cloud LLM would be:
- Expensive
- A privacy violation (raw data leaves device)
- Unnecessary for most tasks

Processing everything with scripts would be:
- Inflexible
- Unable to understand language patterns
- Incapable of generating exercises or explanations

The three-layer system balances all three: privacy, cost, capability.

---

## Sub-Features

| Sub-feature | File | What it covers |
|-------------|------|---------------|
| Scripts layer | [scripts-layer.md](scripts-layer.md) | Deterministic rules, pattern extraction |
| Local LLM | [local-llm.md](local-llm.md) | Ollama integration, private summarization |
| Cloud LLM | [cloud-llm.md](cloud-llm.md) | When allowed, what context is sent |
| Redaction | [redaction.md](redaction.md) | Secret stripping before any processing |

---

## The Three Layers

```
Layer 1: Scripts
  Fast, deterministic, no privacy risk
  Use for: pattern matching, frequency counts, classification, scoring

Layer 2: Local LLM
  Private, flexible, slower
  Use for: summarization, quiz drafts, memory candidates

Layer 3: Cloud LLM
  Most capable, privacy risk, cost
  Use only when: talking mode, high-quality generation, user approved
```

---

## Decision Rule

```
Can a script do it? → Use script.
Can local LLM do it privately? → Use local LLM.
Neither? → Use cloud LLM with summary context only.
```

---

## Related Flows
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
