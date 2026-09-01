____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Model data constraints and business rules for Store360 Inventory Report
## *Version*: 1
## *Updated on*: 
____________________________________________

## 1. Data Expectations

### 1.1 Data Completeness
1. All stores must report inventory data daily and weekly.
2. Each product in every store must have an associated inventory record.
3. RFID cycle count events must be captured for all stores.
4. Fulfillment order data must be available for all customer fulfillment activities.

### 1.2 Data Accuracy
1. Inventory Accuracy % must reflect actual physical inventory counts.
2. Stockout Rate % must be calculated based on real-time inventory status.
3. RFID Cycle Count Coverage % must be based on completed cycle counts.
4. Fill Rate % must be based on actual fulfillment outcomes.

### 1.3 Data Format
1. All percentage KPIs must be reported as numeric values between 0 and 100.
2. On-Hand Units and Available-to-Sell Units must be reported as whole numbers.
3. Dates must be in standard YYYY-MM-DD format.

### 1.4 Data Consistency
1. Inventory data must be consistent across daily and weekly snapshots.
2. Product categories must be uniformly applied across reports.
3. Store codes and region names must be consistent in all entities.

## 2. Constraints

### 2.1 Mandatory Fields
1. Store Name: Required for all store-related records.
2. Product Name: Required for all inventory and search events.
3. Inventory Accuracy %: Required for all inventory snapshots.
4. RFID Cycle Count Coverage %: Required for all RFID events.
5. Fill Rate %: Required for all fulfillment orders.

### 2.2 Uniqueness Requirements
1. Store Name + Date: Must be unique for each inventory snapshot.
2. Product Name + Store Name: Must be unique for each inventory record.

### 2.3 Data Type Limitations
1. Percentage fields: Must be numeric and within 0-100 range.
2. Units fields: Must be integer values.
3. Date fields: Must be valid dates in YYYY-MM-DD format.

### 2.4 Dependencies
1. Inventory records depend on valid Product and Store entities.
2. RFID events depend on associated Product and Store records.
3. Fulfillment orders depend on available inventory.

### 2.5 Referential Integrity
1. Inventory records must reference valid Store and Product entities.
2. InventorySnapshot must reference valid Date and Store entities.
3. RFIDEvent must reference valid Product and Store entities.
4. FulfillmentOrder must reference valid Store and Inventory entities.

## 3. Business Rules

### 3.1 Data Processing Rules
1. Inventory health score must be calculated daily and weekly for each store.
2. RFID cycle count completion must be tracked for each store.

### 3.2 Reporting Logic Rules
1. Zero-Result Search % must be calculated as the ratio of searches with no results to total searches.
2. Walk-In Conversion % must be calculated as the ratio of walk-ins converted to purchases.
3. Fill Rate % must be calculated as the ratio of fulfilled orders to total orders.

### 3.3 Transformation Guidelines
1. Inventory snapshots must aggregate daily and weekly data for reporting.
2. Product discovery metrics must be derived from search and scan events.
