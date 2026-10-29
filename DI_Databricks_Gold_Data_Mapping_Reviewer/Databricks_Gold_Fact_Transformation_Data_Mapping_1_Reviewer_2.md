_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Silver-to-Gold fact transformation data mapping for Rental Revenue-to-Cash against the Silver and Gold physical models, constraints, and business requirements.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Gold Data Mapping Review: Rental Revenue to Cash Reports

## Summary of Reviewed Input
The reviewed file is `Databricks_Gold_Fact_Transformation_Data_Mapping_1.md`. It maps five Silver tables to four Gold facts. The Silver tables are `si_invoices`, `si_rental_contracts`, `si_customer_master`, `si_branch_employee` and `si_cash_receipts`. The Gold facts are `go_fct_rental_revenue`, `go_fct_ar_aging`, `go_fct_cash_application` and `go_fct_credit_risk`. The mapping has field-level rows per fact, a fact-dimension relationship table, validation and cleansing rules, and PySpark patterns.

The review checked it against:
- the Silver physical model;
- the Gold physical model (DDL);
- the constraints file;
- the business requirements (`Rental_Revenue_to_Cash_Reports.txt`).

Main finding: the mapping has good field coverage for the four facts. However, several mappings read Silver columns that do not exist, and several KPI formulas contradict the business requirements. The two aggregate tables and the dimensions are not mapped.

---

## 1. Data Mapping Review

### ✅ Correctly mapped
| Item (Silver → Gold) | Status | Details |
|---|---|---|
| All four fact targets (`go_fct_rental_revenue`, `go_fct_ar_aging`, `go_fct_cash_application`, `go_fct_credit_risk`) | ✅ | Every Gold fact column in the DDL is mapped, except those listed under ❌. |
| `si_invoices.invoice_date` → `go_fct_rental_revenue.reporting_date` | ✅ | Valid date, not-null rule. |
| `si_rental_contracts.{branch_code, sales_rep_id, equipment_class, contract_id, contract_status}` → rental revenue fact | ✅ | Direct maps, correct source tables. |
| `si_customer_master.{customer_id, customer_name}` → all four facts | ✅ | Correct source. |
| `si_cash_receipts.{receipt_date, invoice_id, payment_method, payment_amount}` → cash application fact | ✅ | Correct Silver columns. |
| `si_customer_master.{customer_status, credit_limit}` → credit risk fact | ✅ | Correct Silver columns. |
| `si_rental_contracts.{daily_rate, contract_start_date, contract_end_date, contract_status}` → `open_contract_value` / `open_contract_count` | ✅ | Source columns exist and the duration is guarded with `GREATEST(...,0)`. |
| Audit columns `load_date`, `update_date`, `source_system` | ✅ | Present on all four facts. |
| Join approach (section 4) | ✅ | Matches the joins in the Silver and Gold physical models (invoice→contract, invoice→customer, receipt→invoice, receipt→customer, contract.sales_rep_id→employee_id). |

