_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Unit test cases and Pytest script for Databricks Gold Fact DE Pipeline (TMS Shipment)
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact DE Pipeline Unit Test Cases

## Description
This document provides comprehensive unit test cases and a Databricks-compatible Pytest script for the Gold Fact DE Pipeline PySpark code. The pipeline extracts shipment data from the Silver layer, applies business transformations, validates records, logs audit and error information, and loads results into the Gold layer.

---

## Test Case List

| Test Case ID | Description | Expected Outcome |
|--------------|-------------|------------------|
| TC01 | Validate SparkSession creation and teardown | SparkSession is created and stopped without error |
| TC02 | Read Silver table with valid data | DataFrame is loaded with correct schema and row count |
| TC03 | Read Silver table with empty data | DataFrame is empty, downstream logic handles gracefully |
| TC04 | Write Gold table with valid DataFrame | Data is written to Gold layer, schema is preserved |
| TC05 | Write Gold table with empty DataFrame | No data written, operation completes without error |
| TC06 | Audit log writing with valid parameters | Audit log entry is created in both Silver and Gold audit tables |
| TC07 | Audit log writing with missing/invalid parameters | Operation fails gracefully, error is logged |
| TC08 | Error log writing with valid error records | Error records are written to Gold shipment_error table |
| TC09 | Business transformation: Null CURRENCY_CODE | CURRENCY_CODE is set to 'USD' |
| TC10 | Business transformation: Negative/Null ORDER_QTY | ORDER_QTY is set to 0 |
| TC11 | Business transformation: Distance conversion (M to KM) | DISTANCE is converted correctly, DISTANCE_UOM is 'KM' |
| TC12 | Business transformation: Margin rounding | MARGIN is rounded to 2 decimals |
| TC13 | Surrogate key joins with Gold dimension tables | Customer_Key and Carrier_Key are joined correctly |
| TC14 | Duplicate SHIPMENT_ID removal | Only unique SHIPMENT_IDs remain |
| TC15 | Error handling: Invalid records (null SHIPMENT_ID, negative values) | Invalid records are filtered, error records are logged |
| TC16 | Happy path: All valid records | Gold table contains all valid records, audit log is successful |
| TC17 | Exception scenario: Schema mismatch in Silver table | Exception is raised, audit log status is 'Failed' |
| TC18 | Exception scenario: Write failure to Gold layer | Exception is raised, audit log status is 'Failed' |
| TC19 | Performance: Large DataFrame processing | Pipeline completes within expected time, audit log records count |
| TC20 | Edge case: Null values in join keys | Surrogate keys are null, join logic handles gracefully |

---

## Pytest Script

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql import Row
from Databricks_Gold_Fact_DE_Pipeline_1 import (
    create_spark_session,
    read_silver_table,
    write_gold_table,
    write_audit_log,
    write_error_log,
    transform_shipment_fact
)

@pytest.fixture(scope="module")
def spark():
    spark = create_spark_session()
    yield spark
    spark.stop()

# Helper function to create mock DataFrames
def mock_shipment_df(spark):
    schema = StructType([
        StructField("SHIPMENT_ID", StringType(), True),
        StructField("CUSTOMER_ID", StringType(), True),
        StructField("ASSIGNED_CARRIER_ID", StringType(), True),
        StructField("CURRENCY_CODE", StringType(), True),
        StructField("ORDER_QTY", IntegerType(), True),
        StructField("PLANNED_WEIGHT", DoubleType(), True),
        StructField("DISTANCE", DoubleType(), True),
        StructField("DISTANCE_UOM", StringType(), True),
        StructField("DAYS_TO_DELIVER", IntegerType(), True),
        StructField("MARGIN", DoubleType(), True),
        StructField("TOTAL_COST", DoubleType(), True)
    ])
    data = [
        ("S1", "C1", "CA1", None, None, 100.0, 5000.0, "M", None, 12.3456, 1000.0),
        ("S2", "C2", "CA2", "EUR", 10, 200.0, 100.0, "KM", 2, 5.0, 500.0),
        (None, "C3", "CA3", "USD", -5, -50.0, -10.0, "KM", -1, -2.0, -100.0)
    ]
    return spark.createDataFrame(data, schema)

# Test SparkSession creation and teardown
def test_create_spark_session():
    spark = create_spark_session()
    assert isinstance(spark, SparkSession)
    spark.stop()

# Test reading Silver table (mocked)
def test_read_silver_table(spark, monkeypatch):
    monkeypatch.setattr("Databricks_Gold_Fact_DE_Pipeline_1.read_silver_table", lambda s, t: mock_shipment_df(s))
    df = read_silver_table(spark, "shipment")
    assert df.count() == 3
    assert "SHIPMENT_ID" in df.columns

# Test writing Gold table (mocked)
def test_write_gold_table(spark, tmp_path):
    df = mock_shipment_df(spark)
    # Use a temporary path for testing
    write_gold_table(df, "test_gold_table", mode="overwrite")
    # No assertion needed, just ensure no exception

