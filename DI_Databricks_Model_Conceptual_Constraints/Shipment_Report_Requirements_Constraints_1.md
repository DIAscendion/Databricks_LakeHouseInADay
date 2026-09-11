____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Model data constraints and business rules for Shipment Report Requirements
## *Version*: 1
## *Updated on*: 
____________________________________________

## 1. Data Expectations

### 1.1 Data Completeness
1. Every shipment record must include shipment reference, status, type, origin and destination facility, carrier assignment, and creation details.
2. Creation source and creator role must be present for audit completeness.
3. Facility address details must be complete for both origin and destination.

### 1.2 Data Accuracy
1. Shipment status must match valid domain values (active, completed, cancelled, reconciled).
2. Cancelled shipment identification must use correct planning status value from source system.
3. Distance values must be non-negative and accurate.
4. Direct distance must not exceed total route distance.

### 1.3 Data Format
1. Distance unit of measure must be consistent across all rows; flag mixed units.
2. Billing method datatype must be transformed as required (numeric to string).
3. Creation date must be in valid date format and within operational range.

### 1.4 Data Consistency
1. Shipment identifier must be unique per row at base grain.
2. Facility address joins must use correct stop sequence logic (first stop = origin, last stop = destination).
3. Business partner identifier extraction logic must be confirmed and applied consistently.

## 2. Constraints

### 2.1 Mandatory Fields
1. Shipment reference number: Required for every shipment.
2. Shipment status: Required for operational and audit purposes.
3. Origin and destination facility details: Required for routing and reporting.
4. Creation source and creator role: Required for audit and governance.

### 2.2 Uniqueness Requirements
1. Shipment reference number: Must be unique per shipment record.
2. Bill of lading number: Must be unique for each shipment where applicable.

### 2.3 Data Type Limitations
1. Billing method: Must be transformed to string type for reporting.
2. Distance values: Must be numeric and non-negative.

### 2.4 Dependencies
1. Creator role is derived via join to user role reference table; user must exist in reference.
2. Origin and destination facility derived from stop sequence logic.
3. Business partner identifier is sourced from extended attribute field.

### 2.5 Referential Integrity
1. Shipments must reference valid carrier, facility, and business partner records.
2. Parent shipment reference must point to an existing shipment record.

## 3. Business Rules

### 3.1 Data Processing Rules
1. Exclude zero-distance shipments from rate calculations but count them separately.
2. Validate mapping between shipment identifier fields using real data example.
3. Confirm billing method transformation rule before report development.

### 3.2 Reporting Logic Rules
1. Cancelled shipment count must not exceed total shipment count.
2. Route Efficiency Index must be between 0 and 1.
3. Out-of-route distance must not exceed total route distance; flag anomalies.

### 3.3 Transformation Guidelines
1. Billing method transformation from numeric to string as per system migration.
2. Distance unit conversion if mixed units are present.
3. Business partner identifier extraction from extended attribute structure.
