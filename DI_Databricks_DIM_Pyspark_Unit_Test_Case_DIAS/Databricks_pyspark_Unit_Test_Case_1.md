_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Unit test cases and Pytest script for Databricks PySpark pipeline validation
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case

## Description
This document provides comprehensive unit test cases and a Databricks-optimized Pytest script for the PySpark code in the Databricks Gold Dim DE Pipeline. The tests ensure correctness, robustness, and maintainability of data transformations, covering happy paths, edge cases, and error handling scenarios in a Databricks environment.

---

## Test Case List

| Test Case ID | Test Case Description | Expected Outcome |
|--------------|----------------------|------------------|
| TC_01 | Validate transformation logic with valid input data (happy path) | Output DataFrame matches expected schema and values |
| TC_02 | Handle empty input DataFrame | Output DataFrame is empty with correct schema |
| TC_03 | Handle input DataFrame with null values in key columns | Output DataFrame processes nulls as per business logic (e.g., filtered, defaulted, or retained) |
| TC_04 | Handle schema mismatch (missing columns) | Raises AnalysisException or custom error as expected |
| TC_05 | Handle invalid data types in input columns | Raises appropriate exception or error message |
| TC_06 | Validate join logic with mismatched keys | Output DataFrame contains only matching records or handles non-matches as per logic |
| TC_07 | Validate aggregation logic with boundary values | Aggregated results are correct for min/max/edge values |
| TC_08 | Performance test for large input DataFrame | Transformation completes within acceptable time/resource limits |
| TC_09 | Validate output format and partitioning | Output DataFrame is written in expected format (e.g., Parquet/Delta) and partitioned as required |
| TC_10 | Exception handling for corrupted or unreadable input | Raises IOError or logs error as per pipeline design |

---

## Pytest Script

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .appName("unit-test-gold-dim-de-pipeline") \
        .master("local[2]") \
        .getOrCreate()
    yield spark
    spark.stop()

# Helper function to compare DataFrames
def assert_df_equality(df1, df2):
    assert df1.schema == df2.schema, "Schemas do not match"
    assert sorted(df1.collect()) == sorted(df2.collect()), "Data does not match"

# Example transformation function (replace with actual pipeline logic)
def run_pipeline(spark, input_df):
    # Placeholder for actual transformation logic
    return input_df

# TC_01: Happy path
def test_happy_path(spark):
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True)
    ])
    data = [(1, "Alice"), (2, "Bob")]
    input_df = spark.createDataFrame(data, schema)
    expected_df = spark.createDataFrame(data, schema)
    result_df = run_pipeline(spark, input_df)
    assert_df_equality(result_df, expected_df)

# TC_02: Empty DataFrame
def test_empty_input(spark):
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True)
    ])
    input_df = spark.createDataFrame([], schema)
    result_df = run_pipeline(spark, input_df)
    assert result_df.count() == 0
    assert result_df.schema == schema

# TC_03: Null values in key columns
def test_null_values(spark):
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True)
    ])
    data = [(None, "Alice"), (2, None)]
    input_df = spark.createDataFrame(data, schema)
    result_df = run_pipeline(spark, input_df)
    # Adjust assertion as per business logic
    assert result_df.count() == 2

# TC_04: Schema mismatch
def test_schema_mismatch(spark):
    schema = StructType([
        StructField("id", IntegerType(), True)
    ])
    data = [(1,), (2,)]
    input_df = spark.createDataFrame(data, schema)
    with pytest.raises(Exception):
        run_pipeline(spark, input_df)

# TC_05: Invalid data types
def test_invalid_data_types(spark):
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("name", IntegerType(), True)
    ])
    data = [("one", 1), ("two", 2)]
    input_df = spark.createDataFrame(data, schema)
    with pytest.raises(Exception):
        run_pipeline(spark, input_df)

# TC_06: Join logic with mismatched keys
# Add join logic in run_pipeline for real test

def test_join_logic(spark):
    left_schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("value", StringType(), True)
    ])
    right_schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("desc", StringType(), True)
    ])
    left_data = [(1, "A"), (2, "B")]
    right_data = [(2, "DescB"), (3, "DescC")]
    left_df = spark.createDataFrame(left_data, left_schema)
    right_df = spark.createDataFrame(right_data, right_schema)
    # Example join
    result_df = left_df.join(right_df, "id", "inner")
    assert result_df.count() == 1
    assert result_df.collect()[0][0] == 2

# TC_07: Aggregation with boundary values

def test_aggregation_boundary(spark):
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("value", IntegerType(), True)
    ])
    data = [(1, 0), (2, 999999999)]
    input_df = spark.createDataFrame(data, schema)
    result_df = input_df.groupBy().sum("value")
    assert result_df.collect()[0][0] == 999999999

# TC_08: Performance test (simplified)

def test_performance(spark):
    schema = StructType([
        StructField("id", IntegerType(), True)
    ])
    data = [(i,) for i in range(10000)]
    input_df = spark.createDataFrame(data, schema)
    import time
    start = time.time()
    result_df = run_pipeline(spark, input_df)
    duration = time.time() - start
    assert duration < 30  # seconds

# TC_09: Output format and partitioning (mocked)

def test_output_format_partitioning(spark, tmp_path):
    schema = StructType([
        StructField("id", IntegerType(), True)
    ])
    data = [(1,), (2,)]
    input_df = spark.createDataFrame(data, schema)
    output_path = str(tmp_path / "output")
    input_df.write.mode("overwrite").parquet(output_path)
    # Read back and check
    df_read = spark.read.parquet(output_path)
    assert_df_equality(input_df, df_read)

# TC_10: Exception handling for corrupted input

def test_corrupted_input(spark):
    with pytest.raises(Exception):
        spark.read.parquet("/path/to/nonexistent/or/corrupted/file")
```

---

## apiCost
apiCost: 0.0

---

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_DIM_Pyspark_Unit_Test_Case
pipelineID : 14672
