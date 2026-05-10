# Cloud LLM

**Status:** Built — multi-provider, restricted optional layer
**Stage:** 5

---

## What It Is

Cloud LLM is the most capable intelligence layer. It supports six providers and is not enabled by beginner setup. It is used only when a command explicitly allows cloud fallback or the user has configured a provider through `stareha setup` or `stareha cloud-llm`.

---

## Supported Providers

| Provider ID | Display name | Auth |
|-------------|-------------|------|
| `claude_code_oauth` | Claude Code (claude.ai subscription) | PKCE OAuth — no API key needed |
| `anthropic` | Anthropic API key | `ANTHROPIC_API_KEY` or config |
| `openai` | OpenAI | `OPENAI_API_KEY` or config |
| `groq` | Groq | `GROQ_API_KEY` or config |
| `gemini` | Google Gemini | `GEMINI_API_KEY` or config |
| `openai_compat` | Custom OpenAI-compatible endpoint | API key + base URL |

The active provider is stored as `cloud_provider` in `~/.stareha/config.json`. Per-provider credentials live under `provider_configs.<id>`.

### Claude Code OAuth (recommended)
Uses your existing claude.ai Pro or Max subscription — no separate API key.
```bash
stareha cloud-llm connect       # opens browser → paste code → tokens saved
```
Token storage: `~/.stareha/claude_code_oauth.json` + `provider_configs.claude_code_oauth` in config.
Tokens auto-refresh 120 seconds before expiry.

### API key providers
```bash
stareha cloud-llm set-key anthropic   # or openai / groq / gemini
stareha cloud-llm set-key openai_compat  # also prompts for base_url + model
```

### Switching providers
```bash
stareha cloud-llm list          # table of all providers with status
stareha cloud-llm use groq      # set active provider
stareha cloud-llm status        # show active provider + model
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
| `anthropic` | `claude-haiku-4-5-20251001` |
| `openai` | `gpt-4o-mini` |
| `groq` | `llama3-8b-8192` |
| `gemini` | `gemini-1.5-flash` |
| `openai_compat` | (user-specified) |

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
