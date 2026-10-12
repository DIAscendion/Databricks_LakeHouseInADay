_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Detailed Gold fact transformation data mapping from Silver to Gold for Rental Revenue-to-Cash fact tables with validations, cleansing, aggregations, and Databricks-compatible transformation rules.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Data Mapping

## 1. Overview
This document provides a detailed attribute-level data mapping for Gold fact tables in the Rental Revenue-to-Cash domain. It is derived from the Silver physical model and the Databricks Gold Fact Transformation Recommender output. The mapping defines target Gold fact fields, their Silver source fields, fact-dimension relationships, validations, cleansing logic, transformation rules, aggregations, and business explanations. All rules are aligned with PySpark and Databricks processing patterns and preserve auditability, reconciliation, and conformance.

Key considerations applied in this mapping:
- Fact tables covered: rental revenue, AR aging, cash application, and credit risk.
- Source layer is Silver and target layer is Gold.
- Joins use business keys such as `contract_id`, `customer_id`, `invoice_id`, `sales_rep_id`, and `branch_code`.
- All rate and percentage calculations include divide-by-zero protection.
- Aging buckets are standardized to allowed values only.
- Credit memo amounts are standardized as negative values.
- Missing and invalid records should be quarantined into error handling workflows instead of being silently dropped.
- Numeric values are standardized to financial precision compatible with Databricks Delta and Spark SQL.

## 2. Source Inputs Used

| Input File | Usage in This Mapping |
|---|---|
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Used to identify Silver source tables, source columns, joins, datatypes, and operational metadata |
| `DI_Databricks_Gold_Fact_Transformation_Recommender/Databricks_Gold_Fact_Transformation_Recommender_1.md` | Used to derive target Gold fact tables, metric logic, validations, cleansing rules, aggregations, and recommended transformation patterns |

## 3. Fact Tables in Scope

| Target Table | Grain | Primary Source Tables |
|---|---|---|
| `gold.go_fct_rental_revenue` | One row per reporting date, contract, branch, sales rep, equipment class, customer | `silver.si_invoices`, `silver.si_rental_contracts`, `silver.si_customer_master`, `silver.si_branch_employee` |
| `gold.go_fct_ar_aging` | One row per snapshot date, customer, collector, branch, aging bucket | `silver.si_invoices`, `silver.si_customer_master`, `silver.si_branch_employee`, `silver.si_rental_contracts` |
| `gold.go_fct_cash_application` | One row per reporting date, payment application, customer, invoice, collector, branch | `silver.si_cash_receipts`, `silver.si_invoices`, `silver.si_customer_master`, `silver.si_branch_employee`, `silver.si_rental_contracts` |
| `gold.go_fct_credit_risk` | One row per snapshot date, customer, branch | `silver.si_invoices`, `silver.si_customer_master`, `silver.si_rental_contracts`, `silver.si_branch_employee` |

## 4. Join and Transformation Approach

| Step | Join / Logic | Purpose |
|---|---|---|
| 1 | Join `si_invoices.contract_id = si_rental_contracts.contract_id` | Align invoice measures to contract grain and branch/sales context |
| 2 | Join `si_invoices.customer_id = si_customer_master.customer_id` or `si_cash_receipts.customer_id = si_customer_master.customer_id` | Attach conformed customer attributes and credit information |
| 3 | Join `si_rental_contracts.sales_rep_id = si_branch_employee.employee_id` with branch alignment | Attach sales rep descriptive and regional attributes |
| 4 | Join contract branch to collector branch where role is collector | Attach AR and collections responsibility context |
| 5 | Derive standardized measures | Build gross billings, net billings, aging bucket, CEI, utilization, and other KPIs |
| 6 | Apply validation and cleansing rules | Ensure null handling, sign corrections, valid domains, denominator checks, and standardized outputs |
| 7 | Aggregate to target Gold fact grain | Produce final fact rows ready for Delta load |

## 5. Data Mapping for Fact Tables

