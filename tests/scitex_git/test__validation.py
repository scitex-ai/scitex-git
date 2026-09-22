#!/usr/bin/env python3

"""Tests for git validation utilities."""


import pytest

pytest.importorskip("git")

from scitex_git._validation import (
    validate_branch_name,
    validate_commit_message,
    validate_path,
)


class TestValidateBranchName:
    """Tests for validate_branch_name function."""

    def test_simple_name_returns_valid_true(self):
        # Arrange
        name = "main"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is True

    def test_simple_name_returns_empty_error(self):
        # Arrange
        name = "main"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert error == ""

    def test_feature_branch_returns_valid_true(self):
        # Arrange
        name = "feature/new-feature"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is True

    def test_name_with_numbers_returns_valid_true(self):
        # Arrange
        name = "feature/issue-123"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is True

    def test_name_with_dots_returns_valid_true(self):
        # Arrange
        name = "release/v1.0.0"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is True

    def test_empty_string_returns_valid_false(self):
        # Arrange
        name = ""
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_empty_string_error_mentions_empty(self):
        # Arrange
        name = ""
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "empty" in error.lower()

    def test_whitespace_only_returns_valid_false(self):
        # Arrange
        name = "   "
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_whitespace_only_error_mentions_empty(self):
        # Arrange
        name = "   "
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "empty" in error.lower()

    def test_name_starting_with_dash_returns_valid_false(self):
        # Arrange
        name = "-feature"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_starting_with_dash_error_mentions_dash(self):
        # Arrange
        name = "-feature"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "'-'" in error

    def test_name_ending_with_lock_returns_valid_false(self):
        # Arrange
        name = "branch.lock"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_ending_with_lock_error_mentions_lock(self):
        # Arrange
        name = "branch.lock"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert ".lock" in error

    def test_name_with_double_dots_returns_valid_false(self):
        # Arrange
        name = "feature..branch"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_double_dots_error_mentions_double_dot(self):
        # Arrange
        name = "feature..branch"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert ".." in error

    def test_name_with_tilde_returns_valid_false(self):
        # Arrange
        name = "feature~1"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_tilde_error_mentions_tilde(self):
        # Arrange
        name = "feature~1"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "~" in error

    def test_name_with_caret_returns_valid_false(self):
        # Arrange
        name = "branch^2"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_caret_error_mentions_caret(self):
        # Arrange
        name = "branch^2"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "^" in error

    def test_name_with_colon_returns_valid_false(self):
        # Arrange
        name = "branch:name"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_colon_error_mentions_colon(self):
        # Arrange
        name = "branch:name"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert ":" in error

    def test_name_with_question_mark_returns_valid_false(self):
        # Arrange
        name = "branch?name"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_question_mark_error_mentions_qmark(self):
        # Arrange
        name = "branch?name"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "?" in error

    def test_name_with_asterisk_returns_valid_false(self):
        # Arrange
        name = "branch*name"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_asterisk_error_mentions_asterisk(self):
        # Arrange
        name = "branch*name"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "*" in error

    def test_name_with_bracket_returns_valid_false(self):
        # Arrange
        name = "branch[1]"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_bracket_error_mentions_bracket(self):
        # Arrange
        name = "branch[1]"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "[" in error

    def test_name_with_backslash_returns_valid_false(self):
        # Arrange
        name = "branch\\name"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_backslash_error_mentions_backslash(self):
        # Arrange
        name = "branch\\name"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "\\" in error

    def test_name_with_space_returns_valid_false(self):
        # Arrange
        name = "branch name"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_space_error_mentions_space(self):
        # Arrange
        name = "branch name"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert " " in error

    def test_name_with_tab_returns_valid_false(self):
        # Arrange
        name = "branch\tname"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_ending_with_slash_returns_valid_false(self):
        # Arrange
        name = "feature/"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_ending_with_slash_error_mentions_slash(self):
        # Arrange
        name = "feature/"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "/" in error

    def test_name_starting_with_slash_returns_valid_false(self):
        # Arrange
        name = "/feature"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_starting_with_slash_error_mentions_slash(self):
        # Arrange
        name = "/feature"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "/" in error

    def test_name_with_consecutive_slashes_returns_valid_false(self):
        # Arrange
        name = "feature//branch"
        # Act
        valid, _ = validate_branch_name(name)
        # Assert
        assert valid is False

    def test_name_with_consecutive_slashes_error_mentions_double_slash(self):
        # Arrange
        name = "feature//branch"
        # Act
        _, error = validate_branch_name(name)
        # Assert
        assert "consecutive" in error.lower() or "//" in error


