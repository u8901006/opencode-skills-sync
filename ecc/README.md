# Everything Claude Code (ECC) Integration

Integrated from: https://github.com/affaan-m/everything-claude-code

## Available Skills (13)

| Skill | Description |
|-------|-------------|
| `tdd-workflow` | Test-driven development with 80%+ coverage |
| `continuous-learning` | Auto-extract patterns from sessions |
| `continuous-learning-v2` | Instinct-based learning approach |
| `agentic-engineering` | AI-first development patterns |
| `security-review` | Security audit and vulnerability check |
| `verification-loop` | Continuous verification workflow |
| `autonomous-loops` | Self-directed task execution |
| `backend-patterns` | Backend architecture patterns |
| `frontend-patterns` | Frontend architecture patterns |
| `golang-patterns` | Go coding standards and patterns |
| `python-patterns` | Python coding standards |
| `django-patterns` | Django-specific patterns |
| `springboot-patterns` | Spring Boot patterns |

## Subdirectories

- `agents/` - 18 specialized subagents (code-reviewer, planner, etc.)
- `commands/` - 48 slash command templates
- `rules/` - 9 language-specific rule sets

## Usage

Skills are automatically discovered by opencode. Reference them by name:
- `ecc:tdd-workflow` or just `tdd-workflow`
- `ecc:security-review` or just `security-review`

## Notes

- Agents use Claude Code format (tools, model fields) - may need adaptation
- Commands are slash-command templates for reference
- Rules are language-specific guidelines
