import json
from pathlib import Path
import shutil

import networkx as nx
import pytest

from conftest import CONTENT, FakeProvider, make_pdf
from utility_scripts.contracts import KBError, digest, load_config
from utility_scripts.ingest import run
from utility_scripts.storage import snapshot, load_collection


def submit(repo, name='protein.md', content=CONTENT):
    path = repo / 'markdown' / name
    path.write_text(content)
    return path


def test_mixed_ingestion_links_archives_and_idempotency(repo, provider):
    md = submit(repo)
    make_pdf(repo / 'pdf/protein.pdf')
    inputs = {digest(p.read_bytes()): p.read_bytes() for p in [md, repo / 'pdf/protein.pdf']}
    report = run(repo, provider_factory=provider)
    assert report['new_documents'] == 2 and report['api_requests'] == 3
    records, relationships = load_collection(repo)
    assert len(records) == 2 and len(relationships['edges']) == 1
    assert run(repo, 'validate')['valid']
    for doc_id, record in records.items():
        assert (repo / record['source_path']).read_bytes() == inputs[doc_id]
        assert len(record['summary'].split()) == 100
        assert len(record['keywords']) == 10
    assert (repo / 'markdown/README.md').read_text() == 'Keep these instructions.\n'
    assert (repo / 'pdf/README.md').exists()
    readme = (repo / 'README.md').read_text()
    assert readme.endswith('Hand-maintained instructions.\n')
    assert readme.index('![ThayerLab') < readme.index('### Documents') < readme.index('### Connections')
    for record in records.values():
        assert f"]({record['content_path']})" in readme
    before = snapshot(repo)
    assert run(repo, provider_factory=provider)['changed_paths'] == []
    assert len(provider.instances) == 1
    assert snapshot(repo) == before
    assert run(repo, 'rebuild')['changed_paths'] == []


def test_duplicates_within_batch_and_after_commit(repo, provider):
    submit(repo, 'a.md')
    submit(repo, 'b.md')
    result = run(repo, provider_factory=provider)
    assert result['duplicates'] == 1 and result['api_requests'] == 1
    before = snapshot(repo)
    submit(repo, 'renamed.md')
    result = run(repo, provider_factory=provider)
    assert result['changed_paths'] == ['markdown/renamed.md']
    assert len(provider.instances) == 1
    assert snapshot(repo) == before


def test_all_new_pairs_then_only_pairs_involving_new_document(repo, provider):
    for i, name in enumerate(['one', 'two', 'unrelated']):
        submit(repo, f'{name}.md', CONTENT + f'\nVersion {i}')
    run(repo, provider_factory=provider)
    assert len(provider.instances[0].pairs) == 3
    graph = nx.read_graphml(repo / 'KG/KG.graphml')
    assert graph.number_of_nodes() == 3 and graph.number_of_edges() == 1
    assert sorted(dict(graph.degree()).values()) == [0, 1, 1]
    submit(repo, 'four.md', CONTENT + '\nFourth')
    run(repo, provider_factory=provider)
    assert len(provider.instances[1].pairs) == 3
    assert provider.instances[1].requests == 4


def test_dry_run_does_not_mutate_or_require_key(repo):
    submit(repo)
    before = snapshot(repo)
    def no_provider(*args):
        pytest.fail('Dry-run created a provider')
    result = run(repo, dry_run=True, provider_factory=no_provider)
    assert result['maximum_api_requests'] == 3
    assert snapshot(repo) == before


@pytest.mark.parametrize('failure', ['summary', 'relationship', 'render', 'graph', 'validation'])
def test_failed_batch_preserves_every_input_and_existing_output(repo, provider, monkeypatch, failure):
    submit(repo)
    run(repo, provider_factory=provider)
    submit(repo, 'new.md', CONTENT + '\nNew data')
    before = snapshot(repo)
    def fail(*args, **kwargs):
        raise KBError('Deliberate test failure')
    if failure == 'summary':
        monkeypatch.setattr(FakeProvider, 'summarize', fail)
    elif failure == 'relationship':
        monkeypatch.setattr(FakeProvider, 'relate', fail)
    else:
        monkeypatch.setattr('utility_scripts.ingest.' + {'render': 'render_image', 'graph': 'write_graph', 'validation': 'validate_outputs'}[failure], fail)
    with pytest.raises(KBError):
        run(repo, provider_factory=provider)
    assert snapshot(repo) == before


def test_io_failure_rolls_back(repo, provider, monkeypatch):
    submit(repo)
    before = snapshot(repo)
    import utility_scripts.storage as storage
    original = storage.atomic_write
    count = 0
    def fail_once(path, data):
        nonlocal count
        count += 1
        if count == 3:
            raise OSError('disk error')
        original(path, data)
    monkeypatch.setattr(storage, 'atomic_write', fail_once)
    with pytest.raises(OSError):
        run(repo, provider_factory=provider)
    assert snapshot(repo) == before
    assert not (repo / 'sources').exists()


