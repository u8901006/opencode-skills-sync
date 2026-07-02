---
name: timesfm-forecasting
description: >
  Zero-shot time series forecasting with Google's TimesFM foundation model. Use this
  skill when forecasting ANY univariate time series — sales, sensor readings, stock prices,
  energy demand, patient vitals, weather, or scientific measurements — without training a
  custom model. Supports both basic forecasting and advanced covariate forecasting (XReg)
  with dynamic and static exogenous variables. Automatically checks system RAM/GPU before
  loading the model, validates dataset fit before processing, supports CSV/DataFrame/array
  inputs, and returns point forecasts with calibrated prediction intervals. Includes a
  preflight system checker script that MUST be run before first use to verify the machine
  can load the model and handle your specific dataset.
license: Apache-2.0
metadata:
  author: Clayton Young (@borealBytes)
  version: "1.0.0"
---

# TimesFM Forecasting

## Overview

TimesFM (Time Series Foundation Model) is a pretrained decoder-only foundation model
developed by Google Research for time-series forecasting. It works **zero-shot** — feed it
any univariate time series and it returns point forecasts with calibrated quantile
prediction intervals, no training required.

This skill includes a **mandatory preflight system checker** that verifies RAM, GPU memory,
and disk space before the model is ever loaded so the agent never crashes the user's machine.

> **Key numbers**: TimesFM 2.5 uses 200M parameters (~800 MB on disk, ~1.5 GB in RAM on
> CPU, ~1 GB VRAM on GPU). The archived v1/v2 500M-parameter model needs ~32 GB RAM.
> Always run the system checker first.

## When to Use This Skill

Use this skill when:

- Forecasting **any univariate time series** (sales, demand, sensor, vitals, price, weather)
- You need **zero-shot forecasting** without training a custom model
- You want **probabilistic forecasts** with calibrated prediction intervals (quantiles)
- You have time series of **any length** (the model handles 1–16,384 context points)
- You need to **batch-forecast** hundreds or thousands of series efficiently
- You want a **foundation model** approach instead of hand-tuning ARIMA/ETS parameters
- You need **covariate forecasting** with exogenous variables (price, promotions, holidays, day-of-week effects) → use `forecast_with_covariates()` (TimesFM 2.5 + `pip install timesfm[xreg]`)

## Installation

```bash
pip install timesfm[torch]
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cu121
```

## Quick Start

```python
import torch, numpy as np, timesfm

torch.set_float32_matmul_precision("high")

model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)
model.compile(timesfm.ForecastConfig(
    max_context=1024, max_horizon=256, normalize_inputs=True,
    use_continuous_quantile_head=True, force_flip_invariance=True,
    infer_is_positive=True, fix_quantile_crossing=True,
))

point, quantiles = model.forecast(horizon=24, inputs=[
    np.sin(np.linspace(0, 20, 200)),
])
```

## Output

- `point_forecast`: shape `(batch, horizon)` — the median (0.5 quantile)
- `quantile_forecast`: shape `(batch, horizon, 10)` — [mean, q10, q20, ..., q90]

## Quality Checklist

- [ ] Output shape — `point_fc` is `(n_series, horizon)`, `quant_fc` is `(n_series, horizon, 10)`
- [ ] Quantile indices — index 0 = mean, 1 = q10 ... 9 = q90. NOT 0 = q0.
- [ ] Series length — context must be ≥ 32 data points.
- [ ] No NaN — `np.isnan(point_fc).any()` must be False.
- [ ] `matplotlib.use('Agg')` — before any pyplot import when running headless.
- [ ] `infer_is_positive` — set False for series that can be negative.
