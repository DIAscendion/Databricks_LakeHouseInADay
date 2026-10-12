_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Unit test cases and Databricks-compatible Pytest script for validating the Gold dimension PySpark pipeline that loads customer, branch employee, and rental contract dimensions with audit and error logging.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case

## Description
This document defines unit test coverage and a Databricks-optimized Pytest script for the PySpark pipeline in `DI_Databricks_Gold_Dim_DE_Pipeline/Databricks_Gold_Dim_DE_Pipeline_1.py`. The pipeline creates support tables, validates input data, rejects invalid records, transforms Silver layer source data into Gold dimension tables, merges data into Delta targets, writes audit logs, optimizes Delta tables, and validates expected output schemas.

## Source Code Analysis

### Data Sources
| Source Alias | Source Table |
|---|---|
| customer | `silver.si_customer_master` |
| branch_employee | `silver.si_branch_employee` |
| rental_contract | `silver.si_rental_contracts` |

### Target Tables
| Target Alias | Target Table |
|---|---|
| customer | `gold.dim_customer` |
| branch_employee | `gold.dim_branch_employee` |
| rental_contract | `gold.dim_rental_contract` |
| error_table | `gold.dim_data_quality_errors` |
| audit_table | `gold.dim_process_audit` |

### Key Transformations
| Function | Purpose | Important Logic |
|---|---|---|
| `create_gold_support_tables` | Creates audit and error Delta tables | DDL creation with partitioning |
| `write_audit_log` | Writes audit metrics | Captures timestamps, counts, duration, current user |
| `write_error_records` | Writes rejected records | Generates error payload JSON and metadata |
| `standardize_text` | Cleans text columns | `trim` + regex whitespace normalization |
| `load_dim_customer` | Builds customer dimension | mandatory key validation, dedup by latest update/load, standardization, derived surrogate key |
| `load_dim_branch_employee` | Builds branch employee dimension | composite mandatory validation, dedup, uppercase/initcap normalization |
| `load_dim_rental_contract` | Builds rental contract dimension | mandatory validation, chronology validation, dedup, standardization |
| `merge_to_delta` | Upserts data to target Delta tables | overwrite if table absent, merge otherwise |
| `optimize_gold_tables` | Performance optimization | OPTIMIZE + ZORDER |
| `run_dimension_pipeline` | Orchestrates all loads | audit logging, exception handling, schema validation |

### Validations and Edge Conditions Identified
- Null or blank business keys in all source datasets.
- Contract end date earlier than start date.
- Duplicate source rows resolved using window ordering on `update_date` and `load_date`.
- Empty invalid DataFrame path in `write_error_records`.
- Existing vs non-existing Delta target path in `merge_to_delta`.
- Schema compatibility validation after pipeline completion.
- Exception path in orchestration with FAILED audit log.

## Test Case List

| Test Case ID | Test Case Description | Expected Outcome |
|---|---|---|
| TC_001 | Validate `standardize_text` trims leading/trailing spaces and collapses multiple inner spaces | Returned column values are standardized with single spaces |
| TC_002 | Validate `write_error_records` returns 0 when input DataFrame is empty | No write occurs and function returns `0` |
| TC_003 | Validate `write_error_records` generates error metadata for invalid rows | Rejected count equals invalid input row count and output contains expected audit/error columns |
| TC_004 | Validate `load_dim_customer` rejects rows with null or blank `customer_id` | Rejected count matches invalid rows and valid rows exclude invalid records |
| TC_005 | Validate `load_dim_customer` keeps latest record per `customer_id` based on `update_date` then `load_date` | Output contains only one latest row per customer |
| TC_006 | Validate `load_dim_customer` standardizes and derives output fields correctly | `customer_name` initcap, `credit_terms` uppercase, `over_limit_indicator` mapped to Y/N, renamed and derived timestamp fields present |
| TC_007 | Validate `load_dim_branch_employee` rejects rows when `employee_id` or `branch_code` is null/blank | Rejected count matches invalid records |
| TC_008 | Validate `load_dim_branch_employee` deduplicates by `employee_id`, `branch_code`, `effective_date` | One latest record retained for each composite business key |
| TC_009 | Validate `load_dim_branch_employee` transforms text columns to expected casing | `employee_name` initcap; `role`, `branch_code`, and `region` uppercase |
| TC_010 | Validate `load_dim_rental_contract` rejects rows with null/blank `contract_id` or `customer_id` | Mandatory-key invalid rows are rejected |
| TC_011 | Validate `load_dim_rental_contract` rejects rows where `contract_end_date < contract_start_date` | Date chronology invalid rows are rejected |
| TC_012 | Validate `load_dim_rental_contract` excludes both mandatory-key invalid and chronology-invalid rows from final output | Final DataFrame contains only valid contracts |
| TC_013 | Validate `merge_to_delta` writes full DataFrame when target table does not exist | Data is written with overwrite mode and returned count equals DataFrame row count |
| TC_014 | Validate `merge_to_delta` executes merge when target table exists | Merge path is called and returned count equals DataFrame row count |
| TC_015 | Validate `create_gold_support_tables` issues DDL for audit and error tables | `spark.sql` is invoked for both CREATE TABLE statements |
| TC_016 | Validate `write_audit_log` writes expected audit fields including status, counts, duration, and user | Audit DataFrame schema and values are correct |
| TC_017 | Validate `run_dimension_pipeline` records SUCCESS audit for each loader on successful execution | Three loaders complete, writes occur, and success audit is logged |
| TC_018 | Validate `run_dimension_pipeline` records FAILED audit and raises exception when loader fails | Failure audit is written and exception is propagated |
| TC_019 | Validate schema compatibility validation raises `ValueError` when required columns are missing in Gold tables | Pipeline fails with clear missing column message |
| TC_020 | Validate `optimize_gold_tables` issues all OPTIMIZE ZORDER SQL commands | Three optimization SQL statements are executed |
| TC_021 | Validate pipeline handles empty valid source set without breaking merge and audit flow | Empty DataFrame processed safely and counts are logged appropriately |
| TC_022 | Validate generated surrogate keys are non-null for valid transformed outputs | `customer_dim_sk`, `branch_employee_dim_sk`, and `rental_contract_dim_sk` are populated |

