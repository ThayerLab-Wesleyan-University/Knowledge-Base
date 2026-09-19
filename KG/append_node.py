"""Build a deterministic, scalar-only undirected graph from canonical records."""
import networkx as nx

from utility_scripts.contracts import KBError, validate_edges


def build_graph(records, relationships):
    validate_edges(relationships, records)
    graph = nx.Graph()
    for number, doc_id in enumerate(sorted(records), 1):
        record = records[doc_id]
        graph.add_node(doc_id, title=record["title"], display_label=f"D{number}",
                       content_path=record["content_path"], source_path=record["source_path"],
                       metadata_path=f"KG/node_contents/{doc_id}/metadata.json")
    for edge in sorted(relationships["edges"], key=lambda e: (e["source"], e["target"])):
        graph.add_edge(edge["source"], edge["target"],
                       relation_type=edge["relation_type"], rationale=edge["rationale"],
                       inferred_by=edge["inferred_by"])
    return graph


def write_graph(graph, path):
    nx.write_graphml(graph, path, named_key_ids=True)
    restored = nx.read_graphml(path)
    if restored.is_directed() or restored.is_multigraph():
        raise KBError("GraphML must be a simple undirected graph.")
    if dict(restored.nodes(data=True)) != dict(graph.nodes(data=True)):
        raise KBError("GraphML node round trip failed.")
    if {frozenset((a, b)): d for a, b, d in restored.edges(data=True)} != {
        frozenset((a, b)): d for a, b, d in graph.edges(data=True)
    }:
        raise KBError("GraphML edge round trip failed.")
