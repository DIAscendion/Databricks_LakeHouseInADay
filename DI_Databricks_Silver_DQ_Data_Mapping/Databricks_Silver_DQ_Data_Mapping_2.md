_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Silver Layer Data Mapping for TMS Shipment Application (Bronze to Silver)
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Overview
This document provides a comprehensive data mapping from the Bronze Layer to the Silver Layer in the Databricks Medallion architecture for the TMS Shipment Application. It includes attribute-level cleansing, validation, and business rules to ensure data quality, consistency, and usability. The mapping covers all Bronze layer tables, error data, and audit tables, and is designed for compatibility with Databricks PySpark. 

Key considerations:
- All Bronze columns are mapped to Silver for full lineage and traceability.
- Additional Silver fields are mapped from business logic or derived as required.
- Validation and transformation rules are specified for each attribute.
- Error and audit tables are included for robust governance.
- All rules are compatible with PySpark and Databricks SQL.

---

# Cognos Report Extracted Metadata
*No Cognos .report file was provided in the input. This section is not applicable.*

# Cognos Report to Silver Layer Column Mapping Table
*No Cognos .report file was provided in the input. This section is not applicable.*

# Data Mapping for the Silver Layer (Bronze to Silver)

## Table: SHIPMENT (bronze.bz_shipment) → SI_SHIPMENT_PROCESS (silver.si_shipment_process)

| Target Layer | Target Table           | Target Field                | Source Layer | Source Table           | Source Field                | Validation Rule         | Transformation Rule           |
|--------------|-----------------------|-----------------------------|--------------|-----------------------|-----------------------------|-------------------------|-------------------------------|
| Silver       | si_shipment_process   | shipment_process_id         | Derived      | -                     | -                           | Not null, Unique        | Generate UUID                 |
| Silver       | si_shipment_process   | shipment_number             | Bronze       | bz_shipment           | SHIPMENT_ID                 | Not null, Unique        | Uppercase, Trim               |
| Silver       | si_shipment_process   | shipment_date               | Bronze       | bz_shipment           | CREATED_DTTM                | Not null, Valid date    | To Timestamp                  |
| Silver       | si_shipment_process   | origin                      | Bronze       | bz_shipment           | O_CITY                      | Not null                | Title Case, Trim              |
| Silver       | si_shipment_process   | destination                 | Bronze       | bz_shipment           | D_CITY                      | Not null                | Title Case, Trim              |
| Silver       | si_shipment_process   | customer_name               | Bronze       | bz_shipment           | BILL_TO_NAME                | Not null                | Trim                          |
| Silver       | si_shipment_process   | customer_email              | Bronze       | bz_shipment           | BILL_TO_TITLE               | Valid email format      | Lowercase, Trim               |
| Silver       | si_shipment_process   | customer_phone              | Bronze       | bz_shipment           | BILL_TO_PHONE_NUMBER         | Valid phone format      | Remove non-numeric            |
| Silver       | si_shipment_process   | customer_address            | Bronze       | bz_shipment           | BILL_TO_ADDRESS             | Not null                | Trim                          |
| Silver       | si_shipment_process   | shipment_status             | Bronze       | bz_shipment           | SHIPMENT_STATUS             | Not null, Enum check    | Uppercase, Trim               |
| Silver       | si_shipment_process   | shipment_weight             | Bronze       | bz_shipment           | PLANNED_WEIGHT              | Not null, > 0           | Cast to Decimal(10,2)         |
| Silver       | si_shipment_process   | shipment_type               | Bronze       | bz_shipment           | SHIPMENT_TYPE               | Not null                | Uppercase, Trim               |
| Silver       | si_shipment_process   | customer_segment            | Derived      | -                     | -                           | Not null                | Map from business rule        |
| Silver       | si_shipment_process   | transaction_category        | Derived      | -                     | -                           | Not null                | Map from business rule        |
| Silver       | si_shipment_process   | client_id                   | Bronze       | bz_shipment           | ASSIGNED_CUSTOMER_ID        | Not null                | Trim                          |
| Silver       | si_shipment_process   | order_date                  | Bronze       | bz_shipment           | CREATED_DTTM                | Not null, Valid date    | To Timestamp                  |
| Silver       | si_shipment_process   | amount                      | Bronze       | bz_shipment           | TOTAL_COST                  | Not null, >= 0          | Cast to Decimal(10,2)         |
| Silver       | si_shipment_process   | profit_margin               | Derived      | -                     | -                           | >= 0, <= 1              | Calculate (amount/cost)       |
| Silver       | si_shipment_process   | created_at                  | Bronze       | bz_shipment           | CREATED_DTTM                | Not null                | To Timestamp                  |
| Silver       | si_shipment_process   | updated_at                  | Bronze       | bz_shipment           | LAST_UPDATED_DTTM           | Not null                | To Timestamp                  |
| Silver       | si_shipment_process   | ... (all other columns)     | Bronze       | bz_shipment           | ... (same as Bronze)        | As per DDL              | Direct mapping, Trim strings  |
| Silver       | si_shipment_process   | load_date                   | Bronze       | bz_shipment           | load_timestamp              | Not null                | To Timestamp                  |
| Silver       | si_shipment_process   | update_date                 | Bronze       | bz_shipment           | update_timestamp            | Not null                | To Timestamp                  |
| Silver       | si_shipment_process   | source_system               | Bronze       | bz_shipment           | source_system               | Not null                | Uppercase, Trim               |

