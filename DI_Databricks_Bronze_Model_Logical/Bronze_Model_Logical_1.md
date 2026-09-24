_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Bronze layer logical data model for AscHeavyRentals_Dashboard
## *Version*: 1
## *Updated on*: 
_____________________________________________

# PII Classification

| Column Name         | Reason why it is classified as PII                |
|--------------------|--------------------------------------------------|
| customer_id        | Identifies individual customers (GDPR sensitive)  |
| vendor_id          | Identifies vendors, may contain business PII      |
| sales_rep_id       | Identifies sales reps, personal information       |
| region             | May indirectly identify individuals by geography  |
| paid_date          | Payment dates can be linked to individuals        |
| invoice_date       | Invoice dates tied to customer transactions       |
| contract_id        | Contract identifiers may be linked to individuals |
| ap_id              | AP transaction identifiers may be sensitive       |


# Bronze Layer Logical Model

## Table: Bz_purchase_order
**Description:** Raw purchase order lines from source system.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| po_number         | Purchase order number                        | string    |
| po_date           | Date PO was issued                           | date      |
| vendor_id         | Vendor identifier                            | string    |
| equipment_id      | Equipment unit purchased                     | string    |
| equipment_class   | Equipment class/type                         | string    |
| cost_amount       | PO line cost amount                          | decimal   |
| status            | Open / Received                              | string    |
| received_date     | Date equipment was received                  | date      |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_ar_by_sales_rep_weekly
**Description:** Weekly AR reports by sales rep.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| week_ending       | Week-ending date                             | date      |
| sales_rep_id      | Sales rep identifier                         | string    |
| region            | Region name                                  | string    |
| revenue_amount    | Revenue booked that week                     | decimal   |
| contract_count    | Contracts opened that week                   | integer   |
| ar_balance        | Outstanding AR balance                       | decimal   |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_ar_reports
**Description:** AR transaction details per invoice.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| invoice_id        | Invoice identifier                           | string    |
| customer_id       | Customer identifier                          | string    |
| invoice_date      | Date invoiced                                | date      |
| due_date          | Payment due date                             | date      |
| paid_date         | Date paid (null if open)                     | date      |
| invoice_amount    | Total invoice amount                         | decimal   |
| open_balance      | Remaining unpaid balance                      | decimal   |
| aging_bucket      | Aging category (Current, 1-30, 31-60, 61-90+) | string    |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_bulk_lot_report
**Description:** Fleet bulk lot snapshot per equipment unit.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| equipment_id      | Equipment unit identifier                    | string    |
| equipment_class   | Equipment class/type                         | string    |
| segment           | General Tool / Specialty                     | string    |
| region            | Region name                                  | string    |
| original_cost     | Original cost (OEC)                          | decimal   |
| acquisition_date  | Date acquired                                | date      |
| status            | Owned / On-rent / Idle                       | string    |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_equipment_disposals
**Description:** Equipment disposal transactions.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| equipment_id      | Equipment unit disposed                      | string    |
| disposal_date     | Date disposed                                | date      |
| original_cost     | Original cost of the unit                    | decimal   |
| book_value        | Net book value at disposal                   | decimal   |
| sale_proceeds     | Cash proceeds from sale                      | decimal   |
| disposal_method   | Auction / Wholesale / Retail sale            | string    |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_gl_detail_asset
**Description:** GL asset transaction details.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| date              | Transaction date                             | date      |
| equipment_id      | Related equipment unit                       | string    |
| account           | GL account name                              | string    |
| transaction_type  | Depreciation / Capex / Disposal / Refurb Capex | string    |
| amount            | Transaction amount                           | decimal   |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_gl_detail_datalake
**Description:** GL line details from Data Lake.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| date              | Transaction date                             | date      |
| account           | GL account name                              | string    |
| department        | Owning department/cost center                | string    |
| amount            | Transaction amount                           | decimal   |
| pl_line_mapped    | Target management P&L line                   | string    |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_invoice_detail_master
**Description:** Invoice line details for master account.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| invoice_date      | Date invoiced                                | date      |
| customer_id       | Customer identifier                          | string    |
| revenue_type      | owned_rental / re_rent / ancillary / used_sale / new_sale | string    |
| segment           | General Tool / Specialty (rental lines only) | string    |
| region            | Region name                                  | string    |
| rate              | Daily/period rental rate (rental lines only) | decimal   |
| time_on_rent_days | Days on rent (rental lines only)             | integer   |
| amount            | Line amount                                  | decimal   |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_rental_contracts_by_rep
**Description:** Rental contracts opened by sales rep.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| open_date         | Date contract opened                         | date      |
| sales_rep_id      | Sales rep identifier                         | string    |
| equipment_class   | Equipment class/type                         | string    |
| rate_realization_pct | Rate realization vs list rate              | decimal   |
| time_on_rent_days | Time on rent for the contract                | integer   |
| region            | Region name                                  | string    |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |

## Table: Bz_ap_vendor_rpt
**Description:** AP vendor report transactions.

| Column Name        | Description                                 | Data Type |
|-------------------|---------------------------------------------|-----------|
| vendor_id         | Vendor identifier                            | string    |
| invoice_date      | Vendor invoice date                          | date      |
| amount            | Transaction amount                           | decimal   |
| category          | Equipment purchase / Parts & maintenance / Freight & delivery | string    |
| paid_flag         | Paid / Open                                  | string    |
| load_timestamp    | Timestamp when record was loaded              | datetime  |
| update_timestamp  | Timestamp when record was updated             | datetime  |
| source_system     | Source system name                            | string    |


# Audit Table Design

| Field           | Description                                   | Data Type |
|-----------------|-----------------------------------------------|-----------|
| record_id       | Unique record identifier                      | string    |
| source_table    | Source table name                             | string    |
| load_timestamp  | Timestamp when record was loaded              | datetime  |
| processed_by    | Processing agent name                         | string    |
| processing_time | Time taken to process record                  | decimal   |
| status          | Processing status (success/failure)           | string    |


# Conceptual Data Model Diagram (Tabular Form)

| Source Table                | Relationship Key Field | Target Table                | Relationship Type |
|-----------------------------|-----------------------|----------------------------|-------------------|
| Bz_purchase_order           | vendor_id             | Bz_ap_vendor_rpt           | Many-to-One       |
| Bz_ar_reports               | customer_id           | Bz_invoice_detail_master   | Many-to-One       |
| Bz_bulk_lot_report          | equipment_id          | Bz_equipment_disposals     | One-to-Many       |
| Bz_rental_contracts_by_rep  | sales_rep_id          | Bz_ar_by_sales_rep_weekly  | Many-to-One       |
| Bz_gl_detail_asset          | equipment_id          | Bz_bulk_lot_report         | Many-to-One       |
| Bz_gl_detail_datalake       | department            | Bz_ap_vendor_rpt           | Many-to-One       |


# Rationale for Key Design Decisions
- All source tables are mirrored exactly in the Bronze layer, preserving raw structure for traceability.
- Primary and foreign key fields are excluded to avoid duplication and maintain rawness.
- Metadata columns (load_timestamp, update_timestamp, source_system) are added for auditability and lineage.
- Table names are prefixed with Bz_ for clarity and layer identification.
- PII fields are classified according to GDPR standards, ensuring compliance.
- Audit table enables tracking of data ingestion and processing status.
- Relationships are documented to support downstream modeling and business logic.
- No physical column names (e.g., _ID) are used in the Bronze model.

# API Cost
apiCost: 0.000500
