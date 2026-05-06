-- Stareha SQLite Schema
-- Source of truth. All migrations reference this file.
-- Run: sqlite3 ~/.stareha/db.sqlite < schema.sql

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Immutable event log. Never modified after write.
CREATE TABLE IF NOT EXISTS events (
    id          TEXT    PRIMARY KEY,
    type        TEXT    NOT NULL,   -- 'command_run', 'file_edit', 'ai_session', 'browser_visit', 'user_note'
    source      TEXT    NOT NULL,   -- 'terminal', 'files', 'claude_code', 'browser', 'manual'
    project     TEXT,               -- associated project path (nullable)
    content     TEXT    NOT NULL,   -- redacted raw content
    session_id  TEXT,
    redacted    INTEGER NOT NULL DEFAULT 0,
    created_at  INTEGER NOT NULL    -- unix timestamp
);

CREATE INDEX IF NOT EXISTS idx_events_source     ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_session    ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_type       ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_created    ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_events_project    ON events(project);

-- Sessions (learning or work)
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT    PRIMARY KEY,
    goal        TEXT,               -- user-stated goal (nullable for auto-detected)
    type        TEXT    NOT NULL DEFAULT 'work',  -- 'work' | 'learning'
    project     TEXT,
    status      TEXT    NOT NULL DEFAULT 'active', -- 'active' | 'ended'
    started_at  INTEGER NOT NULL,
    ended_at    INTEGER
);

-- Memory candidates awaiting inbox review
CREATE TABLE IF NOT EXISTS memory_candidates (
    id              TEXT    PRIMARY KEY,
    content         TEXT    NOT NULL,
    type            TEXT    NOT NULL,   -- 'command_pattern', 'project_context', 'error_fix', etc.
    source          TEXT    NOT NULL,
    project         TEXT,
    evidence_ids    TEXT    NOT NULL,   -- JSON array of event IDs
    model_used      TEXT    NOT NULL,   -- 'pattern_extractor' | 'local_llm' | 'cloud_llm'
    confidence      REAL    NOT NULL,
    sensitivity     TEXT    NOT NULL DEFAULT 'normal', -- 'low' | 'normal' | 'high'
    status          TEXT    NOT NULL DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected' | 'edited'
    created_at      INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_candidates_status ON memory_candidates(status);

-- Approved memories with full provenance
CREATE TABLE IF NOT EXISTS memories (
    id              TEXT    PRIMARY KEY,
    content         TEXT    NOT NULL,
    type            TEXT    NOT NULL,
    source          TEXT    NOT NULL,
    project         TEXT,
    evidence_ids    TEXT    NOT NULL,   -- JSON array of event IDs
    model_used      TEXT    NOT NULL,
    confidence      REAL    NOT NULL,
    sensitivity     TEXT    NOT NULL DEFAULT 'normal',
    user_edited     INTEGER NOT NULL DEFAULT 0,
    approved_at     INTEGER NOT NULL,
    created_at      INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memories_type    ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_source  ON memories(source);
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);

-- FTS5 full-text search over memories
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    content='memories',
    content_rowid='rowid'
);

-- User feedback on candidates (for learning improvement)
CREATE TABLE IF NOT EXISTS memory_feedback (
    id              TEXT    PRIMARY KEY,
    candidate_id    TEXT    NOT NULL,
    action          TEXT    NOT NULL,   -- 'approved' | 'rejected' | 'edited' | 'marked_wrong'
    edit_content    TEXT,               -- corrected text if edited
    feedback_at     INTEGER NOT NULL
);

-- Prepared guidance — briefings, quizzes, exercises for next session
CREATE TABLE IF NOT EXISTS prepared_guidance (
    id           TEXT    PRIMARY KEY,
    type         TEXT    NOT NULL,   -- 'briefing' | 'quiz' | 'exercise' | 'note'
    title        TEXT    NOT NULL,
    content      TEXT    NOT NULL,   -- JSON payload
    status       TEXT    NOT NULL DEFAULT 'pending', -- 'pending' | 'delivered' | 'completed' | 'skipped'
    generated_by TEXT    NOT NULL DEFAULT 'scripts', -- 'scripts' | 'cloud_llm' | 'local_llm'
    prepared_at  INTEGER NOT NULL,
    delivered_at INTEGER,
    session_id   TEXT                -- which session triggered prep (nullable = manual)
);

CREATE INDEX IF NOT EXISTS idx_guidance_status ON prepared_guidance(status);
CREATE INDEX IF NOT EXISTS idx_guidance_type   ON prepared_guidance(type);

-- User notes (manual input — highest-signal weak concept source)
CREATE TABLE IF NOT EXISTS user_notes (
    id         TEXT    PRIMARY KEY,
    content    TEXT    NOT NULL,
    tags       TEXT,                -- JSON array of tags (e.g. ["struggling", "concept"])
    created_at INTEGER NOT NULL
);

-- Learning run audit log (one row per run_learning() call)
CREATE TABLE IF NOT EXISTS learning_runs (
    id                  TEXT    PRIMARY KEY,
    session_id          TEXT,
    started_at          INTEGER NOT NULL,
    completed_at        INTEGER,
    events_processed    INTEGER,
    candidates_generated INTEGER,
    model_used          TEXT    NOT NULL DEFAULT 'pattern_extractor',
    status              TEXT    NOT NULL DEFAULT 'running'  -- 'running' | 'completed' | 'failed'
);

CREATE INDEX IF NOT EXISTS idx_runs_started ON learning_runs(started_at);

-- Key-value store for daemon state
CREATE TABLE IF NOT EXISTS meta (
    key     TEXT    PRIMARY KEY,
    value   TEXT    NOT NULL
);
