# Changelog v0.4.0-dev4 (2026-10-29)

Acceptance rules (`LABORATORY_VALIDATION_PROTOCOL_v1.0_FROZEN.md`, `configs/acceptance_criteria.yaml`) are
unchanged and their SHA-256 in `PROTOCOL_FREEZE.json` still verifies. The freeze record names software
0.4.0-dev3; running the formal matrix with dev4 requires the protocol owner to confirm the software change
below (no formal run had been executed).

## Execution blockers removed
1. **Vectorized q=2/q=3 assembly** (`scientific/simulators.py`). The dev3 loops needed ~20 s per path at
   J=12 with elar=12 (minutes per path at J=18); dev4 needs 0.1–0.6 s per path at J=18. For
   `simulator_variant: legacy` the output is bit-identical to the dev3 loops
   (`simulators_reference_loops.py`, test `test_vectorized_legacy_is_bit_identical_to_dev3_loops`).
2. **elar derived as in the supplied source.** `main.py` and eq. (87) use elar = floor(2^(epsilon J)),
   i.e. elar = 1 for epsilon = 0.001; dev3 configs hard-coded elar = 12 (q=2/q=3 never ran, so no
   result is affected). `elar: auto` is now the default; an explicit integer still overrides it.
3. **PyWavelets fallback.** If `pywt` is missing, the closed-form Meyer transform is used on the dmey
   frequency spacing. The backend is written to every `environment.json`; q>1 cells computed with it are
   forced to `PREVIEW_NOT_FORMAL`.

## Simulator variants
- `legacy` (default for the published benchmark): audited source behaviour.
- `corrected`: removes `f = f - mean(f)` and replaces `path / stdev(diff(path))` with the exact
  deterministic constant giving Var Z(1) = 1 (`scientific/normalization.py`).

Diagnostic evidence (D-01..D-05, `validation/distribution.py`):
- legacy q=1: Var Z(1) ~ 0 (bridge);
- legacy q=2: E Z(1) ~ -0.9 (drift);
- legacy q=3: Var Z(1) ~ 0.03.
The corrected variant passes 43 of 45 checks for H in {0.7, 0.8, 0.9} at J=12 with 1,000 paths
(analytic Meyer). q=1 passes all checks. The two isolated misses (q=2 D-05 at H=0.7 and q=3 D-02 at
H=0.7) are borderline under heavy tails. At H = 0.6 and q >= 2 a fine-scale discretisation bias remains
in D-04.

## Published benchmark (preview, analytic Meyer, 100 replications, J=18, N=17)
The legacy variant reproduces the published q=1 values (e.g. identity, gamma=0.8, H=0.6: 0.2950 vs 0.295
published), which indicates that Tables 1-5 were produced with the legacy simulator. The corrected variant
gives q=1 means closer to the theoretical target 1/3 (0.315-0.334) and therefore does not match the
published values. q=2 legacy cells did not match with the analytic Meyer backend; they must be rerun with
PyWavelets before any conclusion.

## Other
- `app.py`: Romanian interface with 4 modes, variant selector, downloads, environment banner.
- `scripts/run_published_matrix.py`, `scripts/run_distribution_diagnostics.py`.
- `hermes_lab/environment.py`: version, library versions and Meyer backend in every result folder.
- Tests: 24 passing (12 dev3 + 12 dev4).
