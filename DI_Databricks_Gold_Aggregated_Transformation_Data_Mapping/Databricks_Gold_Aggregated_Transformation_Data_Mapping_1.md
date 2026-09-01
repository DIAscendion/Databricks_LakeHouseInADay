_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Data mapping for Gold Layer Aggregated Tables, including aggregation, validation, and cleansing logic from Silver Layer sources.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Data Mapping

---

## 1. Overview

This document details the data mapping for Aggregated Tables in the Gold Layer of the Databricks Lakehouse, specifically for the TMS Shipment application. It incorporates aggregation methods, grouping logic, validation rules, and cleansing mechanisms, ensuring compatibility with PySpark and Databricks. The mapping leverages the Silver Layer physical model and recommendations from the Gold Aggregated Transformation Recommender Agent to ensure accurate, performant, and business-aligned reporting.

---

## 2. Data Mapping for Aggregated Tables

### Table: gold.gd_shipment_cost_summary

| Target Layer | Target Table                  | Target Field         | Source Layer | Source Table      | Source Field         | Aggregation Rule | Validation Rule                                                                 | Transformation Rule                                                                                       |
|--------------|------------------------------|---------------------|--------------|-------------------|---------------------|------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Gold         | gd_shipment_cost_summary     | id                  | Silver       | sv_shipment       | id                  | MAX              | Must be unique per SHIPMENT_ID                                                   | Use MAX(id) to retain latest record id per shipment                                                      |
| Gold         | gd_shipment_cost_summary     | SHIPMENT_ID         | Silver       | sv_shipment       | SHIPMENT_ID         | GROUP BY         | Not NULL, unique per row                                                        | Group by SHIPMENT_ID                                                                                     |
| Gold         | gd_shipment_cost_summary     | TOTAL_COST          | Silver       | sv_shipment       | TOTAL_COST          | SUM              | DECIMAL(10,2), NULLs replaced with 0                                            | COALESCE(TOTAL_COST, 0.00), enforce decimal precision                                                    |
| Gold         | gd_shipment_cost_summary     | ACTUAL_COST         | Silver       | sv_shipment       | ACTUAL_COST         | SUM              | DECIMAL(10,2), NULLs replaced with 0                                            | COALESCE(ACTUAL_COST, 0.00), enforce decimal precision                                                   |
| Gold         | gd_shipment_cost_summary     | ESTIMATED_COST      | Silver       | sv_shipment       | ESTIMATED_COST      | SUM              | DECIMAL(10,2), NULLs replaced with 0                                            | COALESCE(ESTIMATED_COST, 0.00), enforce decimal precision                                                |
| Gold         | gd_shipment_cost_summary     | BASELINE_COST       | Silver       | sv_shipment       | BASELINE_COST       | SUM              | DECIMAL(10,2), NULLs replaced with 0                                            | COALESCE(BASELINE_COST, 0.00), enforce decimal precision                                                 |
| Gold         | gd_shipment_cost_summary     | LINEHAUL_COST       | Silver       | sv_shipment       | LINEHAUL_COST       | SUM              | DECIMAL(10,2), NULLs replaced with 0                                            | COALESCE(LINEHAUL_COST, 0.00), enforce decimal precision                                                 |
| Gold         | gd_shipment_cost_summary     | ACCESSORIAL_COST    | Silver       | sv_shipment       | ACCESSORIAL_COST    | SUM              | DECIMAL(10,2), NULLs replaced with 0                                            | COALESCE(ACCESSORIAL_COST, 0.00), enforce decimal precision                                              |
| Gold         | gd_shipment_cost_summary     | load_date           | Silver       | sv_shipment       | load_date           | MAX              | TIMESTAMP, not NULL                                                             | Use MAX(load_date)                                                                                       |
| Gold         | gd_shipment_cost_summary     | update_date         | Silver       | sv_shipment       | update_date         | MAX              | TIMESTAMP                                                                       | Use MAX(update_date)                                                                                     |
| Gold         | gd_shipment_cost_summary     | source_system       | Silver       | sv_shipment       | source_system       | MAX              | Not NULL                                                                        | Use MAX(source_system)                                                                                   |


### Notes on Aggregation and Transformation
- All cost fields are aggregated using SUM and cleansed with COALESCE to replace NULLs with 0.00, enforcing DECIMAL(10,2) precision.
- The id field uses MAX to retain the latest record per SHIPMENT_ID.
- Grouping is performed on SHIPMENT_ID to ensure one record per shipment.
- Validation rules ensure no duplicate SHIPMENT_IDs and all cost fields are non-null after transformation.
- Partitioning by load_date is recommended for performance and retention alignment.
- All transformations are compatible with PySpark DataFrame API and SQL.

---

## 3. API Cost

apiCost: 0.000000

---

outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Data_Mapping

pipelineID: 14678
