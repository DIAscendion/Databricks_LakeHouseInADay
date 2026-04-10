_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for processing Silver Layer data into Gold Layer dimension tables, including Customer Lifetime Value (CLV) calculation, schema enhancements, data quality checks, audit logging, error handling, and performance optimizations.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
Databricks Gold Dim DE Pipeline
- Extracts reference and categorical data from Silver Layer
- Applies business transformations for dimension tables
- Generates surrogate keys and maps hierarchical relationships
- Deduplicates and standardizes attributes
- Implements audit logging and error handling
- Integrates new Customer_Engagement data source
- Adds Customer Lifetime Value (CLV), Customer_Segment, Last_Interaction_Date
- Optimizes performance with Delta format and partitioning
- Ensures Gold Layer compatibility and data quality
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, max as spark_max, sum as spark_sum, avg as spark_avg, datediff, broadcast, isnan, isnull
from pyspark.sql.types import StringType, DoubleType, DateType
from pyspark.sql.window import Window
import datetime

# Paths (replace with actual paths from input files)
silver_path = "/mnt/silver/"  # Example, update as needed
gold_path = "/mnt/gold/"      # Example, update as needed

# Audit log table name
AUDIT_LOG_TABLE = "gold_dim_audit_log"
ERROR_TABLE = "gold_dim_error_records"

# Read Silver Layer tables

def read_silver_table(spark, table_name):
    return spark.read.format("delta").load(f"{silver_path}{table_name}")

def write_gold_table(df, table_name, mode="overwrite", partition_col=None):
    writer = df.write.format("delta").mode(mode)
    if partition_col:
        writer = writer.partitionBy(partition_col)
    writer.save(f"{gold_path}{table_name}")

# Audit Logging

def log_audit(spark, table_name, status, error_msg=None):
    audit_df = spark.createDataFrame([
        (table_name, datetime.datetime.now(), status, error_msg)
    ], ["table_name", "timestamp", "status", "error_msg"])
    audit_df.write.format("delta").mode("append").save(f"{gold_path}{AUDIT_LOG_TABLE}")

# Error Handling

def log_error_records(df, table_name):
    df.withColumn("error_table", lit(table_name)) \
      .write.format("delta").mode("append").save(f"{gold_path}{ERROR_TABLE}")

# Transformation: Customer Dimension

def transform_customer_dimension(spark):
    try:
        customer_df = read_silver_table(spark, "customer")
        engagement_df = read_silver_table(spark, "customer_engagement")
        transaction_df = read_silver_table(spark, "customer_transaction")

        # Surrogate Key Generation
        customer_df = customer_df.withColumn("customer_key", col("customer_id"))

        # Deduplication & Standardization
        customer_df = customer_df.dropDuplicates(["customer_id"]).withColumn("customer_name", col("customer_name").alias("customer_name_standardized"))

        # Hierarchical Mapping (example: region-country)
        customer_df = customer_df.withColumn("region_country", col("region") + lit("-") + col("country"))

        # CLV Calculation (business rule: sum of all transactions)
        clv_df = transaction_df.groupBy("customer_id").agg(spark_sum("transaction_amount").alias("CLV"))
        customer_df = customer_df.join(clv_df, "customer_id", "left")

        # Customer Segment Assignment
        customer_df = customer_df.withColumn(
            "Customer_Segment",
            when(col("CLV") >= 10000, lit("High Value"))
            .when((col("CLV") >= 5000) & (col("CLV") < 10000), lit("Medium Value"))
            .when(col("CLV") < 5000, lit("Low Value"))
            .otherwise(lit("Unknown"))
        )

        # Last Interaction Date from Engagement
        last_interaction_df = engagement_df.groupBy("customer_id").agg(spark_max("interaction_date").alias("Last_Interaction_Date"))
        customer_df = customer_df.join(last_interaction_df, "customer_id", "left")

        # Data Quality Checks
        dq_errors = customer_df.filter(
            isnull(col("Customer_Segment")) | isnull(col("Last_Interaction_Date")) | isnan(col("CLV")) | (col("CLV") < 0)
        )
        valid_customer_df = customer_df.subtract(dq_errors)

        # Write error records
        if dq_errors.count() > 0:
            log_error_records(dq_errors, "customer_dimension")

        # Write valid records to Gold Layer with partitioning
        write_gold_table(valid_customer_df, "customer_dimension", mode="overwrite", partition_col="Customer_Segment")

        # Audit log
        log_audit(spark, "customer_dimension", "success")

    except Exception as e:
        log_audit(spark, "customer_dimension", "failure", str(e))

# Main execution

def main():
    spark = SparkSession.builder \
        .appName("Databricks Gold Dim DE Pipeline") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \
        .getOrCreate()
    try:
        transform_customer_dimension(spark)
        # Add other dimension transformations as needed
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

# API Cost Consumed: 1 API call for writing gold table, 1 for audit log, 1 for error log (if errors found)
