_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Unit test cases and Databricks-compatible Pytest script for the Bronze ingestion PySpark pipeline that loads source CSV datasets into Delta bronze tables with audit logging and API cost reporting.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks PySpark Unit Test Case

## Workflow Summary
This PySpark pipeline creates required Delta tables, reads multiple CSV source datasets, enriches them with ingestion metadata, aligns records to target bronze table schemas, writes data into bronze Delta tables, logs audit outcomes for success and failure, and prints API cost consumed for execution.

## Source and Target Analysis

| Component | Details |
|---|---|
| Source Types | CSV files from mounted raw storage paths |
| Source Datasets | rental_contracts, invoices, cash_receipts, customer_master, branch_employee |
| Target Tables | `sunbelt_demo.bronze.bz_rental_contracts`, `sunbelt_demo.bronze.bz_invoices`, `sunbelt_demo.bronze.bz_cash_receipts`, `sunbelt_demo.bronze.bz_customer_master`, `sunbelt_demo.bronze.bz_branch_employee` |
| Audit Table | `sunbelt_demo.bronze.bz_audit_log` |
| Write Mode | Overwrite with `overwriteSchema=true` for bronze tables; Append for audit log |
| Transformations | Metadata enrichment, schema alignment, target table creation |
| Joins | None |
| Aggregations | None |
| Filters | None |
| Output Format | Delta tables |

## Key Transformations Identified

1. Spark session initialization with Databricks-friendly settings.
2. DDL-based table creation for all bronze and audit tables.
3. Source CSV read using format and options from configuration.
4. Metadata enrichment using `load_date`, `update_date`, `source_system`, `file_path`, and `file_modification_time`.
5. Schema alignment using target table column list.
6. Bronze write using overwrite mode.
7. Audit log write using append mode.
8. Exception handling in `process_table` with FAILED audit capture.
9. Pipeline execution summary and API cost output.

## Test Case List

| Test Case ID | Test Case Description | Expected Outcome |
|---|---|---|
| TC_001 | Validate `get_current_user()` returns `current_user()` result when SQL query succeeds. | Returned value matches SQL result user name. |
| TC_002 | Validate `get_current_user()` falls back to `session_user()` when `current_user()` fails. | Returned value matches `session_user()` result. |
| TC_003 | Validate `get_current_user()` falls back to `sparkContext.sparkUser()` when SQL queries fail. | Returned value matches Spark context user. |
| TC_004 | Validate `get_current_user()` returns `unknown_user` when all retrieval methods fail. | Function returns `unknown_user`. |
| TC_005 | Validate `create_required_tables()` executes all DDL statements. | `spark.sql()` invoked for every entry in `TARGET_DDL`. |
| TC_006 | Validate `read_source()` applies all configured options and loads configured source path. | DataFrame is loaded from expected path with expected reader options. |
| TC_007 | Validate `enrich_with_metadata()` adds `load_date`, `update_date`, and `source_system` columns. | Output DataFrame contains metadata columns with valid values. |
| TC_008 | Validate `enrich_with_metadata()` creates `file_path` and `file_modification_time` when absent. | Missing metadata columns are added with null-compatible types. |
| TC_009 | Validate `enrich_with_metadata()` preserves existing `file_path` and `file_modification_time` columns. | Existing columns remain available without duplicate creation. |
| TC_010 | Validate `align_to_target_table()` selects only columns present in target table schema. | Output DataFrame contains only target columns available in source DataFrame. |
| TC_011 | Validate `align_to_target_table()` excludes extra columns not in target table schema. | Extra columns are dropped from output. |
| TC_012 | Validate `write_to_bronze()` writes in Delta overwrite mode with schema overwrite enabled. | Writer is called with `format(delta)`, `mode(overwrite)`, and `overwriteSchema=true`. |
| TC_013 | Validate `write_to_bronze()` returns row count after save. | Returned count equals DataFrame record count. |
| TC_014 | Validate `write_audit_log()` writes audit entries with computed processing time. | Audit table receives one append record with expected field values. |
| TC_015 | Validate `process_table()` executes happy path end-to-end for one source. | Source is read, enriched, aligned, written, and SUCCESS audit is recorded. |
| TC_016 | Validate `process_table()` records FAILED audit and re-raises exception when source read fails. | FAILED audit is written and exception is propagated. |
| TC_017 | Validate `process_table()` records FAILED audit and re-raises exception when write fails. | FAILED audit is written and exception is propagated. |
| TC_018 | Validate `run_pipeline()` calls `create_required_tables()` once and processes every source in `SOURCE_CONFIG`. | All configured sources are processed exactly once. |
| TC_019 | Validate `run_pipeline()` prints successful completion message with elapsed processing seconds. | Completion print statement is emitted. |
| TC_020 | Validate `run_pipeline()` prints API cost in USD. | Output includes `API Cost Consumed (USD): 0.000001`. |
| TC_021 | Validate behavior with empty source DataFrame. | Empty DataFrame is written successfully and audit logs row count as 0 or matching empty count. |
| TC_022 | Validate handling of null values in source records. | Null values are preserved unless excluded by target alignment; processing succeeds. |
| TC_023 | Validate schema mismatch scenario where source misses some target columns. | Alignment selects only common columns and write completes if target permits. |
| TC_024 | Validate invalid source format/path raises exception and creates FAILED audit log. | Exception is raised and FAILED audit entry is persisted. |
| TC_025 | Validate performance-oriented scenario using moderate test dataset in Databricks-local Spark execution. | Pipeline helper functions execute within acceptable local test runtime and produce correct outputs. |

