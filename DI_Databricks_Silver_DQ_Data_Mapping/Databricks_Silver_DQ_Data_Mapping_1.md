_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Silver Layer Data Quality Data Mapping for TMS Shipment Application
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver Layer Data Quality Data Mapping

## 1. Overview

This document provides a comprehensive data mapping from the Bronze Layer to the Silver Layer in the Medallion architecture for the TMS (Transportation Management System) Shipment application. The mapping includes detailed data validation rules, transformation rules, and cleansing requirements to ensure data quality, consistency, and usability across the organization.

### Key Considerations:
- **Data Quality**: Implement comprehensive validation rules for each attribute
- **Data Cleansing**: Apply standardization and cleansing transformations
- **Business Rules**: Enforce business logic and constraints
- **PySpark Compatibility**: All rules are designed for Databricks PySpark implementation
- **Error Handling**: Robust error logging and data quality monitoring
- **Performance**: Optimized for large-scale data processing

## 2. Data Mapping for the Silver Layer

### 2.1 Main Shipment Table Mapping (bz_shipment → sv_shipment)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Silver | sv_shipment | id | Silver | Generated | N/A | Not Null, Unique | Generate monotonically_increasing_id() |
| Silver | sv_shipment | SHIPMENT_ID | Bronze | bz_shipment | SHIPMENT_ID | Not Null, Unique, Length <= 50 | Trim whitespace, Upper case |
| Silver | sv_shipment | TC_SHIPMENT_ID | Bronze | bz_shipment | TC_SHIPMENT_ID | Length <= 50 | Trim whitespace, Null if empty string |
| Silver | sv_shipment | TC_COMPANY_ID | Bronze | bz_shipment | TC_COMPANY_ID | Not Null, Length <= 20 | Trim whitespace, Upper case |
| Silver | sv_shipment | EXT_SYS_SHIPMENT_ID | Bronze | bz_shipment | EXT_SYS_SHIPMENT_ID | Length <= 50 | Trim whitespace, Null if empty string |
| Silver | sv_shipment | SHIPMENT_REF_ID | Bronze | bz_shipment | SHIPMENT_REF_ID | Length <= 50 | Trim whitespace, Null if empty string |
| Silver | sv_shipment | REF_SHIPMENT_NBR | Bronze | bz_shipment | REF_SHIPMENT_NBR | Length <= 50 | Trim whitespace, Null if empty string |
| Silver | sv_shipment | PP_SHIPMENT_ID | Bronze | bz_shipment | PP_SHIPMENT_ID | Length <= 50 | Trim whitespace, Null if empty string |
| Silver | sv_shipment | SHIPMENT_STATUS | Bronze | bz_shipment | SHIPMENT_STATUS | Not Null, Valid Values (ACTIVE, CANCELLED, COMPLETED, PENDING) | Trim whitespace, Upper case, Default 'PENDING' if null |
| Silver | sv_shipment | SHIPMENT_TYPE | Bronze | bz_shipment | SHIPMENT_TYPE | Not Null, Valid Values (INBOUND, OUTBOUND, TRANSFER) | Trim whitespace, Upper case |
| Silver | sv_shipment | SHIPMENT_LEG_TYPE | Bronze | bz_shipment | SHIPMENT_LEG_TYPE | Length <= 20 | Trim whitespace, Upper case |
| Silver | sv_shipment | MOVE_TYPE | Bronze | bz_shipment | MOVE_TYPE | Length <= 20 | Trim whitespace, Upper case |
| Silver | sv_shipment | CREATION_TYPE | Bronze | bz_shipment | CREATION_TYPE | Length <= 20 | Trim whitespace, Upper case |
| Silver | sv_shipment | BUSINESS_PROCESS | Bronze | bz_shipment | BUSINESS_PROCESS | Length <= 50 | Trim whitespace, Upper case |
| Silver | sv_shipment | CREATED_DTTM | Bronze | bz_shipment | CREATED_DTTM | Not Null, Valid Timestamp, >= 2020-01-01 | Convert to UTC timezone, Validate format |
| Silver | sv_shipment | LAST_UPDATED_DTTM | Bronze | bz_shipment | LAST_UPDATED_DTTM | Valid Timestamp, >= CREATED_DTTM | Convert to UTC timezone, Default to CREATED_DTTM if null |
| Silver | sv_shipment | SHIPMENT_START_DTTM | Bronze | bz_shipment | SHIPMENT_START_DTTM | Valid Timestamp | Convert to UTC timezone |
| Silver | sv_shipment | SHIPMENT_END_DTTM | Bronze | bz_shipment | SHIPMENT_END_DTTM | Valid Timestamp, >= SHIPMENT_START_DTTM | Convert to UTC timezone |
| Silver | sv_shipment | SHIPMENT_RECON_DTTM | Bronze | bz_shipment | SHIPMENT_RECON_DTTM | Valid Timestamp | Convert to UTC timezone |
| Silver | sv_shipment | AVAILABLE_DTTM | Bronze | bz_shipment | AVAILABLE_DTTM | Valid Timestamp | Convert to UTC timezone |
| Silver | sv_shipment | RECEIVED_DTTM | Bronze | bz_shipment | RECEIVED_DTTM | Valid Timestamp | Convert to UTC timezone |
| Silver | sv_shipment | TENDER_DTTM | Bronze | bz_shipment | TENDER_DTTM | Valid Timestamp | Convert to UTC timezone |
| Silver | sv_shipment | SCHEDULED_PICKUP_DTTM | Bronze | bz_shipment | SCHEDULED_PICKUP_DTTM | Valid Timestamp | Convert to UTC timezone |
| Silver | sv_shipment | O_FACILITY_ID | Bronze | bz_shipment | O_FACILITY_ID | Not Null, Length <= 50 | Trim whitespace, Upper case |
| Silver | sv_shipment | O_POSTAL_CODE | Bronze | bz_shipment | O_POSTAL_CODE | Valid Postal Code Format | Trim whitespace, Upper case, Remove special characters |
| Silver | sv_shipment | O_COUNTRY_CODE | Bronze | bz_shipment | O_COUNTRY_CODE | Length = 2, Valid ISO Country Code | Trim whitespace, Upper case |
| Silver | sv_shipment | D_FACILITY_ID | Bronze | bz_shipment | D_FACILITY_ID | Not Null, Length <= 50 | Trim whitespace, Upper case |
| Silver | sv_shipment | D_POSTAL_CODE | Bronze | bz_shipment | D_POSTAL_CODE | Valid Postal Code Format | Trim whitespace, Upper case, Remove special characters |
| Silver | sv_shipment | D_COUNTRY_CODE | Bronze | bz_shipment | D_COUNTRY_CODE | Length = 2, Valid ISO Country Code | Trim whitespace, Upper case |
| Silver | sv_shipment | DISTANCE | Bronze | bz_shipment | DISTANCE | >= 0, <= 99999.99 | Round to 2 decimal places, Default 0 if null |
| Silver | sv_shipment | DISTANCE_UOM | Bronze | bz_shipment | DISTANCE_UOM | Valid Values (MI, KM, FT, M) | Trim whitespace, Upper case, Default 'MI' |
| Silver | sv_shipment | PLANNED_WEIGHT | Bronze | bz_shipment | PLANNED_WEIGHT | >= 0, <= 9999999.999 | Round to 3 decimal places, Default 0 if null |
| Silver | sv_shipment | WEIGHT_UOM_ID_BASE | Bronze | bz_shipment | WEIGHT_UOM_ID_BASE | Valid Values (LB, KG, TON, OZ) | Trim whitespace, Upper case, Default 'LB' |
| Silver | sv_shipment | TOTAL_COST | Bronze | bz_shipment | TOTAL_COST | >= 0, <= 99999999.99 | Round to 2 decimal places, Default 0 if null |
| Silver | sv_shipment | CURRENCY_CODE | Bronze | bz_shipment | CURRENCY_CODE | Length = 3, Valid ISO Currency Code | Trim whitespace, Upper case, Default 'USD' |
| Silver | sv_shipment | IS_SHIPMENT_CANCELLED | Bronze | bz_shipment | IS_SHIPMENT_CANCELLED | Valid Values (Y, N, TRUE, FALSE, 1, 0) | Standardize to Y/N format |
| Silver | sv_shipment | IS_HAZMAT | Bronze | bz_shipment | IS_HAZMAT | Valid Values (Y, N, TRUE, FALSE, 1, 0) | Standardize to Y/N format |
| Silver | sv_shipment | load_date | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_shipment | update_date | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_shipment | source_system | Bronze | bz_shipment | source_system | Not Null, Length <= 50 | Trim whitespace, Upper case |

