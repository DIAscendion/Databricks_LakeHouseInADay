_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Silver-layer data quality recommendations for Rental Revenue-to-Cash reporting entities, facts, and conformed business rules.
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Silver DQ Recommender

## 1. Overview
This document provides recommended Silver-layer data quality checks for the Rental Revenue-to-Cash domain using the conceptual model, business constraints, and Bronze physical model. The recommendations focus on validating conformance, completeness, accuracy, consistency, referential integrity, and business-rule-driven calculations before downstream Gold reporting is produced.

## 2. Input Analysis Summary

| Input File | Purpose | Outcome Used for DQ Design |
|---|---|---|
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` | Business entities, KPIs, and relationships | Used to identify required entities, metrics, and cross-domain dependencies |
| `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Constraints_1.md` | Constraints and business rules | Used to derive mandatory, uniqueness, referential, and metric validation checks |
| `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` | Bronze source tables and physical columns | Used to infer source-to-Silver conformance checks and column-level validations |
| `Input/Input/rental_revenue_to_cash_bronze_schema.sql` | Raw schema DDL | File not found; Bronze physical model was used as the surrogate physical source definition |

## 3. Parsed Source Tables and Key Columns

### 3.1 bronze.bz_rental_contracts
| Column | Data Type | DQ Focus |
|---|---|---|
| contract_id | STRING | mandatory, uniqueness, referential downstream |
| customer_id | STRING | mandatory, FK to customer |
| branch_code | STRING | mandatory, hierarchy conformance |
| sales_rep_id | STRING | employee conformance |
| equipment_class | STRING | domain validation |
| contract_start_date | STRING | date format |
| contract_end_date | STRING | date format and sequencing |
| contract_status | STRING | allowed values |
| daily_rate | DECIMAL(10,2) | non-negative precision |
| source_system | STRING | lineage mandatory |

### 3.2 bronze.bz_invoices
| Column | Data Type | DQ Focus |
|---|---|---|
| invoice_id | STRING | mandatory, uniqueness |
| contract_id | STRING | FK to contracts |
| customer_id | STRING | FK to customer |
| invoice_date | STRING | date format |
| due_date | STRING | date format, due date logic |
| invoice_amount | DECIMAL(12,2) | non-negative for standard invoices |
| tax_amount | DECIMAL(12,2) | non-negative |
| invoice_type | STRING | allowed values, credit memo handling |
| currency | STRING | allowed pattern/domain |

### 3.3 bronze.bz_cash_receipts
| Column | Data Type | DQ Focus |
|---|---|---|
| receipt_id | STRING | mandatory, uniqueness |
| invoice_id | STRING | FK or unapplied exception handling |
| customer_id | STRING | mandatory, FK |
| receipt_date | STRING | date format |
| payment_amount | DECIMAL(12,2) | non-negative |
| payment_method | STRING | allowed values |

### 3.4 bronze.bz_customer_master
| Column | Data Type | DQ Focus |
|---|---|---|
| customer_id | STRING | mandatory, uniqueness after conformance |
| customer_name | STRING | mandatory |
| credit_terms | STRING | domain consistency |
| credit_limit | DECIMAL(12,2) | non-negative |
| customer_since | STRING | date format |
| customer_status | STRING | allowed values |

### 3.5 bronze.bz_branch_employee
| Column | Data Type | DQ Focus |
|---|---|---|
| employee_id | STRING | mandatory |
| employee_name | STRING | completeness |
| role | STRING | allowed values |
| branch_code | STRING | branch conformance |
| region | STRING | region completeness |
| collector_id | STRING | assignment consistency |
| effective_date | STRING | date format |

## 4. Silver-Layer DQ Recommendation Principles
- Validate conformed keys before business aggregation.
- Standardize raw string dates into valid date columns.
- Deduplicate customer and transactional entities before fact construction.
- Enforce business-rule checks on derived measures such as net billings, aging bucket, DSO inputs, CEI inputs, and credit utilization.
- Preserve exceptions such as unapplied cash while ensuring they are explicitly flagged.
- Ensure branch, region, customer, invoice, and contract conformance across all reporting domains.

## 5. Recommended Data Quality Checks

### 5.1 Column-Level Checks

1. **Contract ID Not Null**: Validate that every Silver contract record contains `contract_id`.
   - Rationale: Contracts are core join keys for invoices, revenue, and customer exposure analysis.
   - SQL Example:
```sql
SELECT *
FROM silver.contracts
WHERE contract_id IS NULL;
```

2. **Contract Status Allowed Values**: Validate `contract_status` is only `Open` or `Closed`.
   - Rationale: Constraints explicitly define the allowed contract status values.
   - SQL Example:
```sql
SELECT contract_status, COUNT(*)
FROM silver.contracts
WHERE UPPER(contract_status) NOT IN ('OPEN','CLOSED') OR contract_status IS NULL
GROUP BY contract_status;
```

3. **Contract Date Sequence Validation**: Validate `contract_end_date` is not earlier than `contract_start_date` when both are present.
   - Rationale: Prevents impossible contract periods and downstream ADR distortion.
   - SQL Example:
```sql
SELECT *
FROM silver.contracts
WHERE to_date(contract_end_date) < to_date(contract_start_date);
```

4. **Daily Rate Non-Negative Check**: Validate `daily_rate >= 0`.
   - Rationale: Rental rate cannot be negative in standard contract records.
   - SQL Example:
```sql
SELECT *
FROM silver.contracts
WHERE daily_rate < 0;
```

5. **Invoice ID Not Null**: Validate `invoice_id` is populated.
   - Rationale: Required to uniquely identify invoices and payment applications.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE invoice_id IS NULL;
```

