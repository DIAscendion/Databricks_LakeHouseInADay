"""
_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Updated Databricks Silver DE Pipeline for Rental Revenue-to-Cash Bronze-to-Silver processing with stronger schema enforcement, business rule validation, Delta merge loading, error routing, audit logging, and AP-1 aligned controls.
## *Version*: 3
## *Updated on*:
_____________________________________________
"""

from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T
from delta.tables import DeltaTable
import logging
import sys
import uuid
import json
import datetime
from typing import Dict, Tuple, List


class SilverPipelineConfig:
    BRONZE_TABLES = {
        "rental_contracts": "bronze.bz_rental_contracts",
        "invoices": "bronze.bz_invoices",
        "cash_receipts": "bronze.bz_cash_receipts",
        "customer_master": "bronze.bz_customer_master",
        "branch_employee": "bronze.bz_branch_employee",
    }

    SILVER_TABLES = {
        "rental_contracts": "silver.si_rental_contracts",
        "invoices": "silver.si_invoices",
        "cash_receipts": "silver.si_cash_receipts",
        "customer_master": "silver.si_customer_master",
        "branch_employee": "silver.si_branch_employee",
        "error_data": "silver.si_error_data",
        "pipeline_audit": "silver.si_pipeline_audit",
    }

    GOLD_ERROR_TABLE = "gold.si_error_data"
    PIPELINE_NAME = "databricks_silver_de_pipeline_v3"
    PIPELINE_LAYER = "Silver"
    SOURCE_LAYER = "Bronze"
    VALID_CONTRACT_STATUS = ["OPEN", "CLOSED", "ACTIVE", "CANCELLED", "PENDING"]
    VALID_INVOICE_TYPES = ["INVOICE", "CREDIT_MEMO", "DEBIT_MEMO"]
    VALID_CUSTOMER_STATUS = ["ACTIVE", "SUSPENDED", "INACTIVE", "CLOSED"]
    VALID_PAYMENT_METHODS = ["CASH", "CHECK", "CARD", "ACH", "WIRE", "LOCKBOX"]
    VALID_ROLES = ["SALES_REP", "COLLECTOR"]
    DATE_FORMATS = ["yyyy-MM-dd", "MM/dd/yyyy", "yyyyMMdd"]
    DEFAULT_SOURCE_SYSTEM = "BRONZE"

    TABLE_KEYS = {
        "rental_contracts": ["contract_id"],
        "invoices": ["invoice_id"],
        "cash_receipts": ["receipt_id"],
        "customer_master": ["customer_id"],
        "branch_employee": ["employee_id", "branch_code"],
    }

    TABLE_ZORDER = {
        "rental_contracts": ["contract_id", "customer_id", "branch_code"],
        "invoices": ["invoice_id", "contract_id", "customer_id", "due_date"],
        "cash_receipts": ["receipt_id", "invoice_id", "customer_id"],
        "customer_master": ["customer_id", "customer_status"],
        "branch_employee": ["employee_id", "branch_code", "region"],
    }


class SparkFactory:
    @staticmethod
    def get_spark() -> SparkSession:
        return (
            SparkSession.builder.appName("DatabricksSilverDEPipelineV3")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.databricks.delta.optimizeWrite.enabled", "true")
            .config("spark.databricks.delta.autoCompact.enabled", "true")
            .getOrCreate()
        )


class LogFactory:
    @staticmethod
    def get_logger() -> logging.Logger:
        logger = logging.getLogger("DatabricksSilverDEPipelineV3")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)
        return logger


