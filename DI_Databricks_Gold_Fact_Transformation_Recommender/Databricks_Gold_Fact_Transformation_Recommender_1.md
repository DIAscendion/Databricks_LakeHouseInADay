_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold fact transformation recommendations for Rental Revenue-to-Cash reporting across rental revenue, AR aging, cash application, and credit risk facts.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Fact Transformation Recommender

## 1. Overview
This document provides Databricks Gold fact transformation recommendations for the Rental Revenue-to-Cash domain. It is derived from the conceptual model, data constraints, Silver physical model, and Gold physical model. The recommendations focus only on Gold fact tables and define how Silver-layer data should be standardized, joined, aggregated, validated, and loaded into Gold fact structures with business traceability.

## 2. Input Analysis

| Input File | Purpose | Fact Transformation Impact |
|---|---|---|
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Defines business entities, KPIs, and cross-domain fact expectations | Drives metric definitions for rental revenue, AR aging, cash application, and credit risk facts |
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Defines mandatory fields, business rules, dependencies, integrity rules, and valid domains | Drives data quality rules, denominator checks, reconciliation rules, and referential expectations |
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Defines available Silver source tables and source columns | Determines source-to-target mappings and SQL transformation feasibility |
| `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt` | Defines Gold fact target tables and expected columns | Determines final Gold fact table grain and load targets |

## 3. Fact Tables Identified from Gold Physical Model

| Gold Fact Table | Grain | Core Measures | Primary Source Tables |
|---|---|---|---|
| `gold.go_fct_rental_revenue` | One row per reporting date, contract, branch, sales rep, equipment class, customer | `rental_revenue`, `gross_billings`, `credit_memo_amount`, `net_billings`, `invoice_count`, `average_daily_rate`, `revenue_per_contract`, `credit_memo_rate`, `trend_value` | `silver.si_invoices`, `silver.si_rental_contracts`, `silver.si_customer_master`, `silver.si_branch_employee` |
| `gold.go_fct_ar_aging` | One row per snapshot date, customer, collector, branch, aging bucket | `total_ar_outstanding`, `ar_90_plus_amount`, `ar_90_plus_percentage`, `best_possible_dso`, `dso`, `dso_trend`, `ar_aging_by_bucket` | `silver.si_invoices`, `silver.si_customer_master`, `silver.si_branch_employee` |
| `gold.go_fct_cash_application` | One row per reporting date, payment application, customer, invoice, collector, branch | `cash_collected`, `collection_effectiveness_index`, `average_days_to_pay`, `invoices_paid_on_time_percentage`, `unapplied_cash_amount`, `unapplied_cash_percentage`, `payment_amount` | `silver.si_cash_receipts`, `silver.si_invoices`, `silver.si_customer_master`, `silver.si_branch_employee` |
| `gold.go_fct_credit_risk` | One row per snapshot date, customer, branch | `outstanding_ar`, `credit_limit`, `credit_utilization_percentage`, `customers_over_limit_count`, `customers_over_limit_amount`, `suspended_customers_with_open_exposure`, `ar_90_plus_amount_by_customer`, `open_contract_count`, `open_contract_value` | `silver.si_invoices`, `silver.si_customer_master`, `silver.si_rental_contracts`, `silver.si_branch_employee` |

## 4. Silver Source Columns Relevant to Fact Processing

| Silver Table | Relevant Columns Used in Fact Logic |
|---|---|
| `silver.si_rental_contracts` | `contract_id`, `customer_id`, `branch_code`, `sales_rep_id`, `equipment_class`, `contract_start_date`, `contract_end_date`, `contract_status`, `daily_rate` |
| `silver.si_invoices` | `invoice_id`, `contract_id`, `customer_id`, `invoice_date`, `due_date`, `invoice_amount`, `tax_amount`, `invoice_type`, `currency`, `aging_bucket`, `days_past_due` |
| `silver.si_cash_receipts` | `receipt_id`, `invoice_id`, `customer_id`, `receipt_date`, `payment_amount`, `payment_method`, `match_status`, `unapplied_payment_amount` |
| `silver.si_customer_master` | `customer_id`, `customer_name`, `credit_terms`, `credit_limit`, `customer_since`, `customer_status`, `over_limit_indicator` |
| `silver.si_branch_employee` | `employee_id`, `employee_name`, `role`, `branch_code`, `region`, `collector_id`, `effective_date` |

## 5. Recommended Transformation Rules for Fact Tables

### 5.1 Transformation Rules for `gold.go_fct_rental_revenue`

