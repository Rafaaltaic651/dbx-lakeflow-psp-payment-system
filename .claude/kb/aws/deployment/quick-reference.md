# AWS Deployment Quick Reference

> **MCP Validated**: 2026-03-26

## SAM Commands

```bash
# Validate template
sam validate --lint

# Build Lambda package
sam build

# Deploy (interactive first time)
sam deploy --guided

# Deploy to specific environment
sam deploy --config-env dev
sam deploy --config-env prd

# Tail logs
sam logs --name FunctionName --stack-name StackName --tail
```

## AWS Lambda Commands

```bash
# List functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `psp-`)]'

# Get function config
aws lambda get-function --function-name psp-processor-dev

# Invoke function
aws lambda invoke \
  --function-name psp-processor-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://events/s3-event.json \
  response.json

# Update code
aws lambda update-function-code \
  --function-name psp-processor-dev \
  --zip-file fileb://function.zip
```

## S3 Commands

```bash
# Upload test file
aws s3 cp input/test-data.csv s3://psp-use1-dev-source/data/

# List bucket
aws s3 ls s3://psp-use1-dev-stage/output/

# Download output
aws s3 cp s3://psp-use1-dev-stage/output/result.parquet ./output/
```

## CloudFormation Commands

```bash
# List stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Describe stack
aws cloudformation describe-stacks --stack-name psp-processor-dev

# Get outputs
aws cloudformation describe-stacks \
  --stack-name psp-processor-dev \
  --query 'Stacks[0].Outputs'
```

## samconfig.toml Template

```toml
version = 0.1

[default.deploy.parameters]
stack_name = "psp-processor-dev"
resolve_s3 = true
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
parameter_overrides = "Environment=dev SourceBucket=psp-use1-dev-source OutputBucket=psp-use1-dev-stage"

[prd.deploy.parameters]
stack_name = "psp-processor-prd"
resolve_s3 = true
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
parameter_overrides = "Environment=prd SourceBucket=psp-use1-prd-source OutputBucket=psp-use1-prd-stage"
```
