_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Idempotency, duplicate-data risk, rerun safety and failure recovery validation of the Databricks Bronze DE Pipeline (Rental Revenue to Cash Reports).
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Pipeline Idempotency Checker – Rental Revenue to Cash (Bronze)

**Inputs analyzed (repo `DIAscendion/Databricks_LakeHouseInADay`, branch `main`):**
- `DI_Databricks_Bronze_DE_Pipeline/Databricks_Bronze_DE_Pipeline_1.py`
- `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md`

**Method:** Static code and design review only. I did not run the pipeline, run tests, or connect to a Databricks workspace. Every status below is based on the source code and the physical model document. Runtime behaviour that I could not confirm from those files is marked **Unable to Validate**.

---

## 1. Executive Summary

The pipeline reads 5 CSV source folders and runs them in order. For each table it adds metadata columns, keeps only the columns that also exist in the target table, and writes with `mode("overwrite")` plus `option("overwriteSchema","true")`. It then appends one row per table to `bz_audit_log`.

- **Row duplication on rerun:** Low risk. Each run fully replaces each table, so rerunning on the same source files does not add duplicate rows. This holds only when the source folder content is unchanged between runs.
- **Strict idempotency (same input → identical table state):** Not met. `load_date` and `update_date` use `current_timestamp()` and change on every run. The audit log is append-only and grows on every run.
- **Rerun safety:** At risk. `inferSchema=false` reads every CSV column as STRING, and `overwriteSchema=true` then replaces the typed DDL. For example, `daily_rate DECIMAL(10,2)` becomes STRING after the first run. `align_to_target_table` drops target columns that are missing from the source. Together with `overwriteSchema`, a single bad file can permanently remove columns from the table. Later runs align to the narrowed schema, so the loss cannot fix itself.
- **Failure recovery:** Partial. Each Delta overwrite is atomic per table. The run is sequential and stops at the first failure, so tables earlier in the order are refreshed and later ones are stale. There is no run ID, checkpoint, or cross-table consistency marker.
- **Model alignment:** Several mismatches with the physical model:
  - Metadata column names: `load_date`/`update_date` in the code vs `load_timestamp`/`update_timestamp` in the model.
  - Audit table schema differs.
  - Catalog: `sunbelt_demo.bronze` in the code vs `bronze` in the model.
  - Lineage columns `file_path` and `file_modification_time` are always NULL.

**Overall verdict: FAIL (conditionally rerunnable).** Reruns do not duplicate rows, but schema drift and data-loss risks make repeated runs unsafe.

---

## 2. Idempotency Validation Report

| # | Check | Status | Evidence / Justification |
|---|---|---|---|
| I1 | Write mode prevents row accumulation across reruns | **Pass** | `write_to_bronze` uses `.mode("overwrite").saveAsTable(target_table)`. A rerun replaces the table contents instead of appending to them. |
| I2 | Deterministic output for identical input | **Fail** | `enrich_with_metadata` sets `load_date` and `update_date` to `current_timestamp()`. Every rerun produces different values, so the output is not byte- or value-identical. `load_date` also loses the original load time on every run. |
| I3 | Input set is deterministic / bounded per run | **Warning** | `read_source` loads the whole folder (`/mnt/raw/rental_revenue_to_cash/<source>`). There is no file list, partition, watermark, or `run_date` parameter. Results depend on whatever files are in the folder when the job runs. |
| I4 | Schema stability across reruns | **Fail** | `inferSchema=false` turns all CSV columns into STRING. `overwriteSchema=true` replaces the DDL types (DECIMAL → STRING) on the first run. `align_to_target_table` keeps only the target columns that exist in the source. If a column is missing, the overwrite drops it from the table. The next run reads `spark.table(target).columns` from the narrowed table, so the column cannot come back. |
| I5 | Global session config side effects | **Warning** | `spark.databricks.delta.schema.autoMerge.enabled=true` is set session-wide. This is not needed for overwrite, and it hides schema drift from any other writes in the same session. |
| I6 | DDL creation idempotent | **Pass** | All DDL statements use `CREATE TABLE IF NOT EXISTS`, so reruns are no-ops. Note: after the first overwrite, the table no longer matches this DDL (see I4). |
| I7 | Audit logging idempotent | **Warning** | The audit table is `mode("append")` with `uuid4` IDs, so every rerun adds rows. This is acceptable for an event log. However, there is no `run_id` or batch key to link or deduplicate the attempts from one logical run. |
| I8 | Alignment with physical model | **Fail** | <ul><li>The code uses `load_date`/`update_date`; the model specifies `load_timestamp`/`update_timestamp`.</li><li>The code's audit schema (`audit_id`, `pipeline_name`, …) differs from the model (`record_id`, `source_table`, `load_timestamp`, `processing_time`, `status`).</li><li>The code writes to `sunbelt_demo.bronze.*`; the model specifies `bronze.*`.</li></ul> |
| I9 | Verified by execution | **Unable to Validate** | I found no run logs, test results, or audit records in the repository. |

