# LMS (Learning Management System) — Project Plan

> Status: **draft v0.1**. Items marked **[Q]** are open questions to decide before building.
> Working assumption: a web-based LMS where instructors publish courses and learners enroll, study, and get assessed.

---

## 1. Vision and goals

- Let instructors create and deliver courses made of lessons, resources, and assessments.
- Let learners discover courses, enroll, learn at their own pace, and track progress.
- Give admins a way to manage users, roles, and platform settings.
- Provide basic reporting so instructors and admins can see how learners are doing.

**Out of scope for v1** (to keep the first release small):
- Live video classes and video conferencing
- Payments and subscriptions (unless **[Q1]** says otherwise)
- Native mobile apps (the web app should be responsive instead)
- Advanced AI features (auto-grading of essays, AI tutors)

---

## 2. Users and roles

| Role | Description |
|------|-------------|
| **Learner (Student)** | Browses the catalog, enrolls, consumes content, takes quizzes, earns certificates. |
| **Instructor** | Creates and edits own courses, manages enrolled learners, grades submissions, views course analytics. |
| **Admin** | Manages all users and roles, approves/unpublishes courses, configures platform settings. |
| **Assistant** | Helps the instructor: creates student accounts, grants session access, uploads content, and grades. Cannot change prices or course settings. |
| **Guest** | Can browse public course pages and sign up. |

Role rules:
- A user can be both learner and instructor, but permissions are checked per action.
- Only admins can grant or revoke the instructor role **[Q2]**: self-request with approval, or admin-only.

---

## 3. Feature list

Priority: **P0** = must have for v1, **P1** = should have, **P2** = later.

### 3.1 Accounts and authentication
| ID | Feature | Priority |
|----|---------|----------|
| AUTH-1 | Self sign-up with email and password (optional; students mainly get teacher-created accounts) | P2 |
| AUTH-2 | Log in / log out | P0 |
| AUTH-3 | Email verification | P0 |
| AUTH-4 | Password reset by email | P0 |
| AUTH-5 | Sign in with Google (OAuth) | P1 |
| AUTH-6 | Two-factor authentication (TOTP) | P2 |
| AUTH-7 | Session management (active sessions, sign out everywhere) | P2 |
| AUTH-8 | Teacher or assistant creates a student account and sends an invite; student sets their own password on first login | P0 |

### 3.2 User profile
| ID | Feature | Priority |
|----|---------|----------|
| PRO-1 | View and edit own profile (name, avatar, bio) | P0 |
| PRO-2 | Public instructor profile page | P1 |
| PRO-3 | Change password | P0 |
| PRO-4 | Notification preferences | P2 |

### 3.3 Course catalog and discovery
| ID | Feature | Priority |
|----|---------|----------|
| CAT-1 | Browse published courses | P0 |
| CAT-2 | Search courses by title and keyword | P0 |
| CAT-3 | Filter by category, level, and language | P1 |
| CAT-4 | Course detail page (description, syllabus, instructor, rating) | P0 |
| CAT-5 | Categories and tags managed by admin | P0 |
| CAT-6 | Course ratings and reviews | P1 |
| CAT-7 | Recommended courses | P2 |

### 3.4 Course authoring (instructor)
| ID | Feature | Priority |
|----|---------|----------|
| AUTH-C1 | Create, edit, delete own course (draft) | P0 |
| AUTH-C2 | Course structure: sections → lessons | P0 |
| AUTH-C3 | Lesson content types: rich text, video (link or upload), file attachment | P0 |
| AUTH-C4 | Reorder sections and lessons (drag and drop) | P0 |
| AUTH-C5 | Publish / unpublish course (admin may approve first, see [Q3]) | P0 |
| AUTH-C6 | Course cover image and description | P0 |
| AUTH-C7 | Course prerequisites | P1 |
| AUTH-C8 | Duplicate a course | P2 |
| AUTH-C9 | Scheduled publish date | P2 |

