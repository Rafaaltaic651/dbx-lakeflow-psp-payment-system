# Spark Best Practices Checklist

> **Purpose**: Production-ready checklist for Spark applications.
> **MCP Validated**: 2025-01-19

## Pre-Development Checklist

- [ ] Schema explicitly defined (not inferred)
- [ ] Partition columns identified for large tables
- [ ] Estimated data volumes documented
- [ ] Join strategies planned

## Code Quality

### DataFrame API
- [ ] Using DataFrame API over RDD
- [ ] Built-in functions over UDFs
- [ ] Pandas UDFs for complex logic (not Python UDFs)
- [ ] Type hints and docstrings present

### Transformations
- [ ] Filters applied early (before joins/aggregations)
- [ ] Columns selected explicitly (no `SELECT *`)
- [ ] Null handling is explicit (`coalesce`, `isNotNull`)
- [ ] Column names are descriptive

### Joins
- [ ] Small tables broadcasted (< 10MB)
- [ ] Join conditions use indexed columns
- [ ] Pre-filtering applied before joins
- [ ] No accidental Cartesian products

### Caching
- [ ] Cache only for multi-use DataFrames
- [ ] Cache after filtering (not before)
- [ ] `unpersist()` called when done
- [ ] Storage level appropriate for use case

## Configuration Checklist

### Memory
- [ ] Executor memory: 4-8GB
- [ ] Memory overhead: min 10% or 384MB
- [ ] Off-heap enabled for large shuffles
- [ ] Driver memory sized for collect operations

### Parallelism
- [ ] Shuffle partitions tuned (not default 200)
- [ ] Executor cores: 4-5 per executor
- [ ] Input partitions: ~128MB each

### Optimization
- [ ] AQE enabled (`spark.sql.adaptive.enabled`)
- [ ] Skew join handling enabled
- [ ] Partition coalescing enabled
- [ ] Broadcast threshold tuned

## Anti-Patterns to Avoid

### Collections
```python
# AVOID
all_data = df.collect()  # OOM risk

# PREFER
sample = df.take(100)
df.show(20)
df.write.parquet("output/")
```

### Loops
```python
# AVOID
for date in dates:
    df.filter(col("date") == date).write.parquet(f"output/{date}")

# PREFER
df.write.partitionBy("date").parquet("output/")
```

### Multiple Counts
```python
# AVOID
if df.count() > 0:
    if df.count() > 1000:
        process(df)

# PREFER
df_cached = df.cache()
count = df_cached.count()
if count > 0 and count > 1000:
    process(df_cached)
df_cached.unpersist()
```

### Python UDFs
```python
# AVOID
@udf("string")
def my_upper(s):
    return s.upper() if s else None

# PREFER
from pyspark.sql.functions import upper
df.withColumn("name_upper", upper(col("name")))
```

## Testing Checklist

- [ ] Unit tests with small DataFrames
- [ ] Schema validation tests
- [ ] Null handling tests
- [ ] Edge case tests (empty DataFrames, etc.)
- [ ] Performance benchmarks documented

## Deployment Checklist

- [ ] Logging implemented (not print statements)
- [ ] Error handling with appropriate retries
- [ ] Idempotent writes (overwrite with partition management)
- [ ] Monitoring and alerting configured
- [ ] Resource limits set (max executors, timeout)

## Code Review Checklist

- [ ] No `collect()` on large data
- [ ] Filters applied early
- [ ] Columns selected explicitly
- [ ] Joins optimized (broadcast hints where appropriate)
- [ ] Cache used strategically
- [ ] Built-in functions over UDFs
- [ ] Idempotent writes
- [ ] Proper null handling
- [ ] No hardcoded paths or credentials

## Performance Review

- [ ] Execution plan reviewed (`df.explain()`)
- [ ] No unexpected shuffles
- [ ] Broadcast joins used for small tables
- [ ] No data skew issues
- [ ] GC time < 10% of task time
- [ ] No disk spill in normal operation

## Documentation

- [ ] README with setup instructions
- [ ] Data schema documented
- [ ] Configuration parameters documented
- [ ] Performance benchmarks recorded
- [ ] Known limitations documented
