_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Silver-to-Gold Aggregated Transformation Data Mapping (billing performance and executive health score aggregates) for the Rental Revenue-to-Cash domain.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Gold Aggregated Transformation Data Mapping – Reviewer Report

## Summary of the Reviewed Input
The reviewed document maps two Gold aggregate tables, `gold.go_agg_billing_performance` (13 target fields) and `gold.go_agg_executive_health_score` (13 target fields), to Silver sources (`si_invoices`, `si_rental_contracts`, `si_branch_employee`, `si_cash_receipts`, `si_customer_master`). It defines aggregation, validation and transformation rules, grain, cleansing rules and PySpark patterns. The review compared it with the Gold physical model, the Silver physical model, the constraints file and the business requirements file.

---

## 1. Data Mapping Review

### 1.1 ✅ Correctly mapped
| Item (Silver → Gold) | Status | Details |
|---|---|---|
| Aggregate table coverage | ✅ | Both aggregate tables in the Gold physical model (5.6.1, 5.6.2) are covered. |
| `go_agg_billing_performance` business fields | ✅ | All 13 business columns have a mapping row: reporting_date, region_name, branch_name, sales_rep_name, equipment_class_name, gross_billings, credit_memo_amount, net_billings, rental_revenue, average_daily_rate, revenue_per_contract, credit_memo_rate, invoice_count. |
| `go_agg_executive_health_score` business fields | ✅ | All 13 business columns have a mapping row, including the 7 measures. |
| Grain | ✅ | Billing grain (date, region, branch, sales rep, equipment class) is consistent with the uniqueness rule "Branch, Date, Sales Rep, Equipment Class". |
| Billing joins | ✅ | The `invoices → contracts (contract_id)` and `contracts → employee (sales_rep_id = employee_id)` joins exist in Silver and match the Gold join plan. |
| Silver source columns | ✅ | These exist in Silver: `invoice_date`, `invoice_amount`, `invoice_type`, `invoice_id`, `contract_id`, `branch_code`, `equipment_class`, `daily_rate`, `employee_name`, `region`, `collector_id`, `due_date`, `receipt_date`, `payment_amount`, `credit_limit`. |
| Fields derived from staging | ✅ | `network_level` and the health score are correctly identified as derived rather than direct Silver columns. |

### 1.2 ❌ Incorrect or missing
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 1 | `silver.si_cash_receipts.unapplied_payment_amount` (exec `unapplied_cash_percentage`, PySpark sample) | ❌ | The column does not exist in Silver. `si_cash_receipts` holds only receipt_id, invoice_id, customer_id, receipt_date, payment_amount and payment_method. There is also no match_status. | Derive unapplied cash (a receipt with a null or invalid `invoice_id`, or amount minus applied amount) and document it, or source it from `gold.go_fct_cash_application.unapplied_cash_amount`. |
| 2 | `billed_rental_days` (ADR) | ❌ | It is not in any Silver table. It exists only as an `ALTER` column on `go_fct_rental_revenue`. The mapping calls it "when available". | Map ADR to `go_fct_rental_revenue`, or define a billed-days derivation from contract dates and invoices. |
| 3 | Audit columns of both targets: `agg_*_sk`, `load_date`, `update_date`, `source_system` | ❌ | These columns exist in the Gold DDL but have no mapping rows. | Add mapping rows (surrogate key generation, current_timestamp, source_system constant or lineage). |
| 4 | Gold physical model not used as an input | ❌ | Assumption 9.1 says the Gold DDL "was not directly provided", yet `Databricks_Gold_Model_Physical_1.txt` exists. | Re-base the mapping on the Gold DDL (datatypes, precision). |
| 5 | `collector_name` source | ❌ | No join is defined from invoices, receipts or customers to a collector. Silver has no customer-to-collector assignment. `collector_id` and `employee_name` both come from `si_branch_employee` with no join key. | Define the collector derivation (for example `go_dim_collector` / `go_dim_customer.collector_id`) and the join key. |
| 6 | `branch_name` | ❌ | It is mapped from `branch_code`, so the name column carries a code. Silver has no branch name; Gold has `go_dim_branch.branch_name`. | Map to `go_dim_branch.branch_name` via a `branch_code` lookup. |
| 7 | `equipment_class_name` | ❌ | It is mapped from the code `equipment_class`. | Look up `go_dim_equipment_class.equipment_class_name`. |
| 8 | Source layering | ❌ | The mapping reads Silver directly and treats Gold facts as "optional". The constraints require that drill-through reconcile to `gold.fct_rental_revenue` and `fct_ar_aging`. | Source aggregates from the Gold facts (`go_fct_*`) so totals reconcile by construction. |

