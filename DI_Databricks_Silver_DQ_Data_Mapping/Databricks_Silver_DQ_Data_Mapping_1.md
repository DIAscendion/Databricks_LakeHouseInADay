_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Bronze-to-Silver data mapping for Rental Revenue-to-Cash with cleansing, validation, business rules, error handling, and audit guidance for Databricks Silver layer.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Data Mapping

## 1. Overview
This document provides the detailed Bronze-to-Silver data mapping for the Rental Revenue-to-Cash domain in Databricks Medallion architecture. It aligns the Bronze physical model with the Silver physical model and adds attribute-level cleansing, validation, datatype standardization, business rules, error handling, and audit logging guidance. The mapping is implementation-ready for PySpark and Delta Lake processing.

### Key Considerations
- Preserve lineage from Bronze to Silver using `source_system`, `file_path`, and `file_modification_time`.
- Standardize all business date strings into Silver `DATE` fields using controlled parsing logic.
- Normalize financial fields to `DECIMAL(18,2)`.
- Route invalid records to `silver.si_data_quality_errors`.
- Capture execution metrics in `silver.si_process_audit`.
- Maintain traceability for all field-level transformations.
- No Cognos `.report` file was provided in the inputs; therefore mandatory Cognos extraction and cross-reference processing was not executed.

## 2. Assumptions and Processing Notes
1. Input artifacts available for mapping are:
   - `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md`
   - `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md`
2. No previous DQ recommender agent output was provided in the accessible inputs; validations were inferred from the physical model, Silver design intent, and standard finance-domain data quality practices.
3. No Cognos `.report` file was detected in the provided inputs.
4. Silver surrogate key columns are system-generated in Databricks and therefore do not have direct Bronze source fields.
5. `load_date` and `update_date` in Silver are populated from pipeline processing timestamps, while Bronze `load_timestamp` and `update_timestamp` remain source lineage references.

## 3. Error Handling and Logging Recommendations

### 3.1 Error Handling
- Reject records failing mandatory key validation, invalid date parsing, invalid numeric casting, or unsupported domain values.
- Store rejected records in `silver.si_data_quality_errors` with payload, failed rule name, severity, and source context.
- Classify severity as:
  - `HIGH`: Missing primary business identifier, unparseable required date, invalid foreign-reference-ready key
  - `MEDIUM`: Invalid optional domain value, non-critical formatting issue
  - `LOW`: Standardization issue auto-corrected by trimming or uppercasing
- Preserve original Bronze payload for remediation.

### 3.2 Audit Logging
- Log each source-to-target table load in `silver.si_process_audit`.
- Capture:
  - pipeline name
  - source table
  - target table
  - process start/end timestamp
  - records read/written/rejected
  - execution status
  - error message if failed
- Generate `run_id` per execution for replay and traceability.

## 4. Data Mapping for the Silver Layer (Bronze to Silver)

