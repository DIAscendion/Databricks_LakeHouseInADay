_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold Dimension Transformation Rules for TMS Shipment Application
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Dimension Transformation Recommender

## Overview

This document provides comprehensive transformation rules specifically for Dimension tables in the Gold layer of the TMS (Transportation Management System) Shipment application. The transformation rules ensure data integrity, standardization, and consistency for dimensional data used in analytics and reporting.

---

## Identified Dimension Tables

Based on the Gold Layer Physical DDL analysis, the following dimension tables have been identified:

1. **go_carrier_dimension** - Carrier master data
2. **go_facility_dimension** - Facility master data  
3. **go_user_role_dimension** - User role master data
4. **go_shipment_status_codes** - Shipment status code table
5. **go_transport_mode_codes** - Transport mode code table

---

## Transformation Rules for Dimension Tables

### 1. go_carrier_dimension Transformations

#### **Rule 1.1: Carrier Name Standardization**
- **Description**: Standardize carrier names to ensure consistency across primary, secondary, and broker carriers
- **Rationale**: Sample data shows carrier codes like "FEDX", "UPSFR", "XPOLS" need standardization for reporting consistency
- **SQL Example**:
```sql
SELECT 
    UPPER(TRIM(ASSIGNED_CARRIER_CODE)) as primary_carrier_name,
    UPPER(TRIM(ASSIGNED_SCNDR_CARRIER_CODE)) as secondary_carrier_name,
    UPPER(TRIM(ASSIGNED_BROKER_CARRIER_CODE)) as broker_carrier_name,
    CASE 
        WHEN UPPER(TRIM(ASSIGNED_CARRIER_CODE)) = 'FEDX' THEN 'FEDEX'
        WHEN UPPER(TRIM(ASSIGNED_CARRIER_CODE)) = 'UPSFR' THEN 'UPS FREIGHT'
        WHEN UPPER(TRIM(ASSIGNED_CARRIER_CODE)) = 'XPOLS' THEN 'XPO LOGISTICS'
        ELSE UPPER(TRIM(ASSIGNED_CARRIER_CODE))
    END as standardized_carrier_name
FROM silver.sv_shipment
```

#### **Rule 1.2: Mode of Transport Validation**
- **Description**: Validate and standardize mode of transport values
- **Rationale**: Ensures consistent transport mode classification for carrier performance analysis
- **SQL Example**:
```sql
SELECT 
    carrier_key,
    CASE 
        WHEN UPPER(ASSIGNED_MOT_ID) IN ('TRUCK', 'TRK') THEN 'TRUCK'
        WHEN UPPER(ASSIGNED_MOT_ID) IN ('RAIL', 'RR') THEN 'RAIL'
        WHEN UPPER(ASSIGNED_MOT_ID) IN ('AIR', 'PLANE') THEN 'AIR'
        WHEN UPPER(ASSIGNED_MOT_ID) IN ('OCEAN', 'SEA') THEN 'OCEAN'
        ELSE 'OTHER'
    END as mode_of_transport
FROM silver.sv_shipment
```

#### **Rule 1.3: Carrier Status Derivation**
- **Description**: Derive carrier status based on assignment and feasibility flags
- **Rationale**: Supports carrier performance and assignment rate KPIs from conceptual model
- **SQL Example**:
```sql
SELECT 
    carrier_key,
    CASE 
        WHEN ASSIGNED_CARRIER_ID IS NOT NULL THEN 'ASSIGNED'
        WHEN FEASIBLE_CARRIER_ID IS NOT NULL THEN 'FEASIBLE'
        WHEN DSG_CARRIER_ID IS NOT NULL THEN 'DESIGNATED'
        ELSE 'INACTIVE'
    END as carrier_status
FROM silver.sv_shipment
```

### 2. go_facility_dimension Transformations