*Note: All Bronze columns are included in Silver for full lineage. For derived fields, business logic must be implemented in the ETL pipeline. All string fields are trimmed, and all date/timestamp fields are validated and cast as needed. Null checks and uniqueness are enforced where required.*

## Table: SHIPMENT AUDIT (bronze.bz_shipment_audit) → SI_AUDIT_LOG (silver.si_audit_log)

| Target Layer | Target Table      | Target Field      | Source Layer | Source Table         | Source Field      | Validation Rule         | Transformation Rule           |
|--------------|------------------|-------------------|--------------|---------------------|-------------------|-------------------------|-------------------------------|
| Silver       | si_audit_log      | audit_id          | Derived      | -                   | -                 | Not null, Unique        | Generate UUID                 |
| Silver       | si_audit_log      | source_table      | Bronze       | bz_shipment_audit    | source_table      | Not null                | Uppercase, Trim               |
| Silver       | si_audit_log      | load_date         | Bronze       | bz_shipment_audit    | load_timestamp    | Not null                | To Timestamp                  |
| Silver       | si_audit_log      | processed_by      | Bronze       | bz_shipment_audit    | processed_by      | Not null                | Uppercase, Trim               |
| Silver       | si_audit_log      | processing_time   | Bronze       | bz_shipment_audit    | processing_time   | >= 0                    | Cast to Decimal(10,2)         |
| Silver       | si_audit_log      | status            | Bronze       | bz_shipment_audit    | status            | Not null, Enum check    | Uppercase, Trim               |
| Silver       | si_audit_log      | created_at        | Bronze       | bz_shipment_audit    | load_timestamp    | Not null                | To Timestamp                  |
| Silver       | si_audit_log      | updated_at        | Bronze       | bz_shipment_audit    | processed_by      | Not null                | To Timestamp                  |
| Silver       | si_audit_log      | update_date       | Bronze       | bz_shipment_audit    | processed_by      | Not null                | To Timestamp                  |
| Silver       | si_audit_log      | source_system     | Bronze       | bz_shipment_audit    | source_table      | Not null                | Uppercase, Trim               |

## Table: SI_ERROR_LOG (silver.si_error_log)

| Target Layer | Target Table      | Target Field      | Source Layer | Source Table         | Source Field      | Validation Rule         | Transformation Rule           |
|--------------|------------------|-------------------|--------------|---------------------|-------------------|-------------------------|-------------------------------|
| Silver       | si_error_log      | error_id          | Derived      | -                   | -                 | Not null, Unique        | Generate UUID                 |
| Silver       | si_error_log      | source_table      | Bronze       | bz_shipment         | -                 | Not null                | Uppercase, Trim               |
| Silver       | si_error_log      | error_type        | Derived      | -                   | -                 | Not null                | Map from error logic          |
| Silver       | si_error_log      | error_message     | Derived      | -                   | -                 | Not null                | Capture error message         |
| Silver       | si_error_log      | error_timestamp   | Derived      | -                   | -                 | Not null                | Current timestamp             |
| Silver       | si_error_log      | record_reference  | Bronze       | bz_shipment         | SHIPMENT_ID       | Not null                | Uppercase, Trim               |
| Silver       | si_error_log      | created_at        | Derived      | -                   | -                 | Not null                | Current timestamp             |
| Silver       | si_error_log      | updated_at        | Derived      | -                   | -                 | Not null                | Current timestamp             |
| Silver       | si_error_log      | load_date         | Derived      | -                   | -                 | Not null                | Current timestamp             |
| Silver       | si_error_log      | update_date       | Derived      | -                   | -                 | Not null                | Current timestamp             |
| Silver       | si_error_log      | source_system     | Bronze       | bz_shipment         | source_system     | Not null                | Uppercase, Trim               |

---

# Data Cleansing, Validation, and Business Rules
- All string fields are trimmed of leading/trailing whitespace.
- All date/timestamp fields are validated for correct format and converted to TIMESTAMP.
- Numeric fields are cast to the correct precision and validated for non-negativity where applicable.
- Email and phone fields are validated for correct format using regex.
- Enum fields (e.g., shipment_status, status) are checked against allowed values.
- Uniqueness is enforced for primary business keys (e.g., shipment_number, audit_id, error_id).
- Derived fields (e.g., profit_margin, customer_segment) are calculated per business logic in the ETL pipeline.
- Null checks are enforced for all required fields.
- Error handling: All records failing validation are logged in si_error_log with detailed error messages and references.
- Audit logging: All data loads and transformations are logged in si_audit_log for traceability.

# Recommendations for Error Handling and Logging
- Use try/except blocks in PySpark to catch and log all transformation errors.
- Write failed records to si_error_log with error type, message, and reference.
- Maintain audit logs for all ETL runs in si_audit_log, including timestamps, user, and status.
- Implement data quality dashboards to monitor error and audit logs.

# Assumptions
- All Bronze fields are nullable unless otherwise specified; Silver fields enforce stricter validation.
- Derived fields are calculated in the ETL pipeline and require business logic.
- All mappings are compatible with Databricks PySpark and Delta Lake.
- No Cognos .report file was provided, so Cognos mapping is not included.

# API Cost
apiCost: 0.0005

# Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping

# PipelineID
12361