---

## 3. Duplicate Data Risk Analysis

| # | Scenario | Risk | Status | Evidence |
|---|---|---|---|---|
| D1 | Rerun with the same source files | Low | **Pass** | Full overwrite, so rows are not duplicated across runs. |
| D2 | Source folder keeps old and new extract files | High | **Warning** | The whole folder is read on every run. If extracts pile up (for example, daily full snapshots), each run loads every file at once. The same `contract_id`, `invoice_id`, or `receipt_id` then appears once per file. There is no `_metadata.file_path` or file-date column to tell the copies apart (see D4). |
| D3 | Duplicates inside the source | Accepted by design | **Pass** | The model (§4) says duplicates are intentionally kept in Bronze. No deduplication is expected in Bronze. |
| D4 | Lineage to trace or deduplicate downstream | High | **Fail** | `file_path` and `file_modification_time` are filled with `lit(None)` unless the CSV happens to contain those columns. The `_metadata` column is not used. Silver therefore cannot deduplicate or attribute rows by source file. |
| D5 | Concurrent runs | Medium | **Warning** | There is no locking or job-concurrency guard in the code. Two concurrent overwrites will either cause a Delta conflict or let the last writer win. Neither creates duplicate rows, but the audit log will show two SUCCESS rows. Whether the job's max-concurrent-runs is set to 1 is **Unable to Validate**, because no job definition was provided. |
| D6 | Duplicate audit entries | Low | **Warning** | Retries and reruns add rows with no `run_id`, so operators cannot tell retry attempts from separate logical runs. |

---

## 4. Rerun Safety Assessment

| # | Check | Status | Evidence / Justification |
|---|---|---|---|
| R1 | Safe to rerun the whole pipeline after success | **Warning** | No duplicates are created, but `load_date` is reset and the schema may drift (I4). |
| R2 | Safe to rerun after a source purge or archive | **Fail** | If the raw folder is archived or emptied after a load, a rerun does one of two things: <ul><li>If the path is empty or missing, the CSV read throws an error and the existing table is kept (safe).</li><li>If the files have headers but no data rows, a 0-row DataFrame overwrites the table and wipes Bronze.</li></ul> There is no minimum row-count or empty-input guard. |
| R3 | Partial or selective rerun | **Fail** | `run_pipeline` always processes all 5 sources. There is no parameter to rerun one table, so recovery reprocesses tables that already succeeded. |
| R4 | Type safety on rerun | **Fail** | All columns are read as STRING and written with `overwriteSchema`. The DECIMAL columns from the model (`daily_rate`, `invoice_amount`, `tax_amount`, `payment_amount`, `credit_limit`) become STRING after the first run. There is no explicit schema or cast. |
| R5 | Row count reported accurately | **Warning** | `write_to_bronze` calls `df.count()` after the write. This reads the source a second time, so if files change between the write and the count, the audit `row_count` will not match what was written. |
| R6 | Rollback capability | **Warning** | Delta time travel or `RESTORE` is available in the platform, but the pipeline does not record the table version before or after each write. There is also no documented rollback procedure. |

---

## 5. Failure Recovery Analysis

| # | Failure Point | Behaviour | Status | Notes |
|---|---|---|---|---|
| F1 | Failure in the middle of one table's write | The Delta overwrite is atomic and the previous version stays intact. | **Pass** | Per-table atomicity comes from the Delta transaction log, applied to the single `saveAsTable` call. I have not confirmed this at runtime (**Unable to Validate**). |
| F2 | Failure at table *n* of 5 | `raise` stops the loop. Tables 1..n-1 are refreshed and n..5 are stale. | **Warning** | This leaves the Bronze tables inconsistent with each other (for example, new invoices with old cash receipts). There is no run-level status or "all tables complete" marker. |
| F3 | Audit write fails inside the `except` block | The audit exception replaces the original exception. | **Warning** | `write_audit_log` in `except` is not wrapped in its own try/except. The root cause can be lost. |
| F4 | Audit write fails after a successful data write | The data is committed but no SUCCESS row is recorded, and the exception propagates. | **Warning** | Data and audit are out of sync. On rerun the table is overwritten again, which is safe but leaves an untracked load. |
| F5 | Failure before `create_required_tables` or the user lookup | No tables are touched. | **Pass** | `get_current_user` falls back to `"unknown_user"`. |
| F6 | Restartability (checkpoint/watermark) | None | **Warning** | Recovery means a full rerun. This works because of overwrite, but it costs a full reprocess. |
| F7 | Alerting and notification | None in code | **Unable to Validate** | No job or alert config was provided. |

