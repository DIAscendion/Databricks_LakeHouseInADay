_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Gold layer physical data model and DDL (Databricks_Gold_Model_Physical_1) for the Rental Revenue-to-Cash domain.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Gold Layer Physical Data Model Review

**Summary of the input.** The Gold physical model defines 20 Delta tables in schema `gold`. They are 9 dimensions, 2 code tables, 4 facts (rental revenue, AR aging, cash application, credit risk), 2 aggregates (executive health score, billing performance), 1 error table and 1 audit table. They are built from 5 Silver tables (`si_rental_contracts`, `si_invoices`, `si_cash_receipts`, `si_customer_master`, `si_branch_employee`). The DDL uses `CREATE TABLE IF NOT EXISTS ... USING DELTA`, VARCHAR/DECIMAL/DATE/TIMESTAMP types, `*_sk BIGINT` id columns, partitioning and Z-ORDER guidance. A later `ALTER TABLE ... ADD COLUMNS` section adds 7 more columns.

**Inputs reviewed:**
1. Gold physical model (`Databricks_Gold_Model_Physical_1.txt`)
2. Gold logical model
3. Conceptual model
4. Reporting requirements (`Input/Rental_Revenue_to_Cash_Reports.txt`)
5. Silver physical model

**Not provided:** the Microsoft Fabric unsupported-features knowledge base file was not in the input list and could not be found in the repository. Section 4.3 is therefore not checked against it.

**Versioning note:** `Databricks_Gold_Model_Physical_1_Reviewer_1.md` already exists in the output folder. It was kept, and this review is saved as `_Reviewer_2`.

---

## 1. Alignment with Conceptual Data Model

### 1.1 ✅ Green Tick: Covered Requirements

| # | Item | Status | Details |
|---|---|---|---|
| 1.1.1 | Entity coverage | ✅ | Date, Region, Branch, Customer, Sales Rep, Collector, Equipment Class, Contract and Invoice are all modelled as dimensions. The four facts are present. Organization Hierarchy is folded into `go_dim_branch` (`organization_hierarchy_name`, `network_level`). |
| 1.1.2 | Fact / Dimension / Code classification | ✅ | `go_dim_*`, `go_fct_*` and `go_code_*` are used consistently. The aging bucket and period type code tables are appropriate. Aggregates are in `go_agg_*`. |
| 1.1.3 | KPI columns | ✅ | These are all present in facts or aggregates: Rental Revenue, Gross/Net Billings, ADR, Revenue per Contract, Credit Memo Rate, Total AR, AR 90+ %, DSO, Best Possible DSO, DSO Trend, Cash Collected, CEI, Avg Days to Pay, % Paid On Time, Unapplied Cash $/%, Credit Utilization %, Customers Over Limit, Suspended w/ Exposure, AR 90+ by Customer, and Health Score. |
| 1.1.4 | Data types and sizes | ✅ | Money is `DECIMAL(18,2)`, ratios are `DECIMAL(18,6)`, and rates and averages are `DECIMAL(18,4)`. Dates are `DATE` and counts are `INT`. |
| 1.1.5 | Aging bucket code table | ✅ | `go_code_aging_bucket` supports the fixed 0-30/31-60/61-90/90+ values. |
| 1.1.6 | Audit and error tables | ✅ | `go_error_data` and `go_process_audit` are present, as the logical model requires. |
| 1.1.7 | Relationships | ✅ | Section 10 documents business-key relationships. Physical joins use stable codes (`branch_code`, `customer_id`, `contract_id`) instead of the logical model's names. |

### 1.2 ❌ Red Tick: Missing Requirements

