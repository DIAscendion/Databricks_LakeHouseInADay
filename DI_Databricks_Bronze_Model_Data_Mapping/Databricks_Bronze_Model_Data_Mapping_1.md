_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Bronze layer one-to-one source-to-target data mapping for Rental Revenue-to-Cash raw ingestion tables.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Data Mapping

## 1. Overview
This document defines the Bronze layer data mapping for the Rental Revenue-to-Cash domain in a Databricks Medallion architecture. The Bronze layer preserves raw source structure with minimal handling, append-only ingestion, and lineage retention for downstream Silver processing.

## 2. Source Summary
Based on the provided conceptual model and Bronze schema SQL, the raw source domain includes:

- Rental contracts
- Invoices and credit memos
- Cash receipts / payment applications
- Customer master records
- Branch employee / sales rep / collector assignments

## 3. Ingestion and Processing Characteristics

| Attribute | Value |
|---|---|
| Target Layer | Bronze |
| Storage Format | Delta Lake |
| Processing Pattern | Append-only raw ingestion |
| Transformation Approach | Minimal / no business transformation |
| Schema Style | Raw-but-typed |
| Data Quality Handling | Deferred to Silver layer |
| Lineage Columns | `file_path`, `file_modification_time`, `source_system` |
| Source Feed Type | Structured batch / CDC extracts |
| Expected Cleansing | None in Bronze |

## 4. Table-Level Mapping Summary

| Target Table | Source Table | Grain | Notes |
|---|---|---|---|
| `sunbelt_demo.bronze.bronze_rental_contracts` | Rental contract header extract | One row per rental contract | Preserves raw contract identifiers, dates, rates, and source lineage |
| `sunbelt_demo.bronze.bronze_invoices` | Invoice header extract | One row per invoice or credit memo | Retains invoice and credit memo values without standardization |
| `sunbelt_demo.bronze.bronze_cash_receipts` | Cash receipt / payment application extract | One row per payment or payment attempt | Includes unapplied cash scenarios where invoice is null |
| `sunbelt_demo.bronze.bronze_customer_master` | Customer master extract | One row per extracted customer record | Duplicate customer records may remain in Bronze |
| `sunbelt_demo.bronze.bronze_branch_employee` | Branch / employee assignment extract | One row per employee per effective feed | Retains stale and duplicate feed records as received |

## 5. Data Mapping for Bronze Layer

### 5.1 `sunbelt_demo.bronze.bronze_rental_contracts`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|---|---|---|---|---|---|---|
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `contract_id` | Source | Rental contract header extract | `contract_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `customer_id` | Source | Rental contract header extract | `customer_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `branch_code` | Source | Rental contract header extract | `branch_code` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `sales_rep_id` | Source | Rental contract header extract | `sales_rep_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `equipment_class` | Source | Rental contract header extract | `equipment_class` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `contract_start_date` | Source | Rental contract header extract | `contract_start_date` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `contract_end_date` | Source | Rental contract header extract | `contract_end_date` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `contract_status` | Source | Rental contract header extract | `contract_status` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `daily_rate` | Source | Rental contract header extract | `daily_rate` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `source_system` | Source | Rental contract header extract | `source_system` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `file_path` | Source | Rental contract header extract | `file_path` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_rental_contracts` | `file_modification_time` | Source | Rental contract header extract | `file_modification_time` | 1-1 Mapping |

### 5.2 `sunbelt_demo.bronze.bronze_invoices`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|---|---|---|---|---|---|---|
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `invoice_id` | Source | Invoice header extract | `invoice_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `contract_id` | Source | Invoice header extract | `contract_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `customer_id` | Source | Invoice header extract | `customer_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `invoice_date` | Source | Invoice header extract | `invoice_date` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `due_date` | Source | Invoice header extract | `due_date` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `invoice_amount` | Source | Invoice header extract | `invoice_amount` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `tax_amount` | Source | Invoice header extract | `tax_amount` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `invoice_type` | Source | Invoice header extract | `invoice_type` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `currency` | Source | Invoice header extract | `currency` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `source_system` | Source | Invoice header extract | `source_system` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `file_path` | Source | Invoice header extract | `file_path` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_invoices` | `file_modification_time` | Source | Invoice header extract | `file_modification_time` | 1-1 Mapping |