### 5.1 Data Mapping for `gold.go_fct_rental_revenue`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Gold | `gold.go_fct_rental_revenue` | `reporting_date` | Silver | `silver.si_invoices` | `invoice_date` | Must not be null; must be a valid date | Map `invoice_date` as `reporting_date` at fact grain |
| Gold | `gold.go_fct_rental_revenue` | `branch_code` | Silver | `silver.si_rental_contracts` | `branch_code` | Must not be null; branch must be valid for organization hierarchy | Join from contracts and carry branch at fact grain |
| Gold | `gold.go_fct_rental_revenue` | `region_name` | Silver | `silver.si_branch_employee` | `region` | If available, region should align to active branch assignment | Derive by joining sales rep assignment on `sales_rep_id` and `branch_code` |
| Gold | `gold.go_fct_rental_revenue` | `sales_rep_id` | Silver | `silver.si_rental_contracts` | `sales_rep_id` | Required for sales reporting where contract exists | Map from contract record |
| Gold | `gold.go_fct_rental_revenue` | `sales_rep_name` | Silver | `silver.si_branch_employee` | `employee_name` | Optional descriptive field; if missing, leave null and log warning | Lookup from branch employee where role is sales rep |
| Gold | `gold.go_fct_rental_revenue` | `equipment_class` | Silver | `silver.si_rental_contracts` | `equipment_class` | Should follow standardized equipment class domain | Direct map from contracts |
| Gold | `gold.go_fct_rental_revenue` | `equipment_class_name` | Silver | `silver.si_rental_contracts` | `equipment_class` | Must align to conformed equipment class values | Use `equipment_class` as standardized display name unless separate dimension exists |
| Gold | `gold.go_fct_rental_revenue` | `contract_id` | Silver | `silver.si_rental_contracts` | `contract_id` | Must not be null for contract-based invoice rows | Direct map from contracts after invoice-contract join |
| Gold | `gold.go_fct_rental_revenue` | `contract_status` | Silver | `silver.si_rental_contracts` | `contract_status` | Exclude invalid statuses; cancelled contracts may be filtered based on business rule | Map current contract status; use for downstream filtering |
| Gold | `gold.go_fct_rental_revenue` | `customer_id` | Silver | `silver.si_customer_master` | `customer_id` | Must not be null; must resolve to a conformed customer record | Join from invoices to customer master |
| Gold | `gold.go_fct_rental_revenue` | `customer_name` | Silver | `silver.si_customer_master` | `customer_name` | Optional for descriptive reporting; should align to conformed customer master | Lookup from customer master |
| Gold | `gold.go_fct_rental_revenue` | `rental_revenue` | Silver | `silver.si_invoices` | `invoice_amount` | Standard invoice amounts must be non-negative; credit memos excluded from rental revenue | Sum `invoice_amount` where `invoice_type <> 'CREDIT_MEMO'` |
| Gold | `gold.go_fct_rental_revenue` | `gross_billings` | Silver | `silver.si_invoices` | `invoice_amount` | Gross billings must reconcile with non-credit invoice total | Sum positive invoice amounts for non-credit memo invoices |
| Gold | `gold.go_fct_rental_revenue` | `credit_memo_amount` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_type` | Credit memo amount must be negative | For `invoice_type = 'CREDIT_MEMO'`, store `-ABS(invoice_amount)` |
| Gold | `gold.go_fct_rental_revenue` | `net_billings` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_type` | Must reconcile as `gross_billings + credit_memo_amount` | Compute gross billings plus negative credit memo amount |
| Gold | `gold.go_fct_rental_revenue` | `invoice_count` | Silver | `silver.si_invoices` | `invoice_id` | Invoice ID should not be null | Count distinct `invoice_id` at target grain |
| Gold | `gold.go_fct_rental_revenue` | `average_daily_rate` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_amount`, `contract_start_date`, `contract_end_date` | Denominator must be greater than zero; dates must be valid | `SUM(non_credit_invoice_amount) / DATEDIFF(contract_end_date, contract_start_date)` when duration > 0 |
| Gold | `gold.go_fct_rental_revenue` | `revenue_per_contract` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_amount`, `contract_id` | Denominator must be non-zero | `SUM(non_credit_invoice_amount) / COUNT(DISTINCT contract_id)` |
| Gold | `gold.go_fct_rental_revenue` | `credit_memo_rate` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_type` | Denominator must be non-zero | `ABS(credit_memo_amount) / gross_billings` when gross billings <> 0 |
| Gold | `gold.go_fct_rental_revenue` | `trend_value` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_date`, `invoice_amount`, `invoice_type`, `branch_code` | Prior-period comparison requires ordered reporting periods | Compute `net_billings - LAG(net_billings)` partitioned by branch and ordered by reporting date |
| Gold | `gold.go_fct_rental_revenue` | `load_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate current processing timestamp |
| Gold | `gold.go_fct_rental_revenue` | `update_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate current processing timestamp |
| Gold | `gold.go_fct_rental_revenue` | `source_system` | Silver | Derived | constant | Must be populated for lineage | Set to `'silver_to_gold'` or enterprise lineage value |

