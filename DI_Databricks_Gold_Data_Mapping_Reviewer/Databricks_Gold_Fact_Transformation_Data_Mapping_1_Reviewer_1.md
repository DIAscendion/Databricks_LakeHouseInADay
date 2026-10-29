_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Silver-to-Gold Fact Transformation Data Mapping (Rental Revenue-to-Cash) for correctness, consistency, completeness, Databricks best practices and business-requirement alignment.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Gold Fact Transformation Data Mapping – Review Report

## Summary of the Reviewed Input
The reviewed file, `Databricks_Gold_Fact_Transformation_Data_Mapping_1.md`, maps Silver tables (`si_invoices`, `si_rental_contracts`, `si_customer_master`, `si_branch_employee`, `si_cash_receipts`) to four Gold fact tables:
- `go_fct_rental_revenue`
- `go_fct_ar_aging`
- `go_fct_cash_application`
- `go_fct_credit_risk`

For each target field it gives the source field, a validation rule and a transformation rule. It also covers fact-dimension relationships, cleansing rules, KPI explanations and two PySpark snippets.

I checked it against these inputs:
- Gold physical model (`Databricks_Gold_Model_Physical_1.txt`)
- Silver physical model (`Databricks_Silver_Model_Physical_1.md`)
- Constraints (`Rental_Revenue_to_Cash_Reports_Constraints_1.md`)
- Business requirements (`Rental_Revenue_to_Cash_Reports.txt`)

The Recommender file that the mapping cites as a source was not among the review inputs. Rules that say "per recommender" could not be verified.

**Overall verdict:** The mapping has a good skeleton. Credit-memo signing, divide-by-zero protection, bucket domain and sum-of-metric logic are mostly sound. It has significant defects:
- Several source columns do not exist in Silver.
- Outstanding AR is computed without deducting cash.
- The aging-bucket logic is wrong.
- Grains conflict with the uniqueness constraints.
- Several KPI formulas are undefined or not meaningful at fact grain.
- The two aggregate tables, including the Health Score, are not mapped.

---

## 1. Data Mapping Review

### ✅ Correctly mapped Silver to Gold
| Item (Silver → Gold) | Status | Details |
|---|---|---|
| `si_invoices.invoice_date` → `go_fct_rental_revenue.reporting_date` | ✅ | Valid date check and direct map. |
| `si_rental_contracts.{branch_code, sales_rep_id, equipment_class, contract_id, contract_status}` → `go_fct_rental_revenue` | ✅ | Columns exist in Silver and the invoice→contract join is defined. |
| `si_customer_master.{customer_id, customer_name}` → all four facts | ✅ | Columns exist; join keys are valid. |
| `si_invoices.invoice_amount/invoice_type` → `gross_billings`, `credit_memo_amount`, `net_billings`, `invoice_count` | ✅ | Credit memo is stored as `-ABS()`. Net = gross + negative memo, which equals gross − memo as the requirement states. |
| `si_cash_receipts.{receipt_date, invoice_id, payment_method, payment_amount}` → `go_fct_cash_application` | ✅ | The columns exist in Silver. |
| `si_customer_master.{customer_status, credit_limit}` → `go_fct_credit_risk` | ✅ | Columns exist in Silver. |
| `si_rental_contracts.{daily_rate, contract_start_date, contract_end_date, contract_status}` → `open_contract_value` / `open_contract_count` | ✅ | Source columns exist. `GREATEST(…,0)` protects against negative duration. |
| Metadata `load_date`, `update_date`, `source_system` in all four facts | ✅ | Present in every fact mapping and in the Gold DDL. |
| Join approach (Section 4) | ✅ | Keys are consistent with the Silver relationships. |

