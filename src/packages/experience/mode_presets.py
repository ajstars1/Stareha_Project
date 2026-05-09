"""Mode presets for the Stareha product experience."""

DEFAULT_MODE = "learner"

MODE_PRESETS: dict[str, dict] = {
    "learner": {
        "label": "Learner",
        "status": "stable_alpha",
        "recommended": True,
        "description": (
            "For learning programming, AI, technical skills, or project-based study."
        ),
        "default_sources": ["terminal", "file_metadata", "manual_notes"],
        "main_artifact": "learning_card",
    },
    "companion": {
        "label": "Companion",
        "status": "experimental",
        "recommended": False,
        "description": "For broader work continuity, personal projects, and daily progress.",
        "default_sources": ["terminal", "file_metadata", "manual_notes"],
        "main_artifact": "work_brief",
    },
    "researcher": {
        "label": "Researcher",
        "status": "experimental",
        "recommended": False,
        "description": "For reading, research sessions, saved pages, notes, and synthesis.",
        "default_sources": ["manual_notes"],
        "main_artifact": "research_summary",
    },
}


def get_mode(mode: str | None) -> dict:
    """Return a mode preset, falling back to learner."""
    return MODE_PRESETS.get(mode or DEFAULT_MODE, MODE_PRESETS[DEFAULT_MODE])

