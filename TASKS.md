# LMS — Task Breakdown

Sized for **under 5 hours per week**. Each task is one sitting of about 1–3 hours, with a clear "done when". Work top to bottom inside a phase; phases map to the milestones in [PROJECT_PLAN.md](PROJECT_PLAN.md).

**Total estimate:** about 330–370 hours for v1, which is roughly 16–18 months at 5 hours per week. This was revised upward after review; the frontend tasks are the most likely to run long. Plan for that, and expect the first phases to go faster than later ones.

## Stack (decided)

| Layer | Choice |
|-------|--------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| Database | PostgreSQL (Docker locally) |
| Frontend | React + TypeScript + Vite, React Router, TanStack Query |
| UI | Tailwind CSS (simple components; add a component library later if needed) |
| Auth | Email + password, HTTP-only cookie sessions, invite links |
| Email | Console printer in dev; real provider added in Phase 6 |
| File storage | Local folder in dev; S3-compatible (Cloudflare R2) later |
| Recordings | Zoom cloud recordings; the platform stores the link |
| Tests | pytest (backend), Vitest (frontend), Playwright later for key flows |
| Lint | ruff (Python), ESLint + Prettier (frontend) |
| CI | GitHub Actions |

## Architecture rule (read first)

Each layer only talks to the layer below it:

```
api/        FastAPI routers: parse request, call service, return response. No business logic.
services/   Business rules (who can enroll, when a recording expires). Knows nothing about HTTP.
repos/      Database queries only.
adapters/   Code that talks to outside providers, behind an interface:
            EmailSender, FileStorage, VideoLinks (Zoom today; another provider later).
```

Services receive adapters through interfaces (Python `Protocol`). Swapping Zoom for another video host, or Mailgun for SMTP, then means writing one new adapter class and changing one line in the config. No service or router changes.

---

## Phase 0 — Project setup (about 12 h)

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| S0.1 | Create folders `backend/`, `frontend/`, `docs/` and a root `README.md` with the project name | Folders exist and README explains the layout | 1 h |
| S0.2 | Create `backend/` Python project with `uv` (or Poetry); add FastAPI, uvicorn | `uv run uvicorn app.main:app` starts | 1 h |
| S0.3 | Add `GET /health` endpoint with one pytest test | `pytest` passes | 1 h |
| S0.4 | Add `docker-compose.yml` with PostgreSQL 16 | `docker compose up db` runs, and you can connect | 1 h |
| S0.5 | Add settings module (Pydantic Settings) reading env vars; add `.env.example` | App reads DB URL from `.env`; no secrets in git | 1 h |
| S0.6 | Set up SQLAlchemy engine and Alembic; create empty first migration | `alembic upgrade head` runs | 1.5 h |
| S0.7 | Create `frontend/` with Vite + React + TypeScript | `npm run dev` shows a page | 1 h |
| S0.8 | Connect frontend to `/health` through the Vite proxy | Page shows "API OK" | 1 h |
| S0.9 | Add ruff (backend) and ESLint + Prettier (frontend), with format scripts | Lint commands pass on the starter code | 1.5 h |
| S0.10 | Add `.gitignore` for Python, Node, `.env`, and uploads | `git status` shows no build or secret files | 0.5 h |
| S0.11 | Add GitHub Actions workflow: backend lint and tests, frontend lint and build | Green check on a test push | 1.5 h |
| S0.12 | Write `docs/architecture.md` with the layer rule above and a folder map | Document is committed | 1 h |
| S0.13 | Draw the architecture diagram (Mermaid) in `docs/architecture.md`: layers, and the replaceable providers (Zoom, email, file storage) | Diagram renders on GitHub and matches the layer rule | 1 h |

---

