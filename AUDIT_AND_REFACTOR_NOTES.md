# Audit and refactor notes – v0.4.0-dev1

## P0 fixed in refactored branch
1. GPH sign/scaling: coefficient on `-2*log(2*sin(w/2))` is used directly as d.
2. Reproducibility: every validation replication receives a spawned NumPy Generator.
3. Generalized order-2 index misuse is guarded: sigma2 requires exactly 2 indices.
4. Baseline no longer imports R/rpy2.

## P0 staged but not scientifically accepted
1. Legacy `scipy.integrate.simps` in generalized integrals must become `simpson`.
2. Generalized processes require a construction with common Gaussian driving noise across FARIMA sequences with different d. Existing source generates them independently. This must be resolved against the mathematical construction before GHP can enter the frozen TRL4 evidence set.

## P1 remaining
- Install/lock PyWavelets to execute q=2/q=3 standard simulations.
- Add integrated-volatility runner reproducing Tables 1–5.
- Define ex-ante scientific acceptance thresholds.
- Run full published benchmark matrix and independent reproduction.

## dev2 finding – integrated-volatility endpoint
The supplied `maketableofstochint()` evaluates the final special increment at `1 + 2^-N`, while the original driver simulates only to `T=1`. The refactored validation runner does not extrapolate or suppress this mismatch: it simulates through `1 + 2^-N + 2^-J`, adding the single interpolation grid step required to evaluate the endpoint without extrapolation. This preserves the published estimator grid while making the numerical experiment well-defined and auditable.