#### Rule 1: Rental Revenue Base Fact Assembly
- **Description:** Assemble rental revenue fact rows by joining invoice, contract, customer, and branch-sales context at the reporting date and contract grain.
- **Rationale:** The conceptual model requires branch, region, contract, customer, and sales rep aligned revenue reporting. The Gold physical model defines these descriptive columns in the fact.
- **Traceability:**
  - Conceptual: Fact Rental Revenue, Invoice, Contract, Branch, Sales Rep
  - Constraints: Branch/region required, invoice amount required, drill-through reconciliation required
  - Silver: `silver.si_invoices`, `silver.si_rental_contracts`, `silver.si_customer_master`, `silver.si_branch_employee`
  - Gold: `gold.go_fct_rental_revenue`
- **SQL Example:**
```sql
WITH sales_rep_dim AS (
  SELECT
    employee_id AS sales_rep_id,
    employee_name AS sales_rep_name,
    branch_code,
    region
  FROM silver.si_branch_employee
  WHERE lower(role) = 'sales rep'
),
base AS (
  SELECT
    i.invoice_date AS reporting_date,
    c.branch_code,
    sr.region AS region_name,
    c.sales_rep_id,
    sr.sales_rep_name,
    c.equipment_class,
    c.equipment_class AS equipment_class_name,
    c.contract_id,
    c.contract_status,
    cm.customer_id,
    cm.customer_name,
    i.invoice_id,
    i.invoice_amount,
    i.invoice_type,
    c.daily_rate
  FROM silver.si_invoices i
  INNER JOIN silver.si_rental_contracts c
    ON i.contract_id = c.contract_id
  INNER JOIN silver.si_customer_master cm
    ON i.customer_id = cm.customer_id
  LEFT JOIN sales_rep_dim sr
    ON c.sales_rep_id = sr.sales_rep_id
   AND c.branch_code = sr.branch_code
)
SELECT * FROM base;
```

#### Rule 2: Gross Billings, Credit Memo, and Net Billings Standardization
- **Description:** Standardize invoice-derived billing measures so gross billings remain positive, credit memo amounts remain negative, and net billings reconcile to gross billings minus credit memos.
- **Rationale:** Constraints explicitly require net billings reconciliation and negative credit memo amount behavior.
- **Traceability:**
  - Conceptual KPI: Gross Billings, Net Billings, Credit Memo Rate
  - Constraints: Net billings must reconcile; credit memo amount must be negative
  - Gold physical fact columns: `gross_billings`, `credit_memo_amount`, `net_billings`
- **SQL Example:**
```sql
SELECT
  invoice_date AS reporting_date,
  contract_id,
  customer_id,
  SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END) AS gross_billings,
  SUM(CASE WHEN upper(invoice_type) = 'CREDIT_MEMO' THEN -ABS(invoice_amount) ELSE 0 END) AS credit_memo_amount,
  SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END)
    + SUM(CASE WHEN upper(invoice_type) = 'CREDIT_MEMO' THEN -ABS(invoice_amount) ELSE 0 END) AS net_billings
FROM silver.si_invoices
GROUP BY invoice_date, contract_id, customer_id;
```

#### Rule 3: Average Daily Rate and Revenue per Contract Calculation
- **Description:** Calculate ADR and revenue per contract only when denominator values are non-zero and only for valid contract activity.
- **Rationale:** Constraints require denominator checks and conceptual KPI definitions depend on rental revenue and billed rental days or contract counts.
- **Traceability:**
  - Conceptual KPI: ADR, Revenue per Contract
  - Constraints: ADR depends on rental revenue and billed rental days; rate-based calculations require non-zero denominator
  - Gold physical model includes `average_daily_rate`, `revenue_per_contract`
- **SQL Example:**
```sql
SELECT
  invoice_date AS reporting_date,
  contract_id,
  SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END) AS rental_revenue,
  CASE
    WHEN DATEDIFF(contract_end_date, contract_start_date) > 0
      THEN SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END)
           / DATEDIFF(contract_end_date, contract_start_date)
    ELSE NULL
  END AS average_daily_rate,
  CASE
    WHEN COUNT(DISTINCT contract_id) > 0
      THEN SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END)
           / COUNT(DISTINCT contract_id)
    ELSE NULL
  END AS revenue_per_contract
FROM silver.si_invoices i
JOIN silver.si_rental_contracts c
  ON i.contract_id = c.contract_id
WHERE COALESCE(c.contract_status, 'UNKNOWN') <> 'CANCELLED'
GROUP BY invoice_date, contract_id, contract_start_date, contract_end_date;
```