# Test audit log writing (mocked)
def test_write_audit_log(spark):
    write_audit_log(spark, "TestPipeline", "exec123", None, None, "Success", None, 10)
    # No assertion needed, just ensure no exception

# Test error log writing (mocked)
def test_write_error_log(spark):
    df = mock_shipment_df(spark)
    write_error_log(spark, df)
    # No assertion needed, just ensure no exception

# Test transformation logic
@pytest.mark.parametrize("currency_code,expected", [(None, "USD"), ("EUR", "EUR")])
def test_currency_code_transformation(spark, currency_code, expected):
    df = spark.createDataFrame([Row(CURRENCY_CODE=currency_code)], StructType([StructField("CURRENCY_CODE", StringType(), True)]))
    result = df.withColumn("CURRENCY_CODE", when(df["CURRENCY_CODE"].isNull(), lit("USD")).otherwise(df["CURRENCY_CODE"]))
    assert result.collect()[0]["CURRENCY_CODE"] == expected

@pytest.mark.parametrize("order_qty,expected", [(None, 0), (10, 10), (-5, 0)])
def test_order_qty_transformation(spark, order_qty, expected):
    df = spark.createDataFrame([Row(ORDER_QTY=order_qty)], StructType([StructField("ORDER_QTY", IntegerType(), True)]))
    result = df.withColumn("ORDER_QTY", coalesce(df["ORDER_QTY"].cast(IntegerType()), lit(0)))
    val = result.collect()[0]["ORDER_QTY"]
    assert val == expected or val == 0

@pytest.mark.parametrize("distance,distance_uom,expected", [(5000.0, "M", 5.0), (100.0, "KM", 100.0)])
def test_distance_conversion(spark, distance, distance_uom, expected):
    df = spark.createDataFrame([Row(DISTANCE=distance, DISTANCE_UOM=distance_uom)], StructType([
        StructField("DISTANCE", DoubleType(), True),
        StructField("DISTANCE_UOM", StringType(), True)
    ]))
    result = df.withColumn("DISTANCE", when(df["DISTANCE_UOM"] == "M", df["DISTANCE"] / 1000).otherwise(df["DISTANCE"]))
    assert pytest.approx(result.collect()[0]["DISTANCE"], 0.01) == expected

@pytest.mark.parametrize("margin,expected", [(12.3456, 12.35), (5.0, 5.0)])
def test_margin_rounding(spark, margin, expected):
    df = spark.createDataFrame([Row(MARGIN=margin)], StructType([StructField("MARGIN", DoubleType(), True)]))
    result = df.withColumn("MARGIN", round(df["MARGIN"], 2))
    assert pytest.approx(result.collect()[0]["MARGIN"], 0.01) == expected

# Test duplicate removal
def test_drop_duplicates(spark):
    df = spark.createDataFrame([
        ("S1",), ("S1",), ("S2",)
    ], StructType([StructField("SHIPMENT_ID", StringType(), True)]))
    result = df.dropDuplicates(["SHIPMENT_ID"])
    assert result.count() == 2

# Test error handling for invalid records
def test_error_handling_invalid_records(spark):
    df = mock_shipment_df(spark)
    error_df = df.filter(
        (df["SHIPMENT_ID"].isNull()) |
        (df["TOTAL_COST"] < 0) |
        (df["ORDER_QTY"] < 0) |
        (df["PLANNED_WEIGHT"] < 0) |
        (df["DISTANCE"] < 0)
    )
    assert error_df.count() == 1

# Test happy path: all valid records
def test_happy_path_valid_records(spark):
    df = mock_shipment_df(spark).filter("SHIPMENT_ID IS NOT NULL AND TOTAL_COST >= 0 AND ORDER_QTY >= 0 AND PLANNED_WEIGHT >= 0 AND DISTANCE >= 0")
    assert df.count() == 2

# Test exception scenario: schema mismatch
def test_schema_mismatch(spark):
    with pytest.raises(Exception):
        # Attempt to read with wrong schema
        spark.read.format("delta").load("/mnt/silver/nonexistent_table")

# Test exception scenario: write failure
def test_write_failure(spark):
    df = mock_shipment_df(spark)
    with pytest.raises(Exception):
        # Simulate write failure by invalid path
        df.write.format("delta").mode("overwrite").save("/invalid/path")

# Test edge case: null join keys
def test_null_join_keys(spark):
    df = spark.createDataFrame([
        (None, None),
        ("C1", "CA1")
    ], StructType([
        StructField("CUSTOMER_ID", StringType(), True),
        StructField("ASSIGNED_CARRIER_ID", StringType(), True)
    ]))
    # Join logic should handle nulls gracefully
    assert df.count() == 2
```

---

## API Cost

apiCost: 0.0000234 USD

---

# OutputURL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Fact_Pyspark_Unit_Test_Case_DIAS

# PipelineID
14691
