_____________________________________________
## *Author*: Ascendion AVA+
## *Created on*:   
## *Description*: Gold layer logical data model for Rental Revenue-to-Cash analytical reporting in a medallion architecture.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# 1. Gold Layer Logical Model

## 1.1 Design Summary
1. The Gold layer is designed as a dimensional model to support executive scorecards, billing performance, AR aging, cash application, and customer credit risk analytics.
2. Transaction-oriented analytical tables are classified as Facts.
3. Descriptive business context tables are classified as Dimensions.
4. Controlled value support tables are classified as Code Tables.
5. Additional Gold structures are included for process audit data, validation error data, and reporting aggregates.
6. Naming convention uses the prefix `Go_` for all Gold logical tables.
7. Based on the instruction, primary key, foreign key, unique identifier, and explicit ID fields are not included.
8. Metadata columns `load_date`, `update_date`, and `source_system` are included in each Gold table.

## 1.2 Table Inventory

### 1.2.1 Go_dim_date
1. **Table Description**: Conformed reporting calendar dimension used for daily, weekly, monthly, quarterly, and snapshot-based analysis across all Gold facts.
2. **Table Type**: Dimension
3. **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| reporting_date | Calendar date used for reporting and snapshot analysis. | date | None |
| reporting_period | Business reporting period such as week, month, or quarter. | string | None |
| period_type | Reporting grain such as day, week, month, or quarter. | string | None |
| number_of_days_in_period | Day count for the reporting period used in DSO and other period metrics. | integer | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.2 Go_dim_region
1. **Table Description**: Region dimension used for performance comparison, rollups, and regional analytics.
2. **Table Type**: Dimension
3. **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| region_name | Name of the organizational region used for aggregation and comparison. | string | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.3 Go_dim_branch
1. **Table Description**: Branch dimension representing the operating business unit used in revenue, AR, collections, and risk reporting.
2. **Table Type**: Dimension
3. **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| branch_name | Name of the operating branch used in reporting. | string | None |
| branch_status | Branch activity status for the reporting date. | string | None |
| region_name | Region assignment for the branch. | string | None |
| organization_hierarchy_name | Rollup hierarchy used for drill-down, drill-up, and governed reporting. | string | None |
| network_level | Highest enterprise rollup level for cross-network comparisons. | string | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.4 Go_dim_customer
1. **Table Description**: Conformed customer dimension used across AR, cash application, and credit risk analytics.
2. **Table Type**: Dimension
3. **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| customer_name | Business name of the customer. | string | Business Sensitive |
| customer_status | Customer operational status such as Active or Suspended. | string | Business Sensitive |
| credit_terms | Agreed payment terms for the customer. | string | Business Sensitive |
| credit_limit | Approved customer credit exposure limit. | decimal(18,2) | Financial Sensitive |
| customer_since_date | Date indicating when the customer relationship started. | date | Business Sensitive |
| collector_name | Assigned collector responsible for customer collection activity. | string | Business Sensitive |
| sales_rep_name | Assigned sales representative associated with customer business. | string | Business Sensitive |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.5 Go_dim_sales_rep
1. **Table Description**: Sales representative dimension supporting sales and billing performance drill-down.
2. **Table Type**: Dimension
3. **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| sales_rep_name | Name of the sales representative associated with contracts and revenue. | string | Personal Data |
| branch_name | Branch associated with the sales representative. | string | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.6 Go_dim_collector
1. **Table Description**: Collector dimension supporting collections performance and cash application analysis.
2. **Table Type**: Dimension
3. **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| collector_name | Name of the collector responsible for collection activities. | string | Personal Data |
| branch_name | Branch associated with the collector. | string | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.7 Go_dim_equipment_class
1. **Table Description**: Equipment classification dimension used to analyze revenue and billing mix.
2. **Table Type**: Dimension
3. **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| equipment_class_name | Category used to analyze rental revenue and billing performance. | string | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.8 Go_dim_contract
1. **Table Description**: Contract dimension used for contract status, exposure, and billing context.
2. **Table Type**: Dimension
3. **SCD Type**: Type 2

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| contract_status | Indicates whether the contract is open or closed. | string | None |
| open_contract_count | Number of open contracts related to the reporting grain. | integer | None |
| open_contract_value | Value of open contracts used in exposure analysis. | decimal(18,2) | Financial Sensitive |
| total_billed_rental_days | Total billed rental days used for ADR calculation. | integer | None |
| customer_name | Customer associated with the contract. | string | Business Sensitive |
| branch_name | Branch associated with the contract. | string | None |
| equipment_class_name | Equipment class assigned to the contract. | string | None |
| sales_rep_name | Sales representative associated with the contract. | string | Personal Data |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.9 Go_dim_invoice
1. **Table Description**: Invoice dimension holding invoice-related descriptive attributes for billing, AR aging, and payment analysis.
2. **Table Type**: Dimension
3. **SCD Type**: Type 1

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| invoice_date | Date the invoice was issued. | date | None |
| due_date | Date when payment is expected for the invoice. | date | None |
| aging_bucket | Aging bucket derived from days past due using governed bucket ranges. | string | None |
| days_past_due | Number of days the invoice is overdue at snapshot time. | integer | None |
| match_status | Payment application status such as applied or unapplied where relevant for invoice analysis. | string | None |
| customer_name | Customer associated with the invoice. | string | Business Sensitive |
| contract_status | Contract status associated with the invoiced business activity. | string | None |
| load_date | Date the Gold record was loaded. | timestamp | None |
| update_date | Date the Gold record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.10 Go_code_aging_bucket
1. **Table Description**: Code table containing the allowed aging bucket categories used by AR aging and credit risk analytics.
2. **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| aging_bucket_name | Allowed bucket values such as 0-30, 31-60, 61-90, and 90+. | string | None |
| bucket_sequence | Business sort sequence for the bucket. | integer | None |
| bucket_definition | Business rule definition for the bucket range. | string | None |
| load_date | Date the Gold code record was loaded. | timestamp | None |
| update_date | Date the Gold code record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.11 Go_code_period_type
1. **Table Description**: Code table defining supported reporting grains for time analysis.
2. **Table Type**: Code Table

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| period_type_name | Supported period grain such as day, week, month, or quarter. | string | None |
| period_type_description | Description of how the period type is used in reporting. | string | None |
| load_date | Date the Gold code record was loaded. | timestamp | None |
| update_date | Date the Gold code record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.12 Go_fct_rental_revenue
1. **Table Description**: Fact table capturing rental revenue and billing measures for executive and billing performance analytics.
2. **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| reporting_date | Date for the revenue measurement. | date | None |
| branch_name | Branch associated with the revenue activity. | string | None |
| region_name | Region rollup for the branch. | string | None |
| sales_rep_name | Sales representative associated with the revenue activity. | string | Personal Data |
| equipment_class_name | Equipment class used for revenue mix analysis. | string | None |
| contract_status | Contract status driving the revenue event. | string | None |
| rental_revenue | Revenue recognized from rental activity. | decimal(18,2) | Financial Sensitive |
| gross_billings | Total billing value before credit memo adjustments. | decimal(18,2) | Financial Sensitive |
| credit_memo_amount | Reduction amount applied through credit memos. | decimal(18,2) | Financial Sensitive |
| net_billings | Billing value after credit memo adjustments. | decimal(18,2) | Financial Sensitive |
| invoice_count | Count of invoices contributing to the revenue measures. | integer | None |
| average_daily_rate | Revenue per billed rental day. | decimal(18,4) | Financial Sensitive |
| revenue_per_contract | Average revenue earned per contract. | decimal(18,4) | Financial Sensitive |
| credit_memo_rate | Ratio of credit memo amount to gross billings. | decimal(18,6) | Financial Sensitive |
| trend_value | Period-over-period trend indicator for revenue analysis. | decimal(18,4) | None |
| load_date | Date the Gold fact record was loaded. | timestamp | None |
| update_date | Date the Gold fact record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.13 Go_fct_ar_aging
1. **Table Description**: Fact table representing point-in-time outstanding receivables and aging measures for AR monitoring.
2. **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| snapshot_date | Date at which AR aging is measured. | date | None |
| customer_name | Customer for whom AR exposure is analyzed. | string | Business Sensitive |
| branch_name | Branch associated with the receivable exposure. | string | None |
| collector_name | Collector responsible for the receivable portfolio. | string | Personal Data |
| aging_bucket | Aging category used for receivable summarization. | string | None |
| total_ar_outstanding | Total receivable balance outstanding at the snapshot date. | decimal(18,2) | Financial Sensitive |
| ar_90_plus_amount | Receivable amount in the 90+ aging bucket. | decimal(18,2) | Financial Sensitive |
| ar_90_plus_percentage | Proportion of total AR in the 90+ bucket. | decimal(18,6) | Financial Sensitive |
| best_possible_dso | Best achievable days sales outstanding measure. | decimal(18,4) | Financial Sensitive |
| dso | Days sales outstanding measure. | decimal(18,4) | Financial Sensitive |
| dso_trend | Period-over-period movement in DSO. | decimal(18,4) | Financial Sensitive |
| ar_aging_by_bucket | Receivable amount summarized by aging bucket. | decimal(18,2) | Financial Sensitive |
| load_date | Date the Gold fact record was loaded. | timestamp | None |
| update_date | Date the Gold fact record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.14 Go_fct_cash_application
1. **Table Description**: Fact table representing cash collection and payment application effectiveness.
2. **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| reporting_date | Date for the cash application measurement. | date | None |
| branch_name | Branch associated with the cash collection activity. | string | None |
| collector_name | Collector responsible for payment collection performance. | string | Personal Data |
| customer_name | Customer making the payment. | string | Business Sensitive |
| payment_method | Method used for payment. | string | None |
| match_status | Indicates whether payment is applied or unapplied. | string | None |
| cash_collected | Total cash collected in the reporting period. | decimal(18,2) | Financial Sensitive |
| collection_effectiveness_index | Measure of collection effectiveness in the period. | decimal(18,6) | Financial Sensitive |
| average_days_to_pay | Average elapsed time between invoice and payment. | decimal(18,4) | Financial Sensitive |
| invoices_paid_on_time_percentage | Percentage of invoices paid by the due date. | decimal(18,6) | Financial Sensitive |
| unapplied_cash_amount | Total payment amount not applied to invoices. | decimal(18,2) | Financial Sensitive |
| unapplied_cash_percentage | Share of total payments remaining unapplied. | decimal(18,6) | Financial Sensitive |
| payment_amount | Amount collected in the receipt. | decimal(18,2) | Financial Sensitive |
| payment_date | Date on which payment was made. | date | None |
| load_date | Date the Gold fact record was loaded. | timestamp | None |
| update_date | Date the Gold fact record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.15 Go_fct_credit_risk
1. **Table Description**: Fact table representing customer credit exposure, utilization, and risk conditions.
2. **Table Type**: Fact

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| snapshot_date | Date at which customer credit risk is measured. | date | None |
| customer_name | Customer whose credit exposure is evaluated. | string | Business Sensitive |
| branch_name | Branch associated with the customer exposure. | string | None |
| customer_status | Status used to identify suspended customers with exposure. | string | Business Sensitive |
| outstanding_ar | Current receivable exposure for the customer. | decimal(18,2) | Financial Sensitive |
| credit_limit | Approved customer credit limit used in utilization analysis. | decimal(18,2) | Financial Sensitive |
| credit_utilization_percentage | Ratio of outstanding AR to credit limit. | decimal(18,6) | Financial Sensitive |
| customers_over_limit_count | Count indicator for customers exceeding credit limit. | integer | None |
| customers_over_limit_amount | Amount of exposure above the approved limit. | decimal(18,2) | Financial Sensitive |
| suspended_customers_with_open_exposure | Indicator or count of suspended customers with AR or open contracts. | integer | None |
| ar_90_plus_amount_by_customer | Customer-level exposure in the 90+ bucket. | decimal(18,2) | Financial Sensitive |
| open_contract_count | Count of open contracts contributing to exposure. | integer | None |
| open_contract_value | Value of open contracts contributing to exposure. | decimal(18,2) | Financial Sensitive |
| load_date | Date the Gold fact record was loaded. | timestamp | None |
| update_date | Date the Gold fact record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.16 Go_agg_executive_health_score
1. **Table Description**: Aggregate table for executive scorecard reporting across network, region, branch, sales rep, and collector levels.
2. **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| reporting_date | Date for the executive health score reporting period. | date | None |
| network_level | Enterprise rollup level for scorecard reporting. | string | None |
| region_name | Region summary level. | string | None |
| branch_name | Branch summary level. | string | None |
| sales_rep_name | Sales representative summary level where required. | string | Personal Data |
| collector_name | Collector summary level where required. | string | Personal Data |
| overall_revenue_to_cash_health_score | Composite score of normalized domain scores. | decimal(18,4) | None |
| rental_revenue | Revenue metric used in the scorecard. | decimal(18,2) | Financial Sensitive |
| dso | Days sales outstanding metric used in the scorecard. | decimal(18,4) | Financial Sensitive |
| ar_90_plus_percentage | AR 90+ percentage used in the scorecard. | decimal(18,6) | Financial Sensitive |
| collection_effectiveness_index | CEI used in the scorecard. | decimal(18,6) | Financial Sensitive |
| unapplied_cash_percentage | Unapplied cash percentage used in the scorecard. | decimal(18,6) | Financial Sensitive |
| credit_utilization_percentage | Credit utilization percentage used in the scorecard. | decimal(18,6) | Financial Sensitive |
| load_date | Date the aggregate record was loaded. | timestamp | None |
| update_date | Date the aggregate record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.17 Go_agg_billing_performance
1. **Table Description**: Aggregate table supporting billing performance reporting by branch, region, sales rep, and equipment class.
2. **Table Type**: Aggregated

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| reporting_date | Date for billing performance reporting. | date | None |
| region_name | Region used for billing aggregation. | string | None |
| branch_name | Branch used for billing aggregation. | string | None |
| sales_rep_name | Sales representative used for billing drill-down. | string | Personal Data |
| equipment_class_name | Equipment class used for mix analysis. | string | None |
| gross_billings | Total billing amount before credits. | decimal(18,2) | Financial Sensitive |
| credit_memo_amount | Credit adjustment amount. | decimal(18,2) | Financial Sensitive |
| net_billings | Billing amount after credits. | decimal(18,2) | Financial Sensitive |
| rental_revenue | Rental revenue generated. | decimal(18,2) | Financial Sensitive |
| average_daily_rate | Average revenue earned per billed day. | decimal(18,4) | Financial Sensitive |
| revenue_per_contract | Average revenue earned per contract. | decimal(18,4) | Financial Sensitive |
| credit_memo_rate | Ratio of credits to gross billings. | decimal(18,6) | Financial Sensitive |
| invoice_count | Count of invoices in the aggregate. | integer | None |
| load_date | Date the aggregate record was loaded. | timestamp | None |
| update_date | Date the aggregate record was last updated. | timestamp | None |
| source_system | Source application or curated Silver process that supplied the record. | string | None |

