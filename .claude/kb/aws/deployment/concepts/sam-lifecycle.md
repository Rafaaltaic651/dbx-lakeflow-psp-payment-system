# SAM Lifecycle

> **MCP Validated**: 2026-03-26

## Build -> Validate -> Deploy -> Verify

```text
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  VALIDATE   │───>│    BUILD    │───>│   DEPLOY    │───>│   VERIFY    │
│  sam valid. │    │  sam build  │    │  sam deploy │    │   aws cf    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Step 1: Validate

```bash
sam validate --lint
```

**Checks:**
- Template syntax
- Resource references
- IAM policy structure

## Step 2: Build

```bash
sam build
```

**Actions:**
- Resolves dependencies
- Packages Lambda code
- Creates `.aws-sam/build/` directory

**Options:**

```bash
# Use Docker for native dependencies
sam build --use-container

# Specify template
sam build --template-file sam/template.yaml
```

## Step 3: Deploy

```bash
# First time (interactive)
sam deploy --guided

# Subsequent deploys
sam deploy --config-env dev
```

**Creates:**
- CloudFormation stack
- Lambda function
- S3 event trigger
- IAM role

## Step 4: Verify

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name psp-processor-dev \
  --query 'Stacks[0].StackStatus'

# Expected: CREATE_COMPLETE or UPDATE_COMPLETE
```

## Rollback

If deployment fails:

```bash
# CloudFormation auto-rollbacks on failure

# Manual rollback to previous version
aws lambda update-function-code \
  --function-name psp-processor-dev \
  --s3-bucket deployment-bucket \
  --s3-key previous-version.zip
```
