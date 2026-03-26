# DABs Deployment Patterns

> **MCP Validated**: 2026-03-26
> **Source**: https://docs.databricks.com/aws/en/dev-tools/bundles

## Databricks Asset Bundles (DABs)

DABs provide declarative deployment of Databricks resources including Lakeflow pipelines.

## Project Structure

```text
project-lakeflow/
├── databricks.yml           # Main bundle config
├── resources/
│   ├── transactions_pipeline.yml
│   ├── merchants_pipeline.yml
│   └── settlements_pipeline.yml
├── src/
│   ├── transactions/
│   │   ├── bronze.py
│   │   ├── silver.py
│   │   └── gold.py
│   ├── merchants/
│   │   ├── bronze.py
│   │   ├── silver.py
│   │   └── gold.py
│   └── shared/
│       └── expectations.py
└── tests/
    └── test_pipelines.py
```

## Main Bundle Configuration

```yaml
bundle:
  name: psp-lakeflow

variables:
  catalog:
    default: psp_catalog
  schema:
    default: lakeflow
  source_bucket:
    default: psp-data-source
  stage_bucket:
    default: psp-data-stage

include:
  - resources/*.yml

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: psp_catalog_dev
      schema: lakeflow_dev
      source_bucket: psp-use1-dev-source
      stage_bucket: psp-use1-dev-stage
    workspace:
      host: https://dbc-xxxxx.cloud.databricks.com

  prd:
    mode: production
    variables:
      catalog: psp_catalog
      schema: lakeflow
      source_bucket: psp-use1-prd-source
      stage_bucket: psp-use1-prd-stage
    workspace:
      host: https://dbc-xxxxx.cloud.databricks.com
    run_as:
      service_principal_name: psp-service-principal
```

## Pipeline Resource Configuration

### Transactions Pipeline (`resources/transactions_pipeline.yml`)

```yaml
resources:
  pipelines:
    transactions_pipeline:
      name: "psp-transactions-${bundle.target}"
      catalog: "${var.catalog}"
      target: "bronze"
      serverless: true
      channel: "CURRENT"
      edition: "ADVANCED"
      photon: true
      continuous: false

      libraries:
        - notebook:
            path: ../src/transactions/bronze.py
        - notebook:
            path: ../src/transactions/silver.py
        - notebook:
            path: ../src/transactions/gold.py

      configuration:
        stage_bucket: "${var.stage_bucket}"
        catalog: "${var.catalog}"
```

### Merchants Pipeline (with Notifications)

```yaml
resources:
  pipelines:
    merchants_pipeline:
      name: "psp-merchants-${bundle.target}"
      catalog: "${var.catalog}"
      target: "bronze"
      serverless: true
      channel: "CURRENT"
      edition: "ADVANCED"
      photon: true
      continuous: false

      libraries:
        - notebook:
            path: ../src/merchants/bronze.py
        - notebook:
            path: ../src/merchants/silver.py
        - notebook:
            path: ../src/merchants/gold.py

      configuration:
        stage_bucket: "${var.stage_bucket}"
        catalog: "${var.catalog}"

      notifications:
        - email_recipients:
            - data-team@company.com
          alerts:
            - on_failure
            - on_flow_failure
```

## CLI Commands

### Deploy to Dev

```bash
databricks bundle validate
databricks bundle deploy --target dev
```

### Deploy to Production

```bash
databricks bundle deploy --target prd
```

### Run Pipeline

```bash
databricks bundle run transactions_pipeline --target dev
databricks bundle run transactions_pipeline --target dev --refresh-all
```

### Destroy Resources

```bash
databricks bundle destroy --target dev
```

## Parameterization Patterns

### Access Parameters in Pipeline Code

```python
import dlt

stage_bucket = spark.conf.get("stage_bucket")

@dlt.table(name="transactions_bronze")
def transactions_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .load(f"s3://{stage_bucket}/transactions/")
    )
```

### Environment-Specific Logic

```python
import dlt

is_dev = spark.conf.get("pipelines.development", "false") == "true"

@dlt.table(name="transactions_silver")
@dlt.expect_or_drop("valid_id", "transaction_id IS NOT NULL")
def transactions_silver():
    df = dlt.read_stream("transactions_bronze")

    if is_dev:
        df = df.limit(10000)

    return df
```

## Unity Catalog Integration

```yaml
resources:
  pipelines:
    transactions_pipeline:
      catalog: "${var.catalog}"
      target: "${var.schema}"

      permissions:
        - level: CAN_VIEW
          group_name: data-consumers
        - level: CAN_RUN
          group_name: data-engineers
        - level: CAN_MANAGE
          service_principal_name: psp-admin
```

## Validation Checklist

Before deploying:

```bash
databricks bundle validate
databricks bundle validate --target prd
```

| Check | Command |
|-------|---------|
| Syntax valid | `databricks bundle validate` |
| Variables resolved | Check output for unresolved `${var.*}` |
| Permissions correct | Review `permissions` section |
| Cluster config valid | Check `clusters` autoscale settings |

## Related

- [Gold Aggregation](gold-aggregation.md) - Pipeline output
- [Pipeline Configuration](../reference/pipeline-configuration.md) - Advanced settings
- [Unity Catalog](../reference/unity-catalog.md) - Catalog integration
