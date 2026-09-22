"""Shared pytest fixtures for scitex-git tests.

Also wires module-import-time coverage support for subprocess children
(see scitex_dev skill leaf 05_development_06_subprocess-coverage.md).

`os.environ.setdefault` is intentionally NOT used: pytest-cov has
already set COVERAGE_FILE to a tmp dir by the time conftest is loaded,
so `setdefault` would be a silent no-op.
"""

from __future__ import annotations

import os
import sysconfig
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pin coverage's data file at the repo root and point process_startup
# at our pyproject so child interpreters configure themselves correctly.
os.environ["COVERAGE_PROCESS_START"] = str(_PROJECT_ROOT / "pyproject.toml")
os.environ["COVERAGE_FILE"] = str(_PROJECT_ROOT / ".coverage")


def _ensure_subprocess_coverage_shim() -> None:
    """Drop an idempotent `.pth` file in site-packages that auto-starts
    coverage in every child Python interpreter via
    `coverage.process_startup()`.
    """
    purelib = Path(sysconfig.get_paths()["purelib"])
    pth = purelib / "_scitex_git_subprocess_coverage.pth"
    shim = (
        "import os, coverage\n"
        "if os.environ.get('COVERAGE_PROCESS_START'):\n"
        "    coverage.process_startup()\n"
    )
    try:
        if not pth.exists() or pth.read_text() != shim:
            pth.write_text(shim)
    except OSError:
        # site-packages may be read-only (e.g. system Python); silently
        # skip — local dev venvs are writable and that's where this matters.
        pass


_ensure_subprocess_coverage_shim()


_GIT_IDENTITY_ENV = {
    "GIT_AUTHOR_NAME": "Test User",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test User",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


@pytest.fixture(autouse=True)
def _git_identity():
    """Set git author/committer env vars so commits work in any environment.

    Uses save/restore pattern (no monkeypatch) per PA-306 no-mocks rule.
    """
    saved: dict[str, str | None] = {
        key: os.environ.get(key) for key in _GIT_IDENTITY_ENV
    }
    for key, value in _GIT_IDENTITY_ENV.items():
        os.environ[key] = value
    try:
        yield
    finally:
        for key, prev in saved.items():
            if prev is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prev
