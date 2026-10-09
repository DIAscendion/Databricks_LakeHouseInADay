# Rental Revenue-to-Cash — Bronze Sample Data

Sample rows for the five `sunbelt_demo.bronze` tables. Rows are linked across tables (same contracts, invoices, customers, reps) and **deliberately include the known source-system data quality issues** listed in the DDL, so Silver has something real to clean.

Legend: `NULL` = null value · `''` = blank string · ⚠️ = intentional DQ issue

---

## 1. `bronze_branch_employee`

| employee_id | employee_name | role | branch_code | region | collector_id | effective_date | source_system | file_path | file_modification_time |
|---|---|---|---|---|---|---|---|---|---|
| E1001 | Priya Raman | Collector | SE01 | Southeast | '' | 2024-01-01 | HR_FEED | /landing/hr/HR_FEED/2026-10-08/employees_20261008.csv | 2026-10-08 01:05:12 |
| E1002 | Marcus Lee | Collector | MW01 | Midwest | '' | 2024-01-01 | HR_FEED | /landing/hr/HR_FEED/2026-10-08/employees_20261008.csv | 2026-10-08 01:05:12 |
| E2001 | John Carter | Sales Rep | SE01 | Southeast | E1001 | 2024-03-15 | HR_FEED | /landing/hr/HR_FEED/2026-10-08/employees_20261008.csv | 2026-10-08 01:05:12 |
| E2002 | Ana Lopez | Sales Rep | SE02 | Southeast | E1001 | 2024-06-01 | HR_FEED | /landing/hr/HR_FEED/2026-10-08/employees_20261008.csv | 2026-10-08 01:05:12 |
| E2003 | David Kim | Sales Rep | MW01 | Midwest | E1002 | 2025-01-10 | HR_FEED | /landing/hr/HR_FEED/2026-10-08/employees_20261008.csv | 2026-10-08 01:05:12 |
| E2004 | Sarah Brooks | Sales Rep | MW02 | Midwest | E1002 | 2025-02-01 | HR_FEED | /landing/hr/HR_FEED/2026-10-08/employees_20261008.csv | 2026-10-08 01:05:12 |
| E2001 ⚠️ | John Carter | Sales Rep | SE01 | South East | E1001 | 03/15/2023 | HR_FEED_OLD | /landing/hr/HR_FEED_OLD/2026-10-08/emp_legacy.csv | 2026-10-08 01:07:44 |
| E2002 ⚠️ | Ana Lopez | Sales Rep | SE01 | SouthEast | E1001 | 01/05/2024 | HR_FEED_OLD | /landing/hr/HR_FEED_OLD/2026-10-08/emp_legacy.csv | 2026-10-08 01:07:44 |
| E2003 ⚠️ | David Kim | Sales Rep | MW01 | Mid-West | E1002 | 2024-11-01 | HR_FEED_OLD | /landing/hr/HR_FEED_OLD/2026-10-08/emp_legacy.csv | 2026-10-08 01:07:44 |

**DQ issues:** stale duplicates from `HR_FEED_OLD` for E2001/E2002/E2003 with region spelling variants (`South East`, `SouthEast`, `Mid-West`) and mixed date formats. E2002's legacy row shows a prior branch (SE01 → SE02), which becomes a genuine SCD2 history row in Silver.

---

## 2. `bronze_customer_master`

