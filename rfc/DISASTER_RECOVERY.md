# DISASTER_RECOVERY.md

## How to Restore

1. Extract RFC_V1_2026_PRE_REPLICATION.zip to D:/multi/scalogramv3/
2. Verify hashes: `python verify_rfc.py`
3. Install environment: `pip install -r source_code/requirements.txt`

## How to Verify Frozen Metrics

```python
import json
from pathlib import Path
DBG = Path('debug')
d = json.load(open(DBG/'MASTER_RESEARCH_STATUS.json'))
assert abs(d['key_results']['spearman_rho'] - (-0.134)) < 0.01
d = json.load(open(DBG/'bse2_results.json'))
assert abs(d['best_mce'] - 27.45) < 0.1
d = json.load(open(DBG/'az8_validation_complete.json'))
assert d['AZ8Rc']['ci95'][0] > 0  # CI lower > 0
print('All frozen metrics verified.')
```

## How to Rerun 2027 Replication

```bash
# Place 2027 catalog at: 2027_blindtest_sanitized.csv
# Place HDF5 files at: 2027/scalogram/
python phase_r1_independent_validation.py
```

## Key File Locations

| Asset | Path |
|-------|------|
| V8 checkpoint | checkpoints/best_entropy.pth |
| V9.5 checkpoint | Bayesian/v9_5_best.pth |
| V9.5 architecture | Bayesian/V9_5_Bayesian_Model.py |
| Station priors | Bayesian/priors/prior_*.pt |
| R1 runner | phase_r1_independent_validation.py |
| Analysis protocol | debug/analysis_protocol.yaml |
