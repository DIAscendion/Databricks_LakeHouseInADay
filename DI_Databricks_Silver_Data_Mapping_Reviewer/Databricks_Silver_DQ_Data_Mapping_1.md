_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Detailed data mapping from Bronze to Silver Layer for TMS Shipment Application, including cleansing, validations, and business rules.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Data Mapping

## 1. Overview
This document provides a comprehensive data mapping from the Bronze Layer to the Silver Layer in the Databricks Medallion architecture for the TMS Shipment application. It details attribute-level mappings, data cleansing, validation, and business rules to ensure high data quality, consistency, and readiness for analytics. The mapping covers all core tables, error data, and audit tables, and is designed for compatibility with PySpark and Databricks best practices.

## 2. Data Mapping for the Silver Layer

### 2.1 Main Shipment Table Mapping (bronze.bz_shipment → silver.sv_shipment)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|-------------|--------------|--------------|-------------|--------------|-----------------|---------------------|
| Silver | sv_shipment | id | - | - | - | Not null, Unique, Auto-increment | Generate surrogate key (monotonically_increasing_id in PySpark) |
| Silver | sv_shipment | SHIPMENT_ID | Bronze | bz_shipment | SHIPMENT_ID | Not null, Unique | Trim, uppercase |
| Silver | sv_shipment | TC_SHIPMENT_ID | Bronze | bz_shipment | TC_SHIPMENT_ID | Not null | Trim |
| Silver | sv_shipment | TC_COMPANY_ID | Bronze | bz_shipment | TC_COMPANY_ID | Not null | Trim |
| Silver | sv_shipment | EXT_SYS_SHIPMENT_ID | Bronze | bz_shipment | EXT_SYS_SHIPMENT_ID | Nullable | Trim |
| Silver | sv_shipment | SHIPMENT_REF_ID | Bronze | bz_shipment | SHIPMENT_REF_ID | Nullable | Trim |
| Silver | sv_shipment | REF_SHIPMENT_NBR | Bronze | bz_shipment | REF_SHIPMENT_NBR | Nullable | Trim |
| Silver | sv_shipment | PP_SHIPMENT_ID | Bronze | bz_shipment | PP_SHIPMENT_ID | Nullable | Trim |
| Silver | sv_shipment | SHIPMENT_STATUS | Bronze | bz_shipment | SHIPMENT_STATUS | Not null, Valid values (predefined list) | Uppercase, map to standard codes |
| Silver | sv_shipment | SHIPMENT_TYPE | Bronze | bz_shipment | SHIPMENT_TYPE | Not null, Valid values | Uppercase |
| Silver | sv_shipment | SHIPMENT_LEG_TYPE | Bronze | bz_shipment | SHIPMENT_LEG_TYPE | Nullable | Uppercase |
| Silver | sv_shipment | MOVE_TYPE | Bronze | bz_shipment | MOVE_TYPE | Nullable | Uppercase |
| Silver | sv_shipment | CREATION_TYPE | Bronze | bz_shipment | CREATION_TYPE | Nullable | Uppercase |
| Silver | sv_shipment | BUSINESS_PROCESS | Bronze | bz_shipment | BUSINESS_PROCESS | Nullable | Uppercase |
| Silver | sv_shipment | CREATED_DTTM | Bronze | bz_shipment | CREATED_DTTM | Not null, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | LAST_UPDATED_DTTM | Bronze | bz_shipment | LAST_UPDATED_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | SHIPMENT_START_DTTM | Bronze | bz_shipment | SHIPMENT_START_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | SHIPMENT_END_DTTM | Bronze | bz_shipment | SHIPMENT_END_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | SHIPMENT_RECON_DTTM | Bronze | bz_shipment | SHIPMENT_RECON_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | AVAILABLE_DTTM | Bronze | bz_shipment | AVAILABLE_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | RECEIVED_DTTM | Bronze | bz_shipment | RECEIVED_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | TENDER_DTTM | Bronze | bz_shipment | TENDER_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | SCHEDULED_PICKUP_DTTM | Bronze | bz_shipment | SCHEDULED_PICKUP_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | CREATED_SOURCE | Bronze | bz_shipment | CREATED_SOURCE | Nullable | Trim |
| Silver | sv_shipment | CREATED_SOURCE_TYPE | Bronze | bz_shipment | CREATED_SOURCE_TYPE | Nullable | Trim |
| Silver | sv_shipment | LAST_UPDATED_SOURCE | Bronze | bz_shipment | LAST_UPDATED_SOURCE | Nullable | Trim |
| Silver | sv_shipment | LAST_UPDATED_SOURCE_TYPE | Bronze | bz_shipment | LAST_UPDATED_SOURCE_TYPE | Nullable | Trim |
| Silver | sv_shipment | O_FACILITY_ID | Bronze | bz_shipment | O_FACILITY_ID | Nullable | Trim |
| Silver | sv_shipment | O_FACILITY_NUMBER | Bronze | bz_shipment | O_FACILITY_NUMBER | Nullable | Trim |
| Silver | sv_shipment | O_STOP_LOCATION_NAME | Bronze | bz_shipment | O_STOP_LOCATION_NAME | Nullable | Trim |
| Silver | sv_shipment | O_ADDRESS | Bronze | bz_shipment | O_ADDRESS | Nullable | Trim |
| Silver | sv_shipment | O_CITY | Bronze | bz_shipment | O_CITY | Nullable | Trim |
| Silver | sv_shipment | O_STATE_PROV | Bronze | bz_shipment | O_STATE_PROV | Nullable | Uppercase |
| Silver | sv_shipment | O_POSTAL_CODE | Bronze | bz_shipment | O_POSTAL_CODE | Nullable | Trim |
| Silver | sv_shipment | O_COUNTRY_CODE | Bronze | bz_shipment | O_COUNTRY_CODE | Nullable | Uppercase |
| Silver | sv_shipment | O_COUNTY | Bronze | bz_shipment | O_COUNTY | Nullable | Trim |
| Silver | sv_shipment | O_TANDEM_FACILITY | Bronze | bz_shipment | O_TANDEM_FACILITY | Nullable | Trim |
| Silver | sv_shipment | O_TANDEM_FACILITY_ALIAS | Bronze | bz_shipment | O_TANDEM_FACILITY_ALIAS | Nullable | Trim |
| Silver | sv_shipment | D_FACILITY_ID | Bronze | bz_shipment | D_FACILITY_ID | Nullable | Trim |
| Silver | sv_shipment | D_FACILITY_NUMBER | Bronze | bz_shipment | D_FACILITY_NUMBER | Nullable | Trim |
| Silver | sv_shipment | D_STOP_LOCATION_NAME | Bronze | bz_shipment | D_STOP_LOCATION_NAME | Nullable | Trim |
| Silver | sv_shipment | D_ADDRESS | Bronze | bz_shipment | D_ADDRESS | Nullable | Trim |
| Silver | sv_shipment | D_CITY | Bronze | bz_shipment | D_CITY | Nullable | Trim |
| Silver | sv_shipment | D_STATE_PROV | Bronze | bz_shipment | D_STATE_PROV | Nullable | Uppercase |
| Silver | sv_shipment | D_POSTAL_CODE | Bronze | bz_shipment | D_POSTAL_CODE | Nullable | Trim |
| Silver | sv_shipment | D_COUNTRY_CODE | Bronze | bz_shipment | D_COUNTRY_CODE | Nullable | Uppercase |
| Silver | sv_shipment | D_COUNTY | Bronze | bz_shipment | D_COUNTY | Nullable | Trim |
| Silver | sv_shipment | D_TANDEM_FACILITY | Bronze | bz_shipment | D_TANDEM_FACILITY | Nullable | Trim |
| Silver | sv_shipment | D_TANDEM_FACILITY_ALIAS | Bronze | bz_shipment | D_TANDEM_FACILITY_ALIAS | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_CARRIER_ID | Bronze | bz_shipment | ASSIGNED_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_CARRIER_CODE | Bronze | bz_shipment | ASSIGNED_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_SCNDR_CARRIER_ID | Bronze | bz_shipment | ASSIGNED_SCNDR_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_SCNDR_CARRIER_CODE | Bronze | bz_shipment | ASSIGNED_SCNDR_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_BROKER_CARRIER_ID | Bronze | bz_shipment | ASSIGNED_BROKER_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_BROKER_CARRIER_CODE | Bronze | bz_shipment | ASSIGNED_BROKER_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | DSG_CARRIER_ID | Bronze | bz_shipment | DSG_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | DSG_CARRIER_CODE | Bronze | bz_shipment | DSG_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | DSG_SCNDR_CARRIER_ID | Bronze | bz_shipment | DSG_SCNDR_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | DSG_SCNDR_CARRIER_CODE | Bronze | bz_shipment | DSG_SCNDR_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | FEASIBLE_CARRIER_ID | Bronze | bz_shipment | FEASIBLE_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | FEASIBLE_CARRIER_CODE | Bronze | bz_shipment | FEASIBLE_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | BROKER_CARRIER_ID | Bronze | bz_shipment | BROKER_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | SCNDR_CARRIER_ID | Bronze | bz_shipment | SCNDR_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | PAYEE_CARRIER_ID | Bronze | bz_shipment | PAYEE_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | LH_PAYEE_CARRIER_ID | Bronze | bz_shipment | LH_PAYEE_CARRIER_ID | Nullable | Trim |
| Silver | sv_shipment | LH_PAYEE_CARRIER_CODE | Bronze | bz_shipment | LH_PAYEE_CARRIER_CODE | Nullable | Trim |
| Silver | sv_shipment | HAULING_CARRIER | Bronze | bz_shipment | HAULING_CARRIER | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_EQUIPMENT_ID | Bronze | bz_shipment | ASSIGNED_EQUIPMENT_ID | Nullable | Trim |
| Silver | sv_shipment | DSG_EQUIPMENT_ID | Bronze | bz_shipment | DSG_EQUIPMENT_ID | Nullable | Trim |
| Silver | sv_shipment | FEASIBLE_EQUIPMENT_ID | Bronze | bz_shipment | FEASIBLE_EQUIPMENT_ID | Nullable | Trim |
| Silver | sv_shipment | FEASIBLE_EQUIPMENT2_ID | Bronze | bz_shipment | FEASIBLE_EQUIPMENT2_ID | Nullable | Trim |
| Silver | sv_shipment | EQUIPMENT_TYPE | Bronze | bz_shipment | EQUIPMENT_TYPE | Nullable | Uppercase |
| Silver | sv_shipment | ASSIGNED_MOT_ID | Bronze | bz_shipment | ASSIGNED_MOT_ID | Nullable | Trim |
| Silver | sv_shipment | DSG_MOT_ID | Bronze | bz_shipment | DSG_MOT_ID | Nullable | Trim |
| Silver | sv_shipment | FEASIBLE_MOT_ID | Bronze | bz_shipment | FEASIBLE_MOT_ID | Nullable | Trim |
| Silver | sv_shipment | TRAILER_NUMBER | Bronze | bz_shipment | TRAILER_NUMBER | Nullable | Trim |
| Silver | sv_shipment | TRACTOR_NUMBER | Bronze | bz_shipment | TRACTOR_NUMBER | Nullable | Trim |
| Silver | sv_shipment | TRLR_TYPE | Bronze | bz_shipment | TRLR_TYPE | Nullable | Uppercase |
| Silver | sv_shipment | TRLR_SIZE | Bronze | bz_shipment | TRLR_SIZE | Nullable | Uppercase |
| Silver | sv_shipment | TRLR_GEN_CODE | Bronze | bz_shipment | TRLR_GEN_CODE | Nullable | Uppercase |
| Silver | sv_shipment | DISTANCE | Bronze | bz_shipment | DISTANCE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | DIRECT_DISTANCE | Bronze | bz_shipment | DIRECT_DISTANCE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | OUT_OF_ROUTE_DISTANCE | Bronze | bz_shipment | OUT_OF_ROUTE_DISTANCE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | RADIAL_DISTANCE | Bronze | bz_shipment | RADIAL_DISTANCE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | DISTANCE_UOM | Bronze | bz_shipment | DISTANCE_UOM | Nullable | Uppercase |
| Silver | sv_shipment | RADIAL_DISTANCE_UOM | Bronze | bz_shipment | RADIAL_DISTANCE_UOM | Nullable | Uppercase |
| Silver | sv_shipment | NUM_STOPS | Bronze | bz_shipment | NUM_STOPS | Nullable, Integer | Cast to Integer |
| Silver | sv_shipment | NUM_CHARGE_LAYOVERS | Bronze | bz_shipment | NUM_CHARGE_LAYOVERS | Nullable, Integer | Cast to Integer |
| Silver | sv_shipment | NUM_DOCKS | Bronze | bz_shipment | NUM_DOCKS | Nullable, Integer | Cast to Integer |
| Silver | sv_shipment | PLANNED_WEIGHT | Bronze | bz_shipment | PLANNED_WEIGHT | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | PLANNED_VOLUME | Bronze | bz_shipment | PLANNED_VOLUME | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | FINANCIAL_WT | Bronze | bz_shipment | FINANCIAL_WT | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | LEFT_WT | Bronze | bz_shipment | LEFT_WT | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | RIGHT_WT | Bronze | bz_shipment | RIGHT_WT | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | ORDER_QTY | Bronze | bz_shipment | ORDER_QTY | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | QTY_UOM_ID | Bronze | bz_shipment | QTY_UOM_ID | Nullable | Uppercase |
| Silver | sv_shipment | WEIGHT_UOM_ID_BASE | Bronze | bz_shipment | WEIGHT_UOM_ID_BASE | Nullable | Uppercase |
| Silver | sv_shipment | VOLUME_UOM_ID_BASE | Bronze | bz_shipment | VOLUME_UOM_ID_BASE | Nullable | Uppercase |
| Silver | sv_shipment | SIZE1_VALUE | Bronze | bz_shipment | SIZE1_VALUE | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | SIZE1_UOM_ID | Bronze | bz_shipment | SIZE1_UOM_ID | Nullable | Uppercase |
| Silver | sv_shipment | SIZE2_VALUE | Bronze | bz_shipment | SIZE2_VALUE | Nullable, Numeric | Cast to Decimal(10,3) |
| Silver | sv_shipment | SIZE2_UOM_ID | Bronze | bz_shipment | SIZE2_UOM_ID | Nullable | Uppercase |
| Silver | sv_shipment | TOTAL_COST | Bronze | bz_shipment | TOTAL_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | ACTUAL_COST | Bronze | bz_shipment | ACTUAL_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | ESTIMATED_COST | Bronze | bz_shipment | ESTIMATED_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | BASELINE_COST | Bronze | bz_shipment | BASELINE_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | LINEHAUL_COST | Bronze | bz_shipment | LINEHAUL_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | ACCESSORIAL_COST | Bronze | bz_shipment | ACCESSORIAL_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | ACCESSORIAL_COST_TO_CARRIER | Bronze | bz_shipment | ACCESSORIAL_COST_TO_CARRIER | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | STOP_COST | Bronze | bz_shipment | STOP_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | SPOT_CHARGE | Bronze | bz_shipment | SPOT_CHARGE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | CARRIER_CHARGE | Bronze | bz_shipment | CARRIER_CHARGE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | CM_DISCOUNT | Bronze | bz_shipment | CM_DISCOUNT | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | TOTAL_COST_EXCL_TAX | Bronze | bz_shipment | TOTAL_COST_EXCL_TAX | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | TOTAL_REVENUE | Bronze | bz_shipment | TOTAL_REVENUE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | TOTAL_REVENUE_CURRENCY_CODE | Bronze | bz_shipment | TOTAL_REVENUE_CURRENCY_CODE | Nullable | Uppercase |
| Silver | sv_shipment | EARNED_INCOME | Bronze | bz_shipment | EARNED_INCOME | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | EARNED_INCOME_CURRENCY_CODE | Bronze | bz_shipment | EARNED_INCOME_CURRENCY_CODE | Nullable | Uppercase |
| Silver | sv_shipment | MARGIN | Bronze | bz_shipment | MARGIN | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | NORMALIZED_MARGIN | Bronze | bz_shipment | NORMALIZED_MARGIN | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | NORMALIZED_TOTAL_COST | Bronze | bz_shipment | NORMALIZED_TOTAL_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | NORMALIZED_TOTAL_REVENUE | Bronze | bz_shipment | NORMALIZED_TOTAL_REVENUE | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | NORMALIZED_BASELINE_COST | Bronze | bz_shipment | NORMALIZED_BASELINE_COST | Nullable, Numeric | Cast to Decimal(10,2) |
| Silver | sv_shipment | BILL_TO_CODE | Bronze | bz_shipment | BILL_TO_CODE | Nullable | Trim |
| Silver | sv_shipment | BILL_TO_NAME | Bronze | bz_shipment | BILL_TO_NAME | Nullable | Trim |
| Silver | sv_shipment | BILL_TO_ADDRESS | Bronze | bz_shipment | BILL_TO_ADDRESS | Nullable | Trim |
| Silver | sv_shipment | BILL_TO_CITY | Bronze | bz_shipment | BILL_TO_CITY | Nullable | Trim |
| Silver | sv_shipment | BILL_TO_STATE_PROV | Bronze | bz_shipment | BILL_TO_STATE_PROV | Nullable | Uppercase |
| Silver | sv_shipment | BILL_TO_POSTAL_CODE | Bronze | bz_shipment | BILL_TO_POSTAL_CODE | Nullable | Trim |
| Silver | sv_shipment | BILL_TO_COUNTRY_CODE | Bronze | bz_shipment | BILL_TO_COUNTRY_CODE | Nullable | Uppercase |
| Silver | sv_shipment | BILL_TO_PHONE_NUMBER | Bronze | bz_shipment | BILL_TO_PHONE_NUMBER | Nullable | Trim |
| Silver | sv_shipment | BILL_TO_TITLE | Bronze | bz_shipment | BILL_TO_TITLE | Nullable | Trim |
| Silver | sv_shipment | BILLING_METHOD | Bronze | bz_shipment | BILLING_METHOD | Nullable | Uppercase |
| Silver | sv_shipment | BILL_OF_LADING_NUMBER | Bronze | bz_shipment | BILL_OF_LADING_NUMBER | Nullable | Trim |
| Silver | sv_shipment | PRO_NUMBER | Bronze | bz_shipment | PRO_NUMBER | Nullable | Trim |
| Silver | sv_shipment | PURCHASE_ORDER | Bronze | bz_shipment | PURCHASE_ORDER | Nullable | Trim |
| Silver | sv_shipment | CONTRACT_NUMBER | Bronze | bz_shipment | CONTRACT_NUMBER | Nullable | Trim |
| Silver | sv_shipment | BUSINESS_PARTNER_ID | Bronze | bz_shipment | BUSINESS_PARTNER_ID | Nullable | Trim |
| Silver | sv_shipment | CUSTOMER_ID | Bronze | bz_shipment | CUSTOMER_ID | Nullable | Trim |
| Silver | sv_shipment | ASSIGNED_CUSTOMER_ID | Bronze | bz_shipment | ASSIGNED_CUSTOMER_ID | Nullable | Trim |
| Silver | sv_shipment | CUSTOMER_CREDIT_LIMIT_ID | Bronze | bz_shipment | CUSTOMER_CREDIT_LIMIT_ID | Nullable | Trim |
| Silver | sv_shipment | IS_SHIPMENT_CANCELLED | Bronze | bz_shipment | IS_SHIPMENT_CANCELLED | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | IS_SHIPMENT_RECONCILED | Bronze | bz_shipment | IS_SHIPMENT_RECONCILED | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | SHIPMENT_CLOSED_INDICATOR | Bronze | bz_shipment | SHIPMENT_CLOSED_INDICATOR | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | IS_MANUAL_ASSIGN | Bronze | bz_shipment | IS_MANUAL_ASSIGN | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | IS_HAZMAT | Bronze | bz_shipment | IS_HAZMAT | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | IS_PERISHABLE | Bronze | bz_shipment | IS_PERISHABLE | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | IS_BOOKING_REQUIRED | Bronze | bz_shipment | IS_BOOKING_REQUIRED | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | IS_AUTO_DELIVERED | Bronze | bz_shipment | IS_AUTO_DELIVERED | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | ON_TIME_INDICATOR | Bronze | bz_shipment | ON_TIME_INDICATOR | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | HAS_ALERTS | Bronze | bz_shipment | HAS_ALERTS | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | HAS_NOTES | Bronze | bz_shipment | HAS_NOTES | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | HAS_TRACKING_MSG | Bronze | bz_shipment | HAS_TRACKING_MSG | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | HAS_EM_NOTIFY_FLAG | Bronze | bz_shipment | HAS_EM_NOTIFY_FLAG | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | HAS_IMPORT_ERROR | Bronze | bz_shipment | HAS_IMPORT_ERROR | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | HAS_SOFT_CHECK_ERROR | Bronze | bz_shipment | HAS_SOFT_CHECK_ERROR | Nullable, Valid values (Y/N) | Uppercase, map to boolean |
| Silver | sv_shipment | PICKUP_START_DATE | Bronze | bz_shipment | PICKUP_START_DATE | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | PICKUP_END_DTTM | Bronze | bz_shipment | PICKUP_END_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | PICKUP_TZ | Bronze | bz_shipment | PICKUP_TZ | Nullable | Uppercase |
| Silver | sv_shipment | DELIVERY_START_DTTM | Bronze | bz_shipment | DELIVERY_START_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | DELIVERY_END_DTTM | Bronze | bz_shipment | DELIVERY_END_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | DELIVERY_TZ | Bronze | bz_shipment | DELIVERY_TZ | Nullable | Uppercase |
| Silver | sv_shipment | SCHEDULED_PICKUP_DTTM | Bronze | bz_shipment | SCHEDULED_PICKUP_DTTM | Nullable, Valid timestamp | Parse to timestamp |
| Silver | sv_shipment | PLN_MIN_TEMPERATURE | Bronze | bz_shipment | PLN_MIN_TEMPERATURE | Nullable, Numeric | Cast to Decimal(5,2) |
| Silver | sv_shipment | PLN_MAX_TEMPERATURE | Bronze | bz_shipment | PLN_MAX_TEMPERATURE | Nullable, Numeric | Cast to Decimal(5,2) |
| Silver | sv_shipment | TEMPERATURE_UOM | Bronze | bz_shipment | TEMPERATURE_UOM | Nullable | Uppercase |
| Silver | sv_shipment | AUTH_NBR | Bronze | bz_shipment | AUTH_NBR | Nullable | Trim |
| Silver | sv_shipment | BROKER_REF | Bronze | bz_shipment | BROKER_REF | Nullable | Trim |
| Silver | sv_shipment | SEAL_NUMBER | Bronze | bz_shipment | SEAL_NUMBER | Nullable | Trim |
| Silver | sv_shipment | DOOR | Bronze | bz_shipment | DOOR | Nullable | Trim |
| Silver | sv_shipment | WAVE_ID | Bronze | bz_shipment | WAVE_ID | Nullable | Trim |
| Silver | sv_shipment | MANIFEST_ID | Bronze | bz_shipment | MANIFEST_ID | Nullable | Trim |
| Silver | sv_shipment | BOOKING_ID | Bronze | bz_shipment | BOOKING_ID | Nullable | Trim |
| Silver | sv_shipment | CMID | Bronze | bz_shipment | CMID | Nullable | Trim |
| Silver | sv_shipment | load_date | Bronze | bz_shipment | load_timestamp | Not null | Rename, parse to timestamp |
| Silver | sv_shipment | update_date | Bronze | bz_shipment | update_timestamp | Nullable | Rename, parse to timestamp |
| Silver | sv_shipment | source_system | Bronze | bz_shipment | source_system | Not null | Trim |

