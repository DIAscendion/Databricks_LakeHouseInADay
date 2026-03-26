_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Comprehensive data mapping for Dimension tables in the Gold Layer with transformations, validations, and cleansing rules
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Dim Transformation Data Mapping

## 1. Overview

This document provides a comprehensive data mapping for Dimension tables from the Silver to Gold Layer in the TMS (Transportation Management System) Shipment application. The mapping incorporates necessary transformations, validations, and cleansing rules at the attribute level to ensure high data quality, consistency, and business intelligence capabilities.

### Key Considerations:
- **Data Quality**: Implement robust validation rules to ensure data integrity
- **Standardization**: Apply consistent naming conventions and format standardization
- **Business Rules**: Incorporate domain-specific transformation logic
- **Performance**: Optimize for efficient lookups and reporting
- **Auditability**: Maintain complete lineage and transformation tracking
- **Slowly Changing Dimensions**: Implement SCD Type 2 for historical tracking

---

## 2. Data Mapping for Dimension Tables

### 2.1 go_carrier_dimension

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Gold | go_carrier_dimension | carrier_id | Silver | sv_shipment | - | Auto-generated surrogate key | Generate BIGINT surrogate key using ROW_NUMBER() |
| Gold | go_carrier_dimension | carrier_key | Silver | sv_shipment | ASSIGNED_CARRIER_ID | NOT NULL, Unique | SHA2(CONCAT(COALESCE(ASSIGNED_CARRIER_CODE, ''), '\|', COALESCE(ASSIGNED_MOT_ID, '')), 256) |
| Gold | go_carrier_dimension | primary_carrier_name | Silver | sv_shipment | ASSIGNED_CARRIER_CODE | NOT NULL, Length > 0 | CASE WHEN UPPER(TRIM(ASSIGNED_CARRIER_CODE)) = 'FEDX' THEN 'FEDEX' WHEN UPPER(TRIM(ASSIGNED_CARRIER_CODE)) = 'UPSFR' THEN 'UPS FREIGHT' WHEN UPPER(TRIM(ASSIGNED_CARRIER_CODE)) = 'XPOLS' THEN 'XPO LOGISTICS' ELSE UPPER(TRIM(ASSIGNED_CARRIER_CODE)) END |
| Gold | go_carrier_dimension | secondary_carrier_name | Silver | sv_shipment | ASSIGNED_SCNDR_CARRIER_CODE | Optional | UPPER(TRIM(ASSIGNED_SCNDR_CARRIER_CODE)) |
| Gold | go_carrier_dimension | broker_carrier_name | Silver | sv_shipment | ASSIGNED_BROKER_CARRIER_CODE | Optional | UPPER(TRIM(ASSIGNED_BROKER_CARRIER_CODE)) |
| Gold | go_carrier_dimension | mode_of_transport | Silver | sv_shipment | ASSIGNED_MOT_ID | NOT NULL, Valid values | CASE WHEN UPPER(ASSIGNED_MOT_ID) IN ('TRUCK', 'TRK') THEN 'TRUCK' WHEN UPPER(ASSIGNED_MOT_ID) IN ('RAIL', 'RR') THEN 'RAIL' WHEN UPPER(ASSIGNED_MOT_ID) IN ('AIR', 'PLANE') THEN 'AIR' WHEN UPPER(ASSIGNED_MOT_ID) IN ('OCEAN', 'SEA') THEN 'OCEAN' ELSE 'OTHER' END |
| Gold | go_carrier_dimension | designated_carrier | Silver | sv_shipment | DSG_CARRIER_CODE | Optional | UPPER(TRIM(DSG_CARRIER_CODE)) |
| Gold | go_carrier_dimension | feasible_carrier | Silver | sv_shipment | FEASIBLE_CARRIER_CODE | Optional | UPPER(TRIM(FEASIBLE_CARRIER_CODE)) |
| Gold | go_carrier_dimension | carrier_status | Silver | sv_shipment | Multiple fields | NOT NULL, Valid status | CASE WHEN ASSIGNED_CARRIER_ID IS NOT NULL THEN 'ASSIGNED' WHEN FEASIBLE_CARRIER_ID IS NOT NULL THEN 'FEASIBLE' WHEN DSG_CARRIER_ID IS NOT NULL THEN 'DESIGNATED' ELSE 'INACTIVE' END |
| Gold | go_carrier_dimension | effective_start_date | Silver | sv_shipment | CREATED_DTTM | NOT NULL | CAST(CREATED_DTTM AS DATE) |
| Gold | go_carrier_dimension | effective_end_date | Silver | sv_shipment | - | NOT NULL | DATE('9999-12-31') for current records |
| Gold | go_carrier_dimension | is_current | Silver | sv_shipment | - | NOT NULL | TRUE for active records, FALSE for historical |
| Gold | go_carrier_dimension | load_date | Silver | sv_shipment | load_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_carrier_dimension | update_date | Silver | sv_shipment | update_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_carrier_dimension | source_system | Silver | sv_shipment | source_system | NOT NULL | COALESCE(source_system, 'TMS') |

