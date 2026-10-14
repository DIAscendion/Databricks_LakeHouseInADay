_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Silver layer Bronze-to-Silver data mapping for Rental Revenue-to-Cash with cleansing, validations, business rules, error handling, and audit logging.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Data Mapping

## 1) Overview
This document defines the Bronze-to-Silver attribute-level data mapping for the Rental Revenue-to-Cash domain in Databricks Medallion architecture. It uses the Bronze physical model, Silver physical model, and prior Silver DQ recommender guidance to specify source-to-target traceability, PySpark-compatible validation rules, cleansing logic, standardization, exception routing, and audit logging behavior. The Silver layer preserves Bronze lineage, standardizes dates and numeric precision, enforces domain and referential controls, and supports downstream reporting for revenue, billing, AR aging, cash application, and credit risk.

### Key Considerations
- Bronze-to-Silver mapping is limited to provided Bronze and Silver physical structures.
- All mappings are aligned to Databricks and PySpark processing patterns.
- Validation failures should be routed to `silver.si_error_data` rather than silently discarded.
- Pipeline execution and reconciliation metrics should be logged to `silver.si_pipeline_audit`.
- No Cognos `.report` file was provided in the inputs for this run; therefore mandatory Cognos parsing and cross-reference steps were not triggered.

## 2) Data Mapping for the Silver Layer (Bronze to Silver)

### 2.1 `silver.si_rental_contracts`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_rental_contracts` | `rental_contract_sk` | Bronze | `bronze.bz_rental_contracts` | `[Derived]` | Must be populated for successful Silver load; unique within target table | Generate surrogate key during Silver load using deterministic sequence/identity strategy |
| Silver | `silver.si_rental_contracts` | `contract_id` | Bronze | `bronze.bz_rental_contracts` | `contract_id` | Not null; unique business key at source grain; trim blanks | `trim(contract_id)` |
| Silver | `silver.si_rental_contracts` | `customer_id` | Bronze | `bronze.bz_rental_contracts` | `customer_id` | Not null; must map to valid `silver.si_customer_master.customer_id` for conformed records | `trim(customer_id)` |
| Silver | `silver.si_rental_contracts` | `branch_code` | Bronze | `bronze.bz_rental_contracts` | `branch_code` | Not null; must be active and valid in organizational hierarchy per business rule | `upper(trim(branch_code))` |
| Silver | `silver.si_rental_contracts` | `sales_rep_id` | Bronze | `bronze.bz_rental_contracts` | `sales_rep_id` | Nullable; if present must match `silver.si_branch_employee.employee_id` | `trim(sales_rep_id)` |
| Silver | `silver.si_rental_contracts` | `equipment_class` | Bronze | `bronze.bz_rental_contracts` | `equipment_class` | Nullable but recommended valid domain standardization | `upper(trim(equipment_class))` |
| Silver | `silver.si_rental_contracts` | `contract_start_date` | Bronze | `bronze.bz_rental_contracts` | `contract_start_date` | Valid date format; not null when contract is active | `to_date(contract_start_date)` |
| Silver | `silver.si_rental_contracts` | `contract_end_date` | Bronze | `bronze.bz_rental_contracts` | `contract_end_date` | Valid date format if present; must be >= `contract_start_date` when both exist | `to_date(contract_end_date)` |
| Silver | `silver.si_rental_contracts` | `contract_status` | Bronze | `bronze.bz_rental_contracts` | `contract_status` | Allowed values `OPEN`, `CLOSED`; reject unexpected values for manual review | `upper(trim(contract_status))` |
| Silver | `silver.si_rental_contracts` | `daily_rate` | Bronze | `bronze.bz_rental_contracts` | `daily_rate` | Non-negative; valid decimal precision | `cast(daily_rate as decimal(18,2))` |
| Silver | `silver.si_rental_contracts` | `source_system` | Bronze | `bronze.bz_rental_contracts` | `source_system` | Not null; lineage mandatory | `upper(trim(source_system))` |
| Silver | `silver.si_rental_contracts` | `file_path` | Bronze | `bronze.bz_rental_contracts` | `file_path` | Not null for lineage traceability | `trim(file_path)` |
| Silver | `silver.si_rental_contracts` | `file_modification_time` | Bronze | `bronze.bz_rental_contracts` | `file_modification_time` | Valid timestamp | Direct map |
| Silver | `silver.si_rental_contracts` | `load_timestamp` | Bronze | `bronze.bz_rental_contracts` | `load_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_rental_contracts` | `update_timestamp` | Bronze | `bronze.bz_rental_contracts` | `update_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_rental_contracts` | `load_date` | Bronze | `bronze.bz_rental_contracts` | `load_timestamp` | Not null | `to_date(load_timestamp)` |
| Silver | `silver.si_rental_contracts` | `update_date` | Bronze | `bronze.bz_rental_contracts` | `update_timestamp` | Not null | `to_date(update_timestamp)` |

