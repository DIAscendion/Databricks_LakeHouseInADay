_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold Fact Transformation Recommender for TMS Shipment Application
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Recommender

## Overview

This document provides comprehensive transformation rules specifically for the Fact table `go_shipment_facts` in the Gold layer. The transformations ensure data quality, business alignment, and analytical readiness by addressing metric standardization, fact-dimension mapping, data aggregation, normalization, and missing data handling.

---

## 1. Transformation Rules for Fact Tables

### 1.1 Metric Standardization Rules

#### **Rule 1.1.1: Distance Metric Standardization**
- **Description**: Ensure all distance measurements are standardized to a consistent unit of measure and validate distance relationships.
- **Rationale**: Business requires consistent distance reporting across all shipments. Direct distance should not exceed total route distance, and out-of-route distance should be calculated correctly.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN DISTANCE_UOM = 'KM' THEN DISTANCE * 0.621371 
        ELSE DISTANCE 
    END AS DISTANCE_MILES,
    CASE 
        WHEN DISTANCE_UOM = 'KM' THEN DIRECT_DISTANCE * 0.621371 
        ELSE DIRECT_DISTANCE 
    END AS DIRECT_DISTANCE_MILES,
    CASE 
        WHEN DIRECT_DISTANCE > DISTANCE THEN 'INVALID_DISTANCE_RELATIONSHIP'
        WHEN OUT_OF_ROUTE_DISTANCE > DISTANCE THEN 'INVALID_OUT_OF_ROUTE'
        ELSE 'VALID'
    END AS DISTANCE_VALIDATION_FLAG,
    CASE 
        WHEN DISTANCE > 0 THEN ROUND((DIRECT_DISTANCE / DISTANCE) * 100, 2)
        ELSE NULL
    END AS ROUTE_EFFICIENCY_PERCENTAGE
FROM silver.sv_shipment
```

#### **Rule 1.1.2: Cost and Revenue Standardization**
- **Description**: Standardize all cost and revenue fields to USD currency and ensure proper decimal precision for financial calculations.
- **Rationale**: Financial KPIs require consistent currency representation and accurate calculations for margin analysis.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN CURRENCY_CODE != 'USD' THEN TOTAL_COST * exchange_rate.rate
        ELSE TOTAL_COST
    END AS TOTAL_COST_USD,
    CASE 
        WHEN TOTAL_REVENUE_CURRENCY_CODE != 'USD' THEN TOTAL_REVENUE * exchange_rate.rate
        ELSE TOTAL_REVENUE
    END AS TOTAL_REVENUE_USD,
    ROUND(COALESCE(TOTAL_REVENUE, 0) - COALESCE(TOTAL_COST, 0), 2) AS CALCULATED_MARGIN_USD,
    CASE 
        WHEN TOTAL_REVENUE > 0 THEN ROUND(((TOTAL_REVENUE - TOTAL_COST) / TOTAL_REVENUE) * 100, 2)
        ELSE NULL
    END AS MARGIN_PERCENTAGE
FROM silver.sv_shipment s
LEFT JOIN currency_exchange_rates exchange_rate 
    ON s.CURRENCY_CODE = exchange_rate.from_currency 
    AND exchange_rate.to_currency = 'USD'
    AND exchange_rate.effective_date = CURRENT_DATE()
```

#### **Rule 1.1.3: Weight and Volume Standardization**
- **Description**: Standardize weight to pounds (LB) and volume to cubic feet (CUFT) for consistent reporting.
- **Rationale**: Operational KPIs require consistent units for capacity planning and utilization calculations.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN WEIGHT_UOM_ID_BASE = 'KG' THEN PLANNED_WEIGHT * 2.20462
        WHEN WEIGHT_UOM_ID_BASE = 'TON' THEN PLANNED_WEIGHT * 2000
        ELSE PLANNED_WEIGHT
    END AS PLANNED_WEIGHT_LB,
    CASE 
        WHEN VOLUME_UOM_ID_BASE = 'CUM' THEN PLANNED_VOLUME * 35.3147
        WHEN VOLUME_UOM_ID_BASE = 'LITER' THEN PLANNED_VOLUME * 0.0353147
        ELSE PLANNED_VOLUME
    END AS PLANNED_VOLUME_CUFT,
    ROUND((PLANNED_WEIGHT / NULLIF(PLANNED_VOLUME, 0)), 2) AS DENSITY_RATIO
