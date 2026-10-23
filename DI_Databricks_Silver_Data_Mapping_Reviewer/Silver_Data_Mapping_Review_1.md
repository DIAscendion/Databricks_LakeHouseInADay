=============================================
Author:        Ascendion AVA+
Created on:    
Description:   Review of the Bronze-to-Silver data mapping for Rental Revenue-to-Cash (cleansing, validation, business rules, error handling and audit) in the Databricks Silver layer
=============================================

# Silver Data Mapping Review – Rental Revenue to Cash Reports

Reviewed artifacts:
- Primary input (the mapping): `DI_Databricks_Silver_DQ_Data_Mapping/Databricks_Silver_DQ_Data_Mapping_1.md` (Version 1)
- Reference input (DQ requirements): `DI_Databricks_Silver_DQ_Recommender/Databricks_Silver_DQ_Recommender_1.md` (Version 1)

Legend: ✅ = correct / adequate   ❌ = incorrect, ambiguous or missing

---

## 1. Executive Summary

**Overall verdict: CONDITIONALLY ACCEPTABLE – REWORK REQUIRED BEFORE PIPELINE BUILD.**

The mapping is well structured. It covers all 5 business entities (`si_rental_contracts`, `si_invoices`, `si_cash_receipts`, `si_customer_master`, `si_branch_employee`) plus an error table (`si_data_quality_errors`) and an audit table (`si_process_audit`). Lineage columns are kept, and trimming, casing, date and decimal standardization is applied consistently. However, the mapping was written without the DQ Recommender output; its Section 2 says "No previous DQ recommender agent output was provided". As a result, it conflicts with several business constraints from the Recommender. Its derived attributes also depend on data and joins that the mapping does not define.

**Finding counts:** ✅ 36 | ❌ 49

**Top critical issues:**
1. ❌ The domain values for `contract_status` and `customer_status` conflict with the business constraints (the Recommender allows only OPEN/CLOSED and ACTIVE/SUSPENDED).
2. ❌ The credit memo sign rule is vague. The constraints require CREDIT_MEMO amounts to be negative and all other invoice amounts to be ≥ 0.
3. ❌ `due_date` is nullable, yet it drives `aging_bucket` and `days_past_due`. The aging buckets (0-30/31-60/61-90/90+) are not listed. Aging uses `current_date` instead of a snapshot date, so results change every time the job is re-run.
4. ❌ `match_status`, `unapplied_payment_amount` and `over_limit_indicator` need cross-table data (applied amounts, outstanding AR). No source, join or formula is given for this data. The `match_status` domain also conflicts with the Recommender's `APPLIED` value.
5. ❌ Referential checks are optional ("may be logged"). The constraints require every contract and invoice to map to a valid customer, and every invoice to map to a valid contract.
6. ❌ There is no explicit deduplication logic (business key + latest record), even though customer deduplication is a business requirement.
7. ❌ The error table has no `run_id` link to the audit table. The audit table takes its start time and run_id from Bronze audit rows instead of the Silver run.
8. ❌ Silver target data types are not stated for any column, and `load_date`/`update_date` have two possible sources ("pipeline timestamp or Bronze load timestamp").

---

## 2. Methodology

1. I read both input files in full from GitHub (`DIAscendion/Databricks_LakeHouseInADay`, branch `main`).
2. I extracted:
   - Source tables: `bronze.bz_rental_contracts`, `bz_invoices`, `bz_cash_receipts`, `bz_customer_master`, `bz_branch_employee`, `bz_audit_log`
   - Target tables: the 7 Silver tables listed in Section 4 of the mapping
   - Transformations: trim/upper/initcap, date parsing, DECIMAL(18,2) casting, derived fields
   - Joins: implied for derived fields only; none are specified
   - Aggregations: none at Silver level
   - Filters: the valid/invalid split
   - Output format: Delta tables, with MERGE INTO, OPTIMIZE and ZORDER
   - Validation rules, error/audit design and lineage columns
3. I checked each mapped attribute against the 9-point checklist: structure, consistency, transformations, validation, audit, business requirements, error handling, lineage, and nulls/edge cases.
4. I cross-checked each attribute against the Recommender's 50 DQ checks and the Bronze column data types the Recommender documents (e.g., `daily_rate DECIMAL(10,2)`, `invoice_amount DECIMAL(12,2)`, dates stored as STRING).
5. All findings come only from these two files. Where information needed for a check was missing, I marked it ❌.

---

## 3. Findings

