_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Physical data model for the Bronze layer of AscHeavyRentals, including DDLs for all raw ingestion tables, audit table, and conceptual relationships.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Bronze Model Physical — AscHeavyRentals

This document defines the physical data model for the Bronze layer of the AscHeavyRentals Lakehouse, translating the logical model and process tables into Databricks Delta Lake DDLs. The Bronze layer stores raw, ingested data with minimal transformation and includes metadata for governance and lineage.

---

## Table of Contents
- [Bronze Layer DDL Scripts](#bronze-layer-ddl-scripts)
- [Audit Table DDL](#audit-table-ddl)
- [Conceptual Data Model Diagram (Tabular Form)](#conceptual-data-model-diagram-tabular-form)
- [Assumptions and Design Decisions](#assumptions-and-design-decisions)
- [API Cost](#api-cost)

---

## Bronze Layer DDL Scripts

All tables are created in the `bronze` schema, use Delta format, and include metadata columns for governance.

### 1. Purchase Order Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_purchase_order (
  po_number STRING,
  po_date DATE,
  vendor_id STRING,
  equipment_id STRING,
  equipment_class STRING,
  cost_amount DOUBLE,
  status STRING,
  received_date DATE,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 2. AR by Sales Rep Weekly Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_ar_by_sales_rep_weekly (
  week_ending DATE,
  sales_rep_id STRING,
  region STRING,
  revenue_amount DOUBLE,
  contract_count INT,
  ar_balance DOUBLE,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 3. AR Reports Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_ar_reports (
  invoice_id STRING,
  customer_id STRING,
  invoice_date DATE,
  due_date DATE,
  paid_date DATE,
  invoice_amount DOUBLE,
  open_balance DOUBLE,
  aging_bucket STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 4. Bulk Lot Report Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_bulk_lot_report (
  equipment_id STRING,
  equipment_class STRING,
  segment STRING,
  region STRING,
  original_cost DOUBLE,
  acquisition_date DATE,
  status STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 5. Equipment Disposals Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_equipment_disposals (
  equipment_id STRING,
  disposal_date DATE,
  original_cost DOUBLE,
  book_value DOUBLE,
  sale_proceeds DOUBLE,
  disposal_method STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 6. GL Detail Asset Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_gl_detail_asset (
  gl_line_id STRING,
  date DATE,
  equipment_id STRING,
  account STRING,
  transaction_type STRING,
  amount DOUBLE,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 7. GL Detail Data Lake Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_gl_detail_datalake (
  gl_line_id STRING,
  date DATE,
  account STRING,
  department STRING,
  amount DOUBLE,
  pl_line_mapped STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 8. Invoice Detail Master Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_invoice_detail_master (
  invoice_line_id STRING,
  invoice_date DATE,
  customer_id STRING,
  revenue_type STRING,
  segment STRING,
  region STRING,
  rate DOUBLE,
  time_on_rent_days INT,
  amount DOUBLE,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 9. Rental Contracts by Rep Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_rental_contracts_by_rep (
  contract_id STRING,
  open_date DATE,
  sales_rep_id STRING,
  equipment_class STRING,
  rate_realization_pct DOUBLE,
  time_on_rent_days INT,
  region STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

### 10. AP Vendor Report Table
```sql
CREATE TABLE IF NOT EXISTS bronze.bz_ap_vendor_rpt (
  ap_id STRING,
  vendor_id STRING,
  invoice_date DATE,
  amount DOUBLE,
  category STRING,
  paid_flag STRING,
  load_timestamp TIMESTAMP,
  update_timestamp TIMESTAMP,
  source_system STRING
) USING DELTA;
```

---

## Audit Table DDL

```sql
CREATE TABLE IF NOT EXISTS bronze.bz_audit (
  record_id STRING,
  source_table STRING,
  load_timestamp TIMESTAMP,
  processed_by STRING,
  processing_time DOUBLE,
  status STRING
) USING DELTA;
```

---

## Conceptual Data Model Diagram (Tabular Form)

| Source Table                        | Relationship Key Field   | Target Table                     | Relationship Type |
|-------------------------------------|-------------------------|----------------------------------|-------------------|
| bz_purchase_order                   | equipment_id            | bz_bulk_lot_report               | Many-to-One       |
| bz_bulk_lot_report                  | equipment_id            | bz_equipment_disposals           | One-to-Many       |
| bz_ar_by_sales_rep_weekly           | sales_rep_id, region    | bz_rental_contracts_by_rep       | Many-to-One       |
| bz_ar_reports                       | invoice_id              | bz_invoice_detail_master         | One-to-Many       |
| bz_invoice_detail_master            | customer_id             | bz_ar_reports                    | Many-to-One       |
| bz_gl_detail_asset                  | equipment_id            | bz_bulk_lot_report               | Many-to-One       |
| bz_gl_detail_datalake               | gl_line_id              | bz_gl_detail_asset               | Many-to-One       |
| bz_ap_vendor_rpt                    | vendor_id               | bz_purchase_order                | Many-to-One       |

---

## Assumptions and Design Decisions
- All tables are created in the `bronze` schema and use Delta Lake storage.
- No primary keys, foreign keys, or constraints are enforced at the Bronze layer.
- All tables include metadata columns: `load_timestamp`, `update_timestamp`, and `source_system` for governance and lineage.
- Data types are chosen for compatibility with Databricks SQL and PySpark.
- The Audit table is used for tracking ingestion and processing status.
- Table relationships are documented for downstream modeling but not enforced in the Bronze layer.
- All DDLs use `CREATE TABLE IF NOT EXISTS` to support idempotent deployment.

---

## API Cost

apiCost: 0.002000
