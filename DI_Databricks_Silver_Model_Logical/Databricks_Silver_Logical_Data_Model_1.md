_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Silver layer logical data model for standardized and validated Rental Revenue-to-Cash reporting entities.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Data Model

## 1.1 Summary
The Silver layer logical data model standardizes and validates the Rental Revenue-to-Cash data domain for downstream analytical use. It mirrors the Bronze data structure while removing primary key, foreign key, unique identifier, and ID-style fields from the logical inventory. The design applies data type standardization, preserves business-relevant attributes, and adds dedicated structures for data quality exceptions and process audit tracking in alignment with medallion architecture standards.

## 1.2 Source Inputs Reviewed
| Input Type | File | Purpose |
|---|---|---|
| Conceptual Model | `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Provides business entities, attributes, KPIs, and conceptual relationships |
| Data Constraints | `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Provides completeness, accuracy, format, consistency, and business rules |
| Bronze Logical Model | `DI_Databricks_Bronze_Model_Logical/Bronze_Model_Logical_1.md` | Provides Bronze-aligned logical source structures to be mirrored in Silver |

## 1.3 Silver Design Rules Applied
1. Bronze table structures are mirrored into Silver with a required `Si_` prefix.
2. Primary key, foreign key, unique identifier, and ID fields are excluded from the Silver logical column inventory.
3. All remaining Bronze business attributes are retained and standardized.
4. Mixed Bronze date fields represented as `Date/Text` are standardized to `Date` or `Timestamp` in Silver based on business meaning.
5. Textual categorical fields are standardized to `String`.
6. Numeric measures are standardized to `Decimal(18,2)` unless they represent elapsed duration or score-style values.
7. Silver includes one table for data quality and validation exceptions and one table for pipeline process audit tracking.
8. Silver preserves lineage-supporting fields needed for traceability and reconciliation.
9. Silver supports conformance and downstream reporting readiness without introducing unsupported new business entities.

## 1.4 Silver Tables

### 1.4.1 Si_Rental_Contracts
**Description:** Standardized Silver representation of rental contract data used for validated contract and billing readiness analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Branch Code | String | Standardized branch code identifying where the rental contract activity was recorded. |
| Equipment Class | String | Standardized equipment category associated with the rental contract. |
| Contract Start Date | Date | Standardized contract start date indicating when rental coverage begins. |
| Contract End Date | Date | Standardized contract end date indicating when rental coverage ends or is expected to end. |
| Contract Status | String | Standardized contract lifecycle status such as Open or Closed. |
| Daily Rate | Decimal(18,2) | Standardized daily rental charge associated with the contract. |
| Source System | String | Name of the originating operational source system. |
| File Path | String | Source file or batch reference retained for lineage tracking. |
| File Modification Time | Timestamp | Original source file modification timestamp captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the record was last updated in the platform. |

### 1.4.2 Si_Invoices
**Description:** Standardized Silver representation of invoice and credit memo data for billing, receivable, and cash application analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Invoice Date | Date | Standardized billing date for the invoice or credit memo transaction. |
| Due Date | Date | Standardized due date used for payment timeliness and aging analysis. |
| Invoice Amount | Decimal(18,2) | Standardized billed amount for the invoice transaction. |
| Tax Amount | Decimal(18,2) | Standardized tax amount associated with the invoice transaction. |
| Invoice Type | String | Standardized business type of transaction such as invoice or credit memo. |
| Currency | String | Standardized currency code for the monetary amounts. |
| Source System | String | Name of the originating billing or source transaction system. |
| File Path | String | Source file or batch reference retained for lineage tracking. |
| File Modification Time | Timestamp | Original source file modification timestamp captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the record was last updated in the platform. |

### 1.4.3 Si_Cash_Receipts
**Description:** Standardized Silver representation of payment receipt data for cash collection and application monitoring.

| Column Name | Data Type | Description |
|---|---|---|
| Receipt Date | Date | Standardized payment receipt date from the source payment feed. |
| Payment Amount | Decimal(18,2) | Standardized payment amount collected in the receipt record. |
| Payment Method | String | Standardized payment method such as ACH, check, card, or wire. |
| Source System | String | Name of the originating payment or lockbox source system. |
| File Path | String | Source file or batch reference retained for lineage tracking. |
| File Modification Time | Timestamp | Original source file modification timestamp captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the record was last updated in the platform. |