### 4.1 Rental Contracts Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_rental_contracts` | `rental_contract_sk` | Bronze | `bronze.bz_rental_contracts` | `[SYSTEM GENERATED]` | Must be generated and not null | Generate surrogate key using deterministic sequence/identity strategy during Silver load |
| Silver | `silver.si_rental_contracts` | `contract_id` | Bronze | `bronze.bz_rental_contracts` | `contract_id` | Not null; Not empty after trim; Unique within active source snapshot | `trim(contract_id)`; reject if null/blank |
| Silver | `silver.si_rental_contracts` | `customer_id` | Bronze | `bronze.bz_rental_contracts` | `customer_id` | Not null; Not empty after trim | `trim(customer_id)` |
| Silver | `silver.si_rental_contracts` | `branch_code` | Bronze | `bronze.bz_rental_contracts` | `branch_code` | Not null; Valid alphanumeric/code format | `upper(trim(branch_code))` |
| Silver | `silver.si_rental_contracts` | `sales_rep_id` | Bronze | `bronze.bz_rental_contracts` | `sales_rep_id` | Nullable; if present must match employee identifier format | `trim(sales_rep_id)` |
| Silver | `silver.si_rental_contracts` | `equipment_class` | Bronze | `bronze.bz_rental_contracts` | `equipment_class` | Nullable; if present must be standardized text | `upper(trim(equipment_class))` |
| Silver | `silver.si_rental_contracts` | `contract_start_date` | Bronze | `bronze.bz_rental_contracts` | `contract_start_date` | Not null; Valid parseable date | Parse from string using approved formats; reject if unparseable |
| Silver | `silver.si_rental_contracts` | `contract_end_date` | Bronze | `bronze.bz_rental_contracts` | `contract_end_date` | Nullable; if present must be valid parseable date and >= contract_start_date | Parse to date; flag if before start date |
| Silver | `silver.si_rental_contracts` | `contract_status` | Bronze | `bronze.bz_rental_contracts` | `contract_status` | Not null; Valid domain value (`ACTIVE`, `CLOSED`, `CANCELLED`, `PENDING`) or enterprise-approved equivalent | `upper(trim(contract_status))`; map source variants to standard status |
| Silver | `silver.si_rental_contracts` | `daily_rate` | Bronze | `bronze.bz_rental_contracts` | `daily_rate` | Nullable; if present numeric; >= 0 | Cast to `DECIMAL(18,2)`; reject non-numeric; default not applied |
| Silver | `silver.si_rental_contracts` | `load_date` | Bronze | `bronze.bz_rental_contracts` | `load_timestamp` | Not null at target load time | Set from pipeline processing timestamp or Bronze load timestamp per ingestion standard |
| Silver | `silver.si_rental_contracts` | `update_date` | Bronze | `bronze.bz_rental_contracts` | `update_timestamp` | Not null at target upsert/update time | Set to current pipeline timestamp during insert/update |
| Silver | `silver.si_rental_contracts` | `source_system` | Bronze | `bronze.bz_rental_contracts` | `source_system` | Not null; Valid source system code | `upper(trim(source_system))` |
| Silver | `silver.si_rental_contracts` | `file_path` | Bronze | `bronze.bz_rental_contracts` | `file_path` | Not null for lineage | Pass through as-is or normalized path string |
| Silver | `silver.si_rental_contracts` | `file_modification_time` | Bronze | `bronze.bz_rental_contracts` | `file_modification_time` | Nullable; if present valid timestamp | Cast/retain as timestamp |

### 4.2 Invoices Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_invoices` | `invoice_sk` | Bronze | `bronze.bz_invoices` | `[SYSTEM GENERATED]` | Must be generated and not null | Generate surrogate key during Silver load |
| Silver | `silver.si_invoices` | `invoice_id` | Bronze | `bronze.bz_invoices` | `invoice_id` | Not null; Not empty after trim; Unique within source snapshot | `trim(invoice_id)` |
| Silver | `silver.si_invoices` | `contract_id` | Bronze | `bronze.bz_invoices` | `contract_id` | Nullable; if present should align to contract domain | `trim(contract_id)` |
| Silver | `silver.si_invoices` | `customer_id` | Bronze | `bronze.bz_invoices` | `customer_id` | Not null; Not empty after trim | `trim(customer_id)` |
| Silver | `silver.si_invoices` | `invoice_date` | Bronze | `bronze.bz_invoices` | `invoice_date` | Not null; Valid parseable date | Parse to date using controlled formats |
| Silver | `silver.si_invoices` | `due_date` | Bronze | `bronze.bz_invoices` | `due_date` | Nullable; if present valid parseable date and >= invoice_date preferred | Parse to date; flag if due_date < invoice_date |
| Silver | `silver.si_invoices` | `invoice_amount` | Bronze | `bronze.bz_invoices` | `invoice_amount` | Not null; Numeric; business-allowed signed amount based on invoice_type | Cast to `DECIMAL(18,2)` |
| Silver | `silver.si_invoices` | `tax_amount` | Bronze | `bronze.bz_invoices` | `tax_amount` | Nullable; Numeric; >= 0 unless credit adjustment rules apply | Cast to `DECIMAL(18,2)` |
| Silver | `silver.si_invoices` | `invoice_type` | Bronze | `bronze.bz_invoices` | `invoice_type` | Not null; Valid domain (`INVOICE`, `CREDIT_MEMO`, `DEBIT_MEMO`) or approved equivalent | `upper(trim(invoice_type))`; standardize aliases |
| Silver | `silver.si_invoices` | `currency` | Bronze | `bronze.bz_invoices` | `currency` | Not null; ISO currency format preferred length=3 | `upper(trim(currency))` |
| Silver | `silver.si_invoices` | `load_date` | Bronze | `bronze.bz_invoices` | `load_timestamp` | Not null at target load time | Set from pipeline timestamp or Bronze load timestamp |
| Silver | `silver.si_invoices` | `update_date` | Bronze | `bronze.bz_invoices` | `update_timestamp` | Not null at target upsert/update time | Set to current pipeline timestamp |
| Silver | `silver.si_invoices` | `source_system` | Bronze | `bronze.bz_invoices` | `source_system` | Not null; Valid source system code | `upper(trim(source_system))` |
| Silver | `silver.si_invoices` | `file_path` | Bronze | `bronze.bz_invoices` | `file_path` | Not null for lineage | Pass through |
| Silver | `silver.si_invoices` | `file_modification_time` | Bronze | `bronze.bz_invoices` | `file_modification_time` | Nullable; if present valid timestamp | Retain as timestamp |
| Silver | `silver.si_invoices` | `aging_bucket` | Bronze | `bronze.bz_invoices` | `[DERIVED]` | Must conform to approved bucket list | Derive from `datediff(current_date, due_date)` using enterprise aging logic |
| Silver | `silver.si_invoices` | `days_past_due` | Bronze | `bronze.bz_invoices` | `[DERIVED]` | Integer; may be negative for not-yet-due invoices | Derive as `datediff(current_date, due_date)` |

