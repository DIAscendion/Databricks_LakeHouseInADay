_____________________________________________
## *Author*: Ascendion AVA+
## *Created on*:   
## *Description*:   Gold Layer Logical Data Model for Store360 Inventory Report
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# 1. Gold Layer Logical Model

## 1.1 Table Classification and Design

### 1.1.1 Fact Tables

1. **Go_Inventory**
   - Description: Stores inventory levels and health metrics for products in each store.
   - Table Type: Fact
   - Columns:
     - Store Name: Name of the retail location (string)
     - Product Name: Name of the product (string)
     - On-Hand Units: Units currently available in store (integer)
     - Stockout Rate %: Percentage of products out of stock (float)
     - Available Inventory %: Percentage of inventory available (float)
     - Inventory Health Score: Overall score measuring inventory health (float)
     - Inventory Variance Units: Units with inventory variance (integer)
     - Inventory Variance %: Percentage variance in inventory (float)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

2. **Go_FulfillmentOrder**
   - Description: Tracks fulfillment order metrics for customer activities.
   - Table Type: Fact
   - Columns:
     - Store Name: Name of the retail location (string)
     - Pick UPH: Units picked per hour (integer)
     - Available-to-Sell Units: Units available for fulfillment (integer)
     - Fill Rate %: Percentage of orders fulfilled (float)
     - Inventory Readiness %: Readiness of inventory for fulfillment (float)
     - Fulfillment Success Rate %: Success rate of fulfillment activities (float)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

3. **Go_SearchEvent**
   - Description: Captures product search activities and outcomes.
   - Table Type: Fact
   - Columns:
     - Store Name: Name of the retail location (string)
     - Product Name: Name of the product (string)
     - Zero-Result Search %: Percentage of searches with zero results (float)
     - Product Discovery by Scan %: Percentage of products discovered by scan (float)
     - Product Discovery by Catalog Search %: Percentage of products discovered by catalog search (float)
     - Search Success Rate %: Percentage of successful searches (float)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

4. **Go_AthleteInteraction**
   - Description: Tracks athlete interactions with products in stores.
   - Table Type: Fact
   - Columns:
     - Store Name: Name of the retail location (string)
     - Product Name: Name of the product (string)
     - Walk-In Conversion %: Percentage of walk-ins converted to purchases (float)
     - Average Locate Time: Average time to locate a product (float)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

### 1.1.2 Dimension Tables

1. **Go_Store**
   - Description: Describes retail store locations.
   - Table Type: Dimension
   - SCD Type: 2 (historical tracking of store attributes)
   - Columns:
     - Store Name: Name of the retail location (string)
     - Store Code: Business code for the store (string)
     - Region Name: Associated region (string)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

2. **Go_Region**
   - Description: Describes geographic regions.
   - Table Type: Dimension
   - SCD Type: 1 (no historical tracking required)
   - Columns:
     - Region Name: Name of the region (string)
     - Region Manager: Person responsible for the region (string)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: Region Manager (PII: Name)

3. **Go_Product**
   - Description: Describes products available in stores.
   - Table Type: Dimension
   - SCD Type: 2 (historical tracking of product attributes)
   - Columns:
     - Product Name: Name of the product (string)
     - Product Category: Category classification (string)
     - RFID Tag: RFID identifier for the product (string)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

4. **Go_Category**
   - Description: Describes product categories.
   - Table Type: Dimension
   - SCD Type: 1 (no historical tracking required)
   - Columns:
     - Category Name: Name of the category (string)
     - Category Description: Description of the category (string)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

5. **Go_Date**
   - Description: Reporting and analysis dates.
   - Table Type: Dimension
   - SCD Type: 1
   - Columns:
     - Report Date: Date for reporting (date)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

### 1.1.3 Code Tables

1. **Go_Code_ProductCategory**
   - Description: Lookup for product category codes.
   - Table Type: Code Table
   - Columns:
     - Product Category: Category classification (string)
     - Category Code: Code for category (string)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

### 1.1.4 Audit and Error Tables

1. **Go_ProcessAudit**
   - Description: Stores process audit details from pipeline execution.
   - Table Type: Audit
   - Columns:
     - Process Name: Name of the pipeline process (string)
     - Execution Timestamp: Date and time of execution (datetime)
     - Status: Execution status (string)
     - Records Processed: Number of records processed (integer)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

2. **Go_ErrorData**
   - Description: Stores error data from data validation process.
   - Table Type: Error Data
   - Columns:
     - Error Type: Type of error (string)
     - Error Description: Description of error (string)
     - Entity Name: Name of entity where error occurred (string)
     - Error Timestamp: Date and time of error (datetime)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

### 1.1.5 Aggregated Tables

1. **Go_AggregatedInventoryHealth**
   - Description: Aggregated inventory health metrics by store and category.
   - Table Type: Aggregated
   - Columns:
     - Store Name: Name of the retail location (string)
     - Category Name: Name of the category (string)
     - Inventory Health Score: Overall score measuring inventory health (float)
     - Inventory Accuracy %: Measures the accuracy of inventory records (float)
     - Stockout Rate %: Percentage of products out of stock (float)
     - load_date: Date record loaded (date)
     - update_date: Date record updated (date)
     - source_system: Source system name (string)
   - PII Classification: None

## 1.2 Rationale and Assumptions

- Fact tables are designed to capture transactional and event-based metrics for reporting and analytics.
- Dimension tables provide descriptive context and support SCD types for historical tracking where required.
- Code tables ensure consistent lookup values for reporting.
- Audit and error tables support data governance, pipeline monitoring, and validation.
- Aggregated tables are created to optimize reporting on inventory health and KPIs.
- Naming convention 'Go_' ensures clear identification of Gold layer tables.
- PII fields are classified based on GDPR standards; only Region Manager is considered PII.
- No primary key, foreign key, unique identifiers, or ID fields are included as per instructions.

# 2. Conceptual Data Model Diagram (Tabular Form)

| Source Entity      | Relationship Key Field     | Target Entity      | Relationship Type |
|--------------------|---------------------------|--------------------|-------------------|
| Go_Store           | Region Name               | Go_Region          | Many-to-One       |
| Go_Store           | Store Name                | Go_Inventory       | One-to-Many       |
| Go_Store           | Store Name                | Go_InventorySnapshot| One-to-Many      |
| Go_Store           | Store Name                | Go_RFIDEvent       | One-to-Many       |
| Go_Store           | Store Name                | Go_FulfillmentOrder| One-to-Many       |
| Go_Store           | Store Name                | Go_SearchEvent     | One-to-Many       |
| Go_Store           | Store Name                | Go_AthleteInteraction| One-to-Many     |
| Go_Product         | Product Category          | Go_Category        | Many-to-One       |
| Go_Product         | RFID Tag                  | Go_RFIDEvent       | One-to-Many       |
| Go_Inventory       | Product Name              | Go_Product         | Many-to-One       |
| Go_InventorySnapshot| Snapshot Date            | Go_Date            | Many-to-One       |
| Go_FulfillmentOrder| Available-to-Sell Units   | Go_Inventory       | Many-to-One       |
| Go_SearchEvent     | Product Name              | Go_Product         | Many-to-One       |
| Go_AthleteInteraction| Product Name            | Go_Product         | Many-to-One       |

# 3. apiCost: 0.0234

# 4. OutputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Model_Logical

# 5. pipelineID: 12368
