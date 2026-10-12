_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Physical Silver layer data model for cleansed, conformed, and audit-ready Rental Revenue-to-Cash Delta tables.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver Model Physical

## 1. Overview
This document translates the Rental Revenue-to-Cash conceptual model, business constraints, Bronze physical model, and Silver logical model into an implementation-ready Silver physical data model for Databricks. The Silver layer stores standardized, validated, conformed, and analytics-ready data in Delta Lake while preserving Bronze lineage, adding surrogate id fields, supporting exception handling, and enabling downstream Gold reporting for revenue, AR aging, cash application, and credit risk.

## 2. Input Analysis

| Input File | Layer | Purpose | Physical Modeling Impact |
|---|---|---|---|
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Conceptual | Defines business entities, KPIs, and relationships | Drives entity coverage, relationship mapping, and analytical alignment |
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Constraints | Defines mandatory fields, rules, dependencies, and referential expectations | Drives validation, exception design, audit design, and assumptions |
| `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` | Bronze Physical | Defines authoritative Bronze raw tables and columns | All Bronze columns must be preserved in Silver physical tables, with additional id fields and standardized types |
| `DI_Databricks_Silver_Model_Logical/Databricks_Silver_Logical_Data_Model_1.md` | Silver Logical | Defines Silver logical entities and exception/audit structures | Drives Silver naming, conformance rules, and logical-to-physical mapping |

## 3. Identified Data Sources, Targets, Transformations, Joins, Filters, and Outputs

### 3.1 Source Systems
| Source System | Bronze Table | Silver Target Table | Business Purpose |
|---|---|---|---|
| `LEGACY_SE`, `LEGACY_MW`, `SUNBELT_CORE` | `bronze.bz_rental_contracts` | `silver.si_rental_contracts` | Standardized rental contract information |
| Branch / billing platforms | `bronze.bz_invoices` | `silver.si_invoices` | Standardized invoice and billing records |
| `LOCKBOX_FEED` | `bronze.bz_cash_receipts` | `silver.si_cash_receipts` | Standardized payment and receipt data |
| CRM / ERP customer master | `bronze.bz_customer_master` | `silver.si_customer_master` | Conformed customer profile and credit reference |
| `HR_FEED`, `HR_FEED_OLD` | `bronze.bz_branch_employee` | `silver.si_branch_employee` | Standardized employee, sales rep, and collector assignment data |

### 3.2 Intermediate Transformations
1. Cast string dates from Bronze into `DATE` or `TIMESTAMP` where business meaning is stable.
2. Standardize monetary values to `DECIMAL(18,2)` for downstream calculations.
3. Retain all Bronze columns while adding Silver surrogate id fields.
4. Preserve metadata and lineage columns: `load_date`, `update_date`, `source_system`.
5. Retain Bronze ingestion lineage columns `file_path` and `file_modification_time`.
6. Add validation-ready status and match columns where required by conceptual and constraint definitions.
7. Support customer deduplication and conformance in Silver processing logic.
8. Redirect invalid or nonconforming records into a shared Silver/Gold exception table.

### 3.3 Expected Joins in Silver Processing
| Left Table | Join Key | Right Table | Purpose |
|---|---|---|---|
| `silver.si_rental_contracts` | `customer_id` | `silver.si_customer_master` | Customer conformance for contract reporting |
| `silver.si_rental_contracts` | `sales_rep_id = employee_id` | `silver.si_branch_employee` | Sales rep and branch reporting alignment |
| `silver.si_invoices` | `contract_id` | `silver.si_rental_contracts` | Billing to contract standardization |
| `silver.si_invoices` | `customer_id` | `silver.si_customer_master` | Customer-level AR alignment |
| `silver.si_cash_receipts` | `invoice_id` | `silver.si_invoices` | Payment application and matching |
| `silver.si_cash_receipts` | `customer_id` | `silver.si_customer_master` | Customer receipt analysis |
| `silver.si_branch_employee` | `branch_code` | `silver.si_rental_contracts` | Branch-level organizational standardization |

