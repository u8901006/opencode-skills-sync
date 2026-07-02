---
name: chub-first
description: Use when writing code that uses any API, library, or framework - search Context Hub first for up-to-date documentation instead of relying on potentially outdated training data
---

# Chub First

## Overview

**Before writing code that uses any API, library, or framework, query Context Hub (chub) for current documentation.**

AI training data becomes stale. Chub provides versioned, curated docs that agents can trust.

## When to Use

**ALWAYS before:**
- Using any API (OpenAI, Stripe, Twilio, etc.)
- Implementing with frameworks (React, Next.js, etc.)
- Integrating services (Supabase, Firebase, etc.)
- Writing code that depends on external libraries

## Quick Reference

| Command | Purpose |
|---------|---------|
| `chub search <query>` | Find relevant docs |
| `chub get <id> --lang py\|js` | Fetch docs in language variant |
| `chub update` | Refresh cached registry |

## Workflow

```
1. chub search "<library/api name>"
2. chub get <doc-id> --lang <js|py>
3. Read returned docs
4. Write code using current API
```

## Example

```bash
# Before using OpenAI API
chub search openai
chub get openai/chat --lang js
# Now code with confidence using current docs
```

## Red Flags

- Writing API calls from memory → STOP, search chub first
- "I remember how this works" → Training data may be outdated
- Guessing parameters → Check docs

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip search, use memory | Always `chub search` first |
| Wrong language variant | Use `--lang js` or `--lang py` |
| Assume docs exist | If not found, note the gap |
