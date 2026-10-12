"""
_____________________________________________
## *Author*: AAVA
## *Created on*:
## *Description*: PySpark pipeline to build Gold dimension tables from Silver layer with transformations, audit logging, error handling, validation, and Delta optimization.
## *Version*: 1
## *Updated on*:
_____________________________________________
"""

from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField, TimestampType, LongType
from delta.tables import DeltaTable
import time

spark = SparkSession.builder.appName("Databricks_Gold_Dim_DE_Pipeline").getOrCreate()

PIPELINE_NAME = "Databricks_Gold_Dim_DE_Pipeline"
SOURCE_TABLES = {
    "customer": "silver.si_customer_master",
    "branch_employee": "silver.si_branch_employee",
    "rental_contract": "silver.si_rental_contracts"
}
TARGET_TABLES = {
    "customer": "gold.dim_customer",
    "branch_employee": "gold.dim_branch_employee",
    "rental_contract": "gold.dim_rental_contract"
}
ERROR_TABLE = "gold.dim_data_quality_errors"
AUDIT_TABLE = "gold.dim_process_audit"


def create_gold_support_tables() -> None:
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {ERROR_TABLE} (
            error_sk BIGINT,
            source_table STRING,
            target_table STRING,
            source_record_id STRING,
            validation_rule_name STRING,
            validation_category STRING,
            error_description STRING,
            error_record_payload STRING,
            error_severity STRING,
            layer_name STRING,
            detected_timestamp TIMESTAMP,
            processing_status STRING,
            pipeline_name STRING
        ) USING DELTA
        PARTITIONED BY (layer_name, processing_status)
    """)

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {AUDIT_TABLE} (
            audit_sk BIGINT,
            pipeline_name STRING,
            source_table STRING,
            target_table STRING,
            process_start_timestamp TIMESTAMP,
            process_end_timestamp TIMESTAMP,
            processing_status STRING,
            records_read_count BIGINT,
            records_written_count BIGINT,
            records_rejected_count BIGINT,
            processing_duration_seconds DOUBLE,
            error_message STRING,
            executed_by STRING,
            audit_remarks STRING
        ) USING DELTA
        PARTITIONED BY (processing_status)
    """)


def write_audit_log(source_table: str,
                    target_table: str,
                    start_ts,
                    end_ts,
                    status: str,
                    records_read: int,
                    records_written: int,
                    records_rejected: int,
                    error_message: str = None,
                    remarks: str = None) -> None:
    audit_df = spark.createDataFrame([
        (
            int(time.time() * 1000000),
            PIPELINE_NAME,
            source_table,
            target_table,
            start_ts,
            end_ts,
            status,
            records_read,
            records_written,
            records_rejected,
            float(end_ts.timestamp() - start_ts.timestamp()),
            error_message,
            spark.sql("select current_user() as user").collect()[0]["user"],
            remarks
        )
    ], schema="audit_sk long, pipeline_name string, source_table string, target_table string, process_start_timestamp timestamp, process_end_timestamp timestamp, processing_status string, records_read_count long, records_written_count long, records_rejected_count long, processing_duration_seconds double, error_message string, executed_by string, audit_remarks string")

    audit_df.write.format("delta").mode("append").saveAsTable(AUDIT_TABLE)


def write_error_records(df: DataFrame,
                        source_table: str,
                        target_table: str,
                        rule_name: str,
                        category: str,
                        description: str,
                        severity: str,
                        record_id_col: str) -> int:
    if df.rdd.isEmpty():
        return 0

    error_df = (
        df.withColumn("error_sk", F.abs(F.xxhash64(F.to_json(F.struct(*df.columns)))))
          .withColumn("source_table", F.lit(source_table))
          .withColumn("target_table", F.lit(target_table))
          .withColumn("source_record_id", F.col(record_id_col).cast("string"))
          .withColumn("validation_rule_name", F.lit(rule_name))
          .withColumn("validation_category", F.lit(category))
          .withColumn("error_description", F.lit(description))
          .withColumn("error_record_payload", F.to_json(F.struct(*df.columns)))
          .withColumn("error_severity", F.lit(severity))
          .withColumn("layer_name", F.lit("gold"))
          .withColumn("detected_timestamp", F.current_timestamp())
          .withColumn("processing_status", F.lit("REJECTED"))
          .withColumn("pipeline_name", F.lit(PIPELINE_NAME))
          .select(
              "error_sk", "source_table", "target_table", "source_record_id",
              "validation_rule_name", "validation_category", "error_description",
              "error_record_payload", "error_severity", "layer_name",
              "detected_timestamp", "processing_status", "pipeline_name"
          )
    )

    rejected_count = error_df.count()
    error_df.write.format("delta").mode("append").saveAsTable(ERROR_TABLE)
    return rejected_count


def standardize_text(col_name: str):
    return F.regexp_replace(F.trim(F.col(col_name)), r"\\s+", " ")


