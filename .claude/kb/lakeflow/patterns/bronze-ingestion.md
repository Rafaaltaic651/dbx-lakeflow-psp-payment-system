# Bronze Ingestion Patterns

> **MCP Validated**: 2026-03-26
> **Source**: https://docs.databricks.com/aws/en/dlt/auto-loader

## Auto Loader from Cloud Storage

The Bronze layer ingests raw files from cloud storage into Delta tables.

```python
import dlt
from pyspark.sql import functions as F

@dlt.table(
    name="transactions_bronze",
    comment="Raw transaction data from cloud storage",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true"
    }
)
def transactions_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", "/mnt/schema/transactions")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(spark.conf.get("source_path_transactions"))
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )
```

## Auto Loader Configuration

| Option | Value | Purpose |
|--------|-------|---------|
| `cloudFiles.format` | `parquet` | Source file format |
| `cloudFiles.schemaLocation` | `/mnt/schema/{type}` | Schema evolution tracking |
| `cloudFiles.inferColumnTypes` | `true` | Auto-detect column types |
| `cloudFiles.schemaHints` | `amount DECIMAL(18,2)` | Override specific types |

## Multiple Entity Patterns

### Transactions Bronze

```python
@dlt.table(name="transactions_bronze")
def transactions_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", "/mnt/schema/transactions")
        .load(spark.conf.get("path_transactions"))
        .withColumn("_ingested_at", F.current_timestamp())
    )
```

### Refunds Bronze

```python
@dlt.table(name="refunds_bronze")
def refunds_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .load(spark.conf.get("path_refunds"))
        .withColumn("_ingested_at", F.current_timestamp())
    )
```

### Merchants Bronze

```python
@dlt.table(name="merchants_bronze")
def merchants_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .load(spark.conf.get("path_merchants"))
        .withColumn("_ingested_at", F.current_timestamp())
    )
```

## Metadata Columns

Always add these columns to Bronze tables:

```python
.withColumn("_ingested_at", F.current_timestamp())
.withColumn("_source_file", F.input_file_name())
.withColumn("_processing_time", F.current_timestamp())
```

## Data Quality (Bronze)

Bronze layer uses WARN to track issues without blocking:

```python
@dlt.table(name="transactions_bronze")
@dlt.expect("valid_id", "transaction_id IS NOT NULL")
@dlt.expect("valid_date", "transaction_date IS NOT NULL")
def transactions_bronze():
    ...
```

## Related

- [Silver Cleansing](silver-cleansing.md) - Next layer
- [Python Streaming](python-streaming.md) - Streaming fundamentals
- [Expectations](expectations.md) - Data quality patterns