FROM silver.sv_shipment
```

### 1.2 Fact-Dimension Mapping Rules

#### **Rule 1.2.1: Carrier Dimension Mapping**
- **Description**: Map carrier identifiers to carrier dimension surrogate keys and handle multiple carrier assignments.
- **Rationale**: Ensures proper foreign key relationships for carrier performance analysis and supports multiple carrier scenarios (primary, secondary, broker).
- **SQL Example**:
```sql
SELECT 
    s.SHIPMENT_ID,
    COALESCE(cd_assigned.carrier_id, -1) AS assigned_carrier_key,
    COALESCE(cd_broker.carrier_id, -1) AS broker_carrier_key,
    COALESCE(cd_secondary.carrier_id, -1) AS secondary_carrier_key,
    CASE 
        WHEN s.ASSIGNED_CARRIER_ID IS NULL THEN 'UNASSIGNED'
        WHEN cd_assigned.carrier_id IS NULL THEN 'INVALID_CARRIER_REFERENCE'
        ELSE 'VALID'
    END AS carrier_mapping_status
FROM silver.sv_shipment s
LEFT JOIN gold.go_carrier_dimension cd_assigned 
    ON s.ASSIGNED_CARRIER_ID = cd_assigned.carrier_key 
    AND cd_assigned.is_current = TRUE
LEFT JOIN gold.go_carrier_dimension cd_broker 
    ON s.ASSIGNED_BROKER_CARRIER_ID = cd_broker.carrier_key 
    AND cd_broker.is_current = TRUE
LEFT JOIN gold.go_carrier_dimension cd_secondary 
    ON s.ASSIGNED_SCNDR_CARRIER_ID = cd_secondary.carrier_key 
    AND cd_secondary.is_current = TRUE
```

#### **Rule 1.2.2: Facility Dimension Mapping**
- **Description**: Map origin and destination facility identifiers to facility dimension surrogate keys using stop sequence logic.
- **Rationale**: Ensures accurate facility-based reporting and supports route analysis requirements.
- **SQL Example**:
```sql
SELECT 
    s.SHIPMENT_ID,
    COALESCE(fd_origin.facility_id, -1) AS origin_facility_key,
    COALESCE(fd_dest.facility_id, -1) AS destination_facility_key,
    CASE 
        WHEN s.O_FACILITY_ID IS NULL OR s.D_FACILITY_ID IS NULL THEN 'MISSING_FACILITY_DATA'
        WHEN fd_origin.facility_id IS NULL OR fd_dest.facility_id IS NULL THEN 'INVALID_FACILITY_REFERENCE'
        ELSE 'VALID'
    END AS facility_mapping_status
FROM silver.sv_shipment s
LEFT JOIN gold.go_facility_dimension fd_origin 
    ON s.O_FACILITY_ID = fd_origin.facility_key 
    AND fd_origin.is_current = TRUE
LEFT JOIN gold.go_facility_dimension fd_dest 
    ON s.D_FACILITY_ID = fd_dest.facility_key 
    AND fd_dest.is_current = TRUE
```

### 1.3 Data Aggregation Rules

#### **Rule 1.3.1: Daily Shipment Summary Aggregation**
- **Description**: Pre-aggregate daily shipment metrics for performance optimization and dashboard requirements.
- **Rationale**: Supports fast dashboard loading and reduces query complexity for daily operational reports.
- **SQL Example**:
```sql
INSERT INTO gold.go_shipment_daily_summary
SELECT 
    ROW_NUMBER() OVER (ORDER BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_ID, O_FACILITY_ID) AS summary_id,
    DATE(CREATED_DTTM) AS summary_date,
    COALESCE(ASSIGNED_CARRIER_ID, 'UNASSIGNED') AS carrier_key,
    COALESCE(O_FACILITY_ID, 'UNKNOWN') AS facility_key,
    COUNT(*) AS total_shipment_count,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'ACTIVE' THEN 1 END) AS active_shipment_count,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'COMPLETED' THEN 1 END) AS completed_shipment_count,
    COUNT(CASE WHEN IS_SHIPMENT_CANCELLED = 'Y' THEN 1 END) AS cancelled_shipment_count,
    COUNT(CASE WHEN IS_SHIPMENT_RECONCILED = 'Y' THEN 1 END) AS reconciled_shipment_count,
    ROUND((COUNT(CASE WHEN IS_SHIPMENT_CANCELLED = 'Y' THEN 1 END) * 100.0 / COUNT(*)), 2) AS cancelled_shipment_percentage,
    ROUND((COUNT(CASE WHEN IS_SHIPMENT_RECONCILED = 'Y' THEN 1 END) * 100.0 / COUNT(*)), 2) AS reconciled_shipment_percentage,
    SUM(COALESCE(DISTANCE, 0)) AS total_route_distance_sum,
    ROUND(AVG(COALESCE(DISTANCE, 0)), 2) AS average_route_distance,
    SUM(COALESCE(NUM_STOPS, 0)) AS total_stops_sum,
    ROUND(AVG(COALESCE(NUM_STOPS, 0)), 2) AS average_stops_per_shipment,
    SUM(COALESCE(OUT_OF_ROUTE_DISTANCE, 0)) AS out_of_route_distance_sum,
    ROUND((SUM(COALESCE(OUT_OF_ROUTE_DISTANCE, 0)) * 100.0 / NULLIF(SUM(COALESCE(DISTANCE, 0)), 0)), 2) AS out_of_route_percentage,
    ROUND(AVG(CASE WHEN DISTANCE > 0 THEN DIRECT_DISTANCE / DISTANCE ELSE NULL END), 4) AS route_efficiency_index,
    COUNT(CASE WHEN ASSIGNED_BROKER_CARRIER_ID IS NOT NULL THEN 1 END) AS broker_carrier_usage_count,
    ROUND((COUNT(CASE WHEN ASSIGNED_BROKER_CARRIER_ID IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)), 2) AS broker_carrier_usage_percentage,
    CURRENT_TIMESTAMP() AS load_date,
    CURRENT_TIMESTAMP() AS update_date,
    'TMS_SILVER' AS source_system
