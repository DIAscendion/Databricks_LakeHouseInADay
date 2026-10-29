_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Silver-to-Gold transformation rules for the Dimension tables of the Rental Revenue-to-Cash Reports Databricks medallion model.
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Gold Dimension Transformation Recommender

This document defines the transformation rules that load the nine Gold dimension tables (`gold.go_dim_*`) from the Silver tables (`silver.si_rental_contracts`, `si_invoices`, `si_cash_receipts`, `si_customer_master`, `si_branch_employee`). It is based on the Conceptual model, the Data Constraints, the Silver and Gold physical DDL, and the Bronze sample data. Fact, aggregate, code, error and audit tables are out of scope.

**Inferences used throughout** (the inputs do not state these explicitly):
1. Silver has no branch name or region master. Branch and region attributes come from `silver.si_branch_employee` (`branch_code`, `region`), and branch names are derived.
2. `collector_id` is blank for Collector rows in `si_branch_employee`. For those rows the collector's own `employee_id` is the collector key. Sales Rep rows point to their collector through `collector_id`.
3. Gold `load_date` and `update_date` are `TIMESTAMP`. They are set with `current_timestamp()`. Surrogate keys are deterministic `xxhash64(<business key>)` values, because identity syntax is not allowed.
4. Reporting snapshot date: `${snapshot_date}` is a pipeline parameter, for example `current_date()`.

## 0. Shared Conformance Views (used by several rules)

```sql
-- 0.1 Conformed customer map (resolves duplicate legal entities, e.g. C20002 -> C10002)
CREATE OR REPLACE TEMP VIEW v_customer_map AS
WITH ranked AS (
  SELECT customer_id, customer_name, source_system,
         regexp_replace(lower(trim(customer_name)), '[^a-z0-9]', '') AS name_key,
         ROW_NUMBER() OVER (PARTITION BY customer_id
                            ORDER BY file_modification_time DESC, update_timestamp DESC) AS rn
  FROM silver.si_customer_master
  WHERE customer_name IS NOT NULL
), dedup AS (SELECT * FROM ranked WHERE rn = 1),
canon AS (
  SELECT name_key,
         FIRST(customer_id) OVER (PARTITION BY name_key
              ORDER BY CASE WHEN source_system = 'SUNBELT_CORE' THEN 0 ELSE 1 END, customer_id) AS conformed_customer_id,
         customer_id
  FROM dedup
)
SELECT customer_id, conformed_customer_id FROM canon
UNION ALL
SELECT customer_id, customer_id FROM silver.si_customer_master WHERE customer_name IS NULL;

-- 0.2 Current employee record (latest effective_date wins; legacy HR_FEED_OLD duplicates lose)
CREATE OR REPLACE TEMP VIEW v_employee_current AS
SELECT * FROM (
  SELECT e.*,
         CASE
           WHEN lower(regexp_replace(region, '[^A-Za-z]', '')) = 'southeast' THEN 'Southeast'
           WHEN lower(regexp_replace(region, '[^A-Za-z]', '')) = 'midwest'   THEN 'Midwest'
           ELSE initcap(trim(region)) END AS region_std,
         ROW_NUMBER() OVER (PARTITION BY employee_id
              ORDER BY effective_date DESC, CASE WHEN source_system = 'HR_FEED' THEN 0 ELSE 1 END,
                       file_modification_time DESC) AS rn
  FROM silver.si_branch_employee e
) WHERE rn = 1;

-- 0.3 Contract ID standardization (rc100003 -> RC-100003; MW-100009 kept as-is and flagged)
CREATE OR REPLACE TEMP VIEW v_contract_key AS
SELECT contract_id AS raw_contract_id,
       CASE WHEN upper(trim(contract_id)) RLIKE '^RC-[0-9]{6}$' THEN upper(trim(contract_id))
            WHEN upper(trim(contract_id)) RLIKE '^RC[0-9]{6}$'
                 THEN concat('RC-', substr(upper(trim(contract_id)), 3))
            ELSE upper(trim(contract_id)) END AS contract_id_std
FROM (SELECT contract_id FROM silver.si_rental_contracts
      UNION SELECT contract_id FROM silver.si_invoices);
```

---

## 1. Transformation Rules for Dimension Tables

### 1.1 gold.go_dim_date

#### 1. Calendar Generation: Build the date dimension from the Silver date range
- **Rationale:** Silver has no calendar table. All facts must link to a valid reporting date (Constraints 2.5.7). The range is taken from the Silver business dates so no fact date is left unmatched.
- **SQL Example:**
```sql
CREATE OR REPLACE TEMP VIEW v_cal AS
SELECT explode(sequence(min_d, max_d, interval 1 day)) AS reporting_date
FROM (SELECT least(min(invoice_date), min(due_date)) AS min_d,
             greatest(max(invoice_date), max(due_date), current_date()) AS max_d
      FROM silver.si_invoices);
```
- **Traceability:** Conceptual (Date: Date) / Constraints 2.1.3, 2.5.7 / Silver si_invoices.invoice_date, due_date, si_cash_receipts.receipt_date → go_dim_date.reporting_date