### ❌ Incorrect or missing
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 1.1 | `go_fct_ar_aging.aging_bucket` (source `si_invoices.days_past_due`, `aging_bucket`) | ❌ | `si_invoices` has neither `aging_bucket` nor `days_past_due`. Both are Gold-derived (Gold model assumption 4). | Remove the Silver references. Derive only from `snapshot_date - due_date`. |
| 1.2 | `go_fct_cash_application.match_status` (source `si_cash_receipts.match_status`) | ❌ | `si_cash_receipts` has no `match_status`. | Derive it from a `si_cash_receipts` to `si_invoices` join on `invoice_id`: `APPLIED` if the invoice resolves, otherwise `UNAPPLIED`. |
| 1.3 | `go_fct_cash_application.unapplied_cash_amount` (source `si_cash_receipts.unapplied_payment_amount`) | ❌ | `unapplied_payment_amount` does not exist in Silver. | Derive it as `payment_amount` where there is no valid invoice match, plus the residual over the invoice amount. Track partial application, as the requirements say. |
| 1.4 | `best_possible_dso`, `dso`, `collector_id`, `cash_collected` | ❌ | The Silver sources are only partly valid. `aging_bucket` is referenced from Silver. `collector_id` is mapped with no stated join key. Credit sales is never defined as a measure. | Define credit sales explicitly. Define the collector join key. |
| 1.5 | `branch_name` in all four facts | ❌ | The Gold DDL has `branch_name`, but the mapping has no row for it. No Silver source exists (`si_branch_employee` has only `branch_code` and `region`). | Add a mapping from a Gold `go_dim_branch` lookup. Fail the load if it does not resolve (the constraints make Branch Name mandatory). |
| 1.6 | `fct_*_sk` surrogate keys (4 facts) | ❌ | Every Gold fact DDL has an SK column, but no mapping row or generation rule exists. | Add a deterministic SK rule, for example a hash of the grain keys. |
| 1.7 | Columns added by the Gold DDL `ALTER` (`billed_rental_days`, `unapplied_payment_count`, `risk_category`) | ❌ | Not mapped. `billed_rental_days` is needed for ADR. | Add mapping rows. |
| 1.8 | `receipt_id` | ❌ | The constraints require Receipt ID to uniquely identify a payment record. It is not carried into `go_fct_cash_application` (neither the mapping nor the DDL has it). | Map `si_cash_receipts.receipt_id`. Raise a change request on the Gold physical model. |
| 1.9 | `go_agg_executive_health_score` and `go_agg_billing_performance` | ❌ | Both are defined in the Gold physical model and required by the requirements (health score 0–100, billing performance). No mapping exists. | Add section 5.5 and 5.6 mappings, or state that they are out of scope. |
| 1.10 | `go_dim_*` and `go_code_*` tables | ❌ | No Silver→Gold mappings. Section 6 refers to dimensions that this document never populates. | Add dimension mappings, or reference the document that covers them. |
| 1.11 | Input list (section 2) | ❌ | The Gold physical model, the constraints file and the business requirements are not listed as inputs. The recommender file it cites was not provided for this review. | Add the missing inputs. |
| 1.12 | `si_cash_receipts` → `si_invoices` → `si_rental_contracts` for the branch derivation | ❌ | The `go_fct_cash_application.branch_code` path is stated only as text, with no join key and no handling of unapplied receipts (no invoice, so no branch). | Specify the fallback, for example the customer's branch, or quarantine. |

---

## 2. Data Consistency Validation

### ✅ Properly mapped
| Item | Status | Details |
|---|---|---|
| Datatypes | ✅ | Money values use `DECIMAL(18,2)`, consistent with Silver. Gold DDL uses wider precision for ratios, and this is acceptable. |
| Column names | ✅ | Names in the mapping match the Gold DDL (no extra or misspelled targets). |
| Credit memo sign | ✅ | `-ABS(invoice_amount)` is consistent with the "must be negative" constraint. |
| `net_billings = gross_billings + credit_memo_amount` | ✅ | Correct, because the credit memo is stored as a negative value. |
| `average_days_to_pay` | ✅ | Matches the requirement: payment date minus invoice date for paid (applied) invoices. |
| `credit_utilization_percentage`, `open_contract_count` | ✅ | Consistent with the requirements formulas (see 5.2 for the ×100 point). |

