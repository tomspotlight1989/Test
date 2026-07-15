"""Environment and credential loading for the UK Energy /last30days skill."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent


def _find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / ".git").exists():
            return parent
    # Fallback: assume the conventional .claude/skills/<name>/scripts nesting.
    return start.parents[3] if len(start.parents) >= 3 else start


REPO_ROOT = _find_repo_root(SCRIPTS_DIR)
DEFAULT_SAVE_DIR = Path(os.environ.get("UK_ENERGY_SAVE_DIR", str(REPO_ROOT / "guides")))

_env_loaded = False


def load_env() -> None:
    """Load a .env file from the skill directory or CWD, if present. Idempotent."""
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True
    if load_dotenv is None:
        return
    for candidate in (SKILL_DIR / ".env", Path.cwd() / ".env"):
        if candidate.exists():
            load_dotenv(candidate)


def credential(env_var: str) -> str | None:
    """Read a named credential from the environment (after load_env() has run)."""
    return os.environ.get(env_var) or None
