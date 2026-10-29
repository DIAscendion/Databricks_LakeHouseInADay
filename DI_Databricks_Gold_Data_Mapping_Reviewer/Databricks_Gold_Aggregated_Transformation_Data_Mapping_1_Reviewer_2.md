_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Review of the Silver-to-Gold aggregated transformation data mapping (billing performance and executive health score) for the Rental Revenue-to-Cash domain.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Gold Aggregated Transformation Data Mapping – Review Report

**Summary of reviewed input:** The mapping defines two Gold aggregate tables, `gold.go_agg_billing_performance` (12 fields) and `gold.go_agg_executive_health_score` (13 fields). It derives them from `silver.si_invoices`, `silver.si_rental_contracts`, `silver.si_cash_receipts`, `silver.si_customer_master` and `silver.si_branch_employee`. It specifies aggregation rules, validation rules and PySpark patterns. It was checked against the Silver physical model, the Gold physical model, the constraints file and the business requirements text.

**Overall verdict:** The aggregation approach is sound (ratio-of-sums, safe division, pre-aggregation by domain). The mapping has several blocking defects:
1. Wrong grain for the executive aggregate (it ignores `period_type`).
2. Branch name is mapped to `branch_code`.
3. Contract-status and filter gaps.
4. A mapping gap for `average_daily_rate` (the source column is not in the Silver model).
5. Unmapped metrics (`unapplied_payment_amount`, `outstanding_ar`, `billed_rental_days`) that do not exist in Silver.
6. A credit-memo sign convention that conflicts with the constraints.

Ordering note: `Databricks_Gold_Aggregated_Transformation_Data_Mapping_1_Reviewer_1.md` already exists in the output folder, so this review is saved as `_Reviewer_2` per the versioning rule.

---

## 1. Data Mapping Review

### ✅ Correctly mapped Silver to Gold tables / fields
| Item (Silver → Gold) | Status | Details |
|---|---|---|
| `si_invoices.invoice_date` → `go_agg_billing_performance.reporting_date` | ✅ | Valid date source; non-null/parsable validation present. |
| `si_rental_contracts.equipment_class` → `equipment_class_name` | ✅ | Source exists. Trim and case normalization specified. |
| `si_branch_employee.employee_name` → `sales_rep_name` (both aggregates) | ✅ | Join via `sales_rep_id = employee_id` is consistent with the Silver join list. |
| `si_invoices.invoice_amount` → `gross_billings` | ✅ | Cast to DECIMAL(18,2), matches the Gold DDL type. |
| `si_invoices.invoice_id` → `invoice_count` | ✅ | `COUNT(DISTINCT invoice_id)` taken from the invoice base before dimension joins. |
| `si_invoices.invoice_type` + `invoice_amount` → `credit_memo_amount` | ✅ (logic only) | Conditional sum on `invoice_type`. See ❌ 1.5 for sign handling. |
| `si_cash_receipts` → `unapplied_cash_percentage` | ✅ (formula only) | `SUM(unapplied)/SUM(payment)`. See ❌ 1.7 for the source column. |
| `si_customer_master.credit_limit` → `credit_utilization_percentage` | ✅ (denominator) | Column exists in Silver. |
| `si_invoices.due_date` → `ar_90_plus_percentage` | ✅ (inputs) | The due-date based bucketing matches the business rule. |
| Target field coverage vs Gold DDL | ✅ | All 12 billing and 13 executive business columns in the Gold DDL are present in the mapping. |

