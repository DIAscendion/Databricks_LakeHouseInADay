_____________________________________________
## *Author*: Ascendion AVA+
## *Created on*: 
## *Description*: Gold Layer Logical Data Model for Shipment Report Requirements in Medallion Architecture
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Gold Layer Logical Data Model

## 1. Gold Layer Logical Model

### 1.1 Fact Tables

#### Go_Shipment_Facts
**Description**: Central fact table containing shipment transactional data with measures and foreign keys to dimensions
**Table Type**: Fact
**SCD Type**: N/A

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| shipment_reference_number | Unique reference identifier for each shipment | String | Non-PII |
| shipment_status | Current operational state of the shipment | String | Non-PII |
| shipment_type | Category or classification of the shipment | String | Non-PII |
| leg_type | Segment or leg classification of the shipment | String | Non-PII |
| creation_date | Date when the shipment record was created | Date | Non-PII |
| creation_source | Method or system source of shipment creation | String | Non-PII |
| cancelled_flag | Boolean indicator if shipment was cancelled | Boolean | Non-PII |
| reconciled_flag | Boolean indicator if shipment was reconciled | Boolean | Non-PII |
| reconciliation_date | Date when shipment was reconciled | Date | Non-PII |
| trailer_number | Trailer assigned to the shipment | String | Non-PII |
| total_route_distance | Total distance of the shipment route | Decimal | Non-PII |
| direct_distance | Direct distance between origin and destination | Decimal | Non-PII |
| out_of_route_distance | Distance not on optimal route | Decimal | Non-PII |
| distance_unit_of_measure | Unit for distance measurement | String | Non-PII |
| number_of_stops | Total number of stops in shipment route | Integer | Non-PII |
| equipment_type | Type of equipment used for shipment | String | Non-PII |
| bill_of_lading_number | Reference number for shipment billing | String | Non-PII |
| billing_method | Method used for billing the shipment | String | Non-PII |
| purchase_order_reference | Purchase order associated with shipment | String | Non-PII |
| company_identifier | Company associated with the shipment | String | Non-PII |
| business_partner_identifier | Vendor or partner reference identifier | String | Non-PII |
| parent_shipment_reference | Parent shipment reference for tracking | String | Non-PII |
| load_date | Date when record was loaded into Gold layer | Timestamp | Non-PII |
| update_date | Date when record was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

### 1.2 Dimension Tables

#### Go_Carrier_Dimension
**Description**: Dimension table containing carrier information and attributes
**Table Type**: Dimension
**SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| carrier_key | Surrogate key for carrier dimension | String | Non-PII |
| primary_carrier_name | Main carrier assigned to shipment | String | Non-PII |
| secondary_carrier_name | Secondary carrier assigned to shipment | String | Non-PII |
| broker_carrier_name | Broker carrier assigned to shipment | String | Non-PII |
| mode_of_transport | Transportation mode used by carrier | String | Non-PII |
| designated_carrier | Carrier for DC-to-Store master lane | String | Non-PII |
| feasible_carrier | Carrier eligible for assignment | String | Non-PII |
| carrier_status | Current status of the carrier | String | Non-PII |
| effective_start_date | Start date of carrier record validity | Date | Non-PII |
| effective_end_date | End date of carrier record validity | Date | Non-PII |
| is_current | Flag indicating current active record | Boolean | Non-PII |
| load_date | Date when record was loaded into Gold layer | Timestamp | Non-PII |
| update_date | Date when record was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

#### Go_Facility_Dimension
**Description**: Dimension table containing facility location and address information
**Table Type**: Dimension
**SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| facility_key | Surrogate key for facility dimension | String | Non-PII |
| facility_name | Name of the facility | String | Non-PII |
| facility_type | Type of facility (origin/destination) | String | Non-PII |
| facility_address | Street address of the facility | String | Sensitive-PII |
| facility_city | City where facility is located | String | Non-PII |
| facility_state | State or province of facility location | String | Non-PII |
| facility_postal_code | Postal code of facility location | String | Non-PII |
| facility_country | Country where facility is located | String | Non-PII |
| facility_status | Current operational status of facility | String | Non-PII |
| effective_start_date | Start date of facility record validity | Date | Non-PII |
| effective_end_date | End date of facility record validity | Date | Non-PII |
| is_current | Flag indicating current active record | Boolean | Non-PII |
| load_date | Date when record was loaded into Gold layer | Timestamp | Non-PII |
| update_date | Date when record was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

#### Go_User_Role_Dimension
**Description**: Dimension table containing user roles and responsibilities
**Table Type**: Dimension
**SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| user_role_key | Surrogate key for user role dimension | String | Non-PII |
| creator_role | Role of user who created the shipment | String | Non-PII |
| role_description | Description of the user role | String | Non-PII |
| role_department | Department associated with the role | String | Non-PII |
| role_permissions | Permissions associated with the role | String | Non-PII |
| role_status | Current status of the role | String | Non-PII |
| load_date | Date when record was loaded into Gold layer | Timestamp | Non-PII |
| update_date | Date when record was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

