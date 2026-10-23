_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Bronze schema drift report for Rental Revenue-to-Cash Reports, comparing the Bronze Logical Model v1 with the Bronze Physical Model v1
## *Version*: 1
## *Updated on*:
_____________________________________________

# Databricks Bronze Schema Drift Report – Rental Revenue-to-Cash Reports

## Inputs and Comparison Mode

| Item | Value |
|---|---|
| Repository | `DIAscendion/Databricks_LakeHouseInADay` (branch `main`) |
| Physical Agent Version 1 | `DI_Databricks_Bronze_Model_Physical/Databricks_Bronze_Model_Physical_1.md` |
| Physical Agent Version 2 | Not available. `Databricks_Bronze_Model_Physical_1.md` is the only file in `DI_Databricks_Bronze_Model_Physical/` |
| Logical Model | `DI_Databricks_Bronze_Model_Logical/Databricks_Bronze_Model_Logical_1.md` |
| Comparison type | **Logical vs. Physical**. Only one physical version exists, so no physical-vs-physical comparison was done |
| Do_You_Need_Any_Changes | Not provided. Treated as "No". No earlier report was found, so this is version 1 |

---

## 1. Schema Comparison Summary

| Metric | Count |
|---|---|
| Tables in Logical model | 6 (5 business tables + `Bz_Audit_Log`) |
| Tables in Physical model | 6 (5 business tables + `bronze.bz_audit_log`) |
| Tables matched | 6 |
| Tables missing in Physical | 0 |
| Tables added in Physical | 0 |
| Columns that are in Physical but not in Logical (identifier keys) | 12 column instances across 5 tables. The Logical model leaves these out by design |
| Columns that are in Logical but not in Physical | 0 |
| Data type mismatches | 1 (`audit_log.processing_time`) |
| Naming or qualification differences | Table casing and prefix (`Bz_` vs `bz_`), schema and catalog qualification |

**Overall status:** The models mostly match. There is **one real type drift**, in `processing_time`. Every other difference is either a documented design choice (the keys left out of the Logical model) or a naming or documentation difference.

---

## 2. Table-Level Differences

| Logical Table | Physical Table | Status | Notes |
|---|---|---|---|
| Bz_Rental_Contracts | bronze.bz_rental_contracts | Matched (naming differs) | Casing differs and the Physical name is schema-qualified |
| Bz_Invoices | bronze.bz_invoices | Matched (naming differs) | Same as above |
| Bz_Cash_Receipts | bronze.bz_cash_receipts | Matched (naming differs) | Same as above |
| Bz_Customer_Master | bronze.bz_customer_master | Matched (naming differs) | Same as above |
| Bz_Branch_Employee | bronze.bz_branch_employee | Matched (naming differs) | Same as above |
| Bz_Audit_Log | bronze.bz_audit_log | Matched, **type drift** | See `processing_time` in Section 3 |

**Catalog qualification:** Logical rationale #7 says storage follows `sunbelt_demo.bronze.*`. The Physical DDL uses the two-part name `bronze.*` and gives no catalog.

---

## 3. Column-Level Differences

### 3.1 Data Type Drift

| Table | Column | Logical Type | Physical Type | Severity |
|---|---|---|---|---|
| Bz_Audit_Log / bronze.bz_audit_log | processing_time | DECIMAL(10,2) ("Load duration in seconds") | TIMESTAMP | **High**. The meaning differs: the Logical model stores a duration, the Physical model stores a point in time |

### 3.2 Columns in Physical Only (identifier keys the Logical model leaves out by design)

Logical Section 3 and rationale #2 state that these keys are deliberately left out of the logical model and kept in the physical model for joins. **Expected difference, not drift.**

| Physical Table | Columns Present Only in Physical | Physical Type |
|---|---|---|
| bronze.bz_rental_contracts | contract_id, customer_id, sales_rep_id | STRING |
| bronze.bz_invoices | invoice_id, contract_id, customer_id | STRING |
| bronze.bz_cash_receipts | receipt_id, invoice_id, customer_id | STRING |
| bronze.bz_customer_master | customer_id | STRING |
| bronze.bz_branch_employee | employee_id, collector_id | STRING |

### 3.3 Matched Columns (name and type identical)

