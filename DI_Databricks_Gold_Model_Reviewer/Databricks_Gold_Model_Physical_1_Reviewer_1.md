_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Gold layer physical data model and DDL (Rental Revenue-to-Cash) for completeness, correctness, best practices, and Microsoft Fabric / Spark compatibility.
## *Version*: 1
## *Updated on*:
_____________________________________________

## Summary of Input
The reviewed file `Databricks_Gold_Model_Physical_1.txt` defines 20 Delta tables in schema `gold`. These are 9 dimensions, 2 code tables, 4 facts (rental revenue, AR aging, cash application, credit risk), 2 aggregates (executive health score, billing performance), 1 error table and 1 audit table. It also defines 7 `ALTER TABLE ... ADD COLUMNS` statements. The tables are built from five Silver tables (`si_rental_contracts`, `si_invoices`, `si_cash_receipts`, `si_customer_master`, `si_branch_employee`). The review compared them with:
- the Gold logical model
- the conceptual model
- the reporting requirements (5 reports)
- the Silver physical model

**Input limitation:** the Microsoft Fabric unsupported-features knowledge base file was not among the listed input paths. A repository code search also did not find it. Section 4.3 therefore cannot cite it. The checks there use general Fabric/Spark knowledge and are marked as such.

## 1. Alignment with Conceptual Data Model

### 1.1 ✅ Green Tick: Covered Requirements
| # | Item | Status | Details |
|---|---|---|---|
| 1.1.1 | Entity coverage | ✅ | All conceptual entities have a Gold table: Region, Branch, Date, Customer, Sales Rep, Collector, Equipment Class, Contract, Invoice, plus the 4 facts. Organization Hierarchy is carried as `organization_hierarchy_name` and `network_level` on `go_dim_branch`. |
| 1.1.2 | Fact/Dim/Code classification | ✅ | The four facts match the conceptual facts. Aging bucket and period type are correctly modelled as code tables. Two aggregates cover the executive scorecard and billing performance. |
| 1.1.3 | Logical attribute coverage | ✅ | Every logical column is present in the physical DDL, with `*_sk` ids and business keys added. Data types match the logical model (DECIMAL(18,2/4/6), DATE, TIMESTAMP, INT). |
| 1.1.4 | KPI columns | ✅ | Present: health score, rental revenue, DSO, AR 90+ %, CEI, unapplied cash % and $, gross/net billings, ADR, revenue per contract, credit memo rate, total AR, AR by bucket, best possible DSO, DSO trend, cash collected, average days to pay, % paid on time, credit utilization, customers over limit (count/$), AR 90+ by customer, suspended with exposure. |
| 1.1.5 | Customer-level credit data | ✅ | `go_dim_customer` has credit_limit, customer_since_date and customer_status. `go_fct_credit_risk` has open_contract_count and open_contract_value. |
| 1.1.6 | Audit and error tables | ✅ | `go_process_audit` and `go_error_data` exist and cover Gold. |
| 1.1.7 | Aging bucket code table | ✅ | `go_code_aging_bucket` is the governed list of 0-30/31-60/61-90/90+ (per the logical model and requirements). |

