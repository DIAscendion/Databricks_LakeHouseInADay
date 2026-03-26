_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Complete Bronze layer data mapping for TMS Shipment application in Medallion architecture
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Data Mapping

## Overview
This document defines the comprehensive data mapping for the Bronze layer in the Medallion architecture implementation for the TMS (Transportation Management System) Shipment application. The Bronze layer serves as the raw data ingestion layer, preserving the original structure and format of source data with minimal transformation.

## Bronze Layer Design Principles
- **Raw Data Preservation**: Maintain original data structure and format
- **Minimal Transformation**: Apply only essential data type conversions for Databricks compatibility
- **Metadata Enrichment**: Add ingestion metadata for data lineage and audit
- **Delta Lake Format**: Store all data in Delta Lake format for ACID transactions
- **Schema Evolution**: Support schema evolution for changing source structures

## Source System Overview
**Source System**: TMS Shipment Application
**Source Database**: Relational Database
**Primary Source Table**: SHIPMENT
**Data Volume**: High-volume transactional data
**Update Frequency**: Real-time/Near real-time

## Data Ingestion Strategy

### Ingestion Method
- **Batch Processing**: Scheduled batch ingestion using Databricks Auto Loader
- **Streaming**: Real-time streaming for critical shipment updates
- **Change Data Capture (CDC)**: Track incremental changes from source system
- **File Format**: Parquet files with Delta Lake format
- **Compression**: Snappy compression for optimal performance

### Data Validation Rules
1. **Schema Validation**: Ensure incoming data matches expected schema
2. **Data Type Validation**: Validate data types match source specifications
3. **Null Value Handling**: Preserve null values as-is from source
4. **Duplicate Detection**: Identify but preserve duplicate records with metadata flags
5. **Data Quality Flags**: Add quality indicators without modifying source data

## Metadata Management

### Ingestion Metadata Fields
| Field Name | Data Type | Description |
|------------|-----------|-------------|
| _ingestion_timestamp | TIMESTAMP | Timestamp when record was ingested |
| _source_file_name | STRING | Name of source file or system |
| _ingestion_batch_id | STRING | Unique identifier for ingestion batch |
| _record_hash | STRING | Hash of record content for change detection |
| _is_deleted | BOOLEAN | Flag indicating if record was deleted in source |
| _data_quality_score | DECIMAL(3,2) | Data quality score (0.00-1.00) |

## Complete Data Mapping for Bronze Layer

