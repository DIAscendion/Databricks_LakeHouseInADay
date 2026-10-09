-- =============================================================================
-- Rental Revenue-to-Cash (Order-to-Cash / AR) — Bronze Layer Schema
-- Subject area: rental contracts -> invoicing -> cash application -> AR aging/collections
-- Companion to: rental_revenue_to_cash_medallion_architecture (demo deck)
--
-- All five tables below are NEW for this demo — no Bronze exists today.
-- Source feeds currently land as flat exports from branch/legacy systems
-- (LEGACY_SE, LEGACY_MW, SUNBELT_CORE) and a lockbox cash feed, with no
-- conformed landing zone.
--
-- Convention: raw-but-typed, append-only, one row per source record as
-- extracted. Columns are typed to their native source type (not strings)
-- because these are structured batch/CDC extracts, not event streams —
-- unlike Kafka-sourced event tables elsewhere in the enterprise. Known
-- source-system data quality issues (duplicates, nulls, inconsistent ID
-- casing/formats, orphan references) are intentionally NOT cleaned here;
-- that is Silver's job. Every table carries ingestion lineage columns.
-- Naming convention for this demo: catalog.schema.table as
-- sunbelt_demo.bronze.bronze_<table_name>, with Silver counterparts at
-- sunbelt_demo.silver.silver_<table_name> — adjust to the enterprise
-- <env>_ent_bronze_db.finance.<table> pattern when productionized.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Rental contract header
-- Grain: one row per rental contract.
-- Source: branch/legacy rental systems (LEGACY_SE, LEGACY_MW, SUNBELT_CORE),
--         daily batch extract.
-- Known issues: inconsistent contract_id casing/format, duplicate rows,
--         missing sales_rep_id, missing/sentinel contract_end_date,
--         mixed date formats, occasional missing customer_id.
-- Feeds Silver: sunbelt_demo.silver.silver_rental_contracts
-- ---------------------------------------------------------------------------
CREATE TABLE sunbelt_demo.bronze.bronze_rental_contracts (
  contract_id             STRING,     -- raw contract identifier, format varies by source system
  customer_id             STRING,     -- FK to bronze_customer_master, not enforced; can be null
  branch_code             STRING,     -- raw branch code as recorded
  sales_rep_id            STRING,     -- FK to bronze_branch_employee, not enforced; can be null
  equipment_class         STRING,     -- free-text equipment category as recorded
  contract_start_date     STRING,     -- raw date as received (format varies: ISO or MM/DD/YYYY)
  contract_end_date       STRING,     -- raw date as received; blank or sentinel for open contracts
  contract_status         STRING,     -- raw status text (e.g. Open, Closed)
  daily_rate              DECIMAL(10,2), -- raw daily rate
  source_system           STRING,     -- originating system identifier
  file_path                STRING,    -- source file/batch reference
  file_modification_time   TIMESTAMP  -- ingestion file write time
)
USING DELTA;


-- ---------------------------------------------------------------------------
-- Invoice header
-- Grain: one row per invoice or credit memo.
-- Source: branch/legacy billing systems, daily batch extract.
-- Known issues: orphan contract_id (no matching contract), lowercase/
--         unformatted contract_id, mixed date formats, missing due_date,
--         negative amounts for credit memos (expected, not an error).
-- Feeds Silver: sunbelt_demo.silver.silver_invoices
-- ---------------------------------------------------------------------------
CREATE TABLE sunbelt_demo.bronze.bronze_invoices (
  invoice_id               STRING,     -- raw invoice identifier
  contract_id              STRING,     -- raw reference to contract; not validated at Bronze
  customer_id               STRING,    -- raw customer identifier
  invoice_date              STRING,    -- raw date as received (format varies)
  due_date                  STRING,    -- raw date as received; can be null
  invoice_amount             DECIMAL(12,2), -- raw invoice amount (negative = credit memo)
  tax_amount                 DECIMAL(12,2), -- raw tax amount
  invoice_type                STRING,  -- Standard, Credit Memo, etc.
  currency                    STRING,  -- ISO currency code
  source_system                STRING, -- originating system identifier
  file_path                     STRING, -- source file/batch reference
  file_modification_time         TIMESTAMP -- ingestion file write time
)
USING DELTA;


