"""
DependencyAI
============

Production-grade dependency reasoning over a *backlog* of stories.

This module composes the cheap rule layer in :mod:`.dependencies` with
embedding-based similarity matching and graph analytics to answer the
questions that actually matter to a tech lead:

* Which story blocks the most other work?         → ``bottlenecks()``
* What's the critical path through the backlog?    → ``critical_path()``
* Is the sprint plan valid?                        → ``validate_sprints()``
* What's the risk score of each story?             → ``risk_scores()``
* What if I move this story to a different sprint? → ``what_if()``
* Concrete action recommendations                  → ``recommendations()``

The graph is a DAG (cycles are broken at build time) where an edge
``A → B`` means "A must be done before B".

Design
------
* **Pure stdlib at the public path** — no numpy/networkx required.
* **Pluggable embedding backend** — same callable signature as
  :class:`.SemanticParser`.  When supplied, it discovers *cross-domain*
  dependencies that the rule layer can't see (e.g. "pay" → "invoice
  generation" when the latter is phrased unusually).
* **Stable IDs** — every story gets a deterministic ``story_id`` so
  the resulting graph is JSON-serialisable and idempotent.
"""
from __future__ import annotations

import logging
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple,
)

from .dependencies import (
    DependencyEngine, ENTITY_DEPENDENCIES, INTENT_DEPENDENCIES,
)
from .ir import StoryIR

log = logging.getLogger(__name__)

# Embedding backend: same signature as SemanticParser's
EmbeddingBackend = Callable[[str, Iterable[str]], Tuple[Optional[str], float]]


# ─────────────────────────────────────────────────────────────────────────
@dataclass
class Edge:
    """A directed dependency edge.  ``src → dst`` means *do src first*."""
    src: str
    dst: str
    kind: str          # "rule:intent" | "rule:entity" | "embedding" | "manual"
    weight: float = 1.0  # higher = harder dependency
    reason: str = ""


@dataclass
class StoryNode:
    story_id: str
    ir: StoryIR
    sprint: Optional[int] = None
    story_points: Optional[int] = None
    title: Optional[str] = None

    @property
    def text_repr(self) -> str:
        bits = [self.title or "", self.ir.action_phrase or "",
                self.ir.source_text or ""]
        return " ".join(b for b in bits if b)


# ─────────────────────────────────────────────────────────────────────────
def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in (s or ""))[:32] or "n"


def _node_id(ir: StoryIR, idx: int) -> str:
    base = ir.intent or "node"
    extra = ir.entity or ir.actor or str(idx)
    return f"{_slug(base)}_{_slug(extra)}_{idx}"


def _wrap_nodes(
    items: Sequence[Any],
) -> List[StoryNode]:
    """Accept ``StoryIR`` | ``StoryNode`` | ``dict`` and normalise."""
    out: List[StoryNode] = []
    for i, it in enumerate(items):
        if isinstance(it, StoryNode):
            out.append(it)
            continue
        if isinstance(it, StoryIR):
            out.append(StoryNode(
                story_id=_node_id(it, i),
                ir=it,
            ))
            continue
        if isinstance(it, dict):
            ir = it.get("ir")
            if ir is None:
                # Best effort: synthesise a minimal IR from the dict
                ir = StoryIR(source_text=it.get("user_story")
                             or it.get("title") or "")
                ir.intent = it.get("intent") or ""
                ir.entity = it.get("entity") or ""
                ir.domain = it.get("domain") or "General"
            out.append(StoryNode(
                story_id=str(it.get("id") or it.get("story_id")
                             or _node_id(ir, i)),
                ir=ir,
                sprint=it.get("sprint") or it.get("sprint_id"),
                story_points=it.get("story_points") or it.get("sp"),
                title=it.get("title"),
            ))
            continue
        raise TypeError(f"Unsupported node type: {type(it)}")
    return out


