# TMS Shipment Application Data Model

## SHIPMENT Table — Column Definitions

| Table Name | Column Name | Business Description | Data Type | Constraints | Domain Values |
|------------|-------------|----------------------|-----------|-------------|---------------|
| SHIPMENT | ACCESSORIAL_COST | Total accessorial charges applied to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | ACCESSORIAL_COST_TO_CARRIER | Accessorial cost passed to the carrier | DECIMAL(10,2) | Nullable | N/A |
| | ACTUAL_COST | Actual total cost of the shipment | DECIMAL(10,2) | Nullable | N/A |
| | ACTUAL_COST_CURRENCY_CODE | Currency code for the actual shipment cost | VARCHAR(10) | Nullable | N/A |
| | APPT_DOOR_SCHED_TYPE | Appointment door scheduling type | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_BROKER_CARRIER_CODE | Code identifying the broker carrier assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_BROKER_CARRIER_ID | Unique identifier for the broker carrier assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_CARRIER_CODE | Code identifying the primary carrier assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_CARRIER_ID | Unique identifier for the primary carrier assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_CM_SHIPMENT_ID | Identifier for the carrier management shipment assignment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_CUSTOMER_ID | Identifier for the customer assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_EQUIPMENT_ID | Identifier for the equipment assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_LANE_DETAIL_ID | Identifier for the detail record of the assigned lane | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_LANE_ID | Identifier for the lane assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_MOT_ID | Identifier for the mode of transport assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_SCNDR_CARRIER_CODE | Code identifying the secondary carrier assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_SCNDR_CARRIER_ID | Unique identifier for the secondary carrier assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_SERVICE_LEVEL_ID | Identifier for the service level assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | ASSIGNED_SHIP_VIA | Ship-via method assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | AUTH_NBR | Authorization number associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | AVAILABLE_DTTM | Date and time when the shipment became available | DATETIME | Nullable | N/A |
| | BASELINE_COST | Baseline cost used for cost comparison (removed from reporting) | DECIMAL(10,2) | Nullable | N/A |
| | BASELINE_COST_CURRENCY_CODE | Currency code for the baseline shipment cost | VARCHAR(10) | Nullable | N/A |
| | BILL_OF_LADING_NUMBER | Bill of lading reference number for the shipment | VARCHAR(100) | Nullable | N/A |
| | BILL_TO_ADDRESS | Street address of the bill-to party | VARCHAR(300) | Nullable | N/A |
| | BILL_TO_CITY | City of the bill-to party | VARCHAR(100) | Nullable | N/A |
| | BILL_TO_CODE | Code identifying the bill-to party | VARCHAR(50) | Nullable | N/A |
| | BILL_TO_COUNTRY_CODE | Country code of the bill-to party | VARCHAR(10) | Nullable | N/A |
| | BILL_TO_NAME | Name of the bill-to party | VARCHAR(200) | Nullable | N/A |
| | BILL_TO_PHONE_NUMBER | Phone number of the bill-to party | VARCHAR(50) | Nullable | N/A |
| | BILL_TO_POSTAL_CODE | Postal code of the bill-to party | VARCHAR(20) | Nullable | N/A |
| | BILL_TO_STATE_PROV | State or province of the bill-to party | VARCHAR(50) | Nullable | N/A |
| | BILL_TO_TITLE | Title or salutation of the bill-to contact | VARCHAR(50) | Nullable | N/A |
| | BILLING_METHOD | Method used to bill the shipment | VARCHAR(50) | Nullable | N/A |
| | BK_ARRIVAL_DTTM | Booking arrival date and time | DATETIME | Nullable | N/A |
| | BK_ARRIVAL_TZ | Timezone for the booking arrival date and time | VARCHAR(50) | Nullable | N/A |
| | BK_CUTOFF_DTTM | Booking cutoff date and time | DATETIME | Nullable | N/A |
| | BK_CUTOFF_TZ | Timezone for the booking cutoff date and time | VARCHAR(50) | Nullable | N/A |
| | BK_D_FACILITY_ALIAS_ID | Alias identifier for the booking destination facility | VARCHAR(50) | Nullable | N/A |
| | BK_D_FACILITY_ID | Identifier for the booking destination facility | VARCHAR(50) | Nullable | N/A |
| | BK_DEPARTURE_DTTM | Booking departure date and time | DATETIME | Nullable | N/A |
| | BK_DEPARTURE_TZ | Timezone for the booking departure date and time | VARCHAR(50) | Nullable | N/A |
| | BK_FORWARDER_AIRWAY_BILL | Forwarder airway bill number from booking | VARCHAR(100) | Nullable | N/A |
| | BK_MASTER_AIRWAY_BILL | Master airway bill number from booking | VARCHAR(100) | Nullable | N/A |
| | BK_O_FACILITY_ALIAS_ID | Alias identifier for the booking origin facility | VARCHAR(50) | Nullable | N/A |
| | BK_O_FACILITY_ID | Identifier for the booking origin facility | VARCHAR(50) | Nullable | N/A |
| | BK_PICKUP_DTTM | Booking pickup date and time | DATETIME | Nullable | N/A |
| | BK_PICKUP_TZ | Timezone for the booking pickup date and time | VARCHAR(50) | Nullable | N/A |
| | BK_RESOURCE_NAME_EXTERNAL | External resource name associated with the booking | VARCHAR(100) | Nullable | N/A |
| | BK_RESOURCE_REF_EXTERNAL | External resource reference associated with the booking | VARCHAR(100) | Nullable | N/A |
| | BOOKING_ID | Unique identifier for the freight booking | VARCHAR(50) | Nullable | N/A |
| | BOOKING_REF_CARRIER | Carrier-side reference number for the booking | VARCHAR(100) | Nullable | N/A |
| | BOOKING_REF_SHIPPER | Shipper-side reference number for the booking | VARCHAR(100) | Nullable | N/A |
| | BROKER_CARRIER_ID | Identifier for the broker carrier associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | BROKER_REF | Broker reference number for the shipment | VARCHAR(100) | Nullable | N/A |
| | BUDG_CM_DISCOUNT | Budget carrier management discount applied to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | BUDG_CURRENCY_CODE | Currency code for the budget cost fields | VARCHAR(10) | Nullable | N/A |
| | BUDG_NORMALIZED_TOTAL_COST | Normalized total budgeted cost (not used) | DECIMAL(10,2) | Nullable | N/A |
| | BUDG_TOTAL_COST | Total budgeted cost for the shipment (not used) | DECIMAL(10,2) | Nullable | N/A |
| | BUSINESS_PARTNER_ID | Identifier for the business partner or vendor linked to the shipment | VARCHAR(50) | Nullable | N/A |
| | BUSINESS_PROCESS | Business process category associated with the shipment | VARCHAR(100) | Nullable | N/A |
| | CARRIER_CHARGE | Charge amount billed by the carrier | DECIMAL(10,2) | Nullable | N/A |
| | CFMF_STATUS | Status of the CFMF (carrier freight management flow) process | VARCHAR(50) | Nullable | N/A |
| | CM_DISCOUNT | Carrier management discount applied to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | CMID | Carrier management identifier for the shipment | VARCHAR(50) | Nullable | N/A |
| | COD_AMOUNT | Cash on delivery amount for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | COD_CURRENCY_CODE | Currency code for the cash on delivery amount | VARCHAR(10) | Nullable | N/A |
| | COMMODITY_CLASS | Freight commodity class for rating purposes | VARCHAR(50) | Nullable | N/A |
| | COMMODITY_CODE_ID | Identifier for the commodity code assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | CONFIG_CYCLE_SEQ | Configuration cycle sequence number for optimization processing | INT | Nullable | N/A |
| | CONS_ADDR_CODE | Consolidation address code associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | CONS_LOCN_ID | Consolidation location identifier | VARCHAR(50) | Nullable | N/A |
| | CONS_RUN_ID | Consolidation run identifier | VARCHAR(50) | Nullable | N/A |
| | CONTRACT_NUMBER | Contract number governing the shipment pricing | VARCHAR(100) | Nullable | N/A |
| | COST_BREAKUP | Detailed breakdown of shipment cost components | VARCHAR(500) | Nullable | N/A |
| | CREATED_DTTM | Date and time when the shipment record was created | DATETIME | Not Null | N/A |
| | CREATED_SOURCE | System or process that created the shipment record | VARCHAR(100) | Not Null | N/A |
| | CREATED_SOURCE_TYPE | Role type of the user or system that created the shipment | VARCHAR(100) | Nullable | N/A |
| | CREATION_TYPE | Type of creation process used to generate the shipment | VARCHAR(50) | Nullable | N/A |
| | CURRENCY_CODE | Default currency code used for this shipment | VARCHAR(10) | Nullable | N/A |
| | CURRENCY_DTTM | Date and time of the currency rate used for this shipment | DATETIME | Nullable | N/A |
| | CUST_FRGT_CHARGE | Customer freight charge applied to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | CUSTOMER_CREDIT_LIMIT_ID | Credit limit identifier for the customer on this shipment | VARCHAR(50) | Nullable | N/A |
| | CUSTOMER_ID | Identifier for the customer associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | CYCLE_DEADLINE_DTTM | Optimization cycle deadline date and time | DATETIME | Nullable | N/A |
| | CYCLE_EXECUTION_DTTM | Date and time the optimization cycle was executed | DATETIME | Nullable | N/A |
| | CYCLE_RESP_DEADLINE_TZ | Timezone for the cycle response deadline | VARCHAR(50) | Nullable | N/A |
| | D_ADDRESS | Street address of the destination facility | VARCHAR(300) | Nullable | N/A |
| | D_CITY | City of the destination facility | VARCHAR(100) | Nullable | N/A |
| | D_COUNTRY_CODE | Country code of the destination facility | VARCHAR(10) | Nullable | N/A |
| | D_COUNTY | County of the destination facility | VARCHAR(100) | Nullable | N/A |
| | D_FACILITY_ID | Unique identifier for the destination facility (last stop) | VARCHAR(50) | Nullable | N/A |
| | D_FACILITY_NUMBER | Facility number of the destination (last stop) | VARCHAR(50) | Nullable | N/A |
| | D_POSTAL_CODE | Postal code of the destination facility | VARCHAR(20) | Nullable | N/A |
| | D_STATE_PROV | State or province of the destination facility | VARCHAR(50) | Nullable | N/A |
| | D_STOP_LOCATION_NAME | Name of the destination stop location | VARCHAR(200) | Nullable | N/A |
| | D_TANDEM_FACILITY | Tandem facility identifier at the destination | VARCHAR(50) | Nullable | N/A |
| | D_TANDEM_FACILITY_ALIAS | Alias for the tandem facility at the destination | VARCHAR(50) | Nullable | N/A |
| | DAYS_TO_DELIVER | Number of days planned or actual for delivery | INT | Nullable | N/A |
| | DECLARED_VALUE | Declared monetary value of the shipment contents | DECIMAL(10,2) | Nullable | N/A |
| | DELAY_TYPE | Type of delay associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | DELIVERY_END_DTTM | Planned delivery window end date and time | DATETIME | Nullable | N/A |
| | DELIVERY_REQ | Delivery requirements or special instructions | VARCHAR(200) | Nullable | N/A |
| | DELIVERY_START_DTTM | Planned delivery window start date and time | DATETIME | Nullable | N/A |
| | DELIVERY_TZ | Timezone for the delivery window | VARCHAR(50) | Nullable | N/A |
| | DESIGNATED_DRIVER_TYPE | Type of driver designated for the shipment | VARCHAR(50) | Nullable | N/A |
| | DESIGNATED_TRACTOR_CODE | Code for the tractor designated for the shipment | VARCHAR(50) | Nullable | N/A |
| | DIRECT_DISTANCE | Straight-line distance between origin and destination | DECIMAL(10,2) | Nullable | N/A |
| | DISTANCE | Total route distance for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | DISTANCE_UOM | Unit of measure for the shipment distance (e.g., miles, km) | VARCHAR(20) | Nullable | MI, KM |
| | DOOR | Door number assigned to the shipment at the facility | VARCHAR(50) | Nullable | N/A |
| | DRIVER_TYPE_ID | Identifier for the type of driver required | VARCHAR(50) | Nullable | N/A |
| | DROPOFF_PICKUP | Indicates whether the shipment is a drop-off or pickup | VARCHAR(20) | Nullable | DROPOFF, PICKUP |
| | DSG_CARRIER_CODE | Designated carrier code; for DC-to-Store used as Master Lane or Static Route reference | VARCHAR(50) | Nullable | N/A |
| | DSG_CARRIER_ID | Unique identifier for the designated carrier | VARCHAR(50) | Nullable | N/A |
| | DSG_EQUIPMENT_ID | Identifier for the designated equipment | VARCHAR(50) | Nullable | N/A |
| | DSG_MOT_ID | Identifier for the designated mode of transport | VARCHAR(50) | Nullable | N/A |
| | DSG_SCNDR_CARRIER_CODE | Code for the designated secondary carrier | VARCHAR(50) | Nullable | N/A |
| | DSG_SCNDR_CARRIER_ID | Identifier for the designated secondary carrier | VARCHAR(50) | Nullable | N/A |
| | DSG_SERVICE_LEVEL_ID | Identifier for the designated service level | VARCHAR(50) | Nullable | N/A |
| | DSG_VOYAGE_FLIGHT | Voyage or flight number for the designated booking | VARCHAR(100) | Nullable | N/A |
| | DT_PARAM_SET_ID | Date-time parameter set identifier used in scheduling | VARCHAR(50) | Nullable | N/A |
| | DV_CURRENCY_CODE | Currency code for the declared value | VARCHAR(10) | Nullable | N/A |
| | EARNED_INCOME | Income earned on the shipment | DECIMAL(10,2) | Nullable | N/A |
| | EARNED_INCOME_CURRENCY_CODE | Currency code for the earned income amount | VARCHAR(10) | Nullable | N/A |
| | EQUIP_UTIL_PER | Equipment utilization percentage for the shipment | DECIMAL(5,2) | Nullable | 0.0 to 100.0 |
| | EQUIPMENT_TYPE | Type of equipment used or required for the shipment | VARCHAR(50) | Nullable | N/A |
| | ESTIMATED_COST | Estimated cost of the shipment prior to execution | DECIMAL(10,2) | Nullable | N/A |
| | ESTIMATED_DISPATCH_DTTM | Estimated date and time for dispatch | DATETIME | Nullable | N/A |
| | ESTIMATED_SAVINGS | Estimated cost savings achieved on the shipment | DECIMAL(10,2) | Nullable | N/A |
| | EVENT_IND_TYPEID | Event indicator type identifier for the shipment | VARCHAR(50) | Nullable | N/A |
| | EXT_SYS_SHIPMENT_ID | Shipment identifier from an external system | VARCHAR(100) | Nullable | N/A |
| | EXTRACTION_DTTM | Date and time when the record was extracted from the source system | DATETIME | Nullable | N/A |
| | FACILITY_SCHEDULE_ID | Identifier for the facility schedule linked to the shipment | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_CARRIER_CODE | Code of a carrier identified as feasible during optimization | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_CARRIER_ID | Identifier for the feasible carrier identified during optimization | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_DRIVER_TYPE | Driver type identified as feasible for the shipment | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_EQUIPMENT_ID | Primary equipment identifier identified as feasible | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_EQUIPMENT2_ID | Secondary equipment identifier identified as feasible | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_MOT_ID | Mode of transport identified as feasible for the shipment | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_SERVICE_LEVEL_ID | Service level identified as feasible for the shipment | VARCHAR(50) | Nullable | N/A |
| | FEASIBLE_VOYAGE_FLIGHT | Voyage or flight identified as feasible for the shipment | VARCHAR(100) | Nullable | N/A |
| | FINANCIAL_WT | Financial weight used for cost calculation purposes | DECIMAL(10,3) | Nullable | N/A |
| | FIRST_UPDATE_SENT_TO_PKMS | Indicator whether the first update was sent to the warehouse system | VARCHAR(1) | Nullable | Y, N |
| | FRT_REV_ACCESSORIAL_CHARGE | Freight revenue accessorial charge amount | DECIMAL(10,2) | Nullable | N/A |
| | FRT_REV_CM_DISCOUNT | Freight revenue carrier management discount | DECIMAL(10,2) | Nullable | N/A |
| | FRT_REV_LINEHAUL_CHARGE | Freight revenue linehaul charge amount | DECIMAL(10,2) | Nullable | N/A |
| | FRT_REV_RATING_LANE_DETAIL_ID | Rating lane detail identifier for freight revenue | VARCHAR(50) | Nullable | N/A |
| | FRT_REV_RATING_LANE_ID | Rating lane identifier for freight revenue | VARCHAR(50) | Nullable | N/A |
| | FRT_REV_SPOT_CHARGE | Spot charge amount for freight revenue | DECIMAL(10,2) | Nullable | N/A |
| | FRT_REV_SPOT_CHARGE_CURR_CODE | Currency code for the freight revenue spot charge | VARCHAR(10) | Nullable | N/A |
| | FRT_REV_STOP_CHARGE | Stop charge amount for freight revenue | DECIMAL(10,2) | Nullable | N/A |
| | GRS_MAX_SHIPMENT_STATUS | Maximum shipment status within a global routing session | VARCHAR(50) | Nullable | N/A |
| | HAS_ALERTS | Indicates whether the shipment has active alerts | VARCHAR(1) | Nullable | Y, N |
| | HAS_EM_NOTIFY_FLAG | Flag indicating whether event management notifications are active | VARCHAR(1) | Nullable | Y, N |
| | HAS_IMPORT_ERROR | Flag indicating whether an import error exists on the shipment | VARCHAR(1) | Nullable | Y, N |
| | HAS_NOTES | Indicates whether notes have been added to the shipment | VARCHAR(1) | Nullable | Y, N |
| | HAS_SOFT_CHECK_ERROR | Flag indicating a soft validation check error exists | VARCHAR(1) | Nullable | Y, N |
| | HAS_TRACKING_MSG | Indicates whether tracking messages exist for the shipment | VARCHAR(1) | Nullable | Y, N |
| | HAULING_CARRIER | Carrier physically hauling the shipment | VARCHAR(100) | Nullable | N/A |
| | HAZMAT_CERT_CONTACT | Contact information for hazmat certification | VARCHAR(200) | Nullable | N/A |
| | HAZMAT_CERT_DECLARATION | Hazmat certification declaration statement | VARCHAR(500) | Nullable | N/A |
| | HIBERNATE_VERSION | Hibernate ORM version number for the record | INT | Nullable | N/A |
| | HUB_ID | Identifier for the hub facility associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | INBOUND_REGION_ID | Region identifier for the inbound leg of the shipment | VARCHAR(50) | Nullable | N/A |
| | INCOTERM_ID | Incoterm governing the terms of trade for the shipment | VARCHAR(50) | Nullable | N/A |
| | INSURANCE_STATUS | Status of insurance coverage for the shipment | VARCHAR(50) | Nullable | N/A |
| | IS_ASSOCIATED_TO_OUTBOUND | Flag indicating whether the shipment is linked to an outbound shipment | VARCHAR(1) | Nullable | Y, N |
| | IS_AUTO_DELIVERED | Flag indicating the shipment was automatically marked as delivered | VARCHAR(1) | Nullable | Y, N |
| | IS_BOOKING_REQUIRED | Flag indicating whether a booking is required for the shipment | VARCHAR(1) | Nullable | Y, N |
| | IS_CM_OPTION_GEN_ACTIVE | Flag indicating carrier management option generation is active | VARCHAR(1) | Nullable | Y, N |
| | IS_COOLER_AT_NOSE | Flag indicating cooler unit is required at the nose of the trailer | VARCHAR(1) | Nullable | Y, N |
| | IS_FILO | Flag indicating first-in last-out loading sequence | VARCHAR(1) | Nullable | Y, N |
| | IS_GRS_OPT_CYCLE_RUNNING | Flag indicating a global routing session optimization cycle is running | VARCHAR(1) | Nullable | Y, N |
| | IS_HAZMAT | Flag indicating the shipment contains hazardous materials | VARCHAR(1) | Nullable | Y, N |
| | IS_MANUAL_ASSIGN | Flag indicating the carrier was manually assigned | VARCHAR(1) | Nullable | Y, N |
| | IS_MISROUTED | Flag indicating the shipment was identified as misrouted | VARCHAR(1) | Nullable | Y, N |
| | IS_PERISHABLE | Flag indicating the shipment contains perishable goods | VARCHAR(1) | Nullable | Y, N |
| | IS_SHIPMENT_CANCELLED | Flag indicating the shipment has been cancelled | VARCHAR(1) | Nullable | Y, N |
| | IS_SHIPMENT_RECONCILED | Flag indicating the shipment has been financially reconciled | VARCHAR(1) | Nullable | Y, N |
| | IS_TIME_FEAS_ENABLED | Flag indicating time feasibility checks are enabled | VARCHAR(1) | Nullable | Y, N |
| | IS_WAVE_MAN_CHANGED | Flag indicating the wave management assignment was manually changed | VARCHAR(1) | Nullable | Y, N |
| | LANE_NAME | Name of the lane assigned to the shipment | VARCHAR(200) | Nullable | N/A |
| | LAST_CM_OPTION_GEN_DTTM | Date and time of the last carrier management option generation | DATETIME | Nullable | N/A |
| | LAST_RS_NOTIFICATION_DTTM | Date and time of the last routing session notification | DATETIME | Nullable | N/A |
| | LAST_RUN_GRS_DTTM | Date and time of the last global routing session run | DATETIME | Nullable | N/A |
| | LAST_SELECTOR_RUN_DTTM | Date and time of the last carrier selector run | DATETIME | Nullable | N/A |
| | LAST_UPDATED_DTTM | Date and time when the shipment record was last updated | DATETIME | Nullable | N/A |
| | LAST_UPDATED_SOURCE | System or process that last updated the shipment record | VARCHAR(100) | Nullable | N/A |
| | LAST_UPDATED_SOURCE_TYPE | Role type of the user or system that last updated the shipment | VARCHAR(100) | Nullable | N/A |
| | LEFT_WT | Weight on the left side of the load for balance calculation | DECIMAL(10,3) | Nullable | N/A |
| | LH_PAYEE_CARRIER_CODE | Code for the carrier that is the payee for linehaul charges | VARCHAR(50) | Nullable | N/A |
| | LH_PAYEE_CARRIER_ID | Identifier for the carrier that is the payee for linehaul charges | VARCHAR(50) | Nullable | N/A |
| | LINEHAUL_COST | Total linehaul freight cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | LOADING_SEQ_ORD | Loading sequence order for the shipment on the vehicle | INT | Nullable | N/A |
| | LOC_REFERENCE | Location reference identifier associated with the shipment | VARCHAR(100) | Nullable | N/A |
| | LPN_ASSIGNMENT_STOPPED | Flag indicating LPN assignment processing has been stopped | VARCHAR(1) | Nullable | Y, N |
| | MANIFEST_ID | Identifier for the manifest this shipment belongs to | VARCHAR(50) | Nullable | N/A |
| | MARGIN | Margin amount calculated for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | MAX_NBR_OF_CTNS | Maximum number of cartons allowed on the shipment | INT | Nullable | N/A |
| | MERCHANDIZING_DEPARTMENT_ID | Merchandising department identifier linked to the shipment | VARCHAR(50) | Nullable | N/A |
| | MIN_RATE | Minimum rate applicable to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | MONETARY_VALUE | Total monetary value of the shipment contents | DECIMAL(10,2) | Nullable | N/A |
| | MOVE_TYPE | Type of movement for the shipment (e.g., inbound, outbound, transfer) | VARCHAR(50) | Nullable | N/A |
| | MV_CURRENCY_CODE | Currency code for the monetary value of the shipment | VARCHAR(10) | Nullable | N/A |
| | NORM_SPOT_CHARGE_AND_PAYEE_ACC | Normalized total of spot charge and payee accessorial amounts | DECIMAL(10,2) | Nullable | N/A |
| | NORMALIZED_BASELINE_COST | Normalized baseline cost for cross-currency comparison | DECIMAL(10,2) | Nullable | N/A |
| | NORMALIZED_MARGIN | Normalized margin for cross-currency comparison (not used) | DECIMAL(10,2) | Nullable | N/A |
| | NORMALIZED_TOTAL_COST | Normalized total shipment cost for cross-currency comparison (not used) | DECIMAL(10,2) | Nullable | N/A |
| | NORMALIZED_TOTAL_REVENUE | Normalized total revenue for cross-currency comparison | DECIMAL(10,2) | Nullable | N/A |
| | NUM_CHARGE_LAYOVERS | Number of charge-incurring layovers on the shipment route | INT | Nullable | N/A |
| | NUM_DOCKS | Number of dock doors used for the shipment | INT | Nullable | N/A |
| | NUM_STOPS | Total number of stops on the shipment route | INT | Nullable | N/A |
| | O_ADDRESS | Street address of the origin facility | VARCHAR(300) | Nullable | N/A |
| | O_CITY | City of the origin facility | VARCHAR(100) | Nullable | N/A |
| | O_COUNTRY_CODE | Country code of the origin facility | VARCHAR(10) | Nullable | N/A |
| | O_COUNTY | County of the origin facility | VARCHAR(100) | Nullable | N/A |
| | O_FACILITY_ID | Unique identifier for the origin facility (first stop) | VARCHAR(50) | Nullable | N/A |
| | O_FACILITY_NUMBER | Facility number of the origin (first stop) | VARCHAR(50) | Nullable | N/A |
| | O_POSTAL_CODE | Postal code of the origin facility | VARCHAR(20) | Nullable | N/A |
| | O_STATE_PROV | State or province of the origin facility | VARCHAR(50) | Nullable | N/A |
| | O_STOP_LOCATION_NAME | Name of the origin stop location | VARCHAR(200) | Nullable | N/A |
| | O_TANDEM_FACILITY | Tandem facility identifier at the origin | VARCHAR(50) | Nullable | N/A |
| | O_TANDEM_FACILITY_ALIAS | Alias for the tandem facility at the origin | VARCHAR(50) | Nullable | N/A |
| | OCEAN_ROUTING_STAGE | Stage in the ocean routing process for this shipment | VARCHAR(50) | Nullable | N/A |
| | ON_TIME_INDICATOR | Indicates whether the shipment was delivered on time | VARCHAR(20) | Nullable | ON_TIME, LATE, EARLY |
| | ORDER_QTY | Order quantity associated with the shipment | DECIMAL(10,3) | Nullable | N/A |
| | ORIG_BUDG_TOTAL_COST | Original budgeted total cost before any revisions | DECIMAL(10,2) | Nullable | N/A |
| | OUT_OF_ROUTE_DISTANCE | Distance travelled beyond the direct route | DECIMAL(10,2) | Nullable | N/A |
| | OUTBOUND_REGION_ID | Region identifier for the outbound leg of the shipment | VARCHAR(50) | Nullable | N/A |
| | PACKAGING | Packaging type or description for the shipment | VARCHAR(100) | Nullable | N/A |
| | PAPERWORK_START_DTTM | Date and time when shipment paperwork processing began | DATETIME | Nullable | N/A |
| | PAYEE_CARRIER_ID | Identifier for the carrier that will receive payment | VARCHAR(50) | Nullable | N/A |
| | PICK_START_DATE | Date when picking of the shipment began | DATETIME | Nullable | N/A |
| | PICKUP_END_DTTM | Planned pickup window end date and time | DATETIME | Nullable | N/A |
| | PICKUP_START_DATE | Planned pickup window start date and time | DATETIME | Nullable | N/A |
| | PICKUP_TZ | Timezone for the pickup window | VARCHAR(50) | Nullable | N/A |
| | PLANNED_VOLUME | Planned volume of the shipment | DECIMAL(10,3) | Nullable | N/A |
| | PLANNED_WEIGHT | Planned weight of the shipment | DECIMAL(10,3) | Nullable | N/A |
| | PLN_ACCESSORL_COST_TO_CARRIER | Planned accessorial cost to be passed to the carrier | DECIMAL(10,2) | Nullable | N/A |
| | PLN_CARRIER_CHARGE | Planned carrier charge for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | PLN_CURRENCY_CODE | Currency code for the planned cost fields | VARCHAR(10) | Nullable | N/A |
| | PLN_LINEHAUL_COST | Planned linehaul cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | PLN_MAX_TEMPERATURE | Maximum planned temperature for temperature-controlled shipments | DECIMAL(5,2) | Nullable | N/A |
| | PLN_MIN_TEMPERATURE | Minimum planned temperature for temperature-controlled shipments | DECIMAL(5,2) | Nullable | N/A |
| | PLN_NORMALIZED_TOTAL_COST | Normalized planned total cost for cross-currency comparison | DECIMAL(10,2) | Nullable | N/A |
| | PLN_RATING_LANE_DETAIL_ID | Rating lane detail identifier used in planned cost calculation | VARCHAR(50) | Nullable | N/A |
| | PLN_RATING_LANE_ID | Rating lane identifier used in planned cost calculation | VARCHAR(50) | Nullable | N/A |
| | PLN_STOP_OFF_COST | Planned stop-off charge for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | PLN_TOTAL_ACCESSORIAL_COST | Planned total accessorial cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | PLN_TOTAL_COST | Planned total cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | PP_SHIPMENT_ID | Parent or predecessor shipment identifier | VARCHAR(50) | Nullable | N/A |
| | PRINT_CONS_BOL | Flag indicating whether a consolidated bill of lading should be printed | VARCHAR(1) | Nullable | Y, N |
| | PRIORITY_TYPE | Priority classification of the shipment | VARCHAR(50) | Nullable | N/A |
| | PRO_NUMBER | Progressive (PRO) number assigned by the carrier | VARCHAR(100) | Nullable | N/A |
| | PROD_SCHED_REF_NUMBER | Production schedule reference number linked to the shipment | VARCHAR(100) | Nullable | N/A |
| | PRODUCT_CLASS_ID | Product class identifier for the goods in the shipment | VARCHAR(50) | Nullable | N/A |
| | PROTECTION_LEVEL_ID | Protection level required for the shipment contents | VARCHAR(50) | Nullable | N/A |
| | PURCHASE_ORDER | Purchase order number associated with the shipment | VARCHAR(100) | Nullable | N/A |
| | QTY_UOM_ID | Unit of measure identifier for quantity fields | VARCHAR(20) | Nullable | N/A |
| | RADIAL_DISTANCE | Radial (straight-line) distance from a reference point | DECIMAL(10,2) | Nullable | N/A |
| | RADIAL_DISTANCE_UOM | Unit of measure for the radial distance | VARCHAR(20) | Nullable | MI, KM |
| | RATE | Rate applied to the shipment for cost calculation | DECIMAL(10,4) | Nullable | N/A |
| | RATE_TYPE | Type of rate applied to the shipment (e.g., flat, per mile) | VARCHAR(50) | Nullable | N/A |
| | RATE_UOM | Unit of measure for the applied rate | VARCHAR(20) | Nullable | N/A |
| | RATING_LANE_DETAIL_ID | Detail-level identifier for the rating lane used | VARCHAR(50) | Nullable | N/A |
| | RATING_LANE_ID | Identifier for the rating lane used for cost calculation | VARCHAR(50) | Nullable | N/A |
| | RATING_QUALIFIER | Qualifier used to determine the applicable rate | VARCHAR(50) | Nullable | N/A |
| | REC_ACCESSORIAL_COST | Recommended accessorial cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | REC_BROKER_CARRIER_CODE | Recommended broker carrier code | VARCHAR(50) | Nullable | N/A |
| | REC_BROKER_CARRIER_ID | Recommended broker carrier identifier | VARCHAR(50) | Nullable | N/A |
| | REC_BUDG_ACCESSORIAL_COST | Recommended budget accessorial cost | DECIMAL(10,2) | Nullable | N/A |
| | REC_BUDG_CM_DISCOUNT | Recommended budget carrier management discount | DECIMAL(10,2) | Nullable | N/A |
| | REC_BUDG_CURRENCY_CODE | Currency code for the recommended budget fields | VARCHAR(10) | Nullable | N/A |
| | REC_BUDG_LINEHAUL_COST | Recommended budget linehaul cost (not used) | DECIMAL(10,2) | Nullable | N/A |
| | REC_BUDG_NORMALIZED_TOTAL_COST | Recommended normalized total budget cost | DECIMAL(10,2) | Nullable | N/A |
| | REC_BUDG_RATING_LANE_DETAIL_ID | Rating lane detail identifier for the recommended budget | VARCHAR(50) | Nullable | N/A |
| | REC_BUDG_RATING_LANE_ID | Rating lane identifier for the recommended budget | VARCHAR(50) | Nullable | N/A |
| | REC_BUDG_STOP_COST | Recommended budget stop cost | DECIMAL(10,2) | Nullable | N/A |
| | REC_BUDG_TOTAL_COST | Recommended total budget cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | REC_CARRIER_CODE | Code of the recommended carrier | VARCHAR(50) | Nullable | N/A |
| | REC_CARRIER_ID | Identifier for the recommended carrier | VARCHAR(50) | Nullable | N/A |
| | REC_CM_DISCOUNT | Recommended carrier management discount | DECIMAL(10,2) | Nullable | N/A |
| | REC_CM_SHIPMENT_ID | Recommended carrier management shipment identifier | VARCHAR(50) | Nullable | N/A |
| | REC_CMID | Recommended carrier management identifier | VARCHAR(50) | Nullable | N/A |
| | REC_COST_BREAKUP | Detailed breakdown of the recommended shipment cost | VARCHAR(500) | Nullable | N/A |
| | REC_CURRENCY_CODE | Currency code for the recommended cost fields | VARCHAR(10) | Nullable | N/A |
| | REC_EQUIPMENT_ID | Recommended equipment identifier | VARCHAR(50) | Nullable | N/A |
| | REC_LANE_DETAIL_ID | Detail-level identifier for the recommended lane | VARCHAR(50) | Nullable | N/A |
| | REC_LANE_ID | Identifier for the recommended lane | VARCHAR(50) | Nullable | N/A |
| | REC_LINEHAUL_COST | Recommended linehaul cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | REC_MARGIN | Margin on the recommended cost option | DECIMAL(10,2) | Nullable | N/A |
| | REC_MOT_ID | Recommended mode of transport identifier | VARCHAR(50) | Nullable | N/A |
| | REC_NORMALIZED_MARGIN | Normalized margin on the recommended option | DECIMAL(10,2) | Nullable | N/A |
| | REC_NORMALIZED_TOTAL_COST | Normalized total cost for the recommended option | DECIMAL(10,2) | Nullable | N/A |
| | REC_RATING_LANE_DETAIL_ID | Rating lane detail identifier for the recommended option | VARCHAR(50) | Nullable | N/A |
| | REC_RATING_LANE_ID | Rating lane identifier for the recommended option | VARCHAR(50) | Nullable | N/A |
| | REC_SERVICE_LEVEL_ID | Recommended service level identifier | VARCHAR(50) | Nullable | N/A |
| | REC_SPOT_CHARGE | Recommended spot charge amount | DECIMAL(10,2) | Nullable | N/A |
| | REC_SPOT_CHARGE_CURRENCY_CODE | Currency code for the recommended spot charge | VARCHAR(10) | Nullable | N/A |
| | REC_STOP_COST | Recommended stop charge cost | DECIMAL(10,2) | Nullable | N/A |
| | REC_TOTAL_COST | Recommended total cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | RECEIVED_DTTM | Date and time when the shipment was received at the destination | DATETIME | Nullable | N/A |
| | REF_SHIPMENT_NBR | Reference shipment number linked to this shipment | VARCHAR(100) | Nullable | N/A |
| | REGION_ID | Region identifier associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | REPORTED_COST | Cost reported for the shipment after execution | DECIMAL(10,2) | Nullable | N/A |
| | RETAIN_CONSOLIDATOR_TIMES | Flag indicating consolidator times should be retained during re-planning | VARCHAR(1) | Nullable | Y, N |
| | REVENUE_RATING_LEVEL | Rating level used to determine revenue for the shipment | VARCHAR(50) | Nullable | N/A |
| | RIGHT_WT | Weight on the right side of the load for balance calculation | DECIMAL(10,3) | Nullable | N/A |
| | RS_AREA_ID | Routing session area identifier | VARCHAR(50) | Nullable | N/A |
| | RS_CONFIG_CYCLE_ID | Routing session configuration cycle identifier | VARCHAR(50) | Nullable | N/A |
| | RS_CONFIG_ID | Routing session configuration identifier | VARCHAR(50) | Nullable | N/A |
| | RS_CYCLE_REMAINING | Number of optimization cycles remaining in the routing session | INT | Nullable | N/A |
| | RS_TYPE | Type of routing session applied to the shipment | VARCHAR(50) | Nullable | N/A |
| | RTE_SWC_NBR | Route switch number for the shipment | VARCHAR(50) | Nullable | N/A |
| | RTE_TO | Route-to destination code | VARCHAR(50) | Nullable | N/A |
| | RTE_TYPE | Primary route type for the shipment | VARCHAR(50) | Nullable | N/A |
| | RTE_TYPE_1 | Secondary route type classification | VARCHAR(50) | Nullable | N/A |
| | RTE_TYPE_2 | Tertiary route type classification | VARCHAR(50) | Nullable | N/A |
| | SCHEDULED_PICKUP_DTTM | Scheduled date and time for pickup | DATETIME | Nullable | N/A |
| | SCNDR_CARRIER_ID | Identifier for the secondary carrier on the shipment | VARCHAR(50) | Nullable | N/A |
| | SEAL_NUMBER | Seal number applied to the shipment trailer or container | VARCHAR(100) | Nullable | N/A |
| | SED_GENERATED_FLAG | Flag indicating a Shipper's Export Declaration was generated | VARCHAR(1) | Nullable | Y, N |
| | SENT_TO_CREATE_PKMS | Flag indicating the create instruction was sent to the warehouse system | VARCHAR(1) | Nullable | Y, N |
| | SENT_TO_CREATE_PKMS_DTTM | Date and time the create instruction was sent to the warehouse system | DATETIME | Nullable | N/A |
| | SENT_TO_PKMS | Flag indicating an update was sent to the warehouse system | VARCHAR(1) | Nullable | Y, N |
| | SENT_TO_PKMS_DTTM | Date and time the update was sent to the warehouse system | DATETIME | Nullable | N/A |
| | SERV_AREA_CODE | Service area code associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | SHIP_GROUP_ID | Identifier for the shipment group this shipment belongs to | VARCHAR(50) | Nullable | N/A |
| | SHIPMENT_CLOSED_INDICATOR | Flag indicating the shipment has been closed | VARCHAR(1) | Nullable | Y, N |
| | SHIPMENT_END_DTTM | Date and time when the shipment execution ended | DATETIME | Nullable | N/A |
| | SHIPMENT_ID | Unique identifier for the shipment record | VARCHAR(50) | Primary Key, Not Null | N/A |
| | SHIPMENT_LEG_TYPE | Type of shipment leg (e.g., direct, relay, multi-modal) | VARCHAR(50) | Nullable | N/A |
| | SHIPMENT_RECON_DTTM | Date and time when the shipment was financially reconciled | DATETIME | Nullable | N/A |
| | SHIPMENT_REF_ID | Reference identifier linking related shipments | VARCHAR(100) | Nullable | N/A |
| | SHIPMENT_START_DTTM | Date and time when shipment execution began | DATETIME | Nullable | N/A |
| | SHIPMENT_STATUS | Current transit status of the shipment | VARCHAR(50) | Not Null | PLANNED, IN_TRANSIT, DELIVERED, CANCELLED |
| | SHIPMENT_TYPE | Product class type of the shipment | VARCHAR(50) | Not Null | N/A |
| | SHIPMENT_WIN_ADJ_FLAG | Flag indicating a window adjustment was made to the shipment | VARCHAR(1) | Nullable | Y, N |
| | SIZE1_UOM_ID | Unit of measure for the first size dimension | VARCHAR(20) | Nullable | N/A |
| | SIZE1_VALUE | Value of the first size dimension | DECIMAL(10,3) | Nullable | N/A |
| | SIZE2_UOM_ID | Unit of measure for the second size dimension | VARCHAR(20) | Nullable | N/A |
| | SIZE2_VALUE | Value of the second size dimension | DECIMAL(10,3) | Nullable | N/A |
| | SPOT_CHARGE | Spot charge amount applied to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | SPOT_CHARGE_AND_PAYEE_ACC | Combined spot charge and payee accessorial amount | DECIMAL(10,2) | Nullable | N/A |
| | SPOT_CHARGE_AND_PAYEE_ACC_CC | Currency code for the combined spot charge and payee accessorial | VARCHAR(10) | Nullable | N/A |
| | SPOT_CHARGE_CURRENCY_CODE | Currency code for the spot charge amount | VARCHAR(10) | Nullable | N/A |
| | STAGING_LOCN_ID | Identifier for the staging location for the shipment | VARCHAR(50) | Nullable | N/A |
| | STATIC_ROUTE_ID | Identifier for the static route assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | STATUS_CHANGE_DATE | Date when the shipment status last changed (not used) | DATETIME | Nullable | N/A |
| | STOP_COST | Stop charge cost for the shipment | DECIMAL(10,2) | Nullable | N/A |
| | TANDEM_PATH_ID | Identifier for the tandem routing path | VARCHAR(50) | Nullable | N/A |
| | TARIFF | Tariff code or schedule applied to the shipment | VARCHAR(100) | Nullable | N/A |
| | TC_COMPANY_ID | Company identifier within the TMS system | VARCHAR(50) | Not Null | N/A |
| | TC_SHIPMENT_ID | TMS-assigned shipment identifier | VARCHAR(50) | Not Null | N/A |
| | TEMPERATURE_UOM | Unit of measure for temperature fields on the shipment | VARCHAR(20) | Nullable | C, F |
| | TENDER_DTTM | Date and time when the shipment was tendered to the carrier | DATETIME | Nullable | N/A |
| | TENDER_RESP_DEADLINE_DATE | Deadline date for the carrier to respond to the tender | DATETIME | Nullable | N/A |
| | TENDER_RESP_DEADLINE_TZ | Timezone for the tender response deadline | VARCHAR(50) | Nullable | N/A |
| | TOTAL_COST | Total shipment cost including all charges | DECIMAL(10,2) | Nullable | N/A |
| | TOTAL_COST_EXCL_TAX | Total shipment cost excluding tax | DECIMAL(10,2) | Nullable | N/A |
| | TOTAL_REVENUE | Total revenue generated by the shipment | DECIMAL(10,2) | Nullable | N/A |
| | TOTAL_REVENUE_CURRENCY_CODE | Currency code for the total revenue amount | VARCHAR(10) | Nullable | N/A |
| | TOTAL_TAX_AMOUNT | Total tax amount applied to the shipment | DECIMAL(10,2) | Nullable | N/A |
| | TOTAL_TIME | Total elapsed time for the shipment from pickup to delivery | DECIMAL(10,2) | Nullable | N/A |
| | TRACKING_MSG_PROBLEM | Flag or description of a problem with tracking messages | VARCHAR(200) | Nullable | N/A |
| | TRACTOR_NUMBER | Tractor unit number assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | TRAILER_NUMBER | Trailer number assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | TRANS_PLAN_OWNER | Owner or planner responsible for the transportation plan | VARCHAR(100) | Nullable | N/A |
| | TRANS_RESP_CODE | Transport responsibility code indicating who manages the freight | VARCHAR(50) | Nullable | N/A |
| | TRLR_GEN_CODE | Trailer generation code | VARCHAR(50) | Nullable | N/A |
| | TRLR_SIZE | Size category of the trailer assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | TRLR_TYPE | Type of trailer assigned to the shipment | VARCHAR(50) | Nullable | N/A |
| | UN_NUMBER_ID | UN hazmat number identifier for dangerous goods | VARCHAR(50) | Nullable | N/A |
| | UPDATE_SENT | Flag indicating an update notification was sent for the shipment | VARCHAR(1) | Nullable | Y, N |
| | USE_BROKER_AS_CARRIER | Flag indicating the broker should be treated as the carrier | VARCHAR(1) | Nullable | Y, N |
| | VEHICLE_CHECK_START_DTTM | Date and time when the vehicle check process started | DATETIME | Nullable | N/A |
| | VOLUME_UOM_ID_BASE | Base unit of measure identifier for volume fields | VARCHAR(20) | Nullable | N/A |
| | WAVE_ID | Wave planning identifier associated with the shipment | VARCHAR(50) | Nullable | N/A |
| | WAYPOINT_HANDLING_COST | Handling cost at waypoint stops along the route | DECIMAL(10,2) | Nullable | N/A |
| | WAYPOINT_TOTAL_COST | Total cost including all waypoint charges | DECIMAL(10,2) | Nullable | N/A |
| | WEIGHT_UOM_ID_BASE | Base unit of measure identifier for weight fields | VARCHAR(20) | Nullable | N/A |
| | WMS_STATUS_CODE | Status code from the warehouse management system for this shipment | VARCHAR(50) | Nullable | N/A |

