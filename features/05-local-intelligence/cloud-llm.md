# Cloud LLM

**Status:** Built as restricted optional layer
**Stage:** 5

---

## What It Is

Cloud LLM (Claude via Anthropic API) is the most capable intelligence layer. It is not enabled by beginner setup and is used only when a command explicitly allows cloud fallback or a future consent flag enables it for a specific feature.

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

## Model Used

Default: `claude-sonnet-4-6` (as per ai-rag.md rules)

For simple tasks that go to cloud: `claude-haiku-4-5`

---

## Talking Mode

```bash
stareha talk --cloud
```

Opens an interactive conversation with Stareha. In this mode:
- Local LLM is tried first; Claude is used as fallback when `--cloud` is passed and `ANTHROPIC_API_KEY` is set
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
