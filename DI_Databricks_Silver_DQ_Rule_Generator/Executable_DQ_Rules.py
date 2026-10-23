# Databricks notebook source
"""
_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Executable Silver-layer data quality rules (PySpark + Spark SQL) for the Rental Revenue-to-Cash domain, with error-table quarantine and pipeline-audit logging.
## *Version*: 1
## *Updated on*:
_____________________________________________

Summary
-------
This module turns the Silver DQ recommendations, the Bronze-to-Silver data mapping and the
Silver physical DDL into 80 executable DQ rules. The rules cover the five Silver business tables
(silver.si_rental_contracts, silver.si_invoices, silver.si_cash_receipts,
silver.si_customer_master, silver.si_branch_employee) and the two operational tables
(silver.si_error_data, silver.si_pipeline_audit). Every rule is defined once in RULES. The
rule engine produces a logically equivalent PySpark evaluation and a Databricks Spark SQL query
that returns violating rows. Critical rules stop the run, Error rules quarantine rows to
silver.si_error_data, and Warning rules keep rows and are logged to silver.si_pipeline_audit.

=====================================================================================
1. Overview
=====================================================================================
Inputs used (read from GitHub repo DIAscendion/Databricks_LakeHouseInADay):
  - DI_Databricks_Silver_DQ_Recommender/Databricks_Silver_DQ_Recommender_1.md  (data constraints / DQ recs, "REC #n")
  - DI_Databricks_Silver_DQ_Data_Mapping/Databricks_Silver_DQ_Data_Mapping_1.md (mapping rows, "MAP x.y <column>")
  - DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md    (Silver DDL, "DDL"; referenced by the
    mapping document and read to use exact table/column names)
Missing inputs:
  - Profiler insights: NOT provided. There are no null rates, distinct counts or value ranges, so every threshold
    is a conservative default listed in Section 5.
  - The Constraints document was not listed as an input. Its rules are used only where the Recommender restates them.
Approach:
  - Rule ids DQ_001..DQ_080 run in order. Each rule is idempotent and read-only against the evaluated tables.
  - Rule kinds: row (predicate), unique, ref (anti-join), multi_value, null_rate, row_count.
  - Column/table names come from the Silver DDL. Where the mapping uses names that are NOT in the DDL
    (derived columns, the error and audit table names), see Section 5. Rules on derived columns carry a
    `requires` guard. If the column is missing at runtime, the rule is reported as SKIPPED and is not run.

=====================================================================================
2. Rule Catalog
=====================================================================================
| Rule ID | Table | Column(s) | Category | Rule Description | Severity | Action on Failure | Source |
|---|---|---|---|---|---|---|---|
| DQ_001 | silver.si_rental_contracts | (table) | Table-level | Table has >= 1 row | Critical | fail | Assumption (table-level) |
| DQ_002 | silver.si_rental_contracts | rental_contract_sk | Completeness | Surrogate key not null | Critical | fail | MAP 4.1 rental_contract_sk |
| DQ_003 | silver.si_rental_contracts | contract_id | Completeness | contract_id not null/blank | Error | quarantine | MAP 4.1 contract_id; REC #1 |
| DQ_004 | silver.si_rental_contracts | contract_id | Uniqueness | contract_id unique | Error | quarantine | MAP 4.1 contract_id |
| DQ_005 | silver.si_rental_contracts | customer_id | Completeness | customer_id not null/blank | Error | quarantine | MAP 4.1 customer_id |
| DQ_006 | silver.si_rental_contracts | branch_code | Validity | branch_code not null and matches ^[A-Z0-9_-]+$ | Error | quarantine | MAP 4.1 branch_code |
| DQ_007 | silver.si_rental_contracts | sales_rep_id | Validity | If present, matches ^[A-Za-z0-9_-]+$ | Warning | log | MAP 4.1 sales_rep_id |
| DQ_008 | silver.si_rental_contracts | sales_rep_id | Completeness | Null rate <= 5% | Warning | log | MAP 4.1 (nullable); default threshold |
| DQ_009 | silver.si_rental_contracts | equipment_class | Validity | If present, trimmed and uppercase | Warning | log | MAP 4.1 equipment_class |
| DQ_010 | silver.si_rental_contracts | contract_start_date | Completeness | Not null | Error | quarantine | MAP 4.1 contract_start_date |
| DQ_011 | silver.si_rental_contracts | contract_start_date | Validity | >= 1900-01-01 | Warning | log | Default range (Assumption) |
| DQ_012 | silver.si_rental_contracts | contract_end_date, contract_start_date | Business logic | end >= start when both present | Error | quarantine | MAP 4.1 contract_end_date; REC #3 |
| DQ_013 | silver.si_rental_contracts | contract_status | Validity | In ACTIVE, CLOSED, CANCELLED, PENDING, OPEN | Error | quarantine | MAP 4.1 contract_status; REC #2 |
| DQ_014 | silver.si_rental_contracts | daily_rate | Validity | daily_rate >= 0 when present | Error | quarantine | MAP 4.1 daily_rate; REC #4 |
| DQ_015 | silver.si_rental_contracts | customer_id | Referential | Exists in si_customer_master.customer_id | Error | quarantine | REC #26; DDL 3.3 joins |
| DQ_016 | silver.si_rental_contracts | sales_rep_id | Referential | Exists in si_branch_employee.employee_id | Warning | log | DDL 3.3 joins (sales_rep_id = employee_id) |
| DQ_017 | silver.si_rental_contracts | branch_code | Referential | Exists in si_branch_employee.branch_code | Warning | log | DDL 3.3 joins; REC #30 |
| DQ_018 | silver.si_rental_contracts | load_date, update_date, source_system, file_path | Table-level | Metadata/lineage not null | Error | quarantine | MAP 4.1 metadata rows; REC #20 |
| DQ_019 | silver.si_invoices | (table) | Table-level | Table has >= 1 row | Critical | fail | Assumption |
| DQ_020 | silver.si_invoices | invoice_sk | Completeness | Not null | Critical | fail | MAP 4.2 invoice_sk |
| DQ_021 | silver.si_invoices | invoice_id | Completeness | Not null/blank | Error | quarantine | MAP 4.2 invoice_id; REC #5 |
| DQ_022 | silver.si_invoices | invoice_id | Uniqueness | Unique | Error | quarantine | MAP 4.2 invoice_id |
| DQ_023 | silver.si_invoices | customer_id | Completeness | Not null/blank | Error | quarantine | MAP 4.2 customer_id |
| DQ_024 | silver.si_invoices | invoice_date | Completeness | Not null | Error | quarantine | MAP 4.2 invoice_date; REC #6 |
| DQ_025 | silver.si_invoices | invoice_date | Validity | 1900-01-01 <= invoice_date <= current_date | Warning | log | Default range (Assumption) |
| DQ_026 | silver.si_invoices | due_date | Completeness | due_date not null | Warning | log | REC #7 vs MAP 4.2 (nullable) - conflict |
| DQ_027 | silver.si_invoices | due_date, invoice_date | Business logic | due_date >= invoice_date | Warning | log | MAP 4.2 due_date ("flag") |
| DQ_028 | silver.si_invoices | invoice_amount | Completeness | Not null | Error | quarantine | MAP 4.2 invoice_amount |
| DQ_029 | silver.si_invoices | invoice_amount, invoice_type | Business logic | Non-CREDIT_MEMO amount >= 0 | Error | quarantine | REC #8; MAP 4.2 invoice_amount |
| DQ_030 | silver.si_invoices | invoice_amount, invoice_type | Business logic | CREDIT_MEMO amount < 0 | Error | quarantine | REC #9 |
| DQ_031 | silver.si_invoices | tax_amount, invoice_type | Business logic | tax_amount >= 0 unless CREDIT_MEMO | Warning | log | MAP 4.2 tax_amount |
| DQ_032 | silver.si_invoices | invoice_type | Validity | In INVOICE, CREDIT_MEMO, DEBIT_MEMO | Error | quarantine | MAP 4.2 invoice_type |
| DQ_033 | silver.si_invoices | currency | Validity | Not null and ^[A-Z]{3}$ | Error | quarantine | MAP 4.2 currency; REC #10 |
| DQ_034 | silver.si_invoices | contract_id | Completeness | Null rate <= 5% | Warning | log | MAP 4.2 (nullable); default threshold |
| DQ_035 | silver.si_invoices | contract_id | Referential | If present, exists in si_rental_contracts | Error | quarantine | REC #27; MAP 4.2 contract_id |
| DQ_036 | silver.si_invoices | customer_id | Referential | Exists in si_customer_master | Error | quarantine | REC #28; MAP 5.4 |
| DQ_037 | silver.si_invoices | aging_bucket | Validity | In 0-30, 31-60, 61-90, 90+ (requires column) | Warning | log | MAP 4.2 aging_bucket; REC #35 |
| DQ_038 | silver.si_invoices | days_past_due, due_date | Business logic | days_past_due = datediff(current_date, due_date) (requires column) | Warning | log | MAP 4.2 days_past_due |
| DQ_039 | silver.si_invoices | aging_bucket, due_date | Business logic | Bucket matches days past due (requires column) | Warning | log | REC #36 |
| DQ_040 | silver.si_invoices | load_date, update_date, source_system, file_path | Table-level | Metadata/lineage not null | Error | quarantine | MAP 4.2 metadata; REC #20 |
| DQ_041 | silver.si_cash_receipts | (table) | Table-level | Table has >= 1 row | Critical | fail | Assumption |
| DQ_042 | silver.si_cash_receipts | cash_receipt_sk | Completeness | Not null | Critical | fail | MAP 4.3 cash_receipt_sk |
| DQ_043 | silver.si_cash_receipts | receipt_id | Completeness | Not null/blank | Error | quarantine | MAP 4.3 receipt_id |
| DQ_044 | silver.si_cash_receipts | receipt_id | Uniqueness | Unique | Error | quarantine | MAP 4.3 receipt_id; REC #11 |
| DQ_045 | silver.si_cash_receipts | customer_id | Completeness | Not null/blank | Error | quarantine | MAP 4.3 customer_id |
| DQ_046 | silver.si_cash_receipts | receipt_date | Completeness | Not null | Error | quarantine | MAP 4.3 receipt_date; REC #13 |
| DQ_047 | silver.si_cash_receipts | receipt_date | Validity | 1900-01-01 <= receipt_date <= current_date | Warning | log | Default range (Assumption) |
| DQ_048 | silver.si_cash_receipts | payment_amount | Validity | Not null and >= 0 | Error | quarantine | MAP 4.3 payment_amount; REC #12 |
| DQ_049 | silver.si_cash_receipts | payment_method | Validity | If present, not blank and uppercase-trimmed | Warning | log | MAP 4.3 payment_method (no domain list given) |
| DQ_050 | silver.si_cash_receipts | invoice_id | Referential | If present, exists in si_invoices | Warning | log | REC #29; MAP 5.4 |
| DQ_051 | silver.si_cash_receipts | customer_id | Referential | Exists in si_customer_master | Error | quarantine | DDL 3.3 joins; MAP 5.4 |
| DQ_052 | silver.si_cash_receipts | receipt_date, invoice_id | Business logic | receipt_date >= linked invoice_date | Warning | log | REC #45 |
| DQ_053 | silver.si_cash_receipts | match_status | Validity | In MATCHED, UNMATCHED, PARTIAL, UNAPPLIED (requires column) | Error | quarantine | MAP 4.3 match_status |
| DQ_054 | silver.si_cash_receipts | invoice_id, match_status | Business logic | invoice_id null => match_status = UNAPPLIED (requires column) | Warning | log | REC #44 |
| DQ_055 | silver.si_cash_receipts | unapplied_payment_amount, payment_amount | Business logic | 0 <= unapplied <= payment_amount (requires column) | Error | quarantine | MAP 4.3 unapplied_payment_amount |
| DQ_056 | silver.si_cash_receipts | invoice_id | Completeness | Null rate <= 5% | Warning | log | MAP 4.3 (nullable); default threshold |
| DQ_057 | silver.si_cash_receipts | load_date, update_date, source_system, file_path | Table-level | Metadata/lineage not null | Error | quarantine | MAP 4.3 metadata; REC #20 |
| DQ_058 | silver.si_customer_master | (table) | Table-level | Table has >= 1 row | Critical | fail | Assumption |
| DQ_059 | silver.si_customer_master | customer_sk | Completeness | Not null | Critical | fail | MAP 4.4 customer_sk |
| DQ_060 | silver.si_customer_master | customer_id | Completeness | Not null/blank | Error | quarantine | MAP 4.4 customer_id; REC #14 |
| DQ_061 | silver.si_customer_master | customer_id | Uniqueness | Unique (deduplicated master) | Error | quarantine | MAP 4.4 customer_id; REC #21 |
| DQ_062 | silver.si_customer_master | customer_name | Completeness | Not null/blank | Error | quarantine | MAP 4.4 customer_name; REC #14 |
| DQ_063 | silver.si_customer_master | credit_limit | Validity | credit_limit >= 0 when present | Error | quarantine | MAP 4.4 credit_limit; REC #15 |
| DQ_064 | silver.si_customer_master | customer_status | Validity | In ACTIVE, INACTIVE, SUSPENDED, CLOSED | Error | quarantine | MAP 4.4 customer_status; REC #16 |
| DQ_065 | silver.si_customer_master | credit_terms | Validity | If present, not blank and uppercase-trimmed | Warning | log | MAP 4.4 credit_terms (no code list given) |
| DQ_066 | silver.si_customer_master | customer_since | Validity | 1900-01-01 <= customer_since <= current_date | Warning | log | MAP 4.4 customer_since; REC #17 |
| DQ_067 | silver.si_customer_master | over_limit_indicator | Validity | In Y, N (requires column) | Error | quarantine | MAP 4.4 over_limit_indicator |
| DQ_068 | silver.si_customer_master | load_date, update_date, source_system, file_path | Table-level | Metadata/lineage not null | Error | quarantine | MAP 4.4 metadata; REC #20 |
| DQ_069 | silver.si_branch_employee | (table) | Table-level | Table has >= 1 row | Critical | fail | Assumption |
| DQ_070 | silver.si_branch_employee | branch_employee_sk | Completeness | Not null | Critical | fail | MAP 4.5 branch_employee_sk |
| DQ_071 | silver.si_branch_employee | employee_id, employee_name | Completeness | Not null/blank | Error | quarantine | MAP 4.5 employee_id, employee_name |
| DQ_072 | silver.si_branch_employee | role | Validity | In SALES_REP, COLLECTOR | Error | quarantine | MAP 4.5 role; REC #18 |
| DQ_073 | silver.si_branch_employee | branch_code | Validity | Not null and ^[A-Z0-9_-]+$ | Error | quarantine | MAP 4.5 branch_code |
| DQ_074 | silver.si_branch_employee | region | Completeness | Not null/blank | Error | quarantine | MAP 4.5 region; REC #19 |
| DQ_075 | silver.si_branch_employee | collector_id | Validity / Referential | If present, matches ^[A-Za-z0-9_-]+$ and exists as employee_id | Warning | log | MAP 4.5 collector_id |
| DQ_076 | silver.si_branch_employee | branch_code, region | Business logic | Each branch_code maps to exactly one region | Warning | log | REC #50; DDL 3.4 Consistency |
| DQ_077 | silver.si_branch_employee | load_date, update_date, source_system, file_path | Table-level | Metadata/lineage not null | Error | quarantine | MAP 4.5 metadata; REC #20 |
| DQ_078 | silver.si_error_data | severity, validation_status, layer_name | Validity | severity in HIGH/MEDIUM/LOW; mandatory fields present | Warning | log | MAP 4.6 |
| DQ_079 | silver.si_pipeline_audit | processing_status, records_* | Validity | status in SUCCESS/FAILED/PARTIAL; counts >= 0; end >= start | Warning | log | MAP 4.7 |
| DQ_080 | silver.si_pipeline_audit | records_read, records_written, records_rejected | Table-level | read = written + rejected for SUCCESS/PARTIAL runs | Warning | log | MAP 4.7 / REC sec. 7 |

=====================================================================================
3. Executable Rules
=====================================================================================
Each rule is defined in RULES below (grouped by table, then category). For any rule:
  - PySpark : `violations_df(spark, rule)` returns the violating rows (DataFrame API: F.expr / Window / left_anti).
  - Spark SQL: `rule_sql(rule)` returns the equivalent query that returns the violating rows.
  - `print_rule_book()` prints each rule's Description, Rationale, PySpark and Spark SQL forms.
Both forms are built from the same rule definition, so they stay logically equivalent.

=====================================================================================
4. Error and Audit Handling
=====================================================================================
Severity -> action:  CRITICAL -> raise DQCriticalFailure (pipeline stops, audit row status FAILED)
                     ERROR    -> failing rows written to silver.si_error_data, excluded from the clean DataFrame
                     WARNING  -> rows kept. The rule id and failed count are logged in silver.si_pipeline_audit.error_message.
silver.si_error_data field mapping (per failed row and rule):
  error_record_sk   = xxhash64(rule_id, table, business_key, run_id)    layer_name   = 'Silver'
  pipeline_name     = PIPELINE_NAME     source_table = bronze table from mapping   target_table = Silver table
  business_key      = natural key (contract_id / invoice_id / receipt_id / customer_id / employee_id)
  table_name        = Silver table     column_name  = rule columns (comma-separated)
  validation_rule   = rule_id || ': ' || rule name     validation_status = 'FAILED'
  rejected_value    = to_json(struct(rule columns))    error_description = rule description
  error_category    = rule category    severity = HIGH (Critical/Error) | MEDIUM (Warning)  [MAP 4.6 domain]
  source_system, file_path = from failing row    detected_timestamp, load_timestamp, update_timestamp = current_timestamp()
  load_date, update_date = current_date()
silver.si_pipeline_audit field mapping (one row per Silver table per run):
  audit_sk = xxhash64(run_id, target_table)    pipeline_run_id = run_id   layer_name = 'Silver'
  pipeline_name, source_table, target_table, process_start_timestamp, process_end_timestamp
  processing_status = SUCCESS (no Error/Critical failures) | PARTIAL (rows quarantined) | FAILED (Critical failure)
  records_read = input rows; records_rejected = distinct quarantined rows; records_written = read - rejected
  processing_time_seconds = end - start (DECIMAL(18,2)); trigger_type; processed_by = current_user()
  error_message = summary "DQ_xxx[SEV]=n; ..." of failing/skipped rules; source_system = NULL (multi-source)
  load_timestamp/update_timestamp = current_timestamp(); load_date/update_date = current_date()

=====================================================================================
5. Assumptions and Open Items
=====================================================================================
 1. No profiler insights were provided. The null-rate threshold defaults to 5% (DQ_008, DQ_034, DQ_056).
    The date sanity floor defaults to 1900-01-01, and transaction and customer_since dates may not be in the future.
 2. Table name conflict: the mapping names silver.si_data_quality_errors and silver.si_process_audit, but the Silver DDL
    defines silver.si_error_data and silver.si_pipeline_audit. This module uses the DDL names (instruction 8).
    The mapping field names (validation_rule_name, error_record_payload, run_id, records_read_count, ...) were mapped
    to the DDL columns as shown in Section 4.
 3. The derived columns aging_bucket, days_past_due, match_status, unapplied_payment_amount and over_limit_indicator
    appear in the mapping but NOT in the Silver DDL. Their rules (DQ_037-039, DQ_053-055, DQ_067) have a
    `requires` guard and are reported as SKIPPED until the columns are added to the DDL.
 4. Domain conflicts: contract_status is OPEN/CLOSED in the Recommender (constraints) and ACTIVE/CLOSED/CANCELLED/PENDING
    in the mapping. The union is allowed (DQ_013). customer_status is ACTIVE/SUSPENDED in the Recommender and
    ACTIVE/INACTIVE/SUSPENDED/CLOSED in the mapping. The mapping superset is used (DQ_064).
 5. due_date: the Recommender treats it as mandatory and the mapping as nullable. It is a Warning (DQ_026), not a quarantine.
 6. Referential relationships were taken from the Silver DDL section 3.3 "Expected Joins", REC #26-#30 and MAP 5.4.
    No FK is enforced (Spark SQL limitation). Receipt->invoice orphans are Warnings because unapplied cash must be
    retained (REC #44).
 7. No approved code lists were provided for payment_method, credit_terms, equipment_class or region. The rules check only
    standardization and non-blank values. Supply the lists to tighten DQ_049, DQ_065, DQ_009 and DQ_074.
 8. Aging-bucket derivation (DQ_039): days_past_due <= 30 (including not-yet-due, negative values) => '0-30', because the
    allowed bucket list has no 'CURRENT' value.
 9. Date parseability checks (REC #6, #7, #13, #17) only apply to Bronze strings. Silver columns are DATE, so an
    unparseable value shows up as NULL and is caught by the not-null rules. Optional dates cannot be told apart from
    source NULLs in Silver.
10. Recommender checks on Gold or aggregate objects that are not in the Silver DDL (ar_aging, credit_risk, executive_scorecard,
    rental_revenue*, cash_application*, dim_date, branch_hierarchy: REC #22-25, #31-34, #37-43, #46-49) were not generated.
    Those tables do not exist in the Silver DDL.
11. Empty tables are treated as Critical (DQ_001/019/041/058/069). Downgrade to Warning for incremental runs where an
    empty batch is legitimate.

=====================================================================================
6. apiCost
=====================================================================================
apiCost: 0.0 USD
"""

