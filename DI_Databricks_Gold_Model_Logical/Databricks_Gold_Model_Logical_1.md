_____________________________________________
## *Author*: Ascendion AVA+
## *Created on*:   
## *Description*:   Gold Layer Logical Data Model for Shipment Reporting and Analytics
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# 1. Gold Layer Logical Model

## 1.1 Table Classification and Design

### 1.1.1 Fact Tables

1. **Go_ShipmentFact** (Fact)
   - Description: Contains transactional shipment data for reporting and analytics.
   - Columns:
     - Shipment Reference Number: Unique reference for each shipment (string)
     - Shipment Status: Current state of the shipment (string)
     - Shipment Type: Type/category of shipment (string)
     - Leg Type: Segment or leg classification (string)
     - Creation Date: Date the shipment was created (date)
     - Creation Source: Method/source of shipment creation (string)
     - Cancelled Flag: Indicates if shipment was cancelled (boolean)
     - Reconciled Flag: Indicates if shipment was reconciled (boolean)
     - Trailer Number: Trailer assigned to shipment (string)
     - Bill of Lading Number: Reference for shipment billing (string)
     - Company Identifier: Company associated with shipment (string)
     - Purchase Order Reference: Purchase order associated with shipment (string)
     - Total Route Distance: Total distance of shipment route (float)
     - Direct Distance: Direct distance between origin and destination (float)
     - Out-of-Route Distance: Distance not on optimal route (float)
     - Distance Unit of Measure: Unit for distance (string)
     - Number of Stops: Total stops in shipment route (int)
     - Equipment Type: Equipment used for shipment (string)
     - Reconciliation Date: Date shipment was reconciled (date)
     - Parent Shipment Reference: Parent shipment for reference (string)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - PII Classification: None

### 1.1.2 Dimension Tables

2. **Go_CarrierDim** (Dimension, SCD Type 2)
   - Description: Reference data for carriers, including historical changes.
   - Columns:
     - Primary Carrier Name: Main carrier assigned to shipment (string)
     - Secondary Carrier Name: Secondary carrier assigned (string)
     - Broker Carrier Name: Broker carrier assigned (string)
     - Mode of Transport: Transport mode (string)
     - Designated Carrier: Carrier for DC-to-Store master lane/static route (string)
     - Feasible Carrier: Carrier eligible for assignment (string)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - SCD Type: 2 (Tracks historical changes)
   - PII Classification: None

3. **Go_FacilityDim** (Dimension, SCD Type 2)
   - Description: Reference data for facilities (origin/destination), including historical changes.
   - Columns:
     - Facility Name: Name of facility (string)
     - Address: Address of facility (string)
     - City: City of facility (string)
     - State: State/province of facility (string)
     - Postal Code: Postal code of facility (string)
     - Country: Country of facility (string)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - SCD Type: 2 (Tracks historical changes)
   - PII Classification: None

4. **Go_BusinessPartnerDim** (Dimension, SCD Type 1)
   - Description: Reference data for business partners/vendors.
   - Columns:
     - Business Partner Identifier: Vendor/partner reference (string)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - SCD Type: 1 (No history tracking)
   - PII Classification: None

5. **Go_UserRoleDim** (Dimension, SCD Type 1)
   - Description: Reference data for user roles.
   - Columns:
     - Creator Role: Role of user who created shipment (string)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - SCD Type: 1 (No history tracking)
   - PII Classification: None

### 1.1.3 Aggregated Tables

6. **Go_ShipmentAgg** (Aggregated)
   - Description: Pre-aggregated shipment KPIs for reporting.
   - Columns:
     - Shipment Status: Status of shipment (string)
     - Carrier Name: Carrier (string)
     - Origin Facility Name: Origin facility (string)
     - Destination Facility Name: Destination facility (string)
     - Total Shipment Count: Number of shipments (int)
     - Cancelled Shipment %: Cancelled Shipments / Total Shipments × 100 (float)
     - Reconciled Shipment %: Reconciled Shipments / Total Shipments × 100 (float)
     - Shipments per Carrier: Breakdown by assigned carrier (int)
     - Shipments by Origin and Destination Facility: Count per facility (int)
     - Carrier Assignment Rate %: Assigned vs feasible carrier ratio (float)
     - Broker Carrier Usage %: Shipments with broker carrier / Total Shipments × 100 (float)
     - On-time Pickup %: Scheduled vs actual pickup (float)
     - Out-of-Route Distance %: Out-of-route distance / Total distance × 100 (float)
     - Average Stops per Shipment: Total stops / Total shipments (float)
     - Average Route Distance: Average route distance (float)
     - Route Efficiency Index: Direct distance / Total distance (float)
     - Unreconciled Shipment Count with Aging: Count and aging of unreconciled shipments (int)
     - Creation Volume Trend: Shipments created per day/week (int)
     - Source Mix %: Count by source / Total count × 100 (float)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - PII Classification: None

