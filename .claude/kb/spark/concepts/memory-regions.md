# Memory Regions

> **Purpose**: Understanding Spark executor memory architecture.
> **Confidence**: 0.98
> **MCP Validated**: 2025-01-19

## Overview

Spark divides executor memory into distinct regions for different purposes. Understanding this architecture is essential for tuning memory-intensive jobs.

## Memory Layout

```
+-------------------------------------------+
|           Executor JVM Heap               |
|         (spark.executor.memory)           |
+-------------------------------------------+
|  Reserved Memory: 300MB (fixed)           |
+-------------------------------------------+
|  User Memory: (heap - 300MB) * 0.4        |
|  - User data structures                   |
|  - UDF allocations                        |
+-------------------------------------------+
|  Unified Memory: (heap - 300MB) * 0.6    |
|  +-------------------------------------+  |
|  | Storage Memory (50% of unified)     |  |
|  | - Cached DataFrames/RDDs            |  |
|  | - Broadcast variables               |  |
|  +-------------------------------------+  |
|  | Execution Memory (50% of unified)   |  |
|  | - Shuffle buffers                   |  |
|  | - Sort/join operations              |  |
|  +-------------------------------------+  |
+-------------------------------------------+

+-------------------------------------------+
|              Off-Heap Memory              |
|        (spark.memory.offHeap.size)        |
|  - Direct memory allocations              |
|  - Tungsten optimized structures          |
+-------------------------------------------+

+-------------------------------------------+
|            Memory Overhead                |
|      (spark.executor.memoryOverhead)      |
|  - Container overhead                     |
|  - PySpark interop                        |
+-------------------------------------------+
```

## Memory Calculation Example

```
executor_memory = 8GB

usable_memory = 8GB - 300MB = 7.7GB
unified_memory = 7.7GB * 0.6 = 4.62GB
  - storage_memory = 4.62GB * 0.5 = 2.31GB
  - execution_memory = 4.62GB * 0.5 = 2.31GB
user_memory = 7.7GB * 0.4 = 3.08GB
```

## Quick Reference

| Region | Default % | Purpose |
|--------|-----------|---------|
| Reserved | 300MB fixed | System overhead |
| User Memory | 40% | Data structures, UDFs |
| Storage | 30% | Cache, broadcast |
| Execution | 30% | Shuffle, join, sort |

## Configuration

```python
spark.executor.memory = "8g"
spark.memory.fraction = 0.6        # Unified memory %
spark.memory.storageFraction = 0.5 # Storage within unified
spark.memory.offHeap.enabled = true
spark.memory.offHeap.size = "2g"
```

## Related

- [../patterns/memory-tuning.md](../patterns/memory-tuning.md) - Tuning guide
- [../patterns/gc-tuning.md](../patterns/gc-tuning.md) - GC optimization