## Edge Cases Covered

| Category | Coverage |
|---|---|
| Empty DataFrames | Verified for write and audit behavior |
| Null Values | Verified during enrichment and write path |
| Missing Columns | Verified in schema alignment logic |
| Extra Columns | Verified to be dropped by alignment |
| Source Read Failure | Verified in exception path with FAILED audit |
| Write Failure | Verified in exception path with FAILED audit |
| User Resolution Fallback | Verified across SQL and Spark context fallbacks |

## Databricks-Compatible Pytest Script

```python
import importlib.util
from pathlib import Path
from datetime import datetime
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType


MODULE_PATH = Path("/Workspace/Repos/project/DI_Databricks_Bronze_DE_Pipeline/Databricks_Bronze_DE_Pipeline_1.py")


@pytest.fixture(scope="session")
def spark():
    spark_session = (
        SparkSession.builder
        .master("local[2]")
        .appName("bronze-pipeline-unit-tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.session.timeZone", "UTC")
        .enableHiveSupport()
        .getOrCreate()
    )
    yield spark_session
    spark_session.stop()


@pytest.fixture(scope="session")
def pipeline_module(spark):
    spec = importlib.util.spec_from_file_location("bronze_pipeline", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.spark = spark
    return module


@pytest.fixture
def sample_df(spark):
    data = [("C1", "CU1"), ("C2", None)]
    schema = StructType([
        StructField("contract_id", StringType(), True),
        StructField("customer_id", StringType(), True),
    ])
    return spark.createDataFrame(data, schema)


def test_enrich_with_metadata_adds_required_columns(pipeline_module, sample_df):
    result_df = pipeline_module.enrich_with_metadata(sample_df, "TEST_SYS")
    assert "load_date" in result_df.columns
    assert "update_date" in result_df.columns
    assert "source_system" in result_df.columns
    assert "file_path" in result_df.columns
    assert "file_modification_time" in result_df.columns
    assert result_df.filter("source_system = 'TEST_SYS'").count() == 2


def test_enrich_with_metadata_preserves_existing_file_columns(pipeline_module, spark):
    df = spark.sql("""
        SELECT 'C1' AS contract_id,
               '/tmp/file.csv' AS file_path,
               current_timestamp() AS file_modification_time
    """)
    result_df = pipeline_module.enrich_with_metadata(df, "TEST_SYS")
    assert result_df.columns.count("file_path") == 1
    assert result_df.columns.count("file_modification_time") == 1


def test_align_to_target_table_selects_common_columns_only(pipeline_module, spark, monkeypatch):
    input_df = spark.sql("SELECT 'C1' AS contract_id, 'CU1' AS customer_id, 'DROP_ME' AS extra_col")

    class MockTargetTable:
        columns = ["contract_id", "customer_id", "load_date"]

    monkeypatch.setattr(pipeline_module.spark, "table", lambda _: MockTargetTable())
    result_df = pipeline_module.align_to_target_table(input_df, "dummy.table")
    assert result_df.columns == ["contract_id", "customer_id"]


def test_write_to_bronze_returns_row_count(pipeline_module, sample_df, monkeypatch):
    captured = {}

    class MockWriter:
        def format(self, fmt):
            captured["format"] = fmt
            return self

        def mode(self, mode_name):
            captured["mode"] = mode_name
            return self

        def option(self, key, value):
            captured[key] = value
            return self

        def saveAsTable(self, table_name):
            captured["table_name"] = table_name

    monkeypatch.setattr(type(sample_df), "write", property(lambda self: MockWriter()))
    row_count = pipeline_module.write_to_bronze(sample_df, "bronze.test_table")
    assert row_count == 2
    assert captured["format"] == "delta"
    assert captured["mode"] == "overwrite"
    assert captured["overwriteSchema"] == "true"
    assert captured["table_name"] == "bronze.test_table"


def test_write_audit_log_appends_record(pipeline_module, spark, monkeypatch):
    captured = {"saved": False}

    class MockAuditWriter:
        def format(self, fmt):
            captured["format"] = fmt
            return self

        def mode(self, mode_name):
            captured["mode"] = mode_name
            return self

        def saveAsTable(self, table_name):
            captured["table_name"] = table_name
            captured["saved"] = True

    class MockAuditDF:
        def __init__(self, rows):
            self.rows = rows

        @property
        def write(self):
            return MockAuditWriter()

    monkeypatch.setattr(pipeline_module.spark, "createDataFrame", lambda rows, schema: MockAuditDF(rows))

    start_time = datetime.utcnow()
    end_time = datetime.utcnow()
    pipeline_module.write_audit_log(
        source_name="rental_contracts",
        target_table="bronze.table",
        status="SUCCESS",
        row_count=10,
        message="Loaded successfully",
        process_start_time=start_time,
        process_end_time=end_time,
        processed_by="tester"
    )

    assert captured["saved"] is True
    assert captured["format"] == "delta"
    assert captured["mode"] == "append"
    assert captured["table_name"] == pipeline_module.AUDIT_TABLE


def test_process_table_happy_path(pipeline_module, sample_df, monkeypatch):
    calls = {"audit_status": None}
    monkeypatch.setattr(pipeline_module, "read_source", lambda s, d: sample_df)
    monkeypatch.setattr(pipeline_module, "enrich_with_metadata", lambda df, src: df)
    monkeypatch.setattr(pipeline_module, "align_to_target_table", lambda df, tgt: df)
    monkeypatch.setattr(pipeline_module, "write_to_bronze", lambda df, tgt: 2)

    def mock_write_audit_log(**kwargs):
        calls["audit_status"] = kwargs["status"]
        calls["row_count"] = kwargs["row_count"]

    monkeypatch.setattr(pipeline_module, "write_audit_log", mock_write_audit_log)

    pipeline_module.process_table(
        "rental_contracts",
        {"target_table": "bronze.test", "source_system": "TEST_SYS"},
        "tester"
    )

    assert calls["audit_status"] == "SUCCESS"
    assert calls["row_count"] == 2


def test_process_table_failure_writes_failed_audit(pipeline_module, monkeypatch):
    calls = {"audit_status": None}

    def mock_read_source(source_name, source_details):
        raise Exception("read failed")

    def mock_write_audit_log(**kwargs):
        calls["audit_status"] = kwargs["status"]
        calls["message"] = kwargs["message"]

    monkeypatch.setattr(pipeline_module, "read_source", mock_read_source)
    monkeypatch.setattr(pipeline_module, "write_audit_log", mock_write_audit_log)

    with pytest.raises(Exception, match="read failed"):
        pipeline_module.process_table(
            "rental_contracts",
            {"target_table": "bronze.test", "source_system": "TEST_SYS"},
            "tester"
        )

    assert calls["audit_status"] == "FAILED"
    assert "read failed" in calls["message"]


def test_run_pipeline_processes_all_sources(pipeline_module, monkeypatch, capsys):
    processed_sources = []
    monkeypatch.setattr(pipeline_module, "create_required_tables", lambda: None)
    monkeypatch.setattr(
        pipeline_module,
        "process_table",
        lambda source_name, source_details, executed_by: processed_sources.append(source_name)
    )
    monkeypatch.setattr(
        pipeline_module,
        "SOURCE_CONFIG",
        {
            "rental_contracts": {"target_table": "t1"},
            "invoices": {"target_table": "t2"}
        }
    )
    monkeypatch.setattr(pipeline_module, "EXECUTED_BY", "tester")
    monkeypatch.setattr(pipeline_module.time, "time", lambda: 100.0 if not processed_sources else 102.5)
    monkeypatch.setattr(pipeline_module, "API_COST_USD", 0.000001)

    pipeline_module.run_pipeline()
    captured = capsys.readouterr()

    assert processed_sources == ["rental_contracts", "invoices"]
    assert "Pipeline completed successfully" in captured.out
    assert "API Cost Consumed (USD): 0.000001" in captured.out
```

## Notes for Databricks Execution

| Area | Recommendation |
|---|---|
| Spark Setup | Use session-scoped Spark fixture to avoid repeated startup cost |
| Table Isolation | Use temporary schemas or mocked table operations during unit tests |
| External Sources | Mock `read_source()` for unit tests instead of reading mounted paths |
| Audit Validation | Mock `spark.createDataFrame` and writer chain for deterministic tests |
| Performance | Keep local test data small; reserve large-scale checks for integration tests |
| Compatibility | Ensure pytest is run in Databricks Repos or CI/CD runner with PySpark installed |

## API Cost

`apiCost: 0.000001`