### 1.3 Code Tables

#### Go_Shipment_Status_Codes
**Description**: Code table for shipment status values and descriptions
**Table Type**: Code Table
**SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| status_code | Code representing shipment status | String | Non-PII |
| status_description | Description of the shipment status | String | Non-PII |
| status_category | Category grouping of status | String | Non-PII |
| is_active | Flag indicating if status is active | Boolean | Non-PII |
| load_date | Date when record was loaded into Gold layer | Timestamp | Non-PII |
| update_date | Date when record was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

#### Go_Transport_Mode_Codes
**Description**: Code table for transportation modes and their attributes
**Table Type**: Code Table
**SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| transport_mode_code | Code for transportation mode | String | Non-PII |
| transport_mode_description | Description of transportation mode | String | Non-PII |
| transport_category | Category of transportation | String | Non-PII |
| is_active | Flag indicating if mode is active | Boolean | Non-PII |
| load_date | Date when record was loaded into Gold layer | Timestamp | Non-PII |
| update_date | Date when record was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

### 1.4 Process Audit Tables

#### Go_Pipeline_Audit
**Description**: Audit table for tracking pipeline execution details and performance
**Table Type**: Process Audit
**SCD Type**: N/A

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| audit_key | Unique identifier for audit record | String | Non-PII |
| pipeline_name | Name of the executed pipeline | String | Non-PII |
| pipeline_run_id | Unique identifier for pipeline run | String | Non-PII |
| execution_start_time | Start time of pipeline execution | Timestamp | Non-PII |
| execution_end_time | End time of pipeline execution | Timestamp | Non-PII |
| execution_duration_seconds | Duration of pipeline execution in seconds | Integer | Non-PII |
| pipeline_status | Status of pipeline execution | String | Non-PII |
| records_processed | Number of records processed | Integer | Non-PII |
| records_inserted | Number of records inserted | Integer | Non-PII |
| records_updated | Number of records updated | Integer | Non-PII |
| records_deleted | Number of records deleted | Integer | Non-PII |
| source_table_name | Name of source table processed | String | Non-PII |
| target_table_name | Name of target table updated | String | Non-PII |
| pipeline_version | Version of the pipeline executed | String | Non-PII |
| execution_user | User who executed the pipeline | String | Non-PII |
| cluster_details | Details of compute cluster used | String | Non-PII |
| memory_usage_mb | Memory usage during execution | Integer | Non-PII |
| cpu_usage_percent | CPU usage during execution | Decimal | Non-PII |
| error_message | Error message if pipeline failed | String | Non-PII |
| load_date | Date when audit record was created | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

### 1.5 Error Data Tables

#### Go_Data_Validation_Errors
**Description**: Error table for capturing data validation failures and quality issues
**Table Type**: Error Data
**SCD Type**: N/A

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| error_key | Unique identifier for error record | String | Non-PII |
| pipeline_run_id | Pipeline run identifier where error occurred | String | Non-PII |
| table_name | Name of table where validation failed | String | Non-PII |
| column_name | Name of column that failed validation | String | Non-PII |
| record_identifier | Identifier of the record with error | String | Non-PII |
| validation_rule | Name of validation rule that failed | String | Non-PII |
| validation_rule_description | Description of the validation rule | String | Non-PII |
| error_type | Type of validation error | String | Non-PII |
| error_severity | Severity level of the error | String | Non-PII |
| error_message | Detailed error message | String | Non-PII |
| expected_value | Expected value for the field | String | Non-PII |
| actual_value | Actual value that caused the error | String | Non-PII |
| error_count | Number of times this error occurred | Integer | Non-PII |
| first_occurrence_date | Date when error first occurred | Timestamp | Non-PII |
| last_occurrence_date | Date when error last occurred | Timestamp | Non-PII |
| resolution_status | Status of error resolution | String | Non-PII |
| resolution_date | Date when error was resolved | Timestamp | Non-PII |
| resolved_by | User who resolved the error | String | Non-PII |
| load_date | Date when error record was created | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

### 1.6 Aggregated Tables

#### Go_Shipment_Daily_Summary
**Description**: Daily aggregated metrics for shipment performance and KPIs
**Table Type**: Aggregated
**SCD Type**: N/A

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| summary_date | Date for which summary is calculated | Date | Non-PII |
| carrier_key | Foreign key to carrier dimension | String | Non-PII |
| facility_key | Foreign key to facility dimension | String | Non-PII |
| total_shipment_count | Total number of shipments | Integer | Non-PII |
| active_shipment_count | Number of active shipments | Integer | Non-PII |
| completed_shipment_count | Number of completed shipments | Integer | Non-PII |
| cancelled_shipment_count | Number of cancelled shipments | Integer | Non-PII |
| reconciled_shipment_count | Number of reconciled shipments | Integer | Non-PII |
| cancelled_shipment_percentage | Percentage of cancelled shipments | Decimal | Non-PII |
| reconciled_shipment_percentage | Percentage of reconciled shipments | Decimal | Non-PII |
| total_route_distance_sum | Sum of total route distances | Decimal | Non-PII |
| average_route_distance | Average route distance | Decimal | Non-PII |
| total_stops_sum | Sum of all stops | Integer | Non-PII |
| average_stops_per_shipment | Average stops per shipment | Decimal | Non-PII |
| out_of_route_distance_sum | Sum of out-of-route distances | Decimal | Non-PII |
| out_of_route_percentage | Percentage of out-of-route distance | Decimal | Non-PII |
| route_efficiency_index | Direct distance / Total distance ratio | Decimal | Non-PII |
| broker_carrier_usage_count | Count of shipments using broker carrier | Integer | Non-PII |
| broker_carrier_usage_percentage | Percentage of broker carrier usage | Decimal | Non-PII |
| load_date | Date when summary was calculated | Timestamp | Non-PII |
| update_date | Date when summary was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

