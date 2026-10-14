_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Silver layer logical data model for Rental Revenue-to-Cash analytical reporting based on conceptual, constraint, bronze, and Jira requirements
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Model

## 1.1 Summary
1. This Silver layer logical model is designed for the Rental Revenue-to-Cash analytical reporting domain.
2. It is derived from the provided conceptual model, data constraints, Bronze logical model, and Jira business context from AP-1.
3. The Silver layer mirrors the Bronze table structure while removing primary key, foreign key, unique identifier, and ID fields from the logical output.
4. It standardizes data types, supports data quality validation, and adds structures for error handling and process audit tracking.
5. Table names follow the required `Si_` naming convention.

## 1.2 Design Rules Applied
1. Bronze table structures are mirrored into Silver tables.
2. Primary key, foreign key, unique identifier, and ID fields are not included in the logical column listings.
3. Existing Bronze business columns are retained except prohibited key and ID style fields.
4. Data types are standardized to logical Silver data types such as string, date, timestamp, decimal, integer, and boolean.
5. Additional Silver tables are included for error data and pipeline process audit data as required.
6. Jira ticket AP-1 requirements are used exactly as business context for reporting, AR, collections, cash application, and credit risk domains.

## 1.3 Silver Tables

### 1.3.1 Si_Rental_Contracts
**Description:** Conformed Silver table for rental contract data used for reporting on revenue, billing performance, contract status, and open exposure.

| Column Name | Description | Data Type |
|---|---|---|
| Branch Code | Standardized branch code representing the branch where the rental contract was recorded. | string |
| Equipment Class | Standardized equipment category associated with the rental contract. | string |
| Contract Start Date | Standardized contract start date used to indicate when rental coverage begins. | date |
| Contract End Date | Standardized contract end date used to indicate when rental coverage ends or remains open. | date |
| Contract Status | Standardized contract lifecycle status such as Open or Closed. | string |
| Daily Rate | Standardized daily rental charge for the contract. | decimal(18,2) |
| Source System | Source application from which the contract record was received. | string |
| File Path | Ingestion lineage path for the source file or batch. | string |
| File Modification Time | Timestamp when the source file was last modified. | timestamp |
| Load Timestamp | Timestamp when the record was loaded into the platform. | timestamp |
| Update Timestamp | Timestamp when the record was last updated in the platform. | timestamp |

### 1.3.2 Si_Invoices
**Description:** Conformed Silver table for invoice and credit memo data used in billing, AR aging, and revenue reporting.

| Column Name | Description | Data Type |
|---|---|---|
| Invoice Date | Standardized billing date for the invoice or credit memo transaction. | date |
| Due Date | Standardized expected payment due date for aging and collections analysis. | date |
| Invoice Amount | Standardized billed amount for the invoice transaction. | decimal(18,2) |
| Tax Amount | Standardized tax amount recorded on the invoice. | decimal(18,2) |
| Invoice Type | Transaction type such as standard invoice or credit memo. | string |
| Currency | Currency code of the billed transaction. | string |
| Source System | Source application from which the invoice record was received. | string |
| File Path | Ingestion lineage path for the source file or batch. | string |
| File Modification Time | Timestamp when the source file was last modified. | timestamp |
| Load Timestamp | Timestamp when the record was loaded into the platform. | timestamp |
| Update Timestamp | Timestamp when the record was last updated in the platform. | timestamp |

### 1.3.3 Si_Cash_Receipts
**Description:** Conformed Silver table for payment receipt and cash application data used in collections and unapplied cash monitoring.

| Column Name | Description | Data Type |
|---|---|---|
| Receipt Date | Standardized date on which the payment receipt was recorded. | date |
| Payment Amount | Standardized amount collected in the payment transaction. | decimal(18,2) |
| Payment Method | Standardized method used to make the payment. | string |
| Source System | Source application from which the payment record was received. | string |
| File Path | Ingestion lineage path for the source file or batch. | string |
| File Modification Time | Timestamp when the source file was last modified. | timestamp |
| Load Timestamp | Timestamp when the record was loaded into the platform. | timestamp |
| Update Timestamp | Timestamp when the record was last updated in the platform. | timestamp |

