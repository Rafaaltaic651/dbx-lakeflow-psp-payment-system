# SAM Deploy Commands

> **MCP Validated**: 2026-03-26

## Full Deployment Workflow

```bash
# 1. Validate template
sam validate --lint

# 2. Build Lambda package
sam build

# 3. Deploy to dev
sam deploy --config-env default

# 4. Verify deployment
aws cloudformation describe-stacks \
  --stack-name psp-processor-dev \
  --query 'Stacks[0].StackStatus'

# 5. Test with sample file
aws s3 cp input/test-data.csv s3://psp-use1-dev-source/data/

# 6. Check logs
sam logs --name ProcessorFunction --stack-name psp-processor-dev --tail
```

## Deploy Options

```bash
# Guided setup (first time)
sam deploy --guided

# Use specific config environment
sam deploy --config-env prd

# Override parameters
sam deploy \
  --parameter-overrides \
    Environment=dev \
    SourceBucket=psp-use1-dev-source \
    OutputBucket=psp-use1-dev-stage

# Skip confirmation (CI/CD)
sam deploy --no-confirm-changeset

# Force deploy
sam deploy --force-upload
```

## Example Deployment

```bash
sam deploy \
  --stack-name psp-processor-dev \
  --parameter-overrides \
    Environment=dev \
    FileType=transactions \
    SourceBucket=psp-use1-dev-source \
    OutputBucket=psp-use1-dev-stage \
  --capabilities CAPABILITY_IAM
```

## Multi-Function Deploy

```bash
# Deploy all processors to dev
for type in transactions merchants settlements; do
  sam deploy \
    --stack-name psp-${type}-processor-dev \
    --parameter-overrides \
      Environment=dev \
      FileType=${type} \
      SourceBucket=psp-use1-dev-source \
      OutputBucket=psp-use1-dev-stage \
    --capabilities CAPABILITY_IAM
done
```

## Post-Deployment Verification

```bash
# Check function exists
aws lambda get-function \
  --function-name psp-processor-dev

# Check S3 trigger
aws lambda get-function-event-invoke-config \
  --function-name psp-processor-dev

# List stack resources
aws cloudformation list-stack-resources \
  --stack-name psp-processor-dev
```