class TestValidateCommitMessage:
    """Tests for validate_commit_message function."""

    def test_simple_message_returns_valid_true(self):
        # Arrange
        msg = "Initial commit"
        # Act
        valid, _ = validate_commit_message(msg)
        # Assert
        assert valid is True

    def test_simple_message_returns_empty_error(self):
        # Arrange
        msg = "Initial commit"
        # Act
        _, error = validate_commit_message(msg)
        # Assert
        assert error == ""

    def test_multiline_message_returns_valid_true(self):
        # Arrange
        msg = "Add feature\n\nThis adds a new feature."
        # Act
        valid, _ = validate_commit_message(msg)
        # Assert
        assert valid is True

    def test_special_chars_message_returns_valid_true(self):
        # Arrange
        msg = "Fix bug #123: Handle edge case"
        # Act
        valid, _ = validate_commit_message(msg)
        # Assert
        assert valid is True

    def test_empty_message_returns_valid_false(self):
        # Arrange
        msg = ""
        # Act
        valid, _ = validate_commit_message(msg)
        # Assert
        assert valid is False

    def test_empty_message_error_mentions_empty(self):
        # Arrange
        msg = ""
        # Act
        _, error = validate_commit_message(msg)
        # Assert
        assert "empty" in error.lower()

    def test_whitespace_only_message_returns_valid_false(self):
        # Arrange
        msg = "   "
        # Act
        valid, _ = validate_commit_message(msg)
        # Assert
        assert valid is False

    def test_whitespace_only_message_error_mentions_empty(self):
        # Arrange
        msg = "   "
        # Act
        _, error = validate_commit_message(msg)
        # Assert
        assert "empty" in error.lower()

    def test_newlines_only_message_returns_valid_false(self):
        # Arrange
        msg = "\n\n"
        # Act
        valid, _ = validate_commit_message(msg)
        # Assert
        assert valid is False

    def test_newlines_only_message_error_mentions_empty(self):
        # Arrange
        msg = "\n\n"
        # Act
        _, error = validate_commit_message(msg)
        # Assert
        assert "empty" in error.lower()


class TestValidatePath:
    """Tests for validate_path function."""

    def test_existing_path_with_must_exist_returns_valid_true(self, tmp_path):
        # Arrange
        # Act
        valid, _ = validate_path(tmp_path, must_exist=True)
        # Assert
        assert valid is True

    def test_existing_path_with_must_exist_returns_empty_error(self, tmp_path):
        # Arrange
        # Act
        _, error = validate_path(tmp_path, must_exist=True)
        # Assert
        assert error == ""

    def test_new_path_without_must_exist_returns_valid_true(self, tmp_path):
        # Arrange
        new_path = tmp_path / "new_directory"
        # Act
        valid, _ = validate_path(new_path, must_exist=False)
        # Assert
        assert valid is True

    def test_new_path_without_must_exist_returns_empty_error(self, tmp_path):
        # Arrange
        new_path = tmp_path / "new_directory"
        # Act
        _, error = validate_path(new_path, must_exist=False)
        # Assert
        assert error == ""

    def test_nonexistent_with_must_exist_returns_valid_false(self, tmp_path):
        # Arrange
        nonexistent = tmp_path / "does_not_exist"
        # Act
        valid, _ = validate_path(nonexistent, must_exist=True)
        # Assert
        assert valid is False

    def test_nonexistent_with_must_exist_error_mentions_does_not_exist(self, tmp_path):
        # Arrange
        nonexistent = tmp_path / "does_not_exist"
        # Act
        _, error = validate_path(nonexistent, must_exist=True)
        # Assert
        assert "does not exist" in error.lower()

    def test_existing_file_path_returns_valid_true(self, tmp_path):
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        # Act
        valid, _ = validate_path(test_file, must_exist=True)
        # Assert
        assert valid is True

    def test_existing_nested_path_returns_valid_true(self, tmp_path):
        # Arrange
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        # Act
        valid, _ = validate_path(nested, must_exist=True)
        # Assert
        assert valid is True


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
