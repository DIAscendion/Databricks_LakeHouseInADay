_____________________________________________
## *Author*: Ascendion AVA+
## *Created on*:   
## *Description*: Gold layer logical data model for Rental Revenue-to-Cash reporting, analytics, audit, and data quality monitoring.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Gold Layer Logical Model

## 1.1 Gold Layer Design Summary
1. The Gold layer is designed as a dimensional model for executive reporting, billing analysis, AR aging, cash application, and credit risk monitoring.
2. Transaction-oriented analytical tables are classified as Fact tables.
3. Descriptive and conformed business context tables are classified as Dimension tables.
4. Fixed reference value tables are classified as Code tables.
5. Audit and validation outcomes are stored in dedicated Process Audit and Error Data tables.
6. Aggregate tables are added to improve performance for common branch, region, period, collector, and customer reporting patterns.
7. All Gold tables follow the required naming convention beginning with `Go_`.
8. Primary key, foreign key, unique identifier, and explicit ID columns are intentionally excluded.
9. Physical identifier-style field names such as `_ID` are intentionally not included.
10. Metadata columns are included in all tables: `load_date`, `update_date`, and `source_system`.

## 1.2 Table Classification
1. **Fact Tables**
   1. `Go_Fact_Rental_Revenue`
   2. `Go_Fact_AR_Aging`
   3. `Go_Fact_Cash_Application`
   4. `Go_Fact_Credit_Risk`
2. **Dimension Tables**
   1. `Go_Dim_Date`
   2. `Go_Dim_Region`
   3. `Go_Dim_Branch`
   4. `Go_Dim_Customer`
   5. `Go_Dim_Sales_Rep`
   6. `Go_Dim_Collector`
   7. `Go_Dim_Equipment_Class`
   8. `Go_Dim_Contract`
   9. `Go_Dim_Invoice`
   10. `Go_Dim_Organization_Hierarchy`
3. **Code Tables**
   1. `Go_Code_Aging_Bucket`
   2. `Go_Code_Payment_Method`
   3. `Go_Code_Match_Status`
   4. `Go_Code_Customer_Status`
   5. `Go_Code_Contract_Status`
   6. `Go_Code_Period_Type`
4. **Audit and Error Tables**
   1. `Go_Audit_Process_Execution`
   2. `Go_Error_Data_Validation`
5. **Aggregated Tables**
   1. `Go_Agg_Revenue_Branch_Period`
   2. `Go_Agg_AR_Branch_Aging_Period`
   3. `Go_Agg_Cash_Collector_Period`
   4. `Go_Agg_Credit_Risk_Customer_Period`
   5. `Go_Agg_Executive_Health_Score`

## 1.3 Slowly Changing Dimension Strategy
1. `Go_Dim_Date` - **SCD Type 1** because calendar descriptors are static and corrections should overwrite.
2. `Go_Dim_Region` - **SCD Type 1** because region naming corrections should reflect the latest conformed structure.
3. `Go_Dim_Branch` - **SCD Type 2** because branch status and hierarchy assignment may change over time and require history.
4. `Go_Dim_Customer` - **SCD Type 2** because customer status, credit terms, and credit limit require historical tracking for risk analysis.
5. `Go_Dim_Sales_Rep` - **SCD Type 2** because rep-to-branch alignment may change and history supports performance reporting.
6. `Go_Dim_Collector` - **SCD Type 2** because collector assignment may change over time.
7. `Go_Dim_Equipment_Class` - **SCD Type 1** because descriptive category corrections do not require history.
8. `Go_Dim_Contract` - **SCD Type 2** because contract status and exposure indicators may change over time.
9. `Go_Dim_Invoice` - **SCD Type 1** because invoice descriptive corrections should be conformed to latest non-key descriptive state in Gold.
10. `Go_Dim_Organization_Hierarchy` - **SCD Type 2** because rollup structure changes must be historically traceable.

## 1.4 Detailed Table Definitions

