# Layer Responsibilities

> **MCP Validated**: 2026-03-26 | **Max Lines**: 150

## The Golden Rule

**Each layer has ONE job. Don't mix responsibilities.**

## Bronze Layer

### Responsibility
Capture raw data exactly as received, preserving source fidelity.

### What Belongs Here
- Raw file ingestion (Auto Loader)
- Schema inference or minimal schema enforcement
- Metadata columns (`_ingested_at`, `_source_file`)
- Rescue column for malformed data

### What Does NOT Belong Here
- Business logic
- Type casting (beyond basic inference)
- Joins
- Aggregations
- Data quality filtering (only warn)

### Example
```python
@dlt.table(name="bronze_transactions")
@dlt.expect("rescued_null", "_rescued_data IS NULL")
def bronze_transactions():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .load(spark.conf.get("source_path"))
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_file", input_file_name())
    )
```

## Silver Layer

### Responsibility
Cleanse, validate, and conform data for analytical consumption.

### What Belongs Here
- Data type enforcement
- Null handling
- Data quality expectations (DROP bad rows)
- Column renaming/standardization
- Simple lookups/decodes
- SCD Type 2 for dimensions

### What Does NOT Belong Here
- Heavy aggregations
- Complex business calculations
- Dashboard-specific transformations

### Silver L1 vs L2 (Optional Split)

| Sublayer | Purpose |
|----------|---------|
| Silver L1 | 1:1 from Bronze, cleaned and typed |
| Silver L2 | Domain views joining L1 tables |

### Example (L1 Table)
```python
@dlt.table(name="silver_transactions")
@dlt.expect_or_drop("valid_id", "transaction_id IS NOT NULL")
@dlt.expect_or_drop("valid_amount", "amount IS NOT NULL")
def silver_transactions():
    return (
        dlt.read_stream("bronze_transactions")
        .select(
            col("transaction_id").cast("string"),
            col("amount").cast("decimal(18,2)"),
            col("currency_code"),
            col("status").cast("string"),
            current_timestamp().alias("_processed_at")
        )
    )
```

### Example (L2 View)
```python
@dlt.view(name="view_transaction_detail")
def view_transaction_detail():
    return spark.sql("""
        SELECT t.*, c.customer_name
        FROM LIVE.silver_transactions t
        LEFT JOIN LIVE.silver_customers c
            ON t.customer_id = c.customer_id
    """)
```

## Gold Layer

### Responsibility
Deliver business-ready, aggregated data for dashboards and reports.

### What Belongs Here
- Aggregations (SUM, COUNT, AVG)
- Business KPIs
- Denormalized star schemas
- Pre-computed metrics
- Time-series aggregations

### What Does NOT Belong Here
- Raw data
- Record-level detail (unless summary + detail)

### Example
```python
@dlt.table(name="gold_daily_summary")
def gold_daily_summary():
    return (
        dlt.read("silver_transactions")
        .groupBy("merchant_id", "transaction_date")
        .agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_amount")
        )
    )
```

## Decision Tree

```
Is it raw data from source?
├── YES -> BRONZE
└── NO -> Is it record-level cleaned data?
         ├── YES -> SILVER
         └── NO -> Is it aggregated/business metrics?
                  ├── YES -> GOLD
                  └── NO -> Probably SILVER VIEW
```
