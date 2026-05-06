"""
Prompt template manager — Stage 5.

Default prompts are bundled here. On first use they're written to
~/.stareha/prompts/ so the user can edit them. If a user-edited
version exists it takes precedence over the bundled default.
"""
from pathlib import Path
from typing import Optional

_PROMPTS_DIR = Path.home() / ".stareha" / "prompts"

# ── Default prompt templates ──────────────────────────────────────────────────

DEFAULTS: dict[str, str] = {
    "session-summary": """\
You are summarizing a developer's work session. Be factual and brief.

Session goal: {goal}
Duration: {duration}
Total events: {event_count}
Commands run ({cmd_count} unique): {commands}

Write 2-3 sentences covering:
- What the developer worked on
- Any visible patterns or struggles
- What is likely still open

Do not invent details not present above. Do not use filler phrases.""",

    "quiz-generation": """\
Generate a {n}-question quiz about: {concept}

User level: {level}
Context: {context}

Return ONLY valid JSON (no markdown fences):
{{
  "topic": "{concept}",
  "level": "{level}",
  "reason": "one sentence why this is being quizzed",
  "questions": [
    {{
      "type": "multiple_choice",
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "A",
      "explanation": "..."
    }},
    {{
      "type": "short_answer",
      "question": "...",
      "answer": "expected answer",
      "explanation": "..."
    }}
  ]
}}

Mix: {mc} multiple choice, {sa} short answer.
Test practical understanding, not trivia. Keep explanations to 1 sentence.""",

    "memory-enrichment": """\
Rewrite this developer memory as a clear, concise observation.

Raw pattern: {raw_pattern}
Project: {project}
Observation count: {count}

Write ONE sentence that captures what this tells us about the developer's workflow.
Be specific. Do not add words like "it appears" or "it seems".
Return only the sentence, nothing else.""",

    "talk-system": """\
You are Stareha, a local-first AI companion for developers.
You help the user understand their own work patterns, learning progress, and next steps.

What you know about this user (from approved memories):
{memory_context}

Rules:
- Answer concisely — this is a CLI conversation
- Reference specific memories when relevant
- If you don't know something, say so — don't invent
- Never ask for or repeat private data (passwords, keys, tokens)
- Raw data about the user stays local — you only have summaries""",
}


def _prompt_path(name: str) -> Path:
    return _PROMPTS_DIR / f"{name}.txt"


def get(name: str, **kwargs) -> str:
    """
    Return the prompt template for `name`, with {placeholders} filled in.
    Loads from ~/.stareha/prompts/{name}.txt if it exists, else uses bundled default.
    """
    path = _prompt_path(name)
    if path.exists():
        template = path.read_text()
    else:
        template = DEFAULTS.get(name, "")
        if not template:
            raise KeyError(f"Unknown prompt template: {name}")

    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template  # missing keys — return raw template

    return template


def export_defaults() -> None:
    """Write all default prompts to ~/.stareha/prompts/ (does not overwrite existing)."""
    _PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in DEFAULTS.items():
        path = _prompt_path(name)
        if not path.exists():
            path.write_text(content)


def list_prompts() -> list[dict]:
    """Return info about each prompt — name, source (bundled/custom), path."""
    result = []
    for name in DEFAULTS:
        path = _prompt_path(name)
        result.append({
            "name": name,
            "source": "custom" if path.exists() else "bundled",
            "path": str(path) if path.exists() else None,
        })
    return result
