from pathlib import Path
import subprocess

import pytest

from conftest import CONTENT
from utility_scripts.contracts import KBError
from utility_scripts.ingest import run
from utility_scripts.publish import git, publish, publication_base


def git_setup(repo, tmp_path):
    remote = tmp_path / 'remote.git'
    git(tmp_path, 'init', '--bare', str(remote))
    git(repo, 'init', '-b', 'main')
    git(repo, 'config', 'user.name', 'Test')
    git(repo, 'config', 'user.email', 'test@example.invalid')
    git(repo, 'remote', 'add', 'origin', str(remote))
    git(repo, 'add', '.')
    git(repo, 'commit', '-m', 'Fixture')
    git(repo, 'push', '-u', 'origin', 'main')
    return remote


def test_complete_single_commit_publication(repo, tmp_path_factory, provider):
    (repo / 'markdown/paper.md').write_text(CONTENT)
    remote = git_setup(repo, tmp_path_factory.mktemp('git'))
    base = git(repo, 'rev-parse', 'HEAD')
    result = run(repo, provider_factory=provider, publish_changes=True)
    commit = result['published_commit']
    assert git(remote, 'rev-parse', 'refs/heads/main') == commit
    assert git(remote, 'rev-parse', f'{commit}^') == base
    files = git(remote, 'ls-tree', '-r', '--name-only', commit).splitlines()
    assert 'markdown/paper.md' not in files
    assert 'markdown/README.md' in files and 'pdf/README.md' in files
    assert 'KG/KG.png' in files and 'KG/KG.graphml' in files
    assert len([p for p in files if p.startswith('sources/')]) == 1
    assert 'config/ingestion.json' not in git(remote, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit).splitlines()
    assert git(repo, 'diff', '--cached', '--name-only') == ''  # isolated index


def test_remote_advance_refused_without_overwrite(repo, tmp_path_factory, provider):
    (repo / 'markdown/paper.md').write_text(CONTENT)
    directory = tmp_path_factory.mktemp('git')
    remote = git_setup(repo, directory)
    base = publication_base(repo)
    report = run(repo, provider_factory=provider)
    other = directory / 'other'
    git(directory, 'clone', '-b', 'main', str(remote), str(other))
    git(other, 'config', 'user.name', 'Other')
    git(other, 'config', 'user.email', 'other@example.invalid')
    (other / 'README.md').write_text('Concurrent lab edit')
    git(other, 'add', 'README.md')
    git(other, 'commit', '-m', 'Concurrent update')
    git(other, 'push', 'origin', 'main')
    remote_head = git(remote, 'rev-parse', 'refs/heads/main')
    with pytest.raises(KBError, match='advanced'):
        publish(repo, base, report['changed_paths'])
    assert git(remote, 'rev-parse', 'refs/heads/main') == remote_head
    assert 'markdown/paper.md' in git(remote, 'ls-tree', '-r', '--name-only', remote_head)


def test_rejected_push_preserves_remote_intake(repo, tmp_path_factory, provider):
    (repo / 'markdown/paper.md').write_text(CONTENT)
    remote = git_setup(repo, tmp_path_factory.mktemp('git'))
    base = publication_base(repo)
    hook = remote / 'hooks/pre-receive'
    hook.write_text('#!/bin/sh\nexit 1\n')
    hook.chmod(0o755)
    with pytest.raises(KBError, match='push failed'):
        run(repo, provider_factory=provider, publish_changes=True)
    assert git(remote, 'rev-parse', 'refs/heads/main') == base
    assert 'markdown/paper.md' in git(remote, 'ls-tree', '-r', '--name-only', base)
    assert git(repo, 'diff', '--cached', '--name-only') == ''


def test_dirty_checkout_refused(repo, tmp_path_factory):
    git_setup(repo, tmp_path_factory.mktemp('git'))
    (repo / 'README.md').write_text('local change')
    with pytest.raises(KBError, match='clean checkout'):
        publication_base(repo)
