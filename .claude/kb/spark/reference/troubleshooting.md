# Spark Troubleshooting Guide

> **Purpose**: Diagnose and resolve common Spark issues.
> **MCP Validated**: 2025-01-19

## Memory Errors

### OutOfMemoryError: Java heap space

**Symptoms:**
- `java.lang.OutOfMemoryError: Java heap space`
- Executor lost
- Task failures

**Diagnosis:**
```python
# Check executor memory allocation
spark.conf.get("spark.executor.memory")
spark.conf.get("spark.memory.fraction")

# Check data size per partition
df.groupBy(spark_partition_id()).count().describe().show()
```

**Solutions:**
1. Increase executor memory: `spark.executor.memory = "8g"`
2. Increase partitions: `df.repartition(500)`
3. Reduce storage fraction: `spark.memory.storageFraction = 0.3`
4. Enable off-heap: `spark.memory.offHeap.enabled = true`

### Container killed by YARN

**Symptoms:**
- "Container killed by YARN for exceeding memory limits"
- Executor frequently lost

**Solutions:**
1. Increase overhead: `spark.executor.memoryOverhead = "2g"`
2. For PySpark: `spark.executor.pyspark.memory = "1g"`
3. Reduce in-memory operations

### Driver OOM

**Symptoms:**
- Driver out of memory
- `collect()` fails
- Broadcast too large

**Solutions:**
1. Increase driver memory: `spark.driver.memory = "4g"`
2. Avoid `collect()` - use `take(n)` or `write()`
3. Reduce broadcast threshold: `spark.sql.autoBroadcastJoinThreshold = -1`

## Performance Issues

### Slow Jobs

**Diagnosis:**
```python
# Check execution plan
df.explain("formatted")

# Check partition count and distribution
df.rdd.getNumPartitions()
df.groupBy(spark_partition_id()).count().orderBy("count", ascending=False).show()
```

**Common Causes:**
1. Data skew
2. Too few/many partitions
3. Wrong join strategy
4. Missing broadcast

### Data Skew

**Symptoms:**
- Some tasks take much longer than others
- Uneven partition sizes in Spark UI

**Diagnosis:**
```python
df.groupBy("join_key").count().orderBy(desc("count")).show(20)
```

**Solutions:**
1. Enable AQE skew handling
2. Use salting technique
3. Broadcast small tables
4. Filter hot keys separately

### High GC Time

**Symptoms:**
- GC time > 10% in Spark UI
- Varying task durations

**Solutions:**
1. Enable off-heap memory
2. Use DataFrames (not RDDs)
3. Avoid Python UDFs
4. Tune G1GC settings

## Shuffle Issues

### Shuffle Read/Write Too High

**Diagnosis:**
```
Spark UI -> Stages -> Shuffle Read/Write columns
```

**Solutions:**
1. Filter before aggregation
2. Select only needed columns
3. Broadcast small tables
4. Increase shuffle partitions

### MetadataFetchFailedException

**Symptoms:**
- Shuffle files missing
- Tasks failing with metadata errors

**Solutions:**
1. Enable shuffle service: `spark.shuffle.service.enabled = true`
2. Increase retries: `spark.shuffle.io.maxRetries = 10`
3. Check disk space on workers

## Join Issues

### Wrong Join Strategy

**Diagnosis:**
```python
df1.join(df2, "key").explain()
# Look for: BroadcastHashJoin vs SortMergeJoin
```

**Solutions:**
```python
# Force broadcast
result = large_df.join(broadcast(small_df), "key")

# Or use hint
result = large_df.join(small_df.hint("broadcast"), "key")
```

### Cartesian Product

**Symptoms:**
- Massive data explosion
- Very slow execution

**Diagnosis:**
```python
df1.join(df2).explain()
# Look for: CartesianProduct
```

**Solution:**
Always specify join condition.

## Data Issues

### Schema Mismatch

**Symptoms:**
- `AnalysisException: cannot resolve`
- Unexpected null values

**Solutions:**
```python
# Explicitly define schema
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([
    StructField("id", StringType(), False),
    StructField("value", StringType(), True)
])

df = spark.read.schema(schema).json("data/")
```

### Null Values

**Symptoms:**
- Unexpected null results
- Aggregations return null

**Solutions:**
```python
# Check for nulls
df.filter(col("column").isNull()).count()

# Handle nulls
df.na.fill({"column": "default"})
df.withColumn("column", coalesce(col("column"), lit("default")))
```

## Diagnostic Commands

```python
# Check configuration
spark.sparkContext.getConf().getAll()

# Check cached data
spark.catalog.listTables()
spark.catalog.isCached("table_name")

# View execution plan
df.explain("formatted")
df.explain("cost")

# Partition info
df.rdd.getNumPartitions()
df.groupBy(spark_partition_id()).count().show()

# Memory status
spark.sparkContext._jsc.sc().getExecutorMemoryStatus()
```

## Spark UI Navigation

| Tab | What to Check |
|-----|---------------|
| Jobs | Overall job progress, failed stages |
| Stages | Task distribution, shuffle metrics |
| Storage | Cached RDDs/DataFrames |
| Environment | Configuration values |
| Executors | Memory, GC, task counts |
| SQL | Query plans, execution times |
