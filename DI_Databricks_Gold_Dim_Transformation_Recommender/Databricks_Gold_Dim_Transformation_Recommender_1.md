_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Transformation rules for Dimension tables from Silver to Gold layer in Databricks Lakehouse (Shipment Domain)
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Dim Transformation Recommender

This document provides comprehensive transformation rules for Dimension tables in the Gold layer of the Databricks Lakehouse, based on the conceptual model, data constraints, Silver and Gold DDLs for the Shipment domain. The focus is on ensuring data integrity, standardization, and alignment with reporting requirements.

---

## 1. Dimension Tables Identified

| Gold Dimension Table         | Silver Source Table(s)           |
|-----------------------------|----------------------------------|
| go_carrier_dim              | si_shipment_process              |
| go_facility_dim             | si_shipment_process              |
| go_route_dim                | si_shipment_process              |
| go_billing_dim              | si_shipment_process              |
| go_business_partner_dim     | si_shipment_process              |
| go_user_dim                 | si_shipment_process              |

---

## 2. Transformation Rules for Dimension Tables

### 2.1 go_carrier_dim

#### [Rule 1]: Data Type Alignment for Carrier Names
- **Description**: Ensure all carrier name columns are of STRING type and standardized to uppercase.
    - **Rationale**: Consistent data type and casing improves join reliability and reporting.
    - **SQL Example**:
      ```sql
      SELECT
        UPPER(ASSIGNED_CARRIER_ID) AS primary_carrier_name,
        UPPER(ASSIGNED_SCNDR_CARRIER_ID) AS secondary_carrier_name,
        UPPER(BROKER_CARRIER_ID) AS broker_carrier_name,
        UPPER(DSG_CARRIER_ID) AS designated_carrier_name,
        UPPER(FEASIBLE_CARRIER_ID) AS feasible_carrier_name,
        UPPER(ASSIGNED_MOT_ID) AS mode_of_transport
      FROM silver.si_shipment_process
      GROUP BY 1,2,3,4,5,6
      ```

#### [Rule 2]: Deduplication and Surrogate Key Generation
- **Description**: Generate unique carrier_dim_id (UUID or hash) and remove duplicates.
    - **Rationale**: Ensures each carrier combination is unique in the dimension.
    - **SQL Example**:
      ```sql
      SELECT
        sha2(concat_ws('|', primary_carrier_name, secondary_carrier_name, broker_carrier_name, designated_carrier_name, feasible_carrier_name, mode_of_transport), 256) AS carrier_dim_id,
        *
      FROM (
        -- previous select
      )
      ```

#### [Rule 3]: Null Handling and Default Values
- **Description**: Replace NULL carrier names with 'UNKNOWN'.
    - **Rationale**: Prevents NULLs in reporting and downstream joins.
    - **SQL Example**:
      ```sql
      COALESCE(primary_carrier_name, 'UNKNOWN') AS primary_carrier_name
      ```

#### [Rule 4]: Traceability
- **Description**: Add load_date, update_date, and source_system columns from Silver.
    - **Rationale**: Enables audit and lineage tracking.
    - **SQL Example**:
      ```sql
      load_date, update_date, source_system
      ```

---

### 2.2 go_facility_dim

#### [Rule 1]: Facility Name and Address Standardization
- **Description**: Standardize facility_name, address, city, state, postal_code, country to uppercase and trim whitespace.
    - **Rationale**: Ensures consistent facility identification and reporting.
    - **SQL Example**:
      ```sql
      SELECT
        UPPER(TRIM(O_FACILITY_ID)) AS facility_name,
        UPPER(TRIM(O_ADDRESS)) AS address,
        UPPER(TRIM(O_CITY)) AS city,
        UPPER(TRIM(O_STATE_PROV)) AS state,
        UPPER(TRIM(O_POSTAL_CODE)) AS postal_code,
        UPPER(TRIM(O_COUNTRY_CODE)) AS country
      FROM silver.si_shipment_process
      UNION
      SELECT
        UPPER(TRIM(D_FACILITY_ID)),
        UPPER(TRIM(D_ADDRESS)),
        UPPER(TRIM(D_CITY)),
        UPPER(TRIM(D_STATE_PROV)),
        UPPER(TRIM(D_POSTAL_CODE)),
        UPPER(TRIM(D_COUNTRY_CODE))
      FROM silver.si_shipment_process
      ```

