_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Physical Silver layer data model for Rental Revenue-to-Cash conformed Delta tables aligned to Jira AP-1 reporting requirements.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Silver Layer

## Jira Tickets Read
| Ticket Key | Summary | Status |
|---|---|---|
| AP-1 | Reporting Requirements for Rental Revenue-to-Cash | To Do |

## 1. Overview
This physical Silver layer data model translates the provided conceptual model, constraints, Bronze physical model, and Jira ticket AP-1 into implementation-ready Databricks SQL DDL for conformed Silver tables. The design preserves all Bronze business columns, adds id fields required for the physical model, standardizes data types for Databricks Spark SQL compatibility, includes Silver error and audit structures, and supports downstream reporting for revenue, billing, AR aging, cash application, collections performance, and customer credit risk.

## 2. Input Analysis

### 2.1 Source Inputs Used
| Input Source | Purpose | Business Context Applied |
|---|---|---|
| Rental_Revenue_to_Cash_Reports_Conceptual_1.md | Defines business entities, relationships, KPIs, and reporting drill paths | Used to confirm entities, relationship paths, and reporting context |
| Rental_Revenue_to_Cash_Reports_Constraints_1.md | Defines constraints, uniqueness expectations, validations, and business rules | Used to document validation-aligned Silver design decisions |
| Databricks_Bronze_Model_Physical_1.md | Defines Bronze table structures and raw operational columns | Used as the authoritative source for columns that must be preserved in Silver |
| Databricks_Silver_Logical_Data_Model_1.md | Defines Silver logical conformance model | Used to align Silver naming, conformance intent, and support tables |
| Jira AP-1 | Reporting Requirements for Rental Revenue-to-Cash | Used exactly as the business context for Silver reporting support |

### 2.2 Identified Data Sources, Targets, Transformations, Joins, Aggregations, Filters, and Output
| Category | Details |
|---|---|
| Data Sources | `bronze.bz_rental_contracts`, `bronze.bz_invoices`, `bronze.bz_cash_receipts`, `bronze.bz_customer_master`, `bronze.bz_branch_employee` |
| Target Tables | `silver.si_rental_contracts`, `silver.si_invoices`, `silver.si_cash_receipts`, `silver.si_customer_master`, `silver.si_branch_employee`, `silver.si_error_data`, `silver.si_audit_log` |
| Intermediate Transformations | Type standardization, date normalization, business column conformance, duplicate detection preparation, source lineage preservation, metadata enrichment |
| Joins Required Downstream / In Silver Processing | Contracts to customers by `customer_id`; contracts to employees by `sales_rep_id`/`employee_id`; invoices to contracts by `contract_id`; invoices to customers by `customer_id`; cash receipts to invoices by `invoice_id`; cash receipts to customers by `customer_id`; employee assignments to branch and region by `branch_code` and `region` |
| Aggregations Supported Downstream | Rental revenue, net billings, AR aging, DSO, CEI, unapplied cash %, credit utilization %, customer exposure, branch and region rollups |
| Filters / Validation Conditions | Non-negative payment amount, non-negative credit limit, negative credit memos, valid contract mapping, valid customer mapping, fixed aging bucket handling, duplicate prevention by identified business grains |
| Output Format | Databricks SQL DDL using `CREATE TABLE IF NOT EXISTS` and `USING DELTA` |

## 3. Silver Layer DDL Scripts