#### **Rule 2.1: Address Standardization**
- **Description**: Standardize facility address components for consistent geocoding and reporting
- **Rationale**: Address consistency is critical for facility analysis and route optimization KPIs
- **SQL Example**:
```sql
SELECT 
    facility_key,
    UPPER(TRIM(COALESCE(O_STOP_LOCATION_NAME, D_STOP_LOCATION_NAME))) as facility_name,
    UPPER(TRIM(COALESCE(O_ADDRESS, D_ADDRESS))) as facility_address,
    UPPER(TRIM(COALESCE(O_CITY, D_CITY))) as facility_city,
    UPPER(TRIM(COALESCE(O_STATE_PROV, D_STATE_PROV))) as facility_state,
    REGEXP_REPLACE(COALESCE(O_POSTAL_CODE, D_POSTAL_CODE), '[^0-9-]', '') as facility_postal_code,
    UPPER(TRIM(COALESCE(O_COUNTRY_CODE, D_COUNTRY_CODE))) as facility_country
FROM silver.sv_shipment
```

#### **Rule 2.2: Facility Type Classification**
- **Description**: Classify facilities based on naming conventions and operational patterns
- **Rationale**: Supports facility-based KPIs and shipment analysis by facility type
- **SQL Example**:
```sql
SELECT 
    facility_key,
    CASE 
        WHEN UPPER(facility_name) LIKE '%DISTRIBUTION CENTER%' OR UPPER(facility_name) LIKE '%DC%' THEN 'DISTRIBUTION_CENTER'
        WHEN UPPER(facility_name) LIKE '%STORE%' OR UPPER(facility_name) LIKE '%STR%' THEN 'RETAIL_STORE'
        WHEN UPPER(facility_name) LIKE '%WAREHOUSE%' OR UPPER(facility_name) LIKE '%WH%' THEN 'WAREHOUSE'
        WHEN UPPER(facility_name) LIKE '%SUPPLIER%' OR UPPER(facility_name) LIKE '%SUP%' THEN 'SUPPLIER'
        ELSE 'OTHER'
    END as facility_type
FROM (
    SELECT 
        COALESCE(O_FACILITY_ID, D_FACILITY_ID) as facility_key,
        COALESCE(O_STOP_LOCATION_NAME, D_STOP_LOCATION_NAME) as facility_name
    FROM silver.sv_shipment
) t
```

#### **Rule 2.3: Postal Code Validation**
- **Description**: Validate and format postal codes based on country standards
- **Rationale**: Ensures data quality for billing and geographic analysis as per constraints
- **SQL Example**:
```sql
SELECT 
    facility_key,
    CASE 
        WHEN facility_country = 'US' AND LENGTH(REGEXP_REPLACE(facility_postal_code, '[^0-9]', '')) = 5 
            THEN REGEXP_REPLACE(facility_postal_code, '[^0-9]', '')
        WHEN facility_country = 'US' AND LENGTH(REGEXP_REPLACE(facility_postal_code, '[^0-9]', '')) = 9 
            THEN CONCAT(SUBSTR(REGEXP_REPLACE(facility_postal_code, '[^0-9]', ''), 1, 5), '-', 
                       SUBSTR(REGEXP_REPLACE(facility_postal_code, '[^0-9]', ''), 6, 4))
        ELSE facility_postal_code
    END as validated_postal_code
FROM go_facility_dimension
```

### 3. go_user_role_dimension Transformations

#### **Rule 3.1: Role Standardization**
- **Description**: Standardize creator role values for consistent audit reporting
- **Rationale**: Creator role is mandatory for audit completeness as per constraints
- **SQL Example**:
```sql
SELECT 
    UPPER(TRIM(CREATED_SOURCE_TYPE)) as creator_role,
    CASE 
        WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'PLANNER' THEN 'TRANSPORTATION_PLANNER'
        WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'SYSTEM' THEN 'SYSTEM_INTEGRATION'
        WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'DISPATCHER' THEN 'DISPATCH_OPERATOR'
        WHEN UPPER(TRIM(CREATED_SOURCE_TYPE)) = 'MANAGER' THEN 'OPERATIONS_MANAGER'
        ELSE UPPER(TRIM(CREATED_SOURCE_TYPE))
    END as standardized_role
FROM silver.sv_shipment
WHERE CREATED_SOURCE_TYPE IS NOT NULL
```