### 2.2 `silver.si_invoices`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_invoices` | `invoice_sk` | Bronze | `bronze.bz_invoices` | `[Derived]` | Must be populated for successful Silver load; unique within target table | Generate surrogate key during Silver load |
| Silver | `silver.si_invoices` | `invoice_id` | Bronze | `bronze.bz_invoices` | `invoice_id` | Not null; unique at transaction grain | `trim(invoice_id)` |
| Silver | `silver.si_invoices` | `contract_id` | Bronze | `bronze.bz_invoices` | `contract_id` | Not null; must map to valid contract unless routed to error table | `trim(contract_id)` |
| Silver | `silver.si_invoices` | `customer_id` | Bronze | `bronze.bz_invoices` | `customer_id` | Not null; every outstanding invoice must map to valid customer | `trim(customer_id)` |
| Silver | `silver.si_invoices` | `invoice_date` | Bronze | `bronze.bz_invoices` | `invoice_date` | Valid date format; not null | `to_date(invoice_date)` |
| Silver | `silver.si_invoices` | `due_date` | Bronze | `bronze.bz_invoices` | `due_date` | Valid date format; not null; should be >= invoice date when business permits | `to_date(due_date)` |
| Silver | `silver.si_invoices` | `invoice_amount` | Bronze | `bronze.bz_invoices` | `invoice_amount` | Standard invoices must be non-negative; credit memos must be negative | `cast(invoice_amount as decimal(18,2))` |
| Silver | `silver.si_invoices` | `tax_amount` | Bronze | `bronze.bz_invoices` | `tax_amount` | Non-negative; valid decimal precision | `cast(tax_amount as decimal(18,2))` |
| Silver | `silver.si_invoices` | `invoice_type` | Bronze | `bronze.bz_invoices` | `invoice_type` | Not null; allowed values aligned to invoice and credit memo processing | `upper(trim(invoice_type))` |
| Silver | `silver.si_invoices` | `currency` | Bronze | `bronze.bz_invoices` | `currency` | Must match `^[A-Z]{3}$`; not null | `upper(trim(currency))` |
| Silver | `silver.si_invoices` | `source_system` | Bronze | `bronze.bz_invoices` | `source_system` | Not null | `upper(trim(source_system))` |
| Silver | `silver.si_invoices` | `file_path` | Bronze | `bronze.bz_invoices` | `file_path` | Not null for lineage | `trim(file_path)` |
| Silver | `silver.si_invoices` | `file_modification_time` | Bronze | `bronze.bz_invoices` | `file_modification_time` | Valid timestamp | Direct map |
| Silver | `silver.si_invoices` | `load_timestamp` | Bronze | `bronze.bz_invoices` | `load_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_invoices` | `update_timestamp` | Bronze | `bronze.bz_invoices` | `update_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_invoices` | `load_date` | Bronze | `bronze.bz_invoices` | `load_timestamp` | Not null | `to_date(load_timestamp)` |
| Silver | `silver.si_invoices` | `update_date` | Bronze | `bronze.bz_invoices` | `update_timestamp` | Not null | `to_date(update_timestamp)` |

