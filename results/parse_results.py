#!/usr/bin/env python3
import re
import sys


def last_float(pattern: str, text: str):
    values = re.findall(pattern, text, re.MULTILINE)
    return values[-1] if values else "NA"


def main() -> int:
    if len(sys.argv) not in (8, 9):
        raise SystemExit(
            "usage: parse_results.py LOG TOPOLOGY SIZE VCS TRAFFIC RATE STATUS [SEED]"
        )
    log, topology, size, vcs, traffic, rate, status = sys.argv[1:8]
    seed = sys.argv[8] if len(sys.argv) == 9 else None
    text = open(log, encoding="utf-8", errors="replace").read()
    latency = last_float(r"Packet latency average = ([0-9.eE+-]+)", text)
    throughput = last_float(r"Accepted packet rate average\s*=\s*([0-9.eE+-]+)", text)
    invalid = (
        status != "0"
        or latency == "NA"
        or throughput == "NA"
        or re.search(
            r"assert|Assertion|invalid routing|deadlock|unstable|timeout|"
            r"incomplete|too many sample periods|average latency for class .* exceeded",
            text,
            re.IGNORECASE,
        )
    )
    fields = (topology, size, vcs, traffic, rate, latency, throughput)
    if seed is not None:
        fields += (seed,)
    print("\t".join(fields + ("1" if invalid else "0",)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
