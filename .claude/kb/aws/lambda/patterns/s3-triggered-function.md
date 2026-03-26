# S3-Triggered Lambda Function Pattern

> **MCP Validated**: 2026-03-26

## Complete SAM Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: S3-triggered file processor Lambda

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, prd]
  FileType:
    Type: String
    Description: Type of file to process
  SourceBucket:
    Type: String
    Description: S3 bucket for incoming files
  OutputBucket:
    Type: String
    Description: S3 bucket for processed output

Globals:
  Function:
    Timeout: 300
    MemorySize: 1024
    Runtime: python3.11
    Architectures:
      - arm64
    Environment:
      Variables:
        LOG_LEVEL: INFO
        ENVIRONMENT: !Ref Environment

Resources:
  ProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub 'psp-${FileType}-processor-${Environment}'
      Handler: !Sub 'src.handlers.${FileType}_handler.lambda_handler'
      CodeUri: .
      Description: !Sub 'Processes ${FileType} files and outputs Parquet'
      Environment:
        Variables:
          S3_OUTPUT_BUCKET: !Ref OutputBucket
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Sid: ReadSourceBucket
              Effect: Allow
              Action:
                - s3:GetObject
                - s3:GetObjectVersion
              Resource: !Sub 'arn:aws:s3:::${SourceBucket}/${FileType}/*'
            - Sid: WriteOutputBucket
              Effect: Allow
              Action:
                - s3:PutObject
                - s3:PutObjectTagging
              Resource: !Sub 'arn:aws:s3:::${OutputBucket}/${FileType}/*'
            - Sid: CloudWatchLogs
              Effect: Allow
              Action:
                - logs:CreateLogGroup
                - logs:CreateLogStream
                - logs:PutLogEvents
              Resource: !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/psp-${FileType}-processor-${Environment}:*'
      Events:
        S3Event:
          Type: S3
          Properties:
            Bucket: !Ref SourceBucketResource
            Events: s3:ObjectCreated:*
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: !Sub '${FileType}/'

  SourceBucketResource:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref SourceBucket

Outputs:
  FunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt ProcessorFunction.Arn
    Export:
      Name: !Sub '${AWS::StackName}-FunctionArn'
  FunctionName:
    Description: Lambda function name
    Value: !Ref ProcessorFunction
```

## S3 Event Filter Examples

```yaml
# Single file type prefix
Filter:
  S3Key:
    Rules:
      - Name: prefix
        Value: transactions/

# With suffix filter
Filter:
  S3Key:
    Rules:
      - Name: prefix
        Value: data/
      - Name: suffix
        Value: .csv
```

## Usage

```bash
# Deploy processor
sam deploy \
  --parameter-overrides \
    Environment=dev \
    FileType=transactions \
    SourceBucket=psp-use1-dev-source \
    OutputBucket=psp-use1-dev-stage
```
