# Repartition vs Coalesce

> **Purpose**: Choose the right partitioning operation.
> **MCP Validated**: 2025-01-19

## When to Use

- `repartition`: Need to increase partitions or redistribute by column
- `coalesce`: Need to reduce partitions without shuffle

## Comparison

| Feature | repartition | coalesce |
|---------|-------------|----------|
| Shuffle | Always | Never |
| Increase partitions | Yes | No |
| Decrease partitions | Yes | Yes |
| Partition by column | Yes | No |
| Data distribution | Even | Uneven possible |

## Implementation

### Repartition

```python
# By number (full shuffle, even distribution)
df.repartition(100)

# By column (hash partitioning)
df.repartition("customer_id")

# By both
df.repartition(100, "customer_id")

# Range partitioning (sorted)
df.repartitionByRange(100, "date")
```

### Coalesce

```python
# Reduce partitions without shuffle
df.coalesce(10)

# Common pattern: filter then coalesce
df.filter(col("status") == "active") \
    .coalesce(10)  # Reduce after filtering
```

## Decision Tree

```
Need to increase partitions?
  YES -> repartition(n)

Need data partitioned by column?
  YES -> repartition(col) or repartition(n, col)

Just need fewer partitions?
  YES -> coalesce(n)  (no shuffle!)
```

## Example Usage

```python
# Increase parallelism before heavy operation
df.repartition(200).groupBy("category").agg(...)

# Prepare for partitioned write
df.repartition("year", "month").write.partitionBy("year", "month").parquet("out/")

# Reduce partitions after filter (no shuffle)
df.filter(col("region") == "US") \  # 10% of data
    .coalesce(10) \                  # Reduce without shuffle
    .write.parquet("us_data/")

# Co-partition for join
df1 = df1.repartition(100, "key")
df2 = df2.repartition(100, "key")
result = df1.join(df2, "key")  # No additional shuffle
```

## Common Mistakes

### Wrong
```python
# Using repartition when coalesce would work
df.filter(...).repartition(10)  # Unnecessary shuffle!
```

### Correct
```python
# Use coalesce to reduce partitions
df.filter(...).coalesce(10)  # No shuffle
```

### Wrong
```python
# Using coalesce when you need even distribution
df.coalesce(100)  # Can't increase partitions!
```

### Correct
```python
# Use repartition to increase
df.repartition(100)  # Even distribution
```

## Quick Reference

| Scenario | Use |
|----------|-----|
| Increase partitions | `repartition(n)` |
| Decrease with even distribution | `repartition(n)` |
| Decrease after filter | `coalesce(n)` |
| Partition by column | `repartition(col)` |
| Sorted partitions | `repartitionByRange(n, col)` |

## See Also

- [shuffle-optimization.md](shuffle-optimization.md) - Reducing shuffle
- [../concepts/partitions.md](../concepts/partitions.md) - Partition basics
- [../concepts/shuffle.md](../concepts/shuffle.md) - Shuffle fundamentals