class DataFrameUtils:
    @staticmethod
    def trim(col_name: str):
        return F.trim(F.col(col_name))

    @staticmethod
    def upper_trim(col_name: str):
        return F.upper(F.trim(F.col(col_name)))

    @staticmethod
    def initcap_trim(col_name: str):
        return F.initcap(F.trim(F.col(col_name)))

    @staticmethod
    def blank_or_null(col_name: str):
        return F.col(col_name).isNull() | (F.trim(F.col(col_name)) == "")

    @staticmethod
    def parse_date(col_name: str):
        return F.coalesce(*[F.to_date(F.col(col_name), fmt) for fmt in SilverPipelineConfig.DATE_FORMATS])

    @staticmethod
    def append_reason(df: DataFrame, condition, reason: str) -> DataFrame:
        return df.withColumn(
            "error_reason",
            F.when(
                condition,
                F.when(F.col("error_reason").isNull(), F.lit(reason)).otherwise(F.concat_ws("; ", F.col("error_reason"), F.lit(reason))),
            ).otherwise(F.col("error_reason")),
        )

    @staticmethod
    def add_common_metadata(df: DataFrame) -> DataFrame:
        now_ts = F.current_timestamp()
        return (
            df.withColumn("load_date", now_ts)
            .withColumn("update_date", now_ts)
            .withColumn(
                "source_system",
                F.when(F.col("source_system").isNull() | (F.trim(F.col("source_system")) == ""), F.lit(SilverPipelineConfig.DEFAULT_SOURCE_SYSTEM))
                .otherwise(F.upper(F.trim(F.col("source_system")))),
            )
        )


class ErrorManager:
    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def build_error_records(
        self,
        df: DataFrame,
        source_table: str,
        target_table: str,
        business_key_expr,
        run_id: str,
    ) -> DataFrame:
        payload_columns = [c for c in df.columns if c != "error_reason"]
        return (
            df.filter(F.col("error_reason").isNotNull())
            .withColumn("error_record_sk", F.monotonically_increasing_id())
            .withColumn("error_id", F.expr("uuid()"))
            .withColumn("pipeline_layer", F.lit(SilverPipelineConfig.PIPELINE_LAYER))
            .withColumn("source_table_name", F.lit(source_table))
            .withColumn("target_table_name", F.lit(target_table))
            .withColumn("business_key", business_key_expr)
            .withColumn("error_category", F.lit("DATA_QUALITY"))
            .withColumn("error_rule", F.lit("SILVER_VALIDATION"))
            .withColumn("error_description", F.col("error_reason"))
            .withColumn("rejected_record_payload", F.to_json(F.struct(*[F.col(c) for c in payload_columns])))
            .withColumn("validation_status", F.lit("FAILED"))
            .withColumn("detected_timestamp", F.current_timestamp())
            .withColumn("pipeline_run_id", F.lit(run_id))
            .withColumn("pipeline_run_timestamp", F.current_timestamp())
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn(
                "source_system",
                F.when(F.col("source_system").isNull(), F.lit(SilverPipelineConfig.DEFAULT_SOURCE_SYSTEM)).otherwise(F.col("source_system")),
            )
            .select(
                "error_record_sk",
                "error_id",
                "pipeline_layer",
                "source_table_name",
                "target_table_name",
                "business_key",
                "error_category",
                "error_rule",
                "error_description",
                "rejected_record_payload",
                "validation_status",
                "detected_timestamp",
                "pipeline_run_id",
                "pipeline_run_timestamp",
                "file_path",
                "load_date",
                "update_date",
                "source_system",
            )
        )

    def persist(self, error_df: DataFrame) -> int:
        if error_df.rdd.isEmpty():
            self.logger.info("No error records to persist.")
            return 0
        error_count = error_df.count()
        error_df.write.format("delta").mode("append").saveAsTable(SilverPipelineConfig.SILVER_TABLES["error_data"])
        error_df.write.format("delta").mode("append").saveAsTable(SilverPipelineConfig.GOLD_ERROR_TABLE)
        self.logger.info(f"Persisted {error_count} error records to Silver and Gold error tables.")
        return error_count


