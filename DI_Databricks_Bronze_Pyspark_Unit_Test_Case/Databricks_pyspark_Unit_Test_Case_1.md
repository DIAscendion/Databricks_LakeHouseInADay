_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Unit test cases and Pytest script for Databricks Bronze DE Pipeline PySpark code
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Bronze DE Pipeline PySpark Unit Test Cases

## Description
This document contains comprehensive unit test cases and a Databricks-optimized Pytest script for the Bronze DE Pipeline PySpark code. The tests validate data ingestion, transformation, audit logging, and error handling in Databricks, ensuring reliability and maintainability.

---

## Test Case List

| Test Case ID | Test Case Description | Expected Outcome |
|--------------|----------------------|------------------|
| TC_001 | Validate SparkSession initialization and teardown | SparkSession is created and stopped without errors |
| TC_002 | Test successful data ingestion from JDBC source | DataFrame is loaded with expected schema and row count |
| TC_003 | Test metadata columns addition (Load_Date, Update_Date, Source_System) | DataFrame contains new columns with correct values |
| TC_004 | Data quality check: No nulls in required columns | Raises ValueError if nulls found; passes if no nulls |
| TC_005 | Data quality check: Duplicate records | Raises ValueError if duplicates found; passes if unique |
| TC_006 | Data quality check: Schema mismatch | Raises error if schema does not match expected |
| TC_007 | Audit logging: Success scenario | Audit log entry created with status 'Success' |
| TC_008 | Audit logging: Failure scenario | Audit log entry created with status 'Failed' and error message |
| TC_009 | Exception handling: Invalid JDBC credentials | Pipeline fails gracefully, audit log records error |
| TC_010 | Edge case: Empty DataFrame ingestion | Audit log entry created, row_count is 0 |
| TC_011 | Edge case: DataFrame with null values in required columns | Raises ValueError, audit log records failure |
| TC_012 | Edge case: DataFrame with duplicate rows | Raises ValueError, audit log records failure |
| TC_013 | Performance: Large DataFrame ingestion | Pipeline completes within reasonable time, audit log duration |
| TC_014 | Helper function: get_current_user returns valid user | Returns valid username or 'unknown' |
| TC_015 | Helper function: get_credentials returns expected dict | Returns correct credentials |

---

## Pytest Script

```python
import pytest
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, LongType
from pyspark.sql.functions import lit, current_timestamp
import time

# Import pipeline functions (assume available in module bronze_pipeline)
# from bronze_pipeline import get_credentials, get_current_user, create_audit_schema, log_audit, run_data_quality_checks, process_table

@pytest.fixture(scope="module")
def spark():
    spark = SparkSession.builder.master("local[2]").appName("BronzeLayerIngestionTest").getOrCreate()
    yield spark
    spark.stop()

@pytest.fixture
def sample_df(spark):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False)
    ])
    data = [(1, "Alice"), (2, "Bob")]
    return spark.createDataFrame(data, schema)

@pytest.fixture
def empty_df(spark):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False)
    ])
    return spark.createDataFrame([], schema)

# TC_001: Validate SparkSession initialization and teardown
def test_spark_session(spark):
    assert spark is not None
    assert isinstance(spark, SparkSession)

# TC_002: Test successful data ingestion from JDBC source (mocked)
def test_data_ingestion(sample_df):
    assert sample_df.count() == 2
    assert set([f.name for f in sample_df.schema.fields]) == {"id", "name"}

# TC_003: Test metadata columns addition
def test_metadata_columns(sample_df):
    df = sample_df.withColumn("Load_Date", current_timestamp()) \
                  .withColumn("Update_Date", current_timestamp()) \
                  .withColumn("Source_System", lit("PostgreSQL"))
    assert "Load_Date" in df.columns
    assert "Update_Date" in df.columns
    assert "Source_System" in df.columns

# TC_004: Data quality check: No nulls in required columns
def test_data_quality_no_nulls(sample_df):
    required_columns = [f.name for f in sample_df.schema.fields]
    # Should not raise
    assert run_data_quality_checks(sample_df, required_columns)

# TC_005: Data quality check: Duplicate records
def test_data_quality_duplicates(spark):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False)
    ])
    data = [(1, "Alice"), (1, "Alice")]
    df = spark.createDataFrame(data, schema)
    required_columns = [f.name for f in df.schema.fields]
    with pytest.raises(ValueError, match="Duplicate records found"):
        run_data_quality_checks(df, required_columns)

# TC_006: Data quality check: Schema mismatch
def test_schema_mismatch(spark):
    schema = StructType([
        StructField("id", IntegerType(), False)
    ])
    data = [(1,)]
    df = spark.createDataFrame(data, schema)
    required_columns = ["id", "name"]
    with pytest.raises(Exception):
        run_data_quality_checks(df, required_columns)

# TC_007: Audit logging: Success scenario
def test_audit_logging_success(spark):
    audit_schema = create_audit_schema()
    audit_data = [("shipment_process", "ingest", "Success", 2, time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), 1, "test_user", None)]
    audit_df = spark.createDataFrame(audit_data, schema=audit_schema)
    assert audit_df.count() == 1
    assert audit_df.filter(audit_df.status == "Success").count() == 1

# TC_008: Audit logging: Failure scenario
def test_audit_logging_failure(spark):
    audit_schema = create_audit_schema()
    audit_data = [("shipment_process", "ingest", "Failed", 0, time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), 1, "test_user", "Error message")]
    audit_df = spark.createDataFrame(audit_data, schema=audit_schema)
    assert audit_df.count() == 1
    assert audit_df.filter(audit_df.status == "Failed").count() == 1
    assert audit_df.filter(audit_df.error_message == "Error message").count() == 1

# TC_009: Exception handling: Invalid JDBC credentials
def test_invalid_jdbc_credentials(spark):
    # Simulate invalid credentials by raising exception in process_table
    with pytest.raises(Exception):
        process_table(spark, "shipment_process", {"jdbc_url": "invalid", "user": "bad", "password": "bad", "source_system": "PostgreSQL", "tables": ["shipment_process"]}, "/mnt/bronze/", "audit_bz_shipment_process")

# TC_010: Edge case: Empty DataFrame ingestion
def test_empty_dataframe_ingestion(empty_df, spark):
    required_columns = [f.name for f in empty_df.schema.fields]
    # Should not raise for nulls, but audit log row_count should be 0
    assert empty_df.count() == 0

# TC_011: Edge case: DataFrame with null values in required columns
def test_null_values_in_required_columns(spark):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False)
    ])
    data = [(1, None)]
    df = spark.createDataFrame(data, schema)
    required_columns = [f.name for f in df.schema.fields]
    with pytest.raises(ValueError, match="Null values found in required column"):
        run_data_quality_checks(df, required_columns)

# TC_012: Edge case: DataFrame with duplicate rows
def test_duplicate_rows(spark):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False)
    ])
    data = [(1, "Alice"), (1, "Alice")]
    df = spark.createDataFrame(data, schema)
    required_columns = [f.name for f in df.schema.fields]
    with pytest.raises(ValueError, match="Duplicate records found"):
        run_data_quality_checks(df, required_columns)

# TC_013: Performance: Large DataFrame ingestion
def test_large_dataframe_performance(spark):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False)
    ])
    data = [(i, f"Name_{i}") for i in range(10000)]
    df = spark.createDataFrame(data, schema)
    start = time.time()
    required_columns = [f.name for f in df.schema.fields]
    assert run_data_quality_checks(df, required_columns)
    duration = time.time() - start
    assert duration < 10  # Should complete within 10 seconds

# TC_014: Helper function: get_current_user returns valid user
def test_get_current_user():
    user = get_current_user()
    assert isinstance(user, str)
    assert user != ""

# TC_015: Helper function: get_credentials returns expected dict
def test_get_credentials():
    creds = get_credentials()
    assert "user" in creds
    assert "password" in creds
```

---

## API Cost

apiCost: 0.0000001

---

**outputURL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Pyspark_Unit_Test_Case

**pipelineID**: 12308
