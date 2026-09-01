_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Silver layer logical data model for Store360 Inventory domain
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Data Model

Below are the Silver layer tables, each prefixed with 'Si_' and excluding primary key, foreign key, and ID fields. Data types are standardized, and brief descriptions are provided for each column.

## 1.1 Table: Si_REGION
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

## 1.2 Table: Si_DISTRICT
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

## 1.3 Table: Si_STORE
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

## 1.4 Table: Si_ATHLETE
Represents athlete/customer data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
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

## 1.5 Table: Si_ATHLETE_PROFILE
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

## 1.6 Table: Si_PRODUCT
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

## 1.7 Table: Si_PRODUCT_HIERARCHY
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

## 1.8 Table: Si_INVENTORY_BALANCE
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

## 1.9 Table: Si_INVENTORY_ADJUSTMENT
Represents inventory adjustment events.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| adjustment_reason| Reason for adjustment           | string    |
| adjustment_qty   | Adjustment quantity             | integer   |
| adjustment_ts    | Adjustment timestamp            | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## 1.10 Table: Si_INVENTORY_REPLENISHMENT
Represents inventory replenishment events.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| requested_qty    | Requested quantity              | integer   |
| replenished_qty  | Replenished quantity            | integer   |
| replenishment_ts | Replenishment timestamp         | datetime  |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## 1.11 Table: Si_RFID_EVENT
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

## 1.12 Table: Si_RFID_CYCLE_COUNT
Represents RFID cycle count events.

| Column Name      | Description                     | Data Type |
|------------------|---------------------------------|-----------|
| count_date       | Cycle count date                | date      |
| completion_pct   | Completion percentage           | float     |
| variance_pct     | Variance percentage             | float     |
| load_timestamp   | Data load timestamp             | datetime  |
| update_timestamp | Data update timestamp           | datetime  |
| source_system    | Source system identifier        | string    |

## 1.13 Table: Si_SALES_TRANSACTION
Represents sales transactions.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| transaction_ts      | Transaction timestamp         | datetime  |
| total_sales_amount  | Total sales amount            | float     |
| sales_channel       | Sales channel                 | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.14 Table: Si_SALES_TRANSACTION_LINE
Represents sales transaction line items.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| quantity            | Quantity sold                 | integer   |
| net_sale_price      | Net sale price                | float     |
| cost_amount         | Cost amount                   | float     |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.15 Table: Si_FULFILLMENT_REQUEST
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

## 1.16 Table: Si_FULFILLMENT_REQUEST_UNIT
Represents fulfillment request units.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| requested_qty       | Requested quantity            | integer   |
| picked_qty          | Picked quantity               | integer   |
| declined_qty        | Declined quantity             | integer   |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.17 Table: Si_TASK
Represents store tasks.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| task_type_cd        | Task type code                | string    |
| assigned_employee_id| Assigned employee identifier  | string    |
| task_status         | Task status                   | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.18 Table: Si_SEARCH_EVENT
Represents product search events.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| search_phrase       | Search phrase                 | string    |
| results_count       | Number of results             | integer   |
| search_ts           | Search timestamp              | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.19 Table: Si_PRODUCT_VIEW_EVENT
Represents product view events.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| finding_method      | Method used to find product   | string    |
| event_ts            | Event timestamp               | datetime  |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.20 Table: Si_EMPLOYEE
Represents employee data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| employee_role       | Employee role                 | string    |
| hire_date           | Employee hire date            | date      |
| status              | Employee status               | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.21 Table: Si_LABOR_TIMECARD
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

## 1.22 Table: Si_SHIPMENT
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

## 1.23 Table: Si_SHIPMENT_EVENT
Represents shipment event data.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| event_type          | Shipment event type           | string    |
| event_ts            | Event timestamp               | datetime  |
| location            | Event location                | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| update_timestamp    | Data update timestamp         | datetime  |
| source_system       | Source system identifier      | string    |

## 1.24 Table: Si_ERROR_DATA
Captures error data from data quality checks and validation.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| error_type          | Type of error                 | string    |
| error_message       | Error message                 | string    |
| error_source_table  | Source table where error occurred | string |
| error_timestamp     | Timestamp of error occurrence | datetime  |
| record_data         | Data of the record in error   | string    |
| load_timestamp      | Data load timestamp           | datetime  |

## 1.25 Table: Si_AUDIT_LOG
Captures process audit data from pipeline execution.

| Column Name         | Description                   | Data Type |
|---------------------|------------------------------|-----------|
| source_table        | Source table name             | string    |
| load_timestamp      | Data load timestamp           | datetime  |
| processed_by        | Processing agent/user         | string    |
| processing_time     | Processing time (seconds)     | float     |
| status              | Processing status             | string    |

# 2. Conceptual Data Model Diagram (Tabular Form)

| Source Entity      | Relationship Key Field     | Target Entity      | Relationship Type |
|--------------------|---------------------------|--------------------|-------------------|
| Si_STORE           | region_name               | Si_REGION          | Many-to-One       |
| Si_STORE           | store_number              | Si_INVENTORY_BALANCE| One-to-Many      |
| Si_STORE           | store_number              | Si_RFID_EVENT      | One-to-Many       |
| Si_STORE           | store_number              | Si_FULFILLMENT_REQUEST| One-to-Many    |
| Si_STORE           | store_number              | Si_SEARCH_EVENT    | One-to-Many       |
| Si_PRODUCT         | department_description    | Si_PRODUCT_HIERARCHY| Many-to-One      |
| Si_PRODUCT         | sku                      | Si_INVENTORY_BALANCE| One-to-Many      |
| Si_PRODUCT         | sku                      | Si_RFID_EVENT      | One-to-Many       |
| Si_ATHLETE         |                          | Si_ATHLETE_PROFILE | One-to-Many       |
| Si_EMPLOYEE        | employee_role             | Si_TASK            | One-to-Many       |

# 3. apiCost
apiCost: 0.000500
