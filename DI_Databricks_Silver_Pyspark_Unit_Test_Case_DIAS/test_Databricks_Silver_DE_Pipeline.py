"""
Author: AAVA
Created on:
Description: Databricks PySpark Pytest unit tests for DI_Databricks_Silver_DE_Pipeline/Databricks_Silver_DE_Pipeline_1.py
             (extracted as-is from Databricks_pyspark_Unit_Test_Case_1.md; test case list TC_001-TC_035 in that file).
Version: 1
Updated on:
"""

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

# apiCost: 0.000000
