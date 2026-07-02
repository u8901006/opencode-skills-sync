---
name: autoresearch-compat-8gb
description: Use when running autoresearch-win-rtx on a low-VRAM Windows NVIDIA GPU and the user wants the conservative 8GB model preset with --model-preset compat-8gb.
---

# Autoresearch Compat 8GB

## Overview
Use the explicit 8GB preset for `autoresearch-win-rtx` when stability matters more than matching the original model shape. This preset maps to `--model-preset compat-8gb`.

## When to Use
- User asks for the 8GB preset
- User mentions `3060 Ti 8GB`, low VRAM, compatibility path, or stability-first training
- User wants the smaller `depth=6`, `window_pattern=L` profile

## Quick Reference
- Workdir: `D:\自動升級\autoresearch-win-rtx`
- Full run: `uv run train.py --model-preset compat-8gb`
- Smoke test: `uv run train.py --smoke-test --model-preset compat-8gb`

## Implementation
Always run commands inside `D:\自動升級\autoresearch-win-rtx`.

Example:

```powershell
uv run train.py --model-preset compat-8gb
```

## Common Mistakes
- Do not use this skill for the original upstream `karpathy/autoresearch` repo
- Do not omit `--model-preset compat-8gb` if the user explicitly asked for the 8GB preset
- Prefer a smoke test first when the user asks for validation rather than a full run
