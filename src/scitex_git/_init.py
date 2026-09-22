#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-code/src/scitex/git/init.py

"""
Git initialization utilities.

Provides functions to initialize, find, and manage git repositories
with different strategies (child, parent, origin).
"""

from pathlib import Path
from typing import Optional

import scitex_logging as slogging
from git import InvalidGitRepositoryError, Repo

log = slogging.getLogger(__name__)


def find_parent_git(project_dir: Path) -> Optional[Path]:
    """
    Find parent git repository by walking up directory tree.

    Args:
        project_dir: Starting directory to search from

    Returns:
        Path to parent git root, or None if not found
    """
    try:
        repo_parent = Repo(project_dir.parent, search_parent_directories=True)
        return Path(repo_parent.git_dir).parent
    except InvalidGitRepositoryError:
        return None


def remove_child_git(project_dir: Path) -> bool:
    """
    Remove project's local .git folder.

    When parent git is found, the project's own .git/ is redundant and
    should be removed to avoid nested git repository issues.

    Args:
        project_dir: Project directory containing .git to remove

    Returns:
        True if removed successfully or doesn't exist, False on error
    """
    child_git = project_dir / ".git"

    if not child_git.exists():
        log.info(f"No child .git found at {project_dir}")
        return True

    try:
        import shutil

        log.info("Removing child .git to use parent repository...")
        shutil.rmtree(child_git)
        log.info(f"Removed child .git from {project_dir}")
        return True
    except PermissionError as e:
        log.error(f"Permission denied removing .git from {project_dir}: {e}")
        return False
    except Exception as e:
        log.error(f"Failed to remove child .git from {project_dir}: {e}")
        return False


def create_child_git(project_dir: Path) -> Optional[Path]:
    """
    Create isolated git repository in project directory.

    Uses GitPython to initialize and make initial commit.

    Args:
        project_dir: Directory to initialize as git repo

    Returns:
        Path to git root (project_dir), or None on failure
    """
    try:
        try:
            repo = Repo(project_dir)
            log.info(f"Project is already a git repository at {project_dir}")
            # Optional structure validation: only runs if scitex-writer is
            # installed AND the project happens to follow the writer-tree
            # convention. If either is false, fall through quietly — the
            # repo itself is still valid.
            try:
                from scitex_writer._utils._verify_tree_structure import (
                    verify_tree_structure,
                )

                verify_tree_structure(project_dir)
            except Exception as _verify_err:
                # ImportError: scitex-writer not installed.
                # ProjectValidationError / ValueError / OSError: project
                # doesn't follow the writer tree (config/, src/, ... etc).
                # All are non-fatal here — the repo itself is still valid;
                # tree validation is a writer-side concern.
                log.debug(f"Optional verify_tree_structure skipped: {_verify_err}")
            return project_dir
        except InvalidGitRepositoryError:
            log.info(f"Initializing new git repository at {project_dir}")
            repo = Repo.init(project_dir)

        repo.index.add(["."])
        repo.index.commit("Initial commit from scitex template")

        log.info(f"Git repository initialized at {project_dir}")
        return project_dir
    except PermissionError as e:
        log.error(f"Permission denied creating git repository at {project_dir}: {e}")
        return None
    except OSError as e:
        log.error(f"IO error creating git repository at {project_dir}: {e}")
        return None
    except Exception as e:
        log.error(f"Failed to create child git repository at {project_dir}: {e}")
        return None


def init_git_repo(
    project_dir: Path, git_strategy: Optional[str] = "child"
) -> Optional[Path]:
    """
    Initialize or detect git repository based on git_strategy.

    Args:
        project_dir: Project directory
        git_strategy: Git initialization strategy
            - None: Git disabled, returns None
            - 'child': Creates isolated git repo in project directory
            - 'parent': Tries to use parent git, degrades to 'child' if not found
            - 'origin': Preserves template's original git history (handled by clone)

    Returns:
        Path to git repository root, or None if disabled
    """
    if git_strategy is None:
        log.info("Git initialization disabled (git_strategy=None)")
        return None

    if git_strategy == "parent":
        log.info("Using 'parent' git strategy, searching for parent repository...")
        parent_git = find_parent_git(project_dir)

        if parent_git:
            log.info(f"Found parent git repository: {parent_git}")
            remove_child_git(project_dir)
            return parent_git

        log.warning(
            f"No parent git repository found for {project_dir}. "
            f"Degrading to 'child' strategy (isolated git repo)."
        )
        return create_child_git(project_dir)

    if git_strategy == "child":
        log.info("Using 'child' git strategy, creating isolated repository...")
        return create_child_git(project_dir)

    if git_strategy == "origin":
        log.info("Using 'origin' git strategy, template git history preserved...")
        try:
            Repo(project_dir)
            log.info(f"Found git repository at {project_dir}")
            return project_dir
        except InvalidGitRepositoryError:
            log.warning(
                f"No git repository found at {project_dir}. "
                f"Degrading to 'child' strategy."
            )
            return create_child_git(project_dir)

    raise ValueError(
        f"Unknown git_strategy: {git_strategy}. "
        f"Expected 'parent', 'child', 'origin', or None"
    )


__all__ = [
    "find_parent_git",
    "remove_child_git",
    "create_child_git",
    "init_git_repo",
]

# EOF