FROM silver.sv_shipment
WHERE DATE(CREATED_DTTM) = CURRENT_DATE() - INTERVAL 1 DAY
GROUP BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_ID, O_FACILITY_ID
```

### 1.4 Normalization and Standardization Rules

#### **Rule 1.4.1: Status Code Normalization**
- **Description**: Normalize shipment status values to standard business terminology and map cancelled shipments based on planning status.
- **Rationale**: Ensures consistent status reporting across different source systems and supports business rule for cancelled shipment identification.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN UPPER(SHIPMENT_STATUS) IN ('CANCELLED', 'CANCELED', 'CANCEL') THEN 'CANCELLED'
        WHEN UPPER(SHIPMENT_STATUS) IN ('COMPLETE', 'COMPLETED', 'DELIVERED') THEN 'COMPLETED'
        WHEN UPPER(SHIPMENT_STATUS) IN ('IN_TRANSIT', 'INTRANSIT', 'TRANSIT') THEN 'IN_TRANSIT'
        WHEN UPPER(SHIPMENT_STATUS) IN ('PLANNED', 'PLANNING', 'PLAN') THEN 'PLANNED'
        ELSE UPPER(SHIPMENT_STATUS)
    END AS normalized_shipment_status,
    CASE 
        WHEN SHIPMENT_STATUS IN ('CANCELLED', 'CANCELED') OR IS_SHIPMENT_CANCELLED = 'Y' THEN 'Y'
        ELSE 'N'
    END AS is_cancelled_flag,
    CASE 
        WHEN IS_SHIPMENT_RECONCILED = 'Y' THEN 'Y'
        WHEN SHIPMENT_STATUS = 'COMPLETED' AND SHIPMENT_RECON_DTTM IS NOT NULL THEN 'Y'
        ELSE 'N'
    END AS is_reconciled_flag
FROM silver.sv_shipment
```

#### **Rule 1.4.2: Billing Method Transformation**
- **Description**: Transform billing method from numeric (legacy) to string (new system) format and standardize values.
- **Rationale**: Addresses data type inconsistency between legacy and new systems as identified in constraints.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN BILLING_METHOD = '1' OR BILLING_METHOD = 'PREPAID' THEN 'PREPAID'
        WHEN BILLING_METHOD = '2' OR BILLING_METHOD = 'COLLECT' THEN 'COLLECT'
        WHEN BILLING_METHOD = '3' OR BILLING_METHOD = 'THIRD_PARTY' THEN 'THIRD_PARTY'
        WHEN BILLING_METHOD IS NULL THEN 'UNKNOWN'
        ELSE UPPER(BILLING_METHOD)
    END AS standardized_billing_method