### 1.3.4 Si_Customer_Master
**Description:** Conformed Silver customer table used for AR, cash application, and credit risk reporting after Silver-level standardization and deduplication preparation.

| Column Name | Description | Data Type |
|---|---|---|
| Customer Name | Standardized customer business name used for reporting and exposure analysis. | string |
| Credit Terms | Standardized payment terms assigned to the customer account. | string |
| Credit Limit | Standardized approved customer credit exposure limit. | decimal(18,2) |
| Customer Since | Standardized date indicating when the customer relationship began. | date |
| Customer Status | Standardized account status such as Active or Suspended. | string |
| Source System | Source application from which the customer record was received. | string |
| File Path | Ingestion lineage path for the source file or batch. | string |
| File Modification Time | Timestamp when the source file was last modified. | timestamp |
| Load Timestamp | Timestamp when the record was loaded into the platform. | timestamp |
| Update Timestamp | Timestamp when the record was last updated in the platform. | timestamp |

### 1.3.5 Si_Branch_Employee
**Description:** Conformed Silver table for branch employee assignment data used for sales representative and collector reporting.

| Column Name | Description | Data Type |
|---|---|---|
| Employee Name | Standardized employee name for personnel-level reporting and assignment analysis. | string |
| Role | Standardized employee role such as Sales Representative or Collector. | string |
| Branch Code | Standardized branch code for the employee assignment. | string |
| Region | Standardized region aligned with the employee branch assignment. | string |
| Collector Assignment | Standardized collector assignment reference used in collections reporting. | string |
| Effective Date | Standardized effective date for the employee assignment record. | date |
| Source System | Source application from which the employee record was received. | string |
| File Path | Ingestion lineage path for the source file or batch. | string |
| File Modification Time | Timestamp when the source file was last modified. | timestamp |
| Load Timestamp | Timestamp when the record was loaded into the platform. | timestamp |
| Update Timestamp | Timestamp when the record was last updated in the platform. | timestamp |

### 1.3.6 Si_Data_Quality_Errors
**Description:** Silver support table to capture rejected, failed, duplicate, invalid, orphaned, and rule-breaking records identified during Silver data quality and validation processing.

| Column Name | Description | Data Type |
|---|---|---|
| Source Table Name | Name of the Silver source table where the validation issue occurred. | string |
| Error Category | High-level classification of the data quality issue. | string |
| Error Rule | Specific validation or constraint rule that failed. | string |
| Error Description | Human-readable explanation of the identified issue. | string |
| Rejected Record Payload | Record content or serialized payload captured for troubleshooting. | string |
| Validation Status | Status indicating whether the record failed, was quarantined, or was reprocessed. | string |
| Detected Timestamp | Timestamp when the issue was detected. | timestamp |
| Pipeline Run Timestamp | Timestamp of the pipeline execution that identified the issue. | timestamp |
| Source System | Source application associated with the failed record. | string |
| File Path | Ingestion lineage path associated with the failed record. | string |

### 1.3.7 Si_Process_Audit
**Description:** Silver support table to capture pipeline execution, reconciliation, and processing audit details for Silver transformations.

| Column Name | Description | Data Type |
|---|---|---|
| Pipeline Name | Name of the Silver pipeline or workflow executed. | string |
| Source Table Name | Name of the source table processed in the run. | string |
| Target Table Name | Name of the Silver target table loaded in the run. | string |
| Processing Status | Final status of the pipeline step such as success, failed, or partial success. | string |
| Processing Start Timestamp | Timestamp when pipeline execution started. | timestamp |
| Processing End Timestamp | Timestamp when pipeline execution ended. | timestamp |
| Processing Duration Seconds | Total processing duration measured in seconds. | decimal(18,2) |
| Records Read Count | Number of source records read during execution. | integer |
| Records Written Count | Number of target records written during execution. | integer |
| Records Rejected Count | Number of records rejected during data quality validation. | integer |
| Reconciliation Status | Status of count or amount reconciliation for the run. | string |
| Processed By | Process, job, or service responsible for the execution. | string |

# 2. Data Type Standardization

