=============================================
Author: AAVA
Created on:
Description: Reviewer report validating the Databricks Gold Fact DE pipeline (PySpark) against the Gold physical data model for Rental Revenue-to-Cash.
Version: 1
Updated on:
=============================================

# Databricks Gold Fact DE Pipeline Review

## 1. Inputs and Assumptions

| Item | Value |
|---|---|
| Repository (selected) | `DIAscendion/Databricks_LakeHouseInADay` (branch `main`). The task did not name the repository, so I searched the owner's repositories and picked this one. It is the only Databricks repository that holds both input paths. |
| Pipeline code | `DI_Databricks_Gold_Fact_DE_Pipeline/Databricks_Gold_Fact_DE_Pipeline_1.py` |
| Target model | `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt` |
| Mapping rules | No separate mapping file was supplied. I used the joins, aggregations and data quality rules in sections 4.3 to 4.5 of the physical model. |
| Unsupported-features knowledge base | Not supplied. I used the "Databricks Spark SQL Limitations" section of the model and general Databricks knowledge. |
| Source metadata | The Silver physical model was not supplied, so Silver column names could not be checked directly. The only evidence is how the code uses them. |
| Output folder | `DI_Databricks_Gold_Fact_DE_Pipeline_Reviewer` did not exist. No earlier `_Review_<n>.md` was found, so this is version 1. |

## 2. Summary

**Overall verdict: ❌ NOT READY FOR PRODUCTION.** The pipeline has several defects that would make runs fail or give wrong results.

Blocking issues:
- `createDataFrame` is called with a `None` value in the first row, so the audit write fails.
- `write_error_records` references columns that do not exist in some input tables.
- The credit risk join uses an ambiguous `customer_id`.
- Days past due that are negative are put in the `90+` AR aging bucket.
- The collector join fans out rows.
- The pipeline's own DDL is thrown away by the `overwrite` plus `overwriteSchema` write.
- Gold support tables do not match the model.

## 3. Validation Checks

### 3.1 Metadata Alignment (Code vs Gold Physical Model)

| # | Check | Result | Finding |
|---|---|---|---|
| 1 | Fact table names (`go_fct_rental_revenue`, `go_fct_ar_aging`, `go_fct_cash_application`, `go_fct_credit_risk`) | ✅ | Names match the model. |
| 2 | Audit table name `go_process_audit` | ✅ | Name matches the model. |
| 3 | Audit table columns | ❌ | The code defines `source_table`, `target_table`, `process_start_timestamp`, `process_end_timestamp`, `processing_status`, `audit_remarks` and `executed_by`. The model defines `pipeline_run_date`, `layer_name`, `source_table_name`, `target_table_name`, `process_status`, `process_start_time`, `process_end_time` and `audit_message`. The `run_id` column is also in the model's ALTER section. `CREATE TABLE IF NOT EXISTS` will not change an existing table, so appends will fail with a schema mismatch. |
| 4 | Error table | ❌ | The code uses `gold.go_data_quality_errors`. The model defines `gold.go_error_data` with different columns (`pipeline_name`, `error_detected_date`, `source_table_name`, `target_table_name`, `validation_rule_description`, `error_status`, `error_record_summary`, `corrective_action`, `source_record_id`). |
| 5 | Surrogate id columns (`fct_*_sk`) | ❌ | The model requires an id field on every Gold table. The fact DataFrames have no `fct_*_sk` column. The audit and error `_sk` columns are always NULL. |
| 6 | `branch_name` column | ❌ | The model has `branch_name` in all four facts. The code never produces it, and no branch dimension is joined. |
| 7 | Dimensions, code tables, aggregates | ❌ | The model defines `go_dim_*`, `go_code_*` and `go_agg_*`. None are built. The code covers facts, audit and error only. If that scope is intended, document it. |
| 8 | Model-only columns (`billed_rental_days`, `unapplied_payment_count`, `risk_category`) | ❌ | Not populated. The model adds them through ALTER statements. |
| 9 | Partitioning | ❌ | The code partitions the revenue and cash application facts by `(reporting_date, branch_code)`. It partitions AR aging by `(snapshot_date, aging_bucket)` and credit risk by `(snapshot_date, branch_code)`. The model partitions each fact by its date column only. |
| 10 | Gold table DDL actually applied | ❌ | `write_delta_optimized` uses `mode("overwrite")` with `overwriteSchema=true`. This replaces the schema and partitioning created by the DDL with those of the DataFrame, so the DDL has no effect. |

