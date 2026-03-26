# Medallion Architecture Knowledge Base

> **MCP Validated**: 2026-03-26

## Overview

Medallion Architecture is a data design pattern that organizes data in a lakehouse into three layers: Bronze (raw), Silver (refined), and Gold (business). This KB provides patterns and best practices for implementing Medallion on Databricks.

## Quick Navigation

| Need | Go To |
|------|-------|
| Fast syntax lookup | [quick-reference.md](quick-reference.md) |
| Layer responsibilities | [concepts/layer-responsibilities.md](concepts/layer-responsibilities.md) |
| Grain selection | [concepts/grain-and-granularity.md](concepts/grain-and-granularity.md) |
| SCD patterns | [concepts/scd-patterns.md](concepts/scd-patterns.md) |
| Tables vs Views | [concepts/tables-vs-views.md](concepts/tables-vs-views.md) |
| Bronze ingestion | [patterns/bronze-ingestion.md](patterns/bronze-ingestion.md) |
| Silver transformation | [patterns/silver-transformation.md](patterns/silver-transformation.md) |
| Gold aggregation | [patterns/gold-aggregation.md](patterns/gold-aggregation.md) |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SOURCE           BRONZE          SILVER           GOLD        │
│   ──────           ──────          ──────           ────        │
│                                                                  │
│   S3/ADLS    →    Raw Data    →   Cleansed    →   Aggregated   │
│   Kafka           Append-only     Validated       Business      │
│   APIs            Schema-on-read  Typed           KPIs          │
│                                                                  │
│   WHO QUERIES:    Engineers       Analysts        Dashboards    │
│                   (debug)         (explore)       (report)      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Summary

| Layer | Purpose | Data Quality | Consumers |
|-------|---------|--------------|-----------|
| **Bronze** | Raw ingestion, preserve source | Minimal (rescue bad data) | Data Engineers |
| **Silver** | Cleanse, validate, conform | Expectations applied | Analysts, Data Scientists |
| **Gold** | Aggregate, denormalize | Business rules enforced | Dashboards, Reports |

## Related Agents

| Agent | Responsibility |
|-------|----------------|
| `medallion-architect` | Strategy, layer design, best practices |
| `lakeflow-pipeline-builder` | DLT implementation, code generation |
| `lakeflow-expert` | Troubleshooting, optimization |