FROM silver.sv_shipment
```

### 1.5 Handling Missing or Invalid Data Rules

#### **Rule 1.5.1: Mandatory Field Validation and Default Assignment**
- **Description**: Validate mandatory fields and assign appropriate default values or error flags for missing critical data.
- **Rationale**: Ensures data completeness for audit and operational reporting as required by business constraints.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    COALESCE(SHIPMENT_STATUS, 'UNKNOWN') AS shipment_status_clean,
    COALESCE(ASSIGNED_CARRIER_ID, 'UNASSIGNED') AS assigned_carrier_clean,
    COALESCE(O_FACILITY_ID, 'UNKNOWN_ORIGIN') AS origin_facility_clean,
    COALESCE(D_FACILITY_ID, 'UNKNOWN_DESTINATION') AS destination_facility_clean,
    COALESCE(CREATED_DTTM, CURRENT_TIMESTAMP()) AS created_dttm_clean,
    CASE 
        WHEN SHIPMENT_ID IS NULL THEN 'MISSING_SHIPMENT_ID'
        WHEN SHIPMENT_STATUS IS NULL THEN 'MISSING_STATUS'
        WHEN ASSIGNED_CARRIER_ID IS NULL THEN 'MISSING_CARRIER'
        WHEN O_FACILITY_ID IS NULL OR D_FACILITY_ID IS NULL THEN 'MISSING_FACILITY'
        WHEN CREATED_DTTM IS NULL THEN 'MISSING_CREATION_DATE'
        ELSE 'VALID'
    END AS data_quality_flag
FROM silver.sv_shipment
```

#### **Rule 1.5.2: Zero Distance Shipment Handling**
- **Description**: Identify and handle zero-distance shipments according to business rules for rate calculations.
- **Rationale**: Business rule specifies to exclude zero-distance shipments from rate calculations but count them separately.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    DISTANCE,
    CASE 
        WHEN COALESCE(DISTANCE, 0) = 0 THEN 'ZERO_DISTANCE'
        WHEN DISTANCE < 0 THEN 'NEGATIVE_DISTANCE'
        ELSE 'VALID_DISTANCE'
    END AS distance_category,
    CASE 
        WHEN COALESCE(DISTANCE, 0) = 0 THEN 'EXCLUDE_FROM_RATE_CALC'
        ELSE 'INCLUDE_IN_RATE_CALC'
    END AS rate_calculation_flag,
    CASE 
        WHEN COALESCE(DISTANCE, 0) = 0 AND O_FACILITY_ID = D_FACILITY_ID THEN 'SAME_FACILITY_TRANSFER'
        WHEN COALESCE(DISTANCE, 0) = 0 THEN 'ZERO_DISTANCE_ANOMALY'
        ELSE 'NORMAL_SHIPMENT'
    END AS shipment_classification
FROM silver.sv_shipment
```

#### **Rule 1.5.3: Business Partner Identifier Extraction**
- **Description**: Extract business partner identifier from extended attribute fields with proper validation.
- **Rationale**: Business partner data is sourced from extended attributes and requires extraction logic confirmation as per constraints.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN BUSINESS_PARTNER_ID IS NOT NULL AND LENGTH(TRIM(BUSINESS_PARTNER_ID)) > 0 
        THEN TRIM(BUSINESS_PARTNER_ID)
        WHEN CUSTOMER_ID IS NOT NULL AND LENGTH(TRIM(CUSTOMER_ID)) > 0 
        THEN CONCAT('CUST-', TRIM(CUSTOMER_ID))
        ELSE 'UNKNOWN_PARTNER'
    END AS extracted_business_partner_id,
    CASE 
        WHEN BUSINESS_PARTNER_ID IS NOT NULL THEN 'DIRECT_MAPPING'
        WHEN CUSTOMER_ID IS NOT NULL THEN 'DERIVED_FROM_CUSTOMER'
        ELSE 'NO_PARTNER_DATA'
    END AS partner_extraction_method
FROM silver.sv_shipment
```

### 1.6 Data Quality and Validation Rules

#### **Rule 1.6.1: Referential Integrity Validation**
- **Description**: Validate referential integrity between fact table and dimension tables, flagging orphaned records.
- **Rationale**: Ensures data consistency and identifies data quality issues for resolution.
- **SQL Example**:
```sql
SELECT 
    s.SHIPMENT_ID,
    CASE WHEN cd.carrier_id IS NULL AND s.ASSIGNED_CARRIER_ID IS NOT NULL 
         THEN 'ORPHANED_CARRIER' ELSE 'VALID_CARRIER' END AS carrier_integrity_status,
    CASE WHEN fd_o.facility_id IS NULL AND s.O_FACILITY_ID IS NOT NULL 
         THEN 'ORPHANED_ORIGIN_FACILITY' ELSE 'VALID_ORIGIN' END AS origin_integrity_status,
    CASE WHEN fd_d.facility_id IS NULL AND s.D_FACILITY_ID IS NOT NULL 
         THEN 'ORPHANED_DEST_FACILITY' ELSE 'VALID_DESTINATION' END AS dest_integrity_status
FROM silver.sv_shipment s
LEFT JOIN gold.go_carrier_dimension cd ON s.ASSIGNED_CARRIER_ID = cd.carrier_key AND cd.is_current = TRUE
LEFT JOIN gold.go_facility_dimension fd_o ON s.O_FACILITY_ID = fd_o.facility_key AND fd_o.is_current = TRUE
LEFT JOIN gold.go_facility_dimension fd_d ON s.D_FACILITY_ID = fd_d.facility_key AND fd_d.is_current = TRUE
```

