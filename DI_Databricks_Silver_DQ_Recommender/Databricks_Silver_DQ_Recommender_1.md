_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Data Quality Recommendations for TMS Shipment Silver Layer, including Cognos report lineage and compliance
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Recommender for TMS Shipment Application

This document provides comprehensive data quality (DQ) recommendations for the Silver layer of the Databricks Medallion architecture for the TMS Shipment domain. It includes column-level, table-level, referential, and business rule-based checks, as well as lineage and compliance notes from the Cognos report.

---

## Cognos Report Metadata Summary

- **Sources:** TMS Shipment Database
- **Columns:** SHIPMENT_ID, SHIPMENT_STATUS, SHIPMENT_TYPE, O_STOP_LOCATION_NAME, O_CITY, O_STATE_PROV, O_POSTAL_CODE, O_COUNTRY
- **KPIs:**
  - TOTAL ROW COUNT
  - DISTINCT SHIPMENT IDs
  - TOTAL DISTANCE
  - AVG DISTANCE
  - SHIPMENT STATUS BREAKDOWN
  - MODE OF TRANSPORT BREAKDOWN

---

## Cognos Report Business Write-up (Markdown)

# Shipment Operations Report
**Purpose:** To provide operational visibility into shipments, including status, type, origin, and key metrics for logistics and supply chain management.

**Data Sources:** TMS Shipment Database (bronze.bz_shipment, bronze.bz_facility, bronze.bz_carrier, etc.)

**Columns and KPIs:**
- SHIPMENT_ID (unique shipment identifier)
- SHIPMENT_STATUS (current status code)
- SHIPMENT_TYPE (inbound/outbound)
- O_STOP_LOCATION_NAME, O_CITY, O_STATE_PROV, O_POSTAL_CODE, O_COUNTRY (origin details)
- TOTAL ROW COUNT (all shipment records)
- DISTINCT SHIPMENT IDs (uniqueness check)
- TOTAL DISTANCE, AVG DISTANCE (route metrics)
- SHIPMENT STATUS BREAKDOWN (distribution)
- MODE OF TRANSPORT BREAKDOWN (distribution)

**Key Insights:**
- All shipment records are uniquely identified (20/20 distinct IDs)
- Total distance covered: 11K miles; average per shipment: 538.08 miles
- Status and mode breakdowns support operational and compliance reporting

**Compliance Notes:**
- Data is for internal use only (per Cognos footer)
- All customer and shipment data must comply with company data retention and privacy policies

---

## Recommended Data Quality Checks

### 1. Column-Level Checks