6. **Invoice Date Format Validation**: Validate `invoice_date` converts successfully to a valid date.
   - Rationale: Invoice trend, aging, and days-to-pay logic depend on valid invoice dates.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE to_date(invoice_date) IS NULL AND invoice_date IS NOT NULL;
```

7. **Due Date Format Validation**: Validate `due_date` converts successfully to a valid date.
   - Rationale: Due date is mandatory for aging bucket and days past due calculation.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE to_date(due_date) IS NULL OR due_date IS NULL;
```

8. **Standard Invoice Amount Non-Negative Check**: Validate non-credit memo invoices have non-negative `invoice_amount`.
   - Rationale: Business constraints require standard invoice amount to be non-negative.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE UPPER(invoice_type) <> 'CREDIT_MEMO' AND invoice_amount < 0;
```

9. **Credit Memo Amount Direction Check**: Validate credit memo transactions carry negative signed amounts in Silver normalized output.
   - Rationale: Constraints specify credit memo amount must be negative.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE UPPER(invoice_type) = 'CREDIT_MEMO' AND invoice_amount >= 0;
```

10. **Currency Code Pattern Validation**: Validate `currency` follows a 3-letter uppercase ISO-style pattern.
   - Rationale: Prevents inconsistent currency formatting in reporting and reconciliation.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE currency IS NULL OR currency NOT RLIKE '^[A-Z]{3}$';
