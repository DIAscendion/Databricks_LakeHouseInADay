_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Silver layer data mapping from Bronze to Silver for Rental Revenue-to-Cash with cleansing, validations, business rules, error handling, and audit logging.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Data Mapping

## 1) Overview
This document provides a comprehensive Bronze-to-Silver data mapping for the Rental Revenue-to-Cash domain in Databricks Medallion architecture. It uses the Bronze physical model, Silver physical model, and prior Silver DQ recommender guidance to define target mappings, type conversions, cleansing rules, validation rules, transformation logic, exception handling, and audit logging requirements. The Silver layer standardizes raw Bronze data into conformed Delta tables suitable for downstream reporting, AR aging, collections, cash application, and credit risk analytics.

### Key Considerations
- All Bronze business columns are mapped into corresponding Silver conformed tables.
- Raw Bronze string dates are normalized to Silver `DATE` fields where business meaning is stable.
- Financial measures are standardized to `DECIMAL(18,2)`.
- Validation rules are aligned to Databricks PySpark and Delta processing patterns.
- Invalid, duplicate, orphaned, or rule-breaking records must be redirected to `silver.si_error_data`.
- Pipeline execution metrics and reconciliation outcomes must be logged in `silver.si_pipeline_audit`.
- No Cognos `.report` file was provided in the inputs for this run; therefore, mandatory Cognos parsing and cross-reference sections are not applicable for this version.

## 2) Input Analysis Summary

| Input Source | Purpose | Outcome Applied in Mapping |
|---|---|---|
| `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` | Defines Bronze raw source tables, column names, and raw datatypes | Used as authoritative source for Bronze tables and source columns |
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Defines Silver physical target tables and datatypes | Used to determine Silver target tables, target fields, and type conversions |
| Previous Silver DQ Recommender output | Defines recommended DQ checks and business rules | Used to populate validation rules, cleansing rules, business rule logic, and error-handling guidance |

## 3) Source-to-Target Processing Approach

### 3.1 Standard Cleansing Applied in Silver
1. Trim leading and trailing whitespace from all string business columns.
2. Convert blank strings to null for nullable descriptive fields.
3. Normalize string case for controlled domain columns where appropriate, such as `contract_status`, `invoice_type`, `customer_status`, and `role`.
4. Cast raw Bronze date strings into Silver `DATE` fields using safe parsing logic.
5. Standardize monetary and rate values to `DECIMAL(18,2)`.
6. Preserve lineage metadata columns from Bronze.
7. Derive `load_date` and `update_date` from Bronze timestamps where required by the Silver physical model.

### 3.2 Validation and Business Rule Enforcement
1. Mandatory fields must not be null for critical business identifiers and required reporting attributes.
2. Domain checks apply to status, role, currency, and transaction-type fields.
3. Referential checks ensure invoices map to valid contracts and customers, and applied receipts map to valid invoices.
4. Sign-based business rules apply to invoice amounts, payment amounts, and credit limits.
5. Date sequence checks apply to contract dates and payment-versus-invoice timing.
6. Duplicate-prevention checks are required on key business identifiers such as `receipt_id`, `invoice_id`, and conformed `customer_id`.

### 3.3 Error Handling and Logging Recommendations
- Failed rows must be written to `silver.si_error_data` with rule name, rejected value, business key, severity, source table, target table, and error description.
- Every Silver pipeline run must log start/end timestamps, records read, records written, rejected counts, status, and error messages into `silver.si_pipeline_audit`.
- Unapplied cash is a valid business exception and should be retained with explicit flagging rather than discarded.
- Reconciliation status should compare Bronze input counts to Silver accepted + rejected record counts.

## 4) Data Mapping for the Silver Layer (Bronze to Silver)

