# Adaptive Query Execution (AQE)

> **Purpose**: Enable and configure Spark's runtime optimization.
> **MCP Validated**: 2025-01-19

## When to Use

- Queries with unpredictable data distributions
- Joins where table sizes are unknown at planning time
- Jobs suffering from data skew
- Any Spark 3.0+ workload (enabled by default in 3.2+)

## Implementation

```python
# Enable AQE (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")

# Coalesce small partitions after shuffle
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionSize", "64MB")
spark.conf.set("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "400")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "256MB")

# Handle skewed joins
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# Dynamic join strategy selection
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `adaptive.enabled` | `true` (3.2+) | Master switch for AQE |
| `coalescePartitions.enabled` | `true` | Merge small partitions |
| `skewJoin.enabled` | `true` | Handle skewed data |
| `skewJoin.skewedPartitionFactor` | `5` | Skew threshold multiplier |
| `advisoryPartitionSizeInBytes` | `64MB` | Target partition size |

## AQE Features

### 1. Dynamic Coalescing
Merges small post-shuffle partitions:
```
Before AQE: 200 partitions, many < 1MB
After AQE:  50 partitions, all ~64MB
```

### 2. Dynamic Join Selection
Converts Sort Merge Join to Broadcast when runtime stats show small table:
```
Planned: SortMergeJoin (estimated 100MB)
Runtime: BroadcastHashJoin (actual 8MB)
```

### 3. Skew Join Handling
Splits skewed partitions automatically:
```
Before: 1 partition with 10GB, 199 with 100MB
After:  Skewed partition split into multiple tasks
```

## Example Usage

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("AQE-Enabled-Job") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .getOrCreate()

# AQE optimizes automatically at runtime
result = large_df.join(medium_df, "key").groupBy("category").count()
```

## Verifying AQE is Active

```python
# Check in physical plan
df.explain("formatted")
# Look for "AdaptiveSparkPlan" at the top

# Or check configuration
spark.conf.get("spark.sql.adaptive.enabled")
```

## See Also

- [shuffle-optimization.md](shuffle-optimization.md) - Reducing shuffle cost
- [join-strategies.md](join-strategies.md) - Join optimization
- [data-skew.md](data-skew.md) - Handling skewed data
