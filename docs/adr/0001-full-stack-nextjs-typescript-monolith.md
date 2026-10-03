# ADR-0001: Single full-stack Next.js + TypeScript app
- Status: Accepted (Gate 2, 2026-10-03)
- Date: 2026-10-03
- Deciders: architect, CEO

## Context
The MVP (docs/PRD.md) is a small to-do app: email+password auth, CRUD on one entity, strict per-user isolation, a few hundred users, USD 0/month hosting. It is built and maintained by AI agents, so the stack must be mainstream, well documented, strongly typed and easy to test. There is no realtime, offline or native-mobile requirement.

## Options considered
| Option | Pros | Cons | Free tier? |
|---|---|---|---|
| **Next.js 16 (App Router) + TypeScript, UI and JSON API in one app** | One language, one repo, one deploy; huge documentation and training-data base; Route Handlers give an explicit REST API that is easy to integration-test; first-class Vercel hosting | Framework has many features (RSC, caching) that agents can misuse; we restrict usage to a simple subset | Yes (Vercel Hobby, or any Node host) |
| React SPA (Vite) + separate Express/Fastify API | Very simple mental model; clear split | Two deployables, CORS, two hosting configs, cross-site cookie complexity | Yes but two services |
| SvelteKit / Remix-style full-stack | Simpler than Next.js in places | Smaller ecosystem and less agent familiarity | Yes |
| Supabase (BaaS) + SPA, auth and RLS from Supabase | Little backend code; built-in auth | Isolation lives in RLS policies that are easy to get subtly wrong; project pauses after inactivity on free tier; more vendor lock-in | Yes |

## Decision
Build one Next.js 16 App Router application in TypeScript (strict). UI pages are React server/client components; the API is a JSON REST API implemented as Route Handlers under `/api`, running on the Node.js runtime (not Edge). Server Actions are not used for data mutations so that the API contract in docs/architecture.md section 6 is explicit and testable with plain HTTP. Supporting choices: Tailwind CSS for styling, Zod for shared validation, Vitest for unit/integration tests, Playwright for E2E, pnpm as package manager.

## Consequences
- One deployable and one CI pipeline; frontend and backend developers work in the same repo with shared types (`src/lib`).
- Agents must follow the restricted subset: no Server Actions for mutations, no Edge runtime, `force-dynamic` + `no-store` on authenticated pages.
- Portable: the app is a standard Node server (`next start`), so it can move off Vercel without code changes if needed (see ADR-0002, risk R1).
