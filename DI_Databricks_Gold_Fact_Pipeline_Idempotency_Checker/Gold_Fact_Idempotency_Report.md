_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Idempotency, duplicate-data risk, rerun safety and failure recovery assessment of the Databricks Gold Fact DE Pipeline (Rental Revenue-to-Cash)
## *Version*: 1
## *Updated on*: 
_____________________________________________

**Repository:** DIAscendion/Databricks_LakeHouseInADay (branch `main`). The repository was not specified in the request. I picked it because it is the only repository containing both input paths.
**Inputs reviewed (static review via GitHub MCP):**
- `DI_Databricks_Gold_Fact_DE_Pipeline/Databricks_Gold_Fact_DE_Pipeline_1.py`
- `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt`

**Prior version check:** No existing idempotency report was found in `DI_Databricks_Gold_Fact_Pipeline_Idempotency_Checker`. This is version 1.
**Evidence limitation:** This is static code and model analysis only. No pipeline execution, rerun test or data inspection took place. Silver data content, such as key uniqueness, is not available. Checks that depend on it are marked Warning or Unable to Validate.

## 1. Executive Summary
Overall result: **WARNING (not idempotent as a whole).**

- **Fact tables (4):** Each is written with `mode("overwrite")` and `overwriteSchema=true`. This is a full refresh. Rerunning on unchanged Silver data on the same day does not add duplicate fact rows.
- **Audit and error tables:** These are written with `append`, and every run uses a new `RUN_ID`. Each rerun adds duplicate error rows and new audit rows. The pipeline writes these rows to both Silver and Gold tables.
- **Snapshot facts:** `snapshot_date` is `current_date()`, and the overwrite destroys prior snapshots. AR aging and credit risk results therefore change with the run date, and no history is kept. Reruns on different days are not reproducible.
- **Fan-out risk:** Two joins can multiply monetary measures, which creates duplicate-data risk inside a single run.
  - Collector joins on `branch_code` only.
  - Contract joins assume unique `contract_id`.
- **Failure recovery:** Each Delta overwrite is atomic per table. There is no checkpoint, and a failure stops later facts. Audit logging is not atomic across the two tables.
- **Model drift:** The code and the physical model differ in several ways, which are listed in Section 6.

## 2. Idempotency Validation Report

| # | Check | Status | Evidence / Justification |
|---|---|---|---|
| 1 | Fact load strategy is replace or upsert, not blind append | **Pass** | `write_delta_optimized` uses `mode("overwrite")` for all four facts. Row duplication across reruns does not occur at the fact level. The result is idempotent only for unchanged inputs and the same date (see checks 3 and 4). |
| 2 | Deterministic business keys / MERGE on keys | **Warning** | There is no MERGE and no key-based upsert. Idempotency relies on full-table replacement only. The model's Implementation Notes recommend `MERGE`, but the code does not use it. |
| 3 | Deterministic output on unchanged input | **Fail** | `snapshot_date = current_date()`, and `load_date` and `update_date` use `current_timestamp()`. `df` is evaluated twice (`write`, then `df.count()`), so timestamps can differ within a run. Output differs by run date. |
| 4 | Window-function determinism | **Warning** | `trend_value` uses `lag` over `partitionBy(branch_code).orderBy(reporting_date)`. Several rows per date and branch exist (grain includes contract, rep and customer). Ties make the lag value non-deterministic. |
| 5 | Audit table idempotency | **Fail** | Append only, with a unique `RUN_ID` per run and a null `audit_sk`. Each rerun adds rows. Rows are written to both `silver.si_process_audit` and `gold.go_process_audit`, so the Gold pipeline writes into the Silver layer. |
| 6 | Error table idempotency | **Fail** | `write_error_records` appends the same invalid source rows on every run to both Silver and Gold error tables. There is no dedup key or anti-join. |
| 7 | Table DDL idempotency | **Pass** | All DDL uses `CREATE TABLE IF NOT EXISTS`. |
| 8 | Schema / partition stability across reruns | **Warning** | `overwriteSchema=true` with `saveAsTable` can replace the schema and partitioning declared in the pre-created DDL. Whether partitioning is retained was not confirmed. Unable to Validate without execution. |
| 9 | Re-read consistency (`records_read`, `records_written`) | **Warning** | `base_df.count()` and `df.count()` re-execute the full lineage after the write. If Silver changes mid-run, the audit counts can disagree with what was written. |
| 10 | Execution or test evidence | **Unable to Validate** | No logs, run history or tests were provided. |

