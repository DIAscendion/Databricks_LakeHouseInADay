_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Updated Silver layer logical data model for Rental Revenue-to-Cash reporting aligned to Jira ticket AP-1
## *Version*: 2
## *Updated on*: 
## *Changes*: Initial version 2 created by updating v1 baseline with Jira ticket AP-1 business reporting requirements and Silver-layer conformance expectations.
## *Reason*: Change based on Jira ticket AP-1.
_____________________________________________

# 1. Silver Layer Logical Model

## 1.1 Overview
1. This Silver logical model is derived from the conceptual model, constraints, Bronze logical model, and Jira ticket AP-1.
2. The Silver layer mirrors the Bronze table structure while removing primary key fields, foreign key fields, unique identifiers, and ID fields from the attribute inventory.
3. The Silver layer standardizes data types, preserves business attributes, supports data quality handling, and adds process audit tracking required for governed medallion architecture processing.
4. The Jira ticket AP-1 defines the Rental Revenue-to-Cash business context for revenue, billing, AR aging, cash application, and customer credit risk analytical reporting.

## 1.2 Silver Table: Si_Rental_Contracts
**Description:** Conformed Silver representation of rental contract data standardized from Bronze for downstream reporting on contract activity, rental days, billing context, and branch-level revenue analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Branch Code | String | Standardized branch code used to align contract reporting to branch and region rollups. |
| Equipment Class | String | Standardized equipment category used for rental revenue and mix analysis. |
| Contract Start Date | Date | Contract start date standardized from Bronze source values. |
| Contract End Date | Date | Contract end date standardized for duration and open exposure analysis. |
| Contract Status | String | Standardized contract lifecycle status such as Open or Closed. |
| Daily Rate | Decimal(18,2) | Daily rental charge associated with the contract. |
| Source System | String | Source application from which the contract data originated. |
| File Path | String | Source file lineage path retained for traceability. |
| File Modification Time | Timestamp | Source file modification timestamp used for ingestion lineage. |
| Load Timestamp | Timestamp | Timestamp when the record was loaded into the platform. |
| Update Timestamp | Timestamp | Timestamp when the record was last updated in the platform. |

## 1.3 Silver Table: Si_Invoices
**Description:** Conformed Silver representation of invoice and credit memo data used for billing, AR aging, and payment application analytics.

| Column Name | Data Type | Description |
|---|---|---|
| Invoice Date | Date | Billing date standardized from Bronze source values. |
| Due Date | Date | Due date used for payment timeliness and aging calculations. |
| Invoice Amount | Decimal(18,2) | Standardized billed amount for invoice analysis. |
| Tax Amount | Decimal(18,2) | Tax portion of the invoice transaction. |
| Invoice Type | String | Standardized transaction category such as standard invoice or credit memo. |
| Currency | String | Currency code associated with the invoice amount. |
| Source System | String | Source application from which the invoice data originated. |
| File Path | String | Source file lineage path retained for audit and traceability. |
| File Modification Time | Timestamp | Source file modification time captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the record entered the platform. |
| Update Timestamp | Timestamp | Timestamp when the invoice record was last updated. |

## 1.4 Silver Table: Si_Cash_Receipts
**Description:** Conformed Silver representation of payment and receipt data standardized for collections, cash application, and unapplied cash reporting.

| Column Name | Data Type | Description |
|---|---|---|
| Receipt Date | Date | Standardized payment receipt date. |
| Payment Amount | Decimal(18,2) | Non-negative payment amount recorded for collection analysis. |
| Payment Method | String | Standardized payment method such as ACH, check, card, or wire. |
| Source System | String | Originating payment source or lockbox feed. |
| File Path | String | Source file lineage path retained for auditability. |
| File Modification Time | Timestamp | Source file modification timestamp used for lineage. |
| Load Timestamp | Timestamp | Timestamp when the receipt record was loaded. |
| Update Timestamp | Timestamp | Timestamp when the receipt record was last updated. |

## 1.5 Silver Table: Si_Customer_Master
**Description:** Conformed Silver representation of customer master data used for AR, collections, and credit risk reporting after standardization and deduplication preparation.