### 5.2 Data Mapping for `gold.go_fct_ar_aging`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Gold | `gold.go_fct_ar_aging` | `snapshot_date` | Silver | Derived | `current_date()` | Must be a valid processing snapshot date | Use current processing date or controlled snapshot parameter |
| Gold | `gold.go_fct_ar_aging` | `customer_id` | Silver | `silver.si_customer_master` | `customer_id` | Must not be null; must resolve to conformed customer | Join invoice customer to customer master |
| Gold | `gold.go_fct_ar_aging` | `customer_name` | Silver | `silver.si_customer_master` | `customer_name` | Optional descriptive field | Map from customer master |
| Gold | `gold.go_fct_ar_aging` | `branch_code` | Silver | `silver.si_rental_contracts` | `branch_code` | Branch should exist and align with contract | Derive from contract linked to invoice |
| Gold | `gold.go_fct_ar_aging` | `collector_id` | Silver | `silver.si_branch_employee` | `collector_id` | Collector should align to branch assignment | Lookup collector by branch where role is collector |
| Gold | `gold.go_fct_ar_aging` | `collector_name` | Silver | `silver.si_branch_employee` | `employee_name` | Optional descriptive field | Map collector name from branch employee lookup |
| Gold | `gold.go_fct_ar_aging` | `aging_bucket` | Silver | `silver.si_invoices` | `due_date`, `days_past_due`, `aging_bucket` | Allowed values only: `0-30`, `31-60`, `61-90`, `90+` | Recalculate from `DATEDIFF(snapshot_date, due_date)`; override invalid bucket values |
| Gold | `gold.go_fct_ar_aging` | `total_ar_outstanding` | Silver | `silver.si_invoices` | `invoice_amount` | Invoice amount must be valid numeric; nulls treated as zero only if approved | Sum invoice amounts over customer snapshot |
| Gold | `gold.go_fct_ar_aging` | `ar_90_plus_amount` | Silver | `silver.si_invoices` | `invoice_amount`, `due_date` | Must reconcile with aging bucket logic | Sum invoice amounts where derived aging bucket = `90+` |
| Gold | `gold.go_fct_ar_aging` | `ar_90_plus_percentage` | Silver | `silver.si_invoices` | `invoice_amount`, `due_date` | Denominator must be non-zero | `ar_90_plus_amount / total_ar_outstanding` when total outstanding <> 0 |
| Gold | `gold.go_fct_ar_aging` | `best_possible_dso` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_date`, `aging_bucket` | Use same reporting period consistently; denominator must be non-zero | `(best_possible_numerator / total_credit_sales) * days_in_period` using approved reporting window |
| Gold | `gold.go_fct_ar_aging` | `dso` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_date` | Same reporting window required; denominator must be non-zero | `(total_ar_outstanding / total_credit_sales) * days_in_period` |
| Gold | `gold.go_fct_ar_aging` | `dso_trend` | Silver | Derived from AR aging result | `dso`, `snapshot/reporting_month` | Prior-period value required for comparison | Current period `dso - LAG(dso)` by customer |
| Gold | `gold.go_fct_ar_aging` | `ar_aging_by_bucket` | Silver | `silver.si_invoices` | `invoice_amount`, `due_date` | Must reconcile to overall AR by bucket totals | Sum invoice amount grouped by derived `aging_bucket` |
| Gold | `gold.go_fct_ar_aging` | `load_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate processing timestamp |
| Gold | `gold.go_fct_ar_aging` | `update_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate processing timestamp |
| Gold | `gold.go_fct_ar_aging` | `source_system` | Silver | Derived | constant | Must be populated for lineage | Set to `'silver_to_gold'` or enterprise lineage value |

