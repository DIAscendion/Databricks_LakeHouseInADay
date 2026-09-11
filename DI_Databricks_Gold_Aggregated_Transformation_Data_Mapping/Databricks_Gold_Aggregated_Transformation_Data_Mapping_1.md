_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Data mapping for Gold Layer Aggregated Tables with custom business rules and transformations for shipment analytics
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Overview
This document details the data mapping and transformation logic for Aggregated Tables in the Gold Layer of the Databricks Lakehouse (Shipment Domain). It incorporates aggregation methods, grouping, validation, cleansing, and custom business rules, including recent change requests. The mapping ensures consistency, traceability, and performance for analytical/reporting use cases.

# Data Mapping for Aggregated Tables

| Target Layer | Target Table      | Target Field                  | Source Layer | Source Table           | Source Field                  | Aggregation Rule         | Validation Rule                                                                 | Transformation Rule                                                                                                   |
|--------------|------------------|-------------------------------|--------------|------------------------|-------------------------------|--------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Gold         | go_shipment_agg  | total_shipment_count          | Silver       | si_shipment_process    | shipment_number               | COUNT                    | shipment_number NOT NULL, unique per group                                       | Group by shipment_status, shipment_type, mode_of_transport, carrier_name, origin_facility_name, destination_facility_name |
| Gold         | go_shipment_agg  | cancelled_shipment_percent    | Silver       | si_shipment_process    | shipment_status               | SUM/COUNT                | shipment_status in ('CANCELLED', ...)                                            | 100.0 * SUM(CASE WHEN shipment_status = 'CANCELLED' THEN 1 ELSE 0 END) / COUNT(*), round(2)                          |
| Gold         | go_shipment_agg  | reconciled_shipment_percent   | Silver       | si_shipment_process    | shipment_status               | SUM/COUNT                | shipment_status in ('RECONCILED', ...)                                           | 100.0 * SUM(CASE WHEN shipment_status = 'RECONCILED' THEN 1 ELSE 0 END) / COUNT(*), round(2)                         |
| Gold         | go_shipment_agg  | broker_carrier_usage_percent  | Silver       | si_shipment_process    | broker_carrier_name           | SUM/COUNT                | broker_carrier_name NOT NULL/empty                                               | 100.0 * SUM(CASE WHEN broker_carrier_name IS NOT NULL AND broker_carrier_name != '' THEN 1 ELSE 0 END) / COUNT(*), round(2) |
| Gold         | go_shipment_agg  | on_time_pickup_percent        | Silver       | si_shipment_process    | on_time_indicator             | SUM/COUNT                | on_time_indicator in ('Y', 'N')                                                  | 100.0 * SUM(CASE WHEN on_time_indicator = 'Y' THEN 1 ELSE 0 END) / COUNT(*), round(2)                                 |
| Gold         | go_shipment_agg  | out_of_route_distance_percent | Silver       | si_shipment_process    | out_of_route_distance, total_route_distance | SUM, division, percent | total_route_distance > 0                                                          | 100.0 * SUM(out_of_route_distance) / NULLIF(SUM(total_route_distance), 0), round(2)                                   |
| Gold         | go_shipment_agg  | average_stops_per_shipment    | Silver       | si_shipment_process    | number_of_stops                | AVG                      | number_of_stops >= 0                                                              | AVG(number_of_stops), round(2)                                                                                       |
| Gold         | go_shipment_agg  | route_efficiency_index        | Silver       | si_shipment_process    | direct_distance, total_route_distance | AVG, ratio             | total_route_distance > 0                                                          | AVG(CASE WHEN total_route_distance > 0 THEN direct_distance / total_route_distance ELSE NULL END), round(3)           |
| Gold         | go_shipment_agg  | unreconciled_shipment_count_with_aging | Silver | si_shipment_process | reconciled_flag, creation_date, shipment_reference_number | SUM, DATEDIFF, STRING_AGG | reconciled_flag = FALSE, creation_date NOT NULL | SUM(CASE WHEN reconciled_flag = FALSE THEN 1 ELSE 0 END), STRING_AGG(CONCAT(shipment_reference_number, ':', DATEDIFF(current_date(), creation_date)), ',') |
| Gold         | go_shipment_agg  | creation_volume_trend         | Silver       | si_shipment_process    | creation_date                  | DATE_TRUNC, COUNT, STRING_AGG | creation_date NOT NULL                                                            | STRING_AGG(CONCAT(DATE_TRUNC('day', creation_date), ':', COUNT(*)), ',')                                             |
| Gold         | go_shipment_agg  | api_source_percent            | Silver       | si_shipment_process    | creation_source                | SUM/COUNT                | creation_source = 'API'                                                           | 100.0 * SUM(CASE WHEN creation_source = 'API' THEN 1 ELSE 0 END) / COUNT(*), round(2)                                |
| Gold         | go_shipment_agg  | manual_source_percent         | Silver       | si_shipment_process    | creation_source                | SUM/COUNT                | creation_source = 'MANUAL'                                                        | 100.0 * SUM(CASE WHEN creation_source = 'MANUAL' THEN 1 ELSE 0 END) / COUNT(*), round(2)                             |
| Gold         | go_shipment_agg  | integration_source_percent    | Silver       | si_shipment_process    | creation_source                | SUM/COUNT                | creation_source = 'INTEGRATION'                                                   | 100.0 * SUM(CASE WHEN creation_source = 'INTEGRATION' THEN 1 ELSE 0 END) / COUNT(*), round(2)                        |
| Gold         | go_shipment_agg  | Customer_Lifetime_Value       | Silver       | si_shipment_process    | amount, customer_id            | SUM                      | customer_id NOT NULL                                                               | SUM(amount) grouped by customer_id, exclude NULLs, apply outlier removal (z-score > 3)                                |
| Gold         | go_shipment_agg  | Region_Code                   | Silver       | si_shipment_process    | destination                    | LOOKUP                   | destination NOT NULL                                                               | Map destination to Region_Code using Region_Mapping_2023 reference                                                    |
| Gold         | go_shipment_agg  | Sales_Amount                  | Silver       | si_shipment_process    | amount, currency_code          | SUM (with conversion)    | amount >= 0, currency_code valid                                                   | SUM(amount * currency_conversion_factor_to_USD), round(2)                                                             |
| Gold         | go_shipment_agg  | Total_Orders                  | Silver       | si_shipment_process    | order_count                    | SUM                      | order_count >= 0                                                                   | Rename from Order_Count, SUM(order_count)                                                                              |
| Gold         | go_shipment_agg  | Average_Order_Value           | Silver       | si_shipment_process    | amount, order_flag             | AVG (exclude returns)    | amount >= 0, order_flag != 'RETURN'                                                | AVG(amount) WHERE order_flag != 'RETURN', round(2)                                                                    |
| Gold         | go_shipment_agg  | Customer_Segments             | Silver       | si_shipment_process    | customer_segment, amount       | SEGMENTATION             | customer_segment NOT NULL                                                          | Update segmentation logic to add 'High Value' tier: IF SUM(amount) > threshold THEN 'High Value' ELSE existing logic   |
| Gold         | go_shipment_agg  | Product_Category              | Silver       | si_shipment_process    | product_category               | LOOKUP                   | product_category NOT NULL                                                          | Map to standardized taxonomy using Product_Taxonomy_Reference                                                          |
| Gold         | go_shipment_agg  | Geographic_Region             | Silver       | si_shipment_process    | region_id                      | LOOKUP                   | region_id NOT NULL                                                                 | Map to latest regional definitions using Region_Mapping_2023                                                           |
| Gold         | go_shipment_agg  | Last_Updated_Timestamp        | Silver       | si_shipment_process    | updated_at                     | MAX                      | updated_at NOT NULL                                                                | MAX(updated_at) per group                                                                                              |
| Gold         | go_shipment_agg  | Data_Source                   | Silver       | si_shipment_process    | source_system                  | NONE                     | source_system NOT NULL                                                             | Direct mapping, add as metadata column                                                                                 |


