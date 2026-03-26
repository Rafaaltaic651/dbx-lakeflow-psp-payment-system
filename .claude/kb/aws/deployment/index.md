# AWS Deployment KB

> **MCP Validated**: 2026-03-26

SAM CLI and AWS CLI commands for Lambda deployment and testing.

## Quick Navigation

| Need | Go To |
|------|-------|
| SAM lifecycle | `concepts/sam-lifecycle.md` |
| Deploy commands | `patterns/sam-deploy-commands.md` |
| Testing | `patterns/lambda-testing.md` |
| S3 operations | `patterns/s3-test-workflow.md` |

## Deployment Workflow

```text
sam validate -> sam build -> sam deploy -> verify -> test
```

## Confidence Thresholds

| Command Type | Threshold |
|--------------|-----------|
| `sam deploy` to prd | 0.98 |
| `aws lambda update-function-code` | 0.95 |
| `sam build`, `sam validate` | 0.90 |
| `sam local invoke`, `aws s3 ls` | 0.80 |

## Stack Naming Convention

```
{project}-{function}-{environment}

Examples:
- psp-processor-dev
- psp-processor-prd
```

## Related

- Agent: `.claude/agents/aws/aws-deployer.md`
- Lambda: `.claude/kb/aws/lambda/`