### 2.2 go_facility_dimension

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Gold | go_facility_dimension | facility_id | Silver | sv_shipment | - | Auto-generated surrogate key | Generate BIGINT surrogate key using ROW_NUMBER() |
| Gold | go_facility_dimension | facility_key | Silver | sv_shipment | O_FACILITY_ID, D_FACILITY_ID | NOT NULL, Unique | SHA2(CONCAT(COALESCE(facility_id, ''), '\|', COALESCE(facility_name, '')), 256) |
| Gold | go_facility_dimension | facility_name | Silver | sv_shipment | O_STOP_LOCATION_NAME, D_STOP_LOCATION_NAME | NOT NULL, Length > 0 | UPPER(TRIM(COALESCE(O_STOP_LOCATION_NAME, D_STOP_LOCATION_NAME))) |
| Gold | go_facility_dimension | facility_type | Silver | sv_shipment | O_STOP_LOCATION_NAME, D_STOP_LOCATION_NAME | NOT NULL | CASE WHEN UPPER(facility_name) LIKE '%DISTRIBUTION CENTER%' OR UPPER(facility_name) LIKE '%DC%' THEN 'DISTRIBUTION_CENTER' WHEN UPPER(facility_name) LIKE '%STORE%' OR UPPER(facility_name) LIKE '%STR%' THEN 'RETAIL_STORE' WHEN UPPER(facility_name) LIKE '%WAREHOUSE%' OR UPPER(facility_name) LIKE '%WH%' THEN 'WAREHOUSE' WHEN UPPER(facility_name) LIKE '%SUPPLIER%' OR UPPER(facility_name) LIKE '%SUP%' THEN 'SUPPLIER' ELSE 'OTHER' END |
| Gold | go_facility_dimension | facility_address | Silver | sv_shipment | O_ADDRESS, D_ADDRESS | Optional | UPPER(TRIM(COALESCE(O_ADDRESS, D_ADDRESS))) |
| Gold | go_facility_dimension | facility_city | Silver | sv_shipment | O_CITY, D_CITY | NOT NULL | UPPER(TRIM(COALESCE(O_CITY, D_CITY))) |
| Gold | go_facility_dimension | facility_state | Silver | sv_shipment | O_STATE_PROV, D_STATE_PROV | NOT NULL, Valid state codes | UPPER(TRIM(COALESCE(O_STATE_PROV, D_STATE_PROV))) |
| Gold | go_facility_dimension | facility_postal_code | Silver | sv_shipment | O_POSTAL_CODE, D_POSTAL_CODE | Valid postal code format | CASE WHEN facility_country = 'US' AND LENGTH(REGEXP_REPLACE(COALESCE(O_POSTAL_CODE, D_POSTAL_CODE), '[^0-9]', '')) = 5 THEN REGEXP_REPLACE(COALESCE(O_POSTAL_CODE, D_POSTAL_CODE), '[^0-9]', '') WHEN facility_country = 'US' AND LENGTH(REGEXP_REPLACE(COALESCE(O_POSTAL_CODE, D_POSTAL_CODE), '[^0-9]', '')) = 9 THEN CONCAT(SUBSTR(REGEXP_REPLACE(COALESCE(O_POSTAL_CODE, D_POSTAL_CODE), '[^0-9]', ''), 1, 5), '-', SUBSTR(REGEXP_REPLACE(COALESCE(O_POSTAL_CODE, D_POSTAL_CODE), '[^0-9]', ''), 6, 4)) ELSE COALESCE(O_POSTAL_CODE, D_POSTAL_CODE) END |
| Gold | go_facility_dimension | facility_country | Silver | sv_shipment | O_COUNTRY_CODE, D_COUNTRY_CODE | NOT NULL, Valid country codes | UPPER(TRIM(COALESCE(O_COUNTRY_CODE, D_COUNTRY_CODE, 'US'))) |
| Gold | go_facility_dimension | facility_status | Silver | sv_shipment | - | NOT NULL | 'ACTIVE' (default for all facilities) |
| Gold | go_facility_dimension | effective_start_date | Silver | sv_shipment | CREATED_DTTM | NOT NULL | CAST(CREATED_DTTM AS DATE) |
| Gold | go_facility_dimension | effective_end_date | Silver | sv_shipment | - | NOT NULL | DATE('9999-12-31') for current records |
| Gold | go_facility_dimension | is_current | Silver | sv_shipment | - | NOT NULL | TRUE for active records |
| Gold | go_facility_dimension | load_date | Silver | sv_shipment | load_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_facility_dimension | update_date | Silver | sv_shipment | update_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_facility_dimension | source_system | Silver | sv_shipment | source_system | NOT NULL | COALESCE(source_system, 'TMS') |

