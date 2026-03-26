# Execution Plans

> **Purpose**: Understanding and analyzing Spark query execution plans.
> **Confidence**: 0.95
> **MCP Validated**: 2025-01-19

## Overview

Spark uses the Catalyst optimizer to transform logical plans into optimized physical execution plans. Understanding these plans helps diagnose performance issues.

## Plan Stages

```
Query -> Parsed Plan -> Analyzed Plan -> Optimized Plan -> Physical Plan -> Execution
          (Parser)      (Analyzer)       (Catalyst)       (Planner)
```

## Viewing Plans

```python
# Simple plan
df.explain()

# Extended plan with all stages
df.explain(True)

# Formatted output (recommended)
df.explain("formatted")

# With cost estimates
df.explain("cost")
```

## Plan Components

| Section | Description |
|---------|-------------|
| **Parsed Logical Plan** | Initial AST from query |
| **Analyzed Logical Plan** | Resolved columns and types |
| **Optimized Logical Plan** | After Catalyst rules |
| **Physical Plan** | Actual execution operators |

## Key Optimization Rules

| Rule | What It Does |
|------|--------------|
| Predicate Pushdown | Moves filters closer to source |
| Column Pruning | Drops unused columns early |
| Constant Folding | Evaluates constant expressions |
| Filter Reordering | Puts selective filters first |
| Join Reordering | Optimizes join order |

## Reading Physical Plans

```
*(2) HashAggregate(keys=[category], functions=[sum(amount)])
+- Exchange hashpartitioning(category, 200)    <-- Shuffle
   +- *(1) HashAggregate(keys=[category], functions=[partial_sum(amount)])
      +- *(1) Filter (status = active)          <-- Predicate pushed down
         +- *(1) FileScan parquet [category,amount,status]  <-- Column pruning
```

## Plan Indicators

| Indicator | Meaning |
|-----------|---------|
| `*` | Whole-stage code generation |
| `Exchange` | Shuffle operation |
| `BroadcastExchange` | Broadcast data |
| `Sort` | Sorting operation |
| `Filter` | Row filtering |
| `Project` | Column selection |

## Quick Reference

| What to Look For | Good Sign | Bad Sign |
|------------------|-----------|----------|
| Join strategy | BroadcastHashJoin | CartesianProduct |
| Filter location | Near scan | After join |
| Shuffle count | Minimal | Multiple exchanges |
| Scan columns | Only needed | All columns |

## Related

- [dataframes.md](dataframes.md) - DataFrame operations
- [../patterns/aqe.md](../patterns/aqe.md) - Adaptive optimization
