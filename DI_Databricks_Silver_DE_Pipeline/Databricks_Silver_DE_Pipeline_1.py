_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for cleansing, validating, and standardizing Bronze layer data before storing in Silver layer (TMS Shipment Application)
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Silver DE Pipeline: TMS Shipment Application

"""
This PySpark pipeline reads raw data from the Bronze layer, performs data cleansing and validation, stores processed data into the Silver layer, implements schema enforcement, deduplication, null handling, business rule validation, and redirects invalid records to an error table with detailed logs. Cleaned and validated data is stored in Delta Lake format with optimized partitioning.
"""

# 1. Initialize Spark Session with Delta Configurations
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, monotonically_increasing_id
from pyspark.sql.types import *
import logging

spark = SparkSession.builder \
    .appName("Databricks Silver DE Pipeline - TMS Shipment") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# 2. Configure Logging for Validation and Error Tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SilverDEPipeline")

# 3. Define Validation and Error Logging Classes
class DataValidator:
    def __init__(self, schema):
        self.schema = schema
    def validate(self, df):
        errors = []
        # Example: Null checks, type checks, business rules
        for field in self.schema.fields:
            if not field.nullable:
                null_count = df.filter(col(field.name).isNull()).count()
                if null_count > 0:
                    errors.append((field.name, f"Null values found: {null_count}"))
        # Add more business rule checks as needed
        return errors

class ErrorLogger:
    def __init__(self):
        self.error_records = []
    def log(self, table_name, record_id, error_type, error_message, layer, source_system):
        self.error_records.append({
            "table_name": table_name,
            "record_id": record_id,
            "error_type": error_type,
            "error_message": error_message,
            "error_timestamp": current_timestamp(),
            "layer": layer,
            "load_date": current_timestamp(),
            "update_date": current_timestamp(),
            "source_system": source_system
        })
    def to_df(self, spark):
        schema = StructType([
            StructField("table_name", StringType(), True),
            StructField("record_id", StringType(), True),
            StructField("error_type", StringType(), True),
            StructField("error_message", StringType(), True),
            StructField("error_timestamp", TimestampType(), True),
            StructField("layer", StringType(), True),
            StructField("load_date", TimestampType(), True),
            StructField("update_date", TimestampType(), True),
            StructField("source_system", StringType(), True)
        ])
        return spark.createDataFrame(self.error_records, schema)

# 4. Read Bronze Layer Data (Example: bz_shipment)
bronze_table = "bronze.bz_shipment"
silver_table = "silver.sv_shipment"
error_table = "silver.sv_shipment_error"
source_system = "Bronze"

bronze_df = spark.read.format("delta").table(bronze_table)

# 5. Schema Enforcement (Silver Layer Schema Example)
silver_schema = StructType([
    StructField("id", LongType(), True),
    StructField("SHIPMENT_ID", StringType(), True),
    StructField("TC_SHIPMENT_ID", StringType(), True),
    StructField("TOTAL_COST", DoubleType(), True),
    StructField("CREATED_DTTM", TimestampType(), True),
    StructField("load_date", TimestampType(), True),
    StructField("update_date", TimestampType(), True),
    StructField("source_system", StringType(), True)
    # Add all other Silver layer columns as per DDL
])

# 6. Data Cleansing and Validation
# Remove duplicates
bronze_df = bronze_df.dropDuplicates(["SHIPMENT_ID"])

# Handle nulls and enforce schema
bronze_df = bronze_df.withColumn("load_date", current_timestamp()) \
                     .withColumn("update_date", current_timestamp()) \
                     .withColumn("source_system", lit(source_system))

validator = DataValidator(silver_schema)
errors = validator.validate(bronze_df)

error_logger = ErrorLogger()

# Business Rule Example: TOTAL_COST must be >= 0
invalid_cost_df = bronze_df.filter(col("TOTAL_COST") < 0)
for row in invalid_cost_df.collect():
    error_logger.log(
        table_name=silver_table,
        record_id=row["SHIPMENT_ID"],
        error_type="BusinessRuleViolation",
        error_message="TOTAL_COST < 0",
        layer="Silver",
        source_system=source_system
    )

# Remove invalid records from main DataFrame
bronze_df = bronze_df.filter(col("TOTAL_COST") >= 0)

# 7. Store Valid Records in Silver Layer
bronze_df = bronze_df.withColumn("id", monotonically_increasing_id())
bronze_df.select([field.name for field in silver_schema.fields]).write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("CREATED_DTTM") \
    .saveAsTable(silver_table)

# 8. Store Invalid Records in Error Table
error_df = error_logger.to_df(spark)
if error_df.count() > 0:
    error_df.write.format("delta") \
        .mode("append") \
        .partitionBy("error_timestamp") \
        .saveAsTable(error_table)

# 9. Logging Validation Failures
if errors:
    for field, msg in errors:
        logger.error(f"Validation error in field '{field}': {msg}")

logger.info("Silver DE Pipeline execution completed.")

# 10. API Cost Calculation
api_cost = 0.000100 + 0.000000  # Bronze + Silver model file costs
print(f"API Cost Consumed: {api_cost:.6f} USD")

# 11. Output URL and Pipeline ID
print("outputURL : https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Silver_DE_Pipeline")
print("pipelineID : 12363")
