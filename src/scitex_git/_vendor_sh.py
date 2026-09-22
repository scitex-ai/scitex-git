"""Minimal vendored shell wrapper — replaces ``scitex.sh.sh`` for scitex-git.

Only the call-shape used by scitex-git is supported:

    sh(cmd_list, verbose=False, return_as="dict") -> dict with
        {"success": bool, "stdout": str, "stderr": str, "returncode": int, "cmd": str}

Refuses string commands (list-only) to match the upstream contract that
prevents shell injection. When scitex-sh is later split out as its own
package, replace this module with a direct dependency.
"""

from __future__ import annotations

import shlex
import subprocess
from typing import Any, Dict, List, Sequence, Union

import scitex_logging as slogging

log = slogging.getLogger(__name__)

CommandInput = Union[Sequence[str], List[str]]


def sh(
    command_str_or_list: CommandInput,
    verbose: bool = False,
    return_as: str = "dict",
    timeout: int | None = None,
    stream_output: bool = False,
) -> Any:
    if isinstance(command_str_or_list, str):
        raise ValueError(
            "sh() requires list/sequence input (e.g. ['git', 'status']) — "
            "string commands are refused to prevent shell injection."
        )

    cmd_list = [str(x) for x in command_str_or_list]
    pretty = " ".join(shlex.quote(p) for p in cmd_list)

    if verbose:
        log.info("$ %s", pretty)

    try:
        proc = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        result: Dict[str, Any] = {
            "success": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "cmd": pretty,
        }
    except FileNotFoundError as e:
        result = {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": 127,
            "cmd": pretty,
        }
    except subprocess.TimeoutExpired as e:
        out = e.stdout if isinstance(e.stdout, str) else ""
        err = e.stderr if isinstance(e.stderr, str) else ""
        result = {
            "success": False,
            "stdout": out,
            "stderr": err + f"\nTIMEOUT after {timeout}s",
            "returncode": 124,
            "cmd": pretty,
        }

    if verbose:
        if result["stdout"]:
            log.info("%s", result["stdout"])
        if result["stderr"]:
            log.warning("%s", result["stderr"])

    if return_as == "dict":
        return result
    return result["stdout"] if result["success"] else result["stderr"]
