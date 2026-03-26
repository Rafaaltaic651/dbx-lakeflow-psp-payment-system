# Bronze Ingestion Pattern

> **MCP Validated**: 2026-03-26 | **Max Lines**: 200

## Purpose

Ingest raw data from cloud storage into Delta tables with minimal transformation.

## Pattern: Auto Loader from S3

### Basic Template

```python
import dlt
from pyspark.sql.functions import current_timestamp, input_file_name

@dlt.table(
    name="bronze_{source}_{entity}",
    comment="Raw {entity} data from {source}",
    table_properties={
        "quality": "bronze",
        "source": "s3://bucket/path/"
    }
)
@dlt.expect("rescued_data_null", "_rescued_data IS NULL")
def bronze_source_entity():
    source_path = spark.conf.get("bronze_path_{source}_{entity}")

    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .option("cloudFiles.schemaLocation", f"/checkpoints/bronze_{source}_{entity}/schema")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(source_path)
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_file", input_file_name())
    )
```

## Configuration Options

### Essential Options

| Option | Value | Purpose |
|--------|-------|---------|
| `cloudFiles.format` | `parquet` | Source format |
| `cloudFiles.schemaLocation` | `/checkpoints/...` | Schema tracking |
| `cloudFiles.inferColumnTypes` | `true` | Auto-detect types |

### Advanced Options

| Option | Value | Purpose |
|--------|-------|---------|
| `cloudFiles.schemaEvolutionMode` | `addNewColumns` | Handle new columns |
| `cloudFiles.maxFilesPerTrigger` | `1000` | Batch size control |
| `cloudFiles.useNotifications` | `true` | Use S3 events (faster) |

## Metadata Columns

Always add these columns:

```python
.withColumn("_ingested_at", current_timestamp())
.withColumn("_source_file", input_file_name())
```

## Data Quality at Bronze

**Use WARN, not DROP at Bronze:**

```python
# CORRECT - Warn but keep data
@dlt.expect("rescued_null", "_rescued_data IS NULL")

# WRONG - Don't drop at Bronze
@dlt.expect_or_drop(...)  # Save this for Silver
```

## Multi-Table Bronze Pattern

For sources with multiple entity types:

```python
# Bronze for each entity type
BRONZE_TABLES = [
    ("payments", "transactions"),
    ("payments", "refunds"),
    ("merchants", "profiles"),
    ("merchants", "terminals"),
]

for source, entity in BRONZE_TABLES:
    @dlt.table(name=f"bronze_{source}_{entity}")
    def create_bronze():
        return (
            spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "parquet")
            .load(spark.conf.get(f"path_{source}_{entity}"))
            .withColumn("_ingested_at", current_timestamp())
        )
```

## Checkpoint Management

Checkpoints track which files have been processed:

```
/checkpoints/
├── payments/
│   ├── transactions/
│   │   └── schema/     # Schema tracking
│   └── refunds/
├── merchants/
│   └── profiles/
└── ...
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Schema mismatch | Source schema changed | Clear schema checkpoint |
| Missing files | Path incorrect | Verify S3 path exists |
| Slow ingestion | Too many small files | Use `maxFilesPerTrigger` |
| Duplicate data | Checkpoint corrupted | Clear checkpoint, reprocess |
