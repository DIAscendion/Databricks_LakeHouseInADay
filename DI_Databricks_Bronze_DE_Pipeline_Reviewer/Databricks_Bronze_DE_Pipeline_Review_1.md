_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Reviewer report validating the Databricks Bronze DE PySpark pipeline (Rental Revenue to Cash Reports) against the source schema, Bronze physical model, and Bronze data mapping.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Bronze DE Pipeline Review – Rental Revenue to Cash Reports

## 1. Review Scope and Inputs

| Input | Repository Path | Role |
|---|---|---|
| DE Pipeline (PySpark) | `DI_Databricks_Bronze_DE_Pipeline/Databricks_Bronze_DE_Pipeline_1.py` | Code under review |
| Data Mapping | `DI_Databricks_Bronze_Model_Data_Mapping/Databricks_Bronze_Model_Data_Mapping_1.md` | Mapping rules (1-1 source → Bronze) |
| Physical Model | `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` | Target data model (DDL incl. audit table) |
| Source Schema | `Input/rental_revenue_to_cash_bronze_schema.sql` | Source metadata |

Repository: `DIAscendion/Databricks_LakeHouseInADay` (branch `main`).
Unsupported-features knowledge base: none was provided as a separate file, so the review used standard Databricks Runtime and Unity Catalog compatibility rules.

## 2. Summary of Results

| # | Validation Area | Result |
|---|---|---|
| 1 | Metadata alignment (source ↔ model ↔ pipeline) | ❌ |
| 2 | Data type & column consistency | ❌ |
| 3 | Databricks compatibility | ❌ (partial) |
| 4 | Join column validity | ✅ |
| 5 | Syntax correctness | ❌ |
| 6 | Development standards (modularity, logging, formatting) | ❌ (partial) |
| 7 | Transformation logic accuracy | ❌ |

**Overall verdict:** ❌ **Not ready for promotion.** The pipeline has a sound modular structure, but several blocking defects need to be fixed first. The file header is not valid Python. Writing with overwrite and overwriteSchema replaces the decimal schema with strings. Lineage and source_system values are lost. The metadata column names don't match the physical model.

## 3. Metadata Alignment

| Check | Expected (Model / Mapping) | Pipeline | Status |
|---|---|---|---|
| Source tables covered | 5 tables: rental_contracts, invoices, cash_receipts, customer_master, branch_employee | All 5 configured in `SOURCE_CONFIG` | ✅ |
| Target table naming | Physical: `bronze.bz_<name>`; Mapping/Source SQL: `sunbelt_demo.bronze.bronze_<name>` | `sunbelt_demo.bronze.bz_<name>` | ❌ Inconsistent across artifacts (pipeline follows the physical model's naming with a catalog prefix and doesn't match the mapping) |
| Business columns per table | As per source SQL | All business columns present in DDL | ✅ |
| Audit columns | `load_timestamp`, `update_timestamp` | `load_date`, `update_date` | ❌ |
| Lineage columns | `source_system`, `file_path`, `file_modification_time` (1-1 from source) | Present in DDL, but populated with literals/NULL (see §7) | ❌ |
| Audit table schema | `record_id, source_table, load_timestamp, processed_by, processing_time, status` | `audit_id, pipeline_name, source_name, target_table, status, row_count, message, process_start_time, process_end_time, processing_time_seconds, processed_by, created_at` | ❌ Diverges from physical model |

**Recommendations**
1. Rename `load_date`/`update_date` to `load_timestamp`/`update_timestamp` in both the DDL and `enrich_with_metadata`.
2. Settle on one table naming convention (`bz_` or `bronze_`) and update the mapping document or the pipeline to match.
3. Align `bz_audit_log` with the physical model. If the richer audit schema is preferred, update the physical model to version 2 instead.

## 4. Data Type & Column Consistency

