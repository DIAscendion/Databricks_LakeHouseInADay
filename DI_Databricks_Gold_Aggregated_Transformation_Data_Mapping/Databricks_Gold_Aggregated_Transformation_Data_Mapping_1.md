_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold aggregated transformation data mapping for Rental Revenue-to-Cash executive and billing aggregate tables from Silver-informed Gold sources.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Aggregated Transformation Data Mapping

## 1. Overview
This document defines the detailed data mapping for Gold aggregated tables in the Rental Revenue-to-Cash domain. It uses the Silver physical model and prior Gold Aggregated Transformation Recommender guidance to map target Gold aggregate fields to their upstream source tables, source fields, aggregation logic, validation rules, and Databricks/PySpark-compatible transformation rules. The mapping emphasizes additive financial rollups, ratio-of-sums metric derivation, grain conformance, null handling, precision control, and reconciliation-ready executive reporting.

## 2. Source and Target Context

### 2.1 Source Layer Inputs Reviewed
| Input File | Usage in Mapping |
|---|---|
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Identified core Silver source entities, business columns, joins, and data quality considerations |
| `DI_Databricks_Gold_Aggregated_Transformation_Recommender/Databricks_Gold_Aggregated_Transformation_Recommender_1.md` | Identified Gold aggregate targets, recommended aggregation methods, grouping logic, ratio calculations, and executive KPI rules |

### 2.2 Aggregated Gold Targets Covered
- `gold.go_agg_billing_performance`
- `gold.go_agg_executive_health_score`

### 2.3 Key Processing Considerations
- Aggregate only after domain-level staging to prevent join fanout and duplicate metrics.
- Use exact target grain defined by the Gold recommender.
- Prefer ratio-of-sums over average-of-ratios for percentage KPIs.
- Apply `COALESCE`, safe division, decimal rounding, and bounded score logic.
- Align `snapshot_date` and `reporting_date` into a conformed reporting period before joining executive domains.
- Preserve auditability through reproducible metric logic and deterministic grouping keys.

## 3. Aggregated Table Grain and Join Summary

| Target Table | Target Grain | Upstream Source Tables | Join / Grouping Summary |
|---|---|---|---|
| `gold.go_agg_billing_performance` | One row per `reporting_date`, `region_name`, `branch_name`, `sales_rep_name`, `equipment_class_name` | `silver.si_invoices`, `silver.si_rental_contracts`, optionally staged through `gold.go_fct_rental_revenue` | Join invoices to contracts on `contract_id`; group by reporting date and business hierarchy |
| `gold.go_agg_executive_health_score` | One row per `reporting_date`, `network_level`, `region_name`, `branch_name`, `sales_rep_name`, `collector_name` | `silver.si_invoices`, `silver.si_cash_receipts`, `silver.si_rental_contracts`, `silver.si_customer_master`, `silver.si_branch_employee`, optionally staged through Gold facts | Aggregate each metric domain independently, then join by aligned reporting period and organizational hierarchy |