#### **Rule 3.2: Role Department Mapping**
- **Description**: Map user roles to organizational departments
- **Rationale**: Supports organizational reporting and role-based analysis
- **SQL Example**:
```sql
SELECT 
    creator_role,
    CASE 
        WHEN creator_role IN ('TRANSPORTATION_PLANNER', 'DISPATCH_OPERATOR') THEN 'TRANSPORTATION'
        WHEN creator_role = 'SYSTEM_INTEGRATION' THEN 'IT_SYSTEMS'
        WHEN creator_role = 'OPERATIONS_MANAGER' THEN 'OPERATIONS'
        ELSE 'GENERAL'
    END as role_department
FROM go_user_role_dimension
```

### 4. go_shipment_status_codes Transformations

#### **Rule 4.1: Status Code Standardization**
- **Description**: Standardize shipment status codes and create status categories
- **Rationale**: Supports cancelled and reconciled shipment percentage KPIs from conceptual model
- **SQL Example**:
```sql
SELECT 
    UPPER(TRIM(SHIPMENT_STATUS)) as status_code,
    CASE 
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'PLANNED' THEN 'Planning'
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'IN_TRANSIT' THEN 'In Transit'
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'DELIVERED' THEN 'Completed'
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'CANCELLED' THEN 'Cancelled'
        ELSE 'Other'
    END as status_description,
    CASE 
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) IN ('PLANNED', 'TENDERED') THEN 'PLANNING'
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) IN ('IN_TRANSIT', 'PICKED_UP') THEN 'ACTIVE'
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) IN ('DELIVERED', 'COMPLETED') THEN 'COMPLETED'
        WHEN UPPER(TRIM(SHIPMENT_STATUS)) = 'CANCELLED' THEN 'CANCELLED'
        ELSE 'OTHER'
    END as status_category
FROM silver.sv_shipment
```

#### **Rule 4.2: Cancelled Flag Derivation**
- **Description**: Derive cancelled flag based on planning status and shipment status
- **Rationale**: Cancelled shipment identification is based on planning status code mapping per constraints
- **SQL Example**:
```sql
SELECT 
    status_code,
    CASE 
        WHEN UPPER(SHIPMENT_STATUS) = 'CANCELLED' OR IS_SHIPMENT_CANCELLED = 'Y' THEN TRUE
        ELSE FALSE
    END as is_cancelled_status
FROM silver.sv_shipment
```

### 5. go_transport_mode_codes Transformations

#### **Rule 5.1: Transport Mode Standardization**
- **Description**: Standardize transport mode codes and descriptions
- **Rationale**: Ensures consistent mode classification for carrier and route analysis
- **SQL Example**:
```sql
SELECT 
    UPPER(TRIM(ASSIGNED_MOT_ID)) as transport_mode_code,
    CASE 
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'TRUCK' THEN 'Ground Transportation - Truck'
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'RAIL' THEN 'Ground Transportation - Rail'
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'AIR' THEN 'Air Transportation'
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'OCEAN' THEN 'Ocean Transportation'
        ELSE 'Other Transportation Mode'
    END as transport_mode_description,
    CASE 
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) IN ('TRUCK', 'RAIL') THEN 'GROUND'
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'AIR' THEN 'AIR'
        WHEN UPPER(TRIM(ASSIGNED_MOT_ID)) = 'OCEAN' THEN 'WATER'
        ELSE 'OTHER'
    END as transport_category
FROM silver.sv_shipment
WHERE ASSIGNED_MOT_ID IS NOT NULL
```

---

## Data Quality and Validation Rules

