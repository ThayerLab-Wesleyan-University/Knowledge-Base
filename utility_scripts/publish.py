"""Publish one complete commit through an isolated Git index; never force-push."""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from utility_scripts.contracts import KBError


def git(root, *args, env=None, input=None):
    result = subprocess.run(["git", *args], cwd=root, env=env, input=input,
                            text=True, capture_output=True)
    if result.returncode:
        # Git errors can include credential-bearing remote URLs. Keep logs generic.
        raise KBError(f"Git {args[0]} failed; inspect repository permissions and branch state.")
    return result.stdout.strip()


def publication_base(root):
    if git(root, "status", "--porcelain"):
        raise KBError("Publication requires a clean checkout before ingestion.")
    if git(root, "symbolic-ref", "--short", "HEAD") != "main":
        raise KBError("Publication is allowed only from a main checkout.")
    base = git(root, "rev-parse", "HEAD")
    check_remote(root, base)
    return base


def check_remote(root, base):
    remote = git(root, "ls-remote", "--exit-code", "origin", "refs/heads/main")
    if remote.split()[0] != base or git(root, "rev-parse", "HEAD") != base:
        raise KBError("main advanced during ingestion; rerun from the latest main. No force-push attempted.")


def publish(root: Path, base: str, paths: list[str], *, message="Update knowledge base from intake"):
    if not paths:
        return None
    check_remote(root, base)
    for path in paths:
        allowed = (path in {"README.md", "KG/KG.graphml", "KG/KG.png", "KG/relationships.json"}
                   or re.fullmatch(r"KG/rendered/[0-9a-f]{64}\.png", path)
                   or path.startswith(("KG/node_contents/", "sources/", "pdf/", "markdown/")))
        if not allowed or path in ("pdf/README.md", "markdown/README.md"):
            raise KBError("Refusing to publish a path outside the ingestion output set.")
    # Isolate staging from any user's index; commit-tree creates an object without
    # moving local refs. This command is intended for disposable CI checkouts.
    with tempfile.TemporaryDirectory(prefix="kb-index-") as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / "index"),
                   GIT_AUTHOR_NAME="knowledge-base[bot]", GIT_COMMITTER_NAME="knowledge-base[bot]",
                   GIT_AUTHOR_EMAIL="knowledge-base@users.noreply.github.com",
                   GIT_COMMITTER_EMAIL="knowledge-base@users.noreply.github.com",
                   GIT_LITERAL_PATHSPECS="1")
        git(root, "read-tree", base, env=env)
        git(root, "add", "--all", "--", *paths, env=env)
        tree = git(root, "write-tree", env=env)
        commit = git(root, "commit-tree", tree, "-p", base, env=env,
                     input=message + "\n")
        check_remote(root, base)
        git(root, "push", "origin", f"{commit}:refs/heads/main", env=env)
        return commit