## 4. Data Mapping for Aggregated Tables

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Aggregation Rule | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|---|
| Gold | `gold.go_agg_billing_performance` | `reporting_date` | Silver | `silver.si_invoices` | `invoice_date` | Group By | Must be non-null and parsable date; invalid dates rejected to error table | Map `invoice_date` as reporting date; optionally derive week/month/quarter buckets using `date_trunc` in downstream views |
| Gold | `gold.go_agg_billing_performance` | `region_name` | Silver | `silver.si_branch_employee` | `region` | Group By | Must be non-null for published aggregate; unmatched branch-region mappings flagged | Join contracts using `sales_rep_id = employee_id` and derive conformed region from employee branch assignment |
| Gold | `gold.go_agg_billing_performance` | `branch_name` | Silver | `silver.si_rental_contracts` | `branch_code` | Group By | Must be non-null; branch code must map to a valid reporting branch | Use `branch_code` as branch reporting attribute or resolve via conformed branch reference in Gold staging |
| Gold | `gold.go_agg_billing_performance` | `sales_rep_name` | Silver | `silver.si_branch_employee` | `employee_name` | Group By | Must be populated for sales-owned contracts or routed for remediation | Join contract `sales_rep_id` to employee master and standardize nulls to governed unknown member only if allowed |
| Gold | `gold.go_agg_billing_performance` | `equipment_class_name` | Silver | `silver.si_rental_contracts` | `equipment_class` | Group By | Must use allowed equipment class values; unsupported values flagged | Normalize equipment class casing and trim whitespace before grouping |
| Gold | `gold.go_agg_billing_performance` | `gross_billings` | Silver | `silver.si_invoices` | `invoice_amount` | `SUM(invoice_amount)` | Amount must be non-null after defaulting; negative billing rows reviewed by business rule; duplicates prevented by aggregate grain validation | Cast to `DECIMAL(18,2)` and sum invoice amounts for billing period |
| Gold | `gold.go_agg_billing_performance` | `credit_memo_amount` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_type` | `SUM(CASE WHEN invoice_type='CREDIT_MEMO' THEN invoice_amount ELSE 0 END)` | `invoice_type` must be valid; credit memo rows must reconcile with net billings rule | Classify invoice rows by `invoice_type`; preserve sign convention and round to 2 decimals |
| Gold | `gold.go_agg_billing_performance` | `net_billings` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_type` | `SUM(gross billing rows) + SUM(credit memo rows)` | Aggregate result must reconcile to gross billings plus credit memo amount when credit memo stored as negative | Derive net billings using sign-aware invoice classification rather than naïve sum if mixed invoice types exist |
| Gold | `gold.go_agg_billing_performance` | `rental_revenue` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_amount`, `contract_id` | `SUM(invoice_amount)` for rental-related invoices | Include only rental revenue eligible invoice types; exclude non-rental adjustments unless business-approved | Filter invoice population to rental-related billings joined to valid contracts |
| Gold | `gold.go_agg_billing_performance` | `average_daily_rate` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_amount`, `daily_rate` | Weighted average / ratio-of-sums preferred | Denominator must be non-zero; null denominators yield null metric not zero | Prefer `SUM(rental_revenue) / SUM(billed_rental_days)` when available; fallback to governed average of contract daily rates only for complete populations |
| Gold | `gold.go_agg_billing_performance` | `revenue_per_contract` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_amount`, `contract_id` | `SUM(rental_revenue) / COUNT(DISTINCT contract_id)` | Distinct contract count must be > 0; duplicate contract inflation check required | Count distinct contracts in aggregate grain and apply safe division |
| Gold | `gold.go_agg_billing_performance` | `credit_memo_rate` | Silver | `silver.si_invoices` | `invoice_amount`, `invoice_type` | `ABS(SUM(credit_memo_amount)) / SUM(gross_billings)` | Gross billings denominator must be non-zero; percentage bounded to sensible range | Use ratio-of-sums instead of averaging row-level rates; round to 6 decimals |
| Gold | `gold.go_agg_billing_performance` | `invoice_count` | Silver | `silver.si_invoices` | `invoice_id` | `COUNT(DISTINCT invoice_id)` or `SUM(invoice_count)` in staged fact | Must reconcile to source invoice population; duplicates across joins are not allowed | Prefer distinct invoice count from invoice base before joining descriptive dimensions |
| Gold | `gold.go_agg_executive_health_score` | `reporting_date` | Silver | `silver.si_invoices`, `silver.si_cash_receipts` | `invoice_date`, `receipt_date` | Group By conformed reporting date | Reporting date must be aligned across revenue, AR, cash, and risk domains | Standardize domain dates to a common reporting date; align `snapshot_date`-style metrics in staging |
| Gold | `gold.go_agg_executive_health_score` | `network_level` | Silver | Derived from conformed organizational hierarchy using `silver.si_branch_employee` | `region`, `branch_code` | Group By | Must conform to approved hierarchy; hierarchy mismatches rejected or flagged | Derive network level through conformed branch hierarchy staging before final aggregate join |
| Gold | `gold.go_agg_executive_health_score` | `region_name` | Silver | `silver.si_branch_employee` | `region` | Group By | Non-null region required for executive publication | Standardize regional names and use branch-employee conformance mapping |
| Gold | `gold.go_agg_executive_health_score` | `branch_name` | Silver | `silver.si_rental_contracts` | `branch_code` | Group By | Branch must be valid and active for reporting date where applicable | Normalize branch code/name mapping in dimension-style staging |
| Gold | `gold.go_agg_executive_health_score` | `sales_rep_name` | Silver | `silver.si_branch_employee` | `employee_name` | Group By | Sales rep mapping required where revenue exists | Join contracts to employee assignments using `sales_rep_id`; enforce single conformed rep per row |
| Gold | `gold.go_agg_executive_health_score` | `collector_name` | Silver | `silver.si_branch_employee` | `collector_id`, `employee_name` | Group By | Collector assignment must be valid for AR/cash metrics; missing assignments flagged | Resolve collector descriptive name from branch employee mapping or governed collector reference |
| Gold | `gold.go_agg_executive_health_score` | `overall_revenue_to_cash_health_score` | Silver | Derived from aggregated domain measures | `rental_revenue`, `dso`, `ar_90_plus_percentage`, `collection_effectiveness_index`, `unapplied_cash_percentage`, `credit_utilization_percentage` | Weighted composite score | Final score must be between 0 and 100 inclusive | Normalize each component to bounded score, apply configured weights, and use `LEAST/GREATEST` for 0-100 enforcement |
| Gold | `gold.go_agg_executive_health_score` | `rental_revenue` | Silver | `silver.si_invoices`, `silver.si_rental_contracts` | `invoice_amount`, `contract_id`, `branch_code` | `SUM(rental invoice amounts)` | Include only valid rental billings; duplicates prevented by pre-aggregating revenue domain | Aggregate revenue domain independently by reporting date, branch, region, and sales rep before domain joins |
| Gold | `gold.go_agg_executive_health_score` | `dso` | Silver | `silver.si_invoices`, `silver.si_cash_receipts` | `due_date`, `receipt_date`, `invoice_amount`, `payment_amount` | Ratio / governed average in AR staging | Non-zero denominator required; negative or implausible values flagged | Derive DSO using governed AR formula in staging; for aggregate presentation use weighted/period-consistent value rather than simple row average |
| Gold | `gold.go_agg_executive_health_score` | `ar_90_plus_percentage` | Silver | `silver.si_invoices` | `due_date`, `invoice_amount` | `SUM(ar_90_plus_amount) / SUM(total_ar_outstanding)` | Allowed aging bucket logic only; denominator must be non-zero | Bucket receivables by aging relative to reporting date, sum 90+ outstanding, and compute ratio-of-sums |
| Gold | `gold.go_agg_executive_health_score` | `collection_effectiveness_index` | Silver | `silver.si_invoices`, `silver.si_cash_receipts` | `invoice_amount`, `payment_amount`, `receipt_date`, `due_date` | Governed ratio metric at aggregate level | Denominator must be non-zero; values outside expected business range flagged | Compute CEI from aggregated collectible receivables and collected cash measures in staging, then round consistently |
| Gold | `gold.go_agg_executive_health_score` | `unapplied_cash_percentage` | Silver | `silver.si_cash_receipts` | `payment_amount`, `unapplied_payment_amount` | `SUM(unapplied_payment_amount) / SUM(payment_amount)` | Denominator must be non-zero; null unapplied amounts default to 0 where allowed | Use ratio-of-sums from cash application staging; round to 6 decimals |
| Gold | `gold.go_agg_executive_health_score` | `credit_utilization_percentage` | Silver | `silver.si_customer_master`, `silver.si_invoices` | `credit_limit`, derived outstanding AR | `SUM(outstanding_ar) / SUM(credit_limit)` | Credit limit denominator must be non-zero; over-limit counts tracked separately if required | Aggregate outstanding AR by customer and divide by summed credit limit at executive grain |

## 5. Detailed Transformation Logic Notes

### 5.1 Billing Performance Aggregate Logic
1. Start from `silver.si_invoices` as the billing event source.
2. Join to `silver.si_rental_contracts` on `contract_id` to obtain `branch_code`, `sales_rep_id`, and `equipment_class`.
3. Join to `silver.si_branch_employee` on `sales_rep_id = employee_id` to derive `employee_name` and `region`.
4. Filter to valid rental billing population and classify credit memos using `invoice_type`.
5. Aggregate by `invoice_date`, `region`, `branch_code`, `employee_name`, and `equipment_class`.
6. Compute additive measures first, then derive rate measures using safe division.
7. Validate grain uniqueness and billing reconciliation before load.

### 5.2 Executive Health Score Aggregate Logic
1. Build separate domain staging datasets for revenue, AR aging, cash application, and credit risk.
2. Standardize all domain dates to a common `reporting_date`.
3. Pre-aggregate each domain to the executive target grain before joining.
4. Use ratio-of-sums for `ar_90_plus_percentage`, `unapplied_cash_percentage`, and `credit_utilization_percentage`.
5. Derive DSO and CEI in governed staging logic to avoid inconsistent point-in-time calculations.
6. Normalize all component metrics into bounded sub-scores and apply weighted composite scoring.
7. Reject duplicate grain rows and route invalid records to data quality handling.

## 6. Validation and Cleansing Rules

| Rule Category | Rule |
|---|---|
| Grain Validation | Ensure no duplicate rows exist for billing aggregate grain or executive aggregate grain prior to publication |
| Mandatory Fields | Reject records where grouping keys such as reporting date, region, branch, or target business owner dimensions are null |
| Safe Division | For all percentages and rates, return null when denominator is zero; do not force zero unless business-approved |
| Null Handling | Use `COALESCE` for additive numeric components where missing values are allowed to default to zero |
| Decimal Precision | Round currency fields to 2 decimals and percentage/rate fields to 4 or 6 decimals as appropriate |
| Domain Conformance | Permit only valid invoice types, aging bucket derivations, branch mappings, and employee assignments |
| Reconciliation | Validate net billings against gross billings and credit memo amounts; validate aggregate invoice counts against source invoice population |
| Outlier Review | Flag extreme DSO, CEI, or credit utilization values outside expected business thresholds for stewardship review |
| Temporal Alignment | Ensure dates from invoices, receipts, and AR snapshots are aligned to the same reporting period before executive joins |

## 7. PySpark / Databricks Compatibility Guidance
- Use DataFrame aggregations with `groupBy()` and built-in aggregate functions such as `sum`, `countDistinct`, `avg`, `when`, and `round`.
- Use pre-aggregation staging DataFrames to avoid many-to-many fact joins.
- Implement safe division with `when(col(denominator) != 0, numerator / denominator)`.
- Use Delta Lake tables for Gold outputs and apply `OPTIMIZE`/`ZORDER` on common reporting dimensions where appropriate.
- Use window functions only for trend outputs or rolling metrics, not for base additive aggregate duplication-prone logic.

## 8. Example PySpark-Oriented Aggregation Patterns

```python
billing_df = (
    invoices_df.alias("i")
    .join(contracts_df.alias("c"), "contract_id", "left")
    .join(employees_df.alias("e"), col("c.sales_rep_id") == col("e.employee_id"), "left")
    .groupBy(
        col("i.invoice_date").alias("reporting_date"),
        col("e.region").alias("region_name"),
        col("c.branch_code").alias("branch_name"),
        col("e.employee_name").alias("sales_rep_name"),
        col("c.equipment_class").alias("equipment_class_name")
    )
    .agg(
        round(sum("i.invoice_amount"), 2).alias("gross_billings"),
        round(sum(when(col("i.invoice_type") == "CREDIT_MEMO", col("i.invoice_amount")).otherwise(lit(0))), 2).alias("credit_memo_amount"),
        countDistinct("i.invoice_id").alias("invoice_count")
    )
)
```

```python
executive_cash_df = (
    cash_receipts_df
    .groupBy("receipt_date", "customer_id")
    .agg(
        sum(coalesce(col("payment_amount"), lit(0))).alias("total_payment_amount"),
        sum(coalesce(col("unapplied_payment_amount"), lit(0))).alias("unapplied_cash_amount")
    )
    .withColumn(
        "unapplied_cash_percentage",
        when(col("total_payment_amount") != 0, col("unapplied_cash_amount") / col("total_payment_amount"))
    )
)
```

## 9. Assumptions
1. Gold aggregate targets described by the recommender are the required publication objects even though the physical Gold DDL file was not directly provided in the input set.
2. `branch_code` is used as the branch reporting attribute unless a conformed branch dimension resolves a business-friendly branch name.
3. `invoice_type` contains sufficient semantics to identify standard billings versus credit memos.
4. DSO, CEI, and outstanding AR may require governed staging logic beyond raw Silver columns; this mapping documents the expected derivation path.
5. Executive hierarchy conformance may be implemented through a Gold conformed dimension built from Silver branch and employee attributes.

## 10. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Gold_Aggregated_Transformation_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Aggregated_Transformation_Data_Mapping/Databricks_Gold_Aggregated_Transformation_Data_Mapping_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Aggregated_Transformation_Data_Mapping
pipelineID : 14678