### ❌ Incorrect or missing mappings
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 1.1 | `branch_name` (both aggregates) ← `si_rental_contracts.branch_code` | ❌ | A code is loaded into a name column. Silver has no branch name column, and the Gold DDL has `go_dim_branch.branch_name`. | Join to `gold.go_dim_branch` on `branch_code` and map `branch_name`. Carry `branch_code` through the grouping for traceability. |
| 1.2 | `region_name` (billing) ← `si_branch_employee.region` via the sales rep | ❌ | Region is derived from the sales rep's employee row, not the contract's branch. A rep with a reassigned branch (`effective_date`) gives inconsistent branch and region pairs. This contradicts the constraint "same branch and region rollup structure". | Derive region from `go_dim_branch` (via `branch_code`), the same conformed hierarchy used everywhere. Use `effective_date` to pick the version in effect at `invoice_date`. |
| 1.3 | `rental_revenue` (both aggregates) | ❌ | The "rental-related invoice types" filter has no defined value list. `invoice_type` values are not specified, and `gross_billings` and `rental_revenue` end up with the same formula. | Define the eligible `invoice_type` set explicitly. Document how `rental_revenue` differs from `gross_billings`, for example excluding tax and non-rental charges. |
| 1.4 | `average_daily_rate` ← `daily_rate`, `billed_rental_days` | ❌ | The ratio denominator `billed_rental_days` is not in any Silver table. It exists only as a Gold `ALTER TABLE` add-on on `go_fct_rental_revenue`. There is no mapping row or derivation for it. The business rule to exclude zero-duration or cancelled contracts is missing. The fallback "average of daily rates" contradicts the ratio-of-sums principle. | Add a mapping for `billed_rental_days` (derive from contract start/end/invoice period). Add the filter `contract_status <> 'CANCELLED'` and `days > 0`. Remove the fallback. |
| 1.5 | `credit_memo_amount` / `net_billings` sign convention | ❌ | The constraints say credit memos must be negative and net = gross − credit memos. The mapping computes `gross_billings = SUM(all invoice_amount)`, which already includes credit memos, and then adds credit memos again. The mapping and the PySpark example disagree with each other. `credit_memo_rate = ABS(...)/gross` mixes both conventions. | Define: `gross_billings = SUM(amount WHERE invoice_type <> 'CREDIT_MEMO')`; `credit_memo_amount = SUM(amount WHERE CREDIT_MEMO)` (negative); `net_billings = gross_billings + credit_memo_amount`. Fix the PySpark example to match. |
| 1.6 | `network_level` | ❌ | The source is "derived" from `region` and `branch_code`, with no concrete rule. Silver has no network-level attribute. The Gold DDL has `go_dim_branch.network_level` and `organization_hierarchy_name`, but the mapping never uses them. | Map `network_level` from `gold.go_dim_branch.network_level`. Define how network, region and branch roll-up rows are produced (GROUPING SETS / ROLLUP). |
| 1.7 | `unapplied_cash_percentage` ← `si_cash_receipts.unapplied_payment_amount` | ❌ | `unapplied_payment_amount` is not a column in `silver.si_cash_receipts`. It exists only in the Gold fact (`unapplied_cash_amount`). | Source it from `gold.go_fct_cash_application.unapplied_cash_amount` / `payment_amount`, or derive it from the Silver receipt-to-invoice match (`invoice_id` null or unmatched). |
| 1.8 | `credit_utilization_percentage` ← "derived outstanding AR" | ❌ | The outstanding AR derivation (invoice amount less applied receipts per customer at snapshot) is not specified. It is not tied to `gold.go_fct_credit_risk.outstanding_ar`. | Source from `go_fct_credit_risk` (`outstanding_ar`, `credit_limit`). Document the AR formula. |
| 1.9 | `dso`, `collection_effectiveness_index`, `ar_90_plus_percentage` source layer | ❌ | These metrics are mapped from Silver while Gold facts (`go_fct_ar_aging`, `go_fct_cash_application`) already hold them. The mapping says "derived in staging" but defines no formula. DSO needs Total Credit Sales and Days in Period. CEI needs Beginning AR, Credit Sales, Ending AR and Ending Current AR. | State the exact formulas from the constraints and business requirements. Prefer re-aggregating from the Gold facts with ratio-of-sums. |
| 1.10 | `overall_revenue_to_cash_health_score` | ❌ | The weights, normalization thresholds, and target bands are not defined. The rental_revenue input also has no scale. The four domain scores (Revenue, AR, Cash App, Credit Risk) are not mapped, so the roll-up validation "component scores roll up per weights" cannot be tested. | Add a configurable weight table and per-component normalization formulas. Add the domain scores to the staging output. |
| 1.11 | `collector_name` ← `si_branch_employee.collector_id, employee_name` | ❌ | Collectors are linked to customers and invoices, not to the sales-rep join path. Silver has no customer → collector column, only `branch_employee.collector_id`. The join key to AR and cash rows is not given. | Define the join (customer → collector assignment) via `go_dim_customer.collector_id` / `go_dim_collector`. |
| 1.12 | `contract_status` (Open/Closed) | ❌ | The billing report requires contract status as an attribute, but it is not in the mapping and is not a column of the Gold billing aggregate DDL. | Confirm whether it is a slicer only. If it is, add it to the grain or document that it is served via the fact table. |
| 1.13 | Source layer declaration | ❌ | The mapping lists `silver.*` as sources while the grain table also references `gold.go_fct_*`. The input list excludes the Gold physical model, and the assumption states that the Gold DDL "was not provided". | Add `Databricks_Gold_Model_Physical_1` as a reviewed input. Specify a single lineage path (Silver → Gold facts → aggregates). |

