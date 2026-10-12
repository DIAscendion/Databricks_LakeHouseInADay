_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold aggregated transformation recommendations for Rental Revenue-to-Cash executive and billing aggregate tables.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Recommender

## 1. Overview
This document provides Databricks Gold aggregated transformation recommendations for the Rental Revenue-to-Cash domain. It is derived from the conceptual model, data constraints, Silver physical model, Gold physical model, and supporting Gold fact recommendations. The scope is limited to aggregated Gold tables and defines how Silver and Gold fact data should be transformed into governed executive and billing summary outputs.

## 2. Input Analysis

| Input File | Purpose | Aggregated Transformation Impact |
|---|---|---|
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Defines business entities, KPIs, executive scorecards, and billing reporting needs | Drives aggregate KPI definitions, grouping levels, and business rollups |
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Defines mandatory fields, aggregation dependencies, reconciliation rules, and denominator checks | Drives validation, grouping consistency, and safe KPI calculations |
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Defines available Silver source tables and relevant source columns | Determines source availability for pre-aggregation staging logic |
| `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt` | Defines Gold aggregate target tables and required columns | Determines aggregate grain, output schema, and load targets |
| `DI_Databricks_Gold_Fact_Transformation_Recommender/Databricks_Gold_Fact_Transformation_Recommender_1.md` | Defines upstream fact derivation logic used by aggregates | Supports traceable rollup from fact metrics into aggregate tables |

## 3. Aggregated Tables Identified from Gold Physical Model

| Gold Aggregate Table | Grain | Core Measures | Upstream Sources |
|---|---|---|---|
| `gold.go_agg_executive_health_score` | One row per reporting date, network level, region, branch, sales rep, collector | `overall_revenue_to_cash_health_score`, `rental_revenue`, `dso`, `ar_90_plus_percentage`, `collection_effectiveness_index`, `unapplied_cash_percentage`, `credit_utilization_percentage` | `gold.go_fct_rental_revenue`, `gold.go_fct_ar_aging`, `gold.go_fct_cash_application`, `gold.go_fct_credit_risk`, `gold.go_dim_branch` |
| `gold.go_agg_billing_performance` | One row per reporting date, region, branch, sales rep, equipment class | `gross_billings`, `credit_memo_amount`, `net_billings`, `rental_revenue`, `average_daily_rate`, `revenue_per_contract`, `credit_memo_rate`, `invoice_count` | `gold.go_fct_rental_revenue` |

## 4. Relevant Source Columns for Aggregate Processing

| Source Table | Relevant Columns |
|---|---|
| `gold.go_fct_rental_revenue` | `reporting_date`, `branch_code`, `branch_name`, `region_name`, `sales_rep_id`, `sales_rep_name`, `equipment_class`, `equipment_class_name`, `contract_id`, `customer_id`, `rental_revenue`, `gross_billings`, `credit_memo_amount`, `net_billings`, `invoice_count`, `average_daily_rate`, `revenue_per_contract`, `credit_memo_rate`, `trend_value` |
| `gold.go_fct_ar_aging` | `snapshot_date`, `customer_id`, `customer_name`, `branch_code`, `branch_name`, `collector_id`, `collector_name`, `aging_bucket`, `total_ar_outstanding`, `ar_90_plus_amount`, `ar_90_plus_percentage`, `best_possible_dso`, `dso`, `dso_trend`, `ar_aging_by_bucket` |
| `gold.go_fct_cash_application` | `reporting_date`, `branch_code`, `branch_name`, `collector_id`, `collector_name`, `customer_id`, `invoice_id`, `cash_collected`, `collection_effectiveness_index`, `average_days_to_pay`, `invoices_paid_on_time_percentage`, `unapplied_cash_amount`, `unapplied_cash_percentage`, `payment_amount` |
| `gold.go_fct_credit_risk` | `snapshot_date`, `customer_id`, `customer_name`, `branch_code`, `branch_name`, `customer_status`, `outstanding_ar`, `credit_limit`, `credit_utilization_percentage`, `customers_over_limit_count`, `customers_over_limit_amount`, `suspended_customers_with_open_exposure`, `ar_90_plus_amount_by_customer`, `open_contract_count`, `open_contract_value` |
| `gold.go_dim_branch` | `branch_code`, `branch_name`, `region_name`, `organization_hierarchy_name`, `network_level`, `branch_status` |

