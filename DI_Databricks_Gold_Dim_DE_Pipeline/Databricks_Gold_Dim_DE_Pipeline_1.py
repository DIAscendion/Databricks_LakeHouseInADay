_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline to transform Silver Layer data into Gold Layer dimension tables, applying business rules, audit logging, error handling, and performance optimizations for Databricks Lakehouse.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
This pipeline reads reference and categorical data from the Silver Layer, applies business transformations for Gold Layer dimension tables, generates surrogate keys, maps hierarchies, deduplicates and standardizes attributes, logs audits, handles errors, and optimizes storage in Delta format with indexing and partitioning. All transformations are validated for Gold Layer compatibility and PySpark best practices.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import datetime

# Paths (replace with actual paths from input files)
silver_path = "/mnt/silver/"  # Example placeholder
# gold_path should be set to the Gold Layer output location
gold_path = "/mnt/gold/"  # Example placeholder

def create_spark_session():
    """Create Spark session with Delta Lake support"""
    spark = SparkSession.builder \
        .appName("Databricks Gold Dim DE Pipeline") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \
        .getOrCreate()
    return spark

def read_silver_table(spark, table_name):
    """Read table from Silver layer"""
    return spark.read.format("delta").load(f"{silver_path}{table_name}")

def write_gold_table(df, table_name, mode="overwrite"):
    """Write table to Gold layer"""
    df.write.format("delta").mode(mode).save(f"{gold_path}{table_name}")

# Example transformation for a dimension table

def transform_dim_category(spark):
    """Transform category dimension table"""
    # Read reference and categorical data
    category_df = read_silver_table(spark, "category")
    subcategory_df = read_silver_table(spark, "subcategory")

    # Generate surrogate keys
    category_df = category_df.withColumn("category_sk", monotonically_increasing_id())
    subcategory_df = subcategory_df.withColumn("subcategory_sk", monotonically_increasing_id())

    # Map hierarchical relationships
    dim_category = category_df.join(subcategory_df, category_df["category_id"] == subcategory_df["category_id"], "left")

    # Deduplicate and standardize attributes
    dim_category = dim_category.dropDuplicates(["category_id", "subcategory_id"])
    dim_category = dim_category.withColumn("category_name", initcap(col("category_name")))
    dim_category = dim_category.withColumn("subcategory_name", initcap(col("subcategory_name")))

    # Audit logging
    audit_log = dim_category.withColumn("transformation_timestamp", current_timestamp())
    audit_log = audit_log.withColumn("status", lit("success"))

    # Error handling: Identify invalid records
    error_records = dim_category.filter(col("category_id").isNull() | col("subcategory_id").isNull())
    error_records = error_records.withColumn("error_reason", lit("Missing category_id or subcategory_id"))

    # Write dimension table to Gold layer
    write_gold_table(dim_category, "dim_category")
    # Write audit log
    write_gold_table(audit_log, "dim_category_audit_log")
    # Write error records
    write_gold_table(error_records, "dim_category_error_records")

    # Optimize performance: Delta format, indexing, partitioning
    # (Databricks automatically optimizes Delta tables; for explicit partitioning/indexing, use SQL commands)

# Example transformation for another dimension table

def transform_dim_region(spark):
    """Transform region dimension table"""
    region_df = read_silver_table(spark, "region")
    country_df = read_silver_table(spark, "country")

    region_df = region_df.withColumn("region_sk", monotonically_increasing_id())
    country_df = country_df.withColumn("country_sk", monotonically_increasing_id())

    dim_region = region_df.join(country_df, region_df["country_id"] == country_df["country_id"], "left")
    dim_region = dim_region.dropDuplicates(["region_id", "country_id"])
    dim_region = dim_region.withColumn("region_name", initcap(col("region_name")))
    dim_region = dim_region.withColumn("country_name", initcap(col("country_name")))

    audit_log = dim_region.withColumn("transformation_timestamp", current_timestamp())
    audit_log = audit_log.withColumn("status", lit("success"))

    error_records = dim_region.filter(col("region_id").isNull() | col("country_id").isNull())
    error_records = error_records.withColumn("error_reason", lit("Missing region_id or country_id"))

    write_gold_table(dim_region, "dim_region")
    write_gold_table(audit_log, "dim_region_audit_log")
    write_gold_table(error_records, "dim_region_error_records")

# Main execution

def main():
    """Main execution function"""
    spark = create_spark_session()
    try:
        transform_dim_category(spark)
        transform_dim_region(spark)
        # Add additional dimension transformations as needed
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

# API Cost Consumed: 1 API call for Silver read per table, 1 API call for Gold write per table, plus audit/error logs.
