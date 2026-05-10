# Intelligence Policy Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Updated
**Stage:** 1 (scripts), 5 (local LLM), 3 (cloud LLM)

---

## Core Rule

```
Scripts first → Local LLM second → Cloud LLM only when needed.
```

Use the cheapest, safest, most private layer that can do the job.

---

## Decision Tree

```
Task arrives
  ↓
Can a deterministic script handle this?
  YES → Use script. Done.
  NO ↓

Is local LLM (Ollama) available and sufficient?
  YES → Use local LLM. Done.
  NO ↓

Did the user explicitly allow cloud for this command?
    YES → Use cloud LLM with summary context only
    NO  → Use scripts/templates, queue for local LLM, or skip
```

---

## Layer 1: Deterministic Scripts

Use for tasks that have clear rules.

| Task | How |
|------|-----|
| File change detection | inotify / fswatch |
| Git status / active project | `git status`, directory heuristics |
| Command frequency | Count occurrences in event store |
| Command failure detection | Exit code check |
| Secret redaction | Regex patterns (API keys, tokens, passwords) |
| Browser domain stats | URL parsing, domain counting |
| App usage counting | Process list polling |
| Event classification | Rule-based (command type, source) |
| Importance scoring | Frequency + error + explicit signal formula |
| Deduplication | Hash-based dedup on content |

Scripts run synchronously, in-process, with no external calls.

---

## Layer 2: Local LLM

Use for tasks that require language understanding but must stay private.

Requires: Ollama running locally with a suitable model.

Recommended models:
- `llama3.2:3b` — fast, light, good for summarization
- `mistral:7b` — better quality for complex tasks
- `nomic-embed-text` — embeddings for semantic search

| Task | Model |
|------|-------|
| Session summary | llama3.2:3b |
| Terminal output summary | llama3.2:3b |
| Weak concept extraction | mistral:7b |
| Memory candidate generation | mistral:7b |
| Quiz draft generation | mistral:7b |
| Exercise draft generation | mistral:7b |
| Daily recap | llama3.2:3b |
| Work session summary | llama3.2:3b |

Local LLM receives:
- Processed, redacted summaries
- Never raw terminal logs
- Never full file contents
- Never private conversation text

---

## Layer 3: Cloud LLM

Use only when:
- User explicitly passes a cloud-enabled command, such as `stareha talk --cloud`
- User explicitly requests cloud fallback for a task, such as `stareha quiz --cloud <topic>`
- Future setup/config has recorded explicit cloud consent for a specific feature

**Active provider** is selected from five options: `claude_code_oauth` (claude.ai subscription, reads `~/.claude/.credentials.json`), `anthropic` (API key), `gemini`, `openai`, or `groq`. Set via `stareha llm setup` or during `stareha setup`.

Cloud LLM receives:
- Summaries only — never raw data
- Stripped of private details
- Context-scoped to current task

**What cloud LLM gets (example):**
```
User is learning Flexbox. They struggled with alignment and searched 
examples repeatedly. Their preferred style is project-based. 
Generate a beginner-friendly exercise.
```

**What cloud LLM does NOT get:**
```
5,000 lines of terminal output and full browser history
```

---

## Cloud Context Policy

Before sending to cloud LLM:
1. Build a summary from local memories only
2. Include: goal, weak concepts, recent struggles, preferred style
3. Exclude: raw events, file contents, private conversations
4. Maximum context: 2,000 tokens

---

## Fallback Rules

| Situation | Action |
|-----------|--------|
| Local LLM unavailable | Queue task, use scripts only |
| Cloud LLM unavailable | Use local LLM draft or script/template fallback |
| All layers unavailable | Use scripts only, surface raw data to user |

Beginner setup does not enable cloud AI. Cloud access requires both an API key and an explicit cloud-enabled command or future consent flag.

---

## Related Files
- [Local LLM](../features/05-local-intelligence/local-llm.md)
- [Cloud LLM](../features/05-local-intelligence/cloud-llm.md)
- [Redaction](../features/05-local-intelligence/redaction.md)
- [Product Principles](../product/principles.md) — Principle 4
