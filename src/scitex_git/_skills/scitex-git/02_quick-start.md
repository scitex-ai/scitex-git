---
description: |
  [TOPIC] Quick start
  [DETAILS] Clone, init, commit, branch, retry — the smallest useful examples for the most-used helpers.
tags: [scitex-git-quick-start]
---

# Quick Start

## Clone

```python
from scitex_git import clone_repo

clone_repo("https://github.com/u/r.git", dest="/tmp/r")
```

## Init + first commit

```python
from scitex_git import git_init, git_add_all, git_commit

git_init("/tmp/new-repo")
git_add_all("/tmp/new-repo")
git_commit("/tmp/new-repo", message="initial commit")
```

## Branches

```python
from scitex_git import git_checkout_new_branch, git_branch_rename, setup_branches

git_checkout_new_branch("/tmp/r", "feature/x")
git_branch_rename("/tmp/r", old="feature/old-name", new="feature/new-name")
setup_branches("/tmp/r", main="main", develop="develop")
```

## Discover parent + remote

```python
from scitex_git import find_parent_git, get_remote_url, is_cloned_from

root = find_parent_git("/tmp/r/sub/dir")     # walks up to .git/
url = get_remote_url("/tmp/r")
is_cloned_from("/tmp/r", "https://github.com/u/r.git")
```

## Retry transient failures

```python
from scitex_git import git_retry

git_retry(["push"], cwd="/tmp/r", attempts=3)
```

## Next

- [03_python-api.md](03_python-api.md) — full public surface
