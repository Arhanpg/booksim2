#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BOOKSIM="$ROOT/src/booksim"
OUT="$ROOT/results/task3"
mkdir -p "$OUT/raw"
printf 'topology\trouting\tvcs\ttraffic\tinjection_rate\tlatency\tthroughput\tseed\tstatus\n' > "$OUT/task3_results.tsv"
seeds="1 2 3"
for topology in mesh torus; do
  for routing in baseline hacr; do
    for traffic in uniform transpose bitcomp hotspot\(0\); do
      if [ "$traffic" = "hotspot(0)" ]; then
        rates="0.005 0.010 0.015 0.020 0.025 0.030 0.035 0.040 0.045 0.050 0.055 0.060 0.070 0.080 0.100"
      else
        rates="0.02 0.05 0.10 0.15 0.20 0.30 0.35 0.40 0.50 0.60 0.70 0.80 0.90"
      fi
      for rate in $rates; do
        for seed in $seeds; do
        if [ "$topology" = mesh ] && [ "$routing" = baseline ]; then
          config="$ROOT/configs/task3/mesh_dor_4x4_vc4.conf"
          route_name=dor
        elif [ "$topology" = mesh ]; then
          config="$ROOT/configs/task3/hacr_mesh_4x4_vc4.conf"
          route_name=hacr_min_adapt
        elif [ "$routing" = baseline ]; then
          config="$ROOT/configs/task3/torus_dim_order_4x4_vc4.conf"
          route_name=dim_order
        else
          config="$ROOT/configs/task3/hacr_torus_4x4_vc4.conf"
          route_name=hacr_min_adapt
        fi
        log="$OUT/raw/${topology}_${routing}_${traffic//[()]/}_${rate//./p}_seed${seed}.log"
          timeout "${SIM_TIMEOUT_SECONDS:-30}" "$BOOKSIM" "$config" \
            traffic="$traffic" injection_rate="$rate" seed="$seed" > "$log" 2>&1
          status=$?
          python3 "$ROOT/results/parse_results.py" "$log" "$topology" "$route_name" 4 \
            "$traffic" "$rate" "$status" "$seed" >> "$OUT/task3_results.tsv"
        done
      done
    done
  done
done