```

11. **Receipt ID Uniqueness Check**: Validate `receipt_id` is unique.
   - Rationale: Constraints explicitly require receipt ID uniqueness.
   - SQL Example:
```sql
SELECT receipt_id, COUNT(*)
FROM silver.cash_receipts
GROUP BY receipt_id
HAVING COUNT(*) > 1;
```

12. **Payment Amount Non-Negative Check**: Validate `payment_amount >= 0`.
   - Rationale: Payment amount must be non-negative per constraints.
   - SQL Example:
```sql
SELECT *
FROM silver.cash_receipts
WHERE payment_amount < 0;
```

13. **Receipt Date Format Validation**: Validate `receipt_date` is a valid date.
   - Rationale: Needed for payment timing and average days-to-pay calculations.
   - SQL Example:
```sql
SELECT *
FROM silver.cash_receipts
WHERE to_date(receipt_date) IS NULL OR receipt_date IS NULL;
```

14. **Customer ID and Customer Name Completeness**: Validate `customer_id` and `customer_name` are populated in conformed customer records.
   - Rationale: Customer-level AR, cash application, and risk reporting depend on both.
   - SQL Example:
```sql
SELECT *
FROM silver.customers
WHERE customer_id IS NULL OR customer_name IS NULL;
```

15. **Credit Limit Non-Negative Check**: Validate `credit_limit >= 0`.
   - Rationale: Required for valid credit utilization calculations.
   - SQL Example:
```sql
SELECT *
FROM silver.customers
WHERE credit_limit < 0;
```

16. **Customer Status Allowed Values**: Validate `customer_status` is only approved domain values such as `Active` and `Suspended`.
   - Rationale: Constraints explicitly define report-aligned status values.
   - SQL Example:
```sql
SELECT customer_status, COUNT(*)
FROM silver.customers
WHERE UPPER(customer_status) NOT IN ('ACTIVE','SUSPENDED') OR customer_status IS NULL
GROUP BY customer_status;
```

17. **Customer Since Date Validation**: Validate `customer_since` is a valid date.
   - Rationale: Customer tenure reporting relies on valid onboarding dates.
   - SQL Example:
```sql
SELECT *
FROM silver.customers
WHERE to_date(customer_since) IS NULL AND customer_since IS NOT NULL;
```

18. **Employee Role Allowed Values Check**: Validate `role` values map to supported reporting roles such as `SALES_REP` and `COLLECTOR`.
   - Rationale: Personnel drill-down quality depends on consistent role classification.
   - SQL Example:
```sql
SELECT role, COUNT(*)
FROM silver.branch_employee
WHERE UPPER(role) NOT IN ('SALES_REP','COLLECTOR') OR role IS NULL
GROUP BY role;
```

19. **Region Completeness Check**: Validate all branch employee records include `region`.
   - Rationale: Region is mandatory for rollup reporting and hierarchy alignment.
   - SQL Example:
```sql
SELECT *
FROM silver.branch_employee
WHERE region IS NULL OR TRIM(region) = '';
```

20. **Metadata Completeness Check**: Validate `source_system`, `load_timestamp`, and `update_timestamp` exist in Silver source-aligned tables.
   - Rationale: Governance, auditability, and lineage must be preserved.
   - SQL Example:
```sql
SELECT *
FROM silver.invoices
WHERE source_system IS NULL OR load_timestamp IS NULL OR update_timestamp IS NULL;
```

### 5.2 Table-Level and Uniqueness Checks

21. **Customer Deduplication Check**: Validate one conformed customer record per business customer key after Silver deduplication.
   - Rationale: Business rules require duplicate legal-entity customer records to be resolved before exposure aggregation.
   - SQL Example:
```sql
SELECT customer_id, COUNT(*)
FROM silver.customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

22. **Invoice Snapshot Grain Check**: Validate uniqueness of `(customer_id, invoice_id, snapshot_date)` in AR aging outputs.
   - Rationale: Constraints define this as the unique grain for AR snapshots.
   - SQL Example:
```sql
SELECT customer_id, invoice_id, snapshot_date, COUNT(*)
FROM silver.ar_aging
GROUP BY customer_id, invoice_id, snapshot_date
HAVING COUNT(*) > 1;
```

23. **Customer Risk Snapshot Grain Check**: Validate uniqueness of `(customer_id, snapshot_date)` in risk outputs.
   - Rationale: Prevents duplicate customer exposure reporting.
   - SQL Example:
```sql
SELECT customer_id, snapshot_date, COUNT(*)
FROM silver.credit_risk
GROUP BY customer_id, snapshot_date
HAVING COUNT(*) > 1;
```

24. **Branch-Date-Period Health Score Grain Check**: Validate uniqueness of `(branch_name, report_date, period_type)`.
   - Rationale: Constraints define this unique reporting grain.
   - SQL Example:
```sql
SELECT branch_name, report_date, period_type, COUNT(*)
FROM silver.executive_scorecard
GROUP BY branch_name, report_date, period_type
HAVING COUNT(*) > 1;
```

25. **Revenue Aggregate Grain Check**: Validate uniqueness of `(branch_name, report_date, sales_rep, equipment_class)` in revenue aggregate outputs.
   - Rationale: Supports accurate billing performance reporting.
   - SQL Example:
```sql
SELECT branch_name, report_date, sales_rep, equipment_class, COUNT(*)
FROM silver.rental_revenue
GROUP BY branch_name, report_date, sales_rep, equipment_class
HAVING COUNT(*) > 1;
```

### 5.3 Referential Integrity Checks

26. **Contract to Customer Integrity**: Validate every contract customer exists in conformed customers.
   - Rationale: Constraints require every contract to map to a valid customer.
   - SQL Example:
```sql
SELECT c.*
FROM silver.contracts c
LEFT JOIN silver.customers m
  ON c.customer_id = m.customer_id
WHERE m.customer_id IS NULL;
```

27. **Invoice to Contract Integrity**: Validate every invoice references a valid contract.
   - Rationale: Invoice-to-contract linkage is required for rental billing lineage.
   - SQL Example:
```sql
SELECT i.*
FROM silver.invoices i
LEFT JOIN silver.contracts c
  ON i.contract_id = c.contract_id
WHERE c.contract_id IS NULL;
```