### 1.4.1 `Go_Dim_Date`
- **Description**: Conformed reporting calendar dimension used across all Gold facts and aggregates.
- **Table Type**: Dimension
- **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| reporting_date | Business calendar date used for analysis and snapshot reporting | DATE | None |
| reporting_period | Reporting period label such as month or quarter | STRING | None |
| period_type | Reporting grain such as day, week, month, or quarter | STRING | None |
| number_of_days_in_period | Number of days in the reporting period used for DSO calculations | INT | None |
| fiscal_month_name | Fiscal month descriptor for finance reporting alignment | STRING | None |
| fiscal_quarter_name | Fiscal quarter descriptor for trend analysis | STRING | None |
| fiscal_year | Fiscal year value for annual reporting | INT | None |
| month_start_date | Start date of month for aggregation alignment | DATE | None |
| month_end_date | End date of month for aggregation alignment | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.2 `Go_Dim_Region`
- **Description**: Conformed regional dimension for network and regional rollup reporting.
- **Table Type**: Dimension
- **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| region_name | Name of the region used for aggregation and performance comparison | STRING | None |
| region_description | Business description of the regional reporting area | STRING | None |
| network_level | Highest organizational rollup level associated to the region | STRING | None |
| active_indicator | Indicates whether the region is active for reporting | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.3 `Go_Dim_Branch`
- **Description**: Conformed branch dimension supporting operational reporting, hierarchy rollups, and branch status history.
- **Table Type**: Dimension
- **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| branch_name | Name of the branch used in billing, AR, revenue, and cash analytics | STRING | None |
| branch_status | Indicates whether the branch is active for the reporting period | STRING | None |
| region_name | Region to which the branch is assigned | STRING | None |
| organization_hierarchy_name | Rollup path used for drill-down and security filtering | STRING | None |
| branch_open_date | Business effective start date for branch reporting | DATE | None |
| branch_close_date | Business effective close date if branch becomes inactive | DATE | None |
| current_record_indicator | Indicates the active current dimensional version | STRING | None |
| effective_start_date | Historical version start date for SCD tracking | DATE | None |
| effective_end_date | Historical version end date for SCD tracking | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.4 `Go_Dim_Customer`
- **Description**: Conformed customer dimension supporting AR, cash application, and credit risk analytics.
- **Table Type**: Dimension
- **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| customer_name | Business customer name used in receivable and risk reporting | STRING | Personal Data |
| customer_status | Current business status such as Active or Suspended | STRING | Personal Data |
| credit_terms | Agreed payment terms for the customer | STRING | Personal Data |
| credit_limit | Approved credit exposure threshold for the customer | DECIMAL(18,2) | Financial Sensitive |
| customer_since_date | Date indicating when the customer relationship began | DATE | Personal Data |
| collector_name | Collector currently responsible for the customer | STRING | Personal Data |
| sales_rep_name | Sales representative associated with the customer portfolio | STRING | Personal Data |
| conformed_customer_name | Standardized customer name after duplicate resolution | STRING | Personal Data |
| current_record_indicator | Indicates whether the row is the current customer version | STRING | None |
| effective_start_date | Historical version start date for SCD tracking | DATE | None |
| effective_end_date | Historical version end date for SCD tracking | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.5 `Go_Dim_Sales_Rep`
- **Description**: Sales representative dimension for branch and revenue performance analysis.
- **Table Type**: Dimension
- **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| sales_rep_name | Name of the sales representative associated with performance reporting | STRING | Personal Data |
| branch_name | Branch associated with the sales representative | STRING | None |
| region_name | Region associated with the sales representative | STRING | None |
| active_indicator | Indicates whether the representative is active | STRING | None |
| current_record_indicator | Indicates the current historical version | STRING | None |
| effective_start_date | Historical version start date for SCD tracking | DATE | None |
| effective_end_date | Historical version end date for SCD tracking | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.6 `Go_Dim_Collector`
- **Description**: Collector dimension used for collections and cash application performance reporting.
- **Table Type**: Dimension
- **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| collector_name | Name of the collector responsible for collection activity | STRING | Personal Data |
| branch_name | Branch associated with the collector | STRING | None |
| region_name | Region associated with the collector | STRING | None |
| active_indicator | Indicates whether the collector is active | STRING | None |
| current_record_indicator | Indicates the current historical version | STRING | None |
| effective_start_date | Historical version start date for SCD tracking | DATE | None |
| effective_end_date | Historical version end date for SCD tracking | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.7 `Go_Dim_Equipment_Class`
- **Description**: Equipment classification dimension used to analyze rental revenue mix.
- **Table Type**: Dimension
- **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| equipment_class_name | Equipment class category used for revenue and billing analysis | STRING | None |
| equipment_class_description | Business description of the equipment category | STRING | None |
| active_indicator | Indicates whether the class is active for reporting | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.8 `Go_Dim_Contract`
- **Description**: Contract dimension supporting exposure and billing context.
- **Table Type**: Dimension
- **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| contract_status | Indicates whether the contract is open or closed | STRING | None |
| customer_name | Customer associated with the contract | STRING | Personal Data |
| branch_name | Branch where the contract is managed | STRING | None |
| equipment_class_name | Equipment class associated with the contract | STRING | None |
| open_contract_count | Count of open contracts related to exposure analysis | INT | None |
| open_contract_value | Total open contract value used in exposure analysis | DECIMAL(18,2) | Financial Sensitive |
| total_billed_rental_days | Total billed rental duration used in ADR calculation | DECIMAL(18,2) | None |
| contract_start_date | Start date of contract lifecycle | DATE | None |
| contract_end_date | End date of contract lifecycle | DATE | None |
| current_record_indicator | Indicates the current historical version | STRING | None |
| effective_start_date | Historical version start date for SCD tracking | DATE | None |
| effective_end_date | Historical version end date for SCD tracking | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.9 `Go_Dim_Invoice`
- **Description**: Invoice dimension containing descriptive billing and due-date context used across AR and cash analytics.
- **Table Type**: Dimension
- **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| invoice_date | Date the invoice was issued | DATE | None |
| due_date | Date when payment is expected for the invoice | DATE | None |
| invoice_amount | Billed amount for the invoice | DECIMAL(18,2) | Financial Sensitive |
| gross_billings | Total billed amount before credits | DECIMAL(18,2) | Financial Sensitive |
| credit_memo_amount | Total credit memo adjustment amount | DECIMAL(18,2) | Financial Sensitive |
| net_billings | Net billings after credit memo deduction | DECIMAL(18,2) | Financial Sensitive |
| invoice_count | Count of invoices used in reporting aggregates | INT | None |
| days_past_due | Number of days invoice is past due relative to snapshot date | INT | None |
| aging_bucket | Standard aging category for the invoice | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.10 `Go_Dim_Organization_Hierarchy`
- **Description**: Conformed organization hierarchy dimension supporting drill-up, drill-down, and security filtering.
- **Table Type**: Dimension
- **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| organization_hierarchy_name | Name of the hierarchy used for reporting rollups | STRING | None |
| network_level | Highest organizational level used for enterprise reporting | STRING | None |
| region_name | Region associated with the hierarchy path | STRING | None |
| branch_name | Branch associated with the hierarchy path | STRING | None |
| hierarchy_status | Status of the hierarchy assignment | STRING | None |
| current_record_indicator | Indicates the current historical version | STRING | None |
| effective_start_date | Historical version start date for SCD tracking | DATE | None |
| effective_end_date | Historical version end date for SCD tracking | DATE | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.11 `Go_Code_Aging_Bucket`
- **Description**: Code table for valid AR aging buckets.
- **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| aging_bucket | Permitted aging bucket value such as 0-30, 31-60, 61-90, or 90+ | STRING | None |
| aging_bucket_description | Business meaning of the aging range | STRING | None |
| bucket_sequence | Sort order used in reports | INT | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.12 `Go_Code_Payment_Method`
- **Description**: Code table for standardized payment methods.
- **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| payment_method | Standard payment method value used for receipt analysis | STRING | None |
| payment_method_description | Business description of payment method | STRING | None |
| active_indicator | Indicates whether the payment method is active | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.13 `Go_Code_Match_Status`
- **Description**: Code table for applied and unapplied payment statuses.
- **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| match_status | Indicates whether a payment is applied, partially applied, or unapplied | STRING | None |
| match_status_description | Business description of the payment application state | STRING | None |
| active_indicator | Indicates whether the status is active | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.14 `Go_Code_Customer_Status`
- **Description**: Code table for standardized customer statuses.
- **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| customer_status | Standard customer status such as Active or Suspended | STRING | None |
| customer_status_description | Business meaning of the customer status | STRING | None |
| active_indicator | Indicates whether the code is active | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.15 `Go_Code_Contract_Status`
- **Description**: Code table for standardized contract statuses.
- **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| contract_status | Standard contract status such as Open or Closed | STRING | None |
| contract_status_description | Business meaning of the contract status | STRING | None |
| active_indicator | Indicates whether the code is active | STRING | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.16 `Go_Code_Period_Type`
- **Description**: Code table for supported reporting period grains.
- **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| period_type | Supported reporting grain such as day, week, month, or quarter | STRING | None |
| period_type_description | Business description of reporting grain | STRING | None |
| sort_order | Sort sequence used in report presentation | INT | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.17 `Go_Fact_Rental_Revenue`
- **Description**: Gold fact table holding rental revenue and billing analytics measures.
- **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| reporting_date | Reporting date for the revenue measure | DATE | None |
| branch_name | Branch associated with the revenue activity | STRING | None |
| region_name | Region associated with the revenue activity | STRING | None |
| sales_rep_name | Sales representative associated with the revenue activity | STRING | Personal Data |
| equipment_class_name | Equipment class contributing to the revenue | STRING | None |
| contract_status | Contract lifecycle status relevant to the revenue context | STRING | None |
| rental_revenue | Revenue recognized from rental business activity | DECIMAL(18,2) | Financial Sensitive |
| gross_billings | Total billing amount before credits | DECIMAL(18,2) | Financial Sensitive |
| credit_memo_amount | Total credit memo amount reducing billings | DECIMAL(18,2) | Financial Sensitive |
| net_billings | Net billing amount after credit adjustment | DECIMAL(18,2) | Financial Sensitive |
| credit_memo_rate | Ratio of credit memos to gross billings | DECIMAL(18,6) | None |
| average_daily_rate | Rental revenue divided by total billed rental days | DECIMAL(18,6) | None |
| revenue_per_contract | Average revenue earned per contract | DECIMAL(18,6) | None |
| trend_value | Period-over-period trend measure for revenue analysis | DECIMAL(18,6) | None |
| invoice_count | Number of invoices contributing to the measure | INT | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.18 `Go_Fact_AR_Aging`
- **Description**: Gold fact table holding point-in-time accounts receivable aging measures.
- **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| snapshot_date | Date at which AR aging is measured | DATE | None |
| branch_name | Branch associated with the receivable | STRING | None |
| region_name | Region associated with the receivable | STRING | None |
| collector_name | Collector responsible for collection activity | STRING | Personal Data |
| customer_name | Customer included in the AR aging position | STRING | Personal Data |
| aging_bucket | Aging classification assigned using due date and snapshot date | STRING | None |
| total_ar_outstanding | Total receivable amount outstanding at snapshot date | DECIMAL(18,2) | Financial Sensitive |
| ar_90_plus_amount | Receivable amount aged 90 days or more | DECIMAL(18,2) | Financial Sensitive |
| ar_90_plus_percentage | Percentage of total AR in the 90+ bucket | DECIMAL(18,6) | None |
| best_possible_dso | Best-achievable DSO benchmark | DECIMAL(18,6) | None |
| dso | Actual days sales outstanding measure | DECIMAL(18,6) | None |
| dso_trend | Period-over-period movement in DSO | DECIMAL(18,6) | None |
| aging_bucket_amount | Amount outstanding in the assigned aging bucket | DECIMAL(18,2) | Financial Sensitive |
| due_date | Due date used to derive aging bucket | DATE | None |
| days_past_due | Number of days overdue at snapshot time | INT | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.19 `Go_Fact_Cash_Application`
- **Description**: Gold fact table holding cash receipt and payment application analytics.
- **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| reporting_date | Reporting date for cash application analysis | DATE | None |
| branch_name | Branch associated with the receipt or collection | STRING | None |
| region_name | Region associated with the receipt or collection | STRING | None |
| collector_name | Collector responsible for collection outcome | STRING | Personal Data |
| customer_name | Customer associated with the payment | STRING | Personal Data |
| payment_method | Method used to make the payment | STRING | None |
| match_status | Applied or unapplied payment state | STRING | None |
| payment_date | Date on which payment was received | DATE | None |
| payment_amount | Amount collected in the receipt | DECIMAL(18,2) | Financial Sensitive |
| cash_collected | Total cash collected for the reporting grain | DECIMAL(18,2) | Financial Sensitive |
| collection_effectiveness_index | CEI measure for collection effectiveness | DECIMAL(18,6) | None |
| average_days_to_pay | Average elapsed days between invoice date and payment date | DECIMAL(18,6) | None |
| invoices_paid_on_time_percentage | Percentage of invoices settled by due date | DECIMAL(18,6) | None |
| unapplied_cash_amount | Payment amount not yet applied to invoices | DECIMAL(18,2) | Financial Sensitive |
| unapplied_cash_percentage | Percentage of payments that remain unapplied | DECIMAL(18,6) | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.20 `Go_Fact_Credit_Risk`
- **Description**: Gold fact table holding customer credit exposure and risk measures.
- **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| snapshot_date | Date at which credit risk is measured | DATE | None |
| branch_name | Branch associated with the customer exposure | STRING | None |
| region_name | Region associated with the customer exposure | STRING | None |
| customer_name | Customer subject to credit risk monitoring | STRING | Personal Data |
| customer_status | Status such as Active or Suspended used in risk logic | STRING | Personal Data |
| credit_terms | Agreed payment terms influencing customer risk interpretation | STRING | Personal Data |
| credit_limit | Approved credit limit for the customer | DECIMAL(18,2) | Financial Sensitive |
| outstanding_ar | Current accounts receivable exposure | DECIMAL(18,2) | Financial Sensitive |
| credit_utilization_percentage | Ratio of outstanding AR to credit limit | DECIMAL(18,6) | None |
| customers_over_limit_count | Count metric indicating over-limit customer condition | INT | None |
| customers_over_limit_amount | Amount exceeding approved customer credit limit | DECIMAL(18,2) | Financial Sensitive |
| suspended_customers_with_open_exposure | Indicator or count showing suspended customers with open AR or contracts | INT | None |
| ar_90_plus_amount_by_customer | Customer-level past-due amount aged 90 days or more | DECIMAL(18,2) | Financial Sensitive |
| open_contract_count | Count of open contracts contributing to exposure | INT | None |
| open_contract_value | Open contract value contributing to exposure | DECIMAL(18,2) | Financial Sensitive |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.21 `Go_Audit_Process_Execution`
- **Description**: Audit table capturing Gold pipeline execution, reconciliation, and load outcomes.
- **Table Type**: Audit Data

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| pipeline_name | Name of the pipeline or job executed | STRING | None |
| pipeline_run_date | Date and time the pipeline executed | TIMESTAMP | None |
| process_layer | Medallion layer being processed, here Gold | STRING | None |
| process_status | Execution status such as Started, Completed, Failed | STRING | None |
| source_object_name | Source object or domain loaded by the process | STRING | None |
| target_table_name | Gold table loaded by the process | STRING | None |
| records_read_count | Number of records read from source | BIGINT | None |
| records_written_count | Number of records written to target | BIGINT | None |
| records_rejected_count | Number of records rejected during validation | BIGINT | None |
| reconciliation_status | Indicates whether source and target totals reconciled | STRING | None |
| error_summary | Summary of processing error if applicable | STRING | None |
| load_date | Date the audit record was loaded | TIMESTAMP | None |
| update_date | Date the audit record was updated | TIMESTAMP | None |
| source_system | Source system, orchestrator, or framework name | STRING | None |

