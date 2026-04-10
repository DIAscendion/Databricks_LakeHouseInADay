_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Comprehensive data mapping for Fact tables in the Gold Layer with transformations, validations, and aggregation rules from Silver Layer, based on business constraints and reporting requirements.
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Data Mapping

## Overview
This document provides a comprehensive data mapping for Fact tables in the Gold Layer of the TMS Shipment application. It details the transformation, aggregation, validation, and cleansing logic required to move data from the Silver Layer to the Gold Layer, ensuring high data quality, referential integrity, and compatibility with Databricks and PySpark. The mapping is based on the Silver and Gold Layer DDLs, business constraints, and previous transformation recommendations.

---

## Data Mapping for Fact Tables

### Fact Table: go_shipment_facts

| Target Layer | Target Table         | Target Field         | Source Layer | Source Table         | Source Field         | Validation Rule                                                                 | Transformation Rule                                                                                       |
|--------------|---------------------|----------------------|--------------|---------------------|----------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Gold         | go_shipment_facts   | SHIPMENT_ID          | Silver       | sv_shipment         | SHIPMENT_ID          | Must be present and unique per row (2.2.1, 2.1.1)                                | Direct mapping                                                                                           |
| Gold         | go_shipment_facts   | SHIPMENT_STATUS      | Silver       | sv_shipment         | SHIPMENT_STATUS      | Must be a valid domain value (1.2.1); required for reporting (2.1.2)             | Map to status code; join to go_shipment_status_codes for description                                     |
| Gold         | go_shipment_facts   | O_FACILITY_ID        | Silver       | sv_shipment         | O_FACILITY_ID        | Must reference valid facility (2.5.2); required (2.1.3)                          | Join to go_facility_dimension for facility details                                                       |
| Gold         | go_shipment_facts   | D_FACILITY_ID        | Silver       | sv_shipment         | D_FACILITY_ID        | Must reference valid facility (2.5.2); required (2.1.3)                          | Join to go_facility_dimension for facility details                                                       |
| Gold         | go_shipment_facts   | ASSIGNED_CARRIER_ID  | Silver       | sv_shipment         | ASSIGNED_CARRIER_ID  | Must reference valid carrier (2.5.1); required (2.1.4)                           | Join to go_carrier_dimension for carrier details                                                         |
| Gold         | go_shipment_facts   | CREATED_DTTM         | Silver       | sv_shipment         | CREATED_DTTM         | Must be valid date, not null (1.3.3, 2.1.5)                                      | Direct mapping; validate date format and range                                                           |
| Gold         | go_shipment_facts   | CREATION_TYPE        | Silver       | sv_shipment         | CREATION_TYPE        | Must be non-null for audit (1.1.2)                                               | Direct mapping                                                                                           |
| Gold         | go_shipment_facts   | BILLING_METHOD       | Silver       | sv_shipment         | BILLING_METHOD       | Data type transformation required (2.3.1, 1.3.2)                                 | Transform numeric (legacy) to string (new); validate transformation                                      |
| Gold         | go_shipment_facts   | DISTANCE             | Silver       | sv_shipment         | DISTANCE             | Must be numeric, non-negative (2.3.2, 1.2.3); consistent UOM (1.3.1)             | Convert units if mixed; flag anomalies; exclude zero-distance from rate calcs (3.1.1)                    |
| Gold         | go_shipment_facts   | OUT_OF_ROUTE_DISTANCE| Silver       | sv_shipment         | OUT_OF_ROUTE_DISTANCE| Must be numeric, non-negative; must not exceed DISTANCE (1.2.3, 3.2.3)           | Validate and flag if OUT_OF_ROUTE_DISTANCE > DISTANCE                                                    |
| Gold         | go_shipment_facts   | BUSINESS_PARTNER_ID  | Silver       | sv_shipment         | BUSINESS_PARTNER_ID  | Must reference valid partner (2.5.1); extraction logic required (2.4.3, 3.3.3)   | Extract from extended attribute; confirm logic                                                           |
| Gold         | go_shipment_facts   | PURCHASE_ORDER       | Silver       | sv_shipment         | PURCHASE_ORDER       | Consistency required (1.4.4)                                                     | Direct mapping                                                                                           |
| Gold         | go_shipment_facts   | BILL_OF_LADING_NUMBER| Silver       | sv_shipment         | BILL_OF_LADING_NUMBER| Should be unique per shipment (2.2.2)                                            | Direct mapping                                                                                           |
| Gold         | go_shipment_facts   | CREATOR_ROLE         | Silver       | sv_shipment         | CREATOR_ROLE         | Must be non-null; join to user role (2.1.5, 2.4.1)                               | Join to go_user_role_dimension for role details                                                          |
| Gold         | go_shipment_facts   | CURRENCY_CODE        | Silver       | sv_shipment         | CURRENCY_CODE        | Must be valid ISO code                                                            | Standardize/validate ISO code                                                                            |
| Gold         | go_shipment_facts   | TOTAL_COST           | Silver       | sv_shipment         | TOTAL_COST           | Must be numeric; handle nulls                                                     | Nulls to 0.0; round to 2 decimals                                                                        |
| Gold         | go_shipment_facts   | MARGIN               | Silver       | sv_shipment         | MARGIN               | Must be numeric; handle nulls                                                     | Nulls to 0.0; round to 2 decimals                                                                        |
| Gold         | go_shipment_facts   | load_date            | Silver       | sv_shipment         | load_date            | Must be valid date                                                                | Direct mapping                                                                                           |
| Gold         | go_shipment_facts   | update_date          | Silver       | sv_shipment         | update_date          | Must be valid date                                                                | Direct mapping                                                                                           |
| Gold         | go_shipment_facts   | source_system        | Silver       | sv_shipment         | source_system        | Must be present                                                                   | Direct mapping                                                                                           |