---

## Sample Data — 3 Representative Rows

> The following table shows sample values for the most business-critical columns. Nullable columns not relevant to each scenario are omitted for readability.

| Column Name | Row 1 — Planned Outbound (Truck) | Row 2 — In-Transit (Hazmat, Perishable) | Row 3 — Delivered (Cancelled BOL) |
|---|---|---|---|
| **SHIPMENT_ID** | SHP-20260001 | SHP-20260002 | SHP-20260003 |
| **TC_SHIPMENT_ID** | TCS-00100001 | TCS-00100002 | TCS-00100003 |
| **TC_COMPANY_ID** | COMP-001 | COMP-001 | COMP-001 |
| **SHIPMENT_STATUS** | PLANNED | IN_TRANSIT | DELIVERED |
| **SHIPMENT_TYPE** | OUTBOUND | OUTBOUND | INBOUND |
| **SHIPMENT_LEG_TYPE** | DIRECT | DIRECT | RELAY |
| **MOVE_TYPE** | OUTBOUND | OUTBOUND | INBOUND |
| **CREATED_DTTM** | 2026-03-01 08:00:00 | 2026-03-10 06:30:00 | 2026-02-15 09:00:00 |
| **CREATED_SOURCE** | TMS_UI | EDI_INTEGRATION | TMS_UI |
| **CREATED_SOURCE_TYPE** | PLANNER | SYSTEM | PLANNER |
| **LAST_UPDATED_DTTM** | 2026-03-20 14:22:00 | 2026-03-24 11:05:00 | 2026-03-01 17:45:00 |
| **LAST_UPDATED_SOURCE** | TMS_UI | CARRIER_PORTAL | TMS_UI |
| **BILL_OF_LADING_NUMBER** | BOL-2026-00001 | BOL-2026-00002 | BOL-2026-00003 |
| **PRO_NUMBER** | NULL | PRO-78543210 | PRO-65412300 |
| **PURCHASE_ORDER** | PO-45001 | PO-45002 | PO-44890 |
| **CONTRACT_NUMBER** | CNT-2025-FTL-01 | CNT-2025-FTL-01 | CNT-2025-LTL-03 |
| **ASSIGNED_CARRIER_CODE** | FEDX | UPSFR | XPOLS |
| **ASSIGNED_CARRIER_ID** | CARR-FEDX-001 | CARR-UPS-002 | CARR-XPO-003 |
| **ASSIGNED_MOT_ID** | TRUCK | TRUCK | TRUCK |
| **ASSIGNED_SERVICE_LEVEL_ID** | STD-GND | PRIORITY | ECONOMY |
| **ASSIGNED_SHIP_VIA** | FTL | FTL | LTL |
| **EQUIPMENT_TYPE** | DRY_VAN | REEFER | DRY_VAN |
| **TRLR_TYPE** | DRY_VAN | REFRIGERATED | DRY_VAN |
| **TRLR_SIZE** | 53FT | 53FT | 48FT |
| **TRAILER_NUMBER** | TRL-00445 | TRL-00812 | TRL-00231 |
| **TRACTOR_NUMBER** | TRC-10023 | TRC-10098 | TRC-10011 |
| **SEAL_NUMBER** | SEAL-44201 | SEAL-44388 | SEAL-44105 |
| **O_FACILITY_ID** | FAC-CHI-DC-01 | FAC-DAL-DC-02 | FAC-ATL-SUP-01 |
| **O_FACILITY_NUMBER** | 1001 | 1002 | 2001 |
| **O_STOP_LOCATION_NAME** | Chicago Distribution Center | Dallas Distribution Center | Atlanta Supplier Warehouse |
| **O_ADDRESS** | 100 Industrial Pkwy | 500 Commerce Blvd | 220 Supply Chain Dr |
| **O_CITY** | Chicago | Dallas | Atlanta |
| **O_STATE_PROV** | IL | TX | GA |
| **O_POSTAL_CODE** | 60601 | 75201 | 30301 |
| **O_COUNTRY_CODE** | US | US | US |
| **D_FACILITY_ID** | FAC-NYC-STR-05 | FAC-MIA-STR-12 | FAC-CHI-DC-01 |
| **D_FACILITY_NUMBER** | 5005 | 5012 | 1001 |
| **D_STOP_LOCATION_NAME** | New York Store #05 | Miami Store #12 | Chicago Distribution Center |
| **D_ADDRESS** | 900 5th Avenue | 300 Biscayne Blvd | 100 Industrial Pkwy |
| **D_CITY** | New York | Miami | Chicago |
| **D_STATE_PROV** | NY | FL | IL |
| **D_POSTAL_CODE** | 10001 | 33101 | 60601 |
| **D_COUNTRY_CODE** | US | US | US |
| **PICKUP_START_DATE** | 2026-03-22 07:00:00 | 2026-03-10 08:00:00 | 2026-02-17 06:00:00 |
| **PICKUP_END_DTTM** | 2026-03-22 10:00:00 | 2026-03-10 11:00:00 | 2026-02-17 09:00:00 |
| **PICKUP_TZ** | America/Chicago | America/Chicago | America/New_York |
| **DELIVERY_START_DTTM** | 2026-03-24 08:00:00 | 2026-03-13 07:00:00 | 2026-02-19 08:00:00 |
| **DELIVERY_END_DTTM** | 2026-03-24 17:00:00 | 2026-03-13 12:00:00 | 2026-02-19 17:00:00 |
| **DELIVERY_TZ** | America/New_York | America/New_York | America/Chicago |
| **SCHEDULED_PICKUP_DTTM** | 2026-03-22 08:00:00 | 2026-03-10 09:00:00 | 2026-02-17 07:00:00 |
| **SHIPMENT_START_DTTM** | NULL | 2026-03-10 09:15:00 | 2026-02-17 07:30:00 |
| **SHIPMENT_END_DTTM** | NULL | NULL | 2026-02-19 14:20:00 |
| **RECEIVED_DTTM** | NULL | NULL | 2026-02-19 14:20:00 |
| **TENDER_DTTM** | 2026-03-20 10:00:00 | 2026-03-09 15:00:00 | 2026-02-14 11:00:00 |
| **TENDER_RESP_DEADLINE_DATE** | 2026-03-21 17:00:00 | 2026-03-10 06:00:00 | 2026-02-15 17:00:00 |
| **DAYS_TO_DELIVER** | 2 | 3 | 2 |
| **TOTAL_TIME** | NULL | NULL | 48.83 |
| **PLANNED_WEIGHT** | 18500.000 | 22000.000 | 12750.000 |
| **PLANNED_VOLUME** | 1800.000 | 2100.000 | 1100.000 |
| **FINANCIAL_WT** | 18500.000 | 22000.000 | 12750.000 |
| **WEIGHT_UOM_ID_BASE** | LB | LB | LB |
| **VOLUME_UOM_ID_BASE** | CUFT | CUFT | CUFT |
| **DISTANCE** | 790.50 | 1305.75 | 690.20 |
| **DIRECT_DISTANCE** | 785.00 | 1295.00 | 682.00 |
| **DISTANCE_UOM** | MI | MI | MI |
| **EQUIP_UTIL_PER** | 87.50 | 92.00 | 73.40 |
| **NUM_STOPS** | 2 | 2 | 3 |
| **CURRENCY_CODE** | USD | USD | USD |
| **PLN_TOTAL_COST** | 3250.00 | 5800.00 | 1975.00 |
| **PLN_LINEHAUL_COST** | 2950.00 | 5200.00 | 1700.00 |
| **PLN_TOTAL_ACCESSORIAL_COST** | 150.00 | 400.00 | 175.00 |
| **PLN_STOP_OFF_COST** | 150.00 | 200.00 | 100.00 |
| **PLN_CURRENCY_CODE** | USD | USD | USD |
| **ESTIMATED_COST** | 3250.00 | 5800.00 | 1975.00 |
| **ACTUAL_COST** | NULL | NULL | 2010.00 |
| **ACTUAL_COST_CURRENCY_CODE** | NULL | NULL | USD |
| **TOTAL_COST** | 3250.00 | 5800.00 | 2010.00 |
| **TOTAL_COST_EXCL_TAX** | 3250.00 | 5800.00 | 1940.00 |
| **TOTAL_TAX_AMOUNT** | 0.00 | 0.00 | 70.00 |
| **LINEHAUL_COST** | 2950.00 | 5200.00 | 1720.00 |
| **ACCESSORIAL_COST** | 150.00 | 400.00 | 190.00 |
| **STOP_COST** | 150.00 | 200.00 | 100.00 |
| **CARRIER_CHARGE** | 3250.00 | 5800.00 | 2010.00 |
| **ESTIMATED_SAVINGS** | 200.00 | 450.00 | 125.00 |
| **REPORTED_COST** | NULL | NULL | 2010.00 |
| **TOTAL_REVENUE** | NULL | NULL | 2250.00 |
| **TOTAL_REVENUE_CURRENCY_CODE** | NULL | NULL | USD |
| **MARGIN** | NULL | NULL | 240.00 |
| **IS_HAZMAT** | N | Y | N |
| **IS_PERISHABLE** | N | Y | N |
| **IS_SHIPMENT_CANCELLED** | N | N | N |
| **IS_SHIPMENT_RECONCILED** | N | N | Y |
| **IS_MANUAL_ASSIGN** | N | Y | N |
| **IS_BOOKING_REQUIRED** | N | N | N |
| **SHIPMENT_CLOSED_INDICATOR** | N | N | Y |
| **HAS_ALERTS** | N | Y | N |
| **HAS_TRACKING_MSG** | N | Y | Y |
| **HAS_NOTES** | Y | Y | N |
| **ON_TIME_INDICATOR** | NULL | NULL | ON_TIME |
| **DROPOFF_PICKUP** | DROPOFF | DROPOFF | PICKUP |
| **PLN_MIN_TEMPERATURE** | NULL | 34.00 | NULL |
| **PLN_MAX_TEMPERATURE** | NULL | 40.00 | NULL |
| **TEMPERATURE_UOM** | NULL | F | NULL |
| **CUSTOMER_ID** | CUST-10045 | CUST-10078 | CUST-10012 |
| **BILL_TO_NAME** | Acme Retail Corp | BioFresh Distributors | Metro Supply Co |
| **BILL_TO_ADDRESS** | 1500 Corporate Dr | 800 Logistics Ave | 350 Commerce Way |
| **BILL_TO_CITY** | New York | Miami | Chicago |
| **BILL_TO_STATE_PROV** | NY | FL | IL |
| **BILL_TO_POSTAL_CODE** | 10001 | 33101 | 60601 |
| **BILL_TO_COUNTRY_CODE** | US | US | US |
| **BILL_TO_CODE** | ACME-001 | BIOFR-002 | METRO-003 |
| **BILLING_METHOD** | PREPAID | PREPAID | COLLECT |
| **COMMODITY_CLASS** | 70 | 85 | 65 |
| **PACKAGING** | PALLET | PALLET | CARTON |
| **ORDER_QTY** | 200.000 | 150.000 | 320.000 |
| **DECLARED_VALUE** | 45000.00 | 38000.00 | 28500.00 |
| **DV_CURRENCY_CODE** | USD | USD | USD |
| **TRANS_RESP_CODE** | SHIPPER | SHIPPER | CONSIGNEE |
| **PRIORITY_TYPE** | STANDARD | HIGH | STANDARD |
| **LANE_NAME** | CHI-NYC-FTL-DIRECT | DAL-MIA-FTL-PRIORITY | ATL-CHI-LTL-RELAY |
| **REGION_ID** | MIDWEST | SOUTH | SOUTHEAST |
| **SENT_TO_PKMS** | Y | Y | Y |
| **FIRST_UPDATE_SENT_TO_PKMS** | Y | Y | Y |
| **UPDATE_SENT** | Y | Y | Y |
| **WMS_STATUS_CODE** | PICK_COMPLETE | IN_TRANSIT | RECEIVED |
| **EXTRACTION_DTTM** | 2026-03-20 14:30:00 | 2026-03-24 11:15:00 | 2026-03-01 18:00:00 |

---

*Note: NULL values indicate fields not yet populated at the time of the shipment's current status. All datetime values are in UTC unless a timezone column is specified.*