### 1.4.4 Si_Customer_Master
**Description:** Standardized Silver representation of customer master data used for conformed customer reporting and credit analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Customer Name | String | Standardized business name of the customer used in reporting and exposure analysis. |
| Credit Terms | String | Standardized agreed payment terms assigned to the customer. |
| Credit Limit | Decimal(18,2) | Standardized approved credit exposure threshold for the customer. |
| Customer Since | Date | Standardized date indicating when the customer relationship began. |
| Customer Status | String | Standardized operational customer status such as Active or Suspended. |
| Source System | String | Name of the originating customer master source system. |
| File Path | String | Source file or batch reference retained for lineage tracking. |
| File Modification Time | Timestamp | Original source file modification timestamp captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the record was last updated in the platform. |

### 1.4.5 Si_Branch_Employee
**Description:** Standardized Silver representation of branch employee assignment data for sales and collections reporting alignment.

| Column Name | Data Type | Description |
|---|---|---|
| Employee Name | String | Standardized name of the employee assigned to sales or collections responsibilities. |
| Role | String | Standardized employee role classification such as Sales Representative or Collector. |
| Branch Code | String | Standardized branch code to which the employee is assigned. |
| Region | String | Standardized regional assignment associated with the employee branch. |
| Collector Assignment | String | Standardized collector assignment reference used for collections responsibility analysis. |
| Effective Date | Date | Standardized effective date for the employee assignment record. |
| Source System | String | Name of the originating employee or HR source system. |
| File Path | String | Source file or batch reference retained for lineage tracking. |
| File Modification Time | Timestamp | Original source file modification timestamp captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the record was last updated in the platform. |

### 1.4.6 Si_Data_Quality_Exceptions
**Description:** Silver-layer exception structure used to capture records failing data quality checks, validation rules, referential checks, or standardization rules.

| Column Name | Data Type | Description |
|---|---|---|
| Table Name | String | Name of the Silver table where the validation issue occurred. |
| Column Name | String | Name of the column associated with the failed validation rule. |
| Validation Rule | String | Name or expression of the data quality rule that was evaluated. |
| Validation Status | String | Outcome of the validation such as Failed, Warning, or Quarantined. |
| Rejected Value | String | Value that failed validation or standardization checks. |
| Error Description | String | Business-readable explanation of the data quality issue. |
| Error Category | String | Category of issue such as Completeness, Accuracy, Format, Consistency, or Referential Integrity. |
| Source System | String | Originating source system for the rejected or flagged record. |
| File Path | String | File or batch reference associated with the issue for lineage and triage. |
| Detected Timestamp | Timestamp | Timestamp when the data quality issue was detected. |
| Load Timestamp | Timestamp | Timestamp when the exception record was written to Silver exception storage. |

### 1.4.7 Si_Process_Audit
**Description:** Silver-layer audit structure used to capture pipeline execution, processing outcomes, reconciliation status, and operational traceability.

| Column Name | Data Type | Description |
|---|---|---|
| Pipeline Name | String | Name of the pipeline or process that executed the Silver transformation. |
| Source Table | String | Name of the source or Bronze table processed by the pipeline. |
| Target Table | String | Name of the Silver table populated by the pipeline. |
| Process Start Timestamp | Timestamp | Timestamp when the processing step started. |
| Process End Timestamp | Timestamp | Timestamp when the processing step completed. |
| Processing Status | String | Final execution status such as Succeeded, Failed, Partially Succeeded, or Reprocessed. |
| Records Read | Decimal(18,0) | Total number of records read from the source or Bronze layer. |
| Records Written | Decimal(18,0) | Total number of records successfully written to the Silver table. |
| Records Rejected | Decimal(18,0) | Total number of records rejected into exception handling. |
| Processing Time Seconds | Decimal(18,2) | Elapsed execution time in seconds for the processing step. |
| Trigger Type | String | Execution trigger type such as Scheduled, Manual, or Event-Based. |
| Processed By | String | Name of the job, service principal, or process that executed the run. |
| Load Timestamp | Timestamp | Timestamp when the audit record was written. |

# 2. Conceptual Data Model Diagram in Tabular Form

