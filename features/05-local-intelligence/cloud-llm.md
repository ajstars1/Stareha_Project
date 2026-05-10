# Cloud LLM

**Status:** Built — multi-provider, restricted optional layer
**Stage:** 5

---

## What It Is

Cloud LLM is the most capable intelligence layer. It supports five providers and is not enabled by beginner setup. It is used only when a command explicitly allows cloud fallback or the user has configured a provider through `stareha setup` or `stareha llm setup`.

---

## Supported Providers

| Provider ID | Display name | Auth |
|-------------|-------------|------|
| `claude_code_oauth` | Claude Code (claude.ai) | OAuth — reads `~/.claude/.credentials.json`, no API key needed |
| `anthropic` | Claude (Anthropic) | API key — `console.anthropic.com` |
| `gemini` | Gemini (Google) | API key — `aistudio.google.com` |
| `openai` | OpenAI (GPT-4o) | API key — `platform.openai.com` |
| `groq` | Groq | API key — `console.groq.com` |

Active provider stored as `active_cloud_provider` in `~/.stareha/config.json`. Per-provider credentials stored under `llm_providers.<id>`.

### Claude Code OAuth (recommended)
Uses your existing claude.ai Pro or Max subscription — no separate API key.
The setup wizard checks `~/.claude/.credentials.json` (written by Claude Code CLI on login). Token expiry is checked at call time with a 120-second buffer.
```bash
stareha llm setup               # select "Cloud" → "Claude Code (claude.ai)" → done
```

### API key providers
```bash
stareha llm setup               # select "Cloud" → pick provider → paste key
```

### Status and switching
```bash
stareha llm status              # show connected providers + active one
stareha llm setup               # re-run to add or switch provider
```

---

## When Cloud LLM Is Used

| Trigger | Justification |
|---------|--------------|
| `stareha talk --cloud` | User explicitly allows Claude fallback for conversation |
| `stareha quiz --cloud <topic>` | User explicitly allows Claude fallback for that quiz |
| Future cloud-enabled exercise command | Creativity required, only learning profile summary sent |
| Future internet research synthesis | Local models cannot search the web |
| User requests cloud explanation | User decides the privacy tradeoff |

---

## When Cloud LLM Is NOT Used

- Background learning runs (local LLM or scripts)
- Session summaries (local LLM)
- Memory candidate generation (local LLM)
- Quiz drafts unless `--cloud` is passed
- Pattern extraction (scripts)
- Anything that can be done locally

---

## Privacy Policy for Cloud LLM

Cloud LLM receives ONLY:
- Summaries derived from memories (never raw events)
- Learning profile summary (goals, weak concepts, level)
- Current task context

Cloud LLM NEVER receives:
- Raw terminal logs
- Full file contents
- Raw Claude Code conversations
- Browser history
- API keys or secrets
- Full command history

### Example: What is sent for exercise generation

```
User is learning web development. Skill level: beginner-intermediate.
Weak concept: CSS Flexbox alignment (6 searches, 2 incomplete exercises).
Learning style: project-based.
Goal: Build responsive layouts.

Generate a beginner-appropriate mini-project exercise using CSS Flexbox.
Requirements: under 30 minutes, practical, tests alignment concepts.
```

### Example: What is NOT sent

```
[not sent]
Full browser history of 200 URLs visited this week.
All 500 terminal commands from the last 30 days.
Private conversations from Claude Code.
```

---

## Default Models per Provider

| Provider | Default model |
|----------|--------------|
| `claude_code_oauth` | `claude-sonnet-4-6` |
| `anthropic` | `claude-sonnet-4-6` |
| `gemini` | `gemini-3.1-flash-lite` |
| `openai` | `gpt-4o` |
| `groq` | `llama-3.1-70b-versatile` |

Override per-provider with `save_config({"provider_configs": {"groq": {"model": "llama3-70b-8192"}}})`.

---

## Talking Mode

```bash
stareha talk --cloud
```

Opens an interactive conversation with Stareha. In this mode:
- Local LLM is tried first; active cloud provider is used as fallback when `--cloud` is passed and that provider has credentials
- Context sent = session summaries + relevant memories (not raw data)
- User is informed that cloud LLM is being used
- Conversation history stored locally only

---

## Cost Management

- Cloud LLM calls are logged with token counts
- User can see usage: `stareha usage cloud`
- User can set a monthly token limit: `stareha config set cloud.monthly_limit 100000`

---

## Related Files
- [Local Intelligence](README.md)
- [Local LLM](local-llm.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
- [Product Principles](../../product/principles.md) — Principle 4