### 5.3 Data Mapping for `gold.go_fct_cash_application`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Gold | `gold.go_fct_cash_application` | `reporting_date` | Silver | `silver.si_cash_receipts` | `receipt_date` | Must not be null and must be valid date | Map `receipt_date` as reporting date |
| Gold | `gold.go_fct_cash_application` | `branch_code` | Silver | `silver.si_rental_contracts` | `branch_code` | Must align through receipt -> invoice -> contract path | Derive branch from invoice-contract join |
| Gold | `gold.go_fct_cash_application` | `customer_id` | Silver | `silver.si_customer_master` | `customer_id` | Must not be null; conformed customer required | Join receipt customer to customer master |
| Gold | `gold.go_fct_cash_application` | `customer_name` | Silver | `silver.si_customer_master` | `customer_name` | Optional descriptive field | Lookup from customer master |
| Gold | `gold.go_fct_cash_application` | `invoice_id` | Silver | `silver.si_cash_receipts` | `invoice_id` | Required for invoice-linked payments | Direct map from receipts |
| Gold | `gold.go_fct_cash_application` | `collector_id` | Silver | `silver.si_branch_employee` | `collector_id` | Collector should align to branch assignment | Lookup collector by branch |
| Gold | `gold.go_fct_cash_application` | `collector_name` | Silver | `silver.si_branch_employee` | `employee_name` | Optional descriptive field | Map collector employee name |
| Gold | `gold.go_fct_cash_application` | `payment_method` | Silver | `silver.si_cash_receipts` | `payment_method` | Should follow valid payment method domain where available | Direct map from receipts |
| Gold | `gold.go_fct_cash_application` | `match_status` | Silver | `silver.si_cash_receipts` | `match_status` | Must be standardized to `APPLIED` or `UNAPPLIED` | `CASE WHEN upper(coalesce(match_status,'UNAPPLIED'))='APPLIED' THEN 'APPLIED' ELSE 'UNAPPLIED' END` |
| Gold | `gold.go_fct_cash_application` | `cash_collected` | Silver | `silver.si_cash_receipts` | `payment_amount` | Payment amount must be non-negative | Map `payment_amount` as collected cash |
| Gold | `gold.go_fct_cash_application` | `collection_effectiveness_index` | Silver | `silver.si_cash_receipts`, `silver.si_invoices` | `payment_amount`, `invoice_amount`, `aging_bucket` | Same reporting window required; denominator must be non-zero | Compute CEI using beginning/ending AR and credit sales logic from recommender |
| Gold | `gold.go_fct_cash_application` | `average_days_to_pay` | Silver | `silver.si_cash_receipts`, `silver.si_invoices` | `receipt_date`, `invoice_date` | Applicable for applied payments only | `AVG(DATEDIFF(receipt_date, invoice_date))` where match status is applied |
| Gold | `gold.go_fct_cash_application` | `invoices_paid_on_time_percentage` | Silver | `silver.si_cash_receipts`, `silver.si_invoices` | `receipt_date`, `due_date`, `invoice_id` | Denominator must be non-zero | `SUM(receipt_date <= due_date) / COUNT(*)` for applied invoices |
| Gold | `gold.go_fct_cash_application` | `unapplied_cash_amount` | Silver | `silver.si_cash_receipts` | `unapplied_payment_amount` | Nulls should default to zero if business-approved | `COALESCE(unapplied_payment_amount,0)` |
| Gold | `gold.go_fct_cash_application` | `unapplied_cash_percentage` | Silver | `silver.si_cash_receipts` | `payment_amount`, `unapplied_payment_amount` | Denominator must be non-zero | `SUM(unapplied_payment_amount) / SUM(payment_amount)` |
| Gold | `gold.go_fct_cash_application` | `payment_amount` | Silver | `silver.si_cash_receipts` | `payment_amount` | Payment amount must be non-negative | Direct map from receipts |
| Gold | `gold.go_fct_cash_application` | `payment_date` | Silver | `silver.si_cash_receipts` | `receipt_date` | Must be valid date | Map `receipt_date` as payment date |
| Gold | `gold.go_fct_cash_application` | `load_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate processing timestamp |
| Gold | `gold.go_fct_cash_application` | `update_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate processing timestamp |
| Gold | `gold.go_fct_cash_application` | `source_system` | Silver | Derived | constant | Must be populated for lineage | Set to `'silver_to_gold'` or enterprise lineage value |

