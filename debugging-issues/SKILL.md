---
name: debugging-issues
description: Use when encountering bugs, test failures, or unexpected behavior in code
---

# Debugging Issues

## Overview
Systematic debugging approach to identify root causes and verify fixes.

## When to Use
- Tests failing unexpectedly
- Production bugs
- Strange behavior in code
- Performance issues
- Regression after changes

## Core Pattern

1. **Reproduce the issue**
   - Confirm the bug is real
   - Find minimal reproduction case
   - Document exact steps

2. **Gather information**
   - Read relevant code
   - Check logs and error messages
   - Review recent changes (git log/blame)
   - Check environment/configuration

3. **Form hypothesis**
   - What might cause this?
   - Check one theory at a time
   - Use Occam's razor (simplest first)

4. **Test hypothesis**
   - Add logging/debugging
   - Run experiments
   - Check if theory explains behavior

5. **Implement and verify fix**
   - Make the minimal fix
   - Verify it solves the issue
   - Ensure no regressions

## Quick Reference

| Phase | Key Questions | Tools |
|-------|---------------|-------|
| Reproduce | Is it consistent? What triggers it? | Test cases, manual steps |
| Gather | What changed? What's the error? | git, logs, stack traces |
| Hypothesize | What's the simplest explanation? | Code review, rubber duck |
| Test | Does this theory hold? | Debug logging, experiments |
| Fix | Does fix work? Any side effects? | Tests, verification |

## Common Mistakes
- **Fixing symptoms not causes** → Find root cause first
- **Changing multiple things** → One change at a time
- **Not verifying fix** → Always confirm the bug is gone
- **Ignoring edge cases** → Consider what else might break

## Red Flags
- "I know what the problem is" → Verify your assumption
- "Let me try a few things" → Be systematic, not random
- "This should fix it" → Verify before declaring victory
