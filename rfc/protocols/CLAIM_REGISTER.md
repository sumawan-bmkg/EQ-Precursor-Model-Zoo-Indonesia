# Claim Register — V8 Geomagnetic Precursor Model

**Version:** 1.0.0 (FROZEN)
**Date:** 2026-06-01
**Purpose:** Explicit documentation of what is and is not supported by evidence

---

## SUPPORTED CLAIMS

These claims are directly supported by empirical evidence from the 2026 blind test:

### Primary Claims

| Claim | Evidence | Phase |
|-------|----------|-------|
| ✓ Weak temporal precursor signal exists at network level | Spearman ρ = -0.134, p < 0.001 | P3 |
| ✓ Probability increases toward earthquake occurrence | Pearson r = -0.133, CI excludes 0 | P2, P3 |
| ✓ Bootstrap confidence interval excludes zero | 95% CI: [-0.17, -0.10] | P3 |
| ✓ Direction is INCREASING_TOWARD_EARTHQUAKE | 99.9% of bootstrap samples have ρ < 0 | P3 |

### Secondary Claims

| Claim | Evidence | Phase |
|-------|----------|-------|
| ✓ Spatial station contributions are heterogeneous | Delta range: -0.005 to +0.005 | S1 |
| ✓ Signal concentration is non-uniform | Top 5 = 32.6%, Top 10 = 79.6% | S1 |
| ✓ Network aggregation improves detectability | Network: significant, Station: not significant | P3 vs S1 |
| ✓ Station-level analyses are severely underpowered | Power = 5-9%, Need 19-25× more data | S1.7 |

### Technical Claims

| Claim | Evidence | Phase |
|-------|----------|-------|
| ✓ Pipeline integrity verified | HDF5 adapter functional, inputs validated | Audit |
| ✓ Model loading verified | best_entropy.pth loads correctly | Audit |
| ✓ Reproducibility established | Deterministic with seed=42 | Audit |

---

## UNSUPPORTED CLAIMS

These claims are NOT supported by current evidence. They should NOT be made in publications:

### Operational Claims

| Claim | Why Unsupported |
|-------|-----------------|
| ✗ Operational earthquake forecasting capability | Effect size too small (ρ = -0.134), no threshold optimization |
| ✗ Practical prediction utility | No decision-theoretic analysis, no cost-benefit assessment |
| ✗ Real-time deployment readiness | No latency analysis, no infrastructure evaluation |

### Magnitude Claims

| Claim | Why Unsupported |
|-------|-----------------|
| ✗ Magnitude prediction | ROC-AUC = 0.56 (barely above random), not validated |
| ✗ Magnitude threshold discrimination | No consistent pattern across magnitude strata |
| ✗ Large earthquake (M≥6.5) prediction | n=1, statistically meaningless |

### Geographic Claims

| Claim | Why Unsupported |
|-------|-----------------|
| ✗ Geographic causality | No coordinate metadata, no spatial analysis |
| ✗ Station-specific physical mechanisms | Underpowered to detect individual mechanisms |
| ✗ Optimal station placement | Would require controlled experiment |

### Generalization Claims

| Claim | Why Unsupported |
|-------|-----------------|
| ✗ Generalization to 2027 | 2027 data not yet analyzed (pre-registered for R1) |
| ✗ Generalization to other regions | Single region dataset |
| ✗ Generalization to other time periods | Single year dataset |

### Mechanism Claims

| Claim | Why Unsupported |
|-------|-----------------|
| ✗ Electromagnetic precursor mechanism | No physical model, only statistical correlation |
| ✗ Lithosphere-atmosphere coupling | Beyond scope of current analysis |
| ✗ Stress-induced magnetic anomalies | No stress measurements |

---

## BORDERLINE CLAIMS

These claims have partial support but require additional evidence:

| Claim | Current Status | Required Evidence |
|-------|---------------|-------------------|
| ? Top 5 stations more important than others | Top 5 = 32.6% (moderate concentration) | Geographic analysis, replication |
| ? LWA and SRG are positive contributors | Delta > 0, but CI spans zero | More data, statistical power |
| ? MLB and SRO are inverse contributors | Delta < 0, but CI spans zero | More data, statistical power |
| ? Signal is distributed, not concentrated | SCI = 0.28 (< 0.40 threshold) | Replication, clustering analysis |

---

## Publication Guidance

### Statements to AVOID

1. "The model can predict earthquakes" — Not supported. Use: "The model shows weak precursor signal patterns"

2. "This station is the best for detection" — Not supported. Use: "This station has the largest observed contribution"

3. "The model is ready for operational use" — Not supported. Use: "The model requires further validation"

4. "Magnitude can be predicted" — Not supported. Use: "Magnitude proxy shows weak discrimination"

### Statements to USE

1. "The model shows a statistically significant temporal signal at the network level"

2. "Individual station contributions are heterogeneous but underpowered for significance testing"

3. "Network aggregation improves signal detectability compared to individual stations"

4. "Independent replication on 2027 data is required before drawing stronger conclusions"

---

## Claim Evolution Log

| Date | Claim Added | Evidence Phase | Status |
|------|-------------|----------------|--------|
| 2026-06-01 | Temporal signal exists | P3 | SUPPORTED |
| 2026-06-01 | Station heterogeneity | S1 | SUPPORTED |
| 2026-06-01 | Underpowering explained | S1.7 | SUPPORTED |

---

**Register Status: FROZEN**
**Do NOT add new claims without supporting evidence from new phases.**