### 1.4.22 `Go_Error_Data_Validation`
- **Description**: Error table storing row-level and rule-level validation failures identified during Gold processing.
- **Table Type**: Error Data

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| validation_date | Date and time the validation executed | TIMESTAMP | None |
| process_layer | Medallion layer where the validation occurred | STRING | None |
| target_table_name | Gold table to which the validation applies | STRING | None |
| validation_rule_name | Name of the business rule or technical rule evaluated | STRING | None |
| validation_rule_description | Description of the rule violated | STRING | None |
| source_record_reference | Non-identifier business reference used to trace the failed record | STRING | None |
| error_category | Category such as completeness, accuracy, format, consistency, or referential integrity | STRING | None |
| error_severity | Severity level such as warning, high, or critical | STRING | None |
| error_message | Detailed validation failure message | STRING | None |
| offending_column_name | Column causing the validation failure | STRING | None |
| offending_column_value | Source value that failed validation | STRING | Sensitive Operational |
| remediation_status | Current remediation state of the error record | STRING | None |
| load_date | Date the error record was loaded | TIMESTAMP | None |
| update_date | Date the error record was updated | TIMESTAMP | None |
| source_system | Source system or validation engine name | STRING | None |

### 1.4.23 `Go_Agg_Revenue_Branch_Period`
- **Description**: Aggregate table for branch and period revenue reporting.
- **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| reporting_period | Reporting period for summarized revenue | STRING | None |
| period_type | Reporting grain for the aggregate | STRING | None |
| branch_name | Branch represented by the aggregate | STRING | None |
| region_name | Region represented by the aggregate | STRING | None |
| sales_rep_name | Sales representative summarized in the aggregate where applicable | STRING | Personal Data |
| equipment_class_name | Equipment class summarized in the aggregate | STRING | None |
| rental_revenue | Summed rental revenue for the period | DECIMAL(18,2) | Financial Sensitive |
| gross_billings | Summed gross billings for the period | DECIMAL(18,2) | Financial Sensitive |
| net_billings | Summed net billings for the period | DECIMAL(18,2) | Financial Sensitive |
| credit_memo_rate | Period-level credit memo rate | DECIMAL(18,6) | None |
| average_daily_rate | Period-level ADR | DECIMAL(18,6) | None |
| revenue_per_contract | Period-level revenue per contract | DECIMAL(18,6) | None |
| trend_value | Period-over-period trend metric | DECIMAL(18,6) | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.24 `Go_Agg_AR_Branch_Aging_Period`
- **Description**: Aggregate table for AR aging reporting by branch, aging bucket, and reporting period.
- **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| snapshot_date | Snapshot date for the aggregate | DATE | None |
| branch_name | Branch represented by the aggregate | STRING | None |
| region_name | Region represented by the aggregate | STRING | None |
| collector_name | Collector represented in the aggregate where applicable | STRING | Personal Data |
| aging_bucket | Aging bucket represented by the aggregate | STRING | None |
| total_ar_outstanding | Total outstanding AR for the slice | DECIMAL(18,2) | Financial Sensitive |
| ar_90_plus_amount | 90+ outstanding amount for the slice | DECIMAL(18,2) | Financial Sensitive |
| ar_90_plus_percentage | 90+ percentage for the slice | DECIMAL(18,6) | None |
| best_possible_dso | Best possible DSO for the slice | DECIMAL(18,6) | None |
| dso | DSO for the slice | DECIMAL(18,6) | None |
| dso_trend | DSO trend for the slice | DECIMAL(18,6) | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.25 `Go_Agg_Cash_Collector_Period`
- **Description**: Aggregate table for collector performance and cash application reporting by period.
- **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| reporting_period | Reporting period for the aggregate | STRING | None |
| period_type | Reporting grain for the aggregate | STRING | None |
| branch_name | Branch represented by the aggregate | STRING | None |
| region_name | Region represented by the aggregate | STRING | None |
| collector_name | Collector summarized in the aggregate | STRING | Personal Data |
| cash_collected | Total collected cash for the period | DECIMAL(18,2) | Financial Sensitive |
| collection_effectiveness_index | CEI for the period | DECIMAL(18,6) | None |
| average_days_to_pay | Average days to pay for the period | DECIMAL(18,6) | None |
| invoices_paid_on_time_percentage | On-time payment percentage for the period | DECIMAL(18,6) | None |
| unapplied_cash_amount | Total unapplied cash for the period | DECIMAL(18,2) | Financial Sensitive |
| unapplied_cash_percentage | Percentage of unapplied cash for the period | DECIMAL(18,6) | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.26 `Go_Agg_Credit_Risk_Customer_Period`
- **Description**: Aggregate table for customer-level credit exposure and over-limit analysis by period.
- **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| snapshot_date | Snapshot date for the customer risk aggregate | DATE | None |
| branch_name | Branch represented by the aggregate | STRING | None |
| region_name | Region represented by the aggregate | STRING | None |
| customer_name | Customer represented by the aggregate | STRING | Personal Data |
| customer_status | Customer status used in risk reporting | STRING | Personal Data |
| credit_limit | Customer credit limit | DECIMAL(18,2) | Financial Sensitive |
| outstanding_ar | Outstanding AR exposure | DECIMAL(18,2) | Financial Sensitive |
| credit_utilization_percentage | Exposure as a percentage of credit limit | DECIMAL(18,6) | None |
| customers_over_limit_amount | Over-limit amount for the customer | DECIMAL(18,2) | Financial Sensitive |
| ar_90_plus_amount_by_customer | 90+ past due exposure | DECIMAL(18,2) | Financial Sensitive |
| open_contract_value | Open contract exposure value | DECIMAL(18,2) | Financial Sensitive |
| suspended_customers_with_open_exposure | Indicator of suspended open exposure condition | INT | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

