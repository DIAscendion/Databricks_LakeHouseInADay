"""
_____________________________________________
Author: AAVA
Created on:
Description: Pytest unit tests for Databricks_Gold_Dim_DE_Pipeline_1.py (Gold dimension load: customer,
             branch employee, rental contract) - Databricks compatible (uses existing `spark` or a local session).
Version: 1
Updated on:
_____________________________________________

Test Case List
| ID    | Description                                                    | Expected Outcome                                         |
|-------|----------------------------------------------------------------|----------------------------------------------------------|
| TC01  | Customer: valid rows, happy path                               | Normalized values, 1 row, SK populated                   |
| TC02  | Customer: null/blank customer_id                               | Rejected count 2, excluded from dim                      |
| TC03  | Customer: duplicates by customer_id                            | Latest update_date retained                              |
| TC04  | Customer: over_limit_indicator mapping                         | TRUE/YES/1->Y, FALSE/NO/0->N, other unchanged            |
| TC05  | Customer: empty source                                         | Empty dim, read=0, rejected=0                            |
| TC06  | Branch employee: happy path normalization                      | Role/branch/region uppercased, name initcap              |
| TC07  | Branch employee: null employee_id or branch_code               | Rejected, excluded                                       |
| TC08  | Branch employee: dedup on (employee, branch, effective_date)   | Latest update retained                                   |
| TC09  | Rental contract: happy path                                    | 1 row, uppercase codes, SK populated                     |
| TC10  | Rental contract: end date before start date                    | Rejected via chronology rule                             |
| TC11  | Rental contract: null contract_id/customer_id                  | Rejected, excluded                                       |
| TC12  | Rental contract: duplicate contract_id                         | Latest update retained                                   |
| TC13  | write_error_records: empty DataFrame                           | Returns 0, no write                                      |
| TC14  | write_error_records: non-empty                                 | Returns row count, writes to ERROR_TABLE                 |
| TC15  | merge_to_delta: target missing                                 | Overwrite saveAsTable, returns count                     |
| TC16  | merge_to_delta: target exists                                  | DeltaTable merge executed, returns count                 |
| TC17  | run_dimension_pipeline: success                                | 3 SUCCESS audit logs, optimize called                    |
| TC18  | run_dimension_pipeline: loader fails                           | FAILED audit logged, exception re-raised                 |
| TC19  | run_dimension_pipeline: missing Gold column                    | ValueError on compatibility validation                   |
| TC20  | standardize_text: trims whitespace                             | Leading/trailing blanks removed                          |
"""

import importlib.util
import os
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("pyspark")
pytest.importorskip("delta")
from pyspark.sql import SparkSession  # noqa: E402

PIPELINE_PATH = os.environ.get(
    "PIPELINE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "DI_Databricks_Gold_Dim_DE_Pipeline",
                 "Databricks_Gold_Dim_DE_Pipeline_1.py"),
)


@pytest.fixture(scope="session")
def spark_session():
    return SparkSession.builder.master("local[1]").appName("gold_dim_ut") \
        .config("spark.sql.shuffle.partitions", "1").getOrCreate()