#### Rule 4: Credit Memo Rate and Revenue Trend Derivation
- **Description:** Derive credit memo rate as credit memos over gross billings and derive trend values using period-over-period comparison.
- **Rationale:** The conceptual model calls out both credit memo rate and trend value as required revenue analytics.
- **Traceability:**
  - Conceptual KPI: Credit Memo Rate, Trend Value
  - Constraints: Rate-based calculations must be non-zero denominator safe; period consistency required
  - Gold physical fact columns: `credit_memo_rate`, `trend_value`
- **SQL Example:**
```sql
WITH revenue_period AS (
  SELECT
    invoice_date AS reporting_date,
    branch_code,
    SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END) AS gross_billings,
    SUM(CASE WHEN upper(invoice_type) = 'CREDIT_MEMO' THEN ABS(invoice_amount) ELSE 0 END) AS credit_memo_abs,
    SUM(CASE WHEN upper(invoice_type) <> 'CREDIT_MEMO' THEN invoice_amount ELSE 0 END)
      - SUM(CASE WHEN upper(invoice_type) = 'CREDIT_MEMO' THEN ABS(invoice_amount) ELSE 0 END) AS net_billings
  FROM silver.si_invoices i
  JOIN silver.si_rental_contracts c
    ON i.contract_id = c.contract_id
  GROUP BY invoice_date, branch_code
)
SELECT
  reporting_date,
  branch_code,
  CASE WHEN gross_billings <> 0 THEN credit_memo_abs / gross_billings ELSE NULL END AS credit_memo_rate,
  net_billings - LAG(net_billings) OVER (PARTITION BY branch_code ORDER BY reporting_date) AS trend_value
FROM revenue_period;
```

### 5.2 Transformation Rules for `gold.go_fct_ar_aging`

#### Rule 5: Aging Bucket Standardization
- **Description:** Standardize AR aging bucket assignment using due date and snapshot date and restrict output to the allowed bucket set `0-30`, `31-60`, `61-90`, and `90+`.
- **Rationale:** Constraints explicitly require fixed aging bucket categories and conceptual AR reporting depends on bucketed exposure.
- **Traceability:**
  - Conceptual: Fact AR Aging, Days Past Due, Aging Bucket
  - Constraints: Aging buckets must use only defined categories; bucket is based on due date and snapshot date
  - Silver source columns: `due_date`, `days_past_due`, `aging_bucket`
  - Gold target: `gold.go_fct_ar_aging.aging_bucket`
- **SQL Example:**
```sql
SELECT
  CURRENT_DATE() AS snapshot_date,
  i.customer_id,
  i.invoice_id,
  CASE
    WHEN DATEDIFF(CURRENT_DATE(), i.due_date) BETWEEN 0 AND 30 THEN '0-30'
    WHEN DATEDIFF(CURRENT_DATE(), i.due_date) BETWEEN 31 AND 60 THEN '31-60'
    WHEN DATEDIFF(CURRENT_DATE(), i.due_date) BETWEEN 61 AND 90 THEN '61-90'
    WHEN DATEDIFF(CURRENT_DATE(), i.due_date) > 90 THEN '90+'
    ELSE '0-30'
  END AS aging_bucket,
  GREATEST(i.invoice_amount, 0) AS ar_aging_by_bucket
FROM silver.si_invoices i;
```

#### Rule 6: Total AR Outstanding and 90+ Exposure Calculation
- **Description:** Aggregate receivable balances into customer and aging bucket snapshots and derive total AR outstanding plus 90+ concentration.
- **Rationale:** The conceptual model and KPI list require total AR, AR 90+ amount, and AR 90+ percentage.
- **Traceability:**
  - Conceptual KPI: Total AR Outstanding, AR 90+ Amount, AR 90+ %
  - Constraints: Aging bucket totals must reconcile to total AR outstanding; AR 90+ % depends on 90+ and total AR
  - Gold target: `gold.go_fct_ar_aging`