### 1.2.18 Go_process_audit
1. **Table Description**: Process audit table used to store pipeline execution history, row processing metrics, and operational status for Gold loads.
2. **Table Type**: Audit Data

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| pipeline_name | Name of the pipeline or notebook that executed the Gold load. | string | None |
| pipeline_run_date | Date and time when the pipeline run started or completed. | timestamp | None |
| layer_name | Medallion layer name, fixed to Gold for this model. | string | None |
| source_system | Source application or upstream layer used in the load. | string | None |
| source_table_name | Source Silver object used by the process. | string | None |
| target_table_name | Gold object written by the process. | string | None |
| process_status | Final status such as success, warning, or failed. | string | None |
| records_read_count | Number of records read from the source. | bigint | None |
| records_written_count | Number of records written to the target. | bigint | None |
| records_rejected_count | Number of records rejected during processing. | bigint | None |
| process_start_time | Timestamp when execution started. | timestamp | None |
| process_end_time | Timestamp when execution ended. | timestamp | None |
| processing_duration_seconds | Total execution duration in seconds. | decimal(18,2) | None |
| audit_message | Operational message captured during execution. | string | None |
| load_date | Date the audit record was loaded. | timestamp | None |
| update_date | Date the audit record was last updated. | timestamp | None |

### 1.2.19 Go_error_data
1. **Table Description**: Error data table used to store validation failures, business rule exceptions, and reconciliation issues detected during Gold processing.
2. **Table Type**: Error Data

