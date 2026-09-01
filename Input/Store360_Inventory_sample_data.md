# DSG Stores — Sample Data
Sample rows for each table in `DSG_Stores_Full_Process_Tables.txt`, consistent with the declared PKs/FKs.

## REGION

| region_id | region_name | vp_name | is_active | created_ts | updated_ts |
|---|---|---|---|---|---|
| R1 | Northeast | Karen Osei | Y | 2023-01-05 08:00:00 | 2026-06-01 09:00:00 |
| R2 | Midwest | Daniel Ruiz | Y | 2023-01-05 08:00:00 | 2026-06-01 09:00:00 |
| R3 | Southeast | Priya Nair | Y | 2023-01-05 08:00:00 | 2026-06-01 09:00:00 |

## DISTRICT

| district_id | region_id | district_name | district_manager | is_active | created_ts | updated_ts |
|---|---|---|---|---|---|---|
| D101 | R1 | Boston Metro | Alan Cho | Y | 2023-01-10 08:00:00 | 2026-06-01 09:00:00 |
| D102 | R2 | Chicago North | Maria Petrova | Y | 2023-01-10 08:00:00 | 2026-06-01 09:00:00 |
| D103 | R3 | Atlanta South | James Whitfield | Y | 2023-01-10 08:00:00 | 2026-06-01 09:00:00 |

## STORE

| store_id | store_number | store_name | district_id | fieldhouse_type | open_date | close_date | address | city | state | postal_code | is_active | created_ts | updated_ts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1001 | 4501 | Boston Downtown | D101 | Standard | 2015-03-12 | | 200 Boylston St | Boston | MA | 02116 | Y | 2015-03-01 08:00:00 | 2026-06-01 09:00:00 |
| S1002 | 4502 | Chicago Northside | D102 | Fieldhouse | 2018-07-20 | | 1801 W North Ave | Chicago | IL | 60622 | Y | 2018-07-01 08:00:00 | 2026-06-01 09:00:00 |
| S1003 | 4503 | Atlanta Perimeter | D103 | Standard | 2012-11-01 | 2026-02-15 | 4400 Ashford Dunwoody Rd | Atlanta | GA | 30346 | N | 2012-10-01 08:00:00 | 2026-02-15 17:00:00 |

## ATHLETE

| athlete_id | master_account_id | loyalty_flag | gold_flag | first_purchase_date | last_purchase_date | omni_channel_flag | created_ts | updated_ts |
|---|---|---|---|---|---|---|---|---|
| A2001 | MA-9001 | Y | Y | 2020-04-02 | 2026-08-20 | Y | 2020-04-02 10:15:00 | 2026-08-20 14:32:00 |
| A2002 | MA-9002 | Y | N | 2021-09-14 | 2026-07-11 | N | 2021-09-14 11:02:00 | 2026-07-11 16:05:00 |
| A2003 | MA-9003 | N | N | 2024-01-08 | 2024-01-08 | N | 2024-01-08 12:40:00 | 2024-01-08 12:40:00 |

## ATHLETE_PROFILE

| athlete_profile_id | athlete_id | preferred_store_id | persona | micro_cohort | email | created_ts | updated_ts |
|---|---|---|---|---|---|---|---|
| AP3001 | A2001 | S1001 | Performance Runner | Marathon Trainers | a.moore@example.com | 2020-04-02 10:20:00 | 2026-08-20 14:32:00 |
| AP3002 | A2002 | S1002 | Team Sports Parent | Youth League Shoppers | j.kim@example.com | 2021-09-14 11:05:00 | 2026-07-11 16:05:00 |
| AP3003 | A2003 | S1001 | Casual Fitness | Gym Starters | t.nguyen@example.com | 2024-01-08 12:41:00 | 2024-01-08 12:41:00 |

## PRODUCT

| product_id | sku | upc | style_number | brand | department_description | vendor_name | created_ts | updated_ts |
|---|---|---|---|---|---|---|---|---|
| P5001 | SKU-77001 | 049000012345 | STY-5501 | Nike | Footwear | Nike Inc | 2022-02-01 08:00:00 | 2026-05-01 09:00:00 |
| P5002 | SKU-77002 | 049000012346 | STY-5502 | Under Armour | Apparel | UA LLC | 2022-02-01 08:00:00 | 2026-05-01 09:00:00 |
| P5003 | SKU-77003 | 049000012347 | STY-5503 | Wilson | Team Sports | Wilson Sporting Goods | 2022-02-01 08:00:00 | 2026-05-01 09:00:00 |

