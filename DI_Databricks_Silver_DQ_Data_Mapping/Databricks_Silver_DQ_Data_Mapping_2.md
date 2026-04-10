_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Silver Layer Data Quality Data Mapping for TMS Shipment Application (Mode 2)
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Silver Layer Data Quality Data Mapping (Mode 2)

## 1. Overview

This document provides an updated data mapping from the Bronze Layer to the Silver Layer in the Medallion architecture for the TMS (Transportation Management System) Shipment application, reflecting Mode 2 requirements. The mapping includes new and revised data quality rules, transformation logic, and documentation updates to ensure data quality, consistency, and usability across the organization.

### Key Considerations (Mode 2):
- **Workflow Mode**: Mode 2 (Enhanced DQ and mapping updates)
- **Data Quality**: Additional and revised validation rules for each attribute
- **Data Cleansing**: Enhanced standardization and cleansing transformations
- **Business Rules**: Updated business logic and constraints
- **PySpark Compatibility**: All rules are designed for Databricks PySpark implementation
- **Error Handling**: Improved error logging and data quality monitoring
- **Performance**: Optimized for large-scale data processing

## 2. Data Mapping for the Silver Layer (Mode 2)

### 2.1 Main Shipment Table Mapping (bz_shipment → sv_shipment)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule | Comments/Annotations |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|----------------------|
| Silver | sv_shipment | id | Silver | Generated | N/A | Not Null, Unique | Generate monotonically_increasing_id() | |
| Silver | sv_shipment | SHIPMENT_ID | Bronze | bz_shipment | SHIPMENT_ID | Not Null, Unique, Length <= 50 | Trim whitespace, Upper case | |
| Silver | sv_shipment | TC_SHIPMENT_ID | Bronze | bz_shipment | TC_SHIPMENT_ID | Length <= 50 | Trim whitespace, Null if empty string | |
| Silver | sv_shipment | TC_COMPANY_ID | Bronze | bz_shipment | TC_COMPANY_ID | Not Null, Length <= 20 | Trim whitespace, Upper case | |
| Silver | sv_shipment | EXT_SYS_SHIPMENT_ID | Bronze | bz_shipment | EXT_SYS_SHIPMENT_ID | Length <= 50 | Trim whitespace, Null if empty string | |
| Silver | sv_shipment | SHIPMENT_REF_ID | Bronze | bz_shipment | SHIPMENT_REF_ID | Length <= 50 | Trim whitespace, Null if empty string | |
| Silver | sv_shipment | REF_SHIPMENT_NBR | Bronze | bz_shipment | REF_SHIPMENT_NBR | Length <= 50 | Trim whitespace, Null if empty string | |
| Silver | sv_shipment | PP_SHIPMENT_ID | Bronze | bz_shipment | PP_SHIPMENT_ID | Length <= 50 | Trim whitespace, Null if empty string | |
| Silver | sv_shipment | SHIPMENT_STATUS | Bronze | bz_shipment | SHIPMENT_STATUS | Not Null, Valid Values (ACTIVE, CANCELLED, COMPLETED, PENDING, IN_TRANSIT) | Trim whitespace, Upper case, Default 'PENDING' if null | Added 'IN_TRANSIT' as valid status |
| Silver | sv_shipment | SHIPMENT_TYPE | Bronze | bz_shipment | SHIPMENT_TYPE | Not Null, Valid Values (INBOUND, OUTBOUND, TRANSFER, RETURN) | Trim whitespace, Upper case | Added 'RETURN' as valid type |
| Silver | sv_shipment | SHIPMENT_LEG_TYPE | Bronze | bz_shipment | SHIPMENT_LEG_TYPE | Length <= 20 | Trim whitespace, Upper case | |
| Silver | sv_shipment | MOVE_TYPE | Bronze | bz_shipment | MOVE_TYPE | Length <= 20 | Trim whitespace, Upper case | |
| Silver | sv_shipment | CREATION_TYPE | Bronze | bz_shipment | CREATION_TYPE | Length <= 20 | Trim whitespace, Upper case | |
| Silver | sv_shipment | BUSINESS_PROCESS | Bronze | bz_shipment | BUSINESS_PROCESS | Length <= 50 | Trim whitespace, Upper case | |
| Silver | sv_shipment | CREATED_DTTM | Bronze | bz_shipment | CREATED_DTTM | Not Null, Valid Timestamp, >= 2020-01-01 | Convert to UTC timezone, Validate format | |
| Silver | sv_shipment | LAST_UPDATED_DTTM | Bronze | bz_shipment | LAST_UPDATED_DTTM | Valid Timestamp, >= CREATED_DTTM | Convert to UTC timezone, Default to CREATED_DTTM if null | |
| Silver | sv_shipment | SHIPMENT_START_DTTM | Bronze | bz_shipment | SHIPMENT_START_DTTM | Valid Timestamp | Convert to UTC timezone | |
| Silver | sv_shipment | SHIPMENT_END_DTTM | Bronze | bz_shipment | SHIPMENT_END_DTTM | Valid Timestamp, >= SHIPMENT_START_DTTM | Convert to UTC timezone | |
| Silver | sv_shipment | SHIPMENT_RECON_DTTM | Bronze | bz_shipment | SHIPMENT_RECON_DTTM | Valid Timestamp | Convert to UTC timezone | |
| Silver | sv_shipment | AVAILABLE_DTTM | Bronze | bz_shipment | AVAILABLE_DTTM | Valid Timestamp | Convert to UTC timezone | |
| Silver | sv_shipment | RECEIVED_DTTM | Bronze | bz_shipment | RECEIVED_DTTM | Valid Timestamp | Convert to UTC timezone | |
| Silver | sv_shipment | TENDER_DTTM | Bronze | bz_shipment | TENDER_DTTM | Valid Timestamp | Convert to UTC timezone | |
| Silver | sv_shipment | SCHEDULED_PICKUP_DTTM | Bronze | bz_shipment | SCHEDULED_PICKUP_DTTM | Valid Timestamp | Convert to UTC timezone | |
| Silver | sv_shipment | O_FACILITY_ID | Bronze | bz_shipment | O_FACILITY_ID | Not Null, Length <= 50 | Trim whitespace, Upper case | |
| Silver | sv_shipment | O_POSTAL_CODE | Bronze | bz_shipment | O_POSTAL_CODE | Valid Postal Code Format | Trim whitespace, Upper case, Remove special characters | |
| Silver | sv_shipment | O_COUNTRY_CODE | Bronze | bz_shipment | O_COUNTRY_CODE | Length = 2, Valid ISO Country Code | Trim whitespace, Upper case | |
| Silver | sv_shipment | D_FACILITY_ID | Bronze | bz_shipment | D_FACILITY_ID | Not Null, Length <= 50 | Trim whitespace, Upper case | |
| Silver | sv_shipment | D_POSTAL_CODE | Bronze | bz_shipment | D_POSTAL_CODE | Valid Postal Code Format | Trim whitespace, Upper case, Remove special characters | |
| Silver | sv_shipment | D_COUNTRY_CODE | Bronze | bz_shipment | D_COUNTRY_CODE | Length = 2, Valid ISO Country Code | Trim whitespace, Upper case | |
| Silver | sv_shipment | DISTANCE | Bronze | bz_shipment | DISTANCE | >= 0, <= 99999.99 | Round to 2 decimal places, Default 0 if null | |
| Silver | sv_shipment | DISTANCE_UOM | Bronze | bz_shipment | DISTANCE_UOM | Valid Values (MI, KM, FT, M) | Trim whitespace, Upper case, Default 'MI' | |
| Silver | sv_shipment | PLANNED_WEIGHT | Bronze | bz_shipment | PLANNED_WEIGHT | >= 0, <= 9999999.999 | Round to 3 decimal places, Default 0 if null | |
| Silver | sv_shipment | WEIGHT_UOM_ID_BASE | Bronze | bz_shipment | WEIGHT_UOM_ID_BASE | Valid Values (LB, KG, TON, OZ) | Trim whitespace, Upper case, Default 'LB' | |
| Silver | sv_shipment | TOTAL_COST | Bronze | bz_shipment | TOTAL_COST | >= 0, <= 99999999.99 | Round to 2 decimal places, Default 0 if null | |
| Silver | sv_shipment | CURRENCY_CODE | Bronze | bz_shipment | CURRENCY_CODE | Length = 3, Valid ISO Currency Code | Trim whitespace, Upper case, Default 'USD' | |
| Silver | sv_shipment | IS_SHIPMENT_CANCELLED | Bronze | bz_shipment | IS_SHIPMENT_CANCELLED | Valid Values (Y, N, TRUE, FALSE, 1, 0) | Standardize to Y/N format | |
| Silver | sv_shipment | IS_HAZMAT | Bronze | bz_shipment | IS_HAZMAT | Valid Values (Y, N, TRUE, FALSE, 1, 0) | Standardize to Y/N format | |
| Silver | sv_shipment | load_date | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_shipment | update_date | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_shipment | source_system | Bronze | bz_shipment | source_system | Not Null, Length <= 50 | Trim whitespace, Upper case | |
| Silver | sv_shipment | SHIPMENT_PRIORITY | Bronze | bz_shipment | SHIPMENT_PRIORITY | Valid Values (HIGH, MEDIUM, LOW) | Trim whitespace, Upper case, Default 'MEDIUM' | New field added for Mode 2 |