### 4.1 Mapping: `bronze.bz_rental_contracts` -> `silver.si_rental_contracts`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_rental_contracts` | `rental_contract_sk` | Bronze | `bronze.bz_rental_contracts` | `[derived]` | Must be generated and not null for accepted Silver rows | Generate surrogate key during Silver ETL |
| Silver | `silver.si_rental_contracts` | `contract_id` | Bronze | `bronze.bz_rental_contracts` | `contract_id` | Not null; business key completeness | `trim(contract_id)` |
| Silver | `silver.si_rental_contracts` | `customer_id` | Bronze | `bronze.bz_rental_contracts` | `customer_id` | Not null; must map to valid customer for conformed downstream use | `trim(customer_id)` |
| Silver | `silver.si_rental_contracts` | `branch_code` | Bronze | `bronze.bz_rental_contracts` | `branch_code` | Not null; valid branch format; branch conformance recommended | `upper(trim(branch_code))` |
| Silver | `silver.si_rental_contracts` | `sales_rep_id` | Bronze | `bronze.bz_rental_contracts` | `sales_rep_id` | Nullable; if present must map to branch employee assignment | `trim(sales_rep_id)` |
| Silver | `silver.si_rental_contracts` | `equipment_class` | Bronze | `bronze.bz_rental_contracts` | `equipment_class` | Nullable; standardized domain recommended | `trim(equipment_class)` |
| Silver | `silver.si_rental_contracts` | `contract_start_date` | Bronze | `bronze.bz_rental_contracts` | `contract_start_date` | Valid date format when present | `to_date(contract_start_date)` |
| Silver | `silver.si_rental_contracts` | `contract_end_date` | Bronze | `bronze.bz_rental_contracts` | `contract_end_date` | Valid date format when present; must be >= start date when both exist | `to_date(contract_end_date)` |
| Silver | `silver.si_rental_contracts` | `contract_status` | Bronze | `bronze.bz_rental_contracts` | `contract_status` | Allowed values such as Open or Closed; not null preferred | `upper(trim(contract_status))` |
| Silver | `silver.si_rental_contracts` | `daily_rate` | Bronze | `bronze.bz_rental_contracts` | `daily_rate` | Non-negative | `cast(daily_rate as decimal(18,2))` |
| Silver | `silver.si_rental_contracts` | `source_system` | Bronze | `bronze.bz_rental_contracts` | `source_system` | Not null for lineage | `trim(source_system)` |
| Silver | `silver.si_rental_contracts` | `file_path` | Bronze | `bronze.bz_rental_contracts` | `file_path` | Not null recommended for lineage | `trim(file_path)` |
| Silver | `silver.si_rental_contracts` | `file_modification_time` | Bronze | `bronze.bz_rental_contracts` | `file_modification_time` | Valid timestamp when present | direct map |
| Silver | `silver.si_rental_contracts` | `load_timestamp` | Bronze | `bronze.bz_rental_contracts` | `load_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_rental_contracts` | `update_timestamp` | Bronze | `bronze.bz_rental_contracts` | `update_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_rental_contracts` | `load_date` | Bronze | `bronze.bz_rental_contracts` | `load_timestamp` | Derived date must be valid | `to_date(load_timestamp)` |
| Silver | `silver.si_rental_contracts` | `update_date` | Bronze | `bronze.bz_rental_contracts` | `update_timestamp` | Derived date must be valid | `to_date(update_timestamp)` |