| customer_id | customer_name | credit_terms | credit_limit | customer_since | customer_status | source_system | file_path | file_modification_time |
|---|---|---|---|---|---|---|---|---|
| C10001 | Apex Builders LLC | Net 30 | 250000.00 | 2019-04-12 | Active | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008.csv | 2026-10-08 01:20:31 |
| C10002 | Gulf Coast Paving Inc | Net 45 | 500000.00 | 2017-08-01 | Active | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008.csv | 2026-10-08 01:20:31 |
| C10003 | Lakeside Event Rentals | Net 30 | 75000.00 | 2021-02-20 | Active | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008.csv | 2026-10-08 01:20:31 |
| C10004 | Midwest Steel Erectors | Net 60 | 1000000.00 | 2015-11-05 | Active | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008.csv | 2026-10-08 01:20:31 |
| C10005 ⚠️ | NULL | Net 30 | 50000.00 | 2023-07-14 | Active | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008.csv | 2026-10-08 01:20:31 |
| C10006 | Ridgeline Homes | Net 30 | 100000.00 | 2020-09-30 | Suspended | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008.csv | 2026-10-08 01:20:31 |
| C20002 ⚠️ | Gulf Coast Paving, Inc. | Net 45 | 500000.00 | 08/01/2017 | Active | LEGACY_SE | /landing/crm/LEGACY_SE/2026-10-08/cust_extract.csv | 2026-10-08 01:22:09 |
| C10001 ⚠️ | Apex Builders LLC | Net 30 | 250000.00 | 2019-04-12 | Active | SUNBELT_CORE | /landing/crm/SUNBELT_CORE/2026-10-08/customers_20261008_rerun.csv | 2026-10-08 03:45:50 |

**DQ issues:** C20002 is the same legal entity as C10002 under a separate legacy ID (name punctuation differs); C10005 has no name; C10001 appears twice from a rerun file.

---

## 3. `bronze_rental_contracts`

| contract_id | customer_id | branch_code | sales_rep_id | equipment_class | contract_start_date | contract_end_date | contract_status | daily_rate | source_system | file_path | file_modification_time |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RC-100001 | C10001 | SE01 | E2001 | Excavator | 2026-07-01 | 2026-07-31 | Closed | 450.00 | SUNBELT_CORE | /landing/rental/SUNBELT_CORE/2026-10-08/contracts_20261008.csv | 2026-10-08 02:10:03 |
| RC-100002 | C10002 | SE02 | E2002 | Boom Lift | 2026-07-15 | 2026-08-14 | Closed | 325.00 | SUNBELT_CORE | /landing/rental/SUNBELT_CORE/2026-10-08/contracts_20261008.csv | 2026-10-08 02:10:03 |
| rc100003 ⚠️ | C20002 | SE01 | NULL | Skid Steer | 07/20/2026 | 08/19/2026 | Closed | 275.00 | LEGACY_SE | /landing/rental/LEGACY_SE/2026-10-08/rc_extract.csv | 2026-10-08 02:12:41 |
| RC-100004 ⚠️ | C10003 | SE02 | E2002 | Generator 20kW | 2026-08-01 | '' | Open | 180.00 | SUNBELT_CORE | /landing/rental/SUNBELT_CORE/2026-10-08/contracts_20261008.csv | 2026-10-08 02:10:03 |
| RC-100005 ⚠️ | C10004 | MW01 | E2003 | Telehandler | 08/05/2026 | 9999-12-31 | Open | 520.00 | LEGACY_MW | /landing/rental/LEGACY_MW/2026-10-08/mw_contracts.csv | 2026-10-08 02:14:18 |
| RC-100005 ⚠️ | C10004 | MW01 | E2003 | Telehandler | 08/05/2026 | 9999-12-31 | Open | 520.00 | LEGACY_MW | /landing/rental/LEGACY_MW/2026-10-08/mw_contracts.csv | 2026-10-08 02:14:18 |
| RC-100006 ⚠️ | NULL | MW02 | E2004 | Scissor Lift | 2026-08-10 | 2026-09-09 | Closed | 150.00 | LEGACY_MW | /landing/rental/LEGACY_MW/2026-10-08/mw_contracts.csv | 2026-10-08 02:14:18 |
| RC-100007 | C10005 | MW02 | E2004 | Light Tower | 2026-08-20 | 2026-09-19 | Closed | 95.00 | SUNBELT_CORE | /landing/rental/SUNBELT_CORE/2026-10-08/contracts_20261008.csv | 2026-10-08 02:10:03 |
| RC-100008 ⚠️ | C10006 | SE01 | E2001 | Mini Excavator | 2026-09-01 | '' | Open | 300.00 | SUNBELT_CORE | /landing/rental/SUNBELT_CORE/2026-10-08/contracts_20261008.csv | 2026-10-08 02:10:03 |
| MW-100009 ⚠️ | C10004 | MW01 | E2003 | Air Compressor | 09/03/2026 | 10/02/2026 | Open | 140.00 | LEGACY_MW | /landing/rental/LEGACY_MW/2026-10-08/mw_contracts.csv | 2026-10-08 02:14:18 |