### 2.2 Error Data Table Mapping (Bronze Errors → sv_shipment_error)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule | Comments/Annotations |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|----------------------|
| Silver | sv_shipment_error | error_id | Silver | Generated | N/A | Not Null, Unique | Generate monotonically_increasing_id() | |
| Silver | sv_shipment_error | table_name | Silver | Generated | N/A | Not Null | Set to 'bz_shipment' | |
| Silver | sv_shipment_error | record_id | Bronze | bz_shipment | SHIPMENT_ID | Not Null | Source record identifier | |
| Silver | sv_shipment_error | error_type | Silver | Generated | N/A | Not Null, Valid Values (VALIDATION, TRANSFORMATION, BUSINESS_RULE, SYSTEM) | Based on validation failure type | Added 'SYSTEM' error type |
| Silver | sv_shipment_error | error_message | Silver | Generated | N/A | Not Null, Length <= 500 | Descriptive error message | |
| Silver | sv_shipment_error | error_timestamp | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_shipment_error | layer | Silver | Generated | N/A | Not Null | Set to 'BRONZE_TO_SILVER' | |
| Silver | sv_shipment_error | load_date | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_shipment_error | update_date | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_shipment_error | source_system | Bronze | bz_shipment | source_system | Not Null | Source system identifier | |