### 4.2 Mapping: `bronze.bz_invoices` -> `silver.si_invoices`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_invoices` | `invoice_sk` | Bronze | `bronze.bz_invoices` | `[derived]` | Must be generated and not null for accepted Silver rows | Generate surrogate key during Silver ETL |
| Silver | `silver.si_invoices` | `invoice_id` | Bronze | `bronze.bz_invoices` | `invoice_id` | Not null; uniqueness recommended at business grain | `trim(invoice_id)` |
| Silver | `silver.si_invoices` | `contract_id` | Bronze | `bronze.bz_invoices` | `contract_id` | Not null; must map to valid contract for accepted records | `trim(contract_id)` |
| Silver | `silver.si_invoices` | `customer_id` | Bronze | `bronze.bz_invoices` | `customer_id` | Not null; must map to valid customer | `trim(customer_id)` |
| Silver | `silver.si_invoices` | `invoice_date` | Bronze | `bronze.bz_invoices` | `invoice_date` | Valid date; not null recommended | `to_date(invoice_date)` |
| Silver | `silver.si_invoices` | `due_date` | Bronze | `bronze.bz_invoices` | `due_date` | Valid date; not null for aging analysis | `to_date(due_date)` |
| Silver | `silver.si_invoices` | `invoice_amount` | Bronze | `bronze.bz_invoices` | `invoice_amount` | Standard invoices non-negative; credit memos negative | `cast(invoice_amount as decimal(18,2))` |
| Silver | `silver.si_invoices` | `tax_amount` | Bronze | `bronze.bz_invoices` | `tax_amount` | Non-negative when present | `cast(tax_amount as decimal(18,2))` |
| Silver | `silver.si_invoices` | `invoice_type` | Bronze | `bronze.bz_invoices` | `invoice_type` | Allowed domain values; required for sign-rule logic | `upper(trim(invoice_type))` |
| Silver | `silver.si_invoices` | `currency` | Bronze | `bronze.bz_invoices` | `currency` | Must match 3-letter uppercase pattern | `upper(trim(currency))` |
| Silver | `silver.si_invoices` | `source_system` | Bronze | `bronze.bz_invoices` | `source_system` | Not null for lineage | `trim(source_system)` |
| Silver | `silver.si_invoices` | `file_path` | Bronze | `bronze.bz_invoices` | `file_path` | Not null recommended for lineage | `trim(file_path)` |
| Silver | `silver.si_invoices` | `file_modification_time` | Bronze | `bronze.bz_invoices` | `file_modification_time` | Valid timestamp when present | direct map |
| Silver | `silver.si_invoices` | `load_timestamp` | Bronze | `bronze.bz_invoices` | `load_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_invoices` | `update_timestamp` | Bronze | `bronze.bz_invoices` | `update_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_invoices` | `load_date` | Bronze | `bronze.bz_invoices` | `load_timestamp` | Derived date must be valid | `to_date(load_timestamp)` |
| Silver | `silver.si_invoices` | `update_date` | Bronze | `bronze.bz_invoices` | `update_timestamp` | Derived date must be valid | `to_date(update_timestamp)` |

### 4.3 Mapping: `bronze.bz_cash_receipts` -> `silver.si_cash_receipts`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_cash_receipts` | `cash_receipt_sk` | Bronze | `bronze.bz_cash_receipts` | `[derived]` | Must be generated and not null for accepted Silver rows | Generate surrogate key during Silver ETL |
| Silver | `silver.si_cash_receipts` | `receipt_id` | Bronze | `bronze.bz_cash_receipts` | `receipt_id` | Not null; unique | `trim(receipt_id)` |
| Silver | `silver.si_cash_receipts` | `invoice_id` | Bronze | `bronze.bz_cash_receipts` | `invoice_id` | Nullable for unapplied cash; if applied must map to valid invoice | `trim(invoice_id)` |
| Silver | `silver.si_cash_receipts` | `customer_id` | Bronze | `bronze.bz_cash_receipts` | `customer_id` | Not null; must map to valid customer | `trim(customer_id)` |
| Silver | `silver.si_cash_receipts` | `receipt_date` | Bronze | `bronze.bz_cash_receipts` | `receipt_date` | Valid date; not null recommended | `to_date(receipt_date)` |
| Silver | `silver.si_cash_receipts` | `payment_amount` | Bronze | `bronze.bz_cash_receipts` | `payment_amount` | Non-negative | `cast(payment_amount as decimal(18,2))` |
| Silver | `silver.si_cash_receipts` | `payment_method` | Bronze | `bronze.bz_cash_receipts` | `payment_method` | Allowed domain recommended | `upper(trim(payment_method))` |
| Silver | `silver.si_cash_receipts` | `source_system` | Bronze | `bronze.bz_cash_receipts` | `source_system` | Not null for lineage | `trim(source_system)` |
| Silver | `silver.si_cash_receipts` | `file_path` | Bronze | `bronze.bz_cash_receipts` | `file_path` | Not null recommended for lineage | `trim(file_path)` |
| Silver | `silver.si_cash_receipts` | `file_modification_time` | Bronze | `bronze.bz_cash_receipts` | `file_modification_time` | Valid timestamp when present | direct map |
| Silver | `silver.si_cash_receipts` | `load_timestamp` | Bronze | `bronze.bz_cash_receipts` | `load_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_cash_receipts` | `update_timestamp` | Bronze | `bronze.bz_cash_receipts` | `update_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_cash_receipts` | `load_date` | Bronze | `bronze.bz_cash_receipts` | `load_timestamp` | Derived date must be valid | `to_date(load_timestamp)` |
| Silver | `silver.si_cash_receipts` | `update_date` | Bronze | `bronze.bz_cash_receipts` | `update_timestamp` | Derived date must be valid | `to_date(update_timestamp)` |

