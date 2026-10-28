# HERMES Hermite Laboratory Core v0.4 — Laboratory Validation Protocol

Protocol ID: **HERMES-TRL4-LVP-1.0**  
Status: **FROZEN BEFORE FORMAL VALIDATION RUN**  
Software development baseline: **v0.4.0-dev3**

## 1. Purpose and TRL claim boundary

This protocol defines the evidence required to support a TRL 4 claim for the **standard Hermite simulation/inference laboratory core** that will form the scientific baseline of the future Non-Gaussian Self-Similar Engine. The object validated here is not HERMES-AI Core, HERMES-RISK Professional, the AI Model Orchestrator, or an operational platform.

The frozen baseline contains standard Hermite-process functionality for orders q=1,2,3 and a complete inference path through the integrated-volatility estimator. The generalized Hermite/GHP branch is explicitly excluded from this TRL 4 release until its shared-driving-noise construction and numerical implementation are separately validated.

## 2. Scientific benchmark

The primary benchmark is the supplied article, Tables 1–5. The formal reproduction matrix uses:

- J = 18;
- N = 17;
- H ∈ {0.6, 0.7, 0.8, 0.9};
- Hermite orders q ∈ {1,2,3};
- 100 independent trajectories per cell;
- a = 0.99;
- epsilon = 0.001;
- p = 2;
- identity h(s)=s at gamma = 0.80 and gamma = 0.95;
- cubic h(s)=s^3 at gamma = 0.95;
- exponential h(s)=exp(s) at gamma = 0.95;
- square-root h(s)=sqrt(s) at gamma = 0.95.

This gives **5 experiment families × 4 H values × 3 Hermite orders = 60 cells**.

The theoretical integrated-volatility targets are recorded separately from the finite-sample published Monte Carlo values. They are used as scientific context, not substituted for the published benchmark.

## 3. Freeze rule

The acceptance rules in this document and `configs/acceptance_criteria.yaml` are fixed before the formal 100-replication matrix is executed. They must not be changed after inspecting formal validation outcomes. Any later change requires a new protocol version and a new full formal validation run.

## 4. Engineering release gates

All of the following must PASS:

1. **Source chain of custody.** Original supplied source files are retained unmodified and their SHA-256 manifest verifies.
2. **Environment traceability.** Python and all dependency versions used by the formal run are recorded; the formal environment is version locked.
3. **Same-seed reproducibility.** Repeating the same configuration with the same seed in the same locked environment produces identical numerical outputs for the evidence-bearing result files.
4. **Configuration validation.** Invalid process/parameter combinations are rejected before execution.
5. **No silent extrapolation.** Every estimator evaluation point lies inside the simulated horizon. The implementation explicitly extends the simulation horizon to cover the final special increment and interpolation grid point.
6. **Evidence completeness.** Every completed cell produces configuration, environment, replication-level output, aggregate metrics and execution log.
7. **Failure transparency.** Failed or blocked cells are recorded and are never silently removed from the matrix.
8. **Automated software tests.** The complete frozen test suite passes in the formal environment.
9. **Baseline boundary.** No generalized Hermite/GHP result is presented as part of this TRL 4 release.

Failure of any engineering gate prevents a TRL 4 evidence release irrespective of the numerical results.

## 5. Mean-compatibility criterion

The article reports the Monte Carlo mean and sample standard deviation from 100 trajectories for every cell. The formal validation generates an independent set of 100 trajectories.

For cell i, let:

- m_i = mean from the new formal run;
- s_i = standard deviation from the new formal run;
- n_i = 100;
- m_i,pub = published mean;
- s_i,pub = published standard deviation;
- n_pub = 100.

The standardized mean discrepancy is evaluated using an independent two-sample Welch statistic:

`t_i = (m_i - m_i,pub) / sqrt(s_i^2/n_i + s_i,pub^2/n_pub)`.

Degrees of freedom are calculated by the Welch–Satterthwaite formula. A two-sided p-value is reported.

Because 60 cells are evaluated, family-wise type-I error is controlled at 5% using Bonferroni:

`alpha_cell = 0.05 / 60 = 0.0008333333`.

**PASS(mean)** if `p_mean >= 0.0008333333`.  
**FAIL(mean)** otherwise.

This criterion is described as *statistical compatibility with the published Monte Carlo benchmark*, not as proof that the two underlying distributions are identical.

A formal PASS cannot be issued when fewer than 100 new replications are available.

## 6. Dispersion-compatibility criterion

The sample variance ratio is