---

## 2. Data Consistency Validation

### 2.1 ✅ Properly mapped
| Item | Status | Details |
|---|---|---|
| `invoice_count` | ✅ | `COUNT(DISTINCT invoice_id)` before the descriptive joins; avoids fan-out. |
| `credit_memo_rate` | ✅ | Ratio of sums, `ABS(credit)/gross`, 6 decimals; matches DECIMAL(18,6). |
| `revenue_per_contract` | ✅ | `SUM(rental_revenue)/COUNT(DISTINCT contract_id)`, safe division. |
| `unapplied_cash_percentage`, `ar_90_plus_percentage`, `credit_utilization_percentage` | ✅ | Ratio-of-sums with null on a zero denominator (consistent with business rule 3.2.7). |
| Pre-aggregation by domain, then join on aligned grain | ✅ | Prevents many-to-many fan-out. |
| Precision | ✅ | Currency to 2 decimals and rates to 6 decimals are consistent with the Gold DDL for most fields. |

### 2.2 ❌ Misaligned or inconsistent
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 1 | `gross_billings` vs `credit_memo_amount` vs `net_billings` | `gross_billings = SUM(invoice_amount)` over **all** invoice types, so it includes credit memos. `net_billings = SUM(gross rows) + SUM(credit memo rows)` then counts the credit memos twice. The PySpark sample repeats the error. The constraint is Net = Gross − Credit Memos, with credit memos negative. | `gross_billings = SUM(CASE WHEN invoice_type <> 'CREDIT_MEMO' …)`; `credit_memo_amount = SUM(CASE WHEN invoice_type = 'CREDIT_MEMO' …)`; `net_billings = gross + credit_memo` (credit memos negative). Add a reconciliation check. |
| 2 | `rental_revenue` | It equals `SUM(invoice_amount)` for "rental-related" invoices. The eligible `invoice_type` values are not defined, so it is indistinguishable from gross billings. | Define the eligible invoice-type list and the exclusions explicitly. |
| 3 | Region derivation (billing) | Region comes from the **sales rep's** employee row, while branch comes from the **contract**. The rep's `branch_code` can differ from the contract's `branch_code`, giving an inconsistent branch/region pair. | Derive region from the branch via `go_dim_branch`. Use the same branch/region rollup in all domains (constraint 1.4.4). |
| 4 | `reporting_date` (executive) | Invoice, receipt and snapshot dates are said to be "aligned" with no rule: no period type, no week/month bucketing, no snapshot date. | Define the conformed date (`go_dim_date`) and period logic explicitly. |
| 5 | Executive grain vs uniqueness rule | The constraint keys the health score on (Branch, Date, Period Type). The mapped grain has no period type, and the Gold DDL has no `period_type` column. | Add `period_type` (or document day-only) and align the DDL and mapping. |
| 6 | `credit_utilization_percentage` | Silver has no customer → branch/region/sales rep/collector link, so credit exposure cannot be rolled up to the executive grain. | Use `go_dim_customer` / `go_fct_credit_risk` as the source. |
| 7 | SCD handling of `si_branch_employee` (`effective_date`) | Joining on `employee_id` without an effective-date filter can return multiple rows and duplicate billing amounts. | Pick the current or as-of record, or deduplicate before the join. |
| 8 | Aggregate join keys | The Gold physical model's fact-to-aggregate keys use names (`branch_name`, `sales_rep_name`), which are non-unique. | Join on codes or surrogate keys. |

---

## 3. Dimension Attribute Transformations

### 3.1 ✅ Correct
| Item | Status | Details |
|---|---|---|
| Equipment class | ✅ | Casing and whitespace normalisation before grouping. |
| Flagging of unmatched branch and region values | ✅ | Validation rules flag unmatched branch and region mappings and unsupported equipment classes. |
| Hierarchy fields | ✅ | `region_name`, `branch_name` and `network_level` are present, as are the sales rep and collector levels needed for drill-down (Network → Region → Branch → Rep/Collector). |

