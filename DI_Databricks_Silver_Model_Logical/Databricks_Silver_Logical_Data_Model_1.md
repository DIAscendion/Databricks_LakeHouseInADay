_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Silver layer logical data model for Rental Revenue-to-Cash reporting aligned to medallion architecture and reporting constraints
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Silver Layer Logical Model

## 1.1 Summary
1. This Silver layer logical data model is derived from the Jira ticket AP-1, the conceptual data model, the data constraints, and the Bronze logical model.
2. The Silver layer mirrors the Bronze structure while removing primary key fields, foreign key fields, unique identifiers, and ID fields.
3. The Silver layer standardizes data types, applies business-conformed naming, supports downstream Gold reporting, and introduces dedicated structures for data quality exceptions and processing audit data.
4. The Silver table naming convention uses the required `Si_` prefix.

## 1.2 Jira Business Context Used
1. **AP-1** - Reporting Requirements for Rental Revenue-to-Cash - Status: To Do
2. The ticket requires governed analytical support for revenue, billing, AR aging, cash application, collector performance, and customer credit risk reporting across branch and region rollups.
3. The ticket also requires controls for data quality, uniqueness by reporting grain, reconciliation, drill-through consistency, and secure branch/region aligned reporting.

## 1.3 Design Decisions and Rationale
1. **Bronze mirroring with controlled refinement:** All Bronze business fields are retained except primary key, foreign key, unique identifier, and ID fields, in line with the instructions.
2. **Data type standardization:** Mixed Bronze `Date/Text` fields are standardized into Silver business types such as `date`, `timestamp`, `decimal(18,2)`, and `string` wherever the available inputs support such standardization.
3. **Conformed descriptive naming:** Silver table names begin with `Si_` while keeping the same business meaning as Bronze.
4. **Data quality handling:** Separate error and audit tables are included to hold validation exceptions and pipeline execution information required by the task.
5. **No invented identifiers:** Relationships are documented using the relationship keys exactly at business level from the conceptual model and Bronze model context, while not introducing hidden ID columns into the table structures.
6. **Constraint alignment:** Silver structures support branch-region hierarchy consistency, customer conformance, AR aging bucket control, credit limit validation, unapplied cash reporting, and billing reconciliation.

## 1.4 Assumptions Inferred from Provided Inputs
1. The Bronze logical model is the direct source structure for the Silver logical model.
2. Where Bronze uses `Date/Text`, Silver standardizes to `date` when the attribute is clearly a calendar field and to `timestamp` for ingestion metadata.
3. Where Bronze uses financial measures, Silver standardizes to `decimal(18,2)`.
4. The conceptual and constraint documents define the reporting semantics and validation rules for downstream consumption.

## 1.5 Silver Tables

### 1.5.1 Si_Rental_Contracts
**Description:** Silver-conformed rental contract data for branch, equipment class, contract status, and rental duration analysis used in revenue and exposure reporting.

| Column Name | Data Type | Description |
|---|---|---|
| branch_code | string | Standardized branch code used to align rental contract reporting to branch and region rollups. |
| equipment_class | string | Standardized equipment category used for revenue mix and billing performance analysis. |
| contract_start_date | date | Contract start date standardized for period and contract lifecycle analysis. |
| contract_end_date | date | Contract end date standardized for open and closed contract reporting. |
| contract_status | string | Standardized contract status such as Open or Closed for billing and exposure analysis. |
| daily_rate | decimal(18,2) | Daily rental charge standardized for revenue-related calculations. |
| source_system | string | Originating source system for lineage and reconciliation. |
| file_path | string | Source file path retained for lineage and traceability. |
| file_modification_time | timestamp | Source file modification timestamp retained for ingestion traceability. |
| load_timestamp | timestamp | Timestamp when the Silver record was loaded. |
| update_timestamp | timestamp | Timestamp when the Silver record was last updated. |

### 1.5.2 Si_Invoices
**Description:** Silver-conformed invoice and credit memo data used for billing, AR aging, and payment application reporting.

