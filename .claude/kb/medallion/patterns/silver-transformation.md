# Silver Transformation Pattern

> **MCP Validated**: 2026-03-26 | **Max Lines**: 200

## Purpose

Cleanse, validate, and conform data from Bronze for analytical consumption.

## Pattern: Silver L1 (1:1 from Bronze)

### Basic Template

```python
import dlt
from pyspark.sql.functions import col, current_timestamp, trim

@dlt.table(
    name="silver_{source}_{entity}",
    comment="Cleansed {entity} data with quality expectations",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_id", "{primary_key} IS NOT NULL")
@dlt.expect_or_drop("valid_required", "{required_field} IS NOT NULL")
def silver_source_entity():
    return (
        dlt.read_stream("bronze_{source}_{entity}")
        .select(
            col("field1").cast("string").alias("field1"),
            col("field2").cast("decimal(18,2)").alias("field2"),
            trim(col("field3")).alias("field3"),
            col("_ingested_at"),
            col("_source_file")
        )
        .withColumn("_processed_at", current_timestamp())
    )
```

## Pattern: Silver L2 (Domain Views)

For domain-specific join logic, use Lakeflow Views:

```python
@dlt.view(
    name="view_transaction_detail",
    comment="Transaction detail with merchant and customer context"
)
def view_transaction_detail():
    return spark.sql("""
        SELECT
            t.transaction_id,
            t.amount,
            t.currency_code,
            t.status,
            m.merchant_name,
            m.category,
            c.customer_name,
            t._processed_at
        FROM LIVE.silver_transactions t
        LEFT JOIN LIVE.silver_merchants m
            ON t.merchant_id = m.merchant_id
        LEFT JOIN LIVE.silver_customers c
            ON t.customer_id = c.customer_id
    """)
```

## Data Quality Expectations

### Expectation Levels

```python
# WARN - Log but keep row (use sparingly in Silver)
@dlt.expect("check_name", "condition")

# DROP - Remove invalid rows (default for Silver)
@dlt.expect_or_drop("check_name", "condition")

# FAIL - Stop pipeline (use for critical issues)
@dlt.expect_or_fail("check_name", "condition")
```

### Common Expectations

```python
# Null checks
@dlt.expect_or_drop("valid_id", "transaction_id IS NOT NULL")

# Domain checks
@dlt.expect_or_drop("valid_card", "card_type IN ('V', 'M', 'D', 'A', 'J')")

# Range checks
@dlt.expect_or_drop("valid_amount", "amount >= 0")

# Format checks
@dlt.expect("valid_zip", "LENGTH(zip_code) IN (5, 9, 10)")

# Multiple expectations
TRANSACTION_QUALITY = {
    "valid_id": "transaction_id IS NOT NULL",
    "valid_amount": "amount IS NOT NULL",
    "valid_merchant": "merchant_id IS NOT NULL"
}
@dlt.expect_all_or_drop(TRANSACTION_QUALITY)
```

## Type Casting Reference

| Source Type | Silver Type | Cast Method |
|-------------|-------------|-------------|
| String amounts | Decimal(18,2) | `.cast("decimal(18,2)")` |
| String dates | Date | `to_date(col, "yyyyMMdd")` |
| Padded strings | String | `trim(col)` |
| Nullable int | Integer | `.cast("int")` |

## Null Handling

```python
# Replace nulls with default
.withColumn("status", coalesce(col("status"), lit("UNKNOWN")))

# Filter nulls (via expectation)
@dlt.expect_or_drop("not_null", "field IS NOT NULL")
```

## Transformation Examples

### Amount Conversion (cents to dollars)
```python
.withColumn("amount_dollars", col("amount_cents") / 100)
```

### Date Parsing
```python
.withColumn("transaction_date", to_date(col("date_str"), "MMddyyyy"))
```

### Code Decoding
```python
.withColumn("card_network",
    when(col("card_type") == "V", "Visa")
    .when(col("card_type") == "M", "Mastercard")
    .when(col("card_type") == "D", "Discover")
    .otherwise("Other")
)
```

## Silver Checklist

```text
[ ] Primary key not null expectation
[ ] Required fields not null
[ ] Domain values validated
[ ] Types properly cast
[ ] Strings trimmed
[ ] _processed_at column added
[ ] _ingested_at and _source_file preserved
```
