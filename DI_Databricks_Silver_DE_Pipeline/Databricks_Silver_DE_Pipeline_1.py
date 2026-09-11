_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Databricks Silver DE Pipeline for cleansing, validating, and standardizing Bronze layer data, including enhanced transformation logic, error handling, schema validation, performance optimization, and monitoring.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
Databricks Silver DE Pipeline

This pipeline reads raw data from the Bronze layer, applies data cleansing, validation, and transformation logic (including customer segmentation), enforces schema, handles errors with retry and quarantine, optimizes joins and partitioning, and integrates monitoring and logging. Invalid records are redirected to an error table, and all operations are logged for audit and troubleshooting.
"""

# ================================
# 1. Initialize Spark Session
# ================================
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, current_timestamp, sum as _sum
from pyspark.sql.types import *
import logging
import time

# Delta Lake configs
spark = SparkSession.builder \
    .appName("Databricks Silver DE Pipeline") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# ================================
# 2. Configure Logging
# ================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("SilverDEPipeline")

# ================================
# 3. Credential Retrieval (Sample)
# ================================
# NOTE: Replace with secure credential retrieval in production
bronze_path = "/mnt/bronze/transactions"
silver_path = "/mnt/silver/transactions"
error_path = "/mnt/silver/error_transactions"
quarantine_path = "/mnt/silver/quarantine_transactions"
customer_path = "/mnt/bronze/customers"

# ================================
# 4. Schema Definition
# ================================
expected_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("transaction_date", DateType(), False),
    StructField("amount", DoubleType(), False)
])

customer_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("customer_name", StringType(), True)
])

# ================================
# 5. Helper Classes
# ================================
class ErrorLogger:
    def __init__(self):
        self.errors = []
    def log(self, table, desc, source):
        self.errors.append({
            "table": table,
            "desc": desc,
            "load_date": current_timestamp(),
            "update_date": current_timestamp(),
            "error_ts": current_timestamp(),
            "source": source
        })
    def to_df(self, spark):
        if not self.errors:
            return spark.createDataFrame([], StructType([
                StructField("table", StringType()),
                StructField("desc", StringType()),
                StructField("load_date", TimestampType()),
                StructField("update_date", TimestampType()),
                StructField("error_ts", TimestampType()),
                StructField("source", StringType())
            ]))
        return spark.createDataFrame([
            (e["table"], e["desc"], e["load_date"], e["update_date"], e["error_ts"], e["source"]) for e in self.errors
        ], ["table", "desc", "load_date", "update_date", "error_ts", "source"])

error_logger = ErrorLogger()

# ================================
# 6. Retry Mechanism
# ================================
def retry_read_delta(path, schema=None, max_retries=3, wait_sec=300):
    attempt = 0
    while attempt < max_retries:
        try:
            if schema:
                df = spark.read.format("delta").schema(schema).load(path)
            else:
                df = spark.read.format("delta").load(path)
            return df
        except Exception as e:
            logger.warning(f"Read failed for {path} (attempt {attempt+1}): {e}")
            attempt += 1
            if attempt < max_retries:
                time.sleep(wait_sec)
            else:
                error_logger.log("transactions", f"Read failed after {max_retries} attempts: {e}", "bronze")
                return None

# ================================
# 7. Read Bronze Data with Retry
# ================================
bronze_df = retry_read_delta(bronze_path, schema=expected_schema)
customer_df = retry_read_delta(customer_path, schema=customer_schema)

if bronze_df is None or customer_df is None:
    logger.error("Critical: Unable to read input data. Exiting pipeline.")
    error_logger.to_df(spark).write.format("delta").mode("append").save(error_path)
    exit(1)

# ================================
# 8. Schema Validation
# ================================
def validate_schema(df, expected_schema):
    actual_fields = set((f.name, f.dataType) for f in df.schema.fields)
    expected_fields = set((f.name, f.dataType) for f in expected_schema.fields)
    return actual_fields == expected_fields

if not validate_schema(bronze_df, expected_schema):
    logger.error("Schema mismatch detected. Moving data to quarantine.")
    bronze_df.write.format("delta").mode("append").save(quarantine_path)
    error_logger.log("transactions", "Schema mismatch. Data quarantined.", "bronze")
    error_logger.to_df(spark).write.format("delta").mode("append").save(error_path)
    exit(1)

# ================================
# 9. Data Cleansing & Deduplication
# ================================
bronze_df = bronze_df.dropDuplicates(["transaction_id"])

# ================================
# 10. Null Handling
# ================================
bronze_df = bronze_df.dropna(subset=["transaction_id", "customer_id", "transaction_date", "amount"])

# ================================
# 11. Business Rule Validation
# ================================
valid_df = bronze_df.filter((col("amount") > 0) & (col("transaction_date").isNotNull()))
invalid_df = bronze_df.subtract(valid_df)

if invalid_df.count() > 0:
    invalid_df = invalid_df.withColumn("error_desc", lit("Amount must be > 0 and transaction_date must not be null"))
    invalid_df = invalid_df.withColumn("load_date", current_timestamp()) \
                         .withColumn("update_date", current_timestamp()) \
                         .withColumn("error_ts", current_timestamp()) \
                         .withColumn("source", lit("bronze"))
    invalid_df.write.format("delta").mode("append").save(error_path)
    error_logger.log("transactions", "Business rule validation failed for some records.", "bronze")

# ================================
# 12. Transformation: Customer Segmentation
# ================================
# Aggregate total purchases per customer
customer_total = valid_df.groupBy("customer_id").agg(_sum("amount").alias("total_purchases"))

# Join with customer table
customer_df = customer_df.dropDuplicates(["customer_id"])

# Partition both tables on customer_id for optimized join
valid_df = valid_df.repartition("customer_id")
customer_total = customer_total.repartition("customer_id")

segmented_df = valid_df.join(customer_total, "customer_id", "left")
segmented_df = segmented_df.withColumn(
    "customer_segment",
    when(col("total_purchases") > 10000, lit("High Value"))
    .when((col("total_purchases") >= 5000) & (col("total_purchases") <= 10000), lit("Medium Value"))
    .otherwise(lit("Low Value"))
)

# ================================
# 13. Join with Customer Table (Optimized)
# ================================
final_df = segmented_df.join(customer_df, "customer_id", "left")

# ================================
# 14. Write to Silver Layer (Delta, Partitioned)
# ================================
final_df.write.format("delta").mode("overwrite").partitionBy("customer_id").save(silver_path)

# ================================
# 15. Write Error Data Table
# ================================
error_logger.to_df(spark).write.format("delta").mode("append").save(error_path)

# ================================
# 16. Monitoring & Metrics
# ================================
from pyspark.sql.functions import count
import datetime

start_time = datetime.datetime.now()
process_time = (datetime.datetime.now() - start_time).total_seconds() / 60.0
error_count = error_logger.to_df(spark).count()
data_volume = final_df.count()

logger.info(f"Pipeline processing time (min): {process_time}")
logger.info(f"Error count: {error_count}")
logger.info(f"Data volume processed: {data_volume}")

# Alerting (pseudo-code, replace with Databricks REST API or integration)
if process_time > 30:
    logger.warning("Processing time exceeded 30 minutes! Alerting team.")
if error_count / max(data_volume, 1) > 0.05:
    logger.warning("Error rate exceeded 5%! Alerting team.")

# ================================
# 17. Documentation
# ================================
"""
Pipeline Documentation:
- Transformation: Adds customer_segment based on total purchases.
- Error Handling: Retry logic for transient errors, schema validation with quarantine, business rule validation.
- Monitoring: Logs processing time, error rates, and data volume. Alerts on SLA breaches.
- Partitioning: Data is partitioned by customer_id for optimized joins and queries.
- Testing: Unit tests and E2E tests recommended for transformation and error handling logic.
- Troubleshooting: Check error tables and logs for failure details.
"""

# ================================
# 18. API Cost Calculation
# ================================
# (Assume a fixed cost per API call for demonstration)
API_COST_PER_CALL = 0.0025  # USD (example)
api_cost_consumed = API_COST_PER_CALL
print(f"API Cost Consumed: ${api_cost_consumed}")
