# Data Skew Handling

> **Purpose**: Detect and resolve skewed data distributions.
> **MCP Validated**: 2025-01-19

## When to Use

- Some tasks take much longer than others
- Spark UI shows uneven task durations
- OOM errors on specific partitions
- Joins on columns with hot keys

## Detecting Skew

```python
from pyspark.sql.functions import spark_partition_id, count, desc

# Check partition sizes
df.groupBy(spark_partition_id().alias("partition")) \
    .agg(count("*").alias("count")) \
    .orderBy("count", ascending=False) \
    .show()

# Check key distribution
df.groupBy("join_key") \
    .count() \
    .orderBy(desc("count")) \
    .show(20)

# Statistics (look for max >> mean)
df.groupBy("join_key").count().describe().show()
```

## Solutions

### 1. AQE Skew Join (Recommended)

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

### 2. Broadcast for Skew

```python
from pyspark.sql.functions import broadcast

# If lookup table is small enough
if df_small.count() < 10_000_000:
    result = df_skewed.join(broadcast(df_small), "key")
```

### 3. Salting Technique

```python
from pyspark.sql.functions import concat, lit, rand, explode, array

SALT_BUCKETS = 10

# Salt the skewed table
df_skewed_salted = df_skewed.withColumn(
    "salted_key",
    concat(col("key"), lit("_"), (rand() * SALT_BUCKETS).cast("int"))
)

# Explode the lookup table
df_lookup_exploded = df_lookup.withColumn(
    "salt",
    explode(array([lit(i) for i in range(SALT_BUCKETS)]))
).withColumn(
    "salted_key",
    concat(col("key"), lit("_"), col("salt"))
).drop("salt")

# Join on salted key
result = df_skewed_salted.join(df_lookup_exploded, "salted_key") \
    .drop("salted_key")
```

### 4. Filter Hot Keys

```python
# Separate hot keys for special handling
hot_keys = ["key1", "key2"]

df_normal = df.filter(~col("key").isin(hot_keys))
df_hot = df.filter(col("key").isin(hot_keys))

# Process separately
result_normal = df_normal.join(lookup_df, "key")
result_hot = df_hot.join(broadcast(lookup_df.filter(col("key").isin(hot_keys))), "key")

# Combine
result = result_normal.union(result_hot)
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `skewJoin.enabled` | `true` | Enable skew handling |
| `skewJoin.skewedPartitionFactor` | `5` | Skew threshold (5x median) |
| `skewJoin.skewedPartitionThresholdInBytes` | `256MB` | Min size for skew detection |

## Quick Decision Tree

```
Is one side small enough to broadcast?
  YES -> Use broadcast join
  NO  -> Is AQE enabled?
           YES -> Let AQE handle it
           NO  -> Use salting technique
```

## See Also

- [aqe.md](aqe.md) - Adaptive Query Execution
- [join-strategies.md](join-strategies.md) - Join optimization
- [../concepts/partitions.md](../concepts/partitions.md) - Partition basics
