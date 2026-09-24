# AscHeavyRentals — Medallion Architecture Sample Data

Sample data for every Bronze, Silver, and Gold table in the medallion architecture.

- Bronze and Silver tables show a small illustrative set of rows (5-10) per table so the grain and columns are clear -- a real system would carry thousands of transactions.
- Gold tables reproduce the actual figures from the executive dashboard (TTM ended Aug 31, 2026, $ millions), since those are aggregate, dashboard-consumable numbers.
- IDs are shared across tables where they'd naturally join (e.g. `equipment_id` appears in `bulk_lot_report`, `fact_fleet_oec_daily`, `equipment_disposals`).
- All data is synthetic, for illustration of table structure only.

## Bronze layer — raw ingestion

### `bronze.purchase_order`

| po_number | po_date | vendor_id | equipment_id | equipment_class | cost_amount | status | received_date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PO-2026-04-001 | 2026-04-03 | VEND-112 | EQ-1011 | Specialty | 185000 | Received | 2026-04-20 |
| PO-2026-04-002 | 2026-04-11 | VEND-098 | EQ-1012 | General Tool | 42000 | Received | 2026-04-25 |
| PO-2026-05-003 | 2026-05-02 | VEND-112 | EQ-1013 | Specialty | 210000 | Received | 2026-05-19 |
| PO-2026-05-004 | 2026-05-14 | VEND-045 | EQ-1014 | General Tool | 38500 | Received | 2026-05-30 |
| PO-2026-06-005 | 2026-06-06 | VEND-098 | EQ-1015 | General Tool | 41000 | Open | nan |
| PO-2026-06-006 | 2026-06-20 | VEND-112 | EQ-1016 | Specialty | 198000 | Received | 2026-07-08 |
| PO-2026-07-007 | 2026-07-09 | VEND-045 | EQ-1017 | General Tool | 39750 | Received | 2026-07-24 |
| PO-2026-08-008 | 2026-08-01 | VEND-098 | EQ-1018 | General Tool | 43200 | Open | nan |

### `bronze.ar_by_sales_rep_weekly`

| week_ending | sales_rep_id | region | revenue_amount | contract_count | ar_balance |
| --- | --- | --- | --- | --- | --- |
| 2026-08-02 | REP-01 | Southeast | 412000 | 18 | 255000 |
| 2026-08-09 | REP-01 | Southeast | 398500 | 17 | 261000 |
| 2026-08-16 | REP-01 | Southeast | 405200 | 19 | 248000 |
| 2026-08-23 | REP-01 | Southeast | 417800 | 18 | 239500 |
| 2026-08-02 | REP-03 | Midwest | 356000 | 15 | 301000 |
| 2026-08-09 | REP-03 | Midwest | 349200 | 14 | 308500 |
| 2026-08-16 | REP-03 | Midwest | 362100 | 16 | 295000 |
| 2026-08-23 | REP-03 | Midwest | 358700 | 15 | 289900 |

### `bronze.ar_reports`

| invoice_id | customer_id | invoice_date | due_date | paid_date | invoice_amount | open_balance | aging_bucket |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INV-88410 | CUST-2201 | 2026-07-05 | 2026-08-04 | 2026-08-01 | 18400 | 0 | Current |
| INV-88425 | CUST-2214 | 2026-07-11 | 2026-08-10 | 2026-08-22 | 9650 | 9650 | 1-30 days |
| INV-88439 | CUST-2233 | 2026-07-18 | 2026-08-17 | nan | 27300 | 27300 | 1-30 days |
| INV-88462 | CUST-2201 | 2026-07-25 | 2026-08-24 | nan | 15200 | 15200 | Current |
| INV-88477 | CUST-2278 | 2026-06-30 | 2026-07-30 | nan | 41850 | 41850 | 31-60 days |
| INV-88501 | CUST-2214 | 2026-08-01 | 2026-08-31 | 2026-08-29 | 12300 | 0 | Current |
| INV-88519 | CUST-2260 | 2026-05-28 | 2026-06-27 | nan | 8900 | 8900 | 61-90 days |
| INV-88533 | CUST-2233 | 2026-08-08 | 2026-09-07 | nan | 22750 | 22750 | Current |

### `bronze.bulk_lot_report`