- **SQL Example:**
```sql
WITH ar_base AS (
  SELECT
    CURRENT_DATE() AS snapshot_date,
    i.customer_id,
    cm.customer_name,
    be.branch_code,
    be.employee_name AS collector_name,
    be.collector_id,
    CASE
      WHEN DATEDIFF(CURRENT_DATE(), i.due_date) BETWEEN 0 AND 30 THEN '0-30'
      WHEN DATEDIFF(CURRENT_DATE(), i.due_date) BETWEEN 31 AND 60 THEN '31-60'
      WHEN DATEDIFF(CURRENT_DATE(), i.due_date) BETWEEN 61 AND 90 THEN '61-90'
      WHEN DATEDIFF(CURRENT_DATE(), i.due_date) > 90 THEN '90+'
      ELSE '0-30'
    END AS aging_bucket,
    i.invoice_amount
  FROM silver.si_invoices i
  JOIN silver.si_customer_master cm
    ON i.customer_id = cm.customer_id
  LEFT JOIN silver.si_branch_employee be
    ON be.branch_code = (
      SELECT c.branch_code FROM silver.si_rental_contracts c WHERE c.contract_id = i.contract_id LIMIT 1
    )
   AND lower(be.role) = 'collector'
)
SELECT
  snapshot_date,
  customer_id,
  customer_name,
  branch_code,
  collector_id,
  collector_name,
  aging_bucket,
  SUM(invoice_amount) OVER (PARTITION BY snapshot_date, customer_id) AS total_ar_outstanding,
  SUM(CASE WHEN aging_bucket = '90+' THEN invoice_amount ELSE 0 END) OVER (PARTITION BY snapshot_date, customer_id) AS ar_90_plus_amount,
  CASE
    WHEN SUM(invoice_amount) OVER (PARTITION BY snapshot_date, customer_id) <> 0 THEN
      SUM(CASE WHEN aging_bucket = '90+' THEN invoice_amount ELSE 0 END) OVER (PARTITION BY snapshot_date, customer_id)
      / SUM(invoice_amount) OVER (PARTITION BY snapshot_date, customer_id)
    ELSE NULL
  END AS ar_90_plus_percentage,
  SUM(invoice_amount) AS ar_aging_by_bucket
FROM ar_base
GROUP BY snapshot_date, customer_id, customer_name, branch_code, collector_id, collector_name, aging_bucket;
```

#### Rule 7: DSO and Best Possible DSO Calculation
- **Description:** Compute DSO and best possible DSO using a consistent reporting period and non-zero denominator logic.
- **Rationale:** Constraints explicitly define dependencies for DSO and best possible DSO.
- **Traceability:**
  - Conceptual KPI: DSO, Best Possible DSO, DSO Trend
  - Constraints: DSO depends on total AR outstanding, total credit sales, and number of days in period; same reporting period must be used consistently
  - Gold target columns: `dso`, `best_possible_dso`, `dso_trend`
- **SQL Example:**
```sql
WITH period_sales AS (
  SELECT
    DATE_TRUNC('MONTH', invoice_date) AS reporting_month,
    customer_id,
    SUM(invoice_amount) AS total_credit_sales,
    DAY(LAST_DAY(invoice_date)) AS days_in_period
  FROM silver.si_invoices
  WHERE upper(invoice_type) <> 'CREDIT_MEMO'
  GROUP BY DATE_TRUNC('MONTH', invoice_date), customer_id, DAY(LAST_DAY(invoice_date))
),
ar_snapshot AS (
  SELECT
    DATE_TRUNC('MONTH', CURRENT_DATE()) AS reporting_month,
    customer_id,
    SUM(invoice_amount) AS total_ar_outstanding,
    SUM(CASE WHEN aging_bucket IN ('31-60','61-90','90+') THEN invoice_amount ELSE 0 END) AS best_possible_numerator
  FROM silver.si_invoices
  GROUP BY DATE_TRUNC('MONTH', CURRENT_DATE()), customer_id
)
SELECT
  a.reporting_month,
  a.customer_id,
  CASE WHEN p.total_credit_sales <> 0 THEN (a.total_ar_outstanding / p.total_credit_sales) * p.days_in_period ELSE NULL END AS dso,
  CASE WHEN p.total_credit_sales <> 0 THEN (a.best_possible_numerator / p.total_credit_sales) * p.days_in_period ELSE NULL END AS best_possible_dso,
  (CASE WHEN p.total_credit_sales <> 0 THEN (a.total_ar_outstanding / p.total_credit_sales) * p.days_in_period ELSE NULL END)
    - LAG(CASE WHEN p.total_credit_sales <> 0 THEN (a.total_ar_outstanding / p.total_credit_sales) * p.days_in_period ELSE NULL END)
      OVER (PARTITION BY a.customer_id ORDER BY a.reporting_month) AS dso_trend
FROM ar_snapshot a
LEFT JOIN period_sales p
  ON a.reporting_month = p.reporting_month
 AND a.customer_id = p.customer_id;
```

### 5.3 Transformation Rules for `gold.go_fct_cash_application`

