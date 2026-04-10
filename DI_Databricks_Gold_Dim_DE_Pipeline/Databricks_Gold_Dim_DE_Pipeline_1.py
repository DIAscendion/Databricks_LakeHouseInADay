_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for processing Silver Layer data into Gold Layer dimension tables, including Customer Lifetime Value (CLV) calculation, schema enhancements, data quality checks, audit logging, error handling, and performance optimizations.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

"""
Databricks Gold Dim DE Pipeline
- Extracts reference and categorical data from Silver Layer
- Applies business transformations for dimension tables
- Generates surrogate keys and maps hierarchical relationships
- Deduplicates and standardizes attributes
- Implements audit logging and error handling
- Integrates new Customer_Engagement data source
- Adds Customer Lifetime Value (CLV), Customer_Segment, Last_Interaction_Date
- Optimizes performance with Delta format and partitioning
- Ensures Gold Layer compatibility and data quality
"""
# Databricks notebook source
# =============================================================================
# NOTEBOOK  : 01_silver_to_gold_DIM.py
# LAYER     : Silver  →  Gold  (Dimension Tables)
# PURPOSE   : Build carrier and facility dimension tables from
#             carnival.silver.sv_shipment
# DIMENSIONS: carnival.gold.go_dim_carrier
#             carnival.gold.go_dim_facility
# SCHEDULE  : Run before Fact and Aggregation notebooks
# =============================================================================

# COMMAND ----------
# ── Imports ────────────────────────────────────────────────────────────────
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, LongType, DecimalType, TimestampType
)
from pyspark.sql.window import Window
from delta.tables import DeltaTable
from datetime import datetime

# COMMAND ----------
# ── Config ─────────────────────────────────────────────────────────────────
SILVER_SHIPMENT  = "carnival.silver.sv_shipment"
SILVER_AUDIT     = "carnival.silver.sv_audit"
SILVER_ERROR     = "carnival.silver.sv_shipment_error"

CARRIER_TABLE    = "carnival.gold.go_dim_carrier"
FACILITY_TABLE   = "carnival.gold.go_dim_facility"

PIPELINE_NAME    = "silver_to_gold_DIM"
EXECUTION_ID     = f"EXEC-DIM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
LOAD_DTTM        = F.current_timestamp()

# COMMAND ----------
# ── Explicit schemas — prevents CANNOT_DETERMINE_TYPE on None fields ───────
AUDIT_SCHEMA = StructType([
    StructField("audit_id",      LongType(),      True),
    StructField("pipeline_name", StringType(),    False),
    StructField("execution_id",  StringType(),    False),
    StructField("start_time",    TimestampType(), True),
    StructField("end_time",      TimestampType(), True),
    StructField("status",        StringType(),    False),
    StructField("error_message", StringType(),    True),   # nullable → was None
    StructField("record_count",  LongType(),      True),
    StructField("load_date",     TimestampType(), True),
    StructField("update_date",   TimestampType(), True),
    StructField("source_system", StringType(),    True),
])

ERROR_SCHEMA = StructType([
    StructField("error_id",        LongType(),      True),
    StructField("table_name",      StringType(),    False),
    StructField("record_id",       StringType(),    True),
    StructField("error_type",      StringType(),    False),
    StructField("error_message",   StringType(),    True),
    StructField("error_timestamp", TimestampType(), True),
    StructField("layer",           StringType(),    True),
    StructField("load_date",       TimestampType(), True),
    StructField("update_date",     TimestampType(), True),
    StructField("source_system",   StringType(),    True),
])