| Column Name                | Check Name                        | Description                                                                 | Rationale                                                                                  | SQL Example |
|---------------------------|-----------------------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-------------|
| SHIPMENT_ID               | Uniqueness                        | Ensure SHIPMENT_ID is unique per row                                         | Prevents duplicate shipment records                                                        | SELECT SHIPMENT_ID, COUNT(*) FROM silver.shipment GROUP BY SHIPMENT_ID HAVING COUNT(*) > 1; |
| SHIPMENT_ID               | Not Null                          | SHIPMENT_ID must not be null                                                | Required for all shipment records                                                          | SELECT * FROM silver.shipment WHERE SHIPMENT_ID IS NULL; |
| SHIPMENT_STATUS           | Domain Value                      | Must be in ('PLANNED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED')              | Ensures only valid status codes are used                                                   | SELECT * FROM silver.shipment WHERE SHIPMENT_STATUS NOT IN ('PLANNED','IN_TRANSIT','DELIVERED','CANCELLED'); |
| SHIPMENT_TYPE             | Not Null                          | SHIPMENT_TYPE must not be null                                              | Required for operational and audit reporting                                               | SELECT * FROM silver.shipment WHERE SHIPMENT_TYPE IS NULL; |
| O_FACILITY_ID, D_FACILITY_ID | Referential Integrity           | Must reference valid facility IDs in facility table                          | Ensures shipments are linked to valid facilities                                           | SELECT * FROM silver.shipment s LEFT JOIN silver.facility f ON s.O_FACILITY_ID = f.FACILITY_ID WHERE f.FACILITY_ID IS NULL; |
| ASSIGNED_CARRIER_ID       | Referential Integrity             | Must reference valid carrier IDs in carrier table                            | Ensures shipments are linked to valid carriers                                             | SELECT * FROM silver.shipment s LEFT JOIN silver.carrier c ON s.ASSIGNED_CARRIER_ID = c.CARRIER_ID WHERE c.CARRIER_ID IS NULL; |
| CREATED_DTTM              | Date Format & Range               | Must be valid date and within operational range                              | Prevents invalid or out-of-range creation dates                                            | SELECT * FROM silver.shipment WHERE TRY_CAST(CREATED_DTTM AS DATE) IS NULL OR CREATED_DTTM < '2020-01-01'; |
| DISTANCE, DIRECT_DISTANCE, OUT_OF_ROUTE_DISTANCE | Numeric Range | Must be >= 0; DIRECT_DISTANCE <= DISTANCE                                   | Prevents negative or illogical distances                                                   | SELECT * FROM silver.shipment WHERE DISTANCE < 0 OR DIRECT_DISTANCE < 0 OR OUT_OF_ROUTE_DISTANCE < 0 OR DIRECT_DISTANCE > DISTANCE; |
| DISTANCE_UOM              | Consistency                       | All rows must use the same unit (e.g., 'MI' or 'KM')                         | Prevents mixed units in distance calculations                                             | SELECT DISTINCT DISTANCE_UOM FROM silver.shipment; |
| BILLING_METHOD            | Data Type Transformation          | Must be string (if migrated from legacy numeric)                             | Ensures billing method is correctly transformed                                           | SELECT * FROM silver.shipment WHERE TRY_CAST(BILLING_METHOD AS STRING) IS NULL; |
| BILL_OF_LADING_NUMBER     | Uniqueness                        | Should be unique per shipment                                               | Required for billing reconciliation                                                        | SELECT BILL_OF_LADING_NUMBER, COUNT(*) FROM silver.shipment GROUP BY BILL_OF_LADING_NUMBER HAVING COUNT(*) > 1; |
| BUSINESS_PARTNER_ID       | Extraction Logic                   | Must be extracted consistently from extended attribute                       | Ensures business partner is consistently sourced                                          | -- Extraction logic validation required |
| PURCHASE_ORDER            | Consistency                       | Must be consistently sourced                                                | Ensures purchase order reference is reliable                                              | -- Consistency check required |
| IS_SHIPMENT_CANCELLED     | Domain Value                      | Must be 'Y' or 'N'                                                          | Ensures flag is valid                                                                     | SELECT * FROM silver.shipment WHERE IS_SHIPMENT_CANCELLED NOT IN ('Y','N'); |
| IS_SHIPMENT_RECONCILED    | Domain Value                      | Must be 'Y' or 'N'                                                          | Ensures flag is valid                                                                     | SELECT * FROM silver.shipment WHERE IS_SHIPMENT_RECONCILED NOT IN ('Y','N'); |
| TRAILER_NUMBER            | String Length                     | Should not exceed 50 characters                                             | Prevents data truncation                                                                 | SELECT * FROM silver.shipment WHERE LENGTH(TRAILER_NUMBER) > 50; |
| O_POSTAL_CODE, D_POSTAL_CODE | String Length                  | Should not exceed 20 characters                                             | Prevents data truncation                                                                 | SELECT * FROM silver.shipment WHERE LENGTH(O_POSTAL_CODE) > 20 OR LENGTH(D_POSTAL_CODE) > 20; |
| O_COUNTRY_CODE, D_COUNTRY_CODE | Domain Value                 | Must be valid ISO country codes                                             | Ensures country codes are valid                                                           | SELECT * FROM silver.shipment WHERE O_COUNTRY_CODE NOT IN ('US','CA',...) OR D_COUNTRY_CODE NOT IN ('US','CA',...); |
| NUM_STOPS                 | Numeric Range                     | Must be >= 0                                                                | Prevents negative stop counts                                                             | SELECT * FROM silver.shipment WHERE NUM_STOPS < 0; |
| PLANNED_WEIGHT, PLANNED_VOLUME | Numeric Range                | Must be >= 0                                                                | Prevents negative weights/volumes                                                         | SELECT * FROM silver.shipment WHERE PLANNED_WEIGHT < 0 OR PLANNED_VOLUME < 0; |
| CREATED_SOURCE, CREATOR_ROLE | Not Null                       | Must not be null                                                            | Required for audit completeness                                                           | SELECT * FROM silver.shipment WHERE CREATED_SOURCE IS NULL OR CREATOR_ROLE IS NULL; |