class AuditManager:
    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def write_audit(
        self,
        run_id: str,
        source_table: str,
        target_table: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        status: str,
        records_read: int,
        records_written: int,
        records_rejected: int,
        error_message: str = None,
    ) -> None:
        duration_seconds = float(max((end_time - start_time).total_seconds(), 0.0))
        audit_df = self.spark.createDataFrame(
            [(
                None,
                run_id,
                SilverPipelineConfig.PIPELINE_NAME,
                SilverPipelineConfig.PIPELINE_LAYER,
                source_table,
                target_table,
                status,
                "BALANCED" if status == "SUCCESS" else "REVIEW_REQUIRED",
                start_time,
                end_time,
                duration_seconds,
                int(records_read),
                int(records_written),
                int(records_rejected),
                error_message,
                "AAVA",
                end_time,
                end_time,
                SilverPipelineConfig.DEFAULT_SOURCE_SYSTEM,
            )],
            schema=T.StructType([
                T.StructField("audit_sk", T.LongType(), True),
                T.StructField("pipeline_run_id", T.StringType(), True),
                T.StructField("pipeline_name", T.StringType(), True),
                T.StructField("pipeline_layer", T.StringType(), True),
                T.StructField("source_table_name", T.StringType(), True),
                T.StructField("target_table_name", T.StringType(), True),
                T.StructField("processing_status", T.StringType(), True),
                T.StructField("reconciliation_status", T.StringType(), True),
                T.StructField("processing_start_timestamp", T.TimestampType(), True),
                T.StructField("processing_end_timestamp", T.TimestampType(), True),
                T.StructField("processing_duration_seconds", T.DoubleType(), True),
                T.StructField("records_read_count", T.LongType(), True),
                T.StructField("records_written_count", T.LongType(), True),
                T.StructField("records_rejected_count", T.LongType(), True),
                T.StructField("error_message", T.StringType(), True),
                T.StructField("processed_by", T.StringType(), True),
                T.StructField("load_date", T.TimestampType(), True),
                T.StructField("update_date", T.TimestampType(), True),
                T.StructField("source_system", T.StringType(), True),
            ])
        )
        audit_df.write.format("delta").mode("append").saveAsTable(SilverPipelineConfig.SILVER_TABLES["pipeline_audit"])
        self.logger.info(f"Audit record written for {source_table} -> {target_table}.")


class DeltaWriter:
    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def merge_to_delta(self, df: DataFrame, target_table: str, merge_keys: List[str]) -> None:
        if df.rdd.isEmpty():
            self.logger.info(f"No valid records to write for {target_table}.")
            return

        if not self.spark.catalog.tableExists(target_table):
            df.write.format("delta").mode("overwrite").saveAsTable(target_table)
            self.logger.info(f"Created target table {target_table} using overwrite initial load.")
            return

        delta_tbl = DeltaTable.forName(self.spark, target_table)
        source_alias = "src"
        target_alias = "tgt"
        merge_condition = " AND ".join([f"{target_alias}.{k} <=> {source_alias}.{k}" for k in merge_keys])

        update_map = {c: f"{source_alias}.{c}" for c in df.columns if c not in []}
        insert_map = {c: f"{source_alias}.{c}" for c in df.columns}

        (
            delta_tbl.alias(target_alias)
            .merge(df.alias(source_alias), merge_condition)
            .whenMatchedUpdate(set=update_map)
            .whenNotMatchedInsert(values=insert_map)
            .execute()
        )
        self.logger.info(f"Merged records into {target_table} on keys {merge_keys}.")

    def optimize(self, table_name: str, zorder_cols: List[str]) -> None:
        if zorder_cols:
            self.spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({', '.join(zorder_cols)})")
            self.logger.info(f"Optimized {table_name} with ZORDER BY {zorder_cols}.")


