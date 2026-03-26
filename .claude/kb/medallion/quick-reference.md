# Medallion Architecture Quick Reference

> **MCP Validated**: 2026-03-26 | **Max Lines**: 100

## Layer Cheat Sheet

| Layer | Input | Output | Quality | Update Mode |
|-------|-------|--------|---------|-------------|
| Bronze | Raw files | Delta tables | `@dlt.expect` (warn) | Append-only |
| Silver | Bronze tables | Delta tables | `@dlt.expect_or_drop` | Append/Merge |
| Gold | Silver tables | Delta tables | `@dlt.expect_or_fail` | Refresh/Merge |

## DLT Syntax Quick Reference

```python
# Bronze - Raw ingestion
@dlt.table(name="bronze_xxx")
@dlt.expect("rescued_null", "_rescued_data IS NULL")
def bronze_xxx():
    return spark.readStream.format("cloudFiles").load(path)

# Silver - Cleansed
@dlt.table(name="silver_xxx")
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
def silver_xxx():
    return dlt.read_stream("bronze_xxx").select(...)

# Silver View - Business logic
@dlt.view(name="view_xxx")
def view_xxx():
    return spark.sql("SELECT ... FROM LIVE.silver_xxx JOIN ...")

# Gold - Aggregated
@dlt.table(name="gold_xxx")
def gold_xxx():
    return dlt.read("silver_xxx").groupBy(...).agg(...)
```

## Decision Matrix

| Question | Bronze | Silver | Gold |
|----------|--------|--------|------|
| Business logic? | NO | Minimal | YES |
| Aggregation? | NO | NO | YES |
| Data quality? | Warn | Drop | Fail |
| Schema? | Inferred/Loose | Enforced | Enforced |
| Queryable by analysts? | NO | YES | YES |

## Metadata Columns

| Column | Layer | Purpose |
|--------|-------|---------|
| `_ingested_at` | Bronze | When data landed |
| `_source_file` | Bronze | Source file path |
| `_processed_at` | Silver | When cleansed |
| `_is_current` | Silver (SCD2) | Current record flag |
| `_valid_from` | Silver (SCD2) | Effective start |
| `_valid_to` | Silver (SCD2) | Effective end |

## Common Expectations

```python
# Null checks
"id IS NOT NULL"
"amount IS NOT NULL"

# Range checks
"amount >= 0"
"date >= '2020-01-01'"

# Domain checks
"status IN ('ACTIVE', 'INACTIVE', 'PENDING')"
"card_type IN ('V', 'M', 'D', 'A')"

# Format checks
"LENGTH(id) <= 50"
"email RLIKE '^[^@]+@[^@]+$'"
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Business logic in Bronze | Move to Silver/Gold |
| `SELECT *` | Explicit column list |
| Hardcode paths | Use `spark.conf.get()` |
| Skip expectations | Always add quality checks |
| Too many layers | Max: Bronze -> Silver -> Gold |

## File Naming Convention

```
{layer}_{source}_{entity}
bronze_payments_transactions
silver_payments_transactions
gold_transaction_summary
```

## Unity Catalog Structure

```
catalog_name (Catalog)
├── bronze (Schema) - Raw tables
├── silver (Schema) - Cleansed tables + views
└── gold (Schema)   - Aggregated tables
```