### 3.2 ❌ Incorrect or incomplete
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 1 | `network_level` | The derivation is only "through conformed hierarchy staging". `go_dim_branch.network_level` and `organization_hierarchy_name` exist but are not referenced. | Map from `gold.go_dim_branch.network_level`. |
| 2 | Hierarchy roll-up rows | The mandatory-field rule rejects null region, branch and rep keys. Network and region level rows need `ALL`/`NULL` members, so they would be rejected. | Use `GROUPING SETS`/`ROLLUP` with a governed "ALL" member and exempt the non-applicable levels from the non-null rule. |
| 3 | Unknown member | The rep "standardise nulls to governed unknown member only if allowed" is ambiguous and conflicts with "reject nulls". | State a single policy: unknown member `-1/UNKNOWN`, or route to `go_error_data`. |
| 4 | Customer status and contract status | The slicers (customer status) and the contract status dimension of the revenue report are not represented. | Document that they are intentionally excluded, or add them. |
| 5 | Category values | The allowed equipment-class and invoice-type lists are not listed. | Provide the reference value lists. |

---

## 4. Data Validation Rules Assessment

### 4.1 ✅ Correct
| Item | Status | Details |
|---|---|---|
| Grain-uniqueness validation | ✅ | Duplicate-row check on both aggregate grains before publish. |
| Safe division | ✅ | Null (not zero) on a zero denominator. |
| Reconciliation | ✅ | Net vs gross and credit memo; invoice count vs source. |
| Health score bounds | ✅ | `LEAST/GREATEST` bound to 0–100. |
| Outlier and temporal alignment checks | ✅ | DSO, CEI and utilization outliers; same-period alignment. |
| Date format | ✅ | Reject non-parsable invoice dates. |

### 4.2 ❌ Issues
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 1 | Credit memo sign rule | "Credit memos negative; standard invoices non-negative" (constraints 2.3.2/2.3.3) is not enforced. The mapping only "preserves the sign convention". | Add explicit checks and route violations to the error table. |
| 2 | ADR exclusions | The requirement to exclude zero-duration or cancelled contracts (business rule 3.1.4) is absent. | Filter `contract_status` and zero duration out of ADR. |
| 3 | Aging bucket reconciliation | Buckets (0-30, 31-60, 61-90, 90+) must sum to Total AR (constraint 1.2.3). The mapping gives only "allowed aging bucket logic". | Add a bucket-sum reconciliation. |
| 4 | Applied payment ≤ invoice amount | Constraint 1.2.4 is not validated for CEI and unapplied cash. | Add the rule. |
| 5 | Component scores | "Component domain scores roll up to overall score per weights" (constraint 1.2.5) is not validated, and the weights are not defined. | Define weights and persist or validate the component scores. |
| 6 | Active-branch check | Only `branch_code` existence is checked; "active for selected date" (constraint 1.4.1) is not. | Join to the branch status. |
| 7 | Error routing | Rejects go to "an error table" without naming `gold.go_error_data` (needs `source_record_id`, rule names and so on). Records are not tied to `go_process_audit`. | Name the tables and the field mapping. |

---

## 5. Data Cleansing Review

### 5.1 ✅ Correct
| Item | Status | Details |
|---|---|---|
| Null handling | ✅ | `COALESCE` to 0 for additive measures. |
| Zero-denominator handling | ✅ | Ratios return null. |
| Duplicate prevention | ✅ | Distinct counts, pre-aggregation and grain check. |
| Formatting | ✅ | Trim and normalise equipment class, and standardise region names. |
| Precision | ✅ | Rounding per type. |

### 5.2 ❌ Inadequate
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 1 | Customer deduplication | Constraint 1.2.7 and rule 3.1.7 require duplicate customers to be resolved before aggregating exposure. The mapping does not use a conformed customer, so `credit_utilization_percentage` could double count. | Use the deduplicated `go_dim_customer`. |
| 2 | Uniqueness enforcement | There is no concrete method (for example `GROUP BY HAVING COUNT(*)>1` check or `MERGE` on the natural key). The Gold DDL has no constraint enforcement. | Define a dedup/MERGE key: `reporting_date, region, branch, rep, equipment_class` (billing) and `reporting_date, network_level, region, branch, rep, collector` (executive). |
| 3 | Missing receipts or invoices | There is no rule for orphaned invoices (no contract) or orphaned receipts. The left joins would produce null keys that the mandatory rule then rejects without being handled. | Route orphans to the error table with a reason. |
| 4 | Outstanding AR | No formula (invoice amount minus applied receipts as of the snapshot) is given for `ar_90_plus_percentage` and `credit_utilization_percentage`. The mapping sources only `due_date` and `invoice_amount`, which ignores payments. | Define Outstanding AR = invoice − applied receipts as of the reporting date. |

---

