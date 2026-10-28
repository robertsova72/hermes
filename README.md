# HERMES Hermite/GHP Laboratory Validation Environment v0.4

Current version: **0.4.0-dev4 (pre-validation)** – see `CHANGELOG_dev4.md`; ghid în română: `CUM_RULEZ.md`. This is not yet a frozen TRL4 evidence release.

## Purpose
Refactor the supplied research code into an auditable laboratory validation environment for the standard Hermite simulation/inference baseline. The environment deliberately stops before HERMES-AI Core, AI Model Orchestrator and HERMES-RISK.

## Implemented
- immutable snapshot of supplied source + SHA-256 manifest;
- deterministic RNG spawning;
- standard q=1/q=2/q=3 simulator interfaces;
- corrected GPH estimator;
- Hurst-recovery runner;
- integrated-volatility runner;
- automated 60-cell published benchmark plan;
- theoretical targets kept separate from published Monte Carlo reference values;
- configuration/environment/results evidence files;
- optional Streamlit UI;
- automated tests.

## Current execution status
q=1/fBm runs end-to-end. q=2/q=3 require PyWavelets, which is declared in `requirements.txt` but unavailable in the current sandbox. GHP remains excluded from TRL4 acceptance pending scientific validation of the generalized construction.

## Key files
- `LABORATORY_VALIDATION_PROTOCOL_DRAFT.md` – draft validation protocol.
- `configs/published_matrix_plan.csv` – all 60 published benchmark cells.
- `configs/published_matrix_frozen_template.yaml` – formal-run template.
- `PREVALIDATION_STATUS.md` – remaining work before freeze.
- `AUDIT_AND_REFACTOR_NOTES.md` – audit trail.

## Run
After installing dependencies from `requirements.txt`:

```bash
PYTHONPATH=. python scripts/run_integrated_smoke.py
PYTHONPATH=. python scripts/run_published_matrix_dev.py
```

The final 100-replication benchmark must only be executed after the acceptance protocol is approved and frozen.

## Frozen validation protocol (dev3)

The TRL4 laboratory acceptance rules are frozen in `LABORATORY_VALIDATION_PROTOCOL_v1.0_FROZEN.md` and `configs/acceptance_criteria.yaml`. Development runs with fewer than 100 replications are automatically labelled `PREVIEW_NOT_FORMAL` and cannot generate a formal PASS.

## dev4 quick start

```bash
pip install -r requirements.txt
python scripts/check_environment.py          # meyer_backend must be pywt-dmey-level10 for formal runs
python -m pytest -q
streamlit run app.py                          # 4 modes: diagnostics, single cell, published matrix, Hurst
python scripts/run_published_matrix.py --variant legacy
python scripts/run_distribution_diagnostics.py --variant corrected
```
