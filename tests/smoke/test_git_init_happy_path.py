"""Smoke: ``git_init`` creates a repo in a subprocess (PS-211).

Subprocess-driven (``sys.executable -c ...``) so this proves the
installed package resolves its hard dependencies — an in-process call
would not. Hermetic: local ``git init`` only, no network, no
credentials, no writes outside the pytest tmp dir.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(shutil.which("git") is None, reason="git CLI not installed"),
]

CODE = "\n".join(
    [
        "import sys",
        "from pathlib import Path",
        "import scitex_git as sxg",
        "target = Path(sys.argv[1])",
        "target.mkdir(parents=True, exist_ok=True)",
        "ok = sxg.git_init(target, verbose=False)",
        "print('OK' if ok else 'FAIL')",
    ]
)


def test_git_init_in_subprocess(tmp_path) -> None:
    # Arrange
    argv = [sys.executable, "-c", CODE, str(tmp_path / "repo")]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert (completed.returncode, completed.stdout.strip()) == (0, "OK")
