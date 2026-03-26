# IAM Least Privilege

> **MCP Validated**: 2026-03-26

## Core Principle

**Never use wildcards. Always scope to specific resources.**

## Rules (0.98 Confidence Required)

### CORRECT Patterns

```yaml
# Specific bucket + prefix
- Effect: Allow
  Action:
    - s3:GetObject
  Resource: !Sub 'arn:aws:s3:::${SourceBucket}/${Prefix}/*'

# Specific actions only
- Effect: Allow
  Action:
    - s3:GetObject
    - s3:GetObjectVersion
  Resource: !Sub 'arn:aws:s3:::${SourceBucket}/${Prefix}/*'

# CloudWatch logs scoped to function
- Effect: Allow
  Action:
    - logs:CreateLogGroup
    - logs:CreateLogStream
    - logs:PutLogEvents
  Resource: !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${FunctionName}:*'
```

### WRONG Patterns

```yaml
# Wildcard bucket - NEVER DO THIS
- Effect: Allow
  Action:
    - s3:GetObject
  Resource: '*'

# Wildcard actions - NEVER DO THIS
- Effect: Allow
  Action:
    - s3:*
  Resource: 'arn:aws:s3:::my-bucket/*'

# Unrestricted logs - AVOID
- Effect: Allow
  Action:
    - logs:*
  Resource: '*'
```

## Lambda Permission Reference

| Permission | Resource ARN |
|------------|--------------|
| Read source | `arn:aws:s3:::${source-bucket}/${prefix}/*` |
| Write output | `arn:aws:s3:::${output-bucket}/${prefix}/*` |
| CloudWatch | `arn:aws:logs:${region}:${account}:log-group:/aws/lambda/${function}:*` |

## Validation Checklist

- [ ] No `Action: s3:*`
- [ ] No `Resource: '*'`
- [ ] Bucket ARN includes prefix path
- [ ] Logs scoped to specific log group