**DQ issues:** `rc100003` and `MW-100009` don't follow the `RC-NNNNNN` format; RC-100005 is an exact duplicate; RC-100003 has no sales rep and points to the duplicate customer C20002; RC-100006 has no customer; open contracts carry blank or `9999-12-31` end dates; dates mix ISO and MM/DD/YYYY.

---

## 4. `bronze_invoices`

| invoice_id | contract_id | customer_id | invoice_date | due_date | invoice_amount | tax_amount | invoice_type | currency | source_system | file_path | file_modification_time |
|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-500001 | RC-100001 | C10001 | 2026-07-31 | 2026-08-30 | 13950.00 | 976.50 | Standard | USD | SUNBELT_CORE | /landing/billing/SUNBELT_CORE/2026-10-08/invoices_20261008.csv | 2026-10-08 02:30:27 |
| CM-500009 | RC-100001 | C10001 | 2026-08-10 | 2026-08-10 | -900.00 | -63.00 | Credit Memo | USD | SUNBELT_CORE | /landing/billing/SUNBELT_CORE/2026-10-08/invoices_20261008.csv | 2026-10-08 02:30:27 |
| INV-500002 | RC-100002 | C10002 | 2026-08-14 | 2026-09-28 | 9750.00 | 682.50 | Standard | USD | SUNBELT_CORE | /landing/billing/SUNBELT_CORE/2026-10-08/invoices_20261008.csv | 2026-10-08 02:30:27 |
| INV-500003 ⚠️ | rc100003 | C20002 | 08/19/2026 | 10/03/2026 | 8250.00 | 577.50 | Standard | USD | LEGACY_SE | /landing/billing/LEGACY_SE/2026-10-08/inv_extract.csv | 2026-10-08 02:33:55 |
| INV-500004 | RC-100004 | C10003 | 2026-08-31 | 2026-09-30 | 5580.00 | 390.60 | Standard | USD | SUNBELT_CORE | /landing/billing/SUNBELT_CORE/2026-10-08/invoices_20261008.csv | 2026-10-08 02:30:27 |
| INV-500005 ⚠️ | RC-100005 | C10004 | 08/31/2026 | NULL | 14040.00 | 982.80 | Standard | USD | LEGACY_MW | /landing/billing/LEGACY_MW/2026-10-08/mw_invoices.csv | 2026-10-08 02:35:12 |
| INV-500006 | RC-100006 | C10002 | 2026-09-09 | 2026-10-24 | 4500.00 | 315.00 | Standard | USD | LEGACY_MW | /landing/billing/LEGACY_MW/2026-10-08/mw_invoices.csv | 2026-10-08 02:35:12 |
| INV-500007 | RC-100007 | C10005 | 2026-09-19 | 2026-10-19 | 2850.00 | 199.50 | Standard | USD | SUNBELT_CORE | /landing/billing/SUNBELT_CORE/2026-10-08/invoices_20261008.csv | 2026-10-08 02:30:27 |
| INV-500008 ⚠️ | RC-999999 | C10001 | 2026-09-05 | 2026-10-05 | 2200.00 | 154.00 | Standard | USD | SUNBELT_CORE | /landing/billing/SUNBELT_CORE/2026-10-08/invoices_20261008.csv | 2026-10-08 02:30:27 |
| INV-500010 | RC-100005 | C10004 | 09/30/2026 | 11/29/2026 | 15600.00 | 1092.00 | Standard | USD | LEGACY_MW | /landing/billing/LEGACY_MW/2026-10-08/mw_invoices.csv | 2026-10-08 02:35:12 |
| INV-500011 ⚠️ | MW-100009 | C10004 | 09/30/2026 | 11/29/2026 | 3920.00 | 274.40 | Standard | USD | LEGACY_MW | /landing/billing/LEGACY_MW/2026-10-08/mw_invoices.csv | 2026-10-08 02:35:12 |