#### Explanations for Complex Rules
- **Surrogate Key Generation**: The `id` field is generated using PySpark's `monotonically_increasing_id()` to ensure uniqueness.
- **Boolean Mapping**: Fields with Y/N values are mapped to boolean (True/False) in PySpark for downstream compatibility.
- **Data Type Conversions**: All numeric and timestamp fields are explicitly cast to their target types to ensure schema consistency.
- **Trimming and Uppercasing**: String fields are trimmed and uppercased where appropriate to standardize data.
- **Valid Value Checks**: For status and indicator fields, enforce allowed value lists (e.g., shipment status, Y/N flags).

### 2.2 Error Data Table Mapping (bronze.bz_audit → silver.sv_shipment_error)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|-------------|--------------|--------------|-------------|--------------|-----------------|---------------------|
| Silver | sv_shipment_error | error_id | - | - | - | Not null, Unique, Auto-increment | Generate surrogate key |
| Silver | sv_shipment_error | table_name | Bronze | bz_audit | source_table | Not null | Trim, uppercase |
| Silver | sv_shipment_error | record_id | Bronze | bz_audit | record_id | Not null | Trim |
| Silver | sv_shipment_error | error_type | Bronze | bz_audit | status | Not null | Map status to error type |
| Silver | sv_shipment_error | error_message | Bronze | bz_audit | error_message | Nullable | Trim |
| Silver | sv_shipment_error | error_timestamp | Bronze | bz_audit | audit_timestamp | Not null | Parse to timestamp |
| Silver | sv_shipment_error | layer | - | - | - | Not null | Set as 'Silver' |
| Silver | sv_shipment_error | load_date | Bronze | bz_audit | load_timestamp | Not null | Parse to timestamp |
| Silver | sv_shipment_error | update_date | Bronze | bz_audit | update_timestamp | Nullable | Parse to timestamp |
| Silver | sv_shipment_error | source_system | Bronze | bz_audit | audit_source | Not null | Trim |

