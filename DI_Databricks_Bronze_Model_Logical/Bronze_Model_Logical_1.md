_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Bronze layer logical data model for Store360 Inventory domain
## *Version*: 1
## *Updated on*: 
_____________________________________________

# PII Classification

| Column Name        | Reason why it is classified as PII |
|--------------------|------------------------------------|
| email              | Contains personal contact info      |
| address            | Contains personal location info     |
| city               | Contains personal location info     |
| state              | Contains personal location info     |
| postal_code        | Contains personal location info     |
| employee_role      | May reveal sensitive employment info|
| hire_date          | May reveal sensitive employment info|


# Bronze Layer Logical Model

## Table: Bz_REGION
Represents enterprise region hierarchy.

| Column Name   | Description                       | Data Type |
|---------------|-----------------------------------|-----------|
| region_name   | Name of the region                | string    |
| vp_name       | Name of region VP                 | string    |
| is_active     | Region active status              | boolean   |
| created_ts    | Region creation timestamp         | datetime  |
| updated_ts    | Region update timestamp           | datetime  |
| load_timestamp| Data load timestamp               | datetime  |
| update_timestamp| Data update timestamp           | datetime  |
| source_system | Source system identifier          | string    |

## Table: Bz_DISTRICT
Represents district hierarchy.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| district_name    | Name of the district            | string    |
| district_manager | District manager name           | string    |
| is_active        | District active status          | boolean   |
| created_ts       | District creation timestamp     | datetime  |
| updated_ts       | District update timestamp       | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## Table: Bz_STORE
Represents store master data.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| store_number     | Store business number           | string    |
| store_name       | Store name                      | string    |
| fieldhouse_type  | Store fieldhouse type           | string    |
| open_date        | Store opening date              | date      |
| close_date       | Store closing date              | date      |
| address          | Store address                   | string    |
| city             | Store city                      | string    |
| state            | Store state                     | string    |
| postal_code      | Store postal code               | string    |
| is_active        | Store active status             | boolean   |
| created_ts       | Store creation timestamp        | datetime  |
| updated_ts       | Store update timestamp          | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## Table: Bz_ATHLETE
Represents athlete/customer data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| master_account_id   | Athlete master account        | string    |
| loyalty_flag        | Loyalty program flag          | boolean   |
| gold_flag           | Gold program flag             | boolean   |
| first_purchase_date | First purchase date           | date      |
| last_purchase_date  | Last purchase date            | date      |
| omni_channel_flag   | Omni-channel flag             | boolean   |
| created_ts          | Athlete creation timestamp    | datetime  |
| updated_ts          | Athlete update timestamp      | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_ATHLETE_PROFILE
Represents athlete profile data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| persona             | Athlete persona               | string    |
| micro_cohort        | Athlete micro cohort          | string    |
| email               | Athlete email address         | string    |
| created_ts          | Profile creation timestamp    | datetime  |
| updated_ts          | Profile update timestamp      | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_PRODUCT
Represents product master data.

| Column Name            | Description                 | Data Type |
|------------------------|----------------------------|-----------|
| sku                    | Product SKU                | string    |
| upc                    | Product UPC                | string    |
| style_number           | Product style number       | string    |
| brand                  | Product brand              | string    |
| department_description | Department description     | string    |
| vendor_name            | Vendor name                | string    |
| created_ts             | Product creation timestamp | datetime  |
| updated_ts             | Product update timestamp   | datetime  |
| load_timestamp         | Data load timestamp        | datetime  |
| update_timestamp       | Data update timestamp      | datetime  |
| source_system          | Source system identifier   | string    |

## Table: Bz_PRODUCT_HIERARCHY
Represents product hierarchy data.

| Column Name   | Description                       | Data Type |
|---------------|-----------------------------------|-----------|
| division      | Product division                  | string    |
| department    | Product department                | string    |
| class         | Product class                     | string    |
| subclass      | Product subclass                  | string    |
| load_timestamp| Data load timestamp               | datetime  |
| update_timestamp| Data update timestamp           | datetime  |
| source_system | Source system identifier          | string    |

## Table: Bz_INVENTORY_BALANCE
Represents daily inventory position.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| inventory_date   | Inventory date                  | date      |
| on_hand_qty      | On hand quantity                | integer   |
| available_qty    | Available quantity              | integer   |
| allocated_qty    | Allocated quantity              | integer   |
| damaged_qty      | Damaged quantity                | integer   |
| last_update_ts   | Last update timestamp           | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## Table: Bz_INVENTORY_ADJUSTMENT
Represents inventory adjustment events.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| adjustment_reason| Reason for adjustment           | string    |
| adjustment_qty   | Adjustment quantity             | integer   |
| adjustment_ts    | Adjustment timestamp            | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## Table: Bz_INVENTORY_REPLENISHMENT
Represents inventory replenishment events.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| requested_qty    | Requested quantity              | integer   |
| replenished_qty  | Replenished quantity            | integer   |
| replenishment_ts | Replenishment timestamp         | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## Table: Bz_RFID_EVENT
Represents RFID scan events.