### 4.4 Mapping: `bronze.bz_customer_master` -> `silver.si_customer_master`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_customer_master` | `customer_sk` | Bronze | `bronze.bz_customer_master` | `[derived]` | Must be generated and not null for accepted Silver rows | Generate surrogate key during Silver ETL |
| Silver | `silver.si_customer_master` | `customer_id` | Bronze | `bronze.bz_customer_master` | `customer_id` | Not null; unique after conformance and deduplication | `trim(customer_id)` |
| Silver | `silver.si_customer_master` | `customer_name` | Bronze | `bronze.bz_customer_master` | `customer_name` | Not null | `trim(customer_name)` |
| Silver | `silver.si_customer_master` | `credit_terms` | Bronze | `bronze.bz_customer_master` | `credit_terms` | Controlled domain recommended | `upper(trim(credit_terms))` |
| Silver | `silver.si_customer_master` | `credit_limit` | Bronze | `bronze.bz_customer_master` | `credit_limit` | Non-negative | `cast(credit_limit as decimal(18,2))` |
| Silver | `silver.si_customer_master` | `customer_since` | Bronze | `bronze.bz_customer_master` | `customer_since` | Valid date when present | `to_date(customer_since)` |
| Silver | `silver.si_customer_master` | `customer_status` | Bronze | `bronze.bz_customer_master` | `customer_status` | Allowed values such as Active and Suspended | `upper(trim(customer_status))` |
| Silver | `silver.si_customer_master` | `source_system` | Bronze | `bronze.bz_customer_master` | `source_system` | Not null for lineage | `trim(source_system)` |
| Silver | `silver.si_customer_master` | `file_path` | Bronze | `bronze.bz_customer_master` | `file_path` | Not null recommended for lineage | `trim(file_path)` |
| Silver | `silver.si_customer_master` | `file_modification_time` | Bronze | `bronze.bz_customer_master` | `file_modification_time` | Valid timestamp when present | direct map |
| Silver | `silver.si_customer_master` | `load_timestamp` | Bronze | `bronze.bz_customer_master` | `load_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_customer_master` | `update_timestamp` | Bronze | `bronze.bz_customer_master` | `update_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_customer_master` | `load_date` | Bronze | `bronze.bz_customer_master` | `load_timestamp` | Derived date must be valid | `to_date(load_timestamp)` |
| Silver | `silver.si_customer_master` | `update_date` | Bronze | `bronze.bz_customer_master` | `update_timestamp` | Derived date must be valid | `to_date(update_timestamp)` |