## 2.1 Standardization Rules
1. `Text` values from Bronze are standardized to `string` in Silver.
2. `Date/Text` values from Bronze are standardized to `date` where the business meaning is clearly date-based.
3. Date-time operational metadata values are standardized to `timestamp`.
4. Financial and rate-based numeric measures are standardized to `decimal(18,2)`.
5. Count-based measures in audit structures are standardized to `integer`.
6. Silver preserves the Bronze business structure but improves consistency for downstream Gold analytics.

# 3. Data Constraints and Validation Alignment

## 3.1 Constraints Applied from Inputs
1. Branch must exist in the organization hierarchy and be active for the selected date.
2. Health score must remain between 0 and 100.
3. Duplicate score records must be prevented for unique grain Branch, Date, Period Type.
4. Invoice amounts must tie to a valid contract after Silver conformance.
5. Credit memo amounts must be negative and standard invoice amounts must be non-negative.
6. Duplicate revenue aggregates must be prevented for unique grain Branch, Date, Sales Rep, Equipment Class.
7. Every outstanding invoice must map to a valid customer.
8. Aging bucket boundaries are fixed as 0-30, 31-60, 61-90, and 90+ and must not overlap.
9. Duplicate AR snapshot records must be prevented for unique grain Customer, Invoice, Snapshot Date.
10. Payment amount must be non-negative.
11. A payment can apply to zero, one, or more invoices, and partial application must be tracked.
12. Duplicate payment records must be prevented for unique grain Receipt ID.
13. Each customer must resolve to a single conformed customer record after deduplication.
14. Credit limit must be non-negative.
15. Duplicate customer risk snapshot records must be prevented for unique grain Customer, Snapshot Date.

## 3.2 Silver Validation Use
1. The Silver layer standardizes source records before Gold-level KPI computation.
2. Deduplication preparation is required for customer conformance because the inputs explicitly require duplicate customer resolution before exposure aggregation.
3. Silver must preserve unapplied cash as separately traceable data instead of excluding it.
4. Silver must support reconciliation of drill-through totals to downstream fact totals.
5. Silver error handling tables capture violations instead of silently discarding failed records.

# 4. Relationships Between Tables Across Layers

## 4.1 Cross-Layer Relationship Mapping
| Layer | Source Table | Relationship Key Field | Target Table | Relationship Type | Notes |
|---|---|---|---|---|---|
| Conceptual | Region | Region | Branch | One-to-Many | Region rolls up to multiple branches. |
| Conceptual | Branch | Branch | Contract | One-to-Many | Branch owns multiple rental contracts. |
| Conceptual | Customer | Customer | Contract | One-to-Many | Customer can hold multiple contracts. |
| Conceptual | Customer | Customer | Invoice | One-to-Many | Customer can have multiple invoices. |
| Conceptual | Contract | Contract | Invoice | One-to-Many | Contract can generate multiple invoices. |
| Conceptual | Invoice | Invoice to Payment Application | Cash Receipt | One-to-Many | Invoice may be linked to multiple receipts. |
| Bronze to Silver | Bz_Rental_Contracts | Contract reference | Si_Rental_Contracts | One-to-One logical conformance | Same business structure carried into Silver without key fields in output. |
| Bronze to Silver | Bz_Invoices | Invoice reference | Si_Invoices | One-to-One logical conformance | Same business structure carried into Silver without key fields in output. |
| Bronze to Silver | Bz_Cash_Receipts | Receipt reference | Si_Cash_Receipts | One-to-One logical conformance | Same business structure carried into Silver without key fields in output. |
| Bronze to Silver | Bz_Customer_Master | Customer reference | Si_Customer_Master | One-to-One logical conformance | Same business structure carried into Silver with customer standardization. |
| Bronze to Silver | Bz_Branch_Employee | Employee assignment reference | Si_Branch_Employee | One-to-One logical conformance | Same business structure carried into Silver with role standardization. |
| Silver Internal | Si_Customer_Master | Customer business reference | Si_Rental_Contracts | One-to-Many | Customer data supports contract-level analysis after conformance. |
| Silver Internal | Si_Rental_Contracts | Contract business reference | Si_Invoices | One-to-Many | Contract billing relationship remains required for reporting. |
| Silver Internal | Si_Customer_Master | Customer business reference | Si_Invoices | One-to-Many | Customer supports invoice-level AR reporting. |
| Silver Internal | Si_Invoices | Invoice business reference | Si_Cash_Receipts | One-to-Many | Payments can be applied to one or more invoices; unapplied receipts remain supported. |
| Silver Internal | Si_Branch_Employee | Branch Code | Si_Rental_Contracts | One-to-Many | Employee assignment aligns to branch contract activity. |
| Silver Internal | Si_Branch_Employee | Region | Si_Customer_Master | One-to-Many logical rollup | Regional assignment supports reporting and security rollup. |