---

## 6. Identified Issues and Recommended Fixes

| ID | Severity | Issue | Recommended Fix |
|---|---|---|---|
| IS-01 | Critical | `overwriteSchema=true` together with column-intersection alignment silently removes columns and changes types. | Remove `overwriteSchema`. Define an explicit `StructType` per source, or cast to the target types. Fail the run if a required column is missing instead of dropping it. |
| IS-02 | Critical | `inferSchema=false` with no casting turns DECIMAL columns into STRING. | Apply `.schema(explicit_schema)` on read, or `select(col(c).cast(t))` using the target DDL. |
| IS-03 | High | Lineage columns are always NULL. | Use `.withColumn("file_path", col("_metadata.file_path")).withColumn("file_modification_time", col("_metadata.file_modification_time"))`. |
| IS-04 | High | Unbounded folder read loads every file that has accumulated in the folder. | Add a `run_date` or input-path parameter, or use Auto Loader (`cloudFiles`) with a checkpoint. Alternatively, archive processed files in an atomic step after a successful load. |
| IS-05 | High | A header-only (0-row) file can wipe a table. | Add a guard such as `if row_count == 0: raise` (or check against a configurable minimum threshold) before overwriting. |
| IS-06 | Medium | `load_date` is reset on every rerun. | Use a run-level `load_timestamp` taken from a job parameter. For incremental loads, use MERGE or `replaceWhere` keyed on `file_path` so the original load time is kept. |
| IS-07 | Medium | Column, audit-schema, and catalog names do not match the physical model. | Rename the metadata columns to `load_timestamp`/`update_timestamp`. Reconcile the audit DDL with the model (or update the model). Settle on `sunbelt_demo.bronze` or `bronze`. |
| IS-08 | Medium | No `run_id`, and no cross-table consistency marker. | Generate a `run_id` per execution and store it in the audit log and on each Bronze row. Write a run-level `PIPELINE_COMPLETE` audit record. |
| IS-09 | Medium | A failure in the audit write inside `except` hides the original error. | Wrap the audit write in its own try/except and always re-raise the original exception. |
| IS-10 | Low | Double read for `count()`. | Use the Delta commit metrics (`DESCRIBE HISTORY` → `operationMetrics.numOutputRows`), or cache the DataFrame before writing. |
| IS-11 | Low | Session-wide `autoMerge` is enabled. | Remove it, because overwrite does not need it. |
| IS-12 | Low | No selective rerun. | Accept a `sources` job parameter so the run can be limited to failed tables. |
| IS-13 | Low | No concurrency guard visible. | Set job `max_concurrent_runs=1`, and record the Delta table version in the audit log to support RESTORE. |

---

## 7. Overall Validation Results

| Area | Pass | Fail | Warning | Unable to Validate | Area Result |
|---|---|---|---|---|---|
| Idempotency | 2 | 3 | 3 | 1 | **Fail** |
| Duplicate Data Risk | 2 | 1 | 3 | 0 (D5 has a partial unvalidated element) | **Warning** |
| Rerun Safety | 0 | 3 | 3 | 0 | **Fail** |
| Failure Recovery | 2 | 0 | 4 | 1 | **Warning** |
| **Total** | **6** | **7** | **13** | **2** | **FAIL** |

**Conclusion:** Because the pipeline uses full overwrite, rerunning it on unchanged input does not create duplicate rows. It is still **not production-safe to rerun** for three reasons:
- Schema overwrite and column-intersection alignment can permanently remove columns and change types.
- A header-only file can wipe a table.
- File lineage is always NULL.

Fix IS-01 through IS-05 before treating this pipeline as idempotent. None of these conclusions come from executing the pipeline.

---

## apiCost
apiCost: 0.000000 USD (I could not get actual API cost from the tools; this figure is a placeholder)

---
outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Pipeline_Idempotency_Checker/Idempotency_Validation_Report.md