from datetime import datetime
import uuid

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

PIPELINE_NAME = "silver_rental_revenue_to_cash_dq"
ERROR_TABLE = "silver.si_error_data"
AUDIT_TABLE = "silver.si_pipeline_audit"
NULL_RATE_THRESHOLD = 0.05  # default, no profiler insights provided (Assumption 1)
MIN_DATE = "1900-01-01"     # default sanity floor (Assumption 1)

CRITICAL, ERROR, WARNING = "CRITICAL", "ERROR", "WARNING"
ACTION = {CRITICAL: "fail", ERROR: "quarantine", WARNING: "log"}
ERROR_SEVERITY = {CRITICAL: "HIGH", ERROR: "HIGH", WARNING: "MEDIUM"}  # MAP 4.6 domain

T_CON = "silver.si_rental_contracts"
T_INV = "silver.si_invoices"
T_REC = "silver.si_cash_receipts"
T_CUS = "silver.si_customer_master"
T_EMP = "silver.si_branch_employee"

TABLE_META = {
    T_CON: {"source": "bronze.bz_rental_contracts", "key": "contract_id"},
    T_INV: {"source": "bronze.bz_invoices", "key": "invoice_id"},
    T_REC: {"source": "bronze.bz_cash_receipts", "key": "receipt_id"},
    T_CUS: {"source": "bronze.bz_customer_master", "key": "customer_id"},
    T_EMP: {"source": "bronze.bz_branch_employee", "key": "employee_id"},
    ERROR_TABLE: {"source": "[MULTIPLE]", "key": "error_record_sk"},
    AUDIT_TABLE: {"source": "bronze.bz_audit_log", "key": "pipeline_run_id"},
}