| equipment_id | equipment_class | segment | region | original_cost | acquisition_date | status |
| --- | --- | --- | --- | --- | --- | --- |
| EQ-1001 | Skid Steer | General Tool | Southeast | 41200 | 2022-03-12 | On-rent |
| EQ-1002 | Mini Excavator | General Tool | Southeast | 68500 | 2021-11-04 | On-rent |
| EQ-1003 | Boom Lift | General Tool | Midwest | 57300 | 2020-06-18 | Idle |
| EQ-1004 | Telehandler | General Tool | Midwest | 73900 | 2023-01-22 | On-rent |
| EQ-1005 | Air Compressor | General Tool | West | 22400 | 2022-09-08 | On-rent |
| EQ-1006 | Crane, Rough Terrain | Specialty | Southeast | 412000 | 2021-04-15 | On-rent |
| EQ-1007 | Pump, High-Flow | Specialty | Midwest | 118500 | 2022-12-01 | On-rent |
| EQ-1008 | Generator, Industrial | Specialty | West | 96200 | 2023-05-27 | Idle |
| EQ-1009 | Compactor | General Tool | West | 31500 | 2020-10-09 | On-rent |
| EQ-1010 | Forklift, Rough Terrain | General Tool | Southeast | 54800 | 2021-08-19 | On-rent |

### `bronze.equipment_disposals`

| equipment_id | disposal_date | original_cost | book_value | sale_proceeds | disposal_method |
| --- | --- | --- | --- | --- | --- |
| EQ-0940 | 2026-04-14 | 62000 | 9500 | 10800 | Auction |
| EQ-0958 | 2026-05-22 | 48500 | 7200 | 8100 | Wholesale |
| EQ-0971 | 2026-06-09 | 115000 | 18400 | 19900 | Auction |
| EQ-0986 | 2026-07-16 | 39800 | 6100 | 6650 | Retail sale |
| EQ-0993 | 2026-08-03 | 71500 | 11200 | 12400 | Auction |

### `bronze.gl_detail_asset`

| gl_line_id | date | equipment_id | account | transaction_type | amount |
| --- | --- | --- | --- | --- | --- |
| GL-A-55012 | 2026-08-05 | EQ-1002 | Depreciation - Rental Equip | Depreciation | 3180 |
| GL-A-55013 | 2026-08-05 | EQ-1006 | Depreciation - Rental Equip | Depreciation | 4310 |
| GL-A-55014 | 2026-08-12 | EQ-1012 | Fixed Asset Additions | Capex | 42000 |
| GL-A-55015 | 2026-08-18 | EQ-0993 | Disposal - Original Cost | Disposal | -71500 |
| GL-A-55016 | 2026-08-18 | EQ-0993 | Disposal - Gain/Loss | Disposal Gain | 1200 |
| GL-A-55017 | 2026-08-25 | EQ-1016 | Fixed Asset Additions | Capex | 198000 |
| GL-A-55018 | 2026-08-28 | EQ-1005 | Refurbishment - Capitalized | Refurb Capex | 4600 |
| GL-A-55019 | 2026-08-30 | EQ-1010 | Depreciation - Rental Equip | Depreciation | 2950 |

### `bronze.gl_detail_datalake`

| gl_line_id | date | account | department | amount | pl_line_mapped |
| --- | --- | --- | --- | --- | --- |
| GL-D-91201 | 2026-08-04 | Cost of Equipment Rentals | Fleet Ops | 790000 | Cost of equipment rentals, excl. depreciation |
| GL-D-91202 | 2026-08-06 | Maintenance Labor | Fleet Ops | 312000 | Cost of equipment rentals, excl. depreciation |
| GL-D-91203 | 2026-08-09 | SG&A - Sales Salaries | Sales | 245000 | Selling, general and administrative |
| GL-D-91204 | 2026-08-11 | SG&A - Corporate Overhead | Corporate | 198500 | Selling, general and administrative |
| GL-D-91205 | 2026-08-14 | Non-Rental Depreciation | Corporate | 87000 | Non-rental depreciation and amortization |
| GL-D-91206 | 2026-08-19 | Cost of Used Equip Sold | Fleet Ops | 68000 | Cost of used equipment sales |
| GL-D-91207 | 2026-08-22 | Cost of New Equip/Merch | Sales | 41500 | Cost of new equipment, merchandise, and services |
| GL-D-91208 | 2026-08-26 | Cash Tax Paid | Corporate | 820000 | Cash tax |
| GL-D-91209 | 2026-08-28 | Cost of Equipment Rentals | Fleet Ops | 765000 | Cost of equipment rentals, excl. depreciation |
| GL-D-91210 | 2026-08-30 | SG&A - Marketing | Sales | 56000 | Selling, general and administrative |