def load_dim_customer() -> tuple[DataFrame, int, int]:
    source_table = SOURCE_TABLES["customer"]
    df = spark.table(source_table)
    read_count = df.count()

    invalid_df = df.filter(F.col("customer_id").isNull() | (F.trim(F.col("customer_id")) == ""))
    rejected = write_error_records(
        invalid_df,
        source_table,
        TARGET_TABLES["customer"],
        "customer_id_not_null",
        "MANDATORY_KEY",
        "customer_id cannot be null or blank",
        "HIGH",
        "customer_id"
    )

    valid_df = df.subtract(invalid_df)

    w = Window.partitionBy("customer_id").orderBy(F.col("update_date").desc_nulls_last(), F.col("load_date").desc_nulls_last())
    dim_df = (
        valid_df
        .withColumn("customer_id", standardize_text("customer_id"))
        .withColumn("customer_name", F.initcap(standardize_text("customer_name")))
        .withColumn("credit_terms", F.upper(standardize_text("credit_terms")))
        .withColumn("customer_status", F.upper(standardize_text("customer_status")))
        .withColumn("over_limit_indicator",
                    F.when(F.upper(standardize_text("over_limit_indicator")).isin("TRUE", "YES", "1", "Y"), F.lit("Y"))
                     .when(F.upper(standardize_text("over_limit_indicator")).isin("FALSE", "NO", "0", "N"), F.lit("N"))
                     .otherwise(F.col("over_limit_indicator")))
        .withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .withColumn("customer_dim_sk", F.abs(F.xxhash64("customer_id")))
        .withColumnRenamed("customer_since", "customer_since_date")
        .withColumn("record_effective_timestamp", F.coalesce(F.col("update_date"), F.col("load_date")))
        .withColumn("record_load_timestamp", F.col("load_date"))
        .select(
            "customer_dim_sk", "customer_id", "customer_name", "credit_terms",
            "credit_limit", "customer_since_date", "customer_status",
            "over_limit_indicator", "source_system", "record_effective_timestamp",
            "record_load_timestamp"
        )
    )
    return dim_df, read_count, rejected


def load_dim_branch_employee() -> tuple[DataFrame, int, int]:
    source_table = SOURCE_TABLES["branch_employee"]
    df = spark.table(source_table)
    read_count = df.count()

    invalid_df = df.filter(
        F.col("employee_id").isNull() | (F.trim(F.col("employee_id")) == "") |
        F.col("branch_code").isNull() | (F.trim(F.col("branch_code")) == "")
    )
    rejected = write_error_records(
        invalid_df,
        source_table,
        TARGET_TABLES["branch_employee"],
        "employee_branch_key_not_null",
        "MANDATORY_KEY",
        "employee_id and branch_code cannot be null or blank",
        "HIGH",
        "employee_id"
    )

    valid_df = df.subtract(invalid_df)

    w = Window.partitionBy("employee_id", "branch_code", "effective_date").orderBy(F.col("update_date").desc_nulls_last(), F.col("load_date").desc_nulls_last())
    dim_df = (
        valid_df
        .withColumn("employee_id", standardize_text("employee_id"))
        .withColumn("employee_name", F.initcap(standardize_text("employee_name")))
        .withColumn("role", F.upper(standardize_text("role")))
        .withColumn("branch_code", F.upper(standardize_text("branch_code")))
        .withColumn("region", F.upper(standardize_text("region")))
        .withColumn("collector_id", standardize_text("collector_id"))
        .withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .withColumn("branch_employee_dim_sk", F.abs(F.xxhash64("employee_id", "branch_code", "effective_date")))
        .withColumn("record_effective_timestamp", F.coalesce(F.col("update_date"), F.col("load_date")))
        .withColumn("record_load_timestamp", F.col("load_date"))
        .select(
            "branch_employee_dim_sk", "employee_id", "employee_name", "role",
            "branch_code", "region", "collector_id", "effective_date",
            "source_system", "record_effective_timestamp", "record_load_timestamp"
        )
    )
    return dim_df, read_count, rejected


