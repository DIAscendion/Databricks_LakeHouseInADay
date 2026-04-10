_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Silver Layer Data Mapping for TMS Shipment Application, including Cognos report cross-reference and DQ rules
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Overview
This document provides a comprehensive data mapping for the Silver Layer in the Databricks Medallion architecture for the TMS Shipment application. It includes:
- Attribute-level mapping from Bronze to Silver Layer
- Data cleansing, validation, and business rules
- Mandatory Cognos report cross-reference and mapping
- Recommendations for error handling and logging

---

# Cognos Report Extracted Metadata (MANDATORY)

## Report Source Tables
- Shipment (implied from context and column names)

## Report Columns per Table
**Shipment**:
- SHIPMENT_ID
- SHIPMENT_STATUS
- SHIPMENT_TYPE
- O_STOP_LOCATION_NAME
- O_CITY
- O_STATE_PROV
- O_POSTAL_CODE
- O_COUNTRY

## Report KPIs / Calculated Measures
- TOTAL ROW COUNT
- DISTINCT SHIPMENT IDs
- TOTAL DISTANCE
- AVG DISTANCE
- SHIPMENT STATUS BREAKDOWN (Bar Chart)
- MODE OF TRANSPORT BREAKDOWN (Pie Chart)

---

# Cognos Report to Silver Layer Column Mapping Table (MANDATORY)

| Report Table Name | Report Column Name      | Target Layer | Target Table | Target Field           | Match Confidence | Notes |
|------------------|------------------------|--------------|--------------|------------------------|------------------|-------|
| Shipment         | SHIPMENT_ID            | Silver       | sv_shipment  | SHIPMENT_ID            | High             | Exact match by name and business meaning |
| Shipment         | SHIPMENT_STATUS        | Silver       | sv_shipment  | SHIPMENT_STATUS        | High             | Exact match by name and business meaning |
| Shipment         | SHIPMENT_TYPE          | Silver       | sv_shipment  | SHIPMENT_TYPE          | High             | Exact match by name and business meaning |
| Shipment         | O_STOP_LOCATION_NAME   | Silver       | sv_shipment  | O_STOP_LOCATION_NAME   | High             | Exact match by name and business meaning |
| Shipment         | O_CITY                 | Silver       | sv_shipment  | O_CITY                 | High             | Exact match by name and business meaning |
| Shipment         | O_STATE_PROV           | Silver       | sv_shipment  | O_STATE_PROV           | High             | Exact match by name and business meaning |
| Shipment         | O_POSTAL_CODE          | Silver       | sv_shipment  | O_POSTAL_CODE          | High             | Exact match by name and business meaning |
| Shipment         | O_COUNTRY              | Silver       | sv_shipment  | O_COUNTRY_CODE         | Medium           | Cognos uses 'O_COUNTRY', Silver uses 'O_COUNTRY_CODE'; mapped by semantic meaning |
| Shipment         | TOTAL ROW COUNT        | Silver       | sv_shipment  | [UNMAPPED - Review Required] | Unmapped      | KPI, not a physical field; calculated in reporting layer |
| Shipment         | DISTINCT SHIPMENT IDs  | Silver       | sv_shipment  | [UNMAPPED - Review Required] | Unmapped      | KPI, not a physical field; calculated in reporting layer |
| Shipment         | TOTAL DISTANCE         | Silver       | sv_shipment  | DISTANCE               | High             | Aggregated from DISTANCE field |
| Shipment         | AVG DISTANCE           | Silver       | sv_shipment  | DISTANCE               | High             | Aggregated from DISTANCE field |
| Shipment         | SHIPMENT STATUS BREAKDOWN | Silver    | sv_shipment  | SHIPMENT_STATUS        | High             | Visualization based on SHIPMENT_STATUS |
| Shipment         | MODE OF TRANSPORT BREAKDOWN | Silver  | sv_shipment  | MOVE_TYPE              | Medium           | Cognos chart, mapped to MOVE_TYPE field |

---

# Data Mapping for the Silver Layer (Bronze to Silver)

