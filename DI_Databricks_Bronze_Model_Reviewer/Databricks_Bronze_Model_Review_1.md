_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Review of the Rental Revenue-to-Cash Databricks Bronze physical data model and DDL scripts against the conceptual model, source schema, best practices, and Databricks Delta Lake compatibility.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Review – Rental Revenue to Cash Reports

## 0. Review Scope and Inputs

| Item | Value |
|---|---|
| Repository | `DIAscendion/Databricks_LakeHouseInADay` (branch `main`) |
| Source schema (input) | `Input/rental_revenue_to_cash_bronze_schema.sql` |
| Physical model under review | `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` |
| Conceptual reference | `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` |
| Review mode | Mode 1 – New review (no change request supplied) |
| Knowledge base of unsupported features | None attached; assessed against standard Databricks Delta Lake / Spark SQL / Unity Catalog behavior |

### 0.1 Parsed Model Summary

| Aspect | Findings |
|---|---|
| Data sources | `LEGACY_SE`, `LEGACY_MW`, `SUNBELT_CORE` (contracts), branch/legacy billing (invoices), `LOCKBOX_FEED` (cash receipts), CRM/ERP (customer master), `HR_FEED` / `HR_FEED_OLD` (employees) |
| Target tables | `bronze.bz_rental_contracts`, `bronze.bz_invoices`, `bronze.bz_cash_receipts`, `bronze.bz_customer_master`, `bronze.bz_branch_employee`, `bronze.bz_audit_log` |
| Transformations | Type assignment only; added `load_timestamp`, `update_timestamp`; table renaming `bronze_<x>` → `bz_<x>` |
| Joins | None in Bronze (deferred to Silver: customer_id, contract_id, invoice_id, sales_rep_id↔employee_id) |
| Aggregations | None in Bronze (AR aging, DSO, CEI, credit exposure deferred) |
| Filters | None – duplicates, orphans, nulls, stale rows retained by design |
| Output format | Delta Lake tables (`USING DELTA`), Markdown documentation |

---

## 1. Alignment with Conceptual Data Model

### 1.1 ✅ Green Tick: Covered Requirements

| Conceptual Entity | Bronze Table / Column(s) | Status |
|---|---|---|
| Customer (name, status, credit terms, credit limit, customer since) | `bz_customer_master` (all 5 attributes) | ✅ |
| Contract (contract status) | `bz_rental_contracts.contract_status` | ✅ |
| Equipment Class | `bz_rental_contracts.equipment_class` | ✅ |
| Invoice (invoice date, due date, invoice amount, credit memos via negative amount/type) | `bz_invoices` | ✅ |
| Cash Receipt (payment amount, method, date, unapplied via null invoice_id) | `bz_cash_receipts` | ✅ |
| Sales Rep / Collector (name, branch, collector assignment) | `bz_branch_employee` (`role`, `employee_name`, `branch_code`, `collector_id`) | ✅ |
| Contract→Invoice, Customer→Contract/Invoice, Invoice→Cash Receipt relationships | Raw keys `contract_id`, `customer_id`, `invoice_id` retained | ✅ |
| Fact entities (Revenue, AR Aging, Cash App, Credit Risk) and Date | Correctly deferred to Silver/Gold | ✅ |

### 1.2 ❌ Red Tick: Missing / Incomplete Requirements

| Conceptual Requirement | Gap | Status |
|---|---|---|
| Branch (Branch Name, Branch Status) | No branch master feed; only `branch_code` exists | ❌ |
| Region / Organization Hierarchy (Region→Branch, Network level) | Region only as free text on `bz_branch_employee`; no branch→region mapping source | ❌ |
| Collector → Customer assignment (One-to-Many) | Collector linked only to sales rep (`collector_id`), not to customer | ❌ |
| Total Billed Rental Days (ADR KPI) | No billed-days / rental period on invoices; must be derived from contract dates, which are unreliable | ❌ |
| Invoice-to-payment application amount (partial payments) | Receipts carry a single `invoice_id`; no application line/amount table | ❌ |
| Open Contract Value | Derivable only from `daily_rate` × duration; no contract value field | ❌ |

---

## 2. Source Data Structure Compatibility

### 2.1 ✅ Green Tick: Aligned Elements

