_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Silver Layer Physical Data Model for TMS Shipment Application (with required schema and logic changes)
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Silver Layer Physical Data Model

## 1. Overview

This document defines the physical data model for the Silver layer in the Medallion architecture for the TMS (Transportation Management System) Shipment application. The Silver layer stores cleansed, conformed, and enriched data, ready for analytics and reporting. This version incorporates the latest schema and transformation changes as requested.

---

## 2. DDL Scripts

### 2.1 Main Shipment Table (slv_shipment)

```sql
CREATE TABLE IF NOT EXISTS silver.slv_shipment (
  -- Surrogate Key
  shipment_id STRING,
  slv_shipment_sk BIGINT,

  -- Core Shipment Identifiers
  tc_shipment_id STRING,
  tc_company_id STRING,
  ext_sys_shipment_id STRING,
  shipment_ref_id STRING,
  ref_shipment_nbr STRING,
  pp_shipment_id STRING,

  -- Shipment Status and Type
  shipment_status STRING,
  shipment_type STRING,
  shipment_leg_type STRING,
  move_type STRING,
  creation_type STRING,
  business_process STRING,

  -- Dates and Times
  created_dttm TIMESTAMP,
  last_updated_dttm TIMESTAMP,
  shipment_start_dttm TIMESTAMP,
  shipment_end_dttm TIMESTAMP,
  shipment_recon_dttm TIMESTAMP,
  available_dttm TIMESTAMP,
  received_dttm TIMESTAMP,
  tender_dttm TIMESTAMP,
  scheduled_pickup_dttm TIMESTAMP,

  -- Creation and Update Tracking
  created_source STRING,
  created_source_type STRING,
  last_updated_source STRING,
  last_updated_source_type STRING,

  -- Origin Facility Information
  o_facility_id STRING,
  o_facility_number STRING,
  o_stop_location_name STRING,
  o_address STRING,
  o_city STRING,
  o_state_prov STRING,
  o_postal_code STRING,
  o_country_code STRING,
  o_county STRING,
  o_tandem_facility STRING,
  o_tandem_facility_alias STRING,

  -- Destination Facility Information
  d_facility_id STRING,
  d_facility_number STRING,
  d_stop_location_name STRING,
  d_address STRING,
  d_city STRING,
  d_state_prov STRING,
  d_postal_code STRING,
  d_country_code STRING,
  d_county STRING,
  d_tandem_facility STRING,
  d_tandem_facility_alias STRING,

  -- Carrier Information
  assigned_carrier_id STRING,
  assigned_carrier_code STRING,
  assigned_scn_dr_carrier_id STRING,
  assigned_scn_dr_carrier_code STRING,
  assigned_broker_carrier_id STRING,
  assigned_broker_carrier_code STRING,
  dsg_carrier_id STRING,
  dsg_carrier_code STRING,
  dsg_scn_dr_carrier_id STRING,
  dsg_scn_dr_carrier_code STRING,
  feasible_carrier_id STRING,
  feasible_carrier_code STRING,
  broker_carrier_id STRING,
  scndr_carrier_id STRING,
  payee_carrier_id STRING,
  lh_payee_carrier_id STRING,
  lh_payee_carrier_code STRING,
  hauling_carrier STRING,

  -- Equipment and Transport
  assigned_equipment_id STRING,
  dsg_equipment_id STRING,
  feasible_equipment_id STRING,
  feasible_equipment2_id STRING,
  equipment_type STRING,
  assigned_mot_id STRING,
  dsg_mot_id STRING,
  feasible_mot_id STRING,
  trailer_number STRING,
  tractor_number STRING,
  trlr_type STRING,
  trlr_size STRING,
  trlr_gen_code STRING,

  -- Distance and Route Information
  distance DECIMAL(10,2),
  direct_distance DECIMAL(10,2),
  out_of_route_distance DECIMAL(10,2),
  radial_distance DECIMAL(10,2),
  distance_uom STRING,
  radial_distance_uom STRING,
  num_stops INT,
  num_charge_layovers INT,
  num_docks INT,

  -- Weight and Volume
  planned_weight DECIMAL(10,3),
  planned_volume DECIMAL(10,3),
  financial_wt DECIMAL(10,3),
  left_wt DECIMAL(10,3),
  right_wt DECIMAL(10,3),
  order_qty DECIMAL(10,3),
  qty_uom_id STRING,
  weight_uom_id_base STRING,
  volume_uom_id_base STRING,

  -- Dimensions
  size1_value DECIMAL(10,3),
  size1_uom_id STRING,
  size2_value DECIMAL(10,3),
  size2_uom_id STRING,

  -- Cost Information
  total_cost DECIMAL(10,2),
  actual_cost DECIMAL(10,2),
  estimated_cost DECIMAL(10,2),
  baseline_cost DECIMAL(10,2),
  linehaul_cost DECIMAL(10,2),
  accessorial_cost DECIMAL(10,2),
  accessorial_cost_to_carrier DECIMAL(10,2),
  stop_cost DECIMAL(10,2),
  spot_charge DECIMAL(10,2),
  carrier_charge DECIMAL(10,2),
  cust_frgt_charge DECIMAL(10,2),
  cm_discount DECIMAL(10,2),
  total_cost_excl_tax DECIMAL(10,2),
  total_tax_amount DECIMAL(10,2),

  -- Planned Cost Information
  pln_total_cost DECIMAL(10,2),
  pln_linehaul_cost DECIMAL(10,2),
  pln_total_accessorial_cost DECIMAL(10,2),
  pln_accessoril_cost_to_carrier DECIMAL(10,2),
  pln_stop_off_cost DECIMAL(10,2),
  pln_carrier_charge DECIMAL(10,2),
  pln_normalized_total_cost DECIMAL(10,2),

  -- Budget Cost Information
  budg_total_cost DECIMAL(10,2),
  budg_normalized_total_cost DECIMAL(10,2),
  budg_cm_discount DECIMAL(10,2),
  orig_budg_total_cost DECIMAL(10,2),

  -- Recommended Cost Information
  rec_total_cost DECIMAL(10,2),
  rec_linehaul_cost DECIMAL(10,2),
  rec_accessorial_cost DECIMAL(10,2),
  rec_stop_cost DECIMAL(10,2),
  rec_spot_charge DECIMAL(10,2),
  rec_cm_discount DECIMAL(10,2),
  rec_normalized_total_cost DECIMAL(10,2),
  rec_margin DECIMAL(10,2),
  rec_normalized_margin DECIMAL(10,2),

  -- Revenue Information
  total_revenue DECIMAL(10,2),
  earned_income DECIMAL(10,2),
  normalized_total_revenue DECIMAL(10,2),
  frt_rev_linehaul_charge DECIMAL(10,2),
  frt_rev_accessorial_charge DECIMAL(10,2),
  frt_rev_stop_charge DECIMAL(10,2),
  frt_rev_spot_charge DECIMAL(10,2),
  frt_rev_cm_discount DECIMAL(10,2),

  -- Currency Codes
  currency_code STRING,
  actual_cost_currency_code STRING,
  baseline_cost_currency_code STRING,
  pln_currency_code STRING,
  budg_currency_code STRING,
  rec_currency_code STRING,
  total_revenue_currency_code STRING,
  earned_income_currency_code STRING,
  spot_charge_currency_code STRING,
  frt_rev_spot_charge_curr_code STRING,
  cod_currency_code STRING,
  dv_currency_code STRING,
  mv_currency_code STRING,

  -- Billing Information
  bill_to_code STRING,
  bill_to_name STRING,
  bill_to_address STRING,
  bill_to_city STRING,
  bill_to_state_prov STRING,
  bill_to_postal_code STRING,
  bill_to_country_code STRING,
  bill_to_phone_number STRING,
  bill_to_title STRING,
  billing_method STRING,
  bill_of_lading_number STRING,
  purchase_order STRING,
  pro_number STRING,

  -- Service and Lane Information
  assigned_service_level_id STRING,
  dsg_service_level_id STRING,
  feasible_service_level_id STRING,
  rec_service_level_id STRING,
  assigned_lane_id STRING,
  assigned_lane_detail_id STRING,
  rating_lane_id STRING,
  rating_lane_detail_id STRING,
  pln_rating_lane_id STRING,
  pln_rating_lane_detail_id STRING,
  frt_rev_rating_lane_id STRING,
  frt_rev_rating_lane_detail_id STRING,
  rec_lane_id STRING,
  rec_lane_detail_id STRING,
  rec_rating_lane_id STRING,
  rec_rating_lane_detail_id STRING,
  lane_name STRING,

  -- Timing Information
  pickup_start_date TIMESTAMP,
  pickup_end_dttm TIMESTAMP,
  pickup_tz STRING,
  delivery_start_dttm TIMESTAMP,
  delivery_end_dttm TIMESTAMP,
  delivery_tz STRING,
  days_to_deliver INT,
  total_time DECIMAL(10,2),

  -- Temperature Control
  pln_min_temperature DECIMAL(5,2),
  pln_max_temperature DECIMAL(5,2),
  temperature_uom STRING,

  -- Flags and Indicators
  is_shipment_cancelled STRING,
  is_shipment_reconciled STRING,
  is_hazmat STRING,
  is_perishable STRING,
  is_manual_assign STRING,
  is_misrouted STRING,
  is_auto_delivered STRING,
  is_booking_required STRING,
  is_filo STRING,
  is_cooler_at_nose STRING,
  has_alerts STRING,
  has_notes STRING,
  has_tracking_msg STRING,
  has_em_notify_flag STRING,
  has_import_error STRING,
  has_soft_check_error STRING,
  shipment_closed_indicator STRING,
  print_cons_bol STRING,
  sed_generated_flag STRING,

  -- Route and Equipment Details
  rte_type STRING,
  rte_type_1 STRING,
  rte_type_2 STRING,
  rte_to STRING,
  rte_swc_nbr STRING,
  static_route_id STRING,
  assigned_ship_via STRING,
  dropoff_pickup STRING,
  loading_seq_ord INT,
  door STRING,
  seal_number STRING,

  -- Business Partner and Customer
  business_partner_id STRING,
  customer_id STRING,
  assigned_customer_id STRING,

  -- Additional Cost and Charge Fields
  cod_amount DECIMAL(10,2),
  declared_value DECIMAL(10,2),
  monetary_value DECIMAL(10,2),
  margin DECIMAL(10,2),
  normalized_margin DECIMAL(10,2),
  normalized_baseline_cost DECIMAL(10,2),
  normalized_total_cost DECIMAL(10,2),
  estimated_savings DECIMAL(10,2),
  reported_cost DECIMAL(10,2),
  min_rate DECIMAL(10,2),
  rate DECIMAL(10,4),
  rate_type STRING,
  rate_uom STRING,

  -- Optimization and Management
  cmid STRING,
  assigned_cm_shipment_id STRING,
  rec_cm_shipment_id STRING,
  rec_cmid STRING,
  config_cycle_seq INT,
  cycle_deadline_dttm TIMESTAMP,
  cycle_execution_dttm TIMESTAMP,

  -- Booking Information
  booking_id STRING,
  booking_ref_carrier STRING,
  booking_ref_shipper STRING,
  dsg_voyage_flight STRING,
  feasible_voyage_flight STRING,

  -- Warehouse Integration
  sent_to_pkms STRING,
  sent_to_pkms_dttm TIMESTAMP,
  sent_to_create_pkms STRING,
  sent_to_create_pkms_dttm TIMESTAMP,
  first_update_sent_to_pkms STRING,
  wms_status_code STRING,

  -- Additional Fields
  commodity_class STRING,
  commodity_code_id STRING,
  packaging STRING,
  tariff STRING,
  contract_number STRING,
  auth_nbr STRING,
  broker_ref STRING,
  region_id STRING,
  inbound_region_id STRING,
  outbound_region_id STRING,
  hub_id STRING,
  wave_id STRING,
  ship_group_id STRING,
  manifest_id STRING,

  -- System and Technical Fields
  hibernate_version INT,
  extraction_dttm TIMESTAMP,
  currency_dttm TIMESTAMP,

  -- Silver Layer Metadata columns
  load_date DATE,
  update_date DATE,
  source_system STRING,

  -- Additional Silver Layer Columns
  customer_segment STRING,
  loyalty_score DECIMAL(5,2),

  -- Partitioning Columns
  region_id STRING,
  transaction_date DATE
)
USING DELTA
PARTITIONED BY (region_id, transaction_date)
LOCATION '/mnt/silver/shipment'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.zorderCols' = 'transaction_date'
);
```