---

## 2. Data Consistency Validation

### ✅ Properly mapped fields ensuring consistency
| Item | Status | Details |
|---|---|---|
| Target column names and order vs Gold DDL | ✅ | Names match the DDL for both aggregates. |
| Decimal handling | ✅ | Currency to 2 decimals, rates to 6 decimals. This aligns with DECIMAL(18,2) and DECIMAL(18,6) in the Gold DDL for `credit_memo_rate`, `ar_90_plus_percentage`, CEI, `unapplied_cash_percentage` and `credit_utilization_percentage`. |
| Distinct counting before joins | ✅ | `invoice_count` and `revenue_per_contract` use distinct counts to avoid fan-out. |
| Date alignment principle | ✅ | The mapping requires a common reporting date before domain joins. |

### ❌ Misaligned or inconsistent mappings
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 2.1 | Precision mismatch | ❌ | The mapping says "round to 4 or 6 decimals as appropriate". DDL: `average_daily_rate`, `revenue_per_contract`, `dso` DECIMAL(18,4); `overall_revenue_to_cash_health_score` DECIMAL(18,4); percentages DECIMAL(18,6). The rule is not pinned per column. | Add a per-column precision table that matches the DDL. |
| 2.2 | Percentage unit | ❌ | Business requirements express AR 90+ %, Unapplied Cash % and Credit Utilization % "× 100". The mapping uses fractions (ratio) and never states the unit. | State whether Gold stores 0–1 or 0–100. Apply it consistently, including in the health-score normalization. |
| 2.3 | Inconsistent `reporting_date` source | ❌ | In billing, `reporting_date` = `invoice_date`. In the executive aggregate it is a conformed date from the invoice date and receipt date. AR and credit risk use `snapshot_date`. The mapping does not say which date is used for each domain. | Define a `go_dim_date` join per domain (revenue → invoice date; cash → receipt date; AR/credit → snapshot date = reporting date). |
| 2.4 | Grain definitions vs physical model | ❌ | The billing grain is `reporting_date, region, branch, sales_rep, equipment_class`. The constraints say uniqueness is Branch, Date, Sales Rep, Equipment Class. The executive grain has `network_level` and `collector_name`, but the constraint is Branch, Date, **Period Type**. | Align the grain with the constraints (see 4.1). |
| 2.5 | Naming of source fields | ❌ | `region` / `employee_name` → `region_name` / `sales_rep_name` are fine, but the `collector_name` mapping lists `collector_id` as a source for a name column. | List `collector_id` as the join key and the descriptive name column as the source. |
| 2.6 | Metadata columns | ❌ | `agg_*_sk`, `load_date`, `update_date` and `source_system` are not mapped in either table. | Add rows: surrogate key generation, `current_timestamp()` for load/update dates, a literal for `source_system`. |

---

## 3. Dimension Attribute Transformations

### ✅ Correct category mappings and hierarchy structures
| Item | Status | Details |
|---|---|---|
| Equipment class normalization (trim, case) | ✅ | Matches the `equipment_class_name` target. |
| Aging bucket derivation rule | ✅ | Based on due date versus the reporting date, in line with the business rule. |
| Hierarchy levels covered | ✅ | Region, branch, sales rep and collector attributes are all represented in the executive grain. |
| Credit memo classification by `invoice_type` | ✅ | Classification dimension is conceptually right. |

