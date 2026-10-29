_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Idempotency, duplicate-data risk, rerun safety and failure recovery assessment of the Databricks Gold aggregated DE pipeline (Rental Revenue to Cash).
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Pipeline Idempotency Checker – Gold Aggregated Pipeline

**Repository used:** `DIAscendion/Databricks_LakeHouseInADay` (branch `main`). The user did not name a repo, so I picked the most plausible candidate. It is the only repo that contains both input paths.
**Inputs read via GitHub MCP:**
- `DI_Databricks_Gold_Aggregated_DE_Pipeline/Databricks_Gold_Aggregated_DE_Pipeline_1.py`
- `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt`

**Prior report check:** `DI_Databricks_Gold_Aggregated_Pipeline_Idempotency_Checker/` did not exist. Report is version 1. The requested filename is `Gold_Aggregated_Idempotency_Report.md`.
**Method:** static review of the code and DDL only. The pipeline was **not executed**. No runtime or test evidence exists, so every finding is a code-based inference.

## 1. Executive Summary
The two aggregate tables are loaded with a full `overwrite` of a deterministically derived DataFrame. That makes the final aggregate content mostly rerun-safe. Several other issues keep the pipeline from being idempotent overall:
- Error records are appended on every run to two tables with no dedup key, so reruns duplicate them.
- The audit write targets the wrong table and its failures are swallowed.
- The AR 90+ metric depends on `current_timestamp()`, so results change with the run date.
- The invalid-executive-row error path looks likely to fail at runtime.
- The two table loads are not atomic.
- Silver is not snapshot-pinned and has no duplicate guard.

**Overall: WARNING, leaning FAIL for the error and audit handling.**

## 2. Idempotency Validation Report

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Final-table load is replace-style, not append | Pass | `load_gold_table` uses `mode("overwrite")` with `saveAsTable`. Two runs over the same Silver data leave the same row set. Delta atomicity is a platform property that I did not test. |
| 2 | Deterministic business keys and output | Warning | `build_executive_health` uses `datediff(current_timestamp(), due_date) > 90`. `ar_90_plus_percentage` and the health score therefore change for the same `reporting_date` depending on run day. |
| 3 | Run-specific columns | Warning | `load_date`, `update_date` and `run_id` (a new `uuid4` per run) change on every run. Data content is stable but row metadata is not byte-identical. |
| 4 | Gold error tables are idempotent | Fail | `write_error_records` uses `mode("append")` into `gold.go_data_quality_errors` and `silver.si_data_quality_errors`. `error_sk` is null, `detected_timestamp` is `current_timestamp()`, and there is no MERGE or dedupe key. |
| 5 | Audit log is idempotent and correct | Fail | `write_audit_log` appends to `SILVER_AUDIT` and never writes `GOLD_AUDIT`. `audit_sk` is always None. A bare `except: pass` hides failures. It passes `current_timestamp()` Column objects inside `createDataFrame` rows, which I expect to fail and be silently swallowed, and the duration is a placeholder `0.0`. Audit rows are unreliable as evidence of a run. |
| 6 | Source determinism / snapshot isolation | Warning | Silver tables are read at "latest" with no Delta version or timestamp pinning. Each action (`count()`, then the write) re-evaluates the plan. Silver changes mid-run could make the counts differ from the written data. |
| 7 | Grain uniqueness enforced | Warning | Aggregation `groupBy` is on the model grain, so the aggregate output is unique per grain unless the grouping keys contain nulls. The billing aggregate keeps null region and branch (left joins). The executive aggregate drops them. The Delta model has no unique constraints, so uniqueness is not enforced. |
| 8 | Schema / partition stability on rerun | Warning | `overwriteSchema=true` with `saveAsTable` overwrite. The tables are created with `PARTITIONED BY (reporting_date)`, but the write specifies no `partitionBy`. I cannot confirm whether partitioning is preserved (Unable to Validate without execution). Silent schema drift is possible. |
| 9 | Execution / testing performed | Unable to Validate | No run logs, test results or Delta history were provided. |

## 3. Duplicate Data Risk Analysis

| Risk | Level | Detail |
|---|---|---|
| Aggregate tables | Low | They are fully replaced each run, so there is no accumulation. |
| Error tables | **High** | Each rerun re-appends the same invalid invoices. Rows are written twice per run (Gold and Silver) with no key. A retry after a mid-run failure also duplicates them. |
| Audit table | Medium | The table is append-only, which is expected for audit. `run_id` exists but it is not guaranteed unique per attempt because it is created at module import. Audit rows land in Silver, not Gold. |
| Silver duplicate inputs | Medium | There is no dedup on `invoice_id` or `receipt_id` before `sum()`. `invoice_count` uses `countDistinct`, but amounts are summed without distinct. Duplicate Silver rows would inflate money measures and make `invoice_count` inconsistent with them. |
| Join fan-out | Low-Medium | `cash_receipts` is joined to invoices, then contracts, then employees. Duplicate `employee_id` or `contract_id` in Silver would multiply rows. `si_branch_employee` is joined by `employee_id` only. Uniqueness is not checked. |
| Null-key left joins in executive health | Medium | Joins on region, branch and rep never match when a key is null. Cash and credit measures are silently null. This is deterministic but makes the metrics wrong. |
| Credit limit | Medium (correctness) | `credit_limit` is summed per invoice row, so a customer's limit is counted once per invoice. This overstates the limit and understates utilization. |