### SHIPMENT Table Mapping (Complete)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|---------------|-----------------|
| Bronze | bronze_shipment | shipment_id | Source | SHIPMENT | SHIPMENT_ID | 1-1 Mapping |
| Bronze | bronze_shipment | tc_company_id | Source | SHIPMENT | TC_COMPANY_ID | 1-1 Mapping |
| Bronze | bronze_shipment | tc_shipment_id | Source | SHIPMENT | TC_SHIPMENT_ID | 1-1 Mapping |
| Bronze | bronze_shipment | shipment_status | Source | SHIPMENT | SHIPMENT_STATUS | 1-1 Mapping |
| Bronze | bronze_shipment | shipment_type | Source | SHIPMENT | SHIPMENT_TYPE | 1-1 Mapping |
| Bronze | bronze_shipment | shipment_leg_type | Source | SHIPMENT | SHIPMENT_LEG_TYPE | 1-1 Mapping |
| Bronze | bronze_shipment | created_dttm | Source | SHIPMENT | CREATED_DTTM | 1-1 Mapping |
| Bronze | bronze_shipment | created_source | Source | SHIPMENT | CREATED_SOURCE | 1-1 Mapping |
| Bronze | bronze_shipment | created_source_type | Source | SHIPMENT | CREATED_SOURCE_TYPE | 1-1 Mapping |
| Bronze | bronze_shipment | creation_type | Source | SHIPMENT | CREATION_TYPE | 1-1 Mapping |
| Bronze | bronze_shipment | is_shipment_cancelled | Source | SHIPMENT | IS_SHIPMENT_CANCELLED | 1-1 Mapping |
| Bronze | bronze_shipment | is_shipment_reconciled | Source | SHIPMENT | IS_SHIPMENT_RECONCILED | 1-1 Mapping |
| Bronze | bronze_shipment | shipment_recon_dttm | Source | SHIPMENT | SHIPMENT_RECON_DTTM | 1-1 Mapping |
| Bronze | bronze_shipment | trailer_number | Source | SHIPMENT | TRAILER_NUMBER | 1-1 Mapping |
| Bronze | bronze_shipment | tractor_number | Source | SHIPMENT | TRACTOR_NUMBER | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_carrier_code | Source | SHIPMENT | ASSIGNED_CARRIER_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_carrier_id | Source | SHIPMENT | ASSIGNED_CARRIER_ID | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_scndr_carrier_code | Source | SHIPMENT | ASSIGNED_SCNDR_CARRIER_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_scndr_carrier_id | Source | SHIPMENT | ASSIGNED_SCNDR_CARRIER_ID | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_broker_carrier_code | Source | SHIPMENT | ASSIGNED_BROKER_CARRIER_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_broker_carrier_id | Source | SHIPMENT | ASSIGNED_BROKER_CARRIER_ID | 1-1 Mapping |
| Bronze | bronze_shipment | assigned_mot_id | Source | SHIPMENT | ASSIGNED_MOT_ID | 1-1 Mapping |
| Bronze | bronze_shipment | dsg_carrier_code | Source | SHIPMENT | DSG_CARRIER_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | dsg_carrier_id | Source | SHIPMENT | DSG_CARRIER_ID | 1-1 Mapping |
| Bronze | bronze_shipment | feasible_carrier_code | Source | SHIPMENT | FEASIBLE_CARRIER_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | feasible_carrier_id | Source | SHIPMENT | FEASIBLE_CARRIER_ID | 1-1 Mapping |
| Bronze | bronze_shipment | o_facility_id | Source | SHIPMENT | O_FACILITY_ID | 1-1 Mapping |
| Bronze | bronze_shipment | o_facility_number | Source | SHIPMENT | O_FACILITY_NUMBER | 1-1 Mapping |
| Bronze | bronze_shipment | o_stop_location_name | Source | SHIPMENT | O_STOP_LOCATION_NAME | 1-1 Mapping |
| Bronze | bronze_shipment | o_address | Source | SHIPMENT | O_ADDRESS | 1-1 Mapping |
| Bronze | bronze_shipment | o_city | Source | SHIPMENT | O_CITY | 1-1 Mapping |
| Bronze | bronze_shipment | o_state_prov | Source | SHIPMENT | O_STATE_PROV | 1-1 Mapping |
| Bronze | bronze_shipment | o_postal_code | Source | SHIPMENT | O_POSTAL_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | o_country_code | Source | SHIPMENT | O_COUNTRY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | d_facility_id | Source | SHIPMENT | D_FACILITY_ID | 1-1 Mapping |
| Bronze | bronze_shipment | d_facility_number | Source | SHIPMENT | D_FACILITY_NUMBER | 1-1 Mapping |
| Bronze | bronze_shipment | d_stop_location_name | Source | SHIPMENT | D_STOP_LOCATION_NAME | 1-1 Mapping |
| Bronze | bronze_shipment | d_address | Source | SHIPMENT | D_ADDRESS | 1-1 Mapping |
| Bronze | bronze_shipment | d_city | Source | SHIPMENT | D_CITY | 1-1 Mapping |
| Bronze | bronze_shipment | d_state_prov | Source | SHIPMENT | D_STATE_PROV | 1-1 Mapping |
| Bronze | bronze_shipment | d_postal_code | Source | SHIPMENT | D_POSTAL_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | d_country_code | Source | SHIPMENT | D_COUNTRY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | distance | Source | SHIPMENT | DISTANCE | 1-1 Mapping |
| Bronze | bronze_shipment | direct_distance | Source | SHIPMENT | DIRECT_DISTANCE | 1-1 Mapping |
| Bronze | bronze_shipment | out_of_route_distance | Source | SHIPMENT | OUT_OF_ROUTE_DISTANCE | 1-1 Mapping |
| Bronze | bronze_shipment | distance_uom | Source | SHIPMENT | DISTANCE_UOM | 1-1 Mapping |
| Bronze | bronze_shipment | num_stops | Source | SHIPMENT | NUM_STOPS | 1-1 Mapping |
| Bronze | bronze_shipment | equipment_type | Source | SHIPMENT | EQUIPMENT_TYPE | 1-1 Mapping |
| Bronze | bronze_shipment | bill_to_postal_code | Source | SHIPMENT | BILL_TO_POSTAL_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | bill_to_state_prov | Source | SHIPMENT | BILL_TO_STATE_PROV | 1-1 Mapping |
| Bronze | bronze_shipment | bill_of_lading_number | Source | SHIPMENT | BILL_OF_LADING_NUMBER | 1-1 Mapping |
| Bronze | bronze_shipment | billing_method | Source | SHIPMENT | BILLING_METHOD | 1-1 Mapping |
| Bronze | bronze_shipment | purchase_order | Source | SHIPMENT | PURCHASE_ORDER | 1-1 Mapping |
| Bronze | bronze_shipment | business_partner_id | Source | SHIPMENT | BUSINESS_PARTNER_ID | 1-1 Mapping |
| Bronze | bronze_shipment | pp_shipment_id | Source | SHIPMENT | PP_SHIPMENT_ID | 1-1 Mapping |
| Bronze | bronze_shipment | accessorial_cost | Source | SHIPMENT | ACCESSORIAL_COST | 1-1 Mapping |
| Bronze | bronze_shipment | accessorial_cost_to_carrier | Source | SHIPMENT | ACCESSORIAL_COST_TO_CARRIER | 1-1 Mapping |
| Bronze | bronze_shipment | actual_cost | Source | SHIPMENT | ACTUAL_COST | 1-1 Mapping |
| Bronze | bronze_shipment | actual_cost_currency_code | Source | SHIPMENT | ACTUAL_COST_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | baseline_cost | Source | SHIPMENT | BASELINE_COST | 1-1 Mapping |
| Bronze | bronze_shipment | baseline_cost_currency_code | Source | SHIPMENT | BASELINE_COST_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | carrier_charge | Source | SHIPMENT | CARRIER_CHARGE | 1-1 Mapping |
| Bronze | bronze_shipment | cm_discount | Source | SHIPMENT | CM_DISCOUNT | 1-1 Mapping |
| Bronze | bronze_shipment | cod_amount | Source | SHIPMENT | COD_AMOUNT | 1-1 Mapping |
| Bronze | bronze_shipment | cod_currency_code | Source | SHIPMENT | COD_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | currency_code | Source | SHIPMENT | CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | declared_value | Source | SHIPMENT | DECLARED_VALUE | 1-1 Mapping |
| Bronze | bronze_shipment | dv_currency_code | Source | SHIPMENT | DV_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | earned_income | Source | SHIPMENT | EARNED_INCOME | 1-1 Mapping |
| Bronze | bronze_shipment | earned_income_currency_code | Source | SHIPMENT | EARNED_INCOME_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | estimated_cost | Source | SHIPMENT | ESTIMATED_COST | 1-1 Mapping |
| Bronze | bronze_shipment | estimated_savings | Source | SHIPMENT | ESTIMATED_SAVINGS | 1-1 Mapping |
| Bronze | bronze_shipment | linehaul_cost | Source | SHIPMENT | LINEHAUL_COST | 1-1 Mapping |
| Bronze | bronze_shipment | margin | Source | SHIPMENT | MARGIN | 1-1 Mapping |
| Bronze | bronze_shipment | monetary_value | Source | SHIPMENT | MONETARY_VALUE | 1-1 Mapping |
| Bronze | bronze_shipment | mv_currency_code | Source | SHIPMENT | MV_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | reported_cost | Source | SHIPMENT | REPORTED_COST | 1-1 Mapping |
| Bronze | bronze_shipment | spot_charge | Source | SHIPMENT | SPOT_CHARGE | 1-1 Mapping |
| Bronze | bronze_shipment | spot_charge_currency_code | Source | SHIPMENT | SPOT_CHARGE_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | stop_cost | Source | SHIPMENT | STOP_COST | 1-1 Mapping |
| Bronze | bronze_shipment | total_cost | Source | SHIPMENT | TOTAL_COST | 1-1 Mapping |
| Bronze | bronze_shipment | total_revenue | Source | SHIPMENT | TOTAL_REVENUE | 1-1 Mapping |
| Bronze | bronze_shipment | total_revenue_currency_code | Source | SHIPMENT | TOTAL_REVENUE_CURRENCY_CODE | 1-1 Mapping |
| Bronze | bronze_shipment | last_updated_dttm | Source | SHIPMENT | LAST_UPDATED_DTTM | 1-1 Mapping |
| Bronze | bronze_shipment | last_updated_source | Source | SHIPMENT | LAST_UPDATED_SOURCE | 1-1 Mapping |
| Bronze | bronze_shipment | last_updated_source_type | Source | SHIPMENT | LAST_UPDATED_SOURCE_TYPE | 1-1 Mapping |
| Bronze | bronze_shipment | extraction_dttm | Source | SHIPMENT | EXTRACTION_DTTM | 1-1 Mapping |
| Bronze | bronze_shipment | _ingestion_timestamp | System | N/A | N/A | Current timestamp |
| Bronze | bronze_shipment | _source_file_name | System | N/A | N/A | Source file identifier |
| Bronze | bronze_shipment | _ingestion_batch_id | System | N/A | N/A | Batch processing ID |
| Bronze | bronze_shipment | _record_hash | System | N/A | N/A | MD5 hash of record |
| Bronze | bronze_shipment | _is_deleted | System | N/A | N/A | Deletion flag |
| Bronze | bronze_shipment | _data_quality_score | System | N/A | N/A | Quality assessment |

