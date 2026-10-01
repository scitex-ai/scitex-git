#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-git/src/scitex_git/_gh_secrets.py

"""GitHub Actions secrets / variables — thin wrappers around ``gh`` CLI.

The GitHub Actions REST API (and ``gh secret``) is **write-only** for
secret values: you can list names + ``updated_at``, but never read a
value back. This module bundles the everyday read/write primitives any
"rotate the CI key" workflow needs, plus a SHA256 sidecar pattern to
detect drift between local and remote without exposing the secret:

  * :func:`set_secret` / :func:`list_secrets` /
    :func:`get_secret_metadata` — direct ``gh secret`` wrappers.
  * :func:`set_variable` / :func:`get_variable` — ``gh variable``
    wrappers (variables are world-readable; suitable for non-sensitive
    fingerprints, never for token material).
  * :func:`set_secret_with_sha_sidecar` — pushes the secret AND a
    SHA256 fingerprint to a same-name ``…_SHA256`` repo variable so a
    later ``get_variable`` call lets the operator tell whether the
    GitHub-side secret matches the local one. Hash is irreversible.
  * :func:`format_age` — render an ISO-8601 ``updated_at`` as a
    human-readable single-unit age (``15min`` / ``2.4d``) for CLI
    reports.
  * :func:`sha256_hex` — same hashing function the sidecar uses, so
    callers can compute a local fingerprint to compare against
    :func:`get_variable`.

The ``gh`` CLI must be authenticated. Each helper raises
:class:`GhSecretError` on subprocess failure with the underlying stderr
attached, so callers can surface a clean message rather than a stack
trace.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone

import scitex_logging as slogging

log = slogging.getLogger(__name__)

__all__ = [
    "GhSecretError",
    "set_secret",
    "list_secrets",
    "get_secret_metadata",
    "set_variable",
    "get_variable",
    "set_secret_with_sha_sidecar",
    "format_age",
    "sha256_hex",
]


class GhSecretError(RuntimeError):
    """Raised when a ``gh`` subprocess returns non-zero."""


def _run(argv: list[str], *, stdin: str | None = None) -> str:
    """Run ``argv`` and return stdout. Raise :class:`GhSecretError` on failure."""
    proc = subprocess.run(
        argv,
        input=stdin,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        raise GhSecretError(f"{' '.join(argv[:3])}…: {msg}")
    return proc.stdout


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------


def set_secret(repo: str, name: str, value: str) -> None:
    """Push ``value`` into the Actions secret ``name`` for ``repo``.

    ``repo`` follows the ``owner/repo`` form. Idempotent — creates if
    missing, updates otherwise.
    """
    # ``gh secret set`` reads from stdin when ``--body`` is omitted.
    # Earlier we passed ``--body -`` thinking ``-`` meant stdin; gh
    # actually stored the literal one-byte value ``-``, silently
    # truncating the secret. Bug surfaced as in-CI ``$SECRET`` length
    # 1 with sha256 mismatching the local file's hash.
    _run(["gh", "secret", "set", name, "-R", repo], stdin=value)


def list_secrets(repo: str) -> dict[str, str]:
    """Return ``{secret_name: updated_at_iso}`` for the repo.

    Pagination is honoured (``--paginate``) so this scales beyond
    GitHub's 100-secret default page size.
    """
    raw = _run(["gh", "api", f"repos/{repo}/actions/secrets", "--paginate"])
    payload = json.loads(raw)
    return {s["name"]: s["updated_at"] for s in payload.get("secrets", [])}


def get_secret_metadata(repo: str, name: str) -> dict | None:
    """Return the secret's metadata dict (name / created_at / updated_at), or None.

    GitHub never exposes the value itself — that's the whole point of
    Actions secrets. Use :func:`get_variable` against a SHA sidecar
    (see :func:`set_secret_with_sha_sidecar`) if you need to detect
    value drift.
    """
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/secrets/{name}"],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Variables (world-readable)
# ---------------------------------------------------------------------------


def set_variable(repo: str, name: str, value: str) -> None:
    """Create-or-update an Actions variable. Idempotent.

    Variables are visible to anyone with repo read access. Use this
    for non-sensitive metadata (e.g. SHA256 fingerprints of secrets,
    feature flags). NEVER store token material here.
    """
    _run(["gh", "variable", "set", name, "-R", repo, "--body", value])


def get_variable(repo: str, name: str) -> str | None:
    """Return the variable's value, or None if absent."""
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/variables/{name}"],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout).get("value")
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# SHA256 sidecar — secret-drift detection without exposing the value
# ---------------------------------------------------------------------------


def sha256_hex(value: str) -> str:
    """Return the SHA256 hex digest of ``value`` (UTF-8)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def set_secret_with_sha_sidecar(
    repo: str, name: str, value: str, *, sidecar_suffix: str = "_SHA256"
) -> str:
    """Push the secret AND its SHA256 fingerprint as a public variable.

    Returns the SHA256 hex digest so the caller can show it in CLI
    output. The sidecar variable is named ``{name}{sidecar_suffix}`` and
    holds the irreversible hash; later
    ``get_variable(repo, f"{name}{sidecar_suffix}")`` lets you tell
    whether the GitHub-side secret matches a local value (compare with
    ``sha256_hex(local_value)``).

    The hash itself is not sensitive — it cannot be reversed to the
    original token without a brute-force search of the OAuth/api-key
    namespace, which is computationally infeasible. It IS visible to
    repo readers, so don't use the sidecar for tokens whose mere
    existence is sensitive (the hash leaks "this token was rotated at
    {time} to a value with hash {h}" but never the value).
    """
    digest = sha256_hex(value)
    set_secret(repo, name, value)
    set_variable(repo, f"{name}{sidecar_suffix}", digest)
    return digest


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def format_age(updated_iso: str | None) -> str:
    """Render an ISO-8601 timestamp as a single-unit human age.

    Picks the largest unit that gives a readable number: seconds for
    very fresh rotations, then minutes, hours, days. Mirrors the
    ``git relative_date`` style — a single value + unit, no compound
    "1d 4h" form. Returns ``"?"`` for ``None`` input.

    >>> format_age(None)
    '?'
    """
    if not updated_iso:
        return "?"
    dt = datetime.fromisoformat(updated_iso.replace("Z", "+00:00"))
    seconds = (datetime.now(timezone.utc) - dt).total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds / 60)}min"
    if seconds < 86400:
        return f"{seconds / 3600:.1f}h"
    return f"{seconds / 86400:.1f}d"


# EOF