### 5.3 `sunbelt_demo.bronze.bronze_cash_receipts`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|---|---|---|---|---|---|---|
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `receipt_id` | Source | Cash receipt / payment application extract | `receipt_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `invoice_id` | Source | Cash receipt / payment application extract | `invoice_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `customer_id` | Source | Cash receipt / payment application extract | `customer_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `receipt_date` | Source | Cash receipt / payment application extract | `receipt_date` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `payment_amount` | Source | Cash receipt / payment application extract | `payment_amount` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `payment_method` | Source | Cash receipt / payment application extract | `payment_method` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `source_system` | Source | Cash receipt / payment application extract | `source_system` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `file_path` | Source | Cash receipt / payment application extract | `file_path` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_cash_receipts` | `file_modification_time` | Source | Cash receipt / payment application extract | `file_modification_time` | 1-1 Mapping |

### 5.4 `sunbelt_demo.bronze.bronze_customer_master`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|---|---|---|---|---|---|---|
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `customer_id` | Source | Customer master extract | `customer_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `customer_name` | Source | Customer master extract | `customer_name` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `credit_terms` | Source | Customer master extract | `credit_terms` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `credit_limit` | Source | Customer master extract | `credit_limit` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `customer_since` | Source | Customer master extract | `customer_since` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `customer_status` | Source | Customer master extract | `customer_status` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `source_system` | Source | Customer master extract | `source_system` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `file_path` | Source | Customer master extract | `file_path` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_customer_master` | `file_modification_time` | Source | Customer master extract | `file_modification_time` | 1-1 Mapping |

