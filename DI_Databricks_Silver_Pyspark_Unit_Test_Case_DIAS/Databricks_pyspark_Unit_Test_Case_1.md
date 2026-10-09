_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks PySpark unit test cases and Pytest script for validating the Silver DE pipeline that cleanses, validates, writes Silver Delta tables, persists DQ errors, and audits execution.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case

## Description
This document provides Databricks-compatible PySpark unit test cases and a Pytest script for the `Databricks_Silver_DE_Pipeline_1.py` workflow. The pipeline reads Bronze Delta tables, applies cleansing and data quality validation, creates valid and error datasets, writes Silver Delta tables, persists error records to Silver and Gold error tables, optimizes target tables, and records audit details.

## Source Code Summary

| Component | Details |
|---|---|
| Input file | `DI_Databricks_Silver_DE_Pipeline/Databricks_Silver_DE_Pipeline_1.py` |
| Pipeline type | Databricks Silver DE Pipeline |
| Primary purpose | Validate and transform Bronze Rental Revenue-to-Cash domain data into Silver Delta tables |
| Data sources | Bronze Delta tables for rental contracts, invoices, cash receipts, customer master, branch employee |
| Targets | Silver curated tables, Silver DQ error table, Gold DQ error table, Silver audit table |
| Key transformations | trim, upper, initcap, multi-format date parsing, decimal casting, derived columns, DQ validations, duplicate removal |
| Error handling | Invalid records routed to DQ tables with error payload and reason |
| Audit handling | Audit rows appended with status, counts, duration, run_id |

## Data Sources and Targets

| Source Key | Source Table | Target Table | Major Validation/Transformation |
|---|---|---|---|
| rental_contracts | `bronze.bz_rental_contracts` | `silver.si_rental_contracts` | trim, uppercase, parse dates, validate status, negative amount checks |
| invoices | `bronze.bz_invoices` | `silver.si_invoices` | parse dates, decimal casting, invoice type validation, aging bucket derivation |
| cash_receipts | `bronze.bz_cash_receipts` | `silver.si_cash_receipts` | parse dates, payment method validation, match/unapplied amount derivation |
| customer_master | `bronze.bz_customer_master` | `silver.si_customer_master` | initcap, parse dates, status validation, negative credit limit validation |
| branch_employee | `bronze.bz_branch_employee` | `silver.si_branch_employee` | initcap, trim/upper, branch and region completeness checks |
| dq_errors | invalid records from all domains | `silver.si_data_quality_errors`, `gold.go_data_quality_errors` | persist rejected records |
| audit | process metrics | `silver.si_process_audit` | audit append |

## Key Test Scenarios Identified

1. Spark session creation with Delta configs.
2. Multi-format date parsing behavior.
3. String normalization functions for trim and upper logic.
4. Blank/null detection logic.
5. Error reason concatenation behavior.
6. Rental contract valid and invalid split.
7. Invoice aging bucket derivation.
8. Cash receipt match status and unapplied amount derivation.
9. Customer master negative credit limit handling.
10. Branch employee mandatory field validation.
11. Error dataframe structure and payload generation.
12. Error persistence when dataframe is empty vs non-empty.
13. Silver write with and without partition columns.
14. Optimize SQL invocation with and without ZORDER.
15. Audit record writing with expected schema and values.
16. Pipeline success path orchestration.
17. Pipeline exception path audit logging.
18. Empty dataframe edge cases.
19. Null-heavy input edge cases.
20. Schema/type casting exception scenarios.

## Test Case List