| # | Item | Status | Details |
|---|---|---|---|
| 1.2.1 | Executive score domain components | ❌ | `go_agg_executive_health_score` has only the composite score and 6 KPIs. Requirement 1 asks for health score by domain (Revenue, AR, Cash App, Credit Risk) and configurable weights. There are no domain score columns, weight columns, or "top aging/risk drivers" structures. |
| 1.2.2 | Grain support: executive score | ❌ | The required unique grain is (Branch, Date, Period Type). `go_agg_executive_health_score` has no `period_type` and no `branch_code`, only names. It has no `region_name`/`branch_name` split that guarantees uniqueness. |
| 1.2.3 | Grain support: AR snapshot | ❌ | The required grain is (Customer, Invoice, Snapshot Date), and drill-through goes to the invoice list. `go_fct_ar_aging` has no `invoice_id`, `invoice_date`, `due_date`, `days_past_due` or `sales_rep` column. |
| 1.2.4 | Grain support: revenue | ❌ | The required grain is (Branch, Date, Sales Rep, Equipment Class). `go_fct_rental_revenue` is at contract/customer level, per the model's own §6. Section 6 and the §4.4 aggregates do not match the requirement. The fact stores `equipment_class` (code) but not `equipment_class_code` as per `go_dim_equipment_class`. |
| 1.2.5 | Grain support: cash application | ❌ | The unique grain is Receipt ID, and partial application and multiple applications must be tracked. `go_fct_cash_application` has no `receipt_id`. It has no applied-amount-per-invoice column and no `days_to_pay` per record. |
| 1.2.6 | Region / hierarchy for drill and security | ❌ | `go_fct_ar_aging`, `go_fct_cash_application` and `go_fct_credit_risk` have no `region_name`. The requirements need Region → Branch → Collector/Customer drill and region-level security. Executive and billing aggregates have no `branch_code`/`region` key columns. |
| 1.2.7 | Slicers | ❌ | Customer status is not on `go_fct_ar_aging` or `go_fct_cash_application`. Equipment class is not on any AR or cash fact. Both are required slicers. |
| 1.2.8 | Fact-to-Date links | ❌ | Requirement says all facts link to Date. §10/§11 omit Date relationships for `go_fct_ar_aging`, `go_fct_cash_application`, `go_fct_credit_risk` and both aggregates. `go_dim_region` and `go_dim_equipment_class` are also not linked to any fact in §10/§11. |
| 1.2.9 | SCD Type 2 attributes | ❌ | The logical model says `go_dim_branch`, `go_dim_customer` and `go_dim_contract` are SCD Type 2. §6 says "one row per ... version". No `effective_start_date`, `effective_end_date` or `is_current` columns exist in any DDL. |
| 1.2.10 | Surrogate keys unused in relationships | ❌ | Every table has a `*_sk`. No fact or aggregate carries a dimension `*_sk` column. All joins use natural keys or names, so the SKs have no role. |
| 1.2.11 | Credit memo representation | ❌ | The constraint "credit memos negative, invoices non-negative" has no column support. There is no `invoice_type`/credit-memo indicator on the fact, and `credit_memo_amount` sign is undefined. |
| 1.2.12 | Health score range / non-null constraints | ❌ | The 0-100 range, active-branch rule and reconciliation checks are listed only in prose (§4.5). There is no DQ flag/status column, and the §4.5 rules do not cover the 0-100 health score range. |

---

## 2. Source Data Structure Compatibility

### 2.1 ✅ Green Tick: Aligned Elements

| # | Item | Status | Details |
|---|---|---|---|
| 2.1.1 | Silver tables used as sources | ✅ | The 5 business tables (`si_rental_contracts`, `si_invoices`, `si_cash_receipts`, `si_customer_master`, `si_branch_employee`) are the Gold inputs. |
| 2.1.2 | Core attribute carry-over | ✅ | `invoice_id`, `contract_id`, `customer_id`, `invoice_date`, `due_date`, `invoice_amount`, `tax_amount`, `invoice_type`, `currency`, `daily_rate`, `contract_*_date`, `contract_status`, `credit_terms`, `credit_limit`, `customer_status`, `payment_amount`, `payment_method`, `branch_code` and `collector_id` are all in Gold. `customer_since` is carried as `customer_since_date`. |
| 2.1.3 | Joins | ✅ | The §4.3 Silver joins are consistent with the Silver physical join list (`customer_id`, `sales_rep_id = employee_id`, `contract_id`, `invoice_id`). |
| 2.1.4 | Metadata columns | ✅ | `load_date`, `update_date` and `source_system` are in every business table. `go_process_audit` carries `load_date`, `update_date` and `source_system`; `go_error_data` has `source_system`, `load_date` and `update_date`. |
| 2.1.5 | Transformations described | ✅ | Aging bucket derivation, divide-by-zero guard, payment > invoice flag and net = gross − credit reconciliation are documented in §4.2/§4.5. |
| 2.1.6 | Silver-to-Gold audit structure | ✅ | Gold has its own audit and error tables. Silver's shared `si_error_data`/`si_pipeline_audit` remain available. |

