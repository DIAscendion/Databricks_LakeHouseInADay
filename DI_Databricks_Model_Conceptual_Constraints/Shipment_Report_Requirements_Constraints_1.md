____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Model data constraints and business rules for Shipment Report Requirements
## *Version*: 1
## *Updated on*: 
____________________________________________

## 1. Data Expectations

### 1.1 Data Completeness
1. Every shipment record must contain a shipment identifier, status, type, origin facility, destination facility, assigned carrier, creation date, and creator role.
2. Creation source and creator role must be non-null for audit completeness.
3. Facility address and stop sequence logic must derive origin and destination for each shipment.

### 1.2 Data Accuracy
1. Shipment status must be a valid predefined domain value.
2. Cancelled shipment identification is based on a specific planning status value in the source system.
3. Distance values must be non-negative and direct distance must not exceed total route distance.
4. Billing method datatype transformation must be validated before use.

### 1.3 Data Format
1. Distance unit of measure must be consistent across all rows; mixed units must be flagged and converted.
2. Billing method datatype may differ between legacy and new system; transformation rule required.
3. Creation date must be in a valid date format and fall within the expected operational date range.

### 1.4 Data Consistency
1. Shipment identifier must be unique per row at the base grain.
2. Facility address joins must use correct stop sequence logic.
3. Business partner identifier extraction logic must be confirmed for consistency.
4. Purchase order reference source must be confirmed for consistency.

## 2. Constraints

### 2.1 Mandatory Fields
1. Shipment identifier: Required for every shipment record.
2. Shipment status: Required for operational and audit reporting.
3. Origin facility name and destination facility name: Required for route and facility analysis.
4. Assigned carrier: Required for carrier performance and assignment reporting.
5. Creation date and creator role: Required for audit and source reporting.

### 2.2 Uniqueness Requirements
1. Shipment identifier must be unique per row.
2. Bill of lading number should be unique for each shipment for billing reconciliation.

### 2.3 Data Type Limitations
1. Billing method: Numeric in legacy, string in new system; transformation required.
2. Distance fields: Must be numeric and non-negative.

### 2.4 Dependencies
1. Creator role must be resolvable via a join to the user role reference table.
2. Origin and destination facility must be derived using stop sequence logic.
3. Business partner identifier is sourced from an extended attribute field; extraction logic required.

### 2.5 Referential Integrity
1. Shipments must reference valid carriers, facilities, and business partners.
2. Facility address joins must use correct stop sequence logic for origin and destination.

## 3. Business Rules

### 3.1 Data Processing Rules
1. Exclude zero-distance shipments from rate calculations but count them separately.
2. Validate mapping between shipment identifier fields using real data examples.
3. Confirm billing method datatype transformation rule before development.

### 3.2 Reporting Logic Rules
1. Cancelled shipment identification is based on planning status code mapping.
2. Broker carrier fields and assigned lane priority status must be confirmed before inclusion in priority reporting.
3. Validate that out-of-route distance does not exceed total route distance; flag anomalies.

### 3.3 Transformation Guidelines
1. Billing method datatype transformation from numeric (legacy) to string (new system).
2. Distance unit conversion if mixed units are present.
3. Business partner extended attribute extraction logic must be confirmed before use in reports.