### 2.3 `silver.si_cash_receipts`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_cash_receipts` | `cash_receipt_sk` | Bronze | `bronze.bz_cash_receipts` | `[Derived]` | Must be populated for successful Silver load; unique within target table | Generate surrogate key during Silver load |
| Silver | `silver.si_cash_receipts` | `receipt_id` | Bronze | `bronze.bz_cash_receipts` | `receipt_id` | Not null; unique receipt identifier | `trim(receipt_id)` |
| Silver | `silver.si_cash_receipts` | `invoice_id` | Bronze | `bronze.bz_cash_receipts` | `invoice_id` | Nullable because unapplied cash is allowed; if present should map to valid invoice | `trim(invoice_id)` |
| Silver | `silver.si_cash_receipts` | `customer_id` | Bronze | `bronze.bz_cash_receipts` | `customer_id` | Not null; must map to valid customer | `trim(customer_id)` |
| Silver | `silver.si_cash_receipts` | `receipt_date` | Bronze | `bronze.bz_cash_receipts` | `receipt_date` | Valid date format; not null | `to_date(receipt_date)` |
| Silver | `silver.si_cash_receipts` | `payment_amount` | Bronze | `bronze.bz_cash_receipts` | `payment_amount` | Non-negative | `cast(payment_amount as decimal(18,2))` |
| Silver | `silver.si_cash_receipts` | `payment_method` | Bronze | `bronze.bz_cash_receipts` | `payment_method` | Allowed value/domain standardization recommended | `upper(trim(payment_method))` |
| Silver | `silver.si_cash_receipts` | `source_system` | Bronze | `bronze.bz_cash_receipts` | `source_system` | Not null | `upper(trim(source_system))` |
| Silver | `silver.si_cash_receipts` | `file_path` | Bronze | `bronze.bz_cash_receipts` | `file_path` | Not null for lineage | `trim(file_path)` |
| Silver | `silver.si_cash_receipts` | `file_modification_time` | Bronze | `bronze.bz_cash_receipts` | `file_modification_time` | Valid timestamp | Direct map |
| Silver | `silver.si_cash_receipts` | `load_timestamp` | Bronze | `bronze.bz_cash_receipts` | `load_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_cash_receipts` | `update_timestamp` | Bronze | `bronze.bz_cash_receipts` | `update_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_cash_receipts` | `load_date` | Bronze | `bronze.bz_cash_receipts` | `load_timestamp` | Not null | `to_date(load_timestamp)` |
| Silver | `silver.si_cash_receipts` | `update_date` | Bronze | `bronze.bz_cash_receipts` | `update_timestamp` | Not null | `to_date(update_timestamp)` |

### 2.4 `silver.si_customer_master`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_customer_master` | `customer_sk` | Bronze | `bronze.bz_customer_master` | `[Derived]` | Must be populated for successful Silver load; unique within target table | Generate surrogate key during Silver load |
| Silver | `silver.si_customer_master` | `customer_id` | Bronze | `bronze.bz_customer_master` | `customer_id` | Not null; unique after Silver conformance and deduplication | `trim(customer_id)` |
| Silver | `silver.si_customer_master` | `customer_name` | Bronze | `bronze.bz_customer_master` | `customer_name` | Not null; trim blank names | `initcap(trim(customer_name))` |
| Silver | `silver.si_customer_master` | `credit_terms` | Bronze | `bronze.bz_customer_master` | `credit_terms` | Nullable but should align to approved payment terms domain | `upper(trim(credit_terms))` |
| Silver | `silver.si_customer_master` | `credit_limit` | Bronze | `bronze.bz_customer_master` | `credit_limit` | Non-negative | `cast(credit_limit as decimal(18,2))` |
| Silver | `silver.si_customer_master` | `customer_since` | Bronze | `bronze.bz_customer_master` | `customer_since` | Valid date format if present | `to_date(customer_since)` |
| Silver | `silver.si_customer_master` | `customer_status` | Bronze | `bronze.bz_customer_master` | `customer_status` | Allowed values `ACTIVE`, `SUSPENDED`; not null | `upper(trim(customer_status))` |
| Silver | `silver.si_customer_master` | `source_system` | Bronze | `bronze.bz_customer_master` | `source_system` | Not null | `upper(trim(source_system))` |
| Silver | `silver.si_customer_master` | `file_path` | Bronze | `bronze.bz_customer_master` | `file_path` | Not null for lineage | `trim(file_path)` |
| Silver | `silver.si_customer_master` | `file_modification_time` | Bronze | `bronze.bz_customer_master` | `file_modification_time` | Valid timestamp | Direct map |
| Silver | `silver.si_customer_master` | `load_timestamp` | Bronze | `bronze.bz_customer_master` | `load_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_customer_master` | `update_timestamp` | Bronze | `bronze.bz_customer_master` | `update_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_customer_master` | `load_date` | Bronze | `bronze.bz_customer_master` | `load_timestamp` | Not null | `to_date(load_timestamp)` |
| Silver | `silver.si_customer_master` | `update_date` | Bronze | `bronze.bz_customer_master` | `update_timestamp` | Not null | `to_date(update_timestamp)` |