**Notes:**
- The `customer_segment` column (STRING) is added to classify customers.
- The `transaction_amount` column is not present in the Bronze model, but if it exists, its type should be updated to `DECIMAL(10,2)`.
- The deprecated column `legacy_customer_id` is removed.
- The `loyalty_score` column is added as DECIMAL(5,2).
- Partitioning is by `region_id` and `transaction_date`.
- Z-ordering is enabled on `transaction_date`.
- All columns from Bronze are retained, with Silver-specific additions.

---

### 2.2 Error Data Table (slv_shipment_error)

```sql
CREATE TABLE IF NOT EXISTS silver.slv_shipment_error (
  error_id BIGINT,
  shipment_id STRING,
  error_type STRING,
  error_message STRING,
  error_timestamp TIMESTAMP,
  error_source STRING,
  load_date DATE,
  update_date DATE,
  source_system STRING
)
USING DELTA
LOCATION '/mnt/silver/shipment_error';
```

---

### 2.3 Audit Table (slv_audit)

```sql
CREATE TABLE IF NOT EXISTS silver.slv_audit (
  audit_id BIGINT,
  pipeline_name STRING,
  execution_start_time TIMESTAMP,
  execution_end_time TIMESTAMP,
  status STRING,
  error_message STRING,
  record_count BIGINT,
  load_date DATE,
  update_date DATE,
  source_system STRING
)
USING DELTA
LOCATION '/mnt/silver/audit';
```

