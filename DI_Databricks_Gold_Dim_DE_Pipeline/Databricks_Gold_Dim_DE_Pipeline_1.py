_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   PySpark pipeline for transforming Silver Layer shipment domain data into Gold Layer dimension tables with audit logging, error handling, and performance optimization.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Dim DE Pipeline: Shipment Domain

'''
This PySpark pipeline reads shipment domain data from the Silver Layer, applies business transformations and cleansing rules to generate Gold Layer dimension tables, logs audit information, handles errors, and optimizes storage for analytics and BI consumption.
'''

# Imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import sha2, concat_ws, col, upper, trim, coalesce, lit, cast, when, current_timestamp
from pyspark.sql.types import DecimalType, StringType, IntegerType

# Initialize Spark session
spark = SparkSession.builder.appName('GoldDimDEPipeline_Shipment').getOrCreate()

# 1. Extract Data from Silver Layer
si_shipment_process = spark.read.format('delta').table('silver.si_shipment_process')
si_shipment_item = spark.read.format('delta').table('silver.si_shipment_item')
si_error_log = spark.read.format('delta').table('silver.si_error_log')
si_audit_log = spark.read.format('delta').table('silver.si_audit_log')

# 2. Apply Business Transformations for Dimension Tables

## Carrier Dimension
go_carrier_dim = (
    si_shipment_process
    .withColumn('carrier_dim_id', sha2(concat_ws('|',
        col('ASSIGNED_CARRIER_ID'),
        col('ASSIGNED_SCNDR_CARRIER_ID'),
        col('BROKER_CARRIER_ID'),
        col('DSG_CARRIER_ID'),
        col('FEASIBLE_CARRIER_ID'),
        col('ASSIGNED_MOT_ID')
    ), 256))
    .withColumn('primary_carrier_name', upper(coalesce(col('ASSIGNED_CARRIER_ID'), lit('UNKNOWN'))))
    .withColumn('secondary_carrier_name', upper(coalesce(col('ASSIGNED_SCNDR_CARRIER_ID'), lit('UNKNOWN'))))
    .withColumn('broker_carrier_name', upper(coalesce(col('BROKER_CARRIER_ID'), lit('UNKNOWN'))))
    .withColumn('designated_carrier_name', upper(coalesce(col('DSG_CARRIER_ID'), lit('UNKNOWN'))))
    .withColumn('feasible_carrier_name', upper(coalesce(col('FEASIBLE_CARRIER_ID'), lit('UNKNOWN'))))
    .withColumn('mode_of_transport', upper(coalesce(col('ASSIGNED_MOT_ID'), lit('UNKNOWN'))))
    .withColumn('load_date', col('load_date'))
    .withColumn('update_date', col('update_date'))
    .withColumn('source_system', col('source_system'))
    .dropDuplicates(['carrier_dim_id'])
)

## Facility Dimension
go_facility_dim = (
    si_shipment_process
    .withColumn('facility_dim_id', sha2(concat_ws('|',
        col('O_FACILITY_ID'),
        col('D_FACILITY_ID')
    ), 256))
    .withColumn('facility_name', upper(trim(coalesce(col('O_FACILITY_ID'), col('D_FACILITY_ID'), lit('UNKNOWN')))))
    .withColumn('address', upper(trim(coalesce(col('O_ADDRESS'), col('D_ADDRESS'), lit('UNKNOWN')))))
    .withColumn('city', upper(trim(coalesce(col('O_CITY'), col('D_CITY'), lit('UNKNOWN')))))
    .withColumn('state', upper(trim(coalesce(col('O_STATE_PROV'), col('D_STATE_PROV'), lit('UNKNOWN')))))
    .withColumn('postal_code', upper(trim(coalesce(col('O_POSTAL_CODE'), col('D_POSTAL_CODE'), lit('UNKNOWN')))))
    .withColumn('country', upper(trim(coalesce(col('O_COUNTRY_CODE'), col('D_COUNTRY_CODE'), lit('UNKNOWN')))))
    .withColumn('load_date', col('load_date'))
    .withColumn('update_date', col('update_date'))
    .withColumn('source_system', col('source_system'))
    .dropDuplicates(['facility_dim_id'])
)

## Route Dimension
go_route_dim = (
    si_shipment_process
    .withColumn('route_dim_id', sha2(concat_ws('|',
        col('ROUTE_REFERENCE'),
        col('DISTANCE'),
        col('DIRECT_DISTANCE'),
        col('OUT_OF_ROUTE_DISTANCE'),
        col('DISTANCE_UOM'),
        col('NUM_STOPS'),
        col('EQUIPMENT_TYPE')
    ), 256))
    .withColumn('route_reference', col('ROUTE_REFERENCE'))
    .withColumn('total_route_distance', coalesce(col('DISTANCE').cast(DecimalType(10,2)), lit(0)))
    .withColumn('direct_distance', coalesce(col('DIRECT_DISTANCE').cast(DecimalType(10,2)), lit(0)))
    .withColumn('out_of_route_distance', coalesce(col('OUT_OF_ROUTE_DISTANCE').cast(DecimalType(10,2)), lit(0)))
    .withColumn('distance_unit_of_measure', upper(coalesce(col('DISTANCE_UOM'), lit('UNKNOWN'))))
    .withColumn('number_of_stops', coalesce(col('NUM_STOPS').cast(IntegerType()), lit(0)))
    .withColumn('equipment_type', upper(coalesce(col('EQUIPMENT_TYPE'), lit('UNKNOWN'))))
    .withColumn('load_date', col('load_date'))
    .withColumn('update_date', col('update_date'))
    .withColumn('source_system', col('source_system'))
    .dropDuplicates(['route_dim_id'])
)