### ❌ Misaligned or inconsistent
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 2.1 | `go_fct_rental_revenue.rental_revenue` and `gross_billings` | Identical definitions (sum of non-credit invoices). The two columns are indistinguishable. | Define `rental_revenue` as the billed rental charge excluding tax. Define `gross_billings` as invoices including tax, or document why they are equal. |
| 2.2 | Grain of `go_fct_rental_revenue` | The mapping grain is date, contract, branch, rep, equipment class and customer. The constraints require uniqueness on (Branch, Date, Sales Rep, Equipment Class). The aggregate is not defined. | Document the grain. Add a unique-grain check before the load. |
| 2.3 | Grain of `go_fct_ar_aging` | The mapping grain is snapshot, customer, collector, branch and bucket. The constraints require (Customer, Invoice, Snapshot Date). Invoice is not mapped (no `invoice_id` in the fact). | Add `invoice_id`, or alter the grain and update the requirements and constraints. |
| 2.4 | Contradicting reporting dates | `go_fct_ar_aging.snapshot_date` is `current_date()`, so history cannot be rebuilt and a rerun produces a different result. Same for credit risk. | Use a controlled snapshot parameter. |
| 2.5 | `silver.si_branch_employee` joins | The sales rep join uses `employee_id` plus branch. The collector join uses branch and role only, so one branch with several collectors fans out rows and double-counts AR and cash. | Use `si_branch_employee.collector_id` with an effective date (`effective_date`), and choose a single collector per customer or branch. |
| 2.6 | `ar_aging_by_bucket` | Duplicates `total_ar_outstanding` at bucket grain. Naming is confusing next to `aging_bucket`. | Keep a single per-bucket measure, and document that bucket rows sum to `total_ar_outstanding`. |
| 2.7 | `go_fct_ar_aging.total_ar_outstanding` | The mapping sums invoice amounts without removing payments or credit memos, so it counts paid invoices as outstanding. | Subtract applied receipts and credit memos. Include only open balances. |
| 2.8 | `go_fct_credit_risk.outstanding_ar` | Same gross-invoice issue as 2.7. | Use the same open-balance logic. |
| 2.9 | `go_fct_credit_risk.ar_90_plus_amount_by_customer` | Depends on the invalid aging logic (see 3.2). | Use the corrected bucket. |
| 2.10 | `source_system` | The constant `'silver_to_gold'` discards lineage from the Silver `source_system` values. | Propagate the Silver `source_system` or use an enterprise lineage value. |

---

## 3. Dimension Attribute Transformations

### ✅ Correct
| Item | Status | Details |
|---|---|---|
| Aging bucket domain | ✅ | `0-30`, `31-60`, `61-90`, `90+` match the constraints. |
| Fact-dimension table (section 6) | ✅ | Covers date, branch, sales rep, contract, customer, collector, aging bucket and invoice. |
| Customer status / contract status | ✅ | Compared with `upper()`. |
| Equipment class | ✅ | `equipment_class` mapped directly, with a standardized-domain rule. |

### ❌ Incorrect or incomplete
| # | Item | What is wrong | Recommended fix |
|---|---|---|---|
| 3.1 | Hierarchy (Region → Branch → Sales Rep / Collector) | `region_name` is mapped only for the revenue fact. AR aging, cash application and credit risk facts have no `region_name` mapping. The hierarchy needed for drill-down and security filtering is not stated. | Resolve `region_name` through `go_dim_branch`, and publish the hierarchy on every fact. |
| 3.2 | Aging bucket logic (section 10 and 5.2) | `between(0,30)` means `0-30`, but negative `datediff` values (not yet due) are not handled. They fall to `.otherwise("90+")`, so current invoices are reported as 90+. This is a serious defect. | Add a `current`/not-due rule (days ≤ 0 goes into `0-30` or is excluded per the business decision). Quarantine null `due_date`. Reserve `90+` for `> 90`. |
| 3.3 | Fact-dimension relationships | Fact→dimension relationships are listed, but no surrogate-key lookups (`dim_*_sk`) are defined. Joins to `go_dim_date` and `go_dim_equipment_class` are missing (`equipment_class_name` is a plain copy). | Add SK lookups and a rule for unmatched dimension members (for example an "Unknown" member). |
| 3.4 | `equipment_class_name` | Copied from the code. The Gold model has `go_dim_equipment_class`. | Look it up from the dimension. |
| 3.5 | Customer status and contract status domains | The requirement is Active/Suspended and Open/Closed. No mapping of other source values. | Add an explicit value map and a default. |
| 3.6 | Time hierarchy | Constraints need day, week, month and quarter. The mapping has only `reporting_date`. | Join `go_dim_date` for period attributes. |

---

