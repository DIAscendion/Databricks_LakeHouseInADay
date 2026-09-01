_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Silver Layer Data Mapping for TMS Shipment Application (Bronze to Silver)
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Overview
This document provides a comprehensive data mapping from the Bronze Layer to the Silver Layer for the TMS Shipment Application in Databricks. It includes attribute-level cleansing, validation, and business rules to ensure data quality, consistency, and usability. The mapping covers all main, error, and audit tables, and is compatible with Databricks PySpark. Recommendations for error handling and logging are also included.

---

# Data Mapping for the Silver Layer (Bronze to Silver)

| Target Layer | Target Table         | Target Field            | Source Layer | Source Table           | Source Field            | Validation Rule           | Transformation Rule |
|--------------|---------------------|-------------------------|--------------|-----------------------|-------------------------|---------------------------|---------------------|
| Silver       | sv_shipment         | SHIPMENT_ID             | Bronze       | bz_shipment           | shipment_id             | Not null, Unique          | Uppercase, Trim     |
| Silver       | sv_shipment         | TC_SHIPMENT_ID          | Bronze       | bz_shipment           | tc_shipment_id          | Not null                  | Trim                |
| Silver       | sv_shipment         | ORIGIN_STORE_ID         | Bronze       | bz_shipment           | origin_store_id         | Not null, Valid format    | Uppercase, Trim     |
| Silver       | sv_shipment         | DESTINATION_STORE_ID    | Bronze       | bz_shipment           | destination_store_id    | Not null, Valid format    | Uppercase, Trim     |
| Silver       | sv_shipment         | SHIPMENT_STATUS         | Bronze       | bz_shipment           | shipment_status         | Not null, Enum check      | Uppercase, Trim     |
| Silver       | sv_shipment         | SHIPMENT_TYPE           | Bronze       | bz_shipment           | shipment_type           | Not null, Enum check      | Uppercase, Trim     |
| Silver       | sv_shipment         | TOTAL_COST              | Bronze       | bz_shipment           | total_cost              | >= 0                      | Cast to Decimal     |
| Silver       | sv_shipment         | SHIPMENT_START_DTTM     | Bronze       | bz_shipment           | shipment_start_dttm     | Not null, Valid datetime  | To UTC              |
| Silver       | sv_shipment         | SHIPMENT_END_DTTM       | Bronze       | bz_shipment           | shipment_end_dttm       | Valid datetime            | To UTC              |
| Silver       | sv_shipment         | REGION_ID               | Bronze       | bz_shipment           | region_id               | Not null                  | Uppercase, Trim     |
| Silver       | sv_shipment         | load_date               | Bronze       | bz_shipment           | load_timestamp          | Not null                  | To UTC              |
| Silver       | sv_shipment         | update_date             | Bronze       | bz_shipment           | update_timestamp        | Not null                  | To UTC              |
| Silver       | sv_shipment         | source_system           | Bronze       | bz_shipment           | source_system           | Not null                  | Uppercase, Trim     |
| Silver       | sv_shipment_error   | error_id                | Bronze       | bz_audit               | record_id               | Not null, Unique          |                     |
| Silver       | sv_shipment_error   | table_name              | Bronze       | bz_audit               | source_table            | Not null                  | Uppercase, Trim     |
| Silver       | sv_shipment_error   | record_id               | Bronze       | bz_audit               | record_id               | Not null                  |                     |
| Silver       | sv_shipment_error   | error_type              | Bronze       | bz_audit               | status                  | Not null                  | Uppercase, Trim     |
| Silver       | sv_shipment_error   | error_message           | Bronze       | bz_audit               | error_message           |                           | Trim                |
| Silver       | sv_shipment_error   | error_timestamp         | Bronze       | bz_audit               | load_timestamp          | Not null                  | To UTC              |
| Silver       | sv_shipment_error   | layer                   | Bronze       | bz_audit               | source_table            | Not null                  | 'Silver'            |
| Silver       | sv_shipment_error   | load_date               | Bronze       | bz_audit               | load_timestamp          | Not null                  | To UTC              |
| Silver       | sv_shipment_error   | update_date             | Bronze       | bz_audit               | update_timestamp        | Not null                  | To UTC              |
| Silver       | sv_shipment_error   | source_system           | Bronze       | bz_audit               | source_system           | Not null                  | Uppercase, Trim     |
| Silver       | sv_audit            | audit_id                | Bronze       | bz_audit               | record_id               | Not null, Unique          |                     |
| Silver       | sv_audit            | pipeline_name           | Bronze       | bz_audit               | source_table            | Not null                  | Uppercase, Trim     |
| Silver       | sv_audit            | execution_id            | Bronze       | bz_audit               | processed_by            | Not null                  | Uppercase, Trim     |
| Silver       | sv_audit            | start_time              | Bronze       | bz_audit               | load_timestamp          | Not null                  | To UTC              |
| Silver       | sv_audit            | end_time                | Bronze       | bz_audit               | update_timestamp        | Not null                  | To UTC              |
| Silver       | sv_audit            | status                  | Bronze       | bz_audit               | status                  | Not null                  | Uppercase, Trim     |
| Silver       | sv_audit            | error_message           | Bronze       | bz_audit               | error_message           |                           | Trim                |
| Silver       | sv_audit            | record_count            | Bronze       | bz_audit               | processing_time         | >= 0                      | Cast to BIGINT      |
| Silver       | sv_audit            | load_date               | Bronze       | bz_audit               | load_timestamp          | Not null                  | To UTC              |
| Silver       | sv_audit            | update_date             | Bronze       | bz_audit               | update_timestamp        | Not null                  | To UTC              |
| Silver       | sv_audit            | source_system           | Bronze       | bz_audit               | source_system           | Not null                  | Uppercase, Trim     |

---

# Explanations for Complex Rules
- **Enum check**: Validates that the value is within the allowed set of shipment statuses/types.
- **To UTC**: All timestamps are converted to UTC for consistency.
- **Uppercase, Trim**: Standardizes string fields for deduplication and matching.
- **Cast to Decimal/BIGINT**: Ensures numeric fields are in the correct type for analytics.
- **Not null, Unique**: Ensures primary keys and identifiers are always present and unique.

# Data Cleansing Steps
- Remove leading/trailing whitespace from all string fields.
- Convert all string identifiers to uppercase.
- Replace nulls in non-nullable fields with default values or flag as error records.
- Validate and standardize all datetime fields to UTC.

# Error Handling & Logging Recommendations
- All records failing validation rules are redirected to the Silver error table (`sv_shipment_error`) with detailed error messages.
- Audit table (`sv_audit`) logs pipeline execution, record counts, and errors for traceability.
- All transformation and validation steps are logged for data lineage.

# API Cost
apiCost: 0.000100

# Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Data_Mapping_Reviewer

# Pipeline ID
12361
