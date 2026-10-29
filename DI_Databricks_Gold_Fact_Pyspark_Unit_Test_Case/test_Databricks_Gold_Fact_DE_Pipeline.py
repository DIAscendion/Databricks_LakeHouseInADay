"""
Author: AAVA
Created on:
Description: Pytest unit tests for Databricks_Gold_Fact_DE_Pipeline_1.py (Databricks / local PySpark compatible).
Version: 1
Updated on:
"""
import importlib.util
import os
import sys
import types
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql import SparkSession

PIPELINE_PATH = os.environ.get(
    "PIPELINE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "DI_Databricks_Gold_Fact_DE_Pipeline",
                 "Databricks_Gold_Fact_DE_Pipeline_1.py"),
)


@pytest.fixture(scope="session")
def spark():
    s = SparkSession.builder.master("local[1]").appName("ut_gold_fact") \
        .config("spark.sql.shuffle.partitions", "1").getOrCreate()
    yield s


@pytest.fixture(scope="session")
def pl(spark):
    if "delta.tables" not in sys.modules:
        try:
            import delta.tables  # noqa: F401
        except ImportError:
            m = types.ModuleType("delta"); t = types.ModuleType("delta.tables")
            t.DeltaTable = MagicMock(); m.tables = t
            sys.modules["delta"] = m; sys.modules["delta.tables"] = t
    spec = importlib.util.spec_from_file_location("gold_pipeline", PIPELINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def emp(spark):
    return spark.createDataFrame(
        [("E1", "Alice", "SALES", "East", None, "B1"),
         ("E2", "Bob", "COLLECTOR", "East", "COL1", "B1")],
        "employee_id string, employee_name string, role string, region string, collector_id string, branch_code string")


def contracts(spark):
    return spark.createDataFrame(
        [("C1", "CU1", "B1", "E1", "EXC", "OPEN", date(2024, 1, 1), date(2024, 1, 11), Decimal("100.00"))],
        "contract_id string, customer_id string, branch_code string, sales_rep_id string, equipment_class string,"
        " contract_status string, contract_start_date date, contract_end_date date, daily_rate decimal(18,2)")


def customers(spark, rows=None):
    rows = rows if rows is not None else [("CU1", "Cust One", "ACTIVE", Decimal("500.00"))]
    return spark.createDataFrame(rows, "customer_id string, customer_name string, customer_status string, credit_limit decimal(18,2)")


INV_SCHEMA = ("invoice_id string, contract_id string, customer_id string, invoice_date date, due_date date,"
              " invoice_amount decimal(18,2), invoice_type string")


def invoices(spark, rows):
    return spark.createDataFrame(rows, INV_SCHEMA)


def receipts(spark, rows):
    return spark.createDataFrame(
        rows, "receipt_id string, receipt_date date, payment_amount decimal(18,2), invoice_id string, customer_id string,"
              " match_status string, payment_method string, unapplied_payment_amount decimal(18,2)")


def src(spark, inv, rec=None, cust=None):
    rec = rec if rec is not None else receipts(spark, [])
    return {
        "contracts": contracts(spark).alias("c"), "invoices": inv.alias("i"), "receipts": rec.alias("r"),
        "customers": (cust if cust is not None else customers(spark)).alias("cm"), "employees": emp(spark).alias("be"),
    }


# ---------- reference views ----------
def test_TC01_reference_views_split_sales_and_collectors(spark, pl):
    ref = pl.prepare_reference_views(src(spark, invoices(spark, [])))
    assert [r.employee_id for r in ref["sales_rep"].collect()] == ["E1"]
    assert [r.collector_id for r in ref["collector"].collect()] == ["COL1"]


# ---------- rental revenue ----------
def test_TC02_rental_revenue_happy_path(spark, pl):
    d = date(2024, 2, 1)
    inv = invoices(spark, [("I1", "C1", "CU1", d, d, Decimal("1000.00"), "RENTAL"),
                           ("I2", "C1", "CU1", d, d, Decimal("200.00"), "CREDIT_MEMO")])
    s = src(spark, inv); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, read, rej = pl.build_rental_revenue_fact(s, ref)
    r = df.collect()[0]
    assert (r.gross_billings, r.credit_memo_amount, r.net_billings) == (Decimal("1000.00"), Decimal("-200.00"), Decimal("800.00"))
    assert r.rental_revenue == Decimal("1000.00") and r.invoice_count == 2
    assert r.average_daily_rate == Decimal("100.00")  # 1000 / 10 days
    assert r.credit_memo_rate == Decimal("0.200000")
    assert r.sales_rep_name == "Alice" and r.source_system == pl.SOURCE_SYSTEM
    assert read == 2 and rej == 0


def test_TC03_rental_revenue_rejects_missing_mandatory_fields(spark, pl):
    d = date(2024, 2, 1)
    inv = invoices(spark, [(None, "C1", "CU1", d, d, Decimal("1.00"), "RENTAL"),
                           ("I2", "C1", "CU1", None, d, Decimal("1.00"), "RENTAL"),
                           ("I3", "C1", "CU1", d, d, None, "RENTAL"),
                           ("I4", "C1", "CU1", d, d, Decimal("5.00"), "RENTAL")])
    s = src(spark, inv); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=3) as w:
        df, read, rej = pl.build_rental_revenue_fact(s, ref)
    assert w.call_args[0][2] == "REQUIRED_FIELDS_CHECK"
    assert w.call_args[0][0].count() == 3
    assert rej == 3 and read == 1 and df.count() == 1