## 4. Data Validation Rules Assessment

### ✅ Correct
| Item | Status | Details |
|---|---|---|
| Mandatory field and null checks | ✅ | Listed for key fields (customer, invoice, amount, due date, credit limit, branch). |
| Divide-by-zero protection | ✅ | Applied to ADR, DSO, CEI, utilization, on-time percentage, credit memo rate and unapplied cash %. Rule: return null and log. |
| Match status standardization | ✅ | `APPLIED` / `UNAPPLIED` via `CASE`. |
| Non-negative invoice and payment amounts | ✅ | Stated. |
| Contract duration guard | ✅ | `GREATEST(DATEDIFF(...),0)` for open contract value. |

### ❌ Issues
| # | Issue | Recommended fix |
|---|---|---|
| 4.1 | Applied payment must not exceed the related invoice amount (constraint 1.2.4). No rule. | Add the check and route breaches to the error table. |
| 4.2 | Aging bucket totals must reconcile to Total AR Outstanding. No reconciliation rule. | Add a post-load reconciliation. |
| 4.3 | Health score must be between 0 and 100, and domain scores must roll up by configured weights. No mapping or rule. | Add the aggregate mapping (see 1.9). |
| 4.4 | Duplicate customer resolution. The mapping says "deduplicate on business key", but gives no key (the requirement says same legal entity, multiple IDs). | Define the matching key. Dedupe in Silver before aggregation. |
| 4.5 | ADR must exclude zero-duration and cancelled contracts. The ADR mapping excludes only zero duration. `contract_status` is not filtered. | Add a `contract_status <> 'CANCELLED'` rule. The domain says Open/Closed, so confirm the cancelled value. |
| 4.6 | Format standardization for IDs and codes (trim, upper, null-pad) and date format. Only numeric and bucket formats are covered. | Add `trim`/`upper` for ID and code fields. |
| 4.7 | Branch must be active on the selected date. No rule. | Check against `go_dim_branch.branch_status`. |
| 4.8 | Credit memo detection. The mapping uses `invoice_type = 'CREDIT_MEMO'` but the domain of `invoice_type` is not confirmed in Silver. | Validate the value domain first. |
| 4.9 | Unique-grain checks for all four facts (constraints 2.2). No uniqueness validation. | Add a duplicate check on each grain key. |
| 4.10 | Referential checks: invoice→contract, receipt→invoice, outstanding invoice→customer. They are stated in the join approach but not as validation rules with a failure action. | Add them as rules with a failure path. |
| 4.11 | Window alignment for DSO, best possible DSO and CEI. They are described in prose only. `days_in_period` and `total_credit_sales` have no definition. | Source `days_in_period` from `go_dim_date.number_of_days_in_period` and define `total_credit_sales`. |

---

## 5. Data Cleansing Review

### ✅ Proper handling
| Item | Status | Details |
|---|---|---|
| Missing descriptive attributes | ✅ | Names load as null with a warning. |
| Quarantine instead of silent drop | ✅ | The overview states invalid records are routed to error handling. |
| Credit memo sign correction | ✅ | `-ABS`. |
| Null unapplied amount | ✅ | `COALESCE(...,0)`, flagged as business approved. |

