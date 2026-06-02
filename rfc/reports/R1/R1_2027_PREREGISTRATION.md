# R1: 2027 Independent Blind-Test Pre-Registration

**Pre-registration Date:** 2026-06-01
**Expected Validation Date:** TBD
**Status:** PRE-REGISTERED

---

## Objective

Validate the 2026 findings on an independent dataset (2027 blind test) using the exact same protocol.

---

## Success Criteria

The replication will be deemed successful if ALL FOUR criteria are satisfied:

### Criterion 1: Spearman Correlation Direction
- **Requirement:** Spearman ρ < 0 (negative)
- **Rationale:** Negative correlation indicates probability increases toward earthquake
- **Test:** One-tailed test, α = 0.05

### Criterion 2: Bootstrap Confidence Interval
- **Requirement:** 95% bootstrap CI excludes 0
- **Rationale:** CI excluding zero indicates statistically robust signal
- **Method:** Percentile method, 10000 bootstrap iterations

### Criterion 3: Signal Direction
- **Requirement:** Direction = INCREASING_TOWARD_EQ
- **Rationale:** Consistent with precursor hypothesis
- **Test:** >97.5% of bootstrap samples have ρ < 0

### Criterion 4: Effect Size Magnitude
- **Requirement:** |ρ| within same order of magnitude as 2026
- **2026 Reference:** ρ = -0.134
- **Acceptable Range:** -0.30 < ρ < -0.05
- **Rationale:** Same underlying phenomenon should produce similar effect size

---

## Replication Verdict Logic

```
IF all four criteria satisfied:
    REPLICATION_SUCCESS = YES
    CONCLUSION: "2026 findings replicated on independent 2027 dataset"
    
ELSE IF 3 of 4 criteria satisfied:
    REPLICATION_SUCCESS = PARTIAL
    CONCLUSION: "Partial replication, requires investigation"
    
ELSE:
    REPLICATION_SUCCESS = NO
    CONCLUSION: "2026 findings did not replicate"
```

---

## Secondary Endpoints (Exploratory)

These will be analyzed but are NOT required for replication success:

| Endpoint | 2026 Result | 2027 Comparison |
|----------|-------------|-----------------|
| Station heterogeneity | Present | Exploratory |
| Top 5 contribution | 32.6% | Exploratory |
| Mean power | 5.4% | Exploratory |

---

## Methodology (Frozen)

All settings from `analysis_protocol.yaml` must be used:

- **Checkpoint:** best_entropy.pth
- **Model:** V3_Model_v8.py
- **Random seed:** 42
- **Bootstrap iterations:** 10000
- **Near window:** T-3 to T0
- **Far window:** T-14 to T-11
- **Confidence level:** 95%

**NO modifications allowed.**

---

## Data Requirements

- 2027 blind test dataset
- Same format as 2026 (CSV with event_id, timestamp, magnitude)
- HDF5 scalogram files with same structure

---

## Reporting

Results will be reported as:

1. **Primary:** Success/Failure verdict with criteria checklist
2. **Secondary:** Effect size comparison (2026 vs 2027)
3. **Exploratory:** Station-level analysis comparison

---

## Timeline

| Step | Expected Date |
|------|---------------|
| Pre-registration complete | 2026-06-01 ✓ |
| 2027 dataset available | TBD |
| Analysis complete | Within 7 days of data availability |
| Report generated | Within 14 days of data availability |

---

## Signatures

**Pre-registered by:** V8 Research Team
**Date:** 2026-06-01
**Protocol Version:** 1.0.0 FROZEN

---

**This document is FROZEN and must not be modified after 2027 data analysis begins.**