### 1.1.4 Audit and Error Data Tables

7. **Go_ProcessAudit** (Audit)
   - Description: Stores process audit details from pipeline execution.
   - Columns:
     - Process Name: Name of the ETL/data pipeline process (string)
     - Execution Start Time: Start time of execution (datetime)
     - Execution End Time: End time of execution (datetime)
     - Status: Status of execution (string)
     - Records Processed: Number of records processed (int)
     - Records Inserted: Number of records inserted (int)
     - Records Updated: Number of records updated (int)
     - Records Deleted: Number of records deleted (int)
     - Error Count: Number of errors encountered (int)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - PII Classification: None

8. **Go_DataValidationError** (Error Data)
   - Description: Stores error data from data validation process.
   - Columns:
     - Validation Rule Name: Name of the validation rule (string)
     - Failed Record Reference: Reference to the failed record (string)
     - Error Description: Description of the error (string)
     - Error Timestamp: When the error occurred (datetime)
     - Source Table: Table where error occurred (string)
     - load_date: Date record was loaded (datetime)
     - update_date: Date record was last updated (datetime)
     - source_system: Source system of the record (string)
   - PII Classification: None


## 1.2 Table Relationships

- Go_ShipmentFact is connected to Go_CarrierDim by Primary Carrier Name
- Go_ShipmentFact is connected to Go_FacilityDim by Origin Facility Name and Destination Facility Name
- Go_ShipmentFact is connected to Go_BusinessPartnerDim by Business Partner Identifier
- Go_ShipmentFact is connected to Go_UserRoleDim by Creator Role
- Go_ShipmentFact is connected to Go_ShipmentAgg by Shipment Reference Number (for drill-down)
- Go_ShipmentFact is referenced by Go_ProcessAudit and Go_DataValidationError for audit and error tracking


# 2. Conceptual Data Model Diagram (Tabular Form)

| Source Table         | Relationship Key Field         | Target Table           | Relationship Type |
|--------------------- |------------------------------ |----------------------- |-------------------|
| Go_ShipmentFact      | Primary Carrier Name           | Go_CarrierDim          | Many-to-One       |
| Go_ShipmentFact      | Origin Facility Name           | Go_FacilityDim         | Many-to-One       |
| Go_ShipmentFact      | Destination Facility Name      | Go_FacilityDim         | Many-to-One       |
| Go_ShipmentFact      | Business Partner Identifier    | Go_BusinessPartnerDim  | Many-to-One       |
| Go_ShipmentFact      | Creator Role                   | Go_UserRoleDim         | Many-to-One       |
| Go_ShipmentFact      | Shipment Reference Number      | Go_ShipmentAgg         | One-to-One        |
| Go_ShipmentFact      | Shipment Reference Number      | Go_ProcessAudit        | One-to-Many       |
| Go_ShipmentFact      | Shipment Reference Number      | Go_DataValidationError | One-to-Many       |


# 3. apiCost

- apiCost: 0.014


# 4. Rationale and Assumptions

1. Table classification is based on the conceptual model and business requirements.
2. SCD Type 2 is used for Carrier and Facility dimensions to track historical changes, as carrier assignments and facility details may change over time.
3. SCD Type 1 is used for Business Partner and User Role dimensions, as historical tracking is not required.
4. Aggregated table is designed to support KPI reporting as per requirements.
5. Audit and error tables are included for pipeline execution and data quality monitoring.
6. PII classification is based on the provided attributes; none are considered PII under standard frameworks.
7. No physical key fields (e.g., IDs) are included as per instructions.
8. Relationships are documented using business key fields.
9. Silver layer logical model was not available; design is inferred from conceptual and constraints files.
