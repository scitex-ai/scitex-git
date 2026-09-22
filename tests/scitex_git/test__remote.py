#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pytest

pytest.importorskip("git")

from scitex_git._remote import (
    _normalize_git_url,
    _validate_git_url,
    get_remote_url,
    is_cloned_from,
)


class TestGitRemote:
    def test_validate_github_https_url_returns_true(self):
        # Arrange
        url = "https://github.com/user/repo.git"
        # Act
        result = _validate_git_url(url)
        # Assert
        assert result is True

    def test_validate_github_ssh_url_returns_true(self):
        # Arrange
        url = "git@github.com:user/repo.git"
        # Act
        result = _validate_git_url(url)
        # Assert
        assert result is True

    def test_validate_gitlab_https_url_returns_true(self):
        # Arrange
        url = "https://gitlab.com/user/repo.git"
        # Act
        result = _validate_git_url(url)
        # Assert
        assert result is True

    def test_validate_bitbucket_https_url_returns_true(self):
        # Arrange
        url = "https://bitbucket.org/user/repo.git"
        # Act
        result = _validate_git_url(url)
        # Assert
        assert result is True

    def test_validate_unknown_host_returns_false(self):
        # Arrange
        url = "https://invalid.com/user/repo.git"
        # Act
        result = _validate_git_url(url)
        # Assert
        assert result is False

    def test_normalize_https_url_strips_git_suffix(self):
        # Arrange
        url = "https://github.com/user/repo.git"
        expected = "https://github.com/user/repo"
        # Act
        result = _normalize_git_url(url)
        # Assert
        assert result == expected

    def test_normalize_ssh_url_converts_to_https_form(self):
        # Arrange
        url = "git@github.com:user/repo.git"
        expected = "https://github.com/user/repo"
        # Act
        result = _normalize_git_url(url)
        # Assert
        assert result == expected

    def test_normalize_url_strips_trailing_slash(self):
        # Arrange
        url = "https://github.com/user/repo/"
        expected = "https://github.com/user/repo"
        # Act
        result = _normalize_git_url(url)
        # Assert
        assert result == expected

    def test_get_remote_url_returns_none_for_non_git_dir(self, tmp_path):
        # Arrange
        non_repo = tmp_path / "not_repo"
        non_repo.mkdir()
        # Act
        result = get_remote_url(non_repo, verbose=False)
        # Assert
        assert result is None

    def test_is_cloned_from_returns_false_for_non_git_dir(self, tmp_path):
        # Arrange
        non_repo = tmp_path / "not_repo"
        non_repo.mkdir()
        # Act
        result = is_cloned_from(non_repo, "https://github.com/user/repo.git")
        # Assert
        assert result is False


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