## 5. Aggregation Methods and Business Logic Summary

| Metric Area | Aggregation Method | Notes |
|---|---|---|
| Revenue metrics | `SUM` | Sum additive financial amounts such as `rental_revenue`, `gross_billings`, `credit_memo_amount`, `net_billings` |
| Invoice volume | `SUM` or `COUNT DISTINCT` | Use `SUM(invoice_count)` when upstream fact count is validated; otherwise derive `COUNT(DISTINCT invoice_id)` in staging |
| Rate metrics | `AVG`, weighted average, or ratio-of-sums | Prefer ratio-of-sums for production consistency rather than naive averaging when denominators differ |
| AR concentration metrics | ratio-of-sums | Compute 90+ percentage from aggregated numerator and denominator |
| Executive health score | weighted composite | Normalize domain metrics and apply configurable weights |
| Trend metrics | window functions | Use `LAG`, cumulative comparisons, and rolling calculations by reporting period |
| Granularity controls | `GROUP BY` exact target grain | Prevent duplicate rollups caused by customer or contract-level duplication |

## 6. Transformation Rules for Aggregated Tables

### 6.1 Transformation Rules for `gold.go_agg_billing_performance`

#### Rule 1: Billing Performance Aggregate Rollup
- **Description:** Roll up rental revenue fact data into billing performance summaries by reporting date, region, branch, sales rep, and equipment class.
- **Rationale:** The conceptual model requires billing performance reporting by branch, region, sales rep, and equipment class. The Gold physical model defines this exact aggregate grain.
- **Traceability:**
  - Conceptual: Billing performance reporting, Gross Billings, Net Billings, Rental Revenue, ADR, Revenue per Contract
  - Constraints: Billing reporting must support branch, region, sales rep, and equipment class; drill-through totals must reconcile
  - Silver/Gold sources: `silver.si_invoices`, `silver.si_rental_contracts` via `gold.go_fct_rental_revenue`
  - Gold target: `gold.go_agg_billing_performance`
- **SQL Example:**
```sql
INSERT INTO gold.go_agg_billing_performance
SELECT
  monotonically_increasing_id() AS agg_billing_performance_sk,
  reporting_date,
  region_name,
  branch_name,
  sales_rep_name,
  equipment_class_name,
  SUM(gross_billings) AS gross_billings,
  SUM(credit_memo_amount) AS credit_memo_amount,
  SUM(net_billings) AS net_billings,
  SUM(rental_revenue) AS rental_revenue,
  AVG(average_daily_rate) AS average_daily_rate,
  AVG(revenue_per_contract) AS revenue_per_contract,
  AVG(credit_memo_rate) AS credit_memo_rate,
  SUM(invoice_count) AS invoice_count,
  current_timestamp() AS load_date,
  current_timestamp() AS update_date,
  'gold_fact_to_gold_aggregate' AS source_system
FROM gold.go_fct_rental_revenue
GROUP BY reporting_date, region_name, branch_name, sales_rep_name, equipment_class_name;
```

#### Rule 2: Billing Measure Reconciliation
- **Description:** Ensure billing aggregate measures reconcile so that aggregated net billings equal aggregated gross billings plus aggregated credit memo amount, where credit memos are stored as negative values.
- **Rationale:** Constraints explicitly require reconciliation of net billings to gross billings minus credit memos. At aggregate level this must continue to hold.
- **Traceability:**
  - Conceptual KPI: Gross Billings, Net Billings, Credit Memo Rate
  - Constraints: Net billings must reconcile to gross billings minus credit memos; drill-through totals must reconcile
  - Gold source/target: `gold.go_fct_rental_revenue` to `gold.go_agg_billing_performance`
- **SQL Example:**
```sql
WITH billing_rollup AS (
  SELECT
    reporting_date,
    region_name,
    branch_name,
    sales_rep_name,
    equipment_class_name,
    SUM(gross_billings) AS gross_billings,
    SUM(credit_memo_amount) AS credit_memo_amount,
    SUM(net_billings) AS net_billings
  FROM gold.go_fct_rental_revenue
  GROUP BY reporting_date, region_name, branch_name, sales_rep_name, equipment_class_name
)
SELECT
  *,
  CASE
    WHEN net_billings = gross_billings + credit_memo_amount THEN 'PASS'
    ELSE 'FAIL'
  END AS reconciliation_status
FROM billing_rollup;
```

