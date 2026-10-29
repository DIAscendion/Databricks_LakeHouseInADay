_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Idempotency, duplicate-data risk, rerun safety and failure recovery assessment of the Gold dimension PySpark pipeline
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Gold Dimension Pipeline – Idempotency Report

**Repository used:** `DIAscendion/Databricks_LakeHouseInADay` (branch `main`). The request did not name a repo, so I picked the most plausible candidate. The two input files were found there.
**Inputs read via GitHub MCP:**
- `DI_Databricks_Gold_Dim_DE_Pipeline/Databricks_Gold_Dim_DE_Pipeline_1.py`
- `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt`

**Method:** static review only. The pipeline was not executed and no runtime evidence exists. Where behaviour depends on data, the status is Warning or Unable to Validate.
**Change request:** none. No prior report existed at the target path, so this is version 1.

## 1. Executive Summary
Overall result: **FAIL (not idempotent or rerun-safe as written).**

The `MERGE` and the deterministic surrogate keys give a partial base. Four defects outweigh them:
1. `gold.dim_branch_employee` is merged on `employee_id` alone, but its source grain is `(employee_id, branch_code, effective_date)`. Any employee with more than one row makes the MERGE fail with "multiple source rows matched". The table also cannot hold one row per grain.
2. The error table is append-only with no dedup. Every rerun duplicates every rejected record.
3. Error rows are written before the merge. A failed merge followed by a retry duplicates them.
4. The pipeline's table names and schemas do not match the physical model (`gold.dim_*` vs `gold.go_dim_*`), so the model cannot be used to validate or rerun against these tables.

## 2. Idempotency Validation Report

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Deterministic surrogate keys | Warning | `abs(xxhash64(business key))` is stable across runs. There is no collision handling. `abs()` of Long.MIN_VALUE stays negative. |
| 2 | Upsert key matches target grain – customer | Warning | Merge on `customer_id`. Dedup partitions by the raw `customer_id`, but the id is standardized (trim/collapse) afterwards. Two raw ids that differ only by whitespace become the same key, giving duplicate source keys and a merge failure. |
| 3 | Upsert key matches target grain – branch_employee | **Fail** | `merge_key="employee_id"`, but dedup and `branch_employee_dim_sk` use `(employee_id, branch_code, effective_date)`. Multiple source rows match one target row, so Delta raises an error. On first load (overwrite) the table holds several rows per employee. On later runs the merge fails or is ambiguous. |
| 4 | Upsert key matches target grain – rental_contract | Pass (with caveat) | Merge on `contract_id`, same as dedup grain. Same whitespace-normalization caveat as customer. |
| 5 | Deterministic dedup | Warning | `row_number` orders by `update_date`, `load_date` desc. Ties are not broken, so the winning row can differ between runs. |
| 6 | MERGE semantics | Warning | `whenMatchedUpdateAll` is unconditional. A rerun rewrites all matched rows with identical values. The end state is stable, but there is write amplification and a new Delta version each run. |
| 7 | First-run path | Warning | `overwrite` + `saveAsTable` when the table is missing. Schema is inferred from the DataFrame and does not follow the physical model DDL. A concurrent first run is racy. |
| 8 | Deletes and invalidated rows | Warning | Records removed from Silver, or newly rejected, are never removed from Gold. Stale rows persist. |
| 9 | Error table idempotency | **Fail** | `append` with no merge or anti-join. `error_sk` hashes the payload only, so the same error under a different rule collides. `detected_timestamp` changes every run. |
| 10 | Audit table | Warning | Append-only per attempt, which is acceptable for a log. There is no `run_id`, and `audit_sk` is epoch microseconds, so concurrent runs could collide. |
| 11 | Source set operations | Pass | `subtract` is deterministic. It also de-duplicates exact duplicate source rows. |
| 12 | Execution or testing evidence | Unable to Validate | No test or run logs were provided. |

## 3. Duplicate Data Risk Analysis

| Table | Risk | Status | Reason |
|---|---|---|---|
| `gold.dim_customer` | Low–Medium | Warning | Key normalization after dedup. |
| `gold.dim_branch_employee` | **High** | Fail | Merge key coarser than grain. |
| `gold.dim_rental_contract` | Low–Medium | Warning | Same normalization issue as customer. |
| `gold.dim_data_quality_errors` | **High** | Fail | Unbounded duplicates on rerun or retry. |
| `gold.dim_process_audit` | Low | Warning | Retry produces extra rows (intended). |

