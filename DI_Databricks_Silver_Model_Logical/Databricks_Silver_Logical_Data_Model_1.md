_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Logical Silver layer model for Rental Revenue-to-Cash standardized, validated, and audit-ready data structures
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Data Model

## 1.1 Summary
The Silver layer logical data model for Rental Revenue-to-Cash standardizes Bronze layer data, applies data quality and validation-ready structures, removes primary key, foreign key, unique identifier, and ID fields, and prepares conformed analytical structures for downstream reporting in a medallion architecture.

## 1.2 Source Inputs Reviewed
| No. | Input Type | File | Purpose |
|---|---|---|---|
| 1 | Conceptual Data Model | `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Provides business entities, attributes, KPIs, and conceptual relationships |
| 2 | Data Constraints | `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Provides data quality rules, mandatory fields, dependencies, and business rules |
| 3 | Bronze Logical Data Model | `DI_Databricks_Bronze_Model_Logical/Bronze_Model_Logical_1.md` | Provides source-aligned Bronze tables and logical attributes |

## 1.3 Silver Layer Design Rules Applied
1. The Silver layer mirrors the Bronze structure and retains all non-key, non-ID business fields.
2. Primary key fields, foreign key fields, unique identifiers, and ID fields are excluded from Silver output.
3. All Silver table names use the required `Si_` prefix.
4. Data types are standardized from Bronze mixed logical types into Silver conformed logical types.
5. Silver includes separate structures for data quality error handling and pipeline process audit tracking.
6. Column descriptions are written in business-friendly language.
7. Relationships are documented across conceptual, Bronze, and Silver views using the relationship key field names available in the inputs.
8. No new business entities beyond those inferable from the provided inputs are introduced, except required operational support tables for error and audit tracking explicitly requested.

## 1.4 Data Type Standardization Rules
| No. | Bronze Type Pattern | Silver Standard Type | Standardization Purpose |
|---|---|---|---|
| 1 | Text | String | Establishes a consistent string representation across conformed Silver tables |
| 2 | Date/Text | Date | Converts mixed-format date attributes into standardized reportable dates where valid |
| 3 | Decimal | Decimal(18,2) | Standardizes currency and amount precision for reporting calculations |
| 4 | Timestamp | Timestamp | Preserves ingestion and processing chronology |
| 5 | Derived categorical values | String | Ensures standard domain-controlled status and bucket values |

## 1.5 Silver Tables

### 1.5.1 Si_Rental_Contracts
**Description:** Standardized Silver representation of rental contract data prepared for contract, billing, revenue, and exposure analysis.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Branch Code | String | Standardized branch reference indicating where the rental contract was recorded. |
| 2 | Equipment Class | String | Standardized equipment category used for rental mix and billing analysis. |
| 3 | Contract Start Date | Date | Standardized contract start date used for contract lifecycle analysis. |
| 4 | Contract End Date | Date | Standardized contract end date used to determine contract duration and closure state. |
| 5 | Contract Status | String | Standardized business status of the contract such as Open or Closed. |
| 6 | Daily Rate | Decimal(18,2) | Standardized daily rental amount used in contract revenue analysis. |
| 7 | Source System | String | Source application from which the contract record originated. |
| 8 | File Path | String | Ingestion lineage reference indicating the source file or batch path. |
| 9 | File Modification Time | Timestamp | Source file modification timestamp used for lineage and replay support. |
| 10 | Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| 11 | Update Timestamp | Timestamp | Timestamp when the Silver record was last updated. |

### 1.5.2 Si_Invoices
**Description:** Standardized Silver representation of invoice and credit memo data prepared for billing, AR aging, and payment application analysis.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Invoice Date | Date | Standardized billing date of the invoice or credit memo transaction. |
| 2 | Due Date | Date | Standardized payment due date used for aging and delinquency analysis. |
| 3 | Invoice Amount | Decimal(18,2) | Standardized billed amount used for invoice, AR, and reconciliation analysis. |
| 4 | Tax Amount | Decimal(18,2) | Standardized tax component associated with the invoice transaction. |
| 5 | Invoice Type | String | Standardized transaction type such as standard invoice or credit memo. |
| 6 | Currency | String | Standardized currency code for financial reporting consistency. |
| 7 | Source System | String | Source application from which the invoice record originated. |
| 8 | File Path | String | Ingestion lineage reference indicating the source file or batch path. |
| 9 | File Modification Time | Timestamp | Source file modification timestamp captured for lineage and traceability. |
| 10 | Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| 11 | Update Timestamp | Timestamp | Timestamp when the Silver record was last updated. |