### 1.2 ❌ Red Tick: Missing Requirements
| # | Item | Status | Details |
|---|---|---|---|
| 1.2.1 | Region slice/drill missing on facts | ❌ | `go_fct_ar_aging`, `go_fct_cash_application` and `go_fct_credit_risk` have no `region_name`. The Region → Branch → Collector/Customer drill paths and regional security need region on every fact. `go_fct_rental_revenue` has it. |
| 1.2.2 | AR grain keys missing | ❌ | The AR report requires uniqueness on (Customer, Invoice, Snapshot Date) and invoice-level drill-through (invoice_id, due date, amount, days past due). `go_fct_ar_aging` has no `invoice_id`, `due_date` or invoice amount. |
| 1.2.3 | Cash application grain key missing | ❌ | The uniqueness grain is Receipt ID. `go_fct_cash_application` has no `receipt_id`, and no `days_to_pay` (required Cash Receipt attribute). |
| 1.2.4 | Sales rep missing on AR | ❌ | The AR report lists sales rep as a data attribute. `go_fct_ar_aging` has no `sales_rep_id` or `sales_rep_name`. |
| 1.2.5 | Executive scorecard domain scores missing | ❌ | The requirement is a health score by domain (Revenue, AR, Cash App, Credit Risk) plus weights/roll-up validation. `go_agg_executive_health_score` has only the overall score. It has no domain score columns, weight columns or target bands. It also has no `period_type`, although the uniqueness grain is (Branch, Date, Period Type). |
| 1.2.6 | Date dimension lacks period attributes | ❌ | `go_dim_date` has no day/week/month/quarter or year attributes. It has only one `reporting_period` string. Week → Month → Quarter drill-up is not supported. `go_agg_billing_performance` and the facts also carry no `period_type`. |
| 1.2.7 | Credit memo sign / type not carried | ❌ | The rule is credit memos negative and invoices non-negative. `go_fct_rental_revenue` has no invoice type or sign indicator (only aggregates). No documented derivation exists from `silver.si_invoices.invoice_type`. |
| 1.2.8 | SCD Type 2 attributes missing | ❌ | The logical model assigns SCD Type 2 to `go_dim_branch`, `go_dim_customer` and `go_dim_contract`. The DDL has no `effective_start_date`, `effective_end_date` or `is_current`. Section 6 says "One row per ... version", which cannot be implemented. |
| 1.2.9 | Branch/region dimension keys | ❌ | `go_dim_region` has no business key beyond `region_name`. Facts and aggregates join to dimensions by name or code, never by `*_sk`. The aggregates (`go_agg_*`) carry only names (branch_name, sales_rep_name), not codes or SKs. |
| 1.2.10 | Customer–collector/sales rep assignment | ❌ | `go_dim_customer` carries collector_id and sales_rep_id (Collector 1-M Customer), but the Silver customer master has no such columns. See 2.2.1. |
| 1.2.11 | Status code tables | ❌ | The only controlled lists modelled are aging bucket and period type. Match status (applied/unapplied) and contract status (open/closed) are free text. |

## 2. Source Data Structure Compatibility

### 2.1 ✅ Green Tick: Aligned Elements
| # | Item | Status | Details |
|---|---|---|---|
| 2.1.1 | Contract attributes | ✅ | contract_id, customer_id, branch_code, sales_rep_id, equipment_class, start/end dates, status and daily_rate from `si_rental_contracts` are all in `go_dim_contract`. |
| 2.1.2 | Invoice attributes | ✅ | invoice_id, contract_id, customer_id, invoice_date, due_date, invoice_amount, tax_amount, invoice_type and currency are in `go_dim_invoice`. |
| 2.1.3 | Receipt attributes | ✅ | payment_method, payment_amount, invoice_id and customer_id are in `go_fct_cash_application`. `receipt_date` is carried as `payment_date`. |
| 2.1.4 | Customer master attributes | ✅ | customer_name, credit_terms, credit_limit, customer_status and customer_since (as `customer_since_date`) are in `go_dim_customer`. |
| 2.1.5 | Data types | ✅ | Monetary DECIMAL(18,2) and dates are consistent with Silver. |
| 2.1.6 | Joins | ✅ | The documented join keys exist in the Silver physical model (customer_id, contract_id, invoice_id, branch_code, sales_rep_id = employee_id). |
| 2.1.7 | PySpark-safe rule intent | ✅ | Divide-by-zero protection, aging derivation, and payment ≤ invoice checks are documented as filters (section 4.5). |

