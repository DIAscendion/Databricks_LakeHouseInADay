_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Silver Layer Logical Data Model for Shipment Report Requirements
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Silver Layer Logical Data Model

## 1. Silver Layer Logical Model

### 1.1 Si_Shipment
**Description**: Core shipment information with operational details, origin/destination, and status tracking

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| shipment_reference_number | STRING | Unique reference identifier for each shipment |
| shipment_status | STRING | Current operational state of the shipment (active, completed, cancelled, reconciled) |
| shipment_type | STRING | Classification or category of the shipment |
| leg_type | STRING | Segment or leg classification within the shipment route |
| creation_date | DATE | Date when the shipment record was created in the system |
| creation_source | STRING | Method or source of shipment creation (manual, API, integration) |
| creator_role | STRING | User role responsible for creating the shipment record |
| cancelled_flag | BOOLEAN | Indicator flag showing if the shipment has been cancelled |
| reconciled_flag | BOOLEAN | Indicator flag showing if the shipment has been reconciled |
| trailer_number | STRING | Identifier of the trailer assigned to the shipment |
| reconciliation_date | DATE | Date when the shipment was reconciled |

### 1.2 Si_Carrier
**Description**: Carrier assignment and transportation mode information for shipments

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| shipment_reference_number | STRING | Reference to the associated shipment |
| primary_carrier_name | STRING | Name of the main carrier assigned to the shipment |
| secondary_carrier_name | STRING | Name of the secondary carrier assigned to the shipment |
| broker_carrier_name | STRING | Name of the broker carrier assigned to the shipment |
| mode_of_transport | STRING | Transportation mode used (road, rail, air, sea, etc.) |
| designated_carrier | STRING | Carrier designated for DC-to-Store master lane or static route |
| feasible_carrier | STRING | Carrier that is eligible and available for assignment |

### 1.3 Si_Facility
**Description**: Origin and destination facility information including complete address details

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| shipment_reference_number | STRING | Reference to the associated shipment |
| origin_facility_name | STRING | Name of the facility where the shipment originates |
| origin_address | STRING | Street address of the origin facility |
| origin_city | STRING | City where the origin facility is located |
| origin_state | STRING | State or province of the origin facility |
| origin_postal_code | STRING | Postal or ZIP code of the origin facility |
| origin_country | STRING | Country where the origin facility is located |
| destination_facility_name | STRING | Name of the facility where the shipment is delivered |
| destination_address | STRING | Street address of the destination facility |
| destination_city | STRING | City where the destination facility is located |
| destination_state | STRING | State or province of the destination facility |
| destination_postal_code | STRING | Postal or ZIP code of the destination facility |
| destination_country | STRING | Country where the destination facility is located |

### 1.4 Si_Route
**Description**: Route planning and distance information for shipment transportation

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| shipment_reference_number | STRING | Reference to the associated shipment |
| total_route_distance | DECIMAL(10,2) | Total distance covered in the complete shipment route |
| direct_distance | DECIMAL(10,2) | Direct point-to-point distance between origin and destination |
| out_of_route_distance | DECIMAL(10,2) | Additional distance that deviates from the optimal direct route |
| distance_unit_of_measure | STRING | Unit of measurement for distance values (miles, kilometers) |
| number_of_stops | INTEGER | Total count of stops included in the shipment route |
| equipment_type | STRING | Type of equipment or vehicle used for transportation |

### 1.5 Si_Billing
**Description**: Billing and financial information related to shipment processing

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| shipment_reference_number | STRING | Reference to the associated shipment |
| bill_to_postal_code | STRING | Postal code of the party responsible for billing |
| bill_to_state_province | STRING | State or province of the party responsible for billing |
| bill_of_lading_number | STRING | Official document reference number for shipment billing |
| billing_method | STRING | Method or process used for billing the shipment |
| purchase_order_reference | STRING | Purchase order number associated with the shipment |
| company_identifier | STRING | Identifier of the company associated with the shipment |

### 1.6 Si_Business_Partner
**Description**: Vendor and business partner information associated with shipments

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| shipment_reference_number | STRING | Reference to the associated shipment |
| business_partner_identifier | STRING | Unique identifier for the vendor or business partner |
| parent_shipment_reference | STRING | Reference to parent shipment for hierarchical relationships |