### 1.4.27 `Go_Agg_Executive_Health_Score`
- **Description**: Aggregate table for executive scorecard reporting across network, region, branch, sales, and collector views.
- **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|---|---|---|---|
| reporting_period | Reporting period used in scorecard analysis | STRING | None |
| period_type | Reporting grain used in scorecard analysis | STRING | None |
| network_level | Enterprise rollup level for scorecard presentation | STRING | None |
| region_name | Region included in the scorecard | STRING | None |
| branch_name | Branch included in the scorecard | STRING | None |
| sales_rep_name | Sales representative included where scorecard slice requires it | STRING | Personal Data |
| collector_name | Collector included where scorecard slice requires it | STRING | Personal Data |
| overall_revenue_to_cash_health_score | Composite score from revenue, AR, cash application, and credit risk domains | DECIMAL(18,6) | None |
| revenue_domain_score | Revenue domain component of the health score | DECIMAL(18,6) | None |
| ar_domain_score | AR domain component of the health score | DECIMAL(18,6) | None |
| cash_application_domain_score | Cash application domain component of the health score | DECIMAL(18,6) | None |
| credit_risk_domain_score | Credit risk domain component of the health score | DECIMAL(18,6) | None |
| load_date | Date the record was loaded into Gold | TIMESTAMP | None |
| update_date | Date the record was last updated in Gold | TIMESTAMP | None |
| source_system | Source system or processing domain from which the record originated | STRING | None |

