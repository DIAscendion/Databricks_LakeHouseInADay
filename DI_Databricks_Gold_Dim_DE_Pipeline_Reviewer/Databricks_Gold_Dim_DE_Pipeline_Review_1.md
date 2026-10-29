_____________________________________________
**Author**: AAVA
**Created on**:
**Updated on**:
**Description**: Reviewer report validating the Gold dimension PySpark pipeline (`Databricks_Gold_Dim_DE_Pipeline_1.py`) against the Gold physical model (`Databricks_Gold_Model_Physical_1.txt`) for Rental Revenue to Cash.
**Version**: 1
_____________________________________________

# Databricks Gold Dim DE Pipeline Review

## 1. Inputs Reviewed
| Input | Path (repo `DIAscendion/Databricks_LakeHouseInADay`, branch `main`) |
|---|---|
| DE pipeline | `DI_Databricks_Gold_Dim_DE_Pipeline/Databricks_Gold_Dim_DE_Pipeline_1.py` |
| Target model | `DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_1.txt` |

Notes:
- The repository was not named in the request. I picked `DIAscendion/Databricks_LakeHouseInADay`, because both input paths exist there.
- No Silver physical schema, mapping-rule file or unsupported-features knowledge base was supplied. Source column checks are limited to what the pipeline and Gold model imply. Databricks compatibility is judged against the model's own "Spark SQL limitations" section and general Databricks knowledge.

## 2. Summary
**Overall verdict: ❌ NOT READY.** The pipeline runs against a different target schema than the physical model. It also has several logic defects.

| # | Check | Result |
|---|---|---|
| 1 | Metadata alignment (table names) | ❌ |
| 2 | Column / data type consistency | ❌ |
| 3 | Databricks compatibility | ❌ |
| 4 | Join column validity | ✅ (no joins; see 6) |
| 5 | Syntax correctness | ✅ |
| 6 | Development standards | ❌ |
| 7 | Transformation logic accuracy | ❌ |
| 8 | Error / audit table conformance | ❌ |

## 3. Metadata Alignment (Table Names)
| Pipeline table | Model table | Result |
|---|---|---|
| `gold.dim_customer` | `gold.go_dim_customer` | ❌ |
| `gold.dim_branch_employee` | None. The model has `go_dim_branch`, `go_dim_sales_rep` and `go_dim_collector`. | ❌ |
| `gold.dim_rental_contract` | `gold.go_dim_contract` | ❌ |
| `gold.dim_data_quality_errors` | `gold.go_error_data` | ❌ |
| `gold.dim_process_audit` | `gold.go_process_audit` | ❌ |
| Silver sources `si_customer_master`, `si_branch_employee`, `si_rental_contracts` | Match model section 4.1 | ✅ |

The pipeline never loads `go_dim_date`, `go_dim_region`, `go_dim_branch`, `go_dim_sales_rep`, `go_dim_collector`, `go_dim_equipment_class` or `go_dim_invoice`. It also skips the code tables. The scope is therefore only partial.

**Recommendation:** Rename all targets to the `go_` model names. Replace the branch_employee dimension with `go_dim_branch`, `go_dim_sales_rep` and `go_dim_collector`. Add the missing dimensions, or document them as out of scope.

## 4. Column and Data Type Consistency
| Item | Pipeline | Model | Result |
|---|---|---|---|
| Customer SK | `customer_dim_sk` | `dim_customer_sk` | ❌ |
| Contract SK | `rental_contract_dim_sk` | `dim_contract_sk` | ❌ |
| Metadata columns | `record_effective_timestamp`, `record_load_timestamp` | `load_date`, `update_date`, `source_system` | ❌ The pipeline emits the first two, which are not in the model. It does not emit `load_date` or `update_date`. |
| Customer attributes | Selects `over_limit_indicator`. It does not select `collector_id`, `collector_name`, `sales_rep_id`, `sales_rep_name`, `branch_code`, `branch_name` or `region_name`. | The model has all of these. `over_limit_indicator` is added in the update DDL. | ❌ |
| Contract attributes | Omits `customer_name`, `branch_name`, `region_name`, `sales_rep_name`, `equipment_class_name`, `open_contract_count`, `open_contract_value` and `total_billed_rental_days`. | The model has all of these. | ❌ |
| Contract `equipment_class` | Present | Present | ✅ |
| Branch dimension attributes | Employee-grain output (`employee_id`, `role`, `collector_id`) | `go_dim_branch` has `branch_name`, `branch_status`, `organization_hierarchy_name` and `network_level` | ❌ |
| String types | Source types retained | VARCHAR(n) | ⚠️ There are no explicit casts. `credit_limit` and `daily_rate` should be cast to `DECIMAL(18,2)`, and dates to DATE. |
| Table creation | `saveAsTable` overwrite on first run, so the schema is inferred from the DataFrame | Explicit DDL with partitioning | ❌ Partitioning and column types are lost. The model DDL is never run. |
| Pipeline column validation | Checks a subset of columns for only 3 tables | Full DDL | ❌ It validates a column list that was hard-coded in the pipeline, not the model. It also does not check types. |

