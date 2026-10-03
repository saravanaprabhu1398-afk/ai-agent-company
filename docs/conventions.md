# Coding Conventions
> Owner: tech-lead · Applies to: every PR in this repo · Sources: `docs/architecture.md`, `docs/adr/0001`-`0004`, `docs/ux.md`

If this file and `docs/architecture.md` disagree, the architecture wins; open an issue so this file gets fixed.
If something is not covered here, follow the existing code, then ask the Tech Lead in the issue.

## 1. Stack and tooling (pinned majors)

| Tool | Version | Notes |
|---|---|---|
| Node.js | 22 LTS | `"engines": { "node": ">=22 <23" }` and `.nvmrc` with `22` |
| pnpm | latest stable (pinned via `packageManager`) | Only package manager. `pnpm-lock.yaml` is committed. Never commit `package-lock.json` or `yarn.lock`. |
| Next.js | 16, App Router | Node.js runtime only (no Edge) |
| TypeScript | 5.x, `strict: true` | Plus `noUncheckedIndexedAccess`, `noImplicitOverride` |
| Tailwind CSS | 4 | Design tokens from `docs/ux.md` section 7, defined once in `src/app/globals.css` (`@theme`) |
| Zod | 4 | All input validation |
| Drizzle ORM + `pg` + drizzle-kit | latest stable | ADR-0004 |
| `@node-rs/argon2` | latest stable | ADR-0003 |
| Vitest | latest stable | unit + integration |
| Playwright | latest stable | E2E, Chromium in CI |
| ESLint + Prettier | flat config (`eslint.config.mjs`) + `eslint-config-prettier` | see section 4 |

Adding a new runtime dependency that is not listed in `docs/architecture.md` section 2 must be called out in the PR description with a one-line reason. It must be open source and free. The Security Engineer may reject it.

## 2. Folder structure

From `docs/architecture.md` section 4. Do not add new top-level folders without a Tech Lead comment on the issue.

```
.
├── .github/workflows/ci.yml        # lint, typecheck, unit+integration, e2e
├── .env.example                    # names only, no values
├── drizzle/                        # generated SQL migrations (committed, reviewed)
├── drizzle.config.ts
├── next.config.ts                  # security headers
├── playwright.config.ts
├── vitest.config.ts
├── docker-compose.yml              # local postgres:17
├── src/
│   ├── app/                        # routes only: pages, layouts, route handlers
│   │   ├── layout.tsx, page.tsx, not-found.tsx, globals.css
│   │   ├── (auth)/login/page.tsx
│   │   ├── (auth)/signup/page.tsx
│   │   ├── todos/page.tsx
│   │   └── api/
│   │       ├── auth/{signup,login,logout,me}/route.ts
│   │       ├── todos/route.ts
│   │       ├── todos/[id]/route.ts
│   │       └── health/route.ts
│   ├── components/                 # React components (UI only, no DB, no server imports)
│   ├── lib/                        # shared client+server: validation.ts, api.ts, types.ts
│   └── server/                     # server-only, every file starts with `import 'server-only'`
│       ├── auth/{password.ts,session.ts,service.ts}
│       ├── todos/repo.ts
│       ├── db/{index.ts,schema.ts}
│       ├── http/{origin.ts,errors.ts,json.ts}
│       ├── rateLimit.ts
│       ├── env.ts
│       └── log.ts
└── tests/
    ├── unit/                       # pure functions, no DB, no network
    ├── integration/                # route handlers + real Postgres (incl. US-9 isolation)
    ├── e2e/                        # Playwright specs
    └── helpers/                    # shared test utilities (DB reset, user factory, request builder)
```

Routes: the to-do list (UX screen S3) is served at `/todos`; `/` only redirects (architecture 6.10). `docs/ux.md` suggested `/` for S3; the architecture route table is authoritative.

Layering rules:
- `src/app/api/**/route.ts` handlers are thin: origin check, parse, validate, call a `src/server` function, map the result to HTTP. No SQL in handlers.
- `src/components` and any file with `'use client'` must never import from `src/server`. `import 'server-only'` enforces this at build time.
- `src/lib` must not import from `src/server` and must not read `process.env`.
- Only `src/server/todos/repo.ts` touches the `todos` table; only `src/server/auth/*` touches `users` and `sessions`; only `src/server/rateLimit.ts` touches `rate_limits`.

