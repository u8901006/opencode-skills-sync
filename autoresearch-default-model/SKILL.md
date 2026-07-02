---
name: autoresearch-default-model
description: Use when running autoresearch-win-rtx with the original model shape and the user wants the default training path instead of the 8GB compat preset.
---

# Autoresearch Default Model

## Overview
Use the default preset for `autoresearch-win-rtx` when the user wants the original model shape instead of the conservative 8GB tuning. This preset maps to `--model-preset default`.

## When to Use
- User asks for the original model
- User wants the default `depth=8`, `window_pattern=SSSL` path
- User does not want the smaller 8GB compatibility model preset

## Quick Reference
- Workdir: `D:\自動升級\autoresearch-win-rtx`
- Full run: `uv run train.py --model-preset default`
- Smoke test: `uv run train.py --smoke-test --model-preset default`

## Implementation
Always run commands inside `D:\自動升級\autoresearch-win-rtx`.

Example:

```powershell
uv run train.py --model-preset default
```

## Common Mistakes
- Do not confuse this with the upstream Linux/H100-oriented `karpathy/autoresearch` repo
- Do not use `compat-8gb` when the user explicitly wants the original model
- The default model can be slower or heavier on 8GB cards, so avoid silently switching presets