### ❌ Inadequate
| # | Issue | Recommended fix |
|---|---|---|
| 5.1 | The quarantine target is not named. Gold has `gold.go_error_data`, and Silver has a shared `silver.si_error_data`. The mapping says only "error handling workflows". | Name `gold.go_error_data` and map its fields (`target_table_name`, `validation_rule_name`, `source_record_id`). |
| 5.2 | Percentages: the business requirement defines percentages × 100 (AR 90+ %, credit utilization %, unapplied cash %, CEI). The mapping omits ×100. The Gold DDL does not say whether the value is a ratio or a percentage. | Decide and document one convention. |
| 5.3 | Duplicate removal on source rows (invoices, receipts) before aggregation. Only customer dedupe is mentioned. `COUNT(DISTINCT)` partly covers invoices, but sums are not protected. | Dedupe `invoice_id` and `receipt_id` before summing. |
| 5.4 | Null `credit_limit`. Mandatory per the constraints, yet the divide-by-zero rule only returns null for zero. Null or zero limit handling for `customers_over_limit_*` is undefined (`outstanding_ar > NULL` is null, so the count is wrong). | Treat a null limit as a validation error. Define the over-limit rule for a zero limit. |
| 5.5 | Null `due_date` or `invoice_amount` in AR. "Treated as zero only if approved" is ambiguous. | Quarantine them, since the constraints make both mandatory. |
| 5.6 | Row-level metric mappings at the wrong grain. `average_days_to_pay`, `invoices_paid_on_time_percentage` and `unapplied_cash_percentage` are defined as aggregates, yet the fact grain is one row per payment application. `customers_over_limit_count` is per row, and fan-out through collector or contract joins would inflate sums. | State the aggregation level. Compute ratios from summed numerators and denominators, not from averaged row ratios. |
| 5.7 | `trend_value` and `dso_trend` use `LAG` over the row grain (contract rows partitioned by branch). They compare unrelated rows. | Aggregate to a period first, then apply `LAG` at the period grain. |
| 5.8 | `invoice_count` and `revenue_per_contract` are computed row-wise but they are non-additive across rollups. | Store the numerator and denominator in the fact or aggregate. |

---

## 6. Compliance with Microsoft Databricks Best Practices

### ✅ Adheres
| Item | Status | Details |
|---|---|---|
| Delta Lake as target | ✅ | Loads into Gold Delta tables. |
| PySpark / Spark SQL patterns | ✅ | Uses native functions (`when`, `coalesce`, `datediff`, `lag`). |
| Decimal types for finance | ✅ | `DECIMAL(18,2)`. |
| Rejected rows are captured | ✅ | Not silently dropped. |
| Divide-by-zero guard | ✅ | Null return rather than failure. |

### ❌ Violations
| # | Issue | Recommended fix |
|---|---|---|
| 6.1 | No incremental or idempotent load strategy. There is no `MERGE` on the grain keys, so reruns duplicate rows. The Gold model itself recommends `MERGE`. | Add `MERGE INTO` or `replaceWhere` on the date partition. |
| 6.2 | `current_date()`/`current_timestamp()` as snapshot dates make runs non-reproducible (see 2.4). | Pass a run parameter. |
| 6.3 | Daily partitioning on `reporting_date` and `snapshot_date` (Gold DDL) creates many small partitions, and the mapping does not address this. | Recommend liquid clustering, or partitioning by month. The mapping only says "consistent with enterprise standards". |
| 6.4 | Joins: the dimension-style joins use full inner joins, with no broadcast hints for small dimensions and no null-key skew handling. Inner joins also drop unmatched rows silently, which conflicts with the quarantine rule. | Use left joins plus an anti-join to quarantine. Broadcast small dimensions. |
| 6.5 | Windows `LAG` without a `partitionBy` size warning, and trend metrics computed in the fact load. | Compute in a separate step after aggregation. |
| 6.6 | No audit mapping. `gold.go_process_audit` (records read, written, rejected) is not populated by any mapping. | Add audit logging for each fact load. |
| 6.7 | No data quality enforcement mechanism (for example Delta `CHECK` constraints or expectations). The Gold model deliberately excludes constraints, but then validation rules must be enforced in code. | Enforce through the pipeline's validation step, or use Delta Live Tables expectations. |
| 6.8 | No Unity Catalog three-level names (`catalog.schema.table`) used in the mapping. | Use the governed catalog namespace. |
| 6.9 | Security. The requirements describe row-level access (branch, region, network) and an executive view without PII beyond the name. No row filter or column mask is referenced. | Add row filters / column masks (Unity Catalog) design notes. |
| 6.10 | `VARCHAR` types in Gold DDL are accepted by Spark but treated as `STRING`. | Prefer `STRING`. |

---

## 7. Alignment with Business Requirements

