"""
_____________________________________________
Author: AAVA
Created on:
Description: Pytest unit tests for Databricks_Gold_Aggregated_DE_Pipeline_1.py
             (Rental Revenue-to-Cash Gold aggregates: billing performance and executive health score).
Version: 1
Updated on:
_____________________________________________

Test Case List
| ID    | Description                                                    | Expected Outcome                                         |
|-------|----------------------------------------------------------------|----------------------------------------------------------|
| TC01  | safe_divide with valid denominator                             | Returns quotient                                         |
| TC02  | safe_divide with zero / null denominator                       | Returns null                                             |
| TC03  | build_billing_performance happy path                           | Correct gross/credit/net/rental/ADR/ratios/invoice count |
| TC04  | build_billing_performance null contract_id / invoice_date      | Invalid rows logged, excluded from aggregate             |
| TC05  | build_billing_performance with no matching contract (left join)| Row kept with null dimensions                            |
| TC06  | build_executive_health happy path                              | Correct KPIs and health score (82.0)                     |
| TC07  | build_executive_health missing grain (no contract/employee)    | Rows filtered out and error records written              |
| TC08  | health score bounded to 0..100                                 | Score within bounds                                      |
| TC09  | write_error_records with None df                               | No-op                                                    |
| TC10  | write_audit_log failure                                        | Exception swallowed                                      |
| TC11  | optimize_table failure                                         | Exception swallowed                                      |
| TC12  | extract_silver_sources normalization                           | Types cast, strings trimmed/lowercased, type uppercased  |
| TC13  | main success path                                              | Loads both tables, audit status SUCCESS                  |
| TC14  | main failure path                                              | Audit status FAILED and exception re-raised              |
| TC15  | Empty inputs                                                   | Empty aggregate outputs, no error                        |
"""
import importlib.util
import os
import sys
import types
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql import SparkSession

PIPELINE_REL = os.path.join(
    "DI_Databricks_Gold_Aggregated_DE_Pipeline", "Databricks_Gold_Aggregated_DE_Pipeline_1.py"
)


def _find_pipeline():
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (here, os.path.dirname(here), os.getcwd()):
        p = os.path.join(base, PIPELINE_REL)
        if os.path.exists(p):
            return p
    # Databricks repo fallback: same folder
    p = os.path.join(here, "Databricks_Gold_Aggregated_DE_Pipeline_1.py")
    if os.path.exists(p):
        return p
    raise FileNotFoundError("Pipeline script not found")


@pytest.fixture(scope="session")
def spark():
    s = (SparkSession.builder.master("local[1]").appName("gold_agg_tests")
         .config("spark.sql.shuffle.partitions", "1").getOrCreate())
    yield s


@pytest.fixture(scope="session")
def mod(spark):
    # Stub delta if not installed (only imported, never used by the tested logic)
    if "delta" not in sys.modules:
        try:
            import delta.tables  # noqa: F401
        except ImportError:
            d = types.ModuleType("delta")
            dt = types.ModuleType("delta.tables")
            dt.DeltaTable = MagicMock()
            d.tables = dt
            sys.modules["delta"] = d
            sys.modules["delta.tables"] = dt
    spec = importlib.util.spec_from_file_location("gold_pipeline", _find_pipeline())
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------- data helpers ----------------
INV_SCHEMA = ("invoice_id string, contract_id string, customer_id string, invoice_date date, "
              "due_date date, invoice_type string, invoice_amount decimal(18,2)")
CON_SCHEMA = "contract_id string, sales_rep_id string, branch_code string, equipment_class string, daily_rate decimal(18,2)"
EMP_SCHEMA = "employee_id string, employee_name string, region string"
CR_SCHEMA = "invoice_id string, receipt_date date, payment_amount decimal(18,2), unapplied_payment_amount decimal(18,2)"
CUS_SCHEMA = "customer_id string, credit_limit decimal(18,2)"

D = date(2024, 1, 1)


def invoices(spark, rows):
    return spark.createDataFrame(rows, INV_SCHEMA)


