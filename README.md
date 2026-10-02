# AI Agent Software Company: Starter Kit

A virtual software company in which **13 AI agents** fill the engineering roles and **you are the CEO / Product Owner**.
It runs on **Claude Code (subscription)**, uses **GitHub** as the office, and hosts products on **free-tier cloud**.

## What's inside
```
CLAUDE.md                       Company handbook (rules, org chart, Definition of Done)
.claude/agents/*.md             12 role agents (PM, UX, Architect, Tech Lead, BE, FE, QA,
                                Reviewer, Security, DevOps, SRE, Tech Writer)
.claude/skills/orchestrator/    Orchestrator / Scrum Master (/orchestrator)
.claude/settings.json           Safety guardrails (no force-push, no merge, no .env reads)
docs/WORKFLOW.md                Pipeline and the 4 CEO approval gates
docs/PRD.md, architecture.md    Templates the agents fill in
docs/adr/0000-template.md       Architecture Decision Record template
.github/                        Issue/PR templates and the @claude GitHub Action
```

## One-time setup (about 30 minutes)
1. **Install the tools**: Git, Node.js LTS, GitHub CLI (`brew install gh`), then `gh auth login`.
2. **Install Claude Code** and log in with your Claude Pro/Max subscription.
3. **Create a GitHub repo** for the product and push this kit:
   ```bash
   git init && git add . && git commit -m "chore: agent company starter kit"
   gh repo create my-product --private --source=. --push
   ```
4. **Protect `main`**: GitHub → Settings → Branches → require a PR, passing checks and 1 approval.
5. **(Optional) Agents on GitHub**: in Claude Code run `/install-github-app`. Then comment `@claude …` on any issue or PR.
6. **Free-tier accounts** (create them as the Architect asks): Vercel / Cloudflare, Supabase / Neon, Sentry, UptimeRobot.
   You enter keys and secrets yourself in the provider dashboards or GitHub Secrets; agents never handle them.

## Daily use
Open Claude Code in the repo folder:
| You type | What happens |
|---|---|
| `/orchestrator new <your product idea>` | PM writes the PRD and stops at ⛔ Gate 1 |
| `approve gate 1` then `/orchestrator continue` | UX and Architect design it, then stop at ⛔ Gate 2 |
| `approve gate 2` then `/orchestrator continue` | Tech Lead creates GitHub issues |
| `/orchestrator sprint` | Developers build in parallel, then QA, Review and Security check the PRs |
| You merge the approved PRs (⛔ Gate 3) | Then `/orchestrator continue` runs the staging deploy and docs |
| `approve gate 4` | Production release |
| `/orchestrator status` | Board summary anytime |

You can also call any agent directly, e.g. *"Use the architect agent to compare Supabase vs Firebase"* or
*"Use the backend-developer agent on issue #12"*.

## Tips
- **Start small**: build a tiny product first (e.g. a to-do app with login) to tune the prompts and rules.
- **Usage limits**: subscription plans have usage limits. Keep parallelism at 3 or fewer and issues small.
  Model choices in the agent files are `opus` for judgment roles, `sonnet` for builders and `haiku` for docs; change them to suit your plan.
- **Improve the company**: when an agent makes a repeated mistake, add a rule to `CLAUDE.md` or that agent's file.
- **Stay the CEO**: read the PRs before you merge. Agents are fast, but you own what ships.