### 2.2 ❌ Red Tick: Misaligned or Missing Elements

| # | Item | Status | Details |
|---|---|---|---|
| 2.2.1 | Wrong Silver source names | ❌ | §4.1 lists `silver.si_data_quality_errors` and `silver.si_process_audit`. The Silver model defines `silver.si_error_data` and `silver.si_pipeline_audit`. The names do not exist in Silver. |
| 2.2.2 | `receipt_id` not carried | ❌ | `silver.si_cash_receipts.receipt_id` and the Silver id (`cash_receipt_sk`) are not in `go_fct_cash_application`. Receipt-level uniqueness and reconciliation cannot be done. `receipt_date` is renamed `payment_date` without a stated mapping. |
| 2.2.3 | `si_branch_employee` columns dropped | ❌ | `role`, `effective_date` and `employee_id` (renamed `sales_rep_id`/`collector_id`) are not carried. `role` is needed to split sales reps from collectors, and `effective_date` is needed for "at time of contract/assignment". |
| 2.2.4 | No Silver source for several Gold columns | ❌ | There is no Silver column for `branch_name`, `branch_status`, `organization_hierarchy_name`, `network_level`, `region_name` (Silver has `region`), `equipment_class_name`, `collector_name` or `sales_rep_name` (Silver has `employee_name`). `silver.si_customer_master` has no collector or sales rep. §9 item 7 acknowledges that branch/region names are assumed standardized, but no reference or mapping table is defined. |
| 2.2.5 | Credit memo, billed days, credit sales | ❌ | Silver has no credit memo column, no `billed_rental_days`, and no "credit sales" or "beginning AR" input. Gold depends on these for credit memo amount, ADR, DSO and CEI. §9 item 5 says they are "derived from invoice_type", but the derivation rules are not given. |
| 2.2.6 | Ambiguous `branch_code` join | ❌ | §4.3 joins `si_rental_contracts.branch_code` to `si_branch_employee.branch_code`. That is many employees per branch, which would multiply contract rows. Branch attributes need a distinct branch source. |
| 2.2.7 | Lineage columns dropped | ❌ | Silver `file_path`, `file_modification_time`, `load_timestamp` and `update_timestamp` are not in Gold. §3 says lineage fields are "included where useful", but none are. |
| 2.2.8 | Date type mismatch | ❌ | Silver `load_date`/`update_date` are `DATE`. Gold uses `TIMESTAMP`. The conversion is not declared. |
| 2.2.9 | Audit count type mismatch | ❌ | `go_process_audit.records_*_count` are `DECIMAL(18,0)` in §5.5. Logical model and Silver audit use `BIGINT`. |
| 2.2.10 | Column placed only in ALTER | ❌ | `billed_rental_days`, `over_limit_indicator`, `invoice_status`, `unapplied_payment_count`, `risk_category`, `run_id` and `source_record_id` are added in §5.7 although the tables are created in the same script. They are needed for ADR, exposure and run traceability and belong in the CREATE statements. The ALTERs also fail when re-run, because `ADD COLUMNS` is not idempotent. |
| 2.2.11 | Gold-only dimension attributes | ❌ | `go_dim_contract.open_contract_count`/`open_contract_value` and `go_dim_invoice.invoice_amount`/`tax_amount`/`aging_bucket`/`days_past_due`/`match_status` are time-varying measures held in dimensions. They have no rule for which snapshot they refer to. |
| 2.2.12 | PySpark compatibility of calculations | ❌ | Formulas for DSO, CEI, health score weights, `trend_value`, `dso_trend` and `best_possible_dso` are not specified. Their PySpark compatibility cannot be verified. Only the denominators-non-zero rule is stated. |