### 5.4 Data Mapping for `gold.go_fct_credit_risk`

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Gold | `gold.go_fct_credit_risk` | `snapshot_date` | Silver | Derived | `current_date()` | Must be a valid snapshot date | Use processing date or controlled risk snapshot date |
| Gold | `gold.go_fct_credit_risk` | `customer_id` | Silver | `silver.si_customer_master` | `customer_id` | Must not be null; conformed customer required | Direct map from customer master joined to exposure measures |
| Gold | `gold.go_fct_credit_risk` | `customer_name` | Silver | `silver.si_customer_master` | `customer_name` | Optional descriptive field | Map from customer master |
| Gold | `gold.go_fct_credit_risk` | `branch_code` | Silver | `silver.si_rental_contracts` | `branch_code` | Branch should align to customer exposure through contracts/invoices | Derive from invoice-contract join |
| Gold | `gold.go_fct_credit_risk` | `customer_status` | Silver | `silver.si_customer_master` | `customer_status` | Must align to valid customer status domain | Direct map from customer master |
| Gold | `gold.go_fct_credit_risk` | `outstanding_ar` | Silver | `silver.si_invoices` | `invoice_amount` | Must be valid numeric | Sum invoice amounts by customer and branch |
| Gold | `gold.go_fct_credit_risk` | `credit_limit` | Silver | `silver.si_customer_master` | `credit_limit` | Mandatory for utilization logic; must be non-negative | Direct map from customer master |
| Gold | `gold.go_fct_credit_risk` | `credit_utilization_percentage` | Silver | `silver.si_invoices`, `silver.si_customer_master` | `invoice_amount`, `credit_limit` | Denominator must be non-zero | `outstanding_ar / credit_limit` when `credit_limit <> 0` |
| Gold | `gold.go_fct_credit_risk` | `customers_over_limit_count` | Silver | `silver.si_invoices`, `silver.si_customer_master` | `invoice_amount`, `credit_limit` | Customer conformance required before aggregation | `CASE WHEN outstanding_ar > credit_limit THEN 1 ELSE 0 END` |
| Gold | `gold.go_fct_credit_risk` | `customers_over_limit_amount` | Silver | `silver.si_invoices`, `silver.si_customer_master` | `invoice_amount`, `credit_limit` | Must not produce negative over-limit amount | `CASE WHEN outstanding_ar > credit_limit THEN outstanding_ar - credit_limit ELSE 0 END` |
| Gold | `gold.go_fct_credit_risk` | `suspended_customers_with_open_exposure` | Silver | `silver.si_customer_master`, `silver.si_invoices`, `silver.si_rental_contracts` | `customer_status`, `invoice_amount`, `contract_status` | Requires consistent status and exposure logic | `CASE WHEN upper(customer_status)='SUSPENDED' AND (outstanding_ar > 0 OR open_contract_count > 0) THEN 1 ELSE 0 END` |
| Gold | `gold.go_fct_credit_risk` | `ar_90_plus_amount_by_customer` | Silver | `silver.si_invoices` | `invoice_amount`, `aging_bucket`, `due_date` | Must reconcile with aging rules | Sum invoice amount for derived `90+` bucket by customer |
| Gold | `gold.go_fct_credit_risk` | `open_contract_count` | Silver | `silver.si_rental_contracts` | `contract_status`, `contract_id` | Contract statuses must be standardized | Count contracts where `upper(contract_status)='OPEN'` |
| Gold | `gold.go_fct_credit_risk` | `open_contract_value` | Silver | `silver.si_rental_contracts` | `daily_rate`, `contract_start_date`, `contract_end_date`, `contract_status` | Contract dates must be valid; negative durations should be treated as zero | Sum `daily_rate * GREATEST(DATEDIFF(contract_end_date, contract_start_date),0)` for open contracts |
| Gold | `gold.go_fct_credit_risk` | `load_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate processing timestamp |
| Gold | `gold.go_fct_credit_risk` | `update_date` | Silver | Derived | `current_timestamp()` | System-generated | Populate processing timestamp |
| Gold | `gold.go_fct_credit_risk` | `source_system` | Silver | Derived | constant | Must be populated for lineage | Set to `'silver_to_gold'` or enterprise lineage value |

## 6. Fact-Dimension Relationship Mapping

| Gold Fact Table | Fact Field | Dimension Relationship | Source Derivation / Join Logic |
|---|---|---|---|
| `gold.go_fct_rental_revenue` | `reporting_date` | Date dimension | Resolve to conformed date dimension by invoice date |
| `gold.go_fct_rental_revenue` | `branch_code` | Branch dimension | Derived from rental contracts |
| `gold.go_fct_rental_revenue` | `sales_rep_id` | Sales rep dimension | Derived from contract sales rep and branch employee lookup |
| `gold.go_fct_rental_revenue` | `contract_id` | Contract dimension | Derived from rental contracts |
| `gold.go_fct_rental_revenue` | `customer_id` | Customer dimension | Derived from customer master |
| `gold.go_fct_ar_aging` | `customer_id` | Customer dimension | Derived from customer master |
| `gold.go_fct_ar_aging` | `collector_id` | Collector dimension | Derived from branch employee by collector role |
| `gold.go_fct_ar_aging` | `aging_bucket` | Aging bucket code dimension | Derived and validated from due date logic |
| `gold.go_fct_cash_application` | `invoice_id` | Invoice dimension | Derived from cash receipts and invoice linkage |
| `gold.go_fct_cash_application` | `customer_id` | Customer dimension | Derived from customer master |
| `gold.go_fct_cash_application` | `branch_code` | Branch dimension | Derived through invoice-contract chain |
| `gold.go_fct_credit_risk` | `customer_id` | Customer dimension | Derived from customer master |
| `gold.go_fct_credit_risk` | `branch_code` | Branch dimension | Derived from contract / invoice exposure alignment |

## 7. Validation Rules and Cleansing Logic

| Rule Category | Rule | Handling Strategy |
|---|---|---|
| Mandatory fields | `customer_id`, `invoice_id`, `invoice_amount`, `due_date`, `credit_limit`, `branch_code`, and reporting dates should not be null where required by target grain | Reject to data quality workflow or quarantine invalid rows |
| Numeric standardization | Financial values should use fixed decimal precision | Cast to `DECIMAL(18,2)` or equivalent Spark decimal type |
| Credit memo sign standardization | Credit memo amounts must be stored as negative | Convert to `-ABS(invoice_amount)` for credit memos |
| Negative value protection | Standard invoice and payment amounts should not be negative unless business type explicitly allows it | Reject contradictory records or standardize where rule-driven |
| Aging bucket validation | Only `0-30`, `31-60`, `61-90`, `90+` are valid | Recalculate from due date; if impossible, quarantine row |
| Divide-by-zero protection | ADR, DSO, CEI, utilization, on-time percentages, and memo rates must not divide by zero | Return null and log warning when denominator is zero |
| Duplicate handling | Customer conformance required before credit risk aggregation | Deduplicate on business key before final aggregation |
| Missing descriptive attributes | Missing names such as customer or collector names should not block metric load unless required by business | Load with null description and raise warning if needed |
| Contract duration normalization | Negative contract duration should not drive metrics | Use `GREATEST(DATEDIFF(end_date,start_date),0)` |
| Currency and unit normalization | If multiple currencies or units appear in future sources, they must be standardized before Gold aggregation | Apply conversion reference data before final fact load |

## 8. Explanations for Complex Calculations and Business Rules

### 8.1 Net Billings
Net billings are calculated as gross billings plus credit memo amount. Since credit memo amounts are standardized as negative values, the reconciliation is transparent and audit-friendly.

### 8.2 Average Daily Rate
Average daily rate is based on rental revenue divided by the contract duration in days. To avoid invalid outputs, the denominator is only used when the contract duration is greater than zero.

### 8.3 Aging Bucket Assignment
Aging bucket values must be standardized based on the difference between snapshot date and due date. Even if an aging bucket already exists in Silver, recalculation is preferred when invalid or inconsistent values are detected.

### 8.4 DSO and Best Possible DSO
DSO and best possible DSO must use a consistent reporting period. These metrics should not be computed using mismatched invoice and snapshot periods. The denominator must always be checked before division.

### 8.5 Collection Effectiveness Index
CEI should be computed within the same reporting window using beginning AR, credit sales, ending total AR, and ending current AR. If the denominator is zero, the value should return null instead of producing an invalid metric.

### 8.6 Credit Utilization and Over-Limit Logic
Credit utilization is the ratio of outstanding AR to customer credit limit. Over-limit flags and amounts are derived only after exposure is aggregated to a conformed customer grain.

### 8.7 Suspended Customer Exposure
A customer marked as suspended but still carrying open AR or open contracts is flagged for risk review. This rule supports finance and collections controls.

## 9. Databricks / PySpark Compatibility Notes
- Implement joins using DataFrame joins or Spark SQL with Delta tables.
- Use `when`, `otherwise`, `coalesce`, `abs`, `greatest`, `datediff`, `lag`, and window functions for KPI logic.
- Cast numeric outputs to Spark decimal types for stable financial precision.
- Load valid facts to Gold Delta tables and route validation failures to error handling tables.
- Use partitioning and optimization strategies consistent with enterprise Gold model standards.

## 10. Example PySpark-Oriented Transformation Patterns

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

revenue_df = (
    invoices.alias("i")
    .join(contracts.alias("c"), F.col("i.contract_id") == F.col("c.contract_id"), "inner")
    .join(customers.alias("cm"), F.col("i.customer_id") == F.col("cm.customer_id"), "inner")
    .withColumn(
        "credit_memo_amount",
        F.when(F.upper(F.col("i.invoice_type")) == F.lit("CREDIT_MEMO"), -F.abs(F.col("i.invoice_amount"))).otherwise(F.lit(0))
    )
    .withColumn(
        "gross_billings",
        F.when(F.upper(F.col("i.invoice_type")) != F.lit("CREDIT_MEMO"), F.col("i.invoice_amount")).otherwise(F.lit(0))
    )
)
```

```python
ar_df = (
    invoices
    .withColumn("snapshot_date", F.current_date())
    .withColumn(
        "aging_bucket",
        F.when(F.datediff(F.col("snapshot_date"), F.col("due_date")).between(0, 30), F.lit("0-30"))
         .when(F.datediff(F.col("snapshot_date"), F.col("due_date")).between(31, 60), F.lit("31-60"))
         .when(F.datediff(F.col("snapshot_date"), F.col("due_date")).between(61, 90), F.lit("61-90"))
         .otherwise(F.lit("90+"))
    )
)
```

## 11. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Gold_Fact_Transformation_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Fact_Transformation_Data_Mapping/Databricks_Gold_Fact_Transformation_Data_Mapping_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Data_Mapping
pipelineID : 14676