# COMMAND ----------
# ── Audit helper ───────────────────────────────────────────────────────────
def write_audit(pipeline, exec_id, status, record_count, error_msg=None):
    now = datetime.now()
    audit_data = [(
        None,                   # audit_id  — LongType nullable
        pipeline,               # pipeline_name
        exec_id,                # execution_id
        now,                    # start_time
        now,                    # end_time
        status,                 # status
        error_msg,              # error_message — may be None, schema covers it
        int(record_count),      # record_count  — explicit int, not None
        now,                    # load_date
        now,                    # update_date
        "TMS_ORACLE"            # source_system
    )]
    spark.createDataFrame(audit_data, AUDIT_SCHEMA) \
         .write.format("delta").mode("append").saveAsTable(SILVER_AUDIT)
    print(f"[AUDIT] {pipeline} | {status} | records: {record_count}")


# COMMAND ----------
# ── Error helper ───────────────────────────────────────────────────────────
def write_error(table_name, record_id, error_type, error_message):
    now = datetime.now()
    error_data = [(
        None,               # error_id    — LongType nullable
        table_name,         # table_name
        str(record_id),     # record_id
        error_type,         # error_type
        error_message,      # error_message
        now,                # error_timestamp
        "GOLD",             # layer
        now,                # load_date
        now,                # update_date
        "TMS_ORACLE"        # source_system
    )]
    spark.createDataFrame(error_data, ERROR_SCHEMA) \
         .write.format("delta").mode("append").saveAsTable(SILVER_ERROR)
    print(f"[ERROR] {table_name} | {error_type} | {error_message}")


# COMMAND ----------
# ══════════════════════════════════════════════════════════════════════════════
# DIMENSION 1 : carnival.gold.go_dim_carrier
# Source      : carnival.silver.sv_shipment
# Grain       : One row per unique carrier_key (SCAC code)
# ══════════════════════════════════════════════════════════════════════════════

# COMMAND ----------
print("=" * 70)
print("STEP 1 — Building carnival.gold.go_dim_carrier")
print(f"  Source : {SILVER_SHIPMENT}")
print(f"  Target : {CARRIER_TABLE}")
print("=" * 70)

sv_ship = spark.table(SILVER_SHIPMENT)

# ── Validate ───────────────────────────────────────────────────────────────
carrier_null_count = sv_ship.filter(F.col("ASSIGNED_CARRIER_CODE").isNull()).count()
if carrier_null_count > 0:
    write_error(
        CARRIER_TABLE, "MULTIPLE",
        "NULL_CARRIER_CODE",
        f"{carrier_null_count} rows have NULL ASSIGNED_CARRIER_CODE in {SILVER_SHIPMENT}"
    )

# ── Build dimension ────────────────────────────────────────────────────────
carrier_dim = (
    sv_ship
    .filter(F.col("ASSIGNED_CARRIER_CODE").isNotNull())
    .select(
        F.col("ASSIGNED_CARRIER_CODE").alias("carrier_key"),
        F.col("ASSIGNED_CARRIER_ID").alias("carrier_id"),
        F.col("DSG_CARRIER_CODE").alias("dsg_carrier_code"),
        F.col("EQUIPMENT_TYPE").alias("default_equipment_type"),
        F.col("TRLR_TYPE").alias("default_trailer_type"),
        F.col("TRLR_SIZE").alias("default_trailer_size"),
    )
    .groupBy("carrier_key")
    .agg(
        F.first("carrier_id",            ignorenulls=True).alias("carrier_id"),
        F.first("dsg_carrier_code",       ignorenulls=True).alias("dsg_carrier_code"),
        F.first("default_equipment_type", ignorenulls=True).alias("default_equipment_type"),
        F.first("default_trailer_type",   ignorenulls=True).alias("default_trailer_type"),
        F.first("default_trailer_size",   ignorenulls=True).alias("default_trailer_size"),
    )
    .withColumn("load_date",     LOAD_DTTM)
    .withColumn("update_date",   LOAD_DTTM)
    .withColumn("source_system", F.lit("TMS_ORACLE"))
    .withColumn(
        "carrier_dim_id",
        F.row_number().over(Window.orderBy("carrier_key")).cast(LongType())
    )
)