### ❌ Incorrect or missing mappings
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 1.1 | `si_invoices.aging_bucket`, `si_invoices.days_past_due` (5.2 `aging_bucket`; 5.3 CEI; 5.4 `ar_90_plus_amount_by_customer`) | ❌ | Silver `si_invoices` has no `aging_bucket` or `days_past_due` column. The Gold physical model assumes they are derived in Gold. | Remove them as source fields. Derive from `due_date` and `snapshot_date` only. |
| 1.2 | `si_cash_receipts.match_status`, `si_cash_receipts.unapplied_payment_amount` (5.3 `match_status`, `unapplied_cash_amount`, `unapplied_cash_percentage`) | ❌ | Neither column exists in `silver.si_cash_receipts`. It has only receipt_id, invoice_id, customer_id, receipt_date, payment_amount and payment_method. | Derive `match_status` as `APPLIED` when `invoice_id` is non-null and matches `si_invoices`, otherwise `UNAPPLIED`. Derive unapplied amount as `payment_amount` minus applied amount. Alternatively, add the columns to Silver. |
| 1.3 | `branch_name` missing in all four facts | ❌ | Gold DDL defines `branch_name` in all four facts. It is a mandatory field (Constraints 2.1.1) and is not mapped. | Add a `branch_name` mapping from the branch dimension or branch/region standardization. Silver has no branch name column, so the source must be stated. |
| 1.4 | `region_name` missing in `go_fct_ar_aging`, `go_fct_cash_application`, `go_fct_credit_risk` | ❌ | Region is mandatory (Constraints 2.1.2) for regional rollup, and the same rollup structure is required for all facts (1.4.4). It is mapped only for the revenue fact. | Add a region mapping, derived consistently through branch. Add the column to the DDL if needed. |
| 1.5 | Gold-DDL columns without mapping: surrogate keys `fct_*_sk` (all 4), `billed_rental_days`, `unapplied_payment_count`, `risk_category` (added in Gold DDL section 5.7) | ❌ | These are in the Gold physical model but not mapped. | Map the surrogate key generation. Map `billed_rental_days`, which ADR needs. Map or explicitly defer the other two. |
| 1.6 | Grain and uniqueness not carried into the facts: AR aging has no `invoice_id`. Cash application has no `receipt_id`. | ❌ | Constraints 2.2 require Customer+Invoice+Snapshot Date for AR snapshot and Receipt ID for payments. The mapped AR grain is snapshot, customer, collector, branch, bucket. The cash grain has no `receipt_id`. The requirement also asks for invoice-level drill-through. | Add `invoice_id` to `go_fct_ar_aging` and `receipt_id` to `go_fct_cash_application` in mapping and DDL. Alternatively, document how the uniqueness requirement is met. |
| 1.7 | Aggregate tables `go_agg_executive_health_score`, `go_agg_billing_performance` | ❌ | These tables are in the Gold physical model and are required by report 1 (Health Score 0-100) and report 2. There is no mapping, no weighted score formula and no 0-100 rule. | Add mapping sections for both aggregates. Include configurable weights, domain-score normalization, clamping to 0-100 and reconciliation to the facts. |
| 1.8 | Error and audit targets (`go_error_data`, `go_process_audit`) | ❌ | Section 7 says invalid rows go to "error handling workflows", but no target or field mapping exists. Silver also exposes a shared `silver.si_error_data`. | Map the quarantine destination explicitly and its fields. |
| 1.9 | Source/layer labelling | ❌ | `load_date`, `update_date` and `source_system` list "Silver" as the Source Layer with "Derived" as the table. `source_system='silver_to_gold'` replaces upstream lineage (LEGACY_SE, LOCKBOX_FEED, etc.). | Mark these as "System-generated". Preserve the upstream source system or add a lineage column. |

---

## 2. Data Consistency Validation

### ✅ Properly mapped fields ensuring consistency
| Item | Status | Details |
|---|---|---|
| Business keys (`contract_id`, `customer_id`, `invoice_id`, `branch_code`, `sales_rep_id`) | ✅ | Same names and types (STRING/VARCHAR) across Silver and Gold. |
| Metric names and the Gold DDL | ✅ | Target field names for the mapped measures match the Gold DDL exactly. |
| Net billings = gross + credit memo | ✅ | Consistent with Constraints 1.2.2 and the credit memo sign rule. |
| `customer_status` / `open_contract_count` case handling | ✅ | `upper()` is used consistently for `SUSPENDED` and `OPEN`. |