---

## 3. Best Practices Assessment

### 3.1 ✅ Green Tick: Adherence to Best Practices

| # | Item | Status | Details |
|---|---|---|---|
| 3.1.1 | Naming | ✅ | `go_` prefix and `dim`/`fct`/`code`/`agg` infixes, with snake_case columns, are used throughout. |
| 3.1.2 | Idempotent DDL | ✅ | `CREATE TABLE IF NOT EXISTS` is used for all tables. |
| 3.1.3 | No unsupported constraints | ✅ | No PK, FK, UNIQUE, CHECK, identity or `TEXT`/`DATETIME` types. |
| 3.1.4 | Delta format | ✅ | `USING DELTA` on every table. |
| 3.1.5 | Indexing strategy | ✅ | `OPTIMIZE ... ZORDER BY` guidance is given for all dimensions, facts and aggregates. Z-order columns are not partition columns. |
| 3.1.6 | Normalization / star model | ✅ | Star schema with conformed dimensions, aggregates over facts and code tables. |
| 3.1.7 | Retention and archiving | ✅ | Per-category retention (7y / 5y / 2y) is defined. |
| 3.1.8 | Audit and error tables | ✅ | Both exist with status, severity and counts. |
| 3.1.9 | Metadata columns | ✅ | `load_date`, `update_date` and `source_system` are on all business tables. |

### 3.2 ❌ Red Tick: Deviations from Best Practices

| # | Item | Status | Details |
|---|---|---|---|
| 3.2.1 | Over-partitioning | ❌ | `go_dim_invoice` is partitioned by `invoice_date`, which is high cardinality for a dimension. `go_dim_branch` (`branch_status`), `go_dim_customer` (`customer_status`), `go_dim_sales_rep` and `go_dim_collector` (`region_name`) are small tables partitioned by mutable values, so `MERGE` updates will move rows across partitions. Daily-partitioned facts risk small files. Use unpartitioned tables or liquid clustering. |
| 3.2.2 | Date dimension grain | ❌ | `go_dim_date` is one row per (`reporting_date`, `period_type`). Facts join on `reporting_date` only, so a join returns several rows per date and inflates the facts. |
| 3.2.3 | Missing audit/DQ columns | ❌ | `go_error_data` and `go_process_audit` lack `source_record_id` and `run_id` until the ALTERs (see 2.2.10). |
| 3.2.5 | Redundant columns | ❌ | `go_fct_ar_aging.ar_aging_by_bucket` repeats `total_ar_outstanding` split by the `aging_bucket` row. Names (`branch_name`, `customer_name`, `collector_name`) are duplicated from dimensions into every fact, and `go_dim_contract` repeats customer, branch and sales rep names. |
| 3.2.6 | VARCHAR(n) use | ❌ | Silver uses `STRING`. In Delta, `VARCHAR(n)` is stored as string with length enforcement, so over-length values fail writes. Use `STRING`, or keep `VARCHAR` and justify the lengths. |
| 3.2.7 | No table properties/comments | ❌ | No `COMMENT`, `TBLPROPERTIES` (e.g. `delta.autoOptimize.*`, `delta.enableChangeDataFeed`, `delta.columnMapping.mode`) or column comments. No PII tags are carried over from the logical model. |
| 3.2.8 | Missing OPTIMIZE statements | ❌ | §6 lists Z-order columns for `go_error_data` and `go_process_audit`, and the code tables have none. No statements are given. |
| 3.2.9 | Inconsistent grain statements | ❌ | `go_fct_rental_revenue` grain text ("reporting date/contract level") does not match the unique grain in the requirements or the BI aggregation (see 1.2.4). |
| 3.2.10 | Unknown member / default rows | ❌ | No handling of unmatched keys (e.g. `-1` SK rows) for facts that cannot find a dimension row. |
| 3.2.11 | Logical vs physical naming | ❌ | Logical names use `Go_` (capital). Physical uses lower case. Physical `go_dim_contract` has `equipment_class` and `equipment_class_name`, which are two overlapping columns. |