### 2.3 go_user_role_dimension

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Gold | go_user_role_dimension | user_role_id | Silver | sv_shipment | - | Auto-generated surrogate key | Generate BIGINT surrogate key using ROW_NUMBER() |
| Gold | go_user_role_dimension | user_role_key | Silver | sv_shipment | CREATED_SOURCE_TYPE | NOT NULL, Unique | SHA2(CONCAT(COALESCE(CREATED_SOURCE_TYPE, ''), '\|', COALESCE(LAST_UPDATED_SOURCE_TYPE, '')), 256) |
| Gold | go_user_role_dimension | creator_role | Silver | sv_shipment | CREATED_SOURCE_TYPE | NOT NULL, Length > 0 | CASE WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'PLANNER' THEN 'TRANSPORTATION_PLANNER' WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'SYSTEM' THEN 'SYSTEM_INTEGRATION' WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'DISPATCHER' THEN 'DISPATCH_OPERATOR' WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'MANAGER' THEN 'OPERATIONS_MANAGER' ELSE UPPER(TRIM(CREATED_SOURCE_TYPE)) END |
| Gold | go_user_role_dimension | role_description | Silver | sv_shipment | CREATED_SOURCE_TYPE | Optional | CASE WHEN creator_role = 'TRANSPORTATION_PLANNER' THEN 'Plans and optimizes transportation routes' WHEN creator_role = 'SYSTEM_INTEGRATION' THEN 'Automated system processes' WHEN creator_role = 'DISPATCH_OPERATOR' THEN 'Manages shipment dispatch operations' WHEN creator_role = 'OPERATIONS_MANAGER' THEN 'Oversees transportation operations' ELSE 'General user role' END |
| Gold | go_user_role_dimension | role_department | Silver | sv_shipment | CREATED_SOURCE_TYPE | NOT NULL | CASE WHEN creator_role IN ('TRANSPORTATION_PLANNER', 'DISPATCH_OPERATOR') THEN 'TRANSPORTATION' WHEN creator_role = 'SYSTEM_INTEGRATION' THEN 'IT_SYSTEMS' WHEN creator_role = 'OPERATIONS_MANAGER' THEN 'OPERATIONS' ELSE 'GENERAL' END |
| Gold | go_user_role_dimension | role_permissions | Silver | sv_shipment | - | Optional | CASE WHEN creator_role = 'OPERATIONS_MANAGER' THEN 'FULL_ACCESS' WHEN creator_role IN ('TRANSPORTATION_PLANNER', 'DISPATCH_OPERATOR') THEN 'OPERATIONAL_ACCESS' WHEN creator_role = 'SYSTEM_INTEGRATION' THEN 'SYSTEM_ACCESS' ELSE 'READ_only' END |
| Gold | go_user_role_dimension | role_status | Silver | sv_shipment | - | NOT NULL | 'ACTIVE' (default for all roles) |
| Gold | go_user_role_dimension | load_date | Silver | sv_shipment | load_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_user_role_dimension | update_date | Silver | sv_shipment | update_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_user_role_dimension | source_system | Silver | sv_shipment | source_system | NOT NULL | COALESCE(source_system, 'TMS') |