### 5.5 `sunbelt_demo.bronze.bronze_branch_employee`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|---|---|---|---|---|---|---|
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `employee_id` | Source | Branch / employee assignment extract | `employee_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `employee_name` | Source | Branch / employee assignment extract | `employee_name` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `role` | Source | Branch / employee assignment extract | `role` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `branch_code` | Source | Branch / employee assignment extract | `branch_code` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `region` | Source | Branch / employee assignment extract | `region` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `collector_id` | Source | Branch / employee assignment extract | `collector_id` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `effective_date` | Source | Branch / employee assignment extract | `effective_date` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `source_system` | Source | Branch / employee assignment extract | `source_system` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `file_path` | Source | Branch / employee assignment extract | `file_path` | 1-1 Mapping |
| Bronze | `sunbelt_demo.bronze.bronze_branch_employee` | `file_modification_time` | Source | Branch / employee assignment extract | `file_modification_time` | 1-1 Mapping |

## 6. Datatype Compatibility Mapping

| Target Table | Target Field | Declared Datatype | Databricks / PySpark Compatibility Note |
|---|---|---|---|
| `bronze_rental_contracts` | `contract_id` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `customer_id` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `branch_code` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `sales_rep_id` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `equipment_class` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `contract_start_date` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_rental_contracts` | `contract_end_date` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_rental_contracts` | `contract_status` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `daily_rate` | `DECIMAL(10,2)` | Stored as Spark decimal for numeric fidelity |
| `bronze_rental_contracts` | `source_system` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `file_path` | `STRING` | Stored as Spark `string` |
| `bronze_rental_contracts` | `file_modification_time` | `TIMESTAMP` | Stored as Spark `timestamp` |
| `bronze_invoices` | `invoice_id` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `contract_id` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `customer_id` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `invoice_date` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_invoices` | `due_date` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_invoices` | `invoice_amount` | `DECIMAL(12,2)` | Stored as Spark decimal for monetary accuracy |
| `bronze_invoices` | `tax_amount` | `DECIMAL(12,2)` | Stored as Spark decimal for monetary accuracy |
| `bronze_invoices` | `invoice_type` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `currency` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `source_system` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `file_path` | `STRING` | Stored as Spark `string` |
| `bronze_invoices` | `file_modification_time` | `TIMESTAMP` | Stored as Spark `timestamp` |
| `bronze_cash_receipts` | `receipt_id` | `STRING` | Stored as Spark `string` |
| `bronze_cash_receipts` | `invoice_id` | `STRING` | Stored as Spark `string` |
| `bronze_cash_receipts` | `customer_id` | `STRING` | Stored as Spark `string` |
| `bronze_cash_receipts` | `receipt_date` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_cash_receipts` | `payment_amount` | `DECIMAL(12,2)` | Stored as Spark decimal for monetary accuracy |
| `bronze_cash_receipts` | `payment_method` | `STRING` | Stored as Spark `string` |
| `bronze_cash_receipts` | `source_system` | `STRING` | Stored as Spark `string` |
| `bronze_cash_receipts` | `file_path` | `STRING` | Stored as Spark `string` |
| `bronze_cash_receipts` | `file_modification_time` | `TIMESTAMP` | Stored as Spark `timestamp` |
| `bronze_customer_master` | `customer_id` | `STRING` | Stored as Spark `string` |
| `bronze_customer_master` | `customer_name` | `STRING` | Stored as Spark `string` |
| `bronze_customer_master` | `credit_terms` | `STRING` | Stored as Spark `string` |
| `bronze_customer_master` | `credit_limit` | `DECIMAL(12,2)` | Stored as Spark decimal for monetary accuracy |
| `bronze_customer_master` | `customer_since` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_customer_master` | `customer_status` | `STRING` | Stored as Spark `string` |
| `bronze_customer_master` | `source_system` | `STRING` | Stored as Spark `string` |
| `bronze_customer_master` | `file_path` | `STRING` | Stored as Spark `string` |
| `bronze_customer_master` | `file_modification_time` | `TIMESTAMP` | Stored as Spark `timestamp` |
| `bronze_branch_employee` | `employee_id` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `employee_name` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `role` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `branch_code` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `region` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `collector_id` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `effective_date` | `STRING` | Preserved as raw string to retain original source format |
| `bronze_branch_employee` | `source_system` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `file_path` | `STRING` | Stored as Spark `string` |
| `bronze_branch_employee` | `file_modification_time` | `TIMESTAMP` | Stored as Spark `timestamp` |

## 7. Assumptions

- Source-to-Bronze mappings are strictly one-to-one and preserve source values as received.
- Date attributes stored as `STRING` remain unparsed in Bronze to preserve mixed source formats.
- No joins, aggregations, deduplication, validations, or business-rule derivations are performed in Bronze.
- Lineage columns are included in each Bronze table to support auditability and traceability.
- Data quality issues documented in the SQL comments are intentionally retained in Bronze and resolved downstream in Silver.

## 8. Joins, Filters, Aggregations, and Transformations

| Category | Bronze Layer Handling |
|---|---|
| Joins | None |
| Filters | None |
| Aggregations | None |
| Standardization | None |
| Deduplication | None |
| Validation Rules | None |
| Business Logic | None |

## 9. Output Format

| Item | Value |
|---|---|
| Physical Storage | Delta tables |
| Table Naming Pattern | `sunbelt_demo.bronze.bronze_<table_name>` |
| Processing Intent | Raw landing with typed columns |
| Downstream Consumer | Silver layer conformance and cleansing |

## 10. API Cost Reporting

```json
{
  "apiCost": 0.0000
}
```

## 11. GitHub File URL

[Databricks_Bronze_Model_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Bronze_Model_Data_Mapping/Databricks_Bronze_Model_Data_Mapping_1.md)
