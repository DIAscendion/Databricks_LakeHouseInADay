_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold Aggregated Transformation Rules for TMS Shipment Application
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Recommender

## 1. Overview

This document provides comprehensive transformation rules for Aggregated Tables in the Gold layer of the TMS (Transportation Management System) Shipment application. The transformation rules are designed to create optimized, pre-computed summary data that supports efficient analytical reporting and business intelligence operations.

## 2. Aggregated Tables Analysis

Based on the Gold Layer Physical DDL script analysis, the following aggregated tables have been identified:

### 2.1 Identified Aggregated Tables
| Table Name | Purpose | Granularity | Key Dimensions |
|------------|---------|-------------|----------------|
| `go_shipment_daily_summary` | Daily shipment metrics and KPIs | Daily | Date, Carrier, Facility |
| `go_carrier_performance_monthly` | Monthly carrier performance analytics | Monthly | Month, Carrier |

## 3. Transformation Rules for Aggregated Tables

### 3.1 Daily Shipment Summary Transformations

#### **Rule 1: Daily Shipment Count Aggregations**
- **Description**: Aggregate shipment counts by status, carrier, and facility on a daily basis
- **Rationale**: Supports daily operational reporting and trend analysis as defined in KPI requirements
- **Source**: Silver layer `sv_shipment` table
- **Target**: Gold layer `go_shipment_daily_summary` table
- **SQL Example**:
```sql
SELECT 
    DATE(CREATED_DTTM) as summary_date,
    ASSIGNED_CARRIER_CODE as carrier_key,
    O_FACILITY_ID as facility_key,
    COUNT(*) as total_shipment_count,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'ACTIVE' THEN 1 END) as active_shipment_count,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'COMPLETED' THEN 1 END) as completed_shipment_count,
    COUNT(CASE WHEN IS_SHIPMENT_CANCELLED = 'Y' THEN 1 END) as cancelled_shipment_count,
    COUNT(CASE WHEN IS_SHIPMENT_RECONCILED = 'Y' THEN 1 END) as reconciled_shipment_count
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL
GROUP BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_CODE, O_FACILITY_ID
```

#### **Rule 2: Daily Percentage Calculations**
- **Description**: Calculate cancelled and reconciled shipment percentages
- **Rationale**: Aligns with KPI requirements for "Cancelled Shipment %" and "Reconciled Shipment %"
- **Source**: Derived from Rule 1 aggregations
- **SQL Example**:
```sql
SELECT 
    *,
    ROUND((cancelled_shipment_count * 100.0 / NULLIF(total_shipment_count, 0)), 2) as cancelled_shipment_percentage,
    ROUND((reconciled_shipment_count * 100.0 / NULLIF(total_shipment_count, 0)), 2) as reconciled_shipment_percentage
FROM (
    -- Rule 1 query here
)
```

#### **Rule 3: Daily Distance Aggregations**
- **Description**: Aggregate route distance metrics including total, average, and out-of-route calculations
- **Rationale**: Supports route efficiency analysis and out-of-route distance KPIs
- **Data Constraints**: Exclude zero-distance shipments from rate calculations but count separately
- **SQL Example**:
```sql
SELECT 
    DATE(CREATED_DTTM) as summary_date,
    ASSIGNED_CARRIER_CODE as carrier_key,
    O_FACILITY_ID as facility_key,
    SUM(COALESCE(DISTANCE, 0)) as total_route_distance_sum,
    AVG(CASE WHEN DISTANCE > 0 THEN DISTANCE END) as average_route_distance,
    SUM(COALESCE(OUT_OF_ROUTE_DISTANCE, 0)) as out_of_route_distance_sum,
    ROUND((SUM(COALESCE(OUT_OF_ROUTE_DISTANCE, 0)) * 100.0 / NULLIF(SUM(COALESCE(DISTANCE, 0)), 0)), 2) as out_of_route_percentage,
    ROUND((AVG(CASE WHEN DISTANCE > 0 THEN DIRECT_DISTANCE/DISTANCE END)), 4) as route_efficiency_index
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL
GROUP BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_CODE, O_FACILITY_ID
```