### 1.7 Si_User_Role
**Description**: User role information for shipment creation and management audit

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| creator_role | STRING | Role designation of the user responsible for shipment creation |
| role_description | STRING | Detailed description of the user role and responsibilities |

### 1.8 Si_Data_Quality_Errors
**Description**: Error data structure for capturing data validation and quality check failures

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| error_id | STRING | Unique identifier for the error record |
| source_table | STRING | Name of the source table where the error occurred |
| source_record_id | STRING | Identifier of the source record that failed validation |
| error_type | STRING | Category of error (validation, constraint, format, etc.) |
| error_description | STRING | Detailed description of the error encountered |
| error_column | STRING | Specific column name where the error was detected |
| error_value | STRING | Actual value that caused the validation failure |
| expected_value | STRING | Expected value or format for the failed validation |
| error_severity | STRING | Severity level of the error (critical, warning, info) |
| error_timestamp | TIMESTAMP | Date and time when the error was detected |
| pipeline_run_id | STRING | Identifier of the pipeline run that detected the error |

### 1.9 Si_Pipeline_Audit
**Description**: Audit information for pipeline execution and data processing tracking

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| audit_id | STRING | Unique identifier for the audit record |
| pipeline_name | STRING | Name of the data pipeline that was executed |
| pipeline_run_id | STRING | Unique identifier for the specific pipeline execution |
| source_system | STRING | Name of the source system from which data was processed |
| target_table | STRING | Name of the target table where data was loaded |
| records_processed | BIGINT | Total number of records processed in the pipeline run |
| records_successful | BIGINT | Number of records successfully processed and loaded |
| records_failed | BIGINT | Number of records that failed processing or validation |
| pipeline_start_time | TIMESTAMP | Date and time when the pipeline execution started |
| pipeline_end_time | TIMESTAMP | Date and time when the pipeline execution completed |
| pipeline_status | STRING | Final status of the pipeline execution (success, failed, partial) |
| execution_duration_seconds | INTEGER | Total time taken for pipeline execution in seconds |
| data_volume_mb | DECIMAL(10,2) | Volume of data processed in megabytes |
| created_by | STRING | User or system that initiated the pipeline execution |

## 2. Conceptual Data Model Diagram

| Source Table | Relationship Key Field | Target Table | Relationship Type |
|--------------|------------------------|--------------|-------------------|
| Si_Shipment | shipment_reference_number | Si_Carrier | One-to-Many |
| Si_Shipment | shipment_reference_number | Si_Facility | One-to-Many |
| Si_Shipment | shipment_reference_number | Si_Route | One-to-One |
| Si_Shipment | shipment_reference_number | Si_Billing | One-to-One |
| Si_Shipment | shipment_reference_number | Si_Business_Partner | One-to-Many |
| Si_Shipment | creator_role | Si_User_Role | Many-to-One |
| Si_Data_Quality_Errors | source_record_id | Si_Shipment | Many-to-One |
| Si_Pipeline_Audit | target_table | Si_Shipment | One-to-Many |
| Si_Pipeline_Audit | pipeline_run_id | Si_Data_Quality_Errors | One-to-Many |

## 3. Design Rationale and Key Decisions

### 3.1 Naming Convention
- All Silver layer tables use the "Si_" prefix to clearly identify them as Silver layer entities
- Column names follow snake_case convention for consistency and readability
- Table names reflect the business entities from the conceptual model

### 3.2 Data Type Standardization
- STRING data type used for text fields to accommodate varying lengths
- DECIMAL(10,2) used for distance measurements to ensure precision
- TIMESTAMP used for audit fields requiring precise time tracking
- BOOLEAN used for flag fields to ensure data consistency

### 3.3 Data Quality and Audit Framework
- Si_Data_Quality_Errors table captures all validation failures with detailed context
- Si_Pipeline_Audit table tracks execution metrics and performance data
- Error severity levels enable prioritized error handling and resolution

### 3.4 Key Design Decisions
- Removed all primary key and foreign key constraints as per Silver layer requirements
- Maintained referential relationships through common key fields
- Included comprehensive audit trail for data lineage and quality monitoring
- Standardized data types across similar fields for consistency

### 3.5 Assumptions Made
- Distance measurements are standardized to decimal format with 2 decimal places
- All date fields use consistent DATE format unless time precision is required
- Error handling covers both technical and business rule validation failures
- Pipeline audit captures both successful and failed processing attempts

## apiCost: 0.15