| Table | Matched Columns |
|---|---|
| Rental Contracts | branch_code, equipment_class, contract_start_date, contract_end_date, contract_status (STRING); daily_rate DECIMAL(10,2); file_path, source_system (STRING); file_modification_time, load_timestamp, update_timestamp (TIMESTAMP) |
| Invoices | invoice_date, due_date, invoice_type, currency (STRING); invoice_amount, tax_amount DECIMAL(12,2); lineage and metadata columns |
| Cash Receipts | receipt_date, payment_method (STRING); payment_amount DECIMAL(12,2); lineage and metadata columns |
| Customer Master | customer_name, credit_terms, customer_since, customer_status (STRING); credit_limit DECIMAL(12,2); lineage and metadata columns |
| Branch Employee | employee_name, role, branch_code, region, effective_date (STRING); lineage and metadata columns |
| Audit Log | record_id, source_table, processed_by, status (STRING); load_timestamp (TIMESTAMP) |

### 3.4 Column Ordering (cosmetic)

The Logical model lists `source_system` last. The Physical DDL places it after the business columns and before `file_path`. Delta resolves columns by name, so this has no functional impact.

---

## 4. DDL Differences

The Logical model has no DDL. The comparison below checks the Physical DDL against the column and type definitions in the Logical model.

| Aspect | Logical | Physical DDL | Difference |
|---|---|---|---|
| Table creation | Not specified | `CREATE TABLE IF NOT EXISTS ... USING DELTA` | The Physical model adds the implementation. Consistent with "Delta Lake format" (Logical #7) |
| Constraints | None (keys left out) | None enforced | Consistent |
| `bz_audit_log.processing_time` | DECIMAL(10,2) | `processing_time TIMESTAMP` | **Drift** |
| Catalog | `sunbelt_demo.bronze.*` | `bronze.*` | Qualification differs |
| PII and sensitivity | PII/Sensitive tags on customer_name, employee_name, credit_limit, credit_terms | No COMMENT, TAG, or masking in the DDL | The PII classification is not carried into the physical DDL |
| Relationships | Includes Collector → Sales Rep assignment (Bz_Branch_Employee self-relationship) | `collector_id` exists, but the Physical relationship table (Section 8) does not list the collector relationship | Documentation gap only |

---

## 5. Potential Impact and Recommendations

| # | Finding | Impact | Recommendation |
|---|---|---|---|
| 1 | `processing_time` is DECIMAL(10,2) in Logical and TIMESTAMP in Physical | Audit loads may fail or store wrong values. Any duration metric (e.g. load-time SLA) cannot be computed from a TIMESTAMP | Choose one meaning. To keep the Logical intent, change the Physical type to DECIMAL(10,2). If a timestamp is actually needed, update the Logical model and consider a separate `processing_duration_sec` column |
| 2 | Catalog qualification differs (`sunbelt_demo.bronze` vs `bronze`) | Tables may be created in whichever catalog is current at run time | Fully qualify the DDL as `sunbelt_demo.bronze.bz_*`, or confirm the default catalog in the pipeline |
| 3 | PII classification is missing from the Physical DDL | Governance and masking may be skipped | Add Unity Catalog column tags or comments, or masking policies, for customer_name, employee_name, credit_limit, and credit_terms |
| 4 | Table name casing (`Bz_` vs `bz_`) | None functionally, because Databricks identifiers are case-insensitive | Standardize documentation on `bz_` lowercase |
| 5 | Identifier keys present only in Physical | None. This is a documented design choice | No action. Keep the exclusion documented |
| 6 | The Physical model does not document the collector relationship | Downstream join design could miss it | Add `collector_id` → `employee_id` to the Physical relationship table |

---

## 6. Unresolved Items and Limitations

- Only Physical Version 1 exists, so a **physical-vs-physical drift comparison was not possible**. Version-to-version drift can be detected once a Physical Version 2 is produced.
- The Logical model has no DDL, so the DDL comparison is limited to column names and data types.
- The source schema `Input/rental_revenue_to_cash_bronze_schema.sql` was not part of this stage's inputs. Which `processing_time` type is correct cannot be checked against the source.
- No deployed Databricks metastore or live table schema was inspected. This report compares design documents only.
- Do_You_Need_Any_Changes and Required Changes were not provided, so the run assumed "No".

---

## 7. apiCost

apiCost: 0.000000