| Source Table (input SQL) | Bronze Table | Column Parity | Data Types | Status |
|---|---|---|---|---|
| `bronze_rental_contracts` | `bz_rental_contracts` | 12/12 source columns retained | Identical (STRING, DECIMAL(10,2), TIMESTAMP) | ✅ |
| `bronze_invoices` | `bz_invoices` | 12/12 | Identical (DECIMAL(12,2)) | ✅ |
| `bronze_cash_receipts` | `bz_cash_receipts` | 9/9 | Identical | ✅ |
| `bronze_customer_master` | `bz_customer_master` | 9/9 | Identical | ✅ |
| `bronze_branch_employee` | `bz_branch_employee` | 10/10 | Identical | ✅ |
| Raw mixed-format dates kept as STRING | All date columns | — | Correct for raw layer | ✅ |
| Lineage columns (`source_system`, `file_path`, `file_modification_time`) | All 5 tables | — | — | ✅ |

### 2.2 ❌ Red Tick: Misaligned or Missing Elements

| Element | Issue | Status |
|---|---|---|
| Table namespace | Source specifies `sunbelt_demo.bronze.bronze_<table>`; model uses two-part `bronze.bz_<table>` with no catalog – resolves against whatever catalog is current and diverges from the documented Silver naming (`sunbelt_demo.silver.silver_<table>`) | ❌ |
| Added `update_timestamp` | Source convention is **append-only**; an update timestamp implies MERGE/update semantics and will always be null or equal to `load_timestamp` | ❌ |
| Source column comments | Inline source comments (nullability, known issues, FK intent) dropped from DDL | ❌ |
| `bz_audit_log` | Not present in source; acceptable addition but lacks schema definition rationale (no run id, row counts, error detail) | ❌ |

---

## 3. Best Practices Assessment

### 3.1 ✅ Green Tick: Aligned with Best Practices

| Practice | Status |
|---|---|
| Delta Lake format for all tables | ✅ |
| No PK/FK/CHECK constraints enforced in raw layer | ✅ |
| Raw values preserved; no cleansing, filtering, or dedup in Bronze | ✅ |
| Idempotent DDL with `CREATE TABLE IF NOT EXISTS` | ✅ |
| Consistent ingestion lineage columns on every table | ✅ |
| Monetary fields typed as DECIMAL rather than DOUBLE | ✅ |
| Separate audit table for ingestion observability | ✅ |

### 3.2 ❌ Red Tick: Deviations from Best Practices

| Deviation | Impact | Status |
|---|---|---|
| No fully qualified Unity Catalog names (`catalog.schema.table`) | Environment ambiguity; deployment to wrong catalog | ❌ |
| No `COMMENT` on tables/columns | Loss of governance metadata in Unity Catalog / lineage | ❌ |
| No `_rescued_data` column for Auto Loader schema drift | Malformed/unexpected values in typed DECIMAL/TIMESTAMP columns are silently nulled or fail load | ❌ |
| No ingestion batch / run identifier column (e.g., `ingestion_run_id`) | Cannot correlate rows to `bz_audit_log` entries or reprocess a batch | ❌ |
| No data layout (liquid clustering / partitioning) on append-only, growing tables | Poor pruning for incremental Silver reads | ❌ |
| No `TBLPROPERTIES` (e.g., `delta.enableChangeDataFeed`, `delta.autoOptimize.optimizeWrite`, `delta.autoOptimize.autoCompact`) | Less efficient incremental downstream processing and small-file issues | ❌ |
| `load_timestamp` nullable with no default | Relies entirely on pipeline code; risk of null load times | ❌ |
| `bz_audit_log.record_id STRING` without generation strategy | Possible duplicate/missing ids; no row count, error message, or run duration columns | ❌ |
| Typed DECIMAL columns for raw feeds with known DQ issues | Unparseable amounts lost before Silver can inspect them (mitigate via `_rescued_data`) | ❌ |

---

## 4. DDL Script Compatibility

### 4.1 ✅ Databricks Delta Lake / Spark SQL Compatibility

| Check | Result | Status |
|---|---|---|
| `CREATE TABLE IF NOT EXISTS ... USING DELTA` syntax | Valid | ✅ |
| Data types `STRING`, `DECIMAL(p,s)`, `TIMESTAMP` | Supported | ✅ |
| Reserved words as column names (`role`, `status`, `currency`) | Valid in Databricks SQL without quoting | ✅ |
| No PK/FK/IDENTITY/DEFAULT clauses that require feature flags | None used | ✅ |
| Statements terminated and independently executable | Yes | ✅ |

### 4.2 ✅ Used any unsupported features in Databricks

| Feature Check | Found in DDL? | Status |
|---|---|---|
| Clustered/non-clustered indexes, `IDENTITY` (T-SQL style), `AUTO_INCREMENT` | No | ✅ |
| Triggers, stored procedures, sequences | No | ✅ |
| Enforced UNIQUE / FOREIGN KEY constraints | No | ✅ |
| Unsupported types (`VARCHAR(MAX)`, `DATETIME2`, `MONEY`, `NVARCHAR`, `TEXT`) | No | ✅ |
| `TEXTIMAGE_ON`, filegroups, `WITH (NOLOCK)` | No | ✅ |