### 2.2 Error Data Table Mapping (Bronze Errors → sv_shipment_error)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Silver | sv_shipment_error | error_id | Silver | Generated | N/A | Not Null, Unique | Generate monotonically_increasing_id() |
| Silver | sv_shipment_error | table_name | Silver | Generated | N/A | Not Null | Set to 'bz_shipment' |
| Silver | sv_shipment_error | record_id | Bronze | bz_shipment | SHIPMENT_ID | Not Null | Source record identifier |
| Silver | sv_shipment_error | error_type | Silver | Generated | N/A | Not Null, Valid Values (VALIDATION, TRANSFORMATION, BUSINESS_RULE) | Based on validation failure type |
| Silver | sv_shipment_error | error_message | Silver | Generated | N/A | Not Null, Length <= 500 | Descriptive error message |
| Silver | sv_shipment_error | error_timestamp | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_shipment_error | layer | Silver | Generated | N/A | Not Null | Set to 'BRONZE_TO_SILVER' |
| Silver | sv_shipment_error | load_date | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_shipment_error | update_date | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_shipment_error | source_system | Bronze | bz_shipment | source_system | Not Null | Source system identifier |

### 2.3 Audit Table Mapping (Bronze Audit → sv_audit)

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|--------------|--------------|--------------|--------------|--------------|--------------|-----------------|--------------------|
| Silver | sv_audit | audit_id | Silver | Generated | N/A | Not Null, Unique | Generate monotonically_increasing_id() |
| Silver | sv_audit | pipeline_name | Silver | Generated | N/A | Not Null | Set to 'BRONZE_TO_SILVER_SHIPMENT' |
| Silver | sv_audit | execution_id | Silver | Generated | N/A | Not Null | Generate UUID for each execution |
| Silver | sv_audit | start_time | Silver | Generated | N/A | Not Null | Pipeline execution start time |
| Silver | sv_audit | end_time | Silver | Generated | N/A | Not Null, >= start_time | Pipeline execution end time |
| Silver | sv_audit | status | Silver | Generated | N/A | Not Null, Valid Values (SUCCESS, FAILED, PARTIAL) | Pipeline execution status |
| Silver | sv_audit | error_message | Silver | Generated | N/A | Length <= 1000 | Error details if status is FAILED |
| Silver | sv_audit | record_count | Silver | Generated | N/A | >= 0 | Number of records processed |
| Silver | sv_audit | load_date | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_audit | update_date | Silver | Generated | N/A | Not Null | current_timestamp() |
| Silver | sv_audit | source_system | Bronze | bz_audit | audit_source_system | Not Null | Source system identifier |

