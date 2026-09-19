import pytest

from conftest import CONTENT
from test_publication import git_setup
from utility_scripts.contracts import KBError, digest
from utility_scripts.delete_node import run as delete
from utility_scripts.ingest import run
from utility_scripts.publish import git
from utility_scripts.storage import load_collection, snapshot


def seed(repo, provider, count=1):
    ids = []
    for i in range(count):
        content = CONTENT + f'\nNote {i}\n'
        (repo / f'markdown/paper{i}.md').write_text(content)
        ids.append(digest(content.encode()))
    run(repo, provider_factory=provider)
    return ids


def test_remove_node_and_incident_edges_preserves_other_records(repo, provider):
    ids = seed(repo, provider, 3)
    before = snapshot(repo)
    (repo / 'markdown/pending.md').write_text(CONTENT)
    calls = sum(p.requests for p in provider.instances)
    result = delete(repo, ids[0])
    assert result['removed_connections'] == 2
    records, relationships = load_collection(repo)
    assert set(records) == set(ids[1:])
    assert len(relationships['edges']) == 1
    for rel, data in before.items():
        if any(doc_id in rel for doc_id in ids[1:]):
            assert (repo / rel).read_bytes() == data
    assert (repo / 'markdown/pending.md').read_text() == CONTENT
    assert not (repo / f'KG/node_contents/{ids[0]}').exists()
    assert not (repo / f'sources/{ids[0]}').exists()
    assert sum(p.requests for p in provider.instances) == calls
    run(repo, 'validate')


def test_last_node_and_dry_run(repo, provider):
    doc_id, = seed(repo, provider)
    before = snapshot(repo)
    delete(repo, doc_id, dry_run=True)
    assert snapshot(repo) == before
    delete(repo, doc_id)
    assert load_collection(repo) == ({}, {'schema_version': 1, 'edges': []})
    run(repo, 'validate')


@pytest.mark.parametrize('doc_id', ['D1', '../README.md', 'a' * 64])
def test_invalid_or_unknown_id_changes_nothing(repo, provider, doc_id):
    seed(repo, provider)
    before = snapshot(repo)
    with pytest.raises(KBError):
        delete(repo, doc_id)
    assert snapshot(repo) == before


def test_render_failure_changes_nothing(repo, provider, monkeypatch):
    doc_id, = seed(repo, provider)
    before = snapshot(repo)
    def fail(*args):
        raise OSError('render failed')
    monkeypatch.setattr('utility_scripts.delete_node.build_outputs', fail)
    with pytest.raises(OSError):
        delete(repo, doc_id)
    assert snapshot(repo) == before


def test_directory_removal_failure_rolls_back(repo, provider, monkeypatch):
    from pathlib import Path
    doc_id, = seed(repo, provider)
    before = snapshot(repo)
    original = Path.rmdir
    def fail(path):
        if path == repo / f'sources/{doc_id}':
            raise OSError('injected directory failure')
        return original(path)
    monkeypatch.setattr(Path, 'rmdir', fail)
    with pytest.raises(OSError, match='injected'):
        delete(repo, doc_id)
    assert snapshot(repo) == before
    run(repo, 'validate')


def test_publish_deletion_in_one_commit(repo, provider, tmp_path_factory):
    doc_id, = seed(repo, provider)
    remote = git_setup(repo, tmp_path_factory.mktemp('delete-remote'))
    base = git(repo, 'rev-parse', 'HEAD')
    result = delete(repo, doc_id, publish_changes=True)
    commit = result['published_commit']
    assert git(remote, 'rev-parse', 'refs/heads/main') == commit
    assert git(remote, 'rev-parse', f'{commit}^') == base
    files = git(remote, 'ls-tree', '-r', '--name-only', commit).splitlines()
    assert not any(doc_id in p for p in files)
    assert 'KG/KG.png' in files and 'README.md' in files
    assert len([p for p in files if p.startswith('KG/rendered/')]) == 1
    assert set(p for p in files if p.startswith('KG/rendered/')) != set(
        p for p in git(remote, 'ls-tree', '-r', '--name-only', base).splitlines()
        if p.startswith('KG/rendered/'))
    assert 'markdown/README.md' in files and 'pdf/README.md' in files
    assert git(repo, 'diff', '--cached', '--name-only') == ''
    run(repo, 'validate')
