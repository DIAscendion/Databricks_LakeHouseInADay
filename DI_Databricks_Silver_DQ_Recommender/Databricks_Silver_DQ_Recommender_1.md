_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Data quality recommendations for Store360 Inventory Report Silver Layer based on conceptual, business, and physical model constraints
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Recommender for Store360 Inventory Report

This document provides a comprehensive set of data quality recommendations for the Silver layer of the Store360 Inventory Report pipeline. The checks are derived from the conceptual model, business rules, and physical DDL definitions. They are intended to ensure data completeness, accuracy, consistency, and referential integrity for downstream analytics and reporting.

---

## Recommended Data Quality Checks

| # | Check Name | Description | Rationale | SQL Example |
|---|------------|-------------|-----------|-------------|
| 1 | Null Check: Mandatory Fields | Ensure required fields (Store Name, Product Name, Inventory Accuracy %, RFID Cycle Count Coverage %, Fill Rate %) are not null | Mandatory fields are required for accurate reporting and analytics | SELECT * FROM silver.inventory_snapshot WHERE store_name IS NULL OR product_name IS NULL OR inventory_accuracy_pct IS NULL; |
| 2 | Range Check: Percentage Fields | Validate that all percentage KPIs (e.g., Inventory Accuracy %, Stockout Rate %, Fill Rate %, etc.) are between 0 and 100 | Business rules require all percentage KPIs to be numeric and within 0-100 | SELECT * FROM silver.inventory_snapshot WHERE inventory_accuracy_pct < 0 OR inventory_accuracy_pct > 100; |
| 3 | Data Type Check: Units Fields | Ensure On-Hand Units and Available-to-Sell Units are integers (whole numbers) | Units must be reported as whole numbers for inventory accuracy | SELECT * FROM silver.inventory_balance WHERE on_hand_qty != CAST(on_hand_qty AS INT); |
| 4 | Date Format Validation | Validate that all date fields are in YYYY-MM-DD format and are valid dates | Ensures consistency and prevents downstream errors | SELECT * FROM silver.inventory_snapshot WHERE TRY_CAST(snapshot_date AS DATE) IS NULL; |
| 5 | Uniqueness Check: Inventory Snapshot | Ensure Store Name + Date is unique for each inventory snapshot | Prevents duplicate reporting for the same store and date | SELECT store_name, snapshot_date, COUNT(*) FROM silver.inventory_snapshot GROUP BY store_name, snapshot_date HAVING COUNT(*) > 1; |
| 6 | Uniqueness Check: Inventory Record | Ensure Product Name + Store Name is unique for each inventory record | Prevents duplicate inventory records for the same product and store | SELECT product_name, store_name, COUNT(*) FROM silver.inventory GROUP BY product_name, store_name HAVING COUNT(*) > 1; |
| 7 | Referential Integrity: Inventory | Inventory records must reference valid Store and Product entities | Prevents orphan records and ensures data integrity | SELECT * FROM silver.inventory i LEFT JOIN silver.store s ON i.store_id = s.store_id WHERE s.store_id IS NULL; |
| 8 | Referential Integrity: InventorySnapshot | InventorySnapshot must reference valid Date and Store entities | Ensures all snapshots are linked to valid stores and dates | SELECT * FROM silver.inventory_snapshot s LEFT JOIN silver.store st ON s.store_id = st.store_id WHERE st.store_id IS NULL; |
| 9 | Referential Integrity: RFIDEvent | RFIDEvent must reference valid Product and Store entities | Ensures all RFID events are linked to valid products and stores | SELECT * FROM silver.rfid_event r LEFT JOIN silver.product p ON r.product_id = p.product_id WHERE p.product_id IS NULL; |
| 10 | Referential Integrity: FulfillmentOrder | FulfillmentOrder must reference valid Store and Inventory entities | Ensures fulfillment orders are linked to valid stores and inventory | SELECT * FROM silver.fulfillment_order f LEFT JOIN silver.store s ON f.store_id = s.store_id WHERE s.store_id IS NULL; |
| 11 | Consistency Check: Store Codes/Region Names | Store codes and region names must be consistent across all entities | Prevents mismatches and reporting errors | SELECT DISTINCT store_code FROM silver.store EXCEPT SELECT DISTINCT store_code FROM silver.inventory; |
| 12 | Consistency Check: Product Categories | Product categories must be uniformly applied across reports | Ensures consistent classification for analytics | SELECT DISTINCT product_category FROM silver.product EXCEPT SELECT DISTINCT product_category FROM silver.inventory; |
| 13 | Completeness: Daily/Weekly Inventory | All stores must report inventory data daily and weekly | Ensures full coverage for reporting periods | SELECT store_id, COUNT(DISTINCT snapshot_date) FROM silver.inventory_snapshot GROUP BY store_id HAVING COUNT(DISTINCT snapshot_date) < expected_days; |
| 14 | Completeness: RFID Cycle Count | RFID cycle count events must be captured for all stores | Ensures RFID tracking completeness | SELECT store_id FROM silver.store WHERE store_id NOT IN (SELECT DISTINCT store_id FROM silver.rfid_event); |
| 15 | Completeness: Fulfillment Order Data | Fulfillment order data must be available for all customer fulfillment activities | Ensures fulfillment metrics are complete | SELECT * FROM silver.fulfillment_order WHERE order_id IS NULL OR store_id IS NULL; |
| 16 | Accuracy: Inventory Accuracy % | Inventory Accuracy % must reflect actual physical inventory counts | Validates that reported accuracy matches physical counts | -- Compare inventory_accuracy_pct with physical count audit logs |
| 17 | Accuracy: Stockout Rate % | Stockout Rate % must be calculated based on real-time inventory status | Ensures stockout rates are not stale or misreported | -- Compare stockout_rate_pct with real-time inventory balance |
| 18 | Accuracy: RFID Cycle Count Coverage % | RFID Cycle Count Coverage % must be based on completed cycle counts | Ensures reported coverage is based on actual events | -- Compare rfid_cycle_count_coverage_pct with completed cycle counts |
| 19 | Accuracy: Fill Rate % | Fill Rate % must be based on actual fulfillment outcomes | Ensures fill rate is not over/under-reported | -- Compare fill_rate_pct with fulfillment outcomes |
| 20 | Consistency: Inventory Data Across Snapshots | Inventory data must be consistent across daily and weekly snapshots | Prevents reporting discrepancies | -- Compare inventory values across daily and weekly snapshots |

---

## Additional Recommendations Based on Business Rules

- All percentage fields should be FLOAT or DECIMAL(5,2) and validated for precision.
- All date fields should be DATE type and validated for logical ranges (e.g., not in the future for historical data).
- All foreign key relationships should be validated at load time, even if not enforced at the Bronze layer.
- Implement audit logging for all DQ failures for traceability.
- For derived KPIs (e.g., Zero-Result Search %, Walk-In Conversion %), validate calculation logic against business rules.

---

## API Cost
apiCost: 0.000200 USD

## Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Recommender

## Pipeline ID
12360
