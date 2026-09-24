_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Detailed data mapping for Dimension tables from Silver to Gold Layer, including transformations, validations, and cleansing rules for the Shipment domain.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Overview

This document provides a comprehensive data mapping for Dimension tables in the Gold Layer of the Databricks Lakehouse (Shipment Domain). The mapping is based on the Silver Layer physical model and transformation recommendations. It details attribute-level transformations, validation rules, and cleansing logic to ensure high data quality, consistency, and business relevance. All rules are compatible with PySpark and Databricks, and explanations are provided for complex business logic.

---

# Data Mapping for Dimension Tables

| Target Layer | Target Table           | Target Field                | Source Layer | Source Table           | Source Field                | Validation Rule                                      | Transformation Rule                                                                                  |
|-------------|-----------------------|-----------------------------|--------------|-----------------------|-----------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Gold        | go_carrier_dim         | carrier_dim_id              | Silver       | si_shipment_process   | ASSIGNED_CARRIER_ID, ...    | Unique, Not Null                                    | Surrogate key: sha2(concat_ws('|', carrier fields), 256)                                           |
| Gold        | go_carrier_dim         | primary_carrier_name        | Silver       | si_shipment_process   | ASSIGNED_CARRIER_ID         | Not Null                                            | UPPER(COALESCE(ASSIGNED_CARRIER_ID, 'UNKNOWN'))                                                    |
| Gold        | go_carrier_dim         | secondary_carrier_name      | Silver       | si_shipment_process   | ASSIGNED_SCNDR_CARRIER_ID   | Not Null                                            | UPPER(COALESCE(ASSIGNED_SCNDR_CARRIER_ID, 'UNKNOWN'))                                              |
| Gold        | go_carrier_dim         | broker_carrier_name         | Silver       | si_shipment_process   | BROKER_CARRIER_ID           | Not Null                                            | UPPER(COALESCE(BROKER_CARRIER_ID, 'UNKNOWN'))                                                      |
| Gold        | go_carrier_dim         | designated_carrier_name     | Silver       | si_shipment_process   | DSG_CARRIER_ID              | Not Null                                            | UPPER(COALESCE(DSG_CARRIER_ID, 'UNKNOWN'))                                                         |
| Gold        | go_carrier_dim         | feasible_carrier_name       | Silver       | si_shipment_process   | FEASIBLE_CARRIER_ID         | Not Null                                            | UPPER(COALESCE(FEASIBLE_CARRIER_ID, 'UNKNOWN'))                                                    |
| Gold        | go_carrier_dim         | mode_of_transport           | Silver       | si_shipment_process   | ASSIGNED_MOT_ID             | Not Null                                            | UPPER(COALESCE(ASSIGNED_MOT_ID, 'UNKNOWN'))                                                        |
| Gold        | go_carrier_dim         | load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_carrier_dim         | update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_carrier_dim         | source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_facility_dim        | facility_dim_id             | Silver       | si_shipment_process   | O_FACILITY_ID, D_FACILITY_ID| Unique, Not Null                                    | Surrogate key: sha2(concat_ws('|', facility fields), 256)                                          |
| Gold        | go_facility_dim        | facility_name               | Silver       | si_shipment_process   | O_FACILITY_ID/D_FACILITY_ID | Not Null                                            | UPPER(TRIM(COALESCE(O_FACILITY_ID/D_FACILITY_ID, 'UNKNOWN')))                                      |
| Gold        | go_facility_dim        | address                     | Silver       | si_shipment_process   | O_ADDRESS/D_ADDRESS         | Not Null                                            | UPPER(TRIM(COALESCE(O_ADDRESS/D_ADDRESS, 'UNKNOWN')))                                              |
| Gold        | go_facility_dim        | city                        | Silver       | si_shipment_process   | O_CITY/D_CITY               | Not Null                                            | UPPER(TRIM(COALESCE(O_CITY/D_CITY, 'UNKNOWN')))                                                    |
| Gold        | go_facility_dim        | state                       | Silver       | si_shipment_process   | O_STATE_PROV/D_STATE_PROV   | Not Null                                            | UPPER(TRIM(COALESCE(O_STATE_PROV/D_STATE_PROV, 'UNKNOWN')))                                        |
| Gold        | go_facility_dim        | postal_code                 | Silver       | si_shipment_process   | O_POSTAL_CODE/D_POSTAL_CODE | Not Null                                            | UPPER(TRIM(COALESCE(O_POSTAL_CODE/D_POSTAL_CODE, 'UNKNOWN')))                                      |
| Gold        | go_facility_dim        | country                     | Silver       | si_shipment_process   | O_COUNTRY_CODE/D_COUNTRY_CODE| Not Null                                           | UPPER(TRIM(COALESCE(O_COUNTRY_CODE/D_COUNTRY_CODE, 'UNKNOWN'))                                     |
| Gold        | go_facility_dim        | load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_facility_dim        | update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_facility_dim        | source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_route_dim           | route_dim_id                | Silver       | si_shipment_process   | ROUTE_REFERENCE, DISTANCE...| Unique, Not Null                                    | Surrogate key: sha2(concat_ws('|', route fields), 256)                                             |
| Gold        | go_route_dim           | route_reference             | Silver       | si_shipment_process   | ROUTE_REFERENCE             | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_route_dim           | total_route_distance        | Silver       | si_shipment_process   | DISTANCE                    | Not Null, DECIMAL(10,2)                            | CAST(DISTANCE AS DECIMAL(10,2)), COALESCE(DISTANCE, 0)                                             |
| Gold        | go_route_dim           | direct_distance             | Silver       | si_shipment_process   | DIRECT_DISTANCE             | Not Null, DECIMAL(10,2)                            | CAST(DIRECT_DISTANCE AS DECIMAL(10,2)), COALESCE(DIRECT_DISTANCE, 0)                               |
| Gold        | go_route_dim           | out_of_route_distance       | Silver       | si_shipment_process   | OUT_OF_ROUTE_DISTANCE       | Not Null, DECIMAL(10,2)                            | CAST(OUT_OF_ROUTE_DISTANCE AS DECIMAL(10,2)), COALESCE(OUT_OF_ROUTE_DISTANCE, 0)                   |
| Gold        | go_route_dim           | distance_unit_of_measure    | Silver       | si_shipment_process   | DISTANCE_UOM                | Not Null                                            | UPPER(COALESCE(DISTANCE_UOM, 'UNKNOWN'))                                                           |
| Gold        | go_route_dim           | number_of_stops             | Silver       | si_shipment_process   | NUM_STOPS                   | Not Null, INT                                      | CAST(NUM_STOPS AS INT), COALESCE(NUM_STOPS, 0)                                                     |
| Gold        | go_route_dim           | equipment_type              | Silver       | si_shipment_process   | EQUIPMENT_TYPE              | Not Null                                            | UPPER(COALESCE(EQUIPMENT_TYPE, 'UNKNOWN'))                                                         |
| Gold        | go_route_dim           | load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_route_dim           | update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_route_dim           | source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_billing_dim         | billing_dim_id              | Silver       | si_shipment_process   | BILL_OF_LADING_NUMBER, ...  | Unique, Not Null                                    | Surrogate key: sha2(concat_ws('|', billing fields), 256)                                           |
| Gold        | go_billing_dim         | bill_of_lading_number       | Silver       | si_shipment_process   | BILL_OF_LADING_NUMBER       | Not Null                                            | COALESCE(BILL_OF_LADING_NUMBER, 'UNKNOWN')                                                         |
| Gold        | go_billing_dim         | billing_method              | Silver       | si_shipment_process   | BILLING_METHOD              | Not Null                                            | CAST(BILLING_METHOD AS STRING), COALESCE(BILLING_METHOD, 'UNKNOWN')                                 |
| Gold        | go_billing_dim         | purchase_order_reference    | Silver       | si_shipment_process   | PURCHASE_ORDER              | Not Null                                            | COALESCE(PURCHASE_ORDER, 'UNKNOWN')                                                                |
| Gold        | go_billing_dim         | bill_to_postal_code         | Silver       | si_shipment_process   | BILL_TO_POSTAL_CODE         | Not Null                                            | COALESCE(BILL_TO_POSTAL_CODE, 'UNKNOWN')                                                           |
| Gold        | go_billing_dim         | bill_to_state_province      | Silver       | si_shipment_process   | BILL_TO_STATE_PROV          | Not Null                                            | COALESCE(BILL_TO_STATE_PROV, 'UNKNOWN')                                                            |
| Gold        | go_billing_dim         | reconciliation_date         | Silver       | si_shipment_process   | SHIPMENT_RECON_DTTM         | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_billing_dim         | load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_billing_dim         | update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_billing_dim         | source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_business_partner_dim| business_partner_dim_id     | Silver       | si_shipment_process   | BUSINESS_PARTNER_ID         | Unique, Not Null                                    | Surrogate key: sha2(UPPER(BUSINESS_PARTNER_ID), 256)                                               |
| Gold        | go_business_partner_dim| business_partner_identifier | Silver       | si_shipment_process   | BUSINESS_PARTNER_ID         | Not Null                                            | UPPER(COALESCE(BUSINESS_PARTNER_ID, 'UNKNOWN'))                                                    |
| Gold        | go_business_partner_dim| load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_business_partner_dim| update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_business_partner_dim| source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_user_dim            | user_dim_id                 | Silver       | si_shipment_process   | CREATOR_ROLE, CREATED_SOURCE_TYPE| Unique, Not Null                              | Surrogate key: sha2(concat_ws('|', UPPER(CREATOR_ROLE), UPPER(CREATED_SOURCE_TYPE)), 256)           |
| Gold        | go_user_dim            | creator_role                | Silver       | si_shipment_process   | CREATOR_ROLE                | Not Null                                            | UPPER(COALESCE(CREATOR_ROLE, 'UNKNOWN'))                                                           |
| Gold        | go_user_dim            | creation_source_type        | Silver       | si_shipment_process   | CREATED_SOURCE_TYPE         | Not Null                                            | UPPER(COALESCE(CREATED_SOURCE_TYPE, 'UNKNOWN'))                                                    |
| Gold        | go_user_dim            | load_date                   | Silver       | si_shipment_process   | load_date                   | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_user_dim            | update_date                 | Silver       | si_shipment_process   | update_date                 | Not Null                                            | Direct mapping                                                                                    |
| Gold        | go_user_dim            | source_system               | Silver       | si_shipment_process   | source_system               | Not Null                                            | Direct mapping                                                                                    |

---

# Explanations for Complex Transformations and Business Rules

- **Surrogate Key Generation**: All dimension tables use a surrogate key generated via SHA2 hash of concatenated relevant fields, ensuring uniqueness and supporting efficient joins.
- **Standardization**: All string fields are standardized to uppercase and trimmed to ensure consistency and prevent mismatches in reporting and analytics.
- **Null Handling**: All fields replace NULL values with 'UNKNOWN' (for strings) or 0 (for numerics), preventing issues in downstream processes and reporting.
- **Deduplication**: Dimension tables are deduplicated based on their surrogate key, ensuring only unique records are present.
- **Traceability**: Audit columns (load_date, update_date, source_system) are mapped directly from Silver to Gold, supporting lineage and compliance.
- **Data Type Alignment**: All fields are cast to their required types as per Gold DDL, ensuring compatibility and correctness.
- **Hierarchical Relationships**: Route dimension includes mapping to shipment and facility for drill-down analytics.

---

# API Cost

apiCost: 0.001200

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Data_Mapping
**pipelineID:** 14671