### 2.3 Audit Table Mapping (Bronze Audit → sv_audit)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule | Comments/Annotations |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|----------------------|
| Silver | sv_audit | audit_id | Silver | Generated | N/A | Not Null, Unique | Generate monotonically_increasing_id() | |
| Silver | sv_audit | pipeline_name | Silver | Generated | N/A | Not Null | Set to 'BRONZE_TO_SILVER_SHIPMENT' | |
| Silver | sv_audit | execution_id | Silver | Generated | N/A | Not Null | Generate UUID for each execution | |
| Silver | sv_audit | start_time | Silver | Generated | N/A | Not Null | Pipeline execution start time | |
| Silver | sv_audit | end_time | Silver | Generated | N/A | Not Null, >= start_time | Pipeline execution end time | |
| Silver | sv_audit | status | Silver | Generated | N/A | Not Null, Valid Values (SUCCESS, FAILED, PARTIAL, WARNING) | Pipeline execution status | Added 'WARNING' status |
| Silver | sv_audit | error_message | Silver | Generated | N/A | Length <= 1000 | Error details if status is FAILED | |
| Silver | sv_audit | record_count | Silver | Generated | N/A | >= 0 | Number of records processed | |
| Silver | sv_audit | load_date | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_audit | update_date | Silver | Generated | N/A | Not Null | current_timestamp() | |
| Silver | sv_audit | source_system | Bronze | bz_audit | audit_source_system | Not Null | Source system identifier | |

### 2.4 Deprecated Fields (Removed in Mode 2)

| Target Table | Target Field | Reason for Removal |
|--------------|--------------|-------------------|
| sv_shipment | SHIPMENT_LEGACY_CODE | Field deprecated, not used in Mode 2 |

## 3. Data Quality Rules and Validations (Mode 2)

### 3.1 Additional Business Rules

1. **Shipment Priority Rule**:
   - SHIPMENT_PRIORITY must be one of (HIGH, MEDIUM, LOW)
   - Default to 'MEDIUM' if null or invalid
2. **Enhanced Status Rule**:
   - SHIPMENT_STATUS now includes 'IN_TRANSIT' as a valid value
3. **Return Shipments**:
   - SHIPMENT_TYPE now includes 'RETURN' as a valid value
4. **System Error Logging**:
   - Error table now supports 'SYSTEM' error type
5. **Audit Status**:
   - Audit table now supports 'WARNING' status

### 3.2 Enhanced Data Cleansing Rules

- All string fields: Remove non-printable characters
- All date fields: If invalid, log to error table and set to NULL
- All numeric fields: If out of range, log to error table and set to default

## 4. Error Handling and Logging (Mode 2)

- **System Errors**: Now explicitly logged in error table
- **Deprecated Fields**: Any data in deprecated fields is ignored and logged
- **Audit Table**: Now tracks 'WARNING' status for partial issues

## 5. Implementation Guidelines (Mode 2)

- All new and updated rules are compatible with PySpark
- Use comments/annotations in code for complex transformations
- Maintain version history and document all changes

## 6. API Cost Calculation

**API Cost**: $0.000000

*Note: This data mapping document was updated for Mode 2 without external API calls. The cost represents the computational resources used for document generation and validation rule creation.*

## 7. Version History

| Version | Date | Description |
|---------|------|-------------|
| 1 |  | Initial Silver Layer DQ Data Mapping |
| 2 |  | Mode 2: Enhanced DQ rules, new fields, deprecated fields removed, documentation updated |

---

**Output URL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping

**Pipeline ID**: 12361

---

*This Silver Layer Data Quality Data Mapping (Mode 2) provides comprehensive guidelines for implementing robust data quality processes in the Databricks Medallion architecture, ensuring high-quality, reliable data for analytics and downstream processing.*