### 3.5 Enrollment and learning
| ID | Feature | Priority |
|----|---------|----------|
| ENR-1 | Enroll in a free course with one click | P0 |
| ENR-2 | "My courses" dashboard with progress bars | P0 |
| ENR-3 | Course player: navigate lessons in order, next/previous | P0 |
| ENR-4 | Mark lesson complete; progress saved automatically | P0 |
| ENR-5 | Resume where the learner left off | P0 |
| ENR-6 | Lock lessons until prerequisites are complete (optional per course) | P1 |
| ENR-7 | Unenroll / leave course | P1 |
| ENR-8 | Enrollment by invite code or instructor-added learners | P1 |
| ENR-9 | Paid course: learner sees price and InstaPay transfer details | Suspended |
| ENR-10 | Learner submits payment proof (InstaPay reference number and/or screenshot) | Suspended |
| ENR-11 | Instructor or admin confirms or rejects the payment; access is granted only after confirmation | Suspended |
| ENR-12 | Learner sees payment status (pending, confirmed, rejected) | Suspended |
| ENR-13 | Each payment reference can be used only once (prevents reusing a receipt) | Suspended |
| ENR-14 | Automatic payment gateway (Paymob, Fawry, Kashier, or bank API) with webhook confirmation | Suspended (P2 when resumed) |

### 3.6 Assessments
| ID | Feature | Priority |
|----|---------|----------|
| ASM-1 | Quiz with multiple choice and true/false questions | P0 |
| ASM-2 | Auto-grading for quizzes with pass mark | P0 |
| ASM-3 | Limit attempts and show best score | P1 |
| ASM-4 | Show correct answers after submit (instructor setting) | P1 |
| ASM-5 | Assignment: learner uploads file or text, instructor grades with feedback | P1 |
| ASM-6 | Fill-in-the-blank and matching questions | P2 |
| ASM-7 | Question bank reused across quizzes | P2 |
| ASM-8 | Essay questions: student types the answer or uploads a PDF/image | P0 |
| ASM-9 | Manual grading of essay answers with score and feedback (like Google Classroom) | P0 |
| ASM-10 | Timed exams with a countdown; submits automatically when time runs out | P0 |
| ASM-11 | Mixed exam: auto-graded part and manually graded part, shown as one total | P0 |

### 3.7 Progress, certificates, and grades
| ID | Feature | Priority |
|----|---------|----------|
| PRG-1 | Course completion when all required lessons and quizzes are passed | P0 |
| PRG-2 | Certificate of completion (PDF with unique ID) | P1 |
| PRG-3 | Public certificate verification page | P2 |
| PRG-4 | Gradebook view for learner (all scores in one place) | P1 |

### 3.8 Communication
| ID | Feature | Priority |
|----|---------|----------|
| COM-1 | Announcements from instructor to enrolled learners | P1 |
| COM-2 | Discussion thread per lesson or course | P1 |
| COM-3 | Direct messages between learner and instructor | P2 |
| COM-4 | Email notifications (enrollment, new announcement, grade posted) | P1 |
| COM-5 | Calendar of due dates | P2 |

### 3.9 Admin
| ID | Feature | Priority |
|----|---------|----------|
| ADM-1 | List, search, and view all users | P0 |
| ADM-2 | Change user role (learner / instructor / admin) | P0 |
| ADM-3 | Disable or delete user account | P0 |
| ADM-4 | Review and approve/reject courses submitted for publishing | P1 |
| ADM-5 | Manage categories and tags | P0 |
| ADM-6 | Platform settings (site name, logo, default language, registration on/off) | P1 |
| ADM-7 | Audit log of admin actions | P2 |
| ADM-8 | Set and change the recording access length (in days) per course or per session | P0 |
| ADM-9 | Admin or teacher sets the Zoom join link for each session, or sets one link for all sessions at once; each session can change it later | P0 |

### 3.10 Reporting and analytics
| ID | Feature | Priority |
|----|---------|----------|
| RPT-1 | Instructor: enrollments and completion rate per course | P1 |
| RPT-2 | Instructor: per-learner progress table with CSV export | P1 |
| RPT-3 | Admin: platform totals (users, courses, enrollments) | P1 |
| RPT-4 | Quiz item analysis (which questions are missed most) | P2 |