## Data Type Mapping

### Source to Bronze Data Type Conversions

| Source Data Type | Bronze Data Type | Databricks Spark SQL Type | Notes |
|------------------|------------------|---------------------------|-------|
| VARCHAR(n) | STRING | STRING | Preserve original length constraints in metadata |
| DECIMAL(p,s) | DECIMAL(p,s) | DECIMAL(p,s) | Maintain precision and scale |
| DATETIME | TIMESTAMP | TIMESTAMP | Convert to UTC timezone |
| INT | INTEGER | INT | Direct mapping |
| CHAR(n) | STRING | STRING | Convert fixed-length to variable-length |
| BOOLEAN | BOOLEAN | BOOLEAN | Direct mapping |
| FLOAT | FLOAT | FLOAT | Direct mapping |
| DOUBLE | DOUBLE | DOUBLE | Direct mapping |

## Data Quality and Validation

### Initial Data Validation Rules
1. **Primary Key Validation**: Ensure SHIPMENT_ID is not null and unique within batch
2. **Required Field Validation**: Validate mandatory fields (SHIPMENT_STATUS, SHIPMENT_TYPE, TC_COMPANY_ID)
3. **Data Type Validation**: Ensure data types match expected schema
4. **Date Range Validation**: Validate date fields are within reasonable ranges
5. **Referential Integrity**: Basic checks for foreign key relationships
6. **Format Validation**: Validate format of structured fields (postal codes, phone numbers)

