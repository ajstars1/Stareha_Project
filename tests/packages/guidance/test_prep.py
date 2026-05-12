import json
import pytest
from pathlib import Path
from packages.core.db import Store
from packages.guidance.prep import get_pending, _store_guidance, mark_delivered

@pytest.fixture
def store(tmp_path: Path) -> Store:
    db_path = tmp_path / "test.sqlite"
    store = Store(db_path)
    yield store
    store.close()

def test_get_pending_empty(store: Store) -> None:
    assert get_pending(store) == []

def test_get_pending_with_data(store: Store) -> None:
    _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    pending = get_pending(store)
    assert len(pending) == 1
    assert pending[0]["type"] == "quiz"
    assert pending[0]["title"] == "Test Quiz"
    assert pending[0]["content"] == {"q": "a"}
    assert pending[0]["status"] == "pending"

def test_get_pending_with_type_filter(store: Store) -> None:
    _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    _store_guidance(store, "briefing", "Test Briefing", {"b": "b"}, "scripts")

    quizzes = get_pending(store, gtype="quiz")
    assert len(quizzes) == 1
    assert quizzes[0]["type"] == "quiz"

    briefings = get_pending(store, gtype="briefing")
    assert len(briefings) == 1
    assert briefings[0]["type"] == "briefing"

def test_get_pending_ignores_delivered(store: Store) -> None:
    gid = _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    mark_delivered(store, gid)
    assert get_pending(store) == []

def test_get_pending_ordering(store: Store) -> None:
    import time
    gid1 = _store_guidance(store, "quiz", "Quiz 1", {"q": "a"}, "scripts")
    store._conn.execute("UPDATE prepared_guidance SET prepared_at = ? WHERE id = ?", (int(time.time()) - 100, gid1))
    store._conn.commit()

    gid2 = _store_guidance(store, "quiz", "Quiz 2", {"q": "b"}, "scripts")

    pending = get_pending(store)
    assert len(pending) == 2
    assert pending[0]["id"] == gid2  # Newest first
    assert pending[1]["id"] == gid1

def test_get_all_guidance(store: Store) -> None:
    import time
    from packages.guidance.prep import get_all_guidance
    gid1 = _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    store._conn.execute("UPDATE prepared_guidance SET prepared_at = ? WHERE id = ?", (int(time.time()) - 100, gid1))
    store._conn.commit()

    gid2 = _store_guidance(store, "briefing", "Test Briefing", {"b": "b"}, "scripts")
    mark_delivered(store, gid1)

    all_g = get_all_guidance(store)
    assert len(all_g) == 2
    assert all_g[0]["id"] == gid2  # Newest first
    assert all_g[1]["id"] == gid1

def test_get_all_guidance_limit(store: Store) -> None:
    from packages.guidance.prep import get_all_guidance
    for i in range(5):
        _store_guidance(store, "quiz", f"Quiz {i}", {"q": i}, "scripts")

    all_g = get_all_guidance(store, limit=3)
    assert len(all_g) == 3

def test_get_pending_invalid_json(store: Store) -> None:
    # Insert invalid json manually
    import uuid, time
    gid = str(uuid.uuid4())
    store._conn.execute(
        """INSERT INTO prepared_guidance
           (id, type, title, content, status, generated_by, prepared_at)
           VALUES (?, 'quiz', 'Bad JSON', '{bad json}', 'pending', 'scripts', ?)""",
        (gid, int(time.time())),
    )
    store._conn.commit()

    pending = get_pending(store)
    assert len(pending) == 1
    # content should remain a string if parsing fails
    assert pending[0]["content"] == "{bad json}"


def test_mark_completed(store: Store) -> None:
    from packages.guidance.prep import mark_completed
    gid = _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    mark_completed(store, gid)
    pending = get_pending(store)
    assert len(pending) == 0
    row = store._conn.execute("SELECT status FROM prepared_guidance WHERE id=?", (gid,)).fetchone()
    assert row["status"] == "completed"

def test_mark_skipped(store: Store) -> None:
    from packages.guidance.prep import mark_skipped
    gid = _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    mark_skipped(store, gid)
    row = store._conn.execute("SELECT status FROM prepared_guidance WHERE id=?", (gid,)).fetchone()
    assert row["status"] == "skipped"

def test_update_content(store: Store) -> None:
    from packages.guidance.prep import update_content
    gid = _store_guidance(store, "quiz", "Test Quiz", {"q": "a"}, "scripts")
    update_content(store, gid, {"q": "b", "ans": 42})

    pending = get_pending(store)
    assert pending[0]["content"] == {"q": "b", "ans": 42}
