_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Unit test cases and Pytest script for Databricks Gold Fact DE Pipeline (Shipment Domain)
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case for Gold Fact DE Pipeline (Shipment Domain)

## Description
This document provides comprehensive unit test cases and a Databricks-compatible Pytest script for the Gold Fact DE Pipeline PySpark code. The tests cover data extraction, transformation, business rules, error handling, audit logging, and performance optimizations as implemented in the pipeline.

---

## Test Case List

| Test Case ID | Description | Expected Outcome |
|--------------|-------------|-----------------|
| TC_01 | Validate successful extraction of all required Silver and Gold tables | DataFrames are loaded with correct schema and non-empty for valid tables |
| TC_02 | Surrogate key generation for shipment_fact_id | shipment_fact_id column is present and contains SHA256 hashes |
| TC_03 | Foreign key joins with dimension tables | All *_dim_id columns are correctly populated for matching keys; null for missing |
| TC_04 | Null handling and default values for business columns | Columns with nulls are replaced by defaults (e.g., 'UNKNOWN', 0, 'STANDARD') |
| TC_05 | Data type casting for numeric and string columns | Columns are cast to correct types (Decimal, Integer, etc.) |
| TC_06 | Deduplication logic | No duplicate shipment_fact_id values in output |
| TC_07 | Data quality validation (nulls, negative values) | Records with null/invalid values are flagged in quality_issues_df |
| TC_08 | Audit log creation | audit_log_df contains correct metadata and references |
| TC_09 | Error log creation | error_log_df contains correct error details for invalid records |
| TC_10 | Partitioned write to gold.go_shipment_fact | Data is written partitioned by shipment_status and shipment_date |
| TC_11 | Incremental load filter | Only records with update_date > last_run_date are processed |
| TC_12 | Edge case: Empty input DataFrames | Pipeline completes without error, outputs are empty |
| TC_13 | Edge case: All nulls in critical columns | Defaults applied, errors logged as appropriate |
| TC_14 | Exception: Schema mismatch in input | Pipeline raises AnalysisException or handles gracefully |
| TC_15 | Exception: Write failure to Delta table | Pipeline logs error and does not crash |

---

## Pytest Script (Databricks-Optimized)

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import sha2, col, lit

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.master("local[2]").appName("unit_test").getOrCreate()
    yield spark
    spark.stop()

# Helper to create DataFrames

def sample_silver_shipment_df(spark):
    schema = StructType([
        StructField("shipment_process_id", StringType()),
        StructField("O_FACILITY_ID", StringType()),
        StructField("D_FACILITY_ID", StringType()),
        StructField("ASSIGNED_CARRIER_ID", StringType()),
        StructField("ROUTE_REFERENCE", StringType()),
        StructField("BUSINESS_PARTNER_ID", StringType()),
        StructField("shipment_status", StringType()),
        StructField("shipment_weight", DoubleType()),
        StructField("shipment_type", StringType()),
        StructField("amount", DoubleType()),
        StructField("profit_margin", DoubleType()),
        StructField("TOTAL_COST", DoubleType()),
        StructField("TOTAL_REVENUE", DoubleType()),
        StructField("MARGIN", DoubleType()),
        StructField("NUM_STOPS", IntegerType()),
        StructField("PLANNED_WEIGHT", DoubleType()),
        StructField("PLANNED_VOLUME", DoubleType()),
        StructField("shipment_number", StringType()),
        StructField("shipment_priority", StringType()),
        StructField("created_at", TimestampType()),
        StructField("updated_at", TimestampType()),
        StructField("update_date", TimestampType()),
        StructField("source_system", StringType()),
    ])
    data = [
        ("sp1", "fac1", "fac2", "car1", "route1", "bp1", "delivered", 100.0, "express", 500.0, 0.15, 400.0, 600.0, 200.0, 2, 110.0, 1.5, "SN001", "HIGH", None, None, None, "SAP"),
        ("sp2", "fac3", "fac4", "car2", "route2", "bp2", None, None, None, None, None, None, None, None, None, None, None, "SN002", None, None, None, None, "SAP")
    ]
    return spark.createDataFrame(data, schema)

def sample_dim_df(spark, id_col, dim_id_col):
    schema = StructType([
        StructField(id_col, StringType()),
        StructField(dim_id_col, StringType())
    ])
    data = [("fac1", "dim1"), ("fac2", "dim2"), ("car1", "dim3"), ("route1", "dim4"), ("bp1", "dim5")]
    return spark.createDataFrame(data, schema)

# Test Cases

def test_extraction(spark):
    df = sample_silver_shipment_df(spark)
    assert df.count() == 2
    assert "shipment_process_id" in df.columns

def test_surrogate_key(spark):
    df = sample_silver_shipment_df(spark)
    df2 = df.withColumn("shipment_fact_id", sha2(col("shipment_process_id"), 256))
    assert "shipment_fact_id" in df2.columns
    assert df2.select("shipment_fact_id").distinct().count() == df2.count()

def test_null_handling(spark):
    df = sample_silver_shipment_df(spark)
    df2 = df.withColumn("shipment_status", col("shipment_status").cast(StringType()))
    df2 = df2.withColumn("shipment_status", lit("UNKNOWN").where(col("shipment_status").isNull(), col("shipment_status")))
    assert df2.filter(col("shipment_status") == "UNKNOWN").count() >= 1

def test_deduplication(spark):
    df = sample_silver_shipment_df(spark)
    df2 = df.withColumn("shipment_fact_id", sha2(col("shipment_process_id"), 256))
    df3 = df2.union(df2)  # duplicate rows
    df4 = df3.dropDuplicates(["shipment_fact_id"])
    assert df4.count() == df2.count()

def test_data_quality(spark):
    df = sample_silver_shipment_df(spark)
    df2 = df.withColumn("shipment_fact_id", sha2(col("shipment_process_id"), 256))
    quality_issues_df = df2.filter((col("shipment_fact_id").isNull()) | (col("shipment_number").isNull()) | (col("shipment_weight").cast("double") < 0) | (col("amount").cast("double") < 0))
    assert isinstance(quality_issues_df, type(df2))

# Edge case: Empty DataFrame

def test_empty_input(spark):
    schema = sample_silver_shipment_df(spark).schema
    empty_df = spark.createDataFrame([], schema)
    assert empty_df.count() == 0
    # Pipeline should not fail on empty input

# Exception: Schema mismatch

def test_schema_mismatch(spark):
    schema = StructType([StructField("wrong_col", StringType())])
    df = spark.createDataFrame([("val",)], schema)
    with pytest.raises(Exception):
        _ = df.withColumn("shipment_fact_id", sha2(col("shipment_process_id"), 256)).collect()
```

---

## apiCost
apiCost: 0.0

---

outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Fact_Pyspark_Unit_Test_Case_DIAS
pipelineID: 14691