### 3.4 Validation Filters
| Validation Area | Rule |
|---|---|
| Completeness | Mandatory business fields such as branch, customer, invoice amount, due date, payment amount, credit limit must not be null when required |
| Accuracy | `invoice_amount`, `payment_amount`, and `credit_limit` must be non-negative where applicable; credit memo logic handled by `invoice_type` |
| Format | Aging bucket values must align to valid bucket set when derived downstream |
| Consistency | Branch and region values must align to enterprise rollup standards |
| Referential | Applied receipt records should reference valid invoice records; invoice records should reference valid contracts or customers where expected |

### 3.5 Output Format
- Storage format: Delta Lake
- SQL dialect: Databricks Spark SQL compatible
- Documentation format: Markdown
- Output location: `DI_Databricks_Silver_Model_Physical`

## 4. Silver Layer Physical Design Principles
1. All Silver tables are created with `CREATE TABLE IF NOT EXISTS`.
2. All Bronze columns are included in the Silver physical tables.
3. Additional surrogate id fields are added even when the logical model omitted them.
4. No primary keys, foreign keys, unique constraints, or check constraints are included.
5. Databricks-compatible types only are used.
6. Delta Lake is the mandatory storage format.
7. Metadata fields required on each business table: `load_date`, `update_date`, `source_system`.
8. Bronze lineage fields are retained to support reconciliation.
9. Error and audit tables are included for Silver and Gold operational coverage.
10. Partitioning is applied only where useful for time-based pruning and operational performance.
11. Indexes are documented as optimization guidance using Databricks techniques such as `OPTIMIZE`, `ZORDER`, liquid clustering guidance, and partitioning rather than traditional RDBMS indexes.

## 5. Silver Layer Physical DDL Scripts

### 5.1 Rental Contracts
```sql
CREATE TABLE IF NOT EXISTS silver.si_rental_contracts (
  rental_contract_sk BIGINT,
  contract_id STRING,
  customer_id STRING,
  branch_code STRING,
  sales_rep_id STRING,
  equipment_class STRING,
  contract_start_date DATE,
  contract_end_date DATE,
  contract_status STRING,
  daily_rate DECIMAL(18,2),
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_rental_contracts ZORDER BY (contract_id, customer_id, branch_code, sales_rep_id);
```

### 5.2 Invoices
```sql
CREATE TABLE IF NOT EXISTS silver.si_invoices (
  invoice_sk BIGINT,
  invoice_id STRING,
  contract_id STRING,
  customer_id STRING,
  invoice_date DATE,
  due_date DATE,
  invoice_amount DECIMAL(18,2),
  tax_amount DECIMAL(18,2),
  invoice_type STRING,
  currency STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_invoices ZORDER BY (invoice_id, contract_id, customer_id, due_date);
```

### 5.3 Cash Receipts
```sql
CREATE TABLE IF NOT EXISTS silver.si_cash_receipts (
  cash_receipt_sk BIGINT,
  receipt_id STRING,
  invoice_id STRING,
  customer_id STRING,
  receipt_date DATE,
  payment_amount DECIMAL(18,2),
  payment_method STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_cash_receipts ZORDER BY (receipt_id, invoice_id, customer_id, receipt_date);
```

### 5.4 Customer Master
```sql
CREATE TABLE IF NOT EXISTS silver.si_customer_master (
  customer_sk BIGINT,
  customer_id STRING,
  customer_name STRING,
  credit_terms STRING,
  credit_limit DECIMAL(18,2),
  customer_since DATE,
  customer_status STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_customer_master ZORDER BY (customer_id, customer_name, customer_status);
```

### 5.5 Branch Employee
```sql
CREATE TABLE IF NOT EXISTS silver.si_branch_employee (
  branch_employee_sk BIGINT,
  employee_id STRING,
  employee_name STRING,
  role STRING,
  branch_code STRING,
  region STRING,
  collector_id STRING,
  effective_date DATE,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_branch_employee ZORDER BY (employee_id, branch_code, region, collector_id);
```

## 6. Error Data Table DDL Script
The exception table is shared for Silver and Gold validation issues as requested.

```sql
CREATE TABLE IF NOT EXISTS silver.si_error_data (
  error_record_sk BIGINT,
  layer_name STRING,
  pipeline_name STRING,
  source_table STRING,
  target_table STRING,
  business_key STRING,
  table_name STRING,
  column_name STRING,
  validation_rule STRING,
  validation_status STRING,
  rejected_value STRING,
  error_description STRING,
  error_category STRING,
  severity STRING,
  source_system STRING,
  file_path STRING,
  detected_timestamp TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (layer_name, load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_error_data ZORDER BY (source_table, target_table, business_key, validation_status, error_category);
```

