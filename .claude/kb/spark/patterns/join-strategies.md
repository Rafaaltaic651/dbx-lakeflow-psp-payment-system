# Join Strategies

> **Purpose**: Select optimal join strategy based on data characteristics.
> **MCP Validated**: 2025-01-19

## When to Use

- Optimizing query performance
- Choosing between broadcast, shuffle, or sort merge
- Handling large table joins

## Strategy Selection

| Strategy | Best For | Data Movement |
|----------|----------|---------------|
| Broadcast Hash | Small table < 10MB | Broadcast small side |
| Sort Merge | Large + Large tables | Shuffle both sides |
| Shuffle Hash | Medium tables | Shuffle + hash build |

## Implementation

### Broadcast Hash Join (BHJ)

```python
from pyspark.sql.functions import broadcast

# Method 1: Function (recommended)
result = large_df.join(broadcast(small_df), "key")

# Method 2: Hint
result = large_df.join(small_df.hint("broadcast"), "key")

# Method 3: SQL hint
spark.sql("""
    SELECT /*+ BROADCAST(dim) */ *
    FROM fact_table f
    JOIN dim_table dim ON f.dim_key = dim.key
""")
```

### Sort Merge Join (SMJ)

```python
# Default for large tables - no special syntax needed
result = large_df1.join(large_df2, "key")

# Force with hint if needed
result = df1.hint("merge").join(df2, "key")

# Optimize with pre-sorting
df_sorted = df.sortWithinPartitions("join_key")
```

### Shuffle Hash Join (SHJ)

```python
# Force shuffle hash join
result = df1.hint("shuffle_hash").join(df2, "key")
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `autoBroadcastJoinThreshold` | `10MB` | Auto-broadcast size limit |
| `preferSortMergeJoin` | `true` | Prefer SMJ over SHJ |

```python
# Adjust broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "52428800")  # 50MB

# Disable auto-broadcast
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```

## Join Hints Reference

| Hint | Strategy |
|------|----------|
| `BROADCAST` / `BROADCASTJOIN` | Broadcast Hash Join |
| `MERGE` / `SHUFFLE_MERGE` | Sort Merge Join |
| `SHUFFLE_HASH` | Shuffle Hash Join |
| `SHUFFLE_REPLICATE_NL` | Nested Loop Join |

## Best Practices

```python
# 1. Filter before join
df1.filter(col("status") == "active") \
    .join(df2.filter(col("valid") == True), "key")

# 2. Select only needed columns
df1.select("key", "value1") \
    .join(df2.select("key", "value2"), "key")

# 3. Use broadcast for dimension tables
fact_df.join(broadcast(dim_df), "dim_key")
```

## Verifying Join Strategy

```python
# Check physical plan
df1.join(df2, "key").explain("formatted")

# Look for:
# - BroadcastHashJoin (good for small tables)
# - SortMergeJoin (expected for large tables)
# - BroadcastNestedLoopJoin (avoid - expensive)
```

## See Also

- [broadcast-joins.md](broadcast-joins.md) - Deep dive on broadcasting
- [data-skew.md](data-skew.md) - Handling skewed joins
- [../concepts/shuffle.md](../concepts/shuffle.md) - Shuffle fundamentals
