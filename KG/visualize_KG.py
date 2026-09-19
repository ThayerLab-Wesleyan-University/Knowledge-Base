"""Static graph visualization and a generated, relative-link Markdown index."""
from __future__ import annotations

import html
import math
import textwrap
import re
from urllib.parse import quote

from utility_scripts.contracts import KBError

START = "<!-- KG:START -->"
END = "<!-- KG:END -->"


def split_readme(text):
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == START]
    ends = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == END]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise KBError("README must contain one ordered pair of standalone KG markers.")
    return "".join(lines[:starts[0] + 1]), "".join(lines[ends[0]:])


def escape(value):
    value = html.escape(" ".join(value.split()), quote=True)
    # Escape Markdown formatting and table delimiters, including backslashes first.
    return re.sub(r"([\\`*_[\]{}()!|~])", r"\\\1", value)


def link(label, path):
    return f"[{escape(label)}]({quote(path, safe='/')})"


def render_readme(text, records, graph, relationships, *, image_sha256):
    before, after = split_readme(text)
    if not re.fullmatch(r"[0-9a-f]{64}", image_sha256):
        raise KBError("README image version must be a SHA-256 digest.")
    lines = ["", f"![ThayerLab document knowledge graph](KG/KG.png?v={image_sha256})", "",
             f"**{len(records)} documents · {graph.number_of_edges()} LLM-inferred connections**", ""]
    if not records:
        lines += ["No documents have been processed yet. Add a submission using the instructions below.", ""]
    lines += ["### Documents", "", "| Node | Document | Original source | Keywords | Connected documents |",
              "| --- | --- | --- | --- | --- |"]
    for doc_id in sorted(records):
        rec = records[doc_id]
        neighbors = ", ".join(link(records[n]["title"], records[n]["content_path"])
                              for n in sorted(graph.neighbors(doc_id))) or "None"
        lines.append(f"| {graph.nodes[doc_id]['display_label']} | {link(rec['title'], rec['content_path'])} ({link('summary', f'KG/node_contents/{doc_id}/metadata.json')}) | "
                     f"{link(rec['source_type'].upper(), rec['source_path'])} | "
                     f"{escape(', '.join(rec['keywords']))} | {neighbors} |")
    lines += ["", "### Connections", "", "All connections below are LLM-inferred topical similarities.", "",
              "| Document | Related document | Rationale |", "| --- | --- | --- |"]
    for edge in sorted(relationships["edges"], key=lambda e: (e["source"], e["target"])):
        a, b = records[edge["source"]], records[edge["target"]]
        lines.append(f"| {link(a['title'], a['content_path'])} | {link(b['title'], b['content_path'])} | "
                     f"{escape(edge['rationale'])} |")
    if not relationships["edges"]:
        lines += ["", "No connections have been generated."]
    return before + "\n".join(lines) + "\n" + after


def short_title(title):
    """Two compact lines; full titles remain in the linked README table."""
    title = " ".join(title.split())
    return "\n".join(textwrap.wrap(title, width=26, max_lines=2, placeholder="…"))


def spaced_layout(graph):
    """Place spring-layout neighbors near each other on nonoverlapping label cells."""
    import networkx as nx
    count = len(graph)
    columns = max(1, math.ceil(math.sqrt(count * 1.5))) if count > 1 else 1
    rows = max(1, math.ceil(count / columns))
    spring = nx.spring_layout(graph, seed=42)
    slots = [(x, -y) for y in range(rows) for x in range(columns)]
    positions = {}
    for node in sorted(graph):
        x, y = spring[node]
        target = ((x + 1) * (columns - 1) / 2, (y - 1) * (rows - 1) / 2)
        slot = min(slots, key=lambda p: ((p[0] - target[0]) ** 2 + (p[1] - target[1]) ** 2, p))
        positions[node] = slot
        slots.remove(slot)
    return positions, columns, rows


def render_image(graph, path):
    # Keep font caches out of the repository and user configuration directory.
    import os
    import tempfile
    with tempfile.TemporaryDirectory(prefix="kb-mpl-") as cache:
        previous = {key: os.environ.get(key) for key in ("MPLCONFIGDIR", "XDG_CACHE_HOME")}
        os.environ["MPLCONFIGDIR"] = cache
        os.environ["XDG_CACHE_HOME"] = cache
        try:
            import matplotlib
            matplotlib.use("Agg")
            from matplotlib import pyplot as plt
            import networkx as nx

            pos, columns, rows = spaced_layout(graph)
            fig, ax = plt.subplots(figsize=(max(12, columns * 2.6), max(7, rows * 1.8 + 2)), dpi=160)
            fig.patch.set_facecolor("#f6f8fc")
            ax.set_facecolor("#f6f8fc")
            ax.set_title("ThayerLab · Knowledge Base", loc="left", fontsize=22,
                         color="#182641", pad=25, weight="bold")
            if graph:
                nx.draw_networkx_edges(graph, pos, ax=ax, edge_color="#99afc7", alpha=0.45, width=1.2)
                nx.draw_networkx_nodes(graph, pos, ax=ax, node_color="#244c78", node_size=850,
                                       edgecolors="white", linewidths=2)
                nx.draw_networkx_labels(graph, pos, ax=ax,
                                        labels=nx.get_node_attributes(graph, "display_label"),
                                        font_color="white", font_size=10)
                for node, attrs in graph.nodes(data=True):
                    ax.annotate(short_title(attrs.get("title", attrs.get("display_label", str(node)))),
                                xy=pos[node], xytext=(0, -24), textcoords="offset points",
                                ha="center", va="top", fontsize=9.5, color="#24405f",
                                linespacing=1.35, parse_math=False,
                                bbox={"boxstyle": "round,pad=0.3", "facecolor": "#f6f8fc",
                                      "edgecolor": "none", "alpha": 0.95},
                                zorder=4)
                ax.set_xlim(-0.65, columns - 0.35)
                ax.set_ylim(-rows + 0.25, 0.65)
            else:
                ax.text(0.5, 0.55, "The collection starts with your first document.",
                        transform=ax.transAxes, ha="center", fontsize=18, color="#244c78")
                ax.text(0.5, 0.43, "Submit a PDF or Markdown file to grow the knowledge graph.",
                        transform=ax.transAxes, ha="center", fontsize=11, color="#556981")
            ax.text(0, -0.06, f"{graph.number_of_nodes()} documents  |  {graph.number_of_edges()} connections"
                    "    ·    Edges are LLM-inferred; document links appear below.",
                    transform=ax.transAxes, fontsize=10, color="#556981")
            ax.axis("off")
            fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight",
                        metadata={"Software": "ThayerLab Knowledge Base"})
            plt.close(fig)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
