-- =====================================================================================
-- Author:            AAVA
-- Created on:        2026-10-23
-- Description:       Databricks Bronze Data Profiler SQL – Rental Revenue to Cash Reports
-- Version:           1
-- Updated on:        2026-10-23
-- Input File:        DI_Databricks_Bronze_Metadata_Discovery/Metadata_Discovery_Output.md (v1)
-- Repository:        DIAscendion/Databricks_LakeHouseInADay (branch: main)
-- Do_You_Need_Any_Changes: No (initial version – no prior profiler output existed)
-- =====================================================================================
--
-- 1. ANALYSIS
--    Five verified Bronze tables in sunbelt_demo.bronze (from the metadata discovery DDL):
--      Bz_Rental_Contracts (12 cols), Bz_Invoices (12), Bz_Cash_Receipts (9),
--      Bz_Customer_Master (9), Bz_Branch_Employee (10).
--    Bz_Branch_Master is "Recommended – Not Verified" and has NO DDL -> not profiled.
--    No PK/FK/NOT NULL constraints exist; logical keys are profiled for duplicates.
--    Dates are STRING with mixed formats (ISO yyyy-MM-dd and MM/dd/yyyy); blank and
--    9999-12-31 sentinels exist. Negative invoice_amount = credit memo (valid).
--
-- 2. PREREQUISITES
--    * Databricks SQL warehouse or cluster (DBR 11.3+ for try_to_date / count_if).
--    * USE CATALOG / SELECT privilege on sunbelt_demo.bronze.* (read-only).
--    * Tables must already be created and loaded. If your catalog/schema differs
--      (e.g. <env>_ent_bronze_db.finance), replace "sunbelt_demo.bronze" globally.
--    * Credentials: authenticate via your Databricks workspace / secret scope.
--      No credentials are embedded here.
--
-- 3. EXECUTION INSTRUCTIONS
--    Run sections in order in a Databricks SQL editor or notebook (%sql). All
--    statements are SELECT-only (read-only); no DDL/DML. Each query returns a small
--    result set; save results for the Silver design stage.
--
-- 4. EXPECTED RESULTS (based on documented sample data; actual values unknown)
--    * Exact duplicate rows in contracts, receipts, customer master (rerun dupes).
--    * Null sales_rep_id/customer_id (contracts), null due_date (invoices),
--      null receipt_date/customer_id/invoice_id (receipts), null customer_name.
--    * Orphan invoices (e.g. contract_id RC-999999), mixed date formats,
--      region spelling variants, stale HR_FEED_OLD duplicates.
--
-- 5. EXECUTION STATUS / LIMITATIONS
--    * NOT EXECUTED. No Databricks workspace credentials were available to this agent;
--      queries were generated only. Row counts/results are not known.
--    * Profiling is limited to columns documented in the source schema.
--
-- 6. CHECKLIST
--    [ ] Catalog/schema confirmed   [ ] SELECT privileges granted
--    [ ] Sections A–G executed      [ ] Results captured and reviewed
--    [ ] DQ issues logged for Silver cleansing rules
--
-- 7. API COST: Not Available
-- =====================================================================================

USE CATALOG sunbelt_demo;
USE SCHEMA bronze;

-- =====================================================================================
-- SECTION A: ROW COUNTS & LINEAGE COVERAGE
-- =====================================================================================
SELECT 'Bz_Rental_Contracts' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT source_system) AS source_systems, COUNT(DISTINCT file_path) AS files, MIN(file_modification_time) AS first_load, MAX(file_modification_time) AS last_load FROM sunbelt_demo.bronze.Bz_Rental_Contracts
UNION ALL
SELECT 'Bz_Invoices', COUNT(*), COUNT(DISTINCT source_system), COUNT(DISTINCT file_path), MIN(file_modification_time), MAX(file_modification_time) FROM sunbelt_demo.bronze.Bz_Invoices
UNION ALL
SELECT 'Bz_Cash_Receipts', COUNT(*), COUNT(DISTINCT source_system), COUNT(DISTINCT file_path), MIN(file_modification_time), MAX(file_modification_time) FROM sunbelt_demo.bronze.Bz_Cash_Receipts
UNION ALL
SELECT 'Bz_Customer_Master', COUNT(*), COUNT(DISTINCT source_system), COUNT(DISTINCT file_path), MIN(file_modification_time), MAX(file_modification_time) FROM sunbelt_demo.bronze.Bz_Customer_Master
UNION ALL
SELECT 'Bz_Branch_Employee', COUNT(*), COUNT(DISTINCT source_system), COUNT(DISTINCT file_path), MIN(file_modification_time), MAX(file_modification_time) FROM sunbelt_demo.bronze.Bz_Branch_Employee;

