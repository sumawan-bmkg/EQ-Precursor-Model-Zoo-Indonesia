# LESSONS_LEARNED.md — CRITICAL RECORD

**Date:** 2026-06-02
**Status:** Permanent record — do not delete

---

## False Leads and Rejected Hypotheses

### L1: V9.5 detection advantage over V8
**Hypothesis:** V9.5 would outperform V8 in detection (ROC-AUC, temporal signal).
**Why plausible:** More sophisticated architecture, Bayesian components.
**Why rejected:** Audit (C0c) showed V8 and V9.5 share identical detection backbone
(frozen). Detection outputs are mathematically identical. Any detection difference
would be due to randomness, not architecture.
**Lesson:** Always audit model path before claiming performance improvement.
**Impact:** Saved time by not pursuing invalid comparison.

### L2: Prior alignment as within-event temporal mediator
**Hypothesis:** Prior alignment improves as earthquake approaches (AZ16/AZ17).
**Why plausible:** AZ15 showed depth effect; AZ16 showed between-station correlation.
**Why rejected:** AZ17 Path A: β=0.000, p=1.000. Within events, prior alignment
is constant — it is a static geographic property, not a temporal variable.
**Lesson:** Between-group predictors do not automatically become within-group mediators.
Distinguish between-subject and within-subject effects explicitly.
**Impact:** Clarified the mechanistic model significantly.

### L3: Operational threshold (MCE < 30°) requires extensive model changes
**Hypothesis:** Achieving MCE < 30° would require retraining, new architecture.
**Why plausible:** Full-network MCE was 65°, far from target.
**Why rejected:** BSE2 showed that station selection + rank weighting alone
achieved MCE = 27.45° (22 independent operational configurations).
**Lesson:** Data selection and aggregation strategy often matters more than
model architecture for applied problems.

### L4: Prior quality (KL) directly predicts station temporal performance
**Hypothesis:** Stations with higher-KL priors have better azimuth accuracy.
**Why plausible:** Higher KL = more informative prior = better prediction.
**Why rejected:** PO2 showed no significant correlation between prior KL and
station MCE (p=0.67). The key metric is prior_alignment (ρ=0.868), not KL.
**Lesson:** "More informative" ≠ "more correctly oriented."

### L5: Geographic distance (km) predicts station reliability
**Hypothesis:** Stations closer to seismicity would perform better.
**Why plausible:** Closer = stronger signal.
**Why rejected:** SR2 found frac_500 (fraction of events within 500 km)
negatively correlates with performance (p=0.020). Stations with many close
events have skewed distance distributions → biased priors.
**Lesson:** More nearby events creates biased priors, not better performance.

---

## Technical Bugs Found and Fixed

### B1: Pipeline input mismatch (E1-E4 Forensic, Apr 2026)
**Bug:** V8 pipeline was loading PNG fallback tensors (zero variance) instead
of HDF5 scalograms. All predictions were near-identical.
**Fix:** HDF5 adapter built; tensor validation added (std > 0 assertion).
**Detection:** A4 audit showed unique_input_hash_count = 1 (should be > 1).

### B2: Bootstrap resampling structure (AZ17)
**Bug:** First AZ17 implementation resampled event-day pairs randomly,
destroying the temporal structure needed to test within-event mediation.
**Fix:** Hierarchical bootstrap (resample events, preserve temporal order within).
**Impact:** Changed CI from [-0.060, +0.060] to properly structured test.

### B3: Prior entropy as predictor
**Bug:** mean_prior_H showed NaN in SR2e correlation because all stations
had nearly identical entropy values (insufficient variance).
**Fix:** Switched to prior_kl and frac_500 as predictors.

---

## Methodological Decisions

### D1: Why hierarchical bootstrap for AZ8Rc
Standard bootstrap resampled event-day pairs randomly, breaking temporal
structure. Hierarchical bootstrap (resample events, keep T-0..T-14 intact)
correctly tests H0: "no within-event trend in R."

### D2: Why within-event demeaning in AZ17
Without demeaning, between-event variance dominates OLS regression.
Demeaning removes event-level random intercepts, equivalent to including
event fixed effects in a panel regression.

### D3: Why piecewise SEM over full SEM (lavaan)
- n=66 events too small for latent-variable SEM
- No latent variables required (all observed)
- Easier to audit path-by-path
- Reviewers in geoscience prefer transparent path models

### D4: Why station selection over bandwidth optimization (PO)
PO1 showed that bandwidth optimization improves MCE only if model is
retrained with new priors. Using different bandwidth at inference time
creates distribution shift (model trained on σ=15°). Station selection
avoids retraining entirely.

---

## Do Not Repeat

1. Do NOT run full 22-station × 14-day inference without batching — timeout risk.
2. Do NOT use standard bootstrap for within-event hypotheses — use hierarchical.
3. Do NOT interpret between-station correlations as within-event mediators.
4. Do NOT claim V9.5 detection advantage — paths are identical.
5. Do NOT add MCE optimization experiments without new data — diminishing returns.
6. Do NOT retrain before 2027 replication — frozen checkpoint is the gold standard.
