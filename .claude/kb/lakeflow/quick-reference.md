# Lakeflow Quick Reference

> Fast lookup tables. For code examples, see linked files.

## Python Decorators

| Decorator | Purpose | Action |
|-----------|---------|--------|
| `@dlt.table()` | Create streaming/materialized table | - |
| `@dlt.view()` | Create temporary view | - |
| `@dlt.expect()` | Data quality check | WARN |
| `@dlt.expect_or_drop()` | Drop invalid rows | DROP |
| `@dlt.expect_or_fail()` | Fail pipeline | FAIL |
| `@dlt.expect_all()` | Multiple checks | WARN |
| `@dlt.expect_all_or_drop()` | Multiple checks | DROP |

## SQL Keywords

| Keyword | Purpose |
|---------|---------|
| `CREATE OR REFRESH STREAMING TABLE` | Streaming table |
| `CREATE OR REFRESH MATERIALIZED VIEW` | Batch aggregation |
| `STREAM read_files()` | Auto Loader |
| `APPLY CHANGES INTO` | CDC processing |
| `CONSTRAINT ... EXPECT` | Data quality |

## Functions

| Function | Purpose |
|----------|---------|
| `dlt.read()` | Read table (batch) |
| `dlt.read_stream()` | Read table (streaming) |
| `dlt.apply_changes()` | CDC processing |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Real-time data | Streaming Table |
| Batch aggregations | Materialized View |
| Track current state | SCD Type 1 |
| Track history | SCD Type 2 |
| Cloud storage | Auto Loader |
| Dev testing | Development mode |
| Production | Serverless + triggered |

## Quality Check Strategy

| Layer | Action | Use Case |
|-------|--------|----------|
| Bronze | WARN | Track issues |
| Silver | DROP | Remove bad data |
| Gold | FAIL | Critical validation |

## Troubleshooting

| Error | Solution |
|-------|----------|
| Permission denied | `GRANT USE CATALOG/SCHEMA` |
| Table already defined | Use different name |
| Slow startup | Use performance mode |
| High costs | Switch to triggered |
| Schema evolution | Use materialized view |

## Common Pitfalls

| ❌ Don't | ✅ Do |
|----------|-------|
| Actions in pipeline code | Keep operations lazy |
| Hardcode environments | Use parameters |
| Skip quality checks | Apply at each layer |
| Use reserved properties | Use proper clauses |

**Reserved properties**: `owner`, `location`, `provider`, `external`

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/getting-started.md` |
| Python API | `patterns/python-api.md` |
| SQL Syntax | `patterns/sql-syntax.md` |
| CDC | `patterns/cdc.md` |
| Data Quality | `patterns/data-quality.md` |
| Configuration | `reference/pipeline-configuration.md` |
| Full Index | `index.md` |
