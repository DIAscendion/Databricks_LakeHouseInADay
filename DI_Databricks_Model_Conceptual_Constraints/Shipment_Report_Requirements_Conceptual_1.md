_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Conceptual data model for Shipment Report Requirements
## *Version*: 1
## *Updated on*: 
_____________________________________________

## 1. Domain Overview
The domain covers transportation management, shipment tracking, carrier performance, route optimization, billing, and audit reporting for supply chain and logistics operations. It includes end-to-end shipment monitoring, carrier assignment, route analysis, billing reconciliation, and shipment creation audit.

## 2. List of Entity Names with Descriptions
1. **Shipment**: Represents each shipment with its operational details, origin/destination, status, and identifiers.
2. **Carrier**: Details about assigned, secondary, broker, and designated carriers for shipments.
3. **Facility**: Information about origin and destination facilities, including address and location.
4. **Route**: Contains route details, distances, and stop information for shipments.
5. **Billing**: Bill-to party, billing method, and financial references for shipments.
6. **Business Partner**: Vendor or partner associated with shipments for financial and operational reference.
7. **User Role**: Roles responsible for shipment creation and updates.

## 3. List of Attributes for Each Entity
### Shipment
1. **Shipment Reference Number**: Unique reference for each shipment.
2. **Shipment Status**: Current state of the shipment (active, completed, cancelled, reconciled).
3. **Shipment Type**: Type/category of shipment.
4. **Leg Type**: Segment or leg classification.
5. **Creation Date**: Date the shipment was created.
6. **Creation Source**: Method/source of shipment creation (manual, API, integration).
7. **Creator Role**: User role responsible for creation.
8. **Cancelled Flag**: Indicates if shipment was cancelled.
9. **Reconciled Flag**: Indicates if shipment was reconciled.
10. **Trailer Number**: Trailer assigned to shipment.

### Carrier
1. **Primary Carrier Name**: Main carrier assigned to shipment.
2. **Secondary Carrier Name**: Secondary carrier assigned.
3. **Broker Carrier Name**: Broker carrier assigned.
4. **Mode of Transport**: Transport mode (road, rail, etc.).
5. **Designated Carrier**: Carrier for DC-to-Store master lane/static route.
6. **Feasible Carrier**: Carrier eligible for assignment.

### Facility
1. **Origin Facility Name**: Name of origin facility.
2. **Origin Address**: Address of origin facility.
3. **Origin City**: City of origin facility.
4. **Origin State**: State/province of origin facility.
5. **Origin Postal Code**: Postal code of origin facility.
6. **Origin Country**: Country of origin facility.
7. **Destination Facility Name**: Name of destination facility.
8. **Destination Address**: Address of destination facility.
9. **Destination City**: City of destination facility.
10. **Destination State**: State/province of destination facility.
11. **Destination Postal Code**: Postal code of destination facility.
12. **Destination Country**: Country of destination facility.

### Route
1. **Total Route Distance**: Total distance of shipment route.
2. **Direct Distance**: Direct distance between origin and destination.
3. **Out-of-Route Distance**: Distance not on optimal route.
4. **Distance Unit of Measure**: Unit for distance (miles, km).
5. **Number of Stops**: Total stops in shipment route.
6. **Equipment Type**: Equipment used for shipment.

### Billing
1. **Bill-to Postal Code**: Postal code for bill-to party.
2. **Bill-to State/Province**: State/province for bill-to party.
3. **Bill of Lading Number**: Reference for shipment billing.
4. **Billing Method**: Method used for billing.
5. **Purchase Order Reference**: Purchase order associated with shipment.
6. **Company Identifier**: Company associated with shipment.
7. **Reconciliation Date**: Date shipment was reconciled.

### Business Partner
1. **Business Partner Identifier**: Vendor/partner reference.
2. **Parent Shipment Reference**: Parent shipment for reference.

### User Role
1. **Creator Role**: Role of user who created shipment.

## 4. KPI List
1. **Total Shipment Count**: Number of shipments by status, type, and mode.
2. **Cancelled Shipment %**: Cancelled Shipments / Total Shipments × 100.
3. **Reconciled Shipment %**: Reconciled Shipments / Total Shipments × 100.
4. **Shipments per Carrier**: Breakdown by assigned carrier.
5. **Shipments by Origin and Destination Facility**: Count per facility.
6. **Carrier Assignment Rate %**: Assigned vs feasible carrier ratio.
7. **Broker Carrier Usage %**: Shipments with broker carrier / Total Shipments × 100.
8. **On-time Pickup %**: Scheduled vs actual pickup.
9. **Out-of-Route Distance %**: Out-of-route distance / Total distance × 100.
10. **Average Stops per Shipment**: Total stops / Total shipments.
11. **Average Route Distance**: Average route distance (miles/km).
12. **Route Efficiency Index**: Direct distance / Total distance.
13. **Reconciled Shipment %**: Reconciled / Total × 100.
14. **Unreconciled Shipment Count with Aging**: Count and aging of unreconciled shipments.
15. **Creation Volume Trend**: Shipments created per day/week.
16. **Source Mix %**: Count by source / Total count × 100.

## 5. Conceptual Data Model Diagram
| Source Entity   | Relationship Key Field      | Target Entity     | Relationship Type |
|-----------------|----------------------------|-------------------|-------------------|
| Shipment        | Shipment Reference Number   | Carrier           | Many-to-One       |
| Shipment        | Origin Facility Name        | Facility          | Many-to-One       |
| Shipment        | Destination Facility Name   | Facility          | Many-to-One       |
| Shipment        | Bill of Lading Number       | Billing           | Many-to-One       |
| Shipment        | Business Partner Identifier | Business Partner  | Many-to-One       |
| Shipment        | Creator Role               | User Role         | Many-to-One       |
| Shipment        | Total Route Distance        | Route             | Many-to-One       |

## 6. Common Data Elements in Report Requirements
1. **Shipment Reference Number**
2. **Shipment Status**
3. **Shipment Type**
4. **Origin Facility Name**
5. **Destination Facility Name**
6. **Assigned Carrier**
7. **Mode of Transport**
8. **Bill of Lading Number**
9. **Company Identifier**
10. **Trailer Number**
11. **Creation Date**
12. **Creator Role**
13. **Cancelled/Reconciled Flags**
14. **Distance Measures**
15. **Equipment Type**
16. **Business Partner Identifier**
17. **Billing Method**
18. **Purchase Order Reference**