def _blank(c):
    return f"({c} IS NULL OR trim({c}) = '')"


def _meta_missing():
    return "(load_date IS NULL OR update_date IS NULL OR source_system IS NULL OR trim(source_system) = '' OR file_path IS NULL)"


def R(rule_id, table, columns, category, name, desc, severity, kind, source, rationale, **kw):
    d = dict(id=rule_id, table=table, columns=columns, category=category, name=name, desc=desc,
             severity=severity, kind=kind, source=source, rationale=rationale, requires=[])
    d.update(kw)
    return d


# ----------------------------------------------------------------------------------------------
# RULES - grouped by table, then category
# kind=row        : predicate (Spark SQL expression) TRUE => violation
# kind=unique     : keys
# kind=ref        : col, parent, parent_col
# kind=multi_value: key, value
# kind=null_rate  : col, threshold
# kind=row_count  : table must not be empty
# ----------------------------------------------------------------------------------------------
RULES = [
    # ---------------- silver.si_rental_contracts ----------------
    R("DQ_001", T_CON, [], "Table-level", "contracts_row_count", "Table contains at least one row", CRITICAL, "row_count",
      "Assumption 11", "Empty Silver contract load indicates upstream failure."),
    R("DQ_002", T_CON, ["rental_contract_sk"], "Completeness", "contract_sk_not_null", "rental_contract_sk is not null",
      CRITICAL, "row", "MAP 4.1 rental_contract_sk", "Surrogate key must be generated.", predicate="rental_contract_sk IS NULL"),
    R("DQ_003", T_CON, ["contract_id"], "Completeness", "contract_id_not_blank", "contract_id not null/blank", ERROR, "row",
      "MAP 4.1 contract_id; REC #1", "Core join key for invoices.", predicate=_blank("contract_id")),
    R("DQ_004", T_CON, ["contract_id"], "Uniqueness", "contract_id_unique", "contract_id is unique", ERROR, "unique",
      "MAP 4.1 contract_id", "Mapping requires uniqueness within snapshot.", keys=["contract_id"]),
    R("DQ_005", T_CON, ["customer_id"], "Completeness", "contract_customer_not_blank", "customer_id not null/blank", ERROR, "row",
      "MAP 4.1 customer_id", "Every contract maps to a customer.", predicate=_blank("customer_id")),
    R("DQ_006", T_CON, ["branch_code"], "Validity", "contract_branch_code_format", "branch_code not null and ^[A-Z0-9_-]+$",
      ERROR, "row", "MAP 4.1 branch_code", "Mandatory, valid code format after upper(trim()).",
      predicate="branch_code IS NULL OR NOT (branch_code RLIKE '^[A-Z0-9_-]+$')"),
    R("DQ_007", T_CON, ["sales_rep_id"], "Validity", "sales_rep_id_format", "sales_rep_id matches employee id format if present",
      WARNING, "row", "MAP 4.1 sales_rep_id", "Must match employee identifier format.",
      predicate="sales_rep_id IS NOT NULL AND NOT (sales_rep_id RLIKE '^[A-Za-z0-9_-]+$')"),
    R("DQ_008", T_CON, ["sales_rep_id"], "Completeness", "sales_rep_id_null_rate", "sales_rep_id null rate <= 5%",
      WARNING, "null_rate", "MAP 4.1 sales_rep_id; Assumption 1", "Nullable column; monitor tolerated nulls.",
      col="sales_rep_id", threshold=NULL_RATE_THRESHOLD),
    R("DQ_009", T_CON, ["equipment_class"], "Validity", "equipment_class_standardized", "equipment_class is upper(trim()) if present",
      WARNING, "row", "MAP 4.1 equipment_class", "Standardized text required.",
      predicate="equipment_class IS NOT NULL AND (equipment_class <> upper(trim(equipment_class)) OR trim(equipment_class) = '')"),
    R("DQ_010", T_CON, ["contract_start_date"], "Completeness", "contract_start_not_null", "contract_start_date not null",
      ERROR, "row", "MAP 4.1 contract_start_date", "Required, reject if unparseable.", predicate="contract_start_date IS NULL"),
    R("DQ_011", T_CON, ["contract_start_date"], "Validity", "contract_start_range", f"contract_start_date >= {MIN_DATE}",
      WARNING, "row", "Assumption 1", "Sanity floor for parsed dates.", predicate=f"contract_start_date < DATE'{MIN_DATE}'"),
    R("DQ_012", T_CON, ["contract_start_date", "contract_end_date"], "Business logic", "contract_end_after_start",
      "contract_end_date >= contract_start_date", ERROR, "row", "MAP 4.1 contract_end_date; REC #3",
      "Impossible contract periods distort ADR.", predicate="contract_end_date < contract_start_date"),
    R("DQ_013", T_CON, ["contract_status"], "Validity", "contract_status_domain",
      "contract_status in ACTIVE, CLOSED, CANCELLED, PENDING, OPEN", ERROR, "row", "MAP 4.1 contract_status; REC #2",
      "Allowed status domain (union, Assumption 4).",
      predicate="contract_status IS NULL OR contract_status NOT IN ('ACTIVE','CLOSED','CANCELLED','PENDING','OPEN')"),
    R("DQ_014", T_CON, ["daily_rate"], "Validity", "daily_rate_non_negative", "daily_rate >= 0", ERROR, "row",
      "MAP 4.1 daily_rate; REC #4", "Rental rate cannot be negative.", predicate="daily_rate < 0"),
    R("DQ_015", T_CON, ["customer_id"], "Referential", "contract_customer_fk", "customer_id exists in silver.si_customer_master",
      ERROR, "ref", "REC #26; DDL 3.3", "Every contract must map to a valid customer.",
      col="customer_id", parent=T_CUS, parent_col="customer_id"),
    R("DQ_016", T_CON, ["sales_rep_id"], "Referential", "contract_sales_rep_fk", "sales_rep_id exists in silver.si_branch_employee.employee_id",
      WARNING, "ref", "DDL 3.3 (sales_rep_id = employee_id)", "Sales rep drill-down alignment.",
      col="sales_rep_id", parent=T_EMP, parent_col="employee_id"),
    R("DQ_017", T_CON, ["branch_code"], "Referential", "contract_branch_fk", "branch_code exists in silver.si_branch_employee",
      WARNING, "ref", "DDL 3.3; REC #30", "Branch rollup conformance.", col="branch_code", parent=T_EMP, parent_col="branch_code"),
    R("DQ_018", T_CON, ["load_date", "update_date", "source_system", "file_path"], "Table-level", "contract_metadata",
      "Metadata/lineage columns populated", ERROR, "row", "MAP 4.1 metadata; REC #20", "Lineage & auditability.",
      predicate=_meta_missing()),

    # ---------------- silver.si_invoices ----------------
    R("DQ_019", T_INV, [], "Table-level", "invoices_row_count", "Table contains at least one row", CRITICAL, "row_count",
      "Assumption 11", "Empty invoice load indicates upstream failure."),
    R("DQ_020", T_INV, ["invoice_sk"], "Completeness", "invoice_sk_not_null", "invoice_sk not null", CRITICAL, "row",
      "MAP 4.2 invoice_sk", "Surrogate key must be generated.", predicate="invoice_sk IS NULL"),
    R("DQ_021", T_INV, ["invoice_id"], "Completeness", "invoice_id_not_blank", "invoice_id not null/blank", ERROR, "row",
      "MAP 4.2 invoice_id; REC #5", "Identifies invoices and applications.", predicate=_blank("invoice_id")),
    R("DQ_022", T_INV, ["invoice_id"], "Uniqueness", "invoice_id_unique", "invoice_id unique", ERROR, "unique",
      "MAP 4.2 invoice_id", "Unique within source snapshot.", keys=["invoice_id"]),
    R("DQ_023", T_INV, ["customer_id"], "Completeness", "invoice_customer_not_blank", "customer_id not null/blank", ERROR, "row",
      "MAP 4.2 customer_id", "Customer-level AR requires customer.", predicate=_blank("customer_id")),
    R("DQ_024", T_INV, ["invoice_date"], "Completeness", "invoice_date_not_null", "invoice_date not null", ERROR, "row",
      "MAP 4.2 invoice_date; REC #6", "Aging and trend logic depend on it.", predicate="invoice_date IS NULL"),
    R("DQ_025", T_INV, ["invoice_date"], "Validity", "invoice_date_range", f"{MIN_DATE} <= invoice_date <= current_date",
      WARNING, "row", "Assumption 1", "Future/ancient invoice dates are suspicious.",
      predicate=f"invoice_date < DATE'{MIN_DATE}' OR invoice_date > current_date()"),
    R("DQ_026", T_INV, ["due_date"], "Completeness", "due_date_not_null", "due_date not null", WARNING, "row",
      "REC #7 vs MAP 4.2 (Assumption 5)", "Needed for aging; mapping allows null.", predicate="due_date IS NULL"),
    R("DQ_027", T_INV, ["due_date", "invoice_date"], "Business logic", "due_after_invoice", "due_date >= invoice_date",
      WARNING, "row", "MAP 4.2 due_date", "Mapping says flag (not reject).", predicate="due_date < invoice_date"),
    R("DQ_028", T_INV, ["invoice_amount"], "Completeness", "invoice_amount_not_null", "invoice_amount not null", ERROR, "row",
      "MAP 4.2 invoice_amount", "Mandatory financial amount.", predicate="invoice_amount IS NULL"),
    R("DQ_029", T_INV, ["invoice_amount", "invoice_type"], "Business logic", "standard_invoice_non_negative",
      "Non-credit-memo invoice_amount >= 0", ERROR, "row", "REC #8; MAP 4.2 / 5.3", "Standard invoices non-negative.",
      predicate="coalesce(invoice_type, '') <> 'CREDIT_MEMO' AND invoice_amount < 0"),
    R("DQ_030", T_INV, ["invoice_amount", "invoice_type"], "Business logic", "credit_memo_negative",
      "CREDIT_MEMO invoice_amount < 0", ERROR, "row", "REC #9", "Credit memos carry negative signed amounts.",
      predicate="invoice_type = 'CREDIT_MEMO' AND invoice_amount >= 0"),
    R("DQ_031", T_INV, ["tax_amount", "invoice_type"], "Business logic", "tax_non_negative",
      "tax_amount >= 0 unless CREDIT_MEMO", WARNING, "row", "MAP 4.2 tax_amount", "Credit adjustments may be negative.",
      predicate="coalesce(invoice_type, '') <> 'CREDIT_MEMO' AND tax_amount < 0"),
    R("DQ_032", T_INV, ["invoice_type"], "Validity", "invoice_type_domain", "invoice_type in INVOICE, CREDIT_MEMO, DEBIT_MEMO",
      ERROR, "row", "MAP 4.2 invoice_type", "Allowed domain.",
      predicate="invoice_type IS NULL OR invoice_type NOT IN ('INVOICE','CREDIT_MEMO','DEBIT_MEMO')"),
    R("DQ_033", T_INV, ["currency"], "Validity", "currency_iso", "currency not null and ^[A-Z]{3}$", ERROR, "row",
      "MAP 4.2 currency; REC #10", "ISO-style currency code.", predicate="currency IS NULL OR NOT (currency RLIKE '^[A-Z]{3}$')"),
    R("DQ_034", T_INV, ["contract_id"], "Completeness", "invoice_contract_null_rate", "contract_id null rate <= 5%",
      WARNING, "null_rate", "MAP 4.2 contract_id; Assumption 1", "Nullable; monitor billing lineage gaps.",
      col="contract_id", threshold=NULL_RATE_THRESHOLD),
    R("DQ_035", T_INV, ["contract_id"], "Referential", "invoice_contract_fk", "contract_id exists in silver.si_rental_contracts",
      ERROR, "ref", "REC #27; MAP 4.2", "Billing-to-contract lineage.", col="contract_id", parent=T_CON, parent_col="contract_id"),
    R("DQ_036", T_INV, ["customer_id"], "Referential", "invoice_customer_fk", "customer_id exists in silver.si_customer_master",
      ERROR, "ref", "REC #28; MAP 5.4", "Outstanding invoices must map to customers.",
      col="customer_id", parent=T_CUS, parent_col="customer_id"),
    R("DQ_037", T_INV, ["aging_bucket"], "Validity", "aging_bucket_domain", "aging_bucket in 0-30, 31-60, 61-90, 90+",
      WARNING, "row", "MAP 4.2 aging_bucket; REC #35", "Fixed non-overlapping buckets.",
      predicate="aging_bucket IS NULL OR aging_bucket NOT IN ('0-30','31-60','61-90','90+')", requires=["aging_bucket"]),
    R("DQ_038", T_INV, ["days_past_due", "due_date"], "Business logic", "days_past_due_derivation",
      "days_past_due = datediff(current_date, due_date)", WARNING, "row", "MAP 4.2 days_past_due", "Derived field consistency.",
      predicate="due_date IS NOT NULL AND NOT (days_past_due <=> datediff(current_date(), due_date))", requires=["days_past_due"]),
    R("DQ_039", T_INV, ["aging_bucket", "due_date"], "Business logic", "aging_bucket_derivation",
      "aging_bucket matches datediff(current_date, due_date)", WARNING, "row", "REC #36; Assumption 8", "Consistent derivation.",
      predicate=("due_date IS NOT NULL AND NOT (aging_bucket <=> CASE WHEN datediff(current_date(), due_date) <= 30 THEN '0-30' "
                 "WHEN datediff(current_date(), due_date) <= 60 THEN '31-60' WHEN datediff(current_date(), due_date) <= 90 "
                 "THEN '61-90' ELSE '90+' END)"), requires=["aging_bucket"]),
    R("DQ_040", T_INV, ["load_date", "update_date", "source_system", "file_path"], "Table-level", "invoice_metadata",
      "Metadata/lineage columns populated", ERROR, "row", "MAP 4.2 metadata; REC #20", "Lineage & auditability.",
      predicate=_meta_missing()),

    # ---------------- silver.si_cash_receipts ----------------
    R("DQ_041", T_REC, [], "Table-level", "receipts_row_count", "Table contains at least one row", CRITICAL, "row_count",
      "Assumption 11", "Empty receipts load indicates upstream failure."),
    R("DQ_042", T_REC, ["cash_receipt_sk"], "Completeness", "receipt_sk_not_null", "cash_receipt_sk not null", CRITICAL, "row",
      "MAP 4.3 cash_receipt_sk", "Surrogate key must be generated.", predicate="cash_receipt_sk IS NULL"),
    R("DQ_043", T_REC, ["receipt_id"], "Completeness", "receipt_id_not_blank", "receipt_id not null/blank", ERROR, "row",
      "MAP 4.3 receipt_id", "Receipt identifier mandatory.", predicate=_blank("receipt_id")),
    R("DQ_044", T_REC, ["receipt_id"], "Uniqueness", "receipt_id_unique", "receipt_id unique", ERROR, "unique",
      "MAP 4.3 receipt_id; REC #11", "Constraints require uniqueness.", keys=["receipt_id"]),
    R("DQ_045", T_REC, ["customer_id"], "Completeness", "receipt_customer_not_blank", "customer_id not null/blank", ERROR, "row",
      "MAP 4.3 customer_id", "Customer receipt analysis.", predicate=_blank("customer_id")),
    R("DQ_046", T_REC, ["receipt_date"], "Completeness", "receipt_date_not_null", "receipt_date not null", ERROR, "row",
      "MAP 4.3 receipt_date; REC #13", "Days-to-pay depends on it.", predicate="receipt_date IS NULL"),
    R("DQ_047", T_REC, ["receipt_date"], "Validity", "receipt_date_range", f"{MIN_DATE} <= receipt_date <= current_date",
      WARNING, "row", "Assumption 1", "Future receipts are suspicious.",
      predicate=f"receipt_date < DATE'{MIN_DATE}' OR receipt_date > current_date()"),
    R("DQ_048", T_REC, ["payment_amount"], "Validity", "payment_amount_valid", "payment_amount not null and >= 0", ERROR, "row",
      "MAP 4.3 payment_amount; REC #12", "Payment amount must be non-negative.",
      predicate="payment_amount IS NULL OR payment_amount < 0"),
    R("DQ_049", T_REC, ["payment_method"], "Validity", "payment_method_standardized", "payment_method upper(trim()) and not blank if present",
      WARNING, "row", "MAP 4.3 payment_method; Assumption 7", "No approved list supplied.",
      predicate="payment_method IS NOT NULL AND (trim(payment_method) = '' OR payment_method <> upper(trim(payment_method)))"),
    R("DQ_050", T_REC, ["invoice_id"], "Referential", "receipt_invoice_fk", "invoice_id (if present) exists in silver.si_invoices",
      WARNING, "ref", "REC #29; MAP 5.4; Assumption 6", "Applied cash must reference valid invoice; unapplied retained.",
      col="invoice_id", parent=T_INV, parent_col="invoice_id"),
    R("DQ_051", T_REC, ["customer_id"], "Referential", "receipt_customer_fk", "customer_id exists in silver.si_customer_master",
      ERROR, "ref", "DDL 3.3; MAP 5.4", "Customer receipt analysis.", col="customer_id", parent=T_CUS, parent_col="customer_id"),
    R("DQ_052", T_REC, ["receipt_date", "invoice_id"], "Business logic", "receipt_after_invoice",
      "receipt_date >= linked invoice_date", WARNING, "receipt_vs_invoice", "REC #45", "Negative days-to-pay = sequencing issue."),
    R("DQ_053", T_REC, ["match_status"], "Validity", "match_status_domain", "match_status in MATCHED, UNMATCHED, PARTIAL, UNAPPLIED",
      ERROR, "row", "MAP 4.3 match_status", "Derived status domain.",
      predicate="match_status IS NULL OR match_status NOT IN ('MATCHED','UNMATCHED','PARTIAL','UNAPPLIED')", requires=["match_status"]),
    R("DQ_054", T_REC, ["invoice_id", "match_status"], "Business logic", "unapplied_cash_flag",
      "invoice_id null => match_status = UNAPPLIED", WARNING, "row", "REC #44", "Unapplied cash must be flagged, not dropped.",
      predicate="invoice_id IS NULL AND NOT (match_status <=> 'UNAPPLIED')", requires=["match_status"]),
    R("DQ_055", T_REC, ["unapplied_payment_amount", "payment_amount"], "Business logic", "unapplied_amount_range",
      "0 <= unapplied_payment_amount <= payment_amount", ERROR, "row", "MAP 4.3 unapplied_payment_amount", "Derived residual.",
      predicate="unapplied_payment_amount IS NULL OR unapplied_payment_amount < 0 OR unapplied_payment_amount > payment_amount",
      requires=["unapplied_payment_amount"]),
    R("DQ_056", T_REC, ["invoice_id"], "Completeness", "receipt_invoice_null_rate", "invoice_id null rate <= 5%",
      WARNING, "null_rate", "MAP 4.3 invoice_id; Assumption 1", "Monitor unapplied cash volume.",
      col="invoice_id", threshold=NULL_RATE_THRESHOLD),
    R("DQ_057", T_REC, ["load_date", "update_date", "source_system", "file_path"], "Table-level", "receipt_metadata",
      "Metadata/lineage columns populated", ERROR, "row", "MAP 4.3 metadata; REC #20", "Lineage & auditability.",
      predicate=_meta_missing()),

    # ---------------- silver.si_customer_master ----------------
    R("DQ_058", T_CUS, [], "Table-level", "customers_row_count", "Table contains at least one row", CRITICAL, "row_count",
      "Assumption 11", "Empty master breaks all referential checks."),
    R("DQ_059", T_CUS, ["customer_sk"], "Completeness", "customer_sk_not_null", "customer_sk not null", CRITICAL, "row",
      "MAP 4.4 customer_sk", "Surrogate key must be generated.", predicate="customer_sk IS NULL"),
    R("DQ_060", T_CUS, ["customer_id"], "Completeness", "customer_id_not_blank", "customer_id not null/blank", ERROR, "row",
      "MAP 4.4 customer_id; REC #14", "Master key mandatory.", predicate=_blank("customer_id")),
    R("DQ_061", T_CUS, ["customer_id"], "Uniqueness", "customer_id_unique", "customer_id unique", ERROR, "unique",
      "MAP 4.4 customer_id; REC #21", "Deduplicated master required.", keys=["customer_id"]),
    R("DQ_062", T_CUS, ["customer_name"], "Completeness", "customer_name_not_blank", "customer_name not null/blank", ERROR, "row",
      "MAP 4.4 customer_name; REC #14", "Reporting requires name.", predicate=_blank("customer_name")),
    R("DQ_063", T_CUS, ["credit_limit"], "Validity", "credit_limit_non_negative", "credit_limit >= 0", ERROR, "row",
      "MAP 4.4 credit_limit; REC #15", "Credit utilization validity.", predicate="credit_limit < 0"),
    R("DQ_064", T_CUS, ["customer_status"], "Validity", "customer_status_domain",
      "customer_status in ACTIVE, INACTIVE, SUSPENDED, CLOSED", ERROR, "row", "MAP 4.4 customer_status; REC #16",
      "Allowed domain (Assumption 4).",
      predicate="customer_status IS NULL OR customer_status NOT IN ('ACTIVE','INACTIVE','SUSPENDED','CLOSED')"),
    R("DQ_065", T_CUS, ["credit_terms"], "Validity", "credit_terms_standardized", "credit_terms upper(trim()) and not blank if present",
      WARNING, "row", "MAP 4.4 credit_terms; Assumption 7", "No approved code list supplied.",
      predicate="credit_terms IS NOT NULL AND (trim(credit_terms) = '' OR credit_terms <> upper(trim(credit_terms)))"),
    R("DQ_066", T_CUS, ["customer_since"], "Validity", "customer_since_range", f"{MIN_DATE} <= customer_since <= current_date",
      WARNING, "row", "MAP 4.4 customer_since; REC #17", "Tenure reporting.",
      predicate=f"customer_since < DATE'{MIN_DATE}' OR customer_since > current_date()"),
    R("DQ_067", T_CUS, ["over_limit_indicator"], "Validity", "over_limit_indicator_domain", "over_limit_indicator in Y, N",
      ERROR, "row", "MAP 4.4 over_limit_indicator", "Derived flag domain.",
      predicate="over_limit_indicator IS NULL OR over_limit_indicator NOT IN ('Y','N')", requires=["over_limit_indicator"]),
    R("DQ_068", T_CUS, ["load_date", "update_date", "source_system", "file_path"], "Table-level", "customer_metadata",
      "Metadata/lineage columns populated", ERROR, "row", "MAP 4.4 metadata; REC #20", "Lineage & auditability.",
      predicate=_meta_missing()),

    # ---------------- silver.si_branch_employee ----------------
    R("DQ_069", T_EMP, [], "Table-level", "employees_row_count", "Table contains at least one row", CRITICAL, "row_count",
      "Assumption 11", "Empty HR load breaks rep/branch alignment."),
    R("DQ_070", T_EMP, ["branch_employee_sk"], "Completeness", "employee_sk_not_null", "branch_employee_sk not null", CRITICAL,
      "row", "MAP 4.5 branch_employee_sk", "Surrogate key must be generated.", predicate="branch_employee_sk IS NULL"),
    R("DQ_071", T_EMP, ["employee_id", "employee_name"], "Completeness", "employee_id_name_not_blank",
      "employee_id and employee_name not null/blank", ERROR, "row", "MAP 4.5 employee_id, employee_name", "Mandatory fields.",
      predicate=f"{_blank('employee_id')} OR {_blank('employee_name')}"),
    R("DQ_072", T_EMP, ["role"], "Validity", "role_domain", "role in SALES_REP, COLLECTOR", ERROR, "row",
      "MAP 4.5 role; REC #18", "Personnel drill-down classification.", predicate="role IS NULL OR role NOT IN ('SALES_REP','COLLECTOR')"),
    R("DQ_073", T_EMP, ["branch_code"], "Validity", "employee_branch_code_format", "branch_code not null and ^[A-Z0-9_-]+$",
      ERROR, "row", "MAP 4.5 branch_code", "Valid branch code format.",
      predicate="branch_code IS NULL OR NOT (branch_code RLIKE '^[A-Z0-9_-]+$')"),
    R("DQ_074", T_EMP, ["region"], "Completeness", "region_not_blank", "region not null/blank", ERROR, "row",
      "MAP 4.5 region; REC #19", "Region mandatory for rollups.", predicate=_blank("region")),
    R("DQ_075", T_EMP, ["collector_id"], "Validity", "collector_id_valid",
      "collector_id (if present) matches ^[A-Za-z0-9_-]+$ and exists as employee_id", WARNING, "collector_ref",
      "MAP 4.5 collector_id", "Valid employee identifier."),
    R("DQ_076", T_EMP, ["branch_code", "region"], "Business logic", "branch_single_region", "Each branch_code maps to one region",
      WARNING, "multi_value", "REC #50; DDL 3.4", "Common rollup structure.", key="branch_code", value="region"),
    R("DQ_077", T_EMP, ["load_date", "update_date", "source_system", "file_path"], "Table-level", "employee_metadata",
      "Metadata/lineage columns populated", ERROR, "row", "MAP 4.5 metadata; REC #20", "Lineage & auditability.",
      predicate=_meta_missing()),

    # ---------------- operational tables ----------------
    R("DQ_078", ERROR_TABLE, ["severity", "validation_status", "layer_name"], "Validity", "error_table_conformance",
      "severity in HIGH/MEDIUM/LOW and mandatory fields present", WARNING, "row", "MAP 4.6", "Error table integrity.",
      predicate=("severity IS NULL OR severity NOT IN ('HIGH','MEDIUM','LOW') OR layer_name IS NULL OR validation_rule IS NULL "
                 "OR error_description IS NULL OR source_table IS NULL OR detected_timestamp IS NULL")),
    R("DQ_079", AUDIT_TABLE, ["processing_status", "records_read", "records_written", "records_rejected"], "Validity",
      "audit_table_conformance", "status domain, non-negative counts, end >= start", WARNING, "row", "MAP 4.7",
      "Audit table integrity.",
      predicate=("processing_status IS NULL OR processing_status NOT IN ('SUCCESS','FAILED','PARTIAL') OR records_read < 0 "
                 "OR records_written < 0 OR records_rejected < 0 OR processing_time_seconds < 0 "
                 "OR process_end_timestamp < process_start_timestamp OR pipeline_run_id IS NULL OR processed_by IS NULL")),
    R("DQ_080", AUDIT_TABLE, ["records_read", "records_written", "records_rejected"], "Table-level", "audit_count_reconciliation",
      "records_read = records_written + records_rejected for SUCCESS/PARTIAL", WARNING, "row", "MAP 4.7; REC sec. 7",
      "Row-count reconciliation.",
      predicate="processing_status IN ('SUCCESS','PARTIAL') AND records_read <> records_written + records_rejected"),
]