#### Rule 8: Cash Collection and Match Status Standardization
- **Description:** Standardize payment records into applied and unapplied categories and preserve unapplied cash explicitly in the Gold fact.
- **Rationale:** Constraints require applied versus unapplied distinction and conceptual reporting requires unapplied cash metrics.
- **Traceability:**
  - Conceptual: Fact Cash Application, Match Status, Unapplied Payment Amount
  - Constraints: Payment reporting must distinguish applied and unapplied status explicitly; unapplied cash must be separately reported
  - Silver source: `silver.si_cash_receipts.match_status`, `unapplied_payment_amount`
  - Gold target: `gold.go_fct_cash_application`
- **SQL Example:**
```sql
SELECT
  r.receipt_date AS reporting_date,
  c.branch_code,
  cm.customer_id,
  cm.customer_name,
  r.invoice_id,
  r.payment_method,
  CASE WHEN upper(COALESCE(r.match_status, 'UNAPPLIED')) = 'APPLIED' THEN 'APPLIED' ELSE 'UNAPPLIED' END AS match_status,
  r.payment_amount AS cash_collected,
  COALESCE(r.unapplied_payment_amount, 0) AS unapplied_cash_amount,
  r.payment_amount,
  r.receipt_date AS payment_date
FROM silver.si_cash_receipts r
LEFT JOIN silver.si_invoices i
  ON r.invoice_id = i.invoice_id
LEFT JOIN silver.si_rental_contracts c
  ON i.contract_id = c.contract_id
LEFT JOIN silver.si_customer_master cm
  ON r.customer_id = cm.customer_id;
```

#### Rule 9: Average Days to Pay and On-Time Payment Percentage
- **Description:** Calculate payment timing metrics using invoice and receipt dates and evaluate whether payment occurred on or before due date.
- **Rationale:** Conceptual KPIs require average days to pay and invoices paid on time percentage.
- **Traceability:**
  - Conceptual KPI: Average Days to Pay, % Invoices Paid On Time
  - Constraints: Average days to pay depends on payment date and invoice date; denominators must be non-zero
  - Gold target columns: `average_days_to_pay`, `invoices_paid_on_time_percentage`
- **SQL Example:**
```sql
SELECT
  r.receipt_date AS reporting_date,
  r.customer_id,
  r.invoice_id,
  AVG(DATEDIFF(r.receipt_date, i.invoice_date)) AS average_days_to_pay,
  CASE
    WHEN COUNT(*) <> 0 THEN
      SUM(CASE WHEN r.receipt_date <= i.due_date THEN 1 ELSE 0 END) / COUNT(*)
    ELSE NULL
  END AS invoices_paid_on_time_percentage
FROM silver.si_cash_receipts r
JOIN silver.si_invoices i
  ON r.invoice_id = i.invoice_id
WHERE upper(COALESCE(r.match_status, 'UNAPPLIED')) = 'APPLIED'
GROUP BY r.receipt_date, r.customer_id, r.invoice_id;
```

#### Rule 10: Unapplied Cash Percentage and Collection Effectiveness Index
- **Description:** Compute unapplied cash percentage from total payments and compute CEI within the same reporting window.
- **Rationale:** Constraints explicitly define dependencies for unapplied cash percentage and CEI.
- **Traceability:**
  - Conceptual KPI: Collection Effectiveness Index, Unapplied Cash %
  - Constraints: CEI depends on beginning AR, credit sales, ending total AR, and ending current AR using same window; unapplied cash % depends on unapplied and total payments
  - Gold target columns: `collection_effectiveness_index`, `unapplied_cash_percentage`
- **SQL Example:**
```sql
WITH payment_window AS (
  SELECT
    DATE_TRUNC('MONTH', receipt_date) AS reporting_month,
    customer_id,
    SUM(payment_amount) AS total_payments,
    SUM(COALESCE(unapplied_payment_amount, 0)) AS unapplied_cash
  FROM silver.si_cash_receipts
  GROUP BY DATE_TRUNC('MONTH', receipt_date), customer_id
),
cei_window AS (
  SELECT
    DATE_TRUNC('MONTH', invoice_date) AS reporting_month,
    customer_id,
    SUM(invoice_amount) AS credit_sales,
    SUM(CASE WHEN aging_bucket = '0-30' THEN invoice_amount ELSE 0 END) AS ending_current_ar,
    SUM(invoice_amount) AS ending_total_ar
  FROM silver.si_invoices
  GROUP BY DATE_TRUNC('MONTH', invoice_date), customer_id
)
SELECT
  p.reporting_month,
  p.customer_id,
  CASE WHEN p.total_payments <> 0 THEN p.unapplied_cash / p.total_payments ELSE NULL END AS unapplied_cash_percentage,
  CASE WHEN (c.credit_sales - c.ending_current_ar) <> 0
    THEN ((c.credit_sales - c.ending_total_ar) / (c.credit_sales - c.ending_current_ar))
    ELSE NULL
  END AS collection_effectiveness_index
FROM payment_window p
LEFT JOIN cei_window c
  ON p.reporting_month = c.reporting_month
 AND p.customer_id = c.customer_id;
```