## 7. Audit Table DDL Script
The audit table stores Silver and Gold pipeline execution history as requested.

```sql
CREATE TABLE IF NOT EXISTS silver.si_pipeline_audit (
  audit_sk BIGINT,
  pipeline_run_id STRING,
  layer_name STRING,
  pipeline_name STRING,
  source_table STRING,
  target_table STRING,
  process_start_timestamp TIMESTAMP,
  process_end_timestamp TIMESTAMP,
  processing_status STRING,
  records_read BIGINT,
  records_written BIGINT,
  records_rejected BIGINT,
  processing_time_seconds DECIMAL(18,2),
  trigger_type STRING,
  processed_by STRING,
  error_message STRING,
  source_system STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (layer_name, load_date);
```

**Optimization Guidance**
```sql
OPTIMIZE silver.si_pipeline_audit ZORDER BY (pipeline_run_id, pipeline_name, source_table, target_table, processing_status);
```

## 8. Update DDL Script
This section provides additive update DDL patterns for future model changes without dropping tables.

```sql
ALTER TABLE silver.si_rental_contracts ADD COLUMNS (
  contract_start_year INT,
  contract_end_year INT
);

ALTER TABLE silver.si_invoices ADD COLUMNS (
  invoice_year INT,
  invoice_month INT,
  due_year INT,
  due_month INT
);

ALTER TABLE silver.si_cash_receipts ADD COLUMNS (
  receipt_year INT,
  receipt_month INT
);

ALTER TABLE silver.si_customer_master ADD COLUMNS (
  customer_tenure_days BIGINT
);

ALTER TABLE silver.si_error_data ADD COLUMNS (
  remediation_status STRING,
  remediated_timestamp TIMESTAMP
);

ALTER TABLE silver.si_pipeline_audit ADD COLUMNS (
  workflow_name STRING,
  notebook_path STRING
);
```

## 9. Partitioning Strategy

| Table | Recommended Partition | Reason |
|---|---|---|
| `silver.si_rental_contracts` | `load_date` | Supports incremental loads and operational pruning |
| `silver.si_invoices` | `load_date` | High-volume billing ingestion and incremental processing |
| `silver.si_cash_receipts` | `load_date` | Payment feed loads are append-heavy and date-driven |
| `silver.si_customer_master` | `load_date` | Supports periodic customer master refresh and reconciliation |
| `silver.si_branch_employee` | `load_date` | HR and assignment refresh handling |
| `silver.si_error_data` | `layer_name`, `load_date` | Efficient support for triage by layer and processing date |
| `silver.si_pipeline_audit` | `layer_name`, `load_date` | Operational monitoring by layer and run date |

## 10. Index and Performance Strategy
Because Databricks Spark SQL does not use traditional B-tree indexes like OLTP platforms, the following supported optimization patterns should be used.

| Table | Optimization Technique | Columns |
|---|---|---|
| `silver.si_rental_contracts` | Z-ORDER | `contract_id`, `customer_id`, `branch_code`, `sales_rep_id` |
| `silver.si_invoices` | Z-ORDER | `invoice_id`, `contract_id`, `customer_id`, `due_date` |
| `silver.si_cash_receipts` | Z-ORDER | `receipt_id`, `invoice_id`, `customer_id`, `receipt_date` |
| `silver.si_customer_master` | Z-ORDER | `customer_id`, `customer_name`, `customer_status` |
| `silver.si_branch_employee` | Z-ORDER | `employee_id`, `branch_code`, `region`, `collector_id` |
| `silver.si_error_data` | Z-ORDER | `source_table`, `target_table`, `business_key`, `validation_status` |
| `silver.si_pipeline_audit` | Z-ORDER | `pipeline_run_id`, `pipeline_name`, `processing_status` |

## 11. Data Retention Policies

### 11.1 Retention Periods for Silver Layer
| Table Category | Retention Period | Rationale |
|---|---|---|
| Core Silver business tables | 7 years | Supports finance, AR, cash reconciliation, and trend analysis |
| Error data table | 2 years online, archive afterward | Supports operational remediation, audit review, and root cause analysis |
| Pipeline audit table | 2 years online, archive afterward | Supports operational governance and job troubleshooting |
| File-level lineage metadata | Same as parent table | Required for source reconciliation and auditability |

