_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Databricks Gold physical model for Rental Revenue-to-Cash reporting with AP-1 reporting requirements applied in version 2.
## *Version*: 2
## *Updated on*: 
_____________________________________________

# Databricks Gold Model Physical

## Jira Tickets Read
| Ticket Key | Summary | Status |
|---|---|---|
| AP-1 | Reporting Requirements for Rental Revenue-to-Cash | To Do |

## 1. Overview
This Databricks Gold physical data model translates the Rental Revenue-to-Cash Gold logical model and Silver physical model into an implementation-ready Gold layer for governed executive scorecards, rental revenue and billing performance, AR aging and collections, cash application and collector performance, and customer credit risk analytics. Version 2 includes the reporting requirements from Jira ticket AP-1 and preserves version history without overwriting prior outputs.

## 2. Source Inputs and Business Context

### 2.1 Input Files Used
| Input File | Layer | Purpose |
|---|---|---|
| `DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model_Physical_1.md` | Silver Physical | Source of required Silver tables and columns that must be represented in Gold physical design |
| `DI_Databricks_Gold_Model_Logical/Databricks_Gold_Model_Logical_1.md` | Gold Logical | Source of Gold entities, facts, dimensions, aggregates, audit, and error structures |
| `AP-1` | Jira | Reporting requirements and acceptance criteria for Revenue-to-Cash reporting |

### 2.2 Jira-Derived Required Changes Applied
The following required changes came from Jira ticket `AP-1` and are applied in this version:
1. Added executive health score aggregate to support Revenue-to-Cash Executive Scorecard.
2. Included billing performance aggregate for rental revenue, gross billings, net billings, ADR, revenue per contract, and credit memo rate.
3. Included AR aging, cash application, and credit risk fact coverage aligned to the ticket KPIs.
4. Included duplicate-prevention design guidance at reporting grain level in assumptions and update DDL guidance.
5. Included role-aware business descriptions reflecting branch, region, collector, and executive reporting needs.
6. Included conceptual relationship mapping and ER visualization graph based on the ticket conceptual model.

## 3. Gold Layer Physical Design Principles
1. All Gold tables use `CREATE TABLE IF NOT EXISTS`.
2. All relevant Silver business columns are carried forward into Gold tables, either as descriptive dimensional fields, fact-level attributes, or aggregate-supporting columns.
3. Surrogate id fields are added to Gold physical tables as `BIGINT` columns because the instructions require id fields in the physical model.
4. No primary keys, foreign keys, unique constraints, generated identity definitions, or unsupported Databricks Spark SQL constraints are included.
5. `VARCHAR`, `DATE`, `TIMESTAMP`, `INT`, `BIGINT`, and `DECIMAL` are used for Databricks Spark SQL compatibility.
6. All business tables include metadata columns `load_date`, `update_date`, and `source_system`.
7. Delta Lake is the storage format for all Gold tables.
8. Traditional indexes are not created; Databricks optimization guidance is provided using partitioning and `OPTIMIZE ... ZORDER BY`.
9. Error and audit tables are included for Gold layer operations and governance.
10. Version 2 description references Jira ticket key `AP-1` as requested.

## 4. Gold Layer DDL Scripts

### 4.1 Dimension Tables DDL Script

#### 4.1.1 `gold.dim_date`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_date (
  date_sk BIGINT,
  reporting_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  number_of_days_in_period INT,
  period_week_start_date DATE,
  period_week_end_date DATE,
  period_month_start_date DATE,
  period_month_end_date DATE,
  fiscal_quarter VARCHAR(20),
  fiscal_year INT,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (period_type, load_date);
```

```sql
OPTIMIZE gold.dim_date ZORDER BY (reporting_date, reporting_period, fiscal_year);
```

#### 4.1.2 `gold.dim_region`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_region (
  region_sk BIGINT,
  region_name VARCHAR(200),
  organization_hierarchy_name VARCHAR(200),
  network_level VARCHAR(100),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA;
```

```sql
OPTIMIZE gold.dim_region ZORDER BY (region_name, organization_hierarchy_name);
```

#### 4.1.3 `gold.dim_branch`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_branch (
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  branch_status VARCHAR(50),
  region_name VARCHAR(200),
  organization_hierarchy_name VARCHAR(200),
  network_level VARCHAR(100),
  active_flag VARCHAR(10),
  effective_start_date DATE,
  effective_end_date DATE,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

```sql
OPTIMIZE gold.dim_branch ZORDER BY (branch_code, branch_name, region_name);
```

#### 4.1.4 `gold.dim_customer`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_customer (
  customer_sk BIGINT,
  customer_id VARCHAR(100),
  customer_name VARCHAR(255),
  customer_status VARCHAR(50),
  credit_terms VARCHAR(100),
  credit_limit DECIMAL(18,2),
  customer_since_date DATE,
  collector_id VARCHAR(100),
  collector_name VARCHAR(255),
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_name VARCHAR(200),
  effective_start_date DATE,
  effective_end_date DATE,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

```sql
OPTIMIZE gold.dim_customer ZORDER BY (customer_id, customer_name, customer_status, branch_code);
```

#### 4.1.5 `gold.dim_sales_rep`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_sales_rep (
  sales_rep_sk BIGINT,
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  employee_id VARCHAR(100),
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_name VARCHAR(200),
  role VARCHAR(100),
  effective_date DATE,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA;
```

```sql
OPTIMIZE gold.dim_sales_rep ZORDER BY (sales_rep_id, branch_code, region_name);
```

#### 4.1.6 `gold.dim_collector`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_collector (
  collector_sk BIGINT,
  collector_id VARCHAR(100),
  collector_name VARCHAR(255),
  employee_id VARCHAR(100),
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_name VARCHAR(200),
  role VARCHAR(100),
  effective_date DATE,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA;
```

```sql
OPTIMIZE gold.dim_collector ZORDER BY (collector_id, branch_code, region_name);
```

#### 4.1.7 `gold.dim_equipment_class`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_equipment_class (
  equipment_class_sk BIGINT,
  equipment_class VARCHAR(100),
  equipment_class_name VARCHAR(200),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA;
```

```sql
OPTIMIZE gold.dim_equipment_class ZORDER BY (equipment_class, equipment_class_name);
```

#### 4.1.8 `gold.dim_contract`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_contract (
  contract_sk BIGINT,
  contract_id VARCHAR(100),
  customer_id VARCHAR(100),
  customer_name VARCHAR(255),
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_name VARCHAR(200),
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  equipment_class VARCHAR(100),
  equipment_class_name VARCHAR(200),
  contract_start_date DATE,
  contract_end_date DATE,
  contract_status VARCHAR(50),
  daily_rate DECIMAL(18,2),
  total_billed_rental_days INT,
  open_contract_count INT,
  open_contract_value DECIMAL(18,2),
  effective_start_date DATE,
  effective_end_date DATE,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

```sql
OPTIMIZE gold.dim_contract ZORDER BY (contract_id, customer_id, branch_code, sales_rep_id);
```

#### 4.1.9 `gold.dim_invoice`
```sql
CREATE TABLE IF NOT EXISTS gold.dim_invoice (
  invoice_sk BIGINT,
  invoice_id VARCHAR(100),
  contract_id VARCHAR(100),
  customer_id VARCHAR(100),
  customer_name VARCHAR(255),
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_name VARCHAR(200),
  invoice_date DATE,
  due_date DATE,
  invoice_amount DECIMAL(18,2),
  tax_amount DECIMAL(18,2),
  invoice_type VARCHAR(50),
  currency VARCHAR(20),
  aging_bucket VARCHAR(20),
  days_past_due INT,
  match_status VARCHAR(50),
  contract_status VARCHAR(50),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (load_date);
```

```sql
OPTIMIZE gold.dim_invoice ZORDER BY (invoice_id, contract_id, customer_id, due_date);
```

#### 4.1.10 `gold.code_aging_bucket`
```sql
CREATE TABLE IF NOT EXISTS gold.code_aging_bucket (
  aging_bucket_sk BIGINT,
  aging_bucket_name VARCHAR(20),
  bucket_sequence INT,
  bucket_definition VARCHAR(255),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA;
```

#### 4.1.11 `gold.code_period_type`
```sql
CREATE TABLE IF NOT EXISTS gold.code_period_type (
  period_type_sk BIGINT,
  period_type_name VARCHAR(20),
  period_type_description VARCHAR(255),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA;
```

### 4.2 Fact Tables DDL Script

#### 4.2.1 `gold.fct_rental_revenue`
```sql
CREATE TABLE IF NOT EXISTS gold.fct_rental_revenue (
  rental_revenue_fact_sk BIGINT,
  reporting_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_sk BIGINT,
  region_name VARCHAR(200),
  sales_rep_sk BIGINT,
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  equipment_class_sk BIGINT,
  equipment_class VARCHAR(100),
  equipment_class_name VARCHAR(200),
  contract_sk BIGINT,
  contract_id VARCHAR(100),
  customer_sk BIGINT,
  customer_id VARCHAR(100),
  invoice_sk BIGINT,
  invoice_id VARCHAR(100),
  contract_status VARCHAR(50),
  invoice_type VARCHAR(50),
  currency VARCHAR(20),
  rental_revenue DECIMAL(18,2),
  gross_billings DECIMAL(18,2),
  credit_memo_amount DECIMAL(18,2),
  net_billings DECIMAL(18,2),
  invoice_count INT,
  total_billed_rental_days INT,
  contract_count INT,
  average_daily_rate DECIMAL(18,4),
  revenue_per_contract DECIMAL(18,4),
  credit_memo_rate DECIMAL(18,6),
  trend_value DECIMAL(18,4),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (period_type, load_date);
```

```sql
OPTIMIZE gold.fct_rental_revenue ZORDER BY (reporting_date, branch_code, sales_rep_id, equipment_class, contract_id, invoice_id);
```

#### 4.2.2 `gold.fct_ar_aging`
```sql
CREATE TABLE IF NOT EXISTS gold.fct_ar_aging (
  ar_aging_fact_sk BIGINT,
  snapshot_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_sk BIGINT,
  region_name VARCHAR(200),
  customer_sk BIGINT,
  customer_id VARCHAR(100),
  customer_name VARCHAR(255),
  collector_sk BIGINT,
  collector_id VARCHAR(100),
  collector_name VARCHAR(255),
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  contract_sk BIGINT,
  contract_id VARCHAR(100),
  invoice_sk BIGINT,
  invoice_id VARCHAR(100),
  invoice_date DATE,
  due_date DATE,
  invoice_amount DECIMAL(18,2),
  days_past_due INT,
  aging_bucket VARCHAR(20),
  total_ar_outstanding DECIMAL(18,2),
  ar_aging_by_bucket DECIMAL(18,2),
  ar_90_plus_amount DECIMAL(18,2),
  ar_90_plus_percentage DECIMAL(18,6),
  credit_sales_in_period DECIMAL(18,2),
  number_of_days_in_period INT,
  dso DECIMAL(18,4),
  best_possible_dso DECIMAL(18,4),
  dso_trend DECIMAL(18,4),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (snapshot_date, load_date);
```

```sql
OPTIMIZE gold.fct_ar_aging ZORDER BY (snapshot_date, branch_code, collector_id, customer_id, invoice_id, aging_bucket);
```

#### 4.2.3 `gold.fct_cash_application`
```sql
CREATE TABLE IF NOT EXISTS gold.fct_cash_application (
  cash_application_fact_sk BIGINT,
  reporting_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_sk BIGINT,
  region_name VARCHAR(200),
  collector_sk BIGINT,
  collector_id VARCHAR(100),
  collector_name VARCHAR(255),
  customer_sk BIGINT,
  customer_id VARCHAR(100),
  customer_name VARCHAR(255),
  invoice_sk BIGINT,
  invoice_id VARCHAR(100),
  receipt_sk BIGINT,
  receipt_id VARCHAR(100),
  payment_method VARCHAR(50),
  match_status VARCHAR(50),
  payment_date DATE,
  receipt_date DATE,
  invoice_date DATE,
  due_date DATE,
  payment_amount DECIMAL(18,2),
  applied_payment_amount DECIMAL(18,2),
  unapplied_cash_amount DECIMAL(18,2),
  cash_collected DECIMAL(18,2),
  total_payments_amount DECIMAL(18,2),
  average_days_to_pay DECIMAL(18,4),
  collection_effectiveness_index DECIMAL(18,6),
  invoices_paid_on_time_percentage DECIMAL(18,6),
  unapplied_cash_percentage DECIMAL(18,6),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (period_type, load_date);
```

```sql
OPTIMIZE gold.fct_cash_application ZORDER BY (reporting_date, branch_code, collector_id, customer_id, receipt_id, invoice_id);
```

#### 4.2.4 `gold.fct_credit_risk`
```sql
CREATE TABLE IF NOT EXISTS gold.fct_credit_risk (
  credit_risk_fact_sk BIGINT,
  snapshot_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  region_sk BIGINT,
  region_name VARCHAR(200),
  customer_sk BIGINT,
  customer_id VARCHAR(100),
  customer_name VARCHAR(255),
  customer_status VARCHAR(50),
  credit_terms VARCHAR(100),
  credit_limit DECIMAL(18,2),
  outstanding_ar DECIMAL(18,2),
  credit_utilization_percentage DECIMAL(18,6),
  customers_over_limit_count INT,
  customers_over_limit_amount DECIMAL(18,2),
  suspended_customers_with_open_exposure INT,
  ar_90_plus_amount_by_customer DECIMAL(18,2),
  open_contract_count INT,
  open_contract_value DECIMAL(18,2),
  customer_since_date DATE,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (snapshot_date, load_date);
```

```sql
OPTIMIZE gold.fct_credit_risk ZORDER BY (snapshot_date, branch_code, customer_id, customer_status);
```

### 4.3 Error Data Table DDL Script
```sql
CREATE TABLE IF NOT EXISTS gold.error_data (
  error_record_sk BIGINT,
  layer_name VARCHAR(20),
  pipeline_name VARCHAR(200),
  source_table_name VARCHAR(200),
  target_table_name VARCHAR(200),
  business_key VARCHAR(500),
  table_name VARCHAR(200),
  column_name VARCHAR(200),
  validation_rule_name VARCHAR(200),
  validation_rule_description VARCHAR(500),
  validation_status VARCHAR(50),
  rejected_value VARCHAR(500),
  error_description VARCHAR(1000),
  error_category VARCHAR(100),
  error_severity VARCHAR(50),
  error_status VARCHAR(50),
  corrective_action VARCHAR(500),
  source_system VARCHAR(100),
  detected_timestamp TIMESTAMP,
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (layer_name, load_date);
```

```sql
OPTIMIZE gold.error_data ZORDER BY (source_table_name, target_table_name, business_key, validation_rule_name, error_status);
```

### 4.4 Audit Table DDL Script
```sql
CREATE TABLE IF NOT EXISTS gold.process_audit (
  audit_sk BIGINT,
  pipeline_run_id VARCHAR(100),
  pipeline_name VARCHAR(200),
  layer_name VARCHAR(20),
  source_system VARCHAR(100),
  source_table_name VARCHAR(200),
  target_table_name VARCHAR(200),
  process_status VARCHAR(50),
  records_read_count BIGINT,
  records_written_count BIGINT,
  records_rejected_count BIGINT,
  process_start_time TIMESTAMP,
  process_end_time TIMESTAMP,
  processing_duration_seconds DECIMAL(18,2),
  trigger_type VARCHAR(50),
  processed_by VARCHAR(200),
  audit_message VARCHAR(1000),
  error_message VARCHAR(1000),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (layer_name, load_date);
```

```sql
OPTIMIZE gold.process_audit ZORDER BY (pipeline_run_id, pipeline_name, source_table_name, target_table_name, process_status);
```

### 4.5 Aggregated Tables DDL Script

#### 4.5.1 `gold.agg_executive_health_score`
```sql
CREATE TABLE IF NOT EXISTS gold.agg_executive_health_score (
  executive_health_score_sk BIGINT,
  reporting_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  network_level VARCHAR(100),
  region_sk BIGINT,
  region_name VARCHAR(200),
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  sales_rep_sk BIGINT,
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  collector_sk BIGINT,
  collector_id VARCHAR(100),
  collector_name VARCHAR(255),
  overall_revenue_to_cash_health_score DECIMAL(18,4),
  revenue_domain_score DECIMAL(18,4),
  ar_domain_score DECIMAL(18,4),
  cash_app_domain_score DECIMAL(18,4),
  credit_risk_domain_score DECIMAL(18,4),
  rental_revenue DECIMAL(18,2),
  dso DECIMAL(18,4),
  ar_90_plus_percentage DECIMAL(18,6),
  collection_effectiveness_index DECIMAL(18,6),
  unapplied_cash_percentage DECIMAL(18,6),
  credit_utilization_percentage DECIMAL(18,6),
  top_aging_risk_driver VARCHAR(500),
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (period_type, load_date);
```

```sql
OPTIMIZE gold.agg_executive_health_score ZORDER BY (reporting_date, region_name, branch_code, sales_rep_id, collector_id);
```

#### 4.5.2 `gold.agg_billing_performance`
```sql
CREATE TABLE IF NOT EXISTS gold.agg_billing_performance (
  billing_performance_sk BIGINT,
  reporting_date DATE,
  reporting_period VARCHAR(50),
  period_type VARCHAR(20),
  region_sk BIGINT,
  region_name VARCHAR(200),
  branch_sk BIGINT,
  branch_code VARCHAR(100),
  branch_name VARCHAR(200),
  sales_rep_sk BIGINT,
  sales_rep_id VARCHAR(100),
  sales_rep_name VARCHAR(255),
  equipment_class_sk BIGINT,
  equipment_class VARCHAR(100),
  equipment_class_name VARCHAR(200),
  gross_billings DECIMAL(18,2),
  credit_memo_amount DECIMAL(18,2),
  net_billings DECIMAL(18,2),
  rental_revenue DECIMAL(18,2),
  average_daily_rate DECIMAL(18,4),
  revenue_per_contract DECIMAL(18,4),
  credit_memo_rate DECIMAL(18,6),
  invoice_count INT,
  source_system VARCHAR(100),
  load_date DATE,
  update_date DATE
)
USING DELTA
PARTITIONED BY (period_type, load_date);
```

```sql
OPTIMIZE gold.agg_billing_performance ZORDER BY (reporting_date, region_name, branch_code, sales_rep_id, equipment_class);
```

## 5. Update DDL Script
The following update DDL script supports version 2 additions and future extensibility without overwriting prior versions.

```sql
ALTER TABLE gold.agg_executive_health_score ADD COLUMNS (
  score_weight_config_name VARCHAR(200),
  score_calculation_version VARCHAR(50)
);

ALTER TABLE gold.fct_ar_aging ADD COLUMNS (
  aging_bucket_sequence INT,
  snapshot_week_start_date DATE
);

ALTER TABLE gold.fct_cash_application ADD COLUMNS (
  beginning_ar DECIMAL(18,2),
  ending_total_ar DECIMAL(18,2),
  ending_current_ar DECIMAL(18,2)
);

ALTER TABLE gold.fct_credit_risk ADD COLUMNS (
  over_limit_flag VARCHAR(10),
  suspended_with_exposure_flag VARCHAR(10)
);

ALTER TABLE gold.process_audit ADD COLUMNS (
  workflow_name VARCHAR(200),
  notebook_path VARCHAR(500)
);

ALTER TABLE gold.error_data ADD COLUMNS (
  remediation_status VARCHAR(50),
  remediated_timestamp TIMESTAMP
);
```

## 6. Data Retention Policies

### 6.1 Retention Periods for the Gold Layer
| Table Category | Retention Period | Rationale |
|---|---|---|
| Gold dimensions | 7 years | Supports historical reporting, branch hierarchy analysis, and customer trend analysis |
| Gold facts | 7 years | Supports finance, AR, cash application, and credit-risk trend reporting |
| Gold aggregate tables | 5 years online, archive older data | Supports executive dashboards while controlling storage cost |
| Gold error data | 2 years online, archive afterward | Supports remediation and audit review |
| Gold process audit | 2 years online, archive afterward | Supports pipeline monitoring and operational governance |

### 6.2 Archiving Strategies
1. Archive fact and aggregate partitions older than the online retention threshold to lower-cost Delta storage.
2. Preserve schema compatibility between active and archived Gold tables.
3. Keep error and audit data queryable after archival for compliance and operational traceability.
4. Apply Delta retention and vacuum settings only in accordance with enterprise audit policy.
5. Retain business-critical month-end and quarter-end snapshots for finance reporting continuity.

## 7. Conceptual Data Model Diagram in Tabular Form
| Source Table | Connected To Table | Key Field Used for Connection | Relationship Description |
|---|---|---|---|
| `gold.dim_region` | `gold.dim_branch` | `region_name` | One region connects to many branches |
| `gold.dim_branch` | `gold.dim_contract` | `branch_code` | One branch connects to many contracts |
| `gold.dim_customer` | `gold.dim_contract` | `customer_id` | One customer connects to many contracts |
| `gold.dim_contract` | `gold.dim_invoice` | `contract_id` | One contract connects to many invoices |
| `gold.dim_customer` | `gold.dim_invoice` | `customer_id` | One customer connects to many invoices |
| `gold.dim_sales_rep` | `gold.dim_contract` | `sales_rep_id` | One sales representative connects to many contracts |
| `gold.dim_collector` | `gold.dim_customer` | `collector_id` | One collector connects to many customers |
| `gold.dim_date` | `gold.fct_rental_revenue` | `reporting_date` | One date connects to many rental revenue fact rows |
| `gold.dim_branch` | `gold.fct_rental_revenue` | `branch_code` | One branch connects to many rental revenue rows |
| `gold.dim_region` | `gold.fct_rental_revenue` | `region_name` | One region connects to many rental revenue rows |
| `gold.dim_sales_rep` | `gold.fct_rental_revenue` | `sales_rep_id` | One sales representative connects to many rental revenue rows |
| `gold.dim_equipment_class` | `gold.fct_rental_revenue` | `equipment_class` | One equipment class connects to many rental revenue rows |
| `gold.dim_date` | `gold.fct_ar_aging` | `snapshot_date` | One date connects to many AR aging snapshot rows |
| `gold.dim_customer` | `gold.fct_ar_aging` | `customer_id` | One customer connects to many AR aging rows |
| `gold.dim_collector` | `gold.fct_ar_aging` | `collector_id` | One collector connects to many AR aging rows |
| `gold.code_aging_bucket` | `gold.fct_ar_aging` | `aging_bucket` | One aging bucket code connects to many AR aging rows |
| `gold.dim_date` | `gold.fct_cash_application` | `reporting_date` | One date connects to many cash application rows |
| `gold.dim_customer` | `gold.fct_cash_application` | `customer_id` | One customer connects to many cash application rows |
| `gold.dim_collector` | `gold.fct_cash_application` | `collector_id` | One collector connects to many cash application rows |
| `gold.dim_date` | `gold.fct_credit_risk` | `snapshot_date` | One date connects to many credit risk rows |
| `gold.dim_customer` | `gold.fct_credit_risk` | `customer_id` | One customer connects to many credit risk rows |
| `gold.fct_rental_revenue` | `gold.agg_billing_performance` | `reporting_date, branch_code, sales_rep_id, equipment_class` | Rental revenue fact rolls into billing performance aggregate |
| `gold.fct_rental_revenue` | `gold.agg_executive_health_score` | `reporting_date, branch_code, region_name` | Rental revenue fact contributes to executive scorecard |
| `gold.fct_ar_aging` | `gold.agg_executive_health_score` | `snapshot_date, branch_code, customer_id` | AR aging fact contributes to executive scorecard |
| `gold.fct_cash_application` | `gold.agg_executive_health_score` | `reporting_date, branch_code, collector_id` | Cash application fact contributes to executive scorecard |
| `gold.fct_credit_risk` | `gold.agg_executive_health_score` | `snapshot_date, branch_code, customer_id` | Credit risk fact contributes to executive scorecard |

## 8. ER Diagram Visualization Graph
```text
[dim_region] --region_name--> [dim_branch]
[dim_branch] --branch_code--> [dim_contract]
[dim_customer] --customer_id--> [dim_contract]
[dim_contract] --contract_id--> [dim_invoice]
[dim_customer] --customer_id--> [dim_invoice]
[dim_sales_rep] --sales_rep_id--> [dim_contract]
[dim_collector] --collector_id--> [dim_customer]
[dim_date] --reporting_date--> [fct_rental_revenue]
[dim_branch] --branch_code--> [fct_rental_revenue]
[dim_region] --region_name--> [fct_rental_revenue]
[dim_sales_rep] --sales_rep_id--> [fct_rental_revenue]
[dim_equipment_class] --equipment_class--> [fct_rental_revenue]
[dim_date] --snapshot_date--> [fct_ar_aging]
[dim_customer] --customer_id--> [fct_ar_aging]
[dim_collector] --collector_id--> [fct_ar_aging]
[code_aging_bucket] --aging_bucket_name--> [fct_ar_aging]
[dim_date] --reporting_date--> [fct_cash_application]
[dim_customer] --customer_id--> [fct_cash_application]
[dim_collector] --collector_id--> [fct_cash_application]
[dim_date] --snapshot_date--> [fct_credit_risk]
[dim_customer] --customer_id--> [fct_credit_risk]
[fct_rental_revenue] --reporting_date/branch_code/sales_rep_id/equipment_class--> [agg_billing_performance]
[fct_rental_revenue] --reporting_date/branch_code/region_name--> [agg_executive_health_score]
[fct_ar_aging] --snapshot_date/branch_code/customer_id--> [agg_executive_health_score]
[fct_cash_application] --reporting_date/branch_code/collector_id--> [agg_executive_health_score]
[fct_credit_risk] --snapshot_date/branch_code/customer_id--> [agg_executive_health_score]
```

## 9. Assumptions and Design Decisions
1. Silver physical tables are treated as the authoritative source for column-level carry-forward into Gold physical design.
2. Additional Gold attributes were added only where needed to support the Gold logical model and AP-1 reporting requirements.
3. Surrogate id fields are modeled as `BIGINT` and are expected to be populated by ETL logic.
4. Duplicate-prevention requirements from AP-1 are handled in ETL and validation logic, not by physical constraints, because Spark SQL-compatible output must not include unsupported constraints.
5. Traditional indexes are not implemented; Databricks Delta optimization techniques are documented instead.
6. `VARCHAR` is used in place of unrestricted text-oriented types to comply with the instruction.
7. `DATE` and `TIMESTAMP` are used according to business semantics; `DATETIME` is not used.
8. Health score must remain between 0 and 100 through ETL validation logic rather than table constraint enforcement.
9. Credit memo sign logic, zero-denominator checks for KPI calculations, and CEI/DSO calculation controls are managed in transformation logic and error capture tables.
10. Description and required changes in this version are derived from Jira ticket `AP-1`.

## 10. Databricks Spark SQL Limitations Considered and Excluded
| Limitation / Consideration | Handling in Final Output |
|---|---|
| Primary key and foreign key enforcement is not appropriate for this Databricks medallion implementation | Excluded from DDL |
| Traditional OLTP indexes are not used in Databricks Delta | Replaced with partitioning and `OPTIMIZE ... ZORDER BY` guidance |
| `GENERATED ALWAYS AS IDENTITY` was explicitly prohibited | Not used |
| `UNIQUE`, `TEXT`, and `DATETIME` were explicitly prohibited | Not used |
| Heavy constraint enforcement can reduce ingestion and processing flexibility | Excluded from table definitions |

## 11. API Cost
apiCost: 0.000000

## Output URL (Clickable Hyperlinks)
[Databricks_Gold_Model_Physical_2.sql](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Model_Physical/Databricks_Gold_Model_Physical_2.sql)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Model_Physical
pipelineID : 12372