**DQ issues:** INV-500008 references a contract (`RC-999999`) that doesn't exist (orphan); INV-500003 and INV-500011 carry non-standard contract IDs; INV-500005 has no due date (derive from Net 60 terms in Silver); dates mix formats. CM-500009 is a negative credit memo — **expected, not an error**. INV-500006 supplies the customer missing from contract RC-100006.

Amounts reconcile to contracts: `daily_rate × billed days`, tax at 7%.

---

## 5. `bronze_cash_receipts`

| receipt_id | invoice_id | customer_id | receipt_date | payment_amount | payment_method | source_system | file_path | file_modification_time |
|---|---|---|---|---|---|---|---|---|
| RCP-700001 | INV-500001 | C10001 | 2026-08-28 | 13963.50 | ACH | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700001 ⚠️ | INV-500001 | C10001 | 2026-08-28 | 13963.50 | ACH | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700002 | INV-500002 | C10002 | 2026-09-25 | 10432.50 | Wire | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700003 ⚠️ | INV-500003 | C20002 | NULL | 4000.00 | Check | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700004 ⚠️ | INV-500004 | NULL | 2026-10-02 | 5970.60 | Credit Card | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700005 ⚠️ | NULL | C10004 | 2026-10-01 | 10000.00 | Wire | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700006 | INV-500007 | C10005 | 2026-10-05 | 3049.50 | ACH | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |
| RCP-700007 | INV-500008 | C10001 | 2026-10-03 | 2354.00 | ACH | LOCKBOX_FEED | /landing/cash/LOCKBOX_FEED/2026-10-08/lockbox_20261008.csv | 2026-10-08 03:00:44 |

**DQ issues:** RCP-700001 duplicated; RCP-700003 missing receipt date (and is a partial payment against $8,827.50 owed); RCP-700004 missing customer (recoverable via invoice); RCP-700005 is unapplied cash with no invoice.

RCP-700001 = INV-500001 total ($14,926.50) net of CM-500009 ($963.00).

---

## Expected AR picture after Silver cleanup (as of 2026-10-08)

| Invoice | Customer (conformed) | Total due | Paid | Open balance | Days past due |
|---|---|---|---|---|---|
| INV-500001 + CM-500009 | C10001 Apex Builders | 13963.50 | 13963.50 | 0.00 | — |
| INV-500002 | C10002 Gulf Coast Paving | 10432.50 | 10432.50 | 0.00 | — |
| INV-500003 | C10002 (merged from C20002) | 8827.50 | 4000.00 | 4827.50 | 5 |
| INV-500004 | C10003 Lakeside Event Rentals | 5970.60 | 5970.60 | 0.00 | — (paid 2 days late) |
| INV-500005 | C10004 Midwest Steel Erectors | 15022.80 | 0.00 | 15022.80 | current (due 2026-10-30, derived from Net 60) |
| INV-500006 | C10002 Gulf Coast Paving | 4815.00 | 0.00 | 4815.00 | current |
| INV-500007 | C10005 | 3049.50 | 3049.50 | 0.00 | — |
| INV-500008 | C10001 (orphan contract) | 2354.00 | 2354.00 | 0.00 | — |
| INV-500010 | C10004 | 16692.00 | 0.00 | 16692.00 | current |
| INV-500011 | C10004 | 4194.40 | 0.00 | 4194.40 | current |
| *Unapplied* | C10004 | — | 10000.00 | -10000.00 | on account |