### 4.5 Mapping: `bronze.bz_branch_employee` -> `silver.si_branch_employee`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_branch_employee` | `branch_employee_sk` | Bronze | `bronze.bz_branch_employee` | `[derived]` | Must be generated and not null for accepted Silver rows | Generate surrogate key during Silver ETL |
| Silver | `silver.si_branch_employee` | `employee_id` | Bronze | `bronze.bz_branch_employee` | `employee_id` | Not null | `trim(employee_id)` |
| Silver | `silver.si_branch_employee` | `employee_name` | Bronze | `bronze.bz_branch_employee` | `employee_name` | Not null recommended | `trim(employee_name)` |
| Silver | `silver.si_branch_employee` | `role` | Bronze | `bronze.bz_branch_employee` | `role` | Allowed values such as SALES_REP and COLLECTOR | `upper(trim(role))` |
| Silver | `silver.si_branch_employee` | `branch_code` | Bronze | `bronze.bz_branch_employee` | `branch_code` | Not null; valid branch conformance recommended | `upper(trim(branch_code))` |
| Silver | `silver.si_branch_employee` | `region` | Bronze | `bronze.bz_branch_employee` | `region` | Not null; standardized region required for rollups | `upper(trim(region))` |
| Silver | `silver.si_branch_employee` | `collector_id` | Bronze | `bronze.bz_branch_employee` | `collector_id` | Nullable; if present should be standardized | `trim(collector_id)` |
| Silver | `silver.si_branch_employee` | `effective_date` | Bronze | `bronze.bz_branch_employee` | `effective_date` | Valid date when present | `to_date(effective_date)` |
| Silver | `silver.si_branch_employee` | `source_system` | Bronze | `bronze.bz_branch_employee` | `source_system` | Not null for lineage | `trim(source_system)` |
| Silver | `silver.si_branch_employee` | `file_path` | Bronze | `bronze.bz_branch_employee` | `file_path` | Not null recommended for lineage | `trim(file_path)` |
| Silver | `silver.si_branch_employee` | `file_modification_time` | Bronze | `bronze.bz_branch_employee` | `file_modification_time` | Valid timestamp when present | direct map |
| Silver | `silver.si_branch_employee` | `load_timestamp` | Bronze | `bronze.bz_branch_employee` | `load_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_branch_employee` | `update_timestamp` | Bronze | `bronze.bz_branch_employee` | `update_timestamp` | Not null for auditability | direct map |
| Silver | `silver.si_branch_employee` | `load_date` | Bronze | `bronze.bz_branch_employee` | `load_timestamp` | Derived date must be valid | `to_date(load_timestamp)` |
| Silver | `silver.si_branch_employee` | `update_date` | Bronze | `bronze.bz_branch_employee` | `update_timestamp` | Derived date must be valid | `to_date(update_timestamp)` |

