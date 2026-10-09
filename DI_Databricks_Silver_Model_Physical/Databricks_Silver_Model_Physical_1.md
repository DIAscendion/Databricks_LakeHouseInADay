_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Physical Silver layer data model for Rental Revenue-to-Cash cleansed, conformed, Delta-based tables with error and audit handling.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Silver Model Physical

## 1. Overview
This document translates the provided conceptual model, constraints, Bronze physical model, and Silver logical model into an implementation-ready Databricks Silver physical data model for the Rental Revenue-to-Cash domain. The Silver layer standardizes Bronze data, retains all Bronze table columns, adds surrogate id fields, introduces data quality error handling, and supports downstream analytical processing in accordance with Medallion architecture principles.

## 2. Input Analysis

| Input File | Purpose | Key Physical Modeling Impact |
|---|---|---|
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Defines business entities, KPIs, and conceptual relationships | Drives entity coverage, conformed business naming, and relationship documentation |
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Defines mandatory fields, rules, dependencies, and integrity expectations | Drives validation-aware design, error table structure, and datatype decisions |
| `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` | Defines Bronze raw physical schema | All Bronze columns are retained in Silver with additional id fields and standardized datatypes |
| `DI_Databricks_Silver_Model_Logical/Databricks_Silver_Logical_Data_Model_1.md` | Defines Silver logical structures and support tables | Drives Silver table intent, conformed structure, and audit/error table coverage |

## 3. Silver Layer Physical Design Principles
- Silver tables preserve all Bronze business columns.
- Each core Silver table includes an added surrogate id field.
- No primary keys, foreign keys, unique constraints, or Spark-incompatible constraints are included.
- All tables are created with `CREATE TABLE IF NOT EXISTS` and `USING DELTA`.
- Standard metadata columns are included in each business table:
  - `load_date TIMESTAMP`
  - `update_date TIMESTAMP`
  - `source_system STRING`
- Datatypes are aligned to Databricks Spark SQL compatibility.
- Partitioning is selected for operational scalability and common access patterns.
- Delta Lake is the storage format for all Silver tables.
- Error and audit tables are included for both data validation support and pipeline observability.

## 4. Identified Sources, Transformations, Joins, Filters, and Outputs

### 4.1 Source Tables from Bronze
- `bronze.bz_rental_contracts`
- `bronze.bz_invoices`
- `bronze.bz_cash_receipts`
- `bronze.bz_customer_master`
- `bronze.bz_branch_employee`
- `bronze.bz_audit_log`

### 4.2 Core Silver Transformations
- Standardize date strings into `DATE` columns where applicable.
- Preserve raw business identifiers from Bronze and add Silver surrogate keys.
- Normalize financial precision to `DECIMAL(18,2)` where needed.
- Standardize status and domain fields for downstream conformance.
- Route invalid and rejected records to the Silver error table.
- Record execution details in the Silver audit table.

### 4.3 Expected Joins in Silver Processing
| Left Table | Join Field | Right Table | Purpose |
|---|---|---|---|
| `silver.si_rental_contracts` | `customer_id` | `silver.si_customer_master` | Conform contract-to-customer context |
| `silver.si_rental_contracts` | `sales_rep_id` | `silver.si_branch_employee.employee_id` | Align contracts to sales representatives |
| `silver.si_invoices` | `contract_id` | `silver.si_rental_contracts.contract_id` | Align invoices to contracts |
| `silver.si_invoices` | `customer_id` | `silver.si_customer_master.customer_id` | Align invoices to customer context |
| `silver.si_cash_receipts` | `invoice_id` | `silver.si_invoices.invoice_id` | Align receipts to invoice application |
| `silver.si_cash_receipts` | `customer_id` | `silver.si_customer_master.customer_id` | Align receipts to customers |
| `silver.si_branch_employee` | `branch_code` | `silver.si_rental_contracts.branch_code` | Support branch-level sales and collections analytics |

### 4.4 Business Filters and Validation Conditions
- Reject records with non-parsable required dates into error table.
- Reject records with null mandatory business values where mandated by rules.
- Flag invalid domain values such as unsupported aging buckets or statuses.
- Flag negative values where business rules require non-negative amounts.
- Preserve source lineage columns for remediation and replay.

### 4.5 Output Format
- Delta tables in Databricks Silver schema.
- Markdown physical model document in GitHub output folder.

## 5. Silver Layer DDL Scripts

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
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP
)
USING DELTA
PARTITIONED BY (contract_status);
```

**Partition Strategy:** Partition by `contract_status` to support common lifecycle-oriented processing and manageable cardinality.

**Indexing / Optimization Guidance:**
- Use `OPTIMIZE silver.si_rental_contracts ZORDER BY (customer_id, branch_code, contract_id)`.
- Avoid traditional RDBMS indexes because Spark SQL relies on file layout and data skipping.

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
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP
)
USING DELTA
PARTITIONED BY (invoice_date);
```