### `bronze.invoice_detail_master`

| invoice_line_id | invoice_date | customer_id | revenue_type | segment | region | rate | time_on_rent_days | amount |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INVL-70011 | 2026-08-02 | CUST-2201 | owned_rental | General Tool | Southeast | 1850 | 12 | 18400 |
| INVL-70012 | 2026-08-03 | CUST-2214 | owned_rental | Specialty | Midwest | 5200 | 8 | 9650 |
| INVL-70013 | 2026-08-05 | CUST-2233 | ancillary | General Tool | West | nan | nan | 2100 |
| INVL-70014 | 2026-08-08 | CUST-2201 | owned_rental | General Tool | Southeast | 1620 | 10 | 15200 |
| INVL-70015 | 2026-08-11 | CUST-2278 | re_rent | Specialty | Southeast | 3900 | 6 | 4850 |
| INVL-70016 | 2026-08-15 | CUST-2214 | owned_rental | General Tool | Midwest | 1710 | 14 | 12300 |
| INVL-70017 | 2026-08-19 | CUST-2260 | used_sale | nan | Midwest | nan | nan | 8900 |
| INVL-70018 | 2026-08-23 | CUST-2233 | owned_rental | Specialty | West | 5450 | 9 | 22750 |
| INVL-70019 | 2026-08-27 | CUST-2278 | ancillary | General Tool | Southeast | nan | nan | 1650 |
| INVL-70020 | 2026-08-30 | CUST-2201 | new_sale | nan | Southeast | nan | nan | 3400 |

### `bronze.rental_contracts_by_rep`

| contract_id | open_date | sales_rep_id | equipment_class | rate_realization_pct | time_on_rent_days | region |
| --- | --- | --- | --- | --- | --- | --- |
| CT-33010 | 2026-08-01 | REP-01 | General Tool | 96.4 | 12 | Southeast |
| CT-33011 | 2026-08-04 | REP-03 | General Tool | 96.8 | 15 | Midwest |
| CT-33012 | 2026-08-06 | REP-01 | Specialty | 97.1 | 8 | Southeast |
| CT-33013 | 2026-08-09 | REP-05 | General Tool | 95.9 | 11 | West |
| CT-33014 | 2026-08-13 | REP-03 | General Tool | 96.5 | 13 | Midwest |
| CT-33015 | 2026-08-17 | REP-01 | General Tool | 96.2 | 10 | Southeast |
| CT-33016 | 2026-08-21 | REP-05 | Specialty | 97.4 | 9 | West |
| CT-33017 | 2026-08-26 | REP-03 | General Tool | 96.6 | 14 | Midwest |

### `bronze.ap_vendor_rpt`

| ap_id | vendor_id | invoice_date | amount | category | paid_flag |
| --- | --- | --- | --- | --- | --- |
| AP-6001 | VEND-112 | 2026-08-03 | 185000 | Equipment purchase | Paid |
| AP-6002 | VEND-045 | 2026-08-07 | 38500 | Equipment purchase | Paid |
| AP-6003 | VEND-771 | 2026-08-10 | 22000 | Parts & maintenance | Paid |
| AP-6004 | VEND-098 | 2026-08-14 | 41000 | Equipment purchase | Open |
| AP-6005 | VEND-220 | 2026-08-18 | 9800 | Freight & delivery | Paid |
| AP-6006 | VEND-771 | 2026-08-22 | 15600 | Parts & maintenance | Paid |
| AP-6007 | VEND-112 | 2026-08-27 | 198000 | Equipment purchase | Paid |
| AP-6008 | VEND-045 | 2026-08-30 | 12400 | Parts & maintenance | Open |

## Silver layer — cleaned facts & dimensions

### `silver.dim_equipment`

