_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Detailed data mapping for Fact tables from Silver to Gold Layer, including transformations, aggregations, validations, and cleansing rules for the Shipment domain.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Overview

This document provides a comprehensive data mapping for Fact tables in the Gold Layer of the Databricks Lakehouse (Shipment Domain). The mapping is based on the Silver Layer physical model and transformation best practices. It details attribute-level transformations, aggregation logic, validation rules, and cleansing logic to ensure high data quality, consistency, and business relevance. All rules are compatible with PySpark and Databricks, and explanations are provided for complex business logic.

---

# Data Mapping for Fact Tables

| Target Layer | Target Table         | Target Field                | Source Layer | Source Table           | Source Field                | Validation Rule                                      | Transformation Rule                                                                                  |
|-------------|---------------------|-----------------------------|--------------|-----------------------|-----------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Gold        | go_shipment_fact    | shipment_fact_id            | Silver       | si_shipment_process   | shipment_process_id         | Unique, Not Null                                    | Surrogate key: sha2(shipment_process_id, 256)                                                      |
| Gold        | go_shipment_fact    | shipment_number             | Silver       | si_shipment_process   | shipment_number             | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | shipment_date               | Silver       | si_shipment_process   | shipment_date               | Not Null, Valid Date                                | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | origin_dim_id               | Gold         | go_facility_dim       | facility_dim_id             | FK exists in go_facility_dim                        | Map via O_FACILITY_ID join to go_facility_dim                                                     |
| Gold        | go_shipment_fact    | destination_dim_id          | Gold         | go_facility_dim       | facility_dim_id             | FK exists in go_facility_dim                        | Map via D_FACILITY_ID join to go_facility_dim                                                     |
| Gold        | go_shipment_fact    | carrier_dim_id              | Gold         | go_carrier_dim        | carrier_dim_id              | FK exists in go_carrier_dim                         | Map via ASSIGNED_CARRIER_ID join to go_carrier_dim                                                |
| Gold        | go_shipment_fact    | route_dim_id                | Gold         | go_route_dim          | route_dim_id                | FK exists in go_route_dim                           | Map via ROUTE_REFERENCE join to go_route_dim                                                       |
| Gold        | go_shipment_fact    | shipment_status             | Silver       | si_shipment_process   | shipment_status             | Not Null, Enum                                      | UPPER(COALESCE(shipment_status, 'UNKNOWN'))                                                       |
| Gold        | go_shipment_fact    | shipment_weight_kg          | Silver       | si_shipment_process   | shipment_weight             | Not Null, >= 0, DECIMAL(10,2)                       | COALESCE(CAST(shipment_weight AS DECIMAL(10,2)), 0)                                               |
| Gold        | go_shipment_fact    | shipment_type               | Silver       | si_shipment_process   | shipment_type               | Not Null                                            | UPPER(COALESCE(shipment_type, 'UNKNOWN'))                                                         |
| Gold        | go_shipment_fact    | customer_dim_id             | Gold         | go_business_partner_dim| business_partner_dim_id     | FK exists in go_business_partner_dim                 | Map via BUSINESS_PARTNER_ID join to go_business_partner_dim                                        |
| Gold        | go_shipment_fact    | order_date                  | Silver       | si_shipment_process   | order_date                  | Valid Date                                          | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | amount_usd                  | Silver       | si_shipment_process   | amount                      | >= 0, DECIMAL(10,2)                                 | COALESCE(CAST(amount AS DECIMAL(10,2)), 0)                                                        |
| Gold        | go_shipment_fact    | profit_margin               | Silver       | si_shipment_process   | profit_margin               | >= 0, <= 1, DECIMAL(5,4)                            | COALESCE(CAST(profit_margin AS DECIMAL(5,4)), 0)                                                  |
| Gold        | go_shipment_fact    | total_cost_usd              | Silver       | si_shipment_process   | TOTAL_COST                  | >= 0, DECIMAL(10,2)                                 | COALESCE(CAST(TOTAL_COST AS DECIMAL(10,2)), 0)                                                    |
| Gold        | go_shipment_fact    | total_revenue_usd           | Silver       | si_shipment_process   | TOTAL_REVENUE               | >= 0, DECIMAL(10,2)                                 | COALESCE(CAST(TOTAL_REVENUE AS DECIMAL(10,2)), 0)                                                 |
| Gold        | go_shipment_fact    | margin_usd                  | Silver       | si_shipment_process   | MARGIN                      | DECIMAL(10,2)                                       | COALESCE(CAST(MARGIN AS DECIMAL(10,2)), 0)                                                        |
| Gold        | go_shipment_fact    | number_of_stops             | Silver       | si_shipment_process   | NUM_STOPS                   | >= 0, INT                                           | COALESCE(CAST(NUM_STOPS AS INT), 0)                                                               |
| Gold        | go_shipment_fact    | planned_weight_kg           | Silver       | si_shipment_process   | PLANNED_WEIGHT              | >= 0, DECIMAL(10,3)                                 | COALESCE(CAST(PLANNED_WEIGHT AS DECIMAL(10,3)), 0)                                                |
| Gold        | go_shipment_fact    | planned_volume_m3           | Silver       | si_shipment_process   | PLANNED_VOLUME              | >= 0, DECIMAL(10,3)                                 | COALESCE(CAST(PLANNED_VOLUME AS DECIMAL(10,3)), 0)                                                |
| Gold        | go_shipment_fact    | created_at                  | Silver       | si_shipment_process   | created_at                  | Valid Timestamp                                     | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | updated_at                  | Silver       | si_shipment_process   | updated_at                  | Valid Timestamp                                     | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_shipment_fact    | source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |

---

# Explanations for Complex Transformations, Aggregations, and Business Rules

- **Surrogate Key Generation**: The fact table uses a surrogate key generated via SHA2 hash of the shipment_process_id, ensuring uniqueness and supporting efficient joins.
- **Fact-Dimension Relationships**: All *_dim_id fields are foreign keys referencing the corresponding dimension tables in the Gold Layer, enabling star schema analytics.
- **Metric Calculations**: Amount, cost, revenue, and margin fields are cast to DECIMAL and nulls are replaced with 0 for reporting accuracy.
- **Unit Standardization**: All weights are assumed to be in kilograms and volumes in cubic meters. If source units differ, conversion logic should be applied (not required in current DDLs).
- **Null Handling**: All fields replace NULL values with 'UNKNOWN' (for strings) or 0 (for numerics), preventing issues in downstream processes and reporting.
- **Data Validation**: Numeric fields are validated for non-negativity and correct data types. Date and timestamp fields are validated for correct format.
- **Aggregation Rules**: For reporting, SUM, AVG, COUNT, MAX, MIN can be applied to amount, cost, revenue, margin, weight, and volume fields as needed in analytics queries.
- **Deduplication**: Fact table is deduplicated based on shipment_fact_id.
- **Traceability**: Audit columns (load_date, update_date, source_system) are mapped directly from Silver to Gold, supporting lineage and compliance.

---

# API Cost

apiCost: 0.001500

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Data_Mapping
**pipelineID:** 14676
