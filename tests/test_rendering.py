import networkx as nx

from KG.visualize_KG import render_readme
from utility_scripts.contracts import digest


def test_image_url_tracks_image_bytes_without_changing_handwritten_text():
    text = '# Lab\n<!-- KG:START -->\nold\n<!-- KG:END -->\nKeep instructions.\n'
    records, edges, graph = {}, {'schema_version': 1, 'edges': []}, nx.Graph()
    first = digest(b'first image')
    second = digest(b'changed image')
    rendered = render_readme(text, records, graph, edges, image_sha256=first)
    assert f'(KG/rendered/{first}.png)' in rendered
    assert rendered == render_readme(rendered, records, graph, edges, image_sha256=first)
    updated = render_readme(rendered, records, graph, edges, image_sha256=second)
    assert updated == rendered.replace(first, second)
    assert updated.startswith('# Lab\n<!-- KG:START -->\n')
    assert updated.endswith('<!-- KG:END -->\nKeep instructions.\n')


def test_versioned_images_follow_ingestion_and_deletion(repo, provider):
    from conftest import CONTENT
    from utility_scripts.ingest import run
    from utility_scripts.delete_node import run as delete
    from utility_scripts.storage import load_collection

    (repo / 'markdown/first.md').write_text(CONTENT)
    run(repo, provider_factory=provider)
    first_files = set((repo / 'KG/rendered').glob('*.png'))
    assert len(first_files) == 1
    (repo / 'markdown/second.md').write_text(CONTENT + '\nAnother note.')
    run(repo, provider_factory=provider)
    second_files = set((repo / 'KG/rendered').glob('*.png'))
    assert len(second_files) == 1 and not first_files & second_files
    run(repo, 'validate')
    records, _ = load_collection(repo)
    delete(repo, next(iter(records)))
    third_files = set((repo / 'KG/rendered').glob('*.png'))
    assert len(third_files) == 1 and not third_files & second_files
    image = (repo / 'KG/KG.png').read_bytes()
    assert next(iter(third_files)).name == digest(image) + '.png'
    assert next(iter(third_files)).read_bytes() == image
    run(repo, 'validate')


def test_invalid_versioned_image_rejected(repo):
    import pytest
    from utility_scripts.ingest import run
    from utility_scripts.contracts import KBError
    run(repo, 'rebuild')
    image = next((repo / 'KG/rendered').glob('*.png'))
    image.write_bytes(b'wrong image')
    with pytest.raises(KBError, match='versioned graph PNG'):
        run(repo, 'validate')