| Test Case ID | Test Case Description | Test Data / Scenario | Expected Outcome |
|---|---|---|---|
| TC_001 | Validate Spark session factory configuration | Create session using `SparkSessionFactory.create()` | Spark session initializes successfully with Delta-related configs set |
| TC_002 | Validate `parse_date_multi` parses `yyyy-MM-dd` | Input date `2024-01-31` | Parsed date equals `2024-01-31` |
| TC_003 | Validate `parse_date_multi` parses `MM/dd/yyyy` | Input date `01/31/2024` | Parsed date equals `2024-01-31` |
| TC_004 | Validate `parse_date_multi` parses `yyyyMMdd` | Input date `20240131` | Parsed date equals `2024-01-31` |
| TC_005 | Validate trim and uppercase normalization | Input value ` ab12 ` | Output becomes `AB12` for `trim_upper` |
| TC_006 | Validate blank detection | Null and whitespace-only values | `is_blank` evaluates to true |
| TC_007 | Validate error reason appending | Existing null error reason with failed condition | Error reason column populated with supplied text |
| TC_008 | Validate rental contracts happy path | Valid contract row | Record lands in valid dataframe with surrogate key |
| TC_009 | Validate rental contracts invalid status | Contract status outside allowed list | Record excluded from valid dataframe and error reason contains invalid status |
| TC_010 | Validate rental contracts negative daily rate | `daily_rate = -10.00` | Record routed to error dataframe |
| TC_011 | Validate rental contracts bad date order | `contract_end_date < contract_start_date` | Error reason contains date sequence validation message |
| TC_012 | Validate invoices happy path and aging bucket current | Due date today or future | Record valid with `aging_bucket = CURRENT` |
| TC_013 | Validate invoice invalid type | Unsupported `invoice_type` | Record appears in error dataframe |
| TC_014 | Validate invoice due date earlier than invoice date | Bad date sequence | Error reason contains due date validation issue |
| TC_015 | Validate invoice amount null after cast | Non-numeric invoice amount | Error reason contains amount invalid/null issue |
| TC_016 | Validate cash receipts matched scenario | Invoice id present | `match_status = MATCHED`, `unapplied_payment_amount = 0.00` |
| TC_017 | Validate cash receipts unapplied scenario | Invoice id blank/null | `match_status = UNAPPLIED`, unapplied amount equals payment amount |
| TC_018 | Validate invalid payment method | Method outside configured list | Record routed to error dataframe |
| TC_019 | Validate customer master happy path | Valid customer row | Record valid with `over_limit_indicator = N` |
| TC_020 | Validate customer master negative credit limit | `credit_limit < 0` | Record routed to error dataframe |
| TC_021 | Validate customer status invalid | Unsupported status | Error dataframe contains row with appropriate reason |
| TC_022 | Validate branch employee happy path | Valid employee row | Record written to valid dataframe |
| TC_023 | Validate branch employee null mandatory field | Missing branch_code/role/region/etc. | Row rejected with concatenated error reason |
| TC_024 | Validate duplicate removal | Duplicate business key records in source | Output contains deduplicated records only |
| TC_025 | Validate error dataframe structure | Invalid source record | Error dataframe contains expected metadata columns and JSON payload |
| TC_026 | Validate `persist_errors` with empty dataframe | Empty error dataframe | No write occurs; logger notes no invalid records |
| TC_027 | Validate `persist_errors` with data | Non-empty error dataframe | Writes executed to Silver and Gold DQ tables |
| TC_028 | Validate `write_silver` partitioned write | Partition column supplied | Writer uses partitionBy and saveAsTable |
| TC_029 | Validate optimize with zorder | Table and zorder cols supplied | SQL `OPTIMIZE ... ZORDER BY (...)` executed |
| TC_030 | Validate optimize without zorder | Table only | SQL `OPTIMIZE table` executed |
| TC_031 | Validate audit write content | Known run metrics provided | Audit dataframe appended with correct counts, status, duration, run_id |
| TC_032 | Validate pipeline success orchestration | All mocked methods succeed | Write, error persist, optimize, and audit are called; status SUCCESS |
| TC_033 | Validate pipeline failure orchestration | Transform/write raises exception | Exception re-raised, audit written with FAILED status and message |
| TC_034 | Validate empty bronze source handling | Empty input dataframe | Valid and error outputs are empty without runtime failure |
| TC_035 | Validate schema mismatch/invalid cast handling | Non-numeric decimal values | Invalid cast produces null-driven DQ rejection or exception path as applicable |

## Databricks-Compatible Pytest Script