### 3.11 Live sessions, recordings, and attendance
| ID | Feature | Priority |
|----|---------|----------|
| LIVE-1 | Session schedule: title, date, time, and optional price | P0 |
| LIVE-2 | "Join" button on the session page, shown only to students with access; the meeting link is fetched on click and never shown as text | P0 |
| LIVE-3 | Teacher or admin enters the Zoom recording link for each session (recordings are hosted in Zoom) | P0 |
| LIVE-4 | Grant access to a session's recording per student (admin, instructor, or assistant) | P0 |
| LIVE-5 | Recording access expires after a set number of days; admin sets the default and can change it per course or session | P0 |
| LIVE-6 | Free access grant for students who had a technical problem during the live session | P0 |
| LIVE-7 | Attendance by QR code: a code is shown on screen and students scan it in the app | P0 |
| LIVE-8 | Attendance report per session | P1 |
| LIVE-9 | Watermark and one-device rule: not built (Zoom-only protection, see Q17) | Not built |
| LIVE-10 | Payment per session (suspended; see ENR-9 to ENR-14) | Suspended |
| LIVE-11 | Session notes: the instructor writes notes for each session; students with access read them on the platform (not a PDF download) | P0 |

### 3.11b Booklets (teacher study booklets)
| ID | Feature | Priority |
|----|---------|----------|
| BK-1 | Booklet with title, description, and units in order (for example Unit 1, Unit 2) | P0 |
| BK-2 | Instructor or assistant uploads each unit's booklet file | P0 |
| BK-3 | Students with access read booklets in an online viewer; no download and no print buttons | P0 |
| BK-4 | Files are stored privately; viewer links are short-lived and work only for students with access | P0 |
| BK-5 | Access is granted per booklet by the instructor, assistant, or admin | P0 |
| BK-6 | Price per booklet (payment suspended; access is granted manually for now) | Suspended |

### 3.11c Code editor for programming and AI courses (later, not a priority)
| ID | Feature | Priority |
|----|---------|----------|
| CODE-1 | Code editor inside a lesson, so students write and edit code on the platform | P2 |
| CODE-2 | Run Python code from the editor and show the output (needs a sandbox service) | P2 |
| CODE-3 | Instructor provides starter code and expected output for exercises | P2 |

### 3.11d Gamification (later)
| ID | Feature | Priority |
|----|---------|----------|
| GAM-1 | Attendance points: each QR check-in adds points to the student's profile | P2 |
| GAM-2 | Unit badges: finishing a booklet unit or a lesson unit earns a badge | P2 |
| GAM-3 | Study streaks: consecutive days with activity; one freeze per month can save a streak | P2 |
| GAM-4 | Quiz badges: perfect score, or pass on the first attempt | P2 |
| GAM-5 | Progress levels from total points | P2 |
| GAM-6 | Leaderboard, opt-in only, shows top few or ranks by improvement (not built unless you ask) | P2 |

### 3.12 Non-functional requirements (cross-cutting)
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Responsive layout that works on phone, tablet, and desktop | P0 |
| NFR-2 | Accessibility: WCAG 2.1 AA target, keyboard navigation, alt text, captions for uploaded video | P0 |
| NFR-3 | Security: hashed passwords, HTTPS, CSRF protection, role checks on every API call, rate limiting on login | P0 |
| NFR-4 | Privacy: learners can export or delete their data (GDPR-style) | P1 |
| NFR-5 | Performance: course pages load in under 2 s on a typical connection | P1 |
| NFR-6 | Backups: daily database backup with tested restore | P0 before launch |
| NFR-7 | Localization-ready (all UI strings in translation files) | P1 |
| NFR-8 | Logging and error monitoring | P1 |

---

## 4. User stories

Format: **As a** [role], **I want** [goal], **so that** [benefit].
Each story has acceptance criteria (AC). Stories are grouped by epic.

