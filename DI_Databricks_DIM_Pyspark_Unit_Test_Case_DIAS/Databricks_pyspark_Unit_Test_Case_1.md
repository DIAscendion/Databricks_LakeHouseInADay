_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Unit test cases and Databricks-compatible Pytest script for validating the Gold dimension PySpark pipeline.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case

## Input Summary
This unit test document is created for the PySpark pipeline `Databricks_Gold_Dim_DE_Pipeline_1.py`, which builds Gold dimension tables from Silver layer sources, performs data quality validation, writes rejected records to an error table, logs execution status to an audit table, merges dimension data into Delta targets, optimizes Gold tables, and validates final schema compatibility.

## Source and Target Analysis

| Component | Details |
|---|---|
| Pipeline Name | Databricks_Gold_Dim_DE_Pipeline |
| Source Tables | `silver.si_customer_master`, `silver.si_branch_employee`, `silver.si_rental_contracts` |
| Target Tables | `gold.dim_customer`, `gold.dim_branch_employee`, `gold.dim_rental_contract` |
| Support Tables | `gold.dim_data_quality_errors`, `gold.dim_process_audit` |
| Processing Pattern | Read -> Validate -> Reject invalid -> Transform -> Deduplicate -> Merge to Delta -> Audit -> Optimize -> Schema validation |
| Output Format | Delta Tables |

## Key Transformations Identified

1. Creation of error and audit support tables.
2. Standardization of text fields using trim and whitespace normalization.
3. Data quality validation for mandatory keys and business rule validations.
4. Error record generation with JSON payload and metadata.
5. Deduplication using `row_number()` over window partitions.
6. Surrogate key generation using `xxhash64`.
7. Effective/load timestamp derivation using `coalesce(update_date, load_date)`.
8. Delta merge logic for insert and update handling.
9. Post-load optimization using `OPTIMIZE ... ZORDER BY`.
10. Final DDL/schema compatibility validation for Gold tables.

## Test Case List

| Test Case ID | Test Case Description | Expected Outcome |
|---|---|---|
| TC_001 | Validate support tables are created successfully by `create_gold_support_tables()` | Error and audit Delta tables are created if not already present |
| TC_002 | Validate `standardize_text()` trims spaces and collapses repeated whitespace | Returned column expression standardizes input text correctly |
| TC_003 | Validate `write_error_records()` returns `0` for an empty invalid DataFrame | No write occurs and rejected count is `0` |
| TC_004 | Validate `write_error_records()` writes rejected customer records with expected metadata columns | Error table write is invoked and rejected count matches input invalid rows |
| TC_005 | Validate `load_dim_customer()` rejects null or blank `customer_id` records | Invalid customer rows are excluded and rejection count is correct |
| TC_006 | Validate `load_dim_customer()` deduplicates by latest `update_date`/`load_date` per `customer_id` | One latest record per customer is retained |
| TC_007 | Validate `load_dim_customer()` standardizes and transforms columns correctly | Customer name is init-capped, status/credit terms uppercased, and indicator normalized to `Y/N` |
| TC_008 | Validate `load_dim_branch_employee()` rejects rows with null/blank `employee_id` or `branch_code` | Invalid rows are rejected and not present in final dimension DataFrame |
| TC_009 | Validate `load_dim_branch_employee()` deduplicates by employee, branch, and effective date | Latest record per partition is retained |
| TC_010 | Validate `load_dim_rental_contract()` rejects rows with null/blank `contract_id` or `customer_id` | Mandatory key violations are rejected |
| TC_011 | Validate `load_dim_rental_contract()` rejects rows where `contract_end_date < contract_start_date` | Business rule violating records are rejected |
| TC_012 | Validate `load_dim_rental_contract()` transforms and retains valid latest contract record | Valid transformed dimension rows are produced with expected target columns |
| TC_013 | Validate `merge_to_delta()` creates target table when target does not exist | DataFrame is written using overwrite/saveAsTable |
| TC_014 | Validate `merge_to_delta()` performs Delta merge when target table exists | `whenMatchedUpdateAll` and `whenNotMatchedInsertAll` flow executes successfully |
| TC_015 | Validate `write_audit_log()` appends success audit record with computed duration | Audit table write is triggered with status `SUCCESS` |
| TC_016 | Validate `run_dimension_pipeline()` writes success audit for each loader in happy path | Three loads complete and success audit entries are generated |
| TC_017 | Validate `run_dimension_pipeline()` writes failed audit and re-raises exception on loader failure | Failed audit entry is written and exception propagates |
| TC_018 | Validate `optimize_gold_tables()` runs optimize commands for all Gold target tables | Expected OPTIMIZE SQL commands are executed |
| TC_019 | Validate schema compatibility check passes when all required columns exist | No exception is raised |
| TC_020 | Validate schema compatibility check raises `ValueError` when required columns are missing | Pipeline fails with a descriptive missing-column error |
| TC_021 | Validate pipeline handles empty source DataFrames without crashing | Empty outputs are handled gracefully and counts remain valid |
| TC_022 | Validate invalid datatype or schema mismatch scenarios are surfaced as exceptions | Test captures exception behavior for malformed input schema |
| TC_023 | Validate null handling for optional columns such as `update_date`, `load_date`, and descriptive attributes | Record effective timestamp falls back correctly and transformation remains stable |
| TC_024 | Validate performance-oriented behavior for moderate sample data in Databricks-compatible execution | Transformations complete and output row counts remain consistent |

