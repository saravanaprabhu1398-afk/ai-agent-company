# Product Requirements Document
> Owner: product-manager · Status: Approved (Gate 1, 2026-10-03)

## 1. Problem
People who want to track simple tasks either rely on paper, scattered notes, or heavyweight project tools with too many features. They want a lightweight, private to-do list they can open from any device and trust that only they can see it. This product is a simple to-do app where each person signs in and manages their own list.

## 2. Target users & personas
- **Primary: "Solo Sam", an individual with personal tasks.** Wants to quickly add, tick off and remove tasks. Low tolerance for setup or clutter. Expects their list to be private and available after logging in again.
- No team, admin or enterprise persona in the MVP.

## 3. Goals / non-goals
**Goals**
- G1: A new user can sign up and add their first to-do in under 2 minutes.
- G2: Each user's to-dos are private and persist across sessions.
- G3: Run on free-tier hosting and services.

**Non-goals (MVP)**: see "Later" in section 4. Each is flagged in Open questions where the CEO may want it sooner.

## 4. MVP scope
In scope:
1. Sign up with email + password.
2. Log in and log out.
3. Create a to-do (title).
4. List my to-dos.
5. Edit a to-do's title.
6. Mark a to-do complete / incomplete.
7. Delete a to-do.
8. Data isolation: a user can only see and change their own to-dos.

**Later (explicitly out of MVP)**: password reset / forgot password, email verification, social/OAuth login, due dates and reminders, priorities, tags/categories/lists, search and filters, sharing or collaboration, notes/descriptions, drag-to-reorder, native mobile apps, notifications, account deletion/profile editing, dark mode, i18n.

## 5. User stories
| ID | As a… | I want… | So that… | Priority |
|---|---|---|---|---|
| US-1 | new visitor | to sign up with email and password | I get my own private account | Must |
| US-2 | registered user | to log in with email and password | I can reach my to-dos | Must |
| US-3 | logged-in user | to log out | my list is safe on a shared device | Must |
| US-4 | logged-in user | to create a to-do with a title | I can capture a task | Must |
| US-5 | logged-in user | to see a list of my to-dos | I know what I need to do | Must |
| US-6 | logged-in user | to mark a to-do complete or incomplete | I can track progress | Must |
| US-7 | logged-in user | to edit a to-do's title | I can fix or update it | Should |
| US-8 | logged-in user | to delete a to-do | I can remove tasks I no longer need | Should |
| US-9 | any user | my to-dos to be visible only to me | my data stays private | Must |

## 6. Acceptance criteria (Given / When / Then per story)

**US-1 Sign up**
- Given I am on the sign-up page, When I submit a valid, unused email and a password meeting the rules, Then an account is created, I am logged in, and I see my empty to-do list.
- Given an account already exists for an email, When I sign up with that email, Then I see an error and no second account is created.
- Given I submit an invalid email or a password that is too short, When I submit, Then I see a clear field-level error and no account is created.
- Password is never stored or shown in plain text.

**US-2 Log in**
- Given I have an account, When I submit the correct email and password, Then I am logged in and see my to-do list.
- Given I submit a wrong email or password, When I submit, Then I see a generic "invalid email or password" error and am not logged in.
- Given I am not logged in, When I open the to-do list URL, Then I am redirected to log in.
- Given I logged in, When I reload or return later within the session duration, Then I remain logged in (session duration: see Open questions).

**US-3 Log out**
- Given I am logged in, When I click Log out, Then my session ends and I am taken to the log-in page.
- Given I have logged out, When I use the browser back button or request a to-do page, Then I cannot see or change my to-dos.

**US-4 Create to-do**
- Given I am logged in, When I enter a non-empty title and submit, Then the to-do appears in my list as incomplete and persists after reload.
- Given I submit an empty or whitespace-only title, When I submit, Then I see an error and nothing is created.
- Given a title longer than the maximum length (see Open questions), When I submit, Then I see an error and nothing is created.

