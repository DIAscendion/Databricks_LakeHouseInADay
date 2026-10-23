# _____________________________________________
# Author: AAVA
# Created on:
# Description: Databricks-compatible Pytest script for the Bronze ingestion PySpark pipeline
#              (Rental Revenue to Cash). Extracted as-is from
#              DI_Databricks_Bronze_Pyspark_Unit_Test_Case/Databricks_pyspark_Unit_Test_Case_1.md
# Version: 1
# Updated on:
# _____________________________________________
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