# ----------------------------------------------------------------------------------------------
# Spark SQL generation (query returns violating rows)
# ----------------------------------------------------------------------------------------------
def rule_sql(r: dict) -> str:
    t, k = r["table"], r["kind"]
    if k == "row":
        return f"SELECT *, '{r['id']}' AS dq_rule_id FROM {t} WHERE coalesce(({r['predicate']}), false)"
    if k == "unique":
        keys = ", ".join(r["keys"])
        nn = " AND ".join(f"{c} IS NOT NULL" for c in r["keys"])
        return (f"SELECT * FROM (SELECT t.*, COUNT(*) OVER (PARTITION BY {keys}) AS dq_dup_cnt FROM {t} t WHERE {nn}) "
                f"WHERE dq_dup_cnt > 1")
    if k == "ref":
        c, p, pc = r["col"], r["parent"], r["parent_col"]
        return (f"SELECT c.* FROM (SELECT * FROM {t} WHERE {c} IS NOT NULL AND trim({c}) <> '') c "
                f"LEFT ANTI JOIN (SELECT DISTINCT {pc} AS ref_key FROM {p} WHERE {pc} IS NOT NULL) p ON c.{c} = p.ref_key")
    if k == "multi_value":
        return (f"SELECT * FROM (SELECT t.*, size(collect_set({r['value']}) OVER (PARTITION BY {r['key']})) AS dq_distinct_cnt "
                f"FROM {t} t WHERE {r['key']} IS NOT NULL) WHERE dq_distinct_cnt > 1")
    if k == "null_rate":
        c = r["col"]
        return (f"SELECT COUNT(*) AS total_rows, SUM(CASE WHEN {c} IS NULL OR trim({c}) = '' THEN 1 ELSE 0 END) AS null_rows, "
                f"try_divide(SUM(CASE WHEN {c} IS NULL OR trim({c}) = '' THEN 1 ELSE 0 END), COUNT(*)) AS null_rate "
                f"FROM {t} HAVING try_divide(SUM(CASE WHEN {c} IS NULL OR trim({c}) = '' THEN 1 ELSE 0 END), COUNT(*)) > {r['threshold']}")
    if k == "row_count":
        return f"SELECT COUNT(*) AS row_cnt FROM {t} HAVING COUNT(*) = 0"
    if k == "receipt_vs_invoice":
        return (f"SELECT r.*, i.invoice_date FROM {t} r JOIN (SELECT invoice_id, MIN(invoice_date) AS invoice_date FROM {T_INV} "
                f"GROUP BY invoice_id) i ON r.invoice_id = i.invoice_id WHERE r.receipt_date < i.invoice_date")
    if k == "collector_ref":
        return (f"SELECT c.* FROM (SELECT * FROM {t} WHERE collector_id IS NOT NULL) c "
                f"LEFT JOIN (SELECT DISTINCT employee_id AS ref_key FROM {T_EMP} WHERE employee_id IS NOT NULL) p "
                f"ON c.collector_id = p.ref_key "
                f"WHERE p.ref_key IS NULL OR NOT (c.collector_id RLIKE '^[A-Za-z0-9_-]+$')")
    raise ValueError(f"Unknown rule kind {k}")