## 3. Naming

| Thing | Convention | Example |
|---|---|---|
| React component files and components | PascalCase | `TodoItem.tsx`, `ConfirmDeleteDialog.tsx` |
| Other TS modules | camelCase | `rateLimit.ts`, `validation.ts` |
| Next.js special files | framework names | `page.tsx`, `route.ts`, `layout.tsx`, `not-found.tsx` |
| Functions, variables | camelCase, verbs for functions | `createSession`, `listTodos` |
| Types, interfaces, Zod schemas | `PascalCase` types; schemas `camelCaseSchema` | `type Todo`, `createTodoSchema` |
| Constants | `UPPER_SNAKE_CASE` | `SESSION_MAX_AGE_SECONDS`, `TITLE_MAX_LENGTH` |
| DB tables and columns | `snake_case`, tables plural | `todos.user_id`, `created_at` |
| Drizzle schema fields (TS side) | camelCase mapped to snake_case | `userId: uuid('user_id')` |
| JSON fields in API | camelCase | `createdAt`, `completed` |
| API error codes | `UPPER_SNAKE_CASE` | `VALIDATION_ERROR` |
| Env vars | `UPPER_SNAKE_CASE` | `APP_ORIGIN` |
| Log events | `domain.action[.result]` | `auth.login.failure` |
| Test files | `*.test.ts(x)` (Vitest), `*.spec.ts` (Playwright) | `tests/integration/todos.isolation.test.ts` |
| Branches | `<type>/<issue>-<slug>` | `feat/12-todo-crud-api` |

Magic numbers from the requirements live as named constants in `src/lib/constants.ts` (shared) and are reused by validation, DB schema and UI: `TITLE_MAX_LENGTH = 200`, `PASSWORD_MIN_LENGTH = 8`, `PASSWORD_MAX_LENGTH = 128`, `EMAIL_MAX_LENGTH = 254`, `SESSION_MAX_AGE_SECONDS = 604800`, `TITLE_COUNTER_THRESHOLD = 180`.

## 4. Lint, format, type-check

- `pnpm lint` (ESLint, `next/core-web-vitals` + `next/typescript` + `eslint-config-prettier`) must pass with zero errors. Warnings are not allowed in CI (`--max-warnings 0`).
- Required rules (set to `error`): `react/no-danger`, `no-console` (allowed only in `src/server/log.ts`), `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-floating-promises` (type-aware), `eqeqeq`.
- `pnpm format` runs Prettier; `pnpm format:check` runs in CI. Prettier config: `printWidth: 100`, `singleQuote: false`, `semi: true`, `trailingComma: "all"`, plus `prettier-plugin-tailwindcss` for class ordering.
- `pnpm typecheck` (`tsc --noEmit`) must pass.
- Disabling a lint rule needs an inline comment with the reason: `// eslint-disable-next-line <rule> -- <reason>`. No file-wide disables.
- No `@ts-ignore`; use `@ts-expect-error` with a reason only in tests.

## 5. Framework rules (ADR-0001)

- No Server Actions for data mutations. All mutations go through `/api/*` route handlers via `src/lib/api.ts`.
- All route handlers run on the Node.js runtime (`export const runtime = 'nodejs'` where needed). No Edge runtime.
- Authenticated pages export `dynamic = 'force-dynamic'` and are never cached; all API responses send `Cache-Control: no-store`.
- `dangerouslySetInnerHTML` is forbidden. Titles are plain text.
- Every `src/server/**` file starts with `import 'server-only'`.
- The user id comes only from the session (`requireSession()`). Never accept `userId` from a body, query or path.
- Every to-do repository function takes `userId` as its first parameter and includes `user_id = $userId` in the same SQL statement as any `id` filter. Reviewers reject anything else.
- Migrations: change `src/server/db/schema.ts`, run `pnpm db:generate`, commit the SQL in `drizzle/`. Never edit an already-merged migration. Migrations are never run at app start-up.