**Partition Strategy:** Partition by `invoice_date` for billing period pruning and AR processing efficiency.

**Indexing / Optimization Guidance:**
- Use `OPTIMIZE silver.si_invoices ZORDER BY (customer_id, contract_id, invoice_id, due_date)`.

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
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP
)
USING DELTA
PARTITIONED BY (receipt_date);
```

**Partition Strategy:** Partition by `receipt_date` for payment-period analytics and cash application processing.

**Indexing / Optimization Guidance:**
- Use `OPTIMIZE silver.si_cash_receipts ZORDER BY (customer_id, invoice_id, receipt_id)`.

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
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP
)
USING DELTA
PARTITIONED BY (customer_status);
```

**Partition Strategy:** Partition by `customer_status` to support risk and suspension-based access patterns with low cardinality.

**Indexing / Optimization Guidance:**
- Use `OPTIMIZE silver.si_customer_master ZORDER BY (customer_id, customer_name)`.

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
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP
)
USING DELTA
PARTITIONED BY (region);
```

**Partition Strategy:** Partition by `region` to support regional rollups and branch assignment analysis.

**Indexing / Optimization Guidance:**
- Use `OPTIMIZE silver.si_branch_employee ZORDER BY (branch_code, employee_id, collector_id)`.

## 6. Error Data Table DDL Script

```sql
CREATE TABLE IF NOT EXISTS silver.si_data_quality_errors (
  error_sk BIGINT,
  source_table STRING,
  source_record_id STRING,
  source_file_path STRING,
  validation_rule_name STRING,
  validation_category STRING,
  error_description STRING,
  error_record_payload STRING,
  error_severity STRING,
  layer_name STRING,
  detected_timestamp TIMESTAMP,
  processing_status STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (layer_name, processing_status);
```

**Purpose:** Stores details of validation errors encountered during Silver and Gold processing, as required.

## 7. Audit Table DDL Script

```sql
CREATE TABLE IF NOT EXISTS silver.si_process_audit (
  audit_sk BIGINT,
  pipeline_name STRING,
  source_table STRING,
  target_table STRING,
  process_start_timestamp TIMESTAMP,
  process_end_timestamp TIMESTAMP,
  processing_status STRING,
  records_read_count DECIMAL(18,0),
  records_written_count DECIMAL(18,0),
  records_rejected_count DECIMAL(18,0),
  processing_duration_seconds DECIMAL(18,2),
  error_message STRING,
  executed_by STRING,
  audit_remarks STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (processing_status);
```

**Purpose:** Tracks pipeline execution details, start and end times, record metrics, status, and errors for auditability.

## 8. Update DDL Script

```sql
ALTER TABLE silver.si_rental_contracts ADD COLUMNS (
  contract_source_status STRING
);

ALTER TABLE silver.si_invoices ADD COLUMNS (
  aging_bucket STRING,
  days_past_due INT
);

ALTER TABLE silver.si_cash_receipts ADD COLUMNS (
  match_status STRING,
  unapplied_payment_amount DECIMAL(18,2)
);

ALTER TABLE silver.si_customer_master ADD COLUMNS (
  over_limit_indicator STRING
);

ALTER TABLE silver.si_process_audit ADD COLUMNS (
  run_id STRING
);
```

**Update Usage Note:** These additive DDL statements support future Silver model evolution without overwriting prior versions.

## 9. Table-by-Table Physical Model Summary

| Table Name | Grain | Added ID Field | Bronze Column Coverage | Storage Format | Recommended Z-Order |
|---|---|---|---|---|---|
| `silver.si_rental_contracts` | One row per conformed contract record | `rental_contract_sk` | Includes all Bronze rental contract columns | Delta | `customer_id, branch_code, contract_id` |
| `silver.si_invoices` | One row per conformed invoice record | `invoice_sk` | Includes all Bronze invoice columns | Delta | `customer_id, contract_id, invoice_id, due_date` |
| `silver.si_cash_receipts` | One row per conformed receipt record | `cash_receipt_sk` | Includes all Bronze cash receipt columns | Delta | `customer_id, invoice_id, receipt_id` |
| `silver.si_customer_master` | One row per conformed customer record | `customer_sk` | Includes all Bronze customer columns | Delta | `customer_id, customer_name` |
| `silver.si_branch_employee` | One row per conformed employee assignment | `branch_employee_sk` | Includes all Bronze employee columns | Delta | `branch_code, employee_id, collector_id` |
| `silver.si_data_quality_errors` | One row per rejected or invalid record | `error_sk` | Operational support table | Delta | `source_table, source_record_id` |
| `silver.si_process_audit` | One row per process execution event | `audit_sk` | Operational audit support table | Delta | `pipeline_name, target_table` |

## 10. Data Retention Policies

### 10.1 Retention Periods for the Silver Layer
| Table Category | Retention Period | Rationale |
|---|---|---|
| Core Silver business tables | 7 years | Supports finance, AR, and reporting auditability requirements |
| Data quality error table | 2 years | Supports remediation trend analysis and controlled reprocessing history |
| Process audit table | 2 years | Supports operational observability, SLA review, and incident tracing |
| Intermediate transient Silver views or temp outputs | 30 days | Supports restart and short-term validation only |

### 10.2 Archiving Strategies
- Archive aged Silver Delta data older than the policy threshold into lower-cost archival storage while preserving replay ability.
- Run scheduled `VACUUM` operations only according to enterprise retention governance and Delta log requirements.
- Preserve audit and error summaries before archival for operational reporting continuity.
- Use date-based archival batches by `invoice_date`, `receipt_date`, `effective_date`, or metadata timestamps depending on table purpose.

## 11. Databricks Spark SQL Limitations Considered
The following items from general data modeling practice are intentionally not implemented because they are not appropriate or required for Databricks Spark SQL Silver physical design:
- No primary key constraints.
- No foreign key constraints.
- No unique constraints.
- No check constraints enforced in the DDL.
- No traditional row-store indexes.

Instead, Delta optimization, partitioning, and Z-Ordering are used.

## 12. Assumptions and Design Decisions
1. Bronze physical DDL is treated as the authoritative base structure and every Bronze business column is preserved in the Silver physical tables.
2. Surrogate id fields were added to all core Silver tables because the instructions require id fields in the physical model.
3. Bronze `STRING` date columns were converted to `DATE` in Silver where business semantics indicate true date values.
4. Metadata columns required by the prompt are standardized as `load_date`, `update_date`, and `source_system`.
5. Existing Bronze lineage columns `file_path` and `file_modification_time` are retained for traceability.
6. Error logging is centralized in `silver.si_data_quality_errors` for both Silver and Gold validation events.
7. Audit logging is centralized in `silver.si_process_audit` for pipeline execution traceability.
8. Partitioning choices are based on low-to-moderate cardinality operational filters and reporting-period access patterns.
9. Spark-incompatible constraints were excluded even where conceptual or business rules imply referential relationships.

## 13. Conceptual Data Model Diagram in Tabular Form

| Source Table | Key Field | Target Table | Relationship Description |
|---|---|---|---|
| `silver.si_customer_master` | `customer_id` | `silver.si_rental_contracts` | One customer connects to many rental contracts by `customer_id`. |
| `silver.si_branch_employee` | `employee_id` = `sales_rep_id` | `silver.si_rental_contracts` | One employee as sales rep connects to many rental contracts by `sales_rep_id`. |
| `silver.si_rental_contracts` | `contract_id` | `silver.si_invoices` | One contract connects to many invoices by `contract_id`. |
| `silver.si_customer_master` | `customer_id` | `silver.si_invoices` | One customer connects to many invoices by `customer_id`. |
| `silver.si_invoices` | `invoice_id` | `silver.si_cash_receipts` | One invoice connects to many cash receipts by `invoice_id`. |
| `silver.si_customer_master` | `customer_id` | `silver.si_cash_receipts` | One customer connects to many cash receipts by `customer_id`. |
| `silver.si_branch_employee` | `branch_code` | `silver.si_rental_contracts` | Branch assignment connects employee context to contracts by `branch_code`. |
| `silver.si_branch_employee` | `region` | `silver.si_rental_contracts` | Regional alignment supports rollup from employee assignments to contract activity by `region`. |
| `silver.si_process_audit` | `target_table` | All Silver tables | Audit records connect processing runs to each target Silver table by `target_table`. |
| `silver.si_data_quality_errors` | `source_table` | All Silver/Gold tables | Error records connect validation failures to source tables by `source_table`. |

## 14. Implementation Notes
- Use Auto Loader or batch ingestion from Bronze into Silver.
- Apply standard casting using `to_date()` and controlled null handling.
- Use `MERGE` for incremental upserts where change data patterns exist.
- Use Delta `OPTIMIZE` and `VACUUM` based on enterprise standards.
- Maintain version history of this Markdown artifact in GitHub.

## 15. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_Model_Physical_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical
pipelineID : 12357