class SilverTransformations:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def rental_contracts(self) -> DataFrame:
        df = self.spark.table(SilverPipelineConfig.BRONZE_TABLES["rental_contracts"])
        df = df.dropDuplicates(["contract_id"])
        df = (
            df.withColumn("contract_id", DataFrameUtils.trim("contract_id"))
            .withColumn("customer_id", DataFrameUtils.trim("customer_id"))
            .withColumn("branch_code", DataFrameUtils.upper_trim("branch_code"))
            .withColumn("sales_rep_id", DataFrameUtils.trim("sales_rep_id"))
            .withColumn("equipment_class", DataFrameUtils.upper_trim("equipment_class"))
            .withColumn("contract_start_date", DataFrameUtils.parse_date("contract_start_date"))
            .withColumn("contract_end_date", DataFrameUtils.parse_date("contract_end_date"))
            .withColumn("contract_status", DataFrameUtils.upper_trim("contract_status"))
            .withColumn("daily_rate", F.col("daily_rate").cast(T.DecimalType(18, 2)))
            .withColumn("error_reason", F.lit(None).cast("string"))
        )
        df = DataFrameUtils.add_common_metadata(df)
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("contract_id"), "contract_id is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("customer_id"), "customer_id is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("branch_code"), "branch_code is null or blank")
        df = DataFrameUtils.append_reason(df, F.col("contract_start_date").isNull(), "contract_start_date is invalid or null")
        df = DataFrameUtils.append_reason(df, ~F.col("contract_status").isin(SilverPipelineConfig.VALID_CONTRACT_STATUS), "contract_status is invalid")
        df = DataFrameUtils.append_reason(df, F.col("contract_end_date").isNotNull() & (F.col("contract_end_date") < F.col("contract_start_date")), "contract_end_date is earlier than contract_start_date")
        df = DataFrameUtils.append_reason(df, F.col("daily_rate").isNotNull() & (F.col("daily_rate") < 0), "daily_rate cannot be negative")
        return (
            df.filter(F.col("error_reason").isNull())
            .withColumn("rental_contract_sk", F.monotonically_increasing_id())
            .select(
                "rental_contract_sk", "contract_id", "customer_id", "branch_code", "sales_rep_id", "equipment_class",
                "contract_start_date", "contract_end_date", "contract_status", "daily_rate", "source_system",
                "file_path", "file_modification_time", "load_timestamp", "update_timestamp", "load_date", "update_date"
            )
        ), df

    def customer_master(self) -> DataFrame:
        df = self.spark.table(SilverPipelineConfig.BRONZE_TABLES["customer_master"])
        window_spec = Window.partitionBy("customer_id").orderBy(F.col("update_timestamp").desc_nulls_last(), F.col("load_timestamp").desc_nulls_last())
        df = (
            df.withColumn("customer_id", DataFrameUtils.trim("customer_id"))
            .withColumn("customer_name", DataFrameUtils.initcap_trim("customer_name"))
            .withColumn("credit_terms", DataFrameUtils.upper_trim("credit_terms"))
            .withColumn("credit_limit", F.col("credit_limit").cast(T.DecimalType(18, 2)))
            .withColumn("customer_since", DataFrameUtils.parse_date("customer_since"))
            .withColumn("customer_status", DataFrameUtils.upper_trim("customer_status"))
            .withColumn("rn", F.row_number().over(window_spec))
            .filter(F.col("rn") == 1)
            .drop("rn")
            .withColumn("error_reason", F.lit(None).cast("string"))
        )
        df = DataFrameUtils.add_common_metadata(df)
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("customer_id"), "customer_id is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("customer_name"), "customer_name is null or blank")
        df = DataFrameUtils.append_reason(df, ~F.col("customer_status").isin(SilverPipelineConfig.VALID_CUSTOMER_STATUS), "customer_status is invalid")
        df = DataFrameUtils.append_reason(df, F.col("credit_limit").isNotNull() & (F.col("credit_limit") < 0), "credit_limit cannot be negative")
        return (
            df.filter(F.col("error_reason").isNull())
            .withColumn("customer_sk", F.monotonically_increasing_id())
            .select(
                "customer_sk", "customer_id", "customer_name", "credit_terms", "credit_limit", "customer_since",
                "customer_status", "source_system", "file_path", "file_modification_time", "load_timestamp",
                "update_timestamp", "load_date", "update_date"
            )
        ), df

    def branch_employee(self) -> DataFrame:
        df = self.spark.table(SilverPipelineConfig.BRONZE_TABLES["branch_employee"]).dropDuplicates(["employee_id", "branch_code"])
        df = (
            df.withColumn("employee_id", DataFrameUtils.trim("employee_id"))
            .withColumn("employee_name", DataFrameUtils.initcap_trim("employee_name"))
            .withColumn("role", DataFrameUtils.upper_trim("role"))
            .withColumn("branch_code", DataFrameUtils.upper_trim("branch_code"))
            .withColumn("region", DataFrameUtils.upper_trim("region"))
            .withColumn("collector_id", DataFrameUtils.trim("collector_id"))
            .withColumn("effective_date", DataFrameUtils.parse_date("effective_date"))
            .withColumn("error_reason", F.lit(None).cast("string"))
        )
        df = DataFrameUtils.add_common_metadata(df)
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("employee_id"), "employee_id is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("employee_name"), "employee_name is null or blank")
        df = DataFrameUtils.append_reason(df, ~F.col("role").isin(SilverPipelineConfig.VALID_ROLES), "role is invalid")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("branch_code"), "branch_code is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("region"), "region is null or blank")
        return (
            df.filter(F.col("error_reason").isNull())
            .withColumn("branch_employee_sk", F.monotonically_increasing_id())
            .select(
                "branch_employee_sk", "employee_id", "employee_name", "role", "branch_code", "region", "collector_id",
                "effective_date", "source_system", "file_path", "file_modification_time", "load_timestamp",
                "update_timestamp", "load_date", "update_date"
            )
        ), df

    def rental_contracts_with_reference_checks(self, valid_contracts: DataFrame, valid_customers: DataFrame, valid_employees: DataFrame) -> Tuple[DataFrame, DataFrame]:
        df = valid_contracts.alias("c") \
            .join(valid_customers.select("customer_id").alias("m"), F.col("c.customer_id") == F.col("m.customer_id"), "left") \
            .join(valid_employees.select("employee_id").alias("e"), F.col("c.sales_rep_id") == F.col("e.employee_id"), "left") \
            .withColumn("error_reason", F.lit(None).cast("string"))
        df = DataFrameUtils.append_reason(df, F.col("m.customer_id").isNull(), "customer_id does not map to silver customer master")
        df = DataFrameUtils.append_reason(df, F.col("c.sales_rep_id").isNotNull() & F.col("e.employee_id").isNull(), "sales_rep_id does not map to branch employee")
        valid_df = df.filter(F.col("error_reason").isNull()).select("c.*")
        return valid_df, df

    def invoices(self, valid_contracts: DataFrame, valid_customers: DataFrame) -> Tuple[DataFrame, DataFrame]:
        df = self.spark.table(SilverPipelineConfig.BRONZE_TABLES["invoices"]).dropDuplicates(["invoice_id"])
        df = (
            df.withColumn("invoice_id", DataFrameUtils.trim("invoice_id"))
            .withColumn("contract_id", DataFrameUtils.trim("contract_id"))
            .withColumn("customer_id", DataFrameUtils.trim("customer_id"))
            .withColumn("invoice_date", DataFrameUtils.parse_date("invoice_date"))
            .withColumn("due_date", DataFrameUtils.parse_date("due_date"))
            .withColumn("invoice_amount", F.col("invoice_amount").cast(T.DecimalType(18, 2)))
            .withColumn("tax_amount", F.col("tax_amount").cast(T.DecimalType(18, 2)))
            .withColumn("invoice_type", DataFrameUtils.upper_trim("invoice_type"))
            .withColumn("currency", DataFrameUtils.upper_trim("currency"))
            .withColumn("error_reason", F.lit(None).cast("string"))
        )
        df = DataFrameUtils.add_common_metadata(df)
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("invoice_id"), "invoice_id is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("customer_id"), "customer_id is null or blank")
        df = DataFrameUtils.append_reason(df, F.col("invoice_date").isNull(), "invoice_date is invalid or null")
        df = DataFrameUtils.append_reason(df, F.col("due_date").isNull(), "due_date is invalid or null")
        df = DataFrameUtils.append_reason(df, ~F.col("invoice_type").isin(SilverPipelineConfig.VALID_INVOICE_TYPES), "invoice_type is invalid")
        df = DataFrameUtils.append_reason(df, ~F.col("currency").rlike("^[A-Z]{3}$"), "currency is invalid")
        df = DataFrameUtils.append_reason(df, F.col("due_date") < F.col("invoice_date"), "due_date is earlier than invoice_date")
        df = DataFrameUtils.append_reason(df, (F.col("invoice_type") == F.lit("CREDIT_MEMO")) & (F.col("invoice_amount") >= 0), "credit memo amount must be negative")
        df = DataFrameUtils.append_reason(df, (F.col("invoice_type") != F.lit("CREDIT_MEMO")) & (F.col("invoice_amount") < 0), "standard invoice amount must be non-negative")
        df = DataFrameUtils.append_reason(df, F.col("tax_amount").isNotNull() & (F.col("tax_amount") < 0), "tax_amount cannot be negative")

        ref_df = (
            df.alias("i")
            .join(valid_contracts.select("contract_id").alias("c"), F.col("i.contract_id") == F.col("c.contract_id"), "left")
            .join(valid_customers.select("customer_id").alias("m"), F.col("i.customer_id") == F.col("m.customer_id"), "left")
        )
        ref_df = DataFrameUtils.append_reason(ref_df, F.col("c.contract_id").isNull(), "contract_id does not map to valid rental contract")
        ref_df = DataFrameUtils.append_reason(ref_df, F.col("m.customer_id").isNull(), "customer_id does not map to valid customer")

        final_valid = (
            ref_df.filter(F.col("error_reason").isNull())
            .withColumn("invoice_sk", F.monotonically_increasing_id())
            .select(
                F.col("i.invoice_id").alias("invoice_id"),
                F.col("i.contract_id").alias("contract_id"),
                F.col("i.customer_id").alias("customer_id"),
                F.col("i.invoice_date").alias("invoice_date"),
                F.col("i.due_date").alias("due_date"),
                F.col("i.invoice_amount").alias("invoice_amount"),
                F.col("i.tax_amount").alias("tax_amount"),
                F.col("i.invoice_type").alias("invoice_type"),
                F.col("i.currency").alias("currency"),
                F.col("i.source_system").alias("source_system"),
                F.col("i.file_path").alias("file_path"),
                F.col("i.file_modification_time").alias("file_modification_time"),
                F.col("i.load_timestamp").alias("load_timestamp"),
                F.col("i.update_timestamp").alias("update_timestamp"),
                F.col("i.load_date").alias("load_date"),
                F.col("i.update_date").alias("update_date"),
                F.col("invoice_sk")
            )
            .withColumn(
                "aging_bucket",
                F.when(F.datediff(F.current_date(), F.col("due_date")).between(0, 30), F.lit("0-30"))
                .when(F.datediff(F.current_date(), F.col("due_date")).between(31, 60), F.lit("31-60"))
                .when(F.datediff(F.current_date(), F.col("due_date")).between(61, 90), F.lit("61-90"))
                .otherwise(F.lit("90+"))
            )
            .withColumn("days_past_due", F.datediff(F.current_date(), F.col("due_date")))
        )
        return final_valid, ref_df

    def cash_receipts(self, valid_invoices: DataFrame, valid_customers: DataFrame) -> Tuple[DataFrame, DataFrame]:
        df = self.spark.table(SilverPipelineConfig.BRONZE_TABLES["cash_receipts"]).dropDuplicates(["receipt_id"])
        df = (
            df.withColumn("receipt_id", DataFrameUtils.trim("receipt_id"))
            .withColumn("invoice_id", DataFrameUtils.trim("invoice_id"))
            .withColumn("customer_id", DataFrameUtils.trim("customer_id"))
            .withColumn("receipt_date", DataFrameUtils.parse_date("receipt_date"))
            .withColumn("payment_amount", F.col("payment_amount").cast(T.DecimalType(18, 2)))
            .withColumn("payment_method", DataFrameUtils.upper_trim("payment_method"))
            .withColumn("error_reason", F.lit(None).cast("string"))
        )
        df = DataFrameUtils.add_common_metadata(df)
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("receipt_id"), "receipt_id is null or blank")
        df = DataFrameUtils.append_reason(df, DataFrameUtils.blank_or_null("customer_id"), "customer_id is null or blank")
        df = DataFrameUtils.append_reason(df, F.col("receipt_date").isNull(), "receipt_date is invalid or null")
        df = DataFrameUtils.append_reason(df, F.col("payment_amount").isNull(), "payment_amount is invalid or null")
        df = DataFrameUtils.append_reason(df, F.col("payment_amount") < 0, "payment_amount cannot be negative")
        df = DataFrameUtils.append_reason(df, F.col("payment_method").isNotNull() & (~F.col("payment_method").isin(SilverPipelineConfig.VALID_PAYMENT_METHODS)), "payment_method is invalid")

        ref_df = (
            df.alias("r")
            .join(valid_customers.select("customer_id").alias("m"), F.col("r.customer_id") == F.col("m.customer_id"), "left")
            .join(valid_invoices.select("invoice_id", "invoice_amount").alias("i"), F.col("r.invoice_id") == F.col("i.invoice_id"), "left")
        )
        ref_df = DataFrameUtils.append_reason(ref_df, F.col("m.customer_id").isNull(), "customer_id does not map to valid customer")
        ref_df = DataFrameUtils.append_reason(ref_df, F.col("r.invoice_id").isNotNull() & F.col("i.invoice_id").isNull(), "invoice_id does not map to valid invoice")
        ref_df = DataFrameUtils.append_reason(ref_df, F.col("i.invoice_amount").isNotNull() & (F.col("r.payment_amount") > F.col("i.invoice_amount")), "payment amount exceeds invoice amount")

        final_valid = (
            ref_df.filter(F.col("error_reason").isNull())
            .withColumn("cash_receipt_sk", F.monotonically_increasing_id())
            .withColumn("match_status", F.when(F.col("r.invoice_id").isNull() | (F.trim(F.col("r.invoice_id")) == ""), F.lit("UNAPPLIED")).otherwise(F.lit("APPLIED")))
            .withColumn("unapplied_payment_amount", F.when(F.col("r.invoice_id").isNull() | (F.trim(F.col("r.invoice_id")) == ""), F.col("r.payment_amount")).otherwise(F.lit(0.00).cast(T.DecimalType(18, 2))))
            .select(
                "cash_receipt_sk",
                F.col("r.receipt_id").alias("receipt_id"),
                F.col("r.invoice_id").alias("invoice_id"),
                F.col("r.customer_id").alias("customer_id"),
                F.col("r.receipt_date").alias("receipt_date"),
                F.col("r.payment_amount").alias("payment_amount"),
                F.col("r.payment_method").alias("payment_method"),
                F.col("r.source_system").alias("source_system"),
                F.col("r.file_path").alias("file_path"),
                F.col("r.file_modification_time").alias("file_modification_time"),
                F.col("r.load_timestamp").alias("load_timestamp"),
                F.col("r.update_timestamp").alias("update_timestamp"),
                F.col("r.load_date").alias("load_date"),
                F.col("r.update_date").alias("update_date"),
                "match_status",
                "unapplied_payment_amount",
            )
        )
        return final_valid, ref_df