28. **Invoice to Customer Integrity**: Validate every invoice customer exists in conformed customers.
   - Rationale: Outstanding invoice reporting must map to valid customers.
   - SQL Example:
```sql
SELECT i.*
FROM silver.invoices i
LEFT JOIN silver.customers c
  ON i.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

29. **Applied Receipt to Invoice Integrity**: Validate applied payments reference valid invoices, while unapplied cash remains separately flagged.
   - Rationale: Constraints allow unapplied cash, but applied records must reference a valid invoice.
   - SQL Example:
```sql
SELECT r.*
FROM silver.cash_receipts r
LEFT JOIN silver.invoices i
  ON r.invoice_id = i.invoice_id
WHERE r.match_status = 'APPLIED' AND i.invoice_id IS NULL;
```

30. **Branch to Hierarchy Integrity**: Validate every branch used in Silver facts exists in the conformed hierarchy mapping.
   - Rationale: Reporting consistency depends on valid branch-region-organization alignment.
   - SQL Example:
```sql
SELECT f.branch_code
FROM silver.rental_revenue f
LEFT JOIN silver.branch_hierarchy h
  ON f.branch_code = h.branch_code
WHERE h.branch_code IS NULL
GROUP BY f.branch_code;
```

31. **Fact-to-Date Integrity**: Validate all Silver fact records link to a valid reporting date.
   - Rationale: Required across revenue, AR aging, cash application, and credit risk facts.
   - SQL Example:
```sql
SELECT f.*
FROM silver.ar_aging f
LEFT JOIN silver.dim_date d
  ON f.snapshot_date = d.calendar_date
WHERE d.calendar_date IS NULL;
```

### 5.4 Business Rule and Derived Metric Checks

32. **Net Billings Reconciliation Check**: Validate `net_billings = gross_billings - credit_memo_amount`.
   - Rationale: Explicit business rule and dependency.
   - SQL Example:
```sql
SELECT *
FROM silver.rental_revenue
WHERE ROUND(net_billings,2) <> ROUND(gross_billings - credit_memo_amount,2);
```

33. **Health Score Range Check**: Validate `health_score` is between 0 and 100.
   - Rationale: Constraints explicitly define valid score range.
   - SQL Example:
```sql
SELECT *
FROM silver.executive_scorecard
WHERE health_score < 0 OR health_score > 100 OR health_score IS NULL;
```

34. **Health Score Weighted Rollup Check**: Validate overall health score matches weighted normalized component scores.
   - Rationale: Business rule requires configurable weighted composition.
   - SQL Example:
```sql
SELECT *
FROM silver.executive_scorecard
WHERE ROUND(health_score,2) <> ROUND(
  revenue_score * revenue_weight +
  ar_score * ar_weight +
  cash_app_score * cash_app_weight +
  credit_risk_score * credit_risk_weight, 2);
```

35. **Aging Bucket Allowed Values Check**: Validate aging bucket is one of `0-30`, `31-60`, `61-90`, `90+`.
   - Rationale: Constraints require fixed, non-overlapping categories.
   - SQL Example:
```sql
SELECT aging_bucket, COUNT(*)
FROM silver.ar_aging
WHERE aging_bucket NOT IN ('0-30','31-60','61-90','90+') OR aging_bucket IS NULL
GROUP BY aging_bucket;
```

36. **Aging Bucket Derivation Check**: Validate bucket assignment matches `snapshot_date - due_date`.
   - Rationale: Bucket must be derived consistently from due date and snapshot date.
   - SQL Example:
```sql
SELECT *, datediff(snapshot_date, due_date) AS days_past_due
FROM silver.ar_aging
WHERE (datediff(snapshot_date, due_date) BETWEEN 0 AND 30 AND aging_bucket <> '0-30')
   OR (datediff(snapshot_date, due_date) BETWEEN 31 AND 60 AND aging_bucket <> '31-60')
   OR (datediff(snapshot_date, due_date) BETWEEN 61 AND 90 AND aging_bucket <> '61-90')
   OR (datediff(snapshot_date, due_date) > 90 AND aging_bucket <> '90+');
```

37. **Aging Bucket Total Reconciliation**: Validate bucketed AR totals reconcile to `total_ar_outstanding`.
   - Rationale: Constraint requires aging bucket totals to tie to overall AR.
   - SQL Example:
```sql
SELECT customer_id, snapshot_date,
       SUM(bucket_amount) AS bucket_total,
       MAX(total_ar_outstanding) AS total_ar_outstanding