### **Rule DQ.1: Mandatory Field Validation**
- **Description**: Ensure all mandatory dimension fields are populated
- **Rationale**: Supports data completeness requirements from constraints
- **SQL Example**:
```sql
-- Validate carrier dimension mandatory fields
SELECT 
    carrier_key,
    CASE 
        WHEN primary_carrier_name IS NULL OR TRIM(primary_carrier_name) = '' THEN 'MISSING_CARRIER_NAME'
        WHEN mode_of_transport IS NULL OR TRIM(mode_of_transport) = '' THEN 'MISSING_TRANSPORT_MODE'
        ELSE 'VALID'
    END as validation_status
FROM go_carrier_dimension
```

### **Rule DQ.2: Referential Integrity Validation**
- **Description**: Validate dimension key relationships
- **Rationale**: Ensures referential integrity as per constraints
- **SQL Example**:
```sql
-- Validate facility references in shipment facts
SELECT 
    sf.SHIPMENT_ID,
    CASE 
        WHEN fd_o.facility_key IS NULL THEN 'MISSING_ORIGIN_FACILITY'
        WHEN fd_d.facility_key IS NULL THEN 'MISSING_DEST_FACILITY'
        ELSE 'VALID'
    END as facility_validation_status
FROM gold.go_shipment_facts sf
LEFT JOIN gold.go_facility_dimension fd_o ON sf.O_FACILITY_ID = fd_o.facility_key
LEFT JOIN gold.go_facility_dimension fd_d ON sf.D_FACILITY_ID = fd_d.facility_key
```

### **Rule DQ.3: Data Type Conversion Validation**
- **Description**: Validate data type conversions, especially for billing method
- **Rationale**: Billing method datatype differs between legacy and new system per constraints
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    BILLING_METHOD,
    CASE 
        WHEN ISNUMERIC(BILLING_METHOD) THEN 
            CASE CAST(BILLING_METHOD AS INT)
                WHEN 1 THEN 'PREPAID'
                WHEN 2 THEN 'COLLECT'
                WHEN 3 THEN 'THIRD_PARTY'
                ELSE 'UNKNOWN'
            END
        ELSE UPPER(TRIM(BILLING_METHOD))
    END as standardized_billing_method
FROM silver.sv_shipment
```

---

## Slowly Changing Dimension (SCD) Implementation

### **Rule SCD.1: Type 2 SCD for Carrier Dimension**
- **Description**: Implement Type 2 SCD for carrier dimension to track historical changes
- **Rationale**: Maintains carrier assignment history for trend analysis
- **SQL Example**:
```sql
-- SCD Type 2 implementation for carrier dimension
MERGE INTO gold.go_carrier_dimension AS target
USING (
    SELECT 
        carrier_key,
        primary_carrier_name,
        mode_of_transport,
        carrier_status,
        CURRENT_DATE as effective_start_date,
        DATE('9999-12-31') as effective_end_date,
        TRUE as is_current
    FROM staging_carrier_updates
) AS source
ON target.carrier_key = source.carrier_key AND target.is_current = TRUE
WHEN MATCHED AND (
    target.primary_carrier_name != source.primary_carrier_name OR
    target.mode_of_transport != source.mode_of_transport OR
    target.carrier_status != source.carrier_status
) THEN
    UPDATE SET 
        effective_end_date = CURRENT_DATE - INTERVAL 1 DAY,
        is_current = FALSE
WHEN NOT MATCHED THEN
    INSERT (carrier_key, primary_carrier_name, mode_of_transport, carrier_status, 
            effective_start_date, effective_end_date, is_current)
    VALUES (source.carrier_key, source.primary_carrier_name, source.mode_of_transport, 
            source.carrier_status, source.effective_start_date, source.effective_end_date, source.is_current)