# 2. Conceptual Data Model Diagram in Tabular Form

| Source Table | Connected To Table | Relationship Key Field | Relationship Description |
|---|---|---|---|
| Go_Dim_Region | Go_Dim_Branch | region_name | One region is connected to many branches by `region_name` |
| Go_Dim_Organization_Hierarchy | Go_Dim_Branch | organization_hierarchy_name | One hierarchy path is connected to many branches by `organization_hierarchy_name` |
| Go_Dim_Branch | Go_Dim_Sales_Rep | branch_name | One branch is connected to many sales representatives by `branch_name` |
| Go_Dim_Branch | Go_Dim_Collector | branch_name | One branch is connected to many collectors by `branch_name` |
| Go_Dim_Branch | Go_Dim_Contract | branch_name | One branch is connected to many contracts by `branch_name` |
| Go_Dim_Customer | Go_Dim_Contract | customer_name | One customer is connected to many contracts by `customer_name` |
| Go_Dim_Equipment_Class | Go_Dim_Contract | equipment_class_name | One equipment class is connected to many contracts by `equipment_class_name` |
| Go_Dim_Contract | Go_Dim_Invoice | contract_status | Contract context is connected to invoice context by business conformance using `contract_status` where status-level reporting is required |
| Go_Dim_Customer | Go_Fact_AR_Aging | customer_name | One customer is connected to many AR aging facts by `customer_name` |
| Go_Dim_Customer | Go_Fact_Credit_Risk | customer_name | One customer is connected to many credit risk facts by `customer_name` |
| Go_Dim_Customer | Go_Fact_Cash_Application | customer_name | One customer is connected to many cash application facts by `customer_name` |
| Go_Dim_Branch | Go_Fact_Rental_Revenue | branch_name | One branch is connected to many rental revenue facts by `branch_name` |
| Go_Dim_Branch | Go_Fact_AR_Aging | branch_name | One branch is connected to many AR aging facts by `branch_name` |
| Go_Dim_Branch | Go_Fact_Cash_Application | branch_name | One branch is connected to many cash application facts by `branch_name` |
| Go_Dim_Branch | Go_Fact_Credit_Risk | branch_name | One branch is connected to many credit risk facts by `branch_name` |
| Go_Dim_Region | Go_Fact_Rental_Revenue | region_name | One region is connected to many rental revenue facts by `region_name` |
| Go_Dim_Region | Go_Fact_AR_Aging | region_name | One region is connected to many AR aging facts by `region_name` |
| Go_Dim_Region | Go_Fact_Cash_Application | region_name | One region is connected to many cash application facts by `region_name` |
| Go_Dim_Region | Go_Fact_Credit_Risk | region_name | One region is connected to many credit risk facts by `region_name` |
| Go_Dim_Date | Go_Fact_Rental_Revenue | reporting_date | One reporting date is connected to many rental revenue facts by `reporting_date` |
| Go_Dim_Date | Go_Fact_Cash_Application | reporting_date | One reporting date is connected to many cash application facts by `reporting_date` |
| Go_Dim_Date | Go_Fact_AR_Aging | snapshot_date | One reporting date is connected to many AR aging facts by `snapshot_date` |
| Go_Dim_Date | Go_Fact_Credit_Risk | snapshot_date | One reporting date is connected to many credit risk facts by `snapshot_date` |
| Go_Dim_Sales_Rep | Go_Fact_Rental_Revenue | sales_rep_name | One sales representative is connected to many rental revenue facts by `sales_rep_name` |
| Go_Dim_Collector | Go_Fact_AR_Aging | collector_name | One collector is connected to many AR aging facts by `collector_name` |
| Go_Dim_Collector | Go_Fact_Cash_Application | collector_name | One collector is connected to many cash application facts by `collector_name` |
| Go_Dim_Equipment_Class | Go_Fact_Rental_Revenue | equipment_class_name | One equipment class is connected to many rental revenue facts by `equipment_class_name` |
| Go_Dim_Invoice | Go_Fact_AR_Aging | due_date | Invoice due date context is connected to AR aging by `due_date` |
| Go_Dim_Invoice | Go_Fact_Cash_Application | payment_date | Invoice and payment timing context is connected to cash application by `payment_date` |
| Go_Code_Aging_Bucket | Go_Fact_AR_Aging | aging_bucket | Aging bucket code is connected to AR aging facts by `aging_bucket` |
| Go_Code_Payment_Method | Go_Fact_Cash_Application | payment_method | Payment method code is connected to cash application facts by `payment_method` |
| Go_Code_Match_Status | Go_Fact_Cash_Application | match_status | Match status code is connected to cash application facts by `match_status` |
| Go_Code_Customer_Status | Go_Dim_Customer | customer_status | Customer status code is connected to customer dimension by `customer_status` |
| Go_Code_Contract_Status | Go_Dim_Contract | contract_status | Contract status code is connected to contract dimension by `contract_status` |
| Go_Code_Period_Type | Go_Dim_Date | period_type | Period type code is connected to date dimension by `period_type` |
| Go_Fact_Rental_Revenue | Go_Agg_Revenue_Branch_Period | branch_name, region_name, reporting_period | Revenue fact is summarized into branch-period aggregate by branch, region, and reporting period |
| Go_Fact_AR_Aging | Go_Agg_AR_Branch_Aging_Period | branch_name, region_name, aging_bucket, snapshot_date | AR fact is summarized into branch aging aggregate by branch, region, aging bucket, and snapshot date |
| Go_Fact_Cash_Application | Go_Agg_Cash_Collector_Period | branch_name, region_name, collector_name, reporting_period | Cash application fact is summarized into collector-period aggregate by branch, region, collector, and reporting period |
| Go_Fact_Credit_Risk | Go_Agg_Credit_Risk_Customer_Period | branch_name, region_name, customer_name, snapshot_date | Credit risk fact is summarized into customer-period aggregate by branch, region, customer, and snapshot date |
| Go_Fact_Rental_Revenue / Go_Fact_AR_Aging / Go_Fact_Cash_Application / Go_Fact_Credit_Risk | Go_Agg_Executive_Health_Score | reporting_period, branch_name, region_name | Domain facts are combined into executive scorecard aggregate by reporting period, branch, and region |

