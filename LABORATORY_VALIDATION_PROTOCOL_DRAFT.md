# HERMES Hermite/GHP Laboratory Validation Protocol – DRAFT

Version: 0.4.0-dev2  
Status: PRE-VALIDATION – acceptance thresholds not yet frozen

## 1. Purpose
This protocol defines the laboratory evidence required before declaring the frozen Hermite baseline as TRL 4. It does not validate HERMES-AI Core, HERMES-RISK Professional, or the generalized Hermite/GHP branch.

## 2. Frozen object to be validated
The initial evidence object is the standard Hermite simulation/inference laboratory core for orders q=1,2,3. GHP remains experimental until its shared-driving-noise construction is independently resolved and validated.

## 3. Source benchmark
The primary scientific benchmark is the supplied article's Tables 1–5: J=18, N=17, H in {0.6,0.7,0.8,0.9}, q in {1,2,3}, 100 trajectories per cell, a=0.99, epsilon=0.001, with identity at gamma 0.80 and 0.95, then cubic, exponential and square-root functions at gamma 0.95.

## 4. Mandatory engineering acceptance criteria
These criteria are binary and will be frozen before the formal run:
1. Source chain of custody: original files and SHA-256 manifest present.
2. Environment reproducibility: Python and all package versions recorded.
3. Same-seed reproducibility: identical configuration and seed reproduce the same numerical output.
4. Configuration validation: invalid process/parameter combinations are rejected before execution.
5. No silent extrapolation: every estimator evaluation point is inside the simulated horizon.
6. Output completeness: configuration, environment, replication metrics, aggregate metrics and execution log are generated for every completed cell.
7. Blocked/failed runs are recorded and never silently omitted.

## 5. Scientific reproduction criteria – proposed statistical form
The final thresholds are not yet approved. To avoid arbitrary percentage tolerances, the preferred approach is statistical reproduction of the published Monte Carlo results. For each published cell:
- mean agreement will be assessed from the difference between the independent replication mean and published mean, scaled by their Monte Carlo standard errors;
- dispersion agreement will compare the independent and published variances using a pre-specified variance-ratio criterion;
- theoretical targets are reported separately and are not substituted for published finite-sample benchmarks.

The exact significance/equivalence thresholds must be approved and frozen before the 100-replication validation matrix is executed.

## 6. Additional scientific diagnostics
Separate controlled experiments will document Hurst-parameter recovery, scaling/self-similarity diagnostics, stationary-increment diagnostics and non-Gaussian behavior for q>1. These diagnostics are supporting evidence; their criteria will be frozen before the formal validation run.

## 7. Published benchmark matrix
The matrix contains 60 cells (5 experiment families × 4 H values × 3 Hermite orders). `configs/published_matrix_plan.csv` records every cell and its execution readiness. q=1 is executable in the current environment. q=2/q=3 require the version-locked PyWavelets dependency used by the supplied simulation code.

## 8. Formal evidence release
Only after the protocol and thresholds are frozen, dependencies are locked, all mandatory cells are executed and a second operator independently reproduces the run will the package be eligible to become a frozen TRL4 evidence release.