# Additional Filter Criteria
- Exclude records where Order_Status is 'Cancelled' from all aggregations.
- Include only records with Transaction_Date within the last 5 years.

# General Validation & Cleansing Rules
- Replace NULLs with 'UNKNOWN' for string fields, 0 for numerics.
- All percentages and monetary values rounded to two decimal places.
- Outlier removal for Customer_Lifetime_Value using z-score > 3.
- Enforce decimal precision as per target DDL.
- Remove duplicate aggregations by grouping on all business keys.

# Explanations for Complex Transformations
- **Currency Conversion for Sales_Amount**: Use a currency conversion factor (from a reference table or API) to standardize all sales to USD before aggregation.
- **Customer Segmentation**: Add a 'High Value' segment for customers whose aggregated lifetime value exceeds a business-defined threshold.
- **Product Category Mapping**: Use the Product_Taxonomy_Reference file to map source product categories to a standardized taxonomy for reporting.
- **Region Code Mapping**: Use the Region_Mapping_2023 file to map destination or region_id to the latest region codes.
- **Average Order Value**: Exclude orders flagged as returns from the average calculation.
- **Order Count Renaming**: The field 'Order_Count' is renamed to 'Total_Orders' for clarity in reporting.

# API Cost
apiCost: 0.002000

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Data_Mapping
**pipelineID:** 14678
