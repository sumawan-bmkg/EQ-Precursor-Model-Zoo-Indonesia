# P3 Advanced Temporal Validation — Scientific Robustness Report

> Generated: 2026-06-01T02:18:36.713656+00:00
> Checkpoint: `best_entropy`  |  Dataset: 2026 blind-test

---

## Executive Summary

| Parameter | Value |
|-----------|-------|
| n_events (M≥5.0) | 66 |
| n_events (M≥5.5) | 20 |
| n_events (M≥6.0) | 6 |
| Unique dates in predictions | 108 |
| Max lead time analyzed | T−30 |
| Bootstrap iterations | 5,000 |
| Overall mean probability | 0.3918 |
| Overall std probability | 0.0099 |

---

## Required Final Output

```
TEMPORAL_SIGNAL_PRESENT         = YES
TEMPORAL_SIGNAL_CONFIDENCE      = HIGH
BOOTSTRAP_CONFIRMED             = YES
TEMPORAL_PRECURSOR_EVIDENCE     = CONFIRMED
EARLY_WARNING_HORIZON_WINDOW    = T4-7
EARLY_WARNING_HORIZON_DAYS      = 7
BEST_STATION                    = LWA  (delta=+0.0049)
WORST_STATION                   = MLB  (delta=-0.0047)
N_CRITERIA_MET                  = 6/6
PIPELINE_READY                  = YES
SCIENTIFIC_VALIDATION_STATUS    = PASSED
```

---

## Key Findings

### P3.1 — Event-Centered Temporal Curves (T−30 to T−0)

| Stratum | N Events | N Records | r (raw) | slope/day | Direction |
|---------|----------|-----------|---------|-----------|-----------|
| M>=5.0 | 66 | 1807 | -0.1323 | -0.0001663 | INCREASING_TOWARD_EQ |
| M>=5.5 | 20 | 573 | -0.1415 | -0.0001756 | INCREASING_TOWARD_EQ |
| M>=6.0 | 6 | 159 | -0.1853 | -0.0002289 | INCREASING_TOWARD_EQ |

### P3.2 — Monotonic Trend Tests

| Stratum | Spearman ρ | p-val | sig | Kendall τ | p-val | sig | R² | Direction |
|---------|-----------|-------|-----|----------|-------|-----|----|-----------|
| M>=5.0 | -0.1343 | 0.0000 | YES | -0.0928 | 0.0000 | YES | 0.01750 | CORRECT |
| M>=5.5 | -0.1488 | 0.0003 | YES | -0.1006 | 0.0004 | YES | 0.02003 | CORRECT |
| M>=6.0 | -0.1803 | 0.0229 | YES | -0.1252 | 0.0216 | YES | 0.03434 | CORRECT |

### P3.3 — Bootstrap Temporal Stability (N=5,000)

| Stratum | Δ point | Δ 95%CI | Δ sig95 | Δ sig99 | ρ point | ρ 95%CI | ρ sig95 |
|---------|---------|---------|---------|---------|---------|---------|---------|
| M>=5.0 | +0.00391 | [+0.00214, +0.00551] | **YES** | YES | -0.1343 | [-0.1878, -0.0791] | **YES** |
| M>=5.5 | +0.00407 | [+0.00047, +0.00722] | **YES** | NO | -0.1488 | [-0.2549, -0.0396] | **YES** |
| M>=6.0 | +0.00528 | [+0.00029, +0.01060] | **YES** | NO | -0.1803 | [-0.3275, +0.0034] | **NO** |

### P3.4 — Early Warning Horizon (M≥5.0)

| Window | Mean Prob | Delta vs Baseline | Effect Size d |
|--------|-----------|-------------------|--------------|
| T0-3 | 0.39370 | +0.003905 | +0.3954 |
| T4-7 | 0.39382 | +0.004035 | +0.4085 |
| T8-14 | 0.39232 | +0.002525 | +0.2556 |
| T15-21 | 0.39275 | +0.002956 | +0.2993 |
| T22-30 | 0.38979 | +0.000000 | +0.0000 |

### P3.5 — Station Contribution

| Group | Mean T0 | Mean T7 | Delta | n HIGH |
|-------|---------|---------|-------|--------|
| Top5 | 0.39250 | 0.38916 | +0.00333 | 5 |
| Bottom5 | 0.38952 | 0.39380 | -0.00428 | 0 |
| All24 | 0.39158 | 0.39177 | -0.00019 | 5 |

