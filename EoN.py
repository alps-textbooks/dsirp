"""In-browser compatibility shim for ``EoN`` (Epidemics on Networks).

Upstream ``EoN`` ships no pure-python wheel, so it cannot install in the browser
(Pyodide) runtime via micropip (``!pip install EoN`` fails with "Can't find a
pure Python 3 wheel for 'eon'"). The DSIRP notebooks use ``EoN`` for exactly one
thing: ``hierarchy_pos(G)``, which lays out a tree for matplotlib. Provide that
one function — the canonical NetworkX tree layout that EoN itself ships (due to
Joel C. Miller, EoN's author) — so the tree-drawing cells run.

NetworkX is imported at module top level, as a plain (unguarded) import, so the
runtime's import scanner sees it as a dependency and loads it before this module
runs. The scanner only detects direct top-level imports; one nested in a
function would be invisible to it.
"""

import networkx as nx


def hierarchy_pos(G, root=None, width=1.0, vert_gap=0.2, vert_loc=0.0, xcenter=0.5):
    """Position the nodes of a tree ``G`` hierarchically for drawing.

    Returns ``{node: (x, y)}``. Matches ``EoN.hierarchy_pos`` for the
    single-argument call the notebooks use. Raises ``TypeError`` when ``G`` is
    not a tree, exactly as EoN does.
    """
    if not nx.is_tree(G):
        raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = next(iter(G.nodes))

    def _hierarchy_pos(node, left, right, vloc, pos, parent):
        xcenter_ = (left + right) / 2.0
        pos[node] = (xcenter_, vloc)
        children = list(G.neighbors(node))
        if not isinstance(G, nx.DiGraph) and parent is not None and parent in children:
            children.remove(parent)
        if children:
            dx = (right - left) / len(children)
            nextleft = left
            for child in children:
                _hierarchy_pos(child, nextleft, nextleft + dx, vloc - vert_gap,
                               pos, node)
                nextleft += dx
        return pos

    half = width / 2.0
    return _hierarchy_pos(root, xcenter - half, xcenter + half, vert_loc, {}, None)
