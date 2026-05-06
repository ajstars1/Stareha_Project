# Ledger Pipeline

**Status:** Concept  
**Stage:** 3

---

## What It Is

The pipeline is the process that transforms raw events into provenance-tracked memory candidates.

---

## Full Pipeline

See also: [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)

```
Step 1: Raw event arrives
  ↓
Step 2: Redaction
  Strip secrets, tokens, passwords
  ↓
Step 3: Write to ledger_events (immutable)
  Event is permanently recorded here, no further modification
  ↓
Step 4: Classification
  Assign type, source, project, session
  ↓
Step 5: Importance scoring
  Score 0.0–1.0, skip if < 0.3
  ↓
Step 6: Deduplication
  Compare to existing memory candidates
  Skip if substantially duplicate
  ↓
Step 7: Summarization
  Scripts → local LLM → cloud LLM (per intelligence policy)
  ↓
Step 8: Memory candidate creation
  {content, source, evidence_ids, model_used, confidence, sensitivity}
  ↓
Step 9: Inbox
  Candidate queued for user review
```

---

## Step Details

### Step 1–2: Redaction
Runs on every event before storage. No exceptions.

Patterns stripped:
- API keys: `sk-*`, `ghp_*`, `AKIA*`, any `_KEY=`, `_TOKEN=`, `_SECRET=`
- Passwords: after `-p`, `--password`, `password=`
- Tokens in URLs: `?token=`, `?api_key=`, `Authorization: Bearer`

### Step 3: Ledger Write
The raw event (post-redaction) is written to `ledger_events`. This record is never modified.

### Step 4: Classification
Rule-based classification into:
- `command_run` (terminal)
- `file_edit` (file_watcher)
- `research_session` (browser)
- `ai_session` (claude_code)
- `user_note` (manual input)

### Step 5: Importance Scoring

```
score = base_score
  + (frequency_bonus if occurrences >= 3)
  + (error_fix_bonus if error→fix pair)
  + (explicit_user_signal_bonus if user stated)
  - (trivial_command_penalty if command in ignore_list)
```

Skip if score < 0.3.

### Step 6: Deduplication
Hash-based: compare content to existing candidates.
If similarity > 0.85 with existing candidate → increment evidence count, skip new candidate.

### Step 7: Summarization
- Simple patterns (sequences, frequencies): scripts only
- Complex patterns (decisions, context): local LLM
- High-quality explanations for guidance: cloud LLM (with permission)

### Step 8: Memory Candidate

```sql
INSERT INTO memory_candidates (
  id, content, source, evidence_ids,
  learning_run_id, model_used, confidence, sensitivity, status
)
```

### Step 9: Inbox
Candidate appears in `stareha memory inbox` with status `pending`.

---

## Related Files
- [Learning Ledger](README.md)
- [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
- [Redaction](../05-local-intelligence/redaction.md)
