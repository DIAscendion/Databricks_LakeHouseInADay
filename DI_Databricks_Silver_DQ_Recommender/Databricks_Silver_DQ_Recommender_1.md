_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Data Quality Recommendations for SHIPMENT Table in Databricks Silver Layer
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Recommender: SHIPMENT Table

This document provides a comprehensive set of data quality recommendations for the SHIPMENT table in the Databricks Silver layer, based on the conceptual model, business rules, and physical DDL. The recommendations ensure completeness, accuracy, consistency, and referential integrity for shipment data in the transportation management system (TMS).

---

## Recommended Data Quality Checks

| # | Check Name | Description | Rationale | SQL Example |
|---|------------|-------------|-----------|-------------|
| 1 | Null Check: Required Fields | Ensure required fields (SHIPMENT_ID, SHIPMENT_STATUS, SHIPMENT_TYPE, O_FACILITY_ID, D_FACILITY_ID, CREATED_DTTM, CREATED_SOURCE, TC_COMPANY_ID, TC_SHIPMENT_ID) are not null. | Mandatory for operational, audit, and reporting completeness. | SELECT * FROM silver.shipment WHERE SHIPMENT_ID IS NULL OR SHIPMENT_STATUS IS NULL OR SHIPMENT_TYPE IS NULL OR O_FACILITY_ID IS NULL OR D_FACILITY_ID IS NULL OR CREATED_DTTM IS NULL OR CREATED_SOURCE IS NULL OR TC_COMPANY_ID IS NULL OR TC_SHIPMENT_ID IS NULL; |
| 2 | Uniqueness: SHIPMENT_ID | SHIPMENT_ID must be unique per row. | Prevents duplicate shipment records; aligns with business rules. | SELECT SHIPMENT_ID, COUNT(*) FROM silver.shipment GROUP BY SHIPMENT_ID HAVING COUNT(*) > 1; |
| 3 | Uniqueness: BILL_OF_LADING_NUMBER | BILL_OF_LADING_NUMBER must be unique where present. | Ensures billing traceability and prevents duplicate billing. | SELECT BILL_OF_LADING_NUMBER, COUNT(*) FROM silver.shipment WHERE BILL_OF_LADING_NUMBER IS NOT NULL GROUP BY BILL_OF_LADING_NUMBER HAVING COUNT(*) > 1; |
| 4 | Domain Value: SHIPMENT_STATUS | SHIPMENT_STATUS must be one of ('PLANNED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED'). | Ensures status accuracy and prevents invalid states. | SELECT * FROM silver.shipment WHERE SHIPMENT_STATUS NOT IN ('PLANNED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED'); |
| 5 | Domain Value: DISTANCE_UOM | DISTANCE_UOM must be consistent and in ('MI', 'KM'). | Prevents mixed units and ensures reporting consistency. | SELECT DISTINCT DISTANCE_UOM FROM silver.shipment; |
| 6 | Numeric Range: DISTANCE, DIRECT_DISTANCE, OUT_OF_ROUTE_DISTANCE | These fields must be non-negative. | Negative distances are not physically possible. | SELECT * FROM silver.shipment WHERE DISTANCE < 0 OR DIRECT_DISTANCE < 0 OR OUT_OF_ROUTE_DISTANCE < 0; |
| 7 | Numeric Logic: DIRECT_DISTANCE <= DISTANCE | DIRECT_DISTANCE must not exceed DISTANCE. | Ensures logical consistency in route calculations. | SELECT * FROM silver.shipment WHERE DIRECT_DISTANCE > DISTANCE; |
| 8 | Numeric Logic: OUT_OF_ROUTE_DISTANCE <= DISTANCE | OUT_OF_ROUTE_DISTANCE must not exceed DISTANCE. | Prevents data anomalies in route reporting. | SELECT * FROM silver.shipment WHERE OUT_OF_ROUTE_DISTANCE > DISTANCE; |
| 9 | Numeric Range: EQUIP_UTIL_PER | EQUIP_UTIL_PER must be between 0.0 and 100.0. | Validates equipment utilization percentage. | SELECT * FROM silver.shipment WHERE EQUIP_UTIL_PER < 0 OR EQUIP_UTIL_PER > 100; |
| 10 | Date Format: CREATED_DTTM, SHIPMENT_START_DTTM, SHIPMENT_END_DTTM | Dates must be valid and within operational range (e.g., 2000-01-01 to current date + 1 year). | Prevents future/past data errors and ensures operational relevance. | SELECT * FROM silver.shipment WHERE CREATED_DTTM < '2000-01-01' OR CREATED_DTTM > DATE_ADD(current_date(), 365); |
| 11 | Referential Integrity: CARRIER, FACILITY, BUSINESS_PARTNER | ASSIGNED_CARRIER_ID, O_FACILITY_ID, D_FACILITY_ID, BUSINESS_PARTNER_ID must reference valid records in their respective tables. | Ensures foreign key relationships and data integrity. | SELECT s.* FROM silver.shipment s LEFT JOIN silver.carrier c ON s.ASSIGNED_CARRIER_ID = c.CARRIER_ID WHERE s.ASSIGNED_CARRIER_ID IS NOT NULL AND c.CARRIER_ID IS NULL; (Repeat for facilities and business partners) |
| 12 | Referential Integrity: Parent Shipment | PP_SHIPMENT_ID must reference an existing SHIPMENT_ID if present. | Maintains shipment hierarchy and lineage. | SELECT * FROM silver.shipment WHERE PP_SHIPMENT_ID IS NOT NULL AND PP_SHIPMENT_ID NOT IN (SELECT SHIPMENT_ID FROM silver.shipment); |
| 13 | String Length: Key Identifiers | Key fields (SHIPMENT_ID, TC_SHIPMENT_ID, BILL_OF_LADING_NUMBER, etc.) must not exceed defined max lengths. | Prevents truncation and data loss. | SELECT * FROM silver.shipment WHERE LENGTH(SHIPMENT_ID) > 50 OR LENGTH(TC_SHIPMENT_ID) > 50 OR LENGTH(BILL_OF_LADING_NUMBER) > 100; |
| 14 | Pattern: Boolean Flags | Fields like IS_SHIPMENT_CANCELLED, IS_SHIPMENT_RECONCILED, etc. must be 'Y' or 'N'. | Ensures binary flag consistency. | SELECT * FROM silver.shipment WHERE IS_SHIPMENT_CANCELLED NOT IN ('Y', 'N') OR IS_SHIPMENT_RECONCILED NOT IN ('Y', 'N'); |
| 15 | Pattern: DROPOFF_PICKUP | DROPOFF_PICKUP must be 'DROPOFF' or 'PICKUP' if present. | Validates allowed values for shipment type. | SELECT * FROM silver.shipment WHERE DROPOFF_PICKUP IS NOT NULL AND DROPOFF_PICKUP NOT IN ('DROPOFF', 'PICKUP'); |
| 16 | Consistency: Facility Address Completeness | O_ADDRESS, O_CITY, O_STATE_PROV, O_POSTAL_CODE, D_ADDRESS, D_CITY, D_STATE_PROV, D_POSTAL_CODE must be present for each shipment. | Required for routing and reporting. | SELECT * FROM silver.shipment WHERE O_ADDRESS IS NULL OR O_CITY IS NULL OR O_STATE_PROV IS NULL OR O_POSTAL_CODE IS NULL OR D_ADDRESS IS NULL OR D_CITY IS NULL OR D_STATE_PROV IS NULL OR D_POSTAL_CODE IS NULL; |
| 17 | Consistency: Creation Source and Role | CREATED_SOURCE and CREATED_SOURCE_TYPE must be present and valid. | Required for audit and governance. | SELECT * FROM silver.shipment WHERE CREATED_SOURCE IS NULL OR CREATED_SOURCE_TYPE IS NULL; |
| 18 | Data Type: BILLING_METHOD | Ensure BILLING_METHOD is stored as STRING. | Required for reporting and system migration. | SELECT * FROM silver.shipment WHERE typeof(BILLING_METHOD) != 'string'; |
| 19 | Row Count Validation | Validate expected row count matches source system for a given period. | Detects missing or duplicate data during ETL. | SELECT COUNT(*) FROM silver.shipment WHERE CREATED_DTTM BETWEEN '2023-01-01' AND '2023-01-31'; |
| 20 | KPI Consistency: Cancelled Shipment % | Cancelled shipment count must not exceed total shipment count. | Ensures logical KPI calculation. | SELECT COUNT(*) FROM silver.shipment WHERE IS_SHIPMENT_CANCELLED = 'Y'; (Compare with total count) |
| 21 | KPI Consistency: Route Efficiency Index | Route Efficiency Index (DIRECT_DISTANCE / DISTANCE) must be between 0 and 1. | Validates KPI logic and prevents division errors. | SELECT * FROM silver.shipment WHERE DISTANCE > 0 AND (DIRECT_DISTANCE / DISTANCE < 0 OR DIRECT_DISTANCE / DISTANCE > 1); |
| 22 | KPI Consistency: Out-of-Route Distance % | Out-of-route distance % (OUT_OF_ROUTE_DISTANCE / DISTANCE) must be between 0 and 1. | Validates KPI logic and prevents anomalies. | SELECT * FROM silver.shipment WHERE DISTANCE > 0 AND (OUT_OF_ROUTE_DISTANCE / DISTANCE < 0 OR OUT_OF_ROUTE_DISTANCE / DISTANCE > 1); |
| 23 | Transformation: Billing Method | Confirm numeric-to-string transformation for BILLING_METHOD. | Ensures correct data type post-migration. | SELECT * FROM silver.shipment WHERE typeof(BILLING_METHOD) != 'string'; |
| 24 | Transformation: Distance Unit Conversion | Flag rows with mixed DISTANCE_UOM values. | Ensures all distances are comparable. | SELECT COUNT(DISTINCT DISTANCE_UOM) FROM silver.shipment; (Should be 1) |
| 25 | Business Partner Extraction | BUSINESS_PARTNER_ID must be extracted and populated as per business rule. | Ensures partner/vendor linkage. | SELECT * FROM silver.shipment WHERE BUSINESS_PARTNER_ID IS NULL; |

---

## Rationale and Coverage

- All checks are derived from the conceptual model, business rules, and DDL constraints.
- Checks cover completeness, accuracy, format, consistency, referential integrity, and transformation logic.
- SQL examples are provided for implementation in Databricks SQL or PySpark.
- These checks support regulatory, operational, and audit requirements for shipment data.

---

## API Cost

apiCost: 0.000200 USD

---

[View Silver DQ Recommender Output in GitHub](https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Recommender)

PipelineID: 12360