-- Row counts by source system
SELECT 'Bz_Rental_Contracts' AS table_name, source_system, COUNT(*) AS rows FROM sunbelt_demo.bronze.Bz_Rental_Contracts GROUP BY source_system
UNION ALL SELECT 'Bz_Invoices', source_system, COUNT(*) FROM sunbelt_demo.bronze.Bz_Invoices GROUP BY source_system
UNION ALL SELECT 'Bz_Cash_Receipts', source_system, COUNT(*) FROM sunbelt_demo.bronze.Bz_Cash_Receipts GROUP BY source_system
UNION ALL SELECT 'Bz_Customer_Master', source_system, COUNT(*) FROM sunbelt_demo.bronze.Bz_Customer_Master GROUP BY source_system
UNION ALL SELECT 'Bz_Branch_Employee', source_system, COUNT(*) FROM sunbelt_demo.bronze.Bz_Branch_Employee GROUP BY source_system
ORDER BY table_name, source_system;

-- =====================================================================================
-- SECTION B: NULL / BLANK PROFILE + DISTINCT COUNTS (per column)
-- =====================================================================================
SELECT
  COUNT(*) AS total_rows,
  count_if(contract_id IS NULL OR trim(contract_id) = '')                 AS contract_id_null_blank,
  COUNT(DISTINCT contract_id)                                             AS contract_id_distinct,
  count_if(customer_id IS NULL OR trim(customer_id) = '')                 AS customer_id_null_blank,
  COUNT(DISTINCT customer_id)                                             AS customer_id_distinct,
  count_if(branch_code IS NULL OR trim(branch_code) = '')                 AS branch_code_null_blank,
  COUNT(DISTINCT branch_code)                                             AS branch_code_distinct,
  count_if(sales_rep_id IS NULL OR trim(sales_rep_id) = '')               AS sales_rep_id_null_blank,
  COUNT(DISTINCT sales_rep_id)                                            AS sales_rep_id_distinct,
  count_if(equipment_class IS NULL OR trim(equipment_class) = '')         AS equipment_class_null_blank,
  COUNT(DISTINCT equipment_class)                                         AS equipment_class_distinct,
  count_if(contract_start_date IS NULL OR trim(contract_start_date) = '') AS start_date_null_blank,
  count_if(contract_end_date IS NULL OR trim(contract_end_date) = '')     AS end_date_null_blank,
  count_if(contract_end_date = '9999-12-31')                              AS end_date_sentinel_9999,
  count_if(contract_status IS NULL OR trim(contract_status) = '')         AS contract_status_null_blank,
  COUNT(DISTINCT contract_status)                                         AS contract_status_distinct,
  count_if(daily_rate IS NULL)                                            AS daily_rate_null
FROM sunbelt_demo.bronze.Bz_Rental_Contracts;

