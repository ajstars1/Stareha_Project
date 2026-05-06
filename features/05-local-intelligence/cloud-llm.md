# Cloud LLM

**Status:** Concept  
**Stage:** 3 (restricted) / 4 (exercise generation)

---

## What It Is

Cloud LLM (Claude via Anthropic API) is the most capable intelligence layer — used only when local capabilities are insufficient and the task value justifies the privacy tradeoff.

---

## When Cloud LLM Is Used

| Trigger | Justification |
|---------|--------------|
| User opens talking mode (`stareha talk`) | User explicitly requests AI conversation |
| Exercise generation | Creativity required, only learning profile summary sent |
| High-quality lesson generation | Local LLM quality too low for this complexity |
| Internet research synthesis (future) | Local models can't search the web |
| User requests explanation | User decides the privacy tradeoff |

---

## When Cloud LLM Is NOT Used

- Background learning runs (local LLM or scripts)
- Session summaries (local LLM)
- Memory candidate generation (local LLM)
- Quiz drafts (local LLM)
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
stareha talk
```

Opens an interactive conversation with Stareha. In this mode:
- Cloud LLM is used
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
