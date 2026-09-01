_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Conceptual data model for Store360 Inventory Report
## *Version*: 1
## *Updated on*: 
_____________________________________________

### 1. Domain Overview
The Store360 Inventory Perspective covers inventory health, product findability, RFID effectiveness, replenishment efficiency, and fulfillment performance across a retail store network. The domain focuses on monitoring and optimizing inventory accuracy, stock availability, search success, and fulfillment readiness.

### 2. List of Entity Names with Descriptions
1. **Store**: Represents individual retail locations in the store network.
2. **Region**: Geographic grouping of stores.
3. **Product**: Items available for sale in stores.
4. **Category**: Classification of products (e.g., apparel, footwear).
5. **Inventory**: Current stock levels and inventory details for products in stores.
6. **InventorySnapshot**: Periodic capture of inventory status for analysis.
7. **RFIDEvent**: Events related to RFID cycle counts and inventory tracking.
8. **FulfillmentOrder**: Orders related to customer fulfillment activities (BOPIS, SDD).
9. **SearchEvent**: Events capturing product search activities by athletes.
10. **AthleteInteraction**: Interactions between athletes and products (search, scan, walk-in).
11. **Date**: Represents dates for reporting and analysis.

### 3. List of Attributes for Each Entity
#### Store
1. **Store Name**: Name of the retail location.
2. **Store Code**: Business code for the store.
3. **Region Name**: Associated region.

#### Region
1. **Region Name**: Name of the region.
2. **Region Manager**: Person responsible for the region.

#### Product
1. **Product Name**: Name of the product.
2. **Product Category**: Category classification.
3. **RFID Tag**: RFID identifier for the product.

#### Category
1. **Category Name**: Name of the category.
2. **Category Description**: Description of the category.

#### Inventory
1. **On-Hand Units**: Units currently available in store.
2. **Stockout Rate %**: Percentage of products out of stock.
3. **Available Inventory %**: Percentage of inventory available.

#### InventorySnapshot
1. **Snapshot Date**: Date of inventory capture.
2. **Inventory Accuracy %**: Accuracy of inventory at snapshot.

#### RFIDEvent
1. **Cycle Count Completion %**: Percentage of completed RFID cycle counts.
2. **RFID Cycle Count Coverage %**: Coverage of RFID cycle counts.

#### FulfillmentOrder
1. **Pick UPH**: Units picked per hour.
2. **Available-to-Sell Units**: Units available for fulfillment.
3. **Fill Rate %**: Percentage of orders fulfilled.

#### SearchEvent
1. **Zero-Result Search %**: Percentage of searches with zero results.
2. **Product Discovery by Scan %**: Percentage of products discovered by scan.
3. **Product Discovery by Catalog Search %**: Percentage of products discovered by catalog search.
4. **Search Success Rate %**: Percentage of successful searches.

#### AthleteInteraction
1. **Walk-In Conversion %**: Percentage of walk-ins converted to purchases.
2. **Average Locate Time**: Average time to locate a product.

#### Date
1. **Report Date**: Date for reporting.

### 4. KPI List
1. **Inventory Accuracy %**: Measures the accuracy of inventory records.
2. **On-Hand Units**: Number of units available in store.
3. **Stockout Rate %**: Percentage of products out of stock.
4. **Zero-Result Search %**: Percentage of searches yielding no results.
5. **Average Locate Time**: Average time taken to locate a product.
6. **Walk-In Conversion %**: Percentage of walk-ins resulting in purchases.
7. **RFID Cycle Count Coverage %**: Coverage of RFID cycle counts in store.
8. **Available Inventory %**: Percentage of inventory available for sale.
9. **Nearby Store Stock Display %**: Percentage of products displayed as available in nearby stores.
10. **Product Discovery by Scan %**: Percentage of products discovered via scan.
11. **Product Discovery by Catalog Search %**: Percentage of products discovered via catalog search.
12. **Search Success Rate %**: Percentage of successful product searches.
13. **Cycle Count Completion %**: Completion rate of RFID cycle counts.
14. **Inventory Variance Units**: Units with inventory variance.
15. **Inventory Variance %**: Percentage variance in inventory.
16. **Pick UPH**: Units picked per hour for fulfillment.
17. **Available-to-Sell Units**: Units available for customer fulfillment.
18. **Inventory Readiness %**: Readiness of inventory for fulfillment.
19. **Fill Rate %**: Percentage of orders fulfilled.
20. **Fulfillment Success Rate %**: Success rate of fulfillment activities.
21. **Category Availability %**: Availability of products by category.
22. **Category Stockout Rate %**: Stockout rate by category.
23. **Inventory Health Score**: Overall score measuring inventory health.
24. **RFID Accuracy %**: RFID-based inventory accuracy.

### 5. Conceptual Data Model Diagram
| Source Entity      | Relationship Key Field     | Target Entity      | Relationship Type |
|--------------------|---------------------------|--------------------|-------------------|
| Store              | Region Name               | Region             | Many-to-One       |
| Store              | Store Code                | Inventory          | One-to-Many       |
| Store              | Store Code                | InventorySnapshot  | One-to-Many       |
| Store              | Store Code                | RFIDEvent          | One-to-Many       |
| Store              | Store Code                | FulfillmentOrder   | One-to-Many       |
| Store              | Store Code                | SearchEvent        | One-to-Many       |
| Store              | Store Code                | AthleteInteraction | One-to-Many       |
| Product            | Product Category          | Category           | Many-to-One       |
| Product            | RFID Tag                  | RFIDEvent          | One-to-Many       |
| Inventory          | Product Name              | Product            | Many-to-One       |
| InventorySnapshot  | Snapshot Date             | Date               | Many-to-One       |
| FulfillmentOrder   | Available-to-Sell Units   | Inventory          | Many-to-One       |
| SearchEvent        | Product Name              | Product            | Many-to-One       |
| AthleteInteraction | Product Name              | Product            | Many-to-One       |

### 6. Common Data Elements in Report Requirements
1. **Inventory Accuracy %**
2. **Stockout Rate %**
3. **Walk-In Conversion %**
4. **Average Locate Time**
5. **RFID Cycle Count Coverage %**
6. **Zero-Result Search %**
7. **Available Inventory %**
8. **Product Discovery by Scan %**
9. **Product Discovery by Catalog Search %**
10. **Search Success Rate %**