| Source Table | Relationship Key Field | Target Table | Relationship Type | Cross-Layer Interpretation |
|---|---|---|---|---|
| Si_Customer_Master | Customer reference | Si_Rental_Contracts | One-to-Many | A customer can hold multiple rental contracts after customer conformance in Silver. |
| Si_Branch_Employee | Branch Code | Si_Rental_Contracts | One-to-Many | Branch employee assignments align to contract activity through branch code. |
| Si_Rental_Contracts | Contract reference | Si_Invoices | One-to-Many | A rental contract can generate multiple invoices or credit memo records. |
| Si_Customer_Master | Customer reference | Si_Invoices | One-to-Many | A customer can be associated with multiple invoice records. |
| Si_Customer_Master | Customer reference | Si_Cash_Receipts | One-to-Many | A customer can have multiple payment receipt records. |
| Si_Invoices | Invoice reference | Si_Cash_Receipts | One-to-Many | An invoice can be associated with one or more payment applications. |
| Si_Branch_Employee | Branch Code | Si_Customer_Master | One-to-Many | Employee branch assignments support customer reporting alignment by branch. |
| Si_Branch_Employee | Region | Si_Rental_Contracts | One-to-Many | Regional workforce alignment supports regional contract rollups. |
| Conceptual Region | Region | Si_Branch_Employee | One-to-Many | Conceptual region rolls down to employee branch-region assignments in Silver. |
| Conceptual Branch | Branch | Si_Rental_Contracts | One-to-Many | Conceptual branch reporting aligns to Silver rental contract records by branch code. |
| Conceptual Customer | Customer | Si_Customer_Master | One-to-One Logical Conformance | Conceptual customer entity is standardized into the Silver customer master table. |
| Conceptual Invoice | Invoice | Si_Invoices | One-to-One Logical Conformance | Conceptual invoice entity is standardized into the Silver invoice table. |
| Conceptual Cash Receipt | Invoice to Payment Application | Si_Cash_Receipts | One-to-Many | Conceptual receipt application logic is represented in standardized payment receipt records. |

# 3. Data Constraints Applied to Silver

## 3.1 Completeness Controls
1. Branch, region, and hierarchy-supporting attributes are retained for branch-level reporting alignment.
2. Date-related fields are standardized and required for time-based reporting.
3. Customer attributes are preserved for AR, cash application, and credit risk reporting.
4. Contract status, invoice amount, due date, payment amount, credit limit, and customer status are retained as mandatory analytical attributes.

## 3.2 Accuracy and Validation Controls
1. Net billings logic remains downstream dependent on gross billings and credit memos as defined in constraints.
2. Applied payment amount logic must not exceed related invoice amount and exceptions are captured in `Si_Data_Quality_Exceptions`.
3. Credit utilization and aging calculations depend on standardized monetary and date fields in Silver.
4. Duplicate customer issues are expected to be resolved during Silver processing using the conformed customer approach indicated by the constraints.

## 3.3 Format Standardization Controls
1. Date/Text Bronze fields are standardized into `Date` or `Timestamp` fields in Silver.
2. Aging bucket, customer status, contract status, and application status are expected to align to fixed business categories in downstream validated transformations.
3. Currency and payment method values are retained as standardized text attributes for controlled domains.

## 3.4 Consistency Controls
1. Branch and region rollups are preserved for reconciliation across revenue, AR, cash application, and credit risk reporting domains.
2. Shared source lineage attributes are retained across all Silver tables to support reconciliation and auditability.
3. A common audit structure and a common exception structure are added to ensure consistent operational monitoring.

# 4. Key Design Decisions and Rationale
1. **Bronze mirroring with Silver standardization:** The Silver model mirrors the Bronze table set exactly to preserve traceability, while applying standardized logical data types for analytics readiness.
2. **Removal of key and ID fields:** Primary keys, foreign keys, unique identifiers, and ID-style fields are intentionally excluded to comply with the stated modeling rule.
3. **Prefix-based naming standard:** All Silver business tables use the `Si_` prefix exactly as required for naming consistency.
4. **Data quality exception handling:** A dedicated exception table is included because the constraints explicitly require validation of completeness, accuracy, format, consistency, and referential integrity.
5. **Pipeline audit support:** A dedicated process audit table is included to capture execution and reconciliation metrics required for operational governance.
6. **Type standardization:** Silver converts mixed Bronze logical types into reusable standard types such as `String`, `Date`, `Timestamp`, and `Decimal(18,2)` to support reliable downstream transformations.
7. **Lineage preservation:** Source system, file path, and file modification time are retained because traceability and reconciliation are necessary across medallion layers.

# 5. Assumptions
1. The Bronze logical model provided is the authoritative source structure to mirror into Silver.
2. Relationship key fields are documented conceptually because explicit key and ID columns are excluded from the logical model output.
3. Data deduplication and business rule validation occur in Silver even where the exact physical implementation is not specified.
4. The Silver layer remains a conformed and validated version of Bronze and does not introduce unsupported fact tables beyond the provided source-aligned structures.

# 6. API Cost
apiCost: 0.000000