# 3. Cross-Layer Relationships

| Layer | Source Table / Entity | Target Gold Table | Relationship Basis |
|---|---|---|---|
| Conceptual to Gold | Region | Go_Dim_Region | Conformed descriptive rollup entity |
| Conceptual to Gold | Branch | Go_Dim_Branch | Conformed operating unit dimension |
| Conceptual to Gold | Date | Go_Dim_Date | Conformed calendar and reporting dimension |
| Conceptual to Gold | Customer | Go_Dim_Customer | Conformed customer reporting dimension with history |
| Conceptual to Gold | Sales Rep | Go_Dim_Sales_Rep | Conformed personnel reporting dimension |
| Conceptual to Gold | Collector | Go_Dim_Collector | Conformed personnel reporting dimension |
| Conceptual to Gold | Equipment Class | Go_Dim_Equipment_Class | Conformed product classification dimension |
| Conceptual to Gold | Contract | Go_Dim_Contract | Contract descriptive and exposure context |
| Conceptual to Gold | Invoice | Go_Dim_Invoice | Billing descriptive context |
| Conceptual to Gold | Fact Rental Revenue | Go_Fact_Rental_Revenue | Revenue and billing analytics fact |
| Conceptual to Gold | Fact AR Aging | Go_Fact_AR_Aging | Receivables aging analytics fact |
| Conceptual to Gold | Fact Cash Application | Go_Fact_Cash_Application | Cash and payment application analytics fact |
| Conceptual to Gold | Fact Credit Risk | Go_Fact_Credit_Risk | Customer credit exposure analytics fact |
| Conceptual to Gold | Organization Hierarchy | Go_Dim_Organization_Hierarchy | Conformed hierarchy dimension |
| Constraints to Gold | Data Completeness Rules | Go_Error_Data_Validation | Missing mandatory fields captured as validation errors |
| Constraints to Gold | Data Accuracy Rules | Go_Error_Data_Validation | Reconciliation and derivation failures captured as validation errors |
| Constraints to Gold | Data Consistency Rules | Go_Audit_Process_Execution / Go_Error_Data_Validation | Execution reconciliation and consistency failures logged |
| Silver to Gold | Conformed Branch, Region, Customer, Contract, Invoice, Date structures | All Gold dimensions and facts | Silver standardization feeds Gold dimensional and fact structures |
| Silver to Gold | Deduplicated customer records | Go_Dim_Customer / Go_Fact_Credit_Risk | Silver deduplication supports conformed Gold customer exposure |
| Silver to Gold | Governed analytical measures | Gold facts and aggregates | Silver cleansed measures are transformed into business-facing aggregates |