| Column Name | Data Type | Description |
|---|---|---|
| invoice_date | date | Billing date standardized for revenue, AR, and trend reporting. |
| due_date | date | Due date standardized for aging and payment timeliness analysis. |
| invoice_amount | decimal(18,2) | Standardized invoice amount used for billing, AR, and reconciliation measures. |
| tax_amount | decimal(18,2) | Standardized tax amount recorded on the invoice transaction. |
| invoice_type | string | Standardized invoice classification such as standard invoice or credit memo. |
| currency | string | Currency code used for invoice reporting. |
| source_system | string | Originating source system for lineage and reconciliation. |
| file_path | string | Source file path retained for lineage and traceability. |
| file_modification_time | timestamp | Source file modification timestamp retained for ingestion traceability. |
| load_timestamp | timestamp | Timestamp when the Silver record was loaded. |
| update_timestamp | timestamp | Timestamp when the Silver record was last updated. |

### 1.5.3 Si_Cash_Receipts
**Description:** Silver-conformed cash receipt and payment application data used for collections, unapplied cash, and collector performance reporting.

| Column Name | Data Type | Description |
|---|---|---|
| receipt_date | date | Payment receipt date standardized for period analysis and payment reporting. |
| payment_amount | decimal(18,2) | Standardized payment amount used in cash collection and application reporting. |
| payment_method | string | Standardized payment method such as ACH, check, card, or wire. |
| source_system | string | Originating payment source for lineage and reconciliation. |
| file_path | string | Source file path retained for lineage and traceability. |
| file_modification_time | timestamp | Source file modification timestamp retained for ingestion traceability. |
| load_timestamp | timestamp | Timestamp when the Silver record was loaded. |
| update_timestamp | timestamp | Timestamp when the Silver record was last updated. |

### 1.5.4 Si_Customer_Master
**Description:** Silver-conformed customer data supporting AR, cash application, and credit risk reporting with conformed customer attributes.

| Column Name | Data Type | Description |
|---|---|---|
| customer_name | string | Standardized customer business name used in AR, credit, and cash application reporting. |
| credit_terms | string | Standardized agreed payment terms for customer collections analysis. |
| credit_limit | decimal(18,2) | Standardized customer credit limit used in utilization and over-limit reporting. |
| customer_since | date | Standardized customer start date used for tenure analysis. |
| customer_status | string | Standardized customer status such as Active or Suspended. |
| source_system | string | Originating source system for lineage and reconciliation. |
| file_path | string | Source file path retained for lineage and traceability. |
| file_modification_time | timestamp | Source file modification timestamp retained for ingestion traceability. |
| load_timestamp | timestamp | Timestamp when the Silver record was loaded. |
| update_timestamp | timestamp | Timestamp when the Silver record was last updated. |

### 1.5.5 Si_Branch_Employee
**Description:** Silver-conformed employee assignment data used for sales rep, collector, branch, and region aligned reporting.

| Column Name | Data Type | Description |
|---|---|---|
| employee_name | string | Standardized employee name used in sales and collection assignment reporting. |
| role | string | Standardized employee role such as Sales Representative or Collector. |
| branch_code | string | Standardized branch code for workforce alignment with branch reporting. |
| region | string | Standardized region value for organization rollups and security views. |
| collector_assignment | string | Collector assignment attribute used for collections responsibility analysis. |
| effective_date | date | Standardized effective date for employee assignment reporting. |
| source_system | string | Originating source system for lineage and reconciliation. |
| file_path | string | Source file path retained for lineage and traceability. |
| file_modification_time | timestamp | Source file modification timestamp retained for ingestion traceability. |
| load_timestamp | timestamp | Timestamp when the Silver record was loaded. |
| update_timestamp | timestamp | Timestamp when the Silver record was last updated. |

### 1.5.6 Si_Data_Quality_Error
**Description:** Silver error table to store records that fail data quality checks, business rule validations, or referential conformance checks.

| Column Name | Data Type | Description |
|---|---|---|
| source_table_name | string | Name of the Silver source table where the validation error occurred. |
| validation_rule_name | string | Name of the rule that failed such as aging bucket validation or payment amount validation. |
| error_category | string | High-level classification of the error such as completeness, accuracy, consistency, or referential integrity. |
| error_description | string | Business-readable explanation of the data quality issue. |
| offending_column_name | string | Column associated with the validation error. |
| offending_column_value | string | Value that caused the validation failure captured for investigation. |
| error_detected_timestamp | timestamp | Timestamp when the error was detected. |
| source_system | string | Source system from which the invalid record originated. |
| processing_status | string | Status of the error handling process such as open, reviewed, corrected, or rejected. |