### Epic A — Accounts

**A1 (P0) Sign up**
As a guest, I want to create an account with my email and password, so that I can enroll in courses.
- AC1: Email must be valid and unique; password must be at least 8 characters.
- AC2: After sign-up, a verification email is sent and the user cannot enroll until verified.
- AC3: Errors (duplicate email, weak password) are shown next to the field.

**A2 (P0) Log in**
As a registered user, I want to log in, so that I can access my courses.
- AC1: Wrong credentials show a generic message ("Email or password is incorrect").
- AC2: After 5 failed attempts in 15 minutes, further attempts are blocked for 15 minutes.
- AC3: "Remember me" keeps the session for 30 days.

**A3 (P0) Reset password**
As a user who forgot my password, I want to reset it by email, so that I can regain access.
- AC1: Reset link expires after 1 hour and works once.
- AC2: The response to "forgot password" is the same whether or not the email exists.

### Epic B — Profile

**B1 (P0) Edit profile**
As a user, I want to edit my name, avatar, and bio, so that others recognize me.
- AC1: Avatar accepts JPG/PNG up to 2 MB.
- AC2: Changes are saved and shown immediately.

### Epic C — Catalog

**C1 (P0) Browse and search**
As a learner, I want to search and browse published courses, so that I can find something to learn.
- AC1: Only courses with status "published" appear.
- AC2: Search matches title, short description, and tags.
- AC3: Results show title, instructor, rating, level, and cover image.

**C2 (P0) Course detail**
As a learner, I want to read a course's description and syllabus before enrolling, so that I know if it fits me.
- AC1: Page shows description, list of sections and lesson titles, instructor name, and an "Enroll" button.
- AC2: Logged-out users see the page and are asked to log in when they click "Enroll".

### Epic D — Course authoring

**D1 (P0) Create a course**
As an instructor, I want to create a course draft with a title, description, and cover image, so that I can start building it.
- AC1: New courses start as "draft" and are visible only to the author and admins.

**D2 (P0) Build course structure**
As an instructor, I want to add sections and lessons and reorder them by drag and drop, so that the course flows logically.
- AC1: Adding, renaming, and deleting sections and lessons works without page reload.
- AC2: Order is saved after each drag.

**D3 (P0) Add lesson content**
As an instructor, I want to write rich text, embed a video, or attach files to a lesson, so that learners have material to study.
- AC1: Video can be an uploaded file or a link (YouTube/Vimeo).
- AC2: Attached files up to 100 MB each; file types are restricted to an allowlist.

**D4 (P0) Publish a course**
As an instructor, I want to publish my course, so that learners can enroll.
- AC1: Publishing requires at least one lesson and a cover image.
- AC2: After publishing, edits go to a draft copy and do not change the live version until republished **[Q3]**.

**D5 (P0) Create a quiz**
As an instructor, I want to add a quiz with single- and multiple-choice questions, so that I can check learner understanding.
- AC1: Each question has at least two options and one or more correct answers.
- AC2: Quiz has a pass mark (percent) and optional attempt limit.

### Epic E — Enrollment and learning

**E1 (P0) Enroll**
As a learner, I want to enroll in a free course, so that I can start learning.
- AC1: Enrolling is one click and redirects to the course player.
- AC2: Enrolling twice does nothing and shows "Already enrolled".

**E2 (P0) Learn through lessons**
As a learner, I want to move through lessons in order with next and previous buttons, so that I can study without getting lost.
- AC1: Sidebar shows all sections and lessons with a check mark on completed ones.
- AC2: Video and file content open inside the page.

**E3 (P0) Track progress**
As a learner, I want my progress saved automatically and shown as a percentage, so that I can pick up where I stopped.
- AC1: Marking a lesson complete updates the progress bar on "My courses" within 1 second.
- AC2: Reopening the course goes to the first incomplete lesson.

**E4 (P0) Take a quiz**
As a learner, I want to take a quiz and see my score, so that I know whether I passed.
- AC1: Score and pass/fail are shown right after submit.
- AC2: If the instructor allows it, correct answers are shown after submit.
- AC3: Best score is kept when multiple attempts are allowed.

