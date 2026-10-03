# ADR-0002: Host on Vercel Hobby with Neon Postgres (Free)
- Status: Accepted (Gate 2, 2026-10-03)
- Date: 2026-10-03
- Deciders: architect, CEO

## Context
PRD G3/M5 require USD 0/month. Expected scale is a few hundred users. Data is relational (users, sessions, to-dos with ownership) and needs unique and foreign-key constraints. The app is a Node.js Next.js server (ADR-0001) that hashes passwords with Argon2id, which needs tens of milliseconds of CPU per hash. Limits below were checked on vendor sites on 2026-10-03.

## Options considered
| Option | Pros | Cons | Free tier? |
|---|---|---|---|
| **Vercel Hobby (app) + Neon Free (Postgres)** | Zero-config Next.js, preview deploy per PR, instant rollback; Neon is permanent free Postgres with branching (staging branch) and no card | Vercel Hobby is non-commercial only and keeps logs 1 h; Neon scales to zero after 5 min (cold start) and has 100 CU-hours/month | Vercel: 1M invocations, 4 h Active CPU, 100 GB transfer/month. Neon: 100 CU-h, 1 GB storage (plan for 0.5 GB), 5 GB egress, 10 branches |
| Cloudflare Workers/Pages + D1 | Generous requests; SQLite D1 free | Free Workers CPU limit (10 ms per request) is too small for Argon2/bcrypt; Next.js needs an adapter; SQLite dialect differs from CI Postgres | Yes, but CPU limit blocks password hashing |
| Render Free web service + Render/Neon Postgres | Plain Node server, commercial use allowed | Free web service sleeps after inactivity (slow cold start, tens of seconds); Render free Postgres expires after a limited period | Partly |
| Supabase Free (Postgres) instead of Neon | Postgres + extras | Project pauses after a week of inactivity; we would not use its extras | Yes |
| Oracle Cloud Always Free VM | Always-on, generous | We would operate a VM (patching, TLS, deploys): too much ops for agents | Yes |

## Decision
- App: Vercel Hobby, function region `iad1`, Node.js runtime. Production deploys from `main`; preview deploys per PR act as staging.
- Database: Neon Free, Postgres 17, region `aws-us-east-1`, branches `main` (production) and `staging`. Compute autoscaling capped at 0.25–0.5 CU to protect CU-hours. Connect with the pooled connection string over TLS.
- CI: GitHub Actions with an ephemeral `postgres:17` service container (no cloud DB in CI).

## Consequences
- USD 0/month at expected scale, provided the app stays non-commercial (CEO to confirm). Commercial use requires Vercel Pro (paid) or moving the unchanged Node app to another host.
- First request after 5 idle minutes pays a Neon cold start (hundreds of ms); M4 is measured on warm requests and cold starts are reported separately.
- Monitoring must not ping the DB periodically (it would keep Neon awake and exceed 100 CU-hours).
- Runtime logs are kept only 1 hour on Hobby.
- Limits hit on either service suspend/block rather than bill; nothing is charged without upgrading.
