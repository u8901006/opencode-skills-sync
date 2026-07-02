---
name: adding-features
description: Use when implementing new features or adding functionality to existing codebase
---

# Adding Features

## Overview
Systematic approach to adding features safely without breaking existing functionality.

## When to Use
- Adding new UI components or pages
- Implementing new API endpoints
- Adding business logic or workflows
- Extending existing features

## Core Pattern

1. **Understand the context**
   - Read existing code in the area
   - Check tests for current behavior
   - Review any documentation or specs

2. **Plan the change**
   - Identify touch points (files, functions, data structures)
   - Consider backward compatibility
   - Plan tests for the new feature

3. **Implement incrementally**
   - Small, focused commits
   - Test after each significant change
   - Keep working state

4. **Verify thoroughly**
   - Unit tests pass
   - Integration tests pass
   - Manual testing if needed
   - No regressions in existing functionality

## Quick Reference

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Read context | Understand existing code |
| 2 | Plan change | Clear implementation path |
| 3 | Write tests | Red-Green-Refactor |
| 4 | Implement | Tests pass |
| 5 | Verify | No regressions |

## Common Mistakes
- **Changing too much at once** → Break into smaller steps
- **Not checking existing tests** → Always run tests first
- **Skipping manual verification** → Test the feature actually works
- **Forgetting edge cases** → Consider error scenarios

## Red Flags
- "I'll just quickly add this" → Stop, plan first
- "Tests are probably fine" → Always verify
- "This won't break anything" → Check anyway
