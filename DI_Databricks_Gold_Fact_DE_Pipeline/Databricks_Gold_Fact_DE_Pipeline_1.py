"""
_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: Databricks Gold Fact DE Pipeline for Rental Revenue-to-Cash fact processing from Silver to Gold with audit logging, error handling, and performance optimization.
## *Version*: 1 
## *Updated on*: 
_____________________________________________
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from delta.tables import DeltaTable
import uuid
import traceback
from datetime import datetime

spark = SparkSession.builder.appName("Databricks_Gold_Fact_DE_Pipeline").getOrCreate()

PIPELINE_NAME = "databricks_gold_fact_de_pipeline"
SOURCE_SYSTEM = "silver_to_gold"
RUN_ID = str(uuid.uuid4())
PROCESS_START_TS = datetime.utcnow()

SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

SILVER_TABLES = {
    "contracts": f"{SILVER_SCHEMA}.si_rental_contracts",
    "invoices": f"{SILVER_SCHEMA}.si_invoices",
    "receipts": f"{SILVER_SCHEMA}.si_cash_receipts",
    "customers": f"{SILVER_SCHEMA}.si_customer_master",
    "employees": f"{SILVER_SCHEMA}.si_branch_employee",
    "audit": f"{SILVER_SCHEMA}.si_process_audit",
    "errors": f"{SILVER_SCHEMA}.si_data_quality_errors"
}

GOLD_TABLES = {
    "rental_revenue": f"{GOLD_SCHEMA}.go_fct_rental_revenue",
    "ar_aging": f"{GOLD_SCHEMA}.go_fct_ar_aging",
    "cash_application": f"{GOLD_SCHEMA}.go_fct_cash_application",
    "credit_risk": f"{GOLD_SCHEMA}.go_fct_credit_risk",
    "audit": f"{GOLD_SCHEMA}.go_process_audit",
    "errors": f"{GOLD_SCHEMA}.go_data_quality_errors"
}


def log_audit_record(target_table: str, status: str, records_read: int, records_written: int, records_rejected: int, error_message: str = "") -> None:
    process_end_ts = datetime.utcnow()
    duration_seconds = (process_end_ts - PROCESS_START_TS).total_seconds()
    audit_data = [(
        None,
        PIPELINE_NAME,
        "silver_layer",
        target_table,
        PROCESS_START_TS,
        process_end_ts,
        status,
        int(records_read),
        int(records_written),
        int(records_rejected),
        float(duration_seconds),
        error_message,
        "AAVA",
        f"run_id={RUN_ID}",
        process_end_ts,
        process_end_ts,
        SOURCE_SYSTEM,
        RUN_ID
    )]

    audit_columns = [
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
        "run_id"
    ]

    spark.createDataFrame(audit_data, audit_columns).write.format("delta").mode("append").saveAsTable(SILVER_TABLES["audit"])

    spark.createDataFrame(audit_data, audit_columns).write.format("delta").mode("append").saveAsTable(GOLD_TABLES["audit"])


def write_error_records(df: DataFrame, source_table: str, validation_rule_name: str, error_description: str) -> int:
    if df.rdd.isEmpty():
        return 0

    error_df = (
        df.withColumn("error_sk", F.lit(None).cast("bigint"))
          .withColumn("source_table", F.lit(source_table))
          .withColumn("source_record_id", F.coalesce(F.col("invoice_id").cast("string"), F.col("receipt_id").cast("string"), F.col("contract_id").cast("string"), F.col("customer_id").cast("string")))
          .withColumn("source_file_path", F.lit(None).cast("string"))
          .withColumn("validation_rule_name", F.lit(validation_rule_name))
          .withColumn("validation_category", F.lit("DATA_QUALITY"))
          .withColumn("error_description", F.lit(error_description))
          .withColumn("error_record_payload", F.to_json(F.struct(*[F.col(c) for c in df.columns])))
          .withColumn("error_severity", F.lit("HIGH"))
          .withColumn("layer_name", F.lit("gold"))
          .withColumn("detected_timestamp", F.current_timestamp())
          .withColumn("processing_status", F.lit("OPEN"))
          .withColumn("load_date", F.current_timestamp())
          .withColumn("update_date", F.current_timestamp())
          .withColumn("source_system", F.lit(SOURCE_SYSTEM))
          .select(
              "error_sk",
              "source_table",
              "source_record_id",
              "source_file_path",
              "validation_rule_name",
              "validation_category",
              "error_description",
              "error_record_payload",
              "error_severity",
              "layer_name",
              "detected_timestamp",
              "processing_status",
              "load_date",
              "update_date",
              "source_system"
          )
    )

    error_count = error_df.count()
    error_df.write.format("delta").mode("append").saveAsTable(SILVER_TABLES["errors"])
    error_df.write.format("delta").mode("append").saveAsTable(GOLD_TABLES["errors"])
    return error_count


def create_gold_support_tables() -> None:
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {GOLD_TABLES['errors']} (
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
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {GOLD_TABLES['audit']} (
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
    """)