#### Rule 3: Weighted Aggregate Rate Calculation for Billing KPIs
- **Description:** Calculate aggregate ADR, revenue per contract, and credit memo rate using weighted or ratio-of-sums logic instead of simple averages where denominators differ materially.
- **Rationale:** Simple averaging of fact-level ratios can distort executive reporting. Aggregate KPI accuracy improves when derived from aggregated numerator and denominator inputs.
- **Traceability:**
  - Conceptual KPI: Average Daily Rate, Revenue per Contract, Credit Memo Rate
  - Constraints: Rate-based calculations must only be computed when denominator is non-zero
  - Gold source: `gold.go_fct_rental_revenue`
- **SQL Example:**
```sql
WITH revenue_base AS (
  SELECT
    reporting_date,
    region_name,
    branch_name,
    sales_rep_name,
    equipment_class_name,
    SUM(rental_revenue) AS rental_revenue,
    SUM(gross_billings) AS gross_billings,
    SUM(ABS(credit_memo_amount)) AS credit_memo_abs,
    COUNT(DISTINCT contract_id) AS contract_count,
    SUM(COALESCE(billed_rental_days, 0)) AS billed_rental_days
  FROM gold.go_fct_rental_revenue
  GROUP BY reporting_date, region_name, branch_name, sales_rep_name, equipment_class_name
)
SELECT
  reporting_date,
  region_name,
  branch_name,
  sales_rep_name,
  equipment_class_name,
  CASE WHEN billed_rental_days <> 0 THEN rental_revenue / billed_rental_days ELSE NULL END AS average_daily_rate,
  CASE WHEN contract_count <> 0 THEN rental_revenue / contract_count ELSE NULL END AS revenue_per_contract,
  CASE WHEN gross_billings <> 0 THEN credit_memo_abs / gross_billings ELSE NULL END AS credit_memo_rate
FROM revenue_base;
```

#### Rule 4: Period Trend and Rolling Billing Analysis
- **Description:** Add window-based period trend logic to support period-over-period billing performance analysis by branch, sales rep, and equipment class.
- **Rationale:** The conceptual model includes trend analysis and reporting across periods. Aggregate tables are a suitable place for fast trend consumption.
- **Traceability:**
  - Conceptual KPI: Trend Value, billing period analysis
  - Constraints: Time analysis must support day, week, month, and quarter reporting
  - Gold source/target: `gold.go_fct_rental_revenue` to `gold.go_agg_billing_performance`
- **SQL Example:**
```sql
WITH billing_summary AS (
  SELECT
    reporting_date,
    region_name,
    branch_name,
    sales_rep_name,
    equipment_class_name,
    SUM(net_billings) AS net_billings,
    SUM(rental_revenue) AS rental_revenue
  FROM gold.go_fct_rental_revenue
  GROUP BY reporting_date, region_name, branch_name, sales_rep_name, equipment_class_name
)
SELECT
  *,
  net_billings - LAG(net_billings) OVER (
    PARTITION BY region_name, branch_name, sales_rep_name, equipment_class_name
    ORDER BY reporting_date
  ) AS net_billings_period_trend,
  AVG(rental_revenue) OVER (
    PARTITION BY region_name, branch_name, sales_rep_name, equipment_class_name
    ORDER BY reporting_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS rolling_3_period_avg_rental_revenue
FROM billing_summary;
```

### 6.2 Transformation Rules for `gold.go_agg_executive_health_score`

#### Rule 5: Executive Domain Metric Consolidation
- **Description:** Consolidate revenue, AR aging, cash application, and credit risk domain metrics into a single executive aggregate keyed by reporting date, network level, region, branch, sales rep, and collector.
- **Rationale:** The conceptual model requires cross-domain executive scorecard reporting across organizational rollups. This aggregate becomes the governed presentation layer for executives.
- **Traceability:**
  - Conceptual KPI: Overall Revenue-to-Cash Health Score, Rental Revenue, DSO, AR 90+ %, CEI, Unapplied Cash %, Credit Utilization %
  - Constraints: Executive scorecard reporting must support comparison across network, region, branch, and sales rep or collector levels
  - Gold sources: `gold.go_fct_rental_revenue`, `gold.go_fct_ar_aging`, `gold.go_fct_cash_application`, `gold.go_fct_credit_risk`, `gold.go_dim_branch`
  - Gold target: `gold.go_agg_executive_health_score`