### 5.4 Transformation Rules for `gold.go_fct_credit_risk`

#### Rule 11: Customer Outstanding Exposure and Credit Utilization
- **Description:** Aggregate customer AR exposure and calculate credit utilization percentage against customer credit limit.
- **Rationale:** Conceptual and constraint documents explicitly require outstanding AR and credit utilization.
- **Traceability:**
  - Conceptual KPI: Outstanding AR, Credit Utilization %
  - Constraints: Credit utilization depends on outstanding AR and credit limit; credit limit is mandatory
  - Silver source: `silver.si_invoices`, `silver.si_customer_master`
  - Gold target: `gold.go_fct_credit_risk`
- **SQL Example:**
```sql
SELECT
  CURRENT_DATE() AS snapshot_date,
  cm.customer_id,
  cm.customer_name,
  c.branch_code,
  cm.customer_status,
  SUM(i.invoice_amount) AS outstanding_ar,
  cm.credit_limit,
  CASE WHEN cm.credit_limit <> 0 THEN SUM(i.invoice_amount) / cm.credit_limit ELSE NULL END AS credit_utilization_percentage
FROM silver.si_customer_master cm
LEFT JOIN silver.si_invoices i
  ON cm.customer_id = i.customer_id
LEFT JOIN silver.si_rental_contracts c
  ON i.contract_id = c.contract_id
GROUP BY CURRENT_DATE(), cm.customer_id, cm.customer_name, c.branch_code, cm.customer_status, cm.credit_limit;
```

#### Rule 12: Over-Limit Customers and Exposure Amounts
- **Description:** Identify customers exceeding their credit limits and derive both customer counts and over-limit amounts.
- **Rationale:** The conceptual KPI set requires customers over limit count and amount.
- **Traceability:**
  - Conceptual KPI: Customers Over Limit Count, Customers Over Limit Amount
  - Constraints: Customer exposure reporting must use a single conformed customer record after deduplication
  - Gold target columns: `customers_over_limit_count`, `customers_over_limit_amount`
- **SQL Example:**
```sql
WITH exposure AS (
  SELECT
    cm.customer_id,
    cm.credit_limit,
    SUM(i.invoice_amount) AS outstanding_ar
  FROM silver.si_customer_master cm
  LEFT JOIN silver.si_invoices i
    ON cm.customer_id = i.customer_id
  GROUP BY cm.customer_id, cm.credit_limit
)
SELECT
  customer_id,
  CASE WHEN outstanding_ar > credit_limit THEN 1 ELSE 0 END AS customers_over_limit_count,
  CASE WHEN outstanding_ar > credit_limit THEN outstanding_ar - credit_limit ELSE 0 END AS customers_over_limit_amount
FROM exposure;
```

#### Rule 13: Suspended Customers with Open Exposure
- **Description:** Flag suspended customers that still carry open AR or open contracts.
- **Rationale:** This is an explicit conceptual KPI and constraint dependency.
- **Traceability:**
  - Conceptual KPI: Suspended Customers with Open Exposure
  - Constraints: Depends on customer status, outstanding AR, and open contracts
  - Gold target column: `suspended_customers_with_open_exposure`
- **SQL Example:**
```sql
WITH customer_exposure AS (
  SELECT
    cm.customer_id,
    cm.customer_status,
    SUM(COALESCE(i.invoice_amount, 0)) AS outstanding_ar,
    SUM(CASE WHEN upper(COALESCE(c.contract_status, 'CLOSED')) = 'OPEN' THEN 1 ELSE 0 END) AS open_contract_count
  FROM silver.si_customer_master cm
  LEFT JOIN silver.si_invoices i
    ON cm.customer_id = i.customer_id
  LEFT JOIN silver.si_rental_contracts c
    ON cm.customer_id = c.customer_id
  GROUP BY cm.customer_id, cm.customer_status
)
SELECT
  customer_id,
  CASE
    WHEN upper(customer_status) = 'SUSPENDED' AND (outstanding_ar > 0 OR open_contract_count > 0) THEN 1
    ELSE 0
  END AS suspended_customers_with_open_exposure
FROM customer_exposure;
```