### ✅ Aligned
| Requirement | Status | Details |
|---|---|---|
| Four facts for revenue, AR aging, cash application, credit risk | ✅ | All present. |
| Credit memo negative, non-credit invoices non-negative | ✅ | Covered. |
| Net billings rule | ✅ | Reconciles to gross plus credit memo (negative). |
| Credit memo rate | ✅ | `ABS(credit_memo)/gross` guarded. |
| Average days to pay, unapplied cash %, utilization %, over-limit, suspended with exposure | ✅ | Present with the right inputs. |
| Aging bucket labels | ✅ | Fixed set. |
| Applied vs unapplied explicit | ✅ | Standardized status field. |

### ❌ Missing attributes or incorrect transformations
| # | Requirement | What is wrong | Recommended fix |
|---|---|---|---|
| 7.1 | ADR = Rental Revenue / Total Billed Rental Days | The mapping divides by `DATEDIFF(contract_end_date, contract_start_date)` (the full contract term). The constraints list billed rental days as the denominator. `billed_rental_days` is in the Gold ALTER but unmapped. | Use billed rental days per invoice or contract. Exclude zero-duration and cancelled contracts. |
| 7.2 | Revenue per Contract = Revenue / Number of Contracts | Mapped as `SUM / COUNT(DISTINCT contract_id)`. At a row grain of one contract, it equals the revenue itself. | Compute at the aggregate grain. |
| 7.3 | `credit_memo_rate` on gross billings | Correct formula, but missing the ×100 convention (see 5.2). | Decide the convention. |
| 7.4 | DSO = (Total AR / Total Credit Sales) × Days in Period | `total_credit_sales` is not defined or mapped. `days_in_period` is not tied to `go_dim_date`. | Define both. |
| 7.5 | Best Possible DSO | Placeholder `best_possible_numerator`, with no definition (typically AR that is current, not yet due). | Define the numerator as current (not past due) AR. |
| 7.6 | CEI = (Beginning AR + Credit Sales − Ending Total AR) / (Beginning AR + Credit Sales − Ending Current AR) × 100 | The transformation says "compute CEI using logic from recommender", with no formula. Beginning AR, ending AR and ending current AR are not mapped. | Write the formula and its source for each input. |
| 7.7 | AR 90+ % (× 100) | Same convention gap. | See 5.2. |
| 7.8 | Health score, domain scores, weights | Entirely missing (no mapping, no config table). | Map `go_agg_executive_health_score`. |
| 7.9 | Weekly and quarterly period views | Not supported (no period attributes or period-type logic). | Add `go_dim_date` joins and a period type. |
| 7.10 | AR drill-through by invoice | The AR fact has no `invoice_id`, so a drill-through "from an aging bucket total to the underlying invoice list" cannot reconcile at fact level. | Add `invoice_id` to the AR fact grain (see 2.3). |
| 7.11 | Collector → Customer assignment | The requirement says Collector 1-M Customer. The mapping derives the collector by branch only. | Use a customer-collector assignment. |
| 7.12 | Cash application: payment applying to zero, one or more invoices, with partial application tracked | No allocation logic (a receipt has a single `invoice_id` in Silver). | Document the limitation. If a receipt can apply to multiple invoices, a Silver bridge or allocation table is needed. |
| 7.13 | Credit risk: customer tenure, credit terms, AR 90+ amount | `credit_terms` and `customer_since` are not mapped to the credit risk fact (the Gold dimension has them, but the fact does not). | Confirm they come from `go_dim_customer`. |
| 7.14 | Credit risk uniqueness (Customer, Snapshot Date) vs the mapping | `branch_code` is part of the mapping grain, so one customer may produce several rows for the same snapshot, which breaks the unique grain. | Remove branch from the grain, or update the requirement. |
| 7.15 | Reconciliation of drill-through totals to `gold.fct_rental_revenue` and `gold.fct_ar_aging` | No reconciliation checks. | Add reconciliation queries per load. |

---

## 8. API Cost
```
apiCost: 0.000000
```