| Column Name           | Description                  | Data Type |
|-----------------------|-----------------------------|-----------|
| scan_ts               | RFID scan timestamp         | datetime  |
| total_on_hand         | Total on hand quantity      | integer   |
| cycle_count_delta     | Cycle count delta           | integer   |
| store_available_on_hand| Store available on hand    | integer   |
| load_timestamp        | Data load timestamp         | datetime  |
| update_timestamp      | Data update timestamp       | datetime  |
| source_system         | Source system identifier    | string    |

## Table: Bz_RFID_CYCLE_COUNT
Represents RFID cycle count events.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| count_date       | Cycle count date                | date      |
| completion_pct   | Completion percentage           | float     |
| variance_pct     | Variance percentage             | float     |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## Table: Bz_SALES_TRANSACTION
Represents sales transactions.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| transaction_ts      | Transaction timestamp         | datetime  |
| total_sales_amount  | Total sales amount            | float     |
| sales_channel       | Sales channel                 | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_SALES_TRANSACTION_LINE
Represents sales transaction line items.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| quantity            | Quantity sold                 | integer   |
| net_sale_price      | Net sale price                | float     |
| cost_amount         | Cost amount                   | float     |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_FULFILLMENT_REQUEST
Represents fulfillment requests.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| request_type        | Type of fulfillment request   | string    |
| request_status      | Status of request             | string    |
| created_ts          | Request creation timestamp    | datetime  |
| completed_ts        | Request completion timestamp  | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_FULFILLMENT_REQUEST_UNIT
Represents fulfillment request units.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| requested_qty       | Requested quantity            | integer   |
| picked_qty          | Picked quantity               | integer   |
| declined_qty        | Declined quantity             | integer   |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_TASK
Represents store tasks.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| task_type_cd        | Task type code                | string    |
| assigned_employee_id| Assigned employee identifier  | string    |
| task_status         | Task status                   | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_SEARCH_EVENT
Represents product search events.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| search_phrase       | Search phrase                 | string    |
| results_count       | Number of results             | integer   |
| search_ts           | Search timestamp              | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_PRODUCT_VIEW_EVENT
Represents product view events.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| finding_method      | Method used to find product   | string    |
| event_ts            | Event timestamp               | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_EMPLOYEE
Represents employee data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| employee_role       | Employee role                 | string    |
| hire_date           | Employee hire date            | date      |
| status              | Employee status               | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_LABOR_TIMECARD
Represents labor timecard data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| work_date           | Work date                     | date      |
| scheduled_hours     | Scheduled hours               | float     |
| worked_hours        | Worked hours                  | float     |
| overtime_hours      | Overtime hours                | float     |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_SHIPMENT
Represents shipment data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| tc_shipment_id      | Transportation carrier shipment id | string |
| shipment_status     | Shipment status               | string    |
| shipment_type       | Shipment type                 | string    |
| total_cost          | Total shipment cost           | float     |
| shipment_start_dttm | Shipment start datetime       | datetime  |
| shipment_end_dttm   | Shipment end datetime         | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## Table: Bz_SHIPMENT_EVENT
Represents shipment event data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| event_type          | Shipment event type           | string    |
| event_ts            | Event timestamp               | datetime  |
| location            | Event location                | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

# Audit Table Design

| Field           | Description                       | Data Type |
|-----------------|-----------------------------------|-----------|
| record_id       | Unique record identifier          | string    |
| source_table    | Source table name                 | string    |
| load_timestamp  | Data load timestamp               | datetime  |
| processed_by    | Processing agent/user             | string    |
| processing_time | Processing time                   | float     |
| status          | Processing status                 | string    |

# Conceptual Data Model Diagram (Tabular Form)

| Source Entity      | Relationship Key Field     | Target Entity      | Relationship Type |
|--------------------|---------------------------|--------------------|-------------------|
| Bz_STORE           | region_name               | Bz_REGION          | Many-to-One       |
| Bz_STORE           | store_number              | Bz_INVENTORY_BALANCE| One-to-Many      |
| Bz_STORE           | store_number              | Bz_RFID_EVENT      | One-to-Many       |
| Bz_STORE           | store_number              | Bz_FULFILLMENT_REQUEST| One-to-Many    |
| Bz_STORE           | store_number              | Bz_SEARCH_EVENT    | One-to-Many       |
| Bz_PRODUCT         | department_description    | Bz_PRODUCT_HIERARCHY| Many-to-One      |
| Bz_PRODUCT         | sku                      | Bz_INVENTORY_BALANCE| One-to-Many      |
| Bz_PRODUCT         | sku                      | Bz_RFID_EVENT      | One-to-Many       |
| Bz_ATHLETE         | master_account_id         | Bz_ATHLETE_PROFILE | One-to-Many       |
| Bz_EMPLOYEE        | employee_role             | Bz_TASK            | One-to-Many       |

# Rationale & Assumptions
- All source tables are mirrored in Bronze layer with prefix 'Bz_'.
- Primary and foreign key fields are excluded from Bronze layer tables.
- Metadata columns (load_timestamp, update_timestamp, source_system) are added for audit and lineage.
- PII fields are classified per GDPR standards.
- Audit table tracks data processing lineage and status.
- Relationships are documented based on conceptual model and source schema.
- No physical column names (e.g., _id) are used in Bronze layer.

# API Cost
apiCost: 0.000500
