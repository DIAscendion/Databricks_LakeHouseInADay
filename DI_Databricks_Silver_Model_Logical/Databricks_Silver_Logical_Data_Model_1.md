_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Silver logical data model for Rental Revenue-to-Cash reporting aligned to medallion architecture and reporting requirements.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Model

## 1.1 Summary
This Silver layer logical model is derived from the Jira reporting requirements in AP-1, the conceptual data model, the business constraints, and the Bronze logical model. The Silver layer mirrors the Bronze table structure, standardizes logical data types, removes primary key, foreign key, unique identifier, and ID-style fields from the model, and adds data quality error handling and process audit structures for governed downstream reporting.

## 1.2 Jira Business Context Used
1. **AP-1** - Reporting Requirements for Rental Revenue-to-Cash - Status: To Do
2. Business scope includes executive scorecard, billing performance, AR aging, cash application, and customer credit risk reporting.
3. Required controls include branch hierarchy validation, health score range validation, duplicate prevention by stated business grain, reconciliation validations, conformed customer resolution, and explicit unapplied cash handling.

## 1.3 Design Rules Applied
1. Silver tables mirror the Bronze structures exactly at the table level.
2. Fields that represent primary keys, foreign keys, unique identifiers, or ID fields are excluded.
3. Table names begin with the required `Si_` prefix.
4. Data types are standardized into logical business types such as `string`, `date`, `timestamp`, `decimal`, and `integer`.
5. Descriptions are provided for every column.
6. Additional Silver support tables are included for data quality errors and processing audit requirements.
7. No new business entities beyond the supplied Bronze, conceptual, and Jira context are invented.

## 1.4 Silver Tables

### 1.4.1 Si_Rental_Contracts
**Description:** Standardized Silver representation of rental contract data used for branch, equipment class, contract status, and revenue-supporting analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Branch Code | string | Standardized branch code from the contract source used for branch-level conformance and reporting alignment. |
| Equipment Class | string | Standardized equipment category used for billing and revenue analysis. |
| Contract Start Date | date | Standardized contract start date used for rental period analysis. |
| Contract End Date | date | Standardized contract end date used to distinguish open and closed rental periods. |
| Contract Status | string | Standardized contract lifecycle status such as Open or Closed. |
| Daily Rate | decimal | Standardized daily rental charge used to support rate-based calculations. |
| Source System | string | Originating operational system for lineage and reconciliation. |
| File Path | string | Source file or ingestion path retained for traceability. |
| File Modification Time | timestamp | Source file modification timestamp used for lineage and ingestion checks. |
| Load Timestamp | timestamp | Platform load timestamp for the Silver record. |
| Update Timestamp | timestamp | Latest platform update timestamp for the Silver record. |

### 1.4.2 Si_Invoices
**Description:** Standardized Silver representation of invoice and credit memo data used in billing, AR, and payment application analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Invoice Date | date | Standardized billing date for the invoice or credit memo transaction. |
| Due Date | date | Standardized due date used for aging and payment timeliness analysis. |
| Invoice Amount | decimal | Standardized billed amount for invoice reporting and downstream validations. |
| Tax Amount | decimal | Standardized tax amount associated with the invoice transaction. |
| Invoice Type | string | Standardized invoice classification such as standard invoice or credit memo. |
| Currency | string | Standardized transaction currency code. |
| Source System | string | Originating source system for billing data lineage. |
| File Path | string | Source file or ingestion path retained for traceability. |
| File Modification Time | timestamp | Source file modification timestamp captured from ingestion lineage. |
| Load Timestamp | timestamp | Platform load timestamp for the Silver invoice record. |
| Update Timestamp | timestamp | Latest platform update timestamp for the Silver invoice record. |

### 1.4.3 Si_Cash_Receipts
**Description:** Standardized Silver representation of payment receipt data used for collection, payment method, and unapplied cash reporting.

