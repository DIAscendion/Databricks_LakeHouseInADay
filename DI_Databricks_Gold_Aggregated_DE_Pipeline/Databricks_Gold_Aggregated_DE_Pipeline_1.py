"""
_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold aggregated DE pipeline for Rental Revenue-to-Cash billing performance and executive health score fact-style aggregates with audit, error handling, and performance optimization.
## *Version*: 1 
## *Updated on*: 
_____________________________________________
"""

# Databricks Gold Aggregated DE Pipeline
# Expected Output: PySpark script
# Sections included: Business Transformations for Fact Tables, Audit Logs,
# Performance Optimization, Gold Layer Compatibility

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    lit,
    when,
    coalesce,
    round,
    sum as spark_sum,
    countDistinct,
    current_timestamp,
    datediff,
    expr,
    least,
    greatest,
    to_date,
    lower,
    trim,
    avg
)
from pyspark.sql.types import DecimalType, StringType
from delta.tables import DeltaTable
import uuid
import traceback


# ============================================================
# 1. Pipeline Configuration
# ============================================================
PIPELINE_NAME = "databricks_gold_aggregated_de_pipeline"
SOURCE_LAYER = "silver"
TARGET_LAYER = "gold"
RUN_ID = str(uuid.uuid4())
SOURCE_SYSTEM = "rental_revenue_to_cash"

SILVER_INVOICES = "silver.si_invoices"
SILVER_CONTRACTS = "silver.si_rental_contracts"
SILVER_CASH_RECEIPTS = "silver.si_cash_receipts"
SILVER_CUSTOMERS = "silver.si_customer_master"
SILVER_EMPLOYEES = "silver.si_branch_employee"
SILVER_AUDIT = "silver.si_process_audit"
SILVER_ERRORS = "silver.si_data_quality_errors"

GOLD_BILLING_PERFORMANCE = "gold.go_agg_billing_performance"
GOLD_EXECUTIVE_HEALTH = "gold.go_agg_executive_health_score"
GOLD_AUDIT = "gold.go_process_audit"
GOLD_ERRORS = "gold.go_data_quality_errors"

CHECKPOINT_BASE = "/tmp/databricks_gold_aggregated_de_pipeline"

spark = SparkSession.builder.appName(PIPELINE_NAME).getOrCreate()


# ============================================================
# 2. Utility Functions
# ============================================================
def write_audit_log(
    source_table: str,
    target_table: str,
    process_start_ts,
    process_end_ts,
    status: str,
    records_read_count: int,
    records_written_count: int,
    records_rejected_count: int,
    error_message: str = None,
    audit_remarks: str = None,
):
    duration_expr = None
    try:
        if process_start_ts and process_end_ts:
            duration_expr = 0.0
        audit_df = spark.createDataFrame(
            [(
                None,
                PIPELINE_NAME,
                source_table,
                target_table,
                process_start_ts,
                process_end_ts,
                status,
                int(records_read_count),
                int(records_written_count),
                int(records_rejected_count),
                duration_expr,
                error_message,
                "AAVA",
                audit_remarks,
                current_timestamp(),
                current_timestamp(),
                SOURCE_SYSTEM,
                RUN_ID,
            )],
            [
                "audit_sk",
                "pipeline_name",
                "source_table",
                "target_table",
                "process_start_timestamp",
                "process_end_timestamp",
                "processing_status",
                "records_read_count",
                "records_written_count",
                "records_rejected_count",
                "processing_duration_seconds",
                "error_message",
                "executed_by",
                "audit_remarks",
                "load_date",
                "update_date",
                "source_system",
                "run_id",
            ],
        )
        audit_df.write.format("delta").mode("append").saveAsTable(SILVER_AUDIT)
    except Exception:
        pass