## 6. Compliance with Microsoft Databricks Best Practices

### 6.1 ✅ Adheres
| Item | Status | Details |
|---|---|---|
| Delta tables | ✅ | Delta for Gold outputs. |
| Native DataFrame API | ✅ | Built-in functions such as `groupBy`, `countDistinct` and `when` are used instead of UDFs. |
| Pre-aggregation | ✅ | Pre-aggregation to avoid join explosion. |
| Decimal types | ✅ | Decimal for money, not float. |
| Optimisation | ✅ | `OPTIMIZE` and `ZORDER` mentioned. |

### 6.2 ❌ Violations
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 1 | Load pattern | There is no idempotent incremental `MERGE`, overwrite-by-partition, or watermark. A full rebuild is implied. | Specify `MERGE INTO` on the grain keys or `replaceWhere` on `reporting_date`. |
| 2 | Surrogate keys | `agg_*_sk` generation is unspecified. | Use a deterministic hash of the grain keys or similar. |
| 3 | PySpark sample code | `sum` and `round` are used without imports, which shadows Python built-ins (use `F.sum`, `F.round`). The second sample groups by `receipt_date, customer_id`, not the executive grain. The first uses left joins on the employee without deduplication. | Use `import pyspark.sql.functions as F` and match the documented grain. |
| 4 | Partitioning | Daily partitioning of small aggregate tables (`PARTITIONED BY reporting_date`) risks small files. Databricks suggests liquid clustering or Z-ORDER for tables under about 1 TB. | Consider `CLUSTER BY (reporting_date, region_name, branch_name)`. |
| 5 | Layer design | Aggregating Silver directly, bypassing the Gold facts, duplicates business logic across layers. | Build the aggregates from the Gold facts and dimensions. |
| 6 | Operational controls | No reference to `go_process_audit` logging, no Unity Catalog three-level names, no Delta `CHECK` constraints for the 0–100 range, no data-quality expectations (DLT or equivalent). | Add them. |
| 7 | Optimisation guidance | No `OPTIMIZE ... ZORDER` is given for the aggregate tables in the Gold DDL. | Add one. |

---

## 7. Alignment with Business Requirements

### 7.1 ✅ Aligned
| Item | Status | Details |
|---|---|---|
| Report 2 KPIs | ✅ | The KPIs Rental Revenue, Gross/Net Billings, ADR, Revenue per Contract, Credit Memo Rate and invoice count are all present. |
| Report 1 scorecard KPIs | ✅ | Health score, rental revenue, DSO, AR 90+ %, CEI and unapplied cash % are present. |
| Ratio rules | ✅ | Rate-based measures follow the "only if denominator is non-zero" rule. |
| AR 90+ and unapplied cash formulas | ✅ | AR 90+ % and unapplied cash % are ratio-of-sums, consistent with the requirement formulas. |
| Drill-down | ✅ | Drill-down hierarchy attributes exist. |

### 7.2 ❌ Gaps / incorrect
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 1 | Net billings | Credit memos are double counted (see 2.2 #1). | See the fix there. |
| 2 | ADR | The formula is Rental Revenue / Total Billed Rental Days, but billed days are unavailable and the fallback (average of daily rates) deviates from the requirement. The exclusion of cancelled or zero-duration contracts is missing. | See 1.2 #2 and 4.2 #2. |
| 3 | Health score | The requirement is "overall + 4 domain scores (Revenue, AR, Cash App, Credit Risk) with configurable weights". The mapping has only the overall score. Normalisation and weights are undefined ("configured weights"). | Define the weights, normalisation (min/max targets) and the component-score columns, or state they are out of scope. |
| 4 | DSO | The requirement gives DSO = (Total AR / Credit Sales in Period) × Days in Period. The mapping only says "governed AR formula". | State the formula and inputs. |
| 5 | CEI | The requirement gives CEI = (Beginning AR + Credit Sales − Ending Total AR) / (Beginning AR + Credit Sales − Ending Current AR) × 100. The mapping does not state it. | State the formula and a beginning-AR snapshot source. |
| 6 | Percent scale | The requirement multiplies by 100, but the mapping returns fractions. | Document the scale (0–1 or 0–100). |
| 7 | Period support | Day, week, month and quarter reporting is required. The mapping says "optionally derive buckets in downstream views". | Define the period type. |
| 8 | Security | Branch, region and network scope rules are not reflected. | Keep the branch and region keys non-null for row filtering. |

---

## 8. API Cost
```
apiCost: 0.000000
```