### 4.3 Cash Receipts Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_cash_receipts` | `cash_receipt_sk` | Bronze | `bronze.bz_cash_receipts` | `[SYSTEM GENERATED]` | Must be generated and not null | Generate surrogate key during Silver load |
| Silver | `silver.si_cash_receipts` | `receipt_id` | Bronze | `bronze.bz_cash_receipts` | `receipt_id` | Not null; Not empty after trim; Unique within source snapshot | `trim(receipt_id)` |
| Silver | `silver.si_cash_receipts` | `invoice_id` | Bronze | `bronze.bz_cash_receipts` | `invoice_id` | Nullable; if present should align to invoice domain | `trim(invoice_id)` |
| Silver | `silver.si_cash_receipts` | `customer_id` | Bronze | `bronze.bz_cash_receipts` | `customer_id` | Not null; Not empty after trim | `trim(customer_id)` |
| Silver | `silver.si_cash_receipts` | `receipt_date` | Bronze | `bronze.bz_cash_receipts` | `receipt_date` | Not null; Valid parseable date | Parse to `DATE` |
| Silver | `silver.si_cash_receipts` | `payment_amount` | Bronze | `bronze.bz_cash_receipts` | `payment_amount` | Not null; Numeric; >= 0 unless reversal logic exists | Cast to `DECIMAL(18,2)` |
| Silver | `silver.si_cash_receipts` | `payment_method` | Bronze | `bronze.bz_cash_receipts` | `payment_method` | Nullable; if present must be approved payment method | `upper(trim(payment_method))` |
| Silver | `silver.si_cash_receipts` | `load_date` | Bronze | `bronze.bz_cash_receipts` | `load_timestamp` | Not null at load time | Set from pipeline timestamp or Bronze load timestamp |
| Silver | `silver.si_cash_receipts` | `update_date` | Bronze | `bronze.bz_cash_receipts` | `update_timestamp` | Not null at update time | Set from pipeline timestamp |
| Silver | `silver.si_cash_receipts` | `source_system` | Bronze | `bronze.bz_cash_receipts` | `source_system` | Not null; Valid source system code | `upper(trim(source_system))` |
| Silver | `silver.si_cash_receipts` | `file_path` | Bronze | `bronze.bz_cash_receipts` | `file_path` | Not null for lineage | Pass through |
| Silver | `silver.si_cash_receipts` | `file_modification_time` | Bronze | `bronze.bz_cash_receipts` | `file_modification_time` | Nullable; valid timestamp if present | Retain as timestamp |
| Silver | `silver.si_cash_receipts` | `match_status` | Bronze | `bronze.bz_cash_receipts` | `[DERIVED]` | Must be one of `MATCHED`, `UNMATCHED`, `PARTIAL`, `UNAPPLIED` | Derive based on invoice linkage and amount application logic |
| Silver | `silver.si_cash_receipts` | `unapplied_payment_amount` | Bronze | `bronze.bz_cash_receipts` | `[DERIVED]` | Numeric; >= 0 | Calculate unapplied portion of payment after invoice application |

