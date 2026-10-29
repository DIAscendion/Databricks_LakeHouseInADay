_____________________________________________
**Author**: AAVA
**Created on**:
**Updated on**:
**Description**: Reviewer report for the Databricks Gold aggregated DE pipeline (Rental Revenue-to-Cash) validated against the Gold physical model.
**Version**: 1
_____________________________________________

# Databricks Gold Aggregated DE Pipeline Review

## 1. Inputs Reviewed
| Item | Path (repo `DIAscendion/Databricks_LakeHouseInADay`, branch `main`) |
|---|---|
| PySpark pipeline | `DI_Databricks_Gold_Aggregated_DE_Pipeline/Databricks_Gold_Aggregated_DE_Pipeline_1.py` |
| Target model | `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt` |

Notes: The repository was not named in the request, so I picked `Databricks_LakeHouseInADay`. Both input files exist there. No separate mapping-rules file or unsupported-features knowledge base was supplied. I used the model's "Databricks Spark SQL Limitations" section and general Databricks rules instead. The output folder did not exist, so this is version 1.

## 2. Summary
| Area | Result |
|---|---|
| Metadata alignment | ❌ |
| Data type / column consistency | ❌ |
| Databricks compatibility | ❌ |
| Join validity | ❌ |
| Syntax / runtime correctness | ❌ |
| Development standards | ❌ |
| Transformation logic | ❌ |

**Overall: NOT READY.** The aggregates run, but there are several blocking defects. The audit log and error handling will not work. Net billings is calculated wrongly. DSO and credit utilization are wrong. Z-ORDER on partition columns fails and the error is swallowed.

## 3. Metadata Alignment
| # | Check | Status | Finding / Recommendation |
|---|---|---|---|
| 1 | Source tables match the model (si_invoices, si_rental_contracts, si_cash_receipts, si_customer_master, si_branch_employee) | ✅ | All five are used. |
| 2 | Target aggregate table names | ✅ | `gold.go_agg_billing_performance` and `gold.go_agg_executive_health_score` match the model. |
| 3 | Error table name | ❌ | The code uses `gold.go_data_quality_errors`. The model defines `gold.go_error_data`. Rename it or align the model. |
| 4 | Error table schema | ❌ | The code uses source_table, source_record_id, error_description, error_record_payload and similar. The model uses pipeline_name, error_detected_date, source_table_name, target_table_name, validation_rule_description, error_status, error_record_summary, corrective_action and others. Align to the model DDL. |
| 5 | Audit table schema | ❌ | The code uses process_start_timestamp, processing_status, audit_remarks and others. The model uses pipeline_run_date, layer_name, process_status, process_start_time, process_end_time, audit_message and others. Align to the model DDL. |
| 6 | Audit target | ❌ | `write_audit_log` writes only to `SILVER_AUDIT`. `GOLD_AUDIT` is created but never written. Write to `gold.go_process_audit`. |
| 7 | Surrogate id columns (`agg_billing_performance_sk`, `agg_executive_health_score_sk`) | ❌ | The model requires them on every Gold table. The aggregate DDLs and DataFrames omit them. Add them, for example with `xxhash64` or `monotonically_increasing_id`. |
| 8 | Metadata columns load_date, update_date, source_system | ✅ | Present. `run_id` is an extra lineage column not in the model. Add it to the model or drop it. |

## 4. Data Type and Column Consistency
| # | Column | Pipeline | Model | Status |
|---|---|---|---|---|
| 1 | billing.average_daily_rate | DECIMAL(18,6) | DECIMAL(18,4) | ❌ |
| 2 | billing.revenue_per_contract | DECIMAL(18,6) | DECIMAL(18,4) | ❌ |
| 3 | billing.invoice_count | BIGINT | INT | ❌ |
| 4 | exec.overall_revenue_to_cash_health_score | DECIMAL(18,6) | DECIMAL(18,4) | ❌ |
| 5 | exec.dso | DECIMAL(18,6) | DECIMAL(18,4) | ❌ |
| 6 | Other amount and percentage columns | DECIMAL(18,2) / (18,6) | Same | ✅ |
| 7 | STRING vs VARCHAR | STRING | VARCHAR(n) | ✅ Acceptable on Databricks (model assumption 8). |
| 8 | Audit counts | DECIMAL(18,0) in DDL, written as Python int | DECIMAL(18,0) | ✅ |
| 9 | Audit `processing_duration_seconds` | Hard-coded 0.0 | Real duration | ❌ Compute `(end - start).total_seconds()`. |
| 10 | Cast to model types before write | Missing | Required | ❌ Cast every output column to the model type. `load_gold_table` uses `overwriteSchema=true`, which silently adopts the DataFrame types. |

