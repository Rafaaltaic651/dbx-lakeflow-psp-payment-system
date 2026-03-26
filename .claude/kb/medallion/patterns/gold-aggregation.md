# Gold Aggregation Pattern

> **MCP Validated**: 2026-03-26 | **Max Lines**: 200

## Purpose

Create business-ready aggregated tables for dashboards and reporting.

## Pattern: Basic Aggregation

### Template

```python
import dlt
from pyspark.sql.functions import sum, count, avg, max, min, countDistinct

@dlt.table(
    name="gold_{domain}_{metric}",
    comment="Business aggregation: {description}",
    table_properties={"quality": "gold"}
)
def gold_domain_metric():
    return (
        dlt.read("silver_{source}_{entity}")
        .groupBy("dimension1", "dimension2")
        .agg(
            count("*").alias("record_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount")
        )
    )
```

## Example Gold Tables

### Merchant Summary

```python
@dlt.table(
    name="gold_merchant_summary",
    comment="Merchant counts by category and region for executive dashboard"
)
def gold_merchant_summary():
    return (
        dlt.read("silver_merchants")
        .groupBy("category", "region", "state")
        .agg(
            countDistinct("merchant_id").alias("merchant_count"),
            count("*").alias("record_count"),
            max("_processed_at").alias("last_updated")
        )
    )
```

### Daily Settlement Summary

```python
@dlt.table(
    name="gold_daily_settlement",
    comment="Daily settlement totals by merchant for operations dashboard"
)
def gold_daily_settlement():
    return (
        dlt.read("silver_transactions")
        .withColumn("settlement_date", to_date("settlement_datetime"))
        .groupBy("merchant_id", "settlement_date", "card_type")
        .agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_transaction"),
            min("amount").alias("min_transaction"),
            max("amount").alias("max_transaction")
        )
    )
```

### Authorization Metrics

```python
@dlt.table(
    name="gold_auth_metrics",
    comment="Authorization success rates by merchant and card type"
)
def gold_auth_metrics():
    return (
        dlt.read("silver_authorizations")
        .withColumn("auth_date", to_date("authorization_datetime"))
        .groupBy("merchant_id", "auth_date", "card_type")
        .agg(
            count("*").alias("auth_count"),
            sum(when(col("response_code") == "00", 1).otherwise(0)).alias("approved_count"),
            sum("authorized_amount").alias("total_authorized"),
            avg("authorized_amount").alias("avg_authorized")
        )
        .withColumn("approval_rate",
            col("approved_count") / col("auth_count") * 100
        )
    )
```

## Aggregation Functions Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `count("*")` | Row count | Transaction count |
| `countDistinct(col)` | Unique values | Unique merchants |
| `sum(col)` | Total | Total amount |
| `avg(col)` | Average | Avg transaction |
| `min(col)` / `max(col)` | Range | Date range |
| `first(col)` / `last(col)` | Sample value | Latest status |
| `collect_list(col)` | Array of values | All statuses |

## Time-Based Aggregations

### Daily Grain
```python
.withColumn("report_date", to_date("timestamp"))
.groupBy("report_date", ...)
```

### Weekly Grain
```python
.withColumn("week_start", date_trunc("week", "timestamp"))
.groupBy("week_start", ...)
```

### Monthly Grain
```python
.withColumn("month", date_trunc("month", "timestamp"))
.groupBy("month", ...)
```

## Data Quality at Gold

Use `expect_or_fail` for critical business rules:

```python
@dlt.table(name="gold_revenue_summary")
@dlt.expect_or_fail("positive_revenue", "total_revenue >= 0")
@dlt.expect_or_fail("has_data", "transaction_count > 0")
def gold_revenue_summary():
    ...
```

## Performance Optimization

### Z-Ordering for Query Performance
```python
@dlt.table(
    name="gold_daily_settlement",
    table_properties={
        "quality": "gold",
        "delta.autoOptimize.optimizeWrite": "true",
        "pipelines.autoOptimize.zOrderCols": "merchant_id,settlement_date"
    }
)
```

### Partitioning for Large Tables
```python
@dlt.table(
    name="gold_transaction_history",
    partition_cols=["year", "month"]
)
def gold_transaction_history():
    return (
        dlt.read("silver_transactions")
        .withColumn("year", year("transaction_date"))
        .withColumn("month", month("transaction_date"))
        .groupBy("year", "month", "merchant_id")
        .agg(...)
    )
```

## Gold Table Naming Convention

```
gold_{domain}_{metric}_{grain}

Examples:
- gold_merchant_summary         (merchant dimension summary)
- gold_settlement_daily         (daily grain settlements)
- gold_auth_hourly              (hourly grain authorizations)
- gold_revenue_monthly          (monthly grain revenue)
```

## Gold Checklist

```text
[ ] Clear grain documented in comment
[ ] Appropriate aggregations for use case
[ ] expect_or_fail for critical metrics
[ ] Z-ordering for common query patterns
[ ] Partitioning if table will be large
[ ] last_updated timestamp included
```
