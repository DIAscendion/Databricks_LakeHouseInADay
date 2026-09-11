_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Transformation rules and recommendations for Fact tables from Silver to Gold Layer in the Shipment domain.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Recommender

This document provides comprehensive transformation rules for Fact tables in the Gold Layer, focusing on the SI_SHIPMENT_PROCESS table from the Silver Layer. The rules ensure metric standardization, fact-dimension mapping, aggregation, normalization, and robust handling of missing or invalid data, supporting accurate and performant analytical reporting.

---

## Fact Table(s) Identified

| Silver Table              | Description                                 |
|--------------------------|---------------------------------------------|
| si_shipment_process      | Shipment process fact table (core metrics)   |

---

## Transformation Rules for Fact Tables

### 1. Metric Standardization

- **Rule Name:** Standardize Key Metrics (Cost, Revenue, Margin, Weight, Distance)
    - **Description:** Ensure all monetary and quantitative metrics (e.g., TOTAL_COST, TOTAL_REVENUE, PROFIT_MARGIN, SHIPMENT_WEIGHT, DISTANCE) are cast to their correct data types, rounded to business-specified precision, and aligned with business KPIs.
    - **Rationale:** Consistent metric formatting is critical for accurate reporting and aggregation. Ensures all downstream analytics use standardized values.
    - **SQL Example:**
      ```sql
      SELECT
        CAST(TOTAL_COST AS DECIMAL(10,2)) AS TOTAL_COST,
        ROUND(CAST(TOTAL_REVENUE AS DECIMAL(10,2)), 2) AS TOTAL_REVENUE,
        ROUND(CAST(PROFIT_MARGIN AS DECIMAL(5,4)), 4) AS PROFIT_MARGIN,
        ROUND(CAST(SHIPMENT_WEIGHT AS DECIMAL(10,2)), 2) AS SHIPMENT_WEIGHT,
        ROUND(CAST(DISTANCE AS DECIMAL(10,2)), 2) AS DISTANCE,
        ...
      FROM silver.si_shipment_process
      ```

### 2. Fact-Dimension Mapping

- **Rule Name:** Map Foreign Keys to Dimension Surrogate Keys
    - **Description:** Replace natural keys (e.g., ASSIGNED_CARRIER_ID, O_FACILITY_ID) with surrogate keys from Gold Dimension tables (e.g., go_carrier_dim.carrier_dim_id) using hash-based or direct mapping.
    - **Rationale:** Surrogate keys ensure referential integrity and efficient joins in the Gold Layer.
    - **SQL Example:**
      ```sql
      SELECT
        f.*, 
        d.carrier_dim_id,
        d.facility_dim_id
      FROM silver.si_shipment_process f
      LEFT JOIN gold.go_carrier_dim d
        ON f.ASSIGNED_CARRIER_ID = d.primary_carrier_name
      LEFT JOIN gold.go_facility_dim fd
        ON f.O_FACILITY_ID = fd.facility_name
      ```

### 3. Data Aggregation Rules

- **Rule Name:** Pre-Aggregate Shipment Metrics
    - **Description:** Create summary tables for key metrics (e.g., total cost, revenue, shipment count) at monthly/quarterly granularity for performance optimization.
    - **Rationale:** Pre-aggregated data supports faster dashboarding and trend analysis.
    - **SQL Example:**
      ```sql
      SELECT
        DATE_TRUNC('month', shipment_date) AS shipment_month,
        COUNT(*) AS shipment_count,
        SUM(TOTAL_COST) AS total_cost,
        SUM(TOTAL_REVENUE) AS total_revenue
      FROM gold.go_shipment_fact
      GROUP BY shipment_month
      ```

### 4. Normalization and Standardization

- **Rule Name:** Normalize Currency and Units
    - **Description:** Convert all monetary values to a standard currency (e.g., USD) and all weights/distances to standard units (e.g., KG, KM) using conversion tables or rates.
    - **Rationale:** Ensures comparability across shipments from different regions/currencies.
    - **SQL Example:**
      ```sql
      SELECT
        CASE WHEN TOTAL_COST_CURRENCY_CODE != 'USD'
             THEN TOTAL_COST * cr.conversion_rate
             ELSE TOTAL_COST END AS TOTAL_COST_USD,
        CASE WHEN WEIGHT_UOM_ID_BASE != 'KG'
             THEN SHIPMENT_WEIGHT * wu.conversion_factor
             ELSE SHIPMENT_WEIGHT END AS SHIPMENT_WEIGHT_KG
      FROM silver.si_shipment_process f
      LEFT JOIN gold.currency_rates cr ON f.TOTAL_COST_CURRENCY_CODE = cr.currency_code
      LEFT JOIN gold.weight_units wu ON f.WEIGHT_UOM_ID_BASE = wu.unit_code
      ```

### 5. Handling Missing or Invalid Data

- **Rule Name:** Impute or Flag Nulls and Outliers
    - **Description:** Replace NULLs with business defaults (e.g., 0 for numerics, 'UNKNOWN' for strings), and flag or filter outliers based on business thresholds (e.g., negative costs, excessive weights).
    - **Rationale:** Prevents data quality issues and ensures robust analytics.
    - **SQL Example:**
      ```sql
      SELECT
        COALESCE(TOTAL_COST, 0) AS TOTAL_COST,
        COALESCE(SHIPMENT_WEIGHT, 0) AS SHIPMENT_WEIGHT,
        CASE WHEN TOTAL_COST < 0 THEN 'Y' ELSE 'N' END AS is_cost_outlier,
        CASE WHEN SHIPMENT_WEIGHT > 100000 THEN 'Y' ELSE 'N' END AS is_weight_outlier,
        ...
      FROM silver.si_shipment_process
      ```

### 6. Traceability and Audit Columns

- **Rule Name:** Preserve Audit Columns
    - **Description:** Ensure all audit and lineage columns (load_date, update_date, source_system) are mapped directly from Silver to Gold.
    - **Rationale:** Supports data lineage, compliance, and troubleshooting.
    - **SQL Example:**
      ```sql
      SELECT
        load_date,
        update_date,
        source_system,
        ...
      FROM silver.si_shipment_process
      ```

---

## Traceability Matrix

| Rule Name                      | Source (Model/Constraint/DDL)         | Target (Gold Layer)           |
|--------------------------------|----------------------------------------|-------------------------------|
| Standardize Key Metrics        | Silver DDL, Business Constraints       | Gold Fact Table Metrics       |
| Map Foreign Keys to Dimensions | Silver DDL, Gold Dim Mapping           | Gold Fact Table FK Columns    |
| Pre-Aggregate Shipment Metrics | Business KPI, Silver DDL               | Gold Aggregated Fact Tables   |
| Normalize Currency/Units       | Silver DDL, Business Constraints       | Gold Fact Table Metrics       |
| Impute/Flag Nulls/Outliers     | Data Constraints, Silver DDL           | Gold Fact Table Metrics       |
| Preserve Audit Columns         | Silver DDL, Data Governance            | Gold Fact Table Audit Columns |

---

## API Cost

apiCost: 0.001600

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Recommender
**pipelineID:** 14675