def test_TC04_rental_revenue_zero_duration_and_no_gross_gives_null_ratios(spark, pl):
    d = date(2024, 2, 1)
    inv = invoices(spark, [("I1", "C1", "CU1", d, d, Decimal("100.00"), "CREDIT_MEMO")])
    s = src(spark, inv)
    s["contracts"] = spark.createDataFrame(
        [("C1", "CU1", "B1", "E1", "EXC", "OPEN", date(2024, 1, 1), date(2024, 1, 1), Decimal("1.00"))],
        contracts(spark).schema).alias("c")
    ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, _, _ = pl.build_rental_revenue_fact(s, ref)
    r = df.collect()[0]
    assert r.average_daily_rate is None and r.credit_memo_rate is None
    assert r.net_billings == Decimal("-100.00")


def test_TC05_rental_revenue_trend_value_lag_by_branch(spark, pl):
    d1, d2 = date(2024, 2, 1), date(2024, 2, 2)
    inv = invoices(spark, [("I1", "C1", "CU1", d1, d1, Decimal("100.00"), "RENTAL"),
                           ("I2", "C1", "CU1", d2, d2, Decimal("250.00"), "RENTAL")])
    s = src(spark, inv); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, _, _ = pl.build_rental_revenue_fact(s, ref)
    rows = {r.reporting_date: r.trend_value for r in df.collect()}
    assert rows[d1] is None and rows[d2] == Decimal("150.00")


def test_TC06_rental_revenue_no_matching_contract_dropped(spark, pl):
    d = date(2024, 2, 1)
    inv = invoices(spark, [("I1", "NOPE", "CU1", d, d, Decimal("100.00"), "RENTAL")])
    s = src(spark, inv); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, read, _ = pl.build_rental_revenue_fact(s, ref)
    assert df.count() == 0 and read == 0


# ---------- AR aging ----------
@pytest.mark.parametrize("days,bucket", [(0, "0-30"), (30, "0-30"), (31, "31-60"), (60, "31-60"),
                                         (61, "61-90"), (90, "61-90"), (91, "90+"), (-5, "90+")])
def test_TC07_ar_aging_buckets(spark, pl, days, bucket):
    due = date.today() - timedelta(days=days)
    inv = invoices(spark, [("I1", "C1", "CU1", due, due, Decimal("100.00"), "RENTAL")])
    s = src(spark, inv); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, read, _ = pl.build_ar_aging_fact(s, ref)
    r = df.collect()[0]
    assert r.aging_bucket == bucket and r.total_ar_outstanding == Decimal("100.00")
    assert r.collector_id == "COL1"
    assert r.ar_90_plus_amount == (Decimal("100.00") if bucket == "90+" else Decimal("0.00"))
    assert r.dso is None and r.dso_trend is None


def test_TC08_ar_aging_rejects_null_due_date_or_customer(spark, pl):
    d = date.today()
    inv = invoices(spark, [("I1", "C1", None, d, d, Decimal("1.00"), "RENTAL"),
                           ("I2", "C1", "CU1", d, None, Decimal("1.00"), "RENTAL"),
                           ("I3", "C1", "CU1", d, d, Decimal("1.00"), "RENTAL")])
    s = src(spark, inv); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=2) as w:
        df, read, rej = pl.build_ar_aging_fact(s, ref)
    assert w.call_args[0][2] == "AR_AGING_VALIDATION" and w.call_args[0][0].count() == 2
    assert rej == 2 and read == 1