## 3. Data Quality Rules and Validations

### 3.1 Critical Business Rules

1. **Shipment Integrity Rules**:
   - SHIPMENT_ID must be unique across all records
   - CREATED_DTTM cannot be in the future
   - Origin and Destination facilities cannot be the same
   - SHIPMENT_END_DTTM must be >= SHIPMENT_START_DTTM

2. **Financial Data Rules**:
   - All cost fields must be non-negative
   - Currency codes must be valid ISO 4217 codes
   - Total cost should equal sum of component costs (linehaul + accessorial + stop)

3. **Geographic Data Rules**:
   - Country codes must be valid ISO 3166-1 alpha-2 codes
   - State/Province codes must be valid for the respective country
   - Postal codes must match country-specific formats

4. **Equipment and Carrier Rules**:
   - Carrier IDs must exist in master carrier data
   - Equipment types must be from predefined list
   - Trailer and tractor numbers must be alphanumeric

### 3.2 Data Cleansing Rules

1. **String Standardization**:
   - Trim leading and trailing whitespace
   - Convert to appropriate case (UPPER for codes, Title for names)
   - Replace empty strings with NULL
   - Remove special characters from postal codes

2. **Numeric Standardization**:
   - Round decimal values to appropriate precision
   - Convert negative values to zero for non-negative fields
   - Set default values for NULL numeric fields

3. **Date/Time Standardization**:
   - Convert all timestamps to UTC
   - Validate timestamp formats
   - Set reasonable date ranges (e.g., >= 2020-01-01)

