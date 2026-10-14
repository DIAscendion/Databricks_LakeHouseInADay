_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Updated Silver layer physical data model for Rental Revenue-to-Cash analytical reporting aligned to Jira AP-1 requirements; changes sourced from AP-1
## *Version*: 1
## *Updated on*: 
_____________________________________________

## *Changes*:
1. Version 1 created as a new Silver physical model output in response to user request `yes and v2`.
2. Applied business reporting requirements, constraints, validations, and relationship context from Jira ticket AP-1.
3. Derived the Silver physical layer from the provided conceptual model, constraints, Bronze physical model, and Silver logical model.
4. Included all Bronze-layer columns in the Silver layer and added id fields where required by the physical model instructions.
5. Added Silver error data and audit tables required for validation, reconciliation, and pipeline observability.
6. Preserved version history by creating a new output file without overwriting prior versions.

## *Reason*:
1. Change requested from Jira ticket AP-1.
2. AP-1 defines reporting requirements for Revenue-to-Cash Executive Scorecard, Rental Revenue and Billing Performance, AR Aging and Collections, Cash Application and Collector Performance, and Customer Credit Risk.
3. User input requested a versioned update and no prior Silver physical output file was found in the target output directory during this run.

# Silver Layer

## 1. Summary
This Silver layer physical data model translates the Rental Revenue-to-Cash logical and Bronze inputs into Databricks Delta tables for cleansed, conformed, and analytics-ready processing. It uses the Jira AP-1 business context exactly as provided and supports downstream reporting for revenue, billing, receivables, collections, unapplied cash tracking, and customer credit risk.

## 2. Source Inputs Used
| Input Type | File / Ticket | Purpose |
|---|---|---|
| Jira | AP-1 | Reporting requirements, business validations, constraints, and conceptual relationships |
| Conceptual | `Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | High-level entities, facts, attributes, and relationships |
| Constraints | `Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Data expectations, business rules, and validation constraints |
| Bronze Physical | `Databricks_Bronze_Model_Physical_1.md` | Authoritative Bronze physical source table structures and metadata columns |
| Silver Logical | `Databricks_Silver_Logical_Data_Model_1.md` and context version 4 | Silver conformance intent and reporting alignment |

## 3. Physical Design Rules Applied
| Rule | Application |
|---|---|
| Bronze columns retained | All Bronze business columns are retained in Silver |
| ID fields added | Physical model includes id fields required for joins and downstream conformance |
| Spark SQL compatibility | No PK, FK, or unsupported constraints included |
| Metadata columns | `load_date`, `update_date`, `source_system` included in all Silver tables as required |
| Delta format | All tables use `USING DELTA` |
| Partition strategy | Date-based partitions used where beneficial for time-sliced reporting and incremental processing |
| Index design | Databricks-friendly optimization guidance provided using ZORDER / clustering guidance rather than unsupported traditional indexes |
| Error handling | Dedicated error table included for Silver and downstream Gold validation traceability |
| Auditability | Dedicated audit table included for Silver and Gold pipeline execution traceability |

## 4. DDL Scripts

### 4.1 DDL scripts

#### 4.1.1 `silver.si_rental_contracts`
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
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (contract_start_date);
```

**Optimization / Index Strategy**

| Table | Suggested Optimize Keys | Notes |
|---|---|---|
| `silver.si_rental_contracts` | `contract_id`, `customer_id`, `branch_code`, `sales_rep_id`, `equipment_class` | Use `OPTIMIZE silver.si_rental_contracts ZORDER BY (contract_id, customer_id, branch_code)` for contract and branch reporting access paths |

#### 4.1.2 `silver.si_invoices`
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
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (invoice_date);
```

**Optimization / Index Strategy**

| Table | Suggested Optimize Keys | Notes |
|---|---|---|
| `silver.si_invoices` | `invoice_id`, `contract_id`, `customer_id`, `due_date`, `invoice_type` | Use `OPTIMIZE silver.si_invoices ZORDER BY (invoice_id, contract_id, customer_id, due_date)` for invoice drill-through and aging access |