| equipment_id | equipment_class | segment | acquisition_date | useful_life_years |
| --- | --- | --- | --- | --- |
| EQ-1001 | Skid Steer | General Tool | 2022-03-12 | 8 |
| EQ-1002 | Mini Excavator | General Tool | 2021-11-04 | 7 |
| EQ-1003 | Boom Lift | General Tool | 2020-06-18 | 10 |
| EQ-1004 | Telehandler | General Tool | 2023-01-22 | 8 |
| EQ-1005 | Air Compressor | General Tool | 2022-09-08 | 6 |
| EQ-1006 | Crane, Rough Terrain | Specialty | 2021-04-15 | 12 |
| EQ-1007 | Pump, High-Flow | Specialty | 2022-12-01 | 8 |
| EQ-1008 | Generator, Industrial | Specialty | 2023-05-27 | 10 |
| EQ-1009 | Compactor | General Tool | 2020-10-09 | 7 |
| EQ-1010 | Forklift, Rough Terrain | General Tool | 2021-08-19 | 9 |

### `silver.dim_region`

| region_id | region_name |
| --- | --- |
| R-SE | Southeast |
| R-MW | Midwest |
| R-W | West |

### `silver.dim_date`

| calendar_date | fiscal_year | fiscal_month | month_end_flag |
| --- | --- | --- | --- |
| 2025-09-30 | 2025 | 9 | False |
| 2025-12-31 | 2025 | 12 | True |
| 2026-03-31 | 2026 | 3 | True |
| 2026-06-30 | 2026 | 6 | True |
| 2026-07-31 | 2026 | 7 | True |
| 2026-08-31 | 2026 | 8 | True |

### `silver.dim_sales_rep`

| sales_rep_id | region_id |
| --- | --- |
| REP-01 | R-SE |
| REP-02 | R-SE |
| REP-03 | R-MW |
| REP-04 | R-MW |
| REP-05 | R-W |

### `silver.fact_fleet_oec_daily`

| equipment_id | date | segment | region_id | original_cost | month_end_flag |
| --- | --- | --- | --- | --- | --- |
| EQ-1001 | 2026-08-31 | General Tool | R-SE | 41200 | True |
| EQ-1002 | 2026-08-31 | General Tool | R-SE | 68500 | True |
| EQ-1003 | 2026-08-31 | General Tool | R-MW | 57300 | True |
| EQ-1004 | 2026-08-31 | General Tool | R-MW | 73900 | True |
| EQ-1005 | 2026-08-31 | General Tool | R-W | 22400 | True |
| EQ-1006 | 2026-08-31 | Specialty | R-SE | 412000 | True |
| EQ-1007 | 2026-08-31 | Specialty | R-MW | 118500 | True |
| EQ-1008 | 2026-08-31 | Specialty | R-W | 96200 | True |
| EQ-1009 | 2026-08-31 | General Tool | R-W | 31500 | True |
| EQ-1010 | 2026-08-31 | General Tool | R-SE | 54800 | True |

### `silver.fact_revenue_transaction`

| invoice_line_id | date | customer_id | revenue_type | segment | rate | time_on_rent_days | amount | region_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INVL-70011 | 2026-08-02 | CUST-2201 | owned_rental | General Tool | 1850 | 12 | 18400 | R-SE |
| INVL-70012 | 2026-08-03 | CUST-2214 | owned_rental | Specialty | 5200 | 8 | 9650 | R-MW |
| INVL-70013 | 2026-08-05 | CUST-2233 | ancillary | General Tool | nan | nan | 2100 | R-W |
| INVL-70014 | 2026-08-08 | CUST-2201 | owned_rental | General Tool | 1620 | 10 | 15200 | R-SE |
| INVL-70015 | 2026-08-11 | CUST-2278 | re_rent | Specialty | 3900 | 6 | 4850 | R-SE |
| INVL-70016 | 2026-08-15 | CUST-2214 | owned_rental | General Tool | 1710 | 14 | 12300 | R-MW |
| INVL-70017 | 2026-08-19 | CUST-2260 | used_sale | nan | nan | nan | 8900 | R-MW |
| INVL-70018 | 2026-08-23 | CUST-2233 | owned_rental | Specialty | 5450 | 9 | 22750 | R-W |
| INVL-70019 | 2026-08-27 | CUST-2278 | ancillary | General Tool | nan | nan | 1650 | R-SE |
| INVL-70020 | 2026-08-30 | CUST-2201 | new_sale | nan | nan | nan | 3400 | R-SE |