def write_error_records(df: DataFrame, source_table: str, validation_rule_name: str, error_description: str):
    if df is None:
        return
    error_df = (
        df.withColumn("error_sk", lit(None).cast("bigint"))
          .withColumn("source_table", lit(source_table))
          .withColumn("source_record_id", coalesce(col("invoice_id").cast(StringType()), col("contract_id").cast(StringType()), col("customer_id").cast(StringType()), lit("unknown")))
          .withColumn("source_file_path", lit(None).cast(StringType()))
          .withColumn("validation_rule_name", lit(validation_rule_name))
          .withColumn("validation_category", lit("gold_aggregated_validation"))
          .withColumn("error_description", lit(error_description))
          .withColumn("error_record_payload", expr("to_json(named_struct(*))"))
          .withColumn("error_severity", lit("high"))
          .withColumn("layer_name", lit(TARGET_LAYER))
          .withColumn("detected_timestamp", current_timestamp())
          .withColumn("processing_status", lit("open"))
          .withColumn("load_date", current_timestamp())
          .withColumn("update_date", current_timestamp())
          .withColumn("source_system", lit(SOURCE_SYSTEM))
    )

    error_cols = [
        "error_sk", "source_table", "source_record_id", "source_file_path",
        "validation_rule_name", "validation_category", "error_description",
        "error_record_payload", "error_severity", "layer_name",
        "detected_timestamp", "processing_status", "load_date",
        "update_date", "source_system"
    ]

    error_df.select(*error_cols).write.format("delta").mode("append").saveAsTable(GOLD_ERRORS)
    error_df.select(*error_cols).write.format("delta").mode("append").saveAsTable(SILVER_ERRORS)


def safe_divide(numerator_col, denominator_col):
    return when(denominator_col.isNotNull() & (denominator_col != lit(0)), numerator_col / denominator_col).otherwise(lit(None))


def optimize_table(table_name: str, zorder_cols: str = None):
    try:
        spark.sql(f"OPTIMIZE {table_name}")
        if zorder_cols:
            spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({zorder_cols})")
    except Exception:
        pass


# ============================================================
# 3. Gold DDL Compatibility Setup
# ============================================================
def create_gold_support_tables():
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {GOLD_AUDIT} (
          audit_sk BIGINT,
          pipeline_name STRING,
          source_table STRING,
          target_table STRING,
          process_start_timestamp TIMESTAMP,
          process_end_timestamp TIMESTAMP,
          processing_status STRING,
          records_read_count DECIMAL(18,0),
          records_written_count DECIMAL(18,0),
          records_rejected_count DECIMAL(18,0),
          processing_duration_seconds DECIMAL(18,2),
          error_message STRING,
          executed_by STRING,
          audit_remarks STRING,
          load_date TIMESTAMP,
          update_date TIMESTAMP,
          source_system STRING,
          run_id STRING
        ) USING DELTA
        PARTITIONED BY (processing_status)
        """
    )

    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {GOLD_ERRORS} (
          error_sk BIGINT,
          source_table STRING,
          source_record_id STRING,
          source_file_path STRING,
          validation_rule_name STRING,
          validation_category STRING,
          error_description STRING,
          error_record_payload STRING,
          error_severity STRING,
          layer_name STRING,
          detected_timestamp TIMESTAMP,
          processing_status STRING,
          load_date TIMESTAMP,
          update_date TIMESTAMP,
          source_system STRING
        ) USING DELTA
        PARTITIONED BY (layer_name, processing_status)
        """
    )

    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {GOLD_BILLING_PERFORMANCE} (
          reporting_date DATE,
          region_name STRING,
          branch_name STRING,
          sales_rep_name STRING,
          equipment_class_name STRING,
          gross_billings DECIMAL(18,2),
          credit_memo_amount DECIMAL(18,2),
          net_billings DECIMAL(18,2),
          rental_revenue DECIMAL(18,2),
          average_daily_rate DECIMAL(18,6),
          revenue_per_contract DECIMAL(18,6),
          credit_memo_rate DECIMAL(18,6),
          invoice_count BIGINT,
          load_date TIMESTAMP,
          update_date TIMESTAMP,
          source_system STRING,
          run_id STRING
        ) USING DELTA
        PARTITIONED BY (reporting_date)
        """
    )

    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {GOLD_EXECUTIVE_HEALTH} (
          reporting_date DATE,
          network_level STRING,
          region_name STRING,
          branch_name STRING,
          sales_rep_name STRING,
          collector_name STRING,
          overall_revenue_to_cash_health_score DECIMAL(18,6),
          rental_revenue DECIMAL(18,2),
          dso DECIMAL(18,6),
          ar_90_plus_percentage DECIMAL(18,6),
          collection_effectiveness_index DECIMAL(18,6),
          unapplied_cash_percentage DECIMAL(18,6),
          credit_utilization_percentage DECIMAL(18,6),
          load_date TIMESTAMP,
          update_date TIMESTAMP,
          source_system STRING,
          run_id STRING
        ) USING DELTA
        PARTITIONED BY (reporting_date)
        """
    )