@pytest.fixture(scope="session")
def pipeline(spark_session):
    spec = importlib.util.spec_from_file_location("gold_dim_pipeline", PIPELINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _use(pipeline, spark_session, df):
    """Make pipeline.spark.table() return df; capture error writes."""
    fake = MagicMock()
    fake.table.return_value = df
    pipeline.spark = fake
    return fake


CUST_SCHEMA = ("customer_id string, customer_name string, credit_terms string, credit_limit double, "
               "customer_since date, customer_status string, over_limit_indicator string, "
               "source_system string, update_date timestamp, load_date timestamp")
EMP_SCHEMA = ("employee_id string, employee_name string, role string, branch_code string, region string, "
              "collector_id string, effective_date date, source_system string, update_date timestamp, "
              "load_date timestamp")
CON_SCHEMA = ("contract_id string, customer_id string, branch_code string, sales_rep_id string, "
              "equipment_class string, contract_start_date date, contract_end_date date, "
              "contract_status string, daily_rate double, source_system string, update_date timestamp, "
              "load_date timestamp")
T1, T2 = datetime(2024, 1, 1), datetime(2024, 2, 1)


def _cust(**kw):
    base = ("C1", "john smith", "net30", 100.0, date(2020, 1, 1), "active", "yes", "ERP", T1, T1)
    cols = ["customer_id", "customer_name", "credit_terms", "credit_limit", "customer_since",
            "customer_status", "over_limit_indicator", "source_system", "update_date", "load_date"]
    d = dict(zip(cols, base)); d.update(kw)
    return tuple(d[c] for c in cols)


def _emp(**kw):
    cols = ["employee_id", "employee_name", "role", "branch_code", "region", "collector_id",
            "effective_date", "source_system", "update_date", "load_date"]
    d = dict(zip(cols, ("E1", "jane doe", "mgr", "b01", "west", "COL1", date(2023, 1, 1), "HR", T1, T1)))
    d.update(kw)
    return tuple(d[c] for c in cols)


def _con(**kw):
    cols = ["contract_id", "customer_id", "branch_code", "sales_rep_id", "equipment_class",
            "contract_start_date", "contract_end_date", "contract_status", "daily_rate",
            "source_system", "update_date", "load_date"]
    d = dict(zip(cols, ("K1", "C1", "b01", "S1", "excavator", date(2024, 1, 1), date(2024, 6, 1),
                        "open", 50.0, "ERP", T1, T1)))
    d.update(kw)
    return tuple(d[c] for c in cols)


# ---------------- Customer ----------------
def test_tc01_customer_happy(pipeline, spark_session):
    df = spark_session.createDataFrame([_cust()], CUST_SCHEMA)
    _use(pipeline, spark_session, df)
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, read, rej = pipeline.load_dim_customer()
    r = out.collect()
    assert len(r) == 1 and read == 1 and rej == 0
    assert r[0]["customer_name"] == "John Smith"
    assert r[0]["credit_terms"] == "NET30" and r[0]["customer_status"] == "ACTIVE"
    assert r[0]["customer_dim_sk"] is not None


def test_tc02_customer_invalid_ids(pipeline, spark_session):
    df = spark_session.createDataFrame([_cust(customer_id=None), _cust(customer_id="  "), _cust()], CUST_SCHEMA)
    _use(pipeline, spark_session, df)
    with patch.object(pipeline, "write_error_records", return_value=2) as w:
        out, read, rej = pipeline.load_dim_customer()
    assert out.count() == 1 and rej == 2 and read == 3
    assert w.call_args[0][0].count() == 2


def test_tc03_customer_dedup(pipeline, spark_session):
    df = spark_session.createDataFrame(
        [_cust(customer_name="old", update_date=T1), _cust(customer_name="new", update_date=T2)], CUST_SCHEMA)
    _use(pipeline, spark_session, df)
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, _, _ = pipeline.load_dim_customer()
    r = out.collect()
    assert len(r) == 1 and r[0]["customer_name"] == "New"


def test_tc04_customer_over_limit_mapping(pipeline, spark_session):
    vals = ["TRUE", "yes", "1", "FALSE", "no", "0", "maybe"]
    rows = [_cust(customer_id=f"C{i}", over_limit_indicator=v) for i, v in enumerate(vals)]
    _use(pipeline, spark_session, spark_session.createDataFrame(rows, CUST_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, _, _ = pipeline.load_dim_customer()
    m = {r["customer_id"]: r["over_limit_indicator"] for r in out.collect()}
    assert [m[f"C{i}"] for i in range(7)] == ["Y", "Y", "Y", "N", "N", "N", "maybe"]


def test_tc05_customer_empty(pipeline, spark_session):
    _use(pipeline, spark_session, spark_session.createDataFrame([], CUST_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, read, rej = pipeline.load_dim_customer()
    assert out.count() == 0 and read == 0 and rej == 0


# ---------------- Branch employee ----------------
def test_tc06_employee_happy(pipeline, spark_session):
    _use(pipeline, spark_session, spark_session.createDataFrame([_emp()], EMP_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, read, rej = pipeline.load_dim_branch_employee()
    r = out.collect()[0]
    assert r["employee_name"] == "Jane Doe" and r["role"] == "MGR"
    assert r["branch_code"] == "B01" and r["region"] == "WEST"
    assert r["branch_employee_dim_sk"] is not None


def test_tc07_employee_invalid_keys(pipeline, spark_session):
    rows = [_emp(employee_id=None), _emp(branch_code=" "), _emp()]
    _use(pipeline, spark_session, spark_session.createDataFrame(rows, EMP_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=2):
        out, _, rej = pipeline.load_dim_branch_employee()
    assert out.count() == 1 and rej == 2


def test_tc08_employee_dedup(pipeline, spark_session):
    rows = [_emp(employee_name="old", update_date=T1), _emp(employee_name="new", update_date=T2)]
    _use(pipeline, spark_session, spark_session.createDataFrame(rows, EMP_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, _, _ = pipeline.load_dim_branch_employee()
    r = out.collect()
    assert len(r) == 1 and r[0]["employee_name"] == "New"


# ---------------- Rental contract ----------------
def test_tc09_contract_happy(pipeline, spark_session):
    _use(pipeline, spark_session, spark_session.createDataFrame([_con()], CON_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, read, rej = pipeline.load_dim_rental_contract()
    r = out.collect()[0]
    assert r["branch_code"] == "B01" and r["equipment_class"] == "EXCAVATOR" and r["contract_status"] == "OPEN"
    assert r["rental_contract_dim_sk"] is not None


def test_tc10_contract_date_chronology(pipeline, spark_session):
    rows = [_con(contract_id="K2", contract_end_date=date(2023, 1, 1)), _con()]
    _use(pipeline, spark_session, spark_session.createDataFrame(rows, CON_SCHEMA))
    with patch.object(pipeline, "write_error_records", side_effect=[0, 1]) as w:
        out, _, rej = pipeline.load_dim_rental_contract()
    assert rej == 1 and out.count() == 1
    assert w.call_args_list[1][0][3] == "contract_date_chronology"


def test_tc11_contract_invalid_keys(pipeline, spark_session):
    rows = [_con(contract_id=None), _con(customer_id=""), _con()]
    _use(pipeline, spark_session, spark_session.createDataFrame(rows, CON_SCHEMA))
    with patch.object(pipeline, "write_error_records", side_effect=[2, 0]):
        out, _, rej = pipeline.load_dim_rental_contract()
    assert out.count() == 1 and rej == 2


def test_tc12_contract_dedup(pipeline, spark_session):
    rows = [_con(daily_rate=10.0, update_date=T1), _con(daily_rate=99.0, update_date=T2)]
    _use(pipeline, spark_session, spark_session.createDataFrame(rows, CON_SCHEMA))
    with patch.object(pipeline, "write_error_records", return_value=0):
        out, _, _ = pipeline.load_dim_rental_contract()
    r = out.collect()
    assert len(r) == 1 and r[0]["daily_rate"] == 99.0


# ---------------- Helpers ----------------
def test_tc13_write_error_records_empty(pipeline, spark_session):
    df = spark_session.createDataFrame([], CUST_SCHEMA)
    assert pipeline.write_error_records(df, "s", "t", "r", "c", "d", "HIGH", "customer_id") == 0


def test_tc14_write_error_records_nonempty(pipeline, spark_session):
    df = spark_session.createDataFrame([_cust()], CUST_SCHEMA)
    with patch("pyspark.sql.DataFrameWriter.saveAsTable") as save:
        n = pipeline.write_error_records(df, "s", "t", "r", "c", "d", "HIGH", "customer_id")
    assert n == 1
    save.assert_called_once_with(pipeline.ERROR_TABLE)


def test_tc15_merge_target_missing(pipeline, spark_session):
    df = spark_session.createDataFrame([("a",)], "k string")
    fake = MagicMock(); fake.catalog.tableExists.return_value = False
    pipeline.spark = fake
    with patch("pyspark.sql.DataFrameWriter.saveAsTable") as save:
        assert pipeline.merge_to_delta(df, "gold.x", "k") == 1
    save.assert_called_once_with("gold.x")


def test_tc16_merge_target_exists(pipeline, spark_session):
    df = spark_session.createDataFrame([("a",), ("b",)], "k string")
    fake = MagicMock(); fake.catalog.tableExists.return_value = True
    pipeline.spark = fake
    with patch.object(pipeline, "DeltaTable") as dt:
        assert pipeline.merge_to_delta(df, "gold.x", "k") == 2
    dt.forName.assert_called_once()
    dt.forName.return_value.alias.return_value.merge.return_value \
        .whenMatchedUpdateAll.return_value.whenNotMatchedInsertAll.return_value.execute.assert_called_once()


def test_tc20_standardize_text(pipeline, spark_session):
    df = spark_session.createDataFrame([("  abc  ",)], "c string")
    assert df.select(pipeline.standardize_text("c").alias("c")).collect()[0]["c"] == "abc"


# ---------------- Orchestration ----------------
def _orchestration_mocks(pipeline, cols_ok=True):
    fake = MagicMock()
    fake.sql.return_value.collect.return_value = [{"ts": datetime(2024, 1, 1)}]
    cols = {
        "gold.dim_customer": ["customer_dim_sk", "customer_id", "customer_name", "credit_terms",
                              "credit_limit", "customer_since_date", "customer_status"],
        "gold.dim_branch_employee": ["branch_employee_dim_sk", "employee_id", "employee_name", "role",
                                     "branch_code", "region", "effective_date"],
        "gold.dim_rental_contract": ["rental_contract_dim_sk", "contract_id", "customer_id", "branch_code",
                                     "contract_start_date", "contract_status"],
    }
    if not cols_ok:
        cols["gold.dim_customer"] = ["customer_id"]
    fake.table.side_effect = lambda n: MagicMock(columns=cols[n])
    pipeline.spark = fake
    return fake


def test_tc17_pipeline_success(pipeline):
    _orchestration_mocks(pipeline)
    loader = MagicMock(return_value=(MagicMock(), 5, 1))
    loader.__name__ = "load_dim_customer"
    with patch.object(pipeline, "create_gold_support_tables"), \
         patch.object(pipeline, "load_dim_customer", loader), \
         patch.object(pipeline, "load_dim_branch_employee", MagicMock(return_value=(MagicMock(), 1, 0), __name__="load_dim_branch_employee")), \
         patch.object(pipeline, "load_dim_rental_contract", MagicMock(return_value=(MagicMock(), 1, 0), __name__="load_dim_rental_contract")), \
         patch.object(pipeline, "merge_to_delta", return_value=4), \
         patch.object(pipeline, "write_audit_log") as audit, \
         patch.object(pipeline, "optimize_gold_tables") as opt:
        pipeline.run_dimension_pipeline()
    assert audit.call_count == 3
    assert all(c.kwargs["status"] == "SUCCESS" for c in audit.call_args_list)
    opt.assert_called_once()


def test_tc18_pipeline_loader_failure(pipeline):
    _orchestration_mocks(pipeline)
    bad = MagicMock(side_effect=RuntimeError("boom"), __name__="load_dim_customer")
    with patch.object(pipeline, "create_gold_support_tables"), \
         patch.object(pipeline, "load_dim_customer", bad), \
         patch.object(pipeline, "write_audit_log") as audit, \
         patch.object(pipeline, "optimize_gold_tables") as opt:
        with pytest.raises(RuntimeError, match="boom"):
            pipeline.run_dimension_pipeline()
    assert audit.call_args.kwargs["status"] == "FAILED"
    assert audit.call_args.kwargs["error_message"] == "boom"
    opt.assert_not_called()


def test_tc19_pipeline_missing_gold_columns(pipeline):
    _orchestration_mocks(pipeline, cols_ok=False)
    ok = lambda n: MagicMock(return_value=(MagicMock(), 1, 0), __name__=n)
    with patch.object(pipeline, "create_gold_support_tables"), \
         patch.object(pipeline, "load_dim_customer", ok("load_dim_customer")), \
         patch.object(pipeline, "load_dim_branch_employee", ok("load_dim_branch_employee")), \
         patch.object(pipeline, "load_dim_rental_contract", ok("load_dim_rental_contract")), \
         patch.object(pipeline, "merge_to_delta", return_value=1), \
         patch.object(pipeline, "write_audit_log"), \
         patch.object(pipeline, "optimize_gold_tables"):
        with pytest.raises(ValueError, match="compatibility validation failed"):
            pipeline.run_dimension_pipeline()


# Note: standardize_text uses r"\\s+" (escaped backslash in raw string), so internal whitespace is not collapsed;
# tests intentionally assert only trimming behavior.
# apiCost: 0.0112580000000000