### 2.5 `silver.si_branch_employee`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_branch_employee` | `branch_employee_sk` | Bronze | `bronze.bz_branch_employee` | `[Derived]` | Must be populated for successful Silver load; unique within target table | Generate surrogate key during Silver load |
| Silver | `silver.si_branch_employee` | `employee_id` | Bronze | `bronze.bz_branch_employee` | `employee_id` | Not null | `trim(employee_id)` |
| Silver | `silver.si_branch_employee` | `employee_name` | Bronze | `bronze.bz_branch_employee` | `employee_name` | Not null; trim blanks | `initcap(trim(employee_name))` |
| Silver | `silver.si_branch_employee` | `role` | Bronze | `bronze.bz_branch_employee` | `role` | Allowed values such as `SALES_REP`, `COLLECTOR`; not null | `upper(trim(role))` |
| Silver | `silver.si_branch_employee` | `branch_code` | Bronze | `bronze.bz_branch_employee` | `branch_code` | Not null; valid branch code | `upper(trim(branch_code))` |
| Silver | `silver.si_branch_employee` | `region` | Bronze | `bronze.bz_branch_employee` | `region` | Not null; required for rollup reporting | `upper(trim(region))` |
| Silver | `silver.si_branch_employee` | `collector_id` | Bronze | `bronze.bz_branch_employee` | `collector_id` | Nullable; if present must be consistent with role/assignment rules | `trim(collector_id)` |
| Silver | `silver.si_branch_employee` | `effective_date` | Bronze | `bronze.bz_branch_employee` | `effective_date` | Valid date format; not null | `to_date(effective_date)` |
| Silver | `silver.si_branch_employee` | `source_system` | Bronze | `bronze.bz_branch_employee` | `source_system` | Not null | `upper(trim(source_system))` |
| Silver | `silver.si_branch_employee` | `file_path` | Bronze | `bronze.bz_branch_employee` | `file_path` | Not null for lineage | `trim(file_path)` |
| Silver | `silver.si_branch_employee` | `file_modification_time` | Bronze | `bronze.bz_branch_employee` | `file_modification_time` | Valid timestamp | Direct map |
| Silver | `silver.si_branch_employee` | `load_timestamp` | Bronze | `bronze.bz_branch_employee` | `load_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_branch_employee` | `update_timestamp` | Bronze | `bronze.bz_branch_employee` | `update_timestamp` | Valid timestamp; not null | Direct map |
| Silver | `silver.si_branch_employee` | `load_date` | Bronze | `bronze.bz_branch_employee` | `load_timestamp` | Not null | `to_date(load_timestamp)` |
| Silver | `silver.si_branch_employee` | `update_date` | Bronze | `bronze.bz_branch_employee` | `update_timestamp` | Not null | `to_date(update_timestamp)` |

