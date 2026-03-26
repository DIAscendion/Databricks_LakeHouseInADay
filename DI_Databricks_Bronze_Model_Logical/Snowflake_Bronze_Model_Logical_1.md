_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Snowflake Bronze Model Logical for Shipment Management System
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Snowflake Bronze Model Logical for Shipment Management System

## 1. PII Classification

| Column Names | Reason why it is classified as PII |
|--------------|------------------------------------|
| BILL_TO_NAME | Contains personal or business entity names that can identify individuals or organizations |
| BILL_TO_PHONE_NUMBER | Contains phone numbers which are personally identifiable information |
| BILL_TO_ADDRESS | Contains street addresses which can identify specific locations and individuals |
| HAZMAT_CERT_CONTACT | Contains contact information for hazmat certification which may include personal details |
| CREATED_SOURCE | May contain user identifiers or system names that could trace back to individuals |
| LAST_UPDATED_SOURCE | May contain user identifiers or system names that could trace back to individuals |
| TRANS_PLAN_OWNER | Contains information about the person responsible for transportation planning |

## 2. Bronze Layer Logical Model

### Bz_Shipment
**Description**: Bronze layer table containing raw shipment data with all operational details, costs, and tracking information from the source TMS system.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| ACCESSORIAL_COST | Total accessorial charges applied to the shipment | Decimal |
| ACCESSORIAL_COST_TO_CARRIER | Accessorial cost passed to the carrier | Decimal |
| ACTUAL_COST | Actual total cost of the shipment | Decimal |
| ACTUAL_COST_CURRENCY_CODE | Currency code for the actual shipment cost | String |
| APPT_DOOR_SCHED_TYPE | Appointment door scheduling type | String |
| ASSIGNED_BROKER_CARRIER_CODE | Code identifying the broker carrier assigned to the shipment | String |
| ASSIGNED_CARRIER_CODE | Code identifying the primary carrier assigned to the shipment | String |
| ASSIGNED_CUSTOMER_ID | Identifier for the customer assigned to the shipment | String |
| ASSIGNED_EQUIPMENT_ID | Identifier for the equipment assigned to the shipment | String |
| ASSIGNED_LANE_DETAIL_ID | Identifier for the detail record of the assigned lane | String |
| ASSIGNED_LANE_ID | Identifier for the lane assigned to the shipment | String |
| ASSIGNED_MOT_ID | Identifier for the mode of transport assigned to the shipment | String |
| ASSIGNED_SCNDR_CARRIER_CODE | Code identifying the secondary carrier assigned to the shipment | String |
| ASSIGNED_SERVICE_LEVEL_ID | Identifier for the service level assigned to the shipment | String |
| ASSIGNED_SHIP_VIA | Ship-via method assigned to the shipment | String |
| AUTH_NBR | Authorization number associated with the shipment | String |
| AVAILABLE_DTTM | Date and time when the shipment became available | DateTime |
| BASELINE_COST | Baseline cost used for cost comparison | Decimal |
| BASELINE_COST_CURRENCY_CODE | Currency code for the baseline shipment cost | String |
| BILL_OF_LADING_NUMBER | Bill of lading reference number for the shipment | String |
| BILL_TO_ADDRESS | Street address of the bill-to party | String |
| BILL_TO_CITY | City of the bill-to party | String |
| BILL_TO_CODE | Code identifying the bill-to party | String |
| BILL_TO_COUNTRY_CODE | Country code of the bill-to party | String |
| BILL_TO_NAME | Name of the bill-to party | String |
| BILL_TO_PHONE_NUMBER | Phone number of the bill-to party | String |
| BILL_TO_POSTAL_CODE | Postal code of the bill-to party | String |
| BILL_TO_STATE_PROV | State or province of the bill-to party | String |
| BILL_TO_TITLE | Title or salutation of the bill-to contact | String |
| BILLING_METHOD | Method used to bill the shipment | String |
| BUSINESS_PARTNER_ID | Identifier for the business partner or vendor linked to the shipment | String |
| BUSINESS_PROCESS | Business process category associated with the shipment | String |
| CARRIER_CHARGE | Charge amount billed by the carrier | Decimal |
| CM_DISCOUNT | Carrier management discount applied to the shipment | Decimal |
| COD_AMOUNT | Cash on delivery amount for the shipment | Decimal |
| COD_CURRENCY_CODE | Currency code for the cash on delivery amount | String |
| COMMODITY_CLASS | Freight commodity class for rating purposes | String |
| COMMODITY_CODE_ID | Identifier for the commodity code assigned to the shipment | String |
| CONTRACT_NUMBER | Contract number governing the shipment pricing | String |
| COST_BREAKUP | Detailed breakdown of shipment cost components | String |
| CREATED_DTTM | Date and time when the shipment record was created | DateTime |
| CREATED_SOURCE | System or process that created the shipment record | String |
| CREATED_SOURCE_TYPE | Role type of the user or system that created the shipment | String |
| CREATION_TYPE | Type of creation process used to generate the shipment | String |
| CURRENCY_CODE | Default currency code used for this shipment | String |
| CURRENCY_DTTM | Date and time of the currency rate used for this shipment | DateTime |
| CUSTOMER_ID | Identifier for the customer associated with the shipment | String |
| D_ADDRESS | Street address of the destination facility | String |
| D_CITY | City of the destination facility | String |
| D_COUNTRY_CODE | Country code of the destination facility | String |
| D_COUNTY | County of the destination facility | String |
| D_FACILITY_NUMBER | Facility number of the destination | String |
| D_POSTAL_CODE | Postal code of the destination facility | String |
| D_STATE_PROV | State or province of the destination facility | String |
| D_STOP_LOCATION_NAME | Name of the destination stop location | String |
| DAYS_TO_DELIVER | Number of days planned or actual for delivery | Integer |
| DECLARED_VALUE | Declared monetary value of the shipment contents | Decimal |
| DELAY_TYPE | Type of delay associated with the shipment | String |
| DELIVERY_END_DTTM | Planned delivery window end date and time | DateTime |
| DELIVERY_REQ | Delivery requirements or special instructions | String |
| DELIVERY_START_DTTM | Planned delivery window start date and time | DateTime |
| DELIVERY_TZ | Timezone for the delivery window | String |
| DIRECT_DISTANCE | Straight-line distance between origin and destination | Decimal |
| DISTANCE | Total route distance for the shipment | Decimal |
| DISTANCE_UOM | Unit of measure for the shipment distance | String |
| DOOR | Door number assigned to the shipment at the facility | String |
| DROPOFF_PICKUP | Indicates whether the shipment is a drop-off or pickup | String |
| DSG_CARRIER_CODE | Designated carrier code for DC-to-Store master lane reference | String |
| EQUIPMENT_TYPE | Type of equipment used or required for the shipment | String |
| ESTIMATED_COST | Estimated cost of the shipment prior to execution | Decimal |
| ESTIMATED_DISPATCH_DTTM | Estimated date and time for dispatch | DateTime |
| ESTIMATED_SAVINGS | Estimated cost savings achieved on the shipment | Decimal |
| EXT_SYS_SHIPMENT_ID | Shipment identifier from an external system | String |
| EXTRACTION_DTTM | Date and time when the record was extracted from the source system | DateTime |
| FEASIBLE_CARRIER_CODE | Code of a carrier identified as feasible during optimization | String |
| FINANCIAL_WT | Financial weight used for cost calculation purposes | Decimal |
| HAS_ALERTS | Indicates whether the shipment has active alerts | String |
| HAS_NOTES | Indicates whether notes have been added to the shipment | String |
| HAULING_CARRIER | Carrier physically hauling the shipment | String |
| HAZMAT_CERT_CONTACT | Contact information for hazmat certification | String |
| HAZMAT_CERT_DECLARATION | Hazmat certification declaration statement | String |
| INSURANCE_STATUS | Status of insurance coverage for the shipment | String |
| IS_SHIPMENT_CANCELLED | Flag indicating the shipment has been cancelled | String |
| IS_SHIPMENT_RECONCILED | Flag indicating the shipment has been financially reconciled | String |
| IS_HAZMAT | Flag indicating the shipment contains hazardous materials | String |
| IS_PERISHABLE | Flag indicating the shipment contains perishable goods | String |
| LANE_NAME | Name of the lane assigned to the shipment | String |
| LAST_UPDATED_DTTM | Date and time when the shipment record was last updated | DateTime |
| LAST_UPDATED_SOURCE | System or process that last updated the shipment record | String |
| LAST_UPDATED_SOURCE_TYPE | Role type of the user or system that last updated the shipment | String |
| LINEHAUL_COST | Total linehaul freight cost for the shipment | Decimal |
| MANIFEST_ID | Identifier for the manifest this shipment belongs to | String |
| MARGIN | Margin amount calculated for the shipment | Decimal |
| MONETARY_VALUE | Total monetary value of the shipment contents | Decimal |
| MOVE_TYPE | Type of movement for the shipment | String |
| NUM_STOPS | Total number of stops on the shipment route | Integer |
| O_ADDRESS | Street address of the origin facility | String |
| O_CITY | City of the origin facility | String |
| O_COUNTRY_CODE | Country code of the origin facility | String |
| O_COUNTY | County of the origin facility | String |
| O_FACILITY_NUMBER | Facility number of the origin | String |
| O_POSTAL_CODE | Postal code of the origin facility | String |
| O_STATE_PROV | State or province of the origin facility | String |
| O_STOP_LOCATION_NAME | Name of the origin stop location | String |
| ON_TIME_INDICATOR | Indicates whether the shipment was delivered on time | String |
| ORDER_QTY | Order quantity associated with the shipment | Decimal |
| OUT_OF_ROUTE_DISTANCE | Distance travelled beyond the direct route | Decimal |
| PACKAGING | Packaging type or description for the shipment | String |
| PICKUP_END_DTTM | Planned pickup window end date and time | DateTime |
| PICKUP_START_DATE | Planned pickup window start date and time | DateTime |
| PICKUP_TZ | Timezone for the pickup window | String |
| PLANNED_VOLUME | Planned volume of the shipment | Decimal |
| PLANNED_WEIGHT | Planned weight of the shipment | Decimal |
| PRO_NUMBER | Progressive number assigned by the carrier | String |
| PURCHASE_ORDER | Purchase order number associated with the shipment | String |
| RATE | Rate applied to the shipment for cost calculation | Decimal |
| RATE_TYPE | Type of rate applied to the shipment | String |
| RECEIVED_DTTM | Date and time when the shipment was received at the destination | DateTime |
| REF_SHIPMENT_NBR | Reference shipment number linked to this shipment | String |
| REPORTED_COST | Cost reported for the shipment after execution | Decimal |
| SEAL_NUMBER | Seal number applied to the shipment trailer or container | String |
| SHIPMENT_CLOSED_INDICATOR | Flag indicating the shipment has been closed | String |
| SHIPMENT_END_DTTM | Date and time when the shipment execution ended | DateTime |
| SHIPMENT_LEG_TYPE | Type of shipment leg | String |
| SHIPMENT_RECON_DTTM | Date and time when the shipment was financially reconciled | DateTime |
| SHIPMENT_REF_ID | Reference identifier linking related shipments | String |
| SHIPMENT_START_DTTM | Date and time when shipment execution began | DateTime |
| SHIPMENT_STATUS | Current transit status of the shipment | String |
| SHIPMENT_TYPE | Product class type of the shipment | String |
| SPOT_CHARGE | Spot charge amount applied to the shipment | Decimal |
| SPOT_CHARGE_CURRENCY_CODE | Currency code for the spot charge amount | String |
| STOP_COST | Stop charge cost for the shipment | Decimal |
| TARIFF | Tariff code or schedule applied to the shipment | String |
| TC_COMPANY_ID | Company identifier within the TMS system | String |
| TC_SHIPMENT_ID | TMS-assigned shipment identifier | String |
| TENDER_DTTM | Date and time when the shipment was tendered to the carrier | DateTime |
| TOTAL_COST | Total shipment cost including all charges | Decimal |
| TOTAL_REVENUE | Total revenue generated by the shipment | Decimal |
| TOTAL_REVENUE_CURRENCY_CODE | Currency code for the total revenue amount | String |
| TOTAL_TIME | Total elapsed time for the shipment from pickup to delivery | Decimal |
| TRACTOR_NUMBER | Tractor unit number assigned to the shipment | String |
| TRAILER_NUMBER | Trailer number assigned to the shipment | String |
| TRANS_PLAN_OWNER | Owner or planner responsible for the transportation plan | String |
| TRANS_RESP_CODE | Transport responsibility code indicating who manages the freight | String |
| TRLR_SIZE | Size category of the trailer assigned to the shipment | String |
| TRLR_TYPE | Type of trailer assigned to the shipment | String |
| VOLUME_UOM_ID_BASE | Base unit of measure identifier for volume fields | String |
| WEIGHT_UOM_ID_BASE | Base unit of measure identifier for weight fields | String |
| WMS_STATUS_CODE | Status code from the warehouse management system | String |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