### 2.2 ❌ Red Tick: Misaligned or Missing Elements
| # | Item | Status | Details |
|---|---|---|---|
| 2.2.1 | Collector/sales rep on customer has no Silver source | ❌ | `go_dim_customer.collector_id/collector_name/sales_rep_id/sales_rep_name` have no source. `silver.si_customer_master` has none of them. `si_branch_employee.collector_id` is per employee. No Silver mapping from customer to collector exists, so the lineage is undefined. |
| 2.2.2 | Wrong Silver table names | ❌ | Section 4.1 lists `silver.si_data_quality_errors` and `silver.si_process_audit`. The Silver model defines `silver.si_error_data` and `silver.si_pipeline_audit`. |
| 2.2.3 | Attributes with no Silver source | ❌ | `branch_name`, `branch_status`, `organization_hierarchy_name`, `network_level`, `equipment_class_name`, `collector_name` and `open_contract_count/value` do not exist in Silver. They are assumed "standardized during Gold conformance" (Assumption 7) with no reference or mapping table. |
| 2.2.4 | Credit memo derivation | ❌ | `credit_memo_amount`, `gross_billings` and `net_billings` have no mapping rule (Assumption 5 states they are "not explicitly present"). The rule (negative credit memos by `invoice_type`, with `invoice_type` values unspecified) is not written down. |
| 2.2.5 | Metadata type mismatch with Silver | ❌ | Silver `load_date` / `update_date` are DATE. Gold uses TIMESTAMP in all tables, and the Gold logical model also says timestamp. This is a cross-layer inconsistency (and the logical description "Date the record was loaded" suggests DATE). |
| 2.2.6 | Silver lineage not carried | ❌ | Silver carries `receipt_id`, `file_path` and `file_modification_time`. Gold keeps none of them and no `source_record_id` (added only via ALTER on the error table), which weakens reconciliation back to Silver. |
| 2.2.7 | Silver columns not used | ❌ | `si_branch_employee.role` and `effective_date` are not used. Role would be needed to separate sales reps from collectors. The Gold DDL does not state how `go_dim_sales_rep` and `go_dim_collector` are filtered from the employee table. |
| 2.2.8 | Audit/error count types | ❌ | The audit counts are DECIMAL(18,0), but the logical model and Silver use BIGINT. The audit table's `records_*` fields should be BIGINT. |
| 2.2.9 | Calculation logic not specified | ❌ | The DDL and notes do not include formulas for DSO, Best Possible DSO, CEI, health score weights, or the trend measures. Required PySpark-compatible logic (reporting rules for DSO, CEI, AR 90+ %) is only referenced as "aggregations" in section 4.4. |

## 3. Best Practices Assessment

### 3.1 ✅ Green Tick: Adherence to Best Practices
| # | Item | Status | Details |
|---|---|---|---|
| 3.1.1 | Metadata columns | ✅ | `load_date`, `update_date` and `source_system` are in all tables except the audit table (see 3.2.7). |
| 3.1.2 | Audit and error tables | ✅ | `go_process_audit` records pipeline, status, counts, start/end and duration. `go_error_data` records rule, severity, status and corrective action. |
| 3.1.3 | Naming conventions | ✅ | Lower snake_case; consistent `go_dim_/go_fct_/go_code_/go_agg_` prefixes; `*_sk` surrogate id naming. |
| 3.1.4 | Idempotent DDL | ✅ | `CREATE TABLE IF NOT EXISTS ... USING DELTA` throughout. |
| 3.1.5 | No unsupported constraints | ✅ | No PK, FK, UNIQUE, CHECK or IDENTITY clauses. |
| 3.1.6 | Indexing strategy | ✅ | `OPTIMIZE ... ZORDER BY` guidance is given for each table in place of RDBMS indexes. |
| 3.1.7 | Normalization / star schema | ✅ | Dimensions, facts and code tables are separated. Aggregates are separate from facts. |
| 3.1.8 | Retention and archiving | ✅ | Retention periods are documented per table category. |

