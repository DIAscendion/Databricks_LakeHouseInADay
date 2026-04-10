_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Silver Layer Logical Data Model for Shipment Reporting and Audit
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Data Model

## 1.1 Table Structures

### 1.1.1 Si_Shipment
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Shipment_Reference_Number | Unique reference for each shipment                      | string    |
| Shipment_Status           | Current state of the shipment                          | string    |
| Shipment_Type             | Type/category of shipment                              | string    |
| Leg_Type                  | Segment or leg classification                          | string    |
| Creation_Date             | Date the shipment was created                          | date      |
| Creation_Source           | Method/source of shipment creation                     | string    |
| Creator_Role              | User role responsible for creation                     | string    |
| Cancelled_Flag            | Indicates if shipment was cancelled                    | boolean   |
| Reconciled_Flag           | Indicates if shipment was reconciled                   | boolean   |
| Trailer_Number            | Trailer assigned to shipment                           | string    |

### 1.1.2 Si_Carrier
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Primary_Carrier_Name      | Main carrier assigned to shipment                      | string    |
| Secondary_Carrier_Name    | Secondary carrier assigned                             | string    |
| Broker_Carrier_Name       | Broker carrier assigned                                | string    |
| Mode_of_Transport         | Transport mode (road, rail, etc.)                      | string    |
| Designated_Carrier        | Carrier for DC-to-Store master lane/static route        | string    |
| Feasible_Carrier          | Carrier eligible for assignment                        | string    |

### 1.1.3 Si_Facility
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Origin_Facility_Name      | Name of origin facility                                | string    |
| Origin_Address            | Address of origin facility                             | string    |
| Origin_City               | City of origin facility                                | string    |
| Origin_State              | State/province of origin facility                      | string    |
| Origin_Postal_Code        | Postal code of origin facility                         | string    |
| Origin_Country            | Country of origin facility                             | string    |
| Destination_Facility_Name | Name of destination facility                           | string    |
| Destination_Address       | Address of destination facility                        | string    |
| Destination_City          | City of destination facility                           | string    |
| Destination_State         | State/province of destination facility                 | string    |
| Destination_Postal_Code   | Postal code of destination facility                    | string    |
| Destination_Country       | Country of destination facility                        | string    |

### 1.1.4 Si_Route
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Total_Route_Distance      | Total distance of shipment route                       | float     |
| Direct_Distance           | Direct distance between origin and destination         | float     |
| Out_of_Route_Distance     | Distance not on optimal route                          | float     |
| Distance_Unit_of_Measure  | Unit for distance (miles, km)                          | string    |
| Number_of_Stops           | Total stops in shipment route                          | int       |
| Equipment_Type            | Equipment used for shipment                            | string    |

### 1.1.5 Si_Billing
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Bill_to_Postal_Code       | Postal code for bill-to party                          | string    |
| Bill_to_State_Province    | State/province for bill-to party                       | string    |
| Bill_of_Lading_Number     | Reference for shipment billing                         | string    |
| Billing_Method            | Method used for billing                                | string    |
| Purchase_Order_Reference  | Purchase order associated with shipment                | string    |
| Company_Identifier        | Company associated with shipment                       | string    |
| Reconciliation_Date       | Date shipment was reconciled                           | date      |

### 1.1.6 Si_BusinessPartner
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Business_Partner_Identifier| Vendor/partner reference                               | string    |
| Parent_Shipment_Reference | Parent shipment for reference                          | string    |

### 1.1.7 Si_UserRole
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Creator_Role              | Role of user who created shipment                      | string    |

### 1.1.8 Si_ErrorLog
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Error_ID                  | Unique error reference                                  | string    |
| Table_Name                | Table where error occurred                              | string    |
| Column_Name               | Column where error occurred                             | string    |
| Error_Type                | Type of error (completeness, accuracy, format, etc.)    | string    |
| Error_Description         | Description of error                                    | string    |
| Error_Timestamp           | When error was detected                                 | datetime  |
| Source_Record_Reference   | Reference to source record                              | string    |

### 1.1.9 Si_AuditLog
| Column Name                | Description                                             | Data Type |
|---------------------------|---------------------------------------------------------|-----------|
| Audit_ID                  | Unique audit reference                                   | string    |
| Pipeline_Name             | Name of pipeline executed                               | string    |
| Execution_Timestamp       | Timestamp of pipeline execution                         | datetime  |
| Execution_Status          | Status of execution (success/failure)                   | string    |
| Record_Count              | Number of records processed                             | int       |
| Error_Count               | Number of errors encountered                            | int       |
| User                      | User who triggered pipeline                             | string    |


## 1.2 Data Type Standardization
- All string fields are standardized to 'string'.
- Dates are 'date' or 'datetime' as appropriate.
- Numeric fields are 'float' or 'int'.
- Boolean fields for flags.

## 1.3 Rationale & Assumptions
- Primary and foreign key fields, unique identifiers, and ID fields are excluded as per instructions.
- Table names prefixed with 'Si_' for Silver layer consistency.
- Error and audit tables included for data quality and pipeline traceability.
- Data types standardized for analytics and reporting.
- Structure inferred from conceptual model due to missing Bronze logical model.

# 2. Conceptual Data Model Diagram (Tabular Form)
| Source Entity   | Relationship Key Field      | Target Entity     | Relationship Type |
|-----------------|----------------------------|-------------------|-------------------|
| Si_Shipment     | Shipment_Reference_Number  | Si_Carrier        | Many-to-One       |
| Si_Shipment     | Origin_Facility_Name       | Si_Facility       | Many-to-One       |
| Si_Shipment     | Destination_Facility_Name  | Si_Facility       | Many-to-One       |
| Si_Shipment     | Bill_of_Lading_Number      | Si_Billing        | Many-to-One       |
| Si_Shipment     | Business_Partner_Identifier| Si_BusinessPartner| Many-to-One       |
| Si_Shipment     | Creator_Role               | Si_UserRole       | Many-to-One       |
| Si_Shipment     | Total_Route_Distance       | Si_Route          | Many-to-One       |

# 3. apiCost
- apiCost: 0.0

# 4. OutputURL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Logical

# 5. pipelineID
12357