**E5 (P1) Lesson prerequisites**
As an instructor, I want to lock later lessons until earlier ones are done, so that learners follow the intended path.
- AC1: Locked lessons show a lock icon and the reason.

**E6 (Suspended) Pay for a paid course via InstaPay**
As a learner, I want to pay for a course by InstaPay and tell the platform, so that I get access once my payment is confirmed.
- AC1: The course page shows the price and the InstaPay account or handle to send to.
- AC2: The learner enters the InstaPay reference number and can attach a screenshot, then the enrollment shows "Payment pending".
- AC3: The learner gets access only after the instructor or admin confirms the payment. Rejected payments show the reason and allow a new submission.
- AC4: A reference number that was already used is refused with a clear message.

### Epic F — Assignments and grading

**F1 (P1) Submit assignment**
As a learner, I want to upload a file or write text for an assignment, so that my instructor can grade it.
- AC1: Submission shows "Submitted on [date]" and can be resubmitted before the due date.

**F2 (P1) Grade assignment**
As an instructor, I want to grade submissions with a score and written feedback, so that learners know how they did.
- AC1: Learner gets an email when a grade is posted.
- AC2: Grades can be edited later and the change is logged.

### Epic G — Certificates

**G1 (P1) Earn certificate**
As a learner, I want a certificate when I finish a course, so that I can show what I learned.
- AC1: Certificate is issued automatically when all required items are complete.
- AC2: Certificate PDF contains learner name, course title, date, and a unique ID.

### Epic H — Communication

**H1 (P1) Announcements**
As an instructor, I want to post announcements to all enrolled learners, so that they see important updates.
- AC1: Learners receive an email and an in-app notification.

**H2 (P1) Discussions**
As a learner, I want to ask questions in a discussion thread on a lesson, so that I can get help.
- AC1: Instructor can reply and mark a reply as the answer.
- AC2: Users can report inappropriate posts; reports appear in admin queue.

### Epic I — Admin

**I1 (P0) Manage users**
As an admin, I want to search users, change roles, and disable accounts, so that I can keep the platform safe.
- AC1: Disabled users cannot log in but their data is kept.
- AC2: Every role change is recorded in the audit log (P2) or at least in the database.

**I2 (P0) Manage categories**
As an admin, I want to create, rename, and remove categories and tags, so that the catalog stays organized.
- AC1: Removing a category in use asks to reassign courses first.

**I3 (P1) Approve courses**
As an admin, I want to review courses before they go public, so that quality stays consistent **[Q3]**.
- AC1: Admin can approve, or reject with a reason that the instructor sees.

### Epic J — Reporting

**J1 (P1) Course analytics**
As an instructor, I want to see enrollments and completion rate for each course, so that I know what is working.
- AC1: Charts update when the date range changes.
- AC2: Per-learner progress table can be exported as CSV.

**J2 (P1) Platform overview**
As an admin, I want totals for users, courses, and enrollments, so that I can track growth.

---

### Epic K — Live sessions, exams, and accounts

**K1 (P0) Watch a session recording**
As a student with access to a session, I want to watch its recording for a set number of days, so that I can catch up.
- AC1: Access ends after the number of days set by the admin.
- AC2: The recording link is shown only while my access is valid.
- AC3: Downloads and sign-in are controlled by the teacher's Zoom settings.

**K2 (P0) Check in by QR code**
As a teacher, I want students to scan a QR code on screen to check in, so that attendance is recorded without a paper list.
- AC1: The code changes every session and cannot be reused in another session.
- AC2: The attendance report shows who checked in and when.

**K3 (P0) Timed exam with mixed questions**
As a teacher, I want an exam with a timer that auto-grades multiple choice and true/false and lets me grade essays by hand, so that I can run exams like Google Classroom.
- AC1: A countdown is always visible; the exam submits automatically at zero.
- AC2: The auto-graded score appears right after submit; the essay score appears once I grade it.