### 1.5.3 Si_Cash_Receipts
**Description:** Standardized Silver representation of payment receipt and cash activity prepared for cash application and collections analysis.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Receipt Date | Date | Standardized date on which payment was received. |
| 2 | Payment Amount | Decimal(18,2) | Standardized payment amount collected from the customer. |
| 3 | Payment Method | String | Standardized payment channel such as ACH, check, card, or wire. |
| 4 | Source System | String | Source application or payment feed from which the receipt originated. |
| 5 | File Path | String | Ingestion lineage reference indicating the source file or batch path. |
| 6 | File Modification Time | Timestamp | Source file modification timestamp used for operational traceability. |
| 7 | Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| 8 | Update Timestamp | Timestamp | Timestamp when the Silver record was last updated. |

### 1.5.4 Si_Customer_Master
**Description:** Standardized Silver representation of customer master data prepared for customer analytics, AR, and credit risk processing.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Customer Name | String | Standardized customer business name used across AR, cash application, and credit risk reporting. |
| 2 | Credit Terms | String | Standardized payment terms assigned to the customer. |
| 3 | Credit Limit | Decimal(18,2) | Standardized approved customer credit exposure threshold. |
| 4 | Customer Since | Date | Standardized date indicating when the customer relationship began. |
| 5 | Customer Status | String | Standardized customer lifecycle status such as Active or Suspended. |
| 6 | Source System | String | Source application from which the customer record originated. |
| 7 | File Path | String | Ingestion lineage reference indicating the source file or batch path. |
| 8 | File Modification Time | Timestamp | Source file modification timestamp used for lineage and source traceability. |
| 9 | Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| 10 | Update Timestamp | Timestamp | Timestamp when the Silver record was last updated. |

### 1.5.5 Si_Branch_Employee
**Description:** Standardized Silver representation of branch employee assignment data prepared for sales and collections performance analysis.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Employee Name | String | Standardized employee name associated with sales or collection responsibilities. |
| 2 | Role | String | Standardized employee role such as Sales Representative or Collector. |
| 3 | Branch Code | String | Standardized branch assignment for the employee. |
| 4 | Region | String | Standardized regional assignment linked to the employee's branch. |
| 5 | Collector Assignment | String | Standardized collector responsibility reference used in collection reporting. |
| 6 | Effective Date | Date | Standardized effective date of the employee assignment record. |
| 7 | Source System | String | Source application from which the employee record originated. |
| 8 | File Path | String | Ingestion lineage reference indicating the source file or batch path. |
| 9 | File Modification Time | Timestamp | Source file modification timestamp used for traceability. |
| 10 | Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| 11 | Update Timestamp | Timestamp | Timestamp when the Silver record was last updated. |

### 1.5.6 Si_Data_Quality_Errors
**Description:** Silver operational table used to hold rejected, invalid, or rule-violating records identified during data quality validation and standardization.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Source Table | String | Name of the source Silver table from which the invalid record originated. |
| 2 | Source File Path | String | File or batch path associated with the invalid record. |
| 3 | Validation Rule Name | String | Name of the validation or business rule that failed. |
| 4 | Validation Category | String | Category of validation such as completeness, format, accuracy, or referential integrity. |
| 5 | Error Description | String | Human-readable description of the data quality issue detected. |
| 6 | Error Record Payload | String | Serialized representation of the failed record retained for remediation. |
| 7 | Error Severity | String | Severity level such as Warning, Error, or Critical. |
| 8 | Detected Timestamp | Timestamp | Timestamp when the error was detected in Silver processing. |
| 9 | Processing Status | String | Remediation status such as Open, Resolved, Reprocessed, or Rejected. |

### 1.5.7 Si_Process_Audit
**Description:** Silver operational table used to track pipeline execution, processing metrics, and audit trail information for Silver transformations.

| No. | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | Pipeline Name | String | Name of the pipeline or job executing Silver transformations. |
| 2 | Source Table | String | Source table processed by the pipeline step. |
| 3 | Target Table | String | Silver target table produced by the pipeline step. |
| 4 | Process Start Timestamp | Timestamp | Timestamp when processing started. |
| 5 | Process End Timestamp | Timestamp | Timestamp when processing completed. |
| 6 | Processing Status | String | Final execution status such as Success, Failed, Partial Success, or Reprocessed. |
| 7 | Records Read Count | Decimal(18,0) | Number of records read from the source during execution. |
| 8 | Records Written Count | Decimal(18,0) | Number of records successfully written to the Silver target. |
| 9 | Records Rejected Count | Decimal(18,0) | Number of rejected records diverted to error handling. |
| 10 | Processing Duration Seconds | Decimal(18,2) | Total elapsed processing time in seconds. |
| 11 | Executed By | String | User, service principal, or orchestration process that executed the pipeline. |
| 12 | Audit Remarks | String | Additional audit comments or execution observations. |