| Column Name | Data Type | Description |
|---|---|---|
| Customer Name | String | Standardized customer business name used in reporting views. |
| Credit Terms | String | Standardized payment terms assigned to the customer. |
| Credit Limit | Decimal(18,2) | Non-negative approved credit exposure threshold for the customer. |
| Customer Since | Date | Start date of customer relationship standardized from source. |
| Customer Status | String | Standardized customer status such as Active or Suspended. |
| Source System | String | Originating CRM or ERP source of the customer record. |
| File Path | String | Source file lineage path retained for traceability. |
| File Modification Time | Timestamp | Source file modification timestamp captured during ingestion. |
| Load Timestamp | Timestamp | Timestamp when the customer record was loaded. |
| Update Timestamp | Timestamp | Timestamp when the customer record was last updated. |

## 1.6 Silver Table: Si_Branch_Employee
**Description:** Conformed Silver representation of employee assignment data supporting sales rep and collector reporting, branch rollups, and workforce-aligned analysis.

| Column Name | Data Type | Description |
|---|---|---|
| Employee Name | String | Standardized employee name used for operational reporting. |
| Role | String | Workforce role such as Sales Representative or Collector. |
| Branch Code | String | Standardized branch code assigned to the employee. |
| Region | String | Standardized region associated with the employee branch assignment. |
| Collector Assignment | String | Collector assignment attribute used for collection ownership analysis. |
| Effective Date | Date | Effective date of the employee assignment record. |
| Source System | String | Source application providing employee assignment data. |
| File Path | String | Source file lineage path retained for traceability. |
| File Modification Time | Timestamp | Source file modification timestamp captured for lineage. |
| Load Timestamp | Timestamp | Timestamp when the employee record was loaded. |
| Update Timestamp | Timestamp | Timestamp when the employee record was last updated. |

## 1.7 Silver Table: Si_Error_Data_Quality
**Description:** Silver error handling structure to store data quality validation failures, conformance issues, and rejected records detected during Silver processing.

| Column Name | Data Type | Description |
|---|---|---|
| Table Name | String | Name of the Silver table where the issue was detected. |
| Column Name | String | Column associated with the validation or quality failure. |
| Validation Rule | String | Business rule or constraint evaluated during processing. |
| Error Message | String | Detailed error message describing the failure. |
| Error Category | String | Classification of the issue such as completeness, accuracy, format, or referential integrity. |
| Source System | String | Source system from which the failed data originated. |
| File Path | String | Lineage reference for the source file associated with the issue. |
| Detected Timestamp | Timestamp | Timestamp when the issue was detected in processing. |
| Processing Status | String | Status of the failed record such as quarantined, rejected, or reviewed. |

## 1.8 Silver Table: Si_Process_Audit
**Description:** Silver process audit structure to track pipeline execution, transformation status, lineage, and operational metrics for the Silver layer.

| Column Name | Data Type | Description |
|---|---|---|
| Process Name | String | Name of the Silver transformation or pipeline step executed. |
| Source Table | String | Bronze source table processed by the pipeline step. |
| Target Table | String | Silver target table produced or updated by the process. |
| Load Timestamp | Timestamp | Timestamp when the Silver processing step executed. |
| Processed By | String | Service, job, or user responsible for the pipeline execution. |
| Processing Time | Decimal(18,2) | Elapsed execution time for the processing step. |
| Status | String | Processing result such as success, failed, warning, or reprocessed. |
| Records Read | Integer | Number of input records read by the pipeline. |
| Records Written | Integer | Number of records successfully written to Silver. |
| Records Rejected | Integer | Number of records rejected or quarantined during processing. |

# 2. Data Type Standardization and Silver Conformance Rules

1. `Date/Text` fields from Bronze are standardized to `Date` where business dates are expected.
2. Monetary and rate-bearing numeric fields are standardized to `Decimal(18,2)`.
3. Descriptive attributes are standardized to `String`.
4. Audit and lineage timestamps are standardized to `Timestamp`.
5. The Silver layer excludes primary key, foreign key, unique identifier, and ID fields from the published logical model.
6. Standardized business values should align to constraints from the provided files, including:
   1. Customer Status values such as `Active` and `Suspended`.
   2. Contract Status values such as `Open` and `Closed`.
   3. Aging bucket values restricted to `0-30`, `31-60`, `61-90`, and `90+` in downstream conformed analytical use.
   4. Payment amounts and credit limits must be non-negative.
   5. Credit memo amounts must remain negative where represented in analytical derivations.

# 3. Data Constraints Applied to Silver Layer