## 4. Rerun Safety Assessment
- **Rerun after success on unchanged Silver (same day):** aggregate content is the same and the audit is unreliable. Error tables get duplicated.
- **Rerun on a later day:** the 90+ metrics and health scores change even with no source change (check 2).
- **Concurrent runs:** there is no lock, and Delta write conflicts are not handled. A concurrent overwrite could fail or interleave. Unable to Validate.
- **Backfill or partial reprocess:** there is no date-parameter or partition-scoped `replaceWhere`. Every run recomputes and replaces the whole history, so there is no incremental mode and cost grows over time.
- **Model alignment:** the model's `go_agg_*` tables have no `run_id`, and the pipeline adds one. Types also differ: the model has DECIMAL(18,4) for `average_daily_rate` and `dso`, the code uses (18,6). `invoice_count` is INT in the model and BIGINT in the code. The model's error and audit tables are `go_error_data` and `go_process_audit`, with different columns. The pipeline writes to `go_data_quality_errors` and a differently shaped `go_process_audit`. `create_gold_support_tables()` uses `IF NOT EXISTS`, so an existing model-created table would not match and the audit and error writes may fail.

## 5. Failure Recovery Analysis

| Scenario | Outcome | Status |
|---|---|---|
| Failure during billing build or load | The old aggregate stays intact because the Delta overwrite is atomic per table. Rerun is safe. | Pass |
| Failure after billing overwrite, before executive overwrite | The two tables are inconsistent (new billing, old executive). A rerun fixes it, but consumers may read mixed states. There is no cross-table transaction. | Warning |
| Failure after `write_error_records` | The error rows persist, and a rerun appends them again. | Fail |
| Invalid executive rows | `write_error_records` coalesces `invoice_id`, `contract_id` and `customer_id`, but `executive_df` has none of those columns. `to_json(named_struct(*))` is also not valid Spark SQL (`struct(*)` is the normal form). The step is likely to raise an AnalysisException, failing the whole run. Not executed, so this is a code-based inference. | Fail (likely) |
| `OPTIMIZE` failure | Swallowed. This is non-critical, but nothing is logged. | Warning |
| Failure logging | The FAILED audit write is likely to be lost (check 5), so failures leave no audit trail. The exception is re-raised, so the job still fails visibly. | Warning |
| Checkpoint | `CHECKPOINT_BASE` is declared but never used. There is no restart state. Restart is a full rerun only. | Warning |

`upper_safe` builds SQL from `c._jc.toString()`. This depends on the JVM Column internals and breaks on Spark Connect and shared clusters. It is a recoverability and portability risk.

## 6. Identified Issues and Recommended Fixes

| ID | Severity | Issue | Recommended fix |
|---|---|---|---|
| 1 | High | Error tables are append-only and duplicate on rerun. | Replace with `MERGE` on a deterministic key (`source_table`, `source_record_id`, `validation_rule_name`, `run_scope/reporting_date`). Alternatively delete the current-scope errors before reinserting. Write only to the Gold error table, or document why Silver is also written. |
| 2 | High | The executive-invalid error path references missing columns and uses invalid `named_struct(*)`. | Build a key from `reporting_date, region, branch, sales_rep`. Use `to_json(struct(*))`. Make `source_record_id` column-safe. |
| 3 | High | The audit target is Silver, `audit_sk` is null, and failures are swallowed. | Write to `GOLD_AUDIT` with the model's columns. Use `current_timestamp()` via a SQL insert or a Python datetime. Compute the real duration. Log audit failures instead of `pass`. Add `run_id` to the model or the table. |
| 4 | Medium | The 90+ ageing uses `current_timestamp()`. | Use an explicit `as_of_date` parameter, defaulting to the run date, and store it in the output. Make reruns for a given date reproducible. |
| 5 | Medium | The two loads are not atomic. | Order writes and record per-table status. Optionally use staging tables plus a swap, or a Delta version check. Add a consistency flag in the audit. |
| 6 | Medium | No Silver dedup or snapshot pinning. | Dedup on business keys (`row_number` over `invoice_id`). Read Silver `VERSION AS OF` and record the versions in the audit. Cache or persist DataFrames before counting. |
| 7 | Medium | No partition-aware overwrite. | Use `replaceWhere` on `reporting_date`, or dynamic partition overwrite, and keep `partitionBy("reporting_date")` explicit. Drop `overwriteSchema` in production. |
| 8 | Medium | Model and code drift. | Align types, the `run_id` column, and the audit and error table names and columns with `Databricks_Gold_Model_Physical_1.txt`. |
| 9 | Low | Credit limit summed per invoice, and null-key joins drop measures. | Aggregate the credit limit per customer first. Use null-safe joins (`eqNullSafe`) or default keys. |
| 10 | Low | Concurrency and unused checkpoint. | Add a run lock or an idempotency token check on `run_id`. Remove the unused constant. |
| 11 | Low | Fragile `upper_safe`. | Replace with `upper(trim(col(...)))`. |

## 7. Overall Validation Results

| Area | Result |
|---|---|
| Aggregate load idempotency | Pass (with Warnings for time-dependence) |
| Duplicate-data risk | Fail (error tables), Warning (Silver duplicates) |
| Rerun safety | Warning |
| Failure recovery | Warning, with Fail on the error-table and executive-invalid paths |
| Execution / testing evidence | Unable to Validate |

**Final verdict: WARNING (not production-idempotent until issues 1–3 are fixed).**

## 8. apiCost
apiCost: 0.000000