#### Rule 14: AR 90+ by Customer and Open Contract Exposure
- **Description:** Derive customer-level 90+ AR exposure and open contract counts and values for risk-oriented reporting.
- **Rationale:** Conceptual credit risk facts require customer-level aged exposure and open contract exposure.
- **Traceability:**
  - Conceptual KPI: AR 90+ Amount by Customer, Open Contract Count, Open Contract Value
  - Constraints: Suspended exposure and credit risk depend on AR and open contract measures
  - Gold target columns: `ar_90_plus_amount_by_customer`, `open_contract_count`, `open_contract_value`
- **SQL Example:**
```sql
WITH ar90 AS (
  SELECT
    customer_id,
    SUM(CASE WHEN aging_bucket = '90+' THEN invoice_amount ELSE 0 END) AS ar_90_plus_amount_by_customer
  FROM silver.si_invoices
  GROUP BY customer_id
),
open_contracts AS (
  SELECT
    customer_id,
    SUM(CASE WHEN upper(contract_status) = 'OPEN' THEN 1 ELSE 0 END) AS open_contract_count,
    SUM(CASE WHEN upper(contract_status) = 'OPEN' THEN COALESCE(daily_rate, 0) * GREATEST(DATEDIFF(contract_end_date, contract_start_date), 0) ELSE 0 END) AS open_contract_value
  FROM silver.si_rental_contracts
  GROUP BY customer_id
)
SELECT
  COALESCE(a.customer_id, o.customer_id) AS customer_id,
  a.ar_90_plus_amount_by_customer,
  o.open_contract_count,
  o.open_contract_value
FROM ar90 a
FULL OUTER JOIN open_contracts o
  ON a.customer_id = o.customer_id;
```

## 6. Fact-Dimension Mapping Recommendations

| Fact Table | Business Key / Link | Recommended Gold Dimension | Mapping Recommendation |
|---|---|---|---|
| `gold.go_fct_rental_revenue` | `reporting_date` | `gold.go_dim_date` | Resolve `reporting_date` to date dimension for reporting period conformance |
| `gold.go_fct_rental_revenue` | `branch_code` | `gold.go_dim_branch` | Use conformed branch mapping and retain branch attributes for reconciliation |
| `gold.go_fct_rental_revenue` | `sales_rep_id` | `gold.go_dim_sales_rep` | Align contracts to active sales rep assignment by branch |
| `gold.go_fct_rental_revenue` | `contract_id` | `gold.go_dim_contract` | Preserve contract grain and contract status |
| `gold.go_fct_ar_aging` | `customer_id` | `gold.go_dim_customer` | Use deduplicated conformed customer record |
| `gold.go_fct_ar_aging` | `collector_id` | `gold.go_dim_collector` | Align AR responsibility to collector assignment |
| `gold.go_fct_ar_aging` | `aging_bucket` | `gold.go_code_aging_bucket` | Validate against approved bucket code table |
| `gold.go_fct_cash_application` | `invoice_id` | `gold.go_dim_invoice` | Preserve invoice-level application traceability |
| `gold.go_fct_cash_application` | `customer_id` | `gold.go_dim_customer` | Use same conformed customer across AR and cash facts |
| `gold.go_fct_credit_risk` | `customer_id` | `gold.go_dim_customer` | Use customer conformance and deduplication before aggregation |
| `gold.go_fct_credit_risk` | `branch_code` | `gold.go_dim_branch` | Align exposure to valid branch hierarchy |

## 7. Data Quality, Missing Data, and Invalid Data Handling Rules

| Rule Name | Description | Handling Strategy |
|---|---|---|
| Mandatory Field Validation | Missing `customer_id`, `invoice_id`, `invoice_amount`, `due_date`, `credit_limit`, `branch_code`, or reporting date fields violate constraints | Reject to error table or quarantine before Gold load |
| Invalid Aging Bucket Correction | Any bucket outside `0-30`, `31-60`, `61-90`, `90+` is invalid | Recalculate from due date and snapshot date; if impossible, route to error table |
| Negative Amount Validation | Payment amount and standard invoice amount must be non-negative; credit memo amount must be negative | Standardize sign based on transaction type; reject contradictory records |
| Divide-by-Zero Protection | Rate-based KPIs such as DSO, ADR, CEI, and utilization require denominator checks | Return NULL and log data quality warning where needed |
| Overpayment Validation | Applied payment amounts must not exceed invoice amount | Flag and route to error handling workflow |
| Conformed Customer Deduplication | Same legal customer represented multiple times must be resolved before credit risk aggregation | Apply Silver conformance key before Gold aggregation |
| Branch Hierarchy Integrity | Branch must exist in organization hierarchy and be active for the selected date | Filter invalid branches and log exceptions |

