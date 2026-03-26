# Silver Cleansing Patterns

> **MCP Validated**: 2026-03-26
> **Source**: https://docs.databricks.com/aws/en/dlt/expectations

## Silver Layer Purpose

Transform Bronze raw data into clean, typed, validated data:

1. **Type Casting** - Enforce correct data types
2. **Null Handling** - Apply defaults or filter
3. **PII Protection** - Mask or exclude sensitive fields
4. **Deduplication** - Remove duplicate records
5. **Standardization** - Normalize formats

## Transaction Silver Pattern

```python
import dlt
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType, DateType

@dlt.table(
    name="transactions_silver",
    comment="Cleaned transaction data",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.managed": "true"
    }
)
@dlt.expect_or_drop("valid_id", "transaction_id IS NOT NULL")
@dlt.expect_or_drop("valid_status", "status IN ('APPROVED', 'DECLINED', 'PENDING', 'REVERSED')")
@dlt.expect("valid_amount", "amount IS NOT NULL")
def transactions_silver():
    return (
        dlt.read_stream("transactions_bronze")
        .select(
            F.col("transaction_id").cast("string"),
            F.col("merchant_id").cast("string"),
            F.col("amount").cast(DecimalType(18, 2)),
            F.col("currency_code").cast("string"),
            F.col("status").cast("string"),
            F.col("transaction_date").cast(DateType()),
            F.col("card_type").cast("string"),
            F.col("_ingested_at"),
            F.col("_source_file")
        )
        .withColumn("_cleaned_at", F.current_timestamp())
    )
```

## Amount Handling Pattern

```python
@dlt.table(name="settlements_silver")
@dlt.expect_or_drop("valid_amount", "amount IS NOT NULL")
@dlt.expect_or_drop("valid_merchant", "merchant_id IS NOT NULL")
@dlt.expect("amount_positive", "amount >= 0 OR entry_type = 'CREDIT'")
def settlements_silver():
    return (
        dlt.read_stream("settlements_bronze")
        .select(
            F.col("merchant_id"),
            F.col("settlement_date").cast(DateType()),
            F.col("amount").cast(DecimalType(18, 2)),
            F.col("entry_type"),
            F.col("card_type"),
            F.col("authorization_code"),
            F.when(F.col("entry_type") == "CREDIT", -F.col("amount"))
             .otherwise(F.col("amount"))
             .alias("signed_amount"),
            F.col("_ingested_at")
        )
        .withColumn("_cleaned_at", F.current_timestamp())
    )
```

## PII Handling Patterns

### Exclude PII Columns

```python
@dlt.table(name="customers_silver_no_pii")
def customers_silver_no_pii():
    return (
        dlt.read_stream("customers_bronze")
        .drop("ssn", "tax_id", "bank_account_number")
        .withColumn("_cleaned_at", F.current_timestamp())
    )
```

### Mask PII Columns

```python
@dlt.table(name="customers_silver_masked")
def customers_silver_masked():
    return (
        dlt.read_stream("customers_bronze")
        .withColumn(
            "tax_id_masked",
            F.concat(F.lit("***-**-"), F.substring(F.col("tax_id"), -4, 4))
        )
        .withColumn(
            "card_number_masked",
            F.concat(F.lit("****-****-****-"), F.substring(F.col("card_number"), -4, 4))
        )
        .drop("tax_id", "card_number")
    )
```

## Deduplication Patterns

### Simple Deduplication

```python
@dlt.table(name="merchants_silver_deduped")
def merchants_silver_deduped():
    return (
        dlt.read_stream("merchants_bronze")
        .dropDuplicates(["merchant_id", "effective_date"])
    )
```

### Keep Latest Record

```python
from pyspark.sql.window import Window

@dlt.table(name="merchants_silver_latest")
def merchants_silver_latest():
    window = Window.partitionBy("merchant_id").orderBy(F.desc("_ingested_at"))
    return (
        dlt.read("merchants_bronze")
        .withColumn("_rank", F.row_number().over(window))
        .filter(F.col("_rank") == 1)
        .drop("_rank")
    )
```

## Data Quality Strategy (Silver)

Silver layer uses DROP to remove invalid records:

```python
@dlt.expect_or_drop("not_null_key", "transaction_id IS NOT NULL")
@dlt.expect_or_drop("valid_date", "transaction_date >= '2020-01-01'")
@dlt.expect_or_drop("valid_amount", "amount > 0")
```

## Type Casting Reference

| Source Type | Target Type | Pattern |
|-------------|-------------|---------|
| String amount | Decimal | `.cast(DecimalType(18, 2))` |
| String date | Date | `.cast(DateType())` |
| String timestamp | Timestamp | `F.to_timestamp(col, 'yyyyMMddHHmmss')` |
| Null handling | Default | `F.coalesce(col, F.lit(default))` |

## Related

- [Bronze Ingestion](bronze-ingestion.md) - Previous layer
- [Gold Aggregation](gold-aggregation.md) - Next layer
- [Expectations Advanced](expectations-advanced.md) - Complex validations