#### **Rule 4: Daily Stops Aggregation**
- **Description**: Calculate total stops and average stops per shipment
- **Rationale**: Supports "Average Stops per Shipment" KPI requirement
- **SQL Example**:
```sql
SELECT 
    DATE(CREATED_DTTM) as summary_date,
    ASSIGNED_CARRIER_CODE as carrier_key,
    O_FACILITY_ID as facility_key,
    SUM(COALESCE(NUM_STOPS, 0)) as total_stops_sum,
    ROUND(AVG(COALESCE(NUM_STOPS, 0)), 2) as average_stops_per_shipment
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL
GROUP BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_CODE, O_FACILITY_ID
```

#### **Rule 5: Daily Broker Carrier Usage**
- **Description**: Calculate broker carrier usage count and percentage
- **Rationale**: Supports "Broker Carrier Usage %" KPI requirement
- **SQL Example**:
```sql
SELECT 
    DATE(CREATED_DTTM) as summary_date,
    ASSIGNED_CARRIER_CODE as carrier_key,
    O_FACILITY_ID as facility_key,
    COUNT(CASE WHEN ASSIGNED_BROKER_CARRIER_ID IS NOT NULL THEN 1 END) as broker_carrier_usage_count,
    ROUND((COUNT(CASE WHEN ASSIGNED_BROKER_CARRIER_ID IS NOT NULL THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) as broker_carrier_usage_percentage
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL
GROUP BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_CODE, O_FACILITY_ID
```

### 3.2 Monthly Carrier Performance Transformations

#### **Rule 6: Monthly Carrier Assignment Metrics**
- **Description**: Aggregate monthly carrier assignment and completion metrics
- **Rationale**: Supports carrier performance analysis and "Carrier Assignment Rate %" KPI
- **Source**: Silver layer `sv_shipment` table
- **Target**: Gold layer `go_carrier_performance_monthly` table
- **SQL Example**:
```sql
SELECT 
    DATE_TRUNC('MONTH', CREATED_DTTM) as summary_month,
    ASSIGNED_CARRIER_CODE as carrier_key,
    COUNT(*) as total_shipments_assigned,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'COMPLETED' OR SHIPMENT_STATUS = 'DELIVERED' THEN 1 END) as completed_shipments,
    COUNT(CASE WHEN IS_SHIPMENT_CANCELLED = 'Y' THEN 1 END) as cancelled_shipments
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL 
  AND ASSIGNED_CARRIER_CODE IS NOT NULL
GROUP BY DATE_TRUNC('MONTH', CREATED_DTTM), ASSIGNED_CARRIER_CODE
```

#### **Rule 7: Monthly Carrier Performance Percentages**
- **Description**: Calculate completion and cancellation rates for carriers
- **Rationale**: Enables carrier performance benchmarking and evaluation
- **SQL Example**:
```sql
SELECT 
    *,
    ROUND((completed_shipments * 100.0 / NULLIF(total_shipments_assigned, 0)), 2) as completion_rate_percentage,
    ROUND((cancelled_shipments * 100.0 / NULLIF(total_shipments_assigned, 0)), 2) as cancellation_rate_percentage
FROM (
    -- Rule 6 query here
)
```

#### **Rule 8: Monthly Carrier Distance Performance**
- **Description**: Aggregate monthly distance metrics per carrier
- **Rationale**: Supports carrier efficiency analysis and route optimization
- **Data Constraints**: Validate that out-of-route distance does not exceed total route distance
- **SQL Example**:
```sql
SELECT 
    DATE_TRUNC('MONTH', CREATED_DTTM) as summary_month,
    ASSIGNED_CARRIER_CODE as carrier_key,
    SUM(COALESCE(DISTANCE, 0)) as total_distance_covered,
    AVG(CASE WHEN DISTANCE > 0 THEN DISTANCE END) as average_distance_per_shipment,
    SUM(COALESCE(NUM_STOPS, 0)) as total_stops_serviced,
    ROUND(AVG(COALESCE(NUM_STOPS, 0)), 2) as average_stops_per_shipment,
    ROUND(AVG(CASE WHEN DISTANCE > 0 AND OUT_OF_ROUTE_DISTANCE <= DISTANCE 
                   THEN DIRECT_DISTANCE/DISTANCE END), 4) as route_efficiency_score
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL 
  AND ASSIGNED_CARRIER_CODE IS NOT NULL
GROUP BY DATE_TRUNC('MONTH', CREATED_DTTM), ASSIGNED_CARRIER_CODE
```

#### **Rule 9: Monthly On-Time Performance Calculation**
- **Description**: Calculate on-time performance percentage using window functions
- **Rationale**: Critical KPI for carrier evaluation and service level monitoring
- **SQL Example**:
```sql
SELECT 
    DATE_TRUNC('MONTH', CREATED_DTTM) as summary_month,
    ASSIGNED_CARRIER_CODE as carrier_key,
    ROUND((
        COUNT(CASE WHEN DELIVERY_END_DTTM <= SCHEDULED_PICKUP_DTTM + INTERVAL DAYS_TO_DELIVER DAY 
                   THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN DELIVERY_END_DTTM IS NOT NULL THEN 1 END), 0)
    ), 2) as on_time_performance_percentage
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL 
  AND ASSIGNED_CARRIER_CODE IS NOT NULL
  AND SCHEDULED_PICKUP_DTTM IS NOT NULL
GROUP BY DATE_TRUNC('MONTH', CREATED_DTTM), ASSIGNED_CARRIER_CODE
```

#### **Rule 10: Monthly Carrier Utilization**
- **Description**: Calculate carrier utilization percentage using equipment and capacity metrics
- **Rationale**: Supports carrier capacity planning and utilization optimization
- **SQL Example**:
```sql
SELECT 
    DATE_TRUNC('MONTH', CREATED_DTTM) as summary_month,
    ASSIGNED_CARRIER_CODE as carrier_key,
    ROUND(AVG(COALESCE(EQUIP_UTIL_PER, 0)), 2) as carrier_utilization_percentage
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL 
  AND ASSIGNED_CARRIER_CODE IS NOT NULL
  AND EQUIP_UTIL_PER IS NOT NULL
GROUP BY DATE_TRUNC('MONTH', CREATED_DTTM), ASSIGNED_CARRIER_CODE
```

## 4. Data Quality and Validation Rules

### 4.1 Aggregation Data Quality Checks
| Rule | Description | Validation Logic |
|------|-------------|------------------|
| **DQ-AGG-01** | Distance Validation | `OUT_OF_ROUTE_DISTANCE <= DISTANCE` |
| **DQ-AGG-02** | Percentage Bounds | All percentage values between 0 and 100 |
| **DQ-AGG-03** | Non-Negative Aggregates | All count and sum aggregates >= 0 |
| **DQ-AGG-04** | Date Consistency | `summary_date` and `summary_month` within operational range |
| **DQ-AGG-05** | Carrier Key Validation | `carrier_key` must exist in carrier dimension |

### 4.2 Business Rule Validations
| Rule | Description | Implementation |
|------|-------------|----------------|
| **BR-AGG-01** | Zero Distance Exclusion | Exclude zero-distance shipments from rate calculations |
| **BR-AGG-02** | Cancelled Shipment Logic | Use `IS_SHIPMENT_CANCELLED = 'Y'` flag |
| **BR-AGG-03** | Reconciled Shipment Logic | Use `IS_SHIPMENT_RECONCILED = 'Y'` flag |
| **BR-AGG-04** | Billing Method Transformation | Handle numeric to string conversion for legacy data |

## 5. Window Functions for Advanced Aggregations

### 5.1 Rolling Average Calculations
```sql
-- 7-day rolling average for daily shipment counts
SELECT 
    summary_date,
    carrier_key,
    total_shipment_count,
    AVG(total_shipment_count) OVER (
        PARTITION BY carrier_key 
        ORDER BY summary_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7day_avg_shipments
FROM gold.go_shipment_daily_summary
```

### 5.2 Cumulative Sum Calculations
```sql
-- Cumulative shipment count by carrier
SELECT 
    summary_month,
    carrier_key,
    total_shipments_assigned,
    SUM(total_shipments_assigned) OVER (
        PARTITION BY carrier_key 
        ORDER BY summary_month 
        ROWS UNBOUNDED PRECEDING
    ) as cumulative_shipments_ytd
FROM gold.go_carrier_performance_monthly
```

## 6. Granularity and Partitioning Strategy

### 6.1 Partitioning Recommendations
| Table | Partition Column | Rationale |
|-------|------------------|----------|
| `go_shipment_daily_summary` | `summary_date` | Optimizes daily reporting queries |
| `go_carrier_performance_monthly` | `summary_month` | Optimizes monthly trend analysis |

### 6.2 Indexing Strategy
- Create Z-ORDER indexes on frequently filtered columns: `carrier_key`, `facility_key`
- Optimize for time-series queries with date-based partitioning

## 7. Data Lineage and Traceability

### 7.1 Source to Target Mapping
| Source Table | Source Columns | Target Table | Target Columns | Transformation Type |
|--------------|----------------|--------------|----------------|--------------------|
| `silver.sv_shipment` | `CREATED_DTTM, SHIPMENT_STATUS` | `go_shipment_daily_summary` | `summary_date, *_shipment_count` | GROUP BY + COUNT |
| `silver.sv_shipment` | `DISTANCE, DIRECT_DISTANCE` | `go_shipment_daily_summary` | `route_efficiency_index` | AVG + DIVISION |
| `silver.sv_shipment` | `ASSIGNED_CARRIER_CODE` | `go_carrier_performance_monthly` | `carrier_key` | DIRECT MAPPING |

### 7.2 Audit Trail Requirements
- Include `load_date`, `update_date`, and `source_system` in all aggregated tables
- Maintain pipeline execution metadata in `go_pipeline_audit` table
- Log data quality violations in `go_data_validation_errors` table

## 8. Performance Optimization

### 8.1 Query Optimization Techniques
- Use `COALESCE` for null handling in aggregations
- Apply `NULLIF` to prevent division by zero errors
- Implement incremental processing for large datasets
- Use broadcast joins for dimension lookups

### 8.2 Incremental Processing Strategy
```sql
-- Incremental daily summary processing
INSERT INTO gold.go_shipment_daily_summary
SELECT 
    -- aggregation logic here
FROM silver.sv_shipment
WHERE DATE(CREATED_DTTM) = CURRENT_DATE - 1
  AND load_date >= (SELECT MAX(load_date) FROM gold.go_shipment_daily_summary)
```

## 9. Error Handling and Data Validation

### 9.1 Exception Handling
- Implement try-catch blocks for data type conversions
- Log transformation errors to audit tables
- Provide fallback values for missing or invalid data

### 9.2 Data Validation Checks
```sql
-- Validation query example
SELECT 
    'Distance Validation' as validation_rule,
    COUNT(*) as violation_count
FROM silver.sv_shipment
WHERE OUT_OF_ROUTE_DISTANCE > DISTANCE
  AND OUT_OF_ROUTE_DISTANCE IS NOT NULL
  AND DISTANCE IS NOT NULL
```

## 10. API Cost

**apiCost**: 0.1247

---

**outputURL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Recommender

**pipelineID**: 14677