# 4. Constraints and Validation Mapping in Gold

1. `Go_Code_Aging_Bucket` enforces allowed aging bucket values: `0-30`, `31-60`, `61-90`, `90+`.
2. `Go_Code_Customer_Status` enforces allowed customer statuses including `Active` and `Suspended`.
3. `Go_Code_Contract_Status` enforces allowed contract statuses including `Open` and `Closed`.
4. `Go_Fact_Rental_Revenue.net_billings` must reconcile to `gross_billings - credit_memo_amount`.
5. `Go_Fact_AR_Aging.aging_bucket_amount` totals must reconcile to `total_ar_outstanding` at reporting grain.
6. `Go_Fact_Cash_Application.payment_amount` applied values must not exceed related invoice amount available in conformed invoice context.
7. `Go_Agg_Executive_Health_Score.overall_revenue_to_cash_health_score` must remain in the range `0` to `100`.
8. `Go_Fact_Credit_Risk.credit_utilization_percentage` is derived from `outstanding_ar / credit_limit` where denominator is non-zero.
9. `Go_Fact_Cash_Application.unapplied_cash_percentage` is derived from `unapplied_cash_amount / payment_amount` where denominator is non-zero.
10. `Go_Error_Data_Validation` stores exceptions for completeness, format, accuracy, consistency, dependency, and referential integrity issues.
11. `Go_Audit_Process_Execution` stores reconciliation outcomes between source, Silver, and Gold loads.

