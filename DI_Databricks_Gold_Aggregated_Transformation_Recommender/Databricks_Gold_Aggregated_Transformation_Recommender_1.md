_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Transformation rules for Aggregated Tables (go_shipment_agg) from Silver to Gold layer in Databricks Lakehouse (Shipment Domain)
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Recommender

This document provides comprehensive transformation rules for Aggregated Tables in the Gold layer of the Databricks Lakehouse, focusing on the `go_shipment_agg` table. The rules are derived from the conceptual model, business constraints, Silver and Gold DDLs, and reporting KPIs for the Shipment domain. The goal is to ensure accurate, performant, and business-aligned aggregations for analytical reporting.

---

## 1. Aggregated Table Identified

| Gold Aggregated Table | Silver Source Table(s)           |
|----------------------|----------------------------------|
| go_shipment_agg      | si_shipment_process              |

---

## 2. Transformation Rules for Aggregated Tables

### [Rule 1]: Total Shipment Count
- **Description**: Calculate the total number of shipments grouped by shipment_status, shipment_type, mode_of_transport, carrier_name, origin_facility_name, and destination_facility_name.
    - **Rationale**: Supports reporting on shipment volumes by key business dimensions.
    - **SQL Example:**
      ```sql
      SELECT
        shipment_status,
        shipment_type,
        mode_of_transport,
        carrier_name,
        origin_facility_name,
        destination_facility_name,
        COUNT(*) AS total_shipment_count
      FROM silver.si_shipment_process
      GROUP BY shipment_status, shipment_type, mode_of_transport, carrier_name, origin_facility_name, destination_facility_name
      ```

### [Rule 2]: Cancelled Shipment Percent
- **Description**: Compute the percentage of cancelled shipments within each group.
    - **Rationale**: Enables monitoring of cancellation rates for operational efficiency.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        100.0 * SUM(CASE WHEN shipment_status = 'CANCELLED' THEN 1 ELSE 0 END) / COUNT(*) AS cancelled_shipment_percent
      FROM ...
      GROUP BY ...
      ```

### [Rule 3]: Reconciled Shipment Percent
- **Description**: Compute the percentage of reconciled shipments within each group.
    - **Rationale**: Tracks reconciliation process effectiveness.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        100.0 * SUM(CASE WHEN shipment_status = 'RECONCILED' THEN 1 ELSE 0 END) / COUNT(*) AS reconciled_shipment_percent
      FROM ...
      GROUP BY ...
      ```

### [Rule 4]: Broker Carrier Usage Percent
- **Description**: Calculate the percentage of shipments using a broker carrier.
    - **Rationale**: Measures reliance on broker carriers for logistics.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        100.0 * SUM(CASE WHEN broker_carrier_name IS NOT NULL AND broker_carrier_name != '' THEN 1 ELSE 0 END) / COUNT(*) AS broker_carrier_usage_percent
      FROM ...
      GROUP BY ...
      ```

### [Rule 5]: On-time Pickup Percent
- **Description**: Calculate the percentage of shipments picked up on time.
    - **Rationale**: Supports service level and carrier performance KPIs.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        100.0 * SUM(CASE WHEN on_time_indicator = 'Y' THEN 1 ELSE 0 END) / COUNT(*) AS on_time_pickup_percent
      FROM ...
      GROUP BY ...
      ```

### [Rule 6]: Out-of-Route Distance Percent
- **Description**: Compute the percent of out-of-route distance relative to total route distance.
    - **Rationale**: Identifies routing inefficiencies and anomalies.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        100.0 * SUM(out_of_route_distance) / NULLIF(SUM(total_route_distance), 0) AS out_of_route_distance_percent
      FROM ...
      GROUP BY ...
      ```

### [Rule 7]: Average Stops per Shipment
- **Description**: Calculate the average number of stops per shipment in each group.
    - **Rationale**: Supports logistics complexity and efficiency analysis.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        AVG(number_of_stops) AS average_stops_per_shipment
      FROM ...
      GROUP BY ...
      ```