*Note: For all other fields, direct mapping is applied unless otherwise specified in constraints or transformation rules. All joins to dimension tables are surrogate-key based, and all transformations are compatible with PySpark/Databricks.*

---

### Key Transformation and Validation Logic

- **Fact-Dimension Relationships:**
  - `ASSIGNED_CARRIER_ID` → `go_carrier_dimension.carrier_key`
  - `O_FACILITY_ID`, `D_FACILITY_ID` → `go_facility_dimension.facility_key`
  - `CREATOR_ROLE` → `go_user_role_dimension.user_role_key`
  - `SHIPMENT_STATUS` → `go_shipment_status_codes.status_code`
- **Metric Calculations and Aggregations:**
  - All cost/revenue fields: Nulls replaced with 0.0, rounded to 2 decimals.
  - Distance fields: Convert to consistent UOM (e.g., kilometers); flag and convert mixed units.
  - Out-of-route distance: Flag if exceeds total distance.
  - Zero-distance shipments: Excluded from rate calculations but counted separately.
- **Data Validation Rules:**
  - All mandatory fields must be present and non-null.
  - Uniqueness enforced for SHIPMENT_ID and BILL_OF_LADING_NUMBER.
  - All date fields validated for format and operational range.
  - All reference fields must join to valid dimension records.
- **Cleansing Logic:**
  - Null handling: Numeric fields default to 0.0; string fields default to empty string if required.
  - Duplicate handling: Deduplicate on SHIPMENT_ID at the base grain.
  - Currency/unit standardization: All currency codes validated to ISO; all units standardized.

---

### Example PySpark Transformation Snippet

```python
from pyspark.sql.functions import col, when, lit, round

df = df.withColumn('TOTAL_COST', round(when(col('TOTAL_COST').isNull(), lit(0.0)).otherwise(col('TOTAL_COST')), 2)) \
         .withColumn('MARGIN', round(when(col('MARGIN').isNull(), lit(0.0)).otherwise(col('MARGIN')), 2))
# Distance unit conversion logic here
# Join to dimension tables as per mapping
```

---

## API Cost

**apiCost**: 0.0847

---

outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Data_Mapping

pipelineID: 14676
