# Broadcast Joins

> **Purpose**: Optimize joins with small tables using broadcast.
> **MCP Validated**: 2025-01-19

## When to Use

- One table is small (< 10MB default, up to ~100MB safe)
- Dimension table lookups
- One-to-many joins where the "one" side is small
- Avoiding shuffle overhead

## Implementation

```python
from pyspark.sql.functions import broadcast

# Explicit broadcast
result = large_df.join(broadcast(small_df), "key")

# Using hint
result = large_df.join(small_df.hint("broadcast"), "key")
```

## How It Works

```
Driver:    [Small DF] --> Broadcast --> All Executors

Executor 1: [Large Part 1] + [Broadcast] -> [Result 1]
Executor 2: [Large Part 2] + [Broadcast] -> [Result 2]
Executor N: [Large Part N] + [Broadcast] -> [Result N]
```

No shuffle required - each executor has full copy of small table.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `autoBroadcastJoinThreshold` | `10485760` (10MB) | Auto-broadcast limit |

```python
# Increase threshold (use with caution)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "52428800")  # 50MB

# Disable auto-broadcast
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```

## Example Usage

```python
# Dimension table lookup
customers = spark.read.parquet("dim_customers/")  # 5MB
transactions = spark.read.parquet("fact_transactions/")  # 500GB

# Efficient: broadcast small dimension
enriched = transactions.join(broadcast(customers), "customer_id")
```

## Common Mistakes

### Wrong
```python
# Broadcasting the large table
result = broadcast(large_df).join(small_df, "key")  # OOM risk!
```

### Correct
```python
# Always broadcast the smaller table
result = large_df.join(broadcast(small_df), "key")
```

## Caveats

- Driver must have enough memory for broadcast
- Broadcast happens once per query (cached)
- Don't broadcast tables that are actually large
- AQE can convert to broadcast at runtime if table is small

## Verifying Broadcast

```python
# Check execution plan
result.explain()
# Should show: BroadcastHashJoin
# Not: SortMergeJoin or ShuffledHashJoin
```

## Size Guidelines

| Table Size | Recommendation |
|------------|----------------|
| < 10MB | Safe to broadcast |
| 10-50MB | Consider driver memory |
| 50-100MB | Use with caution |
| > 100MB | Avoid broadcasting |

## See Also

- [join-strategies.md](join-strategies.md) - All join strategies
- [../concepts/shuffle.md](../concepts/shuffle.md) - Why shuffles are expensive