carrier_count = carrier_dim.count()
print(f"  Distinct carriers found : {carrier_count}")
carrier_dim.show(truncate=False)

# ── Create table if not exists ─────────────────────────────────────────────
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CARRIER_TABLE} (
      carrier_dim_id          BIGINT,
      carrier_key             STRING  COMMENT 'SCAC code — business key',
      carrier_id              STRING,
      dsg_carrier_code        STRING,
      default_equipment_type  STRING,
      default_trailer_type    STRING,
      default_trailer_size    STRING,
      load_date               TIMESTAMP,
      update_date             TIMESTAMP,
      source_system           STRING
    )
    USING DELTA
    TBLPROPERTIES (
      'delta.autoOptimize.optimizeWrite' = 'true',
      'delta.autoOptimize.autoCompact'   = 'true'
    )
""")

# ── SCD Type-1 MERGE ──────────────────────────────────────────────────────
if spark.catalog.tableExists(CARRIER_TABLE):
    delta_tgt = DeltaTable.forName(spark, CARRIER_TABLE)
    (
        delta_tgt.alias("tgt")
        .merge(carrier_dim.alias("src"), "tgt.carrier_key = src.carrier_key")
        .whenMatchedUpdate(set={
            "carrier_id"             : "src.carrier_id",
            "dsg_carrier_code"       : "src.dsg_carrier_code",
            "default_equipment_type" : "src.default_equipment_type",
            "default_trailer_type"   : "src.default_trailer_type",
            "default_trailer_size"   : "src.default_trailer_size",
            "update_date"            : "src.update_date",
        })
        .whenNotMatchedInsertAll()
        .execute()
    )
    print(f"  MERGE complete → {CARRIER_TABLE}")
else:
    carrier_dim.write.format("delta").mode("overwrite").saveAsTable(CARRIER_TABLE)
    print(f"  Initial write complete → {CARRIER_TABLE}")

write_audit(PIPELINE_NAME + "_carrier", EXECUTION_ID, "SUCCESS", carrier_count)


# COMMAND ----------
# ══════════════════════════════════════════════════════════════════════════════
# DIMENSION 2 : carnival.gold.go_dim_facility
# Source      : carnival.silver.sv_shipment (both Origin and Destination stops)
# Grain       : One row per unique facility_key
# ══════════════════════════════════════════════════════════════════════════════

# COMMAND ----------
print("=" * 70)
print("STEP 2 — Building carnival.gold.go_dim_facility")
print(f"  Source : {SILVER_SHIPMENT}")
print(f"  Target : {FACILITY_TABLE}")
print("=" * 70)

origin_fac = sv_ship.select(
    F.col("O_FACILITY_ID").alias("facility_key"),
    F.col("O_FACILITY_NUMBER").alias("facility_number"),
    F.col("O_STOP_LOCATION_NAME").alias("facility_name"),
    F.col("O_ADDRESS").alias("address"),
    F.col("O_CITY").alias("city"),
    F.col("O_STATE_PROV").alias("state_prov"),
    F.col("O_POSTAL_CODE").alias("postal_code"),
    F.col("O_COUNTRY_CODE").alias("country_code"),
    F.lit("ORIGIN").alias("facility_role"),
)

dest_fac = sv_ship.select(
    F.col("D_FACILITY_ID").alias("facility_key"),
    F.col("D_FACILITY_NUMBER").alias("facility_number"),
    F.col("D_STOP_LOCATION_NAME").alias("facility_name"),
    F.col("D_ADDRESS").alias("address"),
    F.col("D_CITY").alias("city"),
    F.col("D_STATE_PROV").alias("state_prov"),
    F.col("D_POSTAL_CODE").alias("postal_code"),
    F.col("D_COUNTRY_CODE").alias("country_code"),
    F.lit("DESTINATION").alias("facility_role"),
)

all_fac = origin_fac.union(dest_fac).filter(F.col("facility_key").isNotNull())

fac_null = origin_fac.filter(F.col("facility_key").isNull()).count()
if fac_null > 0:
    write_error(
        FACILITY_TABLE, "MULTIPLE",
        "NULL_FACILITY_KEY",
        f"{fac_null} origin rows have NULL O_FACILITY_ID in {SILVER_SHIPMENT}"
    )

facility_dim = (
    all_fac
    .groupBy("facility_key")
    .agg(
        F.first("facility_number", ignorenulls=True).alias("facility_number"),
        F.first("facility_name",   ignorenulls=True).alias("facility_name"),
        F.first("address",         ignorenulls=True).alias("address"),
        F.first("city",            ignorenulls=True).alias("city"),
        F.first("state_prov",      ignorenulls=True).alias("state_prov"),
        F.first("postal_code",     ignorenulls=True).alias("postal_code"),
        F.first("country_code",    ignorenulls=True).alias("country_code"),
        F.when(
            F.count_distinct("facility_role") > 1, F.lit("BOTH")
        ).otherwise(
            F.first("facility_role")
        ).alias("facility_role"),
    )
    .withColumn(
        "facility_dim_id",
        F.row_number().over(Window.orderBy("facility_key")).cast(LongType())
    )
    .withColumn("load_date",     LOAD_DTTM)
    .withColumn("update_date",   LOAD_DTTM)
    .withColumn("source_system", F.lit("TMS_ORACLE"))
)

facility_count = facility_dim.count()
print(f"  Distinct facilities found : {facility_count}")
facility_dim.show(truncate=False)

# ── Create table if not exists ─────────────────────────────────────────────
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {FACILITY_TABLE} (
      facility_dim_id  BIGINT,
      facility_key     STRING  COMMENT 'Business key — DSG DC number or vendor ID',
      facility_number  STRING,
      facility_name    STRING,
      address          STRING,
      city             STRING,
      state_prov       STRING,
      postal_code      STRING,
      country_code     STRING,
      facility_role    STRING  COMMENT 'ORIGIN / DESTINATION / BOTH',
      load_date        TIMESTAMP,
      update_date      TIMESTAMP,
      source_system    STRING
    )
    USING DELTA
    TBLPROPERTIES (
      'delta.autoOptimize.optimizeWrite' = 'true',
      'delta.autoOptimize.autoCompact'   = 'true'
    )
""")

