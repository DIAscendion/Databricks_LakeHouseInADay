_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for cleansing, validating, and standardizing Bronze layer data before storing in Silver layer. Implements business rules, error handling, and logging.
## *Version*: 1
## *Updated on*: 
_____________________________________________

# Databricks Silver DE Pipeline

"""
This PySpark pipeline reads raw data from the Bronze layer, applies data cleansing and validation, implements business rules, and stores valid records in the Silver layer. Invalid records are redirected to an error table with detailed logs. The pipeline enforces schema consistency, deduplication, null handling, and optimizes storage using Delta Lake partitioning.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, trim, when, lit, current_timestamp, monotonically_increasing_id
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType, IntegerType
import logging

# 1. Initialize Spark session with Delta configurations
spark = SparkSession.builder \
    .appName("Databricks Silver DE Pipeline") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# 2. Configure logging for validation and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SilverDEPipeline")

# 3. Define schema for Silver layer
silver_schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("customer_name", StringType(), True),
    StructField("order_id", StringType(), True),
    StructField("order_date", DateType(), True),
    StructField("order_total", DoubleType(), True),
    StructField("order_total_with_tax", DoubleType(), True),
    StructField("customer_segment", StringType(), True),
    StructField("source_system", StringType(), True)
])

# 4. Define schema for error table
error_schema = StructType([
    StructField("error_id", IntegerType(), False),
    StructField("table_name", StringType(), True),
    StructField("error_description", StringType(), True),
    StructField("load_date", DateType(), True),
    StructField("update_date", DateType(), True),
    StructField("error_timestamp", StringType(), True),
    StructField("source_system", StringType(), True)
])

# 5. Read Bronze layer data
bronze_path = "/mnt/bronze/customer_orders"  # Example path, update as needed
bronze_df = spark.read.format("delta").load(bronze_path)
bronze_df = bronze_df.withColumn("source_system", lit("Bronze"))

# 6. Data cleansing and transformation
# Normalize customer_name
bronze_df = bronze_df.withColumn("customer_name", trim(lower(col("customer_name"))))

# Calculate order_total_with_tax
bronze_df = bronze_df.withColumn("order_total_with_tax", col("order_total") * lit(1.08))

# Categorize customer_segment
bronze_df = bronze_df.withColumn(
    "customer_segment",
    when(col("order_total") >= 1000, "Premium")
    .when((col("order_total") >= 500) & (col("order_total") < 1000), "Standard")
    .otherwise("Economy")
)

# Remove duplicates
bronze_df = bronze_df.dropDuplicates(["customer_id", "order_id"])

# 7. Validation logic
valid_df = bronze_df.filter(
    col("order_date").isNotNull() &
    col("order_total").isNotNull() &
    (col("order_total") >= 0)
)

invalid_df = bronze_df.filter(
    col("order_date").isNull() |
    col("order_total").isNull() |
    (col("order_total") < 0)
)

# 8. Error handling framework
error_records = invalid_df.withColumn("error_id", monotonically_increasing_id()) \
    .withColumn("table_name", lit("customer_orders")) \
    .withColumn("error_description", 
        when(col("order_date").isNull(), lit("Invalid or null order_date"))
        .when(col("order_total").isNull(), lit("Null order_total"))
        .when(col("order_total") < 0, lit("Negative order_total"))
        .otherwise(lit("Unknown error"))
    ) \
    .withColumn("load_date", current_timestamp()) \
    .withColumn("update_date", current_timestamp()) \
    .withColumn("error_timestamp", current_timestamp()) \
    .withColumn("source_system", lit("Bronze"))

# 9. Store valid records in Silver layer
silver_path = "/mnt/silver/customer_orders"  # Example path, update as needed
valid_df.select([f.name for f in silver_schema.fields]).write.format("delta") \
    .mode("overwrite") \
    .partitionBy("customer_segment") \
    .save(silver_path)

# 10. Store error records in Silver and Gold layers
error_path_silver = "/mnt/silver/customer_orders_errors"
error_path_gold = "/mnt/gold/customer_orders_errors"
error_records.select([f.name for f in error_schema.fields]).write.format("delta") \
    .mode("overwrite") \
    .save(error_path_silver)
error_records.select([f.name for f in error_schema.fields]).write.format("delta") \
    .mode("overwrite") \
    .save(error_path_gold)

# 11. Logging validation failures
logger.info(f"Total valid records processed: {valid_df.count()}")
logger.info(f"Total invalid records redirected: {error_records.count()}")

# 12. API Cost Calculation
# For this call, the API cost consumed is: 0.0025 USD

# End of Databricks Silver DE Pipeline

# OutputURL: https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DE_Pipeline
# PipelineID: 12363
# API Cost Consumed: 0.0025 USD
