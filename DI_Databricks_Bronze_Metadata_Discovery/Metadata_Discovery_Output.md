_____________________________________________
## *Author*: AAVA
## *Created on*: 2026-10-23
## *Description*: Databricks Bronze layer metadata discovery and DDL recommendation for Rental Revenue-to-Cash Reports
## *Version*: 1
## *Updated on*: 2026-10-23
## *Conceptual File*: DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md
## *Source Metadata Evidence*: Input/rental_revenue_to_cash_bronze_schema.sql, Input/bronze_sample_data.md
## *Repository*: DIAscendion/Databricks_LakeHouseInADay (branch: main)
## *Do_You_Need_Any_Changes*: No (initial version — no prior discovery file existed)
_____________________________________________

## 1. Conceptual Analysis

**Domain:** Rental Revenue-to-Cash reporting. It covers revenue, billing, accounts receivable (AR) aging, collections, cash application and customer credit risk, rolled up by branch and region.

| # | Conceptual Entity | Type | Key Attributes Required | Bronze Relevance |
|---|---|---|---|---|
| 1 | Region | Dimension | Region Name | Derived from employee feed `region` text |
| 2 | Branch | Dimension | Branch Name, Branch Status | Only `branch_code` exists in source |
| 3 | Date | Dimension | Date, Period, Period Type, Days in Period | Generated in Silver/Gold; no source table needed |
| 4 | Customer | Dimension | Name, Status, Credit Terms, Credit Limit, Customer Since | Customer master |
| 5 | Sales Rep | Dimension | Sales Rep Name | Branch/employee feed (role = Sales Rep) |
| 6 | Collector | Dimension | Collector Name | Branch/employee feed (role = Collector) |
| 7 | Equipment Class | Dimension | Equipment Class Name | Free-text column on contracts |
| 8 | Contract | Transaction | Status, Open Count/Value, Billed Rental Days | Rental contracts |
| 9 | Invoice | Transaction | Invoice/Due Date, Amount, Credit Memo, Gross/Net Billings | Invoices |
| 10 | Cash Receipt | Transaction | Payment Amount/Method/Date, Match Status, Unapplied | Cash receipts |
| 11–14 | Fact Rental Revenue / AR Aging / Cash Application / Credit Risk | Analytical facts | KPIs (DSO, CEI, AR 90+ %, ADR, etc.) | Built in Gold from the Bronze tables listed here; no Bronze table of their own |
| 15 | Organization Hierarchy | Hierarchy | Hierarchy Name, Network Level | No source found |

## 2. Source Metadata Discovery

**How the metadata was found:** No source-system credentials or connection details were provided, so no live connection was made. The metadata comes from the source schema definition and sample extracts committed to the repository's `Input/` folder:
- `Input/rental_revenue_to_cash_bronze_schema.sql`: the documented structure of the source feeds (tables, columns, types)
- `Input/bronze_sample_data.md`: sample rows that show data values and known data quality issues

**Source systems identified:** SUNBELT_CORE, LEGACY_SE, LEGACY_MW (rental, billing and CRM extracts), LOCKBOX_FEED (cash), HR_FEED and HR_FEED_OLD (employees). All of them arrive as daily batch flat-file exports under `/landing/...`.

**Constraints discovered:** The source declares **no** primary keys, foreign keys or NOT NULL constraints. Relationships are logical only and are not enforced. The sample data confirms duplicates, nulls and orphan references, for example invoice INV-500008 pointing to contract RC-999999, which does not exist.

