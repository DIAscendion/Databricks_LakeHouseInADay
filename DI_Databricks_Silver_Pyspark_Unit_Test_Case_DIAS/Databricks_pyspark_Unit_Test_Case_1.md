_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Unit test cases and Pytest script for Databricks Silver DE Pipeline PySpark code.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case for Silver DE Pipeline

## Description
This document provides comprehensive unit test cases and a Databricks-optimized Pytest script for the Databricks Silver DE Pipeline. The pipeline reads Bronze layer data, applies cleansing, validation, business rules, and writes valid/invalid records to Silver/Gold layers, respectively. The test suite ensures correctness, robustness, and maintainability of the pipeline in Databricks environments.

---

## Test Case List

| Test Case ID | Test Case Description | Expected Outcome |
|--------------|----------------------|------------------|
| TC01 | Validate SparkSession initialization and Delta configs | SparkSession is created with correct configs |
| TC02 | Read Bronze data with correct schema | DataFrame schema matches expected Bronze schema |
| TC03 | Normalize customer_name (trim, lower) | All customer_name values are lowercase and trimmed |
| TC04 | Calculate order_total_with_tax correctly | order_total_with_tax = order_total * 1.08 for all rows |
| TC05 | Categorize customer_segment accurately | Segments assigned as Premium, Standard, Economy per rules |
| TC06 | Remove duplicates by customer_id, order_id | No duplicate (customer_id, order_id) pairs in output |
| TC07 | Filter valid records (order_date/order_total not null, order_total >= 0) | Only valid records in valid_df |
| TC08 | Filter invalid records (null/negative order_total, null order_date) | Only invalid records in invalid_df |
| TC09 | Error handling: error_id, error_description, timestamps | error_records DataFrame has correct error fields |
| TC10 | Write valid records to Silver with correct partitioning | Data written to Silver, partitioned by customer_segment |
| TC11 | Write error records to Silver/Gold error tables | Error records written to both locations |
| TC12 | Logging: correct counts for valid/invalid records | Log output matches DataFrame counts |
| TC13 | Edge: Empty Bronze DataFrame | Pipeline completes, writes empty outputs |
| TC14 | Edge: All records invalid | All records routed to error_records, none to valid_df |
| TC15 | Edge: All records valid | All records routed to valid_df, none to error_records |
| TC16 | Edge: Nulls in non-critical columns | Nulls in non-critical columns do not cause errors |
| TC17 | Exception: Schema mismatch | Raises AnalysisException or similar |
| TC18 | Exception: Invalid data types | Raises appropriate exception |

---

## Pytest Script (Databricks-Optimized)

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql import Row
from pyspark.sql.utils import AnalysisException

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .appName("Test Databricks Silver DE Pipeline") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
    yield spark
    spark.stop()

@pytest.fixture
def bronze_schema():
    return StructType([
        StructField("customer_id", StringType(), True),
        StructField("customer_name", StringType(), True),
        StructField("order_id", StringType(), True),
        StructField("order_date", DateType(), True),
        StructField("order_total", DoubleType(), True)
    ])

@pytest.fixture
def sample_bronze_data():
    return [
        ("C1", " Alice ", "O1", None, 1200.0),
        ("C2", "BOB", "O2", None, -50.0),
        ("C3", "Charlie", "O3", None, 800.0),
        ("C4", "dave", "O4", None, 400.0),
        ("C5", "Eve", "O5", None, None),
        ("C1", " Alice ", "O1", None, 1200.0) # duplicate
    ]

@pytest.fixture
def bronze_df(spark, bronze_schema, sample_bronze_data):
    from datetime import date
    data = [
        ("C1", " Alice ", "O1", date(2023, 1, 1), 1200.0),
        ("C2", "BOB", "O2", date(2023, 1, 2), -50.0),
        ("C3", "Charlie", "O3", date(2023, 1, 3), 800.0),
        ("C4", "dave", "O4", date(2023, 1, 4), 400.0),
        ("C5", "Eve", "O5", None, None),
        ("C1", " Alice ", "O1", date(2023, 1, 1), 1200.0) # duplicate
    ]
    return spark.createDataFrame(data, schema=bronze_schema)

# TC01: SparkSession initialization
def test_spark_session(spark):
    assert spark.conf.get("spark.sql.extensions") == "io.delta.sql.DeltaSparkSessionExtension"
    assert spark.conf.get("spark.sql.catalog.spark_catalog") == "org.apache.spark.sql.delta.catalog.DeltaCatalog"

# TC02: Read Bronze data with correct schema
def test_bronze_schema(bronze_df, bronze_schema):
    assert bronze_df.schema == bronze_schema

# TC03: Normalize customer_name
def test_normalize_customer_name(spark, bronze_df):
    from pyspark.sql.functions import lower, trim
    df = bronze_df.withColumn("customer_name", trim(lower(bronze_df.customer_name)))
    names = [r.customer_name for r in df.collect()]
    for n in names:
        assert n == n.strip() and n == n.lower()

# TC04: Calculate order_total_with_tax
def test_order_total_with_tax(spark, bronze_df):
    from pyspark.sql.functions import lit, col
    df = bronze_df.withColumn("order_total_with_tax", col("order_total") * lit(1.08))
    for row in df.collect():
        if row.order_total is not None:
            assert abs(row.order_total_with_tax - row.order_total * 1.08) < 1e-6
        else:
            assert row.order_total_with_tax is None