### 3.2 Data Type and Column Consistency

| # | Check | Result | Finding |
|---|---|---|---|
| 1 | `invoice_count` and `open_contract_count` types | ❌ | The model uses `INT`. The code uses `BIGINT`. |
| 2 | `average_daily_rate`, `revenue_per_contract`, `trend_value`, `best_possible_dso`, `dso`, `dso_trend`, `average_days_to_pay` precision | ❌ | The model uses `DECIMAL(18,4)`. The code uses `DECIMAL(18,2)`, which loses precision. |
| 3 | String columns | ✅ | The code uses `STRING` where the model uses `VARCHAR(n)`. The model notes that `VARCHAR` is treated as `STRING`. |
| 4 | Monetary amounts `DECIMAL(18,2)`, percentages `DECIMAL(18,6)` | ✅ | These match. |
| 5 | Audit counts as `DECIMAL(18,0)` | ❌ | `log_audit_record` passes Python `int` and `float` values. These are inferred as `bigint` and `double`, which differ from the DDL's decimals. Cast explicitly or supply a schema. |
| 6 | `createDataFrame` type inference | ❌ | The first column is `None` (`audit_sk`) with no schema. Spark cannot infer a type for it and the call raises an error. Supply an explicit `StructType`. |
| 7 | Error DataFrame columns | ✅ | The `select` order matches the code's own error DDL. It does not match the model's error table (see 3.1 check 4). |
| 8 | `equipment_class_name` | ❌ | It is populated from `equipment_class` (the code), not from the equipment class name. A dimension join is needed. |

### 3.3 Databricks Compatibility

| # | Check | Result | Finding |
|---|---|---|---|
| 1 | No PK, FK, unique, identity, TEXT or DATETIME in DDL | ✅ | None are used. |
| 2 | Delta format and `OPTIMIZE ... ZORDER` | ✅ | Both are used. |
| 3 | ZORDER columns must not be partition columns | ❌ | If the DDL's partitions were kept, these would fail: `branch_code` (revenue, cash application, credit risk) and `aging_bucket` (AR aging). Today it only works because of check 3.1.10. Align the partitioning with the model first. |
| 4 | `df.rdd.isEmpty()` | ❌ | RDD APIs are not supported on shared-access clusters and serverless. Use `df.isEmpty()` or `limit(1).count()`. |
| 5 | `datetime.utcnow()` | ❌ | Deprecated in Python 3.12. Use `datetime.now(timezone.utc)`. |
| 6 | `verify_gold_layer_compatibility` | ❌ | It prints "passed" for fixed rule texts and checks nothing. It gives false assurance. Remove it or implement real checks, for example `DESCRIBE DETAIL` and `DESCRIBE TABLE`. |
| 7 | Gold job writing to Silver tables | ❌ | `log_audit_record` and `write_error_records` also append to `silver.si_process_audit` and `silver.si_data_quality_errors`. A Gold job should not write to Silver. This breaks layering and permissions. |
| 8 | Delta overwrite and schema evolution | ❌ | Full overwrite with `overwriteSchema` on every run drops history and allows silent schema drift. The model recommends incremental `MERGE`. |

### 3.4 Join Column Validity

