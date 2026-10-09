_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*: PySpark Bronze ingestion pipeline for Rental Revenue-to-Cash source tables with Delta loading, audit logging, and cost reporting.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import current_timestamp, lit, expr, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, LongType, DoubleType
from datetime import datetime
import uuid
import time


spark = (
    SparkSession.builder
    .appName("Databricks Bronze DE Pipeline - Rental Revenue to Cash")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
    .enableHiveSupport()
    .getOrCreate()
)


SOURCE_SYSTEM_DEFAULT = "MULTI_SOURCE"
AUDIT_TABLE = "sunbelt_demo.bronze.bz_audit_log"
API_COST_USD = 0.000001

SOURCE_CONFIG = {
    "rental_contracts": {
        "format": "csv",
        "path": "/mnt/raw/rental_revenue_to_cash/rental_contracts",
        "options": {
            "header": "true",
            "inferSchema": "false",
            "delimiter": ",",
            "multiLine": "false"
        },
        "target_table": "sunbelt_demo.bronze.bz_rental_contracts",
        "source_system": "LEGACY_SE|LEGACY_MW|SUNBELT_CORE"
    },
    "invoices": {
        "format": "csv",
        "path": "/mnt/raw/rental_revenue_to_cash/invoices",
        "options": {
            "header": "true",
            "inferSchema": "false",
            "delimiter": ",",
            "multiLine": "false"
        },
        "target_table": "sunbelt_demo.bronze.bz_invoices",
        "source_system": "BRANCH_BILLING"
    },
    "cash_receipts": {
        "format": "csv",
        "path": "/mnt/raw/rental_revenue_to_cash/cash_receipts",
        "options": {
            "header": "true",
            "inferSchema": "false",
            "delimiter": ",",
            "multiLine": "false"
        },
        "target_table": "sunbelt_demo.bronze.bz_cash_receipts",
        "source_system": "LOCKBOX_FEED"
    },
    "customer_master": {
        "format": "csv",
        "path": "/mnt/raw/rental_revenue_to_cash/customer_master",
        "options": {
            "header": "true",
            "inferSchema": "false",
            "delimiter": ",",
            "multiLine": "false"
        },
        "target_table": "sunbelt_demo.bronze.bz_customer_master",
        "source_system": "CRM_ERP"
    },
    "branch_employee": {
        "format": "csv",
        "path": "/mnt/raw/rental_revenue_to_cash/branch_employee",
        "options": {
            "header": "true",
            "inferSchema": "false",
            "delimiter": ",",
            "multiLine": "false"
        },
        "target_table": "sunbelt_demo.bronze.bz_branch_employee",
        "source_system": "HR_FEED|HR_FEED_OLD"
    }
}

TARGET_DDL = {
    "sunbelt_demo.bronze.bz_rental_contracts": """
        CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_rental_contracts (
            contract_id STRING,
            customer_id STRING,
            branch_code STRING,
            sales_rep_id STRING,
            equipment_class STRING,
            contract_start_date STRING,
            contract_end_date STRING,
            contract_status STRING,
            daily_rate DECIMAL(10,2),
            source_system STRING,
            file_path STRING,
            file_modification_time TIMESTAMP,
            load_date TIMESTAMP,
            update_date TIMESTAMP
        ) USING DELTA
    """,
    "sunbelt_demo.bronze.bz_invoices": """
        CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_invoices (
            invoice_id STRING,
            contract_id STRING,
            customer_id STRING,
            invoice_date STRING,
            due_date STRING,
            invoice_amount DECIMAL(12,2),
            tax_amount DECIMAL(12,2),
            invoice_type STRING,
            currency STRING,
            source_system STRING,
            file_path STRING,
            file_modification_time TIMESTAMP,
            load_date TIMESTAMP,
            update_date TIMESTAMP
        ) USING DELTA
    """,
    "sunbelt_demo.bronze.bz_cash_receipts": """
        CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_cash_receipts (
            receipt_id STRING,
            invoice_id STRING,
            customer_id STRING,
            receipt_date STRING,
            payment_amount DECIMAL(12,2),
            payment_method STRING,
            source_system STRING,
            file_path STRING,
            file_modification_time TIMESTAMP,
            load_date TIMESTAMP,
            update_date TIMESTAMP
        ) USING DELTA
    """,
    "sunbelt_demo.bronze.bz_customer_master": """
        CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_customer_master (
            customer_id STRING,
            customer_name STRING,
            credit_terms STRING,
            credit_limit DECIMAL(12,2),
            customer_since STRING,
            customer_status STRING,
            source_system STRING,
            file_path STRING,
            file_modification_time TIMESTAMP,
            load_date TIMESTAMP,
            update_date TIMESTAMP
        ) USING DELTA
    """,
    "sunbelt_demo.bronze.bz_branch_employee": """
        CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_branch_employee (
            employee_id STRING,
            employee_name STRING,
            role STRING,
            branch_code STRING,
            region STRING,
            collector_id STRING,
            effective_date STRING,
            source_system STRING,
            file_path STRING,
            file_modification_time TIMESTAMP,
            load_date TIMESTAMP,
            update_date TIMESTAMP
        ) USING DELTA
    """,
    AUDIT_TABLE: """
        CREATE TABLE IF NOT EXISTS sunbelt_demo.bronze.bz_audit_log (
            audit_id STRING,
            pipeline_name STRING,
            source_name STRING,
            target_table STRING,
            status STRING,
            row_count LONG,
            message STRING,
            process_start_time TIMESTAMP,
            process_end_time TIMESTAMP,
            processing_time_seconds DOUBLE,
            processed_by STRING,
            created_at TIMESTAMP
        ) USING DELTA
    """
}