## Phase 1 — Accounts and roles (M1, about 35 h)

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| A1.0 | Draw the data model diagram (Mermaid) in `docs/data-model.md`, from PROJECT_PLAN.md section 5.1, including Booklet, CourseStaff, and AccessGrant | Diagram renders on GitHub and matches the planned models | 1.5 h |
| A1.1 | `User` model: name, email (unique), password hash, role (student / assistant / instructor / admin), status, created_at; first migration | Migration applies; table exists | 1.5 h |
| A1.2 | Password hashing helper (argon2 via `pwdlib` or `argon2-cffi`) with tests | Hash and verify tests pass; plain passwords never stored | 1 h |
| A1.3 | Create-admin CLI command (`python -m app.cli create-admin`) | You can create your admin account from the terminal | 1 h |
| A1.4 | Login endpoint: check password, set HTTP-only cookie session | Correct login returns cookie; wrong login returns generic error | 2.5 h |
| A1.5 | Session storage table and logout endpoint | Logout invalidates the cookie session | 1.5 h |
| A1.6 | `current_user` and `require_role(...)` FastAPI dependencies | Test: student gets 403 on an instructor-only route | 1.5 h |
| A1.7 | Login rate limit: 5 failures per 15 minutes per email | Sixth attempt is blocked with a clear message | 2 h |
| A1.8 | `EmailSender` interface plus console adapter (prints email to terminal) | Email content appears in terminal during dev | 1.5 h |
| A1.9 | `Invite` model: token hash, user_id, expires_at (3 days), used_at | Migration applies; token is stored hashed | 1 h |
| A1.10 | Endpoint: teacher or assistant creates a student and sends an invite | Invite email printed; student row created with status "invited" | 2 h |
| A1.10a | Draw the invite sequence diagram (Mermaid) in `docs/flows/invite.md`: create, send, accept, expire, resend | Diagram matches the tests for A1.10 to A1.12 | 1 h |
| A1.11 | Endpoint: accept invite, student sets password, status becomes active | Expired or used token returns clear error; valid token works once | 2 h |
| A1.12 | Endpoint: resend invite (new token, old one invalid) | Old link stops working after resend | 1.5 h |
| A1.13 | Forgot-password and reset-password endpoints (1-hour, single-use token) | Same response whether email exists or not | 2.5 h |
| A1.14 | Admin: disable and enable a user; disabled users cannot log in | Test covers disabled login | 1.5 h |
| A1.15 | Frontend: login page with error messages | Login works end to end in browser | 2 h |
| A1.16 | Frontend: accept-invite page (set password) and forgot-password pages | Full invite flow works in browser | 2.5 h |
| A1.17 | Frontend: route guards by role; basic "my profile" page (name, change password) | Students cannot open instructor pages | 2.5 h |
| A1.17a | CSRF protection on every request that changes data | Test: request without the CSRF token is rejected | 2 h |
| A1.17b | End all sessions when a user is disabled or resets a password | Test: old cookie stops working | 1.5 h |
| A1.17c | Per-IP login rate limit, plus limits on invite creation and password reset (moved from H6.4) | Test: limit triggers across different emails from one IP | 1.5 h |
| A1.17d | Assistant scope: `CourseStaff` table; assistants act only on assigned courses, including check-in and access grants | Test: assistant blocked on a course not assigned to them | 2.5 h |
| A1.17e | Invite acceptance counts as email verification; no public sign-up route in v1 | Test: sign-up route does not exist | 1 h |
| A1.17f | Object-level checks on course, session, and grant endpoints (a teacher cannot edit another teacher's course) | Test: teacher A gets 403 on course B | 1.5 h |
| A1.18 | Phase 1 review: run tests, check each acceptance criterion in stories A1–A3 and K4 | Checklist in `docs/milestones/m1.md` ticked | 1 h |

---

## Phase 2 — Catalog and course authoring (M2, about 45 h)

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| C2.1 | `Category` model and admin CRUD endpoints | Admin can create and list categories | 1.5 h |
| C2.2 | `Course` model: title, slug, description, cover_url, status (draft / published / archived), category_id, instructor_id | Migration applies | 1.5 h |
| C2.3 | Course create and update endpoints (owner or admin only) | Student gets 403; instructor edits own course | 2 h |
| C2.4 | `Section` and `Lesson` models with position field | Migration applies | 1.5 h |
| C2.5 | Section and lesson CRUD endpoints | Create, rename, delete work; deleting cascades correctly | 2.5 h |
| C2.6 | Reorder endpoint: send new order for sections or lessons | Positions saved and returned in order | 2 h |
| C2.7 | Lesson content types: text, video link, file reference (stored as type + body fields) | Each type validates its fields | 2 h |
| C2.8 | Publish and unpublish endpoints; publish requires at least one lesson and a cover image | Draft cannot publish with no lessons | 1.5 h |
| C2.9 | Catalog endpoint: list published courses, search by title, filter by category | Draft courses never appear; search tests pass | 2 h |
| C2.10 | Course detail endpoint: shows sections and lesson titles, not lesson content | Locked content is not in the response | 1.5 h |
| C2.11 | Cover-image upload: `FileStorage` interface with local adapter; size and type checks (JPG/PNG, max 2 MB) | Upload rejects wrong types and big files | 2.5 h |
| C2.12 | Frontend: catalog page with search and category filter | Page shows published courses only | 2.5 h |
| C2.13 | Frontend: course detail page | Shows description, syllabus, instructor | 2 h |
| C2.14 | Frontend: instructor course list and create-course form | Instructor creates a draft course | 2 h |
| C2.15 | Frontend: course editor for sections and lessons (add, rename, delete) | Changes save and show after refresh | 3 h |
| C2.16 | Frontend: drag-and-drop reorder (use `@dnd-kit`) | New order is saved after each drop | 3 h |
| C2.17 | Frontend: lesson editor for text and video link (rich text can be a plain textarea at first) | Lesson saves and shows in the course | 2.5 h |
| C2.18 | Phase 2 review against stories C1, C2, D1–D4 | Checklist in `docs/milestones/m2.md` ticked | 1 h |

---

## Phase 3 — Live sessions, recordings, attendance (M3b, about 45 h)

Recordings are hosted by Zoom, so the platform stores the Zoom meeting link and the recording link. It does not stream video itself.

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| L3.1 | `VideoLinks` interface and a Zoom adapter that validates a Zoom URL (no Zoom API calls yet) | Non-Zoom URLs are rejected; tests pass | 1.5 h |
| L3.2 | `Session` model: course_id, title, starts_at, ends_at, join_url, recording_url, price (nullable, unused for now) | Migration applies | 1.5 h |
| L3.3 | Session CRUD endpoints for course owner, assistants, and admin. Set the join link and recording link per session, or apply one join link to all sessions in a course | Students get 403; bulk apply updates every session in the course | 2.5 h |
| L3.4 | `AccessGrant` model and grant and revoke endpoints (reason: manual or free_tech_issue) | Grant is stored with who granted it | 2 h |
| L3.5 | Access rule service: access valid if grant exists and not expired; expiry = session or course setting, else platform default of 7 days | Unit tests for: no grant, valid, expired, per-session override | 2.5 h |
| L3.6 | Recording endpoint: returns `recording_url` only if access is valid | Expired grant returns no link | 1.5 h |
| L3.7 | Platform settings table (key-value) with default recording days = 7 and invite days = 3 | Admin can read and change the default | 2 h |
| L3.8 | Attendance: rotating check-in code per session (new code every 30 seconds, signed with a secret) | Old codes stop working | 2.5 h |
| L3.9 | Check-in endpoint: student submits code; creates `Attendance` row once per session | Duplicate check-in is ignored | 1.5 h |
| L3.10 | Attendance report endpoint for a session (name, time, method) | Instructor sees the list | 1.5 h |
| L3.11 | Frontend: session list for a course with a "Join" button, shown only to students with access. The backend returns the Zoom link only when the button is clicked; the link never appears in page text | Button opens Zoom in a new tab; students without access see no button | 2 h |
| L3.12 | Frontend: "Watch recording" button, shown only when the access rule allows | Hidden when access is expired | 1.5 h |
| L3.13 | Frontend: instructor screen to show the check-in QR code (`qrcode` library) | QR changes every 30 seconds | 2.5 h |
| L3.14 | Frontend: student QR scanner page (`html5-qrcode`) that posts the code | Scanning marks attendance | 3 h |
| L3.15 | Frontend: grant-access screen for assistants (search student, pick session, grant or revoke) | Grant shows on the student's session list | 2.5 h |
| L3.16 | Zoom-side settings (downloads, sign-in, waiting room, passcode, share-link removal) are handled by the owner in the Zoom app, not in the platform | Owner confirms the settings are done | 0 h |
| L3.12b | Session notes: `notes` field on `Session` (rich text, sanitized on save); shown on the session page only to students with access, using the same rule as the recording | Students with access read the notes; others see nothing; notes are never a file download | 3 h |
| L3.17 | Phase 3 review against stories K1, K2 and LIVE-1 to LIVE-7 | Checklist in `docs/milestones/m3b.md` ticked | 1 h |

**Decision (Option 1, updated):** Zoom hosts the recordings, and the owner manages Zoom settings in the Zoom app. The platform stores each session's join link and recording link, and hides the recording link once access expires (7 days by default). The watermark and one-device rule are not built. Known gap: anyone who has a recording link can open it until the owner removes it in Zoom. If sharing becomes a problem, move to a dedicated video host.

---

## Phase 3b — Booklets (about 25 h)

Booklets are the teacher's study material, sold per booklet and split into units. Students read them online; downloads and printing are off.

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| B3b.1 | `Booklet` model (title, description, status) and `BookletUnit` model (booklet_id, title, position, file_key) | Migration applies | 1.5 h |
| B3b.2 | `FileStorage` method to save and read private files, with no public URL | Files cannot be opened without the backend | 1.5 h |
| B3b.3 | Upload endpoint for a unit file (PDF only, size limit in settings) | Other file types are rejected | 2 h |
| B3b.4 | Extend `AccessGrant` with `booklet_id` (grant per booklet) | Grant for one booklet does not open others | 1.5 h |
| B3b.0 | Draw the booklet read sequence diagram (Mermaid) in `docs/flows/booklet-read.md`: access check, short-lived link, viewer | Diagram matches the tests for B3b.5 | 1 h |
| B3b.5 | Viewer endpoint: returns a short-lived signed link only if the student has access to that booklet | Expired or no-access requests return 403 | 2.5 h |
| B3b.6 | Frontend viewer with the PDF.js library; download, print, and save buttons removed | Students with access read units in the page | 3 h |
| B3b.7 | Frontend: booklet catalog page (title, units) and grant screen for assistants | Grant shows in the student's list | 2.5 h |
| B3b.8 | Phase review against BK-1 to BK-5 | Checklist in `docs/milestones/m3b.md` ticked | 1 h |

## Phase 4 — Assessments (M4, about 50 h)

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| Q4.1 | `Quiz` model linked to a lesson: pass_percent, max_attempts, show_answers, time_limit_minutes | Migration applies | 1 h |
| Q4.2 | `Question` and `Option` models; question types: single, multiple, true_false, essay; points | Migration applies | 1.5 h |
| Q4.3 | Quiz and question CRUD for instructor (options must include at least one correct answer for auto types) | Validation errors are clear | 2.5 h |
| Q4.4 | Start-attempt endpoint: records `started_at`; sets deadline from time limit | Second start while active returns the same attempt | 2 h |
| Q4.5 | Submit endpoint: rejects answers after deadline; auto-submits open attempts past deadline (checked on read) | Late submit rejected | 2.5 h |
| Q4.6 | Auto-grader: single, multiple (all correct required), true_false | Unit tests for each type | 2.5 h |
| Q4.7 | Attempt limit and best-score rule | Test: 2 attempts, best score kept | 1.5 h |
| Q4.8 | Essay answers: typed text, or file upload (PDF or image, max size set in settings) using `FileStorage` | Upload rejects other file types | 3 h |
| Q4.9 | Manual grading endpoints: score (0 to points), feedback, graded_by | Grade saved; points cannot exceed max | 2 h |
| Q4.10 | Attempt result: auto score, manual score (or "pending"), total | Total shows only when all parts are graded, or shows "partial" | 2 h |
| Q4.11 | Frontend: quiz builder for instructor (question types, options, points, timer) | Quiz saves and reloads correctly | 4 h |
| Q4.12 | Frontend: student exam page with countdown timer; warns at 1 minute | Timer matches server deadline | 3 h |
| Q4.13 | Frontend: essay answer box with text or file upload | Upload shows file name and status | 2.5 h |
| Q4.14 | Frontend: grading page for instructor/assistant (list of essays, score, feedback) | Grades save and learner sees them | 3 h |
| Q4.15 | Frontend: result page for student (auto score, manual score, pass or fail) | Shows pending state correctly | 1.5 h |
| Q4.16 | Phase 4 review against stories E4, K3, and ASM-1 to ASM-11 | Checklist in `docs/milestones/m4.md` ticked | 1 h |

---

## Phase 5 — Learning progress and admin (M3 and M5, about 40 h)

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| P5.1 | `Enrollment` model: user, course, status (active / dropped), enrolled_at | Migration applies | 1 h |
| P5.2 | Enroll and unenroll endpoints (free courses only) | Enrolling twice returns "already enrolled" | 1.5 h |
| P5.3 | `LessonProgress` model; mark complete and last-viewed endpoints | Progress saved per lesson | 1.5 h |
| P5.4 | Progress calculation: share of required lessons complete; course complete when all required lessons and quizzes passed | Unit tests for edge cases (no required lessons) | 2.5 h |
| P5.5 | "My courses" endpoint with progress percent and next lesson | Matches test data | 1.5 h |
| P5.6 | Frontend: course player with sidebar, next and previous, mark complete | Resume goes to first incomplete lesson | 4 h |
| P5.7 | Frontend: "My courses" dashboard with progress bars | Numbers match backend | 2 h |
| P5.8 | Admin user list: search, filter by role, pagination | Works with 200 test users | 2 h |
| P5.9 | Admin: change role (student, assistant, instructor, admin) | Change is logged in `AuditLog` (simple table) | 2 h |
| P5.10 | Admin: categories and platform settings screen (default recording days, invite days) | Changes apply immediately | 2 h |
| P5.11 | Admin: set recording days per course and per session | Access rule uses the new value | 1.5 h |
| P5.12 | Instructor reports: enrollments and completion rate per course; CSV export of learner progress | CSV opens in Excel with correct columns | 3 h |
| P5.13 | Admin overview: total users, courses, enrollments | Numbers update after changes | 1.5 h |
| P5.14 | Phase 5 review against stories E1–E3, I1, I2, J1, J2 | Checklist in `docs/milestones/m5.md` ticked | 1 h |

---

## Phase 6 — Hardening and launch (M6–M7, about 45 h)

| ID | Task | Done when | Est. |
|----|------|-----------|------|
| H6.1 | Real email adapter (Resend or SMTP) replacing the console adapter | Invite email reaches a real inbox | 2 h |
| H6.2 | Real file storage adapter (Cloudflare R2 or S3) replacing local folder | Upload and download work in production config | 3 h |
| H6.3 | Security headers, CORS allowlist, secure cookie settings | Scan with a security header checker shows no missing headers | 2 h |
| H6.4 | Rate limits on forgot-password and invite endpoints | Limits tested | 1.5 h |
| H6.5 | Error tracking (Sentry or similar) on backend and frontend | Test error appears in dashboard | 1.5 h |
| H6.6 | Database backup schedule and one tested restore | Restore into a new database works | 2.5 h |
| H6.7 | Privacy: student can download own data; admin can delete an account and its data | Deletion test removes personal data | 3 h |
| H6.8 | Accessibility pass: keyboard navigation, labels, contrast, alt text, using axe | No critical issues in axe report | 4 h |
| H6.9 | Mobile pass on a real phone: catalog, player, exam, QR scanner | Each flow usable on a phone screen | 3 h |
| H6.10 | Deploy backend (Render, Railway, or Fly.io) and frontend (Vercel or Netlify) with managed PostgreSQL | Public URL works with HTTPS | 4 h |
| H6.11 | Set up domain name and email sending domain (SPF, DKIM) | Verification email lands in inbox, not spam | 2 h |
| H6.12 | Write user guides: instructor, assistant, student (short, one page each) | Guides in `docs/guides/` | 3 h |
| H6.13 | Beta with 10–20 students; collect feedback in one shared list | Feedback list reviewed | 4 h |
| H6.14 | Launch checklist run-through | Checklist in `docs/launch.md` ticked | 1.5 h |

---

## Later (not in v1)

These are in the plan but not in any phase above: certificates (PRG-2), discussions (COM-2), announcements (COM-1, H1), notifications settings, Google sign-in, Zoom API integration (auto-create meetings and pull recordings), and payments (ENR-9 to ENR-14, suspended). Each one becomes a new phase when you decide to build it.

**Code editor (CODE-1 to CODE-3, not a priority):** a browser code editor (Monaco, the editor behind VS Code) inside lessons, for your programming and AI courses. Running student code is the hard part: it needs a sandbox service such as Judge0, or Pyodide to run Python in the browser. Decide on the runner when this phase starts.

**Gamification (GAM-1 to GAM-6, later):** start with attendance points, unit badges, and study streaks. Each is a small backend table (points or badges per user) plus a profile widget. Leaderboards stay off unless you decide otherwise.

---

## Definition of done

A task is done only when every item in its own "Done when" column is true **and** every item in the general checklist below is true. Use the same checklist for every task, so nothing is skipped when you're tired.

### Testing rules
1. **A separate sub agent writes the unit tests, not the agent that builds the function.** Before a function is built, the test agent writes its unit tests from the task's "Done when" (normal input, edge cases, and invalid input) and runs them, so they fail. The build agent then writes the function until the tests pass. The build agent must not edit those tests to make them pass; if a test looks wrong, it reports the problem back instead.
2. **Run the full test suite after every task.** A task is not done while any test fails, including tests from earlier tasks.
3. **Run the full test suite at the end of every phase**, plus the phase's manual checks in the browser (the "Done when" steps of each task, on a phone-width screen where a screen changed).
4. **Record the phase test result** in `docs/milestones/<phase>.md`: the command run, the number of tests passed, and any skipped tests with the reason.
5. **Never skip a failing test to finish a task.** Fix it, or write down the decision to change the test in the plan.

### General checklist (every task)
- [ ] Code runs locally with the documented command (no errors in the terminal or browser console)
- [ ] Tests added or updated for the new behaviour, and all tests pass
- [ ] Lint and format checks pass (ruff for backend, ESLint and Prettier for frontend)
- [ ] Permissions checked: the endpoint or screen refuses users who should not see it (test it with a student account)
- [ ] No secrets, passwords, or real student data in the code, the commit, or the logs
- [ ] Errors show a clear message to the user; nothing fails silently
- [ ] Works at phone width (about 400px) if the task changes a screen
- [ ] The task's ID is in the pull request title, and the PR description says what was checked by hand
- [ ] Any decision made during the task is written in the plan (PROJECT_PLAN.md) or in `docs/decisions/`
- [ ] Any diagram in `docs/` that this task changed is updated in the same task

### Task-level "Done when" format
Write the "Done when" column as a observable result, not an activity. Use this shape:

> **[ID] Task name** — Done when: *[actor]* can *[action]* and sees *[result]*; *[negative case]* is refused with *[message or status code]*.

Example, from task A1.11:
> **A1.11 Accept invite** — Done when: a student can open a valid invite link, set a password, and land on the login page with a success message; an expired or used link shows "This link has expired. Ask your teacher to send a new one." and no account is changed.

### Review step (each phase)
At the end of each phase, run the full test suite and the phase's manual checks, copy the checklist to `docs/milestones/<phase>.md`, tick each task, record the test result (see Testing rules), and write one line on anything that did not match the plan. The phase is done only when all its tasks are ticked.

## How to work through a task

1. Create a GitHub issue with the task ID in the title (for example `[A1.4] Login endpoint`).
2. Create a branch. A test sub agent writes the unit tests for the functions first (see Testing rules); then the build agent writes each function until its tests pass.
3. Open a pull request. CI must pass before you merge.
4. Tick the task in the phase review checklist when its "done when" is true.