SELECT
  COUNT(*) AS total_rows,
  count_if(invoice_id IS NULL OR trim(invoice_id) = '')     AS invoice_id_null_blank,
  COUNT(DISTINCT invoice_id)                                AS invoice_id_distinct,
  count_if(contract_id IS NULL OR trim(contract_id) = '')   AS contract_id_null_blank,
  COUNT(DISTINCT contract_id)                               AS contract_id_distinct,
  count_if(customer_id IS NULL OR trim(customer_id) = '')   AS customer_id_null_blank,
  COUNT(DISTINCT customer_id)                               AS customer_id_distinct,
  count_if(invoice_date IS NULL OR trim(invoice_date) = '') AS invoice_date_null_blank,
  count_if(due_date IS NULL OR trim(due_date) = '')         AS due_date_null_blank,
  count_if(invoice_amount IS NULL)                          AS invoice_amount_null,
  count_if(tax_amount IS NULL)                              AS tax_amount_null,
  count_if(invoice_type IS NULL OR trim(invoice_type) = '') AS invoice_type_null_blank,
  COUNT(DISTINCT invoice_type)                              AS invoice_type_distinct,
  count_if(currency IS NULL OR trim(currency) = '')         AS currency_null_blank,
  COUNT(DISTINCT currency)                                  AS currency_distinct
FROM sunbelt_demo.bronze.Bz_Invoices;

SELECT
  COUNT(*) AS total_rows,
  count_if(receipt_id IS NULL OR trim(receipt_id) = '')         AS receipt_id_null_blank,
  COUNT(DISTINCT receipt_id)                                    AS receipt_id_distinct,
  count_if(invoice_id IS NULL OR trim(invoice_id) = '')         AS invoice_id_null_blank_unapplied,
  COUNT(DISTINCT invoice_id)                                    AS invoice_id_distinct,
  count_if(customer_id IS NULL OR trim(customer_id) = '')       AS customer_id_null_blank,
  COUNT(DISTINCT customer_id)                                   AS customer_id_distinct,
  count_if(receipt_date IS NULL OR trim(receipt_date) = '')     AS receipt_date_null_blank,
  count_if(payment_amount IS NULL)                              AS payment_amount_null,
  count_if(payment_method IS NULL OR trim(payment_method) = '') AS payment_method_null_blank,
  COUNT(DISTINCT payment_method)                                AS payment_method_distinct
FROM sunbelt_demo.bronze.Bz_Cash_Receipts;

SELECT
  COUNT(*) AS total_rows,
  count_if(customer_id IS NULL OR trim(customer_id) = '')         AS customer_id_null_blank,
  COUNT(DISTINCT customer_id)                                     AS customer_id_distinct,
  count_if(customer_name IS NULL OR trim(customer_name) = '')     AS customer_name_null_blank,
  COUNT(DISTINCT upper(trim(customer_name)))                      AS customer_name_distinct_normalized,
  count_if(credit_terms IS NULL OR trim(credit_terms) = '')       AS credit_terms_null_blank,
  COUNT(DISTINCT credit_terms)                                    AS credit_terms_distinct,
  count_if(credit_limit IS NULL)                                  AS credit_limit_null,
  count_if(customer_since IS NULL OR trim(customer_since) = '')   AS customer_since_null_blank,
  count_if(customer_status IS NULL OR trim(customer_status) = '') AS customer_status_null_blank,
  COUNT(DISTINCT customer_status)                                 AS customer_status_distinct
FROM sunbelt_demo.bronze.Bz_Customer_Master;

SELECT
  COUNT(*) AS total_rows,
  count_if(employee_id IS NULL OR trim(employee_id) = '')       AS employee_id_null_blank,
  COUNT(DISTINCT employee_id)                                   AS employee_id_distinct,
  count_if(employee_name IS NULL OR trim(employee_name) = '')   AS employee_name_null_blank,
  count_if(role IS NULL OR trim(role) = '')                     AS role_null_blank,
  COUNT(DISTINCT role)                                          AS role_distinct,
  count_if(branch_code IS NULL OR trim(branch_code) = '')       AS branch_code_null_blank,
  COUNT(DISTINCT branch_code)                                   AS branch_code_distinct,
  count_if(region IS NULL OR trim(region) = '')                 AS region_null_blank,
  COUNT(DISTINCT region)                                        AS region_distinct_raw,
  COUNT(DISTINCT upper(trim(region)))                           AS region_distinct_normalized,
  count_if(collector_id IS NULL OR trim(collector_id) = '')     AS collector_id_null_blank,
  count_if(effective_date IS NULL OR trim(effective_date) = '') AS effective_date_null_blank