#### **Rule 1.6.2: Business Logic Validation**
- **Description**: Validate business logic constraints such as pickup before delivery, valid date ranges, and logical relationships.
- **Rationale**: Ensures data meets business expectations and identifies potential data quality issues.
- **SQL Example**:
```sql
SELECT 
    SHIPMENT_ID,
    CASE 
        WHEN PICKUP_START_DATE > DELIVERY_START_DTTM THEN 'PICKUP_AFTER_DELIVERY'
        WHEN SHIPMENT_START_DTTM > SHIPMENT_END_DTTM THEN 'START_AFTER_END'
        WHEN CREATED_DTTM > CURRENT_TIMESTAMP() THEN 'FUTURE_CREATION_DATE'
        WHEN DATEDIFF(DELIVERY_START_DTTM, PICKUP_START_DATE) > 30 THEN 'EXCESSIVE_TRANSIT_TIME'
        ELSE 'VALID_DATES'
    END AS date_logic_validation,
    CASE 
        WHEN TOTAL_COST < 0 THEN 'NEGATIVE_COST'
        WHEN TOTAL_REVENUE < TOTAL_COST AND TOTAL_REVENUE > 0 THEN 'NEGATIVE_MARGIN'
        WHEN PLANNED_WEIGHT <= 0 AND SHIPMENT_TYPE != 'EMPTY' THEN 'ZERO_WEIGHT_NON_EMPTY'
        ELSE 'VALID_BUSINESS_LOGIC'
    END AS business_logic_validation
FROM silver.sv_shipment
```

---

## 2. Traceability Matrix

| **Transformation Rule** | **Source Reference** | **Business Constraint** | **Gold Layer Impact** |
|------------------------|---------------------|------------------------|----------------------|
| Distance Standardization | Model Conceptual - Route Entity | Distance unit consistency | Standardized distance metrics |
| Cost/Revenue Standardization | Model Conceptual - KPIs | Financial accuracy | Consistent currency reporting |
| Carrier Dimension Mapping | Conceptual Relationships | Carrier performance analysis | Proper FK relationships |
| Facility Dimension Mapping | Conceptual Relationships | Route and facility analysis | Accurate facility reporting |
| Status Code Normalization | Constraints - Cancelled shipment identification | Business rule compliance | Consistent status reporting |
| Billing Method Transformation | Constraints - Datatype transformation | Legacy/new system compatibility | Standardized billing data |
| Zero Distance Handling | Constraints - Rate calculation exclusion | Business logic compliance | Accurate rate calculations |
| Business Partner Extraction | Constraints - Extended attribute extraction | Partner identification | Complete partner data |
| Mandatory Field Validation | Constraints - Data completeness | Audit requirements | Data quality assurance |
| Referential Integrity | Gold Layer DDL | Data consistency | Clean dimensional relationships |

---

## 3. Implementation Recommendations

### 3.1 Execution Order
1. **Data Quality Validation** - Execute validation rules first to identify issues
2. **Metric Standardization** - Apply unit conversions and standardizations
3. **Dimension Mapping** - Map to dimension surrogate keys
4. **Business Logic Application** - Apply business rules and transformations
5. **Aggregation Creation** - Generate pre-aggregated summary tables
6. **Final Load** - Insert into Gold layer fact table

### 3.2 Error Handling Strategy
- Log all validation failures to `gold.go_data_validation_errors` table
- Use default values for non-critical missing data
- Flag records with critical data quality issues for manual review
- Maintain audit trail in `gold.go_pipeline_audit` table

### 3.3 Performance Optimization
- Partition fact table by `CREATED_DTTM` for query performance
- Create pre-aggregated summary tables for common reporting patterns
- Use Delta Lake optimization features (auto-optimize, auto-compact)
- Implement incremental loading for large datasets

---

## 4. API Cost

**apiCost**: 0.1247

---

**outputURL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Recommender

**pipelineID**: 14675