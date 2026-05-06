# Local LLM

**Status:** Concept  
**Stage:** 5

---

## What It Is

The local LLM layer uses locally running models (via Ollama) to perform language understanding tasks that require more than pattern matching — summarization, memory candidate generation, quiz drafts — without any data leaving the device.

---

## Why It Matters

Some tasks require language intelligence that scripts cannot provide:
- "Summarize what happened in this session" — needs understanding
- "Generate a quiz question about Flexbox" — needs generation
- "What is the key decision in this conversation?" — needs reasoning

These tasks must stay private. Local LLM solves this.

---

## Setup

Requires Ollama running locally:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull llama3.2:3b      # fast, light — for summarization
ollama pull mistral:7b        # better quality — for generation
ollama pull nomic-embed-text  # embeddings for semantic search
```

Stareha checks for Ollama on startup:
```bash
stareha status
# → Local LLM: ✓ (llama3.2:3b available)
# → Local LLM: ✗ (Ollama not running — install at ollama.ai)
```

---

## Tasks Handled by Local LLM

| Task | Model | Input | Output |
|------|-------|-------|--------|
| Session summary | llama3.2:3b | Redacted event list | 3–5 sentence summary |
| Terminal output summary | llama3.2:3b | Redacted terminal output | Key points |
| Weak concept extraction | mistral:7b | Session events + searches | Concept list |
| Memory candidate generation | mistral:7b | Pattern clusters | Human-readable memory text |
| Quiz draft generation | mistral:7b | Weak concept + level | 5 quiz questions |
| Exercise draft | mistral:7b | Concept + level + style | Exercise brief |
| Daily recap | llama3.2:3b | Session memories | Briefing text |
| Work session summary | llama3.2:3b | File + command events | Work summary |

---

## Privacy Guarantee

Local LLM receives:
- Processed, redacted summaries only
- Never: raw terminal logs, full file contents, private conversation text, passwords, keys

Redaction runs before any LLM call. No exceptions.

---

## Fallback Behavior

If Ollama is unavailable:
- Queue LLM tasks for when it becomes available
- Use scripts only in the meantime
- Mark memory candidates as `pending_local_llm` — not low confidence
- Never fall back to cloud LLM automatically

---

## Prompt Templates

All prompts are stored in `~/.stareha/prompts/` and are user-editable.

Example: session summary prompt

```
You are summarizing a developer's work session.

Events from the session (already redacted):
{{events_summary}}

Write a 3–5 sentence summary covering:
- What they worked on
- What they struggled with
- What they completed
- What is still open

Do not mention anything not in the events. Be factual.
```

---

## Related Files
- [Local Intelligence](README.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
- [Cloud LLM](cloud-llm.md)
