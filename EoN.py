"""In-browser stand-in for ``EoN`` (Epidemics on Networks).

``EoN`` is published only as a source distribution, so micropip cannot install
it in the browser (Pyodide) runtime. The notebooks use ``EoN`` for one
function, ``hierarchy_pos(G)``, which lays out a tree for matplotlib. This
module provides that function alone: it is EoN's own implementation, copied
from EoN 2.0 (``EoN/auxiliary.py``, MIT License, copyright Joel C. Miller),
so the trees are drawn exactly as they are with EoN installed.

NetworkX is imported at module top level, as a plain (unguarded) import, so the
runtime's import scanner sees it as a dependency and loads it before this module
runs. The scanner only detects direct top-level imports; one nested in a
function would be invisible to it.
"""

# hierarchy_pos below is from EoN 2.0 (EoN/auxiliary.py), under the following license:
#
# Copyright (c) 2016   Joel C Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS OR SPRINGER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random

import networkx as nx


def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0,
                  leaf_vs_root_factor=0.5):
    """Position the nodes of a tree ``G`` for a hierarchical drawing.

    Returns ``{node: (x, y)}``. Horizontal space is allocated partly top down
    (each node's children split its space equally) and partly bottom up (each
    leaf gets equal space, and a node is centred over its leaves);
    ``leaf_vs_root_factor`` sets the blend, ``0`` for bottom up and ``1`` for
    top down. ``root`` defaults to the source of a directed tree, or to a random
    node of an undirected one. Raises ``TypeError`` when ``G`` is not a tree.
    """
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, leftmost, width, leafdx=0.2, vert_gap=0.2,
                       vert_loc=0, xcenter=0.5, rootpos=None, leafpos=None,
                       parent=None):
        if rootpos is None:
            rootpos = {root: (xcenter, vert_loc)}
        else:
            rootpos[root] = (xcenter, vert_loc)
        if leafpos is None:
            leafpos = {}
        children = list(G.neighbors(root))
        leaf_count = 0
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            rootdx = width / len(children)
            nextx = xcenter - width / 2 - rootdx / 2
            for child in children:
                nextx += rootdx
                rootpos, leafpos, newleaves = _hierarchy_pos(
                    G, child, leftmost + leaf_count * leafdx, width=rootdx,
                    leafdx=leafdx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap,
                    xcenter=nextx, rootpos=rootpos, leafpos=leafpos, parent=root)
                leaf_count += newleaves

            leftmostchild = min(x for x, y in [leafpos[child] for child in children])
            rightmostchild = max(x for x, y in [leafpos[child] for child in children])
            leafpos[root] = ((leftmostchild + rightmostchild) / 2, vert_loc)
        else:
            leaf_count = 1
            leafpos[root] = (leftmost, vert_loc)
        return rootpos, leafpos, leaf_count

    xcenter = width / 2.
    if isinstance(G, nx.DiGraph):
        leafcount = len([node for node in nx.descendants(G, root)
                         if G.out_degree(node) == 0])
    elif isinstance(G, nx.Graph):
        leafcount = len([node for node in nx.node_connected_component(G, root)
                         if G.degree(node) == 1 and node != root])
    rootpos, leafpos, leaf_count = _hierarchy_pos(
        G, root, 0, width, leafdx=width * 1. / leafcount, vert_gap=vert_gap,
        vert_loc=vert_loc, xcenter=xcenter)
    pos = {}
    for node in rootpos:
        pos[node] = (leaf_vs_root_factor * leafpos[node][0]
                     + (1 - leaf_vs_root_factor) * rootpos[node][0],
                     leafpos[node][1])
    xmax = max(x for x, y in pos.values())
    for node in pos:
        pos[node] = (pos[node][0] * width / xmax, pos[node][1])
    return pos
