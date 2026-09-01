_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Data mapping for Bronze layer ingestion of Store360 Inventory source tables, preserving original structure and metadata.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Data Mapping

## Summary
This document defines the data mapping between the DSG Stores transactional source schema and the Bronze layer in Databricks Lakehouse. The mapping ensures a one-to-one correspondence between source attributes and Bronze layer tables, preserving the raw structure and metadata for downstream processing.

---

## Data Mapping for Bronze Layer

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|--------------|-------------|--------------|--------------|-------------|--------------|---------------------|
| Bronze | REGION | region_id | Source | REGION | region_id | 1-1 Mapping |
| Bronze | REGION | region_name | Source | REGION | region_name | 1-1 Mapping |
| Bronze | REGION | vp_name | Source | REGION | vp_name | 1-1 Mapping |
| Bronze | REGION | is_active | Source | REGION | is_active | 1-1 Mapping |
| Bronze | REGION | created_ts | Source | REGION | created_ts | 1-1 Mapping |
| Bronze | REGION | updated_ts | Source | REGION | updated_ts | 1-1 Mapping |
| Bronze | DISTRICT | district_id | Source | DISTRICT | district_id | 1-1 Mapping |
| Bronze | DISTRICT | region_id | Source | DISTRICT | region_id | 1-1 Mapping |
| Bronze | DISTRICT | district_name | Source | DISTRICT | district_name | 1-1 Mapping |
| Bronze | DISTRICT | district_manager | Source | DISTRICT | district_manager | 1-1 Mapping |
| Bronze | DISTRICT | is_active | Source | DISTRICT | is_active | 1-1 Mapping |
| Bronze | DISTRICT | created_ts | Source | DISTRICT | created_ts | 1-1 Mapping |
| Bronze | DISTRICT | updated_ts | Source | DISTRICT | updated_ts | 1-1 Mapping |
| Bronze | STORE | store_id | Source | STORE | store_id | 1-1 Mapping |
| Bronze | STORE | store_number | Source | STORE | store_number | 1-1 Mapping |
| Bronze | STORE | store_name | Source | STORE | store_name | 1-1 Mapping |
| Bronze | STORE | district_id | Source | STORE | district_id | 1-1 Mapping |
| Bronze | STORE | fieldhouse_type | Source | STORE | fieldhouse_type | 1-1 Mapping |
| Bronze | STORE | open_date | Source | STORE | open_date | 1-1 Mapping |
| Bronze | STORE | close_date | Source | STORE | close_date | 1-1 Mapping |
| Bronze | STORE | address | Source | STORE | address | 1-1 Mapping |
| Bronze | STORE | city | Source | STORE | city | 1-1 Mapping |
| Bronze | STORE | state | Source | STORE | state | 1-1 Mapping |
| Bronze | STORE | postal_code | Source | STORE | postal_code | 1-1 Mapping |
| Bronze | STORE | is_active | Source | STORE | is_active | 1-1 Mapping |
| Bronze | STORE | created_ts | Source | STORE | created_ts | 1-1 Mapping |
| Bronze | STORE | updated_ts | Source | STORE | updated_ts | 1-1 Mapping |
| Bronze | ATHLETE | athlete_id | Source | ATHLETE | athlete_id | 1-1 Mapping |
| Bronze | ATHLETE | master_account_id | Source | ATHLETE | master_account_id | 1-1 Mapping |
| Bronze | ATHLETE | loyalty_flag | Source | ATHLETE | loyalty_flag | 1-1 Mapping |
| Bronze | ATHLETE | gold_flag | Source | ATHLETE | gold_flag | 1-1 Mapping |
| Bronze | ATHLETE | first_purchase_date | Source | ATHLETE | first_purchase_date | 1-1 Mapping |
| Bronze | ATHLETE | last_purchase_date | Source | ATHLETE | last_purchase_date | 1-1 Mapping |
| Bronze | ATHLETE | omni_channel_flag | Source | ATHLETE | omni_channel_flag | 1-1 Mapping |
| Bronze | ATHLETE | created_ts | Source | ATHLETE | created_ts | 1-1 Mapping |
| Bronze | ATHLETE | updated_ts | Source | ATHLETE | updated_ts | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | athlete_profile_id | Source | ATHLETE_PROFILE | athlete_profile_id | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | athlete_id | Source | ATHLETE_PROFILE | athlete_id | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | preferred_store_id | Source | ATHLETE_PROFILE | preferred_store_id | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | persona | Source | ATHLETE_PROFILE | persona | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | micro_cohort | Source | ATHLETE_PROFILE | micro_cohort | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | email | Source | ATHLETE_PROFILE | email | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | created_ts | Source | ATHLETE_PROFILE | created_ts | 1-1 Mapping |
| Bronze | ATHLETE_PROFILE | updated_ts | Source | ATHLETE_PROFILE | updated_ts | 1-1 Mapping |
| Bronze | PRODUCT | product_id | Source | PRODUCT | product_id | 1-1 Mapping |
| Bronze | PRODUCT | sku | Source | PRODUCT | sku | 1-1 Mapping |
| Bronze | PRODUCT | upc | Source | PRODUCT | upc | 1-1 Mapping |
| Bronze | PRODUCT | style_number | Source | PRODUCT | style_number | 1-1 Mapping |
| Bronze | PRODUCT | brand | Source | PRODUCT | brand | 1-1 Mapping |
| Bronze | PRODUCT | department_description | Source | PRODUCT | department_description | 1-1 Mapping |
| Bronze | PRODUCT | vendor_name | Source | PRODUCT | vendor_name | 1-1 Mapping |
| Bronze | PRODUCT | created_ts | Source | PRODUCT | created_ts | 1-1 Mapping |
| Bronze | PRODUCT | updated_ts | Source | PRODUCT | updated_ts | 1-1 Mapping |
| Bronze | PRODUCT_HIERARCHY | hierarchy_id | Source | PRODUCT_HIERARCHY | hierarchy_id | 1-1 Mapping |
| Bronze | PRODUCT_HIERARCHY | product_id | Source | PRODUCT_HIERARCHY | product_id | 1-1 Mapping |
| Bronze | PRODUCT_HIERARCHY | division | Source | PRODUCT_HIERARCHY | division | 1-1 Mapping |
| Bronze | PRODUCT_HIERARCHY | department | Source | PRODUCT_HIERARCHY | department | 1-1 Mapping |
| Bronze | PRODUCT_HIERARCHY | class | Source | PRODUCT_HIERARCHY | class | 1-1 Mapping |
| Bronze | PRODUCT_HIERARCHY | subclass | Source | PRODUCT_HIERARCHY | subclass | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | inventory_balance_id | Source | INVENTORY_BALANCE | inventory_balance_id | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | store_id | Source | INVENTORY_BALANCE | store_id | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | product_id | Source | INVENTORY_BALANCE | product_id | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | inventory_date | Source | INVENTORY_BALANCE | inventory_date | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | on_hand_qty | Source | INVENTORY_BALANCE | on_hand_qty | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | available_qty | Source | INVENTORY_BALANCE | available_qty | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | allocated_qty | Source | INVENTORY_BALANCE | allocated_qty | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | damaged_qty | Source | INVENTORY_BALANCE | damaged_qty | 1-1 Mapping |
| Bronze | INVENTORY_BALANCE | last_update_ts | Source | INVENTORY_BALANCE | last_update_ts | 1-1 Mapping |
| Bronze | INVENTORY_ADJUSTMENT | adjustment_id | Source | INVENTORY_ADJUSTMENT | adjustment_id | 1-1 Mapping |
| Bronze | INVENTORY_ADJUSTMENT | store_id | Source | INVENTORY_ADJUSTMENT | store_id | 1-1 Mapping |
| Bronze | INVENTORY_ADJUSTMENT | product_id | Source | INVENTORY_ADJUSTMENT | product_id | 1-1 Mapping |
| Bronze | INVENTORY_ADJUSTMENT | adjustment_reason | Source | INVENTORY_ADJUSTMENT | adjustment_reason | 1-1 Mapping |
| Bronze | INVENTORY_ADJUSTMENT | adjustment_qty | Source | INVENTORY_ADJUSTMENT | adjustment_qty | 1-1 Mapping |
| Bronze | INVENTORY_ADJUSTMENT | adjustment_ts | Source | INVENTORY_ADJUSTMENT | adjustment_ts | 1-1 Mapping |
| Bronze | INVENTORY_REPLENISHMENT | replenishment_id | Source | INVENTORY_REPLENISHMENT | replenishment_id | 1-1 Mapping |
| Bronze | INVENTORY_REPLENISHMENT | store_id | Source | INVENTORY_REPLENISHMENT | store_id | 1-1 Mapping |
| Bronze | INVENTORY_REPLENISHMENT | product_id | Source | INVENTORY_REPLENISHMENT | product_id | 1-1 Mapping |
| Bronze | INVENTORY_REPLENISHMENT | requested_qty | Source | INVENTORY_REPLENISHMENT | requested_qty | 1-1 Mapping |
| Bronze | INVENTORY_REPLENISHMENT | replenished_qty | Source | INVENTORY_REPLENISHMENT | replenished_qty | 1-1 Mapping |
| Bronze | INVENTORY_REPLENISHMENT | replenishment_ts | Source | INVENTORY_REPLENISHMENT | replenishment_ts | 1-1 Mapping |
| Bronze | RFID_EVENT | rfid_event_id | Source | RFID_EVENT | rfid_event_id | 1-1 Mapping |
| Bronze | RFID_EVENT | store_id | Source | RFID_EVENT | store_id | 1-1 Mapping |
| Bronze | RFID_EVENT | product_id | Source | RFID_EVENT | product_id | 1-1 Mapping |
| Bronze | RFID_EVENT | scan_ts | Source | RFID_EVENT | scan_ts | 1-1 Mapping |
| Bronze | RFID_EVENT | total_on_hand | Source | RFID_EVENT | total_on_hand | 1-1 Mapping |
| Bronze | RFID_EVENT | cycle_count_delta | Source | RFID_EVENT | cycle_count_delta | 1-1 Mapping |
| Bronze | RFID_EVENT | store_available_on_hand | Source | RFID_EVENT | store_available_on_hand | 1-1 Mapping |
| Bronze | RFID_CYCLE_COUNT | cycle_count_id | Source | RFID_CYCLE_COUNT | cycle_count_id | 1-1 Mapping |
| Bronze | RFID_CYCLE_COUNT | store_id | Source | RFID_CYCLE_COUNT | store_id | 1-1 Mapping |
| Bronze | RFID_CYCLE_COUNT | count_date | Source | RFID_CYCLE_COUNT | count_date | 1-1 Mapping |
| Bronze | RFID_CYCLE_COUNT | completion_pct | Source | RFID_CYCLE_COUNT | completion_pct | 1-1 Mapping |
| Bronze | RFID_CYCLE_COUNT | variance_pct | Source | RFID_CYCLE_COUNT | variance_pct | 1-1 Mapping |
| Bronze | SALES_TRANSACTION | transaction_id | Source | SALES_TRANSACTION | transaction_id | 1-1 Mapping |
| Bronze | SALES_TRANSACTION | athlete_id | Source | SALES_TRANSACTION | athlete_id | 1-1 Mapping |
| Bronze | SALES_TRANSACTION | store_id | Source | SALES_TRANSACTION | store_id | 1-1 Mapping |
| Bronze | SALES_TRANSACTION | transaction_ts | Source | SALES_TRANSACTION | transaction_ts | 1-1 Mapping |
| Bronze | SALES_TRANSACTION | total_sales_amount | Source | SALES_TRANSACTION | total_sales_amount | 1-1 Mapping |
| Bronze | SALES_TRANSACTION | sales_channel | Source | SALES_TRANSACTION | sales_channel | 1-1 Mapping |
| Bronze | SALES_TRANSACTION_LINE | transaction_line_id | Source | SALES_TRANSACTION_LINE | transaction_line_id | 1-1 Mapping |
| Bronze | SALES_TRANSACTION_LINE | transaction_id | Source | SALES_TRANSACTION_LINE | transaction_id | 1-1 Mapping |
| Bronze | SALES_TRANSACTION_LINE | product_id | Source | SALES_TRANSACTION_LINE | product_id | 1-1 Mapping |
| Bronze | SALES_TRANSACTION_LINE | quantity | Source | SALES_TRANSACTION_LINE | quantity | 1-1 Mapping |
| Bronze | SALES_TRANSACTION_LINE | net_sale_price | Source | SALES_TRANSACTION_LINE | net_sale_price | 1-1 Mapping |
| Bronze | SALES_TRANSACTION_LINE | cost_amount | Source | SALES_TRANSACTION_LINE | cost_amount | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | fulfillment_request_id | Source | FULFILLMENT_REQUEST | fulfillment_request_id | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | athlete_id | Source | FULFILLMENT_REQUEST | athlete_id | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | store_id | Source | FULFILLMENT_REQUEST | store_id | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | request_type | Source | FULFILLMENT_REQUEST | request_type | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | request_status | Source | FULFILLMENT_REQUEST | request_status | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | created_ts | Source | FULFILLMENT_REQUEST | created_ts | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST | completed_ts | Source | FULFILLMENT_REQUEST | completed_ts | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST_UNIT | fr_unit_id | Source | FULFILLMENT_REQUEST_UNIT | fr_unit_id | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST_UNIT | fulfillment_request_id | Source | FULFILLMENT_REQUEST_UNIT | fulfillment_request_id | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST_UNIT | product_id | Source | FULFILLMENT_REQUEST_UNIT | product_id | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST_UNIT | requested_qty | Source | FULFILLMENT_REQUEST_UNIT | requested_qty | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST_UNIT | picked_qty | Source | FULFILLMENT_REQUEST_UNIT | picked_qty | 1-1 Mapping |
| Bronze | FULFILLMENT_REQUEST_UNIT | declined_qty | Source | FULFILLMENT_REQUEST_UNIT | declined_qty | 1-1 Mapping |
| Bronze | TASK | task_id | Source | TASK | task_id | 1-1 Mapping |
| Bronze | TASK | task_type_cd | Source | TASK | task_type_cd | 1-1 Mapping |
| Bronze | TASK | store_id | Source | TASK | store_id | 1-1 Mapping |
| Bronze | TASK | assigned_employee_id | Source | TASK | assigned_employee_id | 1-1 Mapping |
| Bronze | TASK | task_status | Source | TASK | task_status | 1-1 Mapping |
| Bronze | SEARCH_EVENT | search_event_id | Source | SEARCH_EVENT | search_event_id | 1-1 Mapping |
| Bronze | SEARCH_EVENT | athlete_id | Source | SEARCH_EVENT | athlete_id | 1-1 Mapping |
| Bronze | SEARCH_EVENT | store_id | Source | SEARCH_EVENT | store_id | 1-1 Mapping |
| Bronze | SEARCH_EVENT | search_phrase | Source | SEARCH_EVENT | search_phrase | 1-1 Mapping |
| Bronze | SEARCH_EVENT | results_count | Source | SEARCH_EVENT | results_count | 1-1 Mapping |
| Bronze | SEARCH_EVENT | search_ts | Source | SEARCH_EVENT | search_ts | 1-1 Mapping |
| Bronze | PRODUCT_VIEW_EVENT | product_view_id | Source | PRODUCT_VIEW_EVENT | product_view_id | 1-1 Mapping |
| Bronze | PRODUCT_VIEW_EVENT | athlete_id | Source | PRODUCT_VIEW_EVENT | athlete_id | 1-1 Mapping |
| Bronze | PRODUCT_VIEW_EVENT | product_id | Source | PRODUCT_VIEW_EVENT | product_id | 1-1 Mapping |
| Bronze | PRODUCT_VIEW_EVENT | finding_method | Source | PRODUCT_VIEW_EVENT | finding_method | 1-1 Mapping |
| Bronze | PRODUCT_VIEW_EVENT | event_ts | Source | PRODUCT_VIEW_EVENT | event_ts | 1-1 Mapping |
| Bronze | EMPLOYEE | employee_id | Source | EMPLOYEE | employee_id | 1-1 Mapping |
| Bronze | EMPLOYEE | store_id | Source | EMPLOYEE | store_id | 1-1 Mapping |
| Bronze | EMPLOYEE | employee_role | Source | EMPLOYEE | employee_role | 1-1 Mapping |
| Bronze | EMPLOYEE | hire_date | Source | EMPLOYEE | hire_date | 1-1 Mapping |
| Bronze | EMPLOYEE | status | Source | EMPLOYEE | status | 1-1 Mapping |
| Bronze | LABOR_TIMECARD | timecard_id | Source | LABOR_TIMECARD | timecard_id | 1-1 Mapping |
| Bronze | LABOR_TIMECARD | employee_id | Source | LABOR_TIMECARD | employee_id | 1-1 Mapping |
| Bronze | LABOR_TIMECARD | work_date | Source | LABOR_TIMECARD | work_date | 1-1 Mapping |
| Bronze | LABOR_TIMECARD | scheduled_hours | Source | LABOR_TIMECARD | scheduled_hours | 1-1 Mapping |
| Bronze | LABOR_TIMECARD | worked_hours | Source | LABOR_TIMECARD | worked_hours | 1-1 Mapping |
| Bronze | LABOR_TIMECARD | overtime_hours | Source | LABOR_TIMECARD | overtime_hours | 1-1 Mapping |
| Bronze | SHIPMENT | shipment_id | Source | SHIPMENT | shipment_id | 1-1 Mapping |
| Bronze | SHIPMENT | tc_shipment_id | Source | SHIPMENT | tc_shipment_id | 1-1 Mapping |
| Bronze | SHIPMENT | origin_store_id | Source | SHIPMENT | origin_store_id | 1-1 Mapping |
| Bronze | SHIPMENT | destination_store_id | Source | SHIPMENT | destination_store_id | 1-1 Mapping |
| Bronze | SHIPMENT | shipment_status | Source | SHIPMENT | shipment_status | 1-1 Mapping |
| Bronze | SHIPMENT | shipment_type | Source | SHIPMENT | shipment_type | 1-1 Mapping |
| Bronze | SHIPMENT | total_cost | Source | SHIPMENT | total_cost | 1-1 Mapping |
| Bronze | SHIPMENT | shipment_start_dttm | Source | SHIPMENT | shipment_start_dttm | 1-1 Mapping |
| Bronze | SHIPMENT | shipment_end_dttm | Source | SHIPMENT | shipment_end_dttm | 1-1 Mapping |
| Bronze | SHIPMENT_EVENT | shipment_event_id | Source | SHIPMENT_EVENT | shipment_event_id | 1-1 Mapping |
| Bronze | SHIPMENT_EVENT | shipment_id | Source | SHIPMENT_EVENT | shipment_id | 1-1 Mapping |
| Bronze | SHIPMENT_EVENT | event_type | Source | SHIPMENT_EVENT | event_type | 1-1 Mapping |
| Bronze | SHIPMENT_EVENT | event_ts | Source | SHIPMENT_EVENT | event_ts | 1-1 Mapping |
| Bronze | SHIPMENT_EVENT | location | Source | SHIPMENT_EVENT | location | 1-1 Mapping |

---

## Data Type Assignments
All fields are ingested as their native types from the source system. Databricks Delta Lake and PySpark compatible types are used (e.g., string, integer, timestamp, float).

---

## Assumptions
- All source tables and fields are mapped directly to Bronze layer tables and fields with no transformation.
- Data types are inferred from source system and mapped to compatible Delta Lake types.
- No business rules, cleansing, or validation applied at Bronze layer.

---

## API Cost Reporting
apiCost: 0.01 // Cost consumed by the API for this call (in USD)

---

## Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Model_Data_Mapping

## Pipeline ID
12301