### 1.5.7 Si_Process_Audit
**Description:** Silver audit table to track pipeline execution, processing status, and lineage for Silver data transformation runs.

| Column Name | Data Type | Description |
|---|---|---|
| pipeline_name | string | Name of the pipeline or process that loaded Silver data. |
| source_table_name | string | Source table processed in the transformation run. |
| target_table_name | string | Silver target table populated by the pipeline run. |
| process_start_timestamp | timestamp | Timestamp when the process started. |
| process_end_timestamp | timestamp | Timestamp when the process ended. |
| processing_status | string | Outcome of the process such as success, failed, partial_success, or reprocessed. |
| records_read_count | decimal(18,0) | Number of source records read during processing. |
| records_written_count | decimal(18,0) | Number of records written to the Silver target. |
| error_record_count | decimal(18,0) | Number of records redirected to the error table. |
| processed_by | string | User, service principal, or job name that executed the process. |

# 2. Data Type Standardization and Constraint Alignment

## 2.1 Standardization Rules
1. `Date/Text` in Bronze is standardized to `date` in Silver for business date fields.
2. File and processing time attributes are standardized to `timestamp`.
3. Monetary and rate-supporting numeric fields are standardized to `decimal(18,2)`.
4. Descriptive attributes are standardized to `string`.

## 2.2 Business Constraints Applied to Silver
1. Branch must exist in organization hierarchy and be active for the selected date.
2. Health score must remain between 0 and 100 when produced in downstream analytical layers.
3. Credit memo amounts must be negative and standard invoice amounts must be non-negative.
4. Payment amount must be non-negative.
5. Aging bucket values must use only 0-30, 31-60, 61-90, and 90+ in downstream derived datasets.
6. Duplicate customer records representing the same legal entity must be resolved before customer exposure aggregation.
7. Unapplied cash must be flagged and retained separately rather than excluded.
8. Applied payment amounts must not exceed the related invoice amount.
9. Revenue, AR, cash application, and credit risk views must use the same branch and region rollup structure.

# 3. Relationships Between Tables Across Layers

## 3.1 Bronze to Silver Mapping
| Bronze Table | Silver Table | Transformation Rule |
|---|---|---|
| Bz_Rental_Contracts | Si_Rental_Contracts | Retain all non-key business fields and standardize names and data types. |
| Bz_Invoices | Si_Invoices | Retain all non-key business fields and standardize names and data types. |
| Bz_Cash_Receipts | Si_Cash_Receipts | Retain all non-key business fields and standardize names and data types. |
| Bz_Customer_Master | Si_Customer_Master | Retain all non-key business fields and standardize names and data types. |
| Bz_Branch_Employee | Si_Branch_Employee | Retain all non-key business fields and standardize names and data types. |

## 3.2 Conceptual Relationship Model in Tabular Form
| Source Entity/Table | Relationship Key Field | Target Entity/Table | Relationship Type | Layer Interpretation |
|---|---|---|---|---|
| Region | Region | Branch | One-to-Many | Conceptual business hierarchy used for regional rollups and security views. |
| Branch | Branch | Contract | One-to-Many | A branch can have multiple contracts supporting revenue and exposure analysis. |
| Customer | Customer | Contract | One-to-Many | A customer can hold multiple rental contracts. |
| Customer | Customer | Invoice | One-to-Many | A customer can have multiple invoice records. |
| Sales Rep | Branch | Branch | Many-to-One | Sales representatives align to branch structures for performance reporting. |
| Collector | Branch | Branch | Many-to-One | Collectors align to branch structures for collections reporting. |
| Collector | Collector Assignment | Customer | One-to-Many | A collector can manage multiple customer collection assignments. |
| Contract | Contract | Invoice | One-to-Many | A contract can generate multiple invoices or credit memos. |
| Invoice | Invoice to Payment Application | Cash Receipt | One-to-Many | One invoice can link to multiple payment applications and a receipt may be unapplied. |
| Date | Date | Fact Rental Revenue | One-to-Many | Reporting date drives revenue fact analysis in downstream layers. |
| Date | Date | Fact AR Aging | One-to-Many | Reporting date drives AR aging snapshot analysis in downstream layers. |
| Date | Date | Fact Cash Application | One-to-Many | Reporting date drives cash application analysis in downstream layers. |
| Date | Date | Fact Credit Risk | One-to-Many | Reporting date drives credit risk snapshot analysis in downstream layers. |
| Customer | Customer | Fact AR Aging | One-to-Many | AR aging facts summarize receivable positions by customer. |
| Customer | Customer | Fact Credit Risk | One-to-Many | Credit risk facts summarize customer-level exposure. |
| Branch | Branch | Fact Rental Revenue | One-to-Many | Revenue facts roll up by branch and region. |
| Branch | Branch | Fact Cash Application | One-to-Many | Cash application facts roll up by branch and region. |
| Organization Hierarchy | Organization Hierarchy | Branch | One-to-Many | Organization hierarchy governs drill-down and security structure. |