# ----------------------------------------------------------------------------------------------
# PySpark evaluation (logically equivalent to rule_sql)
# ----------------------------------------------------------------------------------------------
def _not_blank(c):
    return F.col(c).isNotNull() & (F.trim(F.col(c)) != "")


def violations_df(spark: SparkSession, r: dict, df: DataFrame = None) -> DataFrame:
    """Return violating rows for rule r. `df` defaults to spark.table(r['table'])."""
    df = df if df is not None else spark.table(r["table"])
    k = r["kind"]
    if k == "row":
        return df.where(F.coalesce(F.expr(r["predicate"]), F.lit(False))).withColumn("dq_rule_id", F.lit(r["id"]))
    if k == "unique":
        cond = None
        for c in r["keys"]:
            cond = F.col(c).isNotNull() if cond is None else cond & F.col(c).isNotNull()
        w = Window.partitionBy(*r["keys"])
        return (df.where(cond).withColumn("dq_dup_cnt", F.count(F.lit(1)).over(w)).where(F.col("dq_dup_cnt") > 1))
    if k == "ref":
        parent = (spark.table(r["parent"]).where(F.col(r["parent_col"]).isNotNull())
                  .select(F.col(r["parent_col"]).alias("ref_key")).distinct())
        return df.where(_not_blank(r["col"])).join(parent, F.col(r["col"]) == F.col("ref_key"), "left_anti")
    if k == "multi_value":
        w = Window.partitionBy(r["key"])
        return (df.where(F.col(r["key"]).isNotNull())
                .withColumn("dq_distinct_cnt", F.size(F.collect_set(r["value"]).over(w)))
                .where(F.col("dq_distinct_cnt") > 1))
    if k == "null_rate":
        is_null = F.when(F.col(r["col"]).isNull() | (F.trim(F.col(r["col"])) == ""), 1).otherwise(0)
        agg = df.agg(F.count(F.lit(1)).alias("total_rows"), F.sum(is_null).alias("null_rows"))
        agg = agg.withColumn("null_rate", F.expr("try_divide(null_rows, total_rows)"))
        return agg.where(F.col("null_rate") > F.lit(r["threshold"]))
    if k == "row_count":
        return df.agg(F.count(F.lit(1)).alias("row_cnt")).where(F.col("row_cnt") == 0)
    if k == "receipt_vs_invoice":
        inv = spark.table(T_INV).groupBy("invoice_id").agg(F.min("invoice_date").alias("inv_invoice_date"))
        return (df.join(inv, "invoice_id", "inner").where(F.col("receipt_date") < F.col("inv_invoice_date")))
    if k == "collector_ref":
        emp = (spark.table(T_EMP).where(F.col("employee_id").isNotNull())
               .select(F.col("employee_id").alias("ref_key")).distinct())
        return (df.where(F.col("collector_id").isNotNull())
                .join(emp, F.col("collector_id") == F.col("ref_key"), "left")
                .where(F.col("ref_key").isNull() | ~F.col("collector_id").rlike("^[A-Za-z0-9_-]+$"))
                .drop("ref_key"))
    raise ValueError(f"Unknown rule kind {k}")