### 4.4 Customer Master Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_customer_master` | `customer_sk` | Bronze | `bronze.bz_customer_master` | `[SYSTEM GENERATED]` | Must be generated and not null | Generate surrogate key during Silver load |
| Silver | `silver.si_customer_master` | `customer_id` | Bronze | `bronze.bz_customer_master` | `customer_id` | Not null; Not empty after trim; Unique within master snapshot | `trim(customer_id)` |
| Silver | `silver.si_customer_master` | `customer_name` | Bronze | `bronze.bz_customer_master` | `customer_name` | Not null; Not empty after trim | `initcap(trim(customer_name))` or enterprise standard casing |
| Silver | `silver.si_customer_master` | `credit_terms` | Bronze | `bronze.bz_customer_master` | `credit_terms` | Nullable; if present must match approved credit term codes | `upper(trim(credit_terms))` |
| Silver | `silver.si_customer_master` | `credit_limit` | Bronze | `bronze.bz_customer_master` | `credit_limit` | Nullable; Numeric; >= 0 | Cast to `DECIMAL(18,2)` |
| Silver | `silver.si_customer_master` | `customer_since` | Bronze | `bronze.bz_customer_master` | `customer_since` | Nullable; if present valid parseable date | Parse to `DATE` |
| Silver | `silver.si_customer_master` | `customer_status` | Bronze | `bronze.bz_customer_master` | `customer_status` | Not null; Valid domain (`ACTIVE`, `INACTIVE`, `SUSPENDED`, `CLOSED`) or approved equivalent | `upper(trim(customer_status))`; map synonyms |
| Silver | `silver.si_customer_master` | `load_date` | Bronze | `bronze.bz_customer_master` | `load_timestamp` | Not null at load time | Set from pipeline timestamp or Bronze load timestamp |
| Silver | `silver.si_customer_master` | `update_date` | Bronze | `bronze.bz_customer_master` | `update_timestamp` | Not null at update time | Set from pipeline timestamp |
| Silver | `silver.si_customer_master` | `source_system` | Bronze | `bronze.bz_customer_master` | `source_system` | Not null; Valid source system code | `upper(trim(source_system))` |
| Silver | `silver.si_customer_master` | `file_path` | Bronze | `bronze.bz_customer_master` | `file_path` | Not null for lineage | Pass through |
| Silver | `silver.si_customer_master` | `file_modification_time` | Bronze | `bronze.bz_customer_master` | `file_modification_time` | Nullable; if present valid timestamp | Retain as timestamp |
| Silver | `silver.si_customer_master` | `over_limit_indicator` | Bronze | `bronze.bz_customer_master` | `[DERIVED]` | Must be `Y` or `N` | Set `Y` when outstanding exposure exceeds `credit_limit`, else `N` |

### 4.5 Branch Employee Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_branch_employee` | `branch_employee_sk` | Bronze | `bronze.bz_branch_employee` | `[SYSTEM GENERATED]` | Must be generated and not null | Generate surrogate key during Silver load |
| Silver | `silver.si_branch_employee` | `employee_id` | Bronze | `bronze.bz_branch_employee` | `employee_id` | Not null; Not empty after trim | `trim(employee_id)` |
| Silver | `silver.si_branch_employee` | `employee_name` | Bronze | `bronze.bz_branch_employee` | `employee_name` | Not null; Not empty after trim | `initcap(trim(employee_name))` |
| Silver | `silver.si_branch_employee` | `role` | Bronze | `bronze.bz_branch_employee` | `role` | Not null; Valid role domain | `upper(trim(role))` |
| Silver | `silver.si_branch_employee` | `branch_code` | Bronze | `bronze.bz_branch_employee` | `branch_code` | Not null; Valid branch code format | `upper(trim(branch_code))` |
| Silver | `silver.si_branch_employee` | `region` | Bronze | `bronze.bz_branch_employee` | `region` | Not null; Valid region domain | `upper(trim(region))` |
| Silver | `silver.si_branch_employee` | `collector_id` | Bronze | `bronze.bz_branch_employee` | `collector_id` | Nullable; if present valid employee identifier format | `trim(collector_id)` |
| Silver | `silver.si_branch_employee` | `effective_date` | Bronze | `bronze.bz_branch_employee` | `effective_date` | Nullable; if present valid parseable date | Parse to `DATE` |
| Silver | `silver.si_branch_employee` | `load_date` | Bronze | `bronze.bz_branch_employee` | `load_timestamp` | Not null at load time | Set from pipeline timestamp or Bronze load timestamp |
| Silver | `silver.si_branch_employee` | `update_date` | Bronze | `bronze.bz_branch_employee` | `update_timestamp` | Not null at update time | Set from pipeline timestamp |
| Silver | `silver.si_branch_employee` | `source_system` | Bronze | `bronze.bz_branch_employee` | `source_system` | Not null; Valid source system code | `upper(trim(source_system))` |
| Silver | `silver.si_branch_employee` | `file_path` | Bronze | `bronze.bz_branch_employee` | `file_path` | Not null for lineage | Pass through |
| Silver | `silver.si_branch_employee` | `file_modification_time` | Bronze | `bronze.bz_branch_employee` | `file_modification_time` | Nullable; if present valid timestamp | Retain as timestamp |