### [Rule 8]: Route Efficiency Index
- **Description**: Compute the ratio of direct distance to total route distance (should be between 0 and 1).
    - **Rationale**: Measures route optimization and efficiency.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        AVG(CASE WHEN total_route_distance > 0 THEN direct_distance / total_route_distance ELSE NULL END) AS route_efficiency_index
      FROM ...
      GROUP BY ...
      ```

### [Rule 9]: Unreconciled Shipment Count with Aging
- **Description**: Count unreconciled shipments and provide their aging (days since creation).
    - **Rationale**: Supports audit and operational backlog management.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        SUM(CASE WHEN reconciled_flag = FALSE THEN 1 ELSE 0 END) AS unreconciled_shipment_count,
        STRING_AGG(CASE WHEN reconciled_flag = FALSE THEN CONCAT(shipment_reference_number, ':', DATEDIFF(current_date(), creation_date)) END, ',') AS unreconciled_shipment_count_with_aging
      FROM ...
      GROUP BY ...
      ```

### [Rule 10]: Creation Volume Trend
- **Description**: Provide a trend of shipment creation volume (e.g., by day/week).
    - **Rationale**: Enables time series analysis for planning and forecasting.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        STRING_AGG(CONCAT(DATE_TRUNC('day', creation_date), ':', COUNT(*)), ',') AS creation_volume_trend
      FROM ...
      GROUP BY ...
      ```

### [Rule 11]: Source Mix Percent
- **Description**: Calculate the percent of shipments by creation source within each group.
    - **Rationale**: Monitors the mix of manual, API, and integration-created shipments.
    - **SQL Example:**
      ```sql
      SELECT
        ...,
        100.0 * SUM(CASE WHEN creation_source = 'API' THEN 1 ELSE 0 END) / COUNT(*) AS api_source_percent,
        100.0 * SUM(CASE WHEN creation_source = 'MANUAL' THEN 1 ELSE 0 END) / COUNT(*) AS manual_source_percent,
        100.0 * SUM(CASE WHEN creation_source = 'INTEGRATION' THEN 1 ELSE 0 END) / COUNT(*) AS integration_source_percent
      FROM ...
      GROUP BY ...
      ```

---

## 3. General Aggregation Guidelines

- All aggregations must be performed at the group level defined by shipment_status, shipment_type, mode_of_transport, carrier_name, origin_facility_name, destination_facility_name.
- Nulls must be handled by replacing with 'UNKNOWN' for strings and 0 for numerics.
- All percentages must be rounded to two decimal places.
- All date/time fields must be bucketized as per reporting requirements (e.g., day, week, month).
- All calculations must be traceable to their Silver source columns.
- Audit columns (load_date) must be populated from Silver.

---

## 4. Traceability Matrix

| Gold Aggregated Column                | Silver Source Column(s)                | Transformation Rule(s) Applied                |
|---------------------------------------|----------------------------------------|-----------------------------------------------|
| total_shipment_count                  | shipment_number                        | COUNT, group by business dimensions           |
| cancelled_shipment_percent            | shipment_status                        | SUM/COUNT, filter 'CANCELLED'                 |
| reconciled_shipment_percent           | shipment_status                        | SUM/COUNT, filter 'RECONCILED'                |
| broker_carrier_usage_percent          | broker_carrier_name                    | SUM/COUNT, not null/empty                     |
| on_time_pickup_percent                | on_time_indicator                      | SUM/COUNT, filter 'Y'                         |
| out_of_route_distance_percent         | out_of_route_distance, total_route_distance | SUM, division, percent                  |
| average_stops_per_shipment            | number_of_stops                        | AVG                                           |
| route_efficiency_index                | direct_distance, total_route_distance  | AVG, ratio                                    |
| unreconciled_shipment_count_with_aging| reconciled_flag, creation_date, shipment_reference_number | SUM, DATEDIFF, STRING_AGG      |
| creation_volume_trend                 | creation_date                          | DATE_TRUNC, COUNT, STRING_AGG                 |
| source_mix_percent                    | creation_source                        | SUM/COUNT, filter by source                   |

---

## 5. API Cost

apiCost: 0.001600

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Recommender
**pipelineID:** 14677