Also noted:
- `standardize_text` uses `r"\\s+"` inside a regex. That matches a literal backslash followed by `s`, not whitespace, so internal whitespace is not collapsed. This is a correctness bug, but it affects idempotency only in that the key dedup assumptions above are partly masked.
- A Gold-vs-model table name mismatch exists. The pipeline writes `gold.dim_*`, `gold.dim_data_quality_errors` and `gold.dim_process_audit`. The model defines `gold.go_dim_*`, `gold.go_error_data` and `gold.go_process_audit`. Running both could create two sets of data.

## 4. Rerun Safety Assessment

| Scenario | Status | Assessment |
|---|---|---|
| Rerun, unchanged Silver | Fail | Customer and contract dimensions stay stable. The branch-employee merge fails or is ambiguous. Error rows are duplicated. |
| Rerun after Silver correction | Warning | Upserts apply, but rows that are no longer valid or no longer present stay in Gold. |
| Concurrent runs | Warning | No lock or run-level guard. Delta optimistic concurrency may raise conflicts. |
| Re-execution within a single run | Warning | `dim_df` is lazy. `merge_to_delta` calls `df.count()` after the merge, which re-reads Silver. `records_written` is the source count, not the rows actually changed. |
| Audit accuracy | Warning | `source_table` is derived from the function name, e.g. `silver.si_customer`, `silver.si_branch_employee`, `silver.si_rental_contract`. The real tables are `si_customer_master`, `si_branch_employee`, `si_rental_contracts`. |

## 5. Failure Recovery Analysis

| Aspect | Status | Evidence |
|---|---|---|
| Per-table failure audit | Pass | A try/except writes a FAILED audit row and re-raises. |
| Atomicity across steps | Fail | Error records are appended before the merge. A merge failure leaves the error rows, and a retry duplicates them. |
| Cross-table consistency | Warning | Tables load sequentially. A failure in table N leaves tables 1..N-1 committed. This is safe to rerun only if the merge is idempotent, and it is not for table 2. |
| Resume or checkpoint | Warning | No watermark or checkpoint. Each run does a full reload. This is simple, but costly. |
| Failure-audit detail | Warning | Failed audit rows report 0 read, 0 written and 0 rejected. Partial progress is lost. If the audit write itself fails, the original exception is masked. |
| Post-load steps | Warning | OPTIMIZE and column validation run after all loads. A validation failure happens after data is committed, with no rollback. Delta `RESTORE` is not used. |
| Delta time travel | Unable to Validate | Retention and VACUUM settings were not provided. |

## 6. Identified Issues and Recommended Fixes

| # | Severity | Issue | Recommended fix |
|---|---|---|---|
| 1 | High | Branch-employee merge key is `employee_id` only. | Merge on `branch_employee_dim_sk`, or on `employee_id AND branch_code AND effective_date`. Assert source key uniqueness before the merge. |
| 2 | High | Error table appends duplicates. | Build a deterministic `error_sk` from table, rule, record id and payload. `MERGE ... WHEN NOT MATCHED INSERT`. Alternatively add a `run_id` and delete-then-insert per run, or `replaceWhere`. |
| 3 | High | Error writes precede the merge. | Write errors after a successful merge, or make them idempotent per `run_id`. |
| 4 | High | Table names and schemas differ from the physical model. | Align targets to the `go_*` names, or update the model. Create the tables with explicit DDL. Drop the overwrite first-load path. |
| 5 | Medium | Dedup and key normalization are out of order. | Standardize keys before `row_number`. Add a final unique tiebreaker such as a hash of all columns. |
| 6 | Medium | Unconditional `whenMatchedUpdateAll`. | Add a change-detection condition, e.g. a hash compare or `update_date` comparison. |
| 7 | Medium | No handling of removed or now-invalid records. | Add `WHEN NOT MATCHED BY SOURCE` with a soft-delete flag, or restate that Gold is append-only for business reasons. |
| 8 | Medium | `records_written` and audit source names are inaccurate. | Use the Delta operation metrics from `DeltaTable.history()`. Use the `SOURCE_TABLES` values. Add a `run_id`. |
| 9 | Low | Regex bug in `standardize_text`. | Use `r"\s+"`. |
| 10 | Low | No concurrency guard. | Add a run lock or `run_id` check. Cache or persist `dim_df` for the run. |

## 7. Overall Validation Results

| Dimension | Status |
|---|---|
| Idempotency | **Fail** |
| Duplicate-data risk | **Fail** (error table, branch-employee dimension) |
| Rerun safety | **Fail** |
| Failure recovery | **Warning** (partial) |
| Runtime or test evidence | Unable to Validate |

**Final verdict: FAIL.** Fix issues 1–4 before the pipeline is promoted. Then re-validate with an actual double-run test (run twice on the same Silver data and compare row counts, keys and error counts).

## 8. apiCost
apiCost: 0.000000
