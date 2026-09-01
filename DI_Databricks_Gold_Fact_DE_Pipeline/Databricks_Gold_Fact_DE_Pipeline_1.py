_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline to move Silver Layer TMS Shipment data to Gold Fact Table with business transformations, audit logging, and performance optimization.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
Databricks Gold Fact DE Pipeline for TMS Shipment Application
- Extracts data from Silver Layer
- Applies business transformations and mappings
- Loads data into Gold Fact Table (gd_shipment)
- Maintains audit and error logs
- Optimizes for performance and Gold Layer compatibility
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Silver and Gold Layer paths
silver_path = '/mnt/silver/'
gold_path = '/mnt/gold/'

def create_spark_session():
    """Create Spark session with Delta Lake support and configure paths"""
    spark = SparkSession.builder \
        .appName("Silver to Gold Fact Table Pipeline") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \
        .getOrCreate()
    return spark

def read_silver_table(spark, table_name):
    """Read table from Silver layer"""
    return spark.read.format("delta").load(f"{silver_path}{table_name}")

def write_gold_table(df, table_name, mode="overwrite"):
    """Write table to Gold layer"""
    df.write.format("delta").mode(mode).option("overwriteSchema", "true").save(f"{gold_path}{table_name}")

def write_audit_log(spark, pipeline_name, execution_id, start_time, end_time, status, error_message, record_count):
    """Write audit log to gold and silver audit tables"""
    audit_schema = StructType([
        StructField("audit_id", LongType(), True),
        StructField("pipeline_name", StringType(), True),
        StructField("execution_id", StringType(), True),
        StructField("start_time", TimestampType(), True),
        StructField("end_time", TimestampType(), True),
        StructField("status", StringType(), True),
        StructField("error_message", StringType(), True),
        StructField("record_count", LongType(), True),
        StructField("load_date", TimestampType(), True),
        StructField("update_date", TimestampType(), True),
        StructField("source_system", StringType(), True)
    ])
    audit_df = spark.createDataFrame([
        (None, pipeline_name, execution_id, start_time, end_time, status, error_message, record_count, current_timestamp(), current_timestamp(), 'TMS')
    ], schema=audit_schema)
    audit_df.write.format("delta").mode("append").save(f"{silver_path}audit")
    audit_df.write.format("delta").mode("append").save(f"{gold_path}audit")

def write_error_log(spark, error_records_df):
    """Write error records to gold fact error table"""
    error_records_df.write.format("delta").mode("append").save(f"{gold_path}shipment_error")

def transform_shipment_fact(spark):
    """Transform Silver sv_shipment to Gold gd_shipment with business rules"""
    start_time = current_timestamp()
    execution_id = str(uuid.uuid4())
    status = 'Success'
    error_message = None
    record_count = 0
    try:
        # Read Silver tables
        shipment_df = read_silver_table(spark, "shipment")
        # Read Gold dimension tables for surrogate key joins (assume they exist)
        customer_df = spark.read.format("delta").load(f"{gold_path}customer")
        carrier_df = spark.read.format("delta").load(f"{gold_path}carrier")

        # Business Transformations
        gold_df = shipment_df \
            .withColumn("CURRENCY_CODE", when(col("CURRENCY_CODE").isNull(), lit("USD")).otherwise(col("CURRENCY_CODE"))) \
            .withColumn("ORDER_QTY", coalesce(col("ORDER_QTY").cast(IntegerType()), lit(0))) \
            .withColumn("PLANNED_WEIGHT", col("PLANNED_WEIGHT")) \
            .withColumn("DISTANCE", when(col("DISTANCE_UOM") == "M", col("DISTANCE") / 1000).otherwise(col("DISTANCE"))) \
            .withColumn("DISTANCE_UOM", lit("KM")) \
            .withColumn("DAYS_TO_DELIVER", coalesce(col("DAYS_TO_DELIVER"), lit(0))) \
            .withColumn("MARGIN", round(col("MARGIN"), 2)) \
            .join(customer_df.select(col("CUSTOMER_ID").alias("CUST_ID"), col("Customer_Key")), shipment_df["CUSTOMER_ID"] == col("CUST_ID"), "left") \
            .join(carrier_df.select(col("CARRIER_ID").alias("CARR_ID"), col("Carrier_Key")), shipment_df["ASSIGNED_CARRIER_ID"] == col("CARR_ID"), "left")

        # Remove duplicates
        gold_df = gold_df.dropDuplicates(["SHIPMENT_ID"])

        # Data Validation and Error Handling
        error_records_df = gold_df.filter(
            (col("SHIPMENT_ID").isNull()) |
            (col("TOTAL_COST") < 0) |
            (col("ORDER_QTY") < 0) |
            (col("PLANNED_WEIGHT") < 0) |
            (col("DISTANCE") < 0)
        ).withColumn("error_type", lit("ValidationError")) \
         .withColumn("error_message", lit("Failed business rule validation in Gold Fact transformation")) \
         .withColumn("error_timestamp", current_timestamp()) \
         .withColumn("layer", lit("gold"))

        # Only keep valid records
        gold_df = gold_df.filter(
            col("SHIPMENT_ID").isNotNull() &
            (col("TOTAL_COST") >= 0) &
            (col("ORDER_QTY") >= 0) &
            (col("PLANNED_WEIGHT") >= 0) &
            (col("DISTANCE") >= 0)
        )

        # Write Gold Fact Table
        write_gold_table(gold_df, "shipment")
        record_count = gold_df.count()

        # Write Error Records
        if error_records_df.count() > 0:
            write_error_log(spark, error_records_df)
        status = 'Success'
    except Exception as e:
        status = 'Failed'
        error_message = str(e)
    finally:
        end_time = current_timestamp()
        write_audit_log(spark, "Databricks_Gold_Fact_DE_Pipeline", execution_id, start_time, end_time, status, error_message, record_count)

def main():
    """Main execution function"""
    spark = create_spark_session()
    try:
        transform_shipment_fact(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
