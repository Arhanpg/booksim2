#!/usr/bin/env python3
import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.abspath(__file__))


def read_rows(name):
    with open(os.path.join(ROOT, name), newline="") as f:
        return [
            r for r in csv.DictReader(f, delimiter="\t")
            if r["status"] == "0" and r["latency"] != "NA" and r["throughput"] != "NA"
        ]


def saturation(rows):
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(row[k] for k in ("topology", "size", "vcs", "traffic"))
        grouped[key].append(row)
    summary = []
    for key, values in sorted(grouped.items()):
        values.sort(key=lambda r: float(r["injection_rate"]))
        minimum = min(float(r["latency"]) for r in values)
        maximum_throughput = max(float(r["throughput"]) for r in values)
        plateau = [
            r for index, r in enumerate(values[:-1])
            if float(r["throughput"]) >= 0.95 * maximum_throughput
            and any(float(later["throughput"]) >= 0.95 * maximum_throughput
                    for later in values[index + 1:])
            and float(r["latency"]) <= 1.5 * minimum
        ]
        if plateau:
            reference = plateau[0]
            summary.append((*key, reference["injection_rate"], reference["throughput"], minimum))
        else:
            summary.append((*key, "not observed", "NA", minimum))
    return summary


def plot_curves(rows, output_name, title, selectors, label_key):
    plt.figure(figsize=(8, 5))
    for selector, label in selectors:
        selected = [
            r for r in rows
            if all(r[k] == v for k, v in selector.items())
        ]
        selected.sort(key=lambda r: float(r["injection_rate"]))
        if selected:
            plt.plot(
                [float(r["injection_rate"]) for r in selected],
                [float(r[label_key]) for r in selected],
                marker="o",
                label=label,
            )
    plt.xlabel("Injection rate (packets/node/cycle)")
    plt.ylabel("Average packet latency (cycles)" if label_key == "latency" else "Accepted throughput")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(ROOT, "graphs", output_name), dpi=160)
    plt.close()


def main():
    os.makedirs(os.path.join(ROOT, "graphs"), exist_ok=True)
    rows = read_rows("booksim_results.tsv")
    adaptive = read_rows("adaptive_results.tsv")
    with open(os.path.join(ROOT, "summary.tsv"), "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(("topology", "size", "vcs", "traffic", "saturation_injection", "saturation_throughput", "minimum_latency"))
        writer.writerows(saturation(rows))

    plot_curves(
        rows,
        "mesh_torus_4x4_vc4_latency.png",
        "Mesh versus Torus: 4x4, VC=4, uniform traffic",
        [({"topology": "mesh", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "Mesh"),
         ({"topology": "torus", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "Torus")],
        "latency",
    )
    plot_curves(
        rows,
        "mesh_torus_4x4_vc4_throughput.png",
        "Mesh versus Torus: 4x4, VC=4, uniform traffic",
        [({"topology": "mesh", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "Mesh"),
         ({"topology": "torus", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "Torus")],
        "throughput",
    )
    plot_curves(
        adaptive,
        "dor_adaptive_4x4_vc4_latency.png",
        "DOR versus adaptive XY/YX: 4x4, VC=4, uniform traffic",
        [({"routing": "dor", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "DOR"),
         ({"routing": "adaptive_xy_yx", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "Adaptive XY/YX")],
        "latency",
    )
    plot_curves(
        adaptive,
        "dor_adaptive_4x4_vc4_throughput.png",
        "DOR versus adaptive XY/YX: 4x4, VC=4, uniform traffic",
        [({"routing": "dor", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "DOR"),
         ({"routing": "adaptive_xy_yx", "size": "4x4", "vcs": "4", "traffic": "uniform"}, "Adaptive XY/YX")],
        "throughput",
    )


if __name__ == "__main__":
    main()