# ---------- cash application ----------
def test_TC09_cash_application_happy_path(spark, pl):
    inv_d, due, rec_d = date(2024, 2, 1), date(2024, 2, 20), date(2024, 2, 11)
    inv = invoices(spark, [("I1", "C1", "CU1", inv_d, due, Decimal("100.00"), "RENTAL")])
    rec = receipts(spark, [("R1", rec_d, Decimal("100.00"), "I1", "CU1", "applied", "ACH", None)])
    s = src(spark, inv, rec); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, read, rej = pl.build_cash_application_fact(s, ref)
    r = df.collect()[0]
    assert r.match_status == "APPLIED" and r.cash_collected == Decimal("100.00")
    assert r.average_days_to_pay == Decimal("10.00")
    assert r.invoices_paid_on_time_percentage == Decimal("1.000000")
    assert r.unapplied_cash_amount == Decimal("0.00") and r.unapplied_cash_percentage == Decimal("0.000000")
    assert r.payment_date == rec_d and r.collector_name == "Bob"


def test_TC10_cash_application_unapplied_and_null_status(spark, pl):
    d = date(2024, 2, 11)
    inv = invoices(spark, [("I1", "C1", "CU1", date(2024, 2, 1), date(2024, 2, 20), Decimal("100.00"), "RENTAL")])
    rec = receipts(spark, [("R1", d, Decimal("100.00"), "I1", "CU1", None, "CHK", Decimal("40.00"))])
    s = src(spark, inv, rec); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, _, _ = pl.build_cash_application_fact(s, ref)
    r = df.collect()[0]
    assert r.match_status == "UNAPPLIED"
    assert r.average_days_to_pay is None and r.invoices_paid_on_time_percentage is None
    assert r.unapplied_cash_amount == Decimal("40.00") and r.unapplied_cash_percentage == Decimal("0.400000")


def test_TC11_cash_application_zero_payment_null_percentage_and_rejects(spark, pl):
    d = date(2024, 2, 11)
    inv = invoices(spark, [("I1", "C1", "CU1", d, d, Decimal("0.00"), "RENTAL")])
    rec = receipts(spark, [("R1", d, Decimal("0.00"), "I1", "CU1", "APPLIED", "ACH", None),
                           (None, d, Decimal("5.00"), "I1", "CU1", "APPLIED", "ACH", None)])
    s = src(spark, inv, rec); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=1) as w:
        df, read, rej = pl.build_cash_application_fact(s, ref)
    assert w.call_args[0][2] == "CASH_APP_VALIDATION" and rej == 1
    assert df.collect()[0].unapplied_cash_percentage is None


# ---------- credit risk ----------
def test_TC12_credit_risk_over_limit_and_suspended(spark, pl):
    due = date.today() - timedelta(days=120)
    inv = invoices(spark, [("I1", "C1", "CU1", due, due, Decimal("600.00"), "RENTAL")])
    cust = customers(spark, [("CU1", "Cust One", "suspended", Decimal("500.00"))])
    s = src(spark, inv, cust=cust); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, read, rej = pl.build_credit_risk_fact(s, ref)
    r = df.collect()[0]
    assert r.outstanding_ar == Decimal("600.00") and r.ar_90_plus_amount_by_customer == Decimal("600.00")
    assert r.customers_over_limit_count == 1 and r.customers_over_limit_amount == Decimal("100.00")
    assert r.credit_utilization_percentage == Decimal("1.200000")
    assert r.suspended_customers_with_open_exposure == 1
    assert r.open_contract_count == 1 and r.open_contract_value == Decimal("1000.00")


def test_TC13_credit_risk_zero_limit_and_no_activity(spark, pl):
    inv = invoices(spark, [])
    cust = customers(spark, [("CU9", "Idle", "ACTIVE", Decimal("0.00"))])
    s = src(spark, inv, cust=cust); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=0):
        df, _, _ = pl.build_credit_risk_fact(s, ref)
    r = df.collect()[0]
    assert r.credit_utilization_percentage is None
    assert r.outstanding_ar == Decimal("0.00") and r.customers_over_limit_count == 0
    assert r.suspended_customers_with_open_exposure == 0


def test_TC14_credit_risk_rejects_null_credit_limit(spark, pl):
    cust = customers(spark, [("CU1", "A", "ACTIVE", None)])
    s = src(spark, invoices(spark, []), cust=cust); ref = pl.prepare_reference_views(s)
    with patch.object(pl, "write_error_records", return_value=1) as w:
        _, _, rej = pl.build_credit_risk_fact(s, ref)
    assert w.call_args[0][2] == "CREDIT_RISK_VALIDATION" and rej == 1


# ---------- write_error_records ----------
def test_TC15_write_error_records_empty_returns_zero(spark, pl):
    df = invoices(spark, []).withColumn("receipt_id", invoices(spark, []).invoice_id)
    assert pl.write_error_records(df, "silver.si_invoices", "R", "d") == 0