- **SQL Example:**
```sql
WITH revenue AS (
  SELECT
    reporting_date,
    region_name,
    branch_name,
    sales_rep_name,
    SUM(rental_revenue) AS rental_revenue
  FROM gold.go_fct_rental_revenue
  GROUP BY reporting_date, region_name, branch_name, sales_rep_name
),
ar AS (
  SELECT
    snapshot_date AS reporting_date,
    branch_name,
    collector_name,
    SUM(ar_90_plus_amount) AS ar_90_plus_amount,
    SUM(total_ar_outstanding) AS total_ar_outstanding,
    CASE WHEN SUM(total_ar_outstanding) <> 0 THEN SUM(ar_90_plus_amount) / SUM(total_ar_outstanding) ELSE NULL END AS ar_90_plus_percentage,
    AVG(dso) AS dso
  FROM gold.go_fct_ar_aging
  GROUP BY snapshot_date, branch_name, collector_name
),
cash_app AS (
  SELECT
    reporting_date,
    branch_name,
    collector_name,
    AVG(collection_effectiveness_index) AS collection_effectiveness_index,
    CASE WHEN SUM(payment_amount) <> 0 THEN SUM(unapplied_cash_amount) / SUM(payment_amount) ELSE NULL END AS unapplied_cash_percentage
  FROM gold.go_fct_cash_application
  GROUP BY reporting_date, branch_name, collector_name
),
risk AS (
  SELECT
    snapshot_date AS reporting_date,
    branch_name,
    AVG(credit_utilization_percentage) AS credit_utilization_percentage
  FROM gold.go_fct_credit_risk
  GROUP BY snapshot_date, branch_name
)
SELECT
  monotonically_increasing_id() AS agg_executive_health_score_sk,
  r.reporting_date,
  b.network_level,
  r.region_name,
  r.branch_name,
  r.sales_rep_name,
  a.collector_name,
  NULL AS overall_revenue_to_cash_health_score,
  r.rental_revenue,
  a.dso,
  a.ar_90_plus_percentage,
  c.collection_effectiveness_index,
  c.unapplied_cash_percentage,
  k.credit_utilization_percentage,
  current_timestamp() AS load_date,
  current_timestamp() AS update_date,
  'gold_fact_to_gold_aggregate' AS source_system
FROM revenue r
LEFT JOIN ar a
  ON r.reporting_date = a.reporting_date
 AND r.branch_name = a.branch_name
LEFT JOIN cash_app c
  ON r.reporting_date = c.reporting_date
 AND r.branch_name = c.branch_name
 AND COALESCE(a.collector_name, c.collector_name) = c.collector_name
LEFT JOIN risk k
  ON r.reporting_date = k.reporting_date
 AND r.branch_name = k.branch_name
LEFT JOIN gold.go_dim_branch b
  ON r.branch_name = b.branch_name;
```

#### Rule 6: Executive Health Score Weighted Composite
- **Description:** Compute the overall revenue-to-cash health score as a weighted composite of normalized domain metrics while keeping values bounded between 0 and 100.
- **Rationale:** Constraints require the health score to remain within 0 to 100 and define it as a configurable weighted composite.
- **Traceability:**
  - Conceptual KPI: Overall Revenue-to-Cash Health Score
  - Constraints: Health score must remain within 0 to 100; component domain scores must roll up according to configured weights
  - Gold target: `gold.go_agg_executive_health_score.overall_revenue_to_cash_health_score`
