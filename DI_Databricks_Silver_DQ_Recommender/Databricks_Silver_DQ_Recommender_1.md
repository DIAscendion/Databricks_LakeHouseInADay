_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Comprehensive Data Quality Checks for TMS Shipment Application
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Recommender

## Overview

This document provides comprehensive data quality check recommendations for the TMS (Transportation Management System) Shipment application based on the analysis of DDL statements, business rules, and data constraints. The recommendations are designed to ensure data integrity, accuracy, and consistency across the Silver layer of the Medallion architecture.

## Data Quality Check Categories

### 1. Mandatory Field Validation Checks

#### 1.1 Core Identifier Completeness Check
**Check Name**: Core Shipment Identifier Validation
**Description**: Validates that essential shipment identifiers are present and non-null
**Rationale**: Based on business rules requiring shipment identifier, status, type, origin facility, destination facility, assigned carrier, creation date, and creator role for every shipment record
**SQL Example**:
```sql
SELECT 
  COUNT(*) as total_records,
  COUNT(CASE WHEN SHIPMENT_ID IS NULL OR TRIM(SHIPMENT_ID) = '' THEN 1 END) as missing_shipment_id,
  COUNT(CASE WHEN SHIPMENT_STATUS IS NULL OR TRIM(SHIPMENT_STATUS) = '' THEN 1 END) as missing_status,
  COUNT(CASE WHEN SHIPMENT_TYPE IS NULL OR TRIM(SHIPMENT_TYPE) = '' THEN 1 END) as missing_type,
  COUNT(CASE WHEN O_FACILITY_ID IS NULL OR TRIM(O_FACILITY_ID) = '' THEN 1 END) as missing_origin,
  COUNT(CASE WHEN D_FACILITY_ID IS NULL OR TRIM(D_FACILITY_ID) = '' THEN 1 END) as missing_destination,
  COUNT(CASE WHEN ASSIGNED_CARRIER_ID IS NULL OR TRIM(ASSIGNED_CARRIER_ID) = '' THEN 1 END) as missing_carrier,
  COUNT(CASE WHEN CREATED_DTTM IS NULL THEN 1 END) as missing_creation_date,
  COUNT(CASE WHEN CREATED_SOURCE IS NULL OR TRIM(CREATED_SOURCE) = '' THEN 1 END) as missing_creator
FROM silver.shipment;
```

#### 1.2 Audit Trail Completeness Check
**Check Name**: Creation Source and Type Validation
**Description**: Ensures creation source and creator role are non-null for audit completeness
**Rationale**: Business rules mandate non-null creation source and creator role for audit completeness
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  CREATED_SOURCE,
  CREATED_SOURCE_TYPE,
  CASE 
    WHEN CREATED_SOURCE IS NULL OR TRIM(CREATED_SOURCE) = '' THEN 'Missing Creation Source'
    WHEN CREATED_SOURCE_TYPE IS NULL OR TRIM(CREATED_SOURCE_TYPE) = '' THEN 'Missing Creator Role'
    ELSE 'Valid'
  END as audit_status
FROM silver.shipment
WHERE CREATED_SOURCE IS NULL OR TRIM(CREATED_SOURCE) = '' 
   OR CREATED_SOURCE_TYPE IS NULL OR TRIM(CREATED_SOURCE_TYPE) = '';
```

### 2. Data Type and Format Validation Checks

#### 2.1 Numeric Field Range Validation
**Check Name**: Distance and Weight Range Validation
**Description**: Validates that numeric fields contain non-negative values and logical ranges
**Rationale**: Business rules specify distance values must be non-negative and direct distance must not exceed total route distance
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  DISTANCE,
  DIRECT_DISTANCE,
  OUT_OF_ROUTE_DISTANCE,
  PLANNED_WEIGHT,
  CASE 
    WHEN DISTANCE < 0 THEN 'Negative Total Distance'
    WHEN DIRECT_DISTANCE < 0 THEN 'Negative Direct Distance'
    WHEN OUT_OF_ROUTE_DISTANCE < 0 THEN 'Negative Out-of-Route Distance'
    WHEN DIRECT_DISTANCE > DISTANCE THEN 'Direct Distance Exceeds Total Distance'
    WHEN PLANNED_WEIGHT < 0 THEN 'Negative Weight'
    ELSE 'Valid'
  END as validation_status
FROM silver.shipment
WHERE DISTANCE < 0 OR DIRECT_DISTANCE < 0 OR OUT_OF_ROUTE_DISTANCE < 0 
   OR DIRECT_DISTANCE > DISTANCE OR PLANNED_WEIGHT < 0;
```

