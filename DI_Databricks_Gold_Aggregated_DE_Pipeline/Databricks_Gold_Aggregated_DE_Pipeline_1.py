_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for Gold Layer Aggregated Fact Tables, Audit Logging, Error Handling, and Performance Optimization for Shipment Analytics
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
Databricks Gold Aggregated DE Pipeline
- Extracts validated shipment data from Silver Layer
- Applies business transformations and aggregations for Gold Layer analytics
- Generates audit logs and error records
- Optimizes performance using Delta Lake features
- Ensures Gold Layer compatibility and best practices
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Define Silver and Gold layer paths (update as per environment)
silver_path = "/mnt/silver/"
gold_path = "/mnt/gold/"

def create_spark_session():
    """Create Spark session with Delta Lake support"""
    spark = SparkSession.builder \
        .appName("Gold Aggregated DE Pipeline") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \
        .getOrCreate()
    return spark

def read_silver_table(spark, table_name):
    """Read table from Silver layer"""
    return spark.read.format("delta").load(f"{silver_path}{table_name}")

def write_gold_table(df, table_name, mode="overwrite"):
    """Write table to Gold layer"""
    df.write.format("delta").mode(mode).save(f"{gold_path}{table_name}")

# 1. Business Transformations for Fact Tables

def transform_shipment_agg_fact(spark):
    """Transform and aggregate shipment data for Gold Layer analytics"""
    df = read_silver_table(spark, "si_shipment_process")
    # Apply filters: Exclude cancelled orders, include last 5 years
    df = df.filter((col("shipment_status") != "CANCELLED") & (col("order_date") >= date_add(current_date(), -1825)))
    # Replace NULLs
    df = df.fillna({"shipment_number": "UNKNOWN", "amount": 0, "customer_segment": "UNKNOWN", "order_count": 0})
    # Aggregations
    shipment_agg = df.groupBy(
        "shipment_status", "shipment_type", "origin", "destination", "customer_segment", "client_id"
    ).agg(
        count("shipment_number").alias("total_shipment_count"),
        round(100.0 * sum(when(col("shipment_status") == "CANCELLED", 1).otherwise(0)) / count("shipment_number"), 2).alias("cancelled_shipment_percent"),
        round(100.0 * sum(when(col("shipment_status") == "RECONCILED", 1).otherwise(0)) / count("shipment_number"), 2).alias("reconciled_shipment_percent"),
        round(100.0 * sum(when(col("broker_carrier_name").isNotNull() & (col("broker_carrier_name") != ""), 1).otherwise(0)) / count("shipment_number"), 2).alias("broker_carrier_usage_percent"),
        round(100.0 * sum(when(col("on_time_indicator") == "Y", 1).otherwise(0)) / count("shipment_number"), 2).alias("on_time_pickup_percent"),
        round(100.0 * sum(col("out_of_route_distance")) / greatest(sum(col("total_route_distance")), lit(1)), 2).alias("out_of_route_distance_percent"),
        round(avg(col("number_of_stops")), 2).alias("average_stops_per_shipment"),
        round(avg(when(col("total_route_distance") > 0, col("direct_distance") / col("total_route_distance")).otherwise(None)), 3).alias("route_efficiency_index"),
        sum(when(col("reconciled_flag") == False, 1).otherwise(0)).alias("unreconciled_shipment_count"),
        collect_list(when(col("reconciled_flag") == False, concat_ws(":", col("shipment_reference_number"), datediff(current_date(), col("creation_date")))).otherwise(None)).alias("unreconciled_shipment_aging"),
        collect_list(concat_ws(":", date_trunc("day", col("creation_date")), count("shipment_number"))).alias("creation_volume_trend"),
        round(100.0 * sum(when(col("creation_source") == "API", 1).otherwise(0)) / count("shipment_number"), 2).alias("api_source_percent"),
        round(100.0 * sum(when(col("creation_source") == "MANUAL", 1).otherwise(0)) / count("shipment_number"), 2).alias("manual_source_percent"),
        round(100.0 * sum(when(col("creation_source") == "INTEGRATION", 1).otherwise(0)) / count("shipment_number"), 2).alias("integration_source_percent"),
        sum(col("amount")).alias("Customer_Lifetime_Value"),
        sum(col("amount") * col("currency_conversion_factor_to_USD")).alias("Sales_Amount"),
        sum(col("order_count")).alias("Total_Orders"),
        round(avg(when(col("order_flag") != "RETURN", col("amount"))), 2).alias("Average_Order_Value"),
        max(col("updated_at")).alias("Last_Updated_Timestamp"),
        first(col("source_system")).alias("Data_Source")
    )
    # Customer Segmentation: Add 'High Value' tier
    shipment_agg = shipment_agg.withColumn(
        "Customer_Segments",
        when(col("Customer_Lifetime_Value") > 100000, "High Value").otherwise(col("customer_segment"))
    )
    # Region Code Mapping (stub, replace with actual lookup)
    shipment_agg = shipment_agg.withColumn("Region_Code", col("destination"))
    # Product Category Mapping (stub, replace with actual taxonomy)
    shipment_agg = shipment_agg.withColumn("Product_Category", lit("Standardized"))
    # Geographic Region Mapping (stub, replace with actual region mapping)
    shipment_agg = shipment_agg.withColumn("Geographic_Region", col("region_id"))
    # Write to Gold layer
    write_gold_table(shipment_agg, "go_shipment_agg")