FROM sunbelt_demo.bronze.Bz_Branch_Employee;

-- =====================================================================================
-- SECTION C: CATEGORICAL DOMAINS / VALUE FREQUENCIES
-- =====================================================================================
SELECT 'contract_status' AS column_name, contract_status AS value, COUNT(*) AS freq FROM sunbelt_demo.bronze.Bz_Rental_Contracts GROUP BY contract_status
UNION ALL SELECT 'equipment_class', equipment_class, COUNT(*) FROM sunbelt_demo.bronze.Bz_Rental_Contracts GROUP BY equipment_class
UNION ALL SELECT 'branch_code', branch_code, COUNT(*) FROM sunbelt_demo.bronze.Bz_Rental_Contracts GROUP BY branch_code
ORDER BY column_name, freq DESC;

SELECT 'invoice_type' AS column_name, invoice_type AS value, COUNT(*) AS freq FROM sunbelt_demo.bronze.Bz_Invoices GROUP BY invoice_type
UNION ALL SELECT 'currency', currency, COUNT(*) FROM sunbelt_demo.bronze.Bz_Invoices GROUP BY currency
ORDER BY column_name, freq DESC;

SELECT payment_method AS value, COUNT(*) AS freq FROM sunbelt_demo.bronze.Bz_Cash_Receipts GROUP BY payment_method ORDER BY freq DESC;

SELECT 'credit_terms' AS column_name, credit_terms AS value, COUNT(*) AS freq FROM sunbelt_demo.bronze.Bz_Customer_Master GROUP BY credit_terms
UNION ALL SELECT 'customer_status', customer_status, COUNT(*) FROM sunbelt_demo.bronze.Bz_Customer_Master GROUP BY customer_status
ORDER BY column_name, freq DESC;

SELECT 'role' AS column_name, role AS value, COUNT(*) AS freq FROM sunbelt_demo.bronze.Bz_Branch_Employee GROUP BY role
UNION ALL SELECT 'region', region, COUNT(*) FROM sunbelt_demo.bronze.Bz_Branch_Employee GROUP BY region
UNION ALL SELECT 'branch_code', branch_code, COUNT(*) FROM sunbelt_demo.bronze.Bz_Branch_Employee GROUP BY branch_code
ORDER BY column_name, freq DESC;

-- Credit memo consistency: invoice_type vs amount sign
SELECT invoice_type,
       CASE WHEN invoice_amount < 0 THEN 'negative' WHEN invoice_amount = 0 THEN 'zero' WHEN invoice_amount > 0 THEN 'positive' ELSE 'null' END AS amount_sign,
       COUNT(*) AS freq
FROM sunbelt_demo.bronze.Bz_Invoices
GROUP BY 1, 2 ORDER BY 1, 2;

-- =====================================================================================
-- SECTION D: NUMERIC RANGES
-- =====================================================================================
SELECT 'Bz_Rental_Contracts.daily_rate' AS metric, MIN(daily_rate) AS min_val, MAX(daily_rate) AS max_val, AVG(daily_rate) AS avg_val, percentile_approx(daily_rate, 0.5) AS median_val, count_if(daily_rate <= 0) AS non_positive_cnt FROM sunbelt_demo.bronze.Bz_Rental_Contracts
UNION ALL SELECT 'Bz_Invoices.invoice_amount', MIN(invoice_amount), MAX(invoice_amount), AVG(invoice_amount), percentile_approx(invoice_amount, 0.5), count_if(invoice_amount <= 0) FROM sunbelt_demo.bronze.Bz_Invoices
UNION ALL SELECT 'Bz_Invoices.tax_amount', MIN(tax_amount), MAX(tax_amount), AVG(tax_amount), percentile_approx(tax_amount, 0.5), count_if(tax_amount < 0) FROM sunbelt_demo.bronze.Bz_Invoices
UNION ALL SELECT 'Bz_Cash_Receipts.payment_amount', MIN(payment_amount), MAX(payment_amount), AVG(payment_amount), percentile_approx(payment_amount, 0.5), count_if(payment_amount <= 0) FROM sunbelt_demo.bronze.Bz_Cash_Receipts
UNION ALL SELECT 'Bz_Customer_Master.credit_limit', MIN(credit_limit), MAX(credit_limit), AVG(credit_limit), percentile_approx(credit_limit, 0.5), count_if(credit_limit <= 0) FROM sunbelt_demo.bronze.Bz_Customer_Master;