def load_dim_rental_contract() -> tuple[DataFrame, int, int]:
    source_table = SOURCE_TABLES["rental_contract"]
    df = spark.table(source_table)
    read_count = df.count()

    invalid_df = df.filter(
        F.col("contract_id").isNull() | (F.trim(F.col("contract_id")) == "") |
        F.col("customer_id").isNull() | (F.trim(F.col("customer_id")) == "")
    )
    date_error_df = df.filter(
        F.col("contract_end_date").isNotNull() & F.col("contract_start_date").isNotNull() &
        (F.col("contract_end_date") < F.col("contract_start_date"))
    )

    rejected = 0
    rejected += write_error_records(
        invalid_df,
        source_table,
        TARGET_TABLES["rental_contract"],
        "contract_customer_key_not_null",
        "MANDATORY_KEY",
        "contract_id and customer_id cannot be null or blank",
        "HIGH",
        "contract_id"
    )
    rejected += write_error_records(
        date_error_df,
        source_table,
        TARGET_TABLES["rental_contract"],
        "contract_date_chronology",
        "BUSINESS_RULE",
        "contract_end_date cannot be earlier than contract_start_date",
        "HIGH",
        "contract_id"
    )

    valid_df = df.subtract(invalid_df).subtract(date_error_df)

    w = Window.partitionBy("contract_id").orderBy(F.col("update_date").desc_nulls_last(), F.col("load_date").desc_nulls_last())
    dim_df = (
        valid_df
        .withColumn("contract_id", standardize_text("contract_id"))
        .withColumn("customer_id", standardize_text("customer_id"))
        .withColumn("branch_code", F.upper(standardize_text("branch_code")))
        .withColumn("sales_rep_id", standardize_text("sales_rep_id"))
        .withColumn("equipment_class", F.upper(standardize_text("equipment_class")))
        .withColumn("contract_status", F.upper(standardize_text("contract_status")))
        .withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .withColumn("rental_contract_dim_sk", F.abs(F.xxhash64("contract_id")))
        .withColumn("record_effective_timestamp", F.coalesce(F.col("update_date"), F.col("load_date")))
        .withColumn("record_load_timestamp", F.col("load_date"))
        .select(
            "rental_contract_dim_sk", "contract_id", "customer_id", "branch_code",
            "sales_rep_id", "equipment_class", "contract_start_date", "contract_end_date",
            "contract_status", "daily_rate", "source_system",
            "record_effective_timestamp", "record_load_timestamp"
        )
    )
    return dim_df, read_count, rejected


def merge_to_delta(df: DataFrame, target_table: str, merge_key: str) -> int:
    if not spark.catalog.tableExists(target_table):
        df.write.format("delta").mode("overwrite").saveAsTable(target_table)
    else:
        delta_table = DeltaTable.forName(spark, target_table)
        (
            delta_table.alias("t")
            .merge(df.alias("s"), f"t.{merge_key} = s.{merge_key}")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
    return df.count()


def optimize_gold_tables() -> None:
    spark.sql("OPTIMIZE gold.dim_customer ZORDER BY (customer_id)")
    spark.sql("OPTIMIZE gold.dim_branch_employee ZORDER BY (employee_id, branch_code)")
    spark.sql("OPTIMIZE gold.dim_rental_contract ZORDER BY (contract_id, customer_id, branch_code)")


def run_dimension_pipeline() -> None:
    create_gold_support_tables()

    pipelines = [
        (load_dim_customer, TARGET_TABLES["customer"], "customer_id"),
        (load_dim_branch_employee, TARGET_TABLES["branch_employee"], "employee_id"),
        (load_dim_rental_contract, TARGET_TABLES["rental_contract"], "contract_id")
    ]

    for loader, target_table, merge_key in pipelines:
        start_ts = spark.sql("select current_timestamp() as ts").collect()[0]["ts"]
        source_table = loader.__name__.replace("load_dim_", "silver.si_")
        try:
            dim_df, records_read, records_rejected = loader()
            records_written = merge_to_delta(dim_df, target_table, merge_key)
            end_ts = spark.sql("select current_timestamp() as ts").collect()[0]["ts"]
            write_audit_log(
                source_table=source_table,
                target_table=target_table,
                start_ts=start_ts,
                end_ts=end_ts,
                status="SUCCESS",
                records_read=records_read,
                records_written=records_written,
                records_rejected=records_rejected,
                remarks="Gold dimension load completed successfully"
            )
        except Exception as exc:
            end_ts = spark.sql("select current_timestamp() as ts").collect()[0]["ts"]
            write_audit_log(
                source_table=source_table,
                target_table=target_table,
                start_ts=start_ts,
                end_ts=end_ts,
                status="FAILED",
                records_read=0,
                records_written=0,
                records_rejected=0,
                error_message=str(exc),
                remarks="Gold dimension load failed"
            )
            raise

    optimize_gold_tables()

    gold_ddl_validation = {
        "gold.dim_customer": [
            "customer_dim_sk", "customer_id", "customer_name", "credit_terms",
            "credit_limit", "customer_since_date", "customer_status"
        ],
        "gold.dim_branch_employee": [
            "branch_employee_dim_sk", "employee_id", "employee_name", "role",
            "branch_code", "region", "effective_date"
        ],
        "gold.dim_rental_contract": [
            "rental_contract_dim_sk", "contract_id", "customer_id", "branch_code",
            "contract_start_date", "contract_status"
        ]
    }

    for table_name, expected_cols in gold_ddl_validation.items():
        actual_cols = set(spark.table(table_name).columns)
        missing_cols = [c for c in expected_cols if c not in actual_cols]
        if missing_cols:
            raise ValueError(f"Gold layer compatibility validation failed for {table_name}. Missing columns: {missing_cols}")

    print("Gold dimension pipeline execution completed successfully.")
    print("Error data table available at:", ERROR_TABLE)
    print("Audit log table available at:", AUDIT_TABLE)


if __name__ == "__main__":
    run_dimension_pipeline()
    print("apiCost: 0.000000")

# Output URL (Clickable Hyperlinks)
# https://github.com/DIAscendion/Databricks_LakeHouseInADay/blob/main/DI_Databricks_Gold_Dim_DE_Pipeline/Databricks_Gold_Dim_DE_Pipeline_1.py