### Bz_Carrier
**Description**: Bronze layer table containing carrier information including primary, secondary, and broker carriers.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| ASSIGNED_CARRIER_CODE | Code identifying the primary carrier | String |
| ASSIGNED_BROKER_CARRIER_CODE | Code identifying the broker carrier | String |
| ASSIGNED_SCNDR_CARRIER_CODE | Code identifying the secondary carrier | String |
| DSG_CARRIER_CODE | Designated carrier code for master lane reference | String |
| FEASIBLE_CARRIER_CODE | Code of feasible carrier during optimization | String |
| HAULING_CARRIER | Carrier physically hauling the shipment | String |
| ASSIGNED_MOT_ID | Mode of transport identifier | String |
| CARRIER_CHARGE | Charge amount billed by the carrier | Decimal |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

### Bz_Facility
**Description**: Bronze layer table containing origin and destination facility information.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| O_FACILITY_NUMBER | Origin facility number | String |
| O_ADDRESS | Origin facility street address | String |
| O_CITY | Origin facility city | String |
| O_STATE_PROV | Origin facility state or province | String |
| O_POSTAL_CODE | Origin facility postal code | String |
| O_COUNTRY_CODE | Origin facility country code | String |
| O_COUNTY | Origin facility county | String |
| O_STOP_LOCATION_NAME | Origin stop location name | String |
| D_FACILITY_NUMBER | Destination facility number | String |
| D_ADDRESS | Destination facility street address | String |
| D_CITY | Destination facility city | String |
| D_STATE_PROV | Destination facility state or province | String |
| D_POSTAL_CODE | Destination facility postal code | String |
| D_COUNTRY_CODE | Destination facility country code | String |
| D_COUNTY | Destination facility county | String |
| D_STOP_LOCATION_NAME | Destination stop location name | String |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

