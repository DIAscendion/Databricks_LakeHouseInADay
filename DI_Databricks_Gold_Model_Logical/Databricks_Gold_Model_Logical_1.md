_____________________________________________
## *Author*: Ascendion AVA+
## *Created on*:   
## *Description*:   Gold Layer Logical Data Model for Shipment Reporting and Analytics
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# 1. Gold Layer Logical Model

## 1.1 Table List and Structure

### 1.1.1 Go_ShipmentFact (Fact Table)
- **Description**: Stores transactional shipment events, including shipment status, type, routing, and carrier assignment for analytics and reporting.
- **Table Type**: Fact
- **Columns**:
  1. shipment_reference_number: Unique reference for each shipment (String) [PII: No]
  2. shipment_status: Current state of the shipment (String) [PII: No]
  3. shipment_type: Classification of shipment (String) [PII: No]
  4. leg_type: Segment classification within shipment (String) [PII: No]
  5. creation_date: Date shipment was created (Date) [PII: No]
  6. creation_source: Method or system used to create shipment (String) [PII: No]
  7. creator_role: Role of user who created the shipment (String) [PII: No]
  8. cancelled_flag: Indicates if shipment was cancelled (Boolean) [PII: No]
  9. reconciled_flag: Indicates if shipment was reconciled (Boolean) [PII: No]
  10. trailer_number: Identifier for trailer used (String) [PII: No]
  11. company_identifier: Company associated with shipment (String) [PII: No]
  12. parent_shipment_reference: Reference to parent shipment if applicable (String) [PII: No]
  13. origin_facility_name: Name of shipment origin (String) [PII: No]
  14. destination_facility_name: Name of shipment destination (String) [PII: No]
  15. route_reference: Reference to route (String) [PII: No]
  16. bill_of_lading_number: Reference for shipment billing (String) [PII: No]
  17. business_partner_identifier: Identifier for partner/vendor (String) [PII: No]
  18. mode_of_transport: Type of transport used (String) [PII: No]
  19. total_route_distance: Total distance covered by shipment (Decimal(10,2)) [PII: No]
  20. direct_distance: Shortest possible distance (Decimal(10,2)) [PII: No]
  21. out_of_route_distance: Distance exceeding direct route (Decimal(10,2)) [PII: No]
  22. distance_unit_of_measure: Unit for distance (String) [PII: No]
  23. number_of_stops: Total stops in shipment route (Integer) [PII: No]
  24. equipment_type: Type of equipment used (String) [PII: No]
  25. bill_to_postal_code: Postal code for bill-to party (String) [PII: No]
  26. bill_to_state_province: State/province for bill-to party (String) [PII: No]
  27. billing_method: Method used for billing (String) [PII: No]
  28. purchase_order_reference: Reference for purchase order (String) [PII: No]
  29. reconciliation_date: Date shipment was reconciled (Date) [PII: No]
  30. load_date: Date record loaded (DateTime) [PII: No]
  31. update_date: Date record last updated (DateTime) [PII: No]
  32. source_system: Source system identifier (String) [PII: No]

### 1.1.2 Go_CarrierDim (Dimension Table)
- **Description**: Reference data for all carriers, including primary, secondary, broker, designated, and feasible carriers.
- **Table Type**: Dimension
- **SCD Type**: 2 (Tracks historical changes in carrier assignments)
- **Columns**:
  1. primary_carrier_name: Main carrier assigned (String) [PII: No]
  2. secondary_carrier_name: Backup carrier assigned (String) [PII: No]
  3. broker_carrier_name: Broker involved (String) [PII: No]
  4. designated_carrier_name: Carrier for static/master lane routes (String) [PII: No]
  5. feasible_carrier_name: Carrier eligible for assignment (String) [PII: No]
  6. mode_of_transport: Type of transport (String) [PII: No]
  7. load_date: Date record loaded (DateTime) [PII: No]
  8. update_date: Date record last updated (DateTime) [PII: No]
  9. source_system: Source system identifier (String) [PII: No]

### 1.1.3 Go_FacilityDim (Dimension Table)
- **Description**: Reference data for all facilities (origin and destination locations).
- **Table Type**: Dimension
- **SCD Type**: 2 (Tracks historical changes in facility details)
- **Columns**:
  1. facility_name: Name of facility (String) [PII: No]
  2. address: Address details (String) [PII: Yes]
  3. city: City (String) [PII: Yes]
  4. state: State/province (String) [PII: No]
  5. postal_code: Postal code (String) [PII: Yes]
  6. country: Country (String) [PII: No]
  7. load_date: Date record loaded (DateTime) [PII: No]
  8. update_date: Date record last updated (DateTime) [PII: No]
  9. source_system: Source system identifier (String) [PII: No]

