_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Conceptual data model for Shipment Report Requirements
## *Version*: 2
## *Updated on*: 
## *Changes*: No explicit changes requested; version increment for update workflow.
## *Reason*: Mode 2 update triggered by Do_You_Need_Any_Changes = "yes".
_____________________________________________

### 1. Domain Overview
The domain covers shipment management, carrier assignment, route optimization, billing and financial tracking, and audit of shipment creation and source. The reports are designed to monitor shipment operations, carrier performance, routing efficiency, billing reconciliation, and data quality governance within a transportation management system (TMS).

### 2. List of Entity Names with Descriptions
1. **Shipment**: Represents a transportation event including origin, destination, status, and carrier assignments.
2. **Carrier**: Represents the transportation provider assigned to a shipment (primary, secondary, broker, designated, feasible).
3. **Facility**: Represents origin and destination locations for shipments.
4. **Route**: Represents the path taken by a shipment, including total, direct, and out-of-route distances.
5. **Billing**: Represents financial and bill-to party details associated with shipments.
6. **Business Partner**: Represents vendors or partners involved in shipments.
7. **User**: Represents the creator or updater of shipment records.

### 3. List of Attributes for Each Entity
#### Shipment
1. **Shipment Reference Number**: Unique reference for each shipment.
2. **Shipment Status**: Current state of the shipment (active, completed, cancelled, reconciled).
3. **Shipment Type**: Classification of shipment.
4. **Leg Type**: Segment classification within shipment.
5. **Creation Date**: Date shipment was created.
6. **Creation Source**: Method or system used to create shipment.
7. **Creator Role**: Role of user who created the shipment.
8. **Cancelled Flag**: Indicates if shipment was cancelled.
9. **Reconciled Flag**: Indicates if shipment was reconciled.
10. **Trailer Number**: Identifier for trailer used.
11. **Company Identifier**: Company associated with shipment.
12. **Parent Shipment Reference**: Reference to parent shipment if applicable.

#### Carrier
1. **Primary Carrier Name**: Main carrier assigned to shipment.
2. **Secondary Carrier Name**: Backup carrier assigned.
3. **Broker Carrier Name**: Broker involved in shipment.
4. **Designated Carrier Name**: Carrier used for static/master lane routes.
5. **Feasible Carrier Name**: Carrier eligible for assignment.
6. **Mode of Transport**: Type of transport used (e.g., truck, rail).

#### Facility
1. **Origin Facility Name**: Name of shipment origin.
2. **Origin Address**: Address details for origin.
3. **Origin City**: City of origin.
4. **Origin State**: State/province of origin.
5. **Origin Postal Code**: Postal code of origin.
6. **Origin Country**: Country of origin.
7. **Destination Facility Name**: Name of shipment destination.
8. **Destination Address**: Address details for destination.
9. **Destination City**: City of destination.
10. **Destination State**: State/province of destination.
11. **Destination Postal Code**: Postal code of destination.
12. **Destination Country**: Country of destination.

#### Route
1. **Total Route Distance**: Total distance covered by shipment.
2. **Direct Distance**: Shortest possible distance between origin and destination.
3. **Out-of-Route Distance**: Distance exceeding direct route.
4. **Distance Unit of Measure**: Unit for distance (miles, km).
5. **Number of Stops**: Total stops in shipment route.
6. **Equipment Type**: Type of equipment used for shipment.

#### Billing
1. **Bill-to Postal Code**: Postal code for bill-to party.
2. **Bill-to State/Province**: State/province for bill-to party.
3. **Bill of Lading Number**: Reference for shipment billing.
4. **Billing Method**: Method used for billing.
5. **Purchase Order Reference**: Reference for purchase order.
6. **Reconciliation Date**: Date shipment was reconciled.

#### Business Partner
1. **Business Partner/Vendor Identifier**: Identifier for partner/vendor.

#### User
1. **Creator Role**: Role of user who created shipment.
2. **Creation Source Type**: Category of creation source (manual, API, integration).

### 4. KPI List
1. **Total Shipment Count**: Number of shipments by status, type, and mode.
2. **Cancelled Shipment %**: Cancelled Shipments / Total Shipments × 100.
3. **Reconciled Shipment %**: Reconciled Shipments / Total Shipments × 100.
4. **Shipments per Carrier**: Breakdown of shipments by assigned carrier.
5. **Shipments by Origin and Destination Facility**: Shipment counts by facility.
6. **Carrier Assignment Rate %**: Assigned vs feasible carrier rate.
7. **Broker Carrier Usage %**: Shipments with broker carrier / Total Shipments × 100.
8. **On-time Pickup %**: Scheduled vs actual pickup performance.
9. **Out-of-Route Distance %**: Out-of-route distance / Total distance × 100.
10. **Average Stops per Shipment**: Total stops / Total shipments.
11. **Route Efficiency Index**: Direct distance / Total distance.
12. **Shipments by Billing Method**: Count by billing method.
13. **Unreconciled Shipment Count with Aging**: Count and age of unreconciled shipments.
14. **Creation Volume Trend**: Shipments created per day/week.
15. **Source Mix %**: Count by creation source / Total count × 100.

### 5. Conceptual Data Model Diagram
| Source Entity | Relationship Key Field | Target Entity | Relationship Type |
|---------------|------------------------|---------------|-------------------|
| Shipment      | shipment reference     | Carrier       | Many-to-One       |
| Shipment      | origin facility name   | Facility      | Many-to-One       |
| Shipment      | destination facility name | Facility   | Many-to-One       |
| Shipment      | route reference        | Route         | One-to-One        |
| Shipment      | bill of lading number  | Billing       | One-to-One        |
| Shipment      | business partner/vendor identifier | Business Partner | Many-to-One |
| Shipment      | creator role           | User          | Many-to-One       |
| Shipment      | parent shipment reference | Shipment   | One-to-One        |

### 6. Common Data Elements in Report Requirements
1. **Shipment Reference Number**
2. **Shipment Status**
3. **Shipment Type**
4. **Origin Facility Name**
5. **Destination Facility Name**
6. **Assigned Carrier Name**
7. **Mode of Transport**
8. **Bill of Lading Number**
9. **Company Identifier**
10. **Creation Date**
11. **Creator Role**
12. **Reconciled Flag**
13. **Cancelled Flag**
14. **Distance Unit of Measure**
15. **Number of Stops**