def test_concurrent_edit_not_overwritten(repo, provider, monkeypatch):
    submit(repo)
    original = FakeProvider.summarize
    def change(self, *args):
        (repo / 'README.md').write_text((repo / 'README.md').read_text() + '\nUser edit\n')
        return original(self, *args)
    monkeypatch.setattr(FakeProvider, 'summarize', change)
    with pytest.raises(KBError, match='changed during'):
        run(repo, provider_factory=provider)
    assert (repo / 'markdown/protein.md').exists()
    assert (repo / 'README.md').read_text().endswith('User edit\n')
    assert not (repo / 'sources').exists()


@pytest.mark.parametrize('kind', ['bad_pdf', 'encrypted', 'scan', 'nested', 'unsupported', 'empty', 'symlink', 'local_link', 'invalid_utf8'])
def test_bad_inputs_fail_before_any_api_call(repo, kind):
    if kind == 'bad_pdf':
        (repo / 'pdf/bad.pdf').write_bytes(b'not a PDF')
    elif kind in ('encrypted', 'scan'):
        make_pdf(repo / 'pdf/bad.pdf', encrypted=kind == 'encrypted', blank=kind == 'scan')
    elif kind == 'nested':
        (repo / 'markdown/subdir').mkdir()
    elif kind == 'unsupported':
        (repo / 'markdown/bad.txt').write_text(CONTENT)
    elif kind == 'symlink':
        (repo / 'markdown/link.md').symlink_to(repo / 'README.md')
    elif kind == 'empty':
        submit(repo, content='')
    elif kind == 'invalid_utf8':
        (repo / 'markdown/bad.md').write_bytes(b'\xff')
    else:
        submit(repo, content=CONTENT + '\n![image](../figure.png)')
    def no_provider(*args):
        pytest.fail('Invalid input reached provider')
    with pytest.raises(KBError):
        run(repo, provider_factory=no_provider)


@pytest.mark.parametrize('setting,value', [('max_file_bytes', 10), ('max_extracted_input_tokens', 10),
                                          ('max_new_documents', 1), ('max_api_requests', 2)])
def test_limits_preflight(repo, setting, value):
    submit(repo)
    submit(repo, 'second.md', CONTENT + '\nSecond')
    cfg = load_config(repo)
    cfg[setting] = value
    (repo / 'config/ingestion.json').write_text(json.dumps(cfg))
    with pytest.raises(KBError):
        run(repo, dry_run=True)


@pytest.mark.parametrize('corruption', ['content', 'source', 'metadata', 'relationships', 'orphan'])
def test_corrupt_persistent_records_not_treated_as_duplicates(repo, provider, corruption):
    submit(repo)
    run(repo, provider_factory=provider)
    records, _ = load_collection(repo)
    record = next(iter(records.values()))
    if corruption == 'content':
        (repo / record['content_path']).write_text('changed')
    elif corruption == 'source':
        (repo / record['source_path']).unlink()
    elif corruption == 'metadata':
        (repo / Path(record['content_path']).parent / 'metadata.json').write_text('{}')
    elif corruption == 'relationships':
        (repo / 'KG/relationships.json').unlink()
    else:
        shutil.rmtree(repo / Path(record['content_path']).parent)
    submit(repo, 'duplicate.md')
    with pytest.raises(KBError):
        run(repo, provider_factory=provider)
    assert (repo / 'markdown/duplicate.md').exists()
    assert len(provider.instances) == 1


def test_empty_rebuild_and_broken_markers(repo):
    assert run(repo)['changed_paths'] == []
    run(repo, 'rebuild')
    assert run(repo, 'validate')['documents'] == 0
    assert run(repo, 'rebuild')['changed_paths'] == []
    (repo / 'README.md').write_text('No markers')
    with pytest.raises(KBError, match='markers'):
        run(repo, 'rebuild')


def test_same_filename_different_bytes_and_markdown_escaping(repo, provider):
    name = 'a|[x]<b>.md'
    submit(repo, name)
    run(repo, provider_factory=provider)
    submit(repo, name, CONTENT + '\nAnother edition')
    run(repo, provider_factory=provider)
    assert len(load_collection(repo)[0]) == 2
    text = (repo / 'README.md').read_text()
    assert 'a\\|\\[x\\]&lt;b&gt;' in text
    assert '<b>' not in text


def test_readme_preserves_handwritten_crlf_bytes(repo):
    before = b"# Lab\r\n\r\n<!-- KG:START -->\r\n"
    after = b"<!-- KG:END -->\r\n\r\nKeep this byte-for-byte.\r\n"
    (repo / 'README.md').write_bytes(before + b"Pending\r\n" + after)
    run(repo, 'rebuild')
    result = (repo / 'README.md').read_bytes()
    assert result.startswith(before) and result.endswith(after)
    assert run(repo, 'rebuild')['changed_paths'] == []