| Column Name | Description | Data Type | PII Classification |
|-------------|-------------|-----------|--------------------|
| pipeline_name | Name of the pipeline or validation routine that detected the error. | string | None |
| error_detected_date | Date and time when the error was detected. | timestamp | None |
| source_system | Source application or upstream layer associated with the error. | string | None |
| source_table_name | Source Silver object associated with the validation failure. | string | None |
| target_table_name | Gold target object impacted by the error. | string | None |
| validation_rule_name | Name of the rule that failed. | string | None |
| validation_rule_description | Business or technical description of the failed rule. | string | None |
| error_severity | Severity level such as low, medium, high, or critical. | string | None |
| error_status | Current disposition such as open, resolved, or ignored. | string | None |
| error_record_summary | Summary of the failing business record without using restricted identifier fields. | string | Business Sensitive |
| corrective_action | Expected remediation action for the issue. | string | None |
| load_date | Date the error record was loaded. | timestamp | None |
| update_date | Date the error record was last updated. | timestamp | None |

## 1.3 SCD Rationale
1. `Go_dim_date`, `Go_dim_region`, `Go_dim_sales_rep`, `Go_dim_collector`, and `Go_dim_equipment_class` are assigned **SCD Type 1** because the available inputs only require current descriptive reporting and do not explicitly require attribute history.
2. `Go_dim_branch` is assigned **SCD Type 2** because branch status and hierarchy assignment may change over time and reporting consistency by date is required.
3. `Go_dim_customer` is assigned **SCD Type 2** because customer status, credit terms, credit limit, collector assignment, and sales representative assignment can change and need historical analytics.
4. `Go_dim_contract` is assigned **SCD Type 2** because contract status and exposure-related attributes can change over time and should support as-was reporting.
5. `Go_dim_invoice` is assigned **SCD Type 1** because the available model treats invoice descriptors as point descriptors around facts and not as slowly changing master data.

