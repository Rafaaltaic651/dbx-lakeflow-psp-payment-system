# Partitions

> **Purpose**: Understanding Spark partitioning fundamentals.
> **Confidence**: 0.98
> **MCP Validated**: 2025-01-19

## Overview

A partition is a logical chunk of data that can be processed independently. Partitions enable parallel processing across cluster nodes.

## Partition Diagram

```
+-----------------------------------------------------------+
|                    DataFrame (1TB)                         |
+-----------------------------------------------------------+
|  +-------+  +-------+  +-------+  +-------+               |
|  |Part 0 |  |Part 1 |  |Part 2 |  |Part N |    ...        |
|  |(128MB)|  |(128MB)|  |(128MB)|  |(128MB)|               |
|  +-------+  +-------+  +-------+  +-------+               |
|      |          |          |          |                   |
|  Executor 1  Executor 2  Executor 1  Executor 3          |
+-----------------------------------------------------------+
```

## Partition Types

| Type | When Created | Characteristics |
|------|--------------|-----------------|
| Input | Reading data | Based on file splits |
| Shuffle | After shuffle ops | Configurable count |
| Output | Writing data | Based on partition columns |

## Checking Partitions

```python
# Number of partitions
df.rdd.getNumPartitions()

# Partition distribution
from pyspark.sql.functions import spark_partition_id, count

df.groupBy(spark_partition_id().alias("partition_id")) \
    .agg(count("*").alias("record_count")) \
    .orderBy("record_count", ascending=False) \
    .show()
```

## Partition Operations

| Operation | Shuffle? | Use Case |
|-----------|----------|----------|
| `repartition(n)` | Yes | Increase/decrease partitions |
| `repartition(col)` | Yes | Partition by column |
| `coalesce(n)` | No | Decrease only |
| `repartitionByRange` | Yes | Range partitioning |

## Optimal Partition Size

```
Target: 128MB - 256MB per partition

Formula:
partition_count = data_size_mb / 128

Examples:
  1GB  -> 8 partitions
  10GB -> 80 partitions
  1TB  -> 8000 partitions
```

## Quick Reference

| Data Size | Recommended Partitions |
|-----------|------------------------|
| < 1GB | 2-8 |
| 1-10GB | 8-100 |
| 10-100GB | 100-1000 |
| > 100GB | 1000+ |

## Related

- [../patterns/repartition-vs-coalesce.md](../patterns/repartition-vs-coalesce.md) - When to use each
- [../patterns/shuffle-optimization.md](../patterns/shuffle-optimization.md) - Reducing shuffle
