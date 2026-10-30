#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOKSIM="$ROOT/src/booksim"
RAW="$ROOT/results/raw"
DATA="$ROOT/results/adaptive_results.tsv"

mkdir -p "$RAW"
printf 'routing\tsize\tvcs\ttraffic\tinjection_rate\tlatency\tthroughput\tstatus\n' > "$DATA"

for routing in dor adaptive_xy_yx; do
  for size in 4 8; do
    for traffic in uniform transpose bitcomp hotspot\(0\); do
      if [ "$traffic" = "hotspot(0)" ]; then
        rates="0.005 0.010 0.015 0.020 0.025 0.030 0.035 0.040 0.045 0.050 0.055 0.060 0.070 0.080 0.100"
      else
        rates="0.02 0.05 0.10 0.15 0.20 0.30 0.35 0.40 0.50 0.60 0.70 0.80 0.90"
      fi
      for rate in $rates; do
        tag="adaptive_${routing}_${size}x${size}_vc4_${traffic//[()]/}_${rate//./p}"
        log="$RAW/${tag}.log"
        "$BOOKSIM" "$ROOT/configs/matched/mesh_dor_4x4_vc4.conf" \
          topology=mesh k="$size" n=2 routing_function="$routing" num_vcs=4 \
          traffic="$traffic" injection_rate="$rate" packet_size=1 \
          sample_period=1000 warmup_periods=3 sim_count=1 \
          alloc_iters=1 wait_for_tail_credit=0 > "$log" 2>&1
        status=$?
        python3 "$ROOT/results/parse_results.py" "$log" "$routing" \
          "${size}x${size}" 4 "$traffic" "$rate" "$status" >> "$DATA"
      done
    done
  done
done
