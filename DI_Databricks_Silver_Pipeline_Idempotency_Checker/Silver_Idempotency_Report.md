_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Idempotency, duplicate-data risk, rerun safety, and failure recovery assessment of the Databricks Silver DE Pipeline (Rental Revenue-to-Cash) against the Silver Physical Model.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Silver Pipeline Idempotency Checker – Report

**Repository:** `DIAscendion/Databricks_LakeHouseInADay` (branch `main`)
**Inputs analyzed (read via GitHub MCP):**
- `DI_Databricks_Silver_DE_Pipeline/Databricks_Silver_DE_Pipeline_1.py` (blob `f92ecc5`)
- `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` (blob `7df1427`)

**Analysis method:** Static review of code and model text only. Nothing was executed, tested, or run against a Databricks workspace, so this report contains no runtime evidence. Each status comes from what the code does, not from technology names such as Delta, overwrite, or MERGE.

---

## 1. Executive Summary

The pipeline fully rebuilds five Silver business tables. Each run reads the whole Bronze table and writes the result with `mode("overwrite")`. This design means repeated runs do not pile up duplicate business rows. However, several problems mean the pipeline is **not idempotent as a whole**:

1. **Error tables are append-only.** Each rerun adds every rejected Bronze record again to `silver.si_data_quality_errors` and `gold.go_data_quality_errors`, so these tables gain duplicates on every run.
2. **Business rows are not deterministic.** Surrogate keys come from `monotonically_increasing_id()`. `load_date` and `update_date` come from `current_timestamp()`. `days_past_due` and `aging_bucket` come from `current_date()`. `dropDuplicates()` keeps an arbitrary row. As a result, rerunning on the same Bronze snapshot can give different SKs, different metadata, and possibly different surviving rows.
3. **Deduplication runs before trimming.** Keys such as `" C1"` and `"C1"` both survive dedup and become duplicate business keys in Silver.
4. **The code does not match the physical model.** It uses different error and audit table names, different partition columns, different `load_date` types, and has extra or missing columns. If the model DDL is deployed first, overwrite runs may fail or replace the governed schema.
5. **Failure recovery is weak.** The five tables load one after another with no transaction across tables, no restart checkpoint, and no Bronze snapshot pinning. The Silver write and the two error writes are separate commits, so a partial failure leaves the tables inconsistent. A rerun then duplicates error rows.

**Overall Status: FAIL.** Business-table reruns mostly settle to the same result. Error-table duplication and non-deterministic outputs fail the idempotency requirement.

---

## 2. Idempotency Validation Report

| # | Check | Status | Evidence / Justification |
|---|---|---|---|
| I-1 | Silver business table write mode | **Pass** | `TableProcessor.write_silver` uses `df.write.format("delta").mode("overwrite")...saveAsTable(target_table)`. Each run replaces the whole table, so business rows do not accumulate. |
| I-2 | Source read scope / determinism of input | **Warning** | `read_bronze` uses `spark.table(table_name)` with no Delta version or timestamp pin, watermark, or incremental filter. A rerun picks up whatever Bronze holds at that moment. Results are repeatable only if Bronze has not changed. |
| I-3 | Deterministic surrogate keys | **Fail** | `rental_contract_sk`, `invoice_sk`, `cash_receipt_sk`, `customer_sk`, `branch_employee_sk`, and `error_sk` all use `F.monotonically_increasing_id()`. The values depend on partitioning and change between runs. Downstream joins on SK break after a rerun. The model (§15.2) asks for "deterministic or sequence-style assignment". |
| I-4 | Deterministic deduplication | **Fail** | `.dropDuplicates(["contract_id"])` (and the same for `invoice_id`, `receipt_id`, `customer_id`, `employee_id`+`branch_code`) has no ordering such as latest `file_modification_time`. Which record survives is arbitrary, so the same input can produce different attribute values on each run. |
| I-5 | Dedup before normalization | **Fail** | Dedup runs on raw Bronze keys before `trim_only`/`trim_upper`. Keys that differ only by whitespace survive as separate rows and become duplicate business keys after trimming. |
| I-6 | Deterministic derived/metadata columns | **Fail** | `load_date`/`update_date` = `F.current_timestamp()`. `days_past_due` = `datediff(current_date(), due_date)`, which also drives `aging_bucket`. These values change with run time, so a rerun on another day gives different invoice content. `update_date` is reset every run, so it no longer records when data actually changed. |
| I-7 | Error table write mode | **Fail** | `ErrorManager.persist_errors` uses `mode("append")` on both `silver.si_data_quality_errors` and `gold.go_data_quality_errors`. There is no MERGE, run key, or replace-where. Every rerun appends all rejected rows again. |
| I-8 | Audit table write mode | **Pass** | `AuditManager.write_audit` appends one row per table per run with a new `uuid4` `run_id`. Appending a run history is the intended behaviour. Note: `audit_sk` is always `None`. |
| I-9 | Target schema / table alignment with physical model | **Fail** | Model: `silver.si_error_data`, `silver.si_pipeline_audit`, `PARTITIONED BY (load_date)`, `load_date DATE`, columns `load_timestamp`/`update_timestamp`. Code: `silver.si_data_quality_errors`, `silver.si_process_audit`, partitions `contract_status`/`invoice_date`/`receipt_date`/`customer_status`/`region`, `load_date` TIMESTAMP, extra `aging_bucket`, `days_past_due`, `match_status`, `unapplied_payment_amount`, `over_limit_indicator`, no `load_timestamp`/`update_timestamp`. If the model DDL tables exist, an overwrite with different partitioning or schema and no `overwriteSchema` is expected to fail. Error and audit rows go to tables the model does not define. |
| I-10 | Idempotent table maintenance | **Pass** | `OPTIMIZE ... ZORDER BY` only rewrites files and does not change logical content, so repeating it is safe. |

