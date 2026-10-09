_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Logical Bronze layer model for Rental Revenue-to-Cash source structures and compliance-ready ingestion design
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Bronze Model Logical

## 1. Summary
This document defines the logical Bronze layer model for the Rental Revenue-to-Cash domain. It mirrors the provided source structures from the conceptual model and Bronze schema, preserves raw source attributes except key fields, adds required ingestion metadata, identifies PII under GDPR-style compliance guidance, and documents logical relationships and audit design for traceable Lakehouse ingestion.

## 2. Source Inputs Reviewed
| Input Type | File | Purpose |
|---|---|---|
| Conceptual Model | `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Provides business entities, attributes, KPIs, and conceptual relationships |
| Bronze Schema | `Input/rental_revenue_to_cash_bronze_schema.sql` | Provides source-aligned Bronze tables, grains, and raw attributes |

## 3. Design Assumptions and Logical Rules
- The Bronze layer mirrors the source data structure as closely as possible.
- All source tables from the SQL schema are included in the Bronze logical model.
- Primary key and foreign key style identifier columns are excluded from the logical attribute listings as instructed.
- Physical names ending in `_id` are not used as business attributes in the model.
- Table names use the required `Bz_` prefix.
- Required metadata columns `load_timestamp`, `update_timestamp`, and `source_system` are included in each Bronze table.
- Existing raw lineage fields from source extracts such as file path and file modification time are preserved where present because they are part of the source-aligned Bronze ingestion design.
- Data types are expressed as logical data types only, not storage engine-specific physical types.
- Relationships are documented conceptually because key identifiers are excluded from the logical attribute inventory.
- PII classification is limited to what can be directly inferred from the provided conceptual model and SQL schema.

## 4. PII Classification
| Table Name | Column Name | PII Classification | Reason why it is classified as PII |
|---|---|---|---|
| Bz_Customer_Master | Customer Name | Direct PII / Sensitive Business Identity | Customer name can identify an individual customer or sole proprietor and is treated as personally identifiable information under GDPR-style standards when it can directly identify a natural person. |
| Bz_Branch_Employee | Employee Name | Direct PII | Employee name directly identifies a person and must be handled as personal data. |
| Bz_Branch_Employee | Collector Assignment | Indirect PII / Workforce Data | Collector assignment links a worker to an operational responsibility and can reveal employee role associations tied to an identifiable person. |
| Bz_Rental_Contracts | Sales Representative Reference | Indirect PII | Even though identifier-style fields are excluded from the logical model, the business concept refers to an employee-linked attribute and is sensitive because it references an identifiable worker. |
| Bz_Branch_Employee | Branch | Potential Sensitive Organizational Association | Branch alone is not PII, but when combined with employee identity it can reveal work location and organizational placement. |
| Bz_Branch_Employee | Region | Potential Sensitive Organizational Association | Region combined with employee identity may disclose work assignment information. |

### PII Handling Notes
- No government identifiers, personal email addresses, personal phone numbers, or payment card details were present in the provided inputs.
- Customer financial exposure attributes such as credit limit are commercially sensitive, though not necessarily PII by themselves unless tied to an identifiable individual.
- Employee-related attributes should be access-controlled and masked where required in downstream consumption layers.

## 5. Bronze Layer Logical Model

### 5.1 Bz_Rental_Contracts
**Description:** Raw logical representation of rental contract header data received from branch and legacy rental systems. One record represents one rental contract extraction event.

| Column Name | Data Type | Business Description |
|---|---|---|
| Branch Code | Text | Branch where the rental contract was recorded in the source system. |
| Equipment Class | Text | Source-recorded equipment category associated with the rental contract. |
| Contract Start Date | Date/Text | Contract start date as received from the source, used to indicate when rental coverage begins. |
| Contract End Date | Date/Text | Contract end date as received from the source, may be blank or sentinel valued for open contracts. |
| Contract Status | Text | Current source-recorded status of the contract, such as open or closed. |
| Daily Rate | Decimal | Daily rental charge captured in the source system for the contract. |
| Source System | Text | Originating operational system from which the contract record was extracted. |
| File Path | Text | Source file or batch reference used for ingestion lineage. |
| File Modification Time | Timestamp | Source ingestion file write or modification time captured during landing. |
| Load Timestamp | Timestamp | Timestamp when the Bronze record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the Bronze record was last updated in the platform. |

### 5.2 Bz_Invoices
**Description:** Raw logical representation of invoice and credit memo header data received from branch and legacy billing systems. One record represents one invoice or credit memo extraction event.

| Column Name | Data Type | Business Description |
|---|---|---|
| Invoice Date | Date/Text | Billing date as received from the source system for the invoice or credit memo. |
| Due Date | Date/Text | Expected payment due date associated with the billed transaction. |
| Invoice Amount | Decimal | Total billed amount for the invoice record, including negative values for credit memos where applicable. |
| Tax Amount | Decimal | Tax portion recorded on the invoice transaction. |
| Invoice Type | Text | Business category of the invoice transaction, such as standard invoice or credit memo. |
| Currency | Text | Currency code in which the invoice amount is recorded. |
| Source System | Text | Originating operational system from which the invoice record was extracted. |
| File Path | Text | Source file or batch reference used for ingestion lineage. |
| File Modification Time | Timestamp | Source ingestion file write or modification time captured during landing. |
| Load Timestamp | Timestamp | Timestamp when the Bronze record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the Bronze record was last updated in the platform. |

### 5.3 Bz_Cash_Receipts
**Description:** Raw logical representation of payment receipt and cash application data received from the lockbox or accounts receivable payment feed. One record represents one payment or payment attempt extraction event.

| Column Name | Data Type | Business Description |
|---|---|---|
| Receipt Date | Date/Text | Payment receipt date as received from the source feed. |
| Payment Amount | Decimal | Total amount collected in the payment record. |
| Payment Method | Text | Method used to make the payment, such as ACH, check, card, or wire. |
| Source System | Text | Originating payment source or lockbox feed from which the record was extracted. |
| File Path | Text | Source file or batch reference used for ingestion lineage. |
| File Modification Time | Timestamp | Source ingestion file write or modification time captured during landing. |
| Load Timestamp | Timestamp | Timestamp when the Bronze record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the Bronze record was last updated in the platform. |

### 5.4 Bz_Customer_Master
**Description:** Raw logical representation of customer master data received from CRM or ERP customer sources. One record represents one customer record as extracted, without deduplication.

| Column Name | Data Type | Business Description |
|---|---|---|
| Customer Name | Text | Legal or trade name of the customer as recorded in the source system. |
| Credit Terms | Text | Agreed payment terms assigned to the customer account, such as Net 30. |
| Credit Limit | Decimal | Approved credit exposure threshold assigned to the customer. |
| Customer Since | Date/Text | Date indicating when the customer relationship began, as received from source. |
| Customer Status | Text | Operational status of the customer account, such as active or suspended. |
| Source System | Text | Originating CRM or ERP system from which the customer record was extracted. |
| File Path | Text | Source file or batch reference used for ingestion lineage. |
| File Modification Time | Timestamp | Source ingestion file write or modification time captured during landing. |
| Load Timestamp | Timestamp | Timestamp when the Bronze record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the Bronze record was last updated in the platform. |

### 5.5 Bz_Branch_Employee
**Description:** Raw logical representation of employee assignment data for sales representatives and collectors received from HR-related feeds. One record represents one employee feed record per effective extract.

| Column Name | Data Type | Business Description |
|---|---|---|
| Employee Name | Text | Name of the employee associated with sales or collections responsibilities. |
| Role | Text | Employee role classification, such as Sales Representative or Collector. |
| Branch Code | Text | Branch to which the employee is assigned in the source feed. |
| Region | Text | Region associated with the employee’s branch assignment as received from source. |
| Collector Assignment | Text | Collector reference associated with the employee assignment where provided by source. |
| Effective Date | Date/Text | Date from which the employee feed record is considered effective in the source. |
| Source System | Text | Originating HR or employee feed source from which the record was extracted. |
| File Path | Text | Source file or batch reference used for ingestion lineage. |
| File Modification Time | Timestamp | Source ingestion file write or modification time captured during landing. |
| Load Timestamp | Timestamp | Timestamp when the Bronze record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the Bronze record was last updated in the platform. |

## 6. Audit Table Design
**Audit Table Name:** `Bz_Audit_Processing`

**Description:** Tracks Bronze ingestion processing for each source record or batch event to support lineage, reconciliation, processing status, and audit readiness.

| Field | Data Type | Business Description |
|---|---|---|
| record_id | Text | Unique processing reference for the audited record or ingestion event. |
| source_table | Text | Source table or feed name from which the Bronze data originated. |
| load_timestamp | Timestamp | Timestamp when the record or batch was loaded into Bronze. |
| processed_by | Text | Process, job, user, or service principal that executed the ingestion. |
| processing_time | Decimal | Elapsed processing time for the ingestion event or record handling step. |
| status | Text | Processing outcome such as received, loaded, failed, quarantined, or reprocessed. |

## 7. Conceptual Data Model Diagram (Tabular Form)
| Source Table | Relationship Key Field | Target Table | Relationship Type | Logical Interpretation |
|---|---|---|---|---|
| Bz_Customer_Master | Customer reference | Bz_Rental_Contracts | One-to-Many | A customer can hold multiple rental contracts. |
| Bz_Branch_Employee | Branch Code | Bz_Rental_Contracts | One-to-Many | Employees and contract activity align through branch assignment. |
| Bz_Rental_Contracts | Contract reference | Bz_Invoices | One-to-Many | A rental contract can generate multiple invoices or credit memos. |
| Bz_Customer_Master | Customer reference | Bz_Invoices | One-to-Many | A customer can have multiple invoice records. |
| Bz_Customer_Master | Customer reference | Bz_Cash_Receipts | One-to-Many | A customer can have multiple receipts or payment events. |
| Bz_Invoices | Invoice reference | Bz_Cash_Receipts | One-to-Many | One invoice can be linked to multiple payment applications or receipt events. |
| Bz_Branch_Employee | Branch Code | Bz_Customer_Master | One-to-Many | Employees operate within branch structures serving customers associated to those branches in operations. |
| Bz_Branch_Employee | Region | Bz_Rental_Contracts | One-to-Many | Regional workforce assignments support rollup of contract activity. |

## 8. Key Design Decisions and Rationale
1. **Source mirroring approach:** The Bronze model preserves the source-oriented table breakdown from the SQL schema to support low-transformation ingestion and traceability.
2. **Exclusion of key identifiers:** Identifier columns were intentionally omitted from the logical attribute inventory to comply with the instruction to exclude primary and foreign keys and avoid physical `_ID` style naming.
3. **Metadata enrichment:** `load_timestamp`, `update_timestamp`, and `source_system` are included to support auditability, replay, and operational monitoring.
4. **Retention of file lineage fields:** File path and modification time remain in the logical model because the provided Bronze schema explicitly uses them for ingestion lineage.
5. **Business-friendly naming:** Attribute names are rendered in readable business form rather than physical SQL naming style.
6. **PII-aware handling:** Employee and customer naming fields are explicitly classified to support downstream masking and access control.
7. **No invented entities:** Only the five source tables present in the provided Bronze schema are modeled in the Bronze layer.

## 9. Constraints and Observations
- The conceptual model contains broader reporting entities and fact structures than the Bronze schema. This logical model includes only the source tables explicitly provided for Bronze.
- Some conceptual relationships rely on identifier fields that are intentionally not displayed in attribute inventories; therefore, relationships are documented at a business level.
- Raw date fields arrive in mixed formats according to the schema comments, so they are represented logically as `Date/Text` in Bronze.
- Data quality issues called out in the schema, such as duplicates, orphan references, and missing values, are preserved in Bronze and are not resolved here.

## 10. API Cost
apiCost: 0.000000