---

## 4. DDL Script Compatibility

### 4.1 Microsoft Fabric Compatibility

| # | Check | Status | Details |
|---|---|---|---|
| 4.1.1 | Delta tables (`USING DELTA`) | ✅ | Supported in Fabric Lakehouse Spark. |
| 4.1.2 | `gold.` schema-qualified names | ✅ | Schema-enabled Lakehouses accept them. The `gold` schema must exist, and no `CREATE SCHEMA` is in the script. |
| 4.1.3 | `PARTITIONED BY` | ✅ | Supported syntax. See 3.2.1 for the design concern. |
| 4.1.4 | `OPTIMIZE ... ZORDER BY` | ✅ | Supported in Fabric Spark. These are guidance statements, not part of the DDL. |
| 4.1.5 | `VARCHAR(n)` | ❌ | `go_dim_*`, `go_fct_*` and all other tables. Supported as a Spark SQL type, but Fabric Warehouse/SQL analytics endpoints surface these as `varchar(n)`. Length enforcement on Delta write is a risk, so `STRING` is preferred (see 3.2.6). |
| 4.1.6 | `ALTER TABLE ... ADD COLUMNS` | ❌ | §5.7, 7 statements. These are supported but not idempotent, and they are not guarded for re-runs. |
| 4.1.7 | `schema` missing from script | ❌ | No `CREATE SCHEMA IF NOT EXISTS gold` before the first CREATE. |

### 4.2 Spark Compatibility

| # | Check | Status | Details |
|---|---|---|---|
| 4.2.1 | Data types | ✅ | `BIGINT`, `INT`, `DATE`, `TIMESTAMP` and `DECIMAL(p,s)` are valid. No `TEXT`, `DATETIME` or `IDENTITY`. |
| 4.2.2 | Constraints | ✅ | None present. |
| 4.2.3 | `CREATE TABLE IF NOT EXISTS ... USING DELTA PARTITIONED BY` clause order | ✅ | Valid. |
| 4.2.4 | `DECIMAL(18,0)` for counts | ❌ | `go_process_audit.records_read_count`, `records_written_count`, `records_rejected_count`. Valid, but counts should be `BIGINT` (see 2.2.9). |
| 4.2.5 | `ALTER TABLE ADD COLUMNS` with `VARCHAR` | ✅ | Valid Spark SQL. |
| 4.2.6 | Partition by high-cardinality / mutable columns | ❌ | `go_dim_invoice (invoice_date)`, `go_dim_customer (customer_status)`, `go_dim_branch (branch_status)`. Valid syntax but poor performance (see 3.2.1). |

### 4.3 Used Any Unsupported Features in Microsoft Fabric

The knowledge base file of unsupported Microsoft Fabric features was not supplied and could not be found in the repository, so nothing below is cited against it.

| # | Feature | Used in DDL? | Status | Details |
|---|---|---|---|---|
| 4.3.1 | Primary / Foreign / Unique constraints | No | ✅ | Not used in any DDL. |
| 4.3.2 | `IDENTITY` / generated columns | No | ✅ | Surrogate keys are plain `BIGINT`. |
| 4.3.3 | `TEXT` / `DATETIME` types | No | ✅ | Not used. |
| 4.3.4 | Traditional indexes | No | ✅ | Replaced by Z-ORDER guidance. |
| 4.3.5 | Databricks-only features (Unity Catalog three-part names, liquid clustering, `CLUSTER BY`) | No | ✅ | Not used; two-part `gold.table` names only. |
| 4.3.6 | Anything listed in the knowledge base | Not verified | ❌ | The knowledge base file is missing, so this check cannot be completed. Re-run once it is supplied. |

---

## 5. Identified Issues and Recommendations