-- =====================================================================================
-- SECTION E: DATE (STRING) FORMAT & RANGE PROFILE
--   Classifies each raw date string: ISO (yyyy-MM-dd), US (MM/dd/yyyy), blank/null, other.
--   Parsed range uses coalesce(try_to_date ISO, try_to_date US).
-- =====================================================================================
WITH d AS (
  SELECT 'Bz_Rental_Contracts' t, 'contract_start_date' c, contract_start_date v FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  UNION ALL SELECT 'Bz_Rental_Contracts', 'contract_end_date', contract_end_date FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  UNION ALL SELECT 'Bz_Invoices', 'invoice_date', invoice_date FROM sunbelt_demo.bronze.Bz_Invoices
  UNION ALL SELECT 'Bz_Invoices', 'due_date', due_date FROM sunbelt_demo.bronze.Bz_Invoices
  UNION ALL SELECT 'Bz_Cash_Receipts', 'receipt_date', receipt_date FROM sunbelt_demo.bronze.Bz_Cash_Receipts
  UNION ALL SELECT 'Bz_Customer_Master', 'customer_since', customer_since FROM sunbelt_demo.bronze.Bz_Customer_Master
  UNION ALL SELECT 'Bz_Branch_Employee', 'effective_date', effective_date FROM sunbelt_demo.bronze.Bz_Branch_Employee
), p AS (
  SELECT t, c, v,
    CASE WHEN v IS NULL OR trim(v) = '' THEN 'NULL_OR_BLANK'
         WHEN v RLIKE '^\\d{4}-\\d{2}-\\d{2}$' THEN 'ISO_yyyy-MM-dd'
         WHEN v RLIKE '^\\d{1,2}/\\d{1,2}/\\d{4}$' THEN 'US_MM/dd/yyyy'
         ELSE 'OTHER' END AS fmt,
    coalesce(try_to_date(v, 'yyyy-MM-dd'), try_to_date(v, 'M/d/yyyy')) AS parsed
  FROM d
)
SELECT t AS table_name, c AS column_name,
  COUNT(*) AS total,
  count_if(fmt = 'ISO_yyyy-MM-dd') AS iso_cnt,
  count_if(fmt = 'US_MM/dd/yyyy')  AS us_cnt,
  count_if(fmt = 'NULL_OR_BLANK')  AS null_blank_cnt,
  count_if(fmt = 'OTHER')          AS other_fmt_cnt,
  count_if(fmt <> 'NULL_OR_BLANK' AND parsed IS NULL) AS unparseable_cnt,
  count_if(parsed = DATE'9999-12-31') AS sentinel_9999_cnt,
  MIN(parsed) AS min_date,
  MAX(CASE WHEN parsed <> DATE'9999-12-31' THEN parsed END) AS max_date_excl_sentinel,
  count_if(parsed > current_date() AND parsed <> DATE'9999-12-31') AS future_date_cnt
FROM p GROUP BY t, c ORDER BY t, c;

-- Logical date checks
SELECT 'contract_end_before_start' AS check_name, COUNT(*) AS violations
FROM sunbelt_demo.bronze.Bz_Rental_Contracts
WHERE coalesce(try_to_date(contract_end_date,'yyyy-MM-dd'), try_to_date(contract_end_date,'M/d/yyyy'))
    < coalesce(try_to_date(contract_start_date,'yyyy-MM-dd'), try_to_date(contract_start_date,'M/d/yyyy'))
