# Spark Configuration Reference

> **Purpose**: Complete reference of commonly used Spark configuration parameters.
> **MCP Validated**: 2025-01-19

## Core Configuration

### Application Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.app.name` | - | Application name (shows in Spark UI) |
| `spark.master` | - | Cluster manager (local, yarn, k8s, etc.) |
| `spark.submit.deployMode` | `client` | client or cluster mode |

### Executor Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.executor.memory` | `1g` | Executor heap memory |
| `spark.executor.memoryOverhead` | `384m` or 10% | Non-heap memory |
| `spark.executor.cores` | 1 | Cores per executor |
| `spark.executor.instances` | 2 | Number of executors |
| `spark.executor.pyspark.memory` | - | Python process memory |

### Driver Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.driver.memory` | `1g` | Driver heap memory |
| `spark.driver.memoryOverhead` | `384m` or 10% | Non-heap memory |
| `spark.driver.cores` | 1 | Driver cores |

### Memory Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.memory.fraction` | `0.6` | Unified memory fraction |
| `spark.memory.storageFraction` | `0.5` | Storage within unified |
| `spark.memory.offHeap.enabled` | `false` | Enable off-heap |
| `spark.memory.offHeap.size` | `0` | Off-heap size |

## SQL Configuration

### General SQL

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.sql.shuffle.partitions` | `200` | Shuffle partitions |
| `spark.sql.autoBroadcastJoinThreshold` | `10MB` | Auto-broadcast limit |
| `spark.sql.files.maxPartitionBytes` | `128MB` | Max input partition |
| `spark.sql.files.minPartitionNum` | 1 | Min input partitions |

### Adaptive Query Execution

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.sql.adaptive.enabled` | `true` (3.2+) | Enable AQE |
| `spark.sql.adaptive.coalescePartitions.enabled` | `true` | Coalesce small partitions |
| `spark.sql.adaptive.coalescePartitions.minPartitionSize` | `1MB` | Min coalesced size |
| `spark.sql.adaptive.advisoryPartitionSizeInBytes` | `64MB` | Target partition size |
| `spark.sql.adaptive.skewJoin.enabled` | `true` | Handle skewed joins |
| `spark.sql.adaptive.skewJoin.skewedPartitionFactor` | `5` | Skew factor threshold |
| `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` | `256MB` | Skew size threshold |
| `spark.sql.adaptive.localShuffleReader.enabled` | `true` | Local shuffle optimization |

### Join Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.sql.join.preferSortMergeJoin` | `true` | Prefer SMJ over SHJ |
| `spark.sql.autoBroadcastJoinThreshold` | `10MB` | Auto-broadcast threshold |

## Shuffle Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.shuffle.compress` | `true` | Compress shuffle data |
| `spark.shuffle.spill.compress` | `true` | Compress spill data |
| `spark.shuffle.file.buffer` | `32k` | Buffer for shuffle writes |
| `spark.reducer.maxSizeInFlight` | `48m` | Max fetch size per reduce |
| `spark.shuffle.io.maxRetries` | `3` | Retry count for fetches |
| `spark.shuffle.io.retryWait` | `5s` | Wait between retries |
| `spark.shuffle.service.enabled` | `false` | External shuffle service |

## I/O Configuration

### Compression

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.io.compression.codec` | `lz4` | Default codec (lz4, snappy, zstd) |
| `spark.sql.parquet.compression.codec` | `snappy` | Parquet compression |

### File Handling

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.sql.files.maxPartitionBytes` | `128MB` | Max partition size |
| `spark.sql.files.openCostInBytes` | `4MB` | Small file open cost |
| `spark.hadoop.fs.s3a.multipart.size` | - | S3 multipart size |

## Serialization

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.serializer` | Java | Use KryoSerializer for better perf |
| `spark.kryo.registrationRequired` | `false` | Require class registration |
| `spark.kryo.unsafe` | `false` | Use unsafe Kryo |

## Dynamic Allocation

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spark.dynamicAllocation.enabled` | `false` | Enable dynamic allocation |
| `spark.dynamicAllocation.minExecutors` | `0` | Minimum executors |
| `spark.dynamicAllocation.maxExecutors` | `infinity` | Maximum executors |
| `spark.dynamicAllocation.initialExecutors` | - | Initial executor count |
| `spark.dynamicAllocation.executorIdleTimeout` | `60s` | Idle timeout |
| `spark.dynamicAllocation.schedulerBacklogTimeout` | `1s` | Scale-up trigger |

## Production Configuration Template

```python
spark = SparkSession.builder \
    .appName("ProductionJob") \
    # Memory
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.memoryOverhead", "2g") \
    .config("spark.driver.memory", "4g") \
    .config("spark.memory.fraction", "0.6") \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "2g") \
    # Parallelism
    .config("spark.executor.cores", "5") \
    .config("spark.sql.shuffle.partitions", "200") \
    # AQE
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    # Serialization
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    # Compression
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()
```

## GC Configuration

```python
# G1GC for large heaps (> 4GB)
spark.conf.set("spark.executor.extraJavaOptions",
    "-XX:+UseG1GC "
    "-XX:InitiatingHeapOccupancyPercent=35 "
    "-XX:ConcGCThreads=4 "
    "-XX:ParallelGCThreads=8 "
    "-XX:G1HeapRegionSize=16m"
)
```

## Debugging Configuration

```python
# Verbose logging
spark.conf.set("spark.eventLog.enabled", "true")
spark.conf.set("spark.eventLog.dir", "/tmp/spark-events")

# Heap dumps on OOM
spark.conf.set("spark.executor.extraJavaOptions",
    "-XX:+HeapDumpOnOutOfMemoryError "
    "-XX:HeapDumpPath=/tmp/heapdump"
)
```