### ❌ Misaligned or inconsistent mappings
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 2.1 | Source names | ❌ | In 5.2, `collector_id` is sourced from `si_branch_employee.collector_id`, but the transformation says "lookup collector by branch where role is collector". Silver has both `employee_id` and `collector_id`, and the mapping does not say which identifies the collector. | State that `collector_id` is the collector key (or `employee_id` where `role='COLLECTOR'`) and use it consistently. |
| 2.2 | `rental_revenue` vs `gross_billings` | ❌ | Both map to the identical expression (`invoice_amount`, non-credit). The two measures are indistinguishable. | Define `rental_revenue` separately (for example, excluding tax or non-rental charges) or document that they are intentionally equal. |
| 2.3 | `cash_collected` / `payment_amount`, `reporting_date` / `payment_date` | ❌ | These are duplicates (same source, same rule), which adds redundancy and inconsistency risk. | Document the semantic difference, or derive one from the other. |
| 2.4 | Branch/collector fan-out | ❌ | Collector is looked up "by branch". One branch can have several collectors, so facts will duplicate rows and overstate AR and cash. Requirements say Collector 1-M Customer, and Silver has no customer-collector assignment. The Gold DDL puts `collector_id` on `go_dim_customer`, but no source is mapped. | Define the customer→collector assignment source. Dedupe `si_branch_employee` to one current row per employee using `effective_date` before joining. |
| 2.5 | Data type conflicts | ❌ | Section 7 casts all financial values to `DECIMAL(18,2)`. The Gold DDL uses `DECIMAL(18,4)` for ADR/DSO/trend and `DECIMAL(18,6)` for percentages and rates. | Limit the `DECIMAL(18,2)` rule to monetary amounts. Cast rates to the DDL precision. |
| 2.6 | Unit mismatch for percentages | ❌ | Requirements define AR 90+ %, Credit Utilization % and Unapplied Cash % with ×100. The mapping returns ratios. | State whether ratio or percentage is stored and apply it uniformly. |
| 2.7 | Fact-dimension relationship (Section 6) incomplete | ❌ | Missing links:<br>• Date dimension for AR, cash and credit-risk facts (Constraints 2.5.7: all facts link to date).<br>• Equipment-class dimension for revenue.<br>• Region dimension.<br>• Collector dimension for cash application.<br>• Customer/sales-rep/contract for the rest, per the Gold ER model. | Complete the table to match the Gold ER (Gold model section 10). |

---

## 3. Dimension Attribute Transformations

### ✅ Correct category mappings and hierarchy structures
| Item | Status | Details |
|---|---|---|
| Aging bucket domain | ✅ | The four values `0-30`, `31-60`, `61-90`, `90+` match the requirement and `go_code_aging_bucket`. |
| `match_status` standardization (`APPLIED`/`UNAPPLIED`) | ✅ | Defaults to `UNAPPLIED`, so unapplied cash is not dropped. This matches the requirement to report applied and unapplied explicitly. |
| Hierarchy attributes carried in the rental fact | ✅ | `branch_code`, `region_name`, `sales_rep_id` and `equipment_class` exist. |

### ❌ Incorrect or incomplete transformations
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 3.1 | Aging bucket derivation (5.2 text and the PySpark example) | ❌ | `between(0,30)` leaves negative days (not yet due) and null `due_date` falling to `.otherwise('90+')`. Not-yet-due invoices are wrongly classed as 90+, which overstates 90+ AR. | Use `<=30` (including negative days) for `0-30`, handle null `due_date` explicitly by quarantining, and use `>90` for `90+`. |
| 3.2 | `contract_status` standardization | ❌ | The requirement is Open/Closed only. The mapping says "exclude invalid statuses; cancelled may be filtered" and only maps the value directly. There is no mapping to Open/Closed. | Add a mapping table, e.g. `UPPER(TRIM())` mapped to `OPEN`/`CLOSED`, and quarantine unknown values. |
| 3.3 | `customer_status` standardization | ❌ | It is a direct map with no standardization to Active/Suspended. | Standardize to `ACTIVE`/`SUSPENDED` and quarantine others. |
| 3.4 | `equipment_class_name` | ❌ | It is set equal to `equipment_class`. The Gold model has `go_dim_equipment_class` with a separate code and name. | Look it up in `go_dim_equipment_class`, with a fallback only if missing. |
| 3.5 | Region and branch hierarchy | ❌ | Region comes from the sales-rep employee row, not from the branch. A rep's region can differ from the branch's, which breaks "same rollup structure". There is no active-branch check for the selected date (Constraints 1.4.1) and no organization hierarchy mapping. | Derive region and hierarchy from the branch dimension. Validate the branch is active as of the reporting date. |
| 3.6 | Time hierarchy | ❌ | The facts hold only `reporting_date`. There is no mapping to day/week/month/quarter (Constraints 1.3.5) and no `go_dim_date` resolution. | Map `reporting_date` to `go_dim_date` and carry `period_type`. |
| 3.7 | Collector/sales-rep role filter | ❌ | The role value is unspecified ("where role is sales rep/collector"). | State the exact role literals, case-normalized. |