## PRODUCT_HIERARCHY

| hierarchy_id | product_id | division | department | class | subclass |
|---|---|---|---|---|---|
| H601 | P5001 | Footwear | Running | Road Running | Neutral Cushion |
| H602 | P5002 | Apparel | Training | Tops | Compression Tops |
| H603 | P5003 | Team Sports | Baseball | Equipment | Gloves |

## INVENTORY_BALANCE

| inventory_balance_id | store_id | product_id | inventory_date | on_hand_qty | available_qty | allocated_qty | damaged_qty | last_update_ts |
|---|---|---|---|---|---|---|---|---|
| IB7001 | S1001 | P5001 | 2026-08-30 | 42 | 38 | 4 | 0 | 2026-08-30 23:00:00 |
| IB7002 | S1002 | P5002 | 2026-08-30 | 15 | 12 | 3 | 0 | 2026-08-30 23:00:00 |
| IB7003 | S1001 | P5003 | 2026-08-30 | 8 | 6 | 1 | 1 | 2026-08-30 23:00:00 |

## INVENTORY_ADJUSTMENT

| adjustment_id | store_id | product_id | adjustment_reason | adjustment_qty | adjustment_ts |
|---|---|---|---|---|---|
| IA8001 | S1001 | P5003 | Damaged in stockroom | -1 | 2026-08-28 10:12:00 |
| IA8002 | S1002 | P5002 | Cycle count correction | 2 | 2026-08-29 09:05:00 |
| IA8003 | S1001 | P5001 | Return to vendor | -2 | 2026-08-27 14:20:00 |

## INVENTORY_REPLENISHMENT

| replenishment_id | store_id | product_id | requested_qty | replenished_qty | replenishment_ts |
|---|---|---|---|---|---|
| IR9001 | S1001 | P5001 | 20 | 20 | 2026-08-25 06:00:00 |
| IR9002 | S1002 | P5002 | 10 | 8 | 2026-08-26 06:00:00 |
| IR9003 | S1001 | P5003 | 5 | 5 | 2026-08-24 06:00:00 |

## RFID_EVENT

| rfid_event_id | store_id | product_id | scan_ts | total_on_hand | cycle_count_delta | store_available_on_hand |
|---|---|---|---|---|---|---|
| RE1101 | S1001 | P5001 | 2026-08-30 22:00:00 | 42 | 0 | 38 |
| RE1102 | S1002 | P5002 | 2026-08-30 22:05:00 | 15 | -1 | 12 |
| RE1103 | S1001 | P5003 | 2026-08-30 22:10:00 | 8 | 0 | 6 |

## RFID_CYCLE_COUNT

| cycle_count_id | store_id | count_date | completion_pct | variance_pct |
|---|---|---|---|---|
| CC1201 | S1001 | 2026-08-29 | 100.0 | 0.5 |
| CC1202 | S1002 | 2026-08-29 | 97.5 | 1.2 |
| CC1203 | S1003 | 2026-01-30 | 100.0 | 0.0 |

## SALES_TRANSACTION

| transaction_id | athlete_id | store_id | transaction_ts | total_sales_amount | sales_channel |
|---|---|---|---|---|---|
| T3301 | A2001 | S1001 | 2026-08-20 14:30:00 | 189.98 | In-Store |
| T3302 | A2002 | S1002 | 2026-07-11 16:00:00 | 64.99 | Online |
| T3303 | A2003 | S1001 | 2024-01-08 12:40:00 | 39.99 | In-Store |

## SALES_TRANSACTION_LINE

| transaction_line_id | transaction_id | product_id | quantity | net_sale_price | cost_amount |
|---|---|---|---|---|---|
| TL4401 | T3301 | P5001 | 1 | 129.99 | 65.00 |
| TL4402 | T3301 | P5002 | 1 | 59.99 | 28.00 |
| TL4403 | T3302 | P5002 | 1 | 64.99 | 28.00 |
| TL4404 | T3303 | P5003 | 1 | 39.99 | 18.00 |

## FULFILLMENT_REQUEST