| Table | Column(s) | Model Type | Pipeline Behaviour | Status |
|---|---|---|---|---|
| bz_rental_contracts | daily_rate | DECIMAL(10,2) | CSV read with `inferSchema=false` gives STRING. `overwriteSchema=true` then replaces the table type with STRING | ❌ |
| bz_invoices | invoice_amount, tax_amount | DECIMAL(12,2) | Same issue: written as STRING | ❌ |
| bz_cash_receipts | payment_amount | DECIMAL(12,2) | Same issue: written as STRING | ❌ |
| bz_customer_master | credit_limit | DECIMAL(12,2) | Same issue: written as STRING | ❌ |
| All | file_modification_time | TIMESTAMP | `lit(None).cast("timestamp")` keeps the type but the value is always NULL | ⚠️ type ✅ / value ❌ |
| All | date columns (`*_date`, `customer_since`) | STRING (raw) | STRING | ✅ |
| All | ID / text columns | STRING | STRING | ✅ |
| Audit | row_count | LONG/BIGINT | `LongType` | ✅ |
| All | column presence | All target columns required | `align_to_target_table` silently drops target columns missing from the source | ❌ |

**Recommendations**
- Define an explicit `StructType` schema for each source and pass it to `reader.schema(...)`, or cast to the target types before writing (`col("daily_rate").cast("decimal(10,2)")`).
- Remove `overwriteSchema=true`. Keep the table DDL as the schema contract and let schema enforcement reject drift.
- In `align_to_target_table`, add any missing target columns as typed NULLs and log a warning, so they are not silently dropped.

## 5. Databricks Compatibility

| Feature | Finding | Status |
|---|---|---|
| Delta Lake `saveAsTable`, `CREATE TABLE IF NOT EXISTS ... USING DELTA` | Supported | ✅ |
| Three-level Unity Catalog names (`sunbelt_demo.bronze.*`) | Supported | ✅ |
| `LONG` type in DDL | Accepted alias for BIGINT. Prefer `BIGINT` for consistency | ✅ |
| `/mnt/raw/...` DBFS mount paths | Deprecated and unsupported on Unity Catalog shared/serverless compute | ❌ Use UC Volumes (`/Volumes/sunbelt_demo/raw/...`) or external locations |
| `SparkSession.builder...enableHiveSupport().getOrCreate()` | Works but redundant on Databricks. Builder `.config` for session TZ is ignored when the session already exists | ⚠️ Use `spark.conf.set(...)` |
| `spark.databricks.delta.schema.autoMerge.enabled=true` | Global auto-merge weakens schema enforcement in Bronze | ❌ Remove; use per-write `mergeSchema` only if intended |
| `spark.sparkContext.sparkUser()` fallback | `sparkContext` is not available on serverless / shared access mode | ⚠️ Keep inside try (already), but prefer `current_user()` only |
| `_metadata` column for file lineage | Not used, even though it is the supported way to capture file path and modification time | ❌ |
| `datetime.utcnow()` | Deprecated in Python 3.12 (DBR 15+) | ⚠️ Use `datetime.now(timezone.utc)` |

## 6. Join Column Validity

| Check | Finding | Status |
|---|---|---|
| Joins in Bronze | The mapping and physical model specify no joins in Bronze. The pipeline performs none | ✅ |
| Downstream join keys exist in targets | `customer_id`, `contract_id`, `invoice_id`, `sales_rep_id`/`employee_id`, `branch_code`, `region` are present in the respective Bronze DDLs with matching STRING types | ✅ |

## 7. Transformation Logic Accuracy

| Rule (Mapping / Model) | Pipeline Implementation | Status |
|---|---|---|
| 1-1 mapping of business columns, no cleansing | Columns passed through unchanged | ✅ |
| No filters, dedup, or aggregations | None applied | ✅ |
| Append-only raw ingestion | `.mode("overwrite")` replaces history on every run | ❌ |
| `source_system` is 1-1 from the source field | Overwritten with config literals such as `"LEGACY_SE\|LEGACY_MW\|SUNBELT_CORE"` and `"HR_FEED\|HR_FEED_OLD"`, which removes row-level lineage needed by Silver (e.g. HR_FEED vs HR_FEED_OLD dedup) | ❌ |
| `file_path`, `file_modification_time` are lineage from the source file | Set to NULL unless the CSV contains them | ❌ |
| Audit logging of every load | SUCCESS/FAILED entries are written per table | ✅ |
| Row count accuracy | `df.count()` after the write re-reads the source (extra scan, and the count could differ from what was written) | ⚠️ |
| Failure handling | The first failing table stops all remaining tables (`raise`) | ⚠️ Acceptable, but consider continue-on-error with a final failure summary |

