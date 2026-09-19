import networkx as nx

from KG.visualize_KG import render_readme
from utility_scripts.contracts import digest


def test_image_url_tracks_image_bytes_without_changing_handwritten_text():
    text = '# Lab\n<!-- KG:START -->\nold\n<!-- KG:END -->\nKeep instructions.\n'
    records, edges, graph = {}, {'schema_version': 1, 'edges': []}, nx.Graph()
    first = digest(b'first image')
    second = digest(b'changed image')
    rendered = render_readme(text, records, graph, edges, image_sha256=first)
    assert f'(KG/KG.png?v={first})' in rendered
    assert rendered == render_readme(rendered, records, graph, edges, image_sha256=first)
    updated = render_readme(rendered, records, graph, edges, image_sha256=second)
    assert updated == rendered.replace(first, second)
    assert updated.startswith('# Lab\n<!-- KG:START -->\n')
    assert updated.endswith('<!-- KG:END -->\nKeep instructions.\n')