### 4.6 Error Data Table Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_data_quality_errors` | `error_sk` | Bronze | `[MULTIPLE]` | `[SYSTEM GENERATED]` | Not null | Generate surrogate error key |
| Silver | `silver.si_data_quality_errors` | `source_table` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null | Populate with failing Bronze source table name |
| Silver | `silver.si_data_quality_errors` | `source_record_id` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null when business key available | Capture natural key such as `contract_id`, `invoice_id`, `receipt_id`, `customer_id`, or `employee_id` |
| Silver | `silver.si_data_quality_errors` | `source_file_path` | Bronze | `[MULTIPLE]` | `file_path` | Nullable but recommended | Populate from source lineage |
| Silver | `silver.si_data_quality_errors` | `validation_rule_name` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null | Store failed validation identifier |
| Silver | `silver.si_data_quality_errors` | `validation_category` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null | Categorize as Completeness, Validity, Uniqueness, Referential, Conformance |
| Silver | `silver.si_data_quality_errors` | `error_description` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null | Human-readable rule failure description |
| Silver | `silver.si_data_quality_errors` | `error_record_payload` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null | Store serialized input row JSON |
| Silver | `silver.si_data_quality_errors` | `error_severity` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null; Valid domain (`HIGH`,`MEDIUM`,`LOW`) | Assign based on business criticality |
| Silver | `silver.si_data_quality_errors` | `layer_name` | Bronze | `[MULTIPLE]` | `[CONSTANT]` | Not null | Set to `Silver` |
| Silver | `silver.si_data_quality_errors` | `detected_timestamp` | Bronze | `[MULTIPLE]` | `[SYSTEM GENERATED]` | Not null | Set to current timestamp |
| Silver | `silver.si_data_quality_errors` | `processing_status` | Bronze | `[MULTIPLE]` | `[DERIVED]` | Not null; Valid domain (`OPEN`,`REMEDIATED`,`IGNORED`) | Default to `OPEN` on insert |
| Silver | `silver.si_data_quality_errors` | `load_date` | Bronze | `[MULTIPLE]` | `[SYSTEM GENERATED]` | Not null | Set to current timestamp |
| Silver | `silver.si_data_quality_errors` | `update_date` | Bronze | `[MULTIPLE]` | `[SYSTEM GENERATED]` | Not null | Set to current timestamp |
| Silver | `silver.si_data_quality_errors` | `source_system` | Bronze | `[MULTIPLE]` | `source_system` | Nullable; if available should be standardized | Populate from failing source row |

