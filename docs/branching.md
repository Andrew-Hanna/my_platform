# Branching and environments

## Branches

| Branch | Purpose | Deployed to | Who changes it |
|--------|---------|-------------|----------------|
| `main` | Integrated development. Every merged task lands here first. | Nothing (CI only) | Pull requests from task branches |
| `testing` | Test environment for the owner and assistants to try new features. | Test environment | Pull requests from `main` |
| `staging` | Release candidate. Same settings as production, with test data. | Staging environment | Pull requests from `testing` |
| `production` | What real students use. | Production environment | Pull requests from `staging` only |

## Flow

```
task branch  ──PR──▶  main  ──PR──▶  testing  ──PR──▶  staging  ──PR──▶  production
 (one per task)       (CI)           (try it)          (final check)     (students)
```

1. Create a branch per task from `main`, named after the task ID (for example `a1-4-login`).
2. Open a pull request into `main`. CI must pass before merging.
3. When a set of tasks is ready, open a pull request from `main` into `testing`.
4. When testing is accepted, open a pull request from `testing` into `staging` and check it on staging with test data.
5. When staging is accepted, open a pull request from `staging` into `production`. Tag the release (for example `v1.0.0`) after it merges.

Never commit straight to `testing`, `staging`, or `production`. Hotfixes go through `main` first, then are promoted the same way.

## Environment settings

Each environment has its own `.env` file on its server. Nothing is committed. Templates are in `.env.example` (names and placeholders only).

| Setting | Test | Staging | Production |
|---------|------|---------|------------|
| Database | Separate test database | Separate staging database | Production database |
| Email | Test sender, captures mail | Real sender, test recipients | Real sender |
| Zoom links | Test meetings | Test meetings | Real meetings |
| Data | Made-up data | Copy of made-up data | Real student data |
| Debug mode | On | Off | Off |

## GitHub settings (do once)

Set these in the repository's Settings, which cannot be set from the code:

- **Branch protection on `main`, `testing`, `staging`, and `production`:** require a pull request, require the CI checks to pass, and block force pushes.
- **Production only:** also require one approval before merging.
- **Default branch:** `main`.