-- ---------------------------------------------------------------------------
-- Cash receipt / payment application
-- Grain: one row per payment (or payment attempt) received.
-- Source: AR lockbox feed (LOCKBOX_FEED), daily batch extract.
-- Known issues: duplicate payment rows, missing receipt_date, missing
--         customer_id, missing invoice_id (unapplied cash).
-- Feeds Silver: sunbelt_demo.silver.silver_cash_receipts
-- ---------------------------------------------------------------------------
CREATE TABLE sunbelt_demo.bronze.bronze_cash_receipts (
  receipt_id               STRING,     -- raw receipt identifier
  invoice_id                STRING,    -- raw reference to invoice; can be null (unapplied cash)
  customer_id                STRING,   -- raw customer identifier; can be null
  receipt_date                 STRING, -- raw date as received; can be null
  payment_amount                 DECIMAL(12,2), -- raw payment amount
  payment_method                   STRING, -- ACH, Check, Credit Card, Wire
  source_system                      STRING, -- originating system identifier
  file_path                            STRING, -- source file/batch reference
  file_modification_time                 TIMESTAMP -- ingestion file write time
)
USING DELTA;


-- ---------------------------------------------------------------------------
-- Customer master
-- Grain: one row per customer record as extracted (not yet deduplicated;
--         the same legal customer may appear under more than one ID).
-- Source: CRM/ERP customer master, daily batch extract.
-- Known issues: duplicate customer records under separate IDs, occasional
--         missing customer_name.
-- Feeds Silver: sunbelt_demo.silver.silver_customer_dim (SCD Type 2)
-- ---------------------------------------------------------------------------
CREATE TABLE sunbelt_demo.bronze.bronze_customer_master (
  customer_id              STRING,     -- raw customer identifier
  customer_name              STRING,   -- raw customer legal/trade name; can be null
  credit_terms                 STRING, -- raw credit terms text (e.g. Net 30)
  credit_limit                   DECIMAL(12,2), -- raw credit limit
  customer_since                   STRING, -- raw date as received
  customer_status                    STRING, -- Active, Suspended, etc.
  source_system                        STRING, -- originating system identifier
  file_path                              STRING, -- source file/batch reference
  file_modification_time                   TIMESTAMP -- ingestion file write time
)
USING DELTA;


-- ---------------------------------------------------------------------------
-- Branch / employee (sales rep & collector) assignment
-- Grain: one row per employee record per effective feed (not yet
--         conformed; stale/duplicate feed rows may be present).
-- Source: HR feed (current + legacy/stale feed).
-- Known issues: stale duplicate rows from a legacy feed with inconsistent
--         region spelling/effective dates for the same employee.
-- Feeds Silver: sunbelt_demo.silver.silver_branch_sales_rep_dim (SCD Type 2)
-- ---------------------------------------------------------------------------
CREATE TABLE sunbelt_demo.bronze.bronze_branch_employee (
  employee_id              STRING,     -- raw employee identifier (sales rep or collector)
  employee_name              STRING,   -- raw employee name
  role                          STRING, -- Sales Rep, Collector
  branch_code                     STRING, -- raw branch code
  region                             STRING, -- raw region text (spelling varies by feed)
  collector_id                        STRING, -- raw collector assignment for a sales rep; blank for collectors
  effective_date                        STRING, -- raw date as received
  source_system                           STRING, -- originating system identifier (HR_FEED vs HR_FEED_OLD)
  file_path                                 STRING, -- source file/batch reference
  file_modification_time                      TIMESTAMP -- ingestion file write time
)
USING DELTA;
