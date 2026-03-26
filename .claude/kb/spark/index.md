# Apache Spark Knowledge Base

> **Purpose**: Authoritative reference for Spark development, optimization, and troubleshooting.
> **MCP Validated**: 2025-01-19

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/architecture.md](concepts/architecture.md) | Core Spark architecture and execution model |
| [concepts/dataframes.md](concepts/dataframes.md) | DataFrame creation and operations |
| [concepts/execution-plans.md](concepts/execution-plans.md) | Query planning and Catalyst optimizer |
| [concepts/memory-regions.md](concepts/memory-regions.md) | Executor memory architecture |
| [concepts/partitions.md](concepts/partitions.md) | Partition fundamentals and sizing |
| [concepts/shuffle.md](concepts/shuffle.md) | Shuffle operations and triggers |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/aqe.md](patterns/aqe.md) | Adaptive Query Execution configuration |
| [patterns/join-strategies.md](patterns/join-strategies.md) | Join strategy selection |
| [patterns/broadcast-joins.md](patterns/broadcast-joins.md) | Broadcast join optimization |
| [patterns/data-skew.md](patterns/data-skew.md) | Detecting and handling data skew |
| [patterns/memory-tuning.md](patterns/memory-tuning.md) | Memory configuration |
| [patterns/gc-tuning.md](patterns/gc-tuning.md) | Garbage collection optimization |
| [patterns/caching.md](patterns/caching.md) | Strategic caching patterns |
| [patterns/shuffle-optimization.md](patterns/shuffle-optimization.md) | Reducing shuffle cost |
| [patterns/repartition-vs-coalesce.md](patterns/repartition-vs-coalesce.md) | Partition operations |

### Reference (Comprehensive)

| File | Purpose |
|------|---------|
| [reference/configuration-reference.md](reference/configuration-reference.md) | Complete configuration guide |
| [reference/best-practices-checklist.md](reference/best-practices-checklist.md) | Production checklist |
| [reference/troubleshooting.md](reference/troubleshooting.md) | Error diagnosis guide |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **AQE** | Runtime query optimization (Spark 3.0+) |
| **Broadcast Join** | Send small table to all executors |
| **Shuffle** | Data redistribution across partitions |
| **Partition** | Logical data chunk for parallel processing |
| **Storage Memory** | Cache and broadcast storage |
| **Execution Memory** | Shuffle, join, sort buffers |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/architecture.md -> concepts/dataframes.md |
| **Intermediate** | concepts/partitions.md -> patterns/aqe.md -> patterns/join-strategies.md |
| **Advanced** | patterns/data-skew.md -> reference/troubleshooting.md |

---

## Common Tasks

| Task | Primary Files |
|------|---------------|
| Optimize slow query | patterns/aqe.md, patterns/shuffle-optimization.md |
| Fix OOM errors | patterns/memory-tuning.md, reference/troubleshooting.md |
| Choose join strategy | patterns/join-strategies.md, patterns/broadcast-joins.md |
| Handle data skew | patterns/data-skew.md, patterns/aqe.md |
| Production deployment | reference/best-practices-checklist.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| spark-specialist | All files | Architecture, optimization |
| spark-troubleshooter | reference/troubleshooting.md, patterns/ | Debugging failures |
| spark-performance-analyzer | patterns/aqe.md, patterns/data-skew.md | Performance tuning |