# ----------------------------------------------------------------------------------------------
# Orchestration: Critical -> fail, Error -> quarantine to si_error_data, Warning -> audit log
# ----------------------------------------------------------------------------------------------
class DQCriticalFailure(Exception):
    pass


def _error_records(viol: DataFrame, r: dict, run_id: str) -> DataFrame:
    meta = TABLE_META[r["table"]]
    key = meta["key"]
    cols = [c for c in r["columns"] if c in viol.columns]
    rejected = F.to_json(F.struct(*[F.col(c) for c in cols])) if cols else F.lit(None).cast("string")
    bk = F.col(key).cast("string") if key in viol.columns else F.lit(None).cast("string")
    src_sys = F.col("source_system") if "source_system" in viol.columns else F.lit(None).cast("string")
    fpath = F.col("file_path") if "file_path" in viol.columns else F.lit(None).cast("string")
    return viol.select(
        F.xxhash64(F.lit(r["id"]), F.lit(r["table"]), bk, F.lit(run_id)).alias("error_record_sk"),
        F.lit("Silver").alias("layer_name"),
        F.lit(PIPELINE_NAME).alias("pipeline_name"),
        F.lit(meta["source"]).alias("source_table"),
        F.lit(r["table"]).alias("target_table"),
        bk.alias("business_key"),
        F.lit(r["table"]).alias("table_name"),
        F.lit(",".join(r["columns"])).alias("column_name"),
        F.lit(f"{r['id']}: {r['name']}").alias("validation_rule"),
        F.lit("FAILED").alias("validation_status"),
        rejected.alias("rejected_value"),
        F.lit(r["desc"]).alias("error_description"),
        F.lit(r["category"]).alias("error_category"),
        F.lit(ERROR_SEVERITY[r["severity"]]).alias("severity"),
        src_sys.cast("string").alias("source_system"),
        fpath.cast("string").alias("file_path"),
        F.current_timestamp().alias("detected_timestamp"),
        F.current_timestamp().alias("load_timestamp"),
        F.current_timestamp().alias("update_timestamp"),
        F.current_date().alias("load_date"),
        F.current_date().alias("update_date"),
    )