## 5. Databricks Compatibility
| # | Check | Status | Finding / Recommendation |
|---|---|---|---|
| 1 | Delta format, `CREATE TABLE IF NOT EXISTS ... USING DELTA` | ✅ | |
| 2 | No PK/FK/unique/identity/indexes | ✅ | |
| 3 | `OPTIMIZE ... ZORDER BY (reporting_date, ...)` | ❌ | `reporting_date` is the partition column. Delta cannot Z-ORDER by a partition column, so the statement fails. `optimize_table` catches the error with `except: pass`, so no Z-ORDER runs. Remove `reporting_date` from the Z-ORDER list. |
| 3a | Redundant `OPTIMIZE` run twice | ❌ | `OPTIMIZE` runs once plain and once with Z-ORDER. Run only the Z-ORDER version. |
| 4 | `mode("overwrite")` + `overwriteSchema=true` on `saveAsTable` | ❌ | A full overwrite with schema replacement can drop the DDL-declared partitioning and column types. The pipeline recreates the tables on every run. Use `replaceWhere` or `MERGE`, or a plain overwrite without `overwriteSchema`. |
| 5 | `to_json(named_struct(*))` | ❌ | `named_struct(*)` is not valid Spark SQL. Use `to_json(struct(*))`. |
| 6 | `c._jc.toString()` in `upper_safe` | ❌ | Uses the private JVM handle. It breaks on Spark Connect and serverless compute and is not a robust column-name source. Use `F.upper(F.trim(c))`. |
| 7 | `spark.createDataFrame` with `current_timestamp()` Column objects and an all-`None` column | ❌ | Python rows cannot hold Column objects, and a column of only `None` cannot be type-inferred. Supply an explicit schema and Python values. The exception is swallowed. |
| 8 | `CHECKPOINT_BASE = /tmp/...` | ❌ | Defined but unused. `/tmp` is not recommended on Databricks. Remove it. |
| 9 | `datediff(current_timestamp(), due_date)` | ❌ | Non-deterministic across runs. Use a run-level `as_of_date` parameter. |

## 6. Join Column Validity
| # | Join | Status | Finding / Recommendation |
|---|---|---|---|
| 1 | invoices → contracts on contract_id | ✅ | Matches the model. |
| 2 | invoices → customers on customer_id | ✅ | |
| 3 | cash_receipts → invoices on invoice_id | ✅ | |
| 4 | contracts → employees on sales_rep_id = employee_id | ❌ | The model also joins on branch_code. Without it, an employee with several branch rows duplicates invoices and inflates every SUM. Add branch_code, or deduplicate the employee table first. |
| 5 | cash_receipts → customers on customer_id | ❌ | Listed in the model but not implemented. |
| 6 | Executive joins revenue → cash → credit on region, branch and sales rep | ❌ | Equality joins on nullable columns drop matches when any key is NULL. Use `eqNullSafe` or fill defaults. A branch-level `network_level` is also joined with sales_rep_name. |
| 7 | Column case normalisation | ❌ | `contracts.sales_rep_id` and `employee_id` are lower-cased and trimmed, but `invoices.contract_id` and `contracts.contract_id` are not normalised. Apply the same treatment to every key. |
| 8 | branch_name sourced from `c.branch_code` | ❌ | The model has a separate `branch_name`. Join the branch dimension, or document the mapping. |

## 7. Syntax and Runtime Correctness
| # | Check | Status | Finding / Recommendation |
|---|---|---|---|
| 1 | `upper_safe` is defined after `extract_silver_sources` | ✅ | It resolves at call time. Move it into the utilities section for readability. |
| 2 | `write_error_records` on `invalid_exec_df` | ❌ | The executive DataFrame has no invoice_id, contract_id or customer_id, so `col("invoice_id")` raises AnalysisException. This breaks any run that has invalid executive rows. Select the id columns conditionally. |
| 3 | `write_error_records` on `invalid_billing_df` | ✅ | The columns exist. |
| 4 | `round` shadows the Python built-in | ❌ | Import as `spark_round` or use `F.round`. |
| 5 | Unused imports (`lower`, `DeltaTable`, `to_date` is used) | ❌ | Remove `DeltaTable` and any other unused imports. |
| 6 | `write_audit_log` swallows all exceptions | ❌ | Any failure here is invisible, and per item 7 above the audit write always fails. Log the failure and surface it. |
| 7 | Audit and error row counts | ❌ | `records_rejected` is always 0, even though invalid rows are routed to the error table. Count the rejected rows. |
| 8 | `.count()` called repeatedly | ❌ | Counts are recomputed on every source and on both outputs, so the lineage runs several times. Cache the DataFrames or reuse counts from the write metrics. |