## 6. Error handling and API format

All non-2xx API responses use one envelope (architecture 6):

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Human-readable summary", "fields": { "title": "Title is required" } } }
```

- `fields` only for `VALIDATION_ERROR` (and `EMAIL_TAKEN`, which sets `fields.email`). Keys match request field names: `email`, `password`, `title`, `completed`.
- Allowed codes and statuses: `400 VALIDATION_ERROR`, `401 UNAUTHENTICATED`, `401 INVALID_CREDENTIALS`, `403 FORBIDDEN_ORIGIN`, `404 NOT_FOUND`, `409 EMAIL_TAKEN`, `413 PAYLOAD_TOO_LARGE`, `415 UNSUPPORTED_MEDIA_TYPE`, `429 RATE_LIMITED` (+ `Retry-After`), `500 INTERNAL_ERROR`. Adding a code requires an architecture update.
- Server side: throw or return a typed `HttpError(status, code, message, fields?)` from `src/server/http/errors.ts`. Every handler is wrapped in `withErrorHandling()`, which maps `HttpError` to the envelope and anything else to `500 INTERNAL_ERROR` with a generic message, logging the stack with `requestId`.
- Never put stack traces, SQL, internal IDs or `requestId` in response bodies.
- Another user's to-do is always `404 NOT_FOUND`, never `403`.
- Postgres unique violation `23505` on `users.email` maps to `409 EMAIL_TAKEN`.
- Client side: `src/lib/api.ts` throws `ApiError { status, code, message, fields? }`. Components map `code`/`fields` to the exact copy in `docs/ux.md` section 5; they do not display server `message` strings for validation errors. A `401` from any to-do call redirects to `/login?reason=expired`; logout redirects to `/login?reason=logged-out`.
- Do not swallow errors. `catch` blocks either handle the error meaningfully or rethrow.

## 7. Logging

- Use `src/server/log.ts` only (JSON lines). No `console.*` elsewhere.
- Never log: request bodies of `/api/auth/*`, passwords, tokens, cookies, `Set-Cookie`, full emails (use a short hash), `DATABASE_URL`.
- Event names from architecture 9 (`auth.signup.success`, `auth.login.failure`, `todo.not_found`, ...).

## 8. Environment variables

| Name | Required | Example (local) | Notes |
|---|---|---|---|
| `DATABASE_URL` | yes | `postgres://todo:todo@localhost:5432/todo` | Neon pooled string with `sslmode=require` in staging/prod. Secret. |
| `APP_ORIGIN` | yes | `http://localhost:3000` | Used by the CSRF origin check. Must match the browser origin exactly. |
| `SESSION_COOKIE_SECURE` | no | `false` | Defaults to `true` when `NODE_ENV=production`. Only `false` on `http://localhost`. |
| `LOG_LEVEL` | no | `info` | `info` or `debug` |

- Read env only through `src/server/env.ts` (Zod-validated; the app fails fast with a clear message naming the missing variable, never its value).
- `.env.example` lists names only. `.env*` other than `.env.example` is git-ignored.
- No `NEXT_PUBLIC_*` variable may contain a secret. Today there are none.
- Staging/production values live in Vercel Environment Variables. CI uses the Postgres service container and needs no secrets.

## 9. Testing rules

Every PR that changes behaviour adds or updates tests. CI must be green before review.

| Level | Tool | Location | What | DB |
|---|---|---|---|---|
| Unit | Vitest | `tests/unit/` | Pure logic: Zod schemas, token hashing, error mapping, rate-limit math, components (React Testing Library + jsdom) | none |
| Integration | Vitest | `tests/integration/` | Call route handlers with real `Request` objects; assert status, envelope, cookies, DB state | real Postgres (`DATABASE_URL`) |
| E2E | Playwright | `tests/e2e/` | User flows through the browser against `next build && next start` | real Postgres |

- **No mocking the database** in integration tests. Mock only time (`vi.useFakeTimers` / injected clock) and nothing else where possible.
- Integration tests reset state with `TRUNCATE users, sessions, todos, rate_limits CASCADE` in `beforeEach` (helper in `tests/helpers/db.ts`) and run with `fileParallelism: false`.
- Rate-limit constants must be overridable in tests so other tests do not hit `429`.
- Tests are deterministic: no real sleeps, no dependence on order, unique emails per test (`user-${randomUUID()}@example.com`).
- Name tests after the behaviour and story: `it('US-4: rejects a whitespace-only title with 400 VALIDATION_ERROR')`.
- **US-9 isolation tests are mandatory and may never be skipped or deleted.** The suite `tests/integration/todos.isolation.test.ts` must cover, with users A and B:
  1. `GET /api/todos` as A returns none of B's to-dos.
  2. `PATCH /api/todos/:bId` as A (title, and completed) returns `404 NOT_FOUND`.
  3. `DELETE /api/todos/:bId` as A returns `404 NOT_FOUND`.
  4. After 2 and 3, B's rows are unchanged (same title, completed, `updated_at`).
  5. A `userId` field in a request body is rejected with `400 VALIDATION_ERROR`.
  6. Every to-do endpoint returns `401 UNAUTHENTICATED` without a cookie, with an unknown cookie, and with an expired session.
  The E2E suite repeats the list-isolation check through the UI.
- Auth integration tests are mandatory for: logout invalidates the session server-side, session expiry after 7 days, generic login error for unknown email and wrong password, rate limiting returns `429` with `Retry-After`.
- Accessibility: component tests use accessible queries (`getByRole`, `getByLabelText`). E2E runs an axe scan per screen; zero serious/critical violations.
- `.skip`/`.only` must not be merged. A flaky test is fixed or quarantined with a linked `type:bug` issue, never silently skipped.

## 10. UI rules

- UI copy is taken verbatim from `docs/ux.md` section 5. Do not invent new copy; ask the UX designer in the issue.
- WCAG 2.1 AA as specified in `docs/ux.md` section 8: real buttons and links, labels on every input, `aria-invalid` + `aria-describedby` on field errors, `role="alert"` for form errors, polite live region for status.
- Use Tailwind with the tokens from `docs/ux.md` section 7. No inline hex colours in components.
- Mobile first; no horizontal scroll at 320 px; touch targets at least 44 x 44 px on mobile.
- Shared validation: client forms use the same Zod schemas from `src/lib/validation.ts` as the server.

## 11. Git, commits and PRs

- Never push to `main`. Branch: `<type>/<issue-number>-<short-slug>`, type = `feat`, `fix`, `chore`, `docs`, `test`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org): `<type>(<scope>): <imperative summary>`, max 72 chars in the subject.
  - Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`, `build`, `perf`.
  - Scopes: `auth`, `todos`, `db`, `ui`, `api`, `ci`, `deploy`, `docs`, `e2e`.
  - Example: `feat(todos): add PATCH /api/todos/:id with per-user scoping`.
  - Breaking changes: `!` after the scope and a `BREAKING CHANGE:` footer.
- One issue = one PR. The PR body uses `.github/pull_request_template.md` and contains `Closes #N`.
- PR title = the main Conventional Commit line (PRs are squash-merged by the CEO at Gate 3).
- Keep PRs small (about half a day of work, under ~400 changed lines excluding lockfile and generated migrations). If it grows, stop and ask the Tech Lead to split the issue.
- Update `.env.example`, docs and `CHANGELOG.md` (once it exists) when behaviour or configuration changes.
- Max 3 review/fix cycles per PR, then label `needs-ceo`.
- Never commit secrets, `.env` files, real connection strings or test credentials for hosted services.
- Labels during work: set `status:in-progress` when you start, `status:review` when the PR is open.

## 12. Scripts (`package.json`)

`dev`, `build`, `start`, `lint`, `typecheck`, `format`, `format:check`, `test` (unit + integration via `vitest run`), `test:unit`, `test:integration`, `test:e2e` (`playwright test`), `db:generate`, `db:migrate`. CI runs `lint`, `format:check`, `typecheck`, `test`, `build`, `test:e2e`.
