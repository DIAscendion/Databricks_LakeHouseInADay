_____________________________________________
\
## *Author*: AAVA
\
## *Created on*:   
\
## *Description*:   PySpark pipeline to aggregate, transform, and optimize Gold Layer fact tables from Silver Layer data in Databricks, including audit logging and error handling.
\
## *Version*: 1 
\
## *Updated on*: 
\
_____________________________________________
\

\
"""
\
This pipeline reads validated and transformed transactional data from the Silver Layer, applies business transformations, creates Gold Layer fact tables with required granularity, manages audit logs, handles error records, and optimizes performance using Databricks best practices.
\
"""
\

\
from pyspark.sql import SparkSession
\
from pyspark.sql.functions import *
\
from pyspark.sql.types import *
\
from pyspark.sql.window import Window
\
import datetime
\

\
# Define Silver and Gold layer paths (replace with actual paths from your environment or config)
\
silver_path = '/mnt/silver/'  # Example path, update as needed
\
gold_path = '/mnt/gold/'      # Example path, update as needed
\
audit_log_path = '/mnt/gold/audit_logs/'
\
error_log_path = '/mnt/gold/error_records/'
\

\
# Utility functions
\
def create_spark_session():
\
    """Create Spark session with Delta Lake support and configure paths"""
\
    spark = SparkSession.builder \n\
        .appName("Databricks Gold Aggregated DE Pipeline") \n\
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \n\
        .getOrCreate()
\
    return spark
\

\
def read_silver_table(spark, table_name):
\
    """Read table from Silver layer"""
\
    return spark.read.format("delta").load(f"{silver_path}{table_name}")
\

\
def write_gold_table(df, table_name, mode="overwrite"):
\
    """Write table to Gold layer"""
\
    df.write.format("delta").mode(mode).save(f"{gold_path}{table_name}")
\

\
def write_audit_log(spark, table_name, status, message, start_time, end_time):
\
    """Write audit log entry"""
\
    audit_schema = StructType([
\
        StructField("table_name", StringType(), False),
\
        StructField("status", StringType(), False),
\
        StructField("message", StringType(), True),
\
        StructField("start_time", TimestampType(), False),
\
        StructField("end_time", TimestampType(), False)
\
    ])
\
    audit_data = [(table_name, status, message, start_time, end_time)]
\
    audit_df = spark.createDataFrame(audit_data, schema=audit_schema)
\
    audit_df.write.format("delta").mode("append").save(audit_log_path)
\

\
def write_error_log(spark, table_name, error_records):
\
    """Write error records to Gold error table"""
\
    error_records.write.format("delta").mode("append").save(f"{error_log_path}{table_name}")
\

\
# Example transformation for a fact table (replace with actual logic and table names)
\
def transform_sales_fact(spark):
\
    """Transform sales data into Gold Layer fact table"""
\
    start_time = datetime.datetime.now()
\
    status = "Success"
\
    message = ""
\
    try:
\
        # Read from Silver layer
\
        sales_df = read_silver_table(spark, "sales")
\
        customers_df = read_silver_table(spark, "customers")
\
        products_df = read_silver_table(spark, "products")
\

\
        # Business transformations: join, aggregate, filter, etc.
\
        sales_fact = sales_df \n\
            .join(customers_df, sales_df.customer_id == customers_df.customer_id, "left") \n\
            .join(products_df, sales_df.product_id == products_df.product_id, "left") \n\
            .withColumn("sales_amount", col("quantity") * col("unit_price")) \n\
            .withColumn("transaction_date", to_date(col("timestamp"))) \n\
            .groupBy(
\
                "transaction_date", "customer_id", "product_id"
\
            ).agg(
\
                sum("sales_amount").alias("total_sales"),
\
                sum("quantity").alias("total_quantity"),
\
                avg("unit_price").alias("avg_unit_price")
\
            )
\

\
        # Ensure numeric metrics are in correct format
\
        sales_fact = sales_fact.withColumn("total_sales", col("total_sales").cast(DoubleType()))
\

\
        # Write to Gold layer (partitioned by transaction_date for performance)
\
        sales_fact.write.format("delta").mode("overwrite").partitionBy("transaction_date").save(f"{gold_path}sales_fact")
\

\
        # Write audit log
\
        end_time = datetime.datetime.now()
\
        write_audit_log(spark, "sales_fact", status, message, start_time, end_time)
\

\
    except Exception as e:
\
        status = "Failed"
\
        message = str(e)
\
        end_time = datetime.datetime.now()
\
        write_audit_log(spark, "sales_fact", status, message, start_time, end_time)
\
        # Optionally, capture error records (example: failed rows)
\
        # error_records = ...
\
        # write_error_log(spark, "sales_fact", error_records)
\

\
# Main execution
\
def main():
\
    spark = create_spark_session()
\
    try:
\
        transform_sales_fact(spark)
\
        # Add additional transformation functions for other fact tables as needed
\
    finally:
\
        spark.stop()
\

\
if __name__ == "__main__":
\
    main()
\