### Bz_Route
**Description**: Bronze layer table containing route details, distances, and stop information.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| DISTANCE | Total route distance for the shipment | Decimal |
| DIRECT_DISTANCE | Straight-line distance between origin and destination | Decimal |
| OUT_OF_ROUTE_DISTANCE | Distance travelled beyond the direct route | Decimal |
| DISTANCE_UOM | Unit of measure for the shipment distance | String |
| NUM_STOPS | Total number of stops on the shipment route | Integer |
| EQUIPMENT_TYPE | Type of equipment used or required for the shipment | String |
| LANE_NAME | Name of the lane assigned to the shipment | String |
| ASSIGNED_LANE_ID | Identifier for the lane assigned to the shipment | String |
| ASSIGNED_LANE_DETAIL_ID | Identifier for the detail record of the assigned lane | String |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

### Bz_Billing
**Description**: Bronze layer table containing billing information and financial references.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| BILL_TO_POSTAL_CODE | Postal code of the bill-to party | String |
| BILL_TO_STATE_PROV | State or province of the bill-to party | String |
| BILL_OF_LADING_NUMBER | Bill of lading reference number | String |
| BILLING_METHOD | Method used to bill the shipment | String |
| PURCHASE_ORDER | Purchase order number associated with the shipment | String |
| TC_COMPANY_ID | Company identifier within the TMS system | String |
| SHIPMENT_RECON_DTTM | Date and time when the shipment was financially reconciled | DateTime |
| BILL_TO_CODE | Code identifying the bill-to party | String |
| BILL_TO_NAME | Name of the bill-to party | String |
| BILL_TO_ADDRESS | Street address of the bill-to party | String |
| BILL_TO_CITY | City of the bill-to party | String |
| BILL_TO_COUNTRY_CODE | Country code of the bill-to party | String |
| BILL_TO_PHONE_NUMBER | Phone number of the bill-to party | String |
| BILL_TO_TITLE | Title or salutation of the bill-to contact | String |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