---

## 4. Data Validation Rules Assessment

### ✅ Deduplication logic and format standardization applied correctly
| Item | Status | Details |
|---|---|---|
| Divide-by-zero protection | ✅ | A non-zero denominator is required for ADR, rates, DSO, CEI, utilization and on-time %. Null is returned and a warning logged. |
| Mandatory-field checks | ✅ | `customer_id`, `invoice_id`, `invoice_amount`, `due_date`, `credit_limit`, `branch_code` and dates are listed. |
| Credit-memo sign rule | ✅ | Matches Constraints 2.3.2. |
| Non-negative amounts | ✅ | Standard invoice, payment and credit limit must be non-negative. |
| `invoice_count` | ✅ | Uses `COUNT(DISTINCT invoice_id)`. |

### ❌ Issues with validation logic or missing checks
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 4.1 | Deduplication | ❌ | Only "deduplicate on business key before final aggregation" is stated, and only for credit risk. Not covered:<br>• Duplicate Silver rows (receipts by `receipt_id`, invoices by `invoice_id`, employees by `employee_id` plus `effective_date`).<br>• Duplicate legal-entity customers with multiple IDs (Constraints 1.2.7, 3.1.7, report 5). | Add a documented dedupe step (window `row_number()` over the business key by latest `update_timestamp`). Add a legal-entity survivorship rule or reference to the Silver conformance output. |
| 4.2 | Uniqueness enforcement | ❌ | None of the five uniqueness grains (Constraints 2.2) is validated. Mapped grains differ (see 1.6). | Add post-aggregation duplicate checks per grain that route to the error table. |
| 4.3 | Applied payment ≤ invoice amount | ❌ | This is a stated validation (Constraints 1.2.4, report 4) and is absent. Partial application and one receipt across several invoices are also not tracked. | Add the check and an application-amount field/`unapplied_payment_count`. Quarantine violations. |
| 4.4 | Reconciliation checks | ❌ | The following are missing:<br>• Aging buckets sum to Total AR.<br>• Net billings = gross + credit memo (given as a rule, not as a check).<br>• Drill-through totals match fact totals.<br>• Component scores roll up to the overall score. | Add reconciliation rules, with results logged to `go_error_data` and `go_process_audit`. |
| 4.5 | Format standardization | ❌ | There is no `TRIM`/`UPPER` standardization for IDs and codes. Date validity is only "must be valid". | Add `trim`/`upper` rules for IDs and codes, and date typing checks. |
| 4.6 | ADR exclusion | ❌ | The business rule excludes zero-duration and cancelled contracts. The mapping only says the denominator must be > 0 and that cancelled contracts "may be filtered". | Make the exclusion mandatory: `contract_status <> 'CANCELLED'` and duration > 0. |
| 4.7 | Referential checks | ❌ | Receipt→invoice validity is not checked for applied payments. Branch→hierarchy validity is not checked against a source. | Add referential validation rules with quarantine. |
| 4.8 | Window/period consistency | ❌ | DSO and CEI require the same period, but `days_in_period`, credit-sales window and `snapshot_date` rules are not defined. | Define the period parameter and derive days from `go_dim_date.number_of_days_in_period`. |

---

## 5. Data Cleansing Review

### ✅ Proper handling of missing values and duplicates
| Item | Status | Details |
|---|---|---|
| Missing descriptive attributes | ✅ | Names (customer, collector, sales rep) load as null with a warning. |
| Missing match status | ✅ | `coalesce(match_status,'UNAPPLIED')`. |
| Missing unapplied amount | ✅ | `COALESCE(...,0)`, flagged as "if business-approved". |
| Negative duration | ✅ | `GREATEST(DATEDIFF(),0)`. |
| Quarantine rather than silently drop | ✅ | Stated as a principle in Sections 1 and 7. |

