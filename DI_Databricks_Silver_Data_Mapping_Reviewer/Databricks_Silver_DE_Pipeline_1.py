# _____________________________________________
# ## *Author*: AAVA
# ## *Created on*:   
# ## *Description*:   PySpark pipeline for cleansing, validating, and standardizing Bronze layer data before storing in the Silver layer for analytical processing in Databricks.
# ## *Version*: 1 
# ## *Updated on*: 
# _____________________________________________

"""
This PySpark script implements a robust Silver layer ETL pipeline in Databricks. It reads raw data from the Bronze layer, applies schema enforcement, deduplication, null handling, and business rule validation, and writes clean data to the Silver layer in Delta format. Invalid records are redirected to an error table with detailed logs. The pipeline follows best practices for data quality, auditability, and performance optimization.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, lit, current_timestamp, monotonically_increasing_id
from pyspark.sql.types import *
import logging
import sys

# =============================
# 1. Initialize Spark Session
# =============================
spark = SparkSession.builder \
    .appName("Silver Layer ETL Pipeline") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# =============================
# 2. Configure Logging
# =============================
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("SilverPipelineLogger")

# =============================
# 3. Credential Retrieval (Example placeholders)
# =============================
# In production, retrieve from a secure vault or config file
BRONZE_PATH = "/mnt/bronze/table_name"  # Replace with actual path
SILVER_PATH = "/mnt/silver/table_name"  # Replace with actual path
ERROR_PATH  = "/mnt/silver/error_table" # Replace with actual path

# =============================
# 4. Define Schema (Example)
# =============================
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("created_date", DateType(), True),
    StructField("amount", DoubleType(), True)
])

# =============================
# 5. Validation & Error Logging Classes
# =============================
class ValidationError(Exception):
    pass

def validate_row(row):
    errors = []
    if row['id'] is None:
        errors.append("Missing id")
    if row['email'] is not None and '@' not in row['email']:
        errors.append("Invalid email format")
    if row['amount'] is not None and row['amount'] < 0:
        errors.append("Negative amount")
    # Add more business rules as needed
    return errors

def log_error(df: DataFrame, error_msgs: DataFrame) -> DataFrame:
    return error_msgs.withColumn("Table_Name", lit("table_name")) \
        .withColumn("Load_Date", current_timestamp()) \
        .withColumn("Update_Date", current_timestamp()) \
        .withColumn("Error_Timestamp", current_timestamp()) \
        .withColumn("Source_System", lit("Bronze"))

# =============================
# 6. Read Bronze Layer Data
# =============================
bronze_df = spark.read.format("delta").schema(schema).load(BRONZE_PATH)
bronze_df = bronze_df.withColumnRenamed("ID", "id") # Ensure lowercase columns

# =============================
# 7. Data Cleansing & Deduplication
# =============================
bronze_df = bronze_df.dropDuplicates(["id"])  # Deduplicate by primary key

# =============================
# 8. Validation & Error Segregation
# =============================
from pyspark.sql.functions import udf, array, struct
from pyspark.sql.types import ArrayType, StringType

@udf(ArrayType(StringType()))
def row_errors_udf(row_struct):
    return validate_row(row_struct.asDict())

bronze_with_errors = bronze_df.withColumn("errors", row_errors_udf(struct([bronze_df[x] for x in bronze_df.columns])))

valid_df = bronze_with_errors.filter(col("errors").isNull() | (col("errors").rlike("^\[\]$")))
invalid_df = bronze_with_errors.filter(col("errors").isNotNull() & (~col("errors").rlike("^\[\]$")))

# =============================
# 9. Write Valid Data to Silver Layer
# =============================
valid_df = valid_df.drop("errors")
valid_df.write.format("delta").mode("overwrite").partitionBy("created_date").save(SILVER_PATH)

# =============================
# 10. Write Invalid Data to Error Table
# =============================
from pyspark.sql.functions import explode

error_records = invalid_df.withColumn("Error_Description", explode(col("errors"))) \
    .withColumn("Error_ID", monotonically_increasing_id())

error_table = log_error(invalid_df, error_records)

error_table.select(
    "Error_ID", "Table_Name", "Error_Description", "Load_Date", "Update_Date", "Error_Timestamp", "Source_System"
).write.format("delta").mode("append").save(ERROR_PATH)

# =============================
# 11. Logging and Audit
# =============================
logger.info(f"Total records processed: {bronze_df.count()}")
logger.info(f"Valid records written to Silver: {valid_df.count()}")
logger.info(f"Invalid records written to Error Table: {error_table.count()}")

# =============================
# 12. API Cost Calculation
# =============================
API_COST_USD = 0.0025  # Example cost for this call (replace with actual if available)
print(f"\nAPI Cost Consumed: ${API_COST_USD}")
