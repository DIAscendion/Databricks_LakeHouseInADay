_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Updated Databricks Silver physical data model for Rental Revenue-to-Cash reporting aligned to Jira AP-1 requirements.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver Model Physical

## Jira Tickets Read

| Ticket Key | Summary | Status |
|---|---|---|
| AP-1 | Reporting Requirements for Rental Revenue-to-Cash | To Do |

## Silver Layer

### DDL Scripts

#### 1. silver.si_rental_contracts
```sql
CREATE TABLE IF NOT EXISTS silver.si_rental_contracts (
  rental_contract_sk BIGINT,
  contract_id STRING,
  customer_id STRING,
  branch_code STRING,
  sales_rep_id STRING,
  equipment_class STRING,
  contract_start_date DATE,
  contract_end_date DATE,
  contract_status STRING,
  daily_rate DECIMAL(18,2),
  branch_active_flag STRING,
  contract_duration_days INT,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (branch_code);
```

#### 2. silver.si_invoices
```sql
CREATE TABLE IF NOT EXISTS silver.si_invoices (
  invoice_sk BIGINT,
  invoice_id STRING,
  contract_id STRING,
  customer_id STRING,
  invoice_date DATE,
  due_date DATE,
  invoice_amount DECIMAL(18,2),
  tax_amount DECIMAL(18,2),
  invoice_type STRING,
  currency STRING,
  gross_billings DECIMAL(18,2),
  credit_memo_amount DECIMAL(18,2),
  net_billings DECIMAL(18,2),
  invoice_count INT,
  days_past_due INT,
  aging_bucket STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (invoice_date);
```

#### 3. silver.si_cash_receipts
```sql
CREATE TABLE IF NOT EXISTS silver.si_cash_receipts (
  cash_receipt_sk BIGINT,
  receipt_id STRING,
  invoice_id STRING,
  customer_id STRING,
  receipt_date DATE,
  payment_amount DECIMAL(18,2),
  payment_method STRING,
  match_status STRING,
  applied_amount DECIMAL(18,2),
  unapplied_payment_amount DECIMAL(18,2),
  days_to_pay INT,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (receipt_date);
```

#### 4. silver.si_customer_master
```sql
CREATE TABLE IF NOT EXISTS silver.si_customer_master (
  customer_sk BIGINT,
  customer_id STRING,
  customer_name STRING,
  credit_terms STRING,
  credit_limit DECIMAL(18,2),
  customer_since DATE,
  customer_status STRING,
  conformed_customer_id STRING,
  duplicate_customer_flag STRING,
  open_contract_count INT,
  open_contract_value DECIMAL(18,2),
  outstanding_ar DECIMAL(18,2),
  ar_90_plus_amount DECIMAL(18,2),
  credit_utilization_pct DECIMAL(18,4),
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (customer_status);
```

#### 5. silver.si_branch_employee
```sql
CREATE TABLE IF NOT EXISTS silver.si_branch_employee (
  branch_employee_sk BIGINT,
  employee_id STRING,
  employee_name STRING,
  role STRING,
  branch_code STRING,
  region STRING,
  collector_id STRING,
  effective_date DATE,
  sales_rep_name STRING,
  collector_name STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (region);
```

#### 6. silver.si_revenue_to_cash_health_score
```sql
CREATE TABLE IF NOT EXISTS silver.si_revenue_to_cash_health_score (
  health_score_sk BIGINT,
  branch_code STRING,
  region STRING,
  reporting_date DATE,
  period_type STRING,
  revenue_domain_score DECIMAL(18,4),
  ar_domain_score DECIMAL(18,4),
  cash_app_domain_score DECIMAL(18,4),
  credit_risk_domain_score DECIMAL(18,4),
  overall_health_score DECIMAL(18,4),
  top_aging_risk_driver STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (reporting_date, period_type);
```

#### 7. silver.si_fact_rental_revenue
```sql
CREATE TABLE IF NOT EXISTS silver.si_fact_rental_revenue (
  rental_revenue_fact_sk BIGINT,
  branch_code STRING,
  region STRING,
  contract_id STRING,
  customer_id STRING,
  sales_rep_id STRING,
  equipment_class STRING,
  reporting_date DATE,
  period_type STRING,
  rental_revenue DECIMAL(18,2),
  gross_billings DECIMAL(18,2),
  credit_memo_amount DECIMAL(18,2),
  net_billings DECIMAL(18,2),
  average_daily_rate DECIMAL(18,4),
  revenue_per_contract DECIMAL(18,4),
  credit_memo_rate DECIMAL(18,4),
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (reporting_date, branch_code);
```