UNION ALL
SELECT 'invoice_due_before_invoice_date', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Invoices
WHERE coalesce(try_to_date(due_date,'yyyy-MM-dd'), try_to_date(due_date,'M/d/yyyy'))
    < coalesce(try_to_date(invoice_date,'yyyy-MM-dd'), try_to_date(invoice_date,'M/d/yyyy'));

-- =====================================================================================
-- SECTION F: STRING LENGTH & ID FORMAT PROFILE
-- =====================================================================================
WITH s AS (
  SELECT 'Bz_Rental_Contracts' t, 'contract_id' c, contract_id v FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  UNION ALL SELECT 'Bz_Rental_Contracts', 'customer_id', customer_id FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  UNION ALL SELECT 'Bz_Rental_Contracts', 'sales_rep_id', sales_rep_id FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  UNION ALL SELECT 'Bz_Rental_Contracts', 'equipment_class', equipment_class FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  UNION ALL SELECT 'Bz_Invoices', 'invoice_id', invoice_id FROM sunbelt_demo.bronze.Bz_Invoices
  UNION ALL SELECT 'Bz_Invoices', 'contract_id', contract_id FROM sunbelt_demo.bronze.Bz_Invoices
  UNION ALL SELECT 'Bz_Invoices', 'currency', currency FROM sunbelt_demo.bronze.Bz_Invoices
  UNION ALL SELECT 'Bz_Cash_Receipts', 'receipt_id', receipt_id FROM sunbelt_demo.bronze.Bz_Cash_Receipts
  UNION ALL SELECT 'Bz_Customer_Master', 'customer_id', customer_id FROM sunbelt_demo.bronze.Bz_Customer_Master
  UNION ALL SELECT 'Bz_Customer_Master', 'customer_name', customer_name FROM sunbelt_demo.bronze.Bz_Customer_Master
  UNION ALL SELECT 'Bz_Branch_Employee', 'employee_id', employee_id FROM sunbelt_demo.bronze.Bz_Branch_Employee
  UNION ALL SELECT 'Bz_Branch_Employee', 'employee_name', employee_name FROM sunbelt_demo.bronze.Bz_Branch_Employee
  UNION ALL SELECT 'Bz_Branch_Employee', 'region', region FROM sunbelt_demo.bronze.Bz_Branch_Employee
)
SELECT t AS table_name, c AS column_name,
  MIN(length(v)) AS min_len, MAX(length(v)) AS max_len, ROUND(AVG(length(v)),2) AS avg_len,
  count_if(v <> trim(v))   AS leading_trailing_space_cnt,
  count_if(v <> upper(v))  AS not_uppercase_cnt,
  COUNT(DISTINCT regexp_replace(regexp_replace(regexp_replace(v, '[A-Z]', 'A'), '[a-z]', 'a'), '[0-9]', '9')) AS distinct_patterns
FROM s GROUP BY t, c ORDER BY t, c;

-- ID pattern frequency (casing/format variants across source systems)
SELECT 'contract_id' AS id_col, source_system,
       regexp_replace(regexp_replace(regexp_replace(contract_id,'[A-Z]','A'),'[a-z]','a'),'[0-9]','9') AS pattern, COUNT(*) AS freq
FROM sunbelt_demo.bronze.Bz_Rental_Contracts GROUP BY 1,2,3
UNION ALL
SELECT 'invoice_id', source_system,
       regexp_replace(regexp_replace(regexp_replace(invoice_id,'[A-Z]','A'),'[a-z]','a'),'[0-9]','9'), COUNT(*)
FROM sunbelt_demo.bronze.Bz_Invoices GROUP BY 1,2,3
UNION ALL
SELECT 'customer_id', source_system,
       regexp_replace(regexp_replace(regexp_replace(customer_id,'[A-Z]','A'),'[a-z]','a'),'[0-9]','9'), COUNT(*)
FROM sunbelt_demo.bronze.Bz_Customer_Master GROUP BY 1,2,3
ORDER BY id_col, source_system, freq DESC;