# 2. Gold Layer Relationships Across Layers

## 2.1 Silver-to-Gold Mapping Logic
1. Silver conformed date data feeds `Go_dim_date` and all Gold fact and aggregate tables.
2. Silver conformed organization structures feed `Go_dim_region` and `Go_dim_branch`.
3. Silver conformed customer data feeds `Go_dim_customer`, `Go_fct_ar_aging`, `Go_fct_cash_application`, and `Go_fct_credit_risk`.
4. Silver personnel conformance feeds `Go_dim_sales_rep` and `Go_dim_collector`.
5. Silver contract data feeds `Go_dim_contract` and `Go_fct_rental_revenue`.
6. Silver invoice data feeds `Go_dim_invoice`, `Go_fct_rental_revenue`, `Go_fct_ar_aging`, and `Go_fct_cash_application`.
7. Silver cash receipt and payment application data feeds `Go_fct_cash_application`.
8. Silver exposure and receivable snapshots feed `Go_fct_ar_aging` and `Go_fct_credit_risk`.
9. Gold facts feed Gold aggregated tables for executive and billing analytics.

## 2.2 Fact-to-Dimension Relationships
| Gold Table | Related Table | Relationship Key Field |
|------------|---------------|------------------------|
| Go_fct_rental_revenue | Go_dim_date | reporting_date |
| Go_fct_rental_revenue | Go_dim_branch | branch_name |
| Go_fct_rental_revenue | Go_dim_region | region_name |
| Go_fct_rental_revenue | Go_dim_sales_rep | sales_rep_name |
| Go_fct_rental_revenue | Go_dim_equipment_class | equipment_class_name |
| Go_fct_rental_revenue | Go_dim_contract | contract_status, branch_name, customer_name |
| Go_fct_ar_aging | Go_dim_customer | customer_name |
| Go_fct_ar_aging | Go_dim_branch | branch_name |
| Go_fct_ar_aging | Go_dim_collector | collector_name |
| Go_fct_ar_aging | Go_dim_date | snapshot_date |
| Go_fct_ar_aging | Go_code_aging_bucket | aging_bucket |
| Go_fct_cash_application | Go_dim_date | reporting_date |
| Go_fct_cash_application | Go_dim_branch | branch_name |
| Go_fct_cash_application | Go_dim_collector | collector_name |
| Go_fct_cash_application | Go_dim_customer | customer_name |
| Go_fct_credit_risk | Go_dim_date | snapshot_date |
| Go_fct_credit_risk | Go_dim_customer | customer_name |
| Go_fct_credit_risk | Go_dim_branch | branch_name |
| Go_agg_executive_health_score | Go_dim_date | reporting_date |
| Go_agg_executive_health_score | Go_dim_branch | branch_name |
| Go_agg_executive_health_score | Go_dim_region | region_name |
| Go_agg_billing_performance | Go_dim_date | reporting_date |
| Go_agg_billing_performance | Go_dim_branch | branch_name |
| Go_agg_billing_performance | Go_dim_region | region_name |
| Go_agg_billing_performance | Go_dim_sales_rep | sales_rep_name |
| Go_agg_billing_performance | Go_dim_equipment_class | equipment_class_name |

