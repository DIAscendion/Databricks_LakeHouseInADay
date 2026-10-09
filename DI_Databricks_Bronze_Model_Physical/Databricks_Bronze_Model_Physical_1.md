_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Physical Bronze layer data model for Rental Revenue-to-Cash raw Delta tables and lineage-ready ingestion design.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Physical

## 1. Overview
This document translates the Rental Revenue-to-Cash conceptual model and provided Bronze schema into a physical Bronze layer design for Databricks. The Bronze layer stores raw structured extracts from legacy rental, billing, cash receipt, customer master, and HR/assignment feeds as Delta tables with minimal transformation and with added metadata for governance, lineage, and auditability.

## 2. Source Systems and Input Analysis

| Source File | Type | Purpose | Key Observations |
|---|---|---|---|
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Conceptual model | Defines entities, measures, and relationships for Rental Revenue-to-Cash reporting | Includes Region, Branch, Customer, Contract, Invoice, Cash Receipt, Employee/Collector, and analytical fact concepts |
| `Input/rental_revenue_to_cash_bronze_schema.sql` | Physical source schema reference | Defines raw Bronze-oriented landing tables and source grain | Confirms 5 raw source tables already identified for contracts, invoices, receipts, customers, and employees |

### Identified Raw Data Sources

| Source System | Feed/Table Intent | Landing Table |
|---|---|---|
| `LEGACY_SE`, `LEGACY_MW`, `SUNBELT_CORE` | Rental contract header extracts | `bronze.bz_rental_contracts` |
| Branch/legacy billing systems | Invoice and credit memo extracts | `bronze.bz_invoices` |
| `LOCKBOX_FEED` | Cash receipt/payment extracts | `bronze.bz_cash_receipts` |
| CRM/ERP customer master | Customer reference/master extracts | `bronze.bz_customer_master` |
| `HR_FEED`, `HR_FEED_OLD` | Employee/collector/sales rep assignment extracts | `bronze.bz_branch_employee` |

## 3. Bronze Layer Physical Design Principles
- Bronze stores data as-is from source extracts.
- All tables use `CREATE TABLE IF NOT EXISTS` and `USING DELTA`.
- No primary keys, foreign keys, unique constraints, or check constraints are enforced.
- Source attributes are preserved with raw business column names adapted to Databricks-compatible types.
- Standard metadata columns are included in all tables:
  - `load_timestamp TIMESTAMP`
  - `update_timestamp TIMESTAMP`
  - `source_system STRING`
- Additional ingestion lineage columns from the source schema are retained where relevant:
  - `file_path STRING`
  - `file_modification_time TIMESTAMP`
- An audit table is included for processing traceability.

## 4. Identified Transformations, Filters, Joins, and Aggregation Logic

### Bronze Transformations
Bronze should apply only minimal physical standardization:
- Preserve raw identifiers and status values as received.
- Use typed columns based on structured extract definitions.
- Add governance metadata columns to every table.
- Retain variable-format source date fields as `STRING` where source inconsistency exists.

### Joins Deferred to Silver/Downstream
No business joins are executed in Bronze, but downstream relationships are expected between:
- Contracts and Customers via `customer_id`
- Contracts and Branch Employee via `sales_rep_id` / `employee_id`
- Invoices and Contracts via `contract_id`
- Invoices and Customers via `customer_id`
- Cash Receipts and Invoices via `invoice_id`
- Cash Receipts and Customers via `customer_id`
- Branch Employee and operational hierarchy via `branch_code` and `region`

### Filters
- No business filters should be applied in Bronze.
- Duplicate, orphan, null, stale, and inconsistent records are intentionally retained.

### Aggregations
- No aggregations are performed in Bronze.
- Aggregations such as AR aging, DSO, CEI, revenue trends, and credit exposure remain downstream analytical logic.

### Output Format
- Delta Lake tables in Databricks SQL.
- Markdown documentation output stored in GitHub.

## 5. Table Naming Convention
All Bronze physical tables follow this naming standard:

`bronze.bz_<tablename>`

## 6. Bronze Layer DDL Script