**Recommendation:** Execute the model DDL (`CREATE TABLE IF NOT EXISTS ... USING DELTA PARTITIONED BY ...`) before loading. Select and cast exactly the model columns. Populate `load_date`, `update_date` and `source_system`.

## 5. Databricks Compatibility
| Check | Result | Comment |
|---|---|---|
| Delta format, `DeltaTable.merge`, `OPTIMIZE ... ZORDER` | ✅ | Z-order columns are not partition columns. |
| `df.rdd.isEmpty()` in `write_error_records` | ❌ | RDD APIs are not supported on shared or serverless compute. Use `df.isEmpty()` (Spark 3.3+) or `limit(1).count()`. |
| `DataFrame.subtract` on whole rows | ❌ | It is an `EXCEPT DISTINCT`, which silently removes duplicate valid rows. It also shuffles the whole table and fails on map-type columns. Use a `left_anti` join on the key, or filter with the negated condition. |
| `F.abs(F.xxhash64(...))` as surrogate key | ❌ | Hash collisions are possible. `abs(Long.MIN_VALUE)` stays negative. Use a deterministic key scheme such as `sha2`, or `row_number` on the business key. |
| Python `tuple[...]` return annotations | ⚠️ | Requires Python 3.9+. This is fine on current DBR. |
| Constraints / identity / TEXT / DATETIME | ✅ | None used. |

## 6. Join Column Validity
The pipeline contains no joins. The model's section 4.3 expects joins for branch, region, sales rep and collector enrichment, such as `si_rental_contracts.sales_rep_id` to `si_branch_employee.employee_id`. As a result, the enriched dimension columns cannot be populated. ❌ for enrichment completeness (see section 4). ✅ for join validity, because nothing invalid is present.

## 7. Syntax Correctness
No syntax errors were found on static reading. ✅. Imports are valid. `StringType`, `StructType`, `StructField`, `TimestampType` and `LongType` are imported but unused. This is minor.

## 8. Transformation Logic Accuracy
| Check | Result | Finding and recommendation |
|---|---|---|
| `standardize_text` regex | ❌ | `r"\\s+"` in a raw string matches a literal backslash followed by `s`, not whitespace. Whitespace is therefore never collapsed. Use `r"\s+"`. |
| Dedup window | ❌ | It partitions on the raw `customer_id`, `contract_id` and so on, before standardization. IDs differing only in whitespace become separate groups and then collide after trimming. Standardize first, then deduplicate. |
| Branch-employee merge key | ❌ | The grain is (`employee_id`, `branch_code`, `effective_date`), but the merge uses `employee_id` only. The merge is therefore ambiguous, and multiple source rows can match one target row, which causes a Delta merge failure. Merge on the surrogate key, or on the full composite key. |
| Rejected record handling | ❌ | A contract that fails both the mandatory-key and date checks is logged twice. `rejected` counts both, so rejects can exceed the real number of rejected rows. Rejected rows should be counted once. |
| Invalid rows excluded | ✅ | Invalid rows are excluded from the output. The `subtract` caveat in section 5 still applies. |
| `over_limit_indicator` | ⚠️ | Unknown values pass through unchanged, and so does the original case. Default them to `N` or flag them as errors. |
| Missing model rules | ❌ | There is no negative-amount check, no aging-bucket derivation and no divide-by-zero guard. The model lists these in 4.5, and some belong to facts. The dimension-relevant ones are `credit_limit >= 0` and `daily_rate >= 0`. |
| SCD handling | ⚠️ | The model describes "one row per customer version" and "contract version". The pipeline keeps only the latest row, so history is lost. Clarify the intended SCD behaviour. |
| Audit `source_table` | ❌ | It is derived from the function name. This gives `silver.si_customer` and `silver.si_rental_contract`, which are not real tables. Use `SOURCE_TABLES`. |
| `records_written` | ⚠️ | `merge_to_delta` calls `df.count()` after the write, which recomputes the whole lineage. Count once and cache. |
| Failed-run audit | ⚠️ | A failed run records 0 for read and rejected counts, which loses the diagnostics. |
| Audit key `int(time.time()*1e6)` | ⚠️ | Not guaranteed unique. Use a UUID-based or hash key. |

