# Redaction

**Status:** Concept  
**Stage:** 1

---

## What It Is

Redaction is the first step in every data pipeline — stripping secrets, tokens, passwords, and sensitive patterns from raw events before they are stored or processed.

---

## Why It Matters

Redaction is non-negotiable. If a secret leaks into the event store, it could:
- Be sent to a local LLM
- Eventually reach a cloud LLM
- Persist indefinitely in the database

Redaction runs before anything else. No exceptions.

---

## What Is Redacted

| Pattern | What it catches | Replacement |
|---------|----------------|-------------|
| `sk-[a-zA-Z0-9]{20,}` | OpenAI API keys | `[REDACTED_API_KEY]` |
| `ghp_[a-zA-Z0-9]{36}` | GitHub personal tokens | `[REDACTED_GITHUB_TOKEN]` |
| `AKIA[A-Z0-9]{16}` | AWS access keys | `[REDACTED_AWS_KEY]` |
| `(-p\|--password)\s+\S+` | Passwords in commands | `[REDACTED_PASSWORD]` |
| `Bearer\s+[a-zA-Z0-9._-]+` | Bearer tokens | `Bearer [REDACTED_TOKEN]` |
| `(API_KEY\|TOKEN\|SECRET\|PASSWORD)=[^\s]+` | ENV var assignments | `KEY=[REDACTED]` |
| `https?://[^?\s]+[?&]token=[^\s&]+` | Token in URLs | URL with `token=[REDACTED]` |
| Private key blocks | `-----BEGIN ... KEY-----` blocks | `[REDACTED_PRIVATE_KEY]` |

---

## Redaction Rules

1. Redaction runs before any event is written to the database
2. Redaction runs before any LLM call (belt and suspenders)
3. Redacted content is never reconstructable — the original is never stored
4. If redaction is uncertain, the entire field is masked: `[POSSIBLY_SENSITIVE_CONTENT]`

---

## Implementation

```python
import re

REDACTION_PATTERNS = [
    (r'\bsk-[a-zA-Z0-9]{20,}\b', '[REDACTED_API_KEY]'),
    (r'\bghp_[a-zA-Z0-9]{36}\b', '[REDACTED_GITHUB_TOKEN]'),
    (r'\bAKIA[A-Z0-9]{16}\b', '[REDACTED_AWS_KEY]'),
    (r'(-p|--password)\s+\S+', r'\1 [REDACTED_PASSWORD]'),
    (r'Bearer\s+[a-zA-Z0-9._\-]+', 'Bearer [REDACTED_TOKEN]'),
    (r'(API_KEY|TOKEN|SECRET|PASSWORD)=[^\s]+', r'\1=[REDACTED]'),
    (r'-----BEGIN [A-Z ]+KEY-----[\s\S]+?-----END [A-Z ]+KEY-----', '[REDACTED_PRIVATE_KEY]'),
]

def redact(text: str) -> str:
    for pattern, replacement in REDACTION_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text
```

---

## Redaction Audit Log

Every redaction is logged (not what was redacted — just that it happened):

```json
{
  "event_id": "evt_abc123",
  "redactions_applied": 2,
  "patterns_matched": ["API_KEY", "Bearer token"],
  "redacted_at": 1746700000
}
```

This lets users know when sensitive content was detected and stripped.

---

## User-Defined Patterns

Users can add custom redaction patterns:

```bash
stareha config redact add "MY_INTERNAL_TOKEN=[^\s]+"
stareha config redact list
stareha config redact remove 0
```

---

## Related Files
- [Local Intelligence](README.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
- [Ledger Pipeline](../03-learning-ledger/pipeline.md)
