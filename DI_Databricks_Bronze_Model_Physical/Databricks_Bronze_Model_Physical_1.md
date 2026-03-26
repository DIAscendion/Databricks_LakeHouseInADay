_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Bronze Layer Physical Data Model for TMS Shipment Application
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze Layer Physical Data Model

## 1. Overview

This document defines the physical data model for the Bronze layer in the Medallion architecture for the TMS (Transportation Management System) Shipment application. The Bronze layer stores raw data as-is from source systems with minimal transformation, adding metadata columns for data governance and lineage tracking.

## 2. Design Principles

- **Raw Data Preservation**: Store data exactly as received from source systems
- **Delta Lake Format**: All tables use Delta Lake for ACID transactions and time travel
- **Metadata Enrichment**: Add governance columns for tracking data lineage
- **Schema Evolution**: Support schema changes without breaking downstream processes
- **No Constraints**: Bronze layer does not enforce primary keys, foreign keys, or constraints

## 3. Bronze Layer DDL Scripts

### 3.1 Main Shipment Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_shipment (
  -- Core Shipment Identifiers
  SHIPMENT_ID STRING,
  TC_SHIPMENT_ID STRING,
  TC_COMPANY_ID STRING,
  EXT_SYS_SHIPMENT_ID STRING,
  SHIPMENT_REF_ID STRING,
  REF_SHIPMENT_NBR STRING,
  PP_SHIPMENT_ID STRING,
  
  -- Shipment Status and Type
  SHIPMENT_STATUS STRING,
  SHIPMENT_TYPE STRING,
  SHIPMENT_LEG_TYPE STRING,
  MOVE_TYPE STRING,
  CREATION_TYPE STRING,
  BUSINESS_PROCESS STRING,
  
  -- Dates and Times
  CREATED_DTTM TIMESTAMP,
  LAST_UPDATED_DTTM TIMESTAMP,
  SHIPMENT_START_DTTM TIMESTAMP,
  SHIPMENT_END_DTTM TIMESTAMP,
  SHIPMENT_RECON_DTTM TIMESTAMP,
  AVAILABLE_DTTM TIMESTAMP,
  RECEIVED_DTTM TIMESTAMP,
  TENDER_DTTM TIMESTAMP,
  SCHEDULED_PICKUP_DTTM TIMESTAMP,
  
  -- Creation and Update Tracking
  CREATED_SOURCE STRING,
  CREATED_SOURCE_TYPE STRING,
  LAST_UPDATED_SOURCE STRING,
  LAST_UPDATED_SOURCE_TYPE STRING,
  
  -- Origin Facility Information
  O_FACILITY_ID STRING,
  O_FACILITY_NUMBER STRING,
  O_STOP_LOCATION_NAME STRING,
  O_ADDRESS STRING,
  O_CITY STRING,
  O_STATE_PROV STRING,
  O_POSTAL_CODE STRING,
  O_COUNTRY_CODE STRING,
  O_COUNTY STRING,
  O_TANDEM_FACILITY STRING,
  O_TANDEM_FACILITY_ALIAS STRING,
  
  -- Destination Facility Information
  D_FACILITY_ID STRING,
  D_FACILITY_NUMBER STRING,
  D_STOP_LOCATION_NAME STRING,
  D_ADDRESS STRING,
  D_CITY STRING,
  D_STATE_PROV STRING,
  D_POSTAL_CODE STRING,
  D_COUNTRY_CODE STRING,
  D_COUNTY STRING,
  D_TANDEM_FACILITY STRING,
  D_TANDEM_FACILITY_ALIAS STRING,
  
  -- Carrier Information
  ASSIGNED_CARRIER_ID STRING,
  ASSIGNED_CARRIER_CODE STRING,
  ASSIGNED_SCNDR_CARRIER_ID STRING,
  ASSIGNED_SCNDR_CARRIER_CODE STRING,
  ASSIGNED_BROKER_CARRIER_ID STRING,
  ASSIGNED_BROKER_CARRIER_CODE STRING,
  DSG_CARRIER_ID STRING,
  DSG_CARRIER_CODE STRING,
  DSG_SCNDR_CARRIER_ID STRING,
  DSG_SCNDR_CARRIER_CODE STRING,
  FEASIBLE_CARRIER_ID STRING,
  FEASIBLE_CARRIER_CODE STRING,
  BROKER_CARRIER_ID STRING,
  SCNDR_CARRIER_ID STRING,
  PAYEE_CARRIER_ID STRING,
  LH_PAYEE_CARRIER_ID STRING,
  LH_PAYEE_CARRIER_CODE STRING,
  HAULING_CARRIER STRING,
  
  -- Equipment and Transport
  ASSIGNED_EQUIPMENT_ID STRING,
  DSG_EQUIPMENT_ID STRING,
  FEASIBLE_EQUIPMENT_ID STRING,
  FEASIBLE_EQUIPMENT2_ID STRING,
  EQUIPMENT_TYPE STRING,
  ASSIGNED_MOT_ID STRING,
  DSG_MOT_ID STRING,
  FEASIBLE_MOT_ID STRING,
  TRAILER_NUMBER STRING,
  TRACTOR_NUMBER STRING,
  TRLR_TYPE STRING,
  TRLR_SIZE STRING,
  TRLR_GEN_CODE STRING,
  
  -- Distance and Route Information
  DISTANCE DECIMAL(10,2),
  DIRECT_DISTANCE DECIMAL(10,2),
  OUT_OF_ROUTE_DISTANCE DECIMAL(10,2),
  RADIAL_DISTANCE DECIMAL(10,2),
  DISTANCE_UOM STRING,
  RADIAL_DISTANCE_UOM STRING,
  NUM_STOPS INT,
  NUM_CHARGE_LAYOVERS INT,
  NUM_DOCKS INT,
  
  -- Weight and Volume
  PLANNED_WEIGHT DECIMAL(10,3),
  PLANNED_VOLUME DECIMAL(10,3),
  FINANCIAL_WT DECIMAL(10,3),
  LEFT_WT DECIMAL(10,3),
  RIGHT_WT DECIMAL(10,3),
  ORDER_QTY DECIMAL(10,3),
  QTY_UOM_ID STRING,
  WEIGHT_UOM_ID_BASE STRING,
  VOLUME_UOM_ID_BASE STRING,
  
  -- Dimensions
  SIZE1_VALUE DECIMAL(10,3),
  SIZE1_UOM_ID STRING,
  SIZE2_VALUE DECIMAL(10,3),
  SIZE2_UOM_ID STRING,
  
  -- Cost Information
  TOTAL_COST DECIMAL(10,2),
  ACTUAL_COST DECIMAL(10,2),
  ESTIMATED_COST DECIMAL(10,2),
  BASELINE_COST DECIMAL(10,2),
  LINEHAUL_COST DECIMAL(10,2),
  ACCESSORIAL_COST DECIMAL(10,2),
  ACCESSORIAL_COST_TO_CARRIER DECIMAL(10,2),
  STOP_COST DECIMAL(10,2),
  SPOT_CHARGE DECIMAL(10,2),
  CARRIER_CHARGE DECIMAL(10,2),
  CUST_FRGT_CHARGE DECIMAL(10,2),
  CM_DISCOUNT DECIMAL(10,2),
  TOTAL_COST_EXCL_TAX DECIMAL(10,2),
  TOTAL_TAX_AMOUNT DECIMAL(10,2),
  
  -- Planned Cost Information
  PLN_TOTAL_COST DECIMAL(10,2),
  PLN_LINEHAUL_COST DECIMAL(10,2),
  PLN_TOTAL_ACCESSORIAL_COST DECIMAL(10,2),
  PLN_ACCESSORL_COST_TO_CARRIER DECIMAL(10,2),
  PLN_STOP_OFF_COST DECIMAL(10,2),
  PLN_CARRIER_CHARGE DECIMAL(10,2),
  PLN_NORMALIZED_TOTAL_COST DECIMAL(10,2),
  
  -- Budget Cost Information
  BUDG_TOTAL_COST DECIMAL(10,2),
  BUDG_NORMALIZED_TOTAL_COST DECIMAL(10,2),
  BUDG_CM_DISCOUNT DECIMAL(10,2),
  ORIG_BUDG_TOTAL_COST DECIMAL(10,2),
  
  -- Recommended Cost Information
  REC_TOTAL_COST DECIMAL(10,2),
  REC_LINEHAUL_COST DECIMAL(10,2),
  REC_ACCESSORIAL_COST DECIMAL(10,2),
  REC_STOP_COST DECIMAL(10,2),
  REC_SPOT_CHARGE DECIMAL(10,2),
  REC_CM_DISCOUNT DECIMAL(10,2),
  REC_NORMALIZED_TOTAL_COST DECIMAL(10,2),
  REC_MARGIN DECIMAL(10,2),
  REC_NORMALIZED_MARGIN DECIMAL(10,2),
  
  -- Revenue Information
  TOTAL_REVENUE DECIMAL(10,2),
  EARNED_INCOME DECIMAL(10,2),
  NORMALIZED_TOTAL_REVENUE DECIMAL(10,2),
  FRT_REV_LINEHAUL_CHARGE DECIMAL(10,2),
  FRT_REV_ACCESSORIAL_CHARGE DECIMAL(10,2),
  FRT_REV_STOP_CHARGE DECIMAL(10,2),
  FRT_REV_SPOT_CHARGE DECIMAL(10,2),
  FRT_REV_CM_DISCOUNT DECIMAL(10,2),
  
  -- Currency Codes
  CURRENCY_CODE STRING,
  ACTUAL_COST_CURRENCY_CODE STRING,
  BASELINE_COST_CURRENCY_CODE STRING,
  PLN_CURRENCY_CODE STRING,
  BUDG_CURRENCY_CODE STRING,
  REC_CURRENCY_CODE STRING,
  TOTAL_REVENUE_CURRENCY_CODE STRING,
  EARNED_INCOME_CURRENCY_CODE STRING,
  SPOT_CHARGE_CURRENCY_CODE STRING,
  FRT_REV_SPOT_CHARGE_CURR_CODE STRING,
  COD_CURRENCY_CODE STRING,
  DV_CURRENCY_CODE STRING,
  MV_CURRENCY_CODE STRING,
  
  -- Billing Information
  BILL_TO_CODE STRING,
  BILL_TO_NAME STRING,
  BILL_TO_ADDRESS STRING,
  BILL_TO_CITY STRING,
  BILL_TO_STATE_PROV STRING,
  BILL_TO_POSTAL_CODE STRING,
  BILL_TO_COUNTRY_CODE STRING,
  BILL_TO_PHONE_NUMBER STRING,
  BILL_TO_TITLE STRING,
  BILLING_METHOD STRING,
  BILL_OF_LADING_NUMBER STRING,
  PURCHASE_ORDER STRING,
  PRO_NUMBER STRING,
  
  -- Service and Lane Information
  ASSIGNED_SERVICE_LEVEL_ID STRING,
  DSG_SERVICE_LEVEL_ID STRING,
  FEASIBLE_SERVICE_LEVEL_ID STRING,
  REC_SERVICE_LEVEL_ID STRING,
  ASSIGNED_LANE_ID STRING,
  ASSIGNED_LANE_DETAIL_ID STRING,
  RATING_LANE_ID STRING,
  RATING_LANE_DETAIL_ID STRING,
  PLN_RATING_LANE_ID STRING,
  PLN_RATING_LANE_DETAIL_ID STRING,
  FRT_REV_RATING_LANE_ID STRING,
  FRT_REV_RATING_LANE_DETAIL_ID STRING,
  REC_LANE_ID STRING,
  REC_LANE_DETAIL_ID STRING,
  REC_RATING_LANE_ID STRING,
  REC_RATING_LANE_DETAIL_ID STRING,
  LANE_NAME STRING,
  
  -- Timing Information
  PICKUP_START_DATE TIMESTAMP,
  PICKUP_END_DTTM TIMESTAMP,
  PICKUP_TZ STRING,
  DELIVERY_START_DTTM TIMESTAMP,
  DELIVERY_END_DTTM TIMESTAMP,
  DELIVERY_TZ STRING,
  DAYS_TO_DELIVER INT,
  TOTAL_TIME DECIMAL(10,2),
  
  -- Temperature Control
  PLN_MIN_TEMPERATURE DECIMAL(5,2),
  PLN_MAX_TEMPERATURE DECIMAL(5,2),
  TEMPERATURE_UOM STRING,
  
  -- Flags and Indicators
  IS_SHIPMENT_CANCELLED STRING,
  IS_SHIPMENT_RECONCILED STRING,
  IS_HAZMAT STRING,
  IS_PERISHABLE STRING,
  IS_MANUAL_ASSIGN STRING,
  IS_MISROUTED STRING,
  IS_AUTO_DELIVERED STRING,
  IS_BOOKING_REQUIRED STRING,
  IS_FILO STRING,
  IS_COOLER_AT_NOSE STRING,
  HAS_ALERTS STRING,
  HAS_NOTES STRING,
  HAS_TRACKING_MSG STRING,
  HAS_EM_NOTIFY_FLAG STRING,
  HAS_IMPORT_ERROR STRING,
  HAS_SOFT_CHECK_ERROR STRING,
  SHIPMENT_CLOSED_INDICATOR STRING,
  PRINT_CONS_BOL STRING,
  SED_GENERATED_FLAG STRING,
  
  -- Route and Equipment Details
  RTE_TYPE STRING,
  RTE_TYPE_1 STRING,
  RTE_TYPE_2 STRING,
  RTE_TO STRING,
  RTE_SWC_NBR STRING,
  STATIC_ROUTE_ID STRING,
  ASSIGNED_SHIP_VIA STRING,
  DROPOFF_PICKUP STRING,
  LOADING_SEQ_ORD INT,
  DOOR STRING,
  SEAL_NUMBER STRING,
  
  -- Business Partner and Customer
  BUSINESS_PARTNER_ID STRING,
  CUSTOMER_ID STRING,
  ASSIGNED_CUSTOMER_ID STRING,
  
  -- Additional Cost and Charge Fields
  COD_AMOUNT DECIMAL(10,2),
  DECLARED_VALUE DECIMAL(10,2),
  MONETARY_VALUE DECIMAL(10,2),
  MARGIN DECIMAL(10,2),
  NORMALIZED_MARGIN DECIMAL(10,2),
  NORMALIZED_BASELINE_COST DECIMAL(10,2),
  NORMALIZED_TOTAL_COST DECIMAL(10,2),
  ESTIMATED_SAVINGS DECIMAL(10,2),
  REPORTED_COST DECIMAL(10,2),
  MIN_RATE DECIMAL(10,2),
  RATE DECIMAL(10,4),
  RATE_TYPE STRING,
  RATE_UOM STRING,
  
  -- Optimization and Management
  CMID STRING,
  ASSIGNED_CM_SHIPMENT_ID STRING,
  REC_CM_SHIPMENT_ID STRING,
  REC_CMID STRING,
  CONFIG_CYCLE_SEQ INT,
  CYCLE_DEADLINE_DTTM TIMESTAMP,
  CYCLE_EXECUTION_DTTM TIMESTAMP,
  
  -- Booking Information
  BOOKING_ID STRING,
  BOOKING_REF_CARRIER STRING,
  BOOKING_REF_SHIPPER STRING,
  DSG_VOYAGE_FLIGHT STRING,
  FEASIBLE_VOYAGE_FLIGHT STRING,
  
  -- Warehouse Integration
  SENT_TO_PKMS STRING,
  SENT_TO_PKMS_DTTM TIMESTAMP,
  SENT_TO_CREATE_PKMS STRING,
  SENT_TO_CREATE_PKMS_DTTM TIMESTAMP,
  FIRST_UPDATE_SENT_TO_PKMS STRING,
  WMS_STATUS_CODE STRING,
  
  -- Additional Fields
  COMMODITY_CLASS STRING,
  COMMODITY_CODE_ID STRING,
  PACKAGING STRING,
  TARIFF STRING,
  CONTRACT_NUMBER STRING,
  AUTH_NBR STRING,
  BROKER_REF STRING,
  REGION_ID STRING,
  INBOUND_REGION_ID STRING,
  OUTBOUND_REGION_ID STRING,
  HUB_ID STRING,
  WAVE_ID STRING,
  SHIP_GROUP_ID STRING,
  MANIFEST_ID STRING,
  
  -- System and Technical Fields
  HIBERNATE_VERSION INT,
  EXTRACTION_DTTM TIMESTAMP,
  CURRENCY_DTTM TIMESTAMP,
  
  -- Metadata columns for Bronze layer
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) 
USING DELTA
LOCATION '/mnt/bronze/shipment'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3.2 Audit Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_audit (
  record_id STRING,
  source_table STRING,
  load_timestamp TIMESTAMP,
  processed_by STRING,
  processing_time DECIMAL(10,3),
  status STRING,
  error_message STRING,
  record_count BIGINT,
  file_path STRING,
  file_size BIGINT,
  
  -- Metadata columns
  audit_load_timestamp TIMESTAMP,
  audit_update_timestamp TIMESTAMP,
  audit_source_system STRING
)
USING DELTA
LOCATION '/mnt/bronze/audit'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

