_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Transformation rules and recommendations for Gold Layer Fact tables based on Store360 Inventory Report conceptual model, constraints, and Silver Layer DDL.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Recommender

This document provides comprehensive transformation rules for Fact tables in the Gold layer, derived from the Store360 Inventory Report conceptual model, business constraints, and Silver Layer DDL. It ensures metric standardization, aggregation, normalization, and traceability for analytics and BI.

---

## 1. Transformation Rules for Fact Tables

### 1.1 Metric Standardization

- **Rule Name**: Percentage Metric Standardization
    - **Description**: Ensure all percentage metrics (e.g., Inventory Accuracy %, Stockout Rate %, Fill Rate %) are numeric values between 0 and 100, rounded to two decimal places.
    - **Rationale**: Consistent metric formatting is critical for accurate reporting and comparison across stores, products, and periods.
    - **SQL Example**:
      ```sql
      SELECT
        ROUND(CAST(Inventory_Accuracy AS DECIMAL(5,2)), 2) AS Inventory_Accuracy,
        ROUND(CAST(Stockout_Rate AS DECIMAL(5,2)), 2) AS Stockout_Rate,
        ROUND(CAST(Fill_Rate AS DECIMAL(5,2)), 2) AS Fill_Rate
      FROM silver.sv_inventory_snapshot
      WHERE Inventory_Accuracy BETWEEN 0 AND 100
        AND Stockout_Rate BETWEEN 0 AND 100
        AND Fill_Rate BETWEEN 0 AND 100
      ```

### 1.2 Fact-Dimension Mapping

- **Rule Name**: Surrogate Key Mapping for Fact-Dimension Joins
    - **Description**: Ensure Fact tables reference Dimension tables using surrogate keys (e.g., Store_ID, Product_ID, Date_ID) for efficient joins and referential integrity.
    - **Rationale**: Surrogate keys improve join performance and maintain consistency across layers.
    - **SQL Example**:
      ```sql
      SELECT
        f.id AS Fact_ID,
        d.Store_ID,
        p.Product_ID,
        dt.Date_ID,
        f.On_Hand_Units,
        f.Inventory_Accuracy
      FROM silver.sv_inventory f
      JOIN gold.gd_store d ON f.Store_Code = d.Store_Code
      JOIN gold.gd_product p ON f.Product_Name = p.Product_Name
      JOIN gold.gd_date dt ON f.Snapshot_Date = dt.Report_Date
      ```

### 1.3 Data Aggregation Rules

- **Rule Name**: Pre-Aggregation for Reporting Periods
    - **Description**: Aggregate Fact metrics by reporting periods (e.g., daily, weekly, monthly) for performance optimization and summary reporting.
    - **Rationale**: Pre-aggregated data enables faster queries and supports dashboarding.
    - **SQL Example**:
      ```sql
      SELECT
        Store_ID,
        Product_ID,
        DATE_TRUNC('month', Snapshot_Date) AS Month,
        SUM(On_Hand_Units) AS Total_On_Hand_Units,
        AVG(Inventory_Accuracy) AS Avg_Inventory_Accuracy
      FROM gold.gd_inventory_snapshot
      GROUP BY Store_ID, Product_ID, DATE_TRUNC('month', Snapshot_Date)
      ```

### 1.4 Normalization and Standardization

- **Rule Name**: Currency and Unit Normalization
    - **Description**: Standardize currency codes and units of measure for all cost and quantity fields (e.g., USD, integer units).
    - **Rationale**: Ensures consistency in financial and inventory reporting across regions and products.
    - **SQL Example**:
      ```sql
      SELECT
        SHIPMENT_ID,
        TOTAL_COST,
        CASE WHEN CURRENCY_CODE IS NULL THEN 'USD' ELSE CURRENCY_CODE END AS CURRENCY_CODE,
        CAST(ORDER_QTY AS INT) AS ORDER_QTY
      FROM silver.sv_shipment
      ```

### 1.5 Handling Missing or Invalid Data

- **Rule Name**: Null and Outlier Handling for Fact Metrics
    - **Description**: Replace NULL values with default values (e.g., 0 for units, 100 for percentages) and filter outliers based on business thresholds.
    - **Rationale**: Prevents reporting errors and ensures completeness of Fact data.
    - **SQL Example**:
      ```sql
      SELECT
        COALESCE(On_Hand_Units, 0) AS On_Hand_Units,
        COALESCE(Inventory_Accuracy, 100) AS Inventory_Accuracy,
        CASE WHEN Stockout_Rate < 0 OR Stockout_Rate > 100 THEN NULL ELSE Stockout_Rate END AS Stockout_Rate
      FROM silver.sv_inventory
      ```

### 1.6 Fact Table Uniqueness and Referential Integrity

- **Rule Name**: Enforce Uniqueness and Referential Integrity
    - **Description**: Ensure Fact table records are unique by business keys (e.g., Store_ID + Product_ID + Date_ID) and reference valid Dimension records.
    - **Rationale**: Prevents duplicate records and maintains data integrity.
    - **SQL Example**:
      ```sql
      SELECT DISTINCT
        Store_ID,
        Product_ID,
        Date_ID,
        On_Hand_Units,
        Inventory_Accuracy
      FROM gold.gd_inventory_snapshot
      WHERE Store_ID IS NOT NULL AND Product_ID IS NOT NULL AND Date_ID IS NOT NULL
      ```

---

## 2. Traceability Matrix

| Transformation Rule                        | Source (Conceptual/Constraint/Silver)         | Target (Gold Layer)           |
|---------------------------------------------|-----------------------------------------------|-------------------------------|
| Percentage Metric Standardization           | Constraints 1.3, 2.3, Silver DDL              | Gold Fact Metrics             |
| Surrogate Key Mapping for Fact-Dimension    | Conceptual 5, Constraints 2.5, Silver DDL     | Gold Fact-Dimension Joins     |
| Pre-Aggregation for Reporting Periods       | Business Rules 3.1, 3.2, Silver DDL           | Gold Fact Aggregates          |
| Currency and Unit Normalization             | Constraints 1.3, 2.3, Silver DDL              | Gold Fact Financial Metrics   |
| Null and Outlier Handling                   | Constraints 1.1, 1.2, 2.1, Silver DDL         | Gold Fact Completeness        |
| Uniqueness and Referential Integrity        | Constraints 2.2, 2.5, Silver DDL              | Gold Fact Integrity           |

---

## 3. API Cost

apiCost: 0.000000

---

outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Recommender

pipelineID: 14675
