#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BOOKSIM="$ROOT/src/booksim"
OUT="$ROOT/results/task2"
mkdir -p "$OUT/raw"
printf 'topology\tsize\tvcs\ttraffic\tinjection_rate\tlatency\tthroughput\tseed\tstatus\n' > "$OUT/task2_results.tsv"
seeds="1 2 3"
for topology in mesh hybrid; do
  for traffic in uniform transpose bitcomp hotspot\(0\); do
    if [ "$traffic" = "hotspot(0)" ]; then
      rates="0.005 0.010 0.015 0.020 0.025 0.030 0.035 0.040 0.045 0.050 0.055 0.060 0.070 0.080 0.100"
    else
      rates="0.02 0.05 0.10 0.15 0.20 0.30 0.35 0.40 0.50 0.60 0.70 0.80 0.90"
    fi
    for rate in $rates; do
      for seed in $seeds; do
      if [ "$topology" = mesh ]; then
        config="$ROOT/configs/task2/mesh_4x4_comparison.conf"
        tag="mesh"
      else
        config="$ROOT/configs/task2/hybrid_anynet_4x4.conf"
        tag="hybrid"
      fi
      log="$OUT/raw/${tag}_${traffic//[()]/}_${rate//./p}_seed${seed}.log"
        timeout "${SIM_TIMEOUT_SECONDS:-30}" "$BOOKSIM" "$config" \
          traffic="$traffic" injection_rate="$rate" seed="$seed" > "$log" 2>&1
        status=$?
        python3 "$ROOT/results/parse_results.py" "$log" "$topology" 4x4 4 \
          "$traffic" "$rate" "$status" "$seed" >> "$OUT/task2_results.tsv"
      done
    done
  done
done