## 9. Error and Audit Table Conformance
| Error table | Pipeline | Model `go_error_data` | Result |
|---|---|---|---|
| Name | `dim_data_quality_errors` | `go_error_data` | ❌ |
| Columns | `source_table`, `target_table`, `validation_category`, `error_description`, `error_record_payload`, `detected_timestamp`, `processing_status`, `source_record_id` | `source_table_name`, `target_table_name`, `validation_rule_description`, `error_record_summary`, `error_detected_date`, `error_status`, `corrective_action`, `load_date`, `update_date`, `source_system` | ❌ |
| Partitioning | `layer_name`, `processing_status` | `error_status` | ❌ Partitioning on a constant column (`layer_name`) is wasteful. |

| Audit table | Pipeline | Model `go_process_audit` | Result |
|---|---|---|---|
| Name | `dim_process_audit` | `go_process_audit` | ❌ |
| Columns | `source_table`, `target_table`, `process_start_timestamp`, `process_end_timestamp`, `processing_status`, `error_message`, `executed_by`, `audit_remarks` | `source_table_name`, `target_table_name`, `process_start_time`, `process_end_time`, `process_status`, `audit_message`, `pipeline_run_date`, `layer_name`, `source_system`, `load_date`, `update_date` | ❌ |
| Types | Counts are BIGINT and duration is DOUBLE | Counts are DECIMAL(18,0) and duration is DECIMAL(18,2) | ❌ |

**Recommendation:** Create both tables using the model DDL and map the columns to the model names and types.

## 10. Development Standards
| Standard | Result | Comment |
|---|---|---|
| Header metadata (Author, Description, Version) | ✅ | |
| Modularity | ✅ | There are separate loader, merge, audit and optimize functions. |
| Logging | ❌ | It uses `print` only. Use the `logging` module with per-table start, end and count messages. |
| Hard-coded values | ⚠️ | `optimize_gold_tables` and the validation dictionary hard-code table names instead of using `TARGET_TABLES`. |
| Duplication | ⚠️ | The loaders repeat the same pattern. Extract a generic dimension-load function that takes config. |
| Error handling | ✅ | The pipeline writes a FAILED audit row and re-raises. A failure stops the remaining tables, which is acceptable but should be documented. |
| Formatting and typing | ✅ | There are type hints. The unused imports should be removed. |
| `apiCost` print in `__main__` | ⚠️ | A hard-coded `0.000000` is printed. It is not a real measurement. |

## 11. Prioritised Recommendations
1. Align table names, column names, types and partitioning with the Gold physical model. Run the model DDL, then load.
2. Fix the `standardize_text` regex to `r"\s+"`.
3. Fix the branch-employee merge key and the dimension split (branch, sales rep, collector).
4. Replace `subtract` with a `left_anti` join or a negated filter. Replace `rdd.isEmpty()`.
5. Standardize keys before deduplication. Avoid double-counting rejects.
6. Conform the error and audit tables to the model. Use real source table names in the audit.
7. Add the missing joins and enrichment columns, the missing dimensions and the amount validations.
8. Use the `logging` module and config-driven table lists.

## 12. apiCost
apiCost: 0.000000

Token usage for this call is not exposed to the agent, so the cost could not be measured. The value above is a placeholder, not a real figure.

## Output URL
https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Dim_DE_Pipeline_Reviewer/Databricks_Gold_Dim_DE_Pipeline_Review_1.md
