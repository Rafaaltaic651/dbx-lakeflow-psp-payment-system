# Garbage Collection Tuning

> **Purpose**: Reduce GC overhead in Spark applications.
> **MCP Validated**: 2025-01-19

## When to Use

- GC time > 10% of task time (visible in Spark UI)
- Frequent executor failures
- Task durations vary widely
- Large heaps (> 8GB)

## Implementation

```python
# G1GC configuration (recommended for large heaps)
spark.conf.set("spark.executor.extraJavaOptions",
    "-XX:+UseG1GC "
    "-XX:InitiatingHeapOccupancyPercent=35 "
    "-XX:ConcGCThreads=4 "
    "-XX:ParallelGCThreads=8 "
    "-XX:G1HeapRegionSize=16m"
)

# Driver GC options
spark.conf.set("spark.driver.extraJavaOptions",
    "-XX:+UseG1GC "
    "-XX:InitiatingHeapOccupancyPercent=35"
)
```

## Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `+UseG1GC` | - | Use G1 collector |
| `InitiatingHeapOccupancyPercent` | `35` | Start GC earlier |
| `G1HeapRegionSize` | `16m` | Region size for large heaps |
| `ConcGCThreads` | `4` | Concurrent GC threads |
| `ParallelGCThreads` | `8` | Parallel GC threads |

## Reducing GC Pressure

### 1. Enable Off-Heap Memory

```python
spark.conf.set("spark.memory.offHeap.enabled", "true")
spark.conf.set("spark.memory.offHeap.size", "2g")
```

### 2. Use DataFrames Over RDDs

```python
# Good: DataFrame API (Tungsten optimized)
df.select("col1", "col2").filter(col("col1") > 100)

# Avoid: RDD API (creates Java objects)
rdd.map(lambda x: x[0]).filter(lambda x: x > 100)
```

### 3. Use Built-in Functions

```python
# Good: Built-in (no serialization)
from pyspark.sql.functions import upper
df.withColumn("name_upper", upper(col("name")))

# Avoid: Python UDF (serialization overhead)
@udf("string")
def my_upper(s):
    return s.upper()
```

### 4. Use Pandas UDFs for Complex Logic

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("double")
def vectorized_calc(s: pd.Series) -> pd.Series:
    return s * 2.0  # Vectorized, less GC

df.withColumn("result", vectorized_calc("value"))
```

## Monitoring GC

```
Spark UI -> Executors -> GC Time

Target: GC Time < 10% of Task Time

High GC indicates:
- Too much data in memory
- Large user objects
- String-heavy operations
```

## Heap Dump on OOM

```python
spark.conf.set("spark.executor.extraJavaOptions",
    "-XX:+HeapDumpOnOutOfMemoryError "
    "-XX:HeapDumpPath=/tmp/heapdump"
)
```

## See Also

- [memory-tuning.md](memory-tuning.md) - Memory configuration
- [../concepts/memory-regions.md](../concepts/memory-regions.md) - Memory architecture