### `silver.fact_ar_transactions`

| invoice_id | date | customer_id | invoice_amount | open_balance | aging_days |
| --- | --- | --- | --- | --- | --- |
| INV-88410 | 2026-08-01 | CUST-2201 | 18400 | 0 | 0 |
| INV-88425 | 2026-08-22 | CUST-2214 | 9650 | 9650 | 12 |
| INV-88439 | 2026-08-17 | CUST-2233 | 27300 | 27300 | 14 |
| INV-88462 | 2026-08-24 | CUST-2201 | 15200 | 15200 | 3 |
| INV-88477 | 2026-07-30 | CUST-2278 | 41850 | 41850 | 38 |
| INV-88501 | 2026-08-29 | CUST-2214 | 12300 | 0 | 0 |
| INV-88519 | 2026-06-27 | CUST-2260 | 8900 | 8900 | 82 |
| INV-88533 | 2026-09-07 | CUST-2233 | 22750 | 22750 | 5 |

### `silver.fact_disposals`

| disposal_id | equipment_id | date | original_cost | book_value | sale_proceeds | gain_loss |
| --- | --- | --- | --- | --- | --- | --- |
| DISP-001 | EQ-0940 | 2026-04-14 | 62000 | 9500 | 10800 | 1300 |
| DISP-002 | EQ-0958 | 2026-05-22 | 48500 | 7200 | 8100 | 900 |
| DISP-003 | EQ-0971 | 2026-06-09 | 115000 | 18400 | 19900 | 1500 |
| DISP-004 | EQ-0986 | 2026-07-16 | 39800 | 6100 | 6650 | 550 |
| DISP-005 | EQ-0993 | 2026-08-03 | 71500 | 11200 | 12400 | 1200 |

### `silver.fact_purchase_orders`

| po_line_id | date | equipment_id | cost_amount | capitalized_flag |
| --- | --- | --- | --- | --- |
| POL-001 | 2026-04-20 | EQ-1011 | 185000 | True |
| POL-002 | 2026-04-25 | EQ-1012 | 42000 | True |
| POL-003 | 2026-05-19 | EQ-1013 | 210000 | True |
| POL-004 | 2026-05-30 | EQ-1014 | 38500 | True |
| POL-005 | 2026-06-06 | EQ-1015 | 41000 | False |
| POL-006 | 2026-07-08 | EQ-1016 | 198000 | True |
| POL-007 | 2026-07-24 | EQ-1017 | 39750 | True |
| POL-008 | 2026-08-01 | EQ-1018 | 43200 | False |

### `silver.fact_gl_costs`

| gl_line_id | date | pl_line | amount |
| --- | --- | --- | --- |
| GL-D-91201 | 2026-08-04 | Cost of equipment rentals, excl. depreciation | 790000 |
| GL-D-91202 | 2026-08-06 | Cost of equipment rentals, excl. depreciation | 312000 |
| GL-A-55012 | 2026-08-05 | Depreciation of rental equipment | 3180 |
| GL-A-55013 | 2026-08-05 | Depreciation of rental equipment | 4310 |
| GL-D-91203 | 2026-08-09 | Selling, general and administrative | 245000 |
| GL-D-91204 | 2026-08-11 | Selling, general and administrative | 198500 |
| GL-D-91205 | 2026-08-14 | Non-rental depreciation and amortization | 87000 |
| GL-D-91206 | 2026-08-19 | Cost of used equipment sales | 68000 |
| GL-D-91207 | 2026-08-22 | Cost of new equipment, merchandise, and services | 41500 |
| GL-D-91208 | 2026-08-26 | Cash tax | 820000 |

## Gold layer — KPI-ready tables

### `gold.kpi_scorecard`

| grain | period | revenue_usd_mm | revenue_growth_pct | fleet_oec_growth_pct | same_store_revenue_growth_pct | fleet_productivity_usd_mm | dollar_utilization_pct | dollar_utilization_chg_pt | ebitda_margin_pct | ebitda_usd_mm | ebitda_chg_usd_mm | fcf_usd_mm | net_fleet_investment_usd_mm | disposal_proceeds_pct_of_cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Company | TTM Aug-2026 | 230 | 3.2 | 3.5 | 2.4 | -0.9 | 52.7 | -0.2 | 40.3 | 92.6 | 1.2 | 60.1 | 22.7 | 44 |