---

## 3. Duplicate Data Risk Analysis

| Target | Risk | Status | Mechanism |
|---|---|---|---|
| `silver.si_rental_contracts` / `si_invoices` / `si_cash_receipts` / `si_customer_master` | Medium | **Warning** | Overwrite stops duplicates across runs. Duplicates within a run are possible because dedup runs before trim (I-5). No uniqueness check after transformation. |
| `silver.si_branch_employee` | Medium | **Warning** | Dedup uses the composite key (`employee_id`, `branch_code`) on untrimmed values, so `branch_code` case or whitespace variants survive. The model has no stated grain for this table. |
| `silver.si_data_quality_errors` | High | **Fail** | Append on every run. N reruns produce N copies of each rejected record, each with a different `error_sk`. |
| `gold.go_data_quality_errors` | High | **Fail** | Same append pattern. The Silver pipeline also writes into the Gold layer, which crosses layer boundaries. |
| `silver.si_process_audit` | Low | **Pass** | One row per run per table by design. Each run is a distinct event. |
| Records dropped by dedup | Medium | **Warning** | Rows removed by `dropDuplicates` are not routed to the error table, and nothing reconciles them. The audit `records_read` minus (written + rejected) gap is not explained. |

**Additional observation:** `records_read` comes from a separate `spark.table(source_table).count()` taken before the transform reads the table again. Concurrent Bronze writes can make the audit counts inconsistent.

---

## 4. Rerun Safety Assessment

| Scenario | Status | Assessment |
|---|---|---|
| Rerun after full success, Bronze unchanged | **Warning** | Business row sets settle to the same result, apart from the I-4/I-5 caveats. SKs and timestamps change, and the error tables double. |
| Rerun after full success, Bronze changed | **Warning** | Silver reflects the new full snapshot, which is acceptable for a full refresh. Earlier error rows stay OPEN even if the records were fixed. |
| Rerun of a single table | **Unable to Validate** | No parameters exist to choose a table or date. `run()` always processes all five tables, and no orchestration config was provided. |
| Concurrent runs | **Fail** | No locking, run guard, or concurrency control. Two concurrent overwrites can conflict, and appends to the error tables duplicate rows. |
| Backfill / historical reprocessing | **Unable to Validate** | No backfill logic or parameters, and no time-travel read. `current_date()` aging makes historical results impossible to reproduce. |
| Downstream (Gold) consumers after rerun | **Fail** | SKs change on every run (I-3), so any Gold table that stores Silver SKs ends up with broken references. |

---

## 5. Failure Recovery Analysis