### 4.6 Mapping: Error Data Table Population -> `silver.si_error_data`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_error_data` | `error_record_sk` | Bronze | `[any bronze source]` | `[derived]` | Must be generated for each rejected row | Generate surrogate key |
| Silver | `silver.si_error_data` | `layer_name` | Bronze | `[any bronze source]` | `[constant]` | Not null | Set to `Silver` |
| Silver | `silver.si_error_data` | `pipeline_name` | Bronze | `[pipeline context]` | `[derived]` | Not null | Populate from job/notebook context |
| Silver | `silver.si_error_data` | `source_table` | Bronze | `[any bronze source]` | `[derived]` | Not null | Populate actual Bronze source table name |
| Silver | `silver.si_error_data` | `target_table` | Bronze | `[any bronze source]` | `[derived]` | Not null | Populate intended Silver target table name |
| Silver | `silver.si_error_data` | `business_key` | Bronze | `[business key field(s)]` | `[derived]` | Required for traceability | Concatenate business key columns |
| Silver | `silver.si_error_data` | `table_name` | Bronze | `[any bronze source]` | `[derived]` | Not null | Populate failing table name |
| Silver | `silver.si_error_data` | `column_name` | Bronze | `[failing source column]` | `[derived]` | Not null for column-level validation failures | Populate failing column |
| Silver | `silver.si_error_data` | `validation_rule` | Bronze | `[DQ rule metadata]` | `[derived]` | Not null | Populate failed rule name |
| Silver | `silver.si_error_data` | `validation_status` | Bronze | `[constant]` | `[constant]` | Not null | Set to `FAILED` or `QUARANTINED` |
| Silver | `silver.si_error_data` | `rejected_value` | Bronze | `[failing value]` | `[derived]` | Nullable based on sensitivity policy | Cast rejected value to string |
| Silver | `silver.si_error_data` | `error_description` | Bronze | `[DQ context]` | `[derived]` | Not null | Human-readable failure reason |
| Silver | `silver.si_error_data` | `error_category` | Bronze | `[DQ context]` | `[derived]` | Not null | Set categories such as Completeness, Validity, Referential, Duplicate, BusinessRule |
| Silver | `silver.si_error_data` | `severity` | Bronze | `[DQ policy]` | `[derived]` | Not null | Set severity such as High, Medium, Low |
| Silver | `silver.si_error_data` | `source_system` | Bronze | `[source metadata]` | `source_system` | Not null recommended | direct map from rejected row |
| Silver | `silver.si_error_data` | `file_path` | Bronze | `[source metadata]` | `file_path` | Not null recommended | direct map from rejected row |
| Silver | `silver.si_error_data` | `detected_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | Set current_timestamp() |
| Silver | `silver.si_error_data` | `load_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | Set current_timestamp() |
| Silver | `silver.si_error_data` | `update_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | Set current_timestamp() |
| Silver | `silver.si_error_data` | `load_date` | Bronze | `[runtime context]` | `[derived]` | Not null | `current_date()` |
| Silver | `silver.si_error_data` | `update_date` | Bronze | `[runtime context]` | `[derived]` | Not null | `current_date()` |

### 4.7 Mapping: Audit Logging Population -> `silver.si_pipeline_audit`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_pipeline_audit` | `audit_sk` | Bronze | `[pipeline context]` | `[derived]` | Must be generated for each pipeline run record | Generate surrogate key |
| Silver | `silver.si_pipeline_audit` | `pipeline_run_id` | Bronze | `[pipeline context]` | `[derived]` | Not null | Populate runtime run id |
| Silver | `silver.si_pipeline_audit` | `layer_name` | Bronze | `[constant]` | `[constant]` | Not null | Set to `Silver` |
| Silver | `silver.si_pipeline_audit` | `pipeline_name` | Bronze | `[pipeline context]` | `[derived]` | Not null | Populate job/notebook name |
| Silver | `silver.si_pipeline_audit` | `source_table` | Bronze | `[pipeline context]` | `[derived]` | Not null | Populate processed Bronze source |
| Silver | `silver.si_pipeline_audit` | `target_table` | Bronze | `[pipeline context]` | `[derived]` | Not null | Populate processed Silver target |
| Silver | `silver.si_pipeline_audit` | `process_start_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | Set pipeline start timestamp |
| Silver | `silver.si_pipeline_audit` | `process_end_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | Set pipeline end timestamp |
| Silver | `silver.si_pipeline_audit` | `processing_status` | Bronze | `[runtime context]` | `[derived]` | Allowed values such as SUCCESS, FAILED, PARTIAL_SUCCESS | Set final execution status |
| Silver | `silver.si_pipeline_audit` | `records_read` | Bronze | `[runtime metrics]` | `[derived]` | Non-negative integer | Populate row count read |
| Silver | `silver.si_pipeline_audit` | `records_written` | Bronze | `[runtime metrics]` | `[derived]` | Non-negative integer | Populate accepted Silver row count |
| Silver | `silver.si_pipeline_audit` | `records_rejected` | Bronze | `[runtime metrics]` | `[derived]` | Non-negative integer | Populate rejected row count |
| Silver | `silver.si_pipeline_audit` | `processing_time_seconds` | Bronze | `[runtime metrics]` | `[derived]` | Non-negative | Compute timestamp difference |
| Silver | `silver.si_pipeline_audit` | `trigger_type` | Bronze | `[runtime context]` | `[derived]` | Nullable | Populate schedule/manual/event trigger |
| Silver | `silver.si_pipeline_audit` | `processed_by` | Bronze | `[runtime context]` | `[derived]` | Not null recommended | Populate notebook/service principal/job identity |
| Silver | `silver.si_pipeline_audit` | `error_message` | Bronze | `[runtime context]` | `[derived]` | Nullable | Capture exception message when failed |
| Silver | `silver.si_pipeline_audit` | `source_system` | Bronze | `[source metadata]` | `[derived]` | Nullable for multi-source runs | Populate source system if single-source, else `MULTI_SOURCE` |
| Silver | `silver.si_pipeline_audit` | `load_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | current_timestamp() |
| Silver | `silver.si_pipeline_audit` | `update_timestamp` | Bronze | `[runtime context]` | `[derived]` | Not null | current_timestamp() |
| Silver | `silver.si_pipeline_audit` | `load_date` | Bronze | `[runtime context]` | `[derived]` | Not null | current_date() |
| Silver | `silver.si_pipeline_audit` | `update_date` | Bronze | `[runtime context]` | `[derived]` | Not null | current_date() |

## 5) Table-Level Business Rules and DQ Notes

### 5.1 Rental Contracts
- Reject records with null `contract_id`, null `customer_id`, invalid contract dates, or negative `daily_rate`.
- Flag records where `contract_end_date < contract_start_date`.
- Standardize status values for consistent downstream KPI logic.

### 5.2 Invoices
- Reject or quarantine rows with null `invoice_id`, invalid `invoice_date`, invalid `due_date`, invalid currency pattern, or missing contract/customer references.
- Enforce sign logic: standard invoices must be non-negative; credit memos must be negative.

### 5.3 Cash Receipts
- Reject rows with null `receipt_id`, negative `payment_amount`, or invalid `receipt_date`.
- Retain rows with null `invoice_id` as unapplied cash candidates rather than discarding them.

### 5.4 Customer Master
- Deduplicate by `customer_id` according to survivorship rules before promoting to conformed Silver.
- Reject rows with null `customer_id`, null `customer_name`, invalid `customer_since`, or negative `credit_limit`.

### 5.5 Branch Employee
- Reject rows with null `employee_id`, blank `region`, invalid `effective_date`, or unsupported `role` values.
- Use standardized `branch_code` and `region` for reporting conformance.

## 6) PySpark Implementation Guidance
- Use `trim`, `upper`, `to_date`, `cast`, `when`, `rlike`, and anti-joins for DQ enforcement.
- Write accepted records to Silver tables and failed records to `silver.si_error_data`.
- Capture audit metrics in `silver.si_pipeline_audit` at the end of each source-to-target load.
- Recommended approach is to separate critical hard-fail validations from soft business exceptions.

## 7) Assumptions
1. The Bronze physical model is the authoritative source for input columns.
2. The Silver physical model is the authoritative source for target columns and datatypes.
3. The prior Silver DQ Recommender provides the business-rule basis for Silver validation logic.
4. No Cognos `.report` file was provided in the input set for this run, so Cognos metadata extraction and Cognos-to-Silver mapping were not executed.
5. API cost cannot be retrieved in real time from the execution environment, so it is reported as `0.000000 USD` consistent with available prior agent outputs.

## 8) API Cost
apiCost: 0.000000 USD

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping
pipelineID : 12361

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_DQ_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Data_Mapping_Reviewer/Databricks_Silver_DQ_Data_Mapping_1.md)