#### 2. Period Derivation (Hierarchy Mapping): Day → Week → Month → Quarter rows
- **Rationale:** Time analysis must support day, week, month and quarter (Constraints 1.3.5). One row per date and period type matches the grain "one row per reporting date/period type". `period_type` is a low-cardinality partition column.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_date
SELECT abs(xxhash64(reporting_date, period_type)) AS dim_date_sk,
       reporting_date, reporting_period, period_type, number_of_days_in_period,
       current_timestamp(), current_timestamp(), 'SILVER'
FROM (
  SELECT reporting_date, date_format(reporting_date,'yyyy-MM-dd') AS reporting_period, 'Day' AS period_type, 1 AS number_of_days_in_period FROM v_cal
  UNION ALL
  SELECT reporting_date, concat(year(reporting_date),'-W',lpad(weekofyear(reporting_date),2,'0')), 'Week', 7 FROM v_cal
  UNION ALL
  SELECT reporting_date, date_format(reporting_date,'yyyy-MM'), 'Month', day(last_day(reporting_date)) FROM v_cal
  UNION ALL
  SELECT reporting_date, concat(year(reporting_date),'-Q',quarter(reporting_date)), 'Quarter',
         datediff(add_months(date_trunc('QUARTER', reporting_date), 3), date_trunc('QUARTER', reporting_date)) FROM v_cal
);
```
- **Traceability:** Conceptual (Date: Period, Period Type, Number of Days in Period) / Constraints 1.3.5, 2.4.1 (DSO needs days in period) → go_dim_date.reporting_period, period_type, number_of_days_in_period

#### 3. Period Type Standardization: Fixed value set
- **Rationale:** Only `Day`, `Week`, `Month`, `Quarter` are allowed, so the date dimension agrees with `go_code_period_type` and the uniqueness rule "Branch, Date, Period Type".
- **SQL Example:**
```sql
SELECT * FROM gold.go_dim_date WHERE period_type NOT IN ('Day','Week','Month','Quarter');  -- must return 0 rows
```
- **Traceability:** Constraints 2.2.1 → go_dim_date.period_type

### 1.2 gold.go_dim_region

#### 4. Region Name Normalization: Collapse spelling variants
- **Rationale:** Sample data holds `South East`, `SouthEast` and `Mid-West` from HR_FEED_OLD. These must collapse to one canonical value so branch rollups are consistent (Constraints 1.4.4).
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_region
SELECT abs(xxhash64(region_name)), region_name, current_timestamp(), current_timestamp(), 'SILVER'
FROM (SELECT DISTINCT region_std AS region_name FROM v_employee_current WHERE region_std IS NOT NULL AND region_std <> '');
```
- **Traceability:** Conceptual (Region: Region Name) / Constraints 2.1.2, 1.4.4 / Silver si_branch_employee.region → go_dim_region.region_name

#### 5. Region Key Uniqueness: One row per region
- **Rationale:** `DISTINCT` on the standardized value gives one row per region, which is the Gold grain. Rows with a null region are excluded because Region is mandatory.
- **SQL Example:**
```sql
SELECT region_name, count(*) FROM gold.go_dim_region GROUP BY region_name HAVING count(*) > 1;  -- must return 0 rows
```
- **Traceability:** Constraints 2.1.2 → go_dim_region.region_name

### 1.3 gold.go_dim_branch

#### 6. Branch Attribute Derivation: Branch from employee and contract assignments
- **Rationale:** Branch is the reporting anchor for all reports. Branch codes come from `si_branch_employee` and `si_rental_contracts`. Branch region is the region of the most recently effective employee assignment. SE02 is an example where employees moved branches.
- **SQL Example:**
```sql
CREATE OR REPLACE TEMP VIEW v_branch_src AS
SELECT branch_code, region_std AS region_name,
       ROW_NUMBER() OVER (PARTITION BY branch_code ORDER BY effective_date DESC) AS rn
FROM v_employee_current WHERE branch_code IS NOT NULL;
```
- **Traceability:** Conceptual (Branch) / Constraints 2.1.1, 2.5.1 / Silver si_branch_employee.branch_code, region → go_dim_branch.branch_code, region_name

#### 7. Branch Name Standardization: Derive a display name
- **Rationale:** Silver has no branch name column, but Branch Name is mandatory (Constraints 2.1.1). The recommended name is `Branch <CODE>`, which can be replaced by a branch master when one exists.
- **SQL Example:**
```sql
concat('Branch ', upper(trim(branch_code))) AS branch_name
```
- **Traceability:** Conceptual (Branch: Branch Name) / Constraints 2.1.1 → go_dim_branch.branch_name

#### 8. Branch Status Derivation: Active when assigned
- **Rationale:** Branch Status shows whether the branch is active for the reporting date (Constraints 1.4.1). A branch with a current contract or employee assignment is `Active`. Otherwise it is `Inactive`.
- **SQL Example:**
```sql
CASE WHEN EXISTS (SELECT 1 FROM silver.si_rental_contracts c WHERE c.branch_code = b.branch_code)
       OR EXISTS (SELECT 1 FROM v_employee_current e WHERE e.branch_code = b.branch_code)
     THEN 'Active' ELSE 'Inactive' END AS branch_status
```
- **Traceability:** Conceptual (Branch: Branch Status) / Constraints 1.4.1 → go_dim_branch.branch_status

