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
| sales_rep_id       | Identifies employees (GDPR sensitive)             |
| region             | May indirectly identify individuals if granular   |
| invoice_date       | Transaction date, sensitive in context            |
| paid_date          | Payment date, sensitive in financial context      |
| due_date           | Payment due date, sensitive in financial context  |
| acquisition_date   | Asset acquisition date, sensitive in asset context|
| disposal_date      | Asset disposal date, sensitive in asset context   |


# Bronze Layer Logical Model

## Table: Bz_purchase_order
**Description:** Raw purchase order lines from source system.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| po_number        | Purchase order number               | String      |
| po_date          | Date PO was issued                  | Date        |
| vendor_id        | Vendor identifier                   | String      |
| equipment_id     | Equipment unit purchased            | String      |
| equipment_class  | Equipment class/type                | String      |
| cost_amount      | PO line cost amount                 | Decimal     |
| status           | Open / Received                     | String      |
| received_date    | Date equipment was received         | Date        |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_ar_by_sales_rep_weekly
**Description:** Weekly AR reports by sales rep.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| week_ending      | Week-ending date                    | Date        |
| sales_rep_id     | Sales rep identifier                | String      |
| region           | Region name                         | String      |
| revenue_amount   | Revenue booked that week            | Decimal     |
| contract_count   | Contracts opened that week          | Integer     |
| ar_balance       | Outstanding AR balance              | Decimal     |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_ar_reports
**Description:** AR transactions and invoices.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| invoice_id       | Invoice identifier                  | String      |
| customer_id      | Customer identifier                 | String      |
| invoice_date     | Date invoiced                       | Date        |
| due_date         | Payment due date                    | Date        |
| paid_date        | Date paid (null if open)            | Date        |
| invoice_amount   | Total invoice amount                | Decimal     |
| open_balance     | Remaining unpaid balance            | Decimal     |
| aging_bucket     | Aging category                      | String      |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_bulk_lot_report
**Description:** Fleet snapshot by equipment unit.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| equipment_id     | Equipment unit identifier           | String      |
| equipment_class  | Equipment class/type                | String      |
| segment          | General Tool / Specialty            | String      |
| region           | Region name                         | String      |
| original_cost    | Original cost (OEC)                 | Decimal     |
| acquisition_date | Date acquired                       | Date        |
| status           | Owned / On-rent / Idle              | String      |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_equipment_disposals
**Description:** Equipment disposal transactions.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| equipment_id     | Equipment unit disposed             | String      |
| disposal_date    | Date disposed                       | Date        |
| original_cost    | Original cost of the unit           | Decimal     |
| book_value       | Net book value at disposal          | Decimal     |
| sale_proceeds    | Cash proceeds from sale             | Decimal     |
| disposal_method  | Auction / Wholesale / Retail sale   | String      |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_gl_detail_asset
**Description:** GL asset transactions.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| date             | Transaction date                    | Date        |
| equipment_id     | Related equipment unit              | String      |
| account          | GL account name                     | String      |
| transaction_type | Depreciation / Capex / Disposal     | String      |
| amount           | Transaction amount                  | Decimal     |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_gl_detail_datalake
**Description:** GL detail from Data Lake.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| date             | Transaction date                    | Date        |
| account          | GL account name                     | String      |
| department       | Owning department/cost center       | String      |
| amount           | Transaction amount                  | Decimal     |
| pl_line_mapped   | Target management P&L line          | String      |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_invoice_detail_master
**Description:** Invoice line details for master account.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| invoice_date     | Date invoiced                       | Date        |
| customer_id      | Customer identifier                 | String      |
| revenue_type     | Rental/sale/ancillary type          | String      |
| segment          | General Tool / Specialty            | String      |
| region           | Region name                         | String      |
| rate             | Daily/period rental rate            | Decimal     |
| time_on_rent_days| Days on rent                        | Integer     |
| amount           | Line amount                         | Decimal     |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_rental_contracts_by_rep
**Description:** Rental contracts opened by sales rep.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| open_date        | Date contract opened                | Date        |
| sales_rep_id     | Sales rep identifier                | String      |
| equipment_class  | Equipment class/type                | String      |
| rate_realization_pct | Rate realization vs list rate    | Decimal     |
| time_on_rent_days| Time on rent for the contract       | Integer     |
| region           | Region name                         | String      |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |

## Table: Bz_ap_vendor_rpt
**Description:** AP vendor report transactions.

| Column Name      | Description                        | Data Type   |
|------------------|------------------------------------|-------------|
| vendor_id        | Vendor identifier                   | String      |
| invoice_date     | Vendor invoice date                 | Date        |
| amount           | Transaction amount                  | Decimal     |
| category         | Equipment purchase/maintenance/freight | String  |
| paid_flag        | Paid / Open                         | String      |
| load_timestamp   | Data load timestamp                 | Timestamp   |
| update_timestamp | Last update timestamp               | Timestamp   |
| source_system    | Source system name                  | String      |


# Audit Table Design

| Field Name        | Description                                 | Data Type   |
|-------------------|---------------------------------------------|-------------|
| record_id         | Unique record identifier (audit)            | String      |
| source_table      | Source table name                           | String      |
| load_timestamp    | Data load timestamp                         | Timestamp   |
| processed_by      | Processing agent or user                    | String      |
| processing_time   | Processing time duration                    | Decimal     |
| status            | Processing status (success/failure)         | String      |


# Conceptual Data Model Diagram (Tabular Form)

| Source Table                  | Relationship Key Field   | Target Table                  | Relationship Type |
|-------------------------------|-------------------------|------------------------------|-------------------|
| Bz_purchase_order             | equipment_id            | Bz_bulk_lot_report           | One-to-Many       |
| Bz_ar_by_sales_rep_weekly     | sales_rep_id            | Bz_rental_contracts_by_rep    | One-to-Many       |
| Bz_ar_reports                 | customer_id             | Bz_invoice_detail_master      | One-to-Many       |
| Bz_bulk_lot_report            | equipment_id            | Bz_equipment_disposals        | One-to-Many       |
| Bz_gl_detail_asset            | equipment_id            | Bz_bulk_lot_report            | One-to-Many       |
| Bz_invoice_detail_master      | customer_id             | Bz_ap_vendor_rpt              | One-to-Many       |
| Bz_rental_contracts_by_rep    | sales_rep_id            | Bz_ar_by_sales_rep_weekly     | One-to-Many       |


# Rationale for Key Design Decisions
- All source tables are mirrored exactly in the Bronze layer, preserving raw structure.
- Primary and foreign key fields are excluded from the Bronze logical model, focusing on business attributes.
- Consistent naming convention (Bz_ prefix) for Bronze tables.
- Metadata columns (load_timestamp, update_timestamp, source_system) added for lineage and auditability.
- Audit table tracks ingestion and processing status for compliance.
- PII fields are classified per GDPR and business context.
- Relationships are documented based on business keys, not physical IDs.

# Assumptions
- Only business attributes are retained; IDs are excluded.
- Data types are logical, not physical storage types.
- PII classification is based on typical business usage and GDPR.
- Source system names are assumed to be available for lineage.

# API Cost
apiCost: 0.000100

---

**outputURL:** https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Logical
**pipelineID:** 12297