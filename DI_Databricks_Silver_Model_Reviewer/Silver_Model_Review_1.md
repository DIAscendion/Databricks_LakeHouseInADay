_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Databricks Silver physical data model and DDL for Rental Revenue-to-Cash reporting, checking alignment, best practices and Databricks/Spark compatibility
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Silver Model Review – Rental Revenue to Cash Reports

## Summary
This review covers `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md`. That file defines 7 Delta tables in the `silver` schema:
- 5 business tables: `si_rental_contracts`, `si_invoices`, `si_cash_receipts`, `si_customer_master` and `si_branch_employee`.
- 1 error table shared by Silver and Gold: `si_error_data`.
- 1 audit table shared by Silver and Gold: `si_pipeline_audit`.

It also includes OPTIMIZE/ZORDER guidance, additive `ALTER TABLE` update scripts, partitioning, retention and archiving policies.

**Reference inputs used**
| Input | Path | Used For |
|---|---|---|
| Silver Physical Model (under review) | `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Primary review subject |
| Silver Logical Model | `DI_Databricks_Silver_Model_Logical/Databricks_Silver_Logical_Data_Model_1.md` | Checking against the conceptual model and requirements (Section 1) |
| Bronze source schema | `Input/rental_revenue_to_cash_bronze_schema.sql` | Checking source alignment (Section 2) |
| Knowledge Base (unsupported Databricks features) | **Not provided** | Section 4.3 uses the documented Databricks Delta limitations instead; a formal KB check is **Not verifiable** |

**Overall verdict:** The DDL is syntactically compatible with Databricks and Spark, and it preserves every Bronze column. It needs changes before production in these areas:
- The error and audit tables do not match the logical model.
- There is no way to link an error row to the pipeline run that produced it.
- There are no columns to support unapplied-cash flagging or customer deduplication and SCD2.
- The update DDL cannot be safely re-run.
- Small reference tables are partitioned by `load_date`.

---

## 1. Alignment with Conceptual Data Model

### 1.1 ✅ Covered Requirements
| # | Requirement (from Logical Model / AP-1 context) | Physical Implementation | Status |
|---|---|---|---|
| 1 | Si_Rental_Contracts entity with branch, equipment class, start/end dates, status, daily rate | `silver.si_rental_contracts`: all columns present; dates `DATE`, `daily_rate DECIMAL(18,2)` | ✅ |
| 2 | Si_Invoices entity with invoice/due date, invoice/tax amount, type, currency | `silver.si_invoices`: all present; amounts `DECIMAL(18,2)` | ✅ |
| 3 | Si_Cash_Receipts entity with receipt date, payment amount, method | `silver.si_cash_receipts`: all present | ✅ |
| 4 | Si_Customer_Master with name, credit terms, credit limit, customer since, status | `silver.si_customer_master`: all present | ✅ |
| 5 | Si_Branch_Employee with name, role, branch, region, collector assignment, effective date | `silver.si_branch_employee`: all present (`collector_id` maps to "Collector Assignment") | ✅ |
| 6 | Lineage attributes (Source System, File Path, File Modification Time, Load/Update Timestamp) on all business tables | Present on all 5 business tables | ✅ |
| 7 | Data type standardization (string/date/timestamp/decimal(18,2)) | Applied consistently | ✅ |
| 8 | Error data structure required | `silver.si_error_data` defined | ✅ |
| 9 | Process audit structure required | `silver.si_pipeline_audit` defined | ✅ |
| 10 | Relationship keys for Contract→Invoice, Invoice→Receipt, Customer→Contract/Invoice/Receipt, Sales Rep→Contract | `contract_id`, `invoice_id`, `customer_id`, `sales_rep_id`/`employee_id` retained | ✅ |
| 11 | KPIs (DSO, CEI, AR aging buckets, health score) handled downstream | Documented as Gold outputs (Assumption 8) | ✅ |

### 1.2 ❌ Missing Requirements
| # | Requirement | Location | Finding | Status |
|---|---|---|---|---|
| 1 | Unapplied cash must be "flagged and reported separately" (Logical §3.2.3, §6.5) | `silver.si_cash_receipts` | There is no flag column (for example `is_unapplied_cash BOOLEAN`) and no application-status column. Physical §3.2 item 6 says status and match columns will be added, but none are defined. | ❌ |
| 2 | Partial payment application must be tracked (Constraint 11) | `silver.si_cash_receipts` | There is no `applied_amount`, `unapplied_amount` or `application_status` column. | ❌ |
| 3 | Each customer must resolve to a single conformed record after deduplication (Constraint 13) | `silver.si_customer_master` | There is no conformed/master customer key (for example `conformed_customer_id`) and no duplicate-group indicator. The Bronze schema says this feeds an **SCD Type 2** customer dimension, but there are no SCD columns (`effective_start_date`, `effective_end_date`, `is_current`). | ❌ |
| 4 | Branch/employee stale-feed resolution (Bronze: SCD Type 2) | `silver.si_branch_employee` | There are no SCD2 or current-record columns. `effective_date` alone cannot resolve rows from the stale `HR_FEED_OLD` feed. | ❌ |
| 5 | Error table attribute "Rejected Record Payload" | `silver.si_error_data` | Only `rejected_value` (a single column value) exists. There is no column for the full record payload. | ❌ |
| 6 | Error table attribute "Pipeline Run Timestamp" | `silver.si_error_data` | This attribute is missing, and there is no `pipeline_run_id` either. | ❌ |
| 7 | Audit attribute "Reconciliation Status" | `silver.si_pipeline_audit` | This attribute is missing. | ❌ |
| 8 | Branch must exist in organization hierarchy and be active (Constraint 1) | Model-wide | There is no branch or organization-hierarchy reference table, so this rule cannot be validated in Silver. Branch data is only available through `si_branch_employee`. | ❌ |
| 9 | Table naming parity with logical model | Error/Audit tables | The logical names `Si_Data_Quality_Errors` and `Si_Process_Audit` were renamed to `si_error_data` and `si_pipeline_audit` without documenting a mapping. | ❌ |

---

## 2. Source Data Structure Compatibility

### 2.1 ✅ Aligned Elements
| Bronze Table | Bronze Columns | Silver Table | Transformation | Status |
|---|---|---|---|---|
| `bronze_rental_contracts` | contract_id, customer_id, branch_code, sales_rep_id, equipment_class, contract_status, source_system, file_path, file_modification_time | `si_rental_contracts` | Carried 1:1 | ✅ |
| `bronze_rental_contracts` | contract_start_date, contract_end_date (STRING) | `si_rental_contracts` | STRING → DATE | ✅ |
| `bronze_rental_contracts` | daily_rate DECIMAL(10,2) | `si_rental_contracts` | Widened to DECIMAL(18,2) | ✅ |
| `bronze_invoices` | all 12 columns | `si_invoices` | invoice_date/due_date STRING → DATE; amounts DECIMAL(12,2) → DECIMAL(18,2) | ✅ |
| `bronze_cash_receipts` | all 9 columns | `si_cash_receipts` | receipt_date STRING → DATE; payment_amount widened | ✅ |
| `bronze_customer_master` | all 9 columns | `si_customer_master` | customer_since STRING → DATE; credit_limit widened | ✅ |
| `bronze_branch_employee` | all 10 columns | `si_branch_employee` | effective_date STRING → DATE | ✅ |
| (new) | Error data table | `si_error_data` | Present | ✅ |
| (new) | Surrogate id fields | `*_sk BIGINT` on all tables | Added | ✅ |

All 52 Bronze columns across the 5 tables are present in Silver.

### 2.2 ❌ Misaligned or Missing Elements
| # | Element | Location | Finding | Status |
|---|---|---|---|---|
| 1 | `load_timestamp`, `update_timestamp` | All business tables | These columns do not exist in the Bronze schema. Physical §13.2 says "All Bronze business and lineage columns are preserved", which implies they come from Bronze. They are actually new Silver columns, so their origin should be documented. | ❌ (documentation) |
| 2 | Mixed-format / sentinel date handling | `contract_end_date`, `due_date`, `receipt_date`, etc. | Bronze dates arrive as ISO or MM/DD/YYYY, and some use blank or sentinel values. Silver casts them to `DATE` without defining a parsing rule or a target for dates that fail to parse. Failed parses would silently become NULL unless they are routed to `si_error_data`. | ❌ |
| 3 | ID casing/format normalization | `contract_id`, `customer_id` | Bronze lists inconsistent casing and format as a known issue. No standardized or normalized key column, and no rule for one, is defined. | ❌ |
| 4 | Credit memo sign rule | `si_invoices.invoice_amount` | Logical Constraint 5 says credit memos must be negative. Physical §3.4 says "non-negative where applicable". The two documents conflict. | ❌ |
| 5 | Catalog / naming vs Bronze convention | All tables | Bronze names its Silver targets `sunbelt_demo.silver.silver_<table>` and calls the customer table `silver_customer_dim`. Physical uses `silver.si_<table>` with no catalog. That matches the logical `Si_` rule, but the name mapping should be stated. | ❌ (minor) |

---

## 3. Best Practices Assessment

### 3.1 ✅ Adherence to Best Practices
| Practice | Evidence | Status |
|---|---|---|
| Silver mirrors Bronze grain (appropriate normalization for a conformed layer) | One Silver table per Bronze table | ✅ |
| Id fields present | `rental_contract_sk`, `invoice_sk`, `cash_receipt_sk`, `customer_sk`, `branch_employee_sk`, `error_record_sk`, `audit_sk` | ✅ |
| Metadata columns `load_date`, `update_date`, `source_system` | Present on all 7 tables | ✅ |
| Error data table present | `silver.si_error_data` | ✅ |
| Audit table present | `silver.si_pipeline_audit` | ✅ |
| No PK/FK/UNIQUE/CHECK constraints | None in DDL | ✅ |
| No traditional indexes | Uses partitioning + `OPTIMIZE ... ZORDER BY` | ✅ |
| Consistent snake_case naming with `si_` prefix | All tables/columns | ✅ |
| Monetary precision standardized | `DECIMAL(18,2)` | ✅ |
| Retention policies defined | §11.1 (7 years business; 2 years error/audit) | ✅ |
| Archiving strategy defined | §11.2 | ✅ |
| Lineage retained | `file_path`, `file_modification_time` | ✅ |

### 3.2 ❌ Deviations from Best Practices
| # | Deviation | Location | Detail | Status |
|---|---|---|---|---|
| 1 | Over-partitioning small reference tables | `si_customer_master`, `si_branch_employee` (also `si_rental_contracts`) | Partitioning by daily `load_date` on low-volume master data creates many small files. Databricks recommends against partitioning tables smaller than about 1 TB. Partitioning by load date also does not help queries that filter on business dates. | ❌ |
| 2 | Partitioning on load date, not business date, for facts | `si_invoices`, `si_cash_receipts` | Reporting filters on `invoice_date`, `due_date` and `receipt_date`, so `load_date` pruning will rarely help those queries. Liquid clustering (`CLUSTER BY`) would fit better. | ❌ |
| 3 | No link from error rows to pipeline runs | `si_error_data` | §12 says error events can be traced to pipeline runs, but `si_error_data` has no `pipeline_run_id`. | ❌ |
| 4 | Redundant columns | `si_error_data.table_name` vs `target_table`/`source_table` | The meaning overlaps and is ambiguous. | ❌ |
| 5 | Update DDL cannot be re-run | §8 `ALTER TABLE ... ADD COLUMNS` | If the script runs twice, it fails because the columns already exist. Also, `ADD COLUMNS` on `si_error_data` and `si_pipeline_audit` is inside the model DDL itself rather than in the base CREATE. | ❌ |
| 6 | Derived columns stored in Silver | §8 (`invoice_year`, `invoice_month`, `customer_tenure_days`, ...) | These derived values break normalization, can drift out of date (tenure changes every day), and belong in Gold or a date dimension. | ❌ |
| 7 | Documentation inconsistency | §12 `si_branch_employee.region → si_rental_contracts` | `si_rental_contracts` has no `region` column. | ❌ |
| 8 | ZORDER on partition-irrelevant / low-value columns | `si_customer_master` ZORDER (`customer_status`), §10 vs §7 column lists differ for `si_error_data` and `si_pipeline_audit` | Z-ordering on low-cardinality columns gives little benefit. The §10 table and the §6/§7 scripts also list different columns. | ❌ |
| 9 | Retention settings not expressed as table properties | All tables | There are no `TBLPROPERTIES` such as `delta.logRetentionDuration` or `delta.deletedFileRetentionDuration` to enforce the policy. | ❌ |
| 10 | Surrogate key generation undefined | All `*_sk` | The surrogate keys are plain `BIGINT` with no `GENERATED ALWAYS AS IDENTITY` and no deterministic hashing rule. This is acceptable, but the generation rule is left vague. | ❌ (minor) |

---

## 4. DDL Script Compatibility

### 4.1 Databricks Compatibility
| Check | Result | Status |
|---|---|---|
| `CREATE TABLE IF NOT EXISTS` used for all 7 tables | Yes | ✅ |
| `USING DELTA` specified | Yes, all tables | ✅ |
| `PARTITIONED BY` uses existing columns | Yes (`load_date`, `layer_name`) | ✅ |
| `OPTIMIZE ... ZORDER BY` syntax valid | Yes; ZORDER columns are not partition columns | ✅ |
| `ALTER TABLE ... ADD COLUMNS (...)` syntax valid | Yes, but it cannot be re-run safely (see 3.2 #5) | ✅ |
| Three-level Unity Catalog naming | Not specified; relies on the default catalog | ❌ (minor) |

### 4.2 Spark Compatibility
| Check | Result | Status |
|---|---|---|
| Data types (`STRING`, `DATE`, `TIMESTAMP`, `BIGINT`, `INT`, `DECIMAL(18,2)`) | All supported by Spark SQL | ✅ |
| No unsupported types (`VARCHAR(MAX)`, `NVARCHAR`, `DATETIME`, `MONEY`, `TEXT`) | None used | ✅ |
| Column named `role` | Not reserved in default mode. Under ANSI mode it may need backticks, so consider renaming it to `employee_role` | ✅ (advisory) |
| No T-SQL / RDBMS-specific constructs (`IDENTITY(1,1)`, `CLUSTERED INDEX`, `GO`) | None used | ✅ |

### 4.3 Unsupported Databricks Features Used
**Answer: No unsupported features were detected. The formal Knowledge Base check could not be done because the file was not provided.**

| Feature Category | Found in DDL? | Notes |
|---|---|---|
| Traditional indexes (`CREATE INDEX`) | No | Only ZORDER guidance is used |
| Enforced PK/FK/UNIQUE constraints | No | — |
| CHECK constraints | No | — |
| T-SQL identity / sequences / triggers | No | — |
| Liquid clustering combined with partitioning | No | Liquid clustering is only mentioned as guidance (§4.11). If it is adopted, it **cannot** be combined with `PARTITIONED BY` or `ZORDER` on the same table |
| Knowledge Base list check | **Not verifiable** | The Knowledge Base file of unsupported features was not provided to this run |

---

## 5. Identified Issues and Recommendations

| # | Issue | Location | Severity | Recommended Fix |
|---|---|---|---|---|
| 1 | No unapplied-cash flag or partial-application tracking | `silver.si_cash_receipts` | High | Add `is_unapplied_cash BOOLEAN`, `applied_amount DECIMAL(18,2)`, `unapplied_amount DECIMAL(18,2)` and `application_status STRING` |
| 2 | No customer deduplication or SCD2 support | `silver.si_customer_master` | High | Add `conformed_customer_id STRING`, `effective_start_date DATE`, `effective_end_date DATE`, `is_current BOOLEAN` and `record_hash STRING` |
| 3 | No SCD2 or stale-feed resolution for employees | `silver.si_branch_employee` | High | Add `effective_end_date DATE`, `is_current BOOLEAN` and `record_hash STRING` |
| 4 | Error rows cannot be linked to pipeline runs; payload missing | `silver.si_error_data` | High | Add `pipeline_run_id STRING`, `pipeline_run_timestamp TIMESTAMP` and `rejected_record_payload STRING`; remove or clarify `table_name` |
| 5 | Reconciliation status missing | `silver.si_pipeline_audit` | Medium | Add `reconciliation_status STRING` (and optionally amount-control totals) |
| 6 | Credit memo sign rule conflicts with the logical model | §3.4 vs Logical Constraint 5 | Medium | Align the rule: `invoice_type = 'Credit Memo'` requires `invoice_amount < 0`, and standard invoices require `>= 0` |
| 7 | Date parsing and sentinel handling undefined | All date columns cast from STRING | Medium | Document the parsing rule (try ISO, then MM/DD/YYYY), map sentinels to NULL or a far-future date, and route failed parses to `si_error_data` |
| 8 | ID normalization undefined | `contract_id`, `customer_id`, etc. | Medium | Document `UPPER(TRIM())` standardization; optionally keep the raw value in a `*_raw` column |
| 9 | Over-partitioning small tables | `si_customer_master`, `si_branch_employee`, `si_rental_contracts` | Medium | Remove `PARTITIONED BY`; use liquid clustering (`CLUSTER BY (customer_id)`, etc.) |
| 10 | Load-date partitioning does not serve reporting filters | `si_invoices`, `si_cash_receipts` | Low | Consider `CLUSTER BY (invoice_date, customer_id)` / `(receipt_date, customer_id)` instead of partition + ZORDER |
| 11 | Update DDL cannot be re-run | §8 | Medium | Fold the columns into the base CREATE statements, or guard each ALTER with a schema check in the pipeline |
| 12 | Derived date-part and tenure columns in Silver | §8 | Low | Move them to Gold or a date dimension; compute tenure at query time |
| 13 | Error/audit table names differ from the logical model | `si_error_data`, `si_pipeline_audit` | Low | Rename to `si_data_quality_errors` / `si_process_audit`, or document the mapping |
| 14 | Relationship doc references a nonexistent column | §12 (`region` on contracts) | Low | Correct the relationship to go via `branch_code` |
| 15 | Origin of `load_timestamp`/`update_timestamp` misdescribed | §13.2 | Low | State that these are Silver-added metadata columns |
| 16 | No branch or organization-hierarchy reference | Model-wide | Medium | Add `si_branch` / organization hierarchy reference data, or document the source used for active-branch validation |
| 17 | Retention not enforced in table properties | All tables | Low | Add `TBLPROPERTIES ('delta.logRetentionDuration'=..., 'delta.deletedFileRetentionDuration'=...)` |
| 18 | ZORDER column lists inconsistent between §6/§7 and §10 | `si_error_data`, `si_pipeline_audit` | Low | Make the two lists match; drop low-cardinality columns |
| 19 | Catalog not specified | All DDL | Low | Use the full name (for example `sunbelt_demo.silver.si_<table>`) |
| 20 | Knowledge Base file not supplied | Review input | Info | Attach the unsupported-features KB so section 4.3 can be fully verified |

---

## 6. apiCost
apiCost: 0.0412375