**Recommended enrichment logic**

```python
from pyspark.sql.functions import col, current_timestamp, lit, coalesce

def enrich_with_metadata(df, default_source_system):
    df = df.withColumn("file_path", col("_metadata.file_path")) \
           .withColumn("file_modification_time", col("_metadata.file_modification_time"))
    src = col("source_system") if "source_system" in df.columns else lit(None)
    return (df.withColumn("source_system", coalesce(src, lit(default_source_system)))
              .withColumn("load_timestamp", current_timestamp())
              .withColumn("update_timestamp", current_timestamp()))

def write_to_bronze(df, target_table):
    df = df.cache()
    row_count = df.count()
    df.write.format("delta").mode("append").saveAsTable(target_table)
    df.unpersist()
    return row_count
```

## 8. Syntax Correctness

| Check | Finding | Status |
|---|---|---|
| File header block | Lines `_____________________________________________` and `## *Author*: AAVA` are not Python comments and raise `SyntaxError` on import | ❌ Wrap in a `"""docstring"""` or prefix each line with `#` |
| Imports | `expr`, `col` are imported but unused | ⚠️ |
| Function definitions / type hints | Valid | ✅ |
| DataFrame API usage | Valid | ✅ |
| f-strings / exception handling | Valid | ✅ |

## 9. Development Standards Compliance

| Standard | Finding | Status |
|---|---|---|
| Modularity | Clear separation: read / enrich / align / write / audit / orchestrate | ✅ |
| Configuration-driven | `SOURCE_CONFIG` and `TARGET_DDL` dictionaries | ✅ |
| Logging | Uses `print` only. No `logging` module, log levels, or per-table progress logs | ❌ Add a `logging` logger with INFO/ERROR levels |
| Audit trail | Structured Delta audit table | ✅ |
| Formatting / naming | PEP 8 compliant, descriptive names | ✅ |
| Hard-coded values | Paths, catalog and `API_COST_USD` are hard-coded | ⚠️ Use Databricks widgets / job parameters |
| Docstrings | None on functions | ⚠️ |
| Error-message hygiene | Full exception text goes into the audit table (could exceed limits or expose paths) | ⚠️ Truncate the message |

## 10. Consolidated Recommendations (Priority Order)

1. **Fix the syntax error.** Convert the header block to Python comments or a docstring.
2. **Use append-only writes and enforce the schema.** Switch to `mode("append")`, remove `overwriteSchema` and global autoMerge, and apply explicit source schemas or casts for DECIMAL columns.
3. **Fix lineage.** Populate `file_path`/`file_modification_time` from `_metadata`, and keep the row-level `source_system` with the config value only as a fallback.
4. **Align metadata names.** Use `load_timestamp`/`update_timestamp`, and reconcile the audit table schema with the physical model.
5. **Resolve naming conflicts.** Settle on `bz_` or `bronze_` table names across the mapping, physical model and pipeline.
6. **Update for Unity Catalog.** Replace `/mnt` paths with UC Volumes and use `spark.conf.set` for session settings.
7. **Improve standards.** Add the `logging` module, docstrings, parameterization, and a cached count before the write.

## 11. API Cost

| Metric | Value |
|---|---|
| apiCost (USD) | 0.0412875 |

Estimate based on ~45,000 input tokens and ~5,500 output tokens for this review call.

## 12. Output Location

[Databricks_Bronze_DE_Pipeline_Review_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Bronze_DE_Pipeline_Reviewer/Databricks_Bronze_DE_Pipeline_Review_1.md)