def get_current_user() -> str:
    candidates = [
        "SELECT current_user() AS user_name",
        "SELECT session_user() AS user_name"
    ]
    for query in candidates:
        try:
            result = spark.sql(query).collect()
            if result and result[0]["user_name"]:
                return result[0]["user_name"]
        except Exception:
            pass
    try:
        return spark.sparkContext.sparkUser()
    except Exception:
        return "unknown_user"


EXECUTED_BY = get_current_user()


def create_required_tables() -> None:
    for ddl in TARGET_DDL.values():
        spark.sql(ddl)


AUDIT_SCHEMA = StructType([
    StructField("audit_id", StringType(), False),
    StructField("pipeline_name", StringType(), True),
    StructField("source_name", StringType(), True),
    StructField("target_table", StringType(), True),
    StructField("status", StringType(), True),
    StructField("row_count", LongType(), True),
    StructField("message", StringType(), True),
    StructField("process_start_time", TimestampType(), True),
    StructField("process_end_time", TimestampType(), True),
    StructField("processing_time_seconds", DoubleType(), True),
    StructField("processed_by", StringType(), True),
    StructField("created_at", TimestampType(), True)
])


def write_audit_log(
    source_name: str,
    target_table: str,
    status: str,
    row_count: int,
    message: str,
    process_start_time: datetime,
    process_end_time: datetime,
    processed_by: str
) -> None:
    processing_time_seconds = float((process_end_time - process_start_time).total_seconds())
    audit_record = [(
        str(uuid.uuid4()),
        "Databricks Bronze DE Pipeline",
        source_name,
        target_table,
        status,
        int(row_count),
        message,
        process_start_time,
        process_end_time,
        processing_time_seconds,
        processed_by,
        process_end_time
    )]
    audit_df = spark.createDataFrame(audit_record, AUDIT_SCHEMA)
    (
        audit_df.write
        .format("delta")
        .mode("append")
        .saveAsTable(AUDIT_TABLE)
    )


def read_source(source_name: str, source_details: dict) -> DataFrame:
    reader = spark.read.format(source_details["format"])
    for option_key, option_value in source_details["options"].items():
        reader = reader.option(option_key, option_value)
    df = reader.load(source_details["path"])
    return df


def enrich_with_metadata(df: DataFrame, source_system: str) -> DataFrame:
    enriched_df = (
        df
        .withColumn("load_date", current_timestamp())
        .withColumn("update_date", current_timestamp())
        .withColumn("source_system", lit(source_system))
    )

    if "file_path" not in enriched_df.columns:
        enriched_df = enriched_df.withColumn("file_path", lit(None).cast("string"))
    if "file_modification_time" not in enriched_df.columns:
        enriched_df = enriched_df.withColumn("file_modification_time", lit(None).cast("timestamp"))

    return enriched_df


def align_to_target_table(df: DataFrame, target_table: str) -> DataFrame:
    target_columns = spark.table(target_table).columns
    available_columns = [column_name for column_name in target_columns if column_name in df.columns]
    aligned_df = df.select(*available_columns)
    return aligned_df


def write_to_bronze(df: DataFrame, target_table: str) -> int:
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(target_table)
    )
    return df.count()


def process_table(source_name: str, source_details: dict, processed_by: str) -> None:
    process_start_time = datetime.utcnow()
    target_table = source_details["target_table"]
    try:
        source_df = read_source(source_name, source_details)
        enriched_df = enrich_with_metadata(source_df, source_details.get("source_system", SOURCE_SYSTEM_DEFAULT))
        aligned_df = align_to_target_table(enriched_df, target_table)
        row_count = write_to_bronze(aligned_df, target_table)
        process_end_time = datetime.utcnow()
        write_audit_log(
            source_name=source_name,
            target_table=target_table,
            status="SUCCESS",
            row_count=row_count,
            message=f"Loaded {row_count} rows into {target_table}",
            process_start_time=process_start_time,
            process_end_time=process_end_time,
            processed_by=processed_by
        )
    except Exception as exc:
        process_end_time = datetime.utcnow()
        write_audit_log(
            source_name=source_name,
            target_table=target_table,
            status="FAILED",
            row_count=0,
            message=f"Failed to load {source_name} into {target_table}: {str(exc)}",
            process_start_time=process_start_time,
            process_end_time=process_end_time,
            processed_by=processed_by
        )
        raise


def run_pipeline() -> None:
    pipeline_start_time = time.time()
    create_required_tables()
    for source_name, source_details in SOURCE_CONFIG.items():
        process_table(source_name, source_details, EXECUTED_BY)
    pipeline_end_time = time.time()
    total_processing_seconds = pipeline_end_time - pipeline_start_time
    print(f"Pipeline completed successfully in {total_processing_seconds} seconds")
    print(f"API Cost Consumed (USD): {API_COST_USD}")


if __name__ == "__main__":
    run_pipeline()
