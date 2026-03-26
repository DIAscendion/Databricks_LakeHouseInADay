____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Model data constraints and business rules for Shipment Report Requirements
## *Version*: 1
## *Updated on*: 
____________________________________________

## 1. Data Expectations

### 1.1 Data Completeness
1. Every shipment record must have a shipment reference number, status, type, origin, destination, assigned carrier, and creation date.
2. Creation source and creator role must be present for audit completeness.
3. Facility address details (origin and destination) must be populated for all shipments.
4. Carrier assignment fields (primary, secondary, broker) must be filled for relevant shipments.

### 1.2 Data Accuracy
1. Shipment status must match valid domain values (active, completed, cancelled, reconciled).
2. Cancelled shipment identification must use correct planning status value from source system.
3. Distance values (total, direct, out-of-route) must be accurate and non-negative.
4. Billing method must be transformed correctly between legacy (numeric) and new system (string).

### 1.3 Data Format
1. Distance unit of measure must be uniform across all rows (miles or km).
2. Facility address fields must follow standard postal formatting.
3. Billing method datatype must be consistent with system requirements.
4. Creation date must be in valid date format and within operational range.

### 1.4 Data Consistency
1. Shipment identifier must be unique per row at the base grain.
2. Facility address joins must use correct stop sequence logic (first stop = origin, last stop = destination).
3. Direct distance must not exceed total route distance.
4. Distance unit of measure must not mix units; flag and convert if mixed.

## 2. Constraints

### 2.1 Mandatory Fields
1. Shipment Reference Number: Required for all shipment records.
2. Shipment Status: Required for operational and audit tracking.
3. Origin and Destination Facility Name: Required for shipment routing.
4. Assigned Carrier: Required for carrier performance and assignment reporting.
5. Creation Date and Creator Role: Required for audit and traceability.

### 2.2 Uniqueness Requirements
1. Shipment Reference Number: Must be unique per shipment.
2. Bill of Lading Number: Must be unique per shipment for billing reconciliation.

### 2.3 Data Type Limitations
1. Billing Method: Numeric in legacy system, string in new system; transformation required.
2. Distance Measures: Must be numeric and non-negative.

### 2.4 Dependencies
1. Creator Role is derived via join to user role reference table; user must exist in reference table.
2. Business Partner Identifier is sourced from extended attribute; extraction logic required.
3. Purchase Order Reference must be confirmed in target system before inclusion.

### 2.5 Referential Integrity
1. Facility address joins must use stop sequence logic for origin/destination mapping.
2. Shipment to Carrier relationship must reference valid carrier records.
3. Shipment to Billing must reference valid bill-to party and billing method.

## 3. Business Rules

### 3.1 Data Processing Rules
1. Exclude zero-distance shipments from rate calculations but count separately.
2. Validate mapping between shipment identifier fields using real data examples.
3. Ensure cancelled shipment count does not exceed total shipment count.

### 3.2 Reporting Logic Rules
1. Cancelled Shipment % = Count of cancelled shipments / Total shipments × 100.
2. Reconciled % = Count of reconciled shipments / Total shipments × 100.
3. Out-of-Route % = Out-of-route distance / Total distance × 100.
4. Route Efficiency Index = Direct distance / Total distance (0 to 1).
5. Creation Rate = Count of shipments by source per day or week.

### 3.3 Transformation Guidelines
1. Billing method transformation from numeric (legacy) to string (new system) must be applied.
2. Distance unit conversion must be performed if mixed units detected.
3. Business partner extraction from extended attribute must follow confirmed logic.