### 3.1 Data Consistency
✅ All Bronze business columns documented in the Recommender for the 5 entity tables are mapped 1:1 to Silver columns with the same names. Examples: `contract_id`, `daily_rate`, `invoice_amount`, `payment_method`, `credit_limit`, `collector_id`.
✅ Monetary columns are widened safely from Bronze DECIMAL(10,2)/(12,2) to Silver DECIMAL(18,2) (`daily_rate`, `invoice_amount`, `tax_amount`, `payment_amount`, `credit_limit`).
✅ Bronze STRING dates are converted to Silver DATE (`contract_start_date`, `contract_end_date`, `invoice_date`, `due_date`, `receipt_date`, `customer_since`, `effective_date`).
✅ Naming is consistent: snake_case, `si_` prefix on Silver tables and `_sk` suffix on surrogate keys.
✅ The lineage columns (`source_system`, `file_path`, `file_modification_time`) are carried into every entity table.
❌ The target data type of every Silver column is missing. The mapping tables have no "Target Data Type" column, so string lengths, the timestamp vs date choice for `load_date`/`update_date`, and integer vs bigint for `days_past_due` cannot be verified. **Fix:** Add Source Data Type and Target Data Type columns to every mapping table.
❌ `load_date`/`update_date` (all tables) are named as dates but filled from timestamps, and their source is ambiguous ("pipeline processing timestamp or Bronze load timestamp"). **Fix:** Pick one: `load_date = current_timestamp()` of the Silver run, typed TIMESTAMP. Keep Bronze `load_timestamp` in a separate `bronze_load_timestamp` column.
❌ The Bronze `load_timestamp`/`update_timestamp` values are lost after the Silver load, because Silver overwrites them with pipeline timestamps. **Fix:** Keep them as separate lineage columns.
❌ The table names differ between the two inputs: the Recommender uses `silver.contracts`, `silver.customers` and `silver.branch_employee`, while the mapping uses `silver.si_rental_contracts`, `silver.si_customer_master` and `silver.si_branch_employee`. Recommender check 20 also expects `load_timestamp`/`update_timestamp` columns in Silver. **Fix:** Agree on one set of Silver table and column names and update the DQ rule SQL to match.
❌ `si_process_audit.run_id` comes from `bz_audit_log.record_id`, but the transformation also says "or generated pipeline run id". These two values mean different things. **Fix:** Use a generated Silver run_id and store the Bronze `record_id` as `bronze_audit_record_id`.

### 3.2 Transformations
✅ String standardization is applied consistently: `trim()` on identifiers, `upper(trim())` on codes and domains (`branch_code`, `contract_status`, `invoice_type`, `currency`, `payment_method`, `role`, `region`, `source_system`), and `initcap(trim())` on names.
✅ Date parsing uses a prioritized format list (`yyyy-MM-dd`, `MM/dd/yyyy`, `yyyyMMdd`) and rejects required dates that cannot be parsed (Section 5.1).
✅ Decimal casting is safe: non-numeric values are rejected and no default is applied (`daily_rate`).
✅ Domain synonyms are mapped to standard values before validation (Section 5.2).
✅ `days_past_due` allows negative values for invoices that are not yet due.
❌ `si_invoices.aging_bucket` and `days_past_due` use `datediff(current_date, due_date)`, which is non-deterministic, so re-runs give different results. The Recommender (checks 22 and 36) derives them from `snapshot_date - due_date`. The bucket list is also missing. **Fix:** Add a `snapshot_date` (or as-of date parameter). Derive buckets as 0-30 / 31-60 / 61-90 / 90+ from `datediff(snapshot_date, due_date)`, and define a bucket such as `CURRENT` for negative days.
❌ `si_cash_receipts.match_status` and `unapplied_payment_amount` are based on "invoice linkage and amount application logic", but no source for applied amounts exists in `bz_cash_receipts`, and no join or formula is given. **Fix:** State the formula. For example, join to `si_invoices` on `invoice_id`, then `unapplied = payment_amount - least(payment_amount, open_invoice_amount)`. Define the status rules for each value.
❌ `si_customer_master.over_limit_indicator` needs "outstanding exposure", which `bz_customer_master` does not contain. **Fix:** Specify the cross-table aggregation (Σ open `si_invoices` amount − Σ applied `si_cash_receipts` per `customer_id`) and how often it is refreshed. Alternatively, move this attribute to a later step or the Gold layer.
❌ Credit memo sign normalization is not defined. `invoice_amount` says only "business-allowed signed amount based on invoice_type". **Fix:** Add a rule: if `invoice_type = 'CREDIT_MEMO'` the stored amount must be negative (negate it if the source sends positive amounts, per the business decision); otherwise the amount must be ≥ 0.
❌ The date parse formats `MM/dd/yyyy` and `dd/MM/yyyy` can be ambiguous. The format priority is "such as", not a fixed list, and parsing differs by source system. **Fix:** Fix the format list for each `source_system` and turn off lenient parsing (use ANSI mode or `try_to_date` with explicit formats).
❌ The surrogate key strategy is vague: "deterministic sequence/identity strategy". **Fix:** Use either `GENERATED ALWAYS AS IDENTITY` or `xxhash64(business_key, source_system)`, and state how keys stay stable across MERGE.
❌ No transformation is defined for the `sales_rep_id` "employee identifier format" or for `collector_id`. **Fix:** Give the regex or format and the action taken when a value does not match.