# 5. Conceptual Data Model Diagram in Tabular Form

| Source Entity/Table | Connected To | Key Field Mentioned in Input | Relationship Type | Relationship Description |
|---|---|---|---|---|
| Region | Branch | Region | 1-M | One region is connected to many branches by Region. |
| Branch | Contract | Branch | 1-M | One branch is connected to many contracts by Branch. |
| Customer | Contract | Customer | 1-M | One customer is connected to many contracts by Customer. |
| Customer | Invoice | Customer | 1-M | One customer is connected to many invoices by Customer. |
| Sales Rep | Branch | Branch | M-1 | Many sales rep assignments connect to one branch by Branch. |
| Collector | Branch | Branch | M-1 | Many collector assignments connect to one branch by Branch. |
| Collector | Customer | Collector Assignment | 1-M | One collector is connected to many customers by Collector Assignment. |
| Contract | Invoice | Contract | 1-M | One contract is connected to many invoices by Contract. |
| Invoice | Cash Receipt | Invoice to Payment Application | 1-M | One invoice is connected to many cash receipts by Invoice to Payment Application. |
| Date | Fact Rental Revenue | Date | 1-M | One date is connected to many rental revenue facts by Date. |
| Date | Fact AR Aging | Date | 1-M | One date is connected to many AR aging facts by Date. |
| Date | Fact Cash Application | Date | 1-M | One date is connected to many cash application facts by Date. |
| Date | Fact Credit Risk | Date | 1-M | One date is connected to many credit risk facts by Date. |
| Customer | Fact AR Aging | Customer | 1-M | One customer is connected to many AR aging facts by Customer. |
| Customer | Fact Credit Risk | Customer | 1-M | One customer is connected to many credit risk facts by Customer. |
| Branch | Fact Rental Revenue | Branch | 1-M | One branch is connected to many rental revenue facts by Branch. |
| Branch | Fact Cash Application | Branch | 1-M | One branch is connected to many cash application facts by Branch. |
| Contract | Fact Rental Revenue | Contract | 1-M | One contract is connected to many rental revenue facts by Contract. |
| Invoice | Fact Cash Application | Invoice | 1-M | One invoice is connected to many cash application facts by Invoice. |
| Organization Hierarchy | Branch | Organization Hierarchy | 1-M | One organization hierarchy is connected to many branches by Organization Hierarchy. |

# 6. Rationale for Key Design Decisions

1. The Silver model mirrors the Bronze structure exactly at the table level because the instructions require the Silver structure to follow Bronze while removing key and ID fields.
2. Data types are standardized in Silver to improve consistency for downstream Gold facts and governed analytics.
3. Error and audit tables are included because the instructions explicitly require structures for data quality errors, validation exceptions, and process audit data.
4. Customer conformance is emphasized because the Jira and constraints explicitly require duplicate customer resolution before exposure aggregation.
5. Unapplied cash is preserved as explicit data because the Jira ticket requires it to be flagged and reported separately.
6. Contract, invoice, payment, customer, branch, and employee relationships are documented using the business relationship descriptions exactly inferable from the provided inputs.
7. No new business entities beyond those already supported by the inputs are introduced into the Silver structure except the required error and audit support structures.

# 7. Assumptions Made

1. Source-to-Silver conformance preserves all Bronze business columns because no removal other than keys and ID fields was requested.
2. Mixed Bronze date fields can be standardized to date where their business meaning is clearly date-based in the inputs.
3. Relationship key names are documented exactly at the business level because physical key columns are excluded from the logical model output.
4. The available Bronze logical model is treated as the authoritative Bronze structure for the Silver design in this run.

# 8. apiCost
apiCost: 0.000000
