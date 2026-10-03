# ADR-0003: Email+password auth with Argon2id and database-backed session cookies
- Status: Accepted (Gate 2, 2026-10-03)
- Date: 2026-10-03
- Deciders: architect, CEO

## Context
PRD US-1/2/3/9 and Gate 1: email+password sign-up and login, no reset or verification, min 8-char password, 7-day sessions, logout must really end the session (back button must not show data), strict per-user isolation, generic login errors. No email sending. Auth endpoints need rate limiting, without adding paid services.

## Options considered
| Option | Pros | Cons | Free tier? |
|---|---|---|---|
| **Custom: Argon2id + opaque token cookie, SHA-256 of token stored in `sessions` table** | Small amount of well-understood code (pattern documented by the Lucia project and OWASP); real server-side logout; easy to integration-test; no extra vendor | We own the code, so it must be reviewed carefully | Yes |
| Auth.js (NextAuth) Credentials provider | Popular | Credentials provider pushes JWT sessions (no server-side revocation) and is deliberately limited; sign-up is still custom | Yes |
| Better Auth (library) | Full-featured, DB sessions | Extra abstraction and schema to learn; more than the MVP needs | Yes |
| Stateless JWT in cookie | No session table | Logout cannot revoke a stolen token before expiry; key management | Yes |
| Hosted auth (Clerk, Supabase Auth, Auth0) | Reset/verification for free later | Another vendor, MAU limits, harder isolation testing, cost if commercial | Free tiers with limits |

## Decision
- Password hashing: Argon2id (`@node-rs/argon2`), m=19456 KiB, t=2, p=1; passwords 8–128 chars. Unknown-email logins verify against a dummy hash to equalise timing. Fallback if the native module fails on the host: `bcryptjs` cost 12 behind the same interface.
- Sessions: 32 random bytes, base64url, in cookie `session` (`HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800`). The DB stores only `sha256(token)` with an absolute `expires_at` 7 days after login (no sliding renewal). Login rotates the session; logout deletes the row and clears the cookie.
- CSRF: SameSite=Lax + `Origin` must equal `APP_ORIGIN` on every mutating request + JSON-only bodies.
- Authorization: user id comes only from the session; every to-do query is scoped by `user_id` in the same SQL statement; other users' to-dos return 404.
- Rate limiting: Postgres fixed-window counters (`rate_limits` table, atomic upsert), checked before hashing: login 20/15 min per IP and 10/15 min per email; sign-up 5/hour per IP; 429 with `Retry-After`.

## Consequences
- No auth vendor, no cost, fully testable with a local Postgres; one extra DB query per authenticated request (indexed primary-key lookup, about 1–2 ms when co-located).
- Auth code is security-critical and must get Security Engineer review; integration tests for isolation (US-9), logout and rate limiting are mandatory.
- Password reset and email verification can be added later with new tables (tokens) and an email provider; the session design does not change.
- Sign-up reveals whether an email is registered (409), as US-1 requires; mitigated by the sign-up rate limit.