## Billing Dimension
go_billing_dim = (
    si_shipment_process
    .withColumn('billing_dim_id', sha2(concat_ws('|',
        col('BILL_OF_LADING_NUMBER'),
        col('BILLING_METHOD'),
        col('PURCHASE_ORDER'),
        col('BILL_TO_POSTAL_CODE'),
        col('BILL_TO_STATE_PROV'),
        col('SHIPMENT_RECON_DTTM')
    ), 256))
    .withColumn('bill_of_lading_number', coalesce(col('BILL_OF_LADING_NUMBER'), lit('UNKNOWN')))
    .withColumn('billing_method', coalesce(col('BILLING_METHOD').cast(StringType()), lit('UNKNOWN')))
    .withColumn('purchase_order_reference', coalesce(col('PURCHASE_ORDER'), lit('UNKNOWN')))
    .withColumn('bill_to_postal_code', coalesce(col('BILL_TO_POSTAL_CODE'), lit('UNKNOWN')))
    .withColumn('bill_to_state_province', coalesce(col('BILL_TO_STATE_PROV'), lit('UNKNOWN')))
    .withColumn('reconciliation_date', col('SHIPMENT_RECON_DTTM'))
    .withColumn('load_date', col('load_date'))
    .withColumn('update_date', col('update_date'))
    .withColumn('source_system', col('source_system'))
    .dropDuplicates(['billing_dim_id'])
)

## Business Partner Dimension
go_business_partner_dim = (
    si_shipment_process
    .withColumn('business_partner_dim_id', sha2(upper(col('BUSINESS_PARTNER_ID')), 256))
    .withColumn('business_partner_identifier', upper(coalesce(col('BUSINESS_PARTNER_ID'), lit('UNKNOWN'))))
    .withColumn('load_date', col('load_date'))
    .withColumn('update_date', col('update_date'))
    .withColumn('source_system', col('source_system'))
    .dropDuplicates(['business_partner_dim_id'])
)

## User Dimension
go_user_dim = (
    si_shipment_process
    .withColumn('user_dim_id', sha2(concat_ws('|',
        upper(col('CREATOR_ROLE')),
        upper(col('CREATED_SOURCE_TYPE'))
    ), 256))
    .withColumn('creator_role', upper(coalesce(col('CREATOR_ROLE'), lit('UNKNOWN'))))
    .withColumn('creation_source_type', upper(coalesce(col('CREATED_SOURCE_TYPE'), lit('UNKNOWN'))))
    .withColumn('load_date', col('load_date'))
    .withColumn('update_date', col('update_date'))
    .withColumn('source_system', col('source_system'))
    .dropDuplicates(['user_dim_id'])
)

# 3. Audit Logging for Dimension Tables

def log_audit(table_name, status, error_message=None):
    audit_log = spark.createDataFrame([{
        'audit_id': sha2(concat_ws('|', lit(table_name), current_timestamp()), 256),
        'source_table': table_name,
        'load_date': current_timestamp(),
        'processed_by': 'GoldDimDEPipeline_Shipment',
        'processing_time': lit(0.0),
        'status': status,
        'created_at': current_timestamp(),
        'updated_at': current_timestamp(),
        'update_date': current_timestamp(),
        'source_system': lit('Databricks')
    }])
    audit_log.write.format('delta').mode('append').saveAsTable('gold.si_audit_log')
    if error_message:
        error_log = spark.createDataFrame([{
            'error_id': sha2(concat_ws('|', lit(table_name), current_timestamp()), 256),
            'source_table': table_name,
            'error_type': 'TransformationError',
            'error_message': error_message,
            'error_timestamp': current_timestamp(),
            'record_reference': '',
            'created_at': current_timestamp(),
            'updated_at': current_timestamp(),
            'load_date': current_timestamp(),
            'update_date': current_timestamp(),
            'source_system': lit('Databricks')
        }])
        error_log.write.format('delta').mode('append').saveAsTable('gold.si_error_log')

# 4. Error Record in Dimension Table

def handle_errors(df, table_name):
    error_df = df.filter(
        (col('carrier_dim_id').isNull()) | 
        (col('facility_dim_id').isNull()) |
        (col('route_dim_id').isNull()) |
        (col('billing_dim_id').isNull()) |
        (col('business_partner_dim_id').isNull()) |
        (col('user_dim_id').isNull())
    )
    if error_df.count() > 0:
        error_df.withColumn('error_type', lit('NullSurrogateKey')) \
            .withColumn('error_message', lit('Null surrogate key detected')) \
            .withColumn('error_timestamp', current_timestamp()) \
            .withColumn('record_reference', lit('')) \
            .withColumn('created_at', current_timestamp()) \
            .withColumn('updated_at', current_timestamp()) \
            .withColumn('load_date', current_timestamp()) \
            .withColumn('update_date', current_timestamp()) \
            .withColumn('source_system', lit('Databricks')) \
            .write.format('delta').mode('append').saveAsTable('gold.si_error_log')
        log_audit(table_name, 'Failure', 'Null surrogate key detected')
    else:
        log_audit(table_name, 'Success')

# 5. Optimize Performance for Dimension Tables

def optimize_table(table_name, partition_col=None):
    spark.sql(f