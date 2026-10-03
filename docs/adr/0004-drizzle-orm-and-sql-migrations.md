# ADR-0004: Drizzle ORM with node-postgres and committed SQL migrations
- Status: Accepted (Gate 2, 2026-10-03)
- Date: 2026-10-03
- Deciders: architect, CEO

## Context
We need typed database access from TypeScript, versioned schema migrations, and the same code path against Neon (staging/production) and a plain Postgres container (local and CI) so integration tests exercise real SQL, including the per-user isolation rules.

## Options considered
| Option | Pros | Cons | Free tier? |
|---|---|---|---|
| **Drizzle ORM + `pg` driver + drizzle-kit** | Thin, SQL-like, fully typed; migrations are plain SQL files reviewable in PRs; no binary engine; works with any Postgres | Younger than Prisma; fewer guard rails | Yes (open source) |
| Prisma | Very popular, great docs | Separate query engine/generation step; heavier cold starts in serverless; migration flow more opinionated | Yes |
| Raw `pg` with hand-written SQL | No abstraction | No type safety on results; hand-rolled migrations | Yes |
| Neon serverless HTTP driver | Lowest latency from serverless | Does not talk to a plain local/CI Postgres without a proxy; limited transactions | Yes |

## Decision
Use Drizzle ORM with the `pg` (node-postgres) driver. A single `Pool` (small `max`, e.g. 3) is created per function instance and connects to Neon's pooled (`-pooler`) connection string with TLS. Schema lives in `src/server/db/schema.ts`; `drizzle-kit generate` writes SQL migrations to `drizzle/`, which are committed and reviewed. Migrations are applied by DevOps with `pnpm db:migrate` as an explicit deploy step, never at app start-up.

## Consequences
- Identical driver and SQL in local, CI and production; isolation tests run against real Postgres.
- Generated SQL must be reviewed (CHECK constraints and indexes from docs/architecture.md section 5 must be present).
- If Neon cold-start + TCP connect latency becomes a problem, switching to the Neon serverless driver is a contained change in `src/server/db/index.ts`.