### 11.2 Archiving Strategies
1. Vacuum and retention settings must align with enterprise governance and Delta Lake retention safeguards.
2. Historical Silver records older than operational access thresholds should be archived to lower-cost Delta archive storage.
3. Error and audit records older than 2 years should be moved to archive schema or cold storage while preserving retrieval capability.
4. Archive tables should keep the same schema structure to simplify back-read and replay.
5. Do not use aggressive `VACUUM` windows that violate audit or rollback requirements.

## 12. Conceptual Data Model Diagram in Tabular Form

| Table A | Key Field | Table B | Relationship Description |
|---|---|---|---|
| `silver.si_customer_master` | `customer_id` | `silver.si_rental_contracts` | One customer can relate to many rental contracts |
| `silver.si_branch_employee` | `employee_id = sales_rep_id` | `silver.si_rental_contracts` | One sales representative can manage many rental contracts |
| `silver.si_rental_contracts` | `contract_id` | `silver.si_invoices` | One rental contract can generate many invoices |
| `silver.si_customer_master` | `customer_id` | `silver.si_invoices` | One customer can have many invoices |
| `silver.si_invoices` | `invoice_id` | `silver.si_cash_receipts` | One invoice can relate to many payment applications or receipts |
| `silver.si_customer_master` | `customer_id` | `silver.si_cash_receipts` | One customer can have many receipts |
| `silver.si_branch_employee` | `branch_code` | `silver.si_rental_contracts` | Branch assignment supports branch rollup of contracts |
| `silver.si_branch_employee` | `region` | `silver.si_rental_contracts` | Region assignment supports regional reporting rollups |
| `silver.si_error_data` | `source_table / target_table` | `silver.si_pipeline_audit` | Error events can be traced to specific pipeline runs and targets |

## 13. Assumptions and Design Decisions
1. Bronze physical model is treated as the authoritative column source for Silver physical design.
2. All Bronze business and lineage columns are preserved in Silver.
3. Surrogate id fields were added as `*_sk BIGINT` because the instructions require id fields in the physical model.
4. No PK, FK, unique, or check constraints are included because they are either unsupported or not appropriate for this Databricks Silver implementation requirement.
5. Traditional indexes were not implemented because Databricks favors Delta optimization techniques instead.
6. Date strings from Bronze are standardized to `DATE` where business semantics are stable; timestamps remain `TIMESTAMP`.
7. Error and audit tables are designed to cover Silver and Gold operational needs without duplicating physical structures.
8. Calculated KPI facts such as DSO, CEI, and AR aging bucket summaries are assumed to be downstream Gold outputs, while Silver remains conformed and validation-ready.
9. `load_date` and `update_date` were added in addition to Bronze timestamps to satisfy explicit metadata requirements.
10. Credit memo sign handling is managed in transformation logic via `invoice_type`; the physical model does not enforce numeric sign constraints.

## 14. Databricks Spark SQL Limitations Considered and Excluded
| Limitation / Consideration | Handling in Final Output |
|---|---|
| Traditional PK/FK enforcement is not reliable for medallion physical ingestion patterns | Excluded from DDL |
| Traditional OLTP indexes are not used in Databricks Delta | Replaced with partitioning and `OPTIMIZE ... ZORDER BY` guidance |
| Heavy constraint enforcement can reduce ingestion flexibility | Excluded from table definitions |
| Generated surrogate keys may be populated by ETL logic rather than strict identity dependence | Modeled as `BIGINT` columns without unsupported enforcement assumptions |

## 15. Implementation Notes
1. Use Auto Loader or structured batch ingestion from Bronze to populate these Silver tables.
2. Populate surrogate keys during ETL using deterministic or sequence-style assignment logic consistent with enterprise standards.
3. Route invalid rows to `silver.si_error_data` before promoting conformed rows.
4. Record each pipeline execution in `silver.si_pipeline_audit`.
5. Run `OPTIMIZE` and optionally `VACUUM` based on enterprise retention standards.

## 16. API Cost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_Model_Physical_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical
pipelineID : 12357