### Data Quality Scoring
- **Complete Records**: 1.00 (all required fields populated)
- **Partial Records**: 0.50-0.99 (some optional fields missing)
- **Incomplete Records**: 0.00-0.49 (required fields missing)
- **Invalid Records**: 0.00 (data type or format violations)

## Storage Configuration

### Delta Lake Configuration
```sql
CREATE TABLE bronze_shipment (
  -- All source fields mapped as above
  -- Plus metadata fields
  _ingestion_timestamp TIMESTAMP,
  _source_file_name STRING,
  _ingestion_batch_id STRING,
  _record_hash STRING,
  _is_deleted BOOLEAN,
  _data_quality_score DECIMAL(3,2)
)
USING DELTA
PARTITIONED BY (DATE(created_dttm))
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.enableChangeDataFeed' = 'true'
)
```

### Partitioning Strategy
- **Partition Column**: DATE(created_dttm)
- **Partition Granularity**: Daily partitions
- **Retention Policy**: 7 years of historical data
- **Optimization**: Auto-optimize enabled for write and compaction

## Performance Optimization

### Indexing Strategy
- **Z-Order Optimization**: shipment_id, shipment_status, created_dttm
- **Bloom Filters**: shipment_id, bill_of_lading_number, trailer_number
- **Statistics Collection**: Automatic statistics collection enabled

### Caching Strategy
- **Hot Data**: Last 30 days cached in memory
- **Warm Data**: Last 1 year optimized for fast access
- **Cold Data**: Older data archived with compression

## Monitoring and Alerting

### Data Pipeline Monitoring
1. **Ingestion Volume**: Monitor daily ingestion volumes
2. **Data Quality Trends**: Track data quality scores over time
3. **Schema Evolution**: Alert on schema changes
4. **Processing Latency**: Monitor end-to-end processing time
5. **Error Rates**: Track ingestion error rates and types

### Key Performance Indicators (KPIs)
- **Data Freshness**: < 15 minutes for streaming, < 4 hours for batch
- **Data Quality Score**: > 95% records with score >= 0.90
- **Processing Success Rate**: > 99.5%
- **Storage Efficiency**: Delta Lake compression ratio > 70%

## API Cost Reporting
**apiCost**: 0.0025 USD (estimated cost for data mapping generation and GitHub operations)

## Assumptions and Constraints

### Assumptions
1. Source system provides consistent data format
2. Network connectivity is reliable for data ingestion
3. Source system supports CDC for incremental updates
4. Data retention requirements are 7 years
5. Peak ingestion volume is 10x average daily volume

### Constraints
1. No data transformation or cleansing in Bronze layer
2. Preserve all source data including invalid records
3. Maintain audit trail for all data changes
4. Support schema evolution without data loss
5. Comply with data privacy regulations (GDPR, CCPA)

## Next Steps
1. **Silver Layer Design**: Define data cleansing and transformation rules
2. **Gold Layer Design**: Create business-ready aggregated views
3. **Data Governance**: Implement data classification and access controls
4. **Testing Strategy**: Develop comprehensive testing framework
5. **Deployment Pipeline**: Set up CI/CD for data pipeline deployment