#### [Rule 2]: Deduplication and Surrogate Key Generation
- **Description**: Generate facility_dim_id as hash of facility attributes.
    - **Rationale**: Ensures uniqueness and enables surrogate key joins.
    - **SQL Example**:
      ```sql
      SELECT
        sha2(concat_ws('|', facility_name, address, city, state, postal_code, country), 256) AS facility_dim_id,
        *
      FROM (
        -- previous select
      )
      ```

#### [Rule 3]: Null Handling
- **Description**: Replace NULLs with 'UNKNOWN' for facility attributes.
    - **Rationale**: Prevents NULLs in reporting.
    - **SQL Example**:
      ```sql
      COALESCE(facility_name, 'UNKNOWN') AS facility_name
      ```

#### [Rule 4]: Traceability
- **Description**: Add load_date, update_date, and source_system columns from Silver.
    - **Rationale**: Enables audit and lineage tracking.

---

### 2.3 go_route_dim

#### [Rule 1]: Data Type and Value Standardization
- **Description**: Ensure all distance columns are DECIMAL(10,2), number_of_stops is INT, and distance_unit_of_measure is standardized (e.g., 'MI', 'KM').
    - **Rationale**: Consistent types and units are required for analytics.
    - **SQL Example**:
      ```sql
      SELECT
        ROUTE_REFERENCE,
        CAST(DISTANCE AS DECIMAL(10,2)) AS total_route_distance,
        CAST(DIRECT_DISTANCE AS DECIMAL(10,2)) AS direct_distance,
        CAST(OUT_OF_ROUTE_DISTANCE AS DECIMAL(10,2)) AS out_of_route_distance,
        UPPER(DISTANCE_UOM) AS distance_unit_of_measure,
        CAST(NUM_STOPS AS INT) AS number_of_stops,
        UPPER(EQUIPMENT_TYPE) AS equipment_type
      FROM silver.si_shipment_process
      ```

#### [Rule 2]: Hierarchy Mapping
- **Description**: Map route_reference to shipment and facility for parent-child relationships.
    - **Rationale**: Enables drill-down from route to shipment/facility.
    - **SQL Example**:
      ```sql
      -- Join route_dim to shipment_fact on route_reference
      ```

#### [Rule 3]: Deduplication and Surrogate Key Generation
- **Description**: Generate route_dim_id as hash of route attributes.
    - **Rationale**: Ensures uniqueness.
    - **SQL Example**:
      ```sql
      SELECT
        sha2(concat_ws('|', route_reference, total_route_distance, direct_distance, out_of_route_distance, distance_unit_of_measure, number_of_stops, equipment_type), 256) AS route_dim_id,
        *
      FROM (
        -- previous select
      )
      ```

#### [Rule 4]: Null Handling
- **Description**: Replace NULLs with default values (e.g., 0 for distances, 'UNKNOWN' for strings).
    - **Rationale**: Prevents NULLs in reporting.

#### [Rule 5]: Traceability
- **Description**: Add load_date, update_date, and source_system columns from Silver.

---

### 2.4 go_billing_dim

#### [Rule 1]: Data Type Conversion for Billing Method
- **Description**: Convert billing_method from numeric to STRING if required.
    - **Rationale**: Aligns with reporting and business rules.
    - **SQL Example**:
      ```sql
      SELECT
        BILL_OF_LADING_NUMBER AS bill_of_lading_number,
        CAST(BILLING_METHOD AS STRING) AS billing_method,
        PURCHASE_ORDER AS purchase_order_reference,
        BILL_TO_POSTAL_CODE AS bill_to_postal_code,
        BILL_TO_STATE_PROV AS bill_to_state_province,
        SHIPMENT_RECON_DTTM AS reconciliation_date
      FROM silver.si_shipment_process
      ```

#### [Rule 2]: Deduplication and Surrogate Key Generation
- **Description**: Generate billing_dim_id as hash of billing attributes.
    - **Rationale**: Ensures uniqueness.
    - **SQL Example**:
      ```sql
      SELECT
        sha2(concat_ws('|', bill_of_lading_number, billing_method, purchase_order_reference, bill_to_postal_code, bill_to_state_province, reconciliation_date), 256) AS billing_dim_id,
        *
      FROM (
        -- previous select
      )
      ```