# 2. Constraint Alignment and Validation Readiness

## 2.1 Mandatory Field Coverage
| No. | Constraint Field | Silver Table | Handling in Silver |
|---|---|---|---|
| 1 | Branch Name / Branch context | Si_Rental_Contracts, Si_Branch_Employee | Preserved through standardized branch attributes for branch-level reporting support |
| 2 | Region | Si_Branch_Employee | Preserved for regional rollup and reporting consistency |
| 3 | Date / Snapshot Date | Si_Rental_Contracts, Si_Invoices, Si_Cash_Receipts, Si_Branch_Employee, Si_Customer_Master | Standardized into Date fields for reporting consistency |
| 4 | Customer Name | Si_Customer_Master | Preserved as mandatory customer business attribute |
| 5 | Contract Status | Si_Rental_Contracts | Preserved and standardized for open or closed contract reporting |
| 6 | Invoice Amount | Si_Invoices | Preserved with standardized decimal precision |
| 7 | Due Date | Si_Invoices | Preserved as standardized date for aging logic |
| 8 | Payment Amount | Si_Cash_Receipts | Preserved with standardized decimal precision |
| 9 | Credit Limit | Si_Customer_Master | Preserved with standardized decimal precision |
| 10 | Customer Status | Si_Customer_Master | Preserved as standardized domain value |

## 2.2 Key Validation Rules Reflected in Silver
1. Net billings must reconcile to gross billings minus credit memos in downstream analytical processing.
2. Aging bucket values must be limited to the defined categories `0-30`, `31-60`, `61-90`, and `90+` where derived.
3. Customer status values must align to expected domain values such as `Active` and `Suspended`.
4. Contract status values must align to expected domain values such as `Open` and `Closed`.
5. Payment and invoice reporting must explicitly support applied and unapplied distinctions in downstream processing.
6. Non-zero denominator rules must be enforced for rate-based KPI calculations in downstream layers.
7. Duplicate customer records should be resolved during Silver processing before Gold-layer exposure aggregation.
8. Invalid or nonconforming records should be routed to `Si_Data_Quality_Errors`.
9. Pipeline execution outcomes should be tracked in `Si_Process_Audit`.

# 3. Conceptual Data Model Diagram in Tabular Form

| No. | Source Layer/Table | Relationship Key Field | Target Layer/Table | Relationship Type | Relationship Description |
|---|---|---|---|---|---|
| 1 | Conceptual Region | Region | Conceptual Branch | One-to-Many | One region is connected to many branches by the Region field. |
| 2 | Conceptual Branch | Branch | Conceptual Contract | One-to-Many | One branch is connected to many contracts by the Branch field. |
| 3 | Conceptual Customer | Customer | Conceptual Contract | One-to-Many | One customer is connected to many contracts by the Customer field. |
| 4 | Conceptual Customer | Customer | Conceptual Invoice | One-to-Many | One customer is connected to many invoices by the Customer field. |
| 5 | Conceptual Collector | Collector Assignment | Conceptual Customer | One-to-Many | One collector assignment is connected to many customers by the Collector Assignment field. |
| 6 | Conceptual Contract | Contract | Conceptual Invoice | One-to-Many | One contract is connected to many invoices by the Contract field. |
| 7 | Conceptual Invoice | Invoice to Payment Application | Conceptual Cash Receipt | One-to-Many | One invoice is connected to many cash receipts by the Invoice to Payment Application field. |
| 8 | Bronze Bz_Customer_Master | Customer reference | Bronze Bz_Rental_Contracts | One-to-Many | One customer is connected to many rental contracts by the Customer reference field. |
| 9 | Bronze Bz_Rental_Contracts | Contract reference | Bronze Bz_Invoices | One-to-Many | One rental contract is connected to many invoices by the Contract reference field. |
| 10 | Bronze Bz_Customer_Master | Customer reference | Bronze Bz_Invoices | One-to-Many | One customer is connected to many invoices by the Customer reference field. |
| 11 | Bronze Bz_Customer_Master | Customer reference | Bronze Bz_Cash_Receipts | One-to-Many | One customer is connected to many cash receipts by the Customer reference field. |
| 12 | Bronze Bz_Invoices | Invoice reference | Bronze Bz_Cash_Receipts | One-to-Many | One invoice is connected to many cash receipts by the Invoice reference field. |
| 13 | Bronze Bz_Branch_Employee | Branch Code | Bronze Bz_Rental_Contracts | One-to-Many | One branch assignment is connected to many rental contracts by the Branch Code field. |
| 14 | Bronze Bz_Branch_Employee | Region | Bronze Bz_Rental_Contracts | One-to-Many | One region assignment is connected to many rental contracts by the Region field. |
| 15 | Silver Si_Customer_Master | Customer Name | Silver Si_Rental_Contracts | One-to-Many inferred | Customer-oriented contract analysis is supported after Silver conformance using customer business context. |
| 16 | Silver Si_Rental_Contracts | Contract Status / Branch Code | Silver Si_Invoices | One-to-Many inferred | Contract and billing analysis is aligned through standardized operational business context. |
| 17 | Silver Si_Customer_Master | Customer Name | Silver Si_Invoices | One-to-Many inferred | Customer billing analysis is supported through conformed customer context. |
| 18 | Silver Si_Customer_Master | Customer Name | Silver Si_Cash_Receipts | One-to-Many inferred | Customer payment analysis is supported through conformed customer context. |
| 19 | Silver Si_Branch_Employee | Branch Code | Silver Si_Rental_Contracts | One-to-Many | Branch employee assignments connect to contract activity by Branch Code. |
| 20 | Silver Si_Branch_Employee | Region | Silver Si_Rental_Contracts | One-to-Many | Regional assignments connect to contract activity by Region. |

