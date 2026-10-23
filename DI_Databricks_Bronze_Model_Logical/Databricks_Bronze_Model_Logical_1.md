_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Databricks Bronze layer logical data model for Rental Revenue-to-Cash Reports
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Bronze Layer Logical Data Model – Rental Revenue-to-Cash Reports

## 1. Overview
This logical model defines the Bronze (raw landing) layer for the Rental Revenue-to-Cash domain on Databricks. Every Bronze table mirrors one source table from `Input/rental_revenue_to_cash_bronze_schema.sql`. Each table is named with the `Bz_` prefix. The model covers rental contracts, invoicing, cash receipts, the customer master, and branch employees (sales reps and collectors). The conceptual model `DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md` supplies the business context and the relationships.

**Inputs used**
| Input | Purpose |
|-------|---------|
| DI_Databricks_Model_Conceptual_Constraints/Rental_Revenue_to_Cash_Reports_Conceptual_1.md | Business entities, attributes, KPIs, and relationships |
| Input/rental_revenue_to_cash_bronze_schema.sql | Source table structures (5 tables) |

## 2. PII Classification
| Table | Column | PII Type | Reason |
|-------|--------|----------|--------|
| Bz_Customer_Master | customer_name | PII (business/individual name) | Can identify a customer, including sole proprietors |
| Bz_Branch_Employee | employee_name | PII (personal name) | Directly identifies an employee |
| Bz_Customer_Master | credit_limit | Sensitive (financial) | Confidential customer financial information |
| Bz_Customer_Master | credit_terms | Sensitive (financial) | Confidential commercial terms |

## 3. Bronze Layer Logical Model

Primary-key and foreign-key identifier fields are left out of the logical model by design. The excluded fields are contract_id, customer_id, sales_rep_id, invoice_id, receipt_id, employee_id, and collector_id. Each table includes these standard metadata columns:
- `load_timestamp`: the time the record was loaded into Bronze
- `update_timestamp`: the time the record was last updated in Bronze
- `source_system`: the originating system

### 3.1 Bz_Rental_Contracts
**Description:** Raw rental contract header data. One row per rental contract as extracted from the branch/legacy rental systems (LEGACY_SE, LEGACY_MW, SUNBELT_CORE).

| Column Name | Data Type | Business Description |
|-------------|-----------|----------------------|
| branch_code | STRING | Raw branch code as recorded. Identifies the operating branch for the contract |
| equipment_class | STRING | Free-text equipment category used for rental revenue and billing mix analysis |
| contract_start_date | STRING | Raw contract start date as received (ISO or MM/DD/YYYY) |
| contract_end_date | STRING | Raw contract end date as received. Blank or a sentinel value for open contracts |
| contract_status | STRING | Raw contract status text (e.g. Open, Closed) |
| daily_rate | DECIMAL(10,2) | Raw daily rental rate. Used for revenue and Average Daily Rate analysis |
| file_path | STRING | Source file/batch reference, for lineage |
| file_modification_time | TIMESTAMP | Write time of the ingested source file |
| load_timestamp | TIMESTAMP | Time the record was loaded into Bronze |
| update_timestamp | TIMESTAMP | Time the record was last updated in Bronze |
| source_system | STRING | Originating system identifier |

### 3.2 Bz_Invoices
**Description:** Raw invoice header data. One row per invoice or credit memo from the branch/legacy billing systems.

| Column Name | Data Type | Business Description |
|-------------|-----------|----------------------|
| invoice_date | STRING | Raw invoice issue date as received (format varies) |
| due_date | STRING | Raw payment due date as received. Can be null |
| invoice_amount | DECIMAL(12,2) | Raw invoice amount. Negative values are credit memos |
| tax_amount | DECIMAL(12,2) | Raw tax amount on the invoice |
| invoice_type | STRING | Invoice type (Standard, Credit Memo, etc.) |
| currency | STRING | ISO currency code |
| file_path | STRING | Source file/batch reference, for lineage |
| file_modification_time | TIMESTAMP | Write time of the ingested source file |
| load_timestamp | TIMESTAMP | Time the record was loaded into Bronze |
| update_timestamp | TIMESTAMP | Time the record was last updated in Bronze |
| source_system | STRING | Originating system identifier |

### 3.3 Bz_Cash_Receipts
**Description:** Raw cash receipt and payment application data. One row per payment (or payment attempt) received through the AR lockbox feed (LOCKBOX_FEED).

| Column Name | Data Type | Business Description |
|-------------|-----------|----------------------|
| receipt_date | STRING | Raw payment receipt date as received. Can be null |
| payment_amount | DECIMAL(12,2) | Raw amount collected in the receipt |
| payment_method | STRING | Payment method (ACH, Check, Credit Card, Wire) |
| file_path | STRING | Source file/batch reference, for lineage |
| file_modification_time | TIMESTAMP | Write time of the ingested source file |
| load_timestamp | TIMESTAMP | Time the record was loaded into Bronze |
| update_timestamp | TIMESTAMP | Time the record was last updated in Bronze |
| source_system | STRING | Originating system identifier |

### 3.4 Bz_Customer_Master
**Description:** Raw customer master data from the CRM/ERP system. One row per customer record as extracted. Records are not deduplicated.

