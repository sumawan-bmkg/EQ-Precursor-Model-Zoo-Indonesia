# AZ8Rb + AZ8Rc + AZ13 — Consensus Dynamics Validation

**Date:** 2026-06-02
**Data:** Real V9.5 HDF5 inference, 66 M5+ events, 958 obs.

## Overall Verdict

```
AZ8Rb = MARGINALLY_SIGNIFICANT
AZ8Rc = CONFIRMED_95CI
AZ13  = CIRCULAR_VARIANCE
OVERALL = CONSENSUS_DYNAMICS_CONFIRMED
```

## AZ8Rb: Binomial Consistency Test

- **42/65 events** (65%) show positive per-event rho
- Exact binomial p = **1.24e-02**  (H0: P=0.5, H1: P>0.5)
- Cohen h = 0.2966
- Wilcoxon p = 0.0004

## AZ8Rc: Hierarchical Bootstrap

- Mean per-event rho = **+0.1216**
- 95% CI = [+0.0516, +0.1906]  excl. 0: **True**
- 99% CI = [+0.0297, +0.2114]
- P(mean > 0) = **0.9993**
- t-test p = 0.0006

## AZ13: Mechanism

- Pairwise spread rho = +0.3286
- Circular variance rho = +0.1076
- Window delta R = +0.00153
- Window t-test p = **0.0000**
- Dominant mechanism: **CIRCULAR_VARIANCE**

## Scientific Statement

42/65 M5+ events (65%) showed positive per-event
Spearman correlation between days-before-earthquake and negative consensus R
(binomial p=1.24e-02). Hierarchical bootstrap (resampling events, preserving
temporal structure, n=10000) yielded mean per-event rho=+0.1216
(95% CI [+0.0516,+0.1906]; p(>0)=0.9993).
The near-earthquake temporal window (T0–T3 days) showed higher consensus
than the far window (T11–T14 days; t-test p=0.0000), suggesting a
genuine but small spatio-temporal precursor signal in directional consensus.
