"""E2E: init → add → commit → branch roundtrip on a real repo (PS-212).

No network, no mocks — drives the real helpers end to end against a
local repo. Commit identity comes from ``GIT_AUTHOR_*``/``GIT_COMMITTER_*``
env vars (no global git config touched). Gated on ``RUN_E2E=1`` so the
default unit run stays fast.
"""

from __future__ import annotations

import os
import shutil

import pytest

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(os.environ.get("RUN_E2E") != "1", reason="RUN_E2E!=1"),
    pytest.mark.skipif(shutil.which("git") is None, reason="git CLI not installed"),
]

_IDENTITY_VARS = (
    "GIT_AUTHOR_NAME",
    "GIT_AUTHOR_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_COMMITTER_EMAIL",
)


def test_repo_lifecycle_roundtrip(tmp_path) -> None:
    import scitex_git as sxg

    # Arrange
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    previous = {name: os.environ.get(name) for name in _IDENTITY_VARS}
    os.environ["GIT_AUTHOR_NAME"] = "SciTeX Test"
    os.environ["GIT_AUTHOR_EMAIL"] = "test@scitex.ai"
    os.environ["GIT_COMMITTER_NAME"] = "SciTeX Test"
    os.environ["GIT_COMMITTER_EMAIL"] = "test@scitex.ai"
    try:
        # Act
        ok_init = sxg.git_init(repo, verbose=False)
        (repo / "note.txt").write_text("hello\n")
        ok_add = sxg.git_add_all(repo, verbose=False)
        ok_commit = sxg.git_commit(repo, message="initial", verbose=False)
        ok_branch = sxg.git_checkout_new_branch(repo, "feature/x", verbose=False)
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    # Assert
    assert (ok_init, ok_add, ok_commit, ok_branch) == (True, True, True, True)
