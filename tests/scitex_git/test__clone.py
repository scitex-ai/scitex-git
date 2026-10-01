#!/usr/bin/env python3

"""Tests for git clone operations."""


import pytest

pytest.importorskip("git")

from scitex_git._clone import clone_repo, git_init


class TestGitInit:
    """Tests for git_init function."""

    def test_git_init_returns_true_on_success(self, tmp_path):
        # Arrange
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        # Act
        result = git_init(repo_path, verbose=False)
        # Assert
        assert result is True

    def test_git_init_creates_dot_git_directory(self, tmp_path):
        # Arrange
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        # Act
        git_init(repo_path, verbose=False)
        # Assert
        assert (repo_path / ".git").exists()

    def test_git_init_returns_false_when_already_initialized(self, tmp_path):
        # Arrange
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_init(repo_path, verbose=False)
        # Act
        result = git_init(repo_path, verbose=False)
        # Assert
        assert result is False

    def test_git_init_creates_main_as_active_branch(self, tmp_path):
        # Arrange
        from git import Repo

        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_init(repo_path, verbose=False)
        (repo_path / "test.txt").write_text("test")
        repo = Repo(repo_path)
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")
        # Act
        active = repo.active_branch.name
        # Assert
        assert active == "main"


class TestCloneRepo:
    """Tests for clone_repo function."""

    def test_clone_invalid_url_returns_false(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        # Act
        result = clone_repo("invalid-url", target_path, verbose=False)
        # Assert
        assert result is False

    def test_clone_unknown_host_url_returns_false(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        # Act
        result = clone_repo(
            "https://invalid.com/user/repo.git", target_path, verbose=False
        )
        # Assert
        assert result is False

    def test_clone_with_branch_and_tag_raises_value_error(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        url = "https://github.com/user/repo.git"
        # Act
        ctx = pytest.raises(ValueError)
        # Assert
        with ctx:
            clone_repo(url, target_path, branch="main", tag="v1.0.0", verbose=False)

    def test_clone_with_branch_and_tag_error_mentions_mutually_exclusive(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        url = "https://github.com/user/repo.git"
        # Act
        try:
            clone_repo(url, target_path, branch="main", tag="v1.0.0", verbose=False)
            msg = ""
        except ValueError as exc:
            msg = str(exc).lower()
        # Assert
        assert "mutually exclusive" in msg

    def test_clone_with_branch_only_for_nonexistent_repo_returns_false(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        url = "https://github.com/nonexistent/repo.git"
        # Act
        result = clone_repo(url, target_path, branch="develop", verbose=False)
        # Assert
        assert result is False

    def test_clone_with_tag_only_for_nonexistent_repo_returns_false(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        url = "https://github.com/nonexistent/repo.git"
        # Act
        result = clone_repo(url, target_path, tag="v1.0.0", verbose=False)
        # Assert
        assert result is False

    def test_clone_without_branch_or_tag_for_nonexistent_repo_returns_false(self, tmp_path):
        # Arrange
        target_path = tmp_path / "cloned"
        url = "https://github.com/nonexistent/repo.git"
        # Act
        result = clone_repo(url, target_path, verbose=False)
        # Assert
        assert result is False


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
