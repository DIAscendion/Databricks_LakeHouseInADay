_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Transformation rules and recommendations for Gold Layer Aggregated tables based on Store360 Inventory Report conceptual model, constraints, and Silver Layer DDL.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Recommender

This document provides comprehensive transformation rules for Aggregated tables in the Gold layer, derived from the Store360 Inventory Report conceptual model, business constraints, and Silver Layer DDL. It ensures aggregation logic, data accuracy, and alignment with reporting requirements for analytics and BI.

---

## 1. Aggregated Table Identification

| Gold Table Name                | Source Silver Table(s)      | Aggregation Level | Key Columns                |
|-------------------------------|-----------------------------|-------------------|----------------------------|
| gold.gd_shipment_cost_summary  | silver.sv_shipment          | Shipment          | SHIPMENT_ID                |

---

## 2. Transformation Rules for Aggregated Tables

### 2.1 Shipment Cost Summary Aggregation

- **Rule Name**: Shipment Cost Aggregation
    - **Description**: Aggregate cost-related fields (TOTAL_COST, ACTUAL_COST, ESTIMATED_COST, BASELINE_COST, LINEHAUL_COST, ACCESSORIAL_COST) at the SHIPMENT_ID level.
    - **Rationale**: Provides a summary of shipment costs for each shipment, supporting financial and operational reporting.
    - **SQL Example**:
      ```sql
      SELECT
        MAX(id) AS id,
        SHIPMENT_ID,
        SUM(TOTAL_COST) AS TOTAL_COST,
        SUM(ACTUAL_COST) AS ACTUAL_COST,
        SUM(ESTIMATED_COST) AS ESTIMATED_COST,
        SUM(BASELINE_COST) AS BASELINE_COST,
        SUM(LINEHAUL_COST) AS LINEHAUL_COST,
        SUM(ACCESSORIAL_COST) AS ACCESSORIAL_COST,
        MAX(load_date) AS load_date,
        MAX(update_date) AS update_date,
        MAX(source_system) AS source_system
      FROM silver.sv_shipment
      GROUP BY SHIPMENT_ID
      ```

- **Rule Name**: Data Type and Format Standardization
    - **Description**: Ensure all cost fields are DECIMAL(10,2) and dates are TIMESTAMP. Nulls are replaced with 0 for cost fields.
    - **Rationale**: Ensures consistency and prevents errors in reporting and analytics.
    - **SQL Example**:
      ```sql
      SELECT
        SHIPMENT_ID,
        COALESCE(TOTAL_COST, 0.00) AS TOTAL_COST,
        COALESCE(ACTUAL_COST, 0.00) AS ACTUAL_COST,
        COALESCE(ESTIMATED_COST, 0.00) AS ESTIMATED_COST,
        COALESCE(BASELINE_COST, 0.00) AS BASELINE_COST,
        COALESCE(LINEHAUL_COST, 0.00) AS LINEHAUL_COST,
        COALESCE(ACCESSORIAL_COST, 0.00) AS ACCESSORIAL_COST,
        load_date,
        update_date,
        source_system
      FROM gold.gd_shipment_cost_summary
      ```

- **Rule Name**: Granularity Check
    - **Description**: Ensure one record per SHIPMENT_ID in the aggregated table.
    - **Rationale**: Prevents duplicate shipment summaries and maintains data integrity.
    - **SQL Example**:
      ```sql
      SELECT SHIPMENT_ID, COUNT(*)
      FROM gold.gd_shipment_cost_summary
      GROUP BY SHIPMENT_ID
      HAVING COUNT(*) > 1
      ```

- **Rule Name**: Traceability and Lineage
    - **Description**: Maintain SHIPMENT_ID and source_system fields to enable traceability from Gold to Silver layer.
    - **Rationale**: Supports auditability and data lineage requirements.
    - **SQL Example**:
      ```sql
      SELECT SHIPMENT_ID, source_system FROM gold.gd_shipment_cost_summary
      ```

- **Rule Name**: Partitioning and Performance Optimization
    - **Description**: Partition the aggregated table by load_date for efficient querying and data management.
    - **Rationale**: Improves query performance and supports data retention policies.
    - **SQL Example**:
      ```sql
      CREATE TABLE IF NOT EXISTS gold.gd_shipment_cost_summary (
        ...
      )
      USING DELTA
      PARTITIONED BY (load_date)
      LOCATION '/mnt/gold/shipment_cost_summary'
      TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
      );
      ```

---

## 3. Traceability Matrix

| Transformation Rule                  | Source (Conceptual/Constraint/Silver)         | Target (Gold Layer)                |
|--------------------------------------|-----------------------------------------------|------------------------------------|
| Shipment Cost Aggregation            | Silver DDL, Conceptual 4, Constraints 3.3     | gd_shipment_cost_summary           |
| Data Type and Format Standardization | Constraints 1.3, 2.3, Silver DDL              | gd_shipment_cost_summary           |
| Granularity Check                    | Constraints 2.2, Silver DDL                   | gd_shipment_cost_summary           |
| Traceability and Lineage             | Silver DDL, Constraints 2.5                   | gd_shipment_cost_summary           |
| Partitioning and Performance         | Gold DDL, Silver DDL                          | gd_shipment_cost_summary           |

---

## 4. API Cost

apiCost: 0.000000

---

outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Recommender

pipelineID: 14677
