import sqlite3
import uuid
import time
from pathlib import Path
from typing import Optional

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Store:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(SCHEMA_PATH.read_text())
        self._conn.commit()
        self._run_migrations()

    def _run_migrations(self) -> None:
        """Add columns / tables that didn't exist in earlier schema versions."""
        changed = False
        for table, col, typedef in [
            ("memory_candidates", "learning_run_id", "TEXT"),
            ("memories",          "learning_run_id", "TEXT"),
        ]:
            existing = {row[1] for row in self._conn.execute(f"PRAGMA table_info({table})")}
            if col not in existing:
                self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")
                changed = True
        if changed:
            self._conn.commit()

    # ── Stage 4 helpers ───────────────────────────────────────────────────────

    def write_user_note(self, text: str, tags: list[str] | None = None) -> str:
        import uuid, json
        nid = str(uuid.uuid4())
        self._conn.execute(
            "INSERT INTO user_notes (id, content, tags, created_at) VALUES (?,?,?,?)",
            (nid, text, json.dumps(tags or []), int(time.time())),
        )
        self._conn.commit()
        return nid

    def write_event(self, type: str, source: str, content: str,
                    project: Optional[str] = None, session_id: Optional[str] = None,
                    redacted: bool = False) -> str:
        id = str(uuid.uuid4())
        self._conn.execute(
            "INSERT INTO events (id,type,source,project,content,session_id,redacted,created_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (id, type, source, project, content, session_id, int(redacted), int(time.time())),
        )
        self._conn.commit()
        return id

    def count_events(self, source: Optional[str] = None, since: Optional[int] = None) -> int:
        q, params = "SELECT count(*) FROM events WHERE 1=1", []
        if source: q += " AND source=?"; params.append(source)
        if since:  q += " AND created_at>=?"; params.append(since)
        return self._conn.execute(q, params).fetchone()[0]

    def get_events(self, source: Optional[str] = None, limit: int = 100) -> list:
        q, params = "SELECT * FROM events WHERE 1=1", []
        if source: q += " AND source=?"; params.append(source)
        q += " ORDER BY created_at DESC LIMIT ?"; params.append(limit)
        return self._conn.execute(q, params).fetchall()

    def start_session(self, goal: Optional[str] = None, type: str = "work",
                      project: Optional[str] = None) -> str:
        id = str(uuid.uuid4())
        self._conn.execute(
            "INSERT INTO sessions (id,goal,type,project,status,started_at) VALUES (?,?,?,?,'active',?)",
            (id, goal, type, project, int(time.time())),
        )
        self._conn.commit()
        self.set_meta("active_session_id", id)
        return id

    def end_session(self, session_id: str) -> None:
        self._conn.execute(
            "UPDATE sessions SET status='ended', ended_at=? WHERE id=?",
            (int(time.time()), session_id),
        )
        self._conn.commit()
        self.set_meta("active_session_id", "")

    def get_active_session(self) -> Optional[sqlite3.Row]:
        sid = self.get_meta("active_session_id")
        if not sid:
            return None
        return self._conn.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()

    def set_meta(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO meta (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self._conn.commit()

    def get_meta(self, key: str) -> Optional[str]:
        row = self._conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def close(self) -> None:
        self._conn.close()