def _write_audit(spark, table, run_id, start_ts, status, read, rejected, msg, trigger_type):
    end_ts = datetime.now()
    meta = TABLE_META[table]
    row = [(run_id, table, meta["source"], start_ts, end_ts, status, int(read), int(read - rejected), int(rejected),
            round((end_ts - start_ts).total_seconds(), 2), trigger_type, (msg or None))]
    schema = ("pipeline_run_id string, target_table string, source_table string, process_start_timestamp timestamp, "
              "process_end_timestamp timestamp, processing_status string, records_read bigint, records_written bigint, "
              "records_rejected bigint, secs double, trigger_type string, error_message string")
    (spark.createDataFrame(row, schema).select(
        F.xxhash64("pipeline_run_id", "target_table").alias("audit_sk"),
        "pipeline_run_id", F.lit("Silver").alias("layer_name"), F.lit(PIPELINE_NAME).alias("pipeline_name"),
        "source_table", "target_table", "process_start_timestamp", "process_end_timestamp", "processing_status",
        "records_read", "records_written", "records_rejected",
        F.col("secs").cast("decimal(18,2)").alias("processing_time_seconds"), "trigger_type",
        F.expr("current_user()").alias("processed_by"), "error_message",
        F.lit(None).cast("string").alias("source_system"),
        F.current_timestamp().alias("load_timestamp"), F.current_timestamp().alias("update_timestamp"),
        F.current_date().alias("load_date"), F.current_date().alias("update_date"))
     .write.format("delta").mode("append").saveAsTable(AUDIT_TABLE))