## 4. Conceptual Data Model Diagram (Tabular Form)

| Source Entity | Relationship Key Field | Target Entity | Relationship Type | Description |
|---------------|------------------------|---------------|-------------------|-------------|
| bz_shipment | SHIPMENT_ID | bz_audit | One-to-Many | Each shipment can have multiple audit records |
| bz_shipment | ASSIGNED_CARRIER_ID | Carrier (External) | Many-to-One | Shipment assigned to primary carrier |
| bz_shipment | ASSIGNED_SCNDR_CARRIER_ID | Carrier (External) | Many-to-One | Shipment assigned to secondary carrier |
| bz_shipment | ASSIGNED_BROKER_CARRIER_ID | Carrier (External) | Many-to-One | Shipment assigned to broker carrier |
| bz_shipment | O_FACILITY_ID | Facility (External) | Many-to-One | Origin facility for shipment |
| bz_shipment | D_FACILITY_ID | Facility (External) | Many-to-One | Destination facility for shipment |
| bz_shipment | BUSINESS_PARTNER_ID | Business Partner (External) | Many-to-One | Business partner associated with shipment |
| bz_shipment | CUSTOMER_ID | Customer (External) | Many-to-One | Customer associated with shipment |
| bz_shipment | PP_SHIPMENT_ID | bz_shipment | Many-to-One | Parent shipment relationship (self-referencing) |
| bz_shipment | BILL_TO_CODE | Billing Party (External) | Many-to-One | Bill-to party for shipment |