# 4. Cross-Layer Relationship Mapping

| No. | Bronze Table | Silver Table | Mapping Basis | Notes |
|---|---|---|---|---|
| 1 | Bz_Rental_Contracts | Si_Rental_Contracts | Direct structural mirror excluding keys and IDs | Data types standardized from Text/Date-Text/Decimal into conformed Silver types |
| 2 | Bz_Invoices | Si_Invoices | Direct structural mirror excluding keys and IDs | Supports billing, AR, and payment-related downstream logic |
| 3 | Bz_Cash_Receipts | Si_Cash_Receipts | Direct structural mirror excluding keys and IDs | Supports cash application and collection reporting |
| 4 | Bz_Customer_Master | Si_Customer_Master | Direct structural mirror excluding keys and IDs | Supports customer, AR, and credit risk processing |
| 5 | Bz_Branch_Employee | Si_Branch_Employee | Direct structural mirror excluding keys and IDs | Supports sales and collector assignment analytics |
| 6 | Not applicable | Si_Data_Quality_Errors | Required Silver operational support structure | Added for rejected record storage and rule failure tracking |
| 7 | Bz_Audit_Processing | Si_Process_Audit | Silver audit extension based on Bronze audit intent | Expanded to capture pipeline execution metrics and status |

# 5. Design Decisions and Rationale

1. **Bronze mirroring with controlled refinement:** The Silver model closely mirrors Bronze tables to preserve traceability while standardizing datatypes and preparing conformed analytical inputs.
2. **Removal of keys and identifiers:** Primary keys, foreign keys, unique identifiers, and ID-style fields are excluded to comply with the stated modeling rule.
3. **Standardized naming convention:** Every Silver table begins with `Si_` to align with medallion architecture naming standards.
4. **Support for data quality operations:** `Si_Data_Quality_Errors` is included to store invalid or rejected records detected during transformation and validation.
5. **Support for auditability:** `Si_Process_Audit` is included to capture execution metadata, record counts, status, and duration for operational governance.
6. **Data type harmonization:** Mixed Bronze `Date/Text` fields are standardized to `Date` in Silver wherever business dates are intended.
7. **Constraint-aware design:** Mandatory fields and key business rule dependencies from the constraints document are reflected in the Silver structure and validation-readiness notes.
8. **Business-friendly documentation:** All columns include short descriptions to support engineering, governance, and implementation teams.

# 6. Assumptions

1. Date fields represented as `Date/Text` in Bronze are expected to be parsable into valid dates during Silver processing.
2. Business relationships that rely on hidden key fields remain documented using the relationship key field names present in the conceptual and Bronze documents.
3. Duplicate customer resolution is expected as part of Silver processing logic even though deduplication fields are not explicitly shown in the logical attribute inventory.
4. Applied and unapplied payment distinctions may be implemented through downstream derived logic using standardized Silver structures.
5. Silver remains a conformed and validated layer and does not yet introduce the full Gold fact and KPI aggregation structures.

# 7. apiCost
apiCost: 0.000000