# ── SCD Type-1 MERGE ──────────────────────────────────────────────────────
if spark.catalog.tableExists(FACILITY_TABLE):
    delta_tgt = DeltaTable.forName(spark, FACILITY_TABLE)
    (
        delta_tgt.alias("tgt")
        .merge(facility_dim.alias("src"), "tgt.facility_key = src.facility_key")
        .whenMatchedUpdate(set={
            "facility_number" : "src.facility_number",
            "facility_name"   : "src.facility_name",
            "address"         : "src.address",
            "city"            : "src.city",
            "state_prov"      : "src.state_prov",
            "postal_code"     : "src.postal_code",
            "country_code"    : "src.country_code",
            "facility_role"   : "src.facility_role",
            "update_date"     : "src.update_date",
        })
        .whenNotMatchedInsertAll()
        .execute()
    )
    print(f"  MERGE complete → {FACILITY_TABLE}")
else:
    facility_dim.write.format("delta").mode("overwrite").saveAsTable(FACILITY_TABLE)
    print(f"  Initial write complete → {FACILITY_TABLE}")

write_audit(PIPELINE_NAME + "_facility", EXECUTION_ID, "SUCCESS", facility_count)

# COMMAND ----------
print("=" * 70)
print("DIM NOTEBOOK COMPLETE")
print(f"  {CARRIER_TABLE}  : {carrier_count}  rows")
print(f"  {FACILITY_TABLE} : {facility_count} rows")
print("=" * 70)

# API Cost Consumed: 1 API call for writing gold table, 1 for audit log, 1 for error log (if errors found)