### 1.1.4 Go_RouteDim (Dimension Table)
- **Description**: Reference data for shipment routes.
- **Table Type**: Dimension
- **SCD Type**: 1 (No historical tracking required)
- **Columns**:
  1. route_reference: Unique route reference (String) [PII: No]
  2. total_route_distance: Total distance (Decimal(10,2)) [PII: No]
  3. direct_distance: Direct distance (Decimal(10,2)) [PII: No]
  4. out_of_route_distance: Out-of-route distance (Decimal(10,2)) [PII: No]
  5. distance_unit_of_measure: Unit for distance (String) [PII: No]
  6. number_of_stops: Number of stops (Integer) [PII: No]
  7. equipment_type: Equipment type (String) [PII: No]
  8. load_date: Date record loaded (DateTime) [PII: No]
  9. update_date: Date record last updated (DateTime) [PII: No]
  10. source_system: Source system identifier (String) [PII: No]

### 1.1.5 Go_BillingDim (Dimension Table)
- **Description**: Reference data for billing and financial tracking.
- **Table Type**: Dimension
- **SCD Type**: 1 (No historical tracking required)
- **Columns**:
  1. bill_of_lading_number: Reference for shipment billing (String) [PII: No]
  2. billing_method: Method used for billing (String) [PII: No]
  3. purchase_order_reference: Reference for purchase order (String) [PII: No]
  4. bill_to_postal_code: Postal code for bill-to party (String) [PII: No]
  5. bill_to_state_province: State/province for bill-to party (String) [PII: No]
  6. reconciliation_date: Date shipment was reconciled (Date) [PII: No]
  7. load_date: Date record loaded (DateTime) [PII: No]
  8. update_date: Date record last updated (DateTime) [PII: No]
  9. source_system: Source system identifier (String) [PII: No]

### 1.1.6 Go_BusinessPartnerDim (Dimension Table)
- **Description**: Reference data for business partners/vendors.
- **Table Type**: Dimension
- **SCD Type**: 1 (No historical tracking required)
- **Columns**:
  1. business_partner_identifier: Identifier for partner/vendor (String) [PII: No]
  2. load_date: Date record loaded (DateTime) [PII: No]
  3. update_date: Date record last updated (DateTime) [PII: No]
  4. source_system: Source system identifier (String) [PII: No]

### 1.1.7 Go_UserDim (Dimension Table)
- **Description**: Reference data for users (creators/updaters of shipment records).
- **Table Type**: Dimension
- **SCD Type**: 2 (Tracks historical changes in user roles)
- **Columns**:
  1. creator_role: Role of user (String) [PII: No]
  2. creation_source_type: Category of creation source (String) [PII: No]
  3. load_date: Date record loaded (DateTime) [PII: No]
  4. update_date: Date record last updated (DateTime) [PII: No]
  5. source_system: Source system identifier (String) [PII: No]

### 1.1.8 Go_ProcessAudit (Process Audit Table)
- **Description**: Stores process audit details from pipeline execution for data governance and traceability.
- **Table Type**: Audit
- **Columns**:
  1. process_name: Name of the executed process (String) [PII: No]
  2. execution_start_time: Start time of execution (DateTime) [PII: No]
  3. execution_end_time: End time of execution (DateTime) [PII: No]
  4. status: Status of execution (String) [PII: No]
  5. record_count: Number of records processed (Integer) [PII: No]
  6. error_count: Number of errors encountered (Integer) [PII: No]
  7. source_system: Source system identifier (String) [PII: No]
  8. load_date: Date record loaded (DateTime) [PII: No]

### 1.1.9 Go_ErrorData (Error Data Table)
- **Description**: Stores error data from data validation process for monitoring and remediation.
- **Table Type**: Error Data
- **Columns**:
  1. error_type: Type/category of error (String) [PII: No]
  2. error_description: Description of error (String) [PII: No]
  3. error_source: Source of error (String) [PII: No]
  4. error_timestamp: Timestamp of error occurrence (DateTime) [PII: No]
  5. record_reference: Reference to affected record (String) [PII: No]
  6. process_name: Name of process where error occurred (String) [PII: No]
  7. load_date: Date record loaded (DateTime) [PII: No]