### 3.3 Validation Rules
✅ Every entity table has not-null and not-blank checks on its primary business identifier (`contract_id`, `invoice_id`, `receipt_id`, `customer_id`, `employee_id`).
✅ Numeric range checks are defined: `daily_rate >= 0`, `payment_amount >= 0`, `credit_limit >= 0`, `unapplied_payment_amount >= 0`, and audit counts ≥ 0.
✅ Date sequence checks are defined: `contract_end_date >= contract_start_date` and `due_date >= invoice_date`.
✅ Domain checks are defined for `contract_status`, `invoice_type`, `customer_status`, `match_status`, `error_severity` and `processing_status`.
❌ `si_rental_contracts.contract_status` allows ACTIVE/CLOSED/CANCELLED/PENDING, which conflicts with constraint-based Recommender check 2 (OPEN/CLOSED only). **Fix:** Align with the business constraint, or document approved mappings (e.g., ACTIVE→OPEN). Note that Recommender check 46 also refers to CANCELLED, so this needs business confirmation.
❌ `si_customer_master.customer_status` allows ACTIVE/INACTIVE/SUSPENDED/CLOSED, while Recommender check 16 allows only ACTIVE/SUSPENDED. **Fix:** Align the domain list.
❌ `si_invoices.due_date` is nullable, but Recommender check 7 requires it, and aging depends on it. **Fix:** Make it NOT NULL with HIGH severity, or define a default derived from `invoice_date` + `credit_terms`.
❌ `si_invoices.contract_id` is nullable with a soft rule ("should align"), while Recommender check 27 requires every invoice to reference a valid contract. **Fix:** Make it mandatory and add a referential check against `si_rental_contracts`.
❌ `si_invoices.currency` uses length=3 as "preferred", while Recommender check 10 requires `^[A-Z]{3}$`. **Fix:** Enforce the regex.
❌ The `match_status` domain (MATCHED/UNMATCHED/PARTIAL/UNAPPLIED) conflicts with Recommender check 29, which uses `APPLIED`. **Fix:** Agree on one domain list.
❌ The `role` domain (`si_branch_employee`), `region` domain, `payment_method` approved list, `credit_terms` codes, `source_system` codes and `branch_code` format are not listed. Recommender check 18 expects SALES_REP/COLLECTOR. **Fix:** List the allowed values in a parameterized reference table.
❌ The referential checks (contract→customer, invoice→customer, invoice→contract, receipt→invoice, `sales_rep_id`/`collector_id`→employee, `branch_code`→hierarchy) are optional ("may be logged … based on orchestration policy"). **Fix:** Turn each one into a named rule with a severity and an action (reject vs flag), following Recommender checks 26–30.
❌ Uniqueness is stated as "unique within snapshot", but the uniqueness checks for `employee_id` and the composite (`employee_id`, `effective_date`) are missing, and no Recommender-style rule IDs exist. **Fix:** Give every rule an ID that matches the `validation_rule_name` values in the error table.
❌ The action when `contract_end_date < contract_start_date` or `due_date < invoice_date` is only "flag", with no severity or reject decision. **Fix:** Define the severity and whether the record is loaded.

### 3.4 Compliance with Best Practices
✅ The mapping uses Delta Lake, `MERGE INTO` for incremental upserts, and `OPTIMIZE`/`ZORDER` (Section 6).
✅ It uses a split-and-quarantine pattern, with valid rows written to Silver and invalid rows to the error table.
✅ Native PySpark functions are recommended (no UDFs), which is good for performance.
✅ Bronze payloads are preserved as JSON for remediation.
❌ There is no incremental load or watermark strategy (e.g., by `file_modification_time` or `update_timestamp`), and no idempotency or re-run guarantee. **Fix:** Define the watermark column, the MERGE keys and the match conditions for each table.
❌ No partitioning or liquid clustering columns are given; the mapping only refers to the physical model. **Fix:** State the clustering keys for each table (e.g., `invoice_date`, `customer_id`).
❌ Using `current_date` in Silver transformations breaks reproducibility (`aging_bucket`, `days_past_due`). **Fix:** Use a parameterized as-of date.
❌ Domain lists and thresholds are hard-coded in the text. **Fix:** Store them as config or reference tables, as Recommender Section 7 suggests.
❌ No DLT expectations or Unity Catalog constraints (CHECK / NOT NULL) are specified. **Fix:** Map the HIGH-severity rules to Delta CHECK constraints or DLT `expect_or_drop`.