### `gold.revenue_bridge`

| component | amount_usd_mm |
| --- | --- |
| Prior-year revenue (base) | 222.9 |
| Larger fleet (OEC) | 6.6 |
| Rate | -0.6 |
| Time on rent | -0.5 |
| Mix | 0.2 |
| Ancillary | 0.5 |
| Re-rent | 0.2 |
| Used and new sales | 0.7 |
| Current-year revenue (ending) | 230 |

### `gold.dollar_utilization_by_segm`

| segment | share_of_fleet_pct | dollar_utilization_pct | chg_vs_py_pt | design_band_min_pct | design_band_max_pct | capital_stance | owned_rental_revenue_usd_mm | avg_oec_usd_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| General Tool | 73.5 | 45.9 | -0.8 | 44 | 48 | Replace only, pause growth capex | 124 | 270 |
| Specialty | 26.5 | 71.3 | 1.3 | 68 | 74 | Fund - prefer for growth capex | 69.5 | 97.5 |
| Company | 100 | 52.7 | -0.2 | nan | nan | Ratio of sums | 193.5 | 367.5 |

### `gold.regional_mix`

| region | revenue_usd_mm | revenue_share_pct | ebitda_margin_pct | dollar_utilization_pct |
| --- | --- | --- | --- | --- |
| Southeast | 92 | 40 | 41.2 | 54.2 |
| Midwest | 78.2 | 34 | 39.6 | 51.4 |
| West | 59.8 | 26 | 39.8 | 52 |
| Company | 230 | 100 | 40.3 | 52.7 |

### `gold.management_pl`

| line_item | august_usd_mm | ttm_usd_mm | pct_of_revenue |
| --- | --- | --- | --- |
| Owned rental revenue | 20.4 | 193.5 | 84.1 |
| Re-rent revenue | 0.5 | 4.9 | 2.1 |
| Ancillary revenue | 1.6 | 15.5 | 6.7 |
| Equipment rentals (subtotal) | 22.5 | 213.9 | 93 |
| Used equipment sales | 1 | 9.2 | 4 |
| New equipment, merchandise & services | 0.7 | 6.9 | 3 |
| Total revenue | 24.2 | 230 | 100 |
| Cost of equipment rentals, excl. depreciation | 9.5 | 90.6 | 39.4 |
| Depreciation of rental equipment | 4 | 38.2 | 16.6 |
| Cost of used equipment sales | 0.8 | 8 | 3.5 |
| Cost of new equipment, merchandise & services | 0.5 | 4.8 | 2.1 |
| Gross profit | 9.4 | 88.4 | 38.4 |
| Selling, general and administrative | 3.6 | 34 | 14.8 |
| Non-rental depreciation and amortization | 1 | 9.4 | 4.1 |
| Operating income | 4.8 | 45 | 19.6 |
| EBITDA | 9.8 | 92.6 | 40.3 |

### `gold.oec_rollforward`

| component | amount_usd_mm |
| --- | --- |
| Month-end OEC, Aug 31 2025 | 361.2 |
| Fleet additions | 31.9 |
| Capitalized refurbishment | 1.6 |
| Disposals at original cost | -20.9 |
| Month-end OEC, Aug 31 2026 | 373.8 |

### `gold.decision_metrics`

| grain | period | rate_realization_pct_py | rate_realization_pct_cy | time_on_rent_giveback_usd_mm | specialty_pct_of_oec | ebitda_growth_pct | revenue_growth_pct | cost_of_rentals_ex_dep_usd_mm | maintenance_usd_mm | maintenance_pct_of_oec | disposal_hurdle_pct | gain_on_disposal_usd_mm | book_value_usd_mm | cash_tax_usd_mm | working_capital_delta_usd_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Company | TTM Aug-2026 | 96.8 | 96.5 | -0.5 | 26.5 | 1.3 | 3.2 | 90.6 | 12.5 | 3.3 | 44 | 1.2 | 8 | 9.8 | 0 |