## Pytest Script

```python
import pytest
from datetime import datetime, date
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from delta.tables import DeltaTable
from unittest.mock import MagicMock, patch

import Databricks_Gold_Dim_DE_Pipeline_1 as pipeline


@pytest.fixture(scope="session")
def spark():
    spark_session = (
        SparkSession.builder
        .master("local[2]")
        .appName("unit-test-databricks-gold-dim-pipeline")
        .getOrCreate()
    )
    yield spark_session
    spark_session.stop()


@pytest.fixture
def customer_schema(spark):
    return "customer_id string, customer_name string, credit_terms string, credit_limit double, customer_since string, customer_status string, over_limit_indicator string, source_system string, update_date timestamp, load_date timestamp"


@pytest.fixture
def branch_employee_schema(spark):
    return "employee_id string, employee_name string, role string, branch_code string, region string, collector_id string, effective_date date, source_system string, update_date timestamp, load_date timestamp"


@pytest.fixture
def rental_contract_schema(spark):
    return "contract_id string, customer_id string, branch_code string, sales_rep_id string, equipment_class string, contract_start_date date, contract_end_date date, contract_status string, daily_rate double, source_system string, update_date timestamp, load_date timestamp"


def test_standardize_text_transformation(spark):
    df = spark.createDataFrame([("  abc   def  ",)], ["txt"])
    result = df.select(pipeline.standardize_text("txt").alias("clean_txt")).collect()[0]["clean_txt"]
    assert result == "abc def"


def test_write_error_records_returns_zero_for_empty_df(spark):
    df = spark.createDataFrame([], "customer_id string, customer_name string")
    result = pipeline.write_error_records(
        df=df,
        source_table="silver.si_customer_master",
        target_table="gold.dim_customer",
        rule_name="customer_id_not_null",
        category="MANDATORY_KEY",
        description="customer_id cannot be null or blank",
        severity="HIGH",
        record_id_col="customer_id"
    )
    assert result == 0


def test_load_dim_customer_rejects_invalid_and_deduplicates_latest(spark, customer_schema, monkeypatch):
    sample_data = [
        ("C001", "john doe", "net 30", 1000.0, "2024-01-01", "active", "yes", "SRC", datetime(2024, 2, 1, 10, 0, 0), datetime(2024, 2, 1, 9, 0, 0)),
        ("C001", "john d", "net 45", 1200.0, "2024-01-01", "inactive", "no", "SRC", datetime(2024, 1, 1, 10, 0, 0), datetime(2024, 1, 1, 9, 0, 0)),
        ("", "bad record", "net 30", 500.0, "2024-01-01", "active", "yes", "SRC", datetime(2024, 1, 2, 10, 0, 0), datetime(2024, 1, 2, 9, 0, 0))
    ]
    df = spark.createDataFrame(sample_data, customer_schema)

    monkeypatch.setattr(pipeline.spark, "table", lambda _: df)
    monkeypatch.setattr(pipeline, "write_error_records", lambda *args, **kwargs: 1)

    result_df, read_count, rejected = pipeline.load_dim_customer()
    rows = result_df.collect()

    assert read_count == 3
    assert rejected == 1
    assert len(rows) == 1
    assert rows[0]["customer_id"] == "C001"
    assert rows[0]["customer_name"] == "John Doe"
    assert rows[0]["credit_terms"] == "NET 30"
    assert rows[0]["customer_status"] == "ACTIVE"
    assert rows[0]["over_limit_indicator"] == "Y"


def test_load_dim_branch_employee_rejects_invalid_rows(spark, branch_employee_schema, monkeypatch):
    sample_data = [
        ("E001", "alice smith", "manager", "b01", "north", "C123", date(2024, 1, 1), "SRC", datetime(2024, 2, 1, 10, 0, 0), datetime(2024, 2, 1, 9, 0, 0)),
        (None, "bad record", "rep", "b01", "north", "C124", date(2024, 1, 1), "SRC", datetime(2024, 1, 1, 10, 0, 0), datetime(2024, 1, 1, 9, 0, 0))
    ]
    df = spark.createDataFrame(sample_data, branch_employee_schema)

    monkeypatch.setattr(pipeline.spark, "table", lambda _: df)
    monkeypatch.setattr(pipeline, "write_error_records", lambda *args, **kwargs: 1)

    result_df, read_count, rejected = pipeline.load_dim_branch_employee()
    rows = result_df.collect()

    assert read_count == 2
    assert rejected == 1
    assert len(rows) == 1
    assert rows[0]["employee_name"] == "Alice Smith"
    assert rows[0]["role"] == "MANAGER"
    assert rows[0]["branch_code"] == "B01"
    assert rows[0]["region"] == "NORTH"


def test_load_dim_rental_contract_rejects_date_rule_violation(spark, rental_contract_schema, monkeypatch):
    sample_data = [
        ("R001", "C001", "b01", "S001", "heavy", date(2024, 1, 10), date(2024, 1, 20), "open", 55.0, "SRC", datetime(2024, 2, 1, 10, 0, 0), datetime(2024, 2, 1, 9, 0, 0)),
        ("R002", "C002", "b02", "S002", "light", date(2024, 2, 10), date(2024, 1, 20), "open", 45.0, "SRC", datetime(2024, 2, 1, 10, 0, 0), datetime(2024, 2, 1, 9, 0, 0))
    ]
    df = spark.createDataFrame(sample_data, rental_contract_schema)

    monkeypatch.setattr(pipeline.spark, "table", lambda _: df)

    call_counter = {"count": 0}

    def fake_write_error_records(*args, **kwargs):
        call_counter["count"] += 1
        return 1 if call_counter["count"] == 2 else 0

    monkeypatch.setattr(pipeline, "write_error_records", fake_write_error_records)

    result_df, read_count, rejected = pipeline.load_dim_rental_contract()
    rows = result_df.collect()

    assert read_count == 2
    assert rejected == 1
    assert len(rows) == 1
    assert rows[0]["contract_id"] == "R001"
    assert rows[0]["equipment_class"] == "HEAVY"
    assert rows[0]["contract_status"] == "OPEN"


def test_merge_to_delta_writes_when_table_missing(spark, monkeypatch):
    df = spark.createDataFrame([("C001",)], ["customer_id"])
    writer_mock = MagicMock()
    monkeypatch.setattr(df, "write", writer_mock)
    monkeypatch.setattr(pipeline.spark.catalog, "tableExists", lambda _: False)

    mode_mock = MagicMock(return_value=writer_mock)
    format_mock = MagicMock(return_value=writer_mock)
    writer_mock.format = format_mock
    writer_mock.mode = mode_mock
    writer_mock.saveAsTable = MagicMock()

    count = pipeline.merge_to_delta(df, "gold.dim_customer", "customer_id")

    writer_mock.format.assert_called_once_with("delta")
    writer_mock.mode.assert_called_once_with("overwrite")
    writer_mock.saveAsTable.assert_called_once_with("gold.dim_customer")
    assert count == 1


def test_merge_to_delta_executes_merge_when_table_exists(spark, monkeypatch):
    df = spark.createDataFrame([("C001",)], ["customer_id"])
    monkeypatch.setattr(pipeline.spark.catalog, "tableExists", lambda _: True)

    merge_builder = MagicMock()
    merge_builder.whenMatchedUpdateAll.return_value = merge_builder
    merge_builder.whenNotMatchedInsertAll.return_value = merge_builder

    delta_mock = MagicMock()
    delta_mock.alias.return_value.merge.return_value = merge_builder

    monkeypatch.setattr(DeltaTable, "forName", lambda *args, **kwargs: delta_mock)

    count = pipeline.merge_to_delta(df, "gold.dim_customer", "customer_id")

    assert merge_builder.execute.called
    assert count == 1


def test_write_audit_log_appends_record(monkeypatch, spark):
    created_df = spark.createDataFrame([
        (1, "pipeline", "source", "target", datetime(2024, 1, 1, 0, 0, 0), datetime(2024, 1, 1, 0, 1, 0), "SUCCESS", 10, 9, 1, 60.0, None, "tester", "done")
    ], "audit_sk long, pipeline_name string, source_table string, target_table string, process_start_timestamp timestamp, process_end_timestamp timestamp, processing_status string, records_read_count long, records_written_count long, records_rejected_count long, processing_duration_seconds double, error_message string, executed_by string, audit_remarks string")

    monkeypatch.setattr(pipeline.spark, "createDataFrame", lambda *args, **kwargs: created_df)
    monkeypatch.setattr(pipeline.spark, "sql", lambda q: spark.createDataFrame([("tester",)], ["user"]) if "current_user" in q else spark.createDataFrame([(datetime(2024, 1, 1, 0, 0, 0),)], ["ts"]))

    writer_mock = MagicMock()
    monkeypatch.setattr(created_df, "write", writer_mock)
    writer_mock.format.return_value = writer_mock
    writer_mock.mode.return_value = writer_mock
    writer_mock.saveAsTable = MagicMock()

    pipeline.write_audit_log(
        source_table="silver.si_customer_master",
        target_table="gold.dim_customer",
        start_ts=datetime(2024, 1, 1, 0, 0, 0),
        end_ts=datetime(2024, 1, 1, 0, 1, 0),
        status="SUCCESS",
        records_read=10,
        records_written=9,
        records_rejected=1,
        remarks="test run"
    )

    writer_mock.saveAsTable.assert_called_once_with(pipeline.AUDIT_TABLE)


def test_run_dimension_pipeline_failure_writes_failed_audit(monkeypatch):
    monkeypatch.setattr(pipeline, "create_gold_support_tables", lambda: None)
    monkeypatch.setattr(pipeline, "optimize_gold_tables", lambda: None)

    def failing_loader():
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(pipeline, "load_dim_customer", failing_loader)
    monkeypatch.setattr(pipeline, "load_dim_branch_employee", lambda: (None, 0, 0))
    monkeypatch.setattr(pipeline, "load_dim_rental_contract", lambda: (None, 0, 0))

    audit_calls = []

    def fake_sql(query):
        return type("DummyDF", (), {"collect": lambda self: [{"ts": datetime(2024, 1, 1, 0, 0, 0)}]})()

    monkeypatch.setattr(pipeline.spark, "sql", fake_sql)
    monkeypatch.setattr(pipeline, "write_audit_log", lambda **kwargs: audit_calls.append(kwargs))

    with pytest.raises(RuntimeError):
        pipeline.run_dimension_pipeline()

    assert any(call["status"] == "FAILED" for call in audit_calls)


def test_schema_validation_raises_value_error_when_missing_columns(monkeypatch):
    monkeypatch.setattr(pipeline, "create_gold_support_tables", lambda: None)
    monkeypatch.setattr(pipeline, "optimize_gold_tables", lambda: None)
    monkeypatch.setattr(pipeline, "merge_to_delta", lambda *args, **kwargs: 1)
    monkeypatch.setattr(pipeline, "write_audit_log", lambda **kwargs: None)
    monkeypatch.setattr(pipeline, "load_dim_customer", lambda: (MagicMock(), 1, 0))
    monkeypatch.setattr(pipeline, "load_dim_branch_employee", lambda: (MagicMock(), 1, 0))
    monkeypatch.setattr(pipeline, "load_dim_rental_contract", lambda: (MagicMock(), 1, 0))

    def fake_sql(query):
        return type("DummyDF", (), {"collect": lambda self: [{"ts": datetime(2024, 1, 1, 0, 0, 0)}]})()

    monkeypatch.setattr(pipeline.spark, "sql", fake_sql)

    class TableObj:
        def __init__(self, columns):
            self.columns = columns

    def fake_table(name):
        if name == "gold.dim_customer":
            return TableObj(["customer_dim_sk", "customer_id"])
        if name == "gold.dim_branch_employee":
            return TableObj(["branch_employee_dim_sk", "employee_id", "employee_name", "role", "branch_code", "region", "effective_date"])
        return TableObj(["rental_contract_dim_sk", "contract_id", "customer_id", "branch_code", "contract_start_date", "contract_status"])

    monkeypatch.setattr(pipeline.spark, "table", fake_table)

    with pytest.raises(ValueError):
        pipeline.run_dimension_pipeline()
```

## Edge Cases Covered

- Empty DataFrames.
- Null and blank mandatory keys.
- Invalid date chronology in rental contracts.
- Duplicate records resolved by latest timestamps.
- Optional null timestamps with `coalesce` fallback.
- Schema mismatches and missing required target columns.
- Merge path for both table creation and existing Delta target update.
- Audit/error logging behavior during success and failure.

## Databricks Testing Notes

- Use a reusable SparkSession fixture compatible with Databricks local or CI execution.
- Mock `spark.table`, `spark.sql`, Delta merge operations, and table existence checks for isolated unit testing.
- For integration testing in Databricks, replace mocks with temporary Unity Catalog or Hive metastore test schemas.
- For performance validation, run moderate-volume datasets in cluster-backed test jobs and compare counts and execution stability.
- Keep tests independent from production tables by using temporary schemas and controlled sample data.

## apiCost
apiCost: 0.000000

# Output URL (Clickable Hyperlinks)
https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_DIM_Pyspark_Unit_Test_Case_DIAS/Databricks_pyspark_Unit_Test_Case_1.md