### 2. Table-Level Checks

1. **Row Count Validation**: Ensure row count matches expected volume from source (e.g., Cognos report: 20 rows)
   - Rationale: Detects missing or duplicate data
   - SQL Example: SELECT COUNT(*) FROM silver.shipment;

2. **Uniqueness of SHIPMENT_ID**: No duplicate shipment records
   - Rationale: Prevents data integrity issues
   - SQL Example: SELECT SHIPMENT_ID, COUNT(*) FROM silver.shipment GROUP BY SHIPMENT_ID HAVING COUNT(*) > 1;

3. **Referential Integrity**: All foreign keys reference valid records in related tables
   - Rationale: Ensures data consistency across entities
   - SQL Example: SELECT * FROM silver.shipment s LEFT JOIN silver.facility f ON s.O_FACILITY_ID = f.FACILITY_ID WHERE f.FACILITY_ID IS NULL;

### 3. Business Rule-Based Checks

1. **Cancelled Shipment Identification**: IS_SHIPMENT_CANCELLED must be set based on planning status code
   - Rationale: Ensures correct business logic for cancelled shipments
   - SQL Example: SELECT * FROM silver.shipment WHERE SHIPMENT_STATUS = 'CANCELLED' AND IS_SHIPMENT_CANCELLED <> 'Y';

2. **Distance Consistency**: DIRECT_DISTANCE must not exceed DISTANCE
   - Rationale: Prevents illogical route metrics
   - SQL Example: SELECT * FROM silver.shipment WHERE DIRECT_DISTANCE > DISTANCE;

3. **Billing Method Transformation**: Validate that billing method is string in Silver layer
   - Rationale: Ensures correct data type after migration
   - SQL Example: SELECT * FROM silver.shipment WHERE TRY_CAST(BILLING_METHOD AS STRING) IS NULL;

4. **Unit Consistency**: DISTANCE_UOM must be consistent across all records
   - Rationale: Prevents calculation errors
   - SQL Example: SELECT DISTINCT DISTANCE_UOM FROM silver.shipment;

5. **Audit Completeness**: CREATED_SOURCE and CREATOR_ROLE must be present
   - Rationale: Required for audit and traceability
   - SQL Example: SELECT * FROM silver.shipment WHERE CREATED_SOURCE IS NULL OR CREATOR_ROLE IS NULL;

6. **Zero-Distance Shipments**: Exclude from rate calculations but count separately
   - Rationale: Business rule for reporting
   - SQL Example: SELECT COUNT(*) FROM silver.shipment WHERE DISTANCE = 0;

7. **Out-of-Route Distance**: OUT_OF_ROUTE_DISTANCE must not exceed DISTANCE
   - Rationale: Prevents anomalies in route reporting
   - SQL Example: SELECT * FROM silver.shipment WHERE OUT_OF_ROUTE_DISTANCE > DISTANCE;

8. **Purchase Order Reference Consistency**: Validate consistent sourcing
   - Rationale: Ensures reliable reporting
   - SQL Example: -- Consistency check required

---

## API Cost
apiCost: 0.000000 USD

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Recommender
**pipelineID:** 12360