#### 2.2 Currency and Financial Data Validation
**Check Name**: Financial Field Consistency Check
**Description**: Validates currency codes and financial amounts for consistency
**Rationale**: Multiple currency fields require validation for proper financial reporting and cost analysis
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  TOTAL_COST,
  CURRENCY_CODE,
  ACTUAL_COST,
  ACTUAL_COST_CURRENCY_CODE,
  CASE 
    WHEN TOTAL_COST < 0 THEN 'Negative Total Cost'
    WHEN ACTUAL_COST < 0 THEN 'Negative Actual Cost'
    WHEN CURRENCY_CODE IS NULL AND TOTAL_COST IS NOT NULL THEN 'Missing Currency Code'
    WHEN LENGTH(TRIM(CURRENCY_CODE)) != 3 THEN 'Invalid Currency Code Format'
    ELSE 'Valid'
  END as financial_validation_status
FROM silver.shipment
WHERE TOTAL_COST < 0 OR ACTUAL_COST < 0 
   OR (CURRENCY_CODE IS NULL AND TOTAL_COST IS NOT NULL)
   OR LENGTH(TRIM(CURRENCY_CODE)) != 3;
```

#### 2.3 Date and Time Format Validation
**Check Name**: Date Range and Format Validation
**Description**: Validates date fields for proper format and logical date ranges
**Rationale**: Creation date must be in valid date format and fall within expected operational date range
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  CREATED_DTTM,
  SHIPMENT_START_DTTM,
  SHIPMENT_END_DTTM,
  PICKUP_START_DATE,
  DELIVERY_START_DTTM,
  CASE 
    WHEN CREATED_DTTM > CURRENT_TIMESTAMP() THEN 'Future Creation Date'
    WHEN CREATED_DTTM < '2020-01-01' THEN 'Creation Date Too Old'
    WHEN SHIPMENT_END_DTTM < SHIPMENT_START_DTTM THEN 'End Date Before Start Date'
    WHEN DELIVERY_START_DTTM < PICKUP_START_DATE THEN 'Delivery Before Pickup'
    ELSE 'Valid'
  END as date_validation_status
FROM silver.shipment
WHERE CREATED_DTTM > CURRENT_TIMESTAMP() OR CREATED_DTTM < '2020-01-01'
   OR SHIPMENT_END_DTTM < SHIPMENT_START_DTTM
   OR DELIVERY_START_DTTM < PICKUP_START_DATE;
```

### 3. Domain Value Validation Checks

#### 3.1 Shipment Status Domain Validation
**Check Name**: Shipment Status Domain Check
**Description**: Validates shipment status against predefined domain values
**Rationale**: Business rules specify shipment status must be a valid predefined domain value
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  SHIPMENT_STATUS,
  CASE 
    WHEN SHIPMENT_STATUS NOT IN ('PLANNED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED') THEN 'Invalid Status'
    ELSE 'Valid'
  END as status_validation
FROM silver.shipment
WHERE SHIPMENT_STATUS NOT IN ('PLANNED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED');
```

#### 3.2 Distance Unit of Measure Consistency
**Check Name**: Distance UOM Consistency Check
**Description**: Validates distance unit of measure consistency across all rows
**Rationale**: Business rules require distance unit of measure to be consistent; mixed units must be flagged and converted
**SQL Example**:
```sql
SELECT 
  DISTANCE_UOM,
  COUNT(*) as record_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM silver.shipment
