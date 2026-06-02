# ONE_CLICK_REPRODUCTION.md

## Core Analysis Sequence

```bash
# 1. Detection temporal signal
python phase_p3_temporal_validation.py

# 2. AZ8R Real consensus (requires V9.5 + HDF5)
python phase_az8r_real_consensus.py

# 3. AZ8Rb+Rc+AZ13 validation
python phase_az8b_az8c_az13.py

# 4. AZ15 depth modulation
python phase_az14_az15.py

# 5. AZ16 mechanism
python phase_az16_mechanism.py

# 6. AZ17 piecewise SEM
python phase_az17_psem.py

# 7. BSE2 optimal ensemble
python phase_bse2_optimal_ensemble.py
```

## Expected Outputs (verify against FROZEN_METRICS.md)

| Script | Key Output | Expected Value |
|--------|------------|----------------|
| az8r | mean rho | +0.122 ± 0.01 |
| az8b_az8c | CI lower | > 0.05 |
| az14_az15 | shallow p | < 0.001 |
| az17_psem | Path B beta | +0.123 ± 0.01 |
| bse2 | best MCE | 27.45 ± 0.1 |