**K4 (P0) Create a student account**
As an assistant, I want to create a student account and send an invite, so that the student sets their own password.
- AC1: The invite link expires after 3 days; an expired link can be resent by a teacher or assistant.
- AC2: The student must set a password before the first login.

---

## 5. Technical approach (decided; details in TASKS.md)

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | React + TypeScript (Vite) | Separate app that talks to the FastAPI backend; works well on phones |
| Backend | Python 3.12 + FastAPI (SQLAlchemy 2, Alembic, Pydantic v2) | Matches your Python and FastAPI experience; services are isolated behind interfaces so providers can change |
| Database | PostgreSQL | Relational data fits courses → sections → lessons → progress |
| Auth | Email + password, HTTP-only cookie sessions, invite links | Teacher-created accounts; no third-party auth service needed |
| File storage | Local folder in dev; S3-compatible (Cloudflare R2) later | Booklet PDFs and essay uploads, kept private |
| Video | Zoom hosts recordings; the platform stores links | See Q17 |
| Email | Console printer in dev; Resend or SMTP later | Invites, verification, reset |
| Background jobs | Not needed in v1; add a queue only if email or PDF work gets slow | Keeps the stack small |
| UI | Tailwind CSS (add a component library later if needed) | Simple to start |
| Testing | pytest (backend), Vitest (frontend), Playwright later | Covers core flows |
| Hosting | Backend on Render, Railway, or Fly.io; frontend on Vercel or Netlify; managed PostgreSQL | Simple first deploy |
| CI | GitHub Actions: lint, typecheck, test, build | Catches breakage early |

### 5.1 Core data model (first draft)

- **User**: id, name, email, password_hash, role (learner | instructor | admin), email_verified_at, avatar_url, bio, status (active | disabled), created_at
- **Category**: id, name, slug
- **Course**: id, title, slug, short_description, description, cover_url, level, language, category_id, instructor_id, status (draft | pending_review | published | archived), published_at, created_at, updated_at
- **Section**: id, course_id, title, position
- **Lesson**: id, section_id, title, type (text | video | file | quiz | assignment), content (rich text / video URL / file key), position, is_required
- **Enrollment**: id, user_id, course_id, enrolled_at, completed_at, status (pending_payment | active | dropped)
- **Payment** (suspended; keep the table design, do not build until resumed): id, enrollment_id, user_id, amount, currency, method (instapay), reference_number (unique), proof_url (optional screenshot), status (submitted | confirmed | rejected), confirmed_by, confirmed_at, reject_reason, created_at
- **LessonProgress**: id, enrollment_id, lesson_id, completed_at, last_position
- **Quiz**: id, lesson_id, pass_percent, max_attempts, show_answers, time_limit_minutes (nullable)
- **Question**: id, quiz_id, text, type (single | multiple | true_false | essay), points, position
- **Essay answer**: id, question_id, user_id, typed_text (nullable), file_key (nullable, PDF or image), score (nullable), feedback, graded_by, graded_at
- **Session**: id, course_id, title, starts_at, ends_at, join_url, recording_url (nullable), access_days (nullable; overrides the course or platform default), price (suspended), created_at
- **Attendance**: id, session_id, user_id, method (qr | manual), checked_in_at
- **AccessGrant**: id, user_id, session_id, reason (paid | free_tech_issue | manual), granted_by, granted_at, expires_at
- **Option**: id, question_id, text, is_correct
- **QuizAttempt**: id, quiz_id, user_id, score, passed, submitted_at
- **Assignment / Submission / Grade**: submission linked to assignment lesson and user, with score, feedback, graded_by, graded_at
- **Certificate**: id, enrollment_id, public_id, issued_at
- **Announcement**, **Thread**, **Post**, **Report**: for communication (P1)
- **AuditLog**: id, actor_id, action, target_type, target_id, meta, created_at

---

## 6. Milestones

Estimated effort assumes one developer working part time. Adjust after **[Q4]**.

