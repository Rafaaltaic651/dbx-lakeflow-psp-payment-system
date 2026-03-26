# Spark Architecture

> **Purpose**: Core Spark architecture and execution model.
> **Confidence**: 0.98
> **MCP Validated**: 2025-01-19

## Overview

Apache Spark is a unified analytics engine for large-scale data processing. It uses a master-worker architecture where the Driver orchestrates work across Executors.

## Architecture Diagram

```
+-------------------------------------------------------------+
|                      Spark Application                       |
+-------------------------------------------------------------+
|  +-------------------------------------------------------+  |
|  |                    Driver Program                      |  |
|  |  +-----------+  +----------------------------+        |  |
|  |  |SparkContext|  | DAG Scheduler + Task Sched |        |  |
|  |  +-----------+  +----------------------------+        |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
|  +-------------+  +-------------+  +-------------+          |
|  |  Executor   |  |  Executor   |  |  Executor   |          |
|  | +--+ +--+   |  | +--+ +--+   |  | +--+ +--+   |          |
|  | |T1| |T2|   |  | |T3| |T4|   |  | |T5| |T6|   |          |
|  | +--+ +--+   |  | +--+ +--+   |  | +--+ +--+   |          |
|  |   [Cache]   |  |   [Cache]   |  |   [Cache]   |          |
|  +-------------+  +-------------+  +-------------+          |
+-------------------------------------------------------------+
```

## Core Components

| Component | Purpose |
|-----------|---------|
| **Driver** | Orchestrates application, creates SparkContext |
| **Cluster Manager** | Allocates resources (YARN, K8s, Standalone) |
| **Executors** | Run tasks and store data |
| **Tasks** | Smallest unit of work |

## Execution Model

1. User submits application to Driver
2. Driver creates SparkContext and DAG
3. DAG Scheduler splits work into stages
4. Task Scheduler assigns tasks to executors
5. Executors run tasks and return results

## Quick Reference

| Layer | Components |
|-------|------------|
| Application | SparkSession, SparkContext |
| Scheduling | DAGScheduler, TaskScheduler |
| Execution | Executors, Tasks |
| Storage | BlockManager, Cache |

## Related

- [dataframes.md](dataframes.md) - DataFrame API
- [execution-plans.md](execution-plans.md) - Query planning