def test_TC16_write_error_records_builds_and_writes_to_both_layers(spark, pl):
    d = date(2024, 1, 1)
    df = spark.createDataFrame([(None, "C1", "CU1", d)], "invoice_id string, contract_id string, customer_id string, d date") \
        .withColumn("receipt_id", __import__("pyspark.sql.functions", fromlist=["lit"]).lit(None).cast("string"))
    captured = []
    with patch("pyspark.sql.DataFrameWriter.saveAsTable", lambda self, name, *a, **k: captured.append(name)):
        n = pl.write_error_records(df, "silver.si_invoices", "RULE", "desc")
    assert n == 1
    assert captured == [pl.SILVER_TABLES["errors"], pl.GOLD_TABLES["errors"]]


# ---------- audit ----------
def test_TC17_log_audit_record_writes_both_tables(spark, pl):
    captured = []
    with patch("pyspark.sql.DataFrameWriter.saveAsTable", lambda self, name, *a, **k: captured.append(name)):
        pl.log_audit_record("gold.t", "SUCCESS", 5, 4, 1)
    assert captured == [pl.SILVER_TABLES["audit"], pl.GOLD_TABLES["audit"]]


def test_TC18_log_audit_record_payload(pl):
    frames = []
    fake_spark = MagicMock()
    fake_spark.createDataFrame.side_effect = lambda data, cols: frames.append((data, cols)) or MagicMock()
    with patch.object(pl, "spark", fake_spark):
        pl.log_audit_record("gold.t", "FAILED", 0, 0, 0, "boom")
    data, cols = frames[0]
    row = dict(zip(cols, data[0]))
    assert row["processing_status"] == "FAILED" and row["error_message"] == "boom"
    assert row["target_table"] == "gold.t" and row["run_id"] == pl.RUN_ID
    assert row["pipeline_name"] == pl.PIPELINE_NAME and row["executed_by"] == "AAVA"
    assert isinstance(row["processing_duration_seconds"], float)


# ---------- DDL / write / orchestration ----------
def test_TC19_create_tables_issue_delta_ddl(pl):
    fake = MagicMock()
    with patch.object(pl, "spark", fake):
        pl.create_gold_support_tables(); pl.create_gold_fact_tables()
    sqls = [c.args[0] for c in fake.sql.call_args_list]
    assert len(sqls) == 6
    assert all("CREATE TABLE IF NOT EXISTS" in q and "USING DELTA" in q for q in sqls)
    assert not any("PRIMARY KEY" in q.upper() or "FOREIGN KEY" in q.upper() for q in sqls)


def test_TC20_write_delta_optimized(pl):
    df = MagicMock(); df.count.return_value = 7
    fake = MagicMock()
    with patch.object(pl, "spark", fake):
        n = pl.write_delta_optimized(df, "gold.t", ["a", "b"])
    assert n == 7
    df.write.format.assert_called_with("delta")
    assert "OPTIMIZE gold.t ZORDER BY (a, b)" in fake.sql.call_args[0][0]


def test_TC21_run_pipeline_success_audits_each_fact(pl):
    builder = MagicMock(return_value=(MagicMock(), 10, 1))
    with patch.object(pl, "create_gold_support_tables"), patch.object(pl, "create_gold_fact_tables"), \
         patch.object(pl, "read_silver_sources", return_value={}), patch.object(pl, "prepare_reference_views", return_value={}), \
         patch.object(pl, "build_rental_revenue_fact", builder), patch.object(pl, "build_ar_aging_fact", builder), \
         patch.object(pl, "build_cash_application_fact", builder), patch.object(pl, "build_credit_risk_fact", builder), \
         patch.object(pl, "write_delta_optimized", return_value=9), patch.object(pl, "log_audit_record") as audit:
        pl.run_pipeline()
    assert audit.call_count == 4
    assert all(c.args[1] == "SUCCESS" and c.args[3] == 9 for c in audit.call_args_list)


def test_TC22_run_pipeline_failure_logs_failed_and_reraises(pl):
    with patch.object(pl, "create_gold_support_tables"), patch.object(pl, "create_gold_fact_tables"), \
         patch.object(pl, "read_silver_sources", return_value={}), patch.object(pl, "prepare_reference_views", return_value={}), \
         patch.object(pl, "build_rental_revenue_fact", side_effect=ValueError("bad data")), \
         patch.object(pl, "log_audit_record") as audit:
        with pytest.raises(ValueError, match="bad data"):
            pl.run_pipeline()
    args = audit.call_args.args
    assert args[1] == "FAILED" and args[2:5] == (0, 0, 0) and "bad data" in args[5]


def test_TC23_run_pipeline_setup_failure_propagates(pl):
    with patch.object(pl, "create_gold_support_tables", side_effect=RuntimeError("ddl")):
        with pytest.raises(RuntimeError):
            pl.run_pipeline()


def test_TC24_verify_compat_prints(pl, capsys):
    pl.verify_gold_layer_compatibility()
    assert capsys.readouterr().out.count("Gold compatibility check passed") == 6
