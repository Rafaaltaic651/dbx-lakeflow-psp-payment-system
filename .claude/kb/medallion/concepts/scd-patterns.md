# Slowly Changing Dimension (SCD) Patterns

> **MCP Validated**: 2026-03-26 | **Max Lines**: 150

## What is SCD?

**Slowly Changing Dimensions** handle how dimension data (like merchants, customers) changes over time.

## SCD Types Comparison

| Type | History | Storage | Complexity | Use Case |
|------|---------|---------|------------|----------|
| **Type 0** | None | Lowest | Simplest | Static data (never changes) |
| **Type 1** | Overwrite | Low | Simple | Current state only |
| **Type 2** | Full history | Higher | Complex | Need historical analysis |
| **Type 3** | Previous + Current | Medium | Medium | Need last change only |

## SCD Type 1: Overwrite

**What:** Replace old values with new values. No history preserved.

**When to Use:**
- Only current state matters
- Corrections to data entry errors
- Non-critical attributes

**Lakeflow Implementation:**
```python
dlt.create_streaming_table("silver_merchants")

dlt.apply_changes(
    target="silver_merchants",
    source="bronze_merchants",
    keys=["merchant_id"],
    sequence_by="updated_at",
    stored_as_scd_type=1  # Overwrite
)
```

**Result:**
```
| merchant_id | name            | city    |
|-------------|-----------------|---------|
| 12345       | ACME COFFEE NEW | BOULDER |  <- Only current
```

## SCD Type 2: Full History

**What:** Create new row for each change. Track valid periods.

**When to Use:**
- Need to analyze historical states
- Audit/compliance requirements
- "What was the merchant status on date X?"

**Lakeflow Implementation:**
```python
dlt.create_streaming_table("silver_merchants_history")

dlt.apply_changes(
    target="silver_merchants_history",
    source="bronze_merchants",
    keys=["merchant_id"],
    sequence_by="updated_at",
    stored_as_scd_type=2,  # Full history
    track_history_column_list=[
        "name",
        "status",
        "category",
        "city",
        "state"
    ]
)
```

**Result:**
```
| merchant_id | name            | city   | __START_AT | __END_AT   |
|-------------|-----------------|--------|------------|------------|
| 12345       | ACME COFFEE     | DENVER | 2024-01-01 | 2024-06-15 |
| 12345       | ACME COFFEE NEW | BOULDER| 2024-06-15 | NULL       | <- Current
```

**Querying Current State:**
```sql
SELECT * FROM silver_merchants_history
WHERE __END_AT IS NULL
```

**Querying Point-in-Time:**
```sql
SELECT * FROM silver_merchants_history
WHERE '2024-03-01' BETWEEN __START_AT AND COALESCE(__END_AT, '9999-12-31')
```

## SCD Type 2 Columns (Lakeflow Auto-Generated)

| Column | Description |
|--------|-------------|
| `__START_AT` | When this version became effective |
| `__END_AT` | When this version expired (NULL = current) |

## Best Practices

1. **Choose tracked columns wisely** - Don't track all columns, only business-critical ones
2. **Index on keys + __END_AT** - For efficient current-state queries
3. **Consider Type 1 first** - Only use Type 2 if history is truly needed
4. **Document the decision** - Explain why SCD type was chosen

## Common Mistake

```python
# WRONG - Tracking too many columns creates excessive history
track_history_column_list=["*"]  # Every change = new row

# RIGHT - Track only business-critical columns
track_history_column_list=[
    "status",     # Critical for reporting
    "category",   # Affects business rules
    "name"        # Customer-facing
]
```
