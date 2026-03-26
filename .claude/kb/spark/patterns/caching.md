# Caching and Persistence

> **Purpose**: Strategic caching for iterative or reused DataFrames.
> **MCP Validated**: 2025-01-19

## When to Use

- DataFrame is used in multiple actions
- After expensive transformations
- Iterative algorithms (ML training)
- Interactive analysis

## When NOT to Use

- One-time use DataFrames
- Before filtering (cache after)
- Dataset won't fit in memory

## Implementation

```python
from pyspark.storagelevel import StorageLevel

# Cache (default: MEMORY_AND_DISK)
df_cached = df.filter(col("status") == "active").cache()

# Force materialization
df_cached.count()

# Use multiple times
result1 = df_cached.groupBy("category").count()
result2 = df_cached.filter(col("value") > 100)

# Clean up when done
df_cached.unpersist()
```

## Storage Levels

| Level | Memory | Disk | Serialized | Best For |
|-------|--------|------|------------|----------|
| `MEMORY_ONLY` | Yes | No | No | Fast access, fits in memory |
| `MEMORY_AND_DISK` | Yes | Yes | No | Default, safe option |
| `MEMORY_ONLY_SER` | Yes | No | Yes | Memory-constrained |
| `DISK_ONLY` | No | Yes | Yes | Very large datasets |
| `MEMORY_AND_DISK_2` | Yes | Yes | No | Replication for fault tolerance |

```python
# Custom storage level
df.persist(StorageLevel.MEMORY_ONLY_SER)
df.persist(StorageLevel.DISK_ONLY)
```

## Configuration

```python
# Clear all cached data
spark.catalog.clearCache()

# Clear specific table cache
spark.catalog.uncacheTable("table_name")

# Check if cached
spark.catalog.isCached("table_name")
```

## Best Practices

### Cache After Filter

```python
# Good: Cache filtered data
df.filter(col("status") == "active").cache()

# Bad: Cache then filter (wastes memory)
df.cache().filter(col("status") == "active")
```

### Cache After Expensive Transforms

```python
# Cache after expensive joins/aggregations
expensive_df = df1.join(df2, "key") \
    .groupBy("category") \
    .agg(sum("amount")) \
    .cache()

# Force evaluation
expensive_df.count()
```

### Always Unpersist

```python
try:
    df_cached = df.cache()
    df_cached.count()  # Materialize

    # Use cached data
    result = process(df_cached)
finally:
    df_cached.unpersist()  # Always clean up
```

## Common Mistakes

### Wrong
```python
# Caching without materializing
df.cache()
df.write.parquet("output/")  # Cache never populated!
```

### Correct
```python
# Materialize the cache first
df_cached = df.cache()
df_cached.count()  # Forces caching
df_cached.write.parquet("output/")
```

## Quick Reference

| Operation | Description |
|-----------|-------------|
| `df.cache()` | Cache with MEMORY_AND_DISK |
| `df.persist(level)` | Cache with custom level |
| `df.unpersist()` | Remove from cache |
| `df.storageLevel` | Check current storage level |

## See Also

- [memory-tuning.md](memory-tuning.md) - Memory configuration
- [../concepts/memory-regions.md](../concepts/memory-regions.md) - Storage memory region