#### 8. silver.si_fact_ar_aging
```sql
CREATE TABLE IF NOT EXISTS silver.si_fact_ar_aging (
  ar_aging_fact_sk BIGINT,
  branch_code STRING,
  region STRING,
  customer_id STRING,
  collector_id STRING,
  sales_rep_id STRING,
  invoice_id STRING,
  snapshot_date DATE,
  total_ar_outstanding DECIMAL(18,2),
  aging_bucket STRING,
  aging_bucket_amount DECIMAL(18,2),
  ar_90_plus_amount DECIMAL(18,2),
  ar_90_plus_pct DECIMAL(18,4),
  dso DECIMAL(18,4),
  best_possible_dso DECIMAL(18,4),
  dso_trend DECIMAL(18,4),
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (snapshot_date, branch_code);
```

#### 9. silver.si_fact_cash_application
```sql
CREATE TABLE IF NOT EXISTS silver.si_fact_cash_application (
  cash_application_fact_sk BIGINT,
  branch_code STRING,
  region STRING,
  collector_id STRING,
  customer_id STRING,
  invoice_id STRING,
  receipt_id STRING,
  reporting_date DATE,
  cash_collected DECIMAL(18,2),
  collection_effectiveness_index DECIMAL(18,4),
  average_days_to_pay DECIMAL(18,4),
  invoices_paid_on_time_pct DECIMAL(18,4),
  unapplied_cash_amount DECIMAL(18,2),
  unapplied_cash_pct DECIMAL(18,4),
  payment_method STRING,
  match_status STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (reporting_date, branch_code);
```

#### 10. silver.si_fact_credit_risk
```sql
CREATE TABLE IF NOT EXISTS silver.si_fact_credit_risk (
  credit_risk_fact_sk BIGINT,
  branch_code STRING,
  region STRING,
  customer_id STRING,
  snapshot_date DATE,
  customer_status STRING,
  credit_limit DECIMAL(18,2),
  outstanding_ar DECIMAL(18,2),
  credit_utilization_pct DECIMAL(18,4),
  customers_over_limit_count INT,
  customers_over_limit_amount DECIMAL(18,2),
  suspended_customers_with_open_exposure INT,
  ar_90_plus_amount_by_customer DECIMAL(18,2),
  open_contract_count INT,
  open_contract_value DECIMAL(18,2),
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (snapshot_date, branch_code);
```

### Error Data Table DDL Script

```sql
CREATE TABLE IF NOT EXISTS silver.si_error_data (
  error_data_sk BIGINT,
  layer_name STRING,
  source_table_name STRING,
  target_table_name STRING,
  business_key STRING,
  error_category STRING,
  error_rule STRING,
  error_description STRING,
  rejected_record_payload STRING,
  validation_status STRING,
  detected_timestamp TIMESTAMP,
  pipeline_run_id STRING,
  source_system STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP
)
USING DELTA
PARTITIONED BY (layer_name, source_table_name);
```

### Audit Table DDL Script

```sql
CREATE TABLE IF NOT EXISTS silver.si_pipeline_audit (
  pipeline_audit_sk BIGINT,
  pipeline_run_id STRING,
  pipeline_name STRING,
  layer_name STRING,
  source_table_name STRING,
  target_table_name STRING,
  processing_start_time TIMESTAMP,
  processing_end_time TIMESTAMP,
  processing_status STRING,
  error_message STRING,
  records_read_count BIGINT,
  records_written_count BIGINT,
  records_rejected_count BIGINT,
  reconciliation_status STRING,
  processed_by STRING,
  load_date TIMESTAMP,
  update_date TIMESTAMP,
  source_system STRING
)
USING DELTA
PARTITIONED BY (layer_name, processing_status);
```

### Update DDL Script

```sql
-- Description includes Jira source: AP-1
ALTER TABLE silver.si_invoices ADD COLUMNS (
  gross_billings DECIMAL(18,2),
  credit_memo_amount DECIMAL(18,2),
  net_billings DECIMAL(18,2),
  invoice_count INT,
  days_past_due INT,
  aging_bucket STRING
);

ALTER TABLE silver.si_cash_receipts ADD COLUMNS (
  match_status STRING,
  applied_amount DECIMAL(18,2),
  unapplied_payment_amount DECIMAL(18,2),
  days_to_pay INT
);

ALTER TABLE silver.si_customer_master ADD COLUMNS (
  conformed_customer_id STRING,
  duplicate_customer_flag STRING,
  open_contract_count INT,
  open_contract_value DECIMAL(18,2),
  outstanding_ar DECIMAL(18,2),
  ar_90_plus_amount DECIMAL(18,2),
  credit_utilization_pct DECIMAL(18,4)
);
```

## Index and Performance Strategy

