#!/usr/bin/env python3
import csv
import os
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.abspath(__file__))
GRAPH_DIR = os.path.join(ROOT, "graphs", "task2_task3")


def rows(path):
    with open(path, newline="") as stream:
        return [
            row for row in csv.DictReader(stream, delimiter="\t")
            if row["status"] == "0" and row["latency"] != "NA" and row["throughput"] != "NA"
        ]


def aggregate(data, keys):
    groups = defaultdict(list)
    for row in data:
        groups[tuple(row[key] for key in keys)].append(row)
    output = []
    for key, values in sorted(groups.items()):
        row = dict(zip(keys, key))
        latencies = [float(value["latency"]) for value in values]
        throughputs = [float(value["throughput"]) for value in values]
        row["latency"] = str(statistics.mean(latencies))
        row["throughput"] = str(statistics.mean(throughputs))
        row["latency_stddev"] = str(statistics.stdev(latencies)) if len(latencies) > 1 else "0"
        row["throughput_stddev"] = str(statistics.stdev(throughputs)) if len(throughputs) > 1 else "0"
        output.append(row)
    return output


def safe_name(traffic):
    return traffic.replace("(", "").replace(")", "")


def plot_task2(data, traffic, metric):
    plt.figure(figsize=(8, 5))
    for topology in ("mesh", "hybrid"):
        selected = [r for r in data if r["topology"] == topology and r["traffic"] == traffic]
        selected.sort(key=lambda r: float(r["injection_rate"]))
        plt.plot(
            [float(r["injection_rate"]) for r in selected],
            [float(r[metric]) for r in selected],
            marker="o", label=topology.title(),
        )
    plt.xlabel("Injection rate (packets/node/cycle)")
    plt.ylabel("Average packet latency (cycles)" if metric == "latency" else "Accepted throughput")
    plt.title(f"Task 2: Mesh versus Hybrid ({traffic})")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPH_DIR, f"task2_{safe_name(traffic)}_{metric}.png"), dpi=160)
    plt.close()


def plot_task3(data, topology, traffic, metric):
    plt.figure(figsize=(8, 5))
    for routing, label in (("dor", "DOR"), ("dim_order", "Dimension-order"),
                           ("hacr_min_adapt", "HACR")):
        selected = [r for r in data if r["topology"] == topology and
                    r["routing"] == routing and r["traffic"] == traffic]
        selected.sort(key=lambda r: float(r["injection_rate"]))
        if selected:
            plt.plot(
                [float(r["injection_rate"]) for r in selected],
                [float(r[metric]) for r in selected],
                marker="o", label=label,
            )
    plt.xlabel("Injection rate (packets/node/cycle)")
    plt.ylabel("Average packet latency (cycles)" if metric == "latency" else "Accepted throughput")
    plt.title(f"Task 3: {topology.title()} routing comparison ({traffic})")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPH_DIR, f"task3_{topology}_{safe_name(traffic)}_{metric}.png"), dpi=160)
    plt.close()


def saturation(data, keys):
    groups = defaultdict(list)
    for row in data:
        groups[tuple(row[key] for key in keys)].append(row)
    output = []
    for key, values in sorted(groups.items()):
        values.sort(key=lambda row: float(row["injection_rate"]))
        minimum = min(float(row["latency"]) for row in values)
        maximum_throughput = max(float(row["throughput"]) for row in values)
        plateau = [
            row for index, row in enumerate(values[:-1])
            if float(row["throughput"]) >= 0.95 * maximum_throughput
            and any(
                float(later["throughput"]) >= 0.95 * maximum_throughput
                for later in values[index + 1:]
            )
            and float(row["latency"]) <= 1.5 * minimum
        ]
        if not plateau:
            output.append((*key, "not observed", "NA", minimum))
        else:
            point = plateau[0]
            output.append((*key, point["injection_rate"], point["throughput"], minimum))
    return output


def main():
    os.makedirs(GRAPH_DIR, exist_ok=True)
    task2_raw = rows(os.path.join(ROOT, "task2", "task2_results.tsv"))
    task3_raw = rows(os.path.join(ROOT, "task3", "task3_results.tsv"))
    task2 = aggregate(task2_raw, ("topology", "size", "vcs", "traffic", "injection_rate"))
    task3 = aggregate(task3_raw, ("topology", "routing", "vcs", "traffic", "injection_rate"))
    traffic_patterns = ("uniform", "transpose", "bitcomp", "hotspot(0)")
    for traffic in traffic_patterns:
        for metric in ("latency", "throughput"):
            plot_task2(task2, traffic, metric)
            plot_task3(task3, "mesh", traffic, metric)
            plot_task3(task3, "torus", traffic, metric)
    with open(os.path.join(ROOT, "task2", "saturation_summary.tsv"), "w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("topology", "traffic", "saturation_injection", "saturation_throughput", "minimum_latency"))
        writer.writerows(saturation(task2, ("topology", "traffic")))
    with open(os.path.join(ROOT, "task2", "seed_summary.tsv"), "w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("topology", "traffic", "injection_rate", "latency_mean", "latency_stddev", "throughput_mean", "throughput_stddev"))
        for row in task2:
            writer.writerow((row["topology"], row["traffic"], row["injection_rate"],
                             row["latency"], row["latency_stddev"], row["throughput"], row["throughput_stddev"]))
    with open(os.path.join(ROOT, "task3", "saturation_summary.tsv"), "w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("topology", "routing", "traffic", "saturation_injection", "saturation_throughput", "minimum_latency"))
        writer.writerows(saturation(task3, ("topology", "routing", "traffic")))
    with open(os.path.join(ROOT, "task3", "seed_summary.tsv"), "w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("topology", "routing", "traffic", "injection_rate", "latency_mean", "latency_stddev", "throughput_mean", "throughput_stddev"))
        for row in task3:
            writer.writerow((row["topology"], row["routing"], row["traffic"], row["injection_rate"],
                             row["latency"], row["latency_stddev"], row["throughput"], row["throughput_stddev"]))
    print(f"Task 2 valid rows: {len(task2)}")
    print(f"Task 3 valid rows: {len(task3)}")


if __name__ == "__main__":
    main()
