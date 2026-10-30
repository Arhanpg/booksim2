#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOKSIM="$ROOT/src/booksim"
RAW="$ROOT/results/raw"
DATA="$ROOT/results/booksim_results.tsv"

mkdir -p "$RAW"
printf 'topology\tsize\tvcs\ttraffic\tinjection_rate\tlatency\tthroughput\tstatus\n' > "$DATA"

for topology in mesh torus; do
  if [ "$topology" = "mesh" ]; then
    routing="dor"
    config="$ROOT/configs/matched/mesh_dor_4x4_vc4.conf"
  else
    routing="dim_order"
    config="$ROOT/configs/matched/torus_dim_order_4x4_vc4.conf"
  fi

  for size in 4 6 8; do
    for vcs in 1 2 4 8; do
      for traffic in uniform transpose bitcomp hotspot\(0\); do
        for rate in 0.02 0.05 0.10 0.15 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.90; do
          tag="${topology}_${size}x${size}_vc${vcs}_${traffic//[()]/}_${rate//./p}"
          log="$RAW/${tag}.log"
          if [ "$topology" = torus ] && [ "$vcs" = 1 ]; then
            printf '%s\t%s\t%s\t%s\t%s\tNA\tNA\t1\n' \
              "$topology" "${size}x${size}" "$vcs" "$traffic" "$rate" >> "$DATA"
            continue
          fi
          "$BOOKSIM" "$config" \
              topology="$topology" k="$size" n=2 routing_function="$routing" \
              num_vcs="$vcs" traffic="$traffic" injection_rate="$rate" \
              packet_size=1 sample_period=1000 warmup_periods=3 sim_count=1 \
              alloc_iters=1 wait_for_tail_credit=0 \
              > "$log" 2>&1
          status=$?
          python3 "$ROOT/results/parse_results.py" "$log" "$topology" \
              "${size}x${size}" "$vcs" "$traffic" "$rate" "$status" >> "$DATA"
        done
      done
    done
  done
done

printf 'Wrote %s\n' "$DATA"