#### [Rule 3]: Null Handling
- **Description**: Replace NULLs with 'UNKNOWN' or default values.
    - **Rationale**: Prevents NULLs in reporting.

#### [Rule 4]: Traceability
- **Description**: Add load_date, update_date, and source_system columns from Silver.

---

### 2.5 go_business_partner_dim

#### [Rule 1]: Extraction and Standardization
- **Description**: Extract business_partner_identifier from BUSINESS_PARTNER_ID or extended attribute, standardize to uppercase.
    - **Rationale**: Ensures consistent partner identification.
    - **SQL Example**:
      ```sql
      SELECT
        UPPER(BUSINESS_PARTNER_ID) AS business_partner_identifier
      FROM silver.si_shipment_process
      ```

#### [Rule 2]: Deduplication and Surrogate Key Generation
- **Description**: Generate business_partner_dim_id as hash of identifier.
    - **Rationale**: Ensures uniqueness.
    - **SQL Example**:
      ```sql
      SELECT
        sha2(business_partner_identifier, 256) AS business_partner_dim_id,
        *
      FROM (
        -- previous select
      )
      ```

#### [Rule 3]: Null Handling
- **Description**: Replace NULLs with 'UNKNOWN'.
    - **Rationale**: Prevents NULLs in reporting.

#### [Rule 4]: Traceability
- **Description**: Add load_date, update_date, and source_system columns from Silver.

---

### 2.6 go_user_dim

#### [Rule 1]: Extraction and Standardization
- **Description**: Extract creator_role and creation_source_type, standardize to uppercase.
    - **Rationale**: Ensures consistent user role identification.
    - **SQL Example**:
      ```sql
      SELECT
        UPPER(CREATOR_ROLE) AS creator_role,
        UPPER(CREATED_SOURCE_TYPE) AS creation_source_type
      FROM silver.si_shipment_process
      ```

#### [Rule 2]: Deduplication and Surrogate Key Generation
- **Description**: Generate user_dim_id as hash of role and source type.
    - **Rationale**: Ensures uniqueness.
    - **SQL Example**:
      ```sql
      SELECT
        sha2(concat_ws('|', creator_role, creation_source_type), 256) AS user_dim_id,
        *
      FROM (
        -- previous select
      )
      ```

#### [Rule 3]: Null Handling
- **Description**: Replace NULLs with 'UNKNOWN'.
    - **Rationale**: Prevents NULLs in reporting.

#### [Rule 4]: Traceability
- **Description**: Add load_date, update_date, and source_system columns from Silver.

---

## 3. General Transformation Guidelines

- All dimension tables must enforce uniqueness on their surrogate key.
- All string columns should be standardized to uppercase and trimmed.
- All date columns must be in DATE or TIMESTAMP format as per Gold DDL.
- All numeric columns must be cast to the correct precision/scale.
- All NULLs must be replaced with 'UNKNOWN' or 0 as appropriate.
- All transformations must be traceable to their source columns in Silver.
- Audit columns (load_date, update_date, source_system) must be populated from Silver.

---

## 4. Traceability Matrix

| Gold Dimension Table     | Silver Source Column(s)         | Transformation Rule(s) Applied                |
|-------------------------|----------------------------------|-----------------------------------------------|
| go_carrier_dim          | ASSIGNED_CARRIER_ID, ...         | Data type, uppercase, dedup, null handling    |
| go_facility_dim         | O_FACILITY_ID, D_FACILITY_ID, ...| Standardize, dedup, null handling             |
| go_route_dim            | ROUTE_REFERENCE, DISTANCE, ...   | Data type, dedup, null handling, hierarchy    |
| go_billing_dim          | BILL_OF_LADING_NUMBER, ...       | Data type, dedup, null handling               |
| go_business_partner_dim | BUSINESS_PARTNER_ID              | Extraction, uppercase, dedup, null handling   |
| go_user_dim             | CREATOR_ROLE, CREATED_SOURCE_TYPE| Extraction, uppercase, dedup, null handling   |

---

## 5. API Cost

apiCost: 0.000800

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Recommender
**pipelineID:** 14669
