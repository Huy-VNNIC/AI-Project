"""
Dependency-graph visualisation
==============================

Renders the dependency graph computed by :class:`DependencyEngine` in
three popular formats:

* **Mermaid** (``flowchart TD``) — pastes straight into Markdown / VS Code
  preview and GitHub.
* **Graphviz DOT** — for ``dot -Tpng`` rendering.
* **JSON** — for downstream tooling (D3, Cytoscape …).

A node represents a story; edges point *from prerequisite to dependant*
(read: "you must do A *before* B").  Nodes are coloured by ``ir.domain``.
"""
from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .dependencies import DependencyEngine
from .ir import StoryIR


# ── Palette (kept small + colour-blind-friendly) ───────────────────────────
_DOMAIN_COLOR = {
    "Clinical":           "#e74c3c",
    "Inpatient":          "#c0392b",
    "Surgery":            "#8e44ad",
    "Pharmacy":           "#16a085",
    "Laboratory":         "#27ae60",
    "Healthcare":         "#1abc9c",
    "Payment/Billing":    "#f39c12",
    "Booking/Reservation":"#3498db",
    "Hotel":              "#2980b9",
    "General":            "#7f8c8d",
}


@dataclass
class _Node:
    node_id: str
    label: str
    domain: str
    intent: str
    sp: Optional[int] = None


def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in s)[:40] or "n"


def _node_id(ir: StoryIR, idx: int) -> str:
    base = ir.intent or "node"
    extra = ir.entity or ir.actor or str(idx)
    return f"{_slug(base)}_{_slug(extra)}_{idx}"


def _build_nodes(
    irs: Sequence[StoryIR],
    sp_values: Optional[Sequence[int]] = None,
) -> List[_Node]:
    nodes: List[_Node] = []
    for i, ir in enumerate(irs):
        label_parts = [ir.intent or "?"]
        if ir.entity:
            label_parts.append(ir.entity)
        label = " · ".join(label_parts)
        nodes.append(_Node(
            node_id=_node_id(ir, i),
            label=label,
            domain=ir.domain or "General",
            intent=ir.intent or "unknown",
            sp=(sp_values[i] if sp_values and i < len(sp_values) else None),
        ))
    return nodes


def _build_edges(
    irs: Sequence[StoryIR],
    nodes: Sequence[_Node],
    engine: DependencyEngine,
) -> List[Tuple[str, str]]:
    """Edge from prerequisite-node → dependant-node.

    Dependency tokens are matched against node intents/entities; tokens
    that don't resolve to a known node are silently dropped (they
    represent *external* prerequisites).
    """
    by_intent: Dict[str, str] = {}
    by_entity: Dict[str, str] = {}
    for ir, node in zip(irs, nodes):
        if ir.intent:
            by_intent.setdefault(ir.intent, node.node_id)
        if ir.entity:
            by_entity.setdefault(ir.entity, node.node_id)

    edges: List[Tuple[str, str]] = []
    for ir, node in zip(irs, nodes):
        for dep in engine.dependencies_for(ir):
            if dep.startswith("entity:"):
                target = by_entity.get(dep.split(":", 1)[1])
            else:
                target = by_intent.get(dep)
            if target and target != node.node_id:
                edges.append((target, node.node_id))
    return edges


# ── Renderers ──────────────────────────────────────────────────────────────
def to_mermaid(
    irs: Sequence[StoryIR],
    *,
    sp_values: Optional[Sequence[int]] = None,
    engine: Optional[DependencyEngine] = None,
    title: str = "Story Dependency Graph",
) -> str:
    engine = engine or DependencyEngine()
    nodes = _build_nodes(irs, sp_values)
    edges = _build_edges(irs, nodes, engine)

    lines: List[str] = []
    lines.append(f"%% {title}")
    lines.append("flowchart TD")
    for n in nodes:
        sp_tag = f" ({n.sp} SP)" if n.sp is not None else ""
        # Mermaid label needs HTML escaping for the pipe + quotes
        label = html.escape(f"{n.label}{sp_tag}")
        lines.append(f'    {n.node_id}["{label}"]:::d_{_slug(n.domain)}')
    for src, dst in edges:
        lines.append(f"    {src} --> {dst}")
    # classDefs for domain colours
    for domain, color in _DOMAIN_COLOR.items():
        lines.append(
            f"    classDef d_{_slug(domain)} fill:{color},"
            f"stroke:#222,color:#fff;"
        )
    return "\n".join(lines)


def to_dot(
    irs: Sequence[StoryIR],
    *,
    sp_values: Optional[Sequence[int]] = None,
    engine: Optional[DependencyEngine] = None,
    title: str = "Story Dependency Graph",
) -> str:
    engine = engine or DependencyEngine()
    nodes = _build_nodes(irs, sp_values)
    edges = _build_edges(irs, nodes, engine)

    lines: List[str] = [
        f'digraph "{title}" {{',
        "  rankdir=TB;",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica"];',
    ]
    for n in nodes:
        color = _DOMAIN_COLOR.get(n.domain, _DOMAIN_COLOR["General"])
        sp_tag = f"\\n({n.sp} SP)" if n.sp is not None else ""
        label = (n.label + sp_tag).replace('"', '\\"')
        lines.append(
            f'  {n.node_id} [label="{label}", fillcolor="{color}", '
            f'fontcolor="white"];'
        )
    for src, dst in edges:
        lines.append(f"  {src} -> {dst};")
    lines.append("}")
    return "\n".join(lines)


def to_json(
    irs: Sequence[StoryIR],
    *,
    sp_values: Optional[Sequence[int]] = None,
    engine: Optional[DependencyEngine] = None,
) -> str:
    engine = engine or DependencyEngine()
    nodes = _build_nodes(irs, sp_values)
    edges = _build_edges(irs, nodes, engine)
    payload = {
        "nodes": [
            {
                "id": n.node_id,
                "label": n.label,
                "intent": n.intent,
                "domain": n.domain,
                "sp": n.sp,
                "color": _DOMAIN_COLOR.get(n.domain, _DOMAIN_COLOR["General"]),
            }
            for n in nodes
        ],
        "edges": [{"from": s, "to": d} for s, d in edges],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ── Convenience writer ─────────────────────────────────────────────────────
def write_graph(
    irs: Sequence[StoryIR],
    out_path: str | Path,
    *,
    fmt: Optional[str] = None,
    sp_values: Optional[Sequence[int]] = None,
    engine: Optional[DependencyEngine] = None,
) -> Path:
    """Write the graph to ``out_path``.  Format auto-detected from suffix
    when ``fmt`` is omitted (``.md|.mmd → mermaid``, ``.dot|.gv → dot``,
    ``.json → json``)."""
    p = Path(out_path)
    if fmt is None:
        suffix = p.suffix.lower()
        fmt = {
            ".md": "mermaid", ".mmd": "mermaid",
            ".dot": "dot", ".gv": "dot",
            ".json": "json",
        }.get(suffix, "mermaid")

    if fmt == "mermaid":
        body = to_mermaid(irs, sp_values=sp_values, engine=engine)
        # Make .md files render directly on GitHub
        if p.suffix.lower() == ".md":
            body = "```mermaid\n" + body + "\n```\n"
    elif fmt == "dot":
        body = to_dot(irs, sp_values=sp_values, engine=engine)
    elif fmt == "json":
        body = to_json(irs, sp_values=sp_values, engine=engine)
    else:
        raise ValueError(f"Unknown format: {fmt}")

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p
