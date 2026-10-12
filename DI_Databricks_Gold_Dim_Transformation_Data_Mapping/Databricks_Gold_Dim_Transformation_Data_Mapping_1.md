_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Attribute-level Gold dimension data mapping from Silver to Gold for Rental Revenue-to-Cash dimension entities with Databricks-compatible transformation and validation rules.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Dim Transformation Data Mapping

## 1. Overview
This document defines the detailed attribute-level data mapping for Gold dimension tables in the Rental Revenue-to-Cash lakehouse flow. The mapping is derived primarily from the available Silver physical model and uses Databricks and PySpark-compatible transformation logic to standardize, validate, cleanse, and conform dimension data before Gold publication. Because the referenced Gold Dimension Transformation Recommender input file was not available in the repository path at runtime, the transformation recommendations below were inferred from the Silver model structure, dimension modeling best practices, and the stated requirements for category mappings, hierarchical relationships, surrogate key generation, standardization, deduplication, and enforcement of conformed business definitions.

Key considerations applied in this mapping:
- Gold layer target is restricted to dimension-oriented entities.
- Surrogate keys are generated for each Gold dimension table.
- Business keys from Silver are preserved for traceability.
- Text attributes are standardized using trim, case normalization, and null-safe defaulting where appropriate.
- Effective deduplication is applied using business keys and latest update metadata.
- Validation rules align with expected reporting quality requirements such as non-null keys, allowed domain values, uniqueness, and datatype conformity.
- Hierarchical attributes such as branch-to-region and employee-to-branch are preserved for downstream analytics.
- All logic is implementable in Databricks using PySpark DataFrame transformations and Delta Lake merge patterns.

## 2. Assumptions and Input Notes
| Input | Status | Notes |
|---|---|---|
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Available | Used as the primary schema source for Silver entities and attributes. |
| `DI_Databricks_Gold_Dim_Transformation_Recommender/Databricks_Gold_Dim_Transformation_Recommender_1.md` | Not Available | 404 in repository path; transformation guidance inferred from requirements and available schema. |

## 3. Dimension Mapping Approach
The following Gold dimension tables are identified from the Silver model as the most appropriate conformed dimensions:
- `gold.dim_customer`
- `gold.dim_branch_employee`
- `gold.dim_rental_contract`

These tables support dimensional analytics by customer, branch/employee assignment, and contract master context. Fact-like transactional entities such as invoices and cash receipts are excluded from this dimension-specific mapping.

## 4. Data Mapping for Dimension Tables

| Target Layer | Target Table | Target Field | Source Layer | Source Table | Source Field | Validation Rule | Transformation Rule |
|---|---|---|---|---|---|---|---|
| Gold | gold.dim_customer | customer_dim_sk | Silver | silver.si_customer_master | customer_id | Must be generated and unique for each retained customer record; cannot be null. | Generate surrogate key using deterministic hash or sequence pattern such as `xxhash64(customer_id)` or Delta identity strategy for Gold dimension loading. |
| Gold | gold.dim_customer | customer_id | Silver | silver.si_customer_master | customer_id | Cannot be null or blank; must be unique after deduplication. | Trim whitespace; preserve business key; deduplicate by `customer_id` selecting latest `update_date`, else latest `load_date`. |
| Gold | gold.dim_customer | customer_name | Silver | silver.si_customer_master | customer_name | Cannot be null for active customers; length should be > 1 after trim. | Standardize with `trim`, collapse repeated spaces, convert to initcap or business-approved proper case, default unknowns to `Unknown Customer` when business key exists but name missing. |
| Gold | gold.dim_customer | credit_terms | Silver | silver.si_customer_master | credit_terms | Must conform to approved terms domain if available; invalid values flagged for remediation. | Trim and uppercase; map synonymous values to standard set, e.g. `NET30`, `NET 30`, `N30` to `NET 30`. |
| Gold | gold.dim_customer | credit_limit | Silver | silver.si_customer_master | credit_limit | Must be numeric and non-negative; null allowed only if source policy permits. | Cast to `DECIMAL(18,2)`; replace negative invalid values with null and route to DQ exception flow if required. |
| Gold | gold.dim_customer | customer_since_date | Silver | silver.si_customer_master | customer_since | Must be a valid date; cannot be future dated unless explicitly allowed. | Rename for Gold clarity; preserve as date; invalid dates rejected or quarantined upstream. |
| Gold | gold.dim_customer | customer_status | Silver | silver.si_customer_master | customer_status | Must belong to accepted domain such as `ACTIVE`, `INACTIVE`, `SUSPENDED`; blank not allowed. | Trim and uppercase; normalize variants like `Active`, `A`, `active` to `ACTIVE`. |
| Gold | gold.dim_customer | over_limit_indicator | Silver | silver.si_customer_master | over_limit_indicator | Must be `Y` or `N` when present. | Standardize boolean indicator from source variants such as `true/false`, `yes/no`, `1/0` into `Y` or `N`. |
| Gold | gold.dim_customer | source_system | Silver | silver.si_customer_master | source_system | Cannot be null for lineage. | Pass through as-is after trim normalization. |
| Gold | gold.dim_customer | record_effective_timestamp | Silver | silver.si_customer_master | update_date | Must be a valid timestamp. | Use `update_date` if present, otherwise `load_date` for latest conformed record tracking. |
| Gold | gold.dim_customer | record_load_timestamp | Silver | silver.si_customer_master | load_date | Must be a valid timestamp. | Pass through for auditability. |
| Gold | gold.dim_branch_employee | branch_employee_dim_sk | Silver | silver.si_branch_employee | employee_id | Must be generated and unique per retained employee-branch assignment grain. | Generate surrogate key using deterministic hash on `employee_id`, `branch_code`, and `effective_date` or sequence-based Gold key generation. |
| Gold | gold.dim_branch_employee | employee_id | Silver | silver.si_branch_employee | employee_id | Cannot be null or blank. | Trim and preserve business key; deduplicate using latest effective assignment where required. |
| Gold | gold.dim_branch_employee | employee_name | Silver | silver.si_branch_employee | employee_name | Cannot be null for active employee assignments; must be printable text. | Apply `trim`, remove extra spaces, convert to proper case for display standardization. |
| Gold | gold.dim_branch_employee | role | Silver | silver.si_branch_employee | role | Must match approved role domain where possible. | Trim and uppercase; normalize synonyms such as `sales rep`, `SalesRep`, `SALES_REP` to `SALES_REP`. |
| Gold | gold.dim_branch_employee | branch_code | Silver | silver.si_branch_employee | branch_code | Cannot be null or blank; format must match branch code standard. | Trim and uppercase; remove embedded spaces if not meaningful. |
| Gold | gold.dim_branch_employee | region | Silver | silver.si_branch_employee | region | Cannot be null for active branch assignments. | Trim and uppercase; map regional aliases to conformed naming, preserving branch-to-region hierarchy. |
| Gold | gold.dim_branch_employee | collector_id | Silver | silver.si_branch_employee | collector_id | Optional, but if present must be valid text and standardized. | Trim; preserve nullable collector assignment for collections reporting hierarchy. |
| Gold | gold.dim_branch_employee | effective_date | Silver | silver.si_branch_employee | effective_date | Must be valid date; cannot be null if used in assignment history grain. | Preserve date and use for latest-row selection or slowly-changing assignment logic if implemented. |
| Gold | gold.dim_branch_employee | source_system | Silver | silver.si_branch_employee | source_system | Cannot be null for lineage. | Pass through after trim. |
| Gold | gold.dim_branch_employee | record_effective_timestamp | Silver | silver.si_branch_employee | update_date | Must be valid timestamp. | Use latest of `update_date` or `load_date` to represent published record timestamp. |
| Gold | gold.dim_branch_employee | record_load_timestamp | Silver | silver.si_branch_employee | load_date | Must be valid timestamp. | Pass through for audit. |
| Gold | gold.dim_rental_contract | rental_contract_dim_sk | Silver | silver.si_rental_contracts | contract_id | Must be generated and unique for each retained contract dimension row. | Generate surrogate key using deterministic hash or sequence based on `contract_id`. |
| Gold | gold.dim_rental_contract | contract_id | Silver | silver.si_rental_contracts | contract_id | Cannot be null or blank; must be unique after deduplication. | Trim and preserve business key; deduplicate by `contract_id` using latest `update_date` or `load_date`. |
| Gold | gold.dim_rental_contract | customer_id | Silver | silver.si_rental_contracts | customer_id | Cannot be null where contract is valid; should match conformed customer key domain. | Trim and preserve for customer dimension linkage; optionally validate against `gold.dim_customer.customer_id`. |
| Gold | gold.dim_rental_contract | branch_code | Silver | silver.si_rental_contracts | branch_code | Cannot be null for valid contracts. | Trim and uppercase for conformed branch hierarchy integration. |
| Gold | gold.dim_rental_contract | sales_rep_id | Silver | silver.si_rental_contracts | sales_rep_id | Optional or mandatory based on business rule; if present must be valid text. | Trim and preserve for employee hierarchy linkage to `gold.dim_branch_employee.employee_id`. |
| Gold | gold.dim_rental_contract | equipment_class | Silver | silver.si_rental_contracts | equipment_class | Must belong to approved equipment class domain if maintained. | Trim and uppercase; normalize category labels to standard class values for analytics. |
| Gold | gold.dim_rental_contract | contract_start_date | Silver | silver.si_rental_contracts | contract_start_date | Must be valid date; should not exceed contract_end_date when end date exists. | Preserve typed date from Silver; enforce chronological validation against end date. |
| Gold | gold.dim_rental_contract | contract_end_date | Silver | silver.si_rental_contracts | contract_end_date | Must be valid date when present; should be >= start date. | Preserve typed date; allow null for open contracts. |
| Gold | gold.dim_rental_contract | contract_status | Silver | silver.si_rental_contracts | contract_status | Must belong to approved status domain such as `ACTIVE`, `CLOSED`, `CANCELLED`, `EXPIRED`. | Trim and uppercase; normalize source variants to conformed Gold status labels. |
| Gold | gold.dim_rental_contract | daily_rate | Silver | silver.si_rental_contracts | daily_rate | Must be numeric and non-negative. | Cast/retain as `DECIMAL(18,2)`; invalid negatives flagged and optionally quarantined. |
| Gold | gold.dim_rental_contract | source_system | Silver | silver.si_rental_contracts | source_system | Cannot be null for lineage. | Pass through after trim. |
| Gold | gold.dim_rental_contract | record_effective_timestamp | Silver | silver.si_rental_contracts | update_date | Must be valid timestamp. | Use `update_date` else `load_date` for current conformed record timing. |
| Gold | gold.dim_rental_contract | record_load_timestamp | Silver | silver.si_rental_contracts | load_date | Must be valid timestamp. | Pass through for operational traceability. |

## 5. Complex Transformation and Business Rule Notes

### 5.1 Surrogate Key Generation
Gold dimensions should use surrogate keys to decouple analytics from mutable business keys. In Databricks PySpark, this can be implemented through:
- Deterministic hash keys for repeatable batch rebuilds.
- Delta identity columns for warehouse-managed sequential keying.
- Window-based sequence assignment when deterministic ordering is available.

### 5.2 Deduplication Strategy
For all dimensions, deduplicate using the business key and latest operational timestamp:
1. Partition by natural key such as `customer_id`, `contract_id`, or `employee_id + branch_code + effective_date`.
2. Order by `update_date` descending, then `load_date` descending.
3. Retain row number 1.

### 5.3 Standardization Rules
The following common rules apply across all text attributes:
- `trim()` leading and trailing spaces.
- Replace repeated internal whitespace with a single space.
- Convert code-like fields to uppercase.
- Convert human-readable names to proper case where reporting-friendly.
- Null-safe handling using default placeholders only where business-approved.

### 5.4 Hierarchical Relationship Handling
Dimension data should preserve hierarchy-enabling fields:
- Customer linked to contracts through `customer_id`.
- Contract linked to sales representative through `sales_rep_id`.
- Employee linked to branch and region through `branch_code` and `region`.
These are retained in Gold dimensions to support drill-down and conformed reporting.

### 5.5 Validation and Cleansing Rules
- Reject blank or null natural keys for conformed dimensions.
- Validate dates for format and chronology.
- Validate numeric fields for non-negative financial values.
- Standardize domains for statuses, roles, regions, and credit terms.
- Remove duplicate rows using latest-record survivorship.
- Preserve lineage fields for exception handling and audit traceability.

## 6. PySpark and Databricks Implementation Guidance
Typical implementation functions:
- `trim`, `upper`, `initcap`, `regexp_replace`, `coalesce`, `when`
- `to_date`, `cast`, `current_timestamp`
- `row_number` over window specifications for deduplication
- `merge` into Delta Gold tables for incremental publishing
- `xxhash64` or `sha2` for deterministic surrogate key derivation where appropriate

Illustrative deduplication pattern:
```python
from pyspark.sql import functions as F, Window

w = Window.partitionBy("customer_id").orderBy(F.col("update_date").desc_nulls_last(), F.col("load_date").desc_nulls_last())

dim_customer = (
    silver_customer
    .withColumn("customer_id", F.trim(F.col("customer_id")))
    .withColumn("customer_name", F.initcap(F.regexp_replace(F.trim(F.col("customer_name")), r"\\s+", " ")))
    .withColumn("customer_status", F.upper(F.trim(F.col("customer_status"))))
    .withColumn("rn", F.row_number().over(w))
    .filter(F.col("rn") == 1)
    .withColumn("customer_dim_sk", F.xxhash64("customer_id"))
)
```

## 7. Data Quality Summary
| Rule Category | Applied To | Description |
|---|---|---|
| Mandatory key validation | All Gold dimensions | Business key fields must not be null or blank. |
| Domain standardization | Status, role, region, credit terms, equipment class | Normalize to approved conformed values. |
| Numeric validation | credit_limit, daily_rate | Must be numeric and non-negative. |
| Date validation | customer_since_date, effective_date, contract dates | Dates must be valid and chronologically consistent. |
| Deduplication | All dimensions | Latest valid record retained per business key. |
| Lineage enforcement | source_system, load/update timestamps | Preserve operational traceability to Silver source. |

## 8. apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Gold_Dim_Transformation_Data_Mapping_1.md](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Dim_Transformation_Data_Mapping/Databricks_Gold_Dim_Transformation_Data_Mapping_1.md)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Data_Mapping
pipelineID : 14671
