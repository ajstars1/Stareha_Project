---
name: stareha-doc-sync
version: 1.0.0
description: |
  Stareha documentation sync check. Verifies that SITEMAP.md, the relevant
  feature README, and the relevant _flows/ file are all up to date with
  what was just built or changed. Run at the end of every work session.
  Use when asked to "sync docs", "update stareha docs", "check docs",
  or "end of session". Enforced by CLAUDE.md: docs must be updated every session.
triggers:
  - sync stareha docs
  - check stareha documentation
  - end of session docs
  - update feature report
---

## Stareha Doc Sync

Read `SITEMAP.md` first to understand the current state of documentation.

```bash
echo "=== Stareha Doc Sync ==="
echo "Checking documentation currency..."
echo ""

# Show recently modified files (code changes that may need doc updates)
echo "Files changed in last session:"
git diff --name-only HEAD~1 2>/dev/null || git status --short

echo ""
echo "Current SITEMAP.md:"
cat SITEMAP.md | grep "^|" | head -40
```

After reading the output, check:

1. **For every file changed** — is there a corresponding feature report in `features/`? If not, create it.
2. **For every flow changed** — is the relevant `_flows/` file updated? If not, update it.
3. **Is SITEMAP.md current?** — does it list every file that exists? Add any missing entries.
4. **Is the feature's `README.md` current?** — does it accurately describe what was built?

Then update whatever is stale. The rule from `CLAUDE.md`:

> Every time we work on this project, documentation must be updated before the session ends.

Report what was updated and what was already current.