| Source Table | Grain | Columns | Logical Key (not enforced) | Logical Relationships | Known DQ Issues |
|---|---|---|---|---|---|
| bronze_rental_contracts | 1 row per contract record | 12 | contract_id | customer_id → customer_master; sales_rep_id → branch_employee | ID format/casing, exact duplicates, null sales_rep_id/customer_id, blank/9999-12-31 end dates, mixed date formats |
| bronze_invoices | 1 row per invoice or credit memo | 12 | invoice_id | contract_id → rental_contracts; customer_id → customer_master | Orphan contract_id, non-standard IDs, null due_date, mixed date formats; negative amount = credit memo (valid) |
| bronze_cash_receipts | 1 row per payment received | 9 | receipt_id | invoice_id → invoices (null = unapplied); customer_id → customer_master | Duplicates, null receipt_date, null customer_id, null invoice_id |
| bronze_customer_master | 1 row per customer record as extracted | 9 | customer_id | — | Same legal entity under multiple IDs, null name, rerun duplicates |
| bronze_branch_employee | 1 row per employee per feed | 10 | employee_id (+ source_system/effective_date) | collector_id → employee_id; branch_code → branch | Stale legacy-feed duplicates, region spelling variants, mixed date formats |

### 2.1 Column-Level Metadata (as documented in source schema)

**bronze_rental_contracts:** contract_id STRING, customer_id STRING, branch_code STRING, sales_rep_id STRING, equipment_class STRING, contract_start_date STRING, contract_end_date STRING, contract_status STRING, daily_rate DECIMAL(10,2), source_system STRING, file_path STRING, file_modification_time TIMESTAMP

**bronze_invoices:** invoice_id STRING, contract_id STRING, customer_id STRING, invoice_date STRING, due_date STRING, invoice_amount DECIMAL(12,2), tax_amount DECIMAL(12,2), invoice_type STRING, currency STRING, source_system STRING, file_path STRING, file_modification_time TIMESTAMP

**bronze_cash_receipts:** receipt_id STRING, invoice_id STRING, customer_id STRING, receipt_date STRING, payment_amount DECIMAL(12,2), payment_method STRING, source_system STRING, file_path STRING, file_modification_time TIMESTAMP

**bronze_customer_master:** customer_id STRING, customer_name STRING, credit_terms STRING, credit_limit DECIMAL(12,2), customer_since STRING, customer_status STRING, source_system STRING, file_path STRING, file_modification_time TIMESTAMP

**bronze_branch_employee:** employee_id STRING, employee_name STRING, role STRING, branch_code STRING, region STRING, collector_id STRING, effective_date STRING, source_system STRING, file_path STRING, file_modification_time TIMESTAMP

## 3. Recommended Bronze Tables

| # | Recommended Table | Source Table | Status | Rationale |
|---|---|---|---|---|
| 1 | Bz_Rental_Contracts | bronze_rental_contracts | Verified against documented source schema | Supports Contract, Equipment Class, Branch (code) and the Rental Revenue fact (daily_rate, start and end dates for billed days) |
| 2 | Bz_Invoices | bronze_invoices | Verified against documented source schema | Supports Invoice, Gross/Net Billings, Credit Memo (invoice_type and negative amounts), and AR Aging (invoice/due dates) |
| 3 | Bz_Cash_Receipts | bronze_cash_receipts | Verified against documented source schema | Supports Cash Receipt and Cash Application (applied vs. unapplied, where unapplied means a null invoice_id) and Days to Pay |
| 4 | Bz_Customer_Master | bronze_customer_master | Verified against documented source schema | Supports Customer and Credit Risk (credit_limit, status, terms) |
| 5 | Bz_Branch_Employee | bronze_branch_employee | Verified against documented source schema | Supports Sales Rep, Collector and Region (text), plus the collector assignment |
| 6 | Bz_Branch_Master | — | **Recommended — Not Verified in Source System** | Branch Name, Branch Status and the Organization Hierarchy / Network Level need a branch reference feed. No such table or column was found in the evidence, so no DDL is generated |