| Column Name | Data Type | Business Description |
|-------------|-----------|----------------------|
| customer_name | STRING | Raw customer legal/trade name. Can be null |
| credit_terms | STRING | Raw credit terms text (e.g. Net 30) |
| credit_limit | DECIMAL(12,2) | Raw approved credit exposure limit |
| customer_since | STRING | Raw customer start date as received. Indicates customer tenure |
| customer_status | STRING | Customer status (Active, Suspended, etc.) |
| file_path | STRING | Source file/batch reference, for lineage |
| file_modification_time | TIMESTAMP | Write time of the ingested source file |
| load_timestamp | TIMESTAMP | Time the record was loaded into Bronze |
| update_timestamp | TIMESTAMP | Time the record was last updated in Bronze |
| source_system | STRING | Originating system identifier |

### 3.5 Bz_Branch_Employee
**Description:** Raw branch employee assignment data for sales reps and collectors from the HR feeds (current and legacy). One row per employee record per feed.

| Column Name | Data Type | Business Description |
|-------------|-----------|----------------------|
| employee_name | STRING | Raw employee name (sales rep or collector) |
| role | STRING | Employee role (Sales Rep, Collector) |
| branch_code | STRING | Raw code of the branch the employee is assigned to |
| region | STRING | Raw region text. Spelling varies by feed |
| effective_date | STRING | Raw effective date of the assignment as received |
| file_path | STRING | Source file/batch reference, for lineage |
| file_modification_time | TIMESTAMP | Write time of the ingested source file |
| load_timestamp | TIMESTAMP | Time the record was loaded into Bronze |
| update_timestamp | TIMESTAMP | Time the record was last updated in Bronze |
| source_system | STRING | Originating system identifier (HR_FEED vs HR_FEED_OLD) |

## 4. Audit Table Design

### 4.1 Bz_Audit_Log
**Description:** Tracks ingestion and processing activity for every Bronze table.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| record_id | STRING | Unique identifier of the audit entry |
| source_table | STRING | Name of the Bronze table that was processed |
| load_timestamp | TIMESTAMP | Time the load was performed |
| processed_by | STRING | User, job, or process that ran the load |
| processing_time | DECIMAL(10,2) | Load duration in seconds |
| status | STRING | Load outcome (Success, Failed, Partial) |

## 5. Conceptual Data Model Diagram (Relationships)
| Source Table | Target Table | Relationship Key Field (business) | Relationship Type |
|--------------|--------------|-----------------------------------|-------------------|
| Bz_Customer_Master | Bz_Rental_Contracts | Customer | One-to-Many |
| Bz_Customer_Master | Bz_Invoices | Customer | One-to-Many |
| Bz_Customer_Master | Bz_Cash_Receipts | Customer | One-to-Many |
| Bz_Rental_Contracts | Bz_Invoices | Contract | One-to-Many |
| Bz_Invoices | Bz_Cash_Receipts | Invoice to Payment Application | One-to-Many |
| Bz_Branch_Employee (Sales Rep) | Bz_Rental_Contracts | Sales Rep | One-to-Many |
| Bz_Branch_Employee (Collector) | Bz_Branch_Employee (Sales Rep) | Collector Assignment | One-to-Many |
| Bz_Branch_Employee | Bz_Rental_Contracts | branch_code | Many-to-Many (via branch) |

```
Bz_Customer_Master 1──* Bz_Rental_Contracts 1──* Bz_Invoices 1──* Bz_Cash_Receipts
        │                        ▲
        └──────1──* Bz_Invoices  │ (Sales Rep)
        └──────1──* Bz_Cash_Receipts
Bz_Branch_Employee ──────────────┘   (branch_code shared with Bz_Rental_Contracts)
```

## 6. Design Rationale and Assumptions
1. **One-to-one source mirroring:** There are exactly five Bronze tables, one for each source table. No entities were added. Conceptual entities such as Region, Date, Equipment Class, Organization Hierarchy, and the Fact entities are derived in Silver/Gold, not landed in Bronze.
2. **Key exclusion:** Source identifier columns used as primary/foreign keys (contract_id, customer_id, sales_rep_id, invoice_id, receipt_id, employee_id, collector_id) are left out of the logical model as the agent standard requires. Section 5 describes relationships in business terms. The physical model keeps these identifiers for joins.
3. **branch_code kept:** No branch source table exists, so `branch_code` is not a foreign key to any Bronze table. It is kept as the only business attribute that identifies a branch, which the reports need (Branch Name, Region rollups).
4. **Raw-but-typed and append-only:** Data types match the source DDL. Dates stay as STRING because source formats are mixed. Known data quality issues (duplicates, nulls, inconsistent ID formats, orphan references, stale HR feed rows) are deliberately left uncleaned and passed to Silver.
5. **Metadata columns:** `load_timestamp` and `update_timestamp` are added to every table. `source_system` already exists in each source table and is kept. The source lineage columns `file_path` and `file_modification_time` are kept.
6. **Credit memos:** Negative invoice amounts are expected business data, not errors.
7. **Storage:** Delta Lake format, following the source convention `sunbelt_demo.bronze.*`.
8. **Audit:** `Bz_Audit_Log` records every load for operational monitoring and traceability.

apiCost: 0.0000
