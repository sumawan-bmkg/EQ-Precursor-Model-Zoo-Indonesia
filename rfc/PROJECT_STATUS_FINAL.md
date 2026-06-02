# PROJECT_STATUS_FINAL.md — RFC_V1

**Checkpoint:** RFC_V1_2026_PRE_REPLICATION
**Date:** 2026-06-02
**Status:** CORE DISCOVERY COMPLETE

---

```
DETECTION_SIGNAL        = SUPPORTED   (P3: rho=-0.134, p<0.001)
SPATIAL_HETEROGENEITY   = SUPPORTED   (S1.7: power=5-9%, need 19-25x N)
AZIMUTH_OPERATIONAL     = YES         (BSE2: MCE=27.45°)
CONSENSUS_DYNAMICS      = CONFIRMED   (AZ8Rc: CI=[+0.052,+0.191])
DEPTH_MODULATION        = CONFIRMED   (AZ15: shallow p=0.0009)
CAUSAL_CHAIN            = PARTIAL     (AZ17: spread confirmed, alignment rejected)
REPRODUCIBILITY         = 10/10
REPLICATION_STATUS      = WAITING_2027
CORE_DISCOVERY_PHASE    = COMPLETE
```

## Confirmed Chain

1. Probability signal     → P3  (rho=-0.134, p<0.001)
2. Azimuth operational   → BSE2 (MCE=27.45°, 22 configs < 30°)
3. Prior adds information → AZ4 (ΔMI=0.378 bits, 68% relative gain)
4. Consensus dynamics    → AZ8Rc (CI=[+0.052,+0.191], 99.93% P>0)
5. Depth modulation      → AZ15 (shallow p=0.0009, deep p=0.06)
6. Spread mechanism      → AZ17 (beta=+0.123, p<0.001)
7. Alignment=static      → AZ17 (path A rejected, p=1.0)

## Open Questions

1. WHY does inter-station spread decrease before shallow EQ?
   (requires spectral geomagnetic data + ionospheric indices)
2. Will all findings replicate on 2027 data?
   (pre-registered, R1 runner ready)