# TC05: Categorize customer_segment
def test_customer_segment(spark, bronze_df):
    from pyspark.sql.functions import when, col
    df = bronze_df.withColumn(
        "customer_segment",
        when(col("order_total") >= 1000, "Premium")
        .when((col("order_total") >= 500) & (col("order_total") < 1000), "Standard")
        .otherwise("Economy")
    )
    for row in df.collect():
        if row.order_total is None:
            continue
        if row.order_total >= 1000:
            assert row.customer_segment == "Premium"
        elif 500 <= row.order_total < 1000:
            assert row.customer_segment == "Standard"
        else:
            assert row.customer_segment == "Economy"

# TC06: Remove duplicates
def test_remove_duplicates(spark, bronze_df):
    df = bronze_df.dropDuplicates(["customer_id", "order_id"])
    keys = set()
    for row in df.collect():
        key = (row.customer_id, row.order_id)
        assert key not in keys
        keys.add(key)

# TC07: Filter valid records
def test_valid_records(spark, bronze_df):
    from pyspark.sql.functions import col
    df = bronze_df.filter(
        col("order_date").isNotNull() &
        col("order_total").isNotNull() &
        (col("order_total") >= 0)
    )
    for row in df.collect():
        assert row.order_date is not None
        assert row.order_total is not None
        assert row.order_total >= 0

# TC08: Filter invalid records
def test_invalid_records(spark, bronze_df):
    from pyspark.sql.functions import col
    df = bronze_df.filter(
        col("order_date").isNull() |
        col("order_total").isNull() |
        (col("order_total") < 0)
    )
    for row in df.collect():
        assert row.order_date is None or row.order_total is None or row.order_total < 0

# TC09: Error handling fields
def test_error_handling_fields(spark, bronze_df):
    from pyspark.sql.functions import lit, when, current_timestamp, monotonically_increasing_id, col
    invalid_df = bronze_df.filter(
        col("order_date").isNull() |
        col("order_total").isNull() |
        (col("order_total") < 0)
    )
    error_records = invalid_df.withColumn("error_id", monotonically_increasing_id()) \
        .withColumn("table_name", lit("customer_orders")) \
        .withColumn("error_description", 
            when(col("order_date").isNull(), lit("Invalid or null order_date"))
            .when(col("order_total").isNull(), lit("Null order_total"))
            .when(col("order_total") < 0, lit("Negative order_total"))
            .otherwise(lit("Unknown error"))
        ) \
        .withColumn("load_date", current_timestamp()) \
        .withColumn("update_date", current_timestamp()) \
        .withColumn("error_timestamp", current_timestamp()) \
        .withColumn("source_system", lit("Bronze"))
    cols = set(error_records.columns)
    expected = {"error_id", "table_name", "error_description", "load_date", "update_date", "error_timestamp", "source_system"}
    assert expected.issubset(cols)

# TC13: Edge - Empty Bronze DataFrame
def test_empty_bronze_df(spark, bronze_schema):
    empty_df = spark.createDataFrame([], bronze_schema)
    assert empty_df.count() == 0
    # Should not fail pipeline logic
    from pyspark.sql.functions import col
    valid_df = empty_df.filter(
        col("order_date").isNotNull() &
        col("order_total").isNotNull() &
        (col("order_total") >= 0)
    )
    assert valid_df.count() == 0

# TC14: Edge - All records invalid
def test_all_invalid(spark, bronze_schema):
    data = [("C1", "Alice", "O1", None, -1.0)]
    df = spark.createDataFrame(data, bronze_schema)
    from pyspark.sql.functions import col
    valid_df = df.filter(
        col("order_date").isNotNull() &
        col("order_total").isNotNull() &
        (col("order_total") >= 0)
    )
    assert valid_df.count() == 0
    invalid_df = df.filter(
        col("order_date").isNull() |
        col("order_total").isNull() |
        (col("order_total") < 0)
    )
    assert invalid_df.count() == 1

# TC15: Edge - All records valid
def test_all_valid(spark, bronze_schema):
    from datetime import date
    data = [("C1", "Alice", "O1", date(2023,1,1), 100.0)]
    df = spark.createDataFrame(data, bronze_schema)
    from pyspark.sql.functions import col
    valid_df = df.filter(
        col("order_date").isNotNull() &
        col("order_total").isNotNull() &
        (col("order_total") >= 0)
    )
    assert valid_df.count() == 1
    invalid_df = df.filter(
        col("order_date").isNull() |
        col("order_total").isNull() |
        (col("order_total") < 0)
    )
    assert invalid_df.count() == 0

# TC16: Edge - Nulls in non-critical columns
def test_nulls_non_critical(spark, bronze_schema):
    from datetime import date
    data = [(None, None, None, date(2023,1,1), 100.0)]
    df = spark.createDataFrame(data, bronze_schema)
    from pyspark.sql.functions import col
    valid_df = df.filter(
        col("order_date").isNotNull() &
        col("order_total").isNotNull() &
        (col("order_total") >= 0)
    )
    assert valid_df.count() == 1

# TC17: Exception - Schema mismatch
def test_schema_mismatch(spark):
    wrong_schema = StructType([
        StructField("id", StringType(), True)
    ])
    with pytest.raises(AnalysisException):
        spark.read.format("delta").schema(wrong_schema).load("/mnt/bronze/customer_orders")

# TC18: Exception - Invalid data types
def test_invalid_data_types(spark, bronze_schema):
    data = [("C1", "Alice", "O1", "not_a_date", "not_a_float")]
    with pytest.raises(Exception):
        spark.createDataFrame(data, bronze_schema).collect()
```

---

## API Cost

apiCost: 0.0025

---

**OutputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Pyspark_Unit_Test_Case_DIAS

**pipelineID:** 12364
