# Tables vs Views

> **MCP Validated**: 2026-03-26 | **Max Lines**: 150

## The Decision

**Table** = Persisted data (storage cost, fast queries)
**View** = Computed on read (no storage, compute on query)

## Quick Decision Matrix

| Scenario | Use | Rationale |
|----------|-----|-----------|
| Raw ingestion | **Table** | Need persistence, incremental |
| 1:1 transformation | **Table** | Performance, quality tracking |
| Complex joins (prototype) | **View** | Test before materializing |
| Complex joins (production) | **Table** | If view is too slow |
| Business aggregations | **Table** | Pre-computed for dashboards |
| Ad-hoc exploration | **View** | Flexibility, no storage |
| Existing SQL logic (migration) | **View** | Quick port, optimize later |

## Lakeflow Options

### Streaming Table
```python
@dlt.table(name="silver_xxx")
def silver_xxx():
    return dlt.read_stream("bronze_xxx")  # Incremental
```
- Persisted, incremental processing
- Best for: Bronze, Silver L1

### Materialized View
```python
@dlt.table(name="gold_xxx")
def gold_xxx():
    return dlt.read("silver_xxx")  # Batch read
```
- Persisted, full refresh or incremental
- Best for: Gold aggregations

### View (Non-Materialized)
```python
@dlt.view(name="view_xxx")
def view_xxx():
    return spark.sql("SELECT ... FROM LIVE.silver_xxx")
```
- Not persisted, computed on read
- Best for: Silver L2 domain views, joins

## When to Use Views

### Use Views When:

1. **Prototyping joins** - Test before committing to storage
2. **Porting existing SQL** - Migrate SQL views to Lakeflow
3. **Flexible access patterns** - Different consumers need different joins
4. **Low query frequency** - Not accessed often enough to justify storage
5. **Simple transformations** - Column renaming, filtering

### Example: Domain View
```python
@dlt.view(name="view_transaction_detail")
def view_transaction_detail():
    return spark.sql("""
        SELECT
            t.transaction_id,
            t.amount,
            t.currency_code,
            c.customer_name
        FROM LIVE.silver_transactions t
        LEFT JOIN LIVE.silver_customers c
            ON t.customer_id = c.customer_id
    """)
```

## When to Use Tables

### Use Tables When:

1. **Raw ingestion** - Always persist raw data
2. **Data quality tracking** - Need expectation metrics
3. **High query frequency** - Dashboard queries many times/day
4. **Complex transformations** - Expensive to recompute
5. **Time travel needed** - Need to query historical versions

### Example: High-Frequency Gold Table
```python
@dlt.table(
    name="gold_daily_settlement",
    comment="Pre-aggregated for dashboard (queried 1000x/day)"
)
def gold_daily_settlement():
    return (
        dlt.read("silver_transactions")
        .groupBy("merchant_id", "settlement_date")
        .agg(sum("amount").alias("total_amount"))
    )
```

## Migration Strategy: View -> Table

Start with view, materialize if needed:

```python
# Phase 1: View (test performance)
@dlt.view(name="view_settlement_summary")
def view_settlement_summary():
    return spark.sql("SELECT ... complex join ...")

# Phase 2: If slow, convert to table
@dlt.table(name="silver_settlement_summary")
def silver_settlement_summary():
    return spark.sql("SELECT ... complex join ...")
```

## Recommended Strategy

| Layer | Type | Rationale |
|-------|------|-----------|
| Bronze | **Streaming Tables** | Auto Loader ingestion |
| Silver L1 | **Streaming Tables** | Cleaned, typed data |
| Silver L2 | **Views** | Domain join logic |
| Gold | **Materialized Tables** | Dashboard performance |

```
Bronze (Raw) -> Silver Tables -> Silver Views -> Gold Tables
     ↑                ↑              ↑              ↑
  Auto Loader     Cleansing     Domain Logic    Aggregations
```