### ❌ Inadequate cleansing logic or missing constraints
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 5.1 | Mandatory names | ❌ | `customer_name` and branch name are mandatory (Constraints 2.1.1 and 2.1.4) but are treated as optional ("leave null and log warning"). | Reject or default to "UNKNOWN" with an error record. |
| 5.2 | Inner joins | ❌ | The example uses inner joins to contracts and customers, which silently drop unmatched invoices. That contradicts the quarantine principle. Receipts with a null `invoice_id` (unapplied) would also lose branch and collector, so unapplied cash disappears. | Use left joins and route failures to the error table. Apply a default branch of `UNASSIGNED` for unapplied receipts, or derive branch from customer. |
| 5.3 | Null `invoice_amount` | ❌ | AR says nulls are treated as zero "only if approved". The constraints make invoice amount mandatory. | Reject null amounts instead of zero-filling. |
| 5.4 | Credit-memo identification | ❌ | It relies on `invoice_type = 'CREDIT_MEMO'` but the allowed values are not defined or standardized. | Add `upper(trim(invoice_type))` and a domain list. |
| 5.5 | Default/imputation for null `credit_limit` | ❌ | Credit limit is mandatory for utilization, yet null handling is not defined beyond "must be non-negative". Requirement report 5 says a zero or null limit must not error. | Define null limit handling: utilization is null, a flag is raised, and the over-limit logic is skipped or defined. |
| 5.6 | Currency | ❌ | Silver `currency` is not used or validated. Only a future-state note exists. | Add a single-currency validation. |

---

## 6. Compliance with Microsoft Databricks Best Practices

### ✅ Adheres to Databricks best practices
| Item | Status | Details |
|---|---|---|
| Delta tables and DataFrame/Spark SQL patterns | ✅ | Section 9 uses PySpark/Spark SQL, Delta, `lag`, window functions and decimal types. |
| Error routing instead of failing the job | ✅ | Validation failures go to error handling tables. |
| Decimal types for financial values | ✅ | Spark decimal types are specified. |

### ❌ Violations of recommended design and implementation guidelines
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 6.1 | Non-deterministic snapshots | ❌ | `snapshot_date = current_date()` is non-deterministic, so reruns or backfills produce different data. | Pass `snapshot_date` as a job parameter (Databricks widget/job parameter). |
| 6.2 | No incremental / idempotent load | ❌ | There is no `MERGE INTO` or `replaceWhere` strategy, even though the Gold model recommends `MERGE`. | Add a load strategy per fact keyed on its grain. |
| 6.3 | Surrogate key generation | ❌ | The `*_sk` BIGINT columns have no generation logic. | Define deterministic key generation (e.g., hash of business keys) or an approved sequence. |
| 6.4 | Window functions without a defined frame | ❌ | `trend_value` uses `LAG(net_billings)` at contract/rep/equipment grain, partitioned by branch. Several rows share a date, so "previous row" is not the previous period. Similarly `dso_trend` is "by customer" with no ordering stated. | Aggregate to branch/day (or customer/snapshot) first, then apply `LAG` ordered by date. |
| 6.5 | Non-additive KPIs stored on fine-grain rows | ❌ | ADR, `revenue_per_contract`, `credit_memo_rate`, CEI, DSO, `average_days_to_pay` and the percentages are stored per row at contract/receipt grain. Aggregates will average ratios and produce wrong results. | Store additive components (billed days, numerators, denominators) in the facts. Compute ratios at the final grain or in the aggregate or semantic layer. |
| 6.6 | Aging via Python-style `between` logic | ❌ | See 3.1 for the correctness problem. Wide `when` chains are also repeated. | Use a single `bucket` UDF-free expression or join to `go_code_aging_bucket`. |
| 6.7 | Optimization and clustering | ❌ | No `OPTIMIZE`, Z-order, liquid clustering or partition guidance is given in the mapping. It says "consistent with enterprise standards" only. Daily partitioning on `reporting_date`/`snapshot_date` (Gold DDL) risks small files. | Reference the Gold DDL optimization and consider liquid clustering. |
| 6.8 | Naming / governance | ❌ | Two-level names (`gold.go_*`) are used with no Unity Catalog catalog. Error table naming is inconsistent: `go_error_data` in Gold vs shared `silver.si_error_data`. | Use catalog.schema.table naming and one consistent error table. |
| 6.9 | Audit | ❌ | There is no record-count reconciliation (read/written/rejected) written to `go_process_audit`. | Add audit writes per fact load. |
| 6.10 | PySpark examples | ❌ | They cover only partial logic. The revenue example lacks aggregation and `net_billings`. The AR example has the bucket bug. | Complete and correct them. |

---

## 7. Alignment with Business Requirements