| Target Layer | Target Table  | Target Field           | Source Layer | Source Table  | Source Field           | Validation Rule         | Transformation Rule |
|--------------|--------------|------------------------|--------------|--------------|------------------------|------------------------|--------------------|
| Silver       | sv_shipment  | SHIPMENT_ID            | Bronze       | bz_shipment  | SHIPMENT_ID            | Not null, Unique       | Trim, Uppercase    |
| Silver       | sv_shipment  | SHIPMENT_STATUS        | Bronze       | bz_shipment  | SHIPMENT_STATUS        | Not null, Valid values | Map status codes   |
| Silver       | sv_shipment  | SHIPMENT_TYPE          | Bronze       | bz_shipment  | SHIPMENT_TYPE          | Not null, Valid values | Standardize values |
| Silver       | sv_shipment  | O_STOP_LOCATION_NAME   | Bronze       | bz_shipment  | O_STOP_LOCATION_NAME   | Not null               | Trim               |
| Silver       | sv_shipment  | O_CITY                 | Bronze       | bz_shipment  | O_CITY                 | Not null               | Proper case        |
| Silver       | sv_shipment  | O_STATE_PROV           | Bronze       | bz_shipment  | O_STATE_PROV           | Not null, Valid US state| Uppercase, Validate|
| Silver       | sv_shipment  | O_POSTAL_CODE          | Bronze       | bz_shipment  | O_POSTAL_CODE          | Not null, Valid format | Pad left (5)       |
| Silver       | sv_shipment  | O_COUNTRY_CODE         | Bronze       | bz_shipment  | O_COUNTRY_CODE         | Not null, Valid ISO code| Uppercase, Validate|
| Silver       | sv_shipment  | DISTANCE               | Bronze       | bz_shipment  | DISTANCE               | Not null, >= 0         | Round(2)           |
| Silver       | sv_shipment  | MOVE_TYPE              | Bronze       | bz_shipment  | MOVE_TYPE              | Not null, Valid values | Standardize values |
| Silver       | sv_shipment  | CREATED_DTTM           | Bronze       | bz_shipment  | CREATED_DTTM           | Not null, Valid date   | To timestamp       |
| Silver       | sv_shipment  | ... (all other fields) | Bronze       | bz_shipment  | ... (all other fields) | As per Silver DDL      | As per business rules |
| Silver       | sv_shipment_error | error_id           | Bronze       | bz_audit     | record_id              | Not null, Unique       | Cast to BIGINT     |
| Silver       | sv_shipment_error | table_name         | Bronze       | bz_audit     | source_table           | Not null               | Uppercase          |
| Silver       | sv_shipment_error | error_message      | Bronze       | bz_audit     | error_message          | Nullable               | None               |
| Silver       | sv_shipment_error | error_timestamp    | Bronze       | bz_audit     | audit_timestamp        | Not null, Valid date   | To timestamp       |
| Silver       | sv_audit     | audit_id               | Bronze       | bz_audit     | record_id              | Not null, Unique       | Cast to BIGINT     |
| Silver       | sv_audit     | pipeline_name          | Bronze       | bz_audit     | source_table           | Not null               | Uppercase          |
| Silver       | sv_audit     | execution_id           | Bronze       | bz_audit     | processed_by           | Not null               | None               |
| Silver       | sv_audit     | start_time             | Bronze       | bz_audit     | load_timestamp         | Not null, Valid date   | To timestamp       |
| Silver       | sv_audit     | end_time               | Bronze       | bz_audit     | update_timestamp       | Not null, Valid date   | To timestamp       |
| Silver       | sv_audit     | status                 | Bronze       | bz_audit     | status                 | Not null, Valid values | Standardize values |
| Silver       | sv_audit     | error_message          | Bronze       | bz_audit     | error_message          | Nullable               | None               |
| Silver       | sv_audit     | record_count           | Bronze       | bz_audit     | record_count           | >= 0                   | None               |
| Silver       | sv_audit     | load_date              | Bronze       | bz_audit     | load_timestamp         | Not null, Valid date   | To timestamp       |
| Silver       | sv_audit     | update_date            | Bronze       | bz_audit     | update_timestamp       | Not null, Valid date   | To timestamp       |
| Silver       | sv_audit     | source_system          | Bronze       | bz_audit     | audit_source           | Not null               | Uppercase          |

---

# Data Cleansing, Validation, and Business Rules
- All string fields: Trim whitespace, convert to uppercase where appropriate
- Dates: Validate format, convert to timestamp
- Numeric fields: Validate non-negative, round to required precision
- Status/type fields: Map to standardized values as per business glossary
- Postal codes: Pad left to 5 digits, validate format
- Country codes: Validate against ISO 3166-1 alpha-2
- Error handling: Records failing validation are logged in sv_shipment_error with error type and message
- Audit: All pipeline operations are logged in sv_audit with timestamps and status

# Recommendations for Error Handling and Logging
- Use try/except blocks in PySpark transformations to catch and log errors
- Write failed records to sv_shipment_error with full context
- Maintain audit trail in sv_audit for all pipeline runs
- Use Delta Lake time travel for rollback and recovery

# API Cost
apiCost: 0.000000

---

[outputURL](https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping)

pipelineID: 12361
