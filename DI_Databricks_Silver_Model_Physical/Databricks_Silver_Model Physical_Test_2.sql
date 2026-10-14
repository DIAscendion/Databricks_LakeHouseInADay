_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Updated Databricks Silver Model Physical for Rental Revenue-to-Cash reporting incorporating Jira ticket AP-1 requirements and version 2 changes.
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Silver Model Physical

## Jira Tickets Read

| Ticket Key | Summary | Status |
|---|---|---|
| AP-1 | Reporting Requirements for Rental Revenue-to-Cash | To Do |

## 1. Overview
This document defines the Silver layer physical data model for the Rental Revenue-to-Cash reporting domain. It is derived from the conceptual model, constraints, Bronze physical model, Silver logical model, and Jira ticket AP-1. The Silver layer stores cleansed, standardized, deduplicated, and conformed data in Delta Lake tables for downstream Gold reporting across revenue, billing, AR aging, cash application, collections, and customer credit risk. The description metadata references Jira ticket AP-1 as the source of business-driven changes.

## 2. Source Inputs and Business Context

| Input Source | Purpose | Key Requirement Used |
|---|---|---|
| AP-1 | Jira business context | Defines reporting domains, KPIs, calculations, constraints, validations, and conceptual relationships |
| Rental_Revenue_to_Cash_Reports_Conceptual_1.md | Conceptual model | Defines entities, relationships, common attributes, and KPI context |
| Rental_Revenue_to_Cash_Reports_Constraints_1.md | Constraints and rules | Defines uniqueness, validation, dependency, and transformation rules |
| Databricks_Bronze_Model_Physical_1.md | Bronze physical model | Provides authoritative Bronze tables and columns that must all appear in Silver with added id fields and metadata |
| Databricks_Silver_Logical_Data_Model_1.md | Logical Silver model | Provides Silver table intent, standardized data types, and support-table design |

## 3. Silver Layer Physical Design Principles
- All Silver tables use `CREATE TABLE IF NOT EXISTS` and `USING DELTA`.
- All Bronze columns are retained in the Silver tables.
- Additional id fields are included in the Silver physical model.
- No primary keys, foreign keys, unique constraints, or Spark-incompatible constraints are defined.
- All tables include metadata columns: `load_date`, `update_date`, `source_system`.
- Delta Lake is the required storage format.
- The Silver layer supports conformance, standardization, validation, reconciliation, and downstream Gold consumption.
- Error handling is implemented with a dedicated error data table for Silver and Gold validation issues.
- Audit logging is implemented with a dedicated Silver audit table for pipeline execution tracking.

## 4. Databricks Spark SQL Compatibility Notes

| Item | Included in Output | Reason |
|---|---|---|
| Primary Key constraints | No | Excluded because Spark SQL physical enforcement is not required in this design |
| Foreign Key constraints | No | Excluded because Spark SQL does not rely on FK enforcement in Delta Lake physical modeling |
| Check constraints for business validation | No | Validation is implemented in ETL logic and error tables instead of enforced physical constraints |
| Unique constraints | No | Deduplication handled in transformation logic, not DDL |
| Index DDL | Documented as optimization guidance only | Databricks favors partitioning, ZORDER, clustering, and file optimization over traditional RDBMS indexes |

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
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (source_system);
```

**Optimization Guidance**

| Strategy Type | Columns |
|---|---|
| Partitioning | source_system |
| Suggested ZORDER | branch_code, customer_id, contract_id, sales_rep_id |

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
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (source_system);
```

**Optimization Guidance**

| Strategy Type | Columns |
|---|---|
| Partitioning | source_system |
| Suggested ZORDER | customer_id, contract_id, invoice_id, due_date |

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
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (source_system);
```

**Optimization Guidance**

| Strategy Type | Columns |
|---|---|
| Partitioning | source_system |
| Suggested ZORDER | customer_id, invoice_id, receipt_id, receipt_date |

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
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (source_system);
```

**Optimization Guidance**

