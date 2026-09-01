_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Detailed data mapping for Fact tables in the Gold Layer, including transformations, aggregations, validations, and cleansing rules from Silver to Gold Layer for TMS Shipment application.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Data Mapping

## Overview
This document provides a comprehensive data mapping for Fact tables in the Gold Layer of the TMS Shipment application. It details the mapping from Silver Layer tables, incorporating all necessary transformations, aggregations, validations, and cleansing rules as per business requirements and previous transformation recommendations. The mapping ensures:
- Fact-Dimension relationships are clearly defined
- Metric calculations and aggregations are standardized
- Data validation and cleansing logic is enforced
- All transformations are compatible with PySpark and Databricks

**Assumption:** The Gold Fact table is named `gd_shipment` and is modeled after the Silver table `sv_shipment`. Field names are mapped directly unless otherwise specified by transformation rules.

---

## Data Mapping for Fact Tables

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|-------------|--------------|--------------|--------------|--------------|-----------------|---------------------|
| Gold | gd_shipment | SHIPMENT_ID | Silver | sv_shipment | SHIPMENT_ID | Not Null | None |
| Gold | gd_shipment | TOTAL_COST | Silver | sv_shipment | TOTAL_COST | Numeric, >=0 | Currency normalization: If CURRENCY_CODE is NULL, set to 'USD' |
| Gold | gd_shipment | CURRENCY_CODE | Silver | sv_shipment | CURRENCY_CODE | Must be valid ISO code | If NULL, set to 'USD' |
| Gold | gd_shipment | ORDER_QTY | Silver | sv_shipment | ORDER_QTY | Numeric, >=0 | Cast to INT, NULL to 0 |
| Gold | gd_shipment | PLANNED_WEIGHT | Silver | sv_shipment | PLANNED_WEIGHT | Numeric, >=0 | Standardize to KG if needed |
| Gold | gd_shipment | SHIPMENT_STATUS | Silver | sv_shipment | SHIPMENT_STATUS | Not Null | None |
| Gold | gd_shipment | CREATED_DTTM | Silver | sv_shipment | CREATED_DTTM | Not Null, valid timestamp | None |
| Gold | gd_shipment | CUSTOMER_ID | Silver | sv_shipment | CUSTOMER_ID | Not Null | Surrogate key join to gd_customer |
| Gold | gd_shipment | ASSIGNED_CARRIER_ID | Silver | sv_shipment | ASSIGNED_CARRIER_ID | Not Null | Surrogate key join to gd_carrier |
| Gold | gd_shipment | DISTANCE | Silver | sv_shipment | DISTANCE | Numeric, >=0 | Standardize to KM if needed |
| Gold | gd_shipment | DISTANCE_UOM | Silver | sv_shipment | DISTANCE_UOM | Must be valid UOM | Standardize to 'KM' |
| Gold | gd_shipment | DAYS_TO_DELIVER | Silver | sv_shipment | DAYS_TO_DELIVER | Numeric, >=0 | NULL to 0 |
| Gold | gd_shipment | MARGIN | Silver | sv_shipment | MARGIN | Numeric | Round to 2 decimals |
| Gold | gd_shipment | IS_SHIPMENT_CANCELLED | Silver | sv_shipment | IS_SHIPMENT_CANCELLED | 'Y'/'N' | None |
| Gold | gd_shipment | load_date | Silver | sv_shipment | load_date | Not Null | None |
| Gold | gd_shipment | update_date | Silver | sv_shipment | update_date | Not Null | None |
| Gold | gd_shipment | source_system | Silver | sv_shipment | source_system | Not Null | None |

---

### Example Transformation Rules Applied
- **Currency Normalization:**
  ```sql
  SELECT
    SHIPMENT_ID,
    TOTAL_COST,
    CASE WHEN CURRENCY_CODE IS NULL THEN 'USD' ELSE CURRENCY_CODE END AS CURRENCY_CODE
  FROM silver.sv_shipment
  ```
- **Order Quantity Cleansing:**
  ```sql
  SELECT
    COALESCE(CAST(ORDER_QTY AS INT), 0) AS ORDER_QTY
  FROM silver.sv_shipment
  ```
- **Distance Standardization:**
  ```sql
  SELECT
    CASE WHEN DISTANCE_UOM = 'M' THEN DISTANCE / 1000 ELSE DISTANCE END AS DISTANCE,
    'KM' AS DISTANCE_UOM
  FROM silver.sv_shipment
  ```
- **Surrogate Key Joins:**
  ```sql
  SELECT
    f.*,
    c.Customer_Key,
    cr.Carrier_Key
  FROM silver.sv_shipment f
  JOIN gold.gd_customer c ON f.CUSTOMER_ID = c.CUSTOMER_ID
  JOIN gold.gd_carrier cr ON f.ASSIGNED_CARRIER_ID = cr.CARRIER_ID
  ```

---

## Data Validation and Cleansing Logic
- All numeric fields are validated to be >= 0; NULLs replaced with 0 where appropriate.
- All currency codes are standardized to 'USD' if missing.
- All units of measure are standardized (e.g., distances to KM, weights to KG).
- Surrogate key joins are used for all dimension references.
- Duplicate records are removed based on business keys (e.g., SHIPMENT_ID).
- All timestamps are validated for correct format.

---

## API Cost
apiCost: 0.000000

---

outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Data_Mapping

pipelineID: 14676
