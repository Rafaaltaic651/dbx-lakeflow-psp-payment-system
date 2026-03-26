# AWS Lambda Quick Reference

> **MCP Validated**: 2026-03-26

## SAM Template Structure

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, prd]

Globals:
  Function:
    Timeout: 300
    MemorySize: 1024
    Runtime: python3.11

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src.handlers.my_handler.lambda_handler
      CodeUri: .
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action: [s3:GetObject]
              Resource: !Sub 'arn:aws:s3:::${Bucket}/*'
      Events:
        S3Event:
          Type: S3
          Properties:
            Bucket: !Ref MyBucket
            Events: s3:ObjectCreated:*
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: my-prefix/
```

## IAM Actions by Operation

| Operation | Actions |
|-----------|---------|
| Read S3 | `s3:GetObject`, `s3:GetObjectVersion` |
| Write S3 | `s3:PutObject` |
| List S3 | `s3:ListBucket` |
| Logs | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` |

## S3 Event Filter Syntax

```yaml
Filter:
  S3Key:
    Rules:
      - Name: prefix
        Value: data/
      - Name: suffix
        Value: .parquet
```

## Stack Naming Convention

```
{project}-{function}-{environment}

Examples:
- psp-processor-dev
- psp-processor-prd
```