- **SQL Example:**
```sql
WITH metric_base AS (
  SELECT
    reporting_date,
    network_level,
    region_name,
    branch_name,
    sales_rep_name,
    collector_name,
    rental_revenue,
    dso,
    ar_90_plus_percentage,
    collection_effectiveness_index,
    unapplied_cash_percentage,
    credit_utilization_percentage,
    LEAST(100, GREATEST(0, rental_revenue / 1000)) AS revenue_score,
    LEAST(100, GREATEST(0, 100 - COALESCE(dso, 100))) AS dso_score,
    LEAST(100, GREATEST(0, 100 - (COALESCE(ar_90_plus_percentage, 1) * 100))) AS ar_score,
    LEAST(100, GREATEST(0, COALESCE(collection_effectiveness_index, 0) * 100)) AS cei_score,
    LEAST(100, GREATEST(0, 100 - (COALESCE(unapplied_cash_percentage, 1) * 100))) AS unapplied_cash_score,
    LEAST(100, GREATEST(0, 100 - (COALESCE(credit_utilization_percentage, 1) * 100))) AS credit_score
  FROM some_executive_staging_view
)
SELECT
  *,
  LEAST(100, GREATEST(0,
    (revenue_score * 0.20) +
    (dso_score * 0.20) +
    (ar_score * 0.20) +
    (cei_score * 0.15) +
    (unapplied_cash_score * 0.10) +
    (credit_score * 0.15)
  )) AS overall_revenue_to_cash_health_score
FROM metric_base;
```

#### Rule 7: Ratio-of-Sums Logic for AR 90+, Unapplied Cash, and Credit Utilization
- **Description:** Derive executive percentages from aggregated numerators and denominators rather than averaging branch-customer-level percentages.
- **Rationale:** Ratio-of-sums produces more accurate executive views and better aligns with reconciliation requirements.
- **Traceability:**
  - Conceptual KPI: AR 90+ %, Unapplied Cash %, Credit Utilization %
  - Constraints: KPI dependency rules and reporting consistency rules
  - Gold sources: `gold.go_fct_ar_aging`, `gold.go_fct_cash_application`, `gold.go_fct_credit_risk`
- **SQL Example:**
```sql
WITH ar_rollup AS (
  SELECT
    snapshot_date AS reporting_date,
    branch_name,
    SUM(ar_90_plus_amount) AS ar_90_plus_amount,
    SUM(total_ar_outstanding) AS total_ar_outstanding
  FROM gold.go_fct_ar_aging
  GROUP BY snapshot_date, branch_name
),
cash_rollup AS (
  SELECT
    reporting_date,
    branch_name,
    SUM(unapplied_cash_amount) AS unapplied_cash_amount,
    SUM(payment_amount) AS total_payment_amount
  FROM gold.go_fct_cash_application
  GROUP BY reporting_date, branch_name
),
risk_rollup AS (
  SELECT
    snapshot_date AS reporting_date,
    branch_name,
    SUM(outstanding_ar) AS outstanding_ar,
    SUM(credit_limit) AS total_credit_limit
  FROM gold.go_fct_credit_risk
  GROUP BY snapshot_date, branch_name
)
SELECT
  a.reporting_date,
  a.branch_name,
  CASE WHEN a.total_ar_outstanding <> 0 THEN a.ar_90_plus_amount / a.total_ar_outstanding ELSE NULL END AS ar_90_plus_percentage,
  CASE WHEN c.total_payment_amount <> 0 THEN c.unapplied_cash_amount / c.total_payment_amount ELSE NULL END AS unapplied_cash_percentage,
  CASE WHEN r.total_credit_limit <> 0 THEN r.outstanding_ar / r.total_credit_limit ELSE NULL END AS credit_utilization_percentage
FROM ar_rollup a
LEFT JOIN cash_rollup c
  ON a.reporting_date = c.reporting_date
 AND a.branch_name = c.branch_name
LEFT JOIN risk_rollup r
  ON a.reporting_date = r.reporting_date
 AND a.branch_name = r.branch_name;
```

#### Rule 8: Executive Time-Series Window Calculations
- **Description:** Support executive rolling averages and cumulative trends for rental revenue and DSO using window functions partitioned by organizational hierarchy.
- **Rationale:** Executive users need trend visibility over time and the instructions explicitly require window functions where row-based aggregation is needed.
- **Traceability:**
  - Conceptual KPI: Trend Value, DSO Trend, executive scorecard comparisons
  - Constraints: Time analysis must support day, week, month, quarter reporting
  - Gold target: `gold.go_agg_executive_health_score`