#### Go_Carrier_Performance_Monthly
**Description**: Monthly aggregated carrier performance metrics and KPIs
**Table Type**: Aggregated
**SCD Type**: N/A

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| summary_month | Month for which summary is calculated | Date | Non-PII |
| carrier_key | Foreign key to carrier dimension | String | Non-PII |
| total_shipments_assigned | Total shipments assigned to carrier | Integer | Non-PII |
| completed_shipments | Number of completed shipments | Integer | Non-PII |
| cancelled_shipments | Number of cancelled shipments | Integer | Non-PII |
| completion_rate_percentage | Percentage of completed shipments | Decimal | Non-PII |
| cancellation_rate_percentage | Percentage of cancelled shipments | Decimal | Non-PII |
| total_distance_covered | Total distance covered by carrier | Decimal | Non-PII |
| average_distance_per_shipment | Average distance per shipment | Decimal | Non-PII |
| total_stops_serviced | Total stops serviced by carrier | Integer | Non-PII |
| average_stops_per_shipment | Average stops per shipment | Decimal | Non-PII |
| route_efficiency_score | Overall route efficiency score | Decimal | Non-PII |
| on_time_performance_percentage | Percentage of on-time deliveries | Decimal | Non-PII |
| carrier_utilization_percentage | Percentage of carrier capacity utilized | Decimal | Non-PII |
| load_date | Date when summary was calculated | Timestamp | Non-PII |
| update_date | Date when summary was last updated | Timestamp | Non-PII |
| source_system | Source system that provided the data | String | Non-PII |

## 2. Conceptual Data Model Diagram

| Source Table | Relationship Key Field | Target Table | Relationship Type |
|--------------|------------------------|--------------|-------------------|
| Go_Shipment_Facts | carrier_key | Go_Carrier_Dimension | Many-to-One |
| Go_Shipment_Facts | origin_facility_key | Go_Facility_Dimension | Many-to-One |
| Go_Shipment_Facts | destination_facility_key | Go_Facility_Dimension | Many-to-One |
| Go_Shipment_Facts | creator_role_key | Go_User_Role_Dimension | Many-to-One |
| Go_Shipment_Facts | shipment_status | Go_Shipment_Status_Codes | Many-to-One |
| Go_Carrier_Dimension | mode_of_transport | Go_Transport_Mode_Codes | Many-to-One |
| Go_Shipment_Daily_Summary | carrier_key | Go_Carrier_Dimension | Many-to-One |
| Go_Shipment_Daily_Summary | facility_key | Go_Facility_Dimension | Many-to-One |
| Go_Carrier_Performance_Monthly | carrier_key | Go_Carrier_Dimension | Many-to-One |
| Go_Pipeline_Audit | pipeline_run_id | Go_Data_Validation_Errors | One-to-Many |

## 3. Design Rationale and Assumptions

### 3.1 Design Decisions
1. **Dimensional Modeling**: Implemented star schema with fact tables at the center and dimension tables for descriptive attributes
2. **SCD Implementation**: 
   - Type 2 for Carrier and Facility dimensions to track historical changes
   - Type 1 for User Role and Code tables as they require current state only
3. **Naming Convention**: All Gold layer tables prefixed with 'Go_' for easy identification
4. **Audit Trail**: Comprehensive audit and error tracking tables for data lineage and quality monitoring
5. **Aggregation Strategy**: Pre-calculated daily and monthly summaries for improved query performance

### 3.2 Key Assumptions
1. Shipment reference number serves as the business key for fact table grain
2. Facility addresses are considered sensitive PII due to potential location privacy concerns
3. Distance measurements are standardized to a single unit of measure in Gold layer
4. Billing method transformation from numeric to string is handled in Silver to Gold processing
5. Process audit captures both successful and failed pipeline executions
6. Data validation errors are retained for compliance and troubleshooting purposes

### 3.3 Performance Considerations
1. Fact table partitioned by creation_date for efficient querying
2. Dimension tables include surrogate keys for better join performance
3. Aggregated tables reduce computation overhead for common reporting scenarios
4. Audit tables enable monitoring of data processing performance and quality

## apiCost: 0.0847

**Output URL**: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Model_Logical

**Pipeline ID**: 12368