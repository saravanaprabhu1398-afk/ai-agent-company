# Delivery Workflow

```
CEO idea
  │
  ▼
Product Manager ──► docs/PRD.md + epics/stories
  │                                         ⛔ GATE 1: CEO approves scope
  ▼
UX Designer ──► docs/ux.md     Architect ──► docs/architecture.md + docs/adr/*
  │                                         ⛔ GATE 2: CEO approves design & stack
  ▼
Tech Lead ──► GitHub issues (status:ready, role:*, size:*), project board
  │
  ▼  (developers can run in parallel on independent issues)
Backend / Frontend Developer ──► branch → code + tests → PR
  │
  ▼
QA Engineer + Code Reviewer + Security Engineer ──► review the PR
  │   └─ changes requested → developer fixes (max 3 cycles, then needs-ceo)
  │   └─ all three signed off → orchestrator auto-merges (sensitive PRs: ⛔ GATE 3, CEO merges)
  ▼
DevOps Engineer ──► CI/CD → staging deploy
  │                                         ⛔ GATE 4: CEO approves production
  ▼
SRE monitors · Tech Writer updates docs/changelog · PM plans the next sprint
```

## Gate checklist for the CEO
| Gate | Check |
|---|---|
| 1 Scope | Problem is clear, MVP is small, acceptance criteria are testable |
| 2 Design | Stack fits free tier, data model makes sense, no over-engineering |
| 3 Merge | Only for sensitive PRs (see CLAUDE.md merge policy). CI is green, all three sign-off labels are present, the PR does what the issue asked |
| 4 Production | Staging works, rollback plan exists, no secrets exposed |

## Escalation
Agents add the `needs-ceo` label and @mention the CEO when they're blocked, after 3 failed
review cycles, for anything that costs money, or before any destructive or production action.