### 2.6 `silver.si_error_data`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_error_data` | `error_record_sk` | Bronze | `[Multiple Bronze Tables]` | `[Derived]` | Unique surrogate key | Generate surrogate key for each error record |
| Silver | `silver.si_error_data` | `layer_name` | Bronze | `[Derived from pipeline context]` | `[Derived]` | Not null | Set constant `Silver` |
| Silver | `silver.si_error_data` | `pipeline_name` | Bronze | `[Derived from pipeline context]` | `[Derived]` | Not null | Populate from executing job/notebook name |
| Silver | `silver.si_error_data` | `source_table` | Bronze | `[Any Bronze source]` | `[Derived]` | Not null | Populate actual Bronze source table name that failed validation |
| Silver | `silver.si_error_data` | `target_table` | Bronze | `[Any Bronze source]` | `[Derived]` | Not null | Populate intended Silver target table |
| Silver | `silver.si_error_data` | `business_key` | Bronze | `[Any Bronze source]` | `[Derived from natural key]` | Recommended not null | Concatenate business key columns for traceability |
| Silver | `silver.si_error_data` | `table_name` | Bronze | `[Any Bronze source]` | `[Derived]` | Not null | Populate table under validation |
| Silver | `silver.si_error_data` | `column_name` | Bronze | `[Any Bronze source]` | `[Derived]` | Nullable for row-level errors | Populate failing column name when applicable |
| Silver | `silver.si_error_data` | `validation_rule` | Bronze | `[Derived]` | `[Derived]` | Not null | Store failed rule name such as `NOT_NULL`, `DATE_FORMAT`, `REFERENTIAL_INTEGRITY` |
| Silver | `silver.si_error_data` | `validation_status` | Bronze | `[Derived]` | `[Derived]` | Not null | Set values such as `FAILED`, `QUARANTINED`, `REPROCESSED` |
| Silver | `silver.si_error_data` | `rejected_value` | Bronze | `[Any Bronze source]` | `[Derived]` | Nullable | Cast rejected field value to string |
| Silver | `silver.si_error_data` | `error_description` | Bronze | `[Derived]` | `[Derived]` | Not null | Human-readable error explanation |
| Silver | `silver.si_error_data` | `error_category` | Bronze | `[Derived]` | `[Derived]` | Not null | Classify as completeness, format, domain, duplicate, referential, business_rule |
| Silver | `silver.si_error_data` | `severity` | Bronze | `[Derived]` | `[Derived]` | Not null | Populate severity such as High, Medium, Low |
| Silver | `silver.si_error_data` | `source_system` | Bronze | `[Any Bronze source]` | `source_system` | Not null when available | Direct map from source record |
| Silver | `silver.si_error_data` | `file_path` | Bronze | `[Any Bronze source]` | `file_path` | Not null when available | Direct map from source record |
| Silver | `silver.si_error_data` | `detected_timestamp` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_timestamp()` when issue detected |
| Silver | `silver.si_error_data` | `load_timestamp` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_timestamp()` |
| Silver | `silver.si_error_data` | `update_timestamp` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_timestamp()` |
| Silver | `silver.si_error_data` | `load_date` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_date()` |
| Silver | `silver.si_error_data` | `update_date` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_date()` |

### 2.7 `silver.si_pipeline_audit`
| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_pipeline_audit` | `audit_sk` | Bronze | `[Pipeline Context]` | `[Derived]` | Unique surrogate key | Generate surrogate key |
| Silver | `silver.si_pipeline_audit` | `pipeline_run_id` | Bronze | `[Pipeline Context]` | `[Derived]` | Not null | Populate unique run identifier |
| Silver | `silver.si_pipeline_audit` | `layer_name` | Bronze | `[Pipeline Context]` | `[Derived]` | Not null | Set constant `Silver` |
| Silver | `silver.si_pipeline_audit` | `pipeline_name` | Bronze | `[Pipeline Context]` | `[Derived]` | Not null | Populate notebook/job/pipeline name |
| Silver | `silver.si_pipeline_audit` | `source_table` | Bronze | `[Any Bronze source]` | `[Derived]` | Not null | Populate processed Bronze source table |
| Silver | `silver.si_pipeline_audit` | `target_table` | Bronze | `[Any Silver target]` | `[Derived]` | Not null | Populate loaded Silver target table |
| Silver | `silver.si_pipeline_audit` | `process_start_timestamp` | Bronze | `[Pipeline Context]` | `[Derived]` | Not null | Set pipeline start timestamp |
| Silver | `silver.si_pipeline_audit` | `process_end_timestamp` | Bronze | `[Pipeline Context]` | `[Derived]` | Not null | Set pipeline end timestamp |
| Silver | `silver.si_pipeline_audit` | `processing_status` | Bronze | `[Derived]` | `[Derived]` | Allowed values `SUCCESS`, `FAILED`, `PARTIAL_SUCCESS` | Derive from pipeline execution result |
| Silver | `silver.si_pipeline_audit` | `records_read` | Bronze | `[Any Bronze source]` | `[Derived]` | Non-negative | Count input rows read |
| Silver | `silver.si_pipeline_audit` | `records_written` | Bronze | `[Any Silver target]` | `[Derived]` | Non-negative | Count output rows written |
| Silver | `silver.si_pipeline_audit` | `records_rejected` | Bronze | `[Any Bronze source]` | `[Derived]` | Non-negative | Count rejected rows written to error table |
| Silver | `silver.si_pipeline_audit` | `processing_time_seconds` | Bronze | `[Pipeline Context]` | `[Derived]` | Non-negative | Compute end minus start in seconds |
| Silver | `silver.si_pipeline_audit` | `trigger_type` | Bronze | `[Pipeline Context]` | `[Derived]` | Nullable but recommended | Set trigger source such as schedule/manual/event |
| Silver | `silver.si_pipeline_audit` | `processed_by` | Bronze | `[Pipeline Context]` | `[Derived]` | Not null | Populate service principal, workflow, or notebook identity |
| Silver | `silver.si_pipeline_audit` | `error_message` | Bronze | `[Derived]` | `[Derived]` | Nullable | Populate exception summary when failed |
| Silver | `silver.si_pipeline_audit` | `source_system` | Bronze | `[Any Bronze source]` | `source_system` | Nullable for consolidated runs | Populate dominant or grouped source system |
| Silver | `silver.si_pipeline_audit` | `load_timestamp` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_timestamp()` |
| Silver | `silver.si_pipeline_audit` | `update_timestamp` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_timestamp()` |
| Silver | `silver.si_pipeline_audit` | `load_date` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_date()` |
| Silver | `silver.si_pipeline_audit` | `update_date` | Bronze | `[Derived]` | `[Derived]` | Not null | `current_date()` |

## 3) Cleansing, Validation, and Business Rule Notes

### 3.1 Initial Cleansing Steps
- Trim leading and trailing spaces from all string business keys and code fields.
- Standardize code and domain fields to uppercase where case-insensitive matching is needed.
- Convert customer and employee display names to normalized presentation case where appropriate.
- Convert Bronze string dates to valid `DATE` values using PySpark `to_date` with controlled parsing logic.
- Promote Bronze numeric amounts from `DECIMAL(10,2)` or `DECIMAL(12,2)` to `DECIMAL(18,2)` for Silver consistency.
- Preserve lineage columns exactly for audit and reconciliation.

### 3.2 Core Business Rules Applied
- Invoice records must reference valid contracts after Silver conformance.
- Credit memo amounts must be negative and standard invoice amounts must be non-negative.
- Every outstanding invoice must resolve to a valid customer.
- Payment amount must be non-negative.
- Unapplied cash is valid and must be retained, but explicitly flagged downstream rather than dropped.
- Duplicate customer records must be resolved before exposure aggregation in downstream layers.
- Branch and region values must remain conformed for governed reporting rollups.

### 3.3 Error Handling Recommendations
- Route failed records to `silver.si_error_data` with source table, business key, failed rule, rejected value, and severity.
- Use reject/quarantine patterns for hard failures such as null mandatory keys, invalid date casts, duplicate natural keys, and broken referential integrity.
- Preserve analytically valid exceptions such as unapplied cash with explicit flags instead of rejecting them.
- Maintain replay support by storing record payload context and source lineage.

### 3.4 Audit Logging Recommendations
- Insert one audit row per source-target processing unit into `silver.si_pipeline_audit`.
- Capture read, written, and rejected counts.
- Capture reconciliation status for source-to-target row count checks.
- Persist processing start/end timestamps and error messages for failed or partial runs.

## 4) Assumptions
1. The provided Bronze and Silver physical model files are the authoritative inputs for structural mapping.
2. The prior Silver DQ recommender output supplied in context is used as the validation-rule basis for this mapping.
3. No Cognos `.report` input file was provided in this run, so mandatory Cognos parsing output is not applicable.
4. Surrogate keys in Silver are ETL-generated and therefore mapped as derived fields.
5. `load_date` and `update_date` are derived from Bronze timestamps to satisfy the Silver physical model.

## 5) API Cost
apiCost: 0.000000 USD

**outputURL** : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping
**pipelineID** : 12361

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_DQ_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_DQ_Data_Mapping_Reviewer/Databricks_Silver_DQ_Data_Mapping_1.md)
