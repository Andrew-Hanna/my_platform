"""Shared pytest setup.

The `app` package lives in backend/app (no src/ folder), so we add the
backend folder to sys.path. This lets `from app.main import app` work
no matter where pytest is started from.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