> Note: If `DEFAULT current_timestamp()` is adopted for `load_timestamp` (see recommendations), the table must set `'delta.feature.allowColumnDefaults' = 'supported'`.

---

## 5. Identified Issues and Recommendations

| # | Severity | Area | Issue | Recommendation |
|---|---|---|---|---|
| 1 | High | Naming | Two-part `bronze.bz_*` names omit catalog; diverge from source `sunbelt_demo.bronze.bronze_*` | Use fully qualified names, e.g. `sunbelt_demo.bronze.bz_rental_contracts` (or parameterize `${catalog}`); document the mapping to `sunbelt_demo.silver.silver_*` |
| 2 | High | Conceptual gap | No Branch / Region / Organization Hierarchy source | Add a `bz_branch_master` feed (`branch_code`, `branch_name`, `branch_status`, `region`, lineage cols) or record it as an explicit Silver reference-data dependency |
| 3 | High | Conceptual gap | Collector→Customer assignment missing | Source a customer-collector assignment feed or add `collector_id` to customer master extract |
| 4 | Medium | Conceptual gap | Billed rental days / payment application lines absent (ADR, partial payments) | Confirm with source owners; add `billed_days`/`rental_period_start/end` to invoices and a receipt-application table if available |
| 5 | Medium | Semantics | `update_timestamp` conflicts with append-only design | Remove, or document it as reserved/always equal to `load_timestamp` |
| 6 | Medium | Schema drift | No `_rescued_data` column; typed columns can lose bad values | Add `_rescued_data STRING` to all five tables and ingest with Auto Loader `rescuedDataColumn` |
| 7 | Medium | Lineage | No batch/run id linking data rows to audit log | Add `ingestion_run_id STRING` to all tables and to `bz_audit_log` |
| 8 | Medium | Audit table | `bz_audit_log` too thin | Add `run_id`, `pipeline_name`, `source_file`, `rows_read`, `rows_written`, `error_message`, `start_time`, `end_time`; generate `record_id` via `uuid()` or `BIGINT GENERATED ALWAYS AS IDENTITY` |
| 9 | Low | Performance | No clustering or table properties | Add `CLUSTER BY (load_timestamp)` (or `source_system`) and `TBLPROPERTIES ('delta.enableChangeDataFeed'='true','delta.autoOptimize.optimizeWrite'='true','delta.autoOptimize.autoCompact'='true')` |
| 10 | Low | Governance | No table/column comments | Carry source inline comments into `COMMENT` clauses (grain, known DQ issues, Silver target) |
| 11 | Low | Data quality | `load_timestamp` may be null | Populate in pipeline with `current_timestamp()` or set column default (requires `allowColumnDefaults`) |

### 5.1 Sample Corrected DDL (pattern)

```sql
CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_rental_contracts (
  contract_id            STRING COMMENT 'Raw contract id; format varies by source system',
  customer_id            STRING COMMENT 'Raw FK to bz_customer_master; not enforced; nullable',
  branch_code            STRING,
  sales_rep_id           STRING COMMENT 'Raw FK to bz_branch_employee.employee_id; nullable',
  equipment_class        STRING,
  contract_start_date    STRING COMMENT 'Raw date; ISO or MM/DD/YYYY',
  contract_end_date      STRING COMMENT 'Raw date; blank/sentinel for open contracts',
  contract_status        STRING,
  daily_rate             DECIMAL(10,2),
  source_system          STRING,
  file_path              STRING,
  file_modification_time TIMESTAMP,
  ingestion_run_id       STRING,
  load_timestamp         TIMESTAMP,
  _rescued_data          STRING
)
USING DELTA
CLUSTER BY (load_timestamp)
COMMENT 'Bronze raw rental contract header; one row per source record; append-only. Feeds silver_rental_contracts.'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 5.2 Overall Verdict

| Section | Result |
|---|---|
| Alignment with Conceptual Data Model | Partial – core transactional entities ✅; Branch/Region/Collector-assignment ❌ |
| Source Data Structure Compatibility | ✅ Full column/type parity; ❌ namespace and `update_timestamp` deviations |
| Best Practices | Partial – raw-layer principles ✅; governance/drift/layout ❌ |
| DDL Compatibility (Databricks) | ✅ Fully executable; no unsupported features |
| **Recommendation** | **Approve with changes** – address items 1–3 before Silver build; others recommended |

---

## Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Bronze_Model_Reviewer/Databricks_Bronze_Model_Review_1.md