### 4.7 Audit Table Mapping

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Silver | `silver.si_process_audit` | `audit_sk` | Bronze | `bronze.bz_audit_log` | `[SYSTEM GENERATED]` | Not null | Generate surrogate audit key |
| Silver | `silver.si_process_audit` | `pipeline_name` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Not null | Set to Silver pipeline/job name |
| Silver | `silver.si_process_audit` | `source_table` | Bronze | `bronze.bz_audit_log` | `source_table` | Not null | Standardize source table reference |
| Silver | `silver.si_process_audit` | `target_table` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Not null | Populate Silver target table name |
| Silver | `silver.si_process_audit` | `process_start_timestamp` | Bronze | `bronze.bz_audit_log` | `load_timestamp` | Not null | Map Bronze load timestamp or orchestration start time |
| Silver | `silver.si_process_audit` | `process_end_timestamp` | Bronze | `bronze.bz_audit_log` | `processing_time` | Not null | Map processing completion timestamp |
| Silver | `silver.si_process_audit` | `processing_status` | Bronze | `bronze.bz_audit_log` | `status` | Not null; Valid domain (`SUCCESS`,`FAILED`,`PARTIAL`) | `upper(trim(status))` |
| Silver | `silver.si_process_audit` | `records_read_count` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Numeric; >= 0 | Populate from orchestration metrics |
| Silver | `silver.si_process_audit` | `records_written_count` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Numeric; >= 0 | Populate from successful writes |
| Silver | `silver.si_process_audit` | `records_rejected_count` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Numeric; >= 0 | Populate from DQ rejection counts |
| Silver | `silver.si_process_audit` | `processing_duration_seconds` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Numeric; >= 0 | Compute from start/end timestamps |
| Silver | `silver.si_process_audit` | `error_message` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Nullable | Populate only for failed/partial runs |
| Silver | `silver.si_process_audit` | `executed_by` | Bronze | `bronze.bz_audit_log` | `processed_by` | Not null | `trim(processed_by)` |
| Silver | `silver.si_process_audit` | `audit_remarks` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Nullable | Add load summary remarks |
| Silver | `silver.si_process_audit` | `load_date` | Bronze | `bronze.bz_audit_log` | `load_timestamp` | Not null | Retain or standardize to current load timestamp |
| Silver | `silver.si_process_audit` | `update_date` | Bronze | `bronze.bz_audit_log` | `processing_time` | Not null | Populate from completion timestamp |
| Silver | `silver.si_process_audit` | `source_system` | Bronze | `bronze.bz_audit_log` | `[DERIVED]` | Nullable | Set from pipeline context if available |
| Silver | `silver.si_process_audit` | `run_id` | Bronze | `bronze.bz_audit_log` | `record_id` | Not null | Reuse Bronze record id or generated pipeline run id |

## 5. Complex Validation and Business Rule Explanations

### 5.1 Date Parsing Standardization
Bronze date attributes are stored as strings. Silver must parse dates using a prioritized format list such as `yyyy-MM-dd`, `MM/dd/yyyy`, and `yyyyMMdd`. If none match for a required field, the record must be rejected into the error table.

### 5.2 Domain Standardization
Statuses, payment methods, roles, and invoice types should be trimmed and uppercased before validation. Source synonyms should be mapped to enterprise standard values; unmapped values should be rejected or flagged depending on business criticality.

### 5.3 Financial Amount Rules
Amounts should be cast using safe decimal conversion. Non-numeric values must be rejected. Negative values are allowed only where supported by business context such as credit memos or reversal entries.

### 5.4 Referential Readiness
While no physical foreign key constraints are enforced in Databricks Silver, business-key alignment checks should be performed during transformation. For example, invoice `customer_id` should exist in customer master, and receipt `invoice_id` should align to invoice data when populated. Failures may be logged as DQ exceptions based on orchestration policy.

### 5.5 Derived Attributes
- `aging_bucket` derived from invoice due date aging bands.
- `days_past_due` derived from current date minus due date.
- `match_status` derived from payment application completeness.
- `unapplied_payment_amount` derived from receipt amount less applied amount.
- `over_limit_indicator` derived by comparing exposure against credit limit.

## 6. PySpark / Databricks Implementation Guidance
- Use `trim`, `upper`, `initcap`, `to_date`, `when`, `col`, `cast`, and `datediff` for transformations.
- Use `withColumn` for derived values and standardization.
- Use conditional splits to separate valid and invalid records before writing.
- Write valid records to Silver Delta tables and invalid records to `silver.si_data_quality_errors`.
- Use `MERGE INTO` where incremental updates are required.
- Optimize frequently queried Silver tables with `OPTIMIZE` and `ZORDER` as specified in the Silver physical model.

## 7. API Cost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_DQ_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_DQ_Data_Mapping/Databricks_Silver_DQ_Data_Mapping_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping
pipelineID : 12361
