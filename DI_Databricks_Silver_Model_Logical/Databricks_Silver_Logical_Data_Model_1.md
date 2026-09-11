_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Silver Layer Logical Data Model for Shipment Process (with required updates)
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Data Model

## 1.1 Table: Si_shipment_process
**Description:** Cleaned and standardized shipment process data, with enhanced business columns, audit, and error tracking.

| Column Name         | Description                                                      | Data Type           |
|--------------------|------------------------------------------------------------------|---------------------|
| shipment_number    | Unique shipment reference (business key)                         | string              |
| shipment_date      | Date and time of shipment (timestamp format)                     | timestamp           |
| origin             | Shipment origin location                                         | string              |
| destination        | Shipment destination location                                    | string              |
| customer_name      | Name of the customer (PII)                                       | string              |
| customer_email     | Email address of the customer (PII)                              | string              |
| customer_phone     | Phone number of the customer (PII)                               | string              |
| customer_address   | Address of the customer (PII)                                    | string              |
| shipment_status    | Current status of the shipment                                   | enum('active','inactive','pending') |
| shipment_weight    | Weight of the shipment                                           | decimal(10,2)       |
| shipment_type      | Type of shipment (e.g., express, standard)                       | string              |
| load_timestamp     | Timestamp when record was loaded                                 | timestamp           |
| update_timestamp   | Timestamp when record was last updated                           | timestamp           |
| source_system      | Source system identifier                                         | string              |
| customer_segment   | Customer segment classification                                  | string              |
| transaction_category | Transaction type (retail, wholesale, online)                   | string              |
| client_id          | Unique client identifier (renamed from customer_id)              | string (NOT NULL)   |
| order_date         | Order date and time (timestamp format)                           | timestamp           |
| amount             | Transaction amount                                               | decimal(10,2)       |
| profit_margin      | Derived: (revenue - cost) / revenue                             | decimal(5,4)        |
| created_at         | Record creation timestamp                                        | timestamp           |
| updated_at         | Record last modification timestamp                               | timestamp           |

**Constraints:**
- client_id: NOT NULL
- transaction_id: UNIQUE

**Notes:**
- Column 'legacy_code' removed as per requirements.
- All column names standardized to snake_case.
- Data types standardized for financial and status fields.

## 1.2 Table: Si_shipment_item
**Description:** Cleaned shipment item details, with enhanced audit and error tracking.

| Column Name         | Description                                                      | Data Type           |
|--------------------|------------------------------------------------------------------|---------------------|
| shipment_number    | Reference to shipment (business key)                             | string              |
| item_description   | Description of the shipped item                                  | string              |
| item_quantity      | Quantity of the item                                             | integer             |
| item_weight        | Weight of the item                                               | decimal(10,2)       |
| load_timestamp     | Timestamp when record was loaded                                 | timestamp           |
| update_timestamp   | Timestamp when record was last updated                           | timestamp           |
| source_system      | Source system identifier                                         | string              |
| created_at         | Record creation timestamp                                        | timestamp           |
| updated_at         | Record last modification timestamp                               | timestamp           |

## 1.3 Table: Si_audit_log
**Description:** Tracks pipeline execution, data processing, and audit events for Silver layer tables.

| Column Name         | Description                                                      | Data Type           |
|--------------------|------------------------------------------------------------------|---------------------|
| source_table       | Name of the source table                                         | string              |
| load_timestamp     | Timestamp when record was loaded                                 | timestamp           |
| processed_by       | User or process that loaded the record                           | string              |
| processing_time    | Time taken to process the record                                 | decimal(10,2)       |
| status             | Processing status (success, failed)                              | enum('success','failed') |
| created_at         | Record creation timestamp                                        | timestamp           |
| updated_at         | Record last modification timestamp                               | timestamp           |

## 1.4 Table: Si_error_log
**Description:** Stores error data from data quality checks and validation processes.

| Column Name         | Description                                                      | Data Type           |
|--------------------|------------------------------------------------------------------|---------------------|
| source_table       | Name of the table where error occurred                            | string              |
| error_type         | Type/category of error                                            | string              |
| error_message      | Detailed error message                                            | string              |
| error_timestamp    | Timestamp when error was detected                                 | timestamp           |
| record_reference   | Reference to the affected record                                  | string              |
| created_at         | Record creation timestamp                                        | timestamp           |
| updated_at         | Record last modification timestamp                               | timestamp           |

# 2. Conceptual Data Model Diagram (Tabular Form)

| Source Table         | Relationship Key Field   | Target Table         | Relationship Type |
|--------------------- |------------------------ |--------------------- |-------------------|
| Si_shipment_process  | shipment_number         | Si_shipment_item     | One-to-Many       |
| Si_shipment_process  | client_id               | Gold_client          | Many-to-One (FK)  |
| Si_shipment_process  | shipment_number         | Si_error_log         | One-to-Many       |
| Si_shipment_process  | shipment_number         | Si_audit_log         | One-to-Many       |

# 3. Rationale for Key Design Decisions and Assumptions
1. All Bronze tables are mirrored in Silver with prefix 'Si_' and PK/FK/ID fields removed.
2. Required changes (add/rename/drop/modify columns, constraints, relationships, data types, derived columns, metadata columns, naming conventions) are applied as per user request.
3. Data type standardization is enforced for financial and status fields.
4. Error and audit tables are included for robust data governance and pipeline traceability.
5. Relationships are documented for cross-layer referential integrity.
6. All column names use snake_case for consistency.
7. Derived columns and constraints are explicitly documented.

# 4. apiCost
apiCost: 0.000200

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Logical
**pipelineID:** 12357