| Phase | Goal | Includes | Done when |
|-------|------|----------|-----------|
| **M0 — Setup** | Project skeleton runs | Repo structure, linting, TypeScript, DB, CI, env config, dev docker-compose | `npm run dev` and tests run in CI |
| **M1 — Accounts** | Users can sign up and log in | AUTH-1 to AUTH-4, PRO-1, PRO-3, roles | Sign-up, verify, login, reset all work end to end |
| **M2 — Catalog and authoring** | Instructors can publish a course | CAT-1 to CAT-5, AUTH-C1 to AUTH-C6, D1 to D4, admin categories | A published course is visible in the catalog |
| **M3 — Learning** | Learners can enroll and finish lessons | ENR-1 to ENR-5, E1 to E3, PRG-1 | Full learner path works on mobile and desktop |
| **M3b — Live sessions** | Live sessions, recordings, and attendance work | LIVE-1 to LIVE-7, AUTH-8 | An in-person class runs end to end, with QR attendance and a recording |
| **M4 — Assessment** | Quizzes graded | ASM-1, ASM-2, E4, ASM-3, ASM-4, ASM-8 to ASM-11 | Quiz score recorded and shown |
| **M5 — Admin and reporting** | Admin tools and basic analytics | ADM-1 to ADM-3, ADM-5, RPT-1, RPT-2, RPT-3 | Admin can manage users and see course stats |
| **M6 — Beta hardening** | Ready for real users | NFR-2, NFR-3, NFR-6, NFR-8, accessibility audit, load test, security review | Beta with 10 to 20 real learners |
| **M7 — v1 launch** | Public release | P1 items chosen in **[Q5]**, docs, onboarding | Launch checklist complete |

---

## 7. Setup checklist (do this before M1)

- [ ] Decide answers to the open questions in section 8
- [ ] Choose stack from section 5 (or change it) and record in `docs/decisions/`
- [ ] Create project skeleton (`src/`, `tests/`, `docs/`, `.env.example`)
- [ ] Add `.gitignore`, `README.md` with run instructions, and `CONTRIBUTING.md`
- [ ] Set up TypeScript, ESLint, Prettier, and a pre-commit hook
- [ ] Set up Docker Compose with PostgreSQL (and Redis if queues are used) and MinIO for local file storage
- [ ] Set up the ORM and first migration (User, Category)
- [ ] Set up email in dev mode (e.g. Mailpit) so verification emails can be seen locally
- [ ] Set up GitHub Actions: lint, typecheck, test, build on every pull request
- [ ] Create a project board (GitHub Projects or Trello) with one column per milestone
- [ ] Write the first user stories from epics A to D as issues

---

## 8. Decisions

Status key: **Decided** = fixed for v1. **Assumed** = default chosen without your input; confirm or change.