WHERE DISTANCE_UOM IS NOT NULL
GROUP BY DISTANCE_UOM
ORDER BY record_count DESC;

-- Flag mixed units
SELECT 
  SHIPMENT_ID,
  DISTANCE_UOM,
  RADIAL_DISTANCE_UOM,
  CASE 
    WHEN DISTANCE_UOM NOT IN ('MI', 'KM') THEN 'Invalid Distance UOM'
    WHEN RADIAL_DISTANCE_UOM NOT IN ('MI', 'KM') THEN 'Invalid Radial Distance UOM'
    WHEN DISTANCE_UOM != RADIAL_DISTANCE_UOM THEN 'Inconsistent Distance UOM'
    ELSE 'Valid'
  END as uom_validation_status
FROM silver.shipment
WHERE DISTANCE_UOM NOT IN ('MI', 'KM') 
   OR RADIAL_DISTANCE_UOM NOT IN ('MI', 'KM')
   OR DISTANCE_UOM != RADIAL_DISTANCE_UOM;
```

#### 3.3 Flag Field Validation
**Check Name**: Boolean Flag Field Validation
**Description**: Validates Y/N flag fields contain only valid values
**Rationale**: Multiple flag fields should contain only 'Y' or 'N' values for proper boolean logic
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  IS_SHIPMENT_CANCELLED,
  IS_SHIPMENT_RECONCILED,
  IS_HAZMAT,
  IS_PERISHABLE,
  HAS_ALERTS,
  CASE 
    WHEN IS_SHIPMENT_CANCELLED NOT IN ('Y', 'N') AND IS_SHIPMENT_CANCELLED IS NOT NULL THEN 'Invalid Cancelled Flag'
    WHEN IS_SHIPMENT_RECONCILED NOT IN ('Y', 'N') AND IS_SHIPMENT_RECONCILED IS NOT NULL THEN 'Invalid Reconciled Flag'
    WHEN IS_HAZMAT NOT IN ('Y', 'N') AND IS_HAZMAT IS NOT NULL THEN 'Invalid Hazmat Flag'
    WHEN IS_PERISHABLE NOT IN ('Y', 'N') AND IS_PERISHABLE IS NOT NULL THEN 'Invalid Perishable Flag'
    WHEN HAS_ALERTS NOT IN ('Y', 'N') AND HAS_ALERTS IS NOT NULL THEN 'Invalid Alerts Flag'
    ELSE 'Valid'
  END as flag_validation_status
FROM silver.shipment
WHERE (IS_SHIPMENT_CANCELLED NOT IN ('Y', 'N') AND IS_SHIPMENT_CANCELLED IS NOT NULL)
   OR (IS_SHIPMENT_RECONCILED NOT IN ('Y', 'N') AND IS_SHIPMENT_RECONCILED IS NOT NULL)
   OR (IS_HAZMAT NOT IN ('Y', 'N') AND IS_HAZMAT IS NOT NULL)
   OR (IS_PERISHABLE NOT IN ('Y', 'N') AND IS_PERISHABLE IS NOT NULL)
   OR (HAS_ALERTS NOT IN ('Y', 'N') AND HAS_ALERTS IS NOT NULL);
```

### 4. Uniqueness and Referential Integrity Checks

#### 4.1 Shipment Identifier Uniqueness
**Check Name**: Shipment ID Uniqueness Check
**Description**: Validates shipment identifier uniqueness per row at base grain
**Rationale**: Business rules require shipment identifier to be unique per row at the base grain
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  COUNT(*) as duplicate_count
FROM silver.shipment
GROUP BY SHIPMENT_ID
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