| # | Join | Result | Finding |
|---|---|---|---|
| 1 | invoices to contracts (`contract_id`) | ✅ | Matches the model. The inner join silently drops invoices without a contract and does not send them to the error table. |
| 2 | invoices to customers (`customer_id`) | ✅ | Matches the model. |
| 3 | contracts to sales rep (`sales_rep_id` = `employee_id`) | ✅ | Matches the model. |
| 4 | receipts to invoices (`invoice_id`) and receipts to customers (`customer_id`) | ✅ | Both match the model. |
| 5 | collector join (`c.branch_code` = `cl.branch_code`) in AR aging and cash application | ❌ | This is a many-to-one fan-out by branch. Every invoice and receipt is multiplied by the number of collectors in the branch, which inflates `total_ar_outstanding`, `cash_collected` and counts. Map the collector through the customer or contract, or select one collector per customer. |
| 6 | `prepare_reference_views` collector filter | ❌ | Collectors are chosen with `collector_id IS NOT NULL` and sales reps with `role != 'COLLECTOR'`. This is a guess and not in the model. A NULL `role` is also excluded by the sales rep filter. |
| 7 | Credit risk: customers to `invoice_agg` on `F.col("cm.customer_id") == F.col("customer_id")` | ❌ | The unqualified `customer_id` is ambiguous, because both `cm` and `invoice_agg` carry it. This raises `AMBIGUOUS_REFERENCE`. Use `invoice_agg["customer_id"]`. |
| 8 | Credit risk: `contract_agg` join | ❌ | The condition compares `invoice_agg.branch_code` and `contract_agg.branch_code`. Customers with no invoices have a NULL branch and lose their contract data. The invoice and contract aggregates should be joined on `customer_id` with a deliberate branch rule. |
| 9 | Join of `src["invoices"]` | ✅ | Joins reuse the aliases `i`, `c`, `cm`, `sr`, `cl` and `r` consistently. |

### 3.5 Syntax Correctness

| # | Check | Result | Finding |
|---|---|---|---|
| 1 | Python syntax and imports | ✅ | The file parses and the imports are valid. `tuple[...]` hints need Python 3.9 or later. |
| 2 | SQL DDL syntax | ✅ | The `CREATE TABLE ... USING DELTA PARTITIONED BY` statements are valid. |
| 3 | `write_error_records` column references | ❌ | `F.coalesce(invoice_id, receipt_id, contract_id, customer_id)` is applied to every input table. The customers table has none of `invoice_id`, `receipt_id` or `contract_id`. Receipts have no `contract_id`. This raises `UNRESOLVED_COLUMN`. Pass the key column name as a parameter. |
| 4 | Credit risk join | ❌ | See 3.4 check 7. |
| 5 | `log_audit_record` DataFrame creation | ❌ | See 3.2 check 6. |
| 6 | `write_delta_optimized` with `overwriteSchema` | ❌ | This runs but gives the wrong result (3.1 check 10). |

### 3.6 Transformation Logic Accuracy