def contracts(spark, rows=None):
    rows = rows if rows is not None else [("C1", "e1", "b1", "excavator", Decimal("10.00"))]
    return spark.createDataFrame(rows, CON_SCHEMA)


def employees(spark, rows=None):
    rows = rows if rows is not None else [("e1", "Alice", "east")]
    return spark.createDataFrame(rows, EMP_SCHEMA)


# ---------------- TC01/TC02 ----------------
def test_tc01_safe_divide_valid(spark, mod):
    df = spark.createDataFrame([(10.0, 4.0)], "n double, d double")
    assert df.select(mod.safe_divide(df.n, df.d).alias("r")).first()["r"] == pytest.approx(2.5)


@pytest.mark.parametrize("d", [0.0, None])
def test_tc02_safe_divide_zero_or_null(spark, mod, d):
    df = spark.createDataFrame([(10.0, d)], "n double, d double")
    assert df.select(mod.safe_divide(df.n, df.d).alias("r")).first()["r"] is None


# ---------------- TC03-TC05 ----------------
def test_tc03_billing_happy_path(spark, mod):
    inv = invoices(spark, [
        ("I1", "C1", "cu1", D, D, "INVOICE", Decimal("100.00")),
        ("I2", "C1", "cu1", D, D, "CREDIT_MEMO", Decimal("-20.00")),
    ])
    with patch.object(mod, "write_error_records") as wer:
        out = mod.build_billing_performance(inv, contracts(spark), employees(spark))
    rows = out.collect()
    assert len(rows) == 1
    r = rows[0]
    assert r["reporting_date"] == D
    assert (r["region_name"], r["branch_name"], r["sales_rep_name"], r["equipment_class_name"]) == \
        ("east", "b1", "Alice", "excavator")
    assert float(r["gross_billings"]) == pytest.approx(80.0)
    assert float(r["credit_memo_amount"]) == pytest.approx(-20.0)
    assert float(r["net_billings"]) == pytest.approx(60.0)
    assert float(r["rental_revenue"]) == pytest.approx(100.0)
    assert float(r["average_daily_rate"]) == pytest.approx(10.0)
    assert float(r["revenue_per_contract"]) == pytest.approx(100.0)
    assert float(r["credit_memo_rate"]) == pytest.approx(0.25)
    assert r["invoice_count"] == 2
    assert r["source_system"] == mod.SOURCE_SYSTEM and r["run_id"] == mod.RUN_ID
    assert r["load_date"] is not None and r["update_date"] is not None
    assert "distinct_contract_count" not in out.columns
    wer.assert_called_once()
    assert wer.call_args[0][0].count() == 0


def test_tc04_billing_invalid_rows_logged_and_excluded(spark, mod):
    inv = invoices(spark, [
        ("I1", "C1", "cu1", D, D, "INVOICE", Decimal("100.00")),
        ("I2", None, "cu1", D, D, "INVOICE", Decimal("50.00")),
        ("I3", "C1", "cu1", None, D, "INVOICE", Decimal("70.00")),
    ])
    with patch.object(mod, "write_error_records") as wer:
        out = mod.build_billing_performance(inv, contracts(spark), employees(spark))
    assert out.count() == 1
    assert float(out.first()["gross_billings"]) == pytest.approx(100.0)
    bad_df, src, rule, _ = wer.call_args[0]
    assert bad_df.count() == 2
    assert src == mod.SILVER_INVOICES
    assert rule == "billing_mandatory_field_validation"


def test_tc05_billing_unmatched_contract_keeps_row(spark, mod):
    inv = invoices(spark, [("I1", "CX", "cu1", D, D, "INVOICE", Decimal("100.00"))])
    with patch.object(mod, "write_error_records"):
        out = mod.build_billing_performance(inv, contracts(spark), employees(spark))
    r = out.first()
    assert r["branch_name"] is None and r["region_name"] is None
    assert float(r["rental_revenue"]) == pytest.approx(100.0)
    assert float(r["average_daily_rate"]) == pytest.approx(0.0)