### ✅ Gold Layer aligns with Business Requirements
| Item | Status | Details |
|---|---|---|
| Four analytical facts | ✅ | Revenue, AR aging, cash application and credit risk are all present, as the conceptual model requires. |
| Rental/billing KPIs | ✅ | Gross, net, credit memo rate, invoice count and revenue per contract are all provided. |
| DSO, AR 90+ %, Best Possible DSO, DSO trend present | ✅ | Names align with report 3. |
| Credit utilization, over-limit count/amount, suspended with exposure, open contract count/value | ✅ | Logic follows the report 5 definitions. |
| Cash KPIs | ✅ | Cash collected, CEI, average days to pay, on-time %, unapplied $ and % are all present. |

### ❌ Missing attributes or incorrect transformations affecting business logic
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 7.1 | Outstanding AR ignores cash | ❌ | `total_ar_outstanding` (5.2) and `outstanding_ar` (5.4) are sums of `invoice_amount`. They do not subtract applied receipts and do not filter to open invoices. AR is overstated, and DSO, 90+ % and utilization are overstated with it. | Outstanding = invoice amount (net of credit memos) − applied cash, for open invoices only. Join `si_cash_receipts` and filter on balance > 0. |
| 7.2 | ADR definition | ❌ | Requirement is Rental Revenue / Total Billed Rental Days. The mapping uses contract start/end duration. | Compute billed rental days and divide by that. Exclude zero-duration and cancelled contracts. |
| 7.3 | DSO inputs undefined | ❌ | `total_credit_sales` and `days_in_period` have no mapping and no source rule. `best_possible_numerator` is undefined. Best-possible DSO should use current (non-past-due) AR. | Define credit sales as invoices in the period. Define the numerator as current AR. Source days from `go_dim_date`. |
| 7.4 | CEI | ❌ | The formula is "per recommender", with no formula and no mapped Beginning AR, Credit Sales, Ending Total AR or Ending Current AR. The CEI target is stored at receipt-row level. | Spell out the formula `(Beg AR + Credit Sales − End Total AR) / (Beg AR + Credit Sales − End Current AR)`. Derive the inputs by period and compute it at collector/branch/period grain. |
| 7.5 | AR aging grain mix | ❌ | The AR fact is at bucket grain, yet `total_ar_outstanding`, `ar_90_plus_amount`, `ar_90_plus_percentage` and DSO are customer-level while `ar_aging_by_bucket` is bucket-level. Bucket totals cannot be validated against Total AR on the same row. The requirement is Customer+Invoice+Snapshot. | Move the AR fact to invoice grain (see 1.6), or split into a bucket fact and a customer-level fact. |
| 7.6 | Health Score | ❌ | The central scorecard KPI (0-100, weighted, configurable weights) and the executive and billing aggregates are not mapped (see 1.7). | Add the mapping, the weights table and the range check. |
| 7.7 | Credit-risk attributes | ❌ | `credit_terms` and customer tenure (`customer_since`) required by report 5 are not mapped. They are not in `go_fct_credit_risk` and not in the mapping. Executive-level "no PII beyond name" is not addressed. | Add `credit_terms` and `customer_since` (Silver has them) or confirm they come from `go_dim_customer`. Describe row-level security. |
| 7.8 | Credit-risk grain | ❌ | The grain is customer+branch+snapshot. Constraints 2.2.5 require Customer+Snapshot Date. A customer with contracts in several branches creates duplicate customer snapshots and double-counts limit and over-limit amounts. | Use customer+snapshot grain. Allocate a primary branch or use a separate branch-level fact. |
| 7.9 | Duplicate customers | ❌ | The rule "resolve duplicate legal entities before exposure aggregation" is not enforced in the mapping. | Reference the Silver conformed customer key or add a dedupe rule. |
| 7.10 | Security/hierarchy rollups | ❌ | Network→Region→Branch→Rep/Collector drill levels and security filtering attributes are only partly supported (see 3.5 and 1.4). | Carry the hierarchy attributes in every fact. |
| 7.11 | Unapplied cash reporting | ❌ | Unapplied cash must be reported separately and partial application tracked. The mapping lacks an application-level amount, so partial application and multi-invoice receipts are not modeled. | Add applied amount and `unapplied_payment_count`. Keep unapplied rows with a branch/collector fallback. |
| 7.12 | Average days to pay and on-time % | ❌ | Both should be based on paid invoices. The on-time rule uses `receipt_date <= due_date` per receipt, so a partial payment counts as paid on time. | Use the date of the final payment that fully settles each invoice, counted per invoice. |

---

## 8. API Cost
```
apiCost: 0.000000
```
