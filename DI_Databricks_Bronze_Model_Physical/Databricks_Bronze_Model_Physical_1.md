_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Physical data model for Bronze layer of Medallion architecture for TMS Shipment application
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Physical

## 1. Overview
This document defines the physical data model for the Bronze layer of the Medallion architecture for the TMS (Transportation Management System) Shipment application. The Bronze layer stores raw data as-is from source systems with added metadata for governance and lineage tracking.

## 2. Design Principles
- Store raw data without transformation
- Use Delta Lake format for ACID transactions
- Add metadata columns for governance
- No primary keys, foreign keys, or constraints (Delta tables don't enforce them)
- Use naming convention: bz_<tablename> within bronze schema
- Include audit trail for all data operations

## 3. Bronze Layer DDL Scripts

### 3.1 Main Shipment Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_shipment (
  -- Core Shipment Identifiers
  SHIPMENT_ID STRING,
  TC_SHIPMENT_ID STRING,
  TC_COMPANY_ID STRING,
  SHIPMENT_REF_ID STRING,
  EXT_SYS_SHIPMENT_ID STRING,
  PP_SHIPMENT_ID STRING,
  REF_SHIPMENT_NBR STRING,
  
  -- Shipment Status and Type
  SHIPMENT_STATUS STRING,
  SHIPMENT_TYPE STRING,
  SHIPMENT_LEG_TYPE STRING,
  MOVE_TYPE STRING,
  BUSINESS_PROCESS STRING,
  PRIORITY_TYPE STRING,
  
  -- Dates and Times
  CREATED_DTTM TIMESTAMP,
  LAST_UPDATED_DTTM TIMESTAMP,
  SHIPMENT_START_DTTM TIMESTAMP,
  SHIPMENT_END_DTTM TIMESTAMP,
  SHIPMENT_RECON_DTTM TIMESTAMP,
  AVAILABLE_DTTM TIMESTAMP,
  RECEIVED_DTTM TIMESTAMP,
  TENDER_DTTM TIMESTAMP,
  TENDER_RESP_DEADLINE_DATE TIMESTAMP,
  TENDER_RESP_DEADLINE_TZ STRING,
  
  -- Creation and Update Information
  CREATED_SOURCE STRING,
  CREATED_SOURCE_TYPE STRING,
  CREATION_TYPE STRING,
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
  
  -- Service Levels
  ASSIGNED_SERVICE_LEVEL_ID STRING,
  DSG_SERVICE_LEVEL_ID STRING,
  FEASIBLE_SERVICE_LEVEL_ID STRING,
  
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
  DAYS_TO_DELIVER INT,
  TOTAL_TIME DECIMAL(10,2),
  
  -- Weight and Volume
  PLANNED_WEIGHT DECIMAL(10,3),
  PLANNED_VOLUME DECIMAL(10,3),
  FINANCIAL_WT DECIMAL(10,3),
  LEFT_WT DECIMAL(10,3),
  RIGHT_WT DECIMAL(10,3),
  ORDER_QTY DECIMAL(10,3),
  WEIGHT_UOM_ID_BASE STRING,
  VOLUME_UOM_ID_BASE STRING,
  QTY_UOM_ID STRING,
  
  -- Size Dimensions
  SIZE1_VALUE DECIMAL(10,3),
  SIZE1_UOM_ID STRING,
  SIZE2_VALUE DECIMAL(10,3),
  SIZE2_UOM_ID STRING,
  
  -- Cost Information
  ACTUAL_COST DECIMAL(10,2),
  ACTUAL_COST_CURRENCY_CODE STRING,
  ESTIMATED_COST DECIMAL(10,2),
  BASELINE_COST DECIMAL(10,2),
  BASELINE_COST_CURRENCY_CODE STRING,
  TOTAL_COST DECIMAL(10,2),
  TOTAL_COST_EXCL_TAX DECIMAL(10,2),
  LINEHAUL_COST DECIMAL(10,2),
  ACCESSORIAL_COST DECIMAL(10,2),
  ACCESSORIAL_COST_TO_CARRIER DECIMAL(10,2),
  STOP_COST DECIMAL(10,2),
  SPOT_CHARGE DECIMAL(10,2),
  SPOT_CHARGE_CURRENCY_CODE STRING,
  CARRIER_CHARGE DECIMAL(10,2),
  CM_DISCOUNT DECIMAL(10,2),
  ESTIMATED_SAVINGS DECIMAL(10,2),
  REPORTED_COST DECIMAL(10,2),
  CURRENCY_CODE STRING,
  CURRENCY_DTTM TIMESTAMP,
  
  -- Revenue Information
  TOTAL_REVENUE DECIMAL(10,2),
  TOTAL_REVENUE_CURRENCY_CODE STRING,
  EARNED_INCOME DECIMAL(10,2),
  EARNED_INCOME_CURRENCY_CODE STRING,
  MARGIN DECIMAL(10,2),
  NORMALIZED_MARGIN DECIMAL(10,2),
  NORMALIZED_TOTAL_COST DECIMAL(10,2),
  NORMALIZED_TOTAL_REVENUE DECIMAL(10,2),
  NORMALIZED_BASELINE_COST DECIMAL(10,2),
  
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
  PRO_NUMBER STRING,
  PURCHASE_ORDER STRING,
  CONTRACT_NUMBER STRING,
  
  -- Business Partner Information
  BUSINESS_PARTNER_ID STRING,
  CUSTOMER_ID STRING,
  ASSIGNED_CUSTOMER_ID STRING,
  CUSTOMER_CREDIT_LIMIT_ID STRING,
  
  -- Flags and Indicators
  IS_SHIPMENT_CANCELLED STRING,
  IS_SHIPMENT_RECONCILED STRING,
  SHIPMENT_CLOSED_INDICATOR STRING,
  IS_MANUAL_ASSIGN STRING,
  IS_HAZMAT STRING,
  IS_PERISHABLE STRING,
  IS_BOOKING_REQUIRED STRING,
  IS_AUTO_DELIVERED STRING,
  ON_TIME_INDICATOR STRING,
  HAS_ALERTS STRING,
  HAS_NOTES STRING,
  HAS_TRACKING_MSG STRING,
  HAS_EM_NOTIFY_FLAG STRING,
  HAS_IMPORT_ERROR STRING,
  HAS_SOFT_CHECK_ERROR STRING,
  
  -- Pickup and Delivery Windows
  PICKUP_START_DATE TIMESTAMP,
  PICKUP_END_DTTM TIMESTAMP,
  PICKUP_TZ STRING,
  DELIVERY_START_DTTM TIMESTAMP,
  DELIVERY_END_DTTM TIMESTAMP,
  DELIVERY_TZ STRING,
  SCHEDULED_PICKUP_DTTM TIMESTAMP,
  
  -- Temperature Control
  PLN_MIN_TEMPERATURE DECIMAL(5,2),
  PLN_MAX_TEMPERATURE DECIMAL(5,2),
  TEMPERATURE_UOM STRING,
  
  -- Additional References
  AUTH_NBR STRING,
  BROKER_REF STRING,
  SEAL_NUMBER STRING,
  DOOR STRING,
  WAVE_ID STRING,
  MANIFEST_ID STRING,
  BOOKING_ID STRING,
  CMID STRING,
  
  -- Metadata columns for Bronze layer
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_shipment';
```

### 3.2 Carrier Information Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_carrier (
  carrier_id STRING,
  carrier_code STRING,
  carrier_name STRING,
  carrier_type STRING,
  mode_of_transport STRING,
  is_active STRING,
  
  -- Metadata columns
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_carrier';
```

### 3.3 Facility Information Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_facility (
  facility_id STRING,
  facility_number STRING,
  facility_name STRING,
  facility_type STRING,
  address STRING,
  city STRING,
  state_prov STRING,
  postal_code STRING,
  country_code STRING,
  county STRING,
  tandem_facility STRING,
  tandem_facility_alias STRING,
  
  -- Metadata columns
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_facility';
```

### 3.4 Route Information Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_route (
  route_id STRING,
  shipment_id STRING,
  total_distance DECIMAL(10,2),
  direct_distance DECIMAL(10,2),
  out_of_route_distance DECIMAL(10,2),
  distance_uom STRING,
  num_stops INT,
  equipment_type STRING,
  route_type STRING,
  
  -- Metadata columns
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_route';
```

### 3.5 Billing Information Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_billing (
  billing_id STRING,
  shipment_id STRING,
  bill_to_code STRING,
  bill_to_name STRING,
  bill_to_postal_code STRING,
  bill_to_state_prov STRING,
  bill_of_lading_number STRING,
  billing_method STRING,
  purchase_order STRING,
  company_identifier STRING,
  reconciliation_date TIMESTAMP,
  
  -- Metadata columns
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_billing';
```

### 3.6 Business Partner Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_business_partner (
  business_partner_id STRING,
  partner_name STRING,
  partner_type STRING,
  parent_shipment_reference STRING,
  
  -- Metadata columns
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_business_partner';
```

### 3.7 User Role Table

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_user_role (
  role_id STRING,
  role_name STRING,
  role_description STRING,
  permissions STRING,
  
  -- Metadata columns
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_user_role';
```

### 3.8 Audit Table

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
  
  -- Metadata columns
  audit_timestamp TIMESTAMP,
  audit_source STRING
) USING DELTA
LOCATION '/mnt/bronze/bz_audit';
```

## 4. Conceptual Data Model Diagram (Tabular Form)

| Source Table | Relationship Key Field | Target Table | Connection Type |
|--------------|------------------------|--------------|----------------|
| bz_shipment | ASSIGNED_CARRIER_ID | bz_carrier | Many-to-One |
| bz_shipment | O_FACILITY_ID | bz_facility | Many-to-One |
| bz_shipment | D_FACILITY_ID | bz_facility | Many-to-One |
| bz_shipment | SHIPMENT_ID | bz_billing | One-to-Many |
| bz_shipment | BUSINESS_PARTNER_ID | bz_business_partner | Many-to-One |
| bz_shipment | CREATED_SOURCE_TYPE | bz_user_role | Many-to-One |
| bz_shipment | SHIPMENT_ID | bz_route | One-to-Many |
| bz_carrier | carrier_id | bz_shipment | One-to-Many |
| bz_facility | facility_id | bz_shipment | One-to-Many |
| bz_billing | shipment_id | bz_shipment | Many-to-One |
| bz_business_partner | business_partner_id | bz_shipment | One-to-Many |
| bz_user_role | role_name | bz_shipment | One-to-Many |
| bz_route | shipment_id | bz_shipment | Many-to-One |

## 5. Design Assumptions and Decisions

### 5.1 Data Storage Format
- **Delta Lake**: Chosen for ACID transactions, time travel, and schema evolution capabilities
- **Parquet**: Underlying format for efficient columnar storage and compression

### 5.2 Schema Design
- **No Constraints**: Delta tables don't enforce primary keys, foreign keys, or check constraints
- **Nullable Fields**: Most fields are nullable to accommodate varying data quality from source systems
- **String Data Types**: Used extensively to preserve original data format and avoid conversion issues

### 5.3 Naming Conventions
- **Table Prefix**: All Bronze layer tables prefixed with 'bz_'
- **Schema**: All tables created in 'bronze' schema
- **Column Names**: Preserved original column names from source system for traceability

### 5.4 Metadata Strategy
- **Load Timestamp**: Tracks when data was ingested into Bronze layer
- **Update Timestamp**: Tracks when data was last modified
- **Source System**: Identifies the originating system for data lineage

### 5.5 Partitioning Strategy
- Tables can be partitioned by date fields (e.g., CREATED_DTTM) for performance
- Partitioning implementation depends on data volume and query patterns

### 5.6 Data Quality
- Bronze layer accepts data as-is without validation
- Data quality checks and cleansing will be performed in Silver layer
- Audit table tracks processing status and errors

## 6. Implementation Guidelines

### 6.1 Data Ingestion
- Use Databricks Auto Loader for streaming ingestion
- Implement schema inference and evolution
- Handle late-arriving data with merge operations

### 6.2 Performance Optimization
- Enable Delta Lake optimizations (OPTIMIZE, Z-ORDER)
- Configure appropriate file sizes for optimal performance
- Use liquid clustering for frequently queried columns

### 6.3 Monitoring and Governance
- Implement data lineage tracking through Unity Catalog
- Set up monitoring for data freshness and quality
- Use Delta Lake time travel for data recovery and auditing

## 7. API Cost

apiCost: 0.000000

---

**Note**: This physical data model serves as the foundation for the Bronze layer in the Medallion architecture. The design prioritizes data preservation and lineage while enabling efficient processing in downstream Silver and Gold layers.