## 3. Duplicate Data Risk Analysis

| Area | Risk | Status | Detail |
|---|---|---|---|
| Fact rows across reruns | Low | **Pass** | Overwrite semantics. |
| Rental revenue: invoices inner join contracts on `contract_id` | Medium | **Warning** | If `si_rental_contracts` holds more than one row per `contract_id` (for example versions), invoice amounts are multiplied. Silver key uniqueness is not provable here. |
| AR aging and cash application: join to collectors on `branch_code` only | **High** | **Fail** | `collector_df` has one row per employee with a non-null `collector_id`. Several collectors per branch would duplicate each invoice or receipt row. This inflates `total_ar_outstanding`, `cash_collected` and `payment_amount`. This is also a correctness defect, not only an idempotency defect. |
| Cash application: receipts left join invoices on `invoice_id` | Medium | **Warning** | Duplicate `invoice_id` in invoices would multiply receipts. |
| Credit risk: customer, invoice aggregate and contract aggregate joins | Medium | **Warning** | `F.col("customer_id")` is ambiguous across the joined frames, and the join conditions use `invoice_agg.customer_id`. This may raise an analysis error or join wrongly. The result differs by day because `current_date()` is used. |
| Error table growth | **High** | **Fail** | The same bad records are re-inserted each run, in two layers. The same rule is written once per fact run. |
| Audit table growth | Medium | **Fail** | Two rows are written per fact per run, one in each layer. Counts are not comparable across reruns. |
| Source-level dedup | Unknown | **Unable to Validate** | The pipeline does not dedupe Silver inputs, for example with `dropDuplicates` or a window on business keys. |

## 4. Rerun Safety Assessment

| Scenario | Status | Assessment |
|---|---|---|
| Same-day rerun, unchanged Silver | **Warning** | Fact data is logically the same, except for timestamps. Audit and error tables gain duplicates. |
| Next-day rerun | **Fail** | AR aging and credit risk are rebuilt with a new `snapshot_date` and the previous snapshot is lost. Aging buckets shift. |
| Rerun after partial completion | **Warning** | All four facts are rebuilt. Facts that already loaded are overwritten, which is safe. Audit SUCCESS rows from the earlier attempt remain. |
| Concurrent runs | **Fail** | There is no run lock or guard. Two runs overwrite the same tables, and the order of audit rows is undefined. |
| Backfill / historical reprocessing | **Fail** | `reporting_date` partitions are not selectively replaced (no `replaceWhere`). Every run rewrites the whole table. Prior snapshots cannot be reproduced. |
| Source data reprocessing | **Warning** | There is no watermark or incremental logic. This is simple but expensive, and results depend on whatever Silver holds at run time. |
| Idempotent audit and verification message | **Warning** | `verify_gold_layer_compatibility` prints "passed" for fixed strings without checking anything. It gives false assurance. |

## 5. Failure Recovery Analysis

| Failure point | Status | Behaviour |
|---|---|---|
| Failure in a builder, before the write | **Pass** | The target table is untouched because Delta overwrite is transactional. The failure is audited and the exception is re-raised. |
| Failure in `OPTIMIZE` after the overwrite | **Warning** | The data is already committed but the audit row says FAILED. Audit state and data state disagree. A rerun recovers. |
| Failure during the audit write | **Fail** | The two audit appends are separate writes. A failure after the first leaves Silver and Gold audit tables inconsistent. A failure inside the `except` block replaces the original exception. |
| Failure mid-pipeline | **Warning** | The loop stops at the first failure. Later facts are not attempted and earlier facts are already replaced. The result is a mixed-freshness Gold layer with no cross-table atomicity. |
| Resume / checkpoint | **Fail** | None. Recovery is a full rerun only. |
| Retry / backoff | **Fail** | None. |
| Rollback | **Warning** | Delta time travel (`RESTORE`) could be used manually, but the pipeline does not use it. Prior versions depend on `VACUUM` policy. |
| Error visibility | **Pass** | A failed run records the message and traceback in the audit table. The traceback is stored in an audit text field, so check data-handling policy. |