### 3.2 ❌ Red Tick: Deviations from Best Practices
| # | Item | Status | Details |
|---|---|---|---|
| 3.2.1 | Over-partitioning of dimensions | ❌ | Small dimensions are partitioned on low-value or mutable columns: `go_dim_branch` (branch_status), `go_dim_customer` (customer_status), `go_dim_sales_rep` and `go_dim_collector` (region_name), `go_dim_date` (period_type), `go_dim_contract` (contract_status). Small tables should be unpartitioned. Partitioning on an updatable status column forces row movement on every SCD update. |
| 3.2.2 | High-cardinality partition | ❌ | `go_dim_invoice` is `PARTITIONED BY (invoice_date)`, which creates one partition per day with small files. |
| 3.2.3 | Daily-date partitioned facts/aggregates | ❌ | `go_fct_*` and `go_agg_*` partition on daily `reporting_date` / `snapshot_date`. Where volumes are modest this creates small files. Use liquid clustering or month-level partitioning instead. |
| 3.2.4 | Mutable partition columns on operational tables | ❌ | `go_error_data` is partitioned by `error_status`, and `go_process_audit` by `process_status`. Both values change over time. Better: partition or cluster by date. |
| 3.2.5 | Surrogate keys not populated or guaranteed | ❌ | `*_sk` are plain BIGINT with no generation or uniqueness approach documented in DDL. Non-unique SKs are possible. The notes say to use MERGE, but no key-generation approach (e.g. hash or sequence) is specified. |
| 3.2.6 | Denormalization / redundancy | ❌ | Attributes such as branch_name, region_name, customer_name and sales_rep_name are repeated in facts and in `go_dim_contract`, `go_dim_invoice` and `go_dim_customer`. Facts do not carry `*_sk` references to dimensions, so conformity is by name and can drift (see 1.2.9). Dimensions also hold measures (`go_dim_invoice.invoice_amount`, `go_dim_contract.open_contract_value`). |
| 3.2.7 | Audit table missing standard column | ❌ | `go_process_audit` has `source_system` in its column list, but there is no `run_id` in the base DDL (it is added via ALTER in 5.7), and there is no link from error records to the run. |
| 3.2.8 | ALTER instead of base DDL | ❌ | Section 5.7 adds columns (`over_limit_indicator`, `invoice_status`, `billed_rental_days`, `unapplied_payment_count`, `risk_category`, `run_id`, `source_record_id`) that belong in the base CREATE statements. `billed_rental_days` is needed for ADR. |
| 3.2.9 | Missing schema creation | ❌ | No `CREATE SCHEMA IF NOT EXISTS gold` statement, although all DDL is `gold.`-qualified. |
| 3.2.10 | No table properties | ❌ | No `TBLPROPERTIES` (e.g. `delta.autoOptimize.optimizeWrite`, `delta.enableChangeDataFeed`, retention settings). Retention periods in section 7 are not tied to any property. |
| 3.2.11 | No column comments | ❌ | No `COMMENT` clauses for column or table documentation. PII classification from the logical model (customer, sales rep and collector names) is not carried into the physical model (e.g. tags). |
| 3.2.12 | Deliverable format | ❌ | The physical model is stored as `.txt` while containing Markdown. It also references the wrong output URL (the Silver folder) at the end. |

## 4. DDL Script Compatibility

### 4.1 Microsoft Fabric Compatibility
| # | Check | Status | Details |
|---|---|---|---|
| 4.1.1 | `CREATE TABLE IF NOT EXISTS ... USING DELTA` | ✅ | Supported in Fabric Lakehouse Spark. Delta is the native format. |
| 4.1.2 | Data types BIGINT, INT, DATE, TIMESTAMP, DECIMAL | ✅ | Supported. |
| 4.1.3 | `VARCHAR(n)` | ✅ | Accepted in Fabric Spark SQL (stored as string, length is checked on write). Note: it is inconsistent with the Silver model, which uses STRING. |
| 4.1.4 | Schema-qualified names `gold.<table>` | ❌ | Fabric Lakehouse needs a schema-enabled lakehouse for `gold.` names. No `CREATE SCHEMA` exists in the script (3.2.9). |
| 4.1.5 | `OPTIMIZE ... ZORDER BY` | ✅ | Supported in Fabric Spark runtime (Delta). Not run by the DDL itself, only guidance. |
| 4.1.6 | `ALTER TABLE ... ADD COLUMNS` (section 5.7) | ✅ | Supported by Delta. It is placed after CREATE, so it works only if run after the tables exist. |
| 4.1.7 | `PARTITIONED BY` | ✅ | Supported. Quality concerns are in 3.2.1–3.2.4. |

### 4.2 Spark Compatibility
| # | Check | Status | Details |
|---|---|---|---|
| 4.2.1 | Spark SQL syntax | ✅ | All CREATE statements are valid Spark SQL / Delta syntax. |
| 4.2.2 | `DECIMAL(18,0)` in `go_process_audit` (records_*_count) | ❌ | Valid, but should be BIGINT as in the logical model and Silver (see 2.2.8). |
| 4.2.3 | Partition columns defined as table columns | ✅ | Every column named in `PARTITIONED BY` exists in the table. |
| 4.2.4 | No Spark-incompatible constraints | ✅ | No PK/FK/CHECK/IDENTITY. |
| 4.2.5 | Use of `TEXT` / `DATETIME` | ✅ | Not used. |

### 4.3 Used Any Unsupported Features in Microsoft Fabric
The unsupported-features knowledge base file was not provided and could not be located, so no finding below is cited against it.