#### 4.1.3 `silver.si_cash_receipts`
```sql
CREATE TABLE IF NOT EXISTS silver.si_cash_receipts (
  cash_receipt_sk BIGINT,
  receipt_id STRING,
  invoice_id STRING,
  customer_id STRING,
  receipt_date DATE,
  payment_amount DECIMAL(18,2),
  payment_method STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (receipt_date);
```

**Optimization / Index Strategy**

| Table | Suggested Optimize Keys | Notes |
|---|---|---|
| `silver.si_cash_receipts` | `receipt_id`, `invoice_id`, `customer_id`, `receipt_date` | Use `OPTIMIZE silver.si_cash_receipts ZORDER BY (receipt_id, invoice_id, customer_id)` for payment application and unapplied cash tracing |

#### 4.1.4 `silver.si_customer_master`
```sql
CREATE TABLE IF NOT EXISTS silver.si_customer_master (
  customer_sk BIGINT,
  customer_id STRING,
  customer_name STRING,
  credit_terms STRING,
  credit_limit DECIMAL(18,2),
  customer_since DATE,
  customer_status STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA;
```

**Optimization / Index Strategy**

| Table | Suggested Optimize Keys | Notes |
|---|---|---|
| `silver.si_customer_master` | `customer_id`, `customer_name`, `customer_status` | Use `OPTIMIZE silver.si_customer_master ZORDER BY (customer_id, customer_status)` for conformance, AR, and credit risk lookups |