| fulfillment_request_id | athlete_id | store_id | request_type | request_status | created_ts | completed_ts |
|---|---|---|---|---|---|---|
| FR5501 | A2001 | S1001 | BOPIS | Completed | 2026-08-19 09:00:00 | 2026-08-20 14:00:00 |
| FR5502 | A2002 | S1002 | Ship-from-Store | In Progress | 2026-08-29 11:00:00 | |
| FR5503 | A2003 | S1001 | BOPIS | Cancelled | 2024-01-07 10:00:00 | 2024-01-07 15:00:00 |

## FULFILLMENT_REQUEST_UNIT

| fr_unit_id | fulfillment_request_id | product_id | requested_qty | picked_qty | declined_qty |
|---|---|---|---|---|---|
| FU6601 | FR5501 | P5001 | 1 | 1 | 0 |
| FU6602 | FR5502 | P5002 | 2 | 1 | 1 |
| FU6603 | FR5503 | P5003 | 1 | 0 | 1 |

## TASK

| task_id | task_type_cd | store_id | assigned_employee_id | task_status |
|---|---|---|---|---|
| TSK7701 | PICK | S1001 | E8801 | Completed |
| TSK7702 | RESTOCK | S1002 | E8802 | Open |
| TSK7703 | CYCLE_COUNT | S1001 | E8803 | In Progress |

## SEARCH_EVENT

| search_event_id | athlete_id | store_id | search_phrase | results_count | search_ts |
|---|---|---|---|---|---|
| SE8801 | A2001 | S1001 | running shoes | 24 | 2026-08-19 08:55:00 |
| SE8802 | A2002 | S1002 | compression shirt | 11 | 2026-07-10 19:30:00 |
| SE8803 | A2003 | S1001 | baseball glove | 6 | 2024-01-08 12:20:00 |

## PRODUCT_VIEW_EVENT

| product_view_id | athlete_id | product_id | finding_method | event_ts |
|---|---|---|---|---|
| PV9901 | A2001 | P5001 | Search | 2026-08-19 08:56:00 |
| PV9902 | A2002 | P5002 | Recommendation | 2026-07-10 19:31:00 |
| PV9903 | A2003 | P5003 | Category Browse | 2024-01-08 12:22:00 |

## EMPLOYEE

| employee_id | store_id | employee_role | hire_date | status |
|---|---|---|---|---|
| E8801 | S1001 | Sales Associate | 2021-03-15 | Active |
| E8802 | S1002 | Stock Associate | 2022-06-01 | Active |
| E8803 | S1001 | Team Lead | 2019-11-10 | Active |

## LABOR_TIMECARD

| timecard_id | employee_id | work_date | scheduled_hours | worked_hours | overtime_hours |
|---|---|---|---|---|---|
| LT0001 | E8801 | 2026-08-29 | 8.0 | 8.25 | 0.25 |
| LT0002 | E8802 | 2026-08-29 | 6.0 | 6.0 | 0.0 |
| LT0003 | E8803 | 2026-08-29 | 8.0 | 9.0 | 1.0 |

## SHIPMENT

| shipment_id | tc_shipment_id | origin_store_id | destination_store_id | shipment_status | shipment_type | total_cost | shipment_start_dttm | shipment_end_dttm |
|---|---|---|---|---|---|---|---|---|
| SH1001 | TC-88001 | S1002 | S1001 | Delivered | Store-to-Store | 145.50 | 2026-08-26 07:00:00 | 2026-08-27 15:00:00 |
| SH1002 | TC-88002 | S1001 | S1002 | In Transit | Store-to-Store | 98.20 | 2026-08-30 07:00:00 | |
| SH1003 | TC-88003 | S1003 | S1001 | Delivered | Closure Transfer | 210.00 | 2026-02-16 07:00:00 | 2026-02-18 12:00:00 |

## SHIPMENT_EVENT

| shipment_event_id | shipment_id | event_type | event_ts | location |
|---|---|---|---|---|
| SEV2001 | SH1001 | Departed | 2026-08-26 07:15:00 | S1002 |
| SEV2002 | SH1001 | Arrived | 2026-08-27 15:00:00 | S1001 |
| SEV2003 | SH1002 | Departed | 2026-08-30 07:15:00 | S1001 |

## Data Quality Notes on This Sample Set

- Every `store_id`, `product_id`, and `athlete_id` referenced by a child table above exists in its parent table (STORE, PRODUCT, ATHLETE), per rule 12.
- `available_qty <= on_hand_qty` holds for all INVENTORY_BALANCE rows.
- All inventory quantities are non-negative.
- All `shipment_id` and `athlete_id` values above are unique within this sample.