# 3. Conceptual Data Model Diagram in Tabular Form

| Source Table | Connected To Table | Key Field Used for Connection | Relationship Description |
|--------------|--------------------|-------------------------------|--------------------------|
| Go_dim_region | Go_dim_branch | region_name | One region connects to many branches by region_name. |
| Go_dim_branch | Go_dim_contract | branch_name | One branch connects to many contracts by branch_name. |
| Go_dim_customer | Go_dim_contract | customer_name | One customer connects to many contracts by customer_name. |
| Go_dim_customer | Go_dim_invoice | customer_name | One customer connects to many invoice descriptors by customer_name. |
| Go_dim_sales_rep | Go_dim_branch | branch_name | Many sales representatives connect to one branch by branch_name. |
| Go_dim_collector | Go_dim_branch | branch_name | Many collectors connect to one branch by branch_name. |
| Go_dim_contract | Go_fct_rental_revenue | contract_status and branch_name | Contract context connects to rental revenue analytics by conformed contract business attributes. |
| Go_dim_invoice | Go_fct_cash_application | customer_name and match_status | Invoice descriptors connect to cash application analytics by customer and payment application context. |
| Go_dim_date | Go_fct_rental_revenue | reporting_date | One reporting date connects to many rental revenue fact rows by reporting_date. |
| Go_dim_date | Go_fct_ar_aging | snapshot_date | One date connects to many AR aging snapshots by snapshot_date. |
| Go_dim_date | Go_fct_cash_application | reporting_date | One reporting date connects to many cash application fact rows by reporting_date. |
| Go_dim_date | Go_fct_credit_risk | snapshot_date | One date connects to many credit risk snapshots by snapshot_date. |
| Go_dim_customer | Go_fct_ar_aging | customer_name | One customer connects to many AR aging rows by customer_name. |
| Go_dim_customer | Go_fct_credit_risk | customer_name | One customer connects to many credit risk rows by customer_name. |
| Go_dim_branch | Go_fct_rental_revenue | branch_name | One branch connects to many rental revenue rows by branch_name. |
| Go_dim_branch | Go_fct_cash_application | branch_name | One branch connects to many cash application rows by branch_name. |
| Go_dim_collector | Go_fct_ar_aging | collector_name | One collector connects to many AR aging rows by collector_name. |
| Go_dim_collector | Go_fct_cash_application | collector_name | One collector connects to many cash application rows by collector_name. |
| Go_code_aging_bucket | Go_fct_ar_aging | aging_bucket | One aging bucket code connects to many AR aging rows by aging_bucket. |
| Go_fct_rental_revenue | Go_agg_billing_performance | reporting_date, branch_name, sales_rep_name, equipment_class_name | Revenue fact rolls up into billing performance aggregate. |
| Go_fct_rental_revenue | Go_agg_executive_health_score | reporting_date, branch_name, region_name | Revenue fact contributes to executive scorecard aggregate. |
| Go_fct_ar_aging | Go_agg_executive_health_score | snapshot_date, branch_name, customer_name | AR aging fact contributes to executive scorecard aggregate. |
| Go_fct_cash_application | Go_agg_executive_health_score | reporting_date, branch_name, collector_name | Cash application fact contributes to executive scorecard aggregate. |
| Go_fct_credit_risk | Go_agg_executive_health_score | snapshot_date, branch_name, customer_name | Credit risk fact contributes to executive scorecard aggregate. |