### ❌ Incorrect or incomplete transformations
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 3.1 | Hierarchy (Network → Region → Branch → Sales Rep/Collector) | ❌ | The hierarchy is incomplete. There is no rule to generate subtotal rows per level. Mixing sales rep and collector in one grain produces a sparse cross product, since a revenue row has no collector and a cash row has no sales rep. | Split into level-specific rows (ROLLUP/GROUPING SETS) with explicit `'ALL'` / unknown members, or produce two grains. |
| 3.2 | Equipment class mapping | ❌ | Mapped directly from the free-text `equipment_class`. The Gold dimension `go_dim_equipment_class` exists but is not used. | Join `go_dim_equipment_class` on code and map `equipment_class_name`. |
| 3.3 | Unknown-member handling | ❌ | "Governed unknown member only if allowed" is vague. The mandatory-field rule also rejects null keys, which conflicts with it. | Define `'UNKNOWN'` members per dimension and state which ones are allowed. |
| 3.4 | `network_level` values | ❌ | The allowed values are undefined (for example Network / Region / Branch). | Define the domain and add a validation. |
| 3.5 | Period types (day/week/month/quarter) | ❌ | The business requirement needs day, week, month and quarter. The mapping only suggests `date_trunc` in "downstream views", and the Gold DDL has no `period_type` column in either aggregate. | Add `period_type` to the grain (supported by `go_dim_date` and `go_code_period_type`) or document the alternative. |

---

## 4. Data Validation Rules Assessment

### ✅ Deduplication logic and format standardization applied correctly
| Item | Status | Details |
|---|---|---|
| Grain uniqueness check before publish | ✅ | Section 6 requires no duplicate rows at the aggregate grain. |
| Duplicate protection on counts | ✅ | `COUNT(DISTINCT)` and pre-aggregation by domain. |
| Safe division | ✅ | Null on a zero denominator, in line with "rate-based calculations only when denominator non-zero". |
| Reconciliation checks | ✅ | Net vs gross + credit memo, and invoice count vs source population. |
| Health score bounds | ✅ | `LEAST/GREATEST` enforces 0–100. |
| Aging bucket domain | ✅ | Restricted to the approved set (see Gold DDL and constraints). |

### ❌ Issues with validation logic or missing checks
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 4.1 | Executive grain uniqueness | ❌ | The constraint is Branch + Date + Period Type. The mapped grain (adds network_level, region, sales rep, collector) does not guarantee that and allows several health scores per branch and date. | Define one score per branch, date and period type (with rollup rows flagged by `network_level`). |
| 4.2 | Missing validation: credit memo must be negative; standard invoice, payment and credit limit non-negative | ❌ | Section 6 says "negative billing rows reviewed by business rule", which contradicts the constraint. | Add explicit checks and route breaches to `gold.go_error_data`. |
| 4.3 | Missing validation: applied payments must not exceed invoice amount | ❌ | Not in the mapping rules, though it feeds `unapplied_cash_percentage`, DSO and CEI. | Add the check and an error-table route. |
| 4.4 | Missing validation: aging buckets reconcile to Total AR Outstanding | ❌ | Required by the constraints, absent. | Add `SUM(bucket) = total_ar_outstanding`. |
| 4.5 | Missing validation: component domain scores roll up per configured weights | ❌ | Not mapped (see 1.10). | Add a recomputation check. |
| 4.6 | Missing validation: drill-through totals reconcile to `gold.go_fct_rental_revenue` and `gold.go_fct_ar_aging` | ❌ | Only the invoice count is reconciled. | Add reconciliation of revenue and AR totals against the facts. |
| 4.7 | Missing: branch active for the reporting date, and branch must exist in the hierarchy | ❌ | Stated as "valid and active where applicable" and only for one table. | Make the rule mandatory in both aggregates, using `go_dim_branch.branch_status`. |
| 4.8 | Missing: duplicate customer resolution before exposure aggregation | ❌ | Credit utilization sums by customer with no dedup step. | Require a conformed customer (Silver dedup) and check that each `customer_id` maps to one record. |
| 4.9 | Validation location | ❌ | Rejected rows go to an "error table" without naming it. | Name `gold.go_error_data` with `source_table_name`, `target_table_name`, `validation_rule_name`. |
| 4.10 | Format standardization | ❌ | No rule for ID formats or case (`branch_code`, `employee_id`, `customer_id`), and no invoice type casing (`'CREDIT_MEMO'` literal). | Add trim/upper standardization for keys and codes. |