### 2.3 Audit Table Mapping (bronze.bz_audit → silver.sv_audit)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|-------------|--------------|--------------|-------------|--------------|-----------------|---------------------|
| Silver | sv_audit | audit_id | - | - | - | Not null, Unique, Auto-increment | Generate surrogate key |
| Silver | sv_audit | pipeline_name | Bronze | bz_audit | source_table | Not null | Trim, uppercase |
| Silver | sv_audit | execution_id | Bronze | bz_audit | record_id | Not null | Trim |
| Silver | sv_audit | start_time | Bronze | bz_audit | load_timestamp | Not null | Parse to timestamp |
| Silver | sv_audit | end_time | Bronze | bz_audit | audit_timestamp | Not null | Parse to timestamp |
| Silver | sv_audit | status | Bronze | bz_audit | status | Not null | Uppercase |
| Silver | sv_audit | error_message | Bronze | bz_audit | error_message | Nullable | Trim |
| Silver | sv_audit | record_count | Bronze | bz_audit | record_count | Nullable, Numeric | Cast to BIGINT |
| Silver | sv_audit | load_date | Bronze | bz_audit | load_timestamp | Not null | Parse to timestamp |
| Silver | sv_audit | update_date | Bronze | bz_audit | update_timestamp | Nullable | Parse to timestamp |
| Silver | sv_audit | source_system | Bronze | bz_audit | audit_source | Not null | Trim |

## 3. Error Handling and Logging Recommendations
- All records failing validation rules (e.g., not null, invalid format) are redirected to the `sv_shipment_error` table with detailed error messages and context.
- Use structured logging in Databricks notebooks/jobs to capture transformation errors, validation failures, and processing statistics.
- Maintain audit trails for all data loads and transformations in the `sv_audit` table.
- Implement notification/alerting for critical errors or data quality issues.

## 4. API Cost
apiCost: 0.000000

---

[outputURL](https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping)

pipelineID: 12361