---

### 2.4 Update DDL Script

```sql
-- Add customer_segment column
ALTER TABLE silver.slv_shipment ADD COLUMNS (customer_segment STRING);

-- Add loyalty_score column
ALTER TABLE silver.slv_shipment ADD COLUMNS (loyalty_score DECIMAL(5,2));

-- Change transaction_amount to DECIMAL(10,2) if exists
ALTER TABLE silver.slv_shipment ALTER COLUMN transaction_amount TYPE DECIMAL(10,2);

-- Drop legacy_customer_id column if exists
ALTER TABLE silver.slv_shipment DROP COLUMN legacy_customer_id;
```

---

## 3. Data Retention Policies

### 3.1 Retention Periods for Silver Layer
- **Active Data**: 2 years from load_date
- **Error Data**: 1 year from load_date
- **Audit Data**: 3 years from load_date

### 3.2 Archiving Strategies
- Data older than the retention period is moved to a cold storage location (e.g., `/mnt/archive/silver/`)
- Use Databricks jobs to automate archival and purging
- Delta Lake time travel is enabled for 30 days for rollback and recovery

---

## 4. Conceptual Data Model Diagram (Tabular Form)

| Source Table         | Relationship Key Field      | Target Table           | Relationship Type |
|---------------------|----------------------------|------------------------|-------------------|
| slv_shipment        | shipment_id                | slv_shipment_error     | One-to-Many       |
| slv_shipment        | shipment_id                | slv_audit              | One-to-Many       |
| slv_shipment        | assigned_carrier_id        | Carrier (external)     | Many-to-One       |
| slv_shipment        | o_facility_id              | Facility (external)    | Many-to-One       |
| slv_shipment        | d_facility_id              | Facility (external)    | Many-to-One       |
| slv_shipment        | business_partner_id        | Business Partner (external) | Many-to-One |
| slv_shipment        | customer_id                | Customer (external)    | Many-to-One       |
| slv_shipment        | pp_shipment_id             | slv_shipment           | Many-to-One       |
| slv_shipment        | bill_to_code               | Billing Party (external) | Many-to-One    |

---

## 5. Data Quality and Transformation Logic

- `transaction_amount` must be non-negative (enforced in ETL, flagged in error table if violated)
- `customer_segment` must not be null (flagged in error table if null)
- `order_status` supports new value 'Pending Verification'
- `loyalty_score` is calculated based on transaction recency and frequency (see ETL logic)

---

## 6. Design Decisions and Assumptions

- All Bronze columns are retained unless deprecated or replaced
- Surrogate keys (e.g., slv_shipment_sk) are introduced for Silver layer
- No PK/FK constraints are enforced (Databricks/SparkSQL limitation)
- Partitioning and Z-ordering are used for performance
- Delta Lake is the storage format for all tables
- Data retention and archival are automated via Databricks jobs
- Audit and error tables are present in both Silver and Gold layers

---

## 7. API Cost

**apiCost**: 0.000000

---

[outputURL](https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical)

[pipelineID]: 12357