# ─────────────────────────────────────────────────────────────────────────
class DependencyAI:
    """Backlog-level dependency reasoning + risk analytics.

    Parameters
    ----------
    embedding_backend:
        Optional callable used to *augment* rule-based detection with
        sentence-similarity matches.  Edges discovered by the backend
        carry ``kind="embedding"`` and a confidence ``weight``.
    embedding_threshold:
        Minimum cosine score needed to register an embedding edge.
    """

    def __init__(
        self,
        embedding_backend: Optional[EmbeddingBackend] = None,
        embedding_threshold: float = 0.55,
    ) -> None:
        self._engine = DependencyEngine()
        self._embed = embedding_backend
        self._embed_threshold = embedding_threshold
        # Lazily-built state
        self._nodes: Dict[str, StoryNode] = {}
        self._adj: Dict[str, List[Edge]] = defaultdict(list)   # src → edges
        self._radj: Dict[str, List[Edge]] = defaultdict(list)  # dst → edges

    # ── Public: build ───────────────────────────────────────────────────
    def build(self, items: Sequence[Any]) -> "DependencyAI":
        """Construct the dependency DAG.

        ``items`` may be a list of ``StoryIR``, ``StoryNode`` or plain
        dicts.  Cycles are broken by dropping the lowest-weight edge.
        """
        self._nodes = {}
        self._adj = defaultdict(list)
        self._radj = defaultdict(list)

        nodes = _wrap_nodes(items)
        for n in nodes:
            self._nodes[n.story_id] = n

        # Indices for rule resolution
        by_intent: Dict[str, List[str]] = defaultdict(list)
        by_entity: Dict[str, List[str]] = defaultdict(list)
        for n in nodes:
            if n.ir.intent:
                by_intent[n.ir.intent].append(n.story_id)
            if n.ir.entity:
                by_entity[n.ir.entity].append(n.story_id)

        # 1) Rule layer
        for n in nodes:
            for dep in self._engine.dependencies_for(n.ir):
                if dep.startswith("entity:"):
                    targets = by_entity.get(dep.split(":", 1)[1], [])
                    kind = "rule:entity"
                else:
                    targets = by_intent.get(dep, [])
                    kind = "rule:intent"
                for src_id in targets:
                    if src_id == n.story_id:
                        continue
                    self._add_edge(Edge(
                        src=src_id, dst=n.story_id,
                        kind=kind, weight=1.0,
                        reason=f"{kind}:{dep}",
                    ))

        # 2) Embedding layer (optional)
        if self._embed is not None:
            self._embedding_links(nodes)

        # 3) Break cycles before exposing the graph
        self._break_cycles()
        return self

    def _add_edge(self, edge: Edge) -> None:
        # Dedup by (src, dst) — keep the highest weight + most informative kind
        for e in self._adj[edge.src]:
            if e.dst == edge.dst:
                if edge.weight > e.weight:
                    e.weight = edge.weight
                    e.kind = edge.kind
                    e.reason = edge.reason
                return
        self._adj[edge.src].append(edge)
        self._radj[edge.dst].append(edge)

    # ── Embedding edges ────────────────────────────────────────────────
    def _embedding_links(self, nodes: List[StoryNode]) -> None:
        """Pair every node against every other; create an edge when the
        candidate's title looks like a *prerequisite* of the source."""
        if self._embed is None:
            return
        # Build candidate "definition" snippets once
        defs = {n.story_id: n.text_repr for n in nodes if n.text_repr.strip()}
        if len(defs) < 2:
            return

        # We expose only the "predecessor" direction the rule layer
        # would have caught, by asking the encoder which candidate
        # *precedes* this one.  For each story `n`, ask: among all
        # other story descriptions, which is most similar to a
        # synthetic "before <n.intent>" query?
        for n in nodes:
            if not n.text_repr.strip() or not n.ir.intent:
                continue
            query = f"prerequisite for {n.ir.intent} {n.ir.entity or ''}".strip()
            candidates_ids = [oid for oid in defs if oid != n.story_id]
            candidates_text = [defs[i] for i in candidates_ids]
            try:
                best, score = self._embed(query, candidates_text)
            except Exception as exc:  # backend failure should never break us
                log.debug("Embedding backend error: %s", exc)
                continue
            if not best or score < self._embed_threshold:
                continue
            # Map text back to ID
            try:
                idx = candidates_text.index(best)
            except ValueError:
                continue
            src_id = candidates_ids[idx]
            # Avoid creating reverse edges that contradict an existing rule edge
            if any(e.dst == src_id for e in self._adj[n.story_id]):
                continue
            self._add_edge(Edge(
                src=src_id, dst=n.story_id,
                kind="embedding", weight=float(score),
                reason=f"embedding:sim={score:.2f}",
            ))

    # ── Cycle breaking ─────────────────────────────────────────────────
    def _break_cycles(self) -> None:
        """Greedy: while a cycle exists, remove its lowest-weight edge."""
        while True:
            cyc = self._find_cycle()
            if not cyc:
                return
            # Find the lowest-weight edge along the cycle
            worst: Optional[Edge] = None
            for src, dst in zip(cyc, cyc[1:] + cyc[:1]):
                for e in self._adj[src]:
                    if e.dst == dst and (worst is None or e.weight < worst.weight):
                        worst = e
            if worst is None:
                return  # shouldn't happen
            self._adj[worst.src] = [e for e in self._adj[worst.src]
                                    if e.dst != worst.dst]
            self._radj[worst.dst] = [e for e in self._radj[worst.dst]
                                     if e.src != worst.src]
            log.debug("Broke cycle by removing %s → %s",
                      worst.src, worst.dst)

    def _find_cycle(self) -> List[str]:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {nid: WHITE for nid in self._nodes}
        parent: Dict[str, Optional[str]] = {nid: None for nid in self._nodes}
        cycle: List[str] = []

        def dfs(u: str) -> bool:
            color[u] = GRAY
            for e in self._adj[u]:
                v = e.dst
                if color.get(v, WHITE) == GRAY:
                    # Reconstruct cycle u..v..u
                    nonlocal cycle
                    path = [u]
                    p = parent.get(u)
                    while p is not None and p != v:
                        path.append(p)
                        p = parent.get(p)
                    path.append(v)
                    cycle = list(reversed(path))
                    return True
                if color.get(v, WHITE) == WHITE:
                    parent[v] = u
                    if dfs(v):
                        return True
            color[u] = BLACK
            return False

        for nid in self._nodes:
            if color[nid] == WHITE and dfs(nid):
                return cycle
        return []

    # ── Public: queries ────────────────────────────────────────────────
    @property
    def nodes(self) -> Dict[str, StoryNode]:
        return self._nodes

    def edges(self) -> List[Edge]:
        return [e for edges in self._adj.values() for e in edges]

    def topological_order(self) -> List[StoryNode]:
        """Kahn's algorithm.  Ties broken by domain → intent for stability."""
        indeg: Dict[str, int] = {nid: 0 for nid in self._nodes}
        for e in self.edges():
            indeg[e.dst] = indeg.get(e.dst, 0) + 1
        ready = deque(sorted(
            (nid for nid, d in indeg.items() if d == 0),
            key=lambda nid: (
                self._nodes[nid].ir.domain or "zzz",
                self._nodes[nid].ir.intent or "zzz",
            ),
        ))
        order: List[StoryNode] = []
        while ready:
            nid = ready.popleft()
            order.append(self._nodes[nid])
            for e in self._adj[nid]:
                indeg[e.dst] -= 1
                if indeg[e.dst] == 0:
                    ready.append(e.dst)
        return order

    def bottlenecks(self, top_k: int = 5) -> List[Tuple[StoryNode, int]]:
        """Stories that block the most other work (out-degree, transitive).

        Returns a list of ``(node, blocked_count)`` ordered desc.
        """
        blocked: Dict[str, int] = {}
        for nid in self._nodes:
            seen: Set[str] = set()
            stack = [e.dst for e in self._adj[nid]]
            while stack:
                v = stack.pop()
                if v in seen:
                    continue
                seen.add(v)
                stack.extend(e.dst for e in self._adj[v])
            blocked[nid] = len(seen)
        ordered = sorted(blocked.items(), key=lambda kv: kv[1], reverse=True)
        return [(self._nodes[nid], n) for nid, n in ordered[:top_k] if n > 0]

    def critical_path(self) -> List[StoryNode]:
        """Longest dependency chain weighted by story points (or 1)."""
        # DAG longest path via topological DP
        order = [n.story_id for n in self.topological_order()]
        dist: Dict[str, float] = {nid: 0.0 for nid in self._nodes}
        prev: Dict[str, Optional[str]] = {nid: None for nid in self._nodes}
        for nid in order:
            w = self._nodes[nid].story_points or 1
            for e in self._adj[nid]:
                cand = dist[nid] + (w if e.weight >= 1.0 else w * e.weight)
                if cand > dist.get(e.dst, 0.0):
                    dist[e.dst] = cand
                    prev[e.dst] = nid
        if not dist:
            return []
        end = max(dist, key=lambda k: dist[k])
        path: List[str] = []
        cur: Optional[str] = end
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        return [self._nodes[i] for i in reversed(path)]

    def validate_sprints(self) -> List[Dict[str, Any]]:
        """Return a list of plan-violation issues.

        A violation is reported when a story is scheduled in an *earlier*
        sprint than one of its prerequisites — that's an unbuildable plan.
        """
        issues: List[Dict[str, Any]] = []
        for e in self.edges():
            src = self._nodes[e.src]
            dst = self._nodes[e.dst]
            if src.sprint is None or dst.sprint is None:
                continue
            if src.sprint > dst.sprint:
                issues.append({
                    "type": "dependency_violation",
                    "blocker": src.story_id,
                    "blocked": dst.story_id,
                    "blocker_sprint": src.sprint,
                    "blocked_sprint": dst.sprint,
                    "reason": e.reason,
                    "message": (
                        f"Story '{dst.title or dst.story_id}' is scheduled in "
                        f"Sprint {dst.sprint} but depends on "
                        f"'{src.title or src.story_id}' in Sprint {src.sprint}."
                    ),
                })
        return issues

    def risk_scores(self) -> Dict[str, Dict[str, float]]:
        """Per-story risk score in [0, 1] with a component breakdown.

        risk = w1·dep_depth + w2·blocking_factor + w3·sp_outlier
             + w4·cross_domain + w5·external_dep_flag
        """
        # Depth: longest chain *into* this node
        depth: Dict[str, int] = {nid: 0 for nid in self._nodes}
        order = [n.story_id for n in self.topological_order()]
        for nid in order:
            for e in self._adj[nid]:
                depth[e.dst] = max(depth[e.dst], depth[nid] + 1)
        max_depth = max(depth.values()) if depth else 1

        # Blocking factor: transitive descendants
        blocked = {nid: cnt for (n, cnt) in self.bottlenecks(top_k=10**9)
                   for nid in [n.story_id]}
        max_blocked = max(blocked.values()) if blocked else 1

        # SP outlier: distance from median SP, normalised
        sps = [n.story_points for n in self._nodes.values()
               if n.story_points is not None]
        median_sp = sorted(sps)[len(sps) // 2] if sps else 5
        max_sp_dev = max((abs((n.story_points or median_sp) - median_sp)
                          for n in self._nodes.values()), default=1) or 1

        # Cross-domain: edges whose endpoints span different domains
        cross_dom: Dict[str, int] = defaultdict(int)
        for e in self.edges():
            sd = self._nodes[e.src].ir.domain or ""
            dd = self._nodes[e.dst].ir.domain or ""
            if sd and dd and sd != dd:
                cross_dom[e.dst] += 1
        max_cross = max(cross_dom.values()) if cross_dom else 1

        scores: Dict[str, Dict[str, float]] = {}
        for nid, n in self._nodes.items():
            d = depth[nid] / max_depth if max_depth else 0.0
            b = (blocked.get(nid, 0) / max_blocked) if max_blocked else 0.0
            sp_dev = (abs((n.story_points or median_sp) - median_sp)
                      / max_sp_dev)
            cd = (cross_dom.get(nid, 0) / max_cross) if max_cross else 0.0
            ext = 1.0 if getattr(n.ir, "has_external_api", False) else 0.0

            score = (0.30 * d + 0.30 * b + 0.15 * sp_dev
                     + 0.15 * cd + 0.10 * ext)
            scores[nid] = {
                "score": round(min(1.0, score), 3),
                "dep_depth": round(d, 3),
                "blocking_factor": round(b, 3),
                "sp_outlier": round(sp_dev, 3),
                "cross_domain": round(cd, 3),
                "external_dep": ext,
            }
        return scores

    # ── What-if simulation ─────────────────────────────────────────────
    def what_if(self, story_id: str, new_sprint: int) -> Dict[str, Any]:
        """Move a story to ``new_sprint`` and re-validate.

        The original plan is left untouched; the result includes the
        delta in violations and the affected stories.
        """
        if story_id not in self._nodes:
            raise KeyError(story_id)
        old_sprint = self._nodes[story_id].sprint
        before = {(i["blocker"], i["blocked"])
                  for i in self.validate_sprints()}
        self._nodes[story_id].sprint = new_sprint
        try:
            after_issues = self.validate_sprints()
        finally:
            self._nodes[story_id].sprint = old_sprint
        after = {(i["blocker"], i["blocked"]) for i in after_issues}
        return {
            "story_id": story_id,
            "from_sprint": old_sprint,
            "to_sprint": new_sprint,
            "violations_resolved": sorted(before - after),
            "violations_introduced": sorted(after - before),
            "net_delta": len(after) - len(before),
            "after_issues": after_issues,
        }

    # ── Recommendations ────────────────────────────────────────────────
    def recommendations(self) -> List[Dict[str, Any]]:
        """Concrete, actionable suggestions ranked by impact.

        Combines: critical-path bottlenecks, sprint violations, high-risk
        stories, and over-allocated sprints.
        """
        recs: List[Dict[str, Any]] = []

        # 1) Resolve every dependency violation by suggesting a sprint move
        for issue in self.validate_sprints():
            recs.append({
                "kind": "fix_dependency_violation",
                "priority": "high",
                "story_id": issue["blocked"],
                "action": f"Move to Sprint {issue['blocker_sprint'] + 1} or later",
                "reason": issue["message"],
            })

        # 2) Critical-path stories deserve attention
        cp = self.critical_path()
        if len(cp) >= 3:
            recs.append({
                "kind": "critical_path",
                "priority": "high",
                "story_ids": [n.story_id for n in cp],
                "action": "Protect this chain — slip = whole-project slip",
                "reason": "Longest weighted dependency chain in the backlog",
            })

        # 3) Top bottlenecks
        for n, blocked in self.bottlenecks(top_k=3):
            if blocked >= 3:
                recs.append({
                    "kind": "bottleneck",
                    "priority": "high",
                    "story_id": n.story_id,
                    "action": "Schedule earliest possible / parallelise team",
                    "reason": f"Blocks {blocked} downstream stories",
                })

        # 4) High-risk stories
        for nid, comp in self.risk_scores().items():
            if comp["score"] >= 0.7:
                recs.append({
                    "kind": "high_risk_story",
                    "priority": "medium",
                    "story_id": nid,
                    "action": "Review scope / add buffer / pair-program",
                    "reason": f"Risk score {comp['score']:.2f}: " + ", ".join(
                        f"{k}={v}" for k, v in comp.items()
                        if k != "score" and v >= 0.5
                    ),
                })

        # 5) Sprint overload (relative to median capacity)
        by_sprint: Dict[int, int] = defaultdict(int)
        for n in self._nodes.values():
            if n.sprint is not None:
                by_sprint[n.sprint] += n.story_points or 0
        if by_sprint:
            loads = sorted(by_sprint.values())
            median = loads[len(loads) // 2]
            for sp_idx, load in by_sprint.items():
                if median and load > 1.4 * median:
                    recs.append({
                        "kind": "sprint_overload",
                        "priority": "medium",
                        "sprint": sp_idx,
                        "action": (
                            f"Sprint {sp_idx} carries {load} SP "
                            f"(>{int(median * 1.4)} threshold) — "
                            "consider splitting"
                        ),
                        "reason": f"Median sprint load is {median} SP",
                    })

        return recs

    # ── Export ─────────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {
                    "id": nid,
                    "title": n.title,
                    "intent": n.ir.intent,
                    "entity": n.ir.entity,
                    "domain": n.ir.domain,
                    "sprint": n.sprint,
                    "story_points": n.story_points,
                }
                for nid, n in self._nodes.items()
            ],
            "edges": [
                {"src": e.src, "dst": e.dst, "kind": e.kind,
                 "weight": e.weight, "reason": e.reason}
                for e in self.edges()
            ],
            "topological_order": [n.story_id for n in self.topological_order()],
            "critical_path": [n.story_id for n in self.critical_path()],
            "bottlenecks": [
                {"id": n.story_id, "blocks": cnt}
                for n, cnt in self.bottlenecks()
            ],
            "risk_scores": self.risk_scores(),
            "validation_issues": self.validate_sprints(),
            "recommendations": self.recommendations(),
        }