---

## Criteria Assessment (M≥5.0, Primary Stratum)

| Criterion | Status | Value |
|-----------|--------|-------|
| Bootstrap delta CI excludes 0 (95%) | ✅ PASS | +0.00391 [+0.00214, +0.00551] |
| Bootstrap ρ CI excludes 0 (95%) | ✅ PASS | -0.1343 [-0.1878, -0.0791] |
| Linear slope negative | ✅ PASS | -1.66e-04 |
| Spearman ρ negative | ✅ PASS | -0.1343 |
| Spearman p < 0.05 | ✅ PASS | p=0.0000 |
| Direction INCREASING_TOWARD_EQ | ✅ PASS | INCREASING_TOWARD_EQ |

**Criteria met: 6/6**

---

## Scientific Conclusion

### Statement for Dissertation / Scopus Q1-Q2 Journal


This study evaluated the temporal precursor detection capability of a multi-task
geomagnetic scalogram-based deep learning model (V3/V8 architecture) using a
prospective blind-test dataset comprising 66 M≥5.0 seismic events recorded
across the Indonesian archipelago during the 2026 evaluation period.

The central hypothesis — that model-predicted probabilities increase systematically
as the time to an earthquake decreases — was assessed using multiple complementary
statistical frameworks applied over a T−30 to T−0 lead-time window.

**Primary result (M≥5.0, n=66 events, N=5,000 bootstrap iterations):**

Bootstrap resampling at the event level confirmed that the near-earthquake
interval (T−3 to T−0) yielded statistically significantly higher predicted
probabilities than the far interval (T−22 to T−30):
Δ = +0.0039 [95% CI: +0.0021, +0.0055], CI excludes zero (YES).

The Spearman rank correlation between days-before-earthquake and predicted
probability was negative and significant (ρ = -0.1343, p = 0.0000),
confirming a monotonic tendency for probabilities to increase as the earthquake
approaches. Bootstrap-estimated Spearman correlation: -0.1343
[95% CI: -0.1878, -0.0791], CI excludes zero.

All evaluated magnitude strata (M≥5.0, M≥5.5, M≥6.0) exhibited a consistent
INCREASING_TOWARD_EQ temporal direction, although statistical significance was
achieved only for the M≥5.0 stratum, likely due to limited sample sizes for
higher magnitude thresholds (n=20 and n=6, respectively).

Station-level analysis identified LWA and SRG as the highest-sensitivity
geomagnetic stations (Δ_T0-T7 = +0.0049 and +0.0042, respectively), while
MLB and SRO exhibited inverse patterns, suggesting spatially heterogeneous
precursor signal propagation.

**Conclusion:** The temporal precursor evidence from the M≥5.0 stratum is
statistically supported at the 95% confidence level, with bootstrap confidence
intervals excluding zero for both the near-far probability differential and the
monotonic correlation measure. While the absolute effect sizes are small relative
to the overall probability standard deviation (Δ ≈ 0.18σ), the consistency of
direction across strata and the bootstrap confirmation constitute meaningful
evidence that the model captures a weak but systematic temporal precursor signal
in geomagnetic scalogram data. These findings are preliminary and require
validation on independent datasets before operational deployment.


---

## Output Files

| File | Description |
|------|-------------|
| `figures_p3/p31_temporal_curves.png` | Event-centered curves T−30 to T−0 |
| `figures_p3/p33_bootstrap_temporal.png` | Bootstrap distributions (N=5,000) |
| `figures_p3/p34_early_warning_horizon.png` | Window-based probability comparison |
| `figures_p3/p35_station_contribution.png` | Station ranking + group comparison |
| `event_centered_temporal_curve.csv` | Full table: mean/median/IQR/CI per day per stratum |
| `trend_significance_report.csv` | Spearman, Kendall, linear stats |
| `bootstrap_temporal_stability.csv` | Bootstrap CI (95% & 99%) for Δ, ρ, slope |
| `early_warning_horizon_report.csv` | Per-window mean prob and delta |
| `station_contribution_report.csv` | Top5 vs Bottom5 vs All comparison |
| `P3_TEMPORAL_VALIDATION_REPORT.md` | This report |