# ---------------- TC06-TC08 ----------------
def _exec(spark, mod, inv, con=None, emp=None, cr=None, cus=None):
    cr = cr if cr is not None else spark.createDataFrame([], CR_SCHEMA)
    cus = cus if cus is not None else spark.createDataFrame([], CUS_SCHEMA)
    return mod.build_executive_health(inv, con or contracts(spark), cr, cus, emp or employees(spark))


def test_tc06_executive_happy_path(spark, mod):
    today = date.today()
    inv = invoices(spark, [("I1", "C1", "cu1", D, today, "INVOICE", Decimal("100.00"))])
    cr = spark.createDataFrame([("I1", D, Decimal("50.00"), Decimal("10.00"))], CR_SCHEMA)
    cus = spark.createDataFrame([("cu1", Decimal("400.00"))], CUS_SCHEMA)
    with patch.object(mod, "write_error_records") as wer:
        out = _exec(spark, mod, inv, cr=cr, cus=cus)
    rows = out.collect()
    assert len(rows) == 1
    r = rows[0]
    assert r["network_level"] == "branch"
    assert r["collector_name"] == "Alice"
    assert float(r["rental_revenue"]) == pytest.approx(100.0)
    assert float(r["dso"]) == pytest.approx(100.0)
    assert float(r["ar_90_plus_percentage"]) == pytest.approx(0.0)
    assert float(r["collection_effectiveness_index"]) == pytest.approx(0.5)
    assert float(r["unapplied_cash_percentage"]) == pytest.approx(0.2)
    assert float(r["credit_utilization_percentage"]) == pytest.approx(0.25)
    assert float(r["overall_revenue_to_cash_health_score"]) == pytest.approx(82.0)
    assert wer.call_args[0][0].count() == 0


def test_tc07_executive_missing_grain_filtered_and_logged(spark, mod):
    inv = invoices(spark, [("I1", "CX", "cu1", D, D, "INVOICE", Decimal("100.00"))])
    with patch.object(mod, "write_error_records") as wer:
        out = _exec(spark, mod, inv)
    assert out.count() == 0
    bad_df, src, rule, _ = wer.call_args[0]
    assert bad_df.count() == 1
    assert src == mod.GOLD_EXECUTIVE_HEALTH
    assert rule == "executive_health_grain_validation"


def test_tc08_health_score_bounded(spark, mod):
    # Overdue (>90d), no cash, over-utilised credit -> low score but never outside 0..100
    inv = invoices(spark, [("I1", "C1", "cu1", D, date(2000, 1, 1), "INVOICE", Decimal("1000.00"))])
    cus = spark.createDataFrame([("cu1", Decimal("1.00"))], CUS_SCHEMA)
    with patch.object(mod, "write_error_records"):
        out = _exec(spark, mod, inv, cus=cus)
    s = float(out.first()["overall_revenue_to_cash_health_score"])
    assert 0.0 <= s <= 100.0


# ---------------- TC09-TC11 ----------------
def test_tc09_write_error_records_none(mod):
    assert mod.write_error_records(None, "t", "r", "d") is None


def test_tc10_write_audit_log_swallows_errors(mod):
    fake_spark = MagicMock()
    fake_spark.createDataFrame.side_effect = RuntimeError("boom")
    with patch.object(mod, "spark", fake_spark):
        mod.write_audit_log("s", "t", datetime.now(), datetime.now(), "SUCCESS", 1, 1, 0)


def test_tc11_optimize_table_swallows_errors(mod):
    fake_spark = MagicMock()
    fake_spark.sql.side_effect = RuntimeError("no optimize")
    with patch.object(mod, "spark", fake_spark):
        mod.optimize_table("gold.t", "a, b")
    fake_spark.sql.assert_called()


