# Memory Tuning

> **Purpose**: Configure executor and driver memory for optimal performance.
> **MCP Validated**: 2025-01-19

## When to Use

- OOM errors during execution
- High GC time (> 10% of task time)
- Spill to disk warnings
- Container killed by YARN

## Implementation

```python
# Executor memory
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.executor.memoryOverhead", "2g")

# Driver memory
spark.conf.set("spark.driver.memory", "4g")
spark.conf.set("spark.driver.memoryOverhead", "1g")

# Memory fractions
spark.conf.set("spark.memory.fraction", "0.6")
spark.conf.set("spark.memory.storageFraction", "0.5")

# Off-heap memory
spark.conf.set("spark.memory.offHeap.enabled", "true")
spark.conf.set("spark.memory.offHeap.size", "2g")
```

## Configuration

| Setting | Default | Tuning Guidance |
|---------|---------|-----------------|
| `executor.memory` | 1g | 4-8g per executor |
| `executor.memoryOverhead` | 10% or 384MB | Increase for PySpark |
| `memory.fraction` | 0.6 | Increase for shuffle-heavy |
| `memory.storageFraction` | 0.5 | Decrease for execution-heavy |

## Workload-Specific Settings

### Batch Processing (More Execution)
```python
spark.conf.set("spark.memory.fraction", "0.7")
spark.conf.set("spark.memory.storageFraction", "0.3")
```

### Iterative/ML (More Storage)
```python
spark.conf.set("spark.memory.fraction", "0.6")
spark.conf.set("spark.memory.storageFraction", "0.6")
```

### PySpark with Pandas
```python
spark.conf.set("spark.executor.memoryOverhead", "2g")
spark.conf.set("spark.executor.pyspark.memory", "1g")
```

## Executor Sizing Formula

```python
# Rule of thumb
num_cores = 5
memory_per_core = 2  # GB
executor_memory = num_cores * memory_per_core  # 10GB

spark.conf.set("spark.executor.cores", str(num_cores))
spark.conf.set("spark.executor.memory", f"{executor_memory}g")
spark.conf.set("spark.executor.memoryOverhead",
    f"{max(384, executor_memory * 100)}m")  # 10% or 384MB
```

## Common Errors and Fixes

| Error | Solution |
|-------|----------|
| `java.lang.OutOfMemoryError: Java heap` | Increase `executor.memory` |
| Container killed by YARN | Increase `memoryOverhead` |
| Driver OOM on collect() | Avoid collect(), use `take()` |
| High GC time | Enable off-heap, tune GC |

## Quick Checklist

- [ ] Executors have 4-8g memory
- [ ] Memory overhead is at least 10% or 384MB
- [ ] Off-heap enabled for large shuffles
- [ ] GC time is under 10% of task time

## See Also

- [gc-tuning.md](gc-tuning.md) - Garbage collection optimization
- [../concepts/memory-regions.md](../concepts/memory-regions.md) - Memory architecture