### 2.4 go_shipment_status_codes

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Gold | go_shipment_status_codes | status_id | Silver | sv_shipment | - | Auto-generated surrogate key | Generate BIGINT surrogate key using ROW_NUMBER() |
| Gold | go_shipment_status_codes | status_code | Silver | sv_shipment | SHIPMENT_STATUS | NOT NULL, Unique | UPPER(TRIM(SHIPMENT_STATUS)) |
| Gold | go_shipment_status_codes | status_description | Silver | sv_shipment | SHIPMENT_STATUS | NOT NULL | CASE WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'PLANNED' THEN 'Planning' WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'IN_TRANSIT' THEN 'In Transit' WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'DELIVERED' THEN 'Completed' WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'CANCELLED' THEN 'Cancelled' ELSE 'Other' END |
| Gold | go_shipment_status_codes | status_category | Silver | sv_shipment | SHIPMENT_STATUS | NOT NULL | CASE WHEN UPPER(TRIM(SHIPMENT_STATUS)) IN ('PLANNED', 'TENDERED') THEN 'PLANNING' WHEN UPPER(TRIM(SHIPMENT_STATUS)) IN ('IN_TRANSIT', 'PICKED_UP') THEN 'ACTIVE' WHEN UPPER(TRIM(SHIPMENT_STATUS)) IN ('DELIVERED', 'COMPLETED') THEN 'COMPLETED' WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'CANCELLED' THEN 'CANCELLED' ELSE 'OTHER' END |
| Gold | go_shipment_status_codes | is_active | Silver | sv_shipment | IS_SHIPMENT_CANCELLED | NOT NULL | CASE WHEN UPPER(SHIPMENT_STATUS) = 'CANCELLED' OR IS_SHIPMENT_CANCELLED = 'Y' THEN FALSE ELSE TRUE END |
| Gold | go_shipment_status_codes | load_date | Silver | sv_shipment | load_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_shipment_status_codes | update_date | Silver | sv_shipment | update_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_shipment_status_codes | source_system | Silver | sv_shipment | source_system | NOT NULL | COALESCE(source_system, 'TMS') |

### 2.5 go_transport_mode_codes

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Gold | go_transport_mode_codes | transport_mode_id | Silver | sv_shipment | - | Auto-generated surrogate key | Generate BIGINT surrogate key using ROW_NUMBER() |
| Gold | go_transport_mode_codes | transport_mode_code | Silver | sv_shipment | ASSIGNED_MOT_ID | NOT NULL, Unique | UPPER(TRIM(ASSIGNED_MOT_ID)) |
| Gold | go_transport_mode_codes | transport_mode_description | Silver | sv_shipment | ASSIGNED_MOT_ID | NOT NULL | CASE WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'TRUCK' THEN 'Ground Transportation - Truck' WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'RAIL' THEN 'Ground Transportation - Rail' WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'AIR' THEN 'Air Transportation' WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'OCEAN' THEN 'Ocean Transportation' ELSE 'Other Transportation Mode' END |
| Gold | go_transport_mode_codes | transport_category | Silver | sv_shipment | ASSIGNED_MOT_ID | NOT NULL | CASE WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) IN ('TRUCK', 'RAIL') THEN 'GROUND' WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'AIR' THEN 'AIR' WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'OCEAN' THEN 'WATER' ELSE 'OTHER' END |
| Gold | go_transport_mode_codes | is_active | Silver | sv_shipment | - | NOT NULL | TRUE (default for all transport modes) |
| Gold | go_transport_mode_codes | load_date | Silver | sv_shipment | load_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_transport_mode_codes | update_date | Silver | sv_shipment | update_date | NOT NULL | CURRENT_TIMESTAMP |
| Gold | go_transport_mode_codes | source_system | Silver | sv_shipment | source_system | NOT NULL | COALESCE(source_system, 'TMS') |

---

## 3. Data Quality and Validation Rules

### 3.1 Mandatory Field Validation
- **Rule**: All dimension tables must have non-null values for key business attributes
- **Implementation**: Use COALESCE and CASE statements to handle null values
- **Error Handling**: Log validation errors to go_data_validation_errors table

### 3.2 Referential Integrity Validation
- **Rule**: All dimension keys referenced in fact tables must exist in dimension tables
- **Implementation**: Use LEFT JOIN validation queries to identify orphaned records
- **Error Handling**: Quarantine invalid records for manual review

### 3.3 Data Type Conversion Validation
- **Rule**: Ensure proper data type conversions, especially for legacy system integrations
- **Implementation**: Use TRY_CAST functions with error handling
- **Error Handling**: Log conversion errors with original and target values

