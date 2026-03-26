# Shuffle Operations

> **Purpose**: Understanding what triggers shuffles and their impact.
> **Confidence**: 0.98
> **MCP Validated**: 2025-01-19

## Overview

A shuffle redistributes data across partitions. It is the most expensive operation in Spark, involving disk I/O, network transfer, and serialization.

## Shuffle Process

```
+-----------------------------------------------------------+
|                      Shuffle Process                       |
+-----------------------------------------------------------+
|  Map Side                           Reduce Side            |
|  +-----------+                     +-----------+           |
|  | Partition | -----------------> | Partition |           |
|  |  (Task 1) |    Shuffle         |  (Task A) |           |
|  +-----------+    Write/Read      +-----------+           |
|  +-----------+                     +-----------+           |
|  | Partition | -----------------> | Partition |           |
|  |  (Task 2) |                    |  (Task B) |           |
|  +-----------+                     +-----------+           |
|                                                            |
|  1. Map tasks partition output data                        |
|  2. Data written to local disk (shuffle write)             |
|  3. Reduce tasks fetch data from all mappers               |
|  4. Data read into memory (shuffle read)                   |
+-----------------------------------------------------------+
```

## What Triggers Shuffle?

### Wide Transformations (Shuffle)
- `groupBy`, `groupByKey`
- `reduceByKey`, `aggregateByKey`
- `join`, `cogroup`
- `sortBy`, `orderBy`
- `repartition`
- `distinct`

### Narrow Transformations (No Shuffle)
- `map`, `filter`, `flatMap`
- `select`, `withColumn`
- `union` (if same partitioner)
- `coalesce` (decrease only)

## Quick Reference

| Operation | Shuffle? | Notes |
|-----------|----------|-------|
| `select` | No | Column projection |
| `filter` | No | Row filtering |
| `groupBy` | Yes | Data redistribution |
| `join` | Usually | Unless broadcast |
| `orderBy` | Yes | Global sort |
| `coalesce` | No | Reduce partitions |
| `repartition` | Yes | Full redistribution |

## Configuration

```python
spark.sql.shuffle.partitions = 200    # Shuffle partition count
spark.shuffle.compress = true          # Compress shuffle data
spark.io.compression.codec = "lz4"    # Compression codec
```

## Monitoring

In Spark UI, look for:
- **Shuffle Read**: Data pulled from other executors
- **Shuffle Write**: Data written for other stages
- **Spill (Disk)**: Memory overflow to disk

## Related

- [partitions.md](partitions.md) - Partition basics
- [../patterns/shuffle-optimization.md](../patterns/shuffle-optimization.md) - Reducing shuffle cost