# 5. Design Decisions and Rationale

1. A dimensional Gold model is used because the reporting domain is KPI-driven and optimized for analytics, scorecards, and drill-down queries.
2. Facts are separated by business process domain: revenue, AR aging, cash application, and credit risk. This aligns to the conceptual model and supports modular loading.
3. Conformed dimensions for date, branch, region, customer, and hierarchy ensure consistent slicing across all facts.
4. SCD Type 2 is applied where business history affects analytics, especially for branch, customer, collector, sales rep, contract, and organization hierarchy.
5. SCD Type 1 is used for static or correction-only domains such as date, region, equipment class, and invoice descriptors.
6. Explicit identifier fields are excluded to comply with the requirement not to include keys, IDs, or identifier-style physical names.
7. Aggregate tables are intentionally added to support recurring executive scorecards and operational dashboards with lower query latency.
8. Audit and error tables are included because pipeline traceability and validation transparency are required for governed medallion architecture.
9. PII classification is included to support GDPR-aligned handling of customer and personnel names, statuses, and commercial attributes.
10. Column descriptions are business-oriented so the model can be consumed by analytics, engineering, and governance stakeholders.

# 6. Assumptions Based on Available Input

1. The conceptual model and constraints were available and used as the authoritative Gold design input.
2. No separate Silver logical model file was provided in the supplied GitHub paths, so the Gold model was inferred from the conceptual entities, business rules, and transformation guidance referencing Silver conformance.
3. Customer and personnel names are classified as Personal Data because they can identify natural persons in some operational contexts.
4. Credit limits, invoice amounts, payment amounts, AR balances, and similar monetary fields are classified as Financial Sensitive.
5. Aggregate tables are derived directly from the listed KPI and reporting requirements.

# 7. apiCost
1. **apiCost: 0.000000**

[Databricks_Gold_Model_Logical_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Model_Logical/Databricks_Gold_Model_Logical_1.md)
outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Bronze_Model_Logical
pipelineID : 12368