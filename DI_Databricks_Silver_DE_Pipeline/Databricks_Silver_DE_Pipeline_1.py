"""
_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: Databricks Silver DE Pipeline for cleansing, validating, and loading Rental Revenue-to-Cash Bronze Delta data into Silver Delta tables with audit and error handling.
## *Version*: 1
## *Updated on*:
_____________________________________________
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T
from delta.tables import DeltaTable
import logging
import sys
import uuid
from functools import reduce
from typing import Dict, Tuple


class SilverPipelineConfig:
    BRONZE_CATALOG = "bronze"
    SILVER_CATALOG = "silver"
    GOLD_CATALOG = "gold"

    BRONZE_TABLES = {
        "rental_contracts": "bronze.bz_rental_contracts",
        "invoices": "bronze.bz_invoices",
        "cash_receipts": "bronze.bz_cash_receipts",
        "customer_master": "bronze.bz_customer_master",
        "branch_employee": "bronze.bz_branch_employee",
        "audit_log": "bronze.bz_audit_log",
    }

    SILVER_TABLES = {
        "rental_contracts": "silver.si_rental_contracts",
        "invoices": "silver.si_invoices",
        "cash_receipts": "silver.si_cash_receipts",
        "customer_master": "silver.si_customer_master",
        "branch_employee": "silver.si_branch_employee",
        "dq_errors": "silver.si_data_quality_errors",
        "audit": "silver.si_process_audit",
    }

    GOLD_ERROR_TABLE = "gold.go_data_quality_errors"
    PIPELINE_NAME = "databricks_silver_de_pipeline_v1"
    SOURCE_SYSTEM_BRONZE = "BRONZE"
    VALID_CONTRACT_STATUS = ["ACTIVE", "CLOSED", "CANCELLED", "PENDING"]
    VALID_INVOICE_TYPES = ["INVOICE", "CREDIT_MEMO", "DEBIT_MEMO"]
    VALID_CUSTOMER_STATUS = ["ACTIVE", "INACTIVE", "SUSPENDED", "CLOSED"]
    VALID_PAYMENT_METHODS = ["CASH", "CHECK", "CARD", "ACH", "WIRE", "LOCKBOX"]
    VALID_PROCESSING_STATUS = ["SUCCESS", "FAILED", "PARTIAL"]
    DATE_FORMATS = ["yyyy-MM-dd", "MM/dd/yyyy", "yyyyMMdd"]


class SparkSessionFactory:
    @staticmethod
    def create() -> SparkSession:
        return (
            SparkSession.builder.appName("DatabricksSilverDEPipeline")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.databricks.delta.optimizeWrite.enabled", "true")
            .config("spark.databricks.delta.autoCompact.enabled", "true")
            .getOrCreate()
        )


class LoggerFactory:
    @staticmethod
    def create_logger() -> logging.Logger:
        logger = logging.getLogger("DatabricksSilverDEPipelineLogger")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger


class DataQualityUtils:
    @staticmethod
    def parse_date_multi(column_name: str):
        parsed_columns = [F.to_date(F.col(column_name), fmt) for fmt in SilverPipelineConfig.DATE_FORMATS]
        return F.coalesce(*parsed_columns)

    @staticmethod
    def trim_upper(column_name: str):
        return F.upper(F.trim(F.col(column_name)))

    @staticmethod
    def trim_only(column_name: str):
        return F.trim(F.col(column_name))

    @staticmethod
    def is_blank(column_name: str):
        return F.col(column_name).isNull() | (F.trim(F.col(column_name)) == "")

    @staticmethod
    def append_error_reason(df: DataFrame, condition, reason: str) -> DataFrame:
        return df.withColumn(
            "error_reason",
            F.when(condition, F.concat_ws("; ", F.col("error_reason"), F.lit(reason))).otherwise(F.col("error_reason")),
        )


class AuditManager:
    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def write_audit(
        self,
        run_id: str,
        source_table: str,
        target_table: str,
        start_ts,
        end_ts,
        status: str,
        records_read: int,
        records_written: int,
        records_rejected: int,
        error_message: str = None,
    ) -> None:
        duration_seconds = 0.0
        if start_ts and end_ts:
            duration_seconds = max((end_ts.timestamp() - start_ts.timestamp()), 0.0)

        audit_df = self.spark.createDataFrame(
            [
                (
                    None,
                    SilverPipelineConfig.PIPELINE_NAME,
                    source_table,
                    target_table,
                    start_ts,
                    end_ts,
                    status,
                    int(records_read),
                    int(records_written),
                    int(records_rejected),
                    float(duration_seconds),
                    error_message,
                    "AAVA",
                    f"Run ID: {run_id}",
                    end_ts,
                    end_ts,
                    SilverPipelineConfig.SOURCE_SYSTEM_BRONZE,
                    run_id,
                )
            ],
            schema=T.StructType(
                [
                    T.StructField("audit_sk", T.LongType(), True),
                    T.StructField("pipeline_name", T.StringType(), True),
                    T.StructField("source_table", T.StringType(), True),
                    T.StructField("target_table", T.StringType(), True),
                    T.StructField("process_start_timestamp", T.TimestampType(), True),
                    T.StructField("process_end_timestamp", T.TimestampType(), True),
                    T.StructField("processing_status", T.StringType(), True),
                    T.StructField("records_read_count", T.LongType(), True),
                    T.StructField("records_written_count", T.LongType(), True),
                    T.StructField("records_rejected_count", T.LongType(), True),
                    T.StructField("processing_duration_seconds", T.DoubleType(), True),
                    T.StructField("error_message", T.StringType(), True),
                    T.StructField("executed_by", T.StringType(), True),
                    T.StructField("audit_remarks", T.StringType(), True),
                    T.StructField("load_date", T.TimestampType(), True),
                    T.StructField("update_date", T.TimestampType(), True),
                    T.StructField("source_system", T.StringType(), True),
                    T.StructField("run_id", T.StringType(), True),
                ]
            ),
        )
        audit_df.write.format("delta").mode("append").saveAsTable(SilverPipelineConfig.SILVER_TABLES["audit"])
        self.logger.info(f"Audit written for source={source_table}, target={target_table}, status={status}")


class ErrorManager:
    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def build_error_df(self, df: DataFrame, source_table_name: str, record_id_col: str) -> DataFrame:
        return (
            df.filter(F.col("error_reason").isNotNull() & (F.trim(F.col("error_reason")) != ""))
            .withColumn("error_sk", F.monotonically_increasing_id())
            .withColumn("source_table", F.lit(source_table_name))
            .withColumn("source_record_id", F.col(record_id_col).cast("string"))
            .withColumn("source_file_path", F.col("file_path").cast("string"))
            .withColumn("validation_rule_name", F.lit("SILVER_DQ_VALIDATION"))
            .withColumn("validation_category", F.lit("VALIDITY_AND_COMPLETENESS"))
            .withColumn("error_description", F.col("error_reason"))
            .withColumn("error_record_payload", F.to_json(F.struct(*[F.col(c) for c in df.columns if c != "error_reason"])))
            .withColumn("error_severity", F.lit("HIGH"))
            .withColumn("layer_name", F.lit("Silver"))
            .withColumn("detected_timestamp", F.current_timestamp())
            .withColumn("processing_status", F.lit("OPEN"))
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn("source_system", F.lit(SilverPipelineConfig.SOURCE_SYSTEM_BRONZE))
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
                "source_system",
            )
        )

    def persist_errors(self, error_df: DataFrame) -> None:
        if error_df.rdd.isEmpty():
            self.logger.info("No invalid records found for error persistence.")
            return
        error_df.write.format("delta").mode("append").saveAsTable(SilverPipelineConfig.SILVER_TABLES["dq_errors"])
        error_df.write.format("delta").mode("append").saveAsTable(SilverPipelineConfig.GOLD_ERROR_TABLE)
        self.logger.info("Invalid records persisted to Silver and Gold error tables.")


class TableProcessor:
    def __init__(self, spark: SparkSession, logger: logging.Logger, error_manager: ErrorManager):
        self.spark = spark
        self.logger = logger
        self.error_manager = error_manager

    def read_bronze(self, table_name: str) -> DataFrame:
        self.logger.info(f"Reading Bronze table: {table_name}")
        return self.spark.table(table_name)

    def write_silver(self, df: DataFrame, target_table: str, partition_columns=None) -> None:
        writer = df.write.format("delta").mode("overwrite")
        if partition_columns:
            writer = writer.partitionBy(*partition_columns)
        writer.saveAsTable(target_table)
        self.logger.info(f"Written Silver table: {target_table}")

    def optimize_table(self, table_name: str, zorder_cols: str = None) -> None:
        if zorder_cols:
            self.spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({zorder_cols})")
        else:
            self.spark.sql(f"OPTIMIZE {table_name}")
        self.logger.info(f"Optimized table: {table_name}")

    def validate_and_transform_rental_contracts(self) -> Tuple[DataFrame, DataFrame]:
        df = self.read_bronze(SilverPipelineConfig.BRONZE_TABLES["rental_contracts"]).dropDuplicates(["contract_id"])
        df = (
            df.withColumn("contract_id", DataQualityUtils.trim_only("contract_id"))
            .withColumn("customer_id", DataQualityUtils.trim_only("customer_id"))
            .withColumn("branch_code", DataQualityUtils.trim_upper("branch_code"))
            .withColumn("sales_rep_id", DataQualityUtils.trim_only("sales_rep_id"))
            .withColumn("equipment_class", DataQualityUtils.trim_upper("equipment_class"))
            .withColumn("contract_start_date", DataQualityUtils.parse_date_multi("contract_start_date"))
            .withColumn("contract_end_date", DataQualityUtils.parse_date_multi("contract_end_date"))
            .withColumn("contract_status", DataQualityUtils.trim_upper("contract_status"))
            .withColumn("daily_rate", F.col("daily_rate").cast(T.DecimalType(18, 2)))
            .withColumn("source_system", DataQualityUtils.trim_upper("source_system"))
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn("error_reason", F.lit(None).cast("string"))
        )

        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("contract_id"), "contract_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("customer_id"), "customer_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, F.col("contract_start_date").isNull(), "contract_start_date is invalid or null")
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("contract_status").isNull() | (~F.col("contract_status").isin(SilverPipelineConfig.VALID_CONTRACT_STATUS)),
            "contract_status is invalid",
        )
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("contract_end_date").isNotNull() & (F.col("contract_end_date") < F.col("contract_start_date")),
            "contract_end_date is earlier than contract_start_date",
        )
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("daily_rate").isNotNull() & (F.col("daily_rate") < 0),
            "daily_rate cannot be negative",
        )

        valid_df = (
            df.filter(F.col("error_reason").isNull())
            .withColumn("rental_contract_sk", F.monotonically_increasing_id())
            .select(
                "rental_contract_sk",
                "contract_id",
                "customer_id",
                "branch_code",
                "sales_rep_id",
                "equipment_class",
                "contract_start_date",
                "contract_end_date",
                "contract_status",
                "daily_rate",
                "load_date",
                "update_date",
                "source_system",
                "file_path",
                "file_modification_time",
            )
        )
        error_df = self.error_manager.build_error_df(df, SilverPipelineConfig.BRONZE_TABLES["rental_contracts"], "contract_id")
        return valid_df, error_df

    def validate_and_transform_invoices(self) -> Tuple[DataFrame, DataFrame]:
        df = self.read_bronze(SilverPipelineConfig.BRONZE_TABLES["invoices"]).dropDuplicates(["invoice_id"])
        df = (
            df.withColumn("invoice_id", DataQualityUtils.trim_only("invoice_id"))
            .withColumn("contract_id", DataQualityUtils.trim_only("contract_id"))
            .withColumn("customer_id", DataQualityUtils.trim_only("customer_id"))
            .withColumn("invoice_date", DataQualityUtils.parse_date_multi("invoice_date"))
            .withColumn("due_date", DataQualityUtils.parse_date_multi("due_date"))
            .withColumn("invoice_amount", F.col("invoice_amount").cast(T.DecimalType(18, 2)))
            .withColumn("tax_amount", F.col("tax_amount").cast(T.DecimalType(18, 2)))
            .withColumn("invoice_type", DataQualityUtils.trim_upper("invoice_type"))
            .withColumn("currency", DataQualityUtils.trim_upper("currency"))
            .withColumn("days_past_due", F.datediff(F.current_date(), F.col("due_date")))
            .withColumn(
                "aging_bucket",
                F.when(F.col("due_date").isNull(), F.lit("UNKNOWN"))
                .when(F.col("days_past_due") <= 0, F.lit("CURRENT"))
                .when((F.col("days_past_due") >= 1) & (F.col("days_past_due") <= 30), F.lit("1_30"))
                .when((F.col("days_past_due") >= 31) & (F.col("days_past_due") <= 60), F.lit("31_60"))
                .when((F.col("days_past_due") >= 61) & (F.col("days_past_due") <= 90), F.lit("61_90"))
                .otherwise(F.lit("90_PLUS")),
            )
            .withColumn("source_system", DataQualityUtils.trim_upper("source_system"))
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn("error_reason", F.lit(None).cast("string"))
        )

        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("invoice_id"), "invoice_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("customer_id"), "customer_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, F.col("invoice_date").isNull(), "invoice_date is invalid or null")
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("invoice_type").isNull() | (~F.col("invoice_type").isin(SilverPipelineConfig.VALID_INVOICE_TYPES)),
            "invoice_type is invalid",
        )
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("currency"), "currency is null or blank")
        df = DataQualityUtils.append_error_reason(df, F.col("invoice_amount").isNull(), "invoice_amount is invalid or null")
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("due_date").isNotNull() & (F.col("due_date") < F.col("invoice_date")),
            "due_date is earlier than invoice_date",
        )

        valid_df = (
            df.filter(F.col("error_reason").isNull())
            .withColumn("invoice_sk", F.monotonically_increasing_id())
            .select(
                "invoice_sk",
                "invoice_id",
                "contract_id",
                "customer_id",
                "invoice_date",
                "due_date",
                "invoice_amount",
                "tax_amount",
                "invoice_type",
                "currency",
                "load_date",
                "update_date",
                "source_system",
                "file_path",
                "file_modification_time",
                "aging_bucket",
                "days_past_due",
            )
        )
        error_df = self.error_manager.build_error_df(df, SilverPipelineConfig.BRONZE_TABLES["invoices"], "invoice_id")
        return valid_df, error_df

    def validate_and_transform_cash_receipts(self) -> Tuple[DataFrame, DataFrame]:
        df = self.read_bronze(SilverPipelineConfig.BRONZE_TABLES["cash_receipts"]).dropDuplicates(["receipt_id"])
        df = (
            df.withColumn("receipt_id", DataQualityUtils.trim_only("receipt_id"))
            .withColumn("invoice_id", DataQualityUtils.trim_only("invoice_id"))
            .withColumn("customer_id", DataQualityUtils.trim_only("customer_id"))
            .withColumn("receipt_date", DataQualityUtils.parse_date_multi("receipt_date"))
            .withColumn("payment_amount", F.col("payment_amount").cast(T.DecimalType(18, 2)))
            .withColumn("payment_method", DataQualityUtils.trim_upper("payment_method"))
            .withColumn(
                "match_status",
                F.when(F.col("invoice_id").isNull() | (F.trim(F.col("invoice_id")) == ""), F.lit("UNAPPLIED")).otherwise(F.lit("MATCHED")),
            )
            .withColumn(
                "unapplied_payment_amount",
                F.when(F.col("invoice_id").isNull() | (F.trim(F.col("invoice_id")) == ""), F.col("payment_amount")).otherwise(F.lit(0.00)),
            )
            .withColumn("source_system", DataQualityUtils.trim_upper("source_system"))
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn("error_reason", F.lit(None).cast("string"))
        )

        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("receipt_id"), "receipt_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("customer_id"), "customer_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, F.col("receipt_date").isNull(), "receipt_date is invalid or null")
        df = DataQualityUtils.append_error_reason(df, F.col("payment_amount").isNull(), "payment_amount is invalid or null")
        df = DataQualityUtils.append_error_reason(df, F.col("payment_amount") < 0, "payment_amount cannot be negative")
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("payment_method").isNotNull() & (~F.col("payment_method").isin(SilverPipelineConfig.VALID_PAYMENT_METHODS)),
            "payment_method is invalid",
        )

        valid_df = (
            df.filter(F.col("error_reason").isNull())
            .withColumn("cash_receipt_sk", F.monotonically_increasing_id())
            .select(
                "cash_receipt_sk",
                "receipt_id",
                "invoice_id",
                "customer_id",
                "receipt_date",
                "payment_amount",
                "payment_method",
                "load_date",
                "update_date",
                "source_system",
                "file_path",
                "file_modification_time",
                "match_status",
                "unapplied_payment_amount",
            )
        )
        error_df = self.error_manager.build_error_df(df, SilverPipelineConfig.BRONZE_TABLES["cash_receipts"], "receipt_id")
        return valid_df, error_df

    def validate_and_transform_customer_master(self) -> Tuple[DataFrame, DataFrame]:
        df = self.read_bronze(SilverPipelineConfig.BRONZE_TABLES["customer_master"]).dropDuplicates(["customer_id"])
        df = (
            df.withColumn("customer_id", DataQualityUtils.trim_only("customer_id"))
            .withColumn("customer_name", F.initcap(DataQualityUtils.trim_only("customer_name")))
            .withColumn("credit_terms", DataQualityUtils.trim_upper("credit_terms"))
            .withColumn("credit_limit", F.col("credit_limit").cast(T.DecimalType(18, 2)))
            .withColumn("customer_since", DataQualityUtils.parse_date_multi("customer_since"))
            .withColumn("customer_status", DataQualityUtils.trim_upper("customer_status"))
            .withColumn("over_limit_indicator", F.lit("N"))
            .withColumn("source_system", DataQualityUtils.trim_upper("source_system"))
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn("error_reason", F.lit(None).cast("string"))
        )

        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("customer_id"), "customer_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("customer_name"), "customer_name is null or blank")
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("customer_status").isNull() | (~F.col("customer_status").isin(SilverPipelineConfig.VALID_CUSTOMER_STATUS)),
            "customer_status is invalid",
        )
        df = DataQualityUtils.append_error_reason(
            df,
            F.col("credit_limit").isNotNull() & (F.col("credit_limit") < 0),
            "credit_limit cannot be negative",
        )

        valid_df = (
            df.filter(F.col("error_reason").isNull())
            .withColumn("customer_sk", F.monotonically_increasing_id())
            .select(
                "customer_sk",
                "customer_id",
                "customer_name",
                "credit_terms",
                "credit_limit",
                "customer_since",
                "customer_status",
                "load_date",
                "update_date",
                "source_system",
                "file_path",
                "file_modification_time",
                "over_limit_indicator",
            )
        )
        error_df = self.error_manager.build_error_df(df, SilverPipelineConfig.BRONZE_TABLES["customer_master"], "customer_id")
        return valid_df, error_df

    def validate_and_transform_branch_employee(self) -> Tuple[DataFrame, DataFrame]:
        df = self.read_bronze(SilverPipelineConfig.BRONZE_TABLES["branch_employee"]).dropDuplicates(["employee_id", "branch_code"])
        df = (
            df.withColumn("employee_id", DataQualityUtils.trim_only("employee_id"))
            .withColumn("employee_name", F.initcap(DataQualityUtils.trim_only("employee_name")))
            .withColumn("role", DataQualityUtils.trim_upper("role"))
            .withColumn("branch_code", DataQualityUtils.trim_upper("branch_code"))
            .withColumn("region", DataQualityUtils.trim_upper("region"))
            .withColumn("collector_id", DataQualityUtils.trim_only("collector_id"))
            .withColumn("effective_date", DataQualityUtils.parse_date_multi("effective_date"))
            .withColumn("source_system", DataQualityUtils.trim_upper("source_system"))
            .withColumn("load_date", F.current_timestamp())
            .withColumn("update_date", F.current_timestamp())
            .withColumn("error_reason", F.lit(None).cast("string"))
        )

        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("employee_id"), "employee_id is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("employee_name"), "employee_name is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("role"), "role is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("branch_code"), "branch_code is null or blank")
        df = DataQualityUtils.append_error_reason(df, DataQualityUtils.is_blank("region"), "region is null or blank")

        valid_df = (
            df.filter(F.col("error_reason").isNull())
            .withColumn("branch_employee_sk", F.monotonically_increasing_id())
            .select(
                "branch_employee_sk",
                "employee_id",
                "employee_name",
                "role",
                "branch_code",
                "region",
                "collector_id",
                "effective_date",
                "load_date",
                "update_date",
                "source_system",
                "file_path",
                "file_modification_time",
            )
        )
        error_df = self.error_manager.build_error_df(df, SilverPipelineConfig.BRONZE_TABLES["branch_employee"], "employee_id")
        return valid_df, error_df


class DatabricksSilverDEPipeline:
    def __init__(self):
        self.spark = SparkSessionFactory.create()
        self.logger = LoggerFactory.create_logger()
        self.error_manager = ErrorManager(self.spark, self.logger)
        self.audit_manager = AuditManager(self.spark, self.logger)
        self.processor = TableProcessor(self.spark, self.logger, self.error_manager)

    def run_table_pipeline(self, source_key: str, target_key: str, transform_method, partition_columns, zorder_cols: str):
        import datetime

        run_id = str(uuid.uuid4())
        source_table = SilverPipelineConfig.BRONZE_TABLES[source_key]
        target_table = SilverPipelineConfig.SILVER_TABLES[target_key]
        start_ts = datetime.datetime.now()
        records_read = 0
        records_written = 0
        records_rejected = 0
        status = "SUCCESS"
        error_message = None

        try:
            bronze_df = self.spark.table(source_table)
            records_read = bronze_df.count()
            valid_df, error_df = transform_method()
            records_written = valid_df.count()
            records_rejected = error_df.count()

            self.processor.write_silver(valid_df, target_table, partition_columns)
            self.error_manager.persist_errors(error_df)
            self.processor.optimize_table(target_table, zorder_cols)
        except Exception as exc:
            status = "FAILED"
            error_message = str(exc)
            self.logger.error(f"Pipeline failed for {source_table} -> {target_table}: {error_message}")
            raise
        finally:
            end_ts = datetime.datetime.now()
            self.audit_manager.write_audit(
                run_id=run_id,
                source_table=source_table,
                target_table=target_table,
                start_ts=start_ts,
                end_ts=end_ts,
                status=status,
                records_read=records_read,
                records_written=records_written,
                records_rejected=records_rejected,
                error_message=error_message,
            )

    def run(self):
        self.logger.info("Starting Databricks Silver DE Pipeline")

        self.run_table_pipeline(
            source_key="rental_contracts",
            target_key="rental_contracts",
            transform_method=self.processor.validate_and_transform_rental_contracts,
            partition_columns=["contract_status"],
            zorder_cols="customer_id, branch_code, contract_id",
        )

        self.run_table_pipeline(
            source_key="invoices",
            target_key="invoices",
            transform_method=self.processor.validate_and_transform_invoices,
            partition_columns=["invoice_date"],
            zorder_cols="customer_id, contract_id, invoice_id, due_date",
        )

        self.run_table_pipeline(
            source_key="cash_receipts",
            target_key="cash_receipts",
            transform_method=self.processor.validate_and_transform_cash_receipts,
            partition_columns=["receipt_date"],
            zorder_cols="customer_id, invoice_id, receipt_id",
        )

        self.run_table_pipeline(
            source_key="customer_master",
            target_key="customer_master",
            transform_method=self.processor.validate_and_transform_customer_master,
            partition_columns=["customer_status"],
            zorder_cols="customer_id, customer_name",
        )

        self.run_table_pipeline(
            source_key="branch_employee",
            target_key="branch_employee",
            transform_method=self.processor.validate_and_transform_branch_employee,
            partition_columns=["region"],
            zorder_cols="branch_code, employee_id, collector_id",
        )

        self.logger.info("Databricks Silver DE Pipeline completed successfully")


if __name__ == "__main__":
    pipeline = DatabricksSilverDEPipeline()
    pipeline.run()


# API Cost Consumed (USD): 0.000000