---

## 5. Data Cleansing Review

### ✅ Proper handling of missing values and duplicates
| Item | Status | Details |
|---|---|---|
| `COALESCE` for additive measures | ✅ | Defaults to 0 for sums. |
| Null denominators yield NULL rather than 0 | ✅ | Matches the business rules. |
| Reject null grouping keys | ✅ | Mandatory fields rule covers date, region and branch. |
| Duplicate rows prevented at the aggregate grain | ✅ | Validated before publication. |

### ❌ Inadequate cleansing logic or missing constraints
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 5.1 | Contradictory null handling | ❌ | "Amount must be non-null after defaulting" next to "negative rows reviewed" and "reject null keys / use unknown member". The policy per field is unclear. | Give a table: field → default, reject or unknown, and the error code. |
| 5.2 | Left joins with no orphan handling | ❌ | The PySpark pattern uses left joins to contracts and employees. Invoices with no contract produce NULL region/branch/equipment class, but the constraint requires an invoice to tie to a valid contract. | Route orphan invoices to `go_error_data`. Apply an inner join, or use an explicit `'UNKNOWN'` member. |
| 5.3 | Employee duplicates / versions | ❌ | `si_branch_employee` has `effective_date`, so several rows per employee can exist. A plain join on `employee_id` would duplicate invoices and inflate sums. | Select the latest effective row per employee (window or `QUALIFY`) before joining. |
| 5.4 | Customer dedup missing | ❌ | See 4.8. | Join only to deduplicated customers. |
| 5.5 | Cancelled and zero-duration contracts | ❌ | Not excluded in ADR (see 1.4). | Add the filter. |
| 5.6 | Currency | ❌ | `si_invoices.currency` is never handled, so amounts in different currencies may be summed. | Filter, convert, or assert a single currency. |
| 5.7 | PySpark example flaws | ❌ | `sum(coalesce(...))` and `round`/`sum` rely on shadowed Python built-ins unless imported from `pyspark.sql.functions`. The `executive_cash_df` example groups by `receipt_date, customer_id`, which is not the target grain, and it computes the percentage before aggregating to the target grain. | Import functions as `F`, aggregate to the target grain, then compute ratios on the summed values. |

---

## 6. Compliance with Microsoft Databricks Best Practices

### ✅ Adheres to best practices
| Item | Status | Details |
|---|---|---|
| Delta Lake output | ✅ | Gold outputs are Delta tables. |
| DataFrame API with built-in functions | ✅ | `groupBy`, `agg`, `countDistinct`, `when` are used. |
| Pre-aggregation to avoid many-to-many joins | ✅ | Per-domain staging before the join. |
| Safe division and deterministic grouping keys | ✅ | Reproducible metric logic. |
| `OPTIMIZE`/`ZORDER` suggestion | ✅ | Consistent with the Gold DDL guidance. |