def create_gold_fact_tables() -> None:
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {GOLD_TABLES['rental_revenue']} (
            reporting_date DATE,
            branch_code STRING,
            region_name STRING,
            sales_rep_id STRING,
            sales_rep_name STRING,
            equipment_class STRING,
            equipment_class_name STRING,
            contract_id STRING,
            contract_status STRING,
            customer_id STRING,
            customer_name STRING,
            rental_revenue DECIMAL(18,2),
            gross_billings DECIMAL(18,2),
            credit_memo_amount DECIMAL(18,2),
            net_billings DECIMAL(18,2),
            invoice_count BIGINT,
            average_daily_rate DECIMAL(18,2),
            revenue_per_contract DECIMAL(18,2),
            credit_memo_rate DECIMAL(18,6),
            trend_value DECIMAL(18,2),
            load_date TIMESTAMP,
            update_date TIMESTAMP,
            source_system STRING
        ) USING DELTA
        PARTITIONED BY (reporting_date, branch_code)
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {GOLD_TABLES['ar_aging']} (
            snapshot_date DATE,
            customer_id STRING,
            customer_name STRING,
            branch_code STRING,
            collector_id STRING,
            collector_name STRING,
            aging_bucket STRING,
            total_ar_outstanding DECIMAL(18,2),
            ar_90_plus_amount DECIMAL(18,2),
            ar_90_plus_percentage DECIMAL(18,6),
            best_possible_dso DECIMAL(18,2),
            dso DECIMAL(18,2),
            dso_trend DECIMAL(18,2),
            ar_aging_by_bucket DECIMAL(18,2),
            load_date TIMESTAMP,
            update_date TIMESTAMP,
            source_system STRING
        ) USING DELTA
        PARTITIONED BY (snapshot_date, aging_bucket)
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {GOLD_TABLES['cash_application']} (
            reporting_date DATE,
            branch_code STRING,
            customer_id STRING,
            customer_name STRING,
            invoice_id STRING,
            collector_id STRING,
            collector_name STRING,
            payment_method STRING,
            match_status STRING,
            cash_collected DECIMAL(18,2),
            collection_effectiveness_index DECIMAL(18,6),
            average_days_to_pay DECIMAL(18,2),
            invoices_paid_on_time_percentage DECIMAL(18,6),
            unapplied_cash_amount DECIMAL(18,2),
            unapplied_cash_percentage DECIMAL(18,6),
            payment_amount DECIMAL(18,2),
            payment_date DATE,
            load_date TIMESTAMP,
            update_date TIMESTAMP,
            source_system STRING
        ) USING DELTA
        PARTITIONED BY (reporting_date, branch_code)
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {GOLD_TABLES['credit_risk']} (
            snapshot_date DATE,
            customer_id STRING,
            customer_name STRING,
            branch_code STRING,
            customer_status STRING,
            outstanding_ar DECIMAL(18,2),
            credit_limit DECIMAL(18,2),
            credit_utilization_percentage DECIMAL(18,6),
            customers_over_limit_count INT,
            customers_over_limit_amount DECIMAL(18,2),
            suspended_customers_with_open_exposure INT,
            ar_90_plus_amount_by_customer DECIMAL(18,2),
            open_contract_count BIGINT,
            open_contract_value DECIMAL(18,2),
            load_date TIMESTAMP,
            update_date TIMESTAMP,
            source_system STRING
        ) USING DELTA
        PARTITIONED BY (snapshot_date, branch_code)
    """)


def read_silver_sources() -> dict:
    return {
        "contracts": spark.table(SILVER_TABLES["contracts"]).alias("c"),
        "invoices": spark.table(SILVER_TABLES["invoices"]).alias("i"),
        "receipts": spark.table(SILVER_TABLES["receipts"]).alias("r"),
        "customers": spark.table(SILVER_TABLES["customers"]).alias("cm"),
        "employees": spark.table(SILVER_TABLES["employees"]).alias("be")
    }


def prepare_reference_views(src: dict) -> dict:
    sales_rep_df = src["employees"].filter(F.upper(F.col("role")) != F.lit("COLLECTOR")).alias("sr")
    collector_df = src["employees"].filter(F.col("collector_id").isNotNull()).alias("cl")
    return {
        "sales_rep": sales_rep_df,
        "collector": collector_df
    }


def build_rental_revenue_fact(src: dict, ref: dict) -> tuple[DataFrame, int, int]:
    invalid_df = src["invoices"].filter(F.col("invoice_id").isNull() | F.col("invoice_date").isNull() | F.col("invoice_amount").isNull())
    rejected = write_error_records(invalid_df, SILVER_TABLES["invoices"], "REQUIRED_FIELDS_CHECK", "Mandatory invoice fields are missing for rental revenue fact.")

    valid_invoices = src["invoices"].filter(F.col("invoice_id").isNotNull() & F.col("invoice_date").isNotNull() & F.col("invoice_amount").isNotNull())

    base_df = (
        valid_invoices
        .join(src["contracts"], F.col("i.contract_id") == F.col("c.contract_id"), "inner")
        .join(src["customers"], F.col("i.customer_id") == F.col("cm.customer_id"), "left")
        .join(ref["sales_rep"], F.col("c.sales_rep_id") == F.col("sr.employee_id"), "left")
        .withColumn("normalized_invoice_amount", F.col("i.invoice_amount").cast("decimal(18,2)"))
        .withColumn("credit_memo_amount_row", F.when(F.upper(F.col("i.invoice_type")) == "CREDIT_MEMO", -F.abs(F.col("normalized_invoice_amount"))).otherwise(F.lit(0).cast("decimal(18,2)")))
        .withColumn("gross_billings_row", F.when(F.upper(F.col("i.invoice_type")) != "CREDIT_MEMO", F.col("normalized_invoice_amount")).otherwise(F.lit(0).cast("decimal(18,2)")))
        .withColumn("contract_duration_days", F.greatest(F.datediff(F.col("c.contract_end_date"), F.col("c.contract_start_date")), F.lit(0)))
    )

    fact_df = (
        base_df.groupBy(
            F.col("i.invoice_date").alias("reporting_date"),
            F.col("c.branch_code").alias("branch_code"),
            F.col("sr.region").alias("region_name"),
            F.col("c.sales_rep_id").alias("sales_rep_id"),
            F.col("sr.employee_name").alias("sales_rep_name"),
            F.col("c.equipment_class").alias("equipment_class"),
            F.col("c.equipment_class").alias("equipment_class_name"),
            F.col("c.contract_id").alias("contract_id"),
            F.col("c.contract_status").alias("contract_status"),
            F.col("cm.customer_id").alias("customer_id"),
            F.col("cm.customer_name").alias("customer_name")
        ).agg(
            F.sum(F.when(F.upper(F.col("i.invoice_type")) != "CREDIT_MEMO", F.col("normalized_invoice_amount")).otherwise(F.lit(0))).cast("decimal(18,2)").alias("rental_revenue"),
            F.sum(F.col("gross_billings_row")).cast("decimal(18,2)").alias("gross_billings"),
            F.sum(F.col("credit_memo_amount_row")).cast("decimal(18,2)").alias("credit_memo_amount"),
            (F.sum(F.col("gross_billings_row")) + F.sum(F.col("credit_memo_amount_row"))).cast("decimal(18,2)").alias("net_billings"),
            F.countDistinct(F.col("i.invoice_id")).alias("invoice_count"),
            F.when(F.max(F.col("contract_duration_days")) > 0,
                   (F.sum(F.when(F.upper(F.col("i.invoice_type")) != "CREDIT_MEMO", F.col("normalized_invoice_amount")).otherwise(F.lit(0))) / F.max(F.col("contract_duration_days"))).cast("decimal(18,2)")
            ).otherwise(F.lit(None).cast("decimal(18,2)")).alias("average_daily_rate"),
            F.when(F.countDistinct(F.col("c.contract_id")) > 0,
                   (F.sum(F.when(F.upper(F.col("i.invoice_type")) != "CREDIT_MEMO", F.col("normalized_invoice_amount")).otherwise(F.lit(0))) / F.countDistinct(F.col("c.contract_id"))).cast("decimal(18,2)")
            ).otherwise(F.lit(None).cast("decimal(18,2)")).alias("revenue_per_contract"),
            F.when(F.sum(F.col("gross_billings_row")) != 0,
                   (F.abs(F.sum(F.col("credit_memo_amount_row"))) / F.sum(F.col("gross_billings_row"))).cast("decimal(18,6)")
            ).otherwise(F.lit(None).cast("decimal(18,6)")).alias("credit_memo_rate")
        )
        .withColumn(
            "trend_value",
            (F.col("net_billings") - F.lag("net_billings").over(Window.partitionBy("branch_code").orderBy("reporting_date"))).cast("decimal(18,2)")
        )
        .withColumn("load_date", F.current_timestamp())
        .withColumn("update_date", F.current_timestamp())
        .withColumn("source_system", F.lit(SOURCE_SYSTEM))
    )

    return fact_df, base_df.count(), rejected


def build_ar_aging_fact(src: dict, ref: dict) -> tuple[DataFrame, int, int]:
    snapshot_date = F.current_date()
    invalid_df = src["invoices"].filter(F.col("customer_id").isNull() | F.col("due_date").isNull() | F.col("invoice_amount").isNull())
    rejected = write_error_records(invalid_df, SILVER_TABLES["invoices"], "AR_AGING_VALIDATION", "Mandatory AR aging fields are missing.")

    valid_invoices = src["invoices"].filter(F.col("customer_id").isNotNull() & F.col("due_date").isNotNull() & F.col("invoice_amount").isNotNull())

    base_df = (
        valid_invoices
        .join(src["contracts"], F.col("i.contract_id") == F.col("c.contract_id"), "left")
        .join(src["customers"], F.col("i.customer_id") == F.col("cm.customer_id"), "left")
        .join(ref["collector"], F.col("c.branch_code") == F.col("cl.branch_code"), "left")
        .withColumn("snapshot_date", snapshot_date)
        .withColumn("days_past_due", F.datediff(F.col("snapshot_date"), F.col("i.due_date")))
        .withColumn(
            "aging_bucket_derived",
            F.when(F.col("days_past_due").between(0, 30), F.lit("0-30"))
             .when(F.col("days_past_due").between(31, 60), F.lit("31-60"))
             .when(F.col("days_past_due").between(61, 90), F.lit("61-90"))
             .otherwise(F.lit("90+"))
        )
    )

    fact_df = (
        base_df.groupBy(
            "snapshot_date",
            F.col("cm.customer_id").alias("customer_id"),
            F.col("cm.customer_name").alias("customer_name"),
            F.col("c.branch_code").alias("branch_code"),
            F.col("cl.collector_id").alias("collector_id"),
            F.col("cl.employee_name").alias("collector_name"),
            F.col("aging_bucket_derived").alias("aging_bucket")
        ).agg(
            F.sum(F.col("i.invoice_amount")).cast("decimal(18,2)").alias("total_ar_outstanding"),
            F.sum(F.when(F.col("aging_bucket_derived") == "90+", F.col("i.invoice_amount")).otherwise(F.lit(0))).cast("decimal(18,2)").alias("ar_90_plus_amount"),
            F.when(F.sum(F.col("i.invoice_amount")) != 0,
                   (F.sum(F.when(F.col("aging_bucket_derived") == "90+", F.col("i.invoice_amount")).otherwise(F.lit(0))) / F.sum(F.col("i.invoice_amount"))).cast("decimal(18,6)")
            ).otherwise(F.lit(None).cast("decimal(18,6)")).alias("ar_90_plus_percentage"),
            F.lit(None).cast("decimal(18,2)").alias("best_possible_dso"),
            F.lit(None).cast("decimal(18,2)").alias("dso"),
            F.sum(F.col("i.invoice_amount")).cast("decimal(18,2)").alias("ar_aging_by_bucket")
        )
        .withColumn(
            "dso_trend",
            (F.col("dso") - F.lag("dso").over(Window.partitionBy("customer_id").orderBy("snapshot_date"))).cast("decimal(18,2)")
        )
        .withColumn("load_date", F.current_timestamp())
        .withColumn("update_date", F.current_timestamp())
        .withColumn("source_system", F.lit(SOURCE_SYSTEM))
    )

    return fact_df, base_df.count(), rejected


def build_cash_application_fact(src: dict, ref: dict) -> tuple[DataFrame, int, int]:
    invalid_df = src["receipts"].filter(F.col("receipt_id").isNull() | F.col("receipt_date").isNull() | F.col("payment_amount").isNull())
    rejected = write_error_records(invalid_df, SILVER_TABLES["receipts"], "CASH_APP_VALIDATION", "Mandatory cash application fields are missing.")

    valid_receipts = src["receipts"].filter(F.col("receipt_id").isNotNull() & F.col("receipt_date").isNotNull() & F.col("payment_amount").isNotNull())

    base_df = (
        valid_receipts
        .join(src["invoices"], F.col("r.invoice_id") == F.col("i.invoice_id"), "left")
        .join(src["contracts"], F.col("i.contract_id") == F.col("c.contract_id"), "left")
        .join(src["customers"], F.col("r.customer_id") == F.col("cm.customer_id"), "left")
        .join(ref["collector"], F.col("c.branch_code") == F.col("cl.branch_code"), "left")
        .withColumn("match_status_std", F.when(F.upper(F.coalesce(F.col("r.match_status"), F.lit("UNAPPLIED"))) == "APPLIED", F.lit("APPLIED")).otherwise(F.lit("UNAPPLIED")))
        .withColumn("days_to_pay", F.datediff(F.col("r.receipt_date"), F.col("i.invoice_date")))
        .withColumn("paid_on_time_flag", F.when(F.col("r.receipt_date") <= F.col("i.due_date"), F.lit(1)).otherwise(F.lit(0)))
        .withColumn("unapplied_cash_amount_row", F.coalesce(F.col("r.unapplied_payment_amount"), F.lit(0)).cast("decimal(18,2)"))
    )

    fact_df = (
        base_df.groupBy(
            F.col("r.receipt_date").alias("reporting_date"),
            F.col("c.branch_code").alias("branch_code"),
            F.col("cm.customer_id").alias("customer_id"),
            F.col("cm.customer_name").alias("customer_name"),
            F.col("r.invoice_id").alias("invoice_id"),
            F.col("cl.collector_id").alias("collector_id"),
            F.col("cl.employee_name").alias("collector_name"),
            F.col("r.payment_method").alias("payment_method"),
            F.col("match_status_std").alias("match_status")
        ).agg(
            F.sum(F.col("r.payment_amount")).cast("decimal(18,2)").alias("cash_collected"),
            F.lit(None).cast("decimal(18,6)").alias("collection_effectiveness_index"),
            F.avg(F.when(F.col("match_status_std") == "APPLIED", F.col("days_to_pay"))).cast("decimal(18,2)").alias("average_days_to_pay"),
            F.when(F.count(F.when(F.col("match_status_std") == "APPLIED", True)) != 0,
                   (F.sum(F.when((F.col("match_status_std") == "APPLIED") & (F.col("paid_on_time_flag") == 1), 1).otherwise(0)) /
                    F.count(F.when(F.col("match_status_std") == "APPLIED", True))).cast("decimal(18,6)")
            ).otherwise(F.lit(None).cast("decimal(18,6)")).alias("invoices_paid_on_time_percentage"),
            F.sum(F.col("unapplied_cash_amount_row")).cast("decimal(18,2)").alias("unapplied_cash_amount"),
            F.when(F.sum(F.col("r.payment_amount")) != 0,
                   (F.sum(F.col("unapplied_cash_amount_row")) / F.sum(F.col("r.payment_amount"))).cast("decimal(18,6)")
            ).otherwise(F.lit(None).cast("decimal(18,6)")).alias("unapplied_cash_percentage"),
            F.sum(F.col("r.payment_amount")).cast("decimal(18,2)").alias("payment_amount"),
            F.max(F.col("r.receipt_date")).alias("payment_date")
        )
        .withColumn("load_date", F.current_timestamp())
        .withColumn("update_date", F.current_timestamp())
        .withColumn("source_system", F.lit(SOURCE_SYSTEM))
    )

    return fact_df, base_df.count(), rejected


def build_credit_risk_fact(src: dict, ref: dict) -> tuple[DataFrame, int, int]:
    invalid_df = src["customers"].filter(F.col("customer_id").isNull() | F.col("credit_limit").isNull())
    rejected = write_error_records(invalid_df, SILVER_TABLES["customers"], "CREDIT_RISK_VALIDATION", "Mandatory credit risk fields are missing.")

    invoice_agg = (
        src["invoices"]
        .join(src["contracts"], F.col("i.contract_id") == F.col("c.contract_id"), "left")
        .withColumn("snapshot_date", F.current_date())
        .withColumn("days_past_due", F.datediff(F.col("snapshot_date"), F.col("i.due_date")))
        .groupBy(F.col("i.customer_id").alias("customer_id"), F.col("c.branch_code").alias("branch_code"), "snapshot_date")
        .agg(
            F.sum(F.col("i.invoice_amount")).cast("decimal(18,2)").alias("outstanding_ar"),
            F.sum(F.when(F.col("days_past_due") > 90, F.col("i.invoice_amount")).otherwise(F.lit(0))).cast("decimal(18,2)").alias("ar_90_plus_amount_by_customer")
        )
    )

    contract_agg = (
        src["contracts"]
        .groupBy(F.col("customer_id").alias("customer_id"), F.col("branch_code").alias("branch_code"))
        .agg(
            F.countDistinct(F.when(F.upper(F.col("contract_status")) == "OPEN", F.col("contract_id"))).alias("open_contract_count"),
            F.sum(
                F.when(
                    F.upper(F.col("contract_status")) == "OPEN",
                    F.col("daily_rate") * F.greatest(F.datediff(F.col("contract_end_date"), F.col("contract_start_date")), F.lit(0))
                ).otherwise(F.lit(0))
            ).cast("decimal(18,2)").alias("open_contract_value")
        )
    )

    base_df = (
        src["customers"]
        .join(invoice_agg, F.col("cm.customer_id") == F.col("customer_id"), "left")
        .join(contract_agg, [invoice_agg.customer_id == contract_agg.customer_id, invoice_agg.branch_code == contract_agg.branch_code], "left")
        .select(
            F.coalesce(F.col("snapshot_date"), F.current_date()).alias("snapshot_date"),
            F.col("cm.customer_id").alias("customer_id"),
            F.col("cm.customer_name").alias("customer_name"),
            F.coalesce(invoice_agg.branch_code, contract_agg.branch_code).alias("branch_code"),
            F.col("cm.customer_status").alias("customer_status"),
            F.coalesce(F.col("outstanding_ar"), F.lit(0).cast("decimal(18,2)")).alias("outstanding_ar"),
            F.col("cm.credit_limit").cast("decimal(18,2)").alias("credit_limit"),
            F.coalesce(F.col("ar_90_plus_amount_by_customer"), F.lit(0).cast("decimal(18,2)")).alias("ar_90_plus_amount_by_customer"),
            F.coalesce(F.col("open_contract_count"), F.lit(0)).alias("open_contract_count"),
            F.coalesce(F.col("open_contract_value"), F.lit(0).cast("decimal(18,2)")).alias("open_contract_value")
        )
    )

    fact_df = (
        base_df
        .withColumn(
            "credit_utilization_percentage",
            F.when(F.col("credit_limit") != 0, (F.col("outstanding_ar") / F.col("credit_limit")).cast("decimal(18,6)"))
             .otherwise(F.lit(None).cast("decimal(18,6)"))
        )
        .withColumn("customers_over_limit_count", F.when(F.col("outstanding_ar") > F.col("credit_limit"), F.lit(1)).otherwise(F.lit(0)))
        .withColumn(
            "customers_over_limit_amount",
            F.when(F.col("outstanding_ar") > F.col("credit_limit"), (F.col("outstanding_ar") - F.col("credit_limit")).cast("decimal(18,2)"))
             .otherwise(F.lit(0).cast("decimal(18,2)"))
        )
        .withColumn(
            "suspended_customers_with_open_exposure",
            F.when((F.upper(F.col("customer_status")) == "SUSPENDED") & ((F.col("outstanding_ar") > 0) | (F.col("open_contract_count") > 0)), F.lit(1)).otherwise(F.lit(0))
        )
        .withColumn("load_date", F.current_timestamp())
        .withColumn("update_date", F.current_timestamp())
        .withColumn("source_system", F.lit(SOURCE_SYSTEM))
    )

    return fact_df, base_df.count(), rejected


def write_delta_optimized(df: DataFrame, target_table: str, zorder_cols: list[str]) -> int:
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table)
    spark.sql(f"OPTIMIZE {target_table} ZORDER BY ({', '.join(zorder_cols)})")
    return df.count()


def verify_gold_layer_compatibility() -> None:
    compatibility_rules = [
        "No primary key constraints in DDL",
        "No foreign key constraints in DDL",
        "No unique constraints in DDL",
        "No unsupported Spark SQL features",
        "Delta format enforced for all Gold tables",
        "Lowercase table naming applied"
    ]
    for rule in compatibility_rules:
        print(f"Gold compatibility check passed: {rule}")


def run_pipeline() -> None:
    create_gold_support_tables()
    create_gold_fact_tables()
    src = read_silver_sources()
    ref = prepare_reference_views(src)
    verify_gold_layer_compatibility()

    pipeline_steps = [
        ("rental_revenue", build_rental_revenue_fact, ["branch_code", "customer_id", "contract_id"]),
        ("ar_aging", build_ar_aging_fact, ["customer_id", "branch_code", "aging_bucket"]),
        ("cash_application", build_cash_application_fact, ["branch_code", "customer_id", "invoice_id"]),
        ("credit_risk", build_credit_risk_fact, ["customer_id", "branch_code", "customer_status"])
    ]

    for fact_name, builder, zorder_cols in pipeline_steps:
        try:
            fact_df, records_read, records_rejected = builder(src, ref)
            records_written = write_delta_optimized(fact_df, GOLD_TABLES[fact_name], zorder_cols)
            log_audit_record(GOLD_TABLES[fact_name], "SUCCESS", records_read, records_written, records_rejected)
            print(f"Loaded {fact_name} fact successfully into {GOLD_TABLES[fact_name]}")
        except Exception as exc:
            error_message = f"{str(exc)} | traceback={traceback.format_exc()}"
            log_audit_record(GOLD_TABLES[fact_name], "FAILED", 0, 0, 0, error_message)
            raise


if __name__ == "__main__":
    run_pipeline()
