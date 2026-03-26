# Databricks Lakeflow Knowledge Base

> **Purpose**: Authoritative reference for Lakeflow Declarative Pipelines development.
> **MCP Validated**: 2025-01-19

## Quick Navigation

### Concepts (Explanatory, < 150 lines)

| File | Purpose |
|------|---------|
| [concepts/core-concepts.md](concepts/core-concepts.md) | Streaming tables, materialized views, Lakeflow fundamentals |
| [concepts/getting-started.md](concepts/getting-started.md) | Tutorial for first pipeline |

### Patterns (Code-focused, < 200 lines)

| File | Purpose |
|------|---------|
| [patterns/python-decorators.md](patterns/python-decorators.md) | @dlt.table, @dlt.view, @dlt.expect decorators |
| [patterns/python-streaming.md](patterns/python-streaming.md) | Streaming patterns, Auto Loader, Medallion |
| [patterns/sql-tables.md](patterns/sql-tables.md) | CREATE TABLE statements, TBLPROPERTIES |
| [patterns/sql-streaming.md](patterns/sql-streaming.md) | STREAM syntax, joins, aggregations |
| [patterns/cdc-apply-changes.md](patterns/cdc-apply-changes.md) | APPLY CHANGES, SCD Type 1/2 |
| [patterns/cdc-example.md](patterns/cdc-example.md) | Complete CDC examples (Python/SQL) |
| [patterns/expectations.md](patterns/expectations.md) | Basic data quality expectations |
| [patterns/expectations-advanced.md](patterns/expectations-advanced.md) | Grouped expectations, common patterns |
| [patterns/bronze-ingestion.md](patterns/bronze-ingestion.md) | S3 Parquet ingestion, Auto Loader config |
| [patterns/silver-cleansing.md](patterns/silver-cleansing.md) | Type casting, PII masking, deduplication |
| [patterns/gold-aggregation.md](patterns/gold-aggregation.md) | KPIs, aggregations, time-series |
| [patterns/dabs-deployment.md](patterns/dabs-deployment.md) | Databricks Asset Bundles configuration |

### Reference (Comprehensive, no line limit)

| File | Purpose |
|------|---------|
| [reference/pipeline-configuration.md](reference/pipeline-configuration.md) | Pipeline settings, clusters |
| [reference/serverless-pipelines.md](reference/serverless-pipelines.md) | Serverless compute |
| [reference/materialized-views.md](reference/materialized-views.md) | MV optimization |
| [reference/stateful-processing.md](reference/stateful-processing.md) | Streaming state, watermarks |
| [reference/parameters.md](reference/parameters.md) | Pipeline parameters |
| [reference/unity-catalog.md](reference/unity-catalog.md) | UC integration |
| [reference/limitations.md](reference/limitations.md) | Known limitations |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Streaming Table** | Incrementally processes new data |
| **Materialized View** | Batch-refreshed aggregate table |
| **Expectation** | Data quality constraint |
| **AUTO CDC** | Automatic change data capture |
| **SCD Type 1/2** | Slowly Changing Dimension patterns |

## Common Patterns

### Medallion Architecture
```
Bronze (Raw) -> Silver (Cleaned) -> Gold (Business)
```

### Data Quality Strategy
```
Bronze: WARN  -> Track issues
Silver: DROP  -> Remove bad data
Gold:   FAIL  -> Strict validation
```

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/core-concepts.md -> concepts/getting-started.md |
| **Intermediate** | patterns/python-decorators.md -> patterns/expectations.md -> patterns/cdc-apply-changes.md |
| **Advanced** | reference/stateful-processing.md -> reference/materialized-views.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| lakeflow-architect | patterns/, concepts/ | Pipeline design |
| lakeflow-expert | All files | Comprehensive guidance |
| lakeflow-pipeline-builder | patterns/bronze-*, patterns/silver-*, patterns/gold-*, patterns/dabs-* | Actual pipeline implementation |
