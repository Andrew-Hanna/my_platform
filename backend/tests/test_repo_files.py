"""Task S0.5: the repo has a safe .env.example and a .gitignore that ignores .env."""

from pathlib import Path

# tests/ -> backend/ -> my_platform/ (the repository root)
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_env_example_has_placeholder_database_url():
    """Task S0.5: .env.example has a DATABASE_URL= line with a placeholder value.

    Simple check: the value must contain "change-me" or "localhost".
    Real connection strings usually point at a real host, so this is a rough
    guard against committing a real password. It is not a full secret scanner.
    """
    env_example = REPO_ROOT / ".env.example"
    assert env_example.exists(), ".env.example is missing from the repo root"

    lines = env_example.read_text().splitlines()
    db_lines = [line for line in lines if line.startswith("DATABASE_URL=")]
    assert db_lines, "no line starting with DATABASE_URL= in .env.example"

    value = db_lines[0].split("=", 1)[1]
    assert "change-me" in value or "localhost" in value


def test_gitignore_ignores_dot_env():
    """Task S0.5: .gitignore has a line ".env" so the real secrets file is never committed.

    This test fails until .gitignore is created in the repo root.
    """
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore is missing from the repo root"

    lines = [line.strip() for line in gitignore.read_text().splitlines()]
    assert ".env" in lines