| # | Rule | Result | Finding |
|---|---|---|---|
| 1 | Gross billings, credit memo and net billings | ✅ | `net_billings` = gross + credit memo, with the credit memo stored as a negative. `credit_memo_rate` = ABS(credit memo) / gross, with a divide-by-zero guard. |
| 2 | `rental_revenue` | ❌ | It uses the same expression as `gross_billings`, so the two columns are always equal. Define revenue separately from billings (net of credit memos). |
| 3 | `trend_value` | ❌ | `lag` runs over rows per `branch_code`, but the grain is contract by date. The difference is taken against an unrelated contract's row. Aggregate to the branch and date level first, or partition by the full grain without date. |
| 4 | `average_daily_rate` | ❌ | Revenue is divided by `max(contract_duration_days)`. A date-level revenue amount over a full-contract duration is not a daily rate. Use billed rental days. |
| 5 | AR aging buckets | ❌ | The `otherwise` branch labels negative `days_past_due` (invoices not yet due) as `90+`. Add a current or not-due handling, because the model allows only `0-30`, `31-60`, `61-90` and `90+`. Agree how not-yet-due invoices map. |
| 6 | AR outstanding | ❌ | Total outstanding is the sum of all invoice amounts. Receipts and applied cash are not subtracted, and credit memos are not netted. Paid invoices are counted as outstanding. |
| 7 | `dso`, `best_possible_dso`, `collection_effectiveness_index` | ❌ | These are set to NULL. `dso_trend` is therefore always NULL. They are model measures and need real logic. |
| 8 | Credit risk | ❌ | `outstanding_ar` has the same gross-invoice problem as check 6. Customers that fail validation are not removed from the fact. |
| 9 | Cash application | ❌ | `unapplied_cash_amount` is derived from `unapplied_payment_amount`. The `match_status` default of `UNAPPLIED` is reasonable. The model rules "payment exceeds invoice amount" and "gross - credit memo reconciles to net" are not implemented. |
| 10 | Invalid records routed to the error table | ❌ | Invalid rows are written to the error table. They are also filtered out of the facts. Only the null mandatory field rule is implemented. Negative-measure, reconciliation and aging-bucket-domain rules from the model are missing. |
| 11 | `records_read` | ❌ | It is `base_df.count()` after joins, which is not the source row count. It also re-runs the full plan. |
| 12 | Pipeline-level error handling | ✅ | A try/except writes a FAILED audit row and re-raises. This is good. The audit writer itself fails today (3.2 check 6). |

### 3.7 Development Standards (Modularity, Logging, Formatting)

| # | Check | Result | Finding |
|---|---|---|---|
| 1 | Modularity | ✅ | There is one function per fact, plus helpers and a step list in `run_pipeline`. |
| 2 | Header block | ✅ | The header has Author AAVA, with Created on and Updated on blank. |
| 3 | Logging | ❌ | The pipeline uses `print` only. Use the `logging` module with levels and the run id. |
| 4 | Audit duration | ❌ | `PROCESS_START_TS` is global. Every fact's duration is measured from pipeline start. Capture a start time per step. |
| 5 | Audit `source_table` | ❌ | It is the constant `silver_layer`. Record the actual source tables. |
| 6 | Performance | ❌ | Each fact triggers repeated actions: `count()` on `base_df`, `count()` in the error writer, `df.count()` after the write, and the DataFrame is recomputed. Count the written Delta table or use write metrics. Cache or reuse DataFrames. Window functions without partitioning keys are avoided, which is good. |
| 7 | Configuration | ❌ | Schema names and table maps are hard-coded in the file. Move them to parameters or widgets. |
| 8 | Formatting | ❌ | Several lines are very long, for example the aggregation chains. Break them into helper expressions. |

## 4. Recommendations

1. Replace the audit and error DDL and writers with the model's `go_process_audit` and `go_error_data` schemas. Create them with explicit `StructType` schemas, and stop writing to Silver tables.
2. Pass the key column to `write_error_records`, and use `df.isEmpty()`.
3. Fix the credit risk join by qualifying columns through the DataFrame references.
4. Handle negative `days_past_due` explicitly in aging buckets.
5. Remove the collector fan-out by resolving one collector per customer or contract.
6. Compute AR from invoices less applied receipts, and implement `dso`, `best_possible_dso` and `collection_effectiveness_index`.
7. Replace overwrite with `MERGE` or `replaceWhere` on the date partition. Keep the model's schema, partitioning, surrogate keys, `branch_name` and the `INT` and `DECIMAL(18,4)` types.
8. Fix `trend_value`, `average_daily_rate` and `rental_revenue`.
9. Replace `verify_gold_layer_compatibility` with real checks, and add logging and per-step timing.
10. Decide whether dimensions, code tables and aggregates are in scope for this pipeline.

## 5. apiCost

apiCost: 0.31

This is an estimate and not a metered value. I cannot read exact usage from the tools. It assumes about 75,000 input tokens and about 7,000 output tokens at list prices.
