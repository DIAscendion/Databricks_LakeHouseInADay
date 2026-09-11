_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Bronze Layer Logical Data Model for Shipment Process (Updated)
## *Version*: 4
## *Updated on*: 
_____________________________________________

# PII Classification

| Column Name         | Reason why it is classified as PII                |
|--------------------|--------------------------------------------------|
| customer_name      | Contains personal information (GDPR)              |
| customer_email     | Contains personal contact information (GDPR)      |
| customer_phone     | Contains personal contact information (GDPR)      |
| customer_address   | Contains personal address (GDPR)                  |

# Bronze Layer Logical Model

## Table: Bz_Shipment_Process
**Description:** Raw shipment process data as ingested from the source system, including shipment details and customer information.

| Column Name         | Description                                   | Data Type   |
|--------------------|-----------------------------------------------|-------------|
| shipment_number    | Unique shipment reference (business key)       | String      |
| shipment_date      | Date of shipment                              | Date        |
| origin             | Shipment origin location                       | String      |
| destination        | Shipment destination location                  | String      |
| customer_name      | Name of the customer (PII)                     | String      |
| customer_email     | Email address of the customer (PII)            | String      |
| customer_phone     | Phone number of the customer (PII)             | String      |
| customer_address   | Address of the customer (PII)                  | String      |
| shipment_status    | Current status of the shipment                 | String      |
| shipment_weight    | Weight of the shipment                         | Decimal     |
| shipment_type      | Type of shipment (e.g., express, standard)     | String      |
| load_timestamp     | Timestamp when record was loaded               | Timestamp   |
| update_timestamp   | Timestamp when record was last updated         | Timestamp   |
| source_system      | Source system identifier                       | String      |

## Table: Bz_Shipment_Item
**Description:** Raw shipment item details as ingested from the source system, representing individual items within a shipment.

| Column Name         | Description                                   | Data Type   |
|--------------------|-----------------------------------------------|-------------|
| shipment_number    | Reference to shipment (business key)           | String      |
| item_description   | Description of the shipped item                | String      |
| item_quantity      | Quantity of the item                           | Integer     |
| item_weight        | Weight of the item                             | Decimal     |
| load_timestamp     | Timestamp when record was loaded               | Timestamp   |
| update_timestamp   | Timestamp when record was last updated         | Timestamp   |
| source_system      | Source system identifier                       | String      |

# Audit Table Design

| Field Name         | Description                                    | Data Type   |
|--------------------|------------------------------------------------|-------------|
| record_id          | Unique record identifier (business key)         | String      |
| source_table       | Name of the source table                       | String      |
| load_timestamp     | Timestamp when record was loaded               | Timestamp   |
| processed_by       | User or process that loaded the record         | String      |
| processing_time    | Time taken to process the record               | Decimal     |
| status             | Processing status (e.g., success, failed)      | String      |

# Conceptual Data Model Diagram (Tabular Form)

| Table Name           | Related Table         | Relationship Field      |
|--------------------- |----------------------|------------------------|
| Bz_Shipment_Process  | Bz_Shipment_Item     | shipment_number        |

# Rationale for Key Design Decisions and Assumptions
- All source tables are mirrored in the Bronze layer with the prefix 'Bz_'.
- Primary and foreign key fields (e.g., shipment_id) are excluded as per instructions; business keys are retained for relationships.
- PII fields are classified according to GDPR standards and clearly marked.
- Metadata columns (load_timestamp, update_timestamp, source_system) are added for operational lineage and auditability.
- Audit table is designed to track data ingestion and processing events.
- No physical column names like _ID are used; business keys are used for relationships.
- Only entities and attributes present in the provided source structure are included.

# API Cost
apiCost: 0.000100

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Logical
**pipelineID:** 13782