| # | Question | Decision | Status |
|---|----------|----------|--------|
| Q1 | Will courses be paid? | Payment is suspended for now. All courses are free to enroll in while it is off. When resumed, payment goes through InstaPay with manual confirmation (ENR-9 to ENR-13), and automatic gateway integration is later (ENR-14). | Decided (payment suspended) |
| Q2 | Can learners request to become instructors? | No. Only admins grant or revoke the instructor role. | Decided |
| Q3 | Do courses need admin approval before going live? | No for v1. Instructors publish directly; admins can unpublish at any time. Approval flow (ADM-4, I3) stays P1 and can be switched on later. | Decided |
| Q4 | Who is building it, how many hours per week, and when is launch? | Part time, no fixed launch date. Exact hours per week are unknown; milestones are not tied to dates. | Assumed |
| Q5 | Who are the first users? | Private beta with 10–20 learners (M6), then public v1 launch (M7). | Assumed |
| Q6 | Languages at launch? | English only, with all UI strings kept in translation files (NFR-7 moves to P1). | Decided |
| Q7 | Hosting budget and preference? | Managed cloud on free or low-cost tiers (e.g. Vercel, managed Postgres, Cloudflare R2). No self-hosting in v1. | Assumed |
| Q8 | Compliance needs? | Basic GDPR-style privacy (export and delete, NFR-4). No children's data in v1; revisit if a school uses it. | Assumed |
| Q9 | Brand, name, and logo? | None yet. Use the placeholder name "LMS" until a name is chosen. | Assumed |
| Q10 | Who manages courses? | You now, with assistants helping. More teachers may come later, so roles must allow it. | Decided |
| Q11 | How do students get accounts? | A teacher or assistant creates the account and sends an invite; the student sets their own password. | Decided |
| Q12 | What does a payment buy? | One session at a time. Payment is suspended, so access is granted manually for now. | Decided |
| Q13 | How long is a recording available? | 7 days by default; the admin can change it per course or per session. | Decided |
| Q14 | How do exams work? | Timed. A mix of auto-graded questions (MCQ, true/false) and essays that are uploaded or typed and graded by hand. | Decided |
| Q15 | How strict is anti-sharing and attendance? | Stronger protection (watermark, one device) and QR attendance for in-person students. Revisit the protection before building it. | Decided (revisit) |
| Q16 | Trials and tech-problem recordings? | No free trial sessions. Recordings for students with technical problems are granted free by a teacher or assistant. | Decided |
| Q17 | Where are recordings hosted? | Zoom cloud recordings. The teacher or admin enters each session's join link and recording link (one link can be applied to all sessions). The platform shows the recording link only while access is valid (7 days by default). Zoom's own settings (downloads, sign-in, waiting room, passcode, share-link removal) are handled by the owner in the Zoom app. Watermark and one-device rules are not built. | Decided |
| Q18 | Backend and frontend? | FastAPI backend (Python), React + Vite frontend. Services are isolated behind interfaces. | Decided |
| Q19 | Launch language? | English only. | Decided |
| Q20 | Time available? | Under 5 hours per week; the task breakdown in TASKS.md is sized for that. | Decided |
| Q23 | Can assistants manage every course? | No. Assistants act only on courses assigned to them (CourseStaff, task A1.17d). | Decided |
| Q24 | Does accepting an invite verify the email? | Yes. Public sign-up is removed from v1. | Decided |
| Q25 | Video in v1? | Links only (YouTube, Vimeo, or Zoom). No video uploads in v1. | Decided |
| Q26 | What is sold? | One session at a time, per the second review's default. Booklets are granted, not priced, until payment resumes. | Assumed (confirm) |
| Q27 | How long does a booklet read link last? | 5 minutes, then the viewer requests a new one. Recommended; not yet confirmed. | Recommended |
| Q28 | Keep "remember me" at login? | Drop it for v1. Recommended; not yet confirmed. | Recommended |
| Q22 | How are booklets sold and read? | Sold per booklet, split into units. Students read online with no download or print. The viewer can't stop screenshots. Booklets are uploaded as PDF files. | Decided |
| Q21 | How do students get the session notes? | Read on the platform, shown only to students with access to that session. No PDF download. Students can still copy text, which can't be fully prevented. | Decided |

Items marked **Assumed** that need your real input: Q4 (weekly hours and any target date), Q5 (who the beta users are), Q7 (budget), and Q9 (name).

---

## 9. Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Scope creep (video, payments, AI) | Project never ships | Keep P2 list separate; freeze v1 scope at M2 |
| Video storage and bandwidth costs | High cost | Use link embeds or a hosted video service first |
| Security mistakes in auth and file uploads | Data leak | Use a proven auth library; validate file types; role checks on every API route; security review in M6 |
| Accessibility issues found late | Rework | Use accessible component library; test with keyboard and screen reader each milestone |
| Single developer bottleneck | Slow progress | Keep milestones small; use the setup checklist to avoid early yak-shaving |

---

## 10. Glossary

- **Course**: a set of sections and lessons with a single instructor.
- **Section**: a group of lessons inside a course (like a chapter).
- **Lesson**: one learning item: text, video, file, quiz, or assignment.
- **Enrollment**: the link between a learner and a course.
- **Progress**: the share of required lessons completed in an enrollment.
- **Certificate**: a PDF issued when a course is completed.