```python
import pytest
from unittest.mock import MagicMock, patch
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from DI_Databricks_Silver_DE_Pipeline.Databricks_Silver_DE_Pipeline_1 import (
    SparkSessionFactory,
    DataQualityUtils,
    SilverPipelineConfig,
    ErrorManager,
    AuditManager,
    TableProcessor,
    DatabricksSilverDEPipeline,
)


@pytest.fixture(scope="session")
def spark():
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("silver-pipeline-unit-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def logger_mock():
    return MagicMock()


@pytest.fixture
def error_manager(spark, logger_mock):
    return ErrorManager(spark, logger_mock)


@pytest.fixture
def processor(spark, logger_mock, error_manager):
    return TableProcessor(spark, logger_mock, error_manager)


def collect_values(df, col_name):
    return [row[col_name] for row in df.select(col_name).collect()]


def test_parse_date_multi_supports_multiple_formats(spark):
    data = [("2024-01-31",), ("01/31/2024",), ("20240131",)]
    df = spark.createDataFrame(data, ["raw_date"])
    result = df.withColumn("parsed", DataQualityUtils.parse_date_multi("raw_date"))
    parsed = collect_values(result, "parsed")
    assert all(value is not None for value in parsed)


def test_trim_upper_and_blank_detection(spark):
    df = spark.createDataFrame([
        (" ab12 ",),
        ("   ",),
        (None,),
    ], ["val"])
    result = df.select(
        DataQualityUtils.trim_upper("val").alias("norm"),
        DataQualityUtils.is_blank("val").alias("is_blank")
    ).collect()
    assert result[0]["norm"] == "AB12"
    assert result[1]["is_blank"] is True
    assert result[2]["is_blank"] is True


def test_append_error_reason(spark):
    df = spark.createDataFrame([(1, None)], ["id", "error_reason"])
    result = DataQualityUtils.append_error_reason(df, F.col("id") == 1, "bad record")
    assert result.collect()[0]["error_reason"] == "bad record"


def test_validate_and_transform_rental_contracts_happy_path(spark, processor):
    schema = T.StructType([
        T.StructField("contract_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("branch_code", T.StringType(), True),
        T.StructField("sales_rep_id", T.StringType(), True),
        T.StructField("equipment_class", T.StringType(), True),
        T.StructField("contract_start_date", T.StringType(), True),
        T.StructField("contract_end_date", T.StringType(), True),
        T.StructField("contract_status", T.StringType(), True),
        T.StructField("daily_rate", T.StringType(), True),
        T.StructField("source_system", T.StringType(), True),
        T.StructField("file_path", T.StringType(), True),
        T.StructField("file_modification_time", T.TimestampType(), True),
    ])
    df = spark.createDataFrame([
        ("C1", "CU1", " br1 ", "SR1", "lift", "2024-01-01", "2024-01-10", "active", "100.00", "bronze", "/tmp/a", None)
    ], schema)

    with patch.object(processor, "read_bronze", return_value=df):
        valid_df, error_df = processor.validate_and_transform_rental_contracts()

    assert valid_df.count() == 1
    assert error_df.count() == 0
    row = valid_df.collect()[0]
    assert row["branch_code"] == "BR1"
    assert row["contract_status"] == "ACTIVE"


def test_validate_and_transform_rental_contracts_invalid_status(spark, processor):
    schema = T.StructType([
        T.StructField("contract_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("branch_code", T.StringType(), True),
        T.StructField("sales_rep_id", T.StringType(), True),
        T.StructField("equipment_class", T.StringType(), True),
        T.StructField("contract_start_date", T.StringType(), True),
        T.StructField("contract_end_date", T.StringType(), True),
        T.StructField("contract_status", T.StringType(), True),
        T.StructField("daily_rate", T.StringType(), True),
        T.StructField("source_system", T.StringType(), True),
        T.StructField("file_path", T.StringType(), True),
        T.StructField("file_modification_time", T.TimestampType(), True),
    ])
    df = spark.createDataFrame([
        ("C2", "CU2", "BR1", "SR2", "GEN", "2024-01-01", "2024-01-10", "WRONG", "10.00", "bronze", "/tmp/a", None)
    ], schema)

    with patch.object(processor, "read_bronze", return_value=df):
        valid_df, error_df = processor.validate_and_transform_rental_contracts()

    assert valid_df.count() == 0
    assert error_df.count() == 1
    assert "contract_status is invalid" in error_df.collect()[0]["error_description"]


def test_validate_and_transform_invoices_aging_bucket(spark, processor):
    schema = T.StructType([
        T.StructField("invoice_id", T.StringType(), True),
        T.StructField("contract_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("invoice_date", T.StringType(), True),
        T.StructField("due_date", T.StringType(), True),
        T.StructField("invoice_amount", T.StringType(), True),
        T.StructField("tax_amount", T.StringType(), True),
        T.StructField("invoice_type", T.StringType(), True),
        T.StructField("currency", T.StringType(), True),
        T.StructField("source_system", T.StringType(), True),
        T.StructField("file_path", T.StringType(), True),
        T.StructField("file_modification_time", T.TimestampType(), True),
    ])
    df = spark.createDataFrame([
        ("I1", "C1", "CU1", "2024-01-01", "2999-01-01", "100.00", "10.00", "invoice", "usd", "bronze", "/tmp/i", None)
    ], schema)

    with patch.object(processor, "read_bronze", return_value=df):
        valid_df, error_df = processor.validate_and_transform_invoices()

    assert error_df.count() == 0
    assert valid_df.collect()[0]["aging_bucket"] == "CURRENT"


def test_validate_and_transform_cash_receipts_unapplied(spark, processor):
    schema = T.StructType([
        T.StructField("receipt_id", T.StringType(), True),
        T.StructField("invoice_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("receipt_date", T.StringType(), True),
        T.StructField("payment_amount", T.StringType(), True),
        T.StructField("payment_method", T.StringType(), True),
        T.StructField("source_system", T.StringType(), True),
        T.StructField("file_path", T.StringType(), True),
        T.StructField("file_modification_time", T.TimestampType(), True),
    ])
    df = spark.createDataFrame([
        ("R1", None, "CU1", "2024-01-01", "55.50", "cash", "bronze", "/tmp/r", None)
    ], schema)

    with patch.object(processor, "read_bronze", return_value=df):
        valid_df, error_df = processor.validate_and_transform_cash_receipts()

    assert error_df.count() == 0
    row = valid_df.collect()[0]
    assert row["match_status"] == "UNAPPLIED"
    assert float(row["unapplied_payment_amount"]) == 55.50


def test_validate_and_transform_customer_master_negative_credit_limit(spark, processor):
    schema = T.StructType([
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("customer_name", T.StringType(), True),
        T.StructField("credit_terms", T.StringType(), True),
        T.StructField("credit_limit", T.StringType(), True),
        T.StructField("customer_since", T.StringType(), True),
        T.StructField("customer_status", T.StringType(), True),
        T.StructField("source_system", T.StringType(), True),
        T.StructField("file_path", T.StringType(), True),
        T.StructField("file_modification_time", T.TimestampType(), True),
    ])
    df = spark.createDataFrame([
        ("CU1", "abc corp", "net30", "-1.00", "2020-01-01", "ACTIVE", "bronze", "/tmp/c", None)
    ], schema)

    with patch.object(processor, "read_bronze", return_value=df):
        valid_df, error_df = processor.validate_and_transform_customer_master()

    assert valid_df.count() == 0
    assert error_df.count() == 1
    assert "credit_limit cannot be negative" in error_df.collect()[0]["error_description"]


def test_validate_and_transform_branch_employee_missing_branch_code(spark, processor):
    schema = T.StructType([
        T.StructField("employee_id", T.StringType(), True),
        T.StructField("employee_name", T.StringType(), True),
        T.StructField("role", T.StringType(), True),
        T.StructField("branch_code", T.StringType(), True),
        T.StructField("region", T.StringType(), True),
        T.StructField("collector_id", T.StringType(), True),
        T.StructField("effective_date", T.StringType(), True),
        T.StructField("source_system", T.StringType(), True),
        T.StructField("file_path", T.StringType(), True),
        T.StructField("file_modification_time", T.TimestampType(), True),
    ])
    df = spark.createDataFrame([
        ("E1", "john doe", "mgr", " ", "west", "C1", "2024-01-01", "bronze", "/tmp/e", None)
    ], schema)

    with patch.object(processor, "read_bronze", return_value=df):
        valid_df, error_df = processor.validate_and_transform_branch_employee()

    assert valid_df.count() == 0
    assert error_df.count() == 1
    assert "branch_code is null or blank" in error_df.collect()[0]["error_description"]


def test_build_error_df_contains_expected_columns(spark, error_manager):
    df = spark.createDataFrame([
        ("ID1", "/tmp/a", None, "bad")
    ], ["contract_id", "file_path", "file_modification_time", "error_reason"])
    result = error_manager.build_error_df(df, "bronze.bz_rental_contracts", "contract_id")
    expected_cols = {
        "error_sk", "source_table", "source_record_id", "source_file_path",
        "validation_rule_name", "validation_category", "error_description",
        "error_record_payload", "error_severity", "layer_name", "detected_timestamp",
        "processing_status", "load_date", "update_date", "source_system"
    }
    assert expected_cols.issubset(set(result.columns))
    assert result.count() == 1


def test_persist_errors_empty_dataframe_logs_and_skips_write(spark, logger_mock, error_manager):
    empty_schema = T.StructType([
        T.StructField("error_sk", T.LongType(), True),
        T.StructField("source_table", T.StringType(), True),
        T.StructField("source_record_id", T.StringType(), True),
        T.StructField("source_file_path", T.StringType(), True),
        T.StructField("validation_rule_name", T.StringType(), True),
        T.StructField("validation_category", T.StringType(), True),
        T.StructField("error_description", T.StringType(), True),
        T.StructField("error_record_payload", T.StringType(), True),
        T.StructField("error_severity", T.StringType(), True),
        T.StructField("layer_name", T.StringType(), True),
        T.StructField("detected_timestamp", T.TimestampType(), True),
        T.StructField("processing_status", T.StringType(), True),
        T.StructField("load_date", T.TimestampType(), True),
        T.StructField("update_date", T.TimestampType(), True),
        T.StructField("source_system", T.StringType(), True),
    ])
    df = spark.createDataFrame([], empty_schema)
    error_manager.persist_errors(df)
    logger_mock.info.assert_called()


def test_optimize_table_executes_expected_sql(spark, processor):
    with patch.object(processor.spark, "sql") as sql_mock:
        processor.optimize_table("silver.si_invoices", "customer_id, invoice_id")
        sql_mock.assert_called_once_with("OPTIMIZE silver.si_invoices ZORDER BY (customer_id, invoice_id)")


def test_audit_write_appends_audit_record(spark, logger_mock):
    audit_manager = AuditManager(spark, logger_mock)
    with patch("pyspark.sql.readwriter.DataFrameWriter.saveAsTable") as save_mock:
        import datetime
        audit_manager.write_audit(
            run_id="run-123",
            source_table="bronze.tbl",
            target_table="silver.tbl",
            start_ts=datetime.datetime(2024, 1, 1, 0, 0, 0),
            end_ts=datetime.datetime(2024, 1, 1, 0, 0, 5),
            status="SUCCESS",
            records_read=10,
            records_written=8,
            records_rejected=2,
            error_message=None,
        )
        assert save_mock.called


def test_run_table_pipeline_success_path():
    pipeline = DatabricksSilverDEPipeline()
    pipeline.spark = MagicMock()
    pipeline.logger = MagicMock()
    pipeline.error_manager = MagicMock()
    pipeline.audit_manager = MagicMock()
    pipeline.processor = MagicMock()

    bronze_df = MagicMock()
    bronze_df.count.return_value = 5
    pipeline.spark.table.return_value = bronze_df

    valid_df = MagicMock()
    valid_df.count.return_value = 4
    error_df = MagicMock()
    error_df.count.return_value = 1

    transform_method = MagicMock(return_value=(valid_df, error_df))

    pipeline.run_table_pipeline(
        source_key="invoices",
        target_key="invoices",
        transform_method=transform_method,
        partition_columns=["invoice_date"],
        zorder_cols="customer_id, contract_id",
    )

    pipeline.processor.write_silver.assert_called_once()
    pipeline.error_manager.persist_errors.assert_called_once_with(error_df)
    pipeline.processor.optimize_table.assert_called_once()
    pipeline.audit_manager.write_audit.assert_called_once()


def test_run_table_pipeline_failure_path():
    pipeline = DatabricksSilverDEPipeline()
    pipeline.spark = MagicMock()
    pipeline.logger = MagicMock()
    pipeline.error_manager = MagicMock()
    pipeline.audit_manager = MagicMock()
    pipeline.processor = MagicMock()

    bronze_df = MagicMock()
    bronze_df.count.return_value = 5
    pipeline.spark.table.return_value = bronze_df

    transform_method = MagicMock(side_effect=Exception("forced failure"))

    with pytest.raises(Exception, match="forced failure"):
        pipeline.run_table_pipeline(
            source_key="invoices",
            target_key="invoices",
            transform_method=transform_method,
            partition_columns=["invoice_date"],
            zorder_cols="customer_id, contract_id",
        )

    pipeline.audit_manager.write_audit.assert_called_once()

```

## Execution Notes for Databricks

| Area | Recommendation |
|---|---|
| Spark setup | Use session-scoped Spark fixture with minimal shuffle partitions for unit tests |
| External dependencies | Mock `spark.table`, `saveAsTable`, and `spark.sql` to avoid real metastore and Delta writes |
| DQ/error validation | Assert valid and rejected dataframe counts plus exact error messages |
| Performance awareness | Keep test datasets very small and avoid wide transformations in unit tests |
| Databricks compatibility | Store test file under repo test folder and execute with `pytest` in Databricks Repos or CI runner |
| Maintainability | Group tests by utility, transformation, persistence, and orchestration layers |

## Suggested Test File Name

`test_databricks_silver_de_pipeline.py`

## API Cost
apiCost: 0.000000