### 3.1 DDL Script - `silver.si_rental_contracts`
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
PARTITIONED BY (branch_code)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.2 DDL Script - `silver.si_invoices`
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
PARTITIONED BY (invoice_date)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.3 DDL Script - `silver.si_cash_receipts`
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
PARTITIONED BY (receipt_date)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.4 DDL Script - `silver.si_customer_master`
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
PARTITIONED BY (customer_status)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.5 DDL Script - `silver.si_branch_employee`
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
PARTITIONED BY (region)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.6 Error Data Table DDL Script - `silver.si_error_data`
```sql
CREATE TABLE IF NOT EXISTS silver.si_error_data (
  error_record_sk BIGINT,
  error_id STRING,
  source_layer STRING,
  source_table_name STRING,
  target_table_name STRING,
  business_key STRING,
  error_category STRING,
  error_rule STRING,
  error_description STRING,
  rejected_record_payload STRING,
  validation_status STRING,
  detected_timestamp TIMESTAMP,
  pipeline_run_id STRING,
  pipeline_name STRING,
  source_system STRING,
  file_path STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP
)
USING DELTA
PARTITIONED BY (source_table_name)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.7 Audit Table DDL Script - `silver.si_audit_log`
```sql
CREATE TABLE IF NOT EXISTS silver.si_audit_log (
  audit_sk BIGINT,
  audit_id STRING,
  pipeline_run_id STRING,
  pipeline_name STRING,
  source_table_name STRING,
  target_table_name STRING,
  processing_status STRING,
  processing_start_timestamp TIMESTAMP,
  processing_end_timestamp TIMESTAMP,
  processing_duration_seconds DECIMAL(18,2),
  records_read_count INT,
  records_written_count INT,
  records_rejected_count INT,
  reconciliation_status STRING,
  error_message STRING,
  processed_by STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (processing_status)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

## 4. Update DDL Script
```sql
-- Update DDL template for future Silver model changes
ALTER TABLE silver.si_rental_contracts ADD COLUMNS (
  contract_status_reason STRING
);

ALTER TABLE silver.si_invoices ADD COLUMNS (
  billing_period STRING
);

ALTER TABLE silver.si_cash_receipts ADD COLUMNS (
  match_status STRING,
  unapplied_payment_amount DECIMAL(18,2)
);

ALTER TABLE silver.si_customer_master ADD COLUMNS (
  legal_entity_name STRING
);

ALTER TABLE silver.si_branch_employee ADD COLUMNS (
  assignment_end_date DATE
);
```

## 5. Partitioning and Performance Strategy

### 5.1 Partitioning Strategy
| Table | Partition Column | Rationale |
|---|---|---|
| `silver.si_rental_contracts` | `branch_code` | Supports branch-level reporting and drill-down patterns from AP-1 |
| `silver.si_invoices` | `invoice_date` | Supports billing and AR trend analysis by time period |
| `silver.si_cash_receipts` | `receipt_date` | Supports payment trend and collection reporting by period |
| `silver.si_customer_master` | `customer_status` | Supports suspended vs active customer risk analysis |
| `silver.si_branch_employee` | `region` | Supports regional reporting and access patterns |
| `silver.si_error_data` | `source_table_name` | Supports operational investigation by affected source |
| `silver.si_audit_log` | `processing_status` | Supports operational monitoring and troubleshooting |

### 5.2 Index / Optimization Guidance
Databricks Delta Lake does not use traditional RDBMS indexes in the same way as OLTP databases. To remain compatible with Databricks Spark SQL limitations and the provided guidance, the design excludes PK/FK constraints and traditional indexes. Recommended performance optimization patterns are:

| Table | Recommended Optimization |
|---|---|
| `silver.si_rental_contracts` | `OPTIMIZE silver.si_rental_contracts ZORDER BY (contract_id, customer_id, branch_code)` |
| `silver.si_invoices` | `OPTIMIZE silver.si_invoices ZORDER BY (invoice_id, contract_id, customer_id)` |
| `silver.si_cash_receipts` | `OPTIMIZE silver.si_cash_receipts ZORDER BY (receipt_id, invoice_id, customer_id)` |
| `silver.si_customer_master` | `OPTIMIZE silver.si_customer_master ZORDER BY (customer_id, customer_name)` |
| `silver.si_branch_employee` | `OPTIMIZE silver.si_branch_employee ZORDER BY (employee_id, branch_code, region)` |
| `silver.si_error_data` | `OPTIMIZE silver.si_error_data ZORDER BY (pipeline_run_id, source_table_name, error_category)` |
| `silver.si_audit_log` | `OPTIMIZE silver.si_audit_log ZORDER BY (pipeline_run_id, pipeline_name, processing_status)` |

## 6. Data Retention Policies

### 6.1 Retention Periods for the Silver Layer
| Table Category | Retention Period | Rationale |
|---|---|---|
| Core Silver conformed tables | 7 years | Supports long-term reporting, reconciliations, and trend analysis for finance and AR domains |
| Error data table | 2 years | Supports troubleshooting, remediation review, and recurring data quality analysis |
| Audit table | 3 years | Supports pipeline observability, compliance review, and operational root cause analysis |

### 6.2 Archiving Strategies
| Strategy Area | Approach |
|---|---|
| Historical Silver data | Archive inactive partitions to lower-cost storage while preserving Delta history where governance allows |
| Error data | Archive closed and remediated error partitions quarterly |
| Audit logs | Archive completed pipeline run history by year after retention threshold review |
| Vacuum policy | Apply Delta `VACUUM` only according to enterprise governance and recovery requirements |

## 7. Validation and Business Rule Alignment
| Rule Area | Silver Physical Design Alignment |
|---|---|
| Valid contract mapping | `contract_id` retained across contracts and invoices for downstream validation |
| Valid customer mapping | `customer_id` retained across contracts, invoices, receipts, and customer master |
| Duplicate prevention preparation | Id and business key columns retained for deduplication logic in ETL |
| Negative credit memo handling | `invoice_type` and `invoice_amount` retained for validation logic |
| Non-negative payment amount | `payment_amount` retained in Silver cash receipts |
| Credit limit validation | `credit_limit` retained in customer master |
| Unapplied cash traceability | Receipts retain `receipt_id`, `invoice_id`, and customer context; error/audit tables support exceptions |
| Branch and region reporting | `branch_code` and `region` retained to support AP-1 drill paths |

## 8. Assumptions and Design Decisions
1. The Bronze physical model is treated as the authoritative structural source for Silver physical tables.
2. All Bronze columns are preserved in Silver, with standardized Spark SQL-compatible data types where date normalization is appropriate.
3. Additional surrogate id fields were added because the instructions explicitly require id fields in the physical model if missing from the logical model.
4. No primary keys, foreign keys, unique constraints, or check constraints are included because they are not required and may be incompatible with the intended Spark SQL implementation pattern.
5. Traditional database indexes are not included; Delta optimization guidance is provided instead to stay aligned with Databricks implementation practices.
6. The error data table is designed to capture issues from both Silver and Gold validation processes as required.
7. The audit table is included to capture pipeline execution start time, end time, status, and error details.
8. Jira AP-1 is the exact business context used for revenue, billing, receivables, collections, and credit risk reporting support.

## 9. Conceptual Data Model Diagram in Tabular Form Showing Relationships
| Source Table | Connected Table | Key Field | Relationship Description |
|---|---|---|---|
| `silver.si_customer_master` | `silver.si_rental_contracts` | `customer_id` | One customer connects to many rental contracts by `customer_id` |
| `silver.si_branch_employee` | `silver.si_rental_contracts` | `employee_id` to `sales_rep_id` | One sales representative can connect to many rental contracts |
| `silver.si_rental_contracts` | `silver.si_invoices` | `contract_id` | One contract connects to many invoices by `contract_id` |
| `silver.si_customer_master` | `silver.si_invoices` | `customer_id` | One customer connects to many invoices by `customer_id` |
| `silver.si_invoices` | `silver.si_cash_receipts` | `invoice_id` | One invoice connects to many cash receipts by `invoice_id` |
| `silver.si_customer_master` | `silver.si_cash_receipts` | `customer_id` | One customer connects to many cash receipts by `customer_id` |
| `silver.si_branch_employee` | `silver.si_customer_master` | `region` | Region-based employee assignment supports customer reporting rollups |
| `silver.si_branch_employee` | `silver.si_rental_contracts` | `branch_code` | Branch assignment supports branch-level contract reporting |

## 10. Databricks Spark SQL Limitations Considered
| Limitation / Standard | Treatment in Final Output |
|---|---|
| PK/FK enforcement not required for this Silver layer pattern | Excluded |
| Traditional OLTP indexing model not typical for Delta Lake | Replaced with Z-ORDER and partitioning guidance |
| Constraint-heavy DDL may not align with Medallion Silver processing | Excluded from DDL |
| Mixed raw date formats from Bronze | Standardized to `DATE` in Silver where business meaning is clearly date-based |

## 11. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_Model_Physical_1.sql](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.sql)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical
pipelineID : 12357