## 6. Identified Issues and Recommended Fixes

| ID | Severity | Issue | Recommended fix |
|---|---|---|---|
| I-1 | High | Collector join on `branch_code` fans out AR aging and cash application. | Resolve collector by a unique key (customer-to-collector assignment or a single collector per branch). Add an assertion that the right side is unique. |
| I-2 | High | Audit and error tables are append only and duplicated across layers. | Make errors idempotent by MERGE on (`source_table`, `source_record_id`, `validation_rule_name`). Write only to the Gold tables. Add a `run_id` filter or `replaceWhere`. Treat `run_id` as the audit key. Stop writing to Silver tables from the Gold pipeline. |
| I-3 | High | `snapshot_date = current_date()` and overwrite destroy snapshot history. | Accept a `snapshot_date` / `run_date` parameter. Use `replaceWhere snapshot_date = X` (dynamic partition overwrite) or a MERGE keyed on the snapshot grain. |
| I-4 | Medium | There is no MERGE or key-based upsert. | Define business keys for each grain. Use `MERGE INTO`, or `replaceWhere` per `reporting_date`. |
| I-5 | Medium | Non-deterministic timestamps and double evaluation. | Compute `current_timestamp()` once, as a run-level constant. Cache the DataFrame, or take counts from Delta commit metrics. |
| I-6 | Medium | Non-deterministic `lag` on tied ordering. | Compute `trend_value` after aggregating to a unique grain, or add tie-break columns to the `orderBy`. |
| I-7 | Medium | No Silver dedup or key-uniqueness checks. | Add pre-checks that fail or quarantine duplicates of `contract_id`, `invoice_id`, `receipt_id`. |
| I-8 | Medium | `overwriteSchema=true` may change the declared schema and partitioning. | Remove it. Use `insertInto` or `replaceWhere` against the pre-created DDL. |
| I-9 | Medium | Credit risk join uses ambiguous column references. | Alias the frames explicitly and join on the aliased columns. |
| I-10 | Medium | Failure handling: no lock, resume or atomic audit. | Add a run lock or concurrency guard. Add a per-fact skip or resume based on the audit table. Write audit rows in one transaction, or only to Gold. |
| I-11 | Low | The compatibility verification only prints fixed strings. | Implement real checks or remove it. |
| I-12 | Medium | Code and physical model drift. | Align the code with the model (see the list below). |

**Code vs physical model drift (I-12):**
- Target names differ. The code uses `go_data_quality_errors`, but the model defines `go_error_data`.
- Audit and error table schemas differ.
- Surrogate `*_sk` columns are absent from fact writes.
- `branch_name` is absent from the facts.
- `invoice_count` is BIGINT in the code but INT in the model.
- Some DECIMAL scales differ: 18,2 versus 18,4.
- Partitioning differs: `(reporting_date, branch_code)` versus `reporting_date`.
- The aggregate tables `go_agg_*` and the dimensions are not populated by this pipeline.

## 7. Overall Validation Results

| Dimension | Result |
|---|---|
| Idempotency | **Warning** (facts: Pass for duplicates; snapshots, audit and error tables: Fail) |
| Duplicate data risk | **Fail** (High: collector fan-out and error re-append) |
| Rerun safety | **Fail** (next-day, concurrent and backfill scenarios) |
| Failure recovery | **Warning** |
| Execution evidence | **Unable to Validate** |

**Final status: WARNING. Not production-ready as idempotent until I-1, I-2 and I-3 are resolved.**
No source pipeline or model files were modified.

## 8. apiCost
apiCost: 0.000000