# ---------------- TC12 ----------------
def test_tc12_extract_silver_sources(spark, mod):
    inv = spark.createDataFrame(
        [("I1", "C1", "cu1", "2024-01-01", "2024-02-01", " invoice ", "12.345")],
        "invoice_id string, contract_id string, customer_id string, invoice_date string, due_date string, "
        "invoice_type string, invoice_amount string")
    con = spark.createDataFrame(
        [("C1", " E1 ", " B1 ", " Excavator ", "10")],
        "contract_id string, sales_rep_id string, branch_code string, equipment_class string, daily_rate string"
    ).withColumn("contract_start_date", __import__("pyspark.sql.functions", fromlist=["lit"]).lit("2024-01-01")) \
     .withColumn("contract_end_date", __import__("pyspark.sql.functions", fromlist=["lit"]).lit("2024-12-31"))
    cr = spark.createDataFrame([("I1", "2024-01-05", "5", None)],
                               "invoice_id string, receipt_date string, payment_amount string, unapplied_payment_amount string")
    cus = spark.createDataFrame([("cu1", "100", " ACTIVE ")], "customer_id string, credit_limit string, customer_status string")
    emp = spark.createDataFrame([(" E1 ", " Alice ", " B1 ", " EAST ", " C1 ")],
                                "employee_id string, employee_name string, branch_code string, region string, collector_id string")
    tables = {mod.SILVER_INVOICES: inv, mod.SILVER_CONTRACTS: con, mod.SILVER_CASH_RECEIPTS: cr,
              mod.SILVER_CUSTOMERS: cus, mod.SILVER_EMPLOYEES: emp}
    fake_spark = MagicMock()
    fake_spark.table.side_effect = lambda n: tables[n]
    with patch.object(mod, "spark", fake_spark):
        i, c, r, cu, e = mod.extract_silver_sources()
    ir = i.first()
    assert ir["invoice_date"] == date(2024, 1, 1)
    assert ir["invoice_type"] == "INVOICE"
    assert ir["invoice_amount"] == Decimal("12.35") or ir["invoice_amount"] == Decimal("12.34")
    cr_ = c.first()
    assert (cr_["sales_rep_id"], cr_["branch_code"], cr_["equipment_class"]) == ("e1", "b1", "excavator")
    assert r.first()["unapplied_payment_amount"] == Decimal("0.00")
    assert cu.first()["customer_status"] == "active"
    er = e.first()
    assert (er["employee_id"], er["employee_name"], er["region"]) == ("e1", "Alice", "east")


# ---------------- TC13/TC14 ----------------
def _main_patches(mod, fake_spark):
    fake_spark.sql.return_value.collect.return_value = [{"ts": datetime(2024, 1, 1)}]
    df = MagicMock()
    df.count.return_value = 3
    return df


def test_tc13_main_success(mod):
    fake_spark = MagicMock()
    df = _main_patches(mod, fake_spark)
    with patch.object(mod, "spark", fake_spark), \
         patch.object(mod, "create_gold_support_tables") as cgs, \
         patch.object(mod, "extract_silver_sources", return_value=(df, df, df, df, df)), \
         patch.object(mod, "build_billing_performance", return_value=df), \
         patch.object(mod, "build_executive_health", return_value=df), \
         patch.object(mod, "load_gold_table") as load, \
         patch.object(mod, "write_audit_log") as audit:
        mod.main()
    cgs.assert_called_once()
    assert load.call_count == 2
    assert [c[0][1] for c in load.call_args_list] == [mod.GOLD_BILLING_PERFORMANCE, mod.GOLD_EXECUTIVE_HEALTH]
    kw = audit.call_args.kwargs
    assert kw["status"] == "SUCCESS"
    assert kw["records_read_count"] == 15
    assert kw["records_written_count"] == 6


def test_tc14_main_failure_audits_and_raises(mod):
    fake_spark = MagicMock()
    _main_patches(mod, fake_spark)
    with patch.object(mod, "spark", fake_spark), \
         patch.object(mod, "create_gold_support_tables", side_effect=RuntimeError("ddl failed")), \
         patch.object(mod, "write_audit_log") as audit:
        with pytest.raises(RuntimeError, match="ddl failed"):
            mod.main()
    kw = audit.call_args.kwargs
    assert kw["status"] == "FAILED"
    assert "ddl failed" in kw["error_message"]


# ---------------- TC15 ----------------
def test_tc15_empty_inputs(spark, mod):
    inv = spark.createDataFrame([], INV_SCHEMA)
    with patch.object(mod, "write_error_records"):
        assert mod.build_billing_performance(inv, contracts(spark), employees(spark)).count() == 0
        assert _exec(spark, mod, inv).count() == 0