#### 9. Organization Hierarchy Mapping: Network → Region → Branch
- **Rationale:** The hierarchy supports drill-down, drill-up and security filtering (Constraints 3.3.4). `network_level` is the top level and `organization_hierarchy_name` is the Region-Branch path.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_branch
SELECT abs(xxhash64(branch_code)), branch_code, branch_name, branch_status, region_name,
       concat(region_name, ' > ', branch_name) AS organization_hierarchy_name,
       'Network' AS network_level,
       current_timestamp(), current_timestamp(), 'SILVER'
FROM v_branch_final WHERE region_name IS NOT NULL;  -- v_branch_final = rules 6-8 combined
```
- **Traceability:** Conceptual (Organization Hierarchy: Hierarchy Name, Network Level) / Constraints 2.5.1, 3.3.4 → go_dim_branch.organization_hierarchy_name, network_level

### 1.4 gold.go_dim_customer

#### 10. Customer Deduplication: Resolve duplicate legal entities
- **Rationale:** Duplicate customers must be resolved before exposure is aggregated (Constraints 1.2.7, 3.1.7, 3.3.3). In the sample, C20002 "Gulf Coast Paving, Inc." duplicates C10002, and C10001 appears twice because of a rerun file. The first step keeps the latest row per `customer_id`. Then `v_customer_map` maps legacy IDs to the conformed ID.
- **SQL Example:**
```sql
CREATE OR REPLACE TEMP VIEW v_customer_latest AS
SELECT m.conformed_customer_id AS customer_id, c.*,
       ROW_NUMBER() OVER (PARTITION BY m.conformed_customer_id
            ORDER BY CASE WHEN c.customer_id = m.conformed_customer_id THEN 0 ELSE 1 END,
                     c.file_modification_time DESC) AS rn
FROM silver.si_customer_master c JOIN v_customer_map m ON c.customer_id = m.customer_id;
```
- **Traceability:** Constraints 1.2.7, 2.5.4, 3.1.7 / Silver si_customer_master.customer_id → go_dim_customer.customer_id

#### 11. Customer Name Standardization: Trim, collapse spaces, mandatory check
- **Rationale:** Customer Name is mandatory (Constraints 2.1.4). C10005 has a NULL name. The rule keeps the record, sets a visible placeholder and flags it for `go_error_data`. This keeps AR and credit exposure for the customer reportable.
- **SQL Example:**
```sql
coalesce(nullif(regexp_replace(trim(customer_name), '\\s+', ' '), ''), 'UNKNOWN CUSTOMER') AS customer_name
```
- **Traceability:** Conceptual (Customer: Customer Name) / Constraints 2.1.4 / Silver si_customer_master.customer_name → go_dim_customer.customer_name

#### 12. Customer Status and Credit Terms Standardization
- **Rationale:** Status must be `Active` or `Suspended` (Constraints 1.3.2). Credit terms are normalized to the form `Net N`, and this also supports the due-date derivation in rule 31.
- **SQL Example:**
```sql
CASE WHEN lower(trim(customer_status)) = 'active' THEN 'Active'
     WHEN lower(trim(customer_status)) = 'suspended' THEN 'Suspended'
     ELSE 'Unknown' END AS customer_status,
concat('Net ', regexp_extract(credit_terms, '(\\d+)', 1)) AS credit_terms
```
- **Traceability:** Conceptual (Customer: Customer Status, Credit Terms) / Constraints 1.3.2, 2.1.10 → go_dim_customer.customer_status, credit_terms

#### 13. Credit Limit and Customer Since Type Conversion
- **Rationale:** `credit_limit` is cast to `DECIMAL(18,2)` and must not be negative (Constraints 2.3.5). `customer_since` is renamed `customer_since_date` and holds only a valid DATE, because legacy MM/DD/YYYY values (for example `08/01/2017`) must be parsed in Silver.
- **SQL Example:**
```sql
CASE WHEN credit_limit >= 0 THEN CAST(credit_limit AS DECIMAL(18,2)) END AS credit_limit,
CAST(customer_since AS DATE) AS customer_since_date
```
- **Traceability:** Conceptual (Customer: Credit Limit, Customer Since Date) / Constraints 2.1.9, 2.3.5 / Silver si_customer_master.credit_limit, customer_since → go_dim_customer.credit_limit, customer_since_date

#### 14. Collector and Sales Rep Assignment Derivation
- **Rationale:** Silver has no direct customer-to-collector link. The customer's sales rep is taken from the most recent contract. The collector is that rep's `collector_id` (Conceptual: "Collector Assignment → Customer"). Names are looked up from the employee record.
- **SQL Example:**
```sql
CREATE OR REPLACE TEMP VIEW v_cust_assign AS
SELECT m.conformed_customer_id AS customer_id, c.sales_rep_id, c.branch_code,
       ROW_NUMBER() OVER (PARTITION BY m.conformed_customer_id ORDER BY c.contract_start_date DESC) AS rn