- **SQL Example:**
```sql
WITH executive_summary AS (
  SELECT
    reporting_date,
    network_level,
    region_name,
    branch_name,
    sales_rep_name,
    collector_name,
    rental_revenue,
    dso
  FROM gold.go_agg_executive_health_score
)
SELECT
  *,
  SUM(rental_revenue) OVER (
    PARTITION BY network_level, region_name, branch_name
    ORDER BY reporting_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_rental_revenue,
  AVG(dso) OVER (
    PARTITION BY network_level, region_name, branch_name
    ORDER BY reporting_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS rolling_3_period_dso,
  dso - LAG(dso) OVER (
    PARTITION BY network_level, region_name, branch_name
    ORDER BY reporting_date
  ) AS dso_period_change
FROM executive_summary;
```

#### Rule 9: Granularity and Hierarchy Conformance Validation
- **Description:** Enforce aggregate grain so each executive row is uniquely identified by reporting date, network level, region, branch, sales rep, and collector, and each billing row is uniquely identified by reporting date, region, branch, sales rep, and equipment class.
- **Rationale:** Constraints define uniqueness and consistency expectations. Aggregate duplication would distort executive metrics.
- **Traceability:**
  - Conceptual: Organization hierarchy and executive reporting levels
  - Constraints: Branch/date/period type uniqueness, branch hierarchy consistency, same rollup structure across views
  - Gold targets: `gold.go_agg_executive_health_score`, `gold.go_agg_billing_performance`
- **SQL Example:**
```sql
SELECT
  reporting_date,
  network_level,
  region_name,
  branch_name,
  sales_rep_name,
  collector_name,
  COUNT(*) AS row_count
FROM gold.go_agg_executive_health_score
GROUP BY reporting_date, network_level, region_name, branch_name, sales_rep_name, collector_name
HAVING COUNT(*) > 1;
```

#### Rule 10: Data Normalization and Formatting for Aggregate Outputs
- **Description:** Normalize decimal precision, standardize percentage scales, and bucket reporting dates for daily, weekly, monthly, and quarterly consumption.
- **Rationale:** Instructions require formatting consistency and support for multiple reporting grains.
- **Traceability:**
  - Conceptual: Date / Period / Period Type, executive and billing trend analysis
  - Constraints: Time analysis must support day, week, month, quarter; data formatting must remain consistent
  - Gold sources/targets: all aggregate outputs
- **SQL Example:**
```sql
SELECT
  reporting_date,
  DATE_TRUNC('WEEK', reporting_date) AS reporting_week,
  DATE_TRUNC('MONTH', reporting_date) AS reporting_month,
  DATE_TRUNC('QUARTER', reporting_date) AS reporting_quarter,
  ROUND(rental_revenue, 2) AS rental_revenue,
  ROUND(dso, 4) AS dso,
  ROUND(ar_90_plus_percentage, 6) AS ar_90_plus_percentage,
  ROUND(collection_effectiveness_index, 6) AS collection_effectiveness_index,
  ROUND(unapplied_cash_percentage, 6) AS unapplied_cash_percentage,
  ROUND(credit_utilization_percentage, 6) AS credit_utilization_percentage
FROM gold.go_agg_executive_health_score;
```

## 7. Joins, Intermediate Transformations, Filters, and Output Format

### 7.1 Expected Joins for Aggregate Processing
| Left Table | Join Field(s) | Right Table | Purpose |
|---|---|---|---|
| `gold.go_fct_rental_revenue` | `reporting_date`, `branch_name` | `gold.go_fct_ar_aging` | Align revenue and AR metrics for executive reporting |
| `gold.go_fct_rental_revenue` | `reporting_date`, `branch_name` | `gold.go_fct_cash_application` | Align revenue and cash application metrics |
| `gold.go_fct_rental_revenue` | `reporting_date`, `branch_name` | `gold.go_fct_credit_risk` | Align revenue and credit risk metrics |
| `gold.go_fct_rental_revenue` | `branch_name` | `gold.go_dim_branch` | Resolve network hierarchy and branch conformance |
| `gold.go_fct_ar_aging` | `branch_name`, `collector_name` | `gold.go_fct_cash_application` | Align collector metrics in executive summaries |

