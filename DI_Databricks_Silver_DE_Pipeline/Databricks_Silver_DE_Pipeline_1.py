_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for cleansing, validating, and standardizing Bronze layer data before storing in the Silver layer for analytical processing.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

'''
Databricks Silver DE Pipeline
This pipeline reads raw data from the Bronze layer, applies data cleansing and validation, and writes the processed data to the Silver layer in Delta Lake format. Invalid records are redirected to an error table with detailed logs.
'''

# 1. Initialize Spark Session
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import logging
import datetime

# Initialize Spark session with Delta support
spark = SparkSession.builder \
    .appName('Databricks_Silver_DE_Pipeline') \
    .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension') \
    .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog') \
    .getOrCreate()

# 2. Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SilverDEPipelineLogger')

# 3. Define Validation and Error Logging Classes
class DataValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate(self, df):
        errors = []
        valid_rows = []
        for row in df.collect():
            error_msgs = []
            for field in self.schema.fields:
                value = row[field.name]
                # Null check
                if value is None and not field.nullable:
                    error_msgs.append(f"{field.name} is null")
                # Data type check
                elif value is not None and not isinstance(value, type_map[field.dataType]):
                    error_msgs.append(f"{field.name} has invalid type")
            if error_msgs:
                errors.append((row.asDict(), '; '.join(error_msgs)))
            else:
                valid_rows.append(row)
        return valid_rows, errors

class ErrorLogger:
    def __init__(self):
        self.error_logs = []
    def log(self, table_name, error_desc, source_system):
        now = datetime.datetime.now()
        self.error_logs.append({
            'Table_Name': table_name,
            'Error_Description': error_desc,
            'Load_Date': now,
            'Update_Date': now,
            'Error_Timestamp': now,
            'Source_System': source_system
        })
    def to_df(self, spark):
        return spark.createDataFrame(self.error_logs)

# 4. Read Bronze Layer Data
bronze_table = 'bronze_table_name'  # Replace with actual table name
bronze_path = '/mnt/bronze/bronze_table_name'  # Replace with actual path
bronze_df = spark.read.format('delta').load(bronze_path)

# 5. Define Silver Layer Schema (Example)
silver_schema = StructType([
    StructField('id', IntegerType(), False),
    StructField('name', StringType(), False),
    StructField('date', DateType(), True),
    StructField('amount', DoubleType(), True)
])

type_map = {
    IntegerType(): int,
    StringType(): str,
    DateType(): datetime.date,
    DoubleType(): float
}

# 6. Data Cleansing and Validation
bronze_df = bronze_df.dropDuplicates()
bronze_df = bronze_df.select([col(c).cast(silver_schema[c].dataType) for c in bronze_df.columns if c in silver_schema.fieldNames()])

validator = DataValidator(silver_schema)
valid_rows, errors = validator.validate(bronze_df)

valid_df = spark.createDataFrame(valid_rows, schema=silver_schema) if valid_rows else spark.createDataFrame([], silver_schema)

error_logger = ErrorLogger()
for error in errors:
    error_logger.log('bronze_table_name', error[1], 'Bronze')

error_df = error_logger.to_df(spark)

# 7. Store Valid Data in Silver Layer
silver_path = '/mnt/silver/silver_table_name'  # Replace with actual path
valid_df.write.format('delta').mode('overwrite').partitionBy('date').save(silver_path)

# 8. Store Error Data in Error Table (Silver & Gold)
error_table_silver = '/mnt/silver/error_table'
error_table_gold = '/mnt/gold/error_table'
error_df.write.format('delta').mode('append').save(error_table_silver)
error_df.write.format('delta').mode('append').save(error_table_gold)

# 9. Log Validation Failures
logger.info(f"Total valid records: {valid_df.count()}")
logger.info(f"Total error records: {error_df.count()}")

# 10. API Cost Calculation
api_cost_usd = 0.0025  # Example cost, replace with actual calculation if available
print(f"API Cost Consumed: ${api_cost_usd}")
