# Evaluation Protocol — V8 Geomagnetic Precursor Model

**Version:** 1.0.0 (FROZEN)
**Date:** 2026-06-01
**Purpose:** Pre-registered evaluation protocol for independent replication

---

## Overview

This document specifies the exact evaluation methodology used in the 2026 blind test analysis. This protocol is FROZEN and must not be modified for 2027 replication.

---

## P2: Lead-Time Analysis

### Objective
Determine whether predicted probabilities show temporal patterns relative to earthquake occurrence.

### Methodology
1. **Data Preparation**
   - Extract events with valid `days_before` attribute
   - Define near interval: T-3 to T0 days
   - Define far interval: T-14 to T-11 days

2. **Statistical Analysis**
   - Compute Pearson correlation between `days_before` and `predicted_probability`
   - Compute Spearman correlation (robust to non-linearity)
   - Test significance with permutation test (n=10000)

3. **Expected Finding**
   - Negative correlation indicates probability increases toward earthquake
   - ρ < 0 is the signature of precursor signal

### Primary Metric
- **Spearman correlation coefficient (ρ)** between days_before and probability

### Success Criterion
- ρ < 0 (negative)
- p-value < 0.05

---

## P3: Temporal Validation

### Objective
Validate temporal precursor signal with bootstrap uncertainty quantification.

### Methodology
1. **Bootstrap Resampling**
   - Resample events with replacement (n=10000 iterations)
   - Compute Spearman ρ for each bootstrap sample

2. **Confidence Interval**
   - Use percentile method (2.5th, 97.5th percentiles)
   - 95% CI should exclude 0 for significance

3. **Direction Test**
   - Proportion of bootstrap samples with ρ < 0
   - Should exceed 97.5% for one-tailed significance

### Primary Metrics
- Spearman ρ (point estimate)
- Bootstrap 95% CI
- Proportion of samples with correct direction

### Success Criterion
- Bootstrap CI excludes 0
- Direction = INCREASING_TOWARD_EQ (ρ < 0)

---

## S1: Station Heterogeneity Analysis

### Objective
Quantify spatial heterogeneity in station contributions.

### Methodology

#### S1.1: Leave-One-Out Analysis
- For each station, compute network probability with and without that station
- Delta = P(baseline) - P(LOO)
- Positive delta = station contributes positively to precursor signal

#### S1.2: Station Ranking
- Rank stations by delta magnitude
- Compute bootstrap CI for each station's delta

#### S1.2B: Stability Analysis
- Coefficient of Variation (CV = std/mean) per station
- Bootstrap std of station mean probability
- Reliability score

#### S1.3: Polarity Audit
- Classify stations as POSITIVE, INVERSE, or NEUTRAL
- Based on correlation between days_before and station probability

#### S1.5: Robustness Validation
- Signal Concentration Index
- Network Diversity Score
- Cumulative contribution curve

### Primary Metrics
- Delta per station
- Top 5 / Top 10 contribution percentages
- Signal Concentration Index

### Expected Findings
- Non-uniform station contributions
- Some stations positive, some negative
- Moderate concentration (not flat, not extreme)

---

## S1.7: Statistical Power Analysis

### Objective
Determine whether station-level significance failure is due to insufficient power.

### Methodology
1. **Effect Size Estimation**
   - Cohen's d = delta / pooled_std
   - Compute for each station

2. **Power Calculation**
   - Two-sample t-test framework
   - α = 0.05 (two-tailed)
   - Target power = 0.80
   - Compute required N per station

3. **Achieved Power Estimation**
   - Non-central t-distribution
   - Current N = 400 per station

### Primary Metrics
- Mean Cohen's d
- Mean achieved power
- Required N for 80% power

### Expected Findings
- Very small effect sizes (d ≈ 0.02-0.06)
- Very low power (5-9%)
- Required N >> Current N

---

## Summary Table

| Phase | Primary Metric | Expected Result | Success Criterion |
|-------|---------------|-----------------|-------------------|
| P2 | Spearman ρ | ρ < 0 | p < 0.05 |
| P3 | Bootstrap CI | Excludes 0 | 95% CI excludes 0 |
| S1 | Station delta | Non-uniform | Top 5 > 25% |
| S1.7 | Power | < 20% | Required N > Current N |

---

## Frozen Settings

- Random seed: 42
- Bootstrap iterations: 10000
- Confidence level: 95%
- Near window: T-3 to T0
- Far window: T-14 to T-11
- Checkpoint: best_entropy.pth
- Model: V3_Model_v8.py

---

**Protocol Status: FROZEN**
**Do NOT modify for 2027 replication.**