### 3.5 Business Requirements Alignment
✅ The mapping covers all core Revenue-to-Cash entities: contracts, invoices, receipts, customers and branch personnel.
✅ It supports AR aging, cash application and credit risk through the derived fields (`aging_bucket`, `days_past_due`, `match_status`, `unapplied_payment_amount`, `over_limit_indicator`).
✅ Unapplied cash is kept and flagged instead of being dropped (`match_status = UNAPPLIED`, nullable `invoice_id`), as Recommender check 44 requires.
✅ Negative amounts are allowed only for credit memos and reversals (Section 5.3).
❌ The mapping states that the DQ Recommender output was not available, so its 50 recommended checks are not traced. **Fix:** Add a traceability matrix (Recommender check # → mapping rule) and close the gaps.
❌ Customer deduplication (legal-entity duplicates, Recommender check 21) is not implemented. **Fix:** Define the dedup key, the survivorship rule (latest `update_timestamp`/`file_modification_time`) and the window logic.
❌ The rule "applied amount must not exceed invoice amount" (Recommender check 43) is missing. **Fix:** Add it to the `unapplied_payment_amount` and `match_status` derivation.
❌ The check `receipt_date >= invoice_date` (Recommender check 45) is missing. **Fix:** Add a cross-table validation.
❌ The Silver objects the Recommender relies on (`ar_aging`, `rental_revenue`, `cash_application`, `credit_risk`, `branch_hierarchy`, `dim_date`, `snapshot_date`, `applied_amount`, `gross_billings`, `credit_memo_amount`) are not in the mapping. **Fix:** Confirm whether they belong to Silver or Gold, and add their mappings or record the scope decision.
❌ The Cognos report cross-reference was not done because no `.report` file was supplied. Report-level business rules therefore cannot be verified. **Fix:** Get the report specification, or have the business sign off on the gap.

### 3.6 Error Handling and Logging
✅ There is a dedicated `silver.si_data_quality_errors` table with source table, record ID, file path, rule name, category, description, payload, severity, status and timestamps.
✅ A HIGH/MEDIUM/LOW severity model is defined, with criteria for each level.
✅ The remediation status lifecycle is defined (OPEN/REMEDIATED/IGNORED).
❌ The error table has no `run_id` or audit foreign key, so errors cannot be tied to a pipeline execution. **Fix:** Add `run_id` (and `pipeline_name`).
❌ The column that failed and its value are not captured (`failed_column`, `failed_value`). **Fix:** Add both fields.
❌ The mapping does not say which rules reject a record and which only flag it (or warn and load). One record can fail several rules, and the mapping does not say how that is stored. **Fix:** Add an action column (REJECT/FLAG) to each rule, and store one error row per failed rule.
❌ There is no strategy for reprocessing or replaying remediated records, and no failure threshold (e.g., fail the job if the reject % exceeds X). **Fix:** Define the replay path and the thresholds that lead to PARTIAL or FAILED.
❌ Pipeline-level failures (exceptions, schema drift) have no handling beyond `error_message`. **Fix:** Define try/except logging and alerting.

### 3.7 Effective Data Mapping
✅ All 15 `si_rental_contracts` fields are mapped, with source, validation and transformation.
✅ All 17 `si_invoices` fields are mapped (2 of them derived).
✅ All 14 `si_cash_receipts` fields are mapped (2 of them derived).
✅ All 13 `si_customer_master` and 13 `si_branch_employee` fields are mapped.
✅ System-generated, derived and constant fields are clearly labelled (`[SYSTEM GENERATED]`, `[DERIVED]`, `[CONSTANT]`).
❌ The derived fields `match_status`, `unapplied_payment_amount` and `over_limit_indicator` list only their own Bronze table as the source, although they need other tables. **Fix:** List every source table and the join keys.
❌ Many `si_process_audit` fields are `[DERIVED]` from "orchestration metrics" (`records_read_count`, `records_written_count`, `records_rejected_count`, `pipeline_name`, `target_table`), but they are attributed to `bronze.bz_audit_log`. **Fix:** Set the source to the Silver run context, not the Bronze audit table.
❌ `si_branch_employee` has no history handling (SCD) even though it has `effective_date`. **Fix:** Define SCD Type 1 or Type 2 and the merge key.

### 3.8 Audit Table and Data Lineage
✅ `si_process_audit` captures the pipeline, source and target table, start and end timestamps, status, read/written/rejected counts, duration, error message and executed_by.
✅ Record-level lineage is kept through `source_system`, `file_path` and `file_modification_time` in every entity table, and through `source_file_path` in the error table.
✅ A run_id is generated for each execution so loads can be replayed and traced (Section 3.2).
❌ `process_start_timestamp` and `process_end_timestamp` come from the Bronze `load_timestamp`/`processing_time`. These describe the Bronze load, not the Silver load. **Fix:** Capture the Silver run start and end times.
❌ The entity tables have no `run_id` or batch ID, so a row cannot be traced back to the audit run that loaded it. **Fix:** Add `run_id` to every Silver table.
❌ The audit table is missing the inserted vs updated counts, the watermark or version (Delta version written), and DQ rule-level results (rule name, failed row count), which Recommender Section 7 asks for. **Fix:** Add these fields, or a child table `si_dq_rule_results`.
❌ There is no column-level lineage for derived fields (the formulas and inputs for aging, match and over-limit are not documented). **Fix:** Document the inputs of each derived field.

### 3.9 Data Quality
✅ Nulls are handled explicitly for each column (nullable or mandatory is stated for every field).
✅ Empty strings are treated as missing values ("Not empty after trim").
✅ Negative `days_past_due` (not yet due) is handled as an edge case.
❌ Duplicates have no handling (in-batch or across batches) beyond "unique within snapshot". **Fix:** Add `row_number()` dedup over the business key, ordered by `update_timestamp desc`, `file_modification_time desc`.
❌ Division and exposure edge cases are not covered: `over_limit_indicator` when `credit_limit` is NULL or 0. **Fix:** Define the result (e.g., NULL limit → `N` plus a flag, 0 limit with exposure → `Y`).
❌ Boundary values are not covered: future-dated `invoice_date`/`receipt_date`, implausible `customer_since`, zero-duration contracts (Recommender check 46), and `tax_amount` greater than `invoice_amount`. **Fix:** Add plausibility range rules.
❌ Orphan records (e.g., a receipt whose `invoice_id` does not exist) are not classified as rejected or flagged. **Fix:** Define how they are handled and give each case a severity.

---

## 4. Recommendations

### High priority
1. Align the domain values with the business constraints: `contract_status`, `customer_status`, `match_status` and `role`. Store the allowed values in reference tables.
2. Define the credit memo sign rule and the non-negative rule for standard invoices on `si_invoices.invoice_amount`.
3. Make `due_date` mandatory (or define a fallback). Derive aging from a parameterized `snapshot_date` with the 0-30/31-60/61-90/90+ buckets.
4. Fully specify the joins, sources and formulas for `match_status`, `unapplied_payment_amount` and `over_limit_indicator`, including the rule that applied cash must not exceed the invoice amount. Otherwise, move these fields to a later layer.
5. Make the referential checks mandatory named rules (Recommender checks 26–30), and make `si_invoices.contract_id` mandatory.
6. Add deduplication and survivorship logic for all entity tables, especially `si_customer_master`.
7. Add `run_id` to the error table and to every Silver table. Base the audit timestamps and run_id on the Silver run, not Bronze.

### Medium priority
8. Add target data types to every mapping row and fix the single source of `load_date`/`update_date`. Keep the Bronze timestamps as lineage columns.
9. Add a rule ID, severity and REJECT/FLAG action to every validation, plus a traceability matrix to the 50 Recommender checks.
10. Specify the incremental watermark, MERGE keys, idempotency and the SCD approach for `si_branch_employee`.
11. Add `failed_column` and `failed_value` to the error table, along with reprocessing and failure-threshold rules.
12. Agree on one set of Silver table and column names across the mapping and the DQ rule SQL.

### Low priority
13. Fix the date formats for each source system and enable strict (ANSI) parsing.
14. Define the surrogate key method (IDENTITY vs hash).
15. Add plausibility rules for future dates and boundary amounts, and enforce the currency regex `^[A-Z]{3}$`.
16. Add clustering or partition keys, and Delta CHECK constraints or DLT expectations for HIGH-severity rules.
17. Resolve the missing Cognos report input, or get the business to sign off on the gap.