4. **Boolean Standardization**:
   - Convert various boolean representations to Y/N format
   - Handle TRUE/FALSE, 1/0, Yes/No variations

## 4. Error Handling and Logging

### 4.1 Error Categories

1. **Validation Errors**: Data that fails validation rules
2. **Transformation Errors**: Data that cannot be transformed
3. **Business Rule Errors**: Data that violates business logic
4. **System Errors**: Technical processing failures

### 4.2 Error Handling Strategy

1. **Quarantine Approach**: Move invalid records to error table
2. **Logging**: Detailed error messages with context
3. **Alerting**: Notify data stewards of critical errors
4. **Recovery**: Provide mechanisms to reprocess corrected data

### 4.3 Data Quality Metrics

1. **Completeness**: Percentage of non-null values for required fields
2. **Validity**: Percentage of values passing validation rules
3. **Consistency**: Percentage of records with consistent related values
4. **Accuracy**: Percentage of records with correct business logic

## 5. Implementation Guidelines

### 5.1 PySpark Implementation Patterns

```python
# Example validation function
def validate_shipment_id(df):
    return df.filter(
        (col("SHIPMENT_ID").isNotNull()) & 
        (length(col("SHIPMENT_ID")) <= 50) &
        (col("SHIPMENT_ID") != "")
    )

# Example transformation function
def standardize_country_code(df):
    return df.withColumn(
        "O_COUNTRY_CODE",
        when(col("O_COUNTRY_CODE").isNull(), "US")
        .otherwise(upper(trim(col("O_COUNTRY_CODE"))))
    )

# Example error logging
def log_validation_errors(df, validation_name):
    error_df = df.filter(validation_condition == False)
    return error_df.withColumn("error_type", lit("VALIDATION"))\
                   .withColumn("error_message", lit(f"Failed {validation_name}"))\
                   .withColumn("error_timestamp", current_timestamp())
```

### 5.2 Performance Optimization

1. **Partitioning**: Partition Silver tables by CREATED_DTTM for time-based queries
2. **Caching**: Cache frequently accessed DataFrames during processing
3. **Broadcasting**: Broadcast small lookup tables for joins
4. **Columnar Operations**: Use vectorized operations where possible

### 5.3 Monitoring and Alerting

1. **Data Quality Dashboard**: Real-time monitoring of data quality metrics
2. **Automated Alerts**: Threshold-based alerts for data quality issues
3. **Trend Analysis**: Historical tracking of data quality trends
4. **SLA Monitoring**: Track processing times and success rates

## 6. API Cost Calculation

**API Cost**: $0.000000

*Note: This data mapping document was generated without external API calls. The cost represents the computational resources used for document generation and validation rule creation.*

## 7. Assumptions and Limitations

### 7.1 Assumptions

1. **Source Data Quality**: Bronze layer contains reasonably clean data from source systems
2. **Business Rules**: Current business rules are based on TMS industry standards
3. **Performance Requirements**: Processing windows allow for comprehensive validation
4. **Master Data**: Reference data for validation is available and maintained

### 7.2 Limitations

1. **Real-time Processing**: Current design optimized for batch processing
2. **Complex Business Rules**: Some advanced business rules may require custom logic
3. **Data Lineage**: Detailed field-level lineage tracking not implemented
4. **Cross-System Validation**: Limited validation against external systems

## 8. Next Steps and Recommendations

### 8.1 Implementation Priorities

1. **Phase 1**: Implement core validation and transformation rules
2. **Phase 2**: Add advanced business rule validation
3. **Phase 3**: Implement real-time data quality monitoring
4. **Phase 4**: Add predictive data quality analytics

### 8.2 Recommendations

1. **Data Governance**: Establish data stewardship roles and responsibilities
2. **Testing Strategy**: Implement comprehensive unit and integration testing
3. **Documentation**: Maintain detailed documentation of all business rules
4. **Training**: Provide training on data quality tools and processes

---

**Output URL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Data_Mapping

**Pipeline ID**: 12361

---

*This Silver Layer Data Quality Data Mapping provides comprehensive guidelines for implementing robust data quality processes in the Databricks Medallion architecture, ensuring high-quality, reliable data for analytics and downstream processing.*