# 2. Audit Logs

def generate_audit_log(spark, status="SUCCESS", error_message=None):
    """Generate audit log for Gold Layer transformation"""
    audit_schema = StructType([
        StructField("audit_id", StringType()),
        StructField("source_table", StringType()),
        StructField("load_date", TimestampType()),
        StructField("processed_by", StringType()),
        StructField("processing_time", DoubleType()),
        StructField("status", StringType()),
        StructField("created_at", TimestampType()),
        StructField("updated_at", TimestampType()),
        StructField("update_date", TimestampType()),
        StructField("source_system", StringType())
    ])
    audit_log = spark.createDataFrame([
        (str(uuid.uuid4()), "si_shipment_process", current_timestamp(), "AAVA", 0.0, status, current_timestamp(), current_timestamp(), current_timestamp(), "Databricks")
    ], schema=audit_schema)
    write_gold_table(audit_log, "go_audit_log", mode="append")

# 3. Error Record in Fact Table

def generate_error_log(spark, error_message):
    """Generate error log for Gold Layer transformation"""
    error_schema = StructType([
        StructField("error_id", StringType()),
        StructField("source_table", StringType()),
        StructField("error_type", StringType()),
        StructField("error_message", StringType()),
        StructField("error_timestamp", TimestampType()),
        StructField("record_reference", StringType()),
        StructField("created_at", TimestampType()),
        StructField("updated_at", TimestampType()),
        StructField("load_date", TimestampType()),
        StructField("update_date", TimestampType()),
        StructField("source_system", StringType())
    ])
    error_log = spark.createDataFrame([
        (str(uuid.uuid4()), "si_shipment_process", "TRANSFORMATION_ERROR", error_message, current_timestamp(), "", current_timestamp(), current_timestamp(), current_timestamp(), current_timestamp(), "Databricks")
    ], schema=error_schema)
    write_gold_table(error_log, "go_error_log", mode="append")

# 4. Performance Optimization
# Partitioning, Delta format, indexing handled by Delta Lake and Databricks
# Use OPTIMIZE and VACUUM commands periodically for compaction and cleanup

# 5. Verify Layer Compatibility
# Ensure Gold Layer DDL matches target schema, avoid unsupported features

# Main Execution

def main():
    """Main execution function"""
    spark = create_spark_session()
    try:
        transform_shipment_agg_fact(spark)
        generate_audit_log(spark, status="SUCCESS")
    except Exception as e:
        generate_audit_log(spark, status="FAILURE", error_message=str(e))
        generate_error_log(spark, error_message=str(e))
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