| # | Issue | Recommendation |
|---|---|---|
| 5.1 | Grain does not match the requirements for revenue, AR aging, cash application and executive score (1.2.2 to 1.2.5) | Redesign to the required grains: revenue (Branch, Date, Sales Rep, Equipment Class); AR (Customer, Invoice, Snapshot Date), adding `invoice_id`, `due_date`, `days_past_due`; cash application (`receipt_id` plus invoice application); executive score (Branch, Date, Period Type), adding `period_type` and `branch_code`. |
| 5.2 | Executive aggregate lacks domain scores and weights (1.2.1) | Add `revenue_score`, `ar_score`, `cash_app_score`, `credit_risk_score`, a weight configuration table (or weight columns) and a top-driver structure. Add a 0-100 validation rule in `go_error_data`. |
| 5.3 | SKs not used in relationships (1.2.10) | Add `dim_*_sk` columns to facts and aggregates, populate them via surrogate-key lookup, and seed `-1` unknown-member rows. |
| 5.4 | SCD2 columns missing (1.2.9) | Add `effective_start_date`, `effective_end_date` and `is_current` to `go_dim_branch`, `go_dim_customer` and `go_dim_contract`, or change the logical SCD type. |
| 5.5 | Date dimension grain (3.2.2) | Make `go_dim_date` one row per `reporting_date`, with period attributes as columns. Keep `go_code_period_type` for the grain value, and add `period_type` to the facts that need it. |
| 5.6 | Region, hierarchy, slicers and security attributes missing on facts (1.2.6, 1.2.7) | Add `region_name`/`branch_code`, `customer_status`, `equipment_class_code` and `sales_rep_id` where facts need them, and document the row-level-security attribute. |
| 5.7 | Source mapping gaps (2.2.1 to 2.2.6) | Correct §4.1 Silver names to `si_error_data`/`si_pipeline_audit`. Define sources or reference tables for branch name/status/hierarchy, region, equipment class and collector/sales rep names. Specify the credit memo and billed-days derivations. Carry `receipt_id`, `role` and `effective_date`. Replace the branch join with a branch reference. |
| 5.8 | Source lineage / types (2.2.7 to 2.2.9) | Carry Silver lineage columns (or document why not). Make `load_date`/`update_date` types consistent with Silver. Use `BIGINT` for audit counts. |
| 5.9 | ALTER-only columns (2.2.10) | Move `billed_rental_days`, `over_limit_indicator`, `invoice_status`, `unapplied_payment_count`, `risk_category`, `run_id` and `source_record_id` into the CREATE statements. Keep §5.7 for genuine future changes. |
| 5.10 | Partitioning (3.2.1) | Remove partitioning from small dimensions and from `go_dim_invoice`. Use `OPTIMIZE ZORDER` (or liquid clustering where the platform allows). Keep date partitioning only for large facts, and size it by volume. |
| 5.11 | Dimension measures (2.2.11, 3.2.5) | Move `open_contract_*` and invoice amounts to facts/snapshots. Remove `ar_aging_by_bucket` and the duplicated names. |
| 5.12 | Formulas undefined (2.2.12) | Document the DSO, CEI, best possible DSO, trends and score formulas with the PySpark expressions and zero-denominator handling. |
| 5.13 | Audit and error tables (3.2.3) | Add `run_id` to the audit table and `source_record_id` to the error table at creation. |
| 5.14 | Type and table-property hygiene (3.2.6 to 3.2.8) | Use `STRING` instead of `VARCHAR(n)` (or justify lengths). Add `COMMENT`/`TBLPROPERTIES` and PII tags. Add the missing OPTIMIZE statements and `CREATE SCHEMA IF NOT EXISTS gold`. |
| 5.15 | Relationship coverage (1.2.8) | Complete §10/§11 with all fact-to-date, region and equipment class links. |
| 5.16 | Fabric knowledge base (4.3.6) | Supply the unsupported-features knowledge base file and re-run this review. |

---

## 6. API Cost
```
apiCost: 0.000000
```
