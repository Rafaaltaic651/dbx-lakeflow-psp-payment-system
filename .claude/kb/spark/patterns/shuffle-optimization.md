# Shuffle Optimization

> **Purpose**: Reduce shuffle cost and improve performance.
> **MCP Validated**: 2025-01-19

## When to Use

- High shuffle read/write in Spark UI
- Slow stages with Exchange operators
- Network-bound jobs
- Jobs with many shuffle partitions

## Implementation

### Reduce Shuffle Data

```python
# 1. Filter early
df.filter(col("status") == "active") \
    .groupBy("category") \
    .agg(sum("amount"))

# 2. Aggregate before join
summary = df.groupBy("key").agg(sum("value").alias("total"))
result = dim_table.join(summary, "key")

# 3. Broadcast small tables
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "key")

# 4. Select only needed columns
df.select("key", "value").groupBy("key").agg(sum("value"))
```

### Optimize Shuffle Partitions

```python
# Set optimal shuffle partitions
total_cores = num_executors * cores_per_executor
spark.conf.set("spark.sql.shuffle.partitions", str(total_cores * 2))

# With AQE, let Spark manage it
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `shuffle.partitions` | `200` | Post-shuffle partition count |
| `shuffle.compress` | `true` | Compress shuffle data |
| `io.compression.codec` | `lz4` | Compression codec |
| `shuffle.file.buffer` | `32k` | Buffer for shuffle writes |
| `reducer.maxSizeInFlight` | `48m` | Max size of map outputs to fetch |

```python
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.shuffle.compress", "true")
spark.conf.set("spark.io.compression.codec", "lz4")
spark.conf.set("spark.shuffle.file.buffer", "64k")
spark.conf.set("spark.reducer.maxSizeInFlight", "96m")
```

## Patterns to Avoid Shuffle

### Use Coalesce Instead of Repartition

```python
# Good: No shuffle when reducing partitions
df.coalesce(10)

# Causes shuffle
df.repartition(10)
```

### Co-partition for Joins

```python
# Pre-partition both DataFrames by join key
df1 = df1.repartition(100, "customer_id")
df2 = df2.repartition(100, "customer_id")

# Join without additional shuffle
result = df1.join(df2, "customer_id")
```

### Use Bucketing

```python
# Write bucketed tables
df.write.bucketBy(100, "customer_id") \
    .sortBy("customer_id") \
    .saveAsTable("bucketed_table")

# Subsequent joins avoid shuffle
df1 = spark.table("bucketed_table_1")
df2 = spark.table("bucketed_table_2")
result = df1.join(df2, "customer_id")  # No shuffle!
```

## Monitoring Shuffle

```
Spark UI -> Stages -> Shuffle Read/Write columns

Key Metrics:
- Shuffle Write: Data written for other stages
- Shuffle Read: Data pulled from other executors
- Spill: Memory overflow to disk (bad)
```

## Quick Checklist

- [ ] Filters applied before aggregations
- [ ] Columns selected early
- [ ] Small tables broadcasted
- [ ] Shuffle partitions tuned for cluster size
- [ ] AQE enabled for dynamic optimization

## See Also

- [aqe.md](aqe.md) - Adaptive Query Execution
- [../concepts/shuffle.md](../concepts/shuffle.md) - Shuffle fundamentals
- [../concepts/partitions.md](../concepts/partitions.md) - Partition basics