#### 4.1.5 `silver.si_branch_employee`
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
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date);
```

**Optimization / Index Strategy**

| Table | Suggested Optimize Keys | Notes |
|---|---|---|
| `silver.si_branch_employee` | `employee_id`, `branch_code`, `region`, `collector_id`, `role` | Use `OPTIMIZE silver.si_branch_employee ZORDER BY (employee_id, branch_code, region, collector_id)` for personnel drill-down and security rollup alignment |

### 4.2 Error Data Table DDL script

#### 4.2.1 `silver.si_error_data`
```sql
CREATE TABLE IF NOT EXISTS silver.si_error_data (
  error_record_sk BIGINT,
  error_id STRING,
  pipeline_layer STRING,
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
  pipeline_run_timestamp TIMESTAMP,
  file_path STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (pipeline_layer);
```

**Purpose**

| Table | Purpose |
|---|---|
| `silver.si_error_data` | Stores Silver and Gold validation failures including duplicates, non-negative rule failures, invalid mappings, unapplied trace exceptions, reconciliation issues, and data conformance errors |

### 4.3 Audit Table DDL script

#### 4.3.1 `silver.si_pipeline_audit`
```sql
CREATE TABLE IF NOT EXISTS silver.si_pipeline_audit (
  audit_sk BIGINT,
  pipeline_run_id STRING,
  pipeline_name STRING,
  pipeline_layer STRING,
  source_table_name STRING,
  target_table_name STRING,
  processing_status STRING,
  reconciliation_status STRING,
  processing_start_timestamp TIMESTAMP,
  processing_end_timestamp TIMESTAMP,
  processing_duration_seconds DECIMAL(18,2),
  records_read_count BIGINT,
  records_written_count BIGINT,
  records_rejected_count BIGINT,
  error_message STRING,
  processed_by STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (pipeline_layer);
```

**Purpose**

| Table | Purpose |
|---|---|
| `silver.si_pipeline_audit` | Stores Silver and Gold pipeline execution audit details including run timings, status, reconciliation, and error message capture |

### 4.4 Update DDL script

```sql
-- Example Silver update and merge pattern aligned to AP-1 governed conformance requirements.
MERGE INTO silver.si_customer_master AS tgt
USING (
  SELECT
    CAST(NULL AS BIGINT) AS customer_sk,
    customer_id,
    customer_name,
    credit_terms,
    credit_limit,
    TO_DATE(customer_since) AS customer_since,
    customer_status,
    file_path,
    file_modification_time,
    CURRENT_TIMESTAMP() AS load_date,
    CURRENT_TIMESTAMP() AS update_date,
    source_system
  FROM bronze.bz_customer_master
) AS src
ON tgt.customer_id = src.customer_id
WHEN MATCHED THEN UPDATE SET
  tgt.customer_name = src.customer_name,
  tgt.credit_terms = src.credit_terms,
  tgt.credit_limit = src.credit_limit,
  tgt.customer_since = src.customer_since,
  tgt.customer_status = src.customer_status,
  tgt.file_path = src.file_path,
  tgt.file_modification_time = src.file_modification_time,
  tgt.update_date = src.update_date,
  tgt.source_system = src.source_system
WHEN NOT MATCHED THEN INSERT (
  customer_sk,
  customer_id,
  customer_name,
  credit_terms,
  credit_limit,
  customer_since,
  customer_status,
  file_path,
  file_modification_time,
  load_date,
  update_date,
  source_system
) VALUES (
  src.customer_sk,
  src.customer_id,
  src.customer_name,
  src.credit_terms,
  src.credit_limit,
  src.customer_since,
  src.customer_status,
  src.file_path,
  src.file_modification_time,
  src.load_date,
  src.update_date,
  src.source_system
);
```

## 5. Transformation, Validation, Join, and Filter Design

### 5.1 Intermediate Transformations
| Area | Transformation |
|---|---|
| Date standardization | Convert Bronze string dates to `DATE` in Silver where business meaning is clearly date-based |
| Numeric standardization | Promote monetary values to `DECIMAL(18,2)` for reporting consistency |
| Conformance | Standardize customer, contract, invoice, receipt, employee, branch, and region usage for downstream governed reporting |
| Lineage preservation | Retain `file_path`, `file_modification_time`, and `source_system` |
| Audit enrichment | Add `load_date` and `update_date` in all Silver tables |

### 5.2 Required Business Validations from AP-1 and Constraints
| Validation Area | Rule |
|---|---|
| Branch validity | Branch must exist in organization hierarchy and be active for the selected date |
| Invoice to contract | Invoice amounts must tie to a valid `contract_id` after Silver conformance |
| Credit memo sign | Credit memo amounts must be negative; standard invoice amounts non-negative |
| Customer conformance | Every outstanding invoice must map to a valid customer; duplicate customer records must be resolved before exposure aggregation |
| Aging bucket support | Aging bucket boundaries are fixed as 0-30, 31-60, 61-90, and 90+ and must not overlap |
| Payment validity | Payment amount must be non-negative |
| Payment application | A payment can apply to zero, one, or more invoices; partial application must be tracked |
| Unapplied cash | Unapplied cash must be flagged and reported separately rather than silently excluded |
| Reconciliation | Drill-through totals must reconcile to downstream source fact totals where required |

### 5.3 Join Design
| Left Table | Right Table | Join Key | Purpose |
|---|---|---|---|
| `silver.si_rental_contracts` | `silver.si_customer_master` | `customer_id` | Contract-customer reporting conformance |
| `silver.si_rental_contracts` | `silver.si_branch_employee` | `sales_rep_id` = `employee_id` | Sales rep alignment for revenue reporting |
| `silver.si_invoices` | `silver.si_rental_contracts` | `contract_id` | Billing to contract linkage |
| `silver.si_invoices` | `silver.si_customer_master` | `customer_id` | AR aging and customer exposure linkage |
| `silver.si_cash_receipts` | `silver.si_invoices` | `invoice_id` | Payment application to invoice linkage |
| `silver.si_cash_receipts` | `silver.si_customer_master` | `customer_id` | Customer cash collection reporting |
| `silver.si_branch_employee` | `silver.si_customer_master` | business assignment / regional rollup context | Collector and branch-region reporting alignment |

### 5.4 Filters and Exclusions
| Rule | Handling |
|---|---|
| Duplicate records | Sent to `silver.si_error_data` or quarantined per processing logic |
| Invalid contract or customer mappings | Captured in `silver.si_error_data` |
| Unapplied cash | Retained as valid analytical condition, not filtered out |
| Zero/invalid denominators in downstream rates | Flagged through audit/error processing rather than enforced via table constraints |

## 6. Data Retention Policies

### 6.1 Retention periods for the Silver layer
| Table Category | Retention Period | Rationale |
|---|---|---|
| Core Silver conformed tables | 7 years | Supports trend reporting, reconciliation, and historical analytical restatement needs |
| Silver error data | 2 years | Supports remediation, auditability, and defect investigation |
| Silver pipeline audit | 2 years | Supports observability, SLA review, and operational audit history |

### 6.2 Archiving strategies
| Data Set | Strategy |
|---|---|
| Historical Silver partitions | Archive cold partitions to lower-cost Delta storage tier while preserving queryability through governed access patterns |
| Error data | Archive resolved historical error records by year and pipeline layer |
| Audit data | Archive old audit partitions by pipeline layer and year for compliance and support review |

## 7. Conceptual Data Model Diagram in tabular form showing relationships
| Source Entity/Table | Connected To | Key Field | Relationship Type | Relationship Description |
|---|---|---|---|---|
| `silver.si_customer_master` | `silver.si_rental_contracts` | `customer_id` | 1-M | One customer can hold multiple contracts |
| `silver.si_branch_employee` | `silver.si_rental_contracts` | `employee_id` = `sales_rep_id` | 1-M | One sales representative can align to multiple contracts |
| `silver.si_rental_contracts` | `silver.si_invoices` | `contract_id` | 1-M | One contract can generate multiple invoices |
| `silver.si_customer_master` | `silver.si_invoices` | `customer_id` | 1-M | One customer can have multiple invoices |
| `silver.si_invoices` | `silver.si_cash_receipts` | `invoice_id` | 1-M | One invoice can be paid by multiple receipts and a receipt may remain unapplied |
| `silver.si_customer_master` | `silver.si_cash_receipts` | `customer_id` | 1-M | One customer can have multiple cash receipts |
| `silver.si_branch_employee` | `silver.si_customer_master` | `region` / collector assignment context | 1-M logical rollup | Branch and region assignment supports collections, security, and reporting rollup |

## 8. Assumptions and Design Decisions
| Category | Detail |
|---|---|
| Bronze authority | The Bronze physical model is treated as the authoritative structural input for required source columns |
| ID fields | Surrogate keys were added as physical id fields because the instructions explicitly require id fields in the Silver physical model |
| Metadata columns | `load_date`, `update_date`, and `source_system` were included in every Silver table as required |
| Spark SQL limitation handling | Traditional PK/FK/check constraints and conventional RDBMS indexes are not included because they are not part of the required Databricks Spark SQL physical output |
| Index design | Performance guidance is expressed using Databricks optimization patterns such as `OPTIMIZE` and `ZORDER BY` |
| Versioning | No overwrite performed; new output file created |

## 9. Databricks Spark SQL Limitations Excluded from Final Design
| Unsupported / Not Preferred for this design | Handling |
|---|---|
| Primary keys | Excluded |
| Foreign keys | Excluded |
| Traditional enforced check constraints for all business rules | Implemented as validation logic / error handling instead |
| Traditional RDBMS indexes | Replaced by Delta optimization guidance |

## 10. Jira Tickets Read
| Ticket Key | Summary | Status |
|---|---|---|
| AP-1 | Reporting Requirements for Rental Revenue-to-Cash | To Do |

## 11. apiCost
apiCost: 0.000000

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_Model Physical_Test_1.sql](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model%20Physical_Test_1.sql)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical
pipelineID : 12357