| Failure Point (in `run_table_pipeline`) | Resulting State | Rerun Outcome | Status |
|---|---|---|---|
| During transform/count, before the write | Silver unchanged. Audit `FAILED` row written in `finally`. The exception stops later tables. | Clean rerun of all tables. | **Pass** |
| During `write_silver` | The Delta overwrite commits atomically, so the table keeps its previous version. | Clean. | **Pass** |
| After `write_silver`, during the Silver error append | Silver table refreshed, error rows not written, audit says `FAILED`. | Rerun completes. No duplicate. | **Warning** |
| After the Silver error append, during the Gold error append | Silver error rows committed, Gold missing them. | Rerun appends the Silver errors again, giving duplicates. | **Fail** |
| During `optimize_table` | All data committed, but audit marks the run `FAILED`. | Rerun appends the errors again, giving duplicates. Audit status is misleading. | **Fail** |
| Failure on table k of 5 | Tables 1..k-1 hold the new snapshot and k..5 the old one. Silver is inconsistent across tables, for example new invoices with old receipts. | Full rerun required. No resume or checkpoint. | **Warning** |
| Audit write fails inside `finally` | Can hide the original exception, and no run record is kept. | — | **Warning** |
| Recovery via Delta time travel / RESTORE | Delta history may allow a restore, but the code has no procedure for it, and the model warns against aggressive VACUUM without setting a retention period. | — | **Unable to Validate** |

---

## 6. Identified Issues and Recommended Fixes

| ID | Severity | Issue | Recommended Fix |
|---|---|---|---|
| F-1 | Critical | Error tables appended on every run (I-7) | Add `run_id`/`batch_id` to the error rows. Use `MERGE` on (`source_table`, `source_record_id`, `validation_rule_name`, error hash), or `replaceWhere source_table = '<t>'` overwrite per source table. |
| F-2 | Critical | Non-deterministic SKs (I-3) | Use a deterministic hash such as `xxhash64(source_system, business_key)`, or an identity column with MERGE so existing SKs are kept. |
| F-3 | High | Arbitrary dedup survivor (I-4) | Use a `row_number()` window partitioned by the normalized key, ordered by `file_modification_time DESC, file_path DESC`, and keep rank 1. Send the rest to the error or audit table. |
| F-4 | High | Dedup before trim (I-5) | Normalize keys first, then dedup. Add an assertion after the write that `count == countDistinct(key)`. |
| F-5 | High | Code and physical model mismatch (I-9) | Align table names (`si_error_data`, `si_pipeline_audit`), the `load_date` partition and DATE type, and add `load_timestamp`/`update_timestamp`. Add the derived columns to the model through the model's §8 ALTER pattern. Do not rely on implicit schema replacement. |
| F-6 | High | Time-dependent values (I-6) | Pass a `processing_date` parameter in place of `current_date()`. Keep `load_timestamp` from first insert and only change `update_timestamp` when the row changes, using MERGE with a change hash. |
| F-7 | Medium | No Bronze snapshot pinning (I-2) | Read once with `versionAsOf` captured at the start of the run. Reuse the same DataFrame for counts and the transform, and record the version in the audit row. |
| F-8 | Medium | Partial failure leaves Silver and Gold error tables inconsistent and duplicates on rerun | Write errors before Silver, or make both error writes idempotent (F-1). Move the Gold error write to the Gold pipeline. |
| F-9 | Medium | OPTIMIZE failure marks data-committed run FAILED | Wrap `OPTIMIZE` in its own try block with a non-fatal warning, or run it as a separate maintenance task. |
| F-10 | Medium | No concurrency guard | Use a single-concurrency job setting or a run lock (audit `RUNNING` row check). |
| F-11 | Low | Cross-table inconsistency on mid-run failure | Add a restart parameter (`start_from_table`), or stage to temp tables and swap them only after all five succeed. |
| F-12 | Low | `audit_sk` always NULL. Dedup-dropped rows not counted | Fill `audit_sk` deterministically and add a `records_deduplicated` count. |

---

## 7. Overall Validation Results

| Area | Pass | Warning | Fail | Unable to Validate | Area Status |
|---|---|---|---|---|---|
| Idempotency (I-1..I-10) | 3 | 1 | 6 | 0 | **Fail** |
| Duplicate Data Risk | 1 | 3 | 2 | 0 | **Fail** |
| Rerun Safety | 0 | 2 | 2 | 2 | **Fail** |
| Failure Recovery | 2 | 3 | 2 | 1 | **Fail** |
| **Total** | **6** | **9** | **12** | **3** | **FAIL** |

**Verdict:** The pipeline is **not rerun-safe** in its current form. Full-overwrite business tables give partial protection. Error-table duplication, non-deterministic keys and dedup, and the schema mismatch with the physical model need fixing (F-1 to F-5) before the pipeline can be considered idempotent. All findings come from static code review. No execution or testing was performed.

---

## 8. apiCost
apiCost: 0.000000 USD (not measured by this agent; reported as zero)