-- =====================================================================================
-- SECTION G: DUPLICATES & REFERENTIAL INTEGRITY (logical, not enforced)
-- =====================================================================================
-- G1. Exact duplicate rows (excluding lineage columns)
SELECT 'Bz_Rental_Contracts' AS table_name, COALESCE(SUM(cnt - 1),0) AS exact_dup_rows FROM (
  SELECT COUNT(*) cnt FROM sunbelt_demo.bronze.Bz_Rental_Contracts
  GROUP BY contract_id, customer_id, branch_code, sales_rep_id, equipment_class, contract_start_date, contract_end_date, contract_status, daily_rate, source_system HAVING COUNT(*) > 1)
UNION ALL
SELECT 'Bz_Invoices', COALESCE(SUM(cnt - 1),0) FROM (
  SELECT COUNT(*) cnt FROM sunbelt_demo.bronze.Bz_Invoices
  GROUP BY invoice_id, contract_id, customer_id, invoice_date, due_date, invoice_amount, tax_amount, invoice_type, currency, source_system HAVING COUNT(*) > 1)
UNION ALL
SELECT 'Bz_Cash_Receipts', COALESCE(SUM(cnt - 1),0) FROM (
  SELECT COUNT(*) cnt FROM sunbelt_demo.bronze.Bz_Cash_Receipts
  GROUP BY receipt_id, invoice_id, customer_id, receipt_date, payment_amount, payment_method, source_system HAVING COUNT(*) > 1)
UNION ALL
SELECT 'Bz_Customer_Master', COALESCE(SUM(cnt - 1),0) FROM (
  SELECT COUNT(*) cnt FROM sunbelt_demo.bronze.Bz_Customer_Master
  GROUP BY customer_id, customer_name, credit_terms, credit_limit, customer_since, customer_status, source_system HAVING COUNT(*) > 1)
UNION ALL
SELECT 'Bz_Branch_Employee', COALESCE(SUM(cnt - 1),0) FROM (
  SELECT COUNT(*) cnt FROM sunbelt_demo.bronze.Bz_Branch_Employee
  GROUP BY employee_id, employee_name, role, branch_code, region, collector_id, effective_date, source_system HAVING COUNT(*) > 1);

-- G2. Logical key duplicates (raw and normalized upper/trim)
SELECT 'Bz_Rental_Contracts.contract_id' AS logical_key, COUNT(*) AS dup_keys_raw FROM (SELECT contract_id FROM sunbelt_demo.bronze.Bz_Rental_Contracts WHERE contract_id IS NOT NULL GROUP BY contract_id HAVING COUNT(*) > 1)
UNION ALL SELECT 'Bz_Rental_Contracts.contract_id (normalized)', COUNT(*) FROM (SELECT upper(trim(contract_id)) k FROM sunbelt_demo.bronze.Bz_Rental_Contracts WHERE contract_id IS NOT NULL GROUP BY k HAVING COUNT(*) > 1)
UNION ALL SELECT 'Bz_Invoices.invoice_id', COUNT(*) FROM (SELECT invoice_id FROM sunbelt_demo.bronze.Bz_Invoices WHERE invoice_id IS NOT NULL GROUP BY invoice_id HAVING COUNT(*) > 1)
UNION ALL SELECT 'Bz_Cash_Receipts.receipt_id', COUNT(*) FROM (SELECT receipt_id FROM sunbelt_demo.bronze.Bz_Cash_Receipts WHERE receipt_id IS NOT NULL GROUP BY receipt_id HAVING COUNT(*) > 1)
UNION ALL SELECT 'Bz_Customer_Master.customer_id', COUNT(*) FROM (SELECT customer_id FROM sunbelt_demo.bronze.Bz_Customer_Master WHERE customer_id IS NOT NULL GROUP BY customer_id HAVING COUNT(*) > 1)
UNION ALL SELECT 'Bz_Customer_Master.customer_name (same entity, multiple IDs)', COUNT(*) FROM (SELECT upper(trim(customer_name)) k FROM sunbelt_demo.bronze.Bz_Customer_Master WHERE customer_name IS NOT NULL GROUP BY k HAVING COUNT(DISTINCT customer_id) > 1)
UNION ALL SELECT 'Bz_Branch_Employee.employee_id', COUNT(*) FROM (SELECT employee_id FROM sunbelt_demo.bronze.Bz_Branch_Employee WHERE employee_id IS NOT NULL GROUP BY employee_id HAVING COUNT(*) > 1)
UNION ALL SELECT 'Bz_Branch_Employee.employee_id+source_system+effective_date', COUNT(*) FROM (SELECT employee_id, source_system, effective_date FROM sunbelt_demo.bronze.Bz_Branch_Employee GROUP BY 1,2,3 HAVING COUNT(*) > 1);

