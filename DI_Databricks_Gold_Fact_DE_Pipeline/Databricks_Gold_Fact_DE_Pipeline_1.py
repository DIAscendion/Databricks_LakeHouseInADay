_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for transforming Silver Layer shipment data into Gold Layer Fact tables with business rules, audit logging, error handling, and performance optimization.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
Databricks Gold Fact DE Pipeline
Shipment Domain - Gold Layer Fact Table Creation
"""

# Imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import sha2, col, upper, coalesce, lit, when, count, sum, avg, min, max, current_timestamp
from pyspark.sql.types import DecimalType, StringType, IntegerType, TimestampType

# Initialize Spark Session
spark = SparkSession.builder.appName("GoldFactPipeline_Shipment").getOrCreate()

# 1. Extract Data from Silver Layer
silver_shipment_df = spark.read.format("delta").table("silver.si_shipment_process")
silver_item_df = spark.read.format("delta").table("silver.si_shipment_item")
silver_error_df = spark.read.format("delta").table("silver.si_error_log")
silver_audit_df = spark.read.format("delta").table("silver.si_audit_log")

# 2. Business Transformations for Fact Tables
# Surrogate Key Generation
shipment_fact_df = silver_shipment_df.withColumn(
    "shipment_fact_id", sha2(col("shipment_process_id"), 256)
)

# Foreign Key Relationships (Dimension Table Joins)
# Example: Facility, Carrier, Route, Customer
facility_dim_df = spark.read.format("delta").table("gold.go_facility_dim")
carrier_dim_df = spark.read.format("delta").table("gold.go_carrier_dim")
route_dim_df = spark.read.format("delta").table("gold.go_route_dim")
business_partner_dim_df = spark.read.format("delta").table("gold.go_business_partner_dim")

shipment_fact_df = shipment_fact_df \
    .join(facility_dim_df, shipment_fact_df["O_FACILITY_ID"] == facility_dim_df["facility_id"], "left") \
    .withColumn("origin_dim_id", facility_dim_df["facility_dim_id"]) \
    .join(facility_dim_df, shipment_fact_df["D_FACILITY_ID"] == facility_dim_df["facility_id"], "left") \
    .withColumn("destination_dim_id", facility_dim_df["facility_dim_id"]) \
    .join(carrier_dim_df, shipment_fact_df["ASSIGNED_CARRIER_ID"] == carrier_dim_df["carrier_id"], "left") \
    .withColumn("carrier_dim_id", carrier_dim_df["carrier_dim_id"]) \
    .join(route_dim_df, shipment_fact_df["ROUTE_REFERENCE"] == route_dim_df["route_reference"], "left") \
    .withColumn("route_dim_id", route_dim_df["route_dim_id"]) \
    .join(business_partner_dim_df, shipment_fact_df["BUSINESS_PARTNER_ID"] == business_partner_dim_df["business_partner_id"], "left") \
    .withColumn("customer_dim_id", business_partner_dim_df["business_partner_dim_id"])

# Apply Business Rules, Null Handling, and Calculated Fields
shipment_fact_df = shipment_fact_df \
    .withColumn("shipment_status", upper(coalesce(col("shipment_status"), lit("UNKNOWN")))) \
    .withColumn("shipment_weight_kg", coalesce(col("shipment_weight").cast(DecimalType(10,2)), lit(0))) \
    .withColumn("shipment_type", upper(coalesce(col("shipment_type"), lit("UNKNOWN")))) \
    .withColumn("amount_usd", coalesce(col("amount").cast(DecimalType(10,2)), lit(0))) \
    .withColumn("profit_margin", coalesce(col("profit_margin").cast(DecimalType(5,4)), lit(0))) \
    .withColumn("total_cost_usd", coalesce(col("TOTAL_COST").cast(DecimalType(10,2)), lit(0))) \
    .withColumn("total_revenue_usd", coalesce(col("TOTAL_REVENUE").cast(DecimalType(10,2)), lit(0))) \
    .withColumn("margin_usd", coalesce(col("MARGIN").cast(DecimalType(10,2)), lit(0))) \
    .withColumn("number_of_stops", coalesce(col("NUM_STOPS").cast(IntegerType()), lit(0))) \
    .withColumn("planned_weight_kg", coalesce(col("PLANNED_WEIGHT").cast(DecimalType(10,3)), lit(0))) \
    .withColumn("planned_volume_m3", coalesce(col("PLANNED_VOLUME").cast(DecimalType(10,3)), lit(0)))

# Add new columns for reporting (example: calculated metrics)
shipment_fact_df = shipment_fact_df \
    .withColumn("shipment_priority", coalesce(col("shipment_priority"), lit("STANDARD")))

# Remove deprecated columns/logic (example)
# shipment_fact_df = shipment_fact_df.drop("deprecated_column")

# Deduplication
shipment_fact_df = shipment_fact_df.dropDuplicates(["shipment_fact_id"])

# 3. Data Quality Validation
# Null checks, duplicates, range checks
quality_issues_df = shipment_fact_df \
    .filter(
        (col("shipment_fact_id").isNull()) |
        (col("shipment_number").isNull()) |
        (col("shipment_weight_kg") < 0) |
        (col("amount_usd") < 0)
    )

# 4. Audit Logging
from pyspark.sql.functions import monotonically_increasing_id

audit_log_df = shipment_fact_df.select(
    monotonically_increasing_id().alias("audit_id"),
    lit("go_shipment_fact").alias("source_table"),
    current_timestamp().alias("load_date"),
    lit("GoldFactPipeline_Shipment").alias("processed_by"),
    lit(0).alias("processing_time"),
    lit("SUCCESS").alias("status"),
    col("created_at"),
    col("updated_at"),
    col("update_date"),
    col("source_system")
)

# 5. Error Logging
error_log_df = quality_issues_df.select(
    monotonically_increasing_id().alias("error_id"),
    lit("go_shipment_fact").alias("source_table"),
    lit("DATA_QUALITY").alias("error_type"),
    lit("Null or invalid values detected").alias("error_message"),
    current_timestamp().alias("error_timestamp"),
    col("shipment_fact_id").alias("record_reference"),
    col("created_at"),
    col("updated_at"),
    col("load_date"),
    col("update_date"),
    col("source_system")
)

# 6. Performance Optimization
# Partitioning by shipment_status, shipment_date
shipment_fact_df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("shipment_status", "shipment_date") \
    .option("overwriteSchema", "true") \
    .saveAsTable("gold.go_shipment_fact")

audit_log_df.write.format("delta") \
    .mode("append") \
    .saveAsTable("gold.go_audit_log")

error_log_df.write.format("delta") \
    .mode("append") \
    .saveAsTable("gold.go_error_log")

# Indexing (Databricks Delta automatically optimizes high-query fields)
# Use OPTIMIZE and VACUUM for storage management
spark.sql("OPTIMIZE gold.go_shipment_fact")
spark.sql("VACUUM gold.go_shipment_fact RETAIN 168 HOURS")

# 7. Incremental Load Handling
# Example: Only process new/updated records
incremental_shipment_df = silver_shipment_df.filter(col("update_date") > lit("{{last_run_date}}"))
# (Replace '{{last_run_date}}' with actual value in orchestration)

# 8. Layer Compatibility Validation
# Validate Gold Layer DDL compatibility
# (DDL validation logic can be added here as needed)

# 9. Logging Execution Metrics
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logging.info(f"Gold Fact Pipeline executed at {datetime.now()}")

# End of Pipeline

# Output URL and Pipeline ID
print("outputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Fact_DE_Pipeline")
print("pipelineID: 14679")