| Column Name | Data Type | Description |
|---|---|---|
| Receipt Date | date | Standardized payment receipt date used for collection reporting. |
| Payment Amount | decimal | Standardized payment amount used in cash collected and unapplied cash analysis. |
| Payment Method | string | Standardized payment method such as ACH, check, card, or wire. |
| Source System | string | Originating payment source retained for lineage. |
| File Path | string | Source file or ingestion path retained for auditability. |
| File Modification Time | timestamp | Source file modification timestamp for processing traceability. |
| Load Timestamp | timestamp | Platform load timestamp for the Silver payment record. |
| Update Timestamp | timestamp | Latest platform update timestamp for the Silver payment record. |

### 1.4.4 Si_Customer_Master
**Description:** Standardized Silver representation of conformed customer master data used for AR, collections, and credit risk reporting.

| Column Name | Data Type | Description |
|---|---|---|
| Customer Name | string | Customer business name used in AR, collections, and credit risk reporting. |
| Credit Terms | string | Standardized payment terms assigned to the customer. |
| Credit Limit | decimal | Standardized approved credit exposure threshold for the customer. |
| Customer Since | date | Standardized customer relationship start date used for tenure analysis. |
| Customer Status | string | Standardized customer state such as Active or Suspended. |
| Source System | string | Originating customer source system for lineage and conformance tracking. |
| File Path | string | Source file or ingestion path retained for audit and traceability. |
| File Modification Time | timestamp | Source file modification timestamp used for ingestion lineage. |
| Load Timestamp | timestamp | Platform load timestamp for the Silver customer record. |
| Update Timestamp | timestamp | Latest platform update timestamp for the Silver customer record. |

### 1.4.5 Si_Branch_Employee
**Description:** Standardized Silver representation of employee assignment data used for sales representative and collector reporting alignment.

| Column Name | Data Type | Description |
|---|---|---|
| Employee Name | string | Employee name associated with sales or collection responsibilities. |
| Role | string | Standardized employee role such as Sales Representative or Collector. |
| Branch Code | string | Standardized branch code used to align employee assignments to branch reporting. |
| Region | string | Standardized region associated with the assigned branch. |
| Collector Assignment | string | Collector-related assignment information used for collections reporting alignment. |
| Effective Date | date | Standardized effective date of the employee assignment record. |
| Source System | string | Originating employee or HR source system for lineage. |
| File Path | string | Source file or ingestion path retained for traceability. |
| File Modification Time | timestamp | Source file modification timestamp used in audit lineage. |
| Load Timestamp | timestamp | Platform load timestamp for the Silver employee assignment record. |
| Update Timestamp | timestamp | Latest platform update timestamp for the Silver employee assignment record. |

### 1.4.6 Si_Data_Quality_Errors
**Description:** Silver support table used to store records that fail data quality, validation, or conformance rules defined by the business constraints and Jira requirements.

| Column Name | Data Type | Description |
|---|---|---|
| Source Table | string | Name of the originating Silver table where the validation issue occurred. |
| Error Category | string | High-level classification of the issue such as completeness, accuracy, format, consistency, or referential integrity. |
| Error Rule | string | Specific validation rule that failed. |
| Error Description | string | Human-readable description of the failure condition. |
| Rejected Value | string | Value or value summary that caused the validation issue where available. |
| Business Grain | string | Business-level grain context used to identify the affected record set without using ID fields. |
| Source System | string | Originating source system for the rejected data. |
| File Path | string | Source file path associated with the failed record or batch. |
| Detected Timestamp | timestamp | Timestamp when the data quality issue was detected. |
| Status | string | Resolution state of the error such as open, reviewed, corrected, or waived. |

### 1.4.7 Si_Process_Audit
**Description:** Silver support table used to capture pipeline execution, validation, reconciliation, and operational audit details.

