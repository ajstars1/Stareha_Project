---
name: stareha-stage-check
version: 1.0.0
description: |
  Stareha stage readiness check. Reviews whether the current stage is complete
  and whether it's safe to begin the next stage. Checks: feature reports written,
  flows up to date, code matches documentation, success criteria met.
  Use when asked to "check stage readiness", "ready for next stage",
  "is stage N done", or "can we move to stage N".
triggers:
  - check stage readiness
  - ready for next stage
  - is stage done
  - move to next stage
  - stareha stage check
---

## Stareha Stage Readiness Check

```bash
echo "=== Stareha Stage Readiness Check ==="
echo "Current git branch: $(git branch --show-current)"
echo ""
echo "Recent commits:"
git log --oneline -10
echo ""
echo "Uncommitted changes:"
git status --short
```

Read `product/roadmap.md` to understand the current stage and its success criteria.

Then check for each item in the current stage:

### Documentation Gate (must pass before moving to next stage)
- [ ] All feature reports for this stage are written and accurate
- [ ] All `_flows/` files for this stage are updated
- [ ] SITEMAP.md lists all new files created this stage
- [ ] CLAUDE.md in project root is current

### Code Gate
- [ ] All success criteria from `product/roadmap.md` are met
- [ ] No TODO comments left from this stage's implementation
- [ ] Tests exist for core logic (unit tests for pure functions)
- [ ] Feature works end-to-end as described in the feature README

### Principle Gate (product/principles.md — check all 7)
- [ ] P1: Learning workflows, not private lives
- [ ] P2: Raw data stays local
- [ ] P3: No memory without provenance
- [ ] P4: Scripts first, local LLM second, cloud only when needed
- [ ] P5: Suggest autonomously, act with permission
- [ ] P6: User control is mandatory
- [ ] P7: Quiet until useful

Report: what passed, what failed, what needs to be done before advancing.
