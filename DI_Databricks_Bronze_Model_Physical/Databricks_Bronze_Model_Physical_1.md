_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Physical data model for Databricks Bronze layer based on Store360 Inventory Report and DSG Stores Process Tables
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Physical

## Purpose
This document defines the comprehensive physical data model for the Bronze layer of the Medallion architecture for Store360 Inventory and DSG Stores. It translates the logical model into Delta Lake tables, capturing raw data with added metadata for governance and lineage. All DDL scripts are Databricks SQL compatible.

---

## Bronze Layer DDL Scripts

### REGION
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_region (
  region_id STRING,
  region_name STRING,
  vp_name STRING,
  is_active STRING,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### DISTRICT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_district (
  district_id STRING,
  region_id STRING,
  district_name STRING,
  district_manager STRING,
  is_active STRING,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### STORE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_store (
  store_id STRING,
  store_number STRING,
  store_name STRING,
  district_id STRING,
  fieldhouse_type STRING,
  open_date DATE,
  close_date DATE,
  address STRING,
  city STRING,
  state STRING,
  postal_code STRING,
  is_active STRING,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### ATHLETE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_athlete (
  athlete_id STRING,
  master_account_id STRING,
  loyalty_flag STRING,
  gold_flag STRING,
  first_purchase_date DATE,
  last_purchase_date DATE,
  omni_channel_flag STRING,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### ATHLETE_PROFILE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_athlete_profile (
  athlete_profile_id STRING,
  athlete_id STRING,
  preferred_store_id STRING,
  persona STRING,
  micro_cohort STRING,
  email STRING,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### PRODUCT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_product (
  product_id STRING,
  sku STRING,
  upc STRING,
  style_number STRING,
  brand STRING,
  department_description STRING,
  vendor_name STRING,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### PRODUCT_HIERARCHY
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_product_hierarchy (
  hierarchy_id STRING,
  product_id STRING,
  division STRING,
  department STRING,
  class STRING,
  subclass STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### INVENTORY_BALANCE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_inventory_balance (
  inventory_balance_id STRING,
  store_id STRING,
  product_id STRING,
  inventory_date DATE,
  on_hand_qty INT,
  available_qty INT,
  allocated_qty INT,
  damaged_qty INT,
  last_update_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### INVENTORY_ADJUSTMENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_inventory_adjustment (
  adjustment_id STRING,
  store_id STRING,
  product_id STRING,
  adjustment_reason STRING,
  adjustment_qty INT,
  adjustment_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### INVENTORY_REPLENISHMENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_inventory_replenishment (
  replenishment_id STRING,
  store_id STRING,
  product_id STRING,
  requested_qty INT,
  replenished_qty INT,
  replenishment_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### RFID_EVENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_rfid_event (
  rfid_event_id STRING,
  store_id STRING,
  product_id STRING,
  scan_ts TIMESTAMP,
  total_on_hand INT,
  cycle_count_delta INT,
  store_available_on_hand INT,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### RFID_CYCLE_COUNT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_rfid_cycle_count (
  cycle_count_id STRING,
  store_id STRING,
  count_date DATE,
  completion_pct FLOAT,
  variance_pct FLOAT,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### SALES_TRANSACTION
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_sales_transaction (
  transaction_id STRING,
  athlete_id STRING,
  store_id STRING,
  transaction_ts TIMESTAMP,
  total_sales_amount FLOAT,
  sales_channel STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### SALES_TRANSACTION_LINE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_sales_transaction_line (
  transaction_line_id STRING,
  transaction_id STRING,
  product_id STRING,
  quantity INT,
  net_sale_price FLOAT,
  cost_amount FLOAT,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### FULFILLMENT_REQUEST
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_fulfillment_request (
  fulfillment_request_id STRING,
  athlete_id STRING,
  store_id STRING,
  request_type STRING,
  request_status STRING,
  created_ts TIMESTAMP,
  completed_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### FULFILLMENT_REQUEST_UNIT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_fulfillment_request_unit (
  fr_unit_id STRING,
  fulfillment_request_id STRING,
  product_id STRING,
  requested_qty INT,
  picked_qty INT,
  declined_qty INT,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### TASK
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_task (
  task_id STRING,
  task_type_cd STRING,
  store_id STRING,
  assigned_employee_id STRING,
  task_status STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### SEARCH_EVENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_search_event (
  search_event_id STRING,
  athlete_id STRING,
  store_id STRING,
  search_phrase STRING,
  results_count INT,
  search_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### PRODUCT_VIEW_EVENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_product_view_event (
  product_view_id STRING,
  athlete_id STRING,
  product_id STRING,
  finding_method STRING,
  event_ts TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### EMPLOYEE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_employee (
  employee_id STRING,
  store_id STRING,
  employee_role STRING,
  hire_date DATE,
  status STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### LABOR_TIMECARD
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_labor_timecard (
  timecard_id STRING,
  employee_id STRING,
  work_date DATE,
  scheduled_hours FLOAT,
  worked_hours FLOAT,
  overtime_hours FLOAT,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### SHIPMENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_shipment (
  shipment_id STRING,
  tc_shipment_id STRING,
  origin_store_id STRING,
  destination_store_id STRING,
  shipment_status STRING,
  shipment_type STRING,
  total_cost FLOAT,
  shipment_start_dttm TIMESTAMP,
  shipment_end_dttm TIMESTAMP,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### SHIPMENT_EVENT
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_shipment_event (
  shipment_event_id STRING,
  shipment_id STRING,
  event_type STRING,
  event_ts TIMESTAMP,
  location STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### AUDIT TABLE
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_audit (
  record_id STRING,
  source_table STRING,
  load_timestamp TIMESTAMP,
  processed_by STRING,
  processing_time FLOAT,
  status STRING
) USING DELTA;
```

---

## Conceptual Data Model Diagram (Tabular Form)

| Source Entity      | Relationship Key Field     | Target Entity      | Relationship Type |
|--------------------|---------------------------|--------------------|-------------------|
| Store              | region_id                 | Region             | Many-to-One       |
| District           | region_id                 | Region             | Many-to-One       |
| Store              | district_id               | District           | Many-to-One       |
| Athlete_Profile    | athlete_id                | Athlete            | Many-to-One       |
| Athlete_Profile    | preferred_store_id        | Store              | Many-to-One       |
| Product_Hierarchy  | product_id                | Product            | Many-to-One       |
| Inventory_Balance  | store_id                  | Store              | Many-to-One       |
| Inventory_Balance  | product_id                | Product            | Many-to-One       |
| Inventory_Adjustment| store_id                 | Store              | Many-to-One       |
| Inventory_Adjustment| product_id               | Product            | Many-to-One       |
| Inventory_Replenishment| store_id              | Store              | Many-to-One       |
| Inventory_Replenishment| product_id            | Product            | Many-to-One       |
| RFID_Event         | store_id                  | Store              | Many-to-One       |
| RFID_Event         | product_id                | Product            | Many-to-One       |
| RFID_Cycle_Count   | store_id                  | Store              | Many-to-One       |
| Sales_Transaction  | athlete_id                | Athlete            | Many-to-One       |
| Sales_Transaction  | store_id                  | Store              | Many-to-One       |
| Sales_Transaction_Line| transaction_id         | Sales_Transaction  | Many-to-One       |
| Sales_Transaction_Line| product_id             | Product            | Many-to-One       |
| Fulfillment_Request| athlete_id                | Athlete            | Many-to-One       |
| Fulfillment_Request| store_id                  | Store              | Many-to-One       |
| Fulfillment_Request_Unit| fulfillment_request_id| Fulfillment_Request| Many-to-One       |
| Fulfillment_Request_Unit| product_id           | Product            | Many-to-One       |
| Task               | store_id                  | Store              | Many-to-One       |
| Employee           | store_id                  | Store              | Many-to-One       |
| Labor_Timecard     | employee_id               | Employee           | Many-to-One       |
| Shipment           | origin_store_id           | Store              | Many-to-One       |
| Shipment           | destination_store_id      | Store              | Many-to-One       |
| Shipment_Event     | shipment_id               | Shipment           | Many-to-One       |
| Search_Event       | athlete_id                | Athlete            | Many-to-One       |
| Search_Event       | store_id                  | Store              | Many-to-One       |
| Product_View_Event | athlete_id                | Athlete            | Many-to-One       |
| Product_View_Event | product_id                | Product            | Many-to-One       |

---

## Assumptions & Design Decisions
- All tables are created as Delta tables in the bronze schema.
- Data types are chosen for compatibility with Databricks SQL and PySpark.
- No constraints (PK, FK, UNIQUE) are enforced at the Bronze layer.
- Metadata columns (load_timestamp, update_timestamp, source_system) are included in all tables for governance.
- Audit table tracks ingestion and processing lineage.
- Relationships are documented for downstream modeling but not enforced in Bronze.

---

## API Cost
apiCost: 0.000100

---

## Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Model_Physical

## Pipeline ID
12300