class DatabricksSilverDEPipeline:
    def __init__(self):
        self.spark = SparkFactory.get_spark()
        self.logger = LogFactory.get_logger()
        self.error_manager = ErrorManager(self.spark, self.logger)
        self.audit_manager = AuditManager(self.spark, self.logger)
        self.delta_writer = DeltaWriter(self.spark, self.logger)
        self.transformer = SilverTransformations(self.spark)

    def process_table(self, source_name: str, target_name: str, valid_df: DataFrame, validation_df: DataFrame, business_key_col, merge_keys: List[str]) -> None:
        run_id = str(uuid.uuid4())
        start_time = datetime.datetime.utcnow()
        source_table = SilverPipelineConfig.BRONZE_TABLES[source_name]
        target_table = SilverPipelineConfig.SILVER_TABLES[target_name]
        records_read = self.spark.table(source_table).count()
        records_written = 0
        records_rejected = 0
        status = "SUCCESS"
        error_message = None

        try:
            error_df = self.error_manager.build_error_records(validation_df, source_table, target_table, business_key_col, run_id)
            records_rejected = self.error_manager.persist(error_df)
            records_written = valid_df.count()
            self.delta_writer.merge_to_delta(valid_df, target_table, merge_keys)
            self.delta_writer.optimize(target_table, SilverPipelineConfig.TABLE_ZORDER.get(source_name, []))
        except Exception as exc:
            status = "FAILED"
            error_message = str(exc)
            self.logger.error(f"Failed processing {source_table} -> {target_table}: {error_message}")
            raise
        finally:
            end_time = datetime.datetime.utcnow()
            self.audit_manager.write_audit(
                run_id=run_id,
                source_table=source_table,
                target_table=target_table,
                start_time=start_time,
                end_time=end_time,
                status=status,
                records_read=records_read,
                records_written=records_written,
                records_rejected=records_rejected,
                error_message=error_message,
            )

    def run(self) -> None:
        self.logger.info("Starting Silver DE Pipeline v3")

        valid_customers, customer_validation = self.transformer.customer_master()
        self.process_table(
            "customer_master",
            "customer_master",
            valid_customers,
            customer_validation,
            F.col("customer_id"),
            SilverPipelineConfig.TABLE_KEYS["customer_master"],
        )

        valid_employees, employee_validation = self.transformer.branch_employee()
        self.process_table(
            "branch_employee",
            "branch_employee",
            valid_employees,
            employee_validation,
            F.concat_ws("|", F.col("employee_id"), F.col("branch_code")),
            SilverPipelineConfig.TABLE_KEYS["branch_employee"],
        )

        base_contracts, contract_validation = self.transformer.rental_contracts()
        valid_contracts, contract_reference_validation = self.transformer.rental_contracts_with_reference_checks(base_contracts, valid_customers, valid_employees)
        self.process_table(
            "rental_contracts",
            "rental_contracts",
            valid_contracts,
            contract_reference_validation,
            F.col("c.contract_id").cast("string"),
            SilverPipelineConfig.TABLE_KEYS["rental_contracts"],
        )

        valid_invoices, invoice_validation = self.transformer.invoices(valid_contracts, valid_customers)
        self.process_table(
            "invoices",
            "invoices",
            valid_invoices,
            invoice_validation,
            F.col("i.invoice_id").cast("string"),
            SilverPipelineConfig.TABLE_KEYS["invoices"],
        )

        valid_receipts, receipt_validation = self.transformer.cash_receipts(valid_invoices, valid_customers)
        self.process_table(
            "cash_receipts",
            "cash_receipts",
            valid_receipts,
            receipt_validation,
            F.col("r.receipt_id").cast("string"),
            SilverPipelineConfig.TABLE_KEYS["cash_receipts"],
        )

        self.logger.info("Silver DE Pipeline v3 completed successfully")


if __name__ == "__main__":
    pipeline = DatabricksSilverDEPipeline()
    pipeline.run()


# API Cost Consumed (USD): 0.000000