## 8. Development Standards
| # | Check | Status | Finding / Recommendation |
|---|---|---|---|
| 1 | Modularity (extract / transform / load / audit functions) | ✅ | |
| 2 | Header and metadata block | ✅ | |
| 3 | Logging | ❌ | Uses `print` only. Use the `logging` module with levels. |
| 4 | Error handling | ❌ | The main try/except re-raises, which is good. The `except: pass` blocks in audit and optimize are not acceptable. |
| 5 | Configuration externalised | ❌ | Table names are hard-coded. Use widgets or job parameters. |
| 6 | Formatting / readability | ✅ | Consistent formatting. |
| 7 | Idempotency and incremental loading | ❌ | Full overwrite on every run. Add a reporting-date window. |
| 8 | Data-quality rules from the model (payment > invoice, negative measures, net-billings reconciliation, aging buckets) | ❌ | Only mandatory-field checks exist. Add the other rules. |

## 9. Transformation Logic Accuracy
| # | Check | Status | Finding / Recommendation |
|---|---|---|---|
| 1 | `gross_billings` | ❌ | Currently the sum of all invoice amounts, including credit memos. Gross should be the non-credit-memo billings. |
| 2 | `net_billings = gross + credit_memo_amount` | ❌ | Credit memos are already inside gross, so they are counted twice if they are negative. Per the model, net = gross billings minus credit memo effect. Fix both formulas together and state the sign convention. |
| 3 | `rental_revenue` | ✅ | Non-credit-memo sum. This is consistent but should be reconciled with the corrected gross. |
| 4 | `average_daily_rate` | ❌ | The average is taken over invoice rows after joining, so it is weighted by invoice count and contains zeros where daily_rate is NULL. Average over distinct contracts and ignore NULLs. |
| 5 | `revenue_per_contract`, `credit_memo_rate` | ✅ | Use safe division. `credit_memo_rate` depends on correct gross. |
| 6 | Executive `dso` | ❌ | Computed as total AR divided by invoice count, which is an average invoice amount and not days. Use (open AR / revenue) × days in period. |
| 7 | `ar_90_plus_amount` and `total_ar_amount` | ❌ | Based on every invoice regardless of payment, so it ignores cash received. Use open balance (invoice minus applied payments) and exclude credit memos from the 90+ bucket as the business rules require. |
| 8 | Executive `unapplied_cash_percentage`, `collection_effectiveness_index` | ❌ | The cash amount is on the receipt date, but AR is on the invoice date. The two are joined on the same reporting_date and so rarely match the same period. Define the grain explicitly. |
| 9 | `credit_utilization_percentage` | ❌ | Sums `credit_limit` once per invoice row, which multiplies the limit by the number of invoices. Deduplicate by customer before summing. |
| 10 | `collector_name` | ❌ | Filled with the sales rep name. `collector_id` is loaded from employees but never used. Join on collector_id. |
| 11 | `network_level` | ❌ | Always the literal `branch`. The model expects network, region, branch, sales rep and collector levels. Produce the rollup levels (for example with `grouping sets`). |
| 12 | Health score weights (25/20/15/20/20) and 0–100 bound | ✅ | Clamped with least/greatest. The weights are not documented in the model, so confirm with the business. |
| 13 | Executive null-grain filter | ❌ | Rows with a NULL region or branch are dropped and then written to the error table, which fails (see item 2 in section 7). Left joins to missing employees produce those rows. |

## 10. Recommendations (priority order)
1. Fix `write_audit_log`. Use an explicit schema and real timestamps, write to `gold.go_process_audit` with the model columns, and stop swallowing errors.
2. Fix `write_error_records`. Use `to_json(struct(*))`, handle missing id columns, and align to the `gold.go_error_data` schema.
3. Correct the billing logic for gross, net and average daily rate (items 1, 2 and 4 in section 9).
4. Correct DSO, 90+ AR, credit utilization, collector and rollup levels for the executive aggregate.
5. Remove partition columns from the Z-ORDER lists and run `OPTIMIZE` once.
6. Add `*_sk` columns, cast every output column to the model types, and stop using `overwriteSchema`.
7. Add the branch_code join and deduplicate employees to prevent fan-out. Use null-safe equality in the executive joins.
8. Replace `_jc` usage and the `round` shadowing, add logging, parameterise table names, and add the model's data-quality rules.

## 11. apiCost
apiCost: 0.0 (not measurable. This environment does not report token usage or pricing for the call, so I have not estimated a figure.)

## 12. Output
Output file: `DI_Databricks_Gold_Aggregated_DE_Pipeline_Reviewer/Databricks_Gold_Aggregated_DE_Pipeline_Review_1.md`