def validate_table(spark: SparkSession, table: str, df: DataFrame = None, run_id: str = None,
                   trigger_type: str = "SCHEDULED", write_results: bool = True) -> DataFrame:
    """Run all rules for `table`. Returns the clean DataFrame (Error-rule failures removed).
    Use in-pipeline by passing the pre-write DataFrame, or post-load (df=None) to validate the Delta table."""
    run_id = run_id or str(uuid.uuid4())
    start_ts = datetime.now()
    base = df if df is not None else spark.table(table)
    base = base.withColumn("_dq_row_id", F.monotonically_increasing_id()).cache()
    read_cnt = base.count()
    rejected_ids, msgs, status, critical = None, [], "SUCCESS", []

    for r in [x for x in RULES if x["table"] == table]:
        missing = [c for c in r["requires"] if c not in base.columns]
        if missing:
            msgs.append(f"{r['id']}[SKIPPED: missing {','.join(missing)}]")
            continue
        viol = violations_df(spark, r, base)
        n = viol.count()
        if n == 0:
            continue
        msgs.append(f"{r['id']}[{r['severity']}]={n}")
        if r["severity"] == CRITICAL:
            critical.append(r["id"])
        elif r["severity"] == ERROR and "_dq_row_id" in viol.columns:
            if write_results:
                _error_records(viol, r, run_id).write.format("delta").mode("append").saveAsTable(ERROR_TABLE)
            ids = viol.select("_dq_row_id").distinct()
            rejected_ids = ids if rejected_ids is None else rejected_ids.unionByName(ids).distinct()

    rejected_cnt = rejected_ids.count() if rejected_ids is not None else 0
    if critical:
        status = "FAILED"
    elif rejected_cnt > 0:
        status = "PARTIAL"
    if write_results:
        _write_audit(spark, table, run_id, start_ts, status, read_cnt, rejected_cnt, "; ".join(msgs), trigger_type)
    if critical:
        raise DQCriticalFailure(f"{table}: critical DQ rules failed: {', '.join(critical)}")
    clean = base if rejected_ids is None else base.join(rejected_ids, "_dq_row_id", "left_anti")
    return clean.drop("_dq_row_id")


def run_all(spark: SparkSession, trigger_type: str = "SCHEDULED") -> str:
    """Post-load validation of all Silver business tables plus operational tables (shared run id)."""
    run_id = str(uuid.uuid4())
    failures = []
    for t in [T_CUS, T_EMP, T_CON, T_INV, T_REC]:
        try:
            validate_table(spark, t, run_id=run_id, trigger_type=trigger_type)
        except DQCriticalFailure as e:
            failures.append(str(e))
    for t in [ERROR_TABLE, AUDIT_TABLE]:  # Warning-only checks, logged to audit
        validate_table(spark, t, run_id=run_id, trigger_type=trigger_type)
    if failures:
        raise DQCriticalFailure(" | ".join(failures))
    return run_id


def print_rule_book():
    """Section 3 rendering: Description, Rationale, PySpark and Spark SQL per rule."""
    for r in RULES:
        print(f"**[{r['id']}] {r['name']}**  ({r['table']} / {r['category']} / {r['severity']} -> {ACTION[r['severity']]})")
        print(f"- Description: {r['desc']}")
        print(f"- Rationale: {r['rationale']} (Source: {r['source']})")
        print(f"- PySpark: violations_df(spark, RULES_BY_ID['{r['id']}'])"
              + (f"  # df.where(F.expr(\"{r['predicate']}\"))" if r["kind"] == "row" else f"  # kind={r['kind']}"))
        print(f"- Spark SQL:\n{rule_sql(r)};\n")


RULES_BY_ID = {r["id"]: r for r in RULES}
assert len(RULES_BY_ID) == len(RULES), "Rule ids must be unique"

if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    run_all(spark)