# 4. Conceptual Data Model Diagram in Tabular Form

| Connected From | Connected To | Key Field Connecting Them | Explanation |
|---|---|---|---|
| Region | Branch | Region | Region is connected to Branch by Region for regional aggregation and rollup. |
| Branch | Contract | Branch | Branch is connected to Contract by Branch for branch-level contract and revenue analysis. |
| Customer | Contract | Customer | Customer is connected to Contract by Customer for customer contract tracking. |
| Customer | Invoice | Customer | Customer is connected to Invoice by Customer for billing and AR analysis. |
| Sales Rep | Branch | Branch | Sales Rep is connected to Branch by Branch for sales performance context. |
| Collector | Branch | Branch | Collector is connected to Branch by Branch for collections performance context. |
| Collector | Customer | Collector Assignment | Collector is connected to Customer by Collector Assignment for collections ownership. |
| Contract | Invoice | Contract | Contract is connected to Invoice by Contract for billing generation tracking. |
| Invoice | Cash Receipt | Invoice to Payment Application | Invoice is connected to Cash Receipt by Invoice to Payment Application for cash application tracking. |
| Date | Fact Rental Revenue | Date | Date is connected to Fact Rental Revenue by Date for revenue trend reporting. |
| Date | Fact AR Aging | Date | Date is connected to Fact AR Aging by Date for aging snapshot reporting. |
| Date | Fact Cash Application | Date | Date is connected to Fact Cash Application by Date for collections trend reporting. |
| Date | Fact Credit Risk | Date | Date is connected to Fact Credit Risk by Date for credit exposure trend reporting. |
| Customer | Fact AR Aging | Customer | Customer is connected to Fact AR Aging by Customer for AR analysis. |
| Customer | Fact Credit Risk | Customer | Customer is connected to Fact Credit Risk by Customer for risk exposure analysis. |
| Branch | Fact Rental Revenue | Branch | Branch is connected to Fact Rental Revenue by Branch for branch-level revenue reporting. |
| Branch | Fact Cash Application | Branch | Branch is connected to Fact Cash Application by Branch for branch-level collections reporting. |
| Organization Hierarchy | Branch | Organization Hierarchy | Organization Hierarchy is connected to Branch by Organization Hierarchy for governed drill paths and security. |

# 5. Reporting and Validation Support in Silver

## 5.1 Reporting Domains Supported
1. Revenue-to-Cash Executive Scorecard
2. Rental Revenue and Billing Performance
3. AR Aging and Collections
4. Cash Application and Collector Performance
5. Customer Credit Risk

## 5.2 Data Quality and Validation Coverage
1. Net billings reconcile to gross billings minus credit memos.
2. Aging bucket totals reconcile to total AR outstanding in downstream facts.
3. DSO and CEI denominator checks require non-zero denominators.
4. Duplicate reporting grains are prevented according to the constraints provided.
5. Branch and region rollups remain consistent across domains.
6. Drill-through totals must reconcile to source fact totals where specified in the Jira ticket and constraints.

# 6. apiCost
apiCost: 0.000000
