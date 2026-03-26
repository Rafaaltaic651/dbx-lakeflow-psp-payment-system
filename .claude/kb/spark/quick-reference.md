# Spark Quick Reference

> Fast lookup tables. For details, see linked files.

## Essential Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `spark.sql.adaptive.enabled` | `true` | Enable AQE |
| `spark.sql.shuffle.partitions` | `200` | Shuffle partition count |
| `spark.sql.autoBroadcastJoinThreshold` | `10MB` | Broadcast join threshold |
| `spark.executor.memory` | `4-8g` | Executor heap size |
| `spark.executor.cores` | `4-5` | Cores per executor |

## Memory Allocation

| Region | Default | Purpose |
|--------|---------|---------|
| Reserved | 300MB | System overhead |
| User Memory | 40% | Data structures |
| Storage | 30% | Cache |
| Execution | 30% | Shuffle/join |

## Partition Guidelines

| Data Size | Partitions | Target Size |
|-----------|------------|-------------|
| 1GB | 8-10 | 128MB |
| 10GB | 80-100 | 128MB |
| 100GB | 800-1000 | 128MB |

## Join Strategies

| Strategy | Best For | Trigger |
|----------|----------|---------|
| Broadcast Hash | Small < 10MB | Auto or `broadcast()` |
| Sort Merge | Large + Large | Default |
| Shuffle Hash | Medium tables | Let Spark decide |

## Common Operations

| Operation | Causes Shuffle? |
|-----------|-----------------|
| `select`, `filter` | No |
| `groupBy`, `agg` | Yes |
| `join` | Usually yes |
| `repartition` | Yes |
| `coalesce` | No (reduce only) |

## Storage Levels

| Level | Memory | Disk | Best For |
|-------|--------|------|----------|
| MEMORY_ONLY | Yes | No | Fast access |
| MEMORY_AND_DISK | Yes | Yes | Large datasets |
| DISK_ONLY | No | Yes | Huge datasets |

## AQE Features (Spark 3.0+)

| Feature | Benefit |
|---------|---------|
| Dynamic Coalescing | Merges small partitions |
| Dynamic Join | Switches to broadcast if small |
| Skew Join | Splits skewed partitions |

## Performance Red Flags

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Skewed tasks | Data skew | Salting, AQE |
| Disk spill | Low memory | More executors |
| Long GC | Memory pressure | Tune heap |
| Slow shuffle | Too many partitions | Reduce count |

## Diagnostic Commands

```python
df.explain("formatted")          # View plan
df.rdd.getNumPartitions()        # Partition count
spark.catalog.clearCache()       # Clear cache
```

## Related Files

| Topic | Path |
|-------|------|
| Full Index | `index.md` |
| AQE | `patterns/aqe.md` |
| Memory | `patterns/memory-tuning.md` |
| Troubleshooting | `reference/troubleshooting.md` |