| # | Feature checked | Status | Details |
|---|---|---|---|
| 4.3.1 | Primary/foreign/unique/check constraints | ✅ Not used | None found. |
| 4.3.2 | `GENERATED ... AS IDENTITY` | ✅ Not used | None found. |
| 4.3.3 | Traditional indexes | ✅ Not used | Only ZORDER guidance. |
| 4.3.4 | Triggers, stored procedures, sequences | ✅ Not used | None found. |
| 4.3.5 | Schema-qualified names without schema creation | ❌ | All `gold.` tables. Needs `CREATE SCHEMA` and a schema-enabled Lakehouse (see 4.1.4). |
| 4.3.6 | Result | — | No confirmed unsupported feature. Validation against the KB file remains outstanding. |

## 5. Identified Issues and Recommendations
| # | Issue | Recommendation |
|---|---|---|
| 5.1 | KB file missing from input (4.3) | Add the Fabric unsupported-features KB to the input set and re-run the review. |
| 5.2 | Facts lack region and key fields (1.2.1–1.2.4) | Add `region_name` (or `dim_region_sk`) to `go_fct_ar_aging`, `go_fct_cash_application` and `go_fct_credit_risk`. Add `invoice_id` and `due_date` to `go_fct_ar_aging`. Add `receipt_id` and `days_to_pay` to `go_fct_cash_application`. Add sales rep to `go_fct_ar_aging`. |
| 5.3 | Health score components missing (1.2.5) | Add revenue, AR, cash app and credit risk domain score columns, weight columns, `period_type` and target band to `go_agg_executive_health_score`. Add `period_type` to the other facts and aggregates where grains require it. |
| 5.4 | Date dimension too thin (1.2.6) | Add day, week, month, quarter, year, week start/end and `is_current_period` attributes. |
| 5.5 | SCD Type 2 not implemented (1.2.8) | Add `effective_start_date`, `effective_end_date` and `is_current` to `go_dim_branch`, `go_dim_customer` and `go_dim_contract`. |
| 5.6 | Fact-to-dimension linkage by name (1.2.9, 3.2.6) | Add `*_sk` foreign-reference columns (e.g. `dim_branch_sk`, `dim_customer_sk`) to facts and aggregates. Join by SK and keep only the necessary natural keys. |
| 5.7 | Source lineage gaps (2.2.1–2.2.4, 2.2.6) | Document a mapping table from Silver to Gold per column. Define the customer→collector and customer→sales rep source. Define the credit memo rule by `invoice_type` values. Define the origin of branch_name, org hierarchy and equipment class name (reference tables or added to Silver). |
| 5.8 | Wrong Silver names (2.2.2) | Correct to `silver.si_error_data` and `silver.si_pipeline_audit`. |
| 5.9 | Data type consistency (2.2.5, 2.2.8) | Align `load_date` / `update_date` type with Silver (DATE) or document the change. Change `records_*_count` to BIGINT. |
| 5.10 | Partitioning (3.2.1–3.2.4) | Remove partitioning from small dimensions and the code tables. Replace invoice_date partitioning on `go_dim_invoice` and the status partitions on error/audit with liquid clustering (`CLUSTER BY`) or a date-based partition. Prefer clustering or monthly partitioning for facts. |
| 5.11 | Surrogate key generation (3.2.5) | Document a deterministic key approach (e.g. hash of business key plus effective date) and a uniqueness test in the pipeline. |
| 5.12 | ALTER statements and schema (3.2.8, 3.2.9) | Move the section 5.7 columns into the CREATE statements. Add `CREATE SCHEMA IF NOT EXISTS gold`. |
| 5.13 | Table properties and comments (3.2.10, 3.2.11) | Add `TBLPROPERTIES` and `COMMENT` clauses. Tag PII columns per the logical model. |
| 5.14 | Calculation logic (2.2.9) | Add the formulas for DSO, Best Possible DSO, CEI, AR 90+ %, health score weights and trends, with zero-denominator handling written in PySpark/Spark SQL. |
| 5.15 | Status code tables (1.2.11) | Add code tables for match status and contract status (or document allowed values). |
| 5.16 | File format and URL (3.2.12) | Save the model as `.md` and correct the output URL. |

## 6. API Cost
```
apiCost: 0.000000
```
The platform did not report a cost for this call.
