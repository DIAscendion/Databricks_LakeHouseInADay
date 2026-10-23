_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Databricks Bronze layer PII detection and classification for Rental Revenue to Cash Reports
## *Version*: 1
## *Updated on*:
## *Input Files*: DI_Databricks_Bronze_Metadata_Discovery/Metadata_Discovery_Output.md (v1), DI_Databricks_Bronze_Data_Profiler_SQL/Profiler_Queries.sql (v1)
## *Repository*: DIAscendion/Databricks_LakeHouseInADay (branch: main)
## *Do_You_Need_Any_Changes*: No (Mode 1. Initial version: no earlier PII report existed in DI_Databricks_Bronze_PII_Detection/)
_____________________________________________

## 1. Input Analysis

| Input | Content Used | Notes |
|---|---|---|
| Metadata Discovery Output (v1) | 5 verified Bronze tables (52 columns), data types, column comments, source systems, logical relationships, known data quality issues | Bz_Branch_Master is "Recommended – Not Verified" and has no DDL, so it is out of scope |
| Data Profiler SQL (v1) | Profiling query design (null/distinct counts, value frequencies, string patterns, duplicates, orphans) | **NOT EXECUTED.** No profiling results exist. The evidence is limited to the schema, column comments, documented sample-data observations and source-system context |

**Domain context:** This is B2B equipment rental, covering revenue, billing, AR, collections and cash. The customers appear to be business entities ("legal/trade name", credit terms, credit limits). The employees (sales reps and collectors) are natural persons.

**Evidence rules applied:** A column name alone was not treated as proof. Each classification combines (a) the column comment or semantics from the metadata, (b) the source system (e.g. HR_FEED, CRM), (c) the documented DQ and sample observations, and (d) the possibility of linking the column to other columns. No personal values are reproduced in this report.

## 2. PII Classification

Legend. **Category:** Direct Identifier (DI), Indirect Identifier (II), Sensitive Personal Data (SPD, GDPR Art. 9/10), Financial Personal Info (FPI), Non-PII, Requires Validation (RV). **Sensitivity:** High / Medium / Low / None. **Confidence:** High / Medium / Low.

### 2.1 Bz_Branch_Employee (source: HR_FEED, HR_FEED_OLD)

| Column | Category | Sensitivity | Confidence | Evidence-Based Reasoning (GDPR) |
|---|---|---|---|---|
| employee_name | DI | High | High | Comment: "Raw employee name". Source is an HR feed, and roles are Sales Rep or Collector, so these are natural persons. A name directly identifies a data subject (Art. 4(1)) |
| employee_id | II | Medium | High | Internal employee identifier from the HR feed. It is pseudonymous but can be linked to employee_name in the same table, so it is personal data under Recital 26 |
| collector_id | II | Medium | High | Comment says it references a collector's employee_id. It links one employee to another natural person |
| role | II | Low | High | Job role (Sales Rep, Collector). Combined with branch_code and region, it can narrow down to an individual in small branches |
| branch_code | II | Low | Medium | Work location. Becomes quasi-identifying when combined with role and region |
| region | II | Low | Medium | Coarse work location. Its re-identification risk is low on its own |
| effective_date | II | Low | Medium | Assignment or employment-change date. It is part of the HR employment history, so it is personal data when linked |
| source_system | Non-PII | None | High | System code (HR_FEED / HR_FEED_OLD) |
| file_path | RV | Low | Low | Batch file reference. It is unknown whether HR file names embed personal attributes. Check this when profiling is executed |
| file_modification_time | Non-PII | None | High | Technical ingestion timestamp |

### 2.2 Bz_Customer_Master (source: SUNBELT_CORE, LEGACY_SE)

| Column | Category | Sensitivity | Confidence | Evidence-Based Reasoning (GDPR) |
|---|---|---|---|---|
| customer_name | RV (potential DI) | Medium | Medium | Comment: "Raw legal/trade name". The domain is B2B, so names are mostly companies, and those are not personal data. Sole traders or individuals named as the customer would be direct identifiers. The profiler's name-pattern query has not been executed, so this cannot be confirmed |
| customer_id | II | Low | Medium | Account identifier. It is personal data only where the customer is a natural person or sole trader (see customer_name) |
| credit_limit | FPI (conditional) | Medium | Medium | Credit exposure. For individuals or sole traders it is financial personal information that reflects creditworthiness. For companies it is commercially confidential only |
| credit_terms | FPI (conditional) | Low | Medium | Payment terms (e.g. Net 30). These are personal only when linked to an individual customer |
| customer_status | FPI (conditional) | Medium | Medium | Values include "Suspended", which indicates a credit or collections standing. That is sensitive for individuals, but it is not Art. 9 data |
| customer_since | II | Low | Medium | Relationship start date. It is a quasi-identifier when linked |
| source_system | Non-PII | None | High | System code |
| file_path | RV | Low | Low | File reference. Its content has not been profiled |
| file_modification_time | Non-PII | None | High | Technical timestamp |

### 2.3 Bz_Rental_Contracts (source: SUNBELT_CORE, LEGACY_SE, LEGACY_MW)

| Column | Category | Sensitivity | Confidence | Evidence-Based Reasoning (GDPR) |
|---|---|---|---|---|
| sales_rep_id | II | Medium | High | References employee_id in Bz_Branch_Employee, so it links each contract to a named employee. This enables performance attribution of the sales rep |
| customer_id | II | Low | Medium | Customer reference. Personal only for individual customers |
| contract_id | Non-PII | None | High | Business transaction identifier |
| branch_code | Non-PII | None | High | Organizational code |
| equipment_class | Non-PII | None | High | Free-text equipment category. It could contain free-text notes, but no evidence suggests that |
| contract_start_date / contract_end_date | Non-PII | None | Medium | Transaction dates. Personal only by linkage to an individual customer |
| contract_status | Non-PII | None | High | Business status |
| daily_rate | Non-PII | None | High | Commercial pricing |
| source_system, file_path, file_modification_time | Non-PII | None | High | Lineage columns |

### 2.4 Bz_Invoices (source: SUNBELT_CORE, LEGACY_SE, LEGACY_MW)

| Column | Category | Sensitivity | Confidence | Evidence-Based Reasoning (GDPR) |
|---|---|---|---|---|
| customer_id | II | Low | Medium | Customer reference. Personal only for individual customers |
| invoice_amount | FPI (conditional) | Low | Medium | Billing amount. It is financial personal information only when linked to an individual customer |
| tax_amount | FPI (conditional) | Low | Medium | Same reasoning as invoice_amount |
| invoice_id, contract_id | Non-PII | None | High | Business transaction identifiers |
| invoice_date, due_date | Non-PII | None | Medium | Transaction dates |
| invoice_type, currency | Non-PII | None | High | Reference codes |
| source_system, file_path, file_modification_time | Non-PII | None | High | Lineage columns |

### 2.5 Bz_Cash_Receipts (source: LOCKBOX_FEED)

| Column | Category | Sensitivity | Confidence | Evidence-Based Reasoning (GDPR) |
|---|---|---|---|---|
| customer_id | II | Low | Medium | Payer reference. Personal only for individual customers |
| payment_amount | FPI (conditional) | Low | Medium | Payment behaviour. Personal for individual payers |
| payment_method | FPI (conditional) | Low | Medium | Categorical values (ACH, Check, Credit Card, Wire). No account or card numbers are documented in the schema |
| receipt_date | Non-PII | None | Medium | Transaction date |
| receipt_id, invoice_id | Non-PII | None | High | Transaction identifiers |
| source_system, file_path, file_modification_time | Non-PII | None | High | Lineage columns. Lockbox file names should be confirmed when profiling is executed |

**Sensitive Personal Data (GDPR Art. 9/10):** No column in the documented schema contains special-category or criminal data. There are no bank account numbers, card numbers (PCI), national IDs, addresses, emails or phone numbers.

## 3. Table-Level PII Summary

| Table | Total Cols | DI | II | SPD | FPI | RV | Non-PII | Overall Sensitivity | Data Subjects |
|---|---|---|---|---|---|---|---|---|---|
| Bz_Branch_Employee | 10 | 1 | 6 | 0 | 0 | 1 | 2 | **High** | Employees |
| Bz_Customer_Master | 9 | 0 (1 potential) | 2 | 0 | 3 | 2 | 2 | **Medium** | Customers (individuals/sole traders, if any) |
| Bz_Rental_Contracts | 12 | 0 | 2 | 0 | 0 | 0 | 10 | Low–Medium | Employees (via sales_rep_id), customers |
| Bz_Invoices | 12 | 0 | 1 | 0 | 2 | 0 | 9 | Low | Customers |
| Bz_Cash_Receipts | 9 | 0 | 1 | 0 | 2 | 0 | 6 | Low | Customers |
| **Total** | **52** | **1** | **12** | **0** | **7** | **3** | **29** | | |

## 4. Handling Recommendations

1. **Bronze access control (Unity Catalog):** Restrict SELECT on Bz_Branch_Employee and Bz_Customer_Master to data-engineering and steward groups. Tag columns with UC tags, e.g. `pii=direct|indirect|financial` and `sensitivity=high|medium|low`.
2. **Column masking:** Apply a UC column mask to `employee_name` (High) for all non-privileged groups. Apply a conditional mask to `customer_name` and `credit_limit` until the validation in Section 5 confirms whether individuals are present.
3. **Pseudonymisation in Silver:** Replace `employee_id`, `collector_id` and `sales_rep_id` with salted hash or surrogate keys where reporting needs no identity. Keep the mapping table in a restricted schema.
4. **Gold / reporting:** Sales Rep and Collector performance dashboards process employee personal data. Document the lawful basis (legitimate interest / employment context), limit visibility to the people who need it, and consider aggregation for broad audiences.
5. **Data minimisation:** Do not propagate `file_path` into Gold. Exclude employee attributes from customer-facing datasets.
6. **Retention and erasure:** Bronze is append-only. Define retention for HR_FEED_OLD stale records and a GDPR erasure/rectification process (Delta `DELETE` + `VACUUM`) for employee records and individual customers.
7. **Audit:** Enable UC audit logs and lineage for every table tagged as PII.

## 5. Unresolved Classifications / Limitations

| Item | Status | Required Action |
|---|---|---|
| customer_name (and the dependent customer_id, credit_limit, credit_terms, customer_status, amounts) | Requires Validation | Run the Section B/F profiler queries and steward review to find natural-person or sole-trader names, e.g. those without legal-entity suffixes |
| file_path (all tables) | Requires Validation | Inspect the file naming convention for embedded personal attributes |
| equipment_class free text | Low risk, unverified | Confirm there are no free-text notes containing names |
| Profiler not executed | Limitation | No row counts, value patterns or results are available. Confidence is capped at Medium where the classification depends on actual values |
| Bz_Branch_Master | Out of scope | No DDL or source exists. Reassess if it is added later |
| Undocumented columns | Limitation | Only the documented schema was assessed. No live source connection was made |

## 6. API Cost

apiCost: Not Available