| Column Name | Data Type | Description |
|---|---|---|
| Pipeline Name | string | Name of the Silver processing pipeline. |
| Source Table | string | Source or Silver table processed in the pipeline run. |
| Process Start Timestamp | timestamp | Timestamp when the processing step started. |
| Process End Timestamp | timestamp | Timestamp when the processing step completed. |
| Processing Status | string | Outcome of the processing step such as success, failed, partial_success, or quarantined. |
| Records Read | integer | Count of records read from the upstream source or Bronze table. |
| Records Written | integer | Count of records successfully written to Silver. |
| Error Record Count | integer | Count of records redirected to the data quality error table. |
| Validation Summary | string | Summary of validation and reconciliation outcomes for the run. |
| Processed By | string | Job, workflow, or service responsible for the run. |

## 1.5 Data Type Standardization
1. `Date/Text` values from Bronze are standardized to `date` in Silver where business dates are expected.
2. Event and lineage timestamps are standardized to `timestamp`.
3. Monetary and rate-supporting numeric fields are standardized to `decimal`.
4. Textual classification and descriptive attributes are standardized to `string`.
5. Count-based operational metrics in support tables are standardized to `integer`.

## 1.6 Data Quality and Validation Alignment
1. Branch values must align to the organization hierarchy and active branch expectations from AP-1 and constraints.
2. Health score validations from AP-1 are downstream reporting validations and should be supported by conformed Silver inputs.
3. Invoice amounts must support the rule that standard invoice amounts are non-negative and credit memo amounts are negative.
4. Payment amount must remain non-negative.
5. Aging bucket rules, duplicate prevention, customer conformance, and unapplied cash reporting are supported through Silver cleansing and error capture.
6. Duplicate customer records representing the same legal entity must be resolved before downstream exposure aggregation.
7. Drill-through and reconciliation support is enabled by retaining lineage fields and process audit information.

## 1.7 Relationships Between Tables Across Layers
| Layer | Source Table | Relationship Key Field | Target Table | Relationship Type | Notes |
|---|---|---|---|---|---|
| Conceptual | Region | Region | Branch | One-to-Many | Region rolls down to branch. |
| Conceptual | Branch | Branch | Contract | One-to-Many | Branch supports contract-level reporting. |
| Conceptual | Customer | Customer | Contract | One-to-Many | Customer can hold multiple contracts. |
| Conceptual | Customer | Customer | Invoice | One-to-Many | Customer supports invoice and AR reporting. |
| Conceptual | Contract | Contract | Invoice | One-to-Many | Contract can generate multiple invoices. |
| Conceptual | Invoice | Invoice to Payment Application | Cash Receipt | One-to-Many | Invoice may be paid through multiple receipts. |
| Bronze to Silver | Bz_Rental_Contracts | Business-equivalent contract reference | Si_Rental_Contracts | One-to-One logical transformation | Silver mirrors Bronze structure with standardized types. |
| Bronze to Silver | Bz_Invoices | Business-equivalent invoice reference | Si_Invoices | One-to-One logical transformation | Silver retains invoice attributes excluding ID fields. |
| Bronze to Silver | Bz_Cash_Receipts | Business-equivalent receipt reference | Si_Cash_Receipts | One-to-One logical transformation | Silver retains payment attributes excluding ID fields. |
| Bronze to Silver | Bz_Customer_Master | Business-equivalent customer reference | Si_Customer_Master | One-to-One logical transformation | Silver supports customer conformance and deduplication. |
| Bronze to Silver | Bz_Branch_Employee | Business-equivalent employee assignment reference | Si_Branch_Employee | One-to-One logical transformation | Silver supports sales rep and collector alignment. |
| Silver | Si_Customer_Master | Customer | Si_Rental_Contracts | One-to-Many | Customer context supports contract analysis. |
| Silver | Si_Rental_Contracts | Contract | Si_Invoices | One-to-Many | Contract activity leads to invoice generation. |
| Silver | Si_Customer_Master | Customer | Si_Invoices | One-to-Many | Customer supports invoice and receivable analysis. |
| Silver | Si_Invoices | Invoice | Si_Cash_Receipts | One-to-Many | Invoice payment application relationship. |
| Silver | Si_Branch_Employee | Branch Code | Si_Rental_Contracts | One-to-Many | Employee branch assignments align to contract activity. |
| Silver | Si_Branch_Employee | Region | Si_Rental_Contracts | One-to-Many | Region-based workforce alignment supports rollups. |