**US-5 List to-dos**
- Given I have to-dos, When I open my list, Then I see all of them, with title and completion state, newest first.
- Given I have no to-dos, When I open my list, Then I see an empty-state message prompting me to add one.

**US-6 Toggle complete**
- Given an incomplete to-do, When I mark it complete, Then it shows as complete and stays complete after reload.
- Given a complete to-do, When I mark it incomplete, Then it shows as incomplete and stays so after reload.

**US-7 Edit**
- Given an existing to-do, When I change the title to a valid value and save, Then the new title is shown and persists after reload.
- Given I clear the title or exceed the max length, When I save, Then I see an error and the old title is kept.

**US-8 Delete**
- Given an existing to-do, When I delete it, Then it disappears from my list and does not return after reload.
- Given I choose delete, Then the app asks me to confirm first (confirm vs. undo is an Open question).

**US-9 Privacy / isolation**
- Given users A and B each have to-dos, When A views their list, Then none of B's to-dos appear.
- Given I am logged in as A, When I attempt to read, edit, complete or delete a to-do belonging to B (e.g. by guessing its ID), Then the request is rejected and B's data is unchanged.
- Given I am not logged in, When any to-do data is requested, Then it is rejected as unauthenticated.

## 7. Success metrics
Measured on the staging/production deployment; the MVP is a small product, so targets are modest.
- M1: 100% of Must-story acceptance criteria pass in automated tests (unit + E2E) before Gate 3.
- M2: Zero cross-user data leaks in isolation tests (US-9) and no high/critical security findings.
- M3: A first-time user completes sign up and creates a first to-do in under 2 minutes (manual timed check with at least 3 testers).
- M4: Core actions (list, create, toggle) respond in under 500 ms at p95 under light load (target; Architect to confirm feasibility on free tier).
- M5: Hosting and services cost USD 0/month.
- M6 (post-launch, if analytics allowed): at least 50% of signed-up users create 1 or more to-dos; see Open questions on analytics.

## 8. Open questions
For the CEO unless noted. Nothing below is assumed in the requirements above except where a default is stated.

1. **Password reset / forgot password**: excluded from MVP, meaning a user who forgets their password is locked out. Include it (adds email sending, which may need a free-tier email service), or accept for now?
2. **Email verification**: excluded. Acceptable that anyone can register with any email address?
3. **Password rules**: proposed default is minimum 8 characters, no complexity rules. Confirm or change.
4. **Session duration**: how long should a user stay logged in (for example 7 days, or until logout)? Proposed default: 7 days.
5. **To-do title max length**: proposed default 200 characters. Confirm.
6. **Delete behavior**: confirm-before-delete (as drafted in US-8) or delete with undo?
7. **Social/OAuth login** (Google, GitHub): Later. Wanted earlier?
8. **Due dates, priorities, tags, search/filter**: all Later. Is any needed for MVP?
9. **Sharing / collaboration**: Later. Is a team use case planned?
10. **Account management** (change password, delete account): excluded. Any legal or privacy need (for example GDPR delete-my-data) that makes account deletion a launch requirement?
11. **Platform**: responsive web app assumed; is a native mobile app ever expected? (Technology choice remains with the Architect.)
12. **Analytics**: is any usage tracking allowed? Needed for M6; otherwise M6 is dropped.
13. **Branding/name** of the product: not provided; placeholder "To-Do App" assumed.
14. **Expected scale**: assumed up to a few hundred users in the first months, to fit free tiers. Confirm.

### Gate 1 resolution (2026-10-03)
The CEO approved the scope as drafted without changing anything. The proposed defaults apply until the CEO says otherwise:
- Q1–Q2: no password reset and no email verification in the MVP (accepted risk; revisit next sprint).
- Q3: min 8 characters, no complexity rules. Q4: 7-day session. Q5: 200-char title limit. Q6: confirm before delete.
- Q7–Q12: stay Later or excluded as drafted; no analytics, so M6 is dropped unless the CEO enables it.
- Q13: placeholder name "To-Do App". Q14: scale up to a few hundred users (free tier).