FROM silver.si_rental_contracts c JOIN v_customer_map m ON c.customer_id = m.customer_id
WHERE c.sales_rep_id IS NOT NULL;
-- join: sales rep -> v_employee_current (employee_id = sales_rep_id) -> collector (employee_id = collector_id)
```
- **Traceability:** Conceptual (Collector → Customer, Sales Rep) / Silver si_rental_contracts.sales_rep_id, si_branch_employee.collector_id → go_dim_customer.sales_rep_id, sales_rep_name, collector_id, collector_name

#### 15. Branch and Region Denormalization on Customer
- **Rationale:** `branch_code` comes from the assignment in rule 14. `branch_name` and `region_name` are looked up in `go_dim_branch`, so every report uses the same rollup (Constraints 1.4.4).
- **SQL Example:**
```sql
LEFT JOIN gold.go_dim_branch b ON b.branch_code = a.branch_code  -- yields branch_name, region_name
```
- **Traceability:** Constraints 1.4.4, 3.3.2 / Silver si_rental_contracts.branch_code → go_dim_customer.branch_code, branch_name, region_name

#### 16. Over-Limit Indicator Derivation (update DDL column)
- **Rationale:** Credit risk reporting must identify customers exceeding their limit (Constraints 3.2.5). Utilization is computed only when the denominator is non-zero (Constraints 3.2.7). Outstanding AR is the sum of invoice totals less receipts, on the conformed customer.
- **SQL Example:**
```sql
CASE WHEN credit_limit > 0 AND outstanding_ar > credit_limit THEN 'Y' ELSE 'N' END AS over_limit_indicator
-- outstanding_ar = SUM(invoice_amount + tax_amount) - SUM(payment_amount), per conformed customer_id
```
- **Traceability:** Conceptual (Fact Credit Risk: Customers Over Limit) / Constraints 2.4.9, 3.2.5, 3.2.7 → go_dim_customer.over_limit_indicator

#### 17. Customer Dimension Load
- **Rationale:** Final assembly of the Customer dimension. The surrogate key is deterministic.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_customer (dim_customer_sk, customer_id, customer_name, customer_status, credit_terms,
  credit_limit, customer_since_date, collector_id, collector_name, sales_rep_id, sales_rep_name,
  branch_code, branch_name, region_name, load_date, update_date, source_system, over_limit_indicator)
SELECT abs(xxhash64(customer_id)), customer_id, customer_name, customer_status, credit_terms, credit_limit,
       customer_since_date, collector_id, collector_name, sales_rep_id, sales_rep_name,
       branch_code, branch_name, region_name, current_timestamp(), current_timestamp(), source_system, over_limit_indicator
FROM v_customer_final;   -- v_customer_final = rules 10-16 combined, filtered to rn = 1
```
- **Traceability:** Silver si_customer_master → go_dim_customer (all columns)

### 1.5 gold.go_dim_sales_rep

#### 18. Sales Rep Selection and Deduplication
- **Rationale:** Only `role = 'Sales Rep'` rows apply. Legacy duplicates (E2001, E2002, E2003 from HR_FEED_OLD) are removed by `v_employee_current`, which keeps the latest `effective_date`. For E2002 the current branch is SE02.
- **SQL Example:**
```sql
SELECT employee_id AS sales_rep_id, trim(employee_name) AS sales_rep_name, branch_code, region_std AS region_name
FROM v_employee_current WHERE lower(trim(role)) = 'sales rep';
```
- **Traceability:** Conceptual (Sales Rep: Sales Rep Name) / Silver si_branch_employee.employee_id, employee_name, role → go_dim_sales_rep.sales_rep_id, sales_rep_name

#### 19. Sales Rep Branch Hierarchy Mapping
- **Rationale:** Branch name and region come from `go_dim_branch`, so the Sales Rep → Branch → Region hierarchy is the same as in the other dimensions.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_sales_rep
SELECT abs(xxhash64(s.sales_rep_id)), s.sales_rep_id, s.sales_rep_name, s.branch_code,
       b.branch_name, coalesce(b.region_name, s.region_name),
       current_timestamp(), current_timestamp(), 'SILVER'
FROM v_sales_rep s LEFT JOIN gold.go_dim_branch b ON b.branch_code = s.branch_code;
```
- **Traceability:** Conceptual (Sales Rep → Branch, Many-to-One) / Constraints 2.1.3 → go_dim_sales_rep.branch_code, branch_name, region_name

### 1.6 gold.go_dim_collector

#### 20. Collector Key Derivation
- **Rationale:** Collector rows in Silver have a blank `collector_id`. Sales Rep rows reference collectors through that column (E1001, E1002), so the collector key is the collector's `employee_id`. This keeps joins from the customer dimension and the AR/cash facts consistent.
- **SQL Example:**
```sql
SELECT employee_id AS collector_id, trim(employee_name) AS collector_name, branch_code, region_std AS region_name
FROM v_employee_current WHERE lower(trim(role)) = 'collector';
```
- **Traceability:** Conceptual (Collector: Collector Name) / Silver si_branch_employee.employee_id, collector_id, role → go_dim_collector.collector_id, collector_name

#### 21. Collector Branch Hierarchy Mapping
- **Rationale:** Same approach as rule 19.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_collector
SELECT abs(xxhash64(c.collector_id)), c.collector_id, c.collector_name, c.branch_code,
       b.branch_name, coalesce(b.region_name, c.region_name), current_timestamp(), current_timestamp(), 'SILVER'
FROM v_collector c LEFT JOIN gold.go_dim_branch b ON b.branch_code = c.branch_code;
```
- **Traceability:** Conceptual (Collector → Branch, Many-to-One) → go_dim_collector.branch_code, branch_name, region_name

### 1.7 gold.go_dim_equipment_class