### Bz_Business_Partner
**Description**: Bronze layer table containing business partner and vendor information.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| BUSINESS_PARTNER_ID | Identifier for the business partner or vendor | String |
| REF_SHIPMENT_NBR | Reference shipment number linked to this shipment | String |
| CUSTOMER_ID | Identifier for the customer associated with the shipment | String |
| BUSINESS_PROCESS | Business process category associated with the shipment | String |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

### Bz_User_Role
**Description**: Bronze layer table containing user role information for shipment creation and updates.

| Column Name | Description | Data Type |
|-------------|-------------|----------|
| CREATED_SOURCE_TYPE | Role type of the user or system that created the shipment | String |
| LAST_UPDATED_SOURCE_TYPE | Role type of the user or system that last updated the shipment | String |
| CREATED_SOURCE | System or process that created the shipment record | String |
| LAST_UPDATED_SOURCE | System or process that last updated the shipment record | String |
| TRANS_PLAN_OWNER | Owner or planner responsible for the transportation plan | String |
| load_timestamp | Timestamp when the record was loaded into the Bronze layer | DateTime |
| update_timestamp | Timestamp when the record was last updated in the Bronze layer | DateTime |
| source_system | Source system identifier from which the data originated | String |

## 3. Audit Table Design

### Bz_Audit_Log
**Description**: Audit table to track all data loading and processing activities in the Bronze layer.

