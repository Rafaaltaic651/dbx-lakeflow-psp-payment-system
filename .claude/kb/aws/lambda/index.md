# AWS Lambda KB

> **MCP Validated**: 2026-03-26

SAM templates, IAM policies, and S3 triggers for Lambda functions.

## Quick Navigation

| Need | Go To |
|------|-------|
| SAM syntax | `concepts/sam-model.md` |
| IAM policies | `concepts/least-privilege.md` |
| S3 triggers | `patterns/s3-triggered-function.md` |
| Multi-function | `patterns/multi-function-stack.md` |
| Environment config | `patterns/environment-config.md` |

## Key Principles

1. **Least Privilege** - No wildcards in IAM policies
2. **Specific ARNs** - Always scope to bucket + prefix
3. **Parameters** - Enable dev/prd switching
4. **Outputs** - Export ARNs for cross-stack references

## Related

- Agent: `.claude/agents/aws/aws-lambda-architect.md`
- Deployment: `.claude/kb/aws/deployment/`
