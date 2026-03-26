# DataFrames and Datasets

> **Purpose**: DataFrame/Dataset creation and basic operations.
> **Confidence**: 0.98
> **MCP Validated**: 2025-01-19

## Overview

DataFrames are distributed collections of data organized into named columns. They provide a higher-level abstraction than RDDs with automatic optimization through the Catalyst optimizer.

## Creating DataFrames

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# From files
df = spark.read.parquet("s3://bucket/data/")
df = spark.read.json("path/to/data.json")
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# From data
df = spark.createDataFrame([("a", 1), ("b", 2)], ["key", "value"])
```

## Basic Operations

```python
# Selection
df.select("col1", "col2")

# Filtering
df.filter(df.col1 > 100)
df.where(col("status") == "active")

# Aggregation
df.groupBy("category").agg({"amount": "sum"})

# Joining
df.join(other_df, "key")

# Sorting
df.orderBy("col1", ascending=False)

# Column operations
df.withColumn("new_col", df.col1 * 2)
df.drop("unwanted_col")
```

## Quick Reference

| Operation | Method | Shuffle? |
|-----------|--------|----------|
| Select columns | `select()` | No |
| Filter rows | `filter()`, `where()` | No |
| Add column | `withColumn()` | No |
| Group & aggregate | `groupBy().agg()` | Yes |
| Join tables | `join()` | Usually |
| Sort rows | `orderBy()` | Yes |

## Common Mistakes

### Wrong
```python
# Triggering action inside transformation
df.withColumn("count", df.count())  # Actions return values, not columns
```

### Correct
```python
# Use window functions for row-level aggregates
from pyspark.sql.window import Window
df.withColumn("count", count("*").over(Window.partitionBy("category")))
```

## Related

- [architecture.md](architecture.md) - Spark architecture
- [execution-plans.md](execution-plans.md) - Query optimization