## 5. Design Decisions and Assumptions

### 5.1 Design Decisions

1. **Single Table Approach**: All shipment data is stored in one comprehensive table (`bz_shipment`) to maintain raw data integrity and simplify initial ingestion.

2. **String Data Types**: Most ID fields are stored as STRING to accommodate various source system formats and avoid data type conversion issues.

3. **Decimal Precision**: Financial fields use DECIMAL(10,2) for currency amounts and DECIMAL(10,3) for weights/volumes to maintain precision.

4. **No Constraints**: Following Bronze layer principles, no primary keys, foreign keys, or check constraints are implemented.

5. **Delta Lake Properties**: Auto-optimize features are enabled for better performance and maintenance.

6. **Metadata Columns**: Standard governance columns (load_timestamp, update_timestamp, source_system) are added to all tables.

### 5.2 Assumptions

1. **Source System**: Data originates from a TMS (Transportation Management System) with the table structure provided.

2. **Data Volume**: The table structure supports high-volume transactional data with appropriate partitioning strategies to be implemented at the Silver layer.

3. **Currency Handling**: Multiple currency codes are preserved as-is; currency conversion will be handled in Silver/Gold layers.

4. **Temporal Data**: All timestamp fields preserve source timezone information where available.

5. **External References**: ID fields referencing external entities (carriers, facilities, customers) are stored as strings to accommodate various identifier formats.

6. **Audit Requirements**: The audit table captures processing metadata for compliance and monitoring purposes.

## 6. Implementation Notes

### 6.1 Data Ingestion

- Use MERGE operations for incremental loads based on SHIPMENT_ID and LAST_UPDATED_DTTM
- Implement change data capture (CDC) patterns for real-time updates
- Maintain data lineage through audit table entries

### 6.2 Performance Considerations

- Consider partitioning by CREATED_DTTM (date) for time-based queries
- Implement Z-ordering on frequently queried columns (SHIPMENT_STATUS, SHIPMENT_TYPE, TC_COMPANY_ID)
- Use liquid clustering for optimal query performance

### 6.3 Data Quality

- Implement data quality checks at ingestion time
- Log data quality issues in the audit table
- Preserve all source data even if quality issues are detected

## 7. API Cost

**apiCost**: 0.000000 (No external API calls were made during the generation of this physical data model)

---

*This Bronze Layer Physical Data Model provides the foundation for the Medallion architecture, ensuring raw data preservation while enabling efficient processing and governance for the TMS Shipment application.*