#### 22. Equipment Class Standardization
- **Rationale:** Silver has only the free-text `equipment_class`. The code is an upper-case, underscore-separated form of the value and the name is the title-case form. For example, `Generator 20kW` gives `GENERATOR_20KW` and `Generator 20kw`.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_equipment_class
SELECT abs(xxhash64(code)), code, name, current_timestamp(), current_timestamp(), 'SILVER'
FROM (
  SELECT DISTINCT regexp_replace(upper(trim(equipment_class)), '[^A-Z0-9]+', '_') AS code,
                  initcap(regexp_replace(trim(equipment_class), '\\s+', ' ')) AS name
  FROM silver.si_rental_contracts
  WHERE equipment_class IS NOT NULL AND trim(equipment_class) <> ''
);
```
- **Traceability:** Conceptual (Equipment Class: Equipment Class Name) / Constraints 2.1.5 / Silver si_rental_contracts.equipment_class → go_dim_equipment_class.equipment_class_code, equipment_class_name

### 1.8 gold.go_dim_contract

#### 23. Contract ID Standardization and Deduplication
- **Rationale:** `rc100003` is converted to `RC-100003`. `MW-100009` does not match the format but is kept and flagged. RC-100005 is an exact duplicate, so one row is kept per standardized `contract_id`.
- **SQL Example:**
```sql
CREATE OR REPLACE TEMP VIEW v_contract_latest AS
SELECT k.contract_id_std AS contract_id, c.*,
       ROW_NUMBER() OVER (PARTITION BY k.contract_id_std ORDER BY c.file_modification_time DESC, c.update_timestamp DESC) AS rn
FROM silver.si_rental_contracts c JOIN v_contract_key k ON k.raw_contract_id = c.contract_id;
```
- **Traceability:** Constraints 2.5.2 / Silver si_rental_contracts.contract_id → go_dim_contract.contract_id

#### 24. Customer Conformance on Contract
- **Rationale:** `customer_id` is mapped to the conformed customer, so C20002 becomes C10002 (Constraints 2.5.4). A contract with a NULL customer (RC-100006) takes the customer from its invoices, which is the sample's stated recovery path (INV-500006). Any contract still without a customer is flagged for `go_error_data` (Constraints 2.5.5).
- **SQL Example:**
```sql
coalesce(m.conformed_customer_id, inv_cust.customer_id) AS customer_id,
cu.customer_name
-- m: v_customer_map; inv_cust: most frequent si_invoices.customer_id per contract; cu: gold.go_dim_customer
```
- **Traceability:** Constraints 2.5.4, 2.5.5 / Silver si_rental_contracts.customer_id → go_dim_contract.customer_id, customer_name

#### 25. Contract Status and Date Standardization (Type Conversion)
- **Rationale:** Status must be `Open` or `Closed` (Constraints 1.3.3). Open contracts that carry a blank end date or the `9999-12-31` sentinel are set to NULL, so the sentinel is not used in duration calculations. Silver already holds DATE types, and legacy MM/DD/YYYY strings must already be parsed there.
- **SQL Example:**
```sql
CASE WHEN lower(trim(contract_status)) = 'open' THEN 'Open'
     WHEN lower(trim(contract_status)) = 'closed' THEN 'Closed' END AS contract_status,
CAST(contract_start_date AS DATE) AS contract_start_date,
CASE WHEN contract_end_date IS NULL OR contract_end_date = DATE'9999-12-31' THEN NULL
     ELSE contract_end_date END AS contract_end_date,
CAST(daily_rate AS DECIMAL(18,2)) AS daily_rate
```
- **Traceability:** Conceptual (Contract: Contract Status) / Constraints 1.3.3, 2.1.5 / Silver si_rental_contracts.contract_status, contract_start_date, contract_end_date, daily_rate → go_dim_contract (same-named columns)

#### 26. Sales Rep, Branch and Equipment Denormalization
- **Rationale:** Contract context (branch name, region, sales rep name, equipment class name) comes from the conformed dimensions. A NULL sales rep (RC-100003) stays NULL and is flagged. It is not defaulted.
- **SQL Example:**
```sql
LEFT JOIN gold.go_dim_branch b          ON b.branch_code = c.branch_code
LEFT JOIN gold.go_dim_sales_rep sr      ON sr.sales_rep_id = c.sales_rep_id
LEFT JOIN gold.go_dim_equipment_class e ON e.equipment_class_name = initcap(regexp_replace(trim(c.equipment_class), '\\s+', ' '))
-- selects: b.branch_name, b.region_name, sr.sales_rep_name, c.equipment_class, e.equipment_class_name
```
- **Traceability:** Conceptual (Branch/Sales Rep/Equipment Class → Contract) / Silver si_rental_contracts.branch_code, sales_rep_id, equipment_class → go_dim_contract.branch_name, region_name, sales_rep_name, equipment_class_name

#### 27. Open Contract Count and Value Derivation
- **Rationale:** Open-exposure measures are required for credit risk (Constraints 2.4.10). The count is 1 for an Open contract and 0 otherwise, so it can be summed by customer. The value is the net billed amount (excluding tax) of standard and credit-memo invoices on the contract. This is an inference, because the inputs do not define contract value.
- **SQL Example:**
```sql
CASE WHEN contract_status = 'Open' THEN 1 ELSE 0 END AS open_contract_count,
CASE WHEN contract_status = 'Open' THEN coalesce(bill.net_billed, 0) ELSE 0 END AS open_contract_value
-- bill: SELECT contract_id_std, SUM(invoice_amount) AS net_billed FROM silver.si_invoices i JOIN v_contract_key k ... GROUP BY 1
```
- **Traceability:** Conceptual (Contract: Open Contract Count, Open Contract Value) / Constraints 2.4.10 → go_dim_contract.open_contract_count, open_contract_value

#### 28. Total Billed Rental Days Derivation
- **Rationale:** ADR depends on billed rental days (Constraints 2.4.4). Billed days are `invoice_amount / daily_rate` for standard invoices, which matches the sample ("daily_rate × billed days"). The result is NULL when `daily_rate` is zero, to avoid divide-by-zero (Constraints 3.2.7). Cancelled and zero-duration contracts are left out of ADR later in the facts (Constraints 3.1.4).
- **SQL Example:**
```sql
CAST(round(SUM(CASE WHEN i.invoice_type = 'Standard' AND c.daily_rate > 0
                    THEN i.invoice_amount / c.daily_rate END)) AS INT) AS total_billed_rental_days
```
- **Traceability:** Conceptual (Contract: Total Billed Rental Days) / Constraints 2.4.4, 3.1.4, 3.2.7 → go_dim_contract.total_billed_rental_days

#### 29. Contract Dimension Load
- **Rationale:** Final assembly. Contracts with a non-conforming ID format (`MW-100009`) load with `source_system` unchanged and are listed in `go_error_data`.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_contract
SELECT abs(xxhash64(contract_id)), contract_id, customer_id, customer_name, branch_code, branch_name, region_name,
       sales_rep_id, sales_rep_name, equipment_class, equipment_class_name, contract_start_date, contract_end_date,
       contract_status, daily_rate, open_contract_count, open_contract_value, total_billed_rental_days,
       current_timestamp(), current_timestamp(), source_system
FROM v_contract_final WHERE rn = 1;   -- rules 23-28 combined
```
- **Traceability:** Silver si_rental_contracts → go_dim_contract (all columns)

### 1.9 gold.go_dim_invoice

#### 30. Invoice Conformance: Customer, Contract and Date Standardization
- **Rationale:** Invoice customers are mapped to conformed customers and contract IDs to standard IDs (INV-500003 `rc100003` → `RC-100003`, C20002 → C10002). The orphan contract RC-999999 (INV-500008) is kept and flagged (Constraints 2.5.2). Credit memos keep their negative amounts and are not treated as errors (Constraints 2.3.2). Standard amounts must be non-negative (Constraints 2.3.3).
- **SQL Example:**
```sql
SELECT i.invoice_id, k.contract_id_std AS contract_id, m.conformed_customer_id AS customer_id,
       cu.customer_name, i.invoice_date, i.due_date,
       CAST(i.invoice_amount AS DECIMAL(18,2)) AS invoice_amount,
       CAST(i.tax_amount AS DECIMAL(18,2)) AS tax_amount,
       CASE WHEN lower(trim(i.invoice_type)) = 'credit memo' THEN 'Credit Memo' ELSE 'Standard' END AS invoice_type,
       upper(trim(i.currency)) AS currency
FROM silver.si_invoices i
LEFT JOIN v_contract_key k ON k.raw_contract_id = i.contract_id
LEFT JOIN v_customer_map m ON m.customer_id = i.customer_id
LEFT JOIN gold.go_dim_customer cu ON cu.customer_id = m.conformed_customer_id;
```
- **Traceability:** Conceptual (Invoice: Invoice Date, Invoice Amount, Due Date) / Constraints 2.1.6, 2.3.2, 2.3.3, 2.5.2, 2.5.3 / Silver si_invoices → go_dim_invoice.invoice_id, contract_id, customer_id, customer_name, invoice_date, due_date, invoice_amount, tax_amount, invoice_type, currency

#### 31. Due Date Derivation from Credit Terms
- **Rationale:** Due Date is mandatory (Constraints 2.1.7). INV-500005 has no due date. It is derived as `invoice_date + N` days from the customer's `Net N` terms. For INV-500005 that gives 2026-08-31 + 60 = 2026-10-30, as in the sample. A credit memo keeps its own due date.
- **SQL Example:**
```sql
coalesce(i.due_date,
         date_add(i.invoice_date, CAST(regexp_extract(cu.credit_terms, '(\\d+)', 1) AS INT))) AS due_date
```
- **Traceability:** Constraints 2.1.7 / Silver si_invoices.due_date, si_customer_master.credit_terms → go_dim_invoice.due_date

#### 32. Open Balance and Match Status Derivation
- **Rationale:** Payment matching must distinguish applied from unapplied (Constraints 1.3.4). Applied payments must not exceed the invoice amount (Constraints 1.2.4). Receipts are de-duplicated on `receipt_id` (RCP-700001 is duplicated), then applied by `invoice_id`. A credit memo is netted against the earliest earlier standard invoice on the same contract, which reproduces the sample (INV-500001 total 14,926.50 less CM 963.00 = 13,963.50). Receipts with no invoice (RCP-700005) are unapplied cash and do not belong in this dimension.
- **SQL Example:**
```sql
WITH rcp AS (
  SELECT invoice_id, SUM(payment_amount) AS paid FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY receipt_id ORDER BY file_modification_time DESC) AS rn
    FROM silver.si_cash_receipts WHERE invoice_id IS NOT NULL) WHERE rn = 1 GROUP BY invoice_id),
bal AS (
  SELECT inv.*, inv.invoice_amount + inv.tax_amount + coalesce(cm.cm_total, 0) AS total_due,
         coalesce(r.paid, 0) AS paid_amount
  FROM v_invoice_conformed inv
  LEFT JOIN v_cm_alloc cm ON cm.target_invoice_id = inv.invoice_id   -- credit memos netted per contract
  LEFT JOIN rcp r ON r.invoice_id = inv.invoice_id)
SELECT *,
  CASE WHEN invoice_type = 'Credit Memo' THEN 'Not Applicable'
       WHEN paid_amount = 0 THEN 'Unapplied'
       WHEN paid_amount < total_due THEN 'Partially Applied'
       ELSE 'Applied' END AS match_status,
  CASE WHEN paid_amount > total_due THEN 1 ELSE 0 END AS overpaid_flag     -- route to go_error_data
FROM bal;
```
- **Traceability:** Conceptual (Cash Receipt: Match Status) / Constraints 1.2.4, 1.3.4, 3.1.5, 3.1.6 / Silver si_cash_receipts.invoice_id, payment_amount, si_invoices.invoice_amount → go_dim_invoice.match_status

#### 33. Days Past Due and Aging Bucket Derivation (Hierarchy Mapping)
- **Rationale:** Aging bucket comes from snapshot date minus due date, mapped to the fixed non-overlapping set (Constraints 3.1.2, 2.3.6). Invoices not yet due, or fully paid, give `days_past_due` of 0 and fall into `0-30`. Fully paid invoices have no outstanding balance, so downstream facts include only invoices with an open balance. Bucket names must match `go_code_aging_bucket.aging_bucket_name`.
- **SQL Example:**
```sql
GREATEST(datediff(DATE'${snapshot_date}', due_date), 0) AS days_past_due,
CASE WHEN GREATEST(datediff(DATE'${snapshot_date}', due_date), 0) <= 30 THEN '0-30'
     WHEN GREATEST(datediff(DATE'${snapshot_date}', due_date), 0) <= 60 THEN '31-60'
     WHEN GREATEST(datediff(DATE'${snapshot_date}', due_date), 0) <= 90 THEN '61-90'
     ELSE '90+' END AS aging_bucket
```
- **Traceability:** Conceptual (Invoice: Days Past Due, Aging Bucket) / Constraints 1.3.1, 2.3.6, 3.1.2 / Silver si_invoices.due_date → go_dim_invoice.days_past_due, aging_bucket

#### 34. Invoice Status Derivation (update DDL column)
- **Rationale:** Gives a simple lifecycle value for filtering. `Credit Memo` marks adjustments, `Paid` means the balance is zero, and `Open` means a balance remains.
- **SQL Example:**
```sql
CASE WHEN invoice_type = 'Credit Memo' THEN 'Credit Memo'
     WHEN total_due - paid_amount <= 0 THEN 'Paid'
     ELSE 'Open' END AS invoice_status
```
- **Traceability:** Constraints 3.1.5 / Silver si_invoices.invoice_type → go_dim_invoice.invoice_status

#### 35. Contract Status Denormalization and Invoice Dimension Load
- **Rationale:** `contract_status` is taken from `go_dim_contract`, so invoices on contracts that are Open or Closed can be filtered consistently (Constraints 2.1.5). For an orphan contract the status stays NULL and the record is flagged.
- **SQL Example:**
```sql
INSERT OVERWRITE gold.go_dim_invoice (dim_invoice_sk, invoice_id, contract_id, customer_id, customer_name, invoice_date,
  due_date, invoice_amount, tax_amount, invoice_type, currency, aging_bucket, days_past_due, match_status,
  contract_status, load_date, update_date, source_system, invoice_status)
SELECT abs(xxhash64(b.invoice_id)), b.invoice_id, b.contract_id, b.customer_id, b.customer_name, b.invoice_date,
       b.due_date, b.invoice_amount, b.tax_amount, b.invoice_type, b.currency, b.aging_bucket, b.days_past_due,
       b.match_status, c.contract_status, current_timestamp(), current_timestamp(), b.source_system, b.invoice_status
FROM v_invoice_final b LEFT JOIN gold.go_dim_contract c ON c.contract_id = b.contract_id;
```
- **Traceability:** Silver si_invoices → go_dim_invoice (all columns)

---

## 2. Traceability Summary

| Rule Name | Source (Conceptual / Constraints / Silver Table.Column) | Target (Gold Table.Column) | Category |
|---|---|---|---|
| 1. Calendar Generation | Conceptual Date / Constraints 2.5.7 / si_invoices.invoice_date, due_date | go_dim_date.reporting_date | Column Derivation |
| 2. Period Derivation | Conceptual Date Period / Constraints 1.3.5 | go_dim_date.reporting_period, period_type, number_of_days_in_period | Hierarchy Mapping |
| 3. Period Type Standardization | Constraints 2.2.1 | go_dim_date.period_type | Normalization and Standardization |
| 4. Region Name Normalization | Constraints 1.4.4 / si_branch_employee.region | go_dim_region.region_name | Normalization and Standardization |
| 5. Region Key Uniqueness | Constraints 2.1.2 | go_dim_region.region_name, dim_region_sk | Normalization and Standardization |
| 6. Branch Attribute Derivation | Constraints 2.1.1 / si_branch_employee.branch_code, region | go_dim_branch.branch_code, region_name | Column Derivation |
| 7. Branch Name Standardization | Constraints 2.1.1 | go_dim_branch.branch_name | Column Derivation |
| 8. Branch Status Derivation | Constraints 1.4.1 | go_dim_branch.branch_status | Column Derivation |
| 9. Organization Hierarchy Mapping | Conceptual Organization Hierarchy / Constraints 3.3.4 | go_dim_branch.organization_hierarchy_name, network_level | Hierarchy Mapping |
| 10. Customer Deduplication | Constraints 1.2.7, 3.1.7 / si_customer_master.customer_id | go_dim_customer.customer_id | Normalization and Standardization |
| 11. Customer Name Standardization | Constraints 2.1.4 / si_customer_master.customer_name | go_dim_customer.customer_name | Normalization and Standardization |
| 12. Customer Status and Credit Terms Standardization | Constraints 1.3.2 / si_customer_master.customer_status, credit_terms | go_dim_customer.customer_status, credit_terms | Normalization and Standardization |
| 13. Credit Limit and Customer Since Conversion | Constraints 2.3.5 / si_customer_master.credit_limit, customer_since | go_dim_customer.credit_limit, customer_since_date | Data Type Conversion |
| 14. Collector and Sales Rep Assignment | Conceptual Collector Assignment / si_rental_contracts.sales_rep_id, si_branch_employee.collector_id | go_dim_customer.sales_rep_id, sales_rep_name, collector_id, collector_name | Hierarchy Mapping |
| 15. Branch and Region Denormalization (Customer) | Constraints 1.4.4 | go_dim_customer.branch_code, branch_name, region_name | Hierarchy Mapping |
| 16. Over-Limit Indicator | Constraints 2.4.9, 3.2.5 | go_dim_customer.over_limit_indicator | Column Derivation |
| 17. Customer Dimension Load | si_customer_master | go_dim_customer (all) | Column Derivation |
| 18. Sales Rep Selection and Deduplication | si_branch_employee.employee_id, role | go_dim_sales_rep.sales_rep_id, sales_rep_name | Normalization and Standardization |
| 19. Sales Rep Branch Hierarchy | Conceptual Sales Rep → Branch | go_dim_sales_rep.branch_code, branch_name, region_name | Hierarchy Mapping |
| 20. Collector Key Derivation | si_branch_employee.employee_id, collector_id | go_dim_collector.collector_id, collector_name | Column Derivation |
| 21. Collector Branch Hierarchy | Conceptual Collector → Branch | go_dim_collector.branch_code, branch_name, region_name | Hierarchy Mapping |
| 22. Equipment Class Standardization | Constraints 2.1.5 / si_rental_contracts.equipment_class | go_dim_equipment_class.equipment_class_code, equipment_class_name | Normalization and Standardization |
| 23. Contract ID Standardization and Deduplication | Constraints 2.5.2 / si_rental_contracts.contract_id | go_dim_contract.contract_id | Normalization and Standardization |
| 24. Customer Conformance on Contract | Constraints 2.5.4, 2.5.5 / si_rental_contracts.customer_id | go_dim_contract.customer_id, customer_name | Normalization and Standardization |
| 25. Contract Status and Date Standardization | Constraints 1.3.3 / si_rental_contracts.contract_status, dates, daily_rate | go_dim_contract.contract_status, contract_start_date, contract_end_date, daily_rate | Data Type Conversion |
| 26. Sales Rep, Branch and Equipment Denormalization | Conceptual relationships / si_rental_contracts.branch_code, sales_rep_id, equipment_class | go_dim_contract.branch_name, region_name, sales_rep_name, equipment_class_name | Hierarchy Mapping |
| 27. Open Contract Count and Value | Constraints 2.4.10 | go_dim_contract.open_contract_count, open_contract_value | Column Derivation |
| 28. Total Billed Rental Days | Constraints 2.4.4 | go_dim_contract.total_billed_rental_days | Column Derivation |
| 29. Contract Dimension Load | si_rental_contracts | go_dim_contract (all) | Column Derivation |
| 30. Invoice Conformance | Constraints 2.3.2, 2.3.3, 2.5.2, 2.5.3 / si_invoices | go_dim_invoice.invoice_id, contract_id, customer_id, customer_name, invoice_date, invoice_amount, tax_amount, invoice_type, currency | Normalization and Standardization |
| 31. Due Date Derivation | Constraints 2.1.7 / si_invoices.due_date, si_customer_master.credit_terms | go_dim_invoice.due_date | Column Derivation |
| 32. Open Balance and Match Status | Constraints 1.2.4, 1.3.4 / si_cash_receipts | go_dim_invoice.match_status | Column Derivation |
| 33. Days Past Due and Aging Bucket | Constraints 2.3.6, 3.1.2 / si_invoices.due_date | go_dim_invoice.days_past_due, aging_bucket | Hierarchy Mapping |
| 34. Invoice Status | Constraints 3.1.5 / si_invoices.invoice_type | go_dim_invoice.invoice_status | Column Derivation |
| 35. Contract Status Denormalization and Invoice Load | Constraints 2.1.5 / si_invoices | go_dim_invoice.contract_status (and all columns) | Hierarchy Mapping |

## 3. API Cost
```
apiCost: 0.0
```