| Table | Optimization Strategy |
|---|---|
| silver.si_rental_contracts | OPTIMIZE with ZORDER BY (contract_id, customer_id, branch_code) |
| silver.si_invoices | OPTIMIZE with ZORDER BY (invoice_id, contract_id, customer_id, due_date) |
| silver.si_cash_receipts | OPTIMIZE with ZORDER BY (receipt_id, invoice_id, customer_id) |
| silver.si_customer_master | OPTIMIZE with ZORDER BY (customer_id, conformed_customer_id, customer_status) |
| silver.si_branch_employee | OPTIMIZE with ZORDER BY (employee_id, branch_code, region) |
| silver.si_fact_rental_revenue | OPTIMIZE with ZORDER BY (reporting_date, branch_code, contract_id) |
| silver.si_fact_ar_aging | OPTIMIZE with ZORDER BY (snapshot_date, customer_id, invoice_id) |
| silver.si_fact_cash_application | OPTIMIZE with ZORDER BY (reporting_date, collector_id, receipt_id) |
| silver.si_fact_credit_risk | OPTIMIZE with ZORDER BY (snapshot_date, customer_id, branch_code) |
| silver.si_error_data | OPTIMIZE with ZORDER BY (layer_name, source_table_name, detected_timestamp) |
| silver.si_pipeline_audit | OPTIMIZE with ZORDER BY (pipeline_run_id, layer_name, processing_status) |

## Data Retention Policies

### Retention periods for the Silver layer

| Table Group | Retention Period |
|---|---|
| Core conformed Silver tables | 7 years |
| Error data table | 2 years |
| Audit table | 3 years |
| Weekly and daily health score snapshots | 3 years |

### Archiving strategies

| Data Area | Strategy |
|---|---|
| Historical Silver records | Archive closed historical partitions to lower-cost Delta storage annually |
| Error records | Archive resolved error records after 24 months to cold storage |
| Audit logs | Archive completed pipeline audit records after 36 months |
| Snapshot fact data | Compact and archive aged partitions while preserving Delta history policy per platform standard |

## Assumptions and Design Decisions

1. Bronze physical tables and all Bronze columns were carried into Silver physical structures with additional surrogate id fields as required.
2. No PK, FK, or unsupported Spark SQL constraints were included.
3. Additional Silver analytical structures were added because Jira AP-1 explicitly defines health score, AR aging, cash application, rental revenue, and credit risk reporting requirements.
4. Error and audit tables were included to support both Silver and Gold validation and execution logging requirements.
5. Databricks Spark SQL limitations were respected by excluding enforced relational constraints and traditional RDBMS indexes.
6. Partitioning was selected by high-volume reporting and snapshot dates aligned to the business domain.
7. Description metadata is updated based on Jira ticket AP-1.

## Conceptual Data Model Diagram in tabular form showing relationships

| Source Table | Key Field | Target Table | Relationship Description |
|---|---|---|---|
| silver.si_branch_employee | region | silver.si_rental_contracts | Region supports branch-level rental contract reporting rollups |
| silver.si_rental_contracts | branch_code | silver.si_fact_rental_revenue | Branch-level contract activity feeds rental revenue facts |
| silver.si_customer_master | customer_id | silver.si_rental_contracts | Customer connects to contract by customer_id |
| silver.si_rental_contracts | contract_id | silver.si_invoices | Contract connects to invoice by contract_id |
| silver.si_customer_master | customer_id | silver.si_invoices | Customer connects to invoice by customer_id |
| silver.si_invoices | invoice_id | silver.si_cash_receipts | Invoice connects to receipts by invoice_id |
| silver.si_customer_master | customer_id | silver.si_cash_receipts | Customer connects to cash receipts by customer_id |
| silver.si_branch_employee | collector_id | silver.si_fact_ar_aging | Collector assignment connects to AR aging by collector_id |
| silver.si_branch_employee | collector_id | silver.si_fact_cash_application | Collector assignment connects to cash application by collector_id |
| silver.si_customer_master | customer_id | silver.si_fact_ar_aging | Customer connects to AR aging by customer_id |
| silver.si_customer_master | customer_id | silver.si_fact_credit_risk | Customer connects to credit risk by customer_id |
| silver.si_invoices | invoice_id | silver.si_fact_ar_aging | Invoice connects to AR aging by invoice_id |
| silver.si_cash_receipts | receipt_id | silver.si_fact_cash_application | Receipt connects to cash application by receipt_id |
| silver.si_rental_contracts | contract_id | silver.si_fact_rental_revenue | Contract connects to rental revenue by contract_id |

## apiCost
apiCost: 0.000000

---

## Output URL (Clickable Hyperlinks)
[Databricks_Silver_Model Physical_Test_1.sql](https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Silver_Model_Physical/Databricks_Silver_Model%20Physical_Test_1.sql)

outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_Model_Physical
pipelineID : 12357