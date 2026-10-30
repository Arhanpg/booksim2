#!/usr/bin/env python3
import re
import sys
from collections import defaultdict, deque


def main(path):
    graph = defaultdict(set)
    nodes = set()
    for line in open(path, encoding="utf-8"):
        routers = [int(x) for x in re.findall(r"router\s+(\d+)", line)]
        if not routers:
            continue
        head, *neighbors = routers
        nodes.add(head)
        graph[head].update(neighbors)
        for neighbor in neighbors:
            graph[neighbor].add(head)
        node = re.search(r"\bnode\s+(\d+)", line)
        if node:
            nodes.add(int(node.group(1)))
    edges = {tuple(sorted((a, b))) for a in graph for b in graph[a] if a != b}
    distances = []
    for source in sorted(graph):
        distance = {source: 0}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor in graph[current]:
                if neighbor not in distance:
                    distance[neighbor] = distance[current] + 1
                    queue.append(neighbor)
        if len(distance) != len(graph):
            raise SystemExit(f"disconnected from router {source}")
        distances.extend(distance[d] for d in distance if d > source)
    print(f"routers={len(graph)}")
    print(f"nodes={len(nodes)}")
    print(f"unique_undirected_links={len(edges)}")
    print(f"minimum_degree={min(map(len, graph.values()))}")
    print(f"maximum_degree={max(map(len, graph.values()))}")
    print(f"diameter={max(distances)}")
    print(f"mean_shortest_path={sum(distances) / len(distances):.4f}")
    expected = (16, 16, 42, 4, 6, 3, 1.8167)
    actual = (len(graph), len(nodes), len(edges), min(map(len, graph.values())),
              max(map(len, graph.values())), max(distances),
              round(sum(distances) / len(distances), 4))
    if actual != expected:
        raise SystemExit(f"validation mismatch: expected {expected}, got {actual}")
    print("validation=PASS")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_hybrid_graph.py NETWORK_FILE")
    main(sys.argv[1])