FROM silver.ar_aging_bucket_detail
GROUP BY customer_id, snapshot_date
HAVING ROUND(SUM(bucket_amount),2) <> ROUND(MAX(total_ar_outstanding),2);
```

38. **AR 90+ Percentage Formula Check**: Validate `ar_90_plus_pct = ar_90_plus_amount / total_ar_outstanding` when denominator is non-zero.
   - Rationale: Required dependency-based validation.
   - SQL Example:
```sql
SELECT *
FROM silver.ar_aging_summary
WHERE total_ar_outstanding > 0
  AND ROUND(ar_90_plus_pct,4) <> ROUND(ar_90_plus_amount / total_ar_outstanding,4);
```

39. **DSO Denominator Check**: Validate DSO is calculated only when total credit sales and days in period are valid and non-zero.
   - Rationale: Rate-based calculations must not use zero denominators.
   - SQL Example:
```sql
SELECT *
FROM silver.ar_aging_summary
WHERE dso IS NOT NULL
  AND (total_credit_sales_in_period <= 0 OR number_of_days_in_period <= 0);
```

40. **Credit Utilization Formula Check**: Validate `credit_utilization_pct = outstanding_ar / credit_limit` when credit limit is greater than zero.
   - Rationale: Ensures valid credit exposure calculations.
   - SQL Example:
```sql
SELECT *
FROM silver.credit_risk
WHERE credit_limit > 0
  AND ROUND(credit_utilization_pct,4) <> ROUND(outstanding_ar / credit_limit,4);
```

41. **Over-Limit Customer Flag Check**: Validate customers flagged as over-limit actually have `outstanding_ar > credit_limit`.
   - Rationale: Prevents false risk escalation and reporting errors.
   - SQL Example:
```sql
SELECT *
FROM silver.credit_risk
WHERE over_limit_flag = 'Y' AND NOT (outstanding_ar > credit_limit);
```

42. **Suspended Customer Open Exposure Check**: Validate suspended customers with open exposure are correctly identified when AR or open contracts exist.
   - Rationale: Explicit credit risk reporting rule.
   - SQL Example:
```sql
SELECT *
FROM silver.credit_risk
WHERE UPPER(customer_status) = 'SUSPENDED'
  AND (outstanding_ar > 0 OR open_contract_count > 0)
  AND suspended_open_exposure_flag <> 'Y';
```

43. **Applied Amount Does Not Exceed Invoice Amount**: Validate cumulative applied payments do not exceed related invoice amount.
   - Rationale: Constraint explicitly prohibits over-application.
   - SQL Example:
```sql
SELECT r.invoice_id, SUM(r.applied_amount) AS total_applied, MAX(i.invoice_amount) AS invoice_amount
FROM silver.cash_application r
JOIN silver.invoices i
  ON r.invoice_id = i.invoice_id
GROUP BY r.invoice_id
HAVING SUM(r.applied_amount) > MAX(i.invoice_amount);
```

44. **Unapplied Cash Flagging Check**: Validate receipts without valid invoice applications are retained and flagged as unapplied.
   - Rationale: Business rules require unapplied cash to be reported separately, not dropped.
   - SQL Example:
```sql
SELECT *
FROM silver.cash_receipts
WHERE invoice_id IS NULL AND (match_status IS NULL OR UPPER(match_status) <> 'UNAPPLIED');
```

45. **Average Days to Pay Logical Check**: Validate `payment_date >= invoice_date` for paid invoices and receipts.
   - Rationale: Negative days-to-pay usually indicates source sequencing issues.
   - SQL Example:
```sql
SELECT r.*, i.invoice_date
FROM silver.cash_receipts r
JOIN silver.invoices i
  ON r.invoice_id = i.invoice_id
WHERE to_date(r.receipt_date) < to_date(i.invoice_date);
```

46. **ADR Calculation Guardrail**: Validate ADR excludes zero-duration or cancelled contracts.
   - Rationale: Business rules explicitly prohibit inclusion of zero-duration or cancelled contracts in ADR.
   - SQL Example:
```sql
SELECT *
FROM silver.rental_revenue_detail
WHERE adr IS NOT NULL
  AND (total_billed_rental_days <= 0 OR UPPER(contract_status) = 'CANCELLED');