`F_i = s_i^2 / s_i,pub^2`.

A two-sided F comparison is calculated with degrees of freedom `(n_i-1, n_pub-1)`. The same Bonferroni-adjusted threshold is used:

**PASS(variance)** if `p_variance >= 0.0008333333`.  
**FAIL(variance)** otherwise.

For n_i=n_pub=100, the corresponding approximate non-rejection interval for the variance ratio is **[0.50676, 1.97333]**, or approximately **[0.71187, 1.40475]** for the standard-deviation ratio.

This test is used because the article establishes asymptotic Gaussian behavior for the normalized integrated-volatility estimator, making a Gaussian variance comparison a defensible laboratory diagnostic. It remains a reproduction criterion, not a claim of exact finite-sample normality.

## 7. Cell-level decision

A formally completed benchmark cell receives:

- **PASS** only if `PASS(mean)` AND `PASS(variance)`;
- **FAIL** if either criterion fails;
- **INCOMPLETE** if n < 100, required evidence is missing, or execution is blocked.

Development and pilot runs can display the statistics but are labelled **PREVIEW / NOT FORMAL** and cannot generate a TRL 4 PASS.

## 8. Pre-registered confirmatory rule

To distinguish a genuine implementation discrepancy from an unusually adverse Monte Carlo draw, exactly one confirmatory mechanism is pre-registered now, before the formal run.

If a 100-replication cell fails either mean or variance compatibility:

1. one independent reserve batch of 100 replications is executed using a predeclared disjoint seed stream;
2. the primary and reserve batches are pooled to n=200;
3. mean and variance compatibility are evaluated once more against the published n=100 benchmark using the same per-cell alpha;
4. the pooled result is final.

No third run or discretionary seed selection is permitted. The initial failure, confirmatory trigger and pooled result remain in the audit trail.

## 9. Matrix-level release decision

The standard Hermite baseline is eligible for a TRL 4 evidence release only if:

- all engineering release gates PASS;
- all 60 cells are executed or, where a pre-registered confirmatory batch is triggered, reach a final decision;
- all 60 cells have final PASS for mean compatibility;
- all 60 cells have final PASS for variance compatibility;
- no cell is blocked, missing or silently excluded;
- a second operator reproduces the frozen execution procedure from the documentation and records the reproduction result.

If these conditions are not met, the package remains a pre-validation/development release and the TRL 4 claim must be narrowed or withheld until the cause is resolved and a new protocol/version is issued where necessary.

## 10. Theoretical targets and finite-resolution bias

For p=2, theoretical targets include:

- identity h(s)=s: integral_0^1 s^2 ds = 1/3;
- cubic h(s)=s^3: integral_0^1 s^6 ds = 1/7;
- exponential h(s)=exp(s): integral_0^1 exp(2s) ds = (e^2-1)/2;
- square-root h(s)=sqrt(s): integral_0^1 s ds = 1/2.

The published finite-resolution Monte Carlo means need not equal these asymptotic targets exactly. Therefore theoretical-target bias is reported for every cell but is not used as a separate release gate; doing so would duplicate the mean-reproduction criterion while incorrectly treating finite-resolution bias as an implementation failure.

## 11. Supporting diagnostics

The following are retained as supporting evidence rather than release gates for this first TRL 4 baseline:

- Hurst-parameter recovery;
- self-similarity/scaling diagnostics;
- stationary-increment diagnostics;
- non-Gaussianity diagnostics for q>1.

They will be reported transparently. If any supporting diagnostic reveals a systematic contradiction with the defining properties of the simulated process, this triggers scientific review and prevents release until resolved, even though the diagnostic is not converted into an arbitrary numerical cut-off.

## 12. Evidence package

The final evidence package must contain at minimum:

- frozen source snapshot and SHA-256 manifest;
- protocol and protocol hash;
- frozen acceptance-criteria file;
- environment lock and environment record;
- 60-cell benchmark plan;
- replication-level results;
- aggregate metrics including means, SDs, theoretical targets and published references;
- cell-level acceptance table with test statistics and p-values;
- matrix-level PASS/FAIL report;
- automated-test results;
- execution logs;
- second-operator reproduction record;
- technical note describing any deviations from the article implementation.

## 13. TRL boundary after successful validation

A successful release supports the statement that the **standard Hermite simulation/inference laboratory core has been validated under controlled laboratory conditions**. It does not establish TRL 4 for HERMES-AI as an integrated platform and does not establish TRL 4 for the generalized Hermite/GHP branch unless that branch is validated separately under an additional frozen protocol.