## 2. Conceptual Data Model Diagram in Tabular Form
| Table A | Connected To | Key Field Used for Relationship | Relationship Description |
|---|---|---|---|
| Region | Branch | Region | One region is connected to many branches by Region. |
| Branch | Contract | Branch | One branch is connected to many contracts by Branch. |
| Customer | Contract | Customer | One customer is connected to many contracts by Customer. |
| Customer | Invoice | Customer | One customer is connected to many invoices by Customer. |
| Sales Rep | Branch | Branch | Many sales representatives are connected to one branch by Branch. |
| Collector | Branch | Branch | Many collectors are connected to one branch by Branch. |
| Collector | Customer | Collector Assignment | One collector is connected to many customers by Collector Assignment. |
| Contract | Invoice | Contract | One contract is connected to many invoices by Contract. |
| Invoice | Cash Receipt | Invoice to Payment Application | One invoice is connected to many cash receipts by invoice-to-payment application. |
| Date | Fact Rental Revenue | Date | One date is connected to many rental revenue facts by Date. |
| Date | Fact AR Aging | Date | One date is connected to many AR aging facts by Date. |
| Date | Fact Cash Application | Date | One date is connected to many cash application facts by Date. |
| Date | Fact Credit Risk | Date | One date is connected to many credit risk facts by Date. |
| Customer | Fact AR Aging | Customer | One customer is connected to many AR aging fact records by Customer. |
| Customer | Fact Credit Risk | Customer | One customer is connected to many credit risk fact records by Customer. |
| Branch | Fact Rental Revenue | Branch | One branch is connected to many rental revenue fact records by Branch. |
| Branch | Fact Cash Application | Branch | One branch is connected to many cash application fact records by Branch. |
| Contract | Fact Rental Revenue | Contract | One contract is connected to many rental revenue fact records by Contract. |
| Invoice | Fact Cash Application | Invoice | One invoice is connected to many cash application fact records by Invoice. |
| Organization Hierarchy | Branch | Organization Hierarchy | One organization hierarchy is connected to many branches by organization hierarchy assignment. |

## 3. Key Design Decisions and Rationale
1. **Bronze mirroring in Silver:** The Silver model keeps the same core table structure as Bronze to preserve traceability while preparing the data for conformance and downstream analytics.
2. **Removal of keys and ID fields:** In accordance with the instruction, the logical model excludes primary keys, foreign keys, unique identifiers, and ID-style fields from the table definitions.
3. **Standardized data typing:** Mixed Bronze date/text structures are normalized into business-friendly Silver data types.
4. **Conformance readiness:** Customer, branch, and employee-related structures are retained to support deduplication, hierarchy alignment, and governed reporting.
5. **Validation support:** A dedicated error table and process audit table are included to satisfy the requirement to hold both data quality exceptions and pipeline execution audit information.
6. **Reconciliation and lineage support:** Source system, file path, and processing timestamps are preserved because AP-1 requires reconciliation and drill-through integrity to upstream facts.

## 4. Assumptions Based on Available Inputs
1. The Bronze logical model provided represents the complete available Bronze structure for this Silver design run.
2. Where the Jira ticket references business keys such as contract, customer, invoice, receipt, and branch, those relationships are documented conceptually because explicit ID fields are intentionally excluded from the logical model.
3. The Silver layer supports the downstream reporting domains described in AP-1, but the Gold fact implementation is outside the scope of this document.

## 5. apiCost
apiCost: 0.000000
