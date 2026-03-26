# Grain and Granularity

> **MCP Validated**: 2026-03-26 | **Max Lines**: 150

## The Critical Question

**"What is ONE row in this table?"**

If you can't answer this clearly, your design needs work.

## Grain by Layer

| Layer | Typical Grain | Example |
|-------|---------------|---------|
| Bronze | Source record | 1 row = 1 line from source file |
| Silver L1 | Source record (cleaned) | 1 row = 1 transaction |
| Silver L2 | Domain entity | 1 row = 1 customer (current) |
| Gold | Business metric | 1 row = 1 merchant + 1 day |

## Grain Selection Rules

### Rule 1: Preserve Source Grain in Bronze/Silver L1

```
Source file has 1000 transactions
     ↓
Bronze should have ~1000 rows
     ↓
Silver L1 should have ~1000 rows (minus dropped bad rows)
```

### Rule 2: Domain Grain in Silver L2

Silver L2 (domain tables) consolidate to business entities:

```
Silver L1: 1 row per transaction
Silver L2: 1 row per merchant (SCD2 = multiple rows for history)
```

### Rule 3: Aggregate Grain in Gold

Gold reduces rows through aggregation:

```
Silver: 1,000,000 transactions
Gold:   10,000 daily summaries (merchants x days)
```

## Common Grain Patterns

### Transaction Grain
```
1 row = 1 transaction at 1 point in time

Primary Key: transaction_id
Example: Payment events, authorization requests
```

### Entity Grain (Current State)
```
1 row = 1 entity (most recent version)

Primary Key: entity_id
Example: Merchant master (SCD Type 1)
```

### Entity Grain (Full History)
```
1 row = 1 entity at 1 version

Primary Key: entity_id + valid_from
Example: Merchant history (SCD Type 2)
```

### Aggregate Grain
```
1 row = 1 combination of dimensions

Primary Key: dim1 + dim2 + ... + time_period
Example: merchant_id + date + currency
```

## Grain Mistakes to Avoid

### Mistake 1: Accidental Duplication
```python
# WRONG - Creates duplicates if joining wrong
table_a.join(table_b, "entity_id")  # 1:M join = more rows!

# RIGHT - Understand cardinality first
# If table_b has multiple rows per entity, aggregate first
table_b_agg = table_b.groupBy("entity_id").agg(...)
table_a.join(table_b_agg, "entity_id")
```

### Mistake 2: Mixed Grain
```python
# WRONG - Mixing transaction and daily grain
SELECT
    transaction_id,      # Transaction grain
    daily_total          # Daily grain (aggregated)
FROM ...

# RIGHT - Pick one grain
# Option A: Transaction grain with lookup
# Option B: Daily grain with aggregation
```

### Mistake 3: Undefined Grain
```
Table: "merchant_activity"
What is one row?
- One merchant?
- One merchant per day?
- One transaction?

ALWAYS document the grain in table comments.
```

## Grain Documentation Template

```python
@dlt.table(
    name="silver_merchants",
    comment="""
    Merchant master data.
    GRAIN: 1 row per merchant_id (current state, SCD Type 1)
    PRIMARY KEY: merchant_id
    """
)
```

## Join Cardinality Reference

| Join Type | Result Grain |
|-----------|--------------|
| 1:1 | Same as input |
| 1:M | Increases rows (M per 1) |
| M:1 | Same as M side |
| M:N | Cartesian explosion (avoid!) |

**Always verify grain after joins.**