### ❌ Violations of recommended guidelines
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 6.1 | Write pattern | ❌ | No incremental load strategy. There is no `MERGE INTO` on the grain keys or `replaceWhere` partition overwrite. Re-runs could duplicate aggregates. | Specify an idempotent `MERGE` on the grain, or a dynamic partition overwrite on `reporting_date`. |
| 6.2 | Surrogate key generation | ❌ | `agg_*_sk` has no generation method. | Use a deterministic hash (`xxhash64` of the grain columns) or a controlled sequence. |
| 6.3 | Layer lineage | ❌ | The aggregates read Silver tables directly instead of the Gold facts and dimensions. This repeats logic across layers. Databricks medallion guidance expects Gold aggregates to build on Gold facts/dimensions or governed Silver views. | Build aggregates from `go_fct_*` and `go_dim_*`. |
| 6.4 | Metrics documentation | ❌ | The composite score and DSO/CEI formulas are not specified in a form that can be coded and tested. | Provide formulas and test cases. |
| 6.5 | Governance | ❌ | No Unity Catalog three-level names, row-level security, column masking or dynamic views. The business requirements demand branch, region and network-level access. | Add Unity Catalog row filters or dynamic views by branch and region. Do not expose customer PII beyond name to executives. |
| 6.6 | Table properties and clustering | ❌ | Only `ZORDER` is mentioned. Liquid clustering (`CLUSTER BY`), auto-optimize and `delta.enableChangeDataFeed` are not considered. Partitioning by a daily `reporting_date` risks small files. | Use liquid clustering on `reporting_date, branch_name`, or partition by month. |
| 6.7 | Observability | ❌ | No audit logging to `gold.go_process_audit`, no row counts (read/written/rejected), no run id. | Add audit steps. |
| 6.8 | Data quality enforcement | ❌ | No Delta `CHECK` constraints or expectations (for example the health score 0–100) are proposed. | Add Delta constraints or DLT expectations. The physical model deliberately excludes enforced constraints, so use pipeline-level expectations and route failures to `go_error_data`. |

---

## 7. Alignment with Business Requirements

### ✅ Gold Layer aligns with business requirements
| Requirement | Status | Details |
|---|---|---|
| Billing metrics: gross, net, credit memo, invoice count | ✅ | Present in the billing aggregate. |
| ADR, Revenue per Contract, Credit Memo Rate | ✅ (intent) | Formulas follow the business definitions. See 1.4/1.5 for defects. |
| Executive KPIs: score, rental revenue, DSO, AR 90+ %, CEI, unapplied cash % | ✅ | All are mapped. |
| Credit utilization % = outstanding AR / credit limit | ✅ | Matches the business calculation. |
| Hierarchy attributes (region, branch, sales rep, collector) | ✅ | Present in the aggregates. |
| Ratio-of-sums and zero-denominator handling | ✅ | Aligned with the rate-based validation rule. |

### ❌ Missing attributes or incorrect transformations affecting business logic
| # | Item | Status | What is wrong / where | Recommended fix |
|---|---|---|---|---|
| 7.1 | Health score components | ❌ | Missing weights and the four domain scores (Revenue, AR, Cash App, Credit Risk). No normalization or target bands. | See 1.10. |
| 7.2 | Period support (day/week/month/quarter) | ❌ | Not present in the aggregate grain (see 3.5). | Add `period_type`. |
| 7.3 | Missing KPIs from business reports | ❌ | Not covered by either aggregate: Average Days to Pay, % Invoices Paid On Time, Cash Collected, Total AR Outstanding, Best Possible DSO, DSO trend, Customers Over Limit (count and $), Suspended Customers with Open Exposure, AR 90+ $ by Customer. The Gold DDL aggregates do not hold them either, so they are served only by the facts. | Confirm they are served from the facts. State this in the mapping scope. |
| 7.4 | DSO and CEI definitions | ❌ | Not aligned with the stated business formulas (see 1.9). | Document and implement them as given in the requirements. |
| 7.5 | ADR rule | ❌ | Excludes neither zero-duration nor cancelled contracts (see 1.4). | Implement the exclusion. |
| 7.6 | Credit memo sign rule | ❌ | See 1.5. | Fix. |
| 7.7 | Branch active for the selected date | ❌ | Not enforced (see 4.7). | Enforce. |
| 7.8 | Security and executive PII rule | ❌ | Not addressed (see 6.5). | Add. |
| 7.9 | Collector dimension in billing | ❌ | The billing report requires contract status and drill to contract. The aggregate has no contract-level path. | Document that contract drill-through is served by `go_fct_rental_revenue`. |
| 7.10 | Customer dedup before exposure | ❌ | See 4.8. | Enforce. |

---

## 8. API Cost
```
apiCost: 0.000000
```
