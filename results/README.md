# NoC project experiments and reproducibility

This directory contains the BookSim 2 experiment configurations, parsers, compact result tables, and report-ready discussion for the CS376 NoC project.

## Team

- Arhan Ghosarwade — 24BCS020
- Veeresh Bellerimath — 24BEC065
- C Sathwik — 24BEC008

## Project components

1. **Design-space exploration (Task 1):** Mesh and Torus at 4x4, 6x6, and 8x8; 1, 2, 4, and 8 VCs; Uniform, Transpose, Bit Complement, and Hotspot(0) traffic; extended offered injection rates.
2. **Hybrid topology (Task 2):** a 4x4 Torus graph with ten added express links, modelled with AnyNet and checked by the graph validator.
3. **History-Aware Congestion Routing (Task 3):** topology-specific Mesh and Torus routing functions compared against dimension-order baselines.

## Regenerating results

Run from the BookSim repository root after building `src/booksim`:

```bash
bash results/run_experiments.sh
bash results/run_adaptive.sh
bash scripts/task2_task3/run_task2_sweep.sh
bash scripts/task2_task3/run_task3_sweep.sh
python3 results/parse_results.py
python3 results/task2_task3_analyze.py
```

The scripts expose environment variables for run-time limits and seed selection; inspect each script before changing the experiment matrix. The Task 2 and Task 3 default seed set is 1, 2, and 3.

## Compact datasets

- `booksim_results.tsv`: Task 1 design-space runs.
- `summary.tsv`: Task 1 operational saturation summary.
- `task2/task2_results.tsv`: per-seed Task 2 results.
- `task2/seed_summary.tsv`: Task 2 means and standard deviations across valid seeds.
- `task2/saturation_summary.tsv`: Task 2 operational saturation summary.
- `task3/task3_results.tsv`: per-seed Task 3 results.
- `task3/seed_summary.tsv`: Task 3 means and standard deviations across valid seeds.
- `task3/saturation_summary.tsv`: Task 3 operational saturation summary.

Rows marked invalid are retained in the per-run tables for audit but must not be treated as steady-state performance observations. Saturation summaries are sampled operational estimates, not exact continuous saturation points.

## Latest archived run accounting

The accompanying archived result tables contain:
- Task 1: 1,152 attempted rows, covering two topologies, three sizes, four VC counts, four traffic patterns, and twelve injection-rate samples.
- Task 2: 324 attempted rows, with three seeds.
- Task 3: 648 attempted rows, with three seeds.

Use the status column and seed-summary files to determine which data points contribute to each graph and aggregate. Do not infer that every attempted run is valid.

## Raw logs and generated artifacts

Per-run raw logs and generated graph images are intentionally not included in this focused source PR to avoid committing thousands of large artifacts. Regenerate them with the commands above. Keep the raw logs with the experiment archive when submitting or auditing the final report.

## Implementation notes

- Task 2's Hybrid graph contains 16 routers and 42 unique undirected links (the 32 Torus links plus ten express links). The graph validator reports connectivity, degree range, diameter, and mean shortest-path distance.
- HACR uses current output-port occupancy and an exponentially smoothed historical estimate. The parameters `hacr_alpha` and `hacr_lambda` are configured in the matched examples.
- Finite smoke tests and experiment sweeps are evidence of execution, not a formal deadlock-freedom proof. Interpret HACR results across the entire valid latency/throughput curves; it is not expected to outperform DOR on every traffic pattern.