| Field Name | Description | Data Type |
|------------|-------------|----------|
| record_id | Unique identifier for each audit record | String |
| source_table | Name of the source table being processed | String |
| load_timestamp | Timestamp when the data loading process started | DateTime |
| processed_by | System or user identifier that processed the data | String |
| processing_time | Duration of the processing operation in seconds | Decimal |
| status | Status of the processing operation (SUCCESS, FAILED, IN_PROGRESS) | String |
| error_message | Error message if processing failed | String |
| records_processed | Number of records processed in the operation | Integer |
| records_inserted | Number of records successfully inserted | Integer |
| records_updated | Number of records successfully updated | Integer |
| records_failed | Number of records that failed processing | Integer |

## 4. Conceptual Data Model Diagram (Tabular Form)

| Source Entity | Relationship Key Field | Target Entity | Relationship Type |
|---------------|------------------------|---------------|------------------|
| Bz_Shipment | ASSIGNED_CARRIER_CODE | Bz_Carrier | Many-to-One |
| Bz_Shipment | O_FACILITY_NUMBER | Bz_Facility | Many-to-One |
| Bz_Shipment | D_FACILITY_NUMBER | Bz_Facility | Many-to-One |
| Bz_Shipment | BILL_OF_LADING_NUMBER | Bz_Billing | Many-to-One |
| Bz_Shipment | BUSINESS_PARTNER_ID | Bz_Business_Partner | Many-to-One |
| Bz_Shipment | CREATED_SOURCE_TYPE | Bz_User_Role | Many-to-One |
| Bz_Shipment | DISTANCE | Bz_Route | Many-to-One |
| Bz_Shipment | ASSIGNED_LANE_ID | Bz_Route | Many-to-One |

## 5. Design Rationale and Key Assumptions

### Design Decisions:
1. **Table Naming Convention**: All Bronze layer tables use the "Bz_" prefix to clearly identify them as Bronze layer entities.
2. **Data Preservation**: All source columns are preserved in the Bronze layer to maintain data lineage and enable future analysis.
3. **Metadata Columns**: Standard metadata columns (load_timestamp, update_timestamp, source_system) are added to all tables for tracking and auditing.
4. **PII Identification**: Personal and sensitive information fields are clearly identified for compliance with data privacy regulations.
5. **Logical Data Types**: Generic logical data types are used (String, Decimal, DateTime, Integer) rather than physical storage types.

### Key Assumptions:
1. **Source System**: Data originates from a Transportation Management System (TMS) with the SHIPMENT table as the primary source.
2. **Data Quality**: Source data may contain nulls and inconsistencies that will be addressed in Silver layer processing.
3. **Incremental Loading**: The Bronze layer supports both full and incremental data loading patterns.
4. **Audit Requirements**: All data processing activities must be tracked for compliance and troubleshooting purposes.
5. **Scalability**: The model is designed to handle large volumes of shipment data with appropriate partitioning strategies.

## 6. API Cost

apiCost: 0.000000 // Cost consumed by the API for this call (in USD)