```

47. **Revenue per Contract Denominator Check**: Validate revenue-per-contract is computed only when contract count is non-zero.
   - Rationale: Avoids invalid ratio calculations.
   - SQL Example:
```sql
SELECT *
FROM silver.rental_revenue_summary
WHERE revenue_per_contract IS NOT NULL AND contract_count <= 0;
```

48. **CEI Input Window Consistency Check**: Validate beginning AR, credit sales, ending total AR, and ending current AR use the same reporting window.
   - Rationale: CEI is meaningful only when all components belong to the same period.
   - SQL Example:
```sql
SELECT *
FROM silver.cash_application_summary
WHERE begin_period <> credit_sales_period
   OR begin_period <> ending_total_ar_period
   OR begin_period <> ending_current_ar_period;
```

49. **Drill-Through Reconciliation Check**: Validate summarized values reconcile to underlying fact-level totals.
   - Rationale: Reporting logic requires drill-through totals to tie to fact detail.
   - SQL Example:
```sql
SELECT s.branch_name, s.report_date,
       s.net_billings AS summary_value,
       d.detail_total
FROM silver.rental_revenue_summary s
JOIN (
  SELECT branch_name, report_date, SUM(net_billings) AS detail_total
  FROM silver.rental_revenue_detail
  GROUP BY branch_name, report_date
) d
  ON s.branch_name = d.branch_name AND s.report_date = d.report_date
WHERE ROUND(s.net_billings,2) <> ROUND(d.detail_total,2);
```

50. **Cross-Domain Branch/Region Conformance Check**: Validate the same branch maps to the same region across revenue, AR, cash application, and credit risk datasets.
   - Rationale: Business rules require a common rollup structure across all domains.
   - SQL Example:
```sql
SELECT branch_code, COUNT(DISTINCT region) AS region_cnt
FROM (
  SELECT branch_code, region FROM silver.rental_revenue
  UNION ALL
  SELECT branch_code, region FROM silver.ar_aging
  UNION ALL
  SELECT branch_code, region FROM silver.cash_application
  UNION ALL
  SELECT branch_code, region FROM silver.credit_risk
) x
GROUP BY branch_code
HAVING COUNT(DISTINCT region) > 1;
```

## 6. Suggested Test Coverage by Silver Table

| Silver Table | Recommended Minimum DQ Themes |
|---|---|
| `silver.contracts` | null checks, date validity, contract status domain, customer FK, branch conformance |
| `silver.invoices` | uniqueness, date validity, amount sign logic, contract FK, customer FK, currency validation |
| `silver.cash_receipts` | receipt uniqueness, payment amount non-negative, receipt date validity, invoice FK for applied receipts, unapplied cash flagging |
| `silver.customers` | customer deduplication, mandatory fields, credit limit range, status domain, customer since date validation |
| `silver.branch_employee` | region completeness, role domain, effective-date validity, branch alignment |
| `silver.ar_aging` | snapshot grain, aging bucket derivation, AR bucket reconciliation, AR 90+ % formula, fact-date integrity |
| `silver.rental_revenue` | revenue grain, net billing reconciliation, ADR guardrails, revenue per contract denominator, drill-through reconciliation |
| `silver.cash_application` | CEI window consistency, applied amount controls, average days to pay, unapplied cash handling |
| `silver.credit_risk` | customer risk grain, credit utilization formula, over-limit logic, suspended exposure flagging |

## 7. Implementation Notes for Databricks Unit Testing
- Implement these checks using PySpark expectations, SQL-based assertions, or Delta Live Tables expectations.
- Persist failed-record quarantine tables for critical violations such as invalid keys, duplicate business grain, and formula mismatches.
- Separate rejectable issues from reportable exceptions; for example, unapplied cash is a valid business exception but must be flagged.
- Parameterize allowed-domain values and weighted-score thresholds for maintainability.
- Track DQ execution audit results with check name, severity, failed row count, run timestamp, and source table.
- Write the output in the git output folder and maintain version history without overwriting prior files.

## 8. Assumptions
1. Silver tables are conformed outputs derived from the Bronze structures documented in the Bronze physical model.
2. Additional columns such as `snapshot_date`, `match_status`, `applied_amount`, `gross_billings`, `credit_memo_amount`, `net_billings`, and risk metrics exist or will be derived in Silver.
3. The missing Bronze DDL file did not prevent recommendation generation because the Bronze physical document contained sufficient column definitions.
4. No Cognos `.report` file was provided, so Cognos-specific processing was not included.

## 9. API Cost
apiCost: 0.000000 USD

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_DQ_Recommender_2.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_DQ_Recommender/Databricks_Silver_DQ_Recommender_2.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DQ_Recommender
pipelineID : 12360