| Strategy Type | Columns |
|---|---|
| Partitioning | source_system |
| Suggested ZORDER | customer_id, customer_status, customer_name |

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
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (source_system);
```

**Optimization Guidance**

| Strategy Type | Columns |
|---|---|
| Partitioning | source_system |
| Suggested ZORDER | employee_id, collector_id, branch_code, region |

### 5.6 Error Data Table DDL Script
```sql
CREATE TABLE IF NOT EXISTS silver.si_error_data (
  error_record_sk BIGINT,
  source_table_name STRING,
  target_layer STRING,
  error_category STRING,
  error_rule STRING,
  error_description STRING,
  rejected_record_payload STRING,
  validation_status STRING,
  detected_timestamp TIMESTAMP,
  pipeline_run_timestamp TIMESTAMP,
  source_system STRING,
  file_path STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP
)
USING DELTA
PARTITIONED BY (target_layer, source_system);
```

**Purpose**
- Stores validation failures and rejected records for both Silver and Gold processing.
- Supports rules from AP-1 such as invalid contract linkage, negative/non-negative amount rules, duplicate grain detection, invalid aging buckets, duplicate customer records, and unapplied cash visibility.

### 5.7 Audit Table DDL Script
```sql
CREATE TABLE IF NOT EXISTS silver.si_audit_pipeline (
  audit_run_sk BIGINT,
  pipeline_name STRING,
  source_table_name STRING,
  target_table_name STRING,
  processing_status STRING,
  processing_start_timestamp TIMESTAMP,
  processing_end_timestamp TIMESTAMP,
  processing_duration_seconds DECIMAL(18,2),
  records_read_count BIGINT,
  records_written_count BIGINT,
  records_rejected_count BIGINT,
  reconciliation_status STRING,
  processed_by STRING,
  error_message STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (source_system);
```

### 5.8 Update DDL Script
```sql
-- Version 2 update script based on Jira AP-1 and requested git version update
ALTER TABLE silver.si_rental_contracts ADD COLUMNS (
  rental_contract_sk BIGINT
);

ALTER TABLE silver.si_invoices ADD COLUMNS (
  invoice_sk BIGINT
);

ALTER TABLE silver.si_cash_receipts ADD COLUMNS (
  cash_receipt_sk BIGINT
);

ALTER TABLE silver.si_customer_master ADD COLUMNS (
  customer_sk BIGINT
);

ALTER TABLE silver.si_branch_employee ADD COLUMNS (
  branch_employee_sk BIGINT
);

CREATE TABLE IF NOT EXISTS silver.si_error_data (
  error_record_sk BIGINT,
  source_table_name STRING,
  target_layer STRING,
  error_category STRING,
  error_rule STRING,
  error_description STRING,
  rejected_record_payload STRING,
  validation_status STRING,
  detected_timestamp TIMESTAMP,
  pipeline_run_timestamp TIMESTAMP,
  source_system STRING,
  file_path STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP
)
USING DELTA
PARTITIONED BY (target_layer, source_system);

CREATE TABLE IF NOT EXISTS silver.si_audit_pipeline (
  audit_run_sk BIGINT,
  pipeline_name STRING,
  source_table_name STRING,
  target_table_name STRING,
  processing_status STRING,
  processing_start_timestamp TIMESTAMP,
  processing_end_timestamp TIMESTAMP,
  processing_duration_seconds DECIMAL(18,2),
  records_read_count BIGINT,
  records_written_count BIGINT,
  records_rejected_count BIGINT,
  reconciliation_status STRING,
  processed_by STRING,
  error_message STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (source_system);
```

## 6. Data Validation and Transformation Rules

| Domain | Rule from Inputs/Jira | Silver Handling |
|---|---|---|
| Revenue | Credit memo amounts must be negative and invoice amounts non-negative | Failed records are written to `silver.si_error_data` |
| Revenue | Invoice amounts must tie to a valid contract_id | Validate during Silver conformance |
| AR Aging | Every outstanding invoice must map to a valid customer_id | Validate during Silver conformance |
| AR Aging | Aging buckets must be fixed and non-overlapping | Enforced in transformation logic, not DDL |
| Cash Application | Payment amount must be non-negative | Invalid rows quarantined in error table |
| Cash Application | Applied amounts cannot exceed invoice amount | Reconciliation and validation logic logged in audit/error tables |
| Customer Risk | Duplicate customer records must be resolved before exposure aggregation | Silver customer conformance and deduplication required |
| Executive Scorecard | Health score must be between 0 and 100 | Downstream measure validation logged if violated |
| All domains | Duplicate records at stated business grain must be prevented | Deduplication logic and duplicate logging in error table |

## 7. Data Retention Policies

### 7.1 Retention Periods for Silver Layer

| Table Group | Retention Period | Rationale |
|---|---|---|
| Core Silver conformed tables | 7 years | Supports long-term financial, AR, collections, and trend reporting |
| Error data table | 2 years | Supports issue triage, remediation history, and compliance review |
| Audit pipeline table | 2 years | Supports pipeline observability, reconciliation, and operational traceability |

### 7.2 Archiving Strategies
- Archive historical Silver Delta versions older than active operational need to lower-cost storage while preserving recoverability.
- Retain recent high-access data in active Silver Delta tables for reporting performance.
- Use Delta Lake time travel and scheduled optimize/vacuum operations aligned to enterprise retention policy.
- Archive error and audit records in periodic snapshots before long-term purge.
- Preserve lineage columns and Jira-driven change history in Git versioning.

## 8. Conceptual Data Model Diagram in Tabular Form

| Table A | Key Field | Table B | Relationship Description |
|---|---|---|---|
| silver.si_customer_master | customer_id | silver.si_rental_contracts | One customer connects to many rental contracts by `customer_id` |
| silver.si_branch_employee | employee_id = sales_rep_id | silver.si_rental_contracts | One sales representative connects to many rental contracts by `sales_rep_id` |
| silver.si_rental_contracts | contract_id | silver.si_invoices | One contract connects to many invoices by `contract_id` |
| silver.si_customer_master | customer_id | silver.si_invoices | One customer connects to many invoices by `customer_id` |
| silver.si_invoices | invoice_id | silver.si_cash_receipts | One invoice connects to many cash receipts by `invoice_id` |
| silver.si_customer_master | customer_id | silver.si_cash_receipts | One customer connects to many cash receipts by `customer_id` |
| silver.si_branch_employee | branch_code | silver.si_rental_contracts | Branch employee assignment connects branch context to contracts by `branch_code` |
| silver.si_branch_employee | region | reporting rollups | Employee assignment supports regional rollup by `region` |

## 9. Assumptions and Design Decisions
1. Bronze physical model is treated as authoritative for required source columns.
2. All Bronze columns are carried into Silver, with added surrogate-style id fields in the physical model.
3. Dates represented as strings in Bronze are standardized to `DATE` in Silver where the meaning is clearly date-based.
4. Traditional database indexes are not implemented physically; Databricks optimization guidance is documented instead.
5. No PK/FK/unique/check constraints are physically enforced to remain compatible with Spark SQL and Delta Lake implementation patterns.
6. Error and audit tables are included as required for Silver and Gold validation traceability.
7. Jira ticket AP-1 is the business source for reporting, calculations, validations, and conceptual relationships.
8. This version 2 output was generated because the user requested changes and a git-stored next version.

## 10. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_Model Physical_Test_2.sql](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model%20Physical_Test_2.sql)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical
pipelineID : 12357