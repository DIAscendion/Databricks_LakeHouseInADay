_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Bronze layer data mapping for TMS Shipment application in Medallion architecture (Updated with new columns, metadata, and validation rules)
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Data Mapping (v2)

## Overview
This document defines the data mapping for the Bronze layer in the Medallion architecture implementation for the TMS (Transportation Management System) Shipment application. The Bronze layer serves as the raw data ingestion layer, preserving the original structure and metadata, with minimal transformation. This version includes updates for new columns, metadata, validation rules, and column modifications as per the latest requirements.

---

## Data Mapping for Bronze Layer

| Target Layer | Target Table | Target Field              | Data Type   | Source Layer | Source Table | Source Field         | Transformation Rule | Comments |
|--------------|-------------|--------------------------|-------------|--------------|--------------|---------------------|---------------------|----------|
| Bronze       | shipment    | shipment_id              | STRING      | Source       | shipment     | shipment_id         | 1-1 Mapping         | Unique shipment identifier |
| Bronze       | shipment    | customer_id              | BIGINT      | Source       | shipment     | customer_id         | 1-1 Mapping         | Updated to BIGINT for downstream compatibility |
| Bronze       | shipment    | txn_amount               | DOUBLE      | Source       | shipment     | transaction_amount  | Rename, 1-1 Mapping | Renamed from transaction_amount |
| Bronze       | shipment    | shipment_date            | DATE        | Source       | shipment     | shipment_date       | 1-1 Mapping         | |
| Bronze       | shipment    | product_category         | STRING      | Source       | shipment     | product_category    | Category Mapping    | Mapping for new categories via config file |
| Bronze       | shipment    | source_system_id         | STRING      | Source       | shipment     | (N/A)               | New Column          | Unique identifier of the source system |
| Bronze       | shipment    | record_ingestion_timestamp | TIMESTAMP | Source       | shipment     | (N/A)               | New Column          | Ingestion timestamp |
| Bronze       | shipment    | data_quality_score       | FLOAT       | Source       | shipment     | (N/A)               | New Column          | Calculated per quality rules |

*Column `legacy_flag` has been removed as per requirements.*

---

## Transformation & Validation Rules

- **product_category**: Mapped using external configuration for new categories introduced in the source system.
- **txn_amount**: Validation rule applied to ensure no negative values. Records with negative values are flagged for review.
- **data_quality_score**: Calculated based on predefined quality rules (see Data Quality section).

---

## Data Quality & Metadata

- **data_quality_score**: Field added to track the quality of each record (FLOAT). Calculated during ingestion based on completeness, accuracy, and validity checks.
- **record_ingestion_timestamp**: Captures the timestamp when the record is loaded into the Bronze layer.
- **source_system_id**: Captures the unique identifier of the source system for traceability.

---

## Assumptions & Notes

- All data types are compatible with Databricks Delta Lake and PySpark.
- No business logic or data cleansing is applied in the Bronze layer.
- The mapping for new product categories is maintained in a separate configuration file.
- The column `legacy_flag` is dropped and will not be available in the Bronze layer.
- All changes are documented inline in the mapping table and comments section.

---

## API Cost Reporting

apiCost: 0.05 // Cost consumed by the API for this call (in USD)

---

## Version History

| Version | Date       | Description                                  |
|---------|------------|----------------------------------------------|
| 1       |            | Initial Bronze Model Data Mapping            |
| 2       |            | Added new columns, metadata, validation rules, modified and renamed columns, removed legacy_flag |

---

## Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Model_Data_Mapping

## PipelineID
12301