#### 4.2 Bill of Lading Uniqueness
**Check Name**: Bill of Lading Uniqueness Check
**Description**: Validates bill of lading number uniqueness for billing reconciliation
**Rationale**: Business rules specify bill of lading number should be unique for each shipment for billing reconciliation
**SQL Example**:
```sql
SELECT 
  BILL_OF_LADING_NUMBER,
  COUNT(*) as duplicate_count,
  STRING_AGG(SHIPMENT_ID, ', ') as affected_shipments
FROM silver.shipment
WHERE BILL_OF_LADING_NUMBER IS NOT NULL AND TRIM(BILL_OF_LADING_NUMBER) != ''
GROUP BY BILL_OF_LADING_NUMBER
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

### 5. Business Logic Validation Checks

#### 5.1 Zero Distance Shipment Identification
**Check Name**: Zero Distance Shipment Check
**Description**: Identifies zero-distance shipments for separate processing
**Rationale**: Business rules specify to exclude zero-distance shipments from rate calculations but count them separately
**SQL Example**:
```sql
SELECT 
  COUNT(*) as total_shipments,
  COUNT(CASE WHEN DISTANCE = 0 OR DISTANCE IS NULL THEN 1 END) as zero_distance_shipments,
  ROUND(COUNT(CASE WHEN DISTANCE = 0 OR DISTANCE IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as zero_distance_percentage
FROM silver.shipment;

-- Detail of zero distance shipments
SELECT 
  SHIPMENT_ID,
  DISTANCE,
  DIRECT_DISTANCE,
  O_FACILITY_ID,
  D_FACILITY_ID,
  SHIPMENT_STATUS
FROM silver.shipment
WHERE DISTANCE = 0 OR DISTANCE IS NULL;
```

#### 5.2 Cancelled Shipment Identification
**Check Name**: Cancelled Shipment Status Validation
**Description**: Validates cancelled shipment identification based on planning status
**Rationale**: Business rules specify cancelled shipment identification is based on specific planning status value in source system
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  SHIPMENT_STATUS,
  IS_SHIPMENT_CANCELLED,
  CASE 
    WHEN SHIPMENT_STATUS = 'CANCELLED' AND IS_SHIPMENT_CANCELLED != 'Y' THEN 'Status/Flag Mismatch'
    WHEN SHIPMENT_STATUS != 'CANCELLED' AND IS_SHIPMENT_CANCELLED = 'Y' THEN 'Flag/Status Mismatch'
    ELSE 'Consistent'
  END as cancellation_consistency
FROM silver.shipment
WHERE (SHIPMENT_STATUS = 'CANCELLED' AND IS_SHIPMENT_CANCELLED != 'Y')
   OR (SHIPMENT_STATUS != 'CANCELLED' AND IS_SHIPMENT_CANCELLED = 'Y');
```

#### 5.3 Out-of-Route Distance Validation
**Check Name**: Out-of-Route Distance Logic Check
**Description**: Validates that out-of-route distance does not exceed total route distance
**Rationale**: Business rules require validation that out-of-route distance does not exceed total route distance; flag anomalies
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  DISTANCE as total_distance,
  DIRECT_DISTANCE,
  OUT_OF_ROUTE_DISTANCE,
  CASE 
    WHEN OUT_OF_ROUTE_DISTANCE > DISTANCE THEN 'Out-of-Route Exceeds Total'
    WHEN (DIRECT_DISTANCE + OUT_OF_ROUTE_DISTANCE) > DISTANCE THEN 'Distance Components Exceed Total'
    WHEN OUT_OF_ROUTE_DISTANCE < 0 THEN 'Negative Out-of-Route Distance'
    ELSE 'Valid'
  END as route_distance_validation
FROM silver.shipment
WHERE OUT_OF_ROUTE_DISTANCE > DISTANCE 
   OR (DIRECT_DISTANCE + OUT_OF_ROUTE_DISTANCE) > DISTANCE
   OR OUT_OF_ROUTE_DISTANCE < 0;
```

### 6. Data Consistency and Cross-Field Validation Checks

#### 6.1 Facility Address Consistency
**Check Name**: Facility Address Join Validation
**Description**: Validates facility address consistency using stop sequence logic
**Rationale**: Business rules require facility address joins to use correct stop sequence logic for origin and destination
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  O_FACILITY_ID,
  O_STOP_LOCATION_NAME,
  O_ADDRESS,
  O_CITY,
  O_STATE_PROV,
  D_FACILITY_ID,
  D_STOP_LOCATION_NAME,
  D_ADDRESS,
  D_CITY,
  D_STATE_PROV,
  CASE 
    WHEN O_FACILITY_ID = D_FACILITY_ID THEN 'Same Origin and Destination'
    WHEN O_ADDRESS IS NULL AND O_FACILITY_ID IS NOT NULL THEN 'Missing Origin Address'
    WHEN D_ADDRESS IS NULL AND D_FACILITY_ID IS NOT NULL THEN 'Missing Destination Address'
    ELSE 'Valid'
  END as facility_validation_status
FROM silver.shipment
WHERE O_FACILITY_ID = D_FACILITY_ID 
   OR (O_ADDRESS IS NULL AND O_FACILITY_ID IS NOT NULL)
   OR (D_ADDRESS IS NULL AND D_FACILITY_ID IS NOT NULL);
```

#### 6.2 Billing Method Datatype Validation
**Check Name**: Billing Method Transformation Validation
**Description**: Validates billing method datatype transformation between legacy and new systems
**Rationale**: Business rules specify billing method datatype may differ between legacy and new system; transformation rule required
**SQL Example**:
```sql
SELECT 
  BILLING_METHOD,
  COUNT(*) as record_count,
  CASE 
    WHEN BILLING_METHOD REGEXP '^[0-9]+$' THEN 'Numeric (Legacy)'
    WHEN BILLING_METHOD REGEXP '^[A-Za-z]+$' THEN 'String (New System)'
    WHEN BILLING_METHOD IS NULL THEN 'Null'
    ELSE 'Mixed/Invalid Format'
  END as billing_method_type
FROM silver.shipment
WHERE BILLING_METHOD IS NOT NULL
GROUP BY BILLING_METHOD, 
  CASE 
    WHEN BILLING_METHOD REGEXP '^[0-9]+$' THEN 'Numeric (Legacy)'
    WHEN BILLING_METHOD REGEXP '^[A-Za-z]+$' THEN 'String (New System)'
    WHEN BILLING_METHOD IS NULL THEN 'Null'
    ELSE 'Mixed/Invalid Format'
  END
ORDER BY record_count DESC;
```

### 7. String Field Validation Checks

#### 7.1 String Length Validation
**Check Name**: String Field Length Check
**Description**: Validates string fields against maximum length constraints
**Rationale**: Ensures data fits within defined column constraints and prevents truncation
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  CASE 
    WHEN LENGTH(SHIPMENT_ID) > 50 THEN 'Shipment ID Too Long'
    WHEN LENGTH(O_ADDRESS) > 300 THEN 'Origin Address Too Long'
    WHEN LENGTH(D_ADDRESS) > 300 THEN 'Destination Address Too Long'
    WHEN LENGTH(BILL_TO_NAME) > 200 THEN 'Bill To Name Too Long'
    WHEN LENGTH(BILL_OF_LADING_NUMBER) > 100 THEN 'BOL Number Too Long'
    ELSE 'Valid'
  END as length_validation_status
FROM silver.shipment
WHERE LENGTH(SHIPMENT_ID) > 50 
   OR LENGTH(O_ADDRESS) > 300 
   OR LENGTH(D_ADDRESS) > 300
   OR LENGTH(BILL_TO_NAME) > 200
   OR LENGTH(BILL_OF_LADING_NUMBER) > 100;
```

#### 7.2 Character Set Validation
**Check Name**: Special Character Validation
**Description**: Validates allowed character sets in key identifier fields
**Rationale**: Ensures data quality and prevents issues with downstream systems
**SQL Example**:
```sql
SELECT 
  SHIPMENT_ID,
  TC_SHIPMENT_ID,
  BILL_OF_LADING_NUMBER,
  CASE 
    WHEN SHIPMENT_ID REGEXP '[^A-Za-z0-9_-]' THEN 'Invalid Characters in Shipment ID'
    WHEN TC_SHIPMENT_ID REGEXP '[^A-Za-z0-9_-]' THEN 'Invalid Characters in TC Shipment ID'
    WHEN BILL_OF_LADING_NUMBER REGEXP '[^A-Za-z0-9_-]' THEN 'Invalid Characters in BOL Number'
    ELSE 'Valid'
  END as character_validation_status
FROM silver.shipment
WHERE SHIPMENT_ID REGEXP '[^A-Za-z0-9_-]'
   OR TC_SHIPMENT_ID REGEXP '[^A-Za-z0-9_-]'
   OR BILL_OF_LADING_NUMBER REGEXP '[^A-Za-z0-9_-]';
```

### 8. Comprehensive Data Quality Summary Check

#### 8.1 Overall Data Quality Score
**Check Name**: Comprehensive Data Quality Assessment
**Description**: Provides overall data quality score and summary metrics
**Rationale**: Enables monitoring of overall data quality trends and identification of improvement areas
**SQL Example**:
```sql
WITH quality_metrics AS (
  SELECT 
    COUNT(*) as total_records,
    -- Completeness metrics
    COUNT(CASE WHEN SHIPMENT_ID IS NULL THEN 1 END) as missing_shipment_id,
    COUNT(CASE WHEN SHIPMENT_STATUS IS NULL THEN 1 END) as missing_status,
    COUNT(CASE WHEN CREATED_DTTM IS NULL THEN 1 END) as missing_creation_date,
    -- Validity metrics
    COUNT(CASE WHEN SHIPMENT_STATUS NOT IN ('PLANNED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED') THEN 1 END) as invalid_status,
    COUNT(CASE WHEN DISTANCE < 0 THEN 1 END) as negative_distance,
    COUNT(CASE WHEN DIRECT_DISTANCE > DISTANCE THEN 1 END) as invalid_distance_logic,
    -- Uniqueness metrics
    COUNT(*) - COUNT(DISTINCT SHIPMENT_ID) as duplicate_shipment_ids,
    -- Consistency metrics
    COUNT(CASE WHEN O_FACILITY_ID = D_FACILITY_ID THEN 1 END) as same_origin_destination
  FROM silver.shipment
)
SELECT 
  total_records,
  ROUND((total_records - missing_shipment_id - missing_status - missing_creation_date - 
         invalid_status - negative_distance - invalid_distance_logic - 
         duplicate_shipment_ids - same_origin_destination) * 100.0 / total_records, 2) as data_quality_score_percentage,
  missing_shipment_id,
  missing_status,
  missing_creation_date,
  invalid_status,
  negative_distance,
  invalid_distance_logic,
  duplicate_shipment_ids,
  same_origin_destination
FROM quality_metrics;
```

## Implementation Recommendations

### 1. Data Quality Check Execution Strategy
- **Frequency**: Execute critical checks (completeness, uniqueness) on every data load
- **Performance**: Implement checks as Delta Live Tables expectations for real-time monitoring
- **Alerting**: Set up automated alerts for data quality score drops below 95%
- **Remediation**: Implement automated data cleansing for common issues (trimming spaces, standardizing formats)

### 2. Data Quality Metrics Dashboard
- Track data quality trends over time
- Monitor data quality by source system
- Identify patterns in data quality issues
- Provide drill-down capabilities for root cause analysis

### 3. Data Lineage and Impact Analysis
- Document data quality check results in audit tables
- Track impact of data quality issues on downstream processes
- Maintain data quality SLAs and reporting

## Cost Analysis

**apiCost**: 0.000000 USD (No external API calls were made during the generation of these data quality checks)

---

*This comprehensive data quality framework ensures robust validation of TMS shipment data across all critical dimensions including completeness, accuracy, validity, uniqueness, and consistency, supporting reliable analytics and operational decision-making.*