## 8. Recommended Load Pattern
1. Read Silver source tables.
2. Conform customer, branch, sales rep, and collector context.
3. Derive invoice-level standardized measures and bucket assignments.
4. Create reusable intermediate views for revenue, receivables, payments, and exposure.
5. Aggregate each intermediate view to the grain required by the Gold fact table.
6. Validate business rules and reconciliation totals.
7. Insert valid rows into Gold fact tables.
8. Write failed validations to error/audit tables.

## 9. Example End-to-End Gold Fact Load Pattern
```sql
INSERT INTO gold.go_fct_rental_revenue
SELECT
  monotonically_increasing_id() AS fct_rental_revenue_sk,
  reporting_date,
  branch_code,
  MAX(branch_name) AS branch_name,
  region_name,
  sales_rep_id,
  MAX(sales_rep_name) AS sales_rep_name,
  equipment_class,
  MAX(equipment_class_name) AS equipment_class_name,
  contract_id,
  MAX(contract_status) AS contract_status,
  customer_id,
  MAX(customer_name) AS customer_name,
  SUM(rental_revenue) AS rental_revenue,
  SUM(gross_billings) AS gross_billings,
  SUM(credit_memo_amount) AS credit_memo_amount,
  SUM(net_billings) AS net_billings,
  SUM(invoice_count) AS invoice_count,
  AVG(average_daily_rate) AS average_daily_rate,
  AVG(revenue_per_contract) AS revenue_per_contract,
  AVG(credit_memo_rate) AS credit_memo_rate,
  AVG(trend_value) AS trend_value,
  current_timestamp() AS load_date,
  current_timestamp() AS update_date,
  'silver_to_gold' AS source_system
FROM some_validated_revenue_view
GROUP BY reporting_date, branch_code, region_name, sales_rep_id, equipment_class, contract_id, customer_id;
```

## 10. Traceability Matrix

| Gold Fact Metric / Rule | Conceptual Source | Constraints Source | Silver Source | Gold Target |
|---|---|---|---|---|
| Rental Revenue Base Assembly | Fact Rental Revenue, Contract, Invoice | Branch/region required, drill-through reconciliation | `si_invoices`, `si_rental_contracts`, `si_customer_master`, `si_branch_employee` | `go_fct_rental_revenue` |
| Net Billings Reconciliation | Gross Billings, Net Billings | Net = Gross - Credit Memo | `si_invoices` | `go_fct_rental_revenue` |
| ADR | Average Daily Rate | Denominator and dependency rule | `si_invoices`, `si_rental_contracts` | `go_fct_rental_revenue` |
| Revenue per Contract | Revenue per Contract | Denominator dependency rule | `si_invoices`, `si_rental_contracts` | `go_fct_rental_revenue` |
| Aging Bucket | AR Aging by Bucket | Allowed bucket domain | `si_invoices` | `go_fct_ar_aging` |
| AR 90+ % | AR 90+ % | 90+ / Total AR dependency | `si_invoices` | `go_fct_ar_aging` |
| DSO | DSO | DSO dependency and period consistency | `si_invoices` | `go_fct_ar_aging` |
| Cash Collected | Cash Collected | Payment amount mandatory | `si_cash_receipts` | `go_fct_cash_application` |
| Avg Days to Pay | Average Days to Pay | Payment date and invoice date dependency | `si_cash_receipts`, `si_invoices` | `go_fct_cash_application` |
| CEI | Collection Effectiveness Index | CEI same-window dependency | `si_cash_receipts`, `si_invoices` | `go_fct_cash_application` |
| Credit Utilization | Credit Utilization % | Outstanding AR / Credit Limit dependency | `si_invoices`, `si_customer_master` | `go_fct_credit_risk` |
| Over-Limit Exposure | Customers Over Limit | Conformed customer aggregation rule | `si_invoices`, `si_customer_master` | `go_fct_credit_risk` |
| Suspended Open Exposure | Suspended Customers with Open Exposure | Status + AR + open contracts dependency | `si_customer_master`, `si_invoices`, `si_rental_contracts` | `go_fct_credit_risk` |

## 11. Implementation Notes
- Use reusable staging views for invoice standardization and customer conformance.
- Ensure all rate metrics use decimal precision and null-safe denominator logic.
- Preserve business keys in fact tables for audit and drill-through reconciliation.
- Use Delta optimization and Z-Ordering as defined in the Gold physical model after fact loading.
- Maintain fact load audit records in process audit tables.
- Route failed business validations into error handling tables rather than silently dropping them.

## 12. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Gold_Fact_Transformation_Recommender_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Fact_Transformation_Recommender/Databricks_Gold_Fact_Transformation_Recommender_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_Transformation_Recommender
pipelineID : 14675