# 4. Design Decisions and Assumptions
1. Facts were derived from the conceptual entities explicitly labeled as analytical facts: Rental Revenue, AR Aging, Cash Application, and Credit Risk.
2. Dimensions were derived from descriptive entities: Date, Region, Branch, Customer, Sales Rep, Collector, Equipment Class, Contract, and Invoice.
3. Code tables were created for controlled lists that are constrained in the source rules, specifically aging buckets and period type.
4. Aggregate tables were included because report requirements explicitly require executive scorecard and billing performance analytics at summary levels.
5. Audit and error structures were included because the instructions require support for process audit data and validation error data.
6. Explicit identifier columns were excluded in compliance with the instruction to avoid primary key, foreign key, unique identifier, and ID fields.
7. Business names and descriptive fields are used as logical relationship fields because logical modeling is requested and ID fields are prohibited.
8. PII classification follows common governance practice: personal names are marked as Personal Data, customer commercial details are marked as Business Sensitive, and financial exposure measures are marked as Financial Sensitive.
9. Where the source did not explicitly provide a Silver model file, the Gold logical model was inferred only from the conceptual model and constraints provided in the repository input.
10. Invoice and contract structures are treated as conformed analytical dimensions because they provide descriptive business context to multiple facts.
11. Executive credit-risk visibility is limited to aggregate usage in accordance with the reporting rule that executives may see aggregates only and not customer details beyond name.

# 5. Compliance and Data Quality Considerations
1. Customer names, sales representative names, and collector names should be protected through role-based access and reporting policies.
2. Credit limit, outstanding AR, payment amount, and other financial measures should be classified and handled as sensitive financial data.
3. Aging bucket values must be restricted to `0-30`, `31-60`, `61-90`, and `90+`.
4. Net billings must always reconcile to gross billings minus credit memo amount.
5. Applied payment amounts must not exceed the related invoice amount.
6. Rate-based measures such as DSO, CEI, average days to pay, and percentages must only be calculated when denominators are non-zero.
7. Branch and region rollups must remain conformed across all Gold facts and aggregates.
8. Duplicate customer records must be resolved upstream before Gold credit-risk aggregation.

# 6. apiCost
1. **apiCost**: 0.000000

# 7. Output URL (Clickable Hyperlinks)
1. [Databricks_Gold_Model_Logical_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Model_Logical/Databricks_Gold_Model_Logical_1.md)