### 6.1 Rental Contracts
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_rental_contracts (
  contract_id STRING,
  customer_id STRING,
  branch_code STRING,
  sales_rep_id STRING,
  equipment_class STRING,
  contract_start_date STRING,
  contract_end_date STRING,
  contract_status STRING,
  daily_rate DECIMAL(10,2),
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA;
```

### 6.2 Invoices
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_invoices (
  invoice_id STRING,
  contract_id STRING,
  customer_id STRING,
  invoice_date STRING,
  due_date STRING,
  invoice_amount DECIMAL(12,2),
  tax_amount DECIMAL(12,2),
  invoice_type STRING,
  currency STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA;
```

### 6.3 Cash Receipts
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_cash_receipts (
  receipt_id STRING,
  invoice_id STRING,
  customer_id STRING,
  receipt_date STRING,
  payment_amount DECIMAL(12,2),
  payment_method STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA;
```

### 6.4 Customer Master
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_customer_master (
  customer_id STRING,
  customer_name STRING,
  credit_terms STRING,
  credit_limit DECIMAL(12,2),
  customer_since STRING,
  customer_status STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA;
```

### 6.5 Branch Employee
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_branch_employee (
  employee_id STRING,
  employee_name STRING,
  role STRING,
  branch_code STRING,
  region STRING,
  collector_id STRING,
  effective_date STRING,
  source_system STRING,
  file_path STRING,
  file_modification_time TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP
)
USING DELTA;
```

### 6.6 Audit Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_audit_log (
  record_id STRING,
  source_table STRING,
  load_timestamp TIMESTAMP,
  processed_by STRING,
  processing_time TIMESTAMP,
  status STRING
)
USING DELTA;
```

## 7. Table-by-Table Physical Model Summary

| Table Name | Grain | Description | Key Raw Columns | Metadata Columns |
|---|---|---|---|---|
| `bronze.bz_rental_contracts` | One row per rental contract | Raw contract header data from rental systems | `contract_id`, `customer_id`, `branch_code`, `sales_rep_id`, `equipment_class`, `contract_status` | `source_system`, `file_path`, `file_modification_time`, `load_timestamp`, `update_timestamp` |
| `bronze.bz_invoices` | One row per invoice or credit memo | Raw billing transactions | `invoice_id`, `contract_id`, `customer_id`, `invoice_amount`, `invoice_type`, `currency` | `source_system`, `file_path`, `file_modification_time`, `load_timestamp`, `update_timestamp` |
| `bronze.bz_cash_receipts` | One row per payment or receipt record | Raw cash collection/application data | `receipt_id`, `invoice_id`, `customer_id`, `payment_amount`, `payment_method` | `source_system`, `file_path`, `file_modification_time`, `load_timestamp`, `update_timestamp` |
| `bronze.bz_customer_master` | One row per extracted customer record | Raw customer master records | `customer_id`, `customer_name`, `credit_terms`, `credit_limit`, `customer_status` | `source_system`, `file_path`, `file_modification_time`, `load_timestamp`, `update_timestamp` |
| `bronze.bz_branch_employee` | One row per employee assignment record | Raw sales rep / collector / branch assignment data | `employee_id`, `employee_name`, `role`, `branch_code`, `region`, `collector_id` | `source_system`, `file_path`, `file_modification_time`, `load_timestamp`, `update_timestamp` |
| `bronze.bz_audit_log` | One row per processing event | Audit and ingestion traceability | `record_id`, `source_table`, `processed_by`, `processing_time`, `status` | `load_timestamp` |

## 8. Conceptual Data Model Diagram (Tabular Form)

| Table A | Key Field | Table B | Relationship Description |
|---|---|---|---|
| `bronze.bz_customer_master` | `customer_id` | `bronze.bz_rental_contracts` | One customer can relate to many contracts |
| `bronze.bz_branch_employee` | `employee_id` = `sales_rep_id` | `bronze.bz_rental_contracts` | One sales rep can manage many contracts |
| `bronze.bz_rental_contracts` | `contract_id` | `bronze.bz_invoices` | One contract can produce many invoices |
| `bronze.bz_customer_master` | `customer_id` | `bronze.bz_invoices` | One customer can have many invoices |
| `bronze.bz_invoices` | `invoice_id` | `bronze.bz_cash_receipts` | One invoice can have many associated cash receipts or payment applications |
| `bronze.bz_customer_master` | `customer_id` | `bronze.bz_cash_receipts` | One customer can have many cash receipts |
| `bronze.bz_branch_employee` | `branch_code` | business branch reporting context | Employee assignments support branch-level reporting alignment |
| `bronze.bz_branch_employee` | `region` | business regional reporting context | Employee assignments support regional rollups |

## 9. Intermediate Transformation View of the Pipeline

| Stage | Input | Processing | Output |
|---|---|---|---|
| Landing/Ingestion | Flat file extracts from rental, billing, lockbox, CRM/ERP, HR feeds | Read structured batch extracts into Databricks | Raw source records available for Bronze ingestion |
| Bronze Load | Source extract records | Type assignment, add metadata columns, preserve raw values | Delta Bronze tables in schema `bronze` |
| Audit Logging | Each Bronze ingestion run | Insert processing status and timestamps into audit table | `bronze.bz_audit_log` |
| Downstream Enablement | Bronze Delta tables | No cleansing in Bronze; joins and quality remediation deferred | Silver standardization and reporting-ready models |

## 10. Assumptions and Design Decisions
1. The provided SQL schema is treated as the authoritative Bronze input structure.
2. Table names were normalized from `bronze_<name>` style to required `bz_<name>` style within schema `bronze`.
3. Raw date columns remain `STRING` where the source notes indicate mixed formats or inconsistent date standards.
4. `source_system` is retained as a business lineage column and included in every table as required.
5. `load_timestamp` and `update_timestamp` were appended to all operational Bronze tables for governance.
6. Constraints are intentionally excluded because Delta Bronze tables typically do not enforce PK/FK rules in raw ingestion layers.
7. Fact entities from the conceptual model are not materialized in Bronze because the supplied schema represents raw operational extracts, not curated analytical fact structures.
8. Branch and Region are represented through raw codes and employee assignment context rather than separate conformed Bronze dimensions in the provided source schema.
9. The audit table is designed for ingestion observability rather than business reporting.

## 11. Compliance and Governance Notes
- Format: Markdown with implementation-ready SQL.
- Storage: Delta Lake only.
- Constraint handling: None enforced.
- Lineage support: `source_system`, `file_path`, `file_modification_time`, `load_timestamp`, and `update_timestamp`.
- Auditability: Separate Bronze audit log included.
- Versioning: File created as version 1 in GitHub.

## 12. API Cost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Bronze_Model_Physical_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Model_Physical
pipelineID : 12300