### 1.1.10 Go_ShipmentAgg (Aggregated Table)
- **Description**: Stores pre-aggregated shipment KPIs for reporting and dashboarding.
- **Table Type**: Aggregated
- **Columns**:
  1. shipment_status: Shipment status (String) [PII: No]
  2. shipment_type: Shipment type (String) [PII: No]
  3. mode_of_transport: Mode of transport (String) [PII: No]
  4. carrier_name: Carrier name (String) [PII: No]
  5. origin_facility_name: Origin facility (String) [PII: No]
  6. destination_facility_name: Destination facility (String) [PII: No]
  7. total_shipment_count: Number of shipments (Integer) [PII: No]
  8. cancelled_shipment_percent: Cancelled shipments % (Decimal(5,2)) [PII: No]
  9. reconciled_shipment_percent: Reconciled shipments % (Decimal(5,2)) [PII: No]
  10. broker_carrier_usage_percent: Broker carrier usage % (Decimal(5,2)) [PII: No]
  11. on_time_pickup_percent: On-time pickup % (Decimal(5,2)) [PII: No]
  12. out_of_route_distance_percent: Out-of-route distance % (Decimal(5,2)) [PII: No]
  13. average_stops_per_shipment: Average stops per shipment (Decimal(5,2)) [PII: No]
  14. route_efficiency_index: Route efficiency index (Decimal(5,2)) [PII: No]
  15. unreconciled_shipment_count_with_aging: Count and age of unreconciled shipments (String) [PII: No]
  16. creation_volume_trend: Shipments created per day/week (String) [PII: No]
  17. source_mix_percent: Source mix % (Decimal(5,2)) [PII: No]
  18. load_date: Date record loaded (DateTime) [PII: No]

## 1.2 Relationships and Rationale
- Go_ShipmentFact connects to Go_CarrierDim by carrier name fields (primary, secondary, etc.).
- Go_ShipmentFact connects to Go_FacilityDim by origin_facility_name and destination_facility_name.
- Go_ShipmentFact connects to Go_RouteDim by route_reference.
- Go_ShipmentFact connects to Go_BillingDim by bill_of_lading_number.
- Go_ShipmentFact connects to Go_BusinessPartnerDim by business_partner_identifier.
- Go_ShipmentFact connects to Go_UserDim by creator_role.
- Go_ShipmentFact self-joins by parent_shipment_reference.

**Rationale**: Fact table is designed at the shipment event grain. Dimensions provide descriptive context. SCD2 is used for Carrier, Facility, and User to track changes. Audit and error tables ensure governance and traceability. Aggregated table supports reporting KPIs.

## 1.3 Assumptions
- All reference fields are string-based and not surrogate keys.
- PII is classified based on address, city, and postal code fields.
- No physical key fields (e.g., _id) are included as per requirements.

# 2. Conceptual Data Model Diagram (Tabular)
| Source Table         | Relationship Key Field         | Target Table           | Relationship Type |
|---------------------|-------------------------------|-----------------------|-------------------|
| Go_ShipmentFact     | primary_carrier_name           | Go_CarrierDim         | Many-to-One       |
| Go_ShipmentFact     | secondary_carrier_name         | Go_CarrierDim         | Many-to-One       |
| Go_ShipmentFact     | broker_carrier_name            | Go_CarrierDim         | Many-to-One       |
| Go_ShipmentFact     | designated_carrier_name        | Go_CarrierDim         | Many-to-One       |
| Go_ShipmentFact     | feasible_carrier_name          | Go_CarrierDim         | Many-to-One       |
| Go_ShipmentFact     | origin_facility_name           | Go_FacilityDim        | Many-to-One       |
| Go_ShipmentFact     | destination_facility_name      | Go_FacilityDim        | Many-to-One       |
| Go_ShipmentFact     | route_reference                | Go_RouteDim           | One-to-One        |
| Go_ShipmentFact     | bill_of_lading_number          | Go_BillingDim         | One-to-One        |
| Go_ShipmentFact     | business_partner_identifier    | Go_BusinessPartnerDim | Many-to-One       |
| Go_ShipmentFact     | creator_role                   | Go_UserDim            | Many-to-One       |
| Go_ShipmentFact     | parent_shipment_reference      | Go_ShipmentFact       | One-to-One        |

# 3. apiCost: 0.0000