### 3.4 Business Rule Validation
- **Rule**: Apply domain-specific validation rules (e.g., postal code formats, carrier codes)
- **Implementation**: Use REGEXP and CASE statements for pattern matching
- **Error Handling**: Flag invalid records for business user review

---

## 4. Slowly Changing Dimension (SCD) Implementation

### 4.1 SCD Type 2 for Carrier Dimension
- **Purpose**: Track historical changes in carrier information
- **Implementation**: Use MERGE statements with effective date ranges
- **Key Fields**: effective_start_date, effective_end_date, is_current

### 4.2 SCD Type 2 for Facility Dimension
- **Purpose**: Track facility changes over time (address updates, status changes)
- **Implementation**: Similar to carrier dimension with date range tracking
- **Key Fields**: effective_start_date, effective_end_date, is_current

---

## 5. Performance Optimization

### 5.1 Surrogate Key Generation
- **Method**: Use SHA2 hash functions for deterministic key generation
- **Benefits**: Consistent keys across pipeline runs, improved join performance

### 5.2 Partitioning Strategy
- **Carrier Dimension**: Partition by effective_start_date
- **Facility Dimension**: Partition by effective_start_date
- **Code Tables**: No partitioning due to small size

### 5.3 Indexing Recommendations
- **Primary Keys**: All surrogate key fields
- **Foreign Keys**: All dimension key fields used in fact table joins
- **Business Keys**: Natural business identifiers for lookup performance

---

## 6. Error Handling and Monitoring

### 6.1 Data Validation Errors
- **Capture**: All validation rule violations
- **Storage**: go_data_validation_errors table
- **Monitoring**: Daily error count reports and alerts

### 6.2 Pipeline Audit
- **Capture**: Pipeline execution metrics and performance
- **Storage**: go_pipeline_audit table
- **Monitoring**: Execution time trends and failure analysis

### 6.3 Data Quality Metrics
- **Completeness**: Percentage of non-null values for mandatory fields
- **Accuracy**: Percentage of records passing validation rules
- **Consistency**: Cross-table referential integrity checks

---

## 7. Implementation Guidelines

### 7.1 PySpark Implementation
```python
# Example transformation for carrier dimension
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Carrier name standardization
carrier_df = silver_df.select(
    F.sha2(F.concat_ws('|', 
                      F.coalesce(F.col('ASSIGNED_CARRIER_CODE'), F.lit('')),
                      F.coalesce(F.col('ASSIGNED_MOT_ID'), F.lit(''))), 256).alias('carrier_key'),
    F.when(F.upper(F.trim(F.col('ASSIGNED_CARRIER_CODE'))) == 'FEDX', 'FEDEX')
     .when(F.upper(F.trim(F.col('ASSIGNED_CARRIER_CODE'))) == 'UPSFR', 'UPS FREIGHT')
     .when(F.upper(F.trim(F.col('ASSIGNED_CARRIER_CODE'))) == 'XPOLS', 'XPO LOGISTICS')
     .otherwise(F.upper(F.trim(F.col('ASSIGNED_CARRIER_CODE')))).alias('primary_carrier_name'),
    F.current_timestamp().alias('load_date')
)
```

### 7.2 Delta Lake MERGE Operations
```sql
-- SCD Type 2 implementation example
MERGE INTO gold.go_carrier_dimension AS target
USING (
    SELECT carrier_key, primary_carrier_name, mode_of_transport, 
           CURRENT_DATE as effective_start_date,
           DATE('9999-12-31') as effective_end_date,
           TRUE as is_current
    FROM staging_carrier_updates
) AS source
ON target.carrier_key = source.carrier_key AND target.is_current = TRUE
WHEN MATCHED AND (
    target.primary_carrier_name != source.primary_carrier_name OR
    target.mode_of_transport != source.mode_of_transport
) THEN
    UPDATE SET 
        effective_end_date = CURRENT_DATE - INTERVAL 1 DAY,
        is_current = FALSE
WHEN NOT MATCHED THEN
    INSERT (carrier_key, primary_carrier_name, mode_of_transport, 
            effective_start_date, effective_end_date, is_current)
    VALUES (source.carrier_key, source.primary_carrier_name, source.mode_of_transport,
            source.effective_start_date, source.effective_end_date, source.is_current)
```

---

## 8. API Cost

**apiCost**: 0.1892

---

**outputURL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Data_Mapping

**pipelineID**: 14671