-- G3. Orphan references (normalized upper/trim match)
SELECT 'invoices.contract_id -> contracts' AS relationship, COUNT(*) AS orphan_rows
FROM sunbelt_demo.bronze.Bz_Invoices i
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(contract_id)) k FROM sunbelt_demo.bronze.Bz_Rental_Contracts) c ON upper(trim(i.contract_id)) = c.k
WHERE i.contract_id IS NOT NULL
UNION ALL
SELECT 'invoices.customer_id -> customer_master', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Invoices i
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(customer_id)) k FROM sunbelt_demo.bronze.Bz_Customer_Master) m ON upper(trim(i.customer_id)) = m.k
WHERE i.customer_id IS NOT NULL
UNION ALL
SELECT 'contracts.customer_id -> customer_master', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Rental_Contracts r
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(customer_id)) k FROM sunbelt_demo.bronze.Bz_Customer_Master) m ON upper(trim(r.customer_id)) = m.k
WHERE r.customer_id IS NOT NULL
UNION ALL
SELECT 'contracts.sales_rep_id -> branch_employee', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Rental_Contracts r
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(employee_id)) k FROM sunbelt_demo.bronze.Bz_Branch_Employee) e ON upper(trim(r.sales_rep_id)) = e.k
WHERE r.sales_rep_id IS NOT NULL
UNION ALL
SELECT 'cash_receipts.invoice_id -> invoices', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Cash_Receipts c
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(invoice_id)) k FROM sunbelt_demo.bronze.Bz_Invoices) i ON upper(trim(c.invoice_id)) = i.k
WHERE c.invoice_id IS NOT NULL
UNION ALL
SELECT 'cash_receipts.customer_id -> customer_master', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Cash_Receipts c
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(customer_id)) k FROM sunbelt_demo.bronze.Bz_Customer_Master) m ON upper(trim(c.customer_id)) = m.k
WHERE c.customer_id IS NOT NULL
UNION ALL
SELECT 'branch_employee.collector_id -> branch_employee', COUNT(*)
FROM sunbelt_demo.bronze.Bz_Branch_Employee b
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(employee_id)) k FROM sunbelt_demo.bronze.Bz_Branch_Employee) e ON upper(trim(b.collector_id)) = e.k
WHERE b.collector_id IS NOT NULL AND trim(b.collector_id) <> '';

-- G4. Orphan invoice samples (top 20) for investigation
SELECT i.invoice_id, i.contract_id, i.customer_id, i.source_system, i.file_path
FROM sunbelt_demo.bronze.Bz_Invoices i
LEFT ANTI JOIN (SELECT DISTINCT upper(trim(contract_id)) k FROM sunbelt_demo.bronze.Bz_Rental_Contracts) c ON upper(trim(i.contract_id)) = c.k
WHERE i.contract_id IS NOT NULL
LIMIT 20;

-- G5. Unapplied cash summary
SELECT CASE WHEN invoice_id IS NULL OR trim(invoice_id) = '' THEN 'UNAPPLIED' ELSE 'APPLIED' END AS match_status,
       COUNT(*) AS receipts, SUM(payment_amount) AS total_amount
FROM sunbelt_demo.bronze.Bz_Cash_Receipts GROUP BY 1;

-- END OF FILE (read-only profiling; NOT EXECUTED by the agent)