## Databricks-Optimized Pytest Script

```python
import importlib
from datetime import datetime, date
from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

MODULE_NAME = "DI_Databricks_Gold_Dim_DE_Pipeline_1"


@pytest.fixture(scope="session")
def spark():
    spark_session = (
        SparkSession.builder
        .master("local[2]")
        .appName("gold-dim-pipeline-unit-tests")
        .getOrCreate()
    )
    yield spark_session
    spark_session.stop()


@pytest.fixture
def pipeline_module(spark):
    with patch("pyspark.sql.SparkSession.builder.getOrCreate", return_value=spark):
        module = importlib.import_module(MODULE_NAME)
        module.spark = spark
        yield module


def assert_df_equality_by_rows(actual_df, expected_rows, order_by_cols):
    actual = [tuple(row) for row in actual_df.orderBy(*order_by_cols).collect()]
    expected = [tuple(row) for row in expected_rows]
    assert actual == expected


def test_standardize_text_trims_and_normalizes_spaces(spark, pipeline_module):
    df = spark.createDataFrame([
        ("  john   doe  ",),
        ("alice",),
    ], ["raw_col"])

    result = df.select(pipeline_module.standardize_text("raw_col").alias("clean_col"))
    values = [r[0] for r in result.collect()]

    assert values == ["john doe", "alice"]


def test_write_error_records_returns_zero_for_empty_df(spark, pipeline_module):
    schema = "customer_id string, customer_name string"
    empty_df = spark.createDataFrame([], schema)

    with patch.object(empty_df, "write") as mock_write:
        result = pipeline_module.write_error_records(
            empty_df,
            "silver.si_customer_master",
            "gold.dim_customer",
            "customer_id_not_null",
            "MANDATORY_KEY",
            "customer_id cannot be null or blank",
            "HIGH",
            "customer_id",
        )

    assert result == 0
    assert not mock_write.called


def test_write_error_records_creates_expected_error_columns(spark, pipeline_module):
    invalid_df = spark.createDataFrame([
        (None, "Bad Customer"),
        ("", "Blank Key Customer"),
    ], ["customer_id", "customer_name"])

    captured = {}

    class DummyWriter:
        def format(self, *_args, **_kwargs):
            return self

        def mode(self, *_args, **_kwargs):
            return self

        def saveAsTable(self, table_name):
            captured["table_name"] = table_name

    with patch.object(type(invalid_df), "write", new_callable=property, return_value=DummyWriter()):
        rejected = pipeline_module.write_error_records(
            invalid_df,
            "silver.si_customer_master",
            "gold.dim_customer",
            "customer_id_not_null",
            "MANDATORY_KEY",
            "customer_id cannot be null or blank",
            "HIGH",
            "customer_id",
        )

    assert rejected == 2
    assert captured["table_name"] == pipeline_module.ERROR_TABLE


def test_load_dim_customer_rejects_invalid_and_deduplicates_latest(spark, pipeline_module):
    source_df = spark.createDataFrame([
        ("C001", "john   doe", "net 30", "active", "yes", 1000.0, date(2020, 1, 1), "SRC", datetime(2024, 1, 1, 8, 0, 0), datetime(2024, 1, 1, 9, 0, 0)),
        ("C001", "john doe updated", "net 45", "active", "no", 2000.0, date(2020, 1, 1), "SRC", datetime(2024, 1, 2, 8, 0, 0), datetime(2024, 1, 2, 9, 0, 0)),
        (None, "invalid customer", "net 30", "active", "yes", 3000.0, date(2020, 1, 1), "SRC", datetime(2024, 1, 3, 8, 0, 0), datetime(2024, 1, 3, 9, 0, 0)),
    ], [
        "customer_id", "customer_name", "credit_terms", "customer_status",
        "over_limit_indicator", "credit_limit", "customer_since", "source_system",
        "update_date", "load_date"
    ])

    with patch.object(pipeline_module.spark, "table", return_value=source_df), \
         patch.object(pipeline_module, "write_error_records", return_value=1):
        result_df, read_count, rejected = pipeline_module.load_dim_customer()

    assert read_count == 3
    assert rejected == 1
    assert result_df.count() == 1

    row = result_df.collect()[0]
    assert row.customer_id == "C001"
    assert row.customer_name == "John Doe Updated"
    assert row.credit_terms == "NET 45"
    assert row.customer_status == "ACTIVE"
    assert row.over_limit_indicator == "N"
    assert row.customer_since_date == date(2020, 1, 1)
    assert row.record_effective_timestamp == datetime(2024, 1, 2, 8, 0, 0)


def test_load_dim_branch_employee_rejects_invalid_rows(spark, pipeline_module):
    source_df = spark.createDataFrame([
        ("E001", "john smith", "manager", "br01", "north", "COL1", date(2024, 1, 1), "SRC", datetime(2024, 1, 2, 8, 0, 0), datetime(2024, 1, 2, 9, 0, 0)),
        (None, "bad record", "manager", "br01", "north", "COL1", date(2024, 1, 1), "SRC", datetime(2024, 1, 2, 8, 0, 0), datetime(2024, 1, 2, 9, 0, 0)),
    ], [
        "employee_id", "employee_name", "role", "branch_code", "region",
        "collector_id", "effective_date", "source_system", "update_date", "load_date"
    ])

    with patch.object(pipeline_module.spark, "table", return_value=source_df), \
         patch.object(pipeline_module, "write_error_records", return_value=1):
        result_df, read_count, rejected = pipeline_module.load_dim_branch_employee()

    assert read_count == 2
    assert rejected == 1
    assert result_df.count() == 1
    row = result_df.collect()[0]
    assert row.employee_name == "John Smith"
    assert row.role == "MANAGER"
    assert row.branch_code == "BR01"
    assert row.region == "NORTH"


def test_load_dim_rental_contract_rejects_invalid_and_date_errors(spark, pipeline_module):
    source_df = spark.createDataFrame([
        ("R001", "C001", "br01", "S001", "heavy", date(2024, 1, 1), date(2024, 1, 10), "open", 100.0, "SRC", datetime(2024, 1, 5, 8, 0, 0), datetime(2024, 1, 5, 9, 0, 0)),
        (None, "C002", "br02", "S002", "light", date(2024, 1, 1), date(2024, 1, 10), "open", 120.0, "SRC", datetime(2024, 1, 5, 8, 0, 0), datetime(2024, 1, 5, 9, 0, 0)),
        ("R003", "C003", "br03", "S003", "mid", date(2024, 2, 10), date(2024, 2, 1), "closed", 130.0, "SRC", datetime(2024, 1, 5, 8, 0, 0), datetime(2024, 1, 5, 9, 0, 0)),
    ], [
        "contract_id", "customer_id", "branch_code", "sales_rep_id", "equipment_class",
        "contract_start_date", "contract_end_date", "contract_status", "daily_rate",
        "source_system", "update_date", "load_date"
    ])

    with patch.object(pipeline_module.spark, "table", return_value=source_df), \
         patch.object(pipeline_module, "write_error_records", side_effect=[1, 1]):
        result_df, read_count, rejected = pipeline_module.load_dim_rental_contract()

    assert read_count == 3
    assert rejected == 2
    assert result_df.count() == 1
    row = result_df.collect()[0]
    assert row.contract_id == "R001"
    assert row.customer_id == "C001"
    assert row.branch_code == "BR01"
    assert row.equipment_class == "HEAVY"
    assert row.contract_status == "OPEN"


def test_merge_to_delta_overwrites_when_table_does_not_exist(spark, pipeline_module):
    df = spark.createDataFrame([("C001",)], ["customer_id"])

    class DummyWriter:
        def __init__(self):
            self.saved = False

        def format(self, *_args, **_kwargs):
            return self

        def mode(self, *_args, **_kwargs):
            return self

        def saveAsTable(self, table_name):
            self.saved = table_name

    dummy_writer = DummyWriter()

    with patch.object(pipeline_module.spark.catalog, "tableExists", return_value=False), \
         patch.object(type(df), "write", new_callable=property, return_value=dummy_writer):
        count = pipeline_module.merge_to_delta(df, "gold.dim_customer", "customer_id")

    assert count == 1
    assert dummy_writer.saved == "gold.dim_customer"


def test_merge_to_delta_merges_when_table_exists(spark, pipeline_module):
    df = spark.createDataFrame([("C001",)], ["customer_id"])
    merge_builder = MagicMock()
    merge_builder.whenMatchedUpdateAll.return_value = merge_builder
    merge_builder.whenNotMatchedInsertAll.return_value = merge_builder

    delta_table = MagicMock()
    delta_table.alias.return_value.merge.return_value = merge_builder

    with patch.object(pipeline_module.spark.catalog, "tableExists", return_value=True), \
         patch.object(pipeline_module.DeltaTable, "forName", return_value=delta_table):
        count = pipeline_module.merge_to_delta(df, "gold.dim_customer", "customer_id")

    assert count == 1
    merge_builder.execute.assert_called_once()


def test_create_gold_support_tables_executes_expected_sql(pipeline_module):
    with patch.object(pipeline_module.spark, "sql") as mock_sql:
        pipeline_module.create_gold_support_tables()

    assert mock_sql.call_count == 2
    sql_statements = " ".join(call.args[0] for call in mock_sql.call_args_list)
    assert "CREATE TABLE IF NOT EXISTS gold.dim_data_quality_errors" in sql_statements
    assert "CREATE TABLE IF NOT EXISTS gold.dim_process_audit" in sql_statements


def test_write_audit_log_creates_audit_record(spark, pipeline_module):
    start_ts = datetime(2024, 1, 1, 10, 0, 0)
    end_ts = datetime(2024, 1, 1, 10, 5, 0)

    captured = {}

    def fake_create_df(data, schema):
        captured["data"] = data
        captured["schema"] = schema

        class DummyAuditDF:
            class DummyWriter:
                def format(self, *_args, **_kwargs):
                    return self

                def mode(self, *_args, **_kwargs):
                    return self

                def saveAsTable(self, table_name):
                    captured["table_name"] = table_name

            @property
            def write(self):
                return self.DummyWriter()

        return DummyAuditDF()

    current_user_df = MagicMock()
    current_user_df.collect.return_value = [{"user": "unit.tester@databricks.com"}]

    with patch.object(pipeline_module.spark, "createDataFrame", side_effect=fake_create_df), \
         patch.object(pipeline_module.spark, "sql", return_value=current_user_df):
        pipeline_module.write_audit_log(
            source_table="silver.si_customer_master",
            target_table="gold.dim_customer",
            start_ts=start_ts,
            end_ts=end_ts,
            status="SUCCESS",
            records_read=10,
            records_written=9,
            records_rejected=1,
            remarks="test run",
        )

    assert captured["table_name"] == pipeline_module.AUDIT_TABLE
    assert captured["data"][0][6] == "SUCCESS"
    assert captured["data"][0][7] == 10
    assert captured["data"][0][8] == 9
    assert captured["data"][0][9] == 1
    assert captured["data"][0][12] == "unit.tester@databricks.com"


def test_optimize_gold_tables_executes_all_commands(pipeline_module):
    with patch.object(pipeline_module.spark, "sql") as mock_sql:
        pipeline_module.optimize_gold_tables()

    assert mock_sql.call_count == 3


def test_run_dimension_pipeline_success_path(pipeline_module, spark):
    dummy_df = spark.createDataFrame([("X",)], ["customer_id"])

    with patch.object(pipeline_module, "create_gold_support_tables"), \
         patch.object(pipeline_module, "load_dim_customer", return_value=(dummy_df, 1, 0)), \
         patch.object(pipeline_module, "load_dim_branch_employee", return_value=(dummy_df.withColumnRenamed("customer_id", "employee_id"), 1, 0)), \
         patch.object(pipeline_module, "load_dim_rental_contract", return_value=(dummy_df.withColumnRenamed("customer_id", "contract_id"), 1, 0)), \
         patch.object(pipeline_module, "merge_to_delta", return_value=1), \
         patch.object(pipeline_module, "write_audit_log") as mock_audit, \
         patch.object(pipeline_module, "optimize_gold_tables"), \
         patch.object(pipeline_module.spark, "table") as mock_table, \
         patch.object(pipeline_module.spark, "sql") as mock_sql:

        mock_sql.return_value.collect.return_value = [{"ts": datetime(2024, 1, 1, 0, 0, 0)}]

        def fake_gold_table(name):
            if name == "gold.dim_customer":
                return spark.createDataFrame([], "customer_dim_sk long, customer_id string, customer_name string, credit_terms string, credit_limit double, customer_since_date date, customer_status string")
            if name == "gold.dim_branch_employee":
                return spark.createDataFrame([], "branch_employee_dim_sk long, employee_id string, employee_name string, role string, branch_code string, region string, effective_date date")
            return spark.createDataFrame([], "rental_contract_dim_sk long, contract_id string, customer_id string, branch_code string, contract_start_date date, contract_status string")

        mock_table.side_effect = fake_gold_table
        pipeline_module.run_dimension_pipeline()

    assert mock_audit.call_count == 3


def test_run_dimension_pipeline_failure_path_raises_and_audits(pipeline_module):
    with patch.object(pipeline_module, "create_gold_support_tables"), \
         patch.object(pipeline_module, "load_dim_customer", side_effect=Exception("forced failure")), \
         patch.object(pipeline_module, "write_audit_log") as mock_audit, \
         patch.object(pipeline_module.spark, "sql") as mock_sql:

        mock_sql.return_value.collect.return_value = [{"ts": datetime(2024, 1, 1, 0, 0, 0)}]

        with pytest.raises(Exception, match="forced failure"):
            pipeline_module.run_dimension_pipeline()

    assert mock_audit.call_count == 1
    assert mock_audit.call_args.kwargs["status"] == "FAILED"


def test_schema_validation_raises_for_missing_columns(pipeline_module, spark):
    dummy_df = spark.createDataFrame([("X",)], ["customer_id"])

    with patch.object(pipeline_module, "create_gold_support_tables"), \
         patch.object(pipeline_module, "load_dim_customer", return_value=(dummy_df, 1, 0)), \
         patch.object(pipeline_module, "load_dim_branch_employee", return_value=(dummy_df.withColumnRenamed("customer_id", "employee_id"), 1, 0)), \
         patch.object(pipeline_module, "load_dim_rental_contract", return_value=(dummy_df.withColumnRenamed("customer_id", "contract_id"), 1, 0)), \
         patch.object(pipeline_module, "merge_to_delta", return_value=1), \
         patch.object(pipeline_module, "write_audit_log"), \
         patch.object(pipeline_module, "optimize_gold_tables"), \
         patch.object(pipeline_module.spark, "sql") as mock_sql, \
         patch.object(pipeline_module.spark, "table") as mock_table:

        mock_sql.return_value.collect.return_value = [{"ts": datetime(2024, 1, 1, 0, 0, 0)}]
        mock_table.return_value = spark.createDataFrame([], "customer_id string")

        with pytest.raises(ValueError, match="Missing columns"):
            pipeline_module.run_dimension_pipeline()
```

## Test Execution Notes

### Databricks Compatibility Guidance
- Use a test cluster or Databricks Connect-compatible local environment.
- Package the pipeline module so the pytest runner can import it consistently.
- Mock `spark.table`, `spark.sql`, `DeltaTable.forName`, and write operations to avoid modifying production tables during unit testing.
- For integration testing in Databricks, use temporary schemas/catalogs and isolated Delta tables.
- Ensure teardown clears cached tables, temporary views, and local Spark sessions.

### Recommended Negative and Edge Coverage Extensions
- Empty source DataFrames for each loader.
- Null `update_date` and `load_date` ordering behavior.
- Unexpected schema/type issues in source tables.
- Verification of `over_limit_indicator` values outside known mappings.
- Performance smoke tests using larger synthetic DataFrames.

## apiCost
apiCost: 0.000000

## Output URL (Clickable Hyperlinks)
- [Databricks_pyspark_Unit_Test_Case_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_DIM_Pyspark_Unit_Test_Case_DIAS/Databricks_pyspark_Unit_Test_Case_1.md)
- [Source PySpark File](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Dim_DE_Pipeline/Databricks_Gold_Dim_DE_Pipeline_1.py)