1. Branch must exist in the organization hierarchy and be active for the selected date.
2. Invoice amounts must tie to a valid contract after Silver conformance.
3. Every outstanding invoice must map to a valid customer after conformance.
4. Duplicate customer records representing the same legal entity must be resolved before customer exposure aggregation.
5. Net billings must reconcile to gross billings minus credit memos in downstream analytical calculations.
6. Aging bucket totals must reconcile to Total AR Outstanding in downstream reporting structures.
7. Applied payment amounts must not exceed the related invoice amount.
8. Unapplied cash must be retained and reported separately.
9. Rate-based calculations such as DSO, CEI, AR 90+ %, and Credit Utilization % must only be calculated when the required denominator is non-zero.
10. Health score must remain within the range of 0 to 100 in downstream scorecard structures derived from Silver.

# 4. Conceptual Data Model Diagram in Tabular Form

| Source Table | Relationship Key Field | Target Table | Relationship Type | Description |
|---|---|---|---|---|
| Region | Region | Branch | One-to-Many | One region contains many branches. |
| Branch | Branch Code | Si_Rental_Contracts | One-to-Many | One branch can have many rental contracts. |
| Customer | Customer | Si_Rental_Contracts | One-to-Many | One customer can be associated with many contracts. |
| Si_Rental_Contracts | Contract reference | Si_Invoices | One-to-Many | One contract can produce many invoices. |
| Customer | Customer | Si_Invoices | One-to-Many | One customer can have many invoices. |
| Si_Invoices | Invoice reference | Si_Cash_Receipts | One-to-Many | One invoice can be linked to many payment applications or receipts. |
| Customer | Customer | Si_Cash_Receipts | One-to-Many | One customer can have multiple receipts. |
| Branch | Branch Code | Si_Branch_Employee | One-to-Many | One branch can have many employee assignment records. |
| Region | Region | Si_Branch_Employee | One-to-Many | One region can include many employee assignments through branches. |
| Collector | Collector Assignment | Customer | One-to-Many | One collector can manage many customers. |
| Date | Date | Revenue reporting views | One-to-Many | Reporting dates connect to revenue analytics. |
| Date | Snapshot Date | AR aging reporting views | One-to-Many | Snapshot dates connect to AR aging analytics. |
| Date | Date | Cash application reporting views | One-to-Many | Reporting dates connect to collections analytics. |
| Date | Snapshot Date | Credit risk reporting views | One-to-Many | Snapshot dates connect to credit risk analytics. |

# 5. Cross-Layer Relationships

1. **Bronze to Silver Table Mapping**
   1. `Bz_Rental_Contracts` -> `Si_Rental_Contracts`
   2. `Bz_Invoices` -> `Si_Invoices`
   3. `Bz_Cash_Receipts` -> `Si_Cash_Receipts`
   4. `Bz_Customer_Master` -> `Si_Customer_Master`
   5. `Bz_Branch_Employee` -> `Si_Branch_Employee`
2. **Business Relationship Notes**
   1. Contracts provide the operational basis for branch, equipment class, and rental performance reporting.
   2. Invoices support billing, AR aging, and payment matching analytics.
   3. Cash receipts support cash application, unapplied cash, and collector performance analytics.
   4. Customer master data supports conformed customer reporting, customer status analysis, and credit risk monitoring.
   5. Employee assignment data supports sales rep and collector drill-down reporting.

# 6. Key Design Decisions and Rationale

1. The Silver layer mirrors the Bronze structure exactly at table level as instructed.
2. Primary key fields, foreign key fields, unique identifiers, and ID fields are excluded from the Silver logical model output.
3. Additional Silver tables are included for error handling and process audit support to satisfy data quality and operational governance requirements.
4. Data types are standardized to improve downstream consistency and reduce schema variability inherited from Bronze.
5. File lineage, source system, and load/update timestamps are retained to support traceability and auditability.
6. Customer data is prepared for deduplication because the constraints require a single conformed customer record for exposure reporting.
7. The model supports downstream Rental Revenue-to-Cash reporting themes explicitly described in Jira ticket AP-1, including revenue, AR aging, collections, cash application, and credit risk domains.

# 7. Assumptions

1. The update request is to create version 2 using the provided AP-1 Jira business requirements as the required change context.
2. No additional user-provided change text beyond the Jira ticket context was supplied.
3. Where conceptual relationships reference keys, the relationship key field is documented at business level because ID fields are not included in the logical attribute inventory.
4. Silver analytical derivations such as health score, DSO, CEI, AR 90+ %, and Credit Utilization % are supported by conformed Silver structures but may be implemented downstream in Gold reporting facts.

# 8. apiCost

apiCost: 0.000000