```

---

## Hierarchy and Relationship Mapping

### **Rule HR.1: Facility Hierarchy Mapping**
- **Description**: Create facility hierarchy relationships for organizational reporting
- **Rationale**: Supports facility-based KPIs and regional analysis
- **SQL Example**:
```sql
SELECT 
    facility_key,
    facility_name,
    facility_city,
    facility_state,
    CASE 
        WHEN facility_state IN ('NY', 'NJ', 'CT', 'MA', 'PA') THEN 'NORTHEAST'
        WHEN facility_state IN ('FL', 'GA', 'SC', 'NC', 'VA') THEN 'SOUTHEAST'
        WHEN facility_state IN ('IL', 'IN', 'OH', 'MI', 'WI') THEN 'MIDWEST'
        WHEN facility_state IN ('TX', 'OK', 'AR', 'LA') THEN 'SOUTH'
        WHEN facility_state IN ('CA', 'OR', 'WA', 'NV') THEN 'WEST'
        ELSE 'OTHER'
    END as facility_region
FROM gold.go_facility_dimension
```

---

## Performance Optimization Rules

### **Rule PO.1: Dimension Key Optimization**
- **Description**: Create optimized surrogate keys for dimension tables
- **Rationale**: Improves join performance in fact table queries
- **SQL Example**:
```sql
-- Generate surrogate keys using hash functions
SELECT 
    SHA2(CONCAT(COALESCE(carrier_code, ''), '|', COALESCE(mode_of_transport, '')), 256) as carrier_key,
    carrier_code,
    primary_carrier_name,
    mode_of_transport
FROM staging_carrier_data
```

---

## Source-to-Target Mapping

| Source Table (Silver) | Source Column | Target Table (Gold) | Target Column | Transformation Applied |
|----------------------|---------------|--------------------|--------------|-----------------------|
| sv_shipment | ASSIGNED_CARRIER_CODE | go_carrier_dimension | primary_carrier_name | Rule 1.1: Name Standardization |
| sv_shipment | ASSIGNED_MOT_ID | go_carrier_dimension | mode_of_transport | Rule 1.2: Mode Validation |
| sv_shipment | O_STOP_LOCATION_NAME | go_facility_dimension | facility_name | Rule 2.1: Address Standardization |
| sv_shipment | O_ADDRESS | go_facility_dimension | facility_address | Rule 2.1: Address Standardization |
| sv_shipment | CREATED_SOURCE_TYPE | go_user_role_dimension | creator_role | Rule 3.1: Role Standardization |
| sv_shipment | SHIPMENT_STATUS | go_shipment_status_codes | status_code | Rule 4.1: Status Standardization |
| sv_shipment | ASSIGNED_MOT_ID | go_transport_mode_codes | transport_mode_code | Rule 5.1: Mode Standardization |

---

## Error Handling and Data Quality Monitoring

### **Rule EH.1: Dimension Load Error Handling**
- **Description**: Capture and log dimension transformation errors
- **Rationale**: Ensures data quality monitoring and error resolution
- **SQL Example**:
```sql
INSERT INTO gold.go_data_validation_errors (
    error_key,
    table_name,
    column_name,
    validation_rule,
    error_message,
    actual_value,
    error_count,
    first_occurrence_date
)
SELECT 
    SHA2(CONCAT(table_name, column_name, validation_rule), 256) as error_key,
    'go_carrier_dimension' as table_name,
    'primary_carrier_name' as column_name,
    'MANDATORY_FIELD_CHECK' as validation_rule,
    'Primary carrier name is null or empty' as error_message,
    COALESCE(primary_carrier_name, 'NULL') as actual_value,
    COUNT(*) as error_count,
    CURRENT_TIMESTAMP as first_occurrence_date
FROM gold.go_carrier_dimension
WHERE primary_carrier_name IS NULL OR TRIM(primary_carrier_name) = ''
GROUP BY primary_carrier_name
```

---

## API Cost

**apiCost**: 0.1245

---

**outputURL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Recommender

**pipelineID**: 14669