**Bronze design principles (taken from the source conventions):** Delta tables, append-only, raw but typed, one row per source record, no cleansing or deduplication (that is Silver's job). Every table keeps the lineage columns `source_system`, `file_path` and `file_modification_time`.

## 4. DDL

```sql
-- Catalog/schema follow the source convention: sunbelt_demo.bronze
-- (adjust to <env>_ent_bronze_db.finance when productionized).
-- No PK/FK/NOT NULL constraints are declared because none exist in the source.

CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.Bz_Rental_Contracts (
  contract_id             STRING        COMMENT 'Raw contract identifier; format varies by source system',
  customer_id             STRING        COMMENT 'Raw customer reference; not enforced; can be null',
  branch_code             STRING        COMMENT 'Raw branch code as recorded',
  sales_rep_id            STRING        COMMENT 'Raw sales rep (employee) reference; can be null',
  equipment_class         STRING        COMMENT 'Free-text equipment category',
  contract_start_date     STRING        COMMENT 'Raw date (ISO or MM/DD/YYYY)',
  contract_end_date       STRING        COMMENT 'Raw date; blank or 9999-12-31 for open contracts',
  contract_status         STRING        COMMENT 'Raw status text (Open, Closed)',
  daily_rate              DECIMAL(10,2) COMMENT 'Raw daily rate',
  source_system           STRING        COMMENT 'Originating system identifier',
  file_path               STRING        COMMENT 'Source file/batch reference',
  file_modification_time  TIMESTAMP     COMMENT 'Ingestion file write time'
)
USING DELTA
COMMENT 'Bronze: raw rental contract headers (SUNBELT_CORE, LEGACY_SE, LEGACY_MW)';

CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.Bz_Invoices (
  invoice_id              STRING        COMMENT 'Raw invoice / credit memo identifier',
  contract_id             STRING        COMMENT 'Raw contract reference; not validated',
  customer_id             STRING        COMMENT 'Raw customer identifier',
  invoice_date            STRING        COMMENT 'Raw date (format varies)',
  due_date                STRING        COMMENT 'Raw date; can be null',
  invoice_amount          DECIMAL(12,2) COMMENT 'Raw amount; negative = credit memo',
  tax_amount              DECIMAL(12,2) COMMENT 'Raw tax amount',
  invoice_type            STRING        COMMENT 'Standard, Credit Memo, etc.',
  currency                STRING        COMMENT 'ISO currency code',
  source_system           STRING        COMMENT 'Originating system identifier',
  file_path               STRING        COMMENT 'Source file/batch reference',
  file_modification_time  TIMESTAMP     COMMENT 'Ingestion file write time'
)
USING DELTA
COMMENT 'Bronze: raw invoice and credit memo headers';

CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.Bz_Cash_Receipts (
  receipt_id              STRING        COMMENT 'Raw receipt identifier',
  invoice_id              STRING        COMMENT 'Raw invoice reference; null = unapplied cash',
  customer_id             STRING        COMMENT 'Raw customer identifier; can be null',
  receipt_date            STRING        COMMENT 'Raw date; can be null',
  payment_amount          DECIMAL(12,2) COMMENT 'Raw payment amount',
  payment_method          STRING        COMMENT 'ACH, Check, Credit Card, Wire',
  source_system           STRING        COMMENT 'Originating system identifier',
  file_path               STRING        COMMENT 'Source file/batch reference',
  file_modification_time  TIMESTAMP     COMMENT 'Ingestion file write time'
)
USING DELTA
COMMENT 'Bronze: raw lockbox cash receipts (LOCKBOX_FEED)';

CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.Bz_Customer_Master (
  customer_id             STRING        COMMENT 'Raw customer identifier',
  customer_name           STRING        COMMENT 'Raw legal/trade name; can be null',
  credit_terms            STRING        COMMENT 'Raw credit terms text (e.g. Net 30)',
  credit_limit            DECIMAL(12,2) COMMENT 'Raw credit limit',
  customer_since          STRING        COMMENT 'Raw date',
  customer_status         STRING        COMMENT 'Active, Suspended, etc.',
  source_system           STRING        COMMENT 'Originating system identifier',
  file_path               STRING        COMMENT 'Source file/batch reference',
  file_modification_time  TIMESTAMP     COMMENT 'Ingestion file write time'
)
USING DELTA
COMMENT 'Bronze: raw customer master records (not deduplicated)';

CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.Bz_Branch_Employee (
  employee_id             STRING        COMMENT 'Raw employee identifier (sales rep or collector)',
  employee_name           STRING        COMMENT 'Raw employee name',
  role                    STRING        COMMENT 'Sales Rep, Collector',
  branch_code             STRING        COMMENT 'Raw branch code',
  region                  STRING        COMMENT 'Raw region text; spelling varies by feed',
  collector_id            STRING        COMMENT 'Collector assigned to a sales rep; blank for collectors',
  effective_date          STRING        COMMENT 'Raw date',
  source_system           STRING        COMMENT 'HR_FEED or HR_FEED_OLD',
  file_path               STRING        COMMENT 'Source file/batch reference',
  file_modification_time  TIMESTAMP     COMMENT 'Ingestion file write time'
)
USING DELTA
COMMENT 'Bronze: raw branch employee (sales rep / collector) assignments';
```

## 5. Summary Table

| Bronze Table | Source Table | Source System(s) | Column Count | Verification Status | Conceptual Entities Served |
|---|---|---|---|---|---|
| Bz_Rental_Contracts | bronze_rental_contracts | SUNBELT_CORE, LEGACY_SE, LEGACY_MW | 12 | Verified (documented schema + sample) | Contract, Equipment Class, Branch, Sales Rep (ref), Fact Rental Revenue, Fact Credit Risk |
| Bz_Invoices | bronze_invoices | SUNBELT_CORE, LEGACY_SE, LEGACY_MW | 12 | Verified (documented schema + sample) | Invoice, Fact Rental Revenue, Fact AR Aging, Fact Cash Application |
| Bz_Cash_Receipts | bronze_cash_receipts | LOCKBOX_FEED | 9 | Verified (documented schema + sample) | Cash Receipt, Fact Cash Application |
| Bz_Customer_Master | bronze_customer_master | SUNBELT_CORE, LEGACY_SE | 9 | Verified (documented schema + sample) | Customer, Fact Credit Risk, Fact AR Aging |
| Bz_Branch_Employee | bronze_branch_employee | HR_FEED, HR_FEED_OLD | 10 | Verified (documented schema + sample) | Sales Rep, Collector, Region, Branch |
| Bz_Branch_Master | — | — | — | Recommended — Not Verified in Source System | Branch Name/Status, Organization Hierarchy |

## 6. Mapping Table (Conceptual Attribute → Source)

| Conceptual Entity | Conceptual Attribute | Bronze Table | Source Column(s) | Mapping Type |
|---|---|---|---|---|
| Region | Region Name | Bz_Branch_Employee | region | Direct (needs spelling standardization in Silver) |
| Branch | Branch Name | — | branch_code only | Recommended — Not Verified in Source System |
| Branch | Branch Status | — | — | Recommended — Not Verified in Source System |
| Date | Date / Period / Period Type / Days in Period | — | Generated calendar | Derived (Silver/Gold) |
| Customer | Customer Name | Bz_Customer_Master | customer_name | Direct |
| Customer | Customer Status | Bz_Customer_Master | customer_status | Direct |
| Customer | Credit Terms | Bz_Customer_Master | credit_terms | Direct |
| Customer | Credit Limit | Bz_Customer_Master | credit_limit | Direct |
| Customer | Customer Since Date | Bz_Customer_Master | customer_since | Direct (date parsing in Silver) |
| Sales Rep | Sales Rep Name | Bz_Branch_Employee | employee_name where role='Sales Rep' | Direct (filtered) |
| Collector | Collector Name | Bz_Branch_Employee | employee_name where role='Collector' | Direct (filtered) |
| Collector | Collector Assignment → Customer | Bz_Branch_Employee + Bz_Rental_Contracts | collector_id via sales_rep_id | Derived (indirect: customer → contract → sales rep → collector) |
| Equipment Class | Equipment Class Name | Bz_Rental_Contracts | equipment_class | Direct (free text) |
| Contract | Contract Status | Bz_Rental_Contracts | contract_status | Direct |
| Contract | Open Contract Count / Value | Bz_Rental_Contracts | contract_status, daily_rate, contract dates | Derived |
| Contract | Total Billed Rental Days | Bz_Rental_Contracts | contract_start_date, contract_end_date | Derived |
| Invoice | Invoice Date / Due Date | Bz_Invoices | invoice_date, due_date | Direct (due_date fallback via credit_terms) |
| Invoice | Invoice Amount | Bz_Invoices | invoice_amount (+ tax_amount) | Direct |
| Invoice | Gross Billings / Credit Memo Amount / Net Billings | Bz_Invoices | invoice_amount, invoice_type | Derived |
| Invoice | Invoice Count | Bz_Invoices | invoice_id | Derived |
| Invoice | Days Past Due / Aging Bucket | Bz_Invoices | due_date vs snapshot date | Derived |
| Cash Receipt | Payment Amount / Method / Date | Bz_Cash_Receipts | payment_amount, payment_method, receipt_date | Direct |
| Cash Receipt | Match Status / Unapplied Amount | Bz_Cash_Receipts | invoice_id (null = unapplied) | Derived |
| Cash Receipt | Days to Pay | Bz_Cash_Receipts + Bz_Invoices | receipt_date − invoice_date | Derived |
| Fact Rental Revenue | Rental Revenue, Gross/Net Billings, Credit Memo Rate, ADR, Revenue per Contract, Trend | Bz_Invoices + Bz_Rental_Contracts | invoice_amount, invoice_type, daily_rate, dates | Derived (Gold) |
| Fact AR Aging | Total AR, AR 90+, DSO, Best Possible DSO, DSO Trend, Aging Buckets | Bz_Invoices + Bz_Cash_Receipts | amounts, dates | Derived (Gold) |
| Fact Cash Application | Cash Collected, CEI, Avg Days to Pay, % Paid On Time, Unapplied Cash $/% | Bz_Cash_Receipts + Bz_Invoices | payment_amount, invoice_id, dates | Derived (Gold) |
| Fact Credit Risk | Outstanding AR, Credit Utilization %, Over Limit, Suspended w/ Exposure, AR 90+ by Customer | Bz_Customer_Master + Bz_Invoices + Bz_Cash_Receipts + Bz_Rental_Contracts | credit_limit, customer_status, balances | Derived (Gold) |
| Organization Hierarchy | Hierarchy Name / Network Level | — | — | Recommended — Not Verified in Source System |

## 7. Assumptions / Limitations

1. **No live connection:** No source-system credentials were supplied. Discovery used the source schema definition and sample data in the repository's `Input/` folder. Row counts, real data volumes and any undocumented columns could not be checked.
2. **No constraints:** The source declares no PK, FK or NOT NULL constraints, so none are declared in the Bronze DDL. Logical keys are documented for Silver use only.
3. **Data types kept as-is:** Dates stay `STRING` because the source mixes formats (ISO and MM/DD/YYYY). Parsing happens in Silver.
4. **Branch gaps:** There is no branch master, branch name or status, region-to-branch reference table, or organization hierarchy source. `Bz_Branch_Master` is listed but has no DDL until a source is confirmed.
5. **Collector-to-customer assignment** is only available indirectly, through the sales rep's `collector_id`. A direct assignment feed has not been verified.
6. **Credit memos** are identified by `invoice_type = 'Credit Memo'` and/or a negative `invoice_amount`. These are valid records, not errors.
7. **Naming:** Tables use the required `Bz_` prefix in the source catalog/schema `sunbelt_demo.bronze`. Adjust to the enterprise pattern when productionized.
8. **Optional extra audit columns** (e.g. an ingestion batch ID or load timestamp) are not in the source evidence and were left out of the DDL. Adding them would be Recommended — Not Verified in Source System.

## 8. API Cost

Not Available
