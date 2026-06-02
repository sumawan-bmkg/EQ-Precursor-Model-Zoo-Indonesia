# FROZEN_METRICS.md — RFC_V1_2026_PRE_REPLICATION

**DATE FROZEN:** 2026-06-02
**STATUS:** IMMUTABLE REFERENCE VALUES

These values define the scientific state of the project at freeze.
Do NOT modify. Any future result deviating from these values
must be explained and documented.

---

## Detection Branch

| Metric | Value | Source |
|--------|-------|--------|
| P3 Spearman rho | -0.134 | MASTER_RESEARCH_STATUS.json |
| P3 Bootstrap CI | [-0.17, -0.10] | MASTER_RESEARCH_STATUS.json |
| P3 p-value | <0.001 | MASTER_RESEARCH_STATUS.json |

## Azimuth Branch

| Metric | Value | Source |
|--------|-------|--------|
| AZ1 MCE (all-22 uniform) | 65.02° | az1_results.json |
| AZ2 Prior effect | 20.16% | az2_results.json |
| AZ4 Information gain | 0.378 bits | az4_results.json |
| AZ4 MI (original) | 0.932 bits | az4_results.json |
| AZ4 MI (zero prior) | 0.554 bits | az4_results.json |
| SR prior_alignment rho | +0.868 | sr_bse_results.json |
| SR prior_alignment p | <0.001 | sr_bse_results.json |
| BSE2 MCE (Top-4 rank) | 27.45° | bse2_results.json |
| BSE2 Acc±30° | 78% | bse2_results.json |
| BSE2 Acc±45° | 83% | bse2_results.json |
| BSE2 Improvement vs all-22 | 57.8% | bse2_results.json |

## Consensus Branch

| Metric | Value | Source |
|--------|-------|--------|
| AZ8Rb positive events | 42/65 (64.6%) | az8_validation_complete.json |
| AZ8Rb binomial p | 0.0124 | az8_validation_complete.json |
| AZ8Rb Wilcoxon p | 0.0004 | az8_validation_complete.json |
| AZ8Rc mean per-event rho | +0.122 | az8_validation_complete.json |
| AZ8Rc 95% CI lower | +0.052 | az8_validation_complete.json |
| AZ8Rc 95% CI upper | +0.191 | az8_validation_complete.json |
| AZ8Rc P(>0) | 0.9993 | az8_validation_complete.json |
| AZ13 window t-test p | <0.0001 | az8_validation_complete.json |
| AZ13 delta R | +0.00153 | az8_validation_complete.json |

## Depth & Mechanism Branch

| Metric | Value | Source |
|--------|-------|--------|
| AZ15 shallow t-test p | 0.0009 | az14_az15_results.json |
| AZ15 deep t-test p | 0.0621 | az14_az15_results.json |
| AZ15 shallow 0-20km binom p | 0.0001 | az15_depth_stratified.csv |
| AZ17 Path A (db→align) β | 0.000 | az17_psem_results.json |
| AZ17 Path A p | 1.000 | az17_psem_results.json |
| AZ17 Path B (db→spread) β | +0.123 | az17_psem_results.json |
| AZ17 Path B p | 0.0001 | az17_psem_results.json |
| AZ17 Path C (spread→R) β | -0.991 | az17_psem_results.json |
| AZ17 Path C p | <0.001 | az17_psem_results.json |

## Station Heterogeneity

| Metric | Value | Source |
|--------|-------|--------|
| S1.7 mean power | 5.4% | s17_power_analysis_verdict.json |
| S1.7 required N multiplier | 19-25× | s17_power_analysis_verdict.json |
| S1 Top-5 contribution | 32.6% | s1_results.json |
| S1 Top-10 contribution | 79.6% | s1_results.json |