### 7.2 Intermediate Transformations
- Create domain staging views for revenue, AR, cash application, and credit risk.
- Standardize date grain so `snapshot_date` aligns to `reporting_date` for executive summaries.
- Aggregate customer or contract-level metrics before executive joining to avoid fanout duplication.
- Precompute numerators and denominators for ratio-of-sums metrics.
- Normalize hierarchy attributes using conformed branch dimension.

### 7.3 Filters and Validation Rules
- Exclude inactive branches when branch status is not valid for the reporting date.
- Exclude records with null mandatory grouping dimensions from final aggregate loads and route them to error handling.
- Prevent divide-by-zero for all KPI percentages and rates.
- Ensure only allowed aging buckets contribute to AR rollups.
- Reconcile billing and AR totals back to supporting fact tables before publication.

### 7.4 Output Format
- Databricks Gold Delta aggregate tables.
- Markdown artifact in GitHub output folder.

## 8. Traceability Matrix

| Aggregate Rule / Metric | Conceptual Source | Constraints Source | Silver / Gold Upstream Source | Gold Target |
|---|---|---|---|---|
| Billing Performance Rollup | Billing performance reporting | Reporting by branch/region/sales rep/equipment class | `go_fct_rental_revenue` | `go_agg_billing_performance` |
| Gross/Net Billing Reconciliation | Gross Billings, Net Billings | Net billings reconciliation rule | `go_fct_rental_revenue` | `go_agg_billing_performance` |
| ADR Aggregate | Average Daily Rate | Non-zero denominator rule | `go_fct_rental_revenue` | `go_agg_billing_performance` |
| Revenue per Contract Aggregate | Revenue per Contract | Dependency rule | `go_fct_rental_revenue` | `go_agg_billing_performance` |
| Credit Memo Rate Aggregate | Credit Memo Rate | Non-zero denominator rule | `go_fct_rental_revenue` | `go_agg_billing_performance` |
| Executive Domain Consolidation | Overall executive scorecard | Cross-domain comparison rule | `go_fct_rental_revenue`, `go_fct_ar_aging`, `go_fct_cash_application`, `go_fct_credit_risk` | `go_agg_executive_health_score` |
| Health Score Composite | Overall Revenue-to-Cash Health Score | Weighted composite; 0 to 100 range | Executive staging metrics | `go_agg_executive_health_score` |
| AR 90+ % | AR 90+ % | 90+ dependency rule | `go_fct_ar_aging` | `go_agg_executive_health_score` |
| Unapplied Cash % | Unapplied Cash % | Unapplied / total payments dependency | `go_fct_cash_application` | `go_agg_executive_health_score` |
| Credit Utilization % | Credit Utilization % | Outstanding AR / credit limit dependency | `go_fct_credit_risk` | `go_agg_executive_health_score` |
| DSO Trend | DSO Trend | Same reporting period consistency | `go_fct_ar_aging` | `go_agg_executive_health_score` |
| Hierarchy Conformance | Organization Hierarchy | Branch hierarchy integrity | `go_dim_branch` | Both aggregate tables |

## 9. Recommended Load Pattern
1. Read validated Gold fact tables and conformed branch dimension.
2. Standardize period alignment between `reporting_date` and `snapshot_date`.
3. Build separate domain aggregate staging views.
4. Precompute numerator and denominator components for ratio-based KPIs.
5. Join domain staging views at the exact required executive grain.
6. Calculate executive weighted health score and billing aggregate rates.
7. Run reconciliation, granularity, and formatting checks.
8. Insert valid records into Gold aggregate tables.
9. Write validation failures to error/audit tables.

## 10. Implementation Notes
- Use ratio-of-sums logic for executive KPI percentages whenever possible.
- Avoid many-to-many joins across facts by aggregating each domain first.
- Preserve branch, region, network, sales rep, and collector attributes in aggregate outputs for drill-down and auditability.
- Apply Delta optimization and partition pruning based on `reporting_date` after aggregate loads.
- Maintain historical aggregate versions in GitHub and do not overwrite prior recommender files.

## 11. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Gold_Aggregated_Transformation_Recommender_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Aggregated_Transformation_Recommender/Databricks_Gold_Aggregated_Transformation_Recommender_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Recommender
pipelineID : 14677
