_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Unit test cases and Databricks-optimized Pytest script for Gold Layer aggregation pipeline in Databricks.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Cases for Gold Aggregated DE Pipeline

## Description
This document provides comprehensive unit test cases and a Databricks-compatible Pytest script for the Gold Layer aggregation pipeline. The pipeline reads validated transactional data from the Silver Layer, applies business transformations, creates Gold Layer fact tables, manages audit logs, handles error records, and optimizes performance using Databricks best practices.

---

## Test Case List

| Test Case ID | Test Case Description                                                                 | Expected Outcome                                                                                  |
|--------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| TC01         | Validate SparkSession creation with Delta Lake support                               | SparkSession is created successfully with Delta Lake configuration                                |
| TC02         | Read Silver table with valid table name                                              | DataFrame is returned with expected schema                                                        |
| TC03         | Read Silver table with invalid table name                                            | Exception is raised or empty DataFrame is returned                                                |
| TC04         | Write Gold table with valid DataFrame and table name                                 | Data is written to Gold layer, Delta table exists                                                 |
| TC05         | Write Gold table with empty DataFrame                                                | Delta table is created, but contains no records                                                   |
| TC06         | Write audit log with valid parameters                                                | Audit log entry is appended to audit log Delta table                                              |
| TC07         | Write audit log with missing/invalid parameters                                      | Exception is raised or log entry is not written                                                   |
| TC08         | Write error log with valid error records                                             | Error records are appended to error log Delta table                                               |
| TC09         | Transform sales fact with valid Silver data                                          | Gold Layer sales_fact table is created with correct aggregations                                  |
| TC10         | Transform sales fact with empty Silver data                                          | Gold Layer sales_fact table is created, but contains no records                                   |
| TC11         | Transform sales fact with null values in Silver data                                 | Null values are handled gracefully, aggregations are correct                                      |
| TC12         | Transform sales fact with schema mismatch                                            | Exception is raised, audit log records failure                                                    |
| TC13         | Audit log records failure when transformation fails                                  | Audit log entry with status 'Failed' is written                                                   |
| TC14         | Error log records failed rows when transformation fails                              | Error records are written to error log Delta table                                                |
| TC15         | Performance test for large Silver data                                               | Transformation completes within acceptable time, Gold Layer table is optimized                    |

---

## Pytest Script

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import datetime

# Fixtures for SparkSession
@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .appName("UnitTest_GoldAggregatedDEPipeline") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \
        .getOrCreate()
    yield spark
    spark.stop()

# Mock paths for testing
silver_path = "/tmp/silver/"
gold_path = "/tmp/gold/"
audit_log_path = "/tmp/gold/audit_logs/"
error_log_path = "/tmp/gold/error_records/"

# Utility functions (copied from pipeline for testability)
def read_silver_table(spark, table_name):
    return spark.read.format("delta").load(f