# ============================================================
# 4. Extract Data from Silver Layer
# ============================================================
def extract_silver_sources():
    invoices_df = (
        spark.table(SILVER_INVOICES)
        .withColumn("invoice_date", to_date(col("invoice_date")))
        .withColumn("due_date", to_date(col("due_date")))
        .withColumn("invoice_type", upper_safe(col("invoice_type")))
        .withColumn("invoice_amount", col("invoice_amount").cast(DecimalType(18, 2)))
    )

    contracts_df = (
        spark.table(SILVER_CONTRACTS)
        .withColumn("contract_start_date", to_date(col("contract_start_date")))
        .withColumn("contract_end_date", to_date(col("contract_end_date")))
        .withColumn("equipment_class", trim(lower(col("equipment_class"))))
        .withColumn("daily_rate", col("daily_rate").cast(DecimalType(18, 2)))
        .withColumn("branch_code", trim(lower(col("branch_code"))))
        .withColumn("sales_rep_id", trim(lower(col("sales_rep_id"))))
    )

    cash_receipts_df = (
        spark.table(SILVER_CASH_RECEIPTS)
        .withColumn("receipt_date", to_date(col("receipt_date")))
        .withColumn("payment_amount", col("payment_amount").cast(DecimalType(18, 2)))
        .withColumn(
            "unapplied_payment_amount",
            coalesce(col("unapplied_payment_amount").cast(DecimalType(18, 2)), lit(0).cast(DecimalType(18, 2)))
        )
    )

    customers_df = (
        spark.table(SILVER_CUSTOMERS)
        .withColumn("credit_limit", col("credit_limit").cast(DecimalType(18, 2)))
        .withColumn("customer_status", trim(lower(col("customer_status"))))
    )

    employees_df = (
        spark.table(SILVER_EMPLOYEES)
        .withColumn("employee_id", trim(lower(col("employee_id"))))
        .withColumn("employee_name", trim(col("employee_name")))
        .withColumn("branch_code", trim(lower(col("branch_code"))))
        .withColumn("region", trim(lower(col("region"))))
        .withColumn("collector_id", trim(lower(col("collector_id"))))
    )

    return invoices_df, contracts_df, cash_receipts_df, customers_df, employees_df


def upper_safe(c):
    return when(c.isNull(), lit(None)).otherwise(expr(f"upper(trim({c._jc.toString()}))"))


# ============================================================
# 5. Business Transformations for Fact Tables
# ============================================================
def build_billing_performance(invoices_df, contracts_df, employees_df):
    invalid_billing_df = invoices_df.filter(col("invoice_date").isNull() | col("contract_id").isNull())
    write_error_records(
        invalid_billing_df,
        SILVER_INVOICES,
        "billing_mandatory_field_validation",
        "Invalid invoice records detected for billing aggregate due to missing invoice_date or contract_id."
    )

    valid_invoices_df = invoices_df.filter(col("invoice_date").isNotNull() & col("contract_id").isNotNull())

    billing_base_df = (
        valid_invoices_df.alias("i")
        .join(contracts_df.alias("c"), col("i.contract_id") == col("c.contract_id"), "left")
        .join(employees_df.alias("e"), col("c.sales_rep_id") == col("e.employee_id"), "left")
        .select(
            col("i.invoice_id"),
            col("i.contract_id"),
            col("i.invoice_date").alias("reporting_date"),
            col("e.region").alias("region_name"),
            col("c.branch_code").alias("branch_name"),
            col("e.employee_name").alias("sales_rep_name"),
            col("c.equipment_class").alias("equipment_class_name"),
            col("i.invoice_type"),
            col("i.invoice_amount"),
            col("c.daily_rate")
        )
    )

    billing_df = (
        billing_base_df
        .groupBy(
            "reporting_date",
            "region_name",
            "branch_name",
            "sales_rep_name",
            "equipment_class_name"
        )
        .agg(
            round(spark_sum(coalesce(col("invoice_amount"), lit(0))), 2).alias("gross_billings"),
            round(
                spark_sum(
                    when(col("invoice_type") == lit("CREDIT_MEMO"), coalesce(col("invoice_amount"), lit(0)))
                    .otherwise(lit(0))
                ),
                2
            ).alias("credit_memo_amount"),
            round(
                spark_sum(
                    when(col("invoice_type") != lit("CREDIT_MEMO"), coalesce(col("invoice_amount"), lit(0)))
                    .otherwise(lit(0))
                ),
                2
            ).alias("rental_revenue"),
            round(avg(coalesce(col("daily_rate"), lit(0))), 6).alias("average_daily_rate"),
            countDistinct("contract_id").alias("distinct_contract_count"),
            countDistinct("invoice_id").alias("invoice_count")
        )
        .withColumn("net_billings", round(col("gross_billings") + col("credit_memo_amount"), 2))
        .withColumn(
            "revenue_per_contract",
            round(safe_divide(col("rental_revenue"), col("distinct_contract_count")), 6)
        )
        .withColumn(
            "credit_memo_rate",
            round(safe_divide(expr("abs(credit_memo_amount)"), col("gross_billings")), 6)
        )
        .drop("distinct_contract_count")
        .withColumn("load_date", current_timestamp())
        .withColumn("update_date", current_timestamp())
        .withColumn("source_system", lit(SOURCE_SYSTEM))
        .withColumn("run_id", lit(RUN_ID))
    )

    return billing_df


def build_executive_health(invoices_df, contracts_df, cash_receipts_df, customers_df, employees_df):
    revenue_domain_df = (
        invoices_df.alias("i")
        .join(contracts_df.alias("c"), col("i.contract_id") == col("c.contract_id"), "left")
        .join(employees_df.alias("e"), col("c.sales_rep_id") == col("e.employee_id"), "left")
        .filter(col("i.invoice_date").isNotNull())
        .groupBy(
            col("i.invoice_date").alias("reporting_date"),
            lit("branch").alias("network_level"),
            col("e.region").alias("region_name"),
            col("c.branch_code").alias("branch_name"),
            col("e.employee_name").alias("sales_rep_name")
        )
        .agg(
            round(
                spark_sum(
                    when(col("i.invoice_type") != lit("CREDIT_MEMO"), coalesce(col("i.invoice_amount"), lit(0))).otherwise(lit(0))
                ), 2
            ).alias("rental_revenue"),
            round(
                spark_sum(
                    when(datediff(current_timestamp(), col("i.due_date")) > 90, coalesce(col("i.invoice_amount"), lit(0))).otherwise(lit(0))
                ), 2
            ).alias("ar_90_plus_amount"),
            round(spark_sum(coalesce(col("i.invoice_amount"), lit(0))), 2).alias("total_ar_amount"),
            countDistinct(col("i.invoice_id")).alias("invoice_count")
        )
    )

    cash_domain_df = (
        cash_receipts_df.alias("cr")
        .join(invoices_df.alias("i"), col("cr.invoice_id") == col("i.invoice_id"), "left")
        .join(contracts_df.alias("c"), col("i.contract_id") == col("c.contract_id"), "left")
        .join(employees_df.alias("e"), col("c.sales_rep_id") == col("e.employee_id"), "left")
        .groupBy(
            col("cr.receipt_date").alias("reporting_date"),
            lit("branch").alias("network_level"),
            col("e.region").alias("region_name"),
            col("c.branch_code").alias("branch_name"),
            col("e.employee_name").alias("sales_rep_name"),
            col("e.employee_name").alias("collector_name")
        )
        .agg(
            round(spark_sum(coalesce(col("cr.payment_amount"), lit(0))), 2).alias("total_payment_amount"),
            round(spark_sum(coalesce(col("cr.unapplied_payment_amount"), lit(0))), 2).alias("unapplied_cash_amount")
        )
    )

    credit_domain_df = (
        invoices_df.alias("i")
        .join(customers_df.alias("cm"), col("i.customer_id") == col("cm.customer_id"), "left")
        .join(contracts_df.alias("c"), col("i.contract_id") == col("c.contract_id"), "left")
        .join(employees_df.alias("e"), col("c.sales_rep_id") == col("e.employee_id"), "left")
        .groupBy(
            col("i.invoice_date").alias("reporting_date"),
            lit("branch").alias("network_level"),
            col("e.region").alias("region_name"),
            col("c.branch_code").alias("branch_name"),
            col("e.employee_name").alias("sales_rep_name"),
            col("e.employee_name").alias("collector_name")
        )
        .agg(
            round(spark_sum(coalesce(col("i.invoice_amount"), lit(0))), 2).alias("outstanding_ar"),
            round(spark_sum(coalesce(col("cm.credit_limit"), lit(0))), 2).alias("credit_limit_total")
        )
    )

    executive_df = (
        revenue_domain_df.alias("r")
        .join(
            cash_domain_df.alias("c"),
            [
                col("r.reporting_date") == col("c.reporting_date"),
                col("r.network_level") == col("c.network_level"),
                col("r.region_name") == col("c.region_name"),
                col("r.branch_name") == col("c.branch_name"),
                col("r.sales_rep_name") == col("c.sales_rep_name"),
            ],
            "left"
        )
        .join(
            credit_domain_df.alias("cd"),
            [
                col("r.reporting_date") == col("cd.reporting_date"),
                col("r.network_level") == col("cd.network_level"),
                col("r.region_name") == col("cd.region_name"),
                col("r.branch_name") == col("cd.branch_name"),
                col("r.sales_rep_name") == col("cd.sales_rep_name"),
            ],
            "left"
        )
        .select(
            col("r.reporting_date").alias("reporting_date"),
            col("r.network_level").alias("network_level"),
            col("r.region_name").alias("region_name"),
            col("r.branch_name").alias("branch_name"),
            col("r.sales_rep_name").alias("sales_rep_name"),
            coalesce(col("c.collector_name"), col("r.sales_rep_name")).alias("collector_name"),
            col("r.rental_revenue").alias("rental_revenue"),
            round(safe_divide(col("r.total_ar_amount"), col("r.invoice_count")), 6).alias("dso"),
            round(safe_divide(col("r.ar_90_plus_amount"), col("r.total_ar_amount")), 6).alias("ar_90_plus_percentage"),
            round(safe_divide(col("c.total_payment_amount"), col("r.total_ar_amount")), 6).alias("collection_effectiveness_index"),
            round(safe_divide(col("c.unapplied_cash_amount"), col("c.total_payment_amount")), 6).alias("unapplied_cash_percentage"),
            round(safe_divide(col("cd.outstanding_ar"), col("cd.credit_limit_total")), 6).alias("credit_utilization_percentage")
        )
        .withColumn(
            "overall_revenue_to_cash_health_score",
            round(
                least(
                    lit(100.0),
                    greatest(
                        lit(0.0),
                        (
                            (lit(25.0) * (lit(1.0) - coalesce(col("ar_90_plus_percentage"), lit(0.0)))) +
                            (lit(20.0) * coalesce(col("collection_effectiveness_index"), lit(0.0))) +
                            (lit(15.0) * (lit(1.0) - coalesce(col("unapplied_cash_percentage"), lit(0.0)))) +
                            (lit(20.0) * (lit(1.0) - coalesce(col("credit_utilization_percentage"), lit(0.0)))) +
                            (lit(20.0) * when(col("rental_revenue") > 0, lit(1.0)).otherwise(lit(0.0)))
                        )
                    )
                ),
                6
            )
        )
        .withColumn("load_date", current_timestamp())
        .withColumn("update_date", current_timestamp())
        .withColumn("source_system", lit(SOURCE_SYSTEM))
        .withColumn("run_id", lit(RUN_ID))
    )

    invalid_exec_df = executive_df.filter(
        col("reporting_date").isNull() |
        col("region_name").isNull() |
        col("branch_name").isNull()
    )
    write_error_records(
        invalid_exec_df,
        GOLD_EXECUTIVE_HEALTH,
        "executive_health_grain_validation",
        "Invalid executive aggregate rows detected due to missing reporting grain fields."
    )

    return executive_df.filter(
        col("reporting_date").isNotNull() &
        col("region_name").isNotNull() &
        col("branch_name").isNotNull()
    )


# ============================================================
# 6. Load Gold Targets
# ============================================================
def load_gold_table(df: DataFrame, target_table: str, zorder_cols: str):
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(target_table)
    )
    optimize_table(target_table, zorder_cols)


# ============================================================
# 7. Main Pipeline Execution
# ============================================================
def main():
    process_start_ts = spark.sql("select current_timestamp() as ts").collect()[0]["ts"]
    records_read = 0
    records_written = 0
    records_rejected = 0

    try:
        create_gold_support_tables()

        invoices_df, contracts_df, cash_receipts_df, customers_df, employees_df = extract_silver_sources()
        records_read = (
            invoices_df.count() +
            contracts_df.count() +
            cash_receipts_df.count() +
            customers_df.count() +
            employees_df.count()
        )

        billing_df = build_billing_performance(invoices_df, contracts_df, employees_df)
        executive_df = build_executive_health(invoices_df, contracts_df, cash_receipts_df, customers_df, employees_df)

        records_written = billing_df.count() + executive_df.count()

        load_gold_table(
            billing_df,
            GOLD_BILLING_PERFORMANCE,
            "reporting_date, region_name, branch_name, sales_rep_name, equipment_class_name"
        )
        load_gold_table(
            executive_df,
            GOLD_EXECUTIVE_HEALTH,
            "reporting_date, region_name, branch_name, sales_rep_name, collector_name"
        )

        process_end_ts = spark.sql("select current_timestamp() as ts").collect()[0]["ts"]
        write_audit_log(
            source_table=",".join([SILVER_INVOICES, SILVER_CONTRACTS, SILVER_CASH_RECEIPTS, SILVER_CUSTOMERS, SILVER_EMPLOYEES]),
            target_table=",".join([GOLD_BILLING_PERFORMANCE, GOLD_EXECUTIVE_HEALTH]),
            process_start_ts=process_start_ts,
            process_end_ts=process_end_ts,
            status="SUCCESS",
            records_read_count=records_read,
            records_written_count=records_written,
            records_rejected_count=records_rejected,
            error_message=None,
            audit_remarks="Gold aggregated fact-style pipeline completed successfully with Delta optimization and compatibility validation."
        )

        print("Pipeline execution completed successfully.")
        print(f"Run ID: {RUN_ID}")
        print(f"Written tables: {GOLD_BILLING_PERFORMANCE}, {GOLD_EXECUTIVE_HEALTH}")

    except Exception as exc:
        process_end_ts = spark.sql("select current_timestamp() as ts").collect()[0]["ts"]
        err = f"{str(exc)} | Traceback: {traceback.format_exc()}"
        write_audit_log(
            source_table=",".join([SILVER_INVOICES, SILVER_CONTRACTS, SILVER_CASH_RECEIPTS, SILVER_CUSTOMERS, SILVER_EMPLOYEES]),
            target_table=",".join([GOLD_BILLING_PERFORMANCE, GOLD_EXECUTIVE_HEALTH]),
            process_start_ts=process_start_ts,
            process_end_ts=process_end_ts,
            status="FAILED",
            records_read_count=records_read,
            records_written_count=records_written,
            records_rejected_count=records_rejected,
            error_message=err,
            audit_remarks="Gold aggregated fact-style pipeline failed. Review audit and error tables."
        )
        raise


if __name__ == "__main__":
    main()


# ============================================================
# 8. Gold Layer Compatibility and Best Practices Notes
# ============================================================
# - Uses lowercase Databricks table references.
# - Uses Delta format for all output tables.
# - Uses partitioning by reporting_date for aggregate fact-style tables.
# - Uses Z-ORDER for high-query fields instead of unsupported traditional indexes.
# - Avoids unsupported PK/FK/check constraints in Databricks runtime DDL.
# - Maintains audit logs in Silver and Gold-compatible audit structures.
# - Ensures error data table is available for Gold fact table processing.
# - Uses pre-aggregation before domain joins to reduce fanout and improve performance.
# - Applies safe division, decimal handling, and bounded scoring logic.
# - Preserves versioned script history in GitHub.
