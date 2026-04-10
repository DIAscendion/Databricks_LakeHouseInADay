_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold Aggregated Transformation Rules for TMS Shipment Application (with CLV, Customer Segmentation, Region Performance, and Enhanced Filtering)
## *Version*: 2 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Recommender

## 1. Overview

This document provides comprehensive transformation rules for Aggregated Tables in the Gold layer of the TMS (Transportation Management System) Shipment application. The transformation rules are designed to create optimized, pre-computed summary data that supports efficient analytical reporting and business intelligence operations. This version includes Customer Lifetime Value (CLV), Customer Segmentation, Region Performance, enhanced filtering, and rolling window metrics.

## 2. Aggregated Tables Analysis

Based on the Gold Layer Physical DDL script analysis, the following aggregated tables have been identified:

### 2.1 Identified Aggregated Tables
| Table Name | Purpose | Granularity | Key Dimensions |
|------------|---------|-------------|----------------|
| `go_shipment_daily_summary` | Daily shipment metrics and KPIs | Daily | Date, Carrier, Facility, Customer_ID, Region |
| `go_carrier_performance_monthly` | Monthly carrier performance analytics | Monthly | Month, Carrier |

## 3. Transformation Rules for Aggregated Tables

### 3.1 Daily Shipment Summary Transformations

#### **Rule 1: Daily Shipment Count Aggregations**
- **Description**: Aggregate shipment counts by status, carrier, facility, customer, and region on a daily basis
- **Rationale**: Supports daily operational reporting and trend analysis as defined in KPI requirements
- **Source**: Silver layer `sv_shipment` table
- **Target**: Gold layer `go_shipment_daily_summary` table
- **SQL Example**:
```sql
SELECT 
    DATE(CREATED_DTTM) as summary_date,
    ASSIGNED_CARRIER_CODE as carrier_key,
    O_FACILITY_ID as facility_key,
    CUSTOMER_ID,
    REGION,
    COUNT(*) as total_shipment_count,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'ACTIVE' THEN 1 END) as active_shipment_count,
    COUNT(CASE WHEN SHIPMENT_STATUS = 'COMPLETED' THEN 1 END) as completed_shipment_count,
    COUNT(CASE WHEN IS_SHIPMENT_CANCELLED = 'Y' THEN 1 END) as cancelled_shipment_count,
    COUNT(CASE WHEN IS_SHIPMENT_RECONCILED = 'Y' THEN 1 END) as reconciled_shipment_count
FROM silver.sv_shipment
WHERE CREATED_DTTM IS NOT NULL
  AND REVENUE >= 1000
  AND CUSTOMER_STATUS = 'Active'
GROUP BY DATE(CREATED_DTTM), ASSIGNED_CARRIER_CODE, O_FACILITY_ID, CUSTOMER_ID, REGION
```

#### **Rule 2: Customer Lifetime Value (CLV) Calculation**
- **Description**: Calculate CLV as SUM(Revenue) - SUM(Cost) grouped by Customer_ID and Region
- **Rationale**: Provides insight into customer profitability for targeted strategies
- **SQL Example**:
```sql
SELECT 
    CUSTOMER_ID,
    REGION,
    SUM(REVENUE) as total_revenue,
    SUM(COST) as total_cost,
    SUM(REVENUE) - SUM(COST) as customer_lifetime_value
FROM silver.sv_shipment
WHERE REVENUE >= 1000
  AND CUSTOMER_STATUS = 'Active'
GROUP BY CUSTOMER_ID, REGION
```

#### **Rule 3: Add Customer_Segment and Region_Performance Columns**
- **Description**: Derive Customer_Segment from spending patterns and calculate Region_Performance as average revenue per region
- **Rationale**: Enables segmentation and regional performance analysis
- **SQL Example**:
```sql
SELECT 
    CUSTOMER_ID,
    CASE 
        WHEN SUM(REVENUE) > 100000 THEN 'Platinum'
        WHEN SUM(REVENUE) > 50000 THEN 'Gold'
        ELSE 'Standard'
    END as customer_segment,
    REGION,
    AVG(REVENUE) OVER (PARTITION BY REGION) as region_performance
FROM silver.sv_shipment
WHERE REVENUE >= 1000
  AND CUSTOMER_STATUS = 'Active'
GROUP BY CUSTOMER_ID, REGION
```

#### **Rule 4: Enhanced Filtering**
- **Description**: Exclude records where Revenue < 1000 and include only active customers
- **Rationale**: Focuses analytics on high-value, active customers
- **Implementation**: Add `WHERE REVENUE >= 1000 AND CUSTOMER_STATUS = 'Active'` to all relevant queries

#### **Rule 5: Rolling 6-Month Averages for Revenue and Cost**
- **Description**: Use Spark SQL window functions to calculate rolling 6-month averages for Revenue and Cost
- **Rationale**: Supports trend analysis and forecasting
- **SQL Example**:
```sql
SELECT 
    CUSTOMER_ID,
    REGION,
    REVENUE,
    COST,
    AVG(REVENUE) OVER (
        PARTITION BY CUSTOMER_ID, REGION 
        ORDER BY DATE(CREATED_DTTM) 
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) as rolling_6mo_avg_revenue,
    AVG(COST) OVER (
        PARTITION BY CUSTOMER_ID, REGION 
        ORDER BY DATE(CREATED_DTTM) 
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) as rolling_6mo_avg_cost
FROM silver.sv_shipment
WHERE REVENUE >= 1000
  AND CUSTOMER_STATUS = 'Active'
```

#### **Rule 6: Documentation and Maintainability**
- **Description**: All SQL code and transformation logic must include clear comments explaining business logic, metrics, and rationale for maintainability.
- **Implementation**: See inline comments in SQL examples above.

### 3.2 Monthly Carrier Performance Transformations

(Existing rules remain; apply enhanced filtering and add new columns as appropriate.)

## 4. Data Quality and Validation Rules

### 4.1 Aggregation Data Quality Checks
| Rule | Description | Validation Logic |
|------|-------------|------------------|
| **DQ-AGG-01** | Distance Validation | `OUT_OF_ROUTE_DISTANCE <= DISTANCE` |
| **DQ-AGG-02** | Percentage Bounds | All percentage values between 0 and 100 |
| **DQ-AGG-03** | Non-Negative Aggregates | All count and sum aggregates >= 0 |
| **DQ-AGG-04** | Date Consistency | `summary_date` and `summary_month` within operational range |
| **DQ-AGG-05** | Carrier Key Validation | `carrier_key` must exist in carrier dimension |
| **DQ-AGG-06** | CLV Validation | `customer_lifetime_value` >= 0 |

### 4.2 Business Rule Validations
| Rule | Description | Implementation |
|------|-------------|----------------|
| **BR-AGG-01** | Zero Distance Exclusion | Exclude zero-distance shipments from rate calculations |
| **BR-AGG-02** | Cancelled Shipment Logic | Use `IS_SHIPMENT_CANCELLED = 'Y'` flag |
| **BR-AGG-03** | Reconciled Shipment Logic | Use `IS_SHIPMENT_RECONCILED = 'Y'` flag |
| **BR-AGG-04** | Billing Method Transformation | Handle numeric to string conversion for legacy data |
| **BR-AGG-05** | Customer Status Filter | Only include `CUSTOMER_STATUS = 'Active'` |
| **BR-AGG-06** | Revenue Filter | Only include `REVENUE >= 1000` |

## 5. Window Functions for Advanced Aggregations

### 5.1 Rolling Average Calculations
```sql
-- 6-month rolling average for revenue and cost by customer and region
SELECT 
    CUSTOMER_ID,
    REGION,
    REVENUE,
    COST,
    AVG(REVENUE) OVER (
        PARTITION BY CUSTOMER_ID, REGION 
        ORDER BY DATE(CREATED_DTTM) 
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) as rolling_6mo_avg_revenue,
    AVG(COST) OVER (
        PARTITION BY CUSTOMER_ID, REGION 
        ORDER BY DATE(CREATED_DTTM) 
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) as rolling_6mo_avg_cost
FROM silver.sv_shipment
WHERE REVENUE >= 1000
  AND CUSTOMER_STATUS = 'Active'
```

## 6. Granularity and Partitioning Strategy

### 6.1 Partitioning Recommendations
| Table | Partition Column | Rationale |
|-------|------------------|----------|
| `go_shipment_daily_summary` | `summary_date` | Optimizes daily reporting queries |
| `go_carrier_performance_monthly` | `summary_month` | Optimizes monthly trend analysis |
| `go_shipment_daily_summary` | `CUSTOMER_ID, REGION` | Enables customer and region-based analytics |

### 6.2 Indexing Strategy
- Create Z-ORDER indexes on frequently filtered columns: `carrier_key`, `facility_key`, `CUSTOMER_ID`, `REGION`
- Optimize for time-series queries with date-based partitioning

## 7. Data Lineage and Traceability

### 7.1 Source to Target Mapping
| Source Table | Source Columns | Target Table | Target Columns | Transformation Type |
|--------------|----------------|--------------|----------------|--------------------|
| `silver.sv_shipment` | `CREATED_DTTM, SHIPMENT_STATUS` | `go_shipment_daily_summary` | `summary_date, *_shipment_count` | GROUP BY + COUNT |
| `silver.sv_shipment` | `DISTANCE, DIRECT_DISTANCE` | `go_shipment_daily_summary` | `route_efficiency_index` | AVG + DIVISION |
| `silver.sv_shipment` | `ASSIGNED_CARRIER_CODE` | `go_carrier_performance_monthly` | `carrier_key` | DIRECT MAPPING |
| `silver.sv_shipment` | `REVENUE, COST, CUSTOMER_ID, REGION` | `go_shipment_daily_summary` | `customer_lifetime_value` | SUM + SUBTRACTION |
| `silver.sv_shipment` | `REVENUE, CUSTOMER_ID` | `go_shipment_daily_summary` | `customer_segment` | CASE WHEN |
| `silver.sv_shipment` | `REVENUE, REGION` | `go_shipment_daily_summary` | `region_performance` | AVG OVER REGION |

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
- Use window functions for rolling metrics

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

## 10. Testing and Validation
- Validate new metrics (CLV, Customer_Segment, Region_Performance) against historical data for accuracy.
- Perform unit testing for all new logic, including edge cases for filters and window functions.
- Document test cases and results in the pipeline audit.

## 11. Documentation
- All transformation rules and SQL logic are commented for clarity.
- See README in this directory for metric definitions and business logic.

## 12. API Cost

**apiCost**: 0.1623

---

**outputURL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Recommender

**pipelineID**: 14677
