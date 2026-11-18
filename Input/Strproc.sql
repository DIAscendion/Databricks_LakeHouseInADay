-- Stored Procedure: Bronze -> Silver load for Superstore-style orders
-- This script creates supporting objects (log table) and a stored procedure
-- to load from BRONZE.ORDERS_RAW into SILVER.CUSTOMERS, SILVER.PRODUCTS,
-- SILVER.ORDERS, and SILVER.ORDERS_REJECTED.

USE DATABASE ANALYTICS_DB;

CREATE SCHEMA IF NOT EXISTS UTIL;

-- =====================================================================
-- 1. AUDIT / LOGGING TABLE
-- =====================================================================
CREATE OR REPLACE TABLE UTIL.ETL_RUN_LOG (
    RUN_ID              NUMBER(38,0)        IDENTITY,
    PROCESS_NAME        VARCHAR(200),
    BRONZE_TABLE        VARCHAR(200),
    SILVER_TABLE        VARCHAR(200),
    RUN_TYPE            VARCHAR(50),        -- FULL / INCREMENTAL
    START_TS            TIMESTAMP_NTZ,
    END_TS              TIMESTAMP_NTZ,
    STATUS              VARCHAR(50),        -- STARTED / SUCCESS / FAILED
    ROWS_READ           NUMBER(38,0),
    ROWS_INSERTED       NUMBER(38,0),
    ROWS_REJECTED       NUMBER(38,0),
    INCREMENTAL_FILTER  VARCHAR(500),
    ERROR_MESSAGE       STRING,
    ERROR_STACK         STRING,
    CREATED_BY          VARCHAR(100)        DEFAULT CURRENT_USER(),
    CREATED_TS          TIMESTAMP_NTZ       DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 2. STORED PROCEDURE: BRONZE.ORDERS_RAW -> SILVER.*
-- =====================================================================
-- Name: SP_LOAD_SILVER_ORDERS
-- Parameters:
--   P_RUN_TYPE          : 'FULL' or 'INCREMENTAL'
--   P_SINCE_TS          : for INCREMENTAL, only rows with _LOAD_TS > P_SINCE_TS are considered
-- Behavior:
--   * Validates that source and target tables exist with expected columns
--   * Loads/merges into SILVER.CUSTOMERS and SILVER.PRODUCTS (upsert semantics)
--   * Inserts valid rows into SILVER.ORDERS, de-duplicating by ROW_ID (latest _LOAD_TS wins)
--   * Routes invalid rows into SILVER.ORDERS_REJECTED with a REJECT_REASON
--   * Logs execution status and metrics into UTIL.ETL_RUN_LOG

CREATE OR REPLACE PROCEDURE UTIL.SP_LOAD_SILVER_ORDERS(
    P_RUN_TYPE STRING,
    P_SINCE_TS TIMESTAMP_NTZ
)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    V_PROCESS_NAME      STRING      := 'SP_LOAD_SILVER_ORDERS';
    V_RUN_TYPE          STRING      := IFF(UPPER(P_RUN_TYPE) IN ('FULL','INCREMENTAL'), UPPER(P_RUN_TYPE), 'FULL');
    V_BRONZE_TABLE      STRING      := 'BRONZE.ORDERS_RAW';
    V_SILVER_TABLE      STRING      := 'SILVER.ORDERS';
    V_START_TS          TIMESTAMP_NTZ := CURRENT_TIMESTAMP();
    V_END_TS            TIMESTAMP_NTZ;
    V_STATUS            STRING;
    V_ROWS_READ         NUMBER(38,0) := 0;
    V_ROWS_INSERTED     NUMBER(38,0) := 0;
    V_ROWS_REJECTED     NUMBER(38,0) := 0;
    V_INCREMENTAL_FILTER STRING     := NULL;
    V_ERROR_MESSAGE     STRING;
    V_ERROR_STACK       STRING;
    V_RUN_ID            NUMBER(38,0);

    V_EXPECTED_SRC_COLS ARRAY := ARRAY_CONSTRUCT(
        'ROW_ID','ORDER_ID','ORDER_DATE','SHIP_DATE','SHIP_MODE','CUSTOMER_ID','CUSTOMER_NAME',
        'SEGMENT','COUNTRY','CITY','STATE','POSTAL_CODE','REGION','PRODUCT_ID','CATEGORY',
        'SUB_CATEGORY','PRODUCT_NAME','SALES','QUANTITY','DISCOUNT','PROFIT','_SOURCE_FILE',
        '_SOURCE_ROW_NUM','_LOAD_TS'
    );

    V_EXPECTED_TGT_ORDER_COLS ARRAY := ARRAY_CONSTRUCT(
        'ROW_ID','ORDER_ID','ORDER_DATE','SHIP_DATE','SHIP_MODE','CUSTOMER_ID','PRODUCT_ID',
        'SALES','QUANTITY','DISCOUNT','PROFIT','_SOURCE_FILE','_BRONZE_LOAD_TS','_CREATED_TS','_UPDATED_TS'
    );

    V_SRC_MISSING_COLS  STRING;
    V_TGT_MISSING_COLS  STRING;
BEGIN
    ----------------------------------------------------------------------
    -- 1. INITIAL LOG ENTRY (STATUS = STARTED)
    ----------------------------------------------------------------------
    INSERT INTO UTIL.ETL_RUN_LOG (
        PROCESS_NAME, BRONZE_TABLE, SILVER_TABLE, RUN_TYPE,
        START_TS, STATUS, ROWS_READ, ROWS_INSERTED, ROWS_REJECTED,
        INCREMENTAL_FILTER
    )
    VALUES (
        V_PROCESS_NAME, V_BRONZE_TABLE, V_SILVER_TABLE, V_RUN_TYPE,
        V_START_TS, 'STARTED', 0, 0, 0,
        IFF(V_RUN_TYPE = 'INCREMENTAL', TO_CHAR(P_SINCE_TS), NULL)
    );

    SELECT MAX(RUN_ID) INTO :V_RUN_ID
    FROM UTIL.ETL_RUN_LOG
    WHERE PROCESS_NAME = V_PROCESS_NAME
      AND START_TS = V_START_TS;

    ----------------------------------------------------------------------
    -- 2. BASIC SCHEMA VALIDATION (REQUIRED COLUMNS EXIST)
    ----------------------------------------------------------------------
    -- Validate Bronze.ORDERS_RAW
    V_SRC_MISSING_COLS := (
        SELECT LISTAGG(COL, ',')
        FROM (
            SELECT VALUE::STRING AS COL
            FROM LATERAL FLATTEN(INPUT => V_EXPECTED_SRC_COLS)
            QUALIFY NOT EXISTS (
                SELECT 1
                FROM INFORMATION_SCHEMA.COLUMNS C
                WHERE C.TABLE_SCHEMA = 'BRONZE'
                  AND C.TABLE_NAME   = 'ORDERS_RAW'
                  AND UPPER(C.COLUMN_NAME) = UPPER(VALUE::STRING)
            )
        )
    );

    IF V_SRC_MISSING_COLS IS NOT NULL THEN
        V_STATUS := 'FAILED';
        V_ERROR_MESSAGE := 'Missing expected columns in BRONZE.ORDERS_RAW: ' || V_SRC_MISSING_COLS;
        V_ERROR_STACK   := NULL;
        V_END_TS := CURRENT_TIMESTAMP();

        UPDATE UTIL.ETL_RUN_LOG
        SET STATUS        = V_STATUS,
            END_TS        = V_END_TS,
            ERROR_MESSAGE = V_ERROR_MESSAGE
        WHERE RUN_ID = V_RUN_ID;

        RETURN 'FAILURE: ' || V_ERROR_MESSAGE;
    END IF;

    -- Validate SILVER.ORDERS
    V_TGT_MISSING_COLS := (
        SELECT LISTAGG(COL, ',')
        FROM (
            SELECT VALUE::STRING AS COL
            FROM LATERAL FLATTEN(INPUT => V_EXPECTED_TGT_ORDER_COLS)
            QUALIFY NOT EXISTS (
                SELECT 1
                FROM INFORMATION_SCHEMA.COLUMNS C
                WHERE C.TABLE_SCHEMA = 'SILVER'
                  AND C.TABLE_NAME   = 'ORDERS'
                  AND UPPER(C.COLUMN_NAME) = UPPER(VALUE::STRING)
            )
        )
    );

    IF V_TGT_MISSING_COLS IS NOT NULL THEN
        V_STATUS := 'FAILED';
        V_ERROR_MESSAGE := 'Missing expected columns in SILVER.ORDERS: ' || V_TGT_MISSING_COLS;
        V_ERROR_STACK   := NULL;
        V_END_TS := CURRENT_TIMESTAMP();

        UPDATE UTIL.ETL_RUN_LOG
        SET STATUS        = V_STATUS,
            END_TS        = V_END_TS,
            ERROR_MESSAGE = V_ERROR_MESSAGE
        WHERE RUN_ID = V_RUN_ID;

        RETURN 'FAILURE: ' || V_ERROR_MESSAGE;
    END IF;

    ----------------------------------------------------------------------
    -- 3. DETERMINE INCREMENTAL FILTER
    ----------------------------------------------------------------------
    IF V_RUN_TYPE = 'INCREMENTAL' AND P_SINCE_TS IS NOT NULL THEN
        V_INCREMENTAL_FILTER := '_LOAD_TS > ''' || TO_CHAR(P_SINCE_TS, 'YYYY-MM-DD HH24:MI:SS.FF3') || '''';
    ELSE
        V_INCREMENTAL_FILTER := NULL; -- FULL reload
    END IF;

    ----------------------------------------------------------------------
    -- 4. CREATE TEMPORARY STAGING SET WITH TYPED COLUMNS
    --    - Apply trimming and TRY_TO_* casts
    --    - Deduplicate by ROW_ID, latest _LOAD_TS wins
    ----------------------------------------------------------------------
    CREATE OR REPLACE TEMPORARY TABLE TMP_ORDERS_TYPED AS
    SELECT
        TRY_TO_NUMBER(ROW_ID)                                       AS ROW_ID_NUM,
        TRIM(ORDER_ID)                                              AS ORDER_ID,
        TRY_TO_DATE(ORDER_DATE, 'MM/DD/YYYY')                       AS ORDER_DATE,
        TRY_TO_DATE(SHIP_DATE,  'MM/DD/YYYY')                       AS SHIP_DATE,
        TRIM(SHIP_MODE)                                             AS SHIP_MODE,
        TRIM(CUSTOMER_ID)                                           AS CUSTOMER_ID,
        TRIM(CUSTOMER_NAME)                                         AS CUSTOMER_NAME,
        TRIM(SEGMENT)                                               AS SEGMENT,
        TRIM(COUNTRY)                                               AS COUNTRY,
        TRIM(CITY)                                                  AS CITY,
        TRIM(STATE)                                                 AS STATE,
        TRIM(POSTAL_CODE)                                           AS POSTAL_CODE,
        TRIM(REGION)                                                AS REGION,
        TRIM(PRODUCT_ID)                                            AS PRODUCT_ID,
        TRIM(CATEGORY)                                              AS CATEGORY,
        TRIM(SUB_CATEGORY)                                          AS SUB_CATEGORY,
        TRIM(PRODUCT_NAME)                                          AS PRODUCT_NAME,
        TRY_TO_DECIMAL(SALES, 18, 2)                                AS SALES_NUM,
        TRY_TO_NUMBER(QUANTITY)                                     AS QUANTITY_NUM,
        TRY_TO_DECIMAL(DISCOUNT, 5, 2)                              AS DISCOUNT_NUM,
        TRY_TO_DECIMAL(PROFIT, 18, 2)                               AS PROFIT_NUM,
        _SOURCE_FILE,
        _LOAD_TS,
        _SOURCE_ROW_NUM,
        ROW_NUMBER() OVER (PARTITION BY ROW_ID ORDER BY _LOAD_TS DESC) AS RN
    FROM BRONZE.ORDERS_RAW
    WHERE (V_INCREMENTAL_FILTER IS NULL OR _LOAD_TS > P_SINCE_TS);

    -- Row count from Bronze (after optional incremental filter)
    SELECT COUNT(*) INTO :V_ROWS_READ FROM TMP_ORDERS_TYPED;

    ----------------------------------------------------------------------
    -- 5. SPLIT INTO VALID vs INVALID ROWS FOR SILVER.ORDERS
    --    Validation rules:
    --    * ROW_ID_NUM IS NOT NULL
    --    * ORDER_ID IS NOT NULL
    --    * ORDER_DATE IS NOT NULL
    --    * CUSTOMER_ID IS NOT NULL
    --    * PRODUCT_ID IS NOT NULL
    --    * RN = 1 (latest record per ROW_ID)
    ----------------------------------------------------------------------
    CREATE OR REPLACE TEMPORARY TABLE TMP_ORDERS_VALID AS
    SELECT *
    FROM TMP_ORDERS_TYPED
    WHERE RN = 1
      AND ROW_ID_NUM IS NOT NULL
      AND ORDER_ID IS NOT NULL
      AND ORDER_DATE IS NOT NULL
      AND CUSTOMER_ID IS NOT NULL
      AND PRODUCT_ID IS NOT NULL;

    CREATE OR REPLACE TEMPORARY TABLE TMP_ORDERS_INVALID AS
    SELECT T.*,
           ARRAY_TO_STRING(
               ARRAY_CONSTRUCT_COMPACT(
                   IFF(RN <> 1, 'Duplicate ROW_ID (not latest _LOAD_TS)', NULL),
                   IFF(ROW_ID_NUM IS NULL, 'ROW_ID invalid or missing', NULL),
                   IFF(ORDER_ID IS NULL, 'ORDER_ID missing', NULL),
                   IFF(ORDER_DATE IS NULL, 'ORDER_DATE invalid or missing', NULL),
                   IFF(CUSTOMER_ID IS NULL, 'CUSTOMER_ID missing', NULL),
                   IFF(PRODUCT_ID IS NULL, 'PRODUCT_ID missing', NULL)
               ),
               '; '
           ) AS REJECT_REASON
    FROM TMP_ORDERS_TYPED T
    WHERE RN <> 1
       OR ROW_ID_NUM IS NULL
       OR ORDER_ID IS NULL
       OR ORDER_DATE IS NULL
       OR CUSTOMER_ID IS NULL
       OR PRODUCT_ID IS NULL;

    ----------------------------------------------------------------------
    -- 6. LOAD / UPSERT SILVER.CUSTOMERS
    --    Business key: CUSTOMER_ID
    ----------------------------------------------------------------------
    MERGE INTO SILVER.CUSTOMERS T
    USING (
        SELECT DISTINCT
            CUSTOMER_ID,
            CUSTOMER_NAME,
            SEGMENT,
            COUNTRY,
            CITY,
            STATE,
            POSTAL_CODE,
            REGION
        FROM TMP_ORDERS_VALID
    ) S
      ON T.CUSTOMER_ID = S.CUSTOMER_ID
    WHEN MATCHED THEN UPDATE SET
        T.CUSTOMER_NAME = S.CUSTOMER_NAME,
        T.SEGMENT       = S.SEGMENT,
        T.COUNTRY       = S.COUNTRY,
        T.CITY          = S.CITY,
        T.STATE         = S.STATE,
        T.POSTAL_CODE   = S.POSTAL_CODE,
        T.REGION        = S.REGION,
        T._UPDATED_TS   = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        CUSTOMER_ID, CUSTOMER_NAME, SEGMENT, COUNTRY, CITY, STATE, POSTAL_CODE, REGION
    ) VALUES (
        S.CUSTOMER_ID, S.CUSTOMER_NAME, S.SEGMENT, S.COUNTRY, S.CITY, S.STATE, S.POSTAL_CODE, S.REGION
    );

    ----------------------------------------------------------------------
    -- 7. LOAD / UPSERT SILVER.PRODUCTS
    --    Business key: PRODUCT_ID
    ----------------------------------------------------------------------
    MERGE INTO SILVER.PRODUCTS T
    USING (
        SELECT DISTINCT
            PRODUCT_ID,
            CATEGORY,
            SUB_CATEGORY,
            PRODUCT_NAME
        FROM TMP_ORDERS_VALID
    ) S
      ON T.PRODUCT_ID = S.PRODUCT_ID
    WHEN MATCHED THEN UPDATE SET
        T.CATEGORY      = S.CATEGORY,
        T.SUB_CATEGORY  = S.SUB_CATEGORY,
        T.PRODUCT_NAME  = S.PRODUCT_NAME,
        T._UPDATED_TS   = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        PRODUCT_ID, CATEGORY, SUB_CATEGORY, PRODUCT_NAME
    ) VALUES (
        S.PRODUCT_ID, S.CATEGORY, S.SUB_CATEGORY, S.PRODUCT_NAME
    );

    ----------------------------------------------------------------------
    -- 8. IDempotent load into SILVER.ORDERS
    --    Strategy: MERGE on ROW_ID (PK). For FULL loads this will update
    --    existing rows; for INCREMENTAL, only changed/new ROW_IDs are affected.
    ----------------------------------------------------------------------
    MERGE INTO SILVER.ORDERS T
    USING (
        SELECT
            ROW_ID_NUM          AS ROW_ID,
            ORDER_ID,
            ORDER_DATE,
            SHIP_DATE,
            SHIP_MODE,
            CUSTOMER_ID,
            PRODUCT_ID,
            SALES_NUM           AS SALES,
            QUANTITY_NUM        AS QUANTITY,
            DISCOUNT_NUM        AS DISCOUNT,
            PROFIT_NUM          AS PROFIT,
            _SOURCE_FILE,
            _LOAD_TS            AS _BRONZE_LOAD_TS
        FROM TMP_ORDERS_VALID
    ) S
      ON T.ROW_ID = S.ROW_ID
    WHEN MATCHED THEN UPDATE SET
        T.ORDER_ID        = S.ORDER_ID,
        T.ORDER_DATE      = S.ORDER_DATE,
        T.SHIP_DATE       = S.SHIP_DATE,
        T.SHIP_MODE       = S.SHIP_MODE,
        T.CUSTOMER_ID     = S.CUSTOMER_ID,
        T.PRODUCT_ID      = S.PRODUCT_ID,
        T.SALES           = S.SALES,
        T.QUANTITY        = S.QUANTITY,
        T.DISCOUNT        = S.DISCOUNT,
        T.PROFIT          = S.PROFIT,
        T._SOURCE_FILE    = S._SOURCE_FILE,
        T._BRONZE_LOAD_TS = S._BRONZE_LOAD_TS,
        T._UPDATED_TS     = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        ROW_ID, ORDER_ID, ORDER_DATE, SHIP_DATE, SHIP_MODE,
        CUSTOMER_ID, PRODUCT_ID, SALES, QUANTITY, DISCOUNT, PROFIT,
        _SOURCE_FILE, _BRONZE_LOAD_TS
    ) VALUES (
        S.ROW_ID, S.ORDER_ID, S.ORDER_DATE, S.SHIP_DATE, S.SHIP_MODE,
        S.CUSTOMER_ID, S.PRODUCT_ID, S.SALES, S.QUANTITY, S.DISCOUNT, S.PROFIT,
        S._SOURCE_FILE, S._BRONZE_LOAD_TS
    );

    -- Rows successfully present in SILVER.ORDERS from this run
    SELECT COUNT(*) INTO :V_ROWS_INSERTED
    FROM SILVER.ORDERS O
    WHERE EXISTS (
        SELECT 1
        FROM TMP_ORDERS_VALID V
        WHERE V.ROW_ID_NUM = O.ROW_ID
          AND V._LOAD_TS   = O._BRONZE_LOAD_TS
    );

    ----------------------------------------------------------------------
    -- 9. INSERT INVALID ROWS INTO SILVER.ORDERS_REJECTED
    ----------------------------------------------------------------------
    INSERT INTO SILVER.ORDERS_REJECTED (
        ROW_ID, ORDER_ID, REJECT_REASON, RAW_RECORD
    )
    SELECT
        ROW_ID,
        ORDER_ID,
        REJECT_REASON,
        OBJECT_CONSTRUCT(
            'ROW_ID', ROW_ID,
            'ORDER_ID', ORDER_ID,
            'ORDER_DATE', ORDER_DATE,
            'SHIP_DATE', SHIP_DATE,
            'SHIP_MODE', SHIP_MODE,
            'CUSTOMER_ID', CUSTOMER_ID,
            'CUSTOMER_NAME', CUSTOMER_NAME,
            'SEGMENT', SEGMENT,
            'COUNTRY', COUNTRY,
            'CITY', CITY,
            'STATE', STATE,
            'POSTAL_CODE', POSTAL_CODE,
            'REGION', REGION,
            'PRODUCT_ID', PRODUCT_ID,
            'CATEGORY', CATEGORY,
            'SUB_CATEGORY', SUB_CATEGORY,
            'PRODUCT_NAME', PRODUCT_NAME,
            'SALES', SALES_NUM,
            'QUANTITY', QUANTITY_NUM,
            'DISCOUNT', DISCOUNT_NUM,
            'PROFIT', PROFIT_NUM,
            '_SOURCE_FILE', _SOURCE_FILE,
            '_LOAD_TS', _LOAD_TS,
            '_SOURCE_ROW_NUM', _SOURCE_ROW_NUM
        ) AS RAW_RECORD
    FROM TMP_ORDERS_INVALID;

    SELECT COUNT(*) INTO :V_ROWS_REJECTED FROM TMP_ORDERS_INVALID;

    ----------------------------------------------------------------------
    -- 10. FINALIZE LOG (SUCCESS)
    ----------------------------------------------------------------------
    V_STATUS := 'SUCCESS';
    V_END_TS := CURRENT_TIMESTAMP();

    UPDATE UTIL.ETL_RUN_LOG
    SET STATUS         = V_STATUS,
        END_TS         = V_END_TS,
        ROWS_READ      = V_ROWS_READ,
        ROWS_INSERTED  = V_ROWS_INSERTED,
        ROWS_REJECTED  = V_ROWS_REJECTED,
        INCREMENTAL_FILTER = V_INCREMENTAL_FILTER
    WHERE RUN_ID = V_RUN_ID;

    RETURN 'SUCCESS: Loaded Silver orders. Rows read=' || V_ROWS_READ || ', inserted/updated=' || V_ROWS_INSERTED || ', rejected=' || V_ROWS_REJECTED;

EXCEPTION
    WHEN OTHER THEN
        V_STATUS        := 'FAILED';
        V_ERROR_MESSAGE := ERROR_MESSAGE();
        V_ERROR_STACK   := ERROR_STACK_TRACE();
        V_END_TS        := CURRENT_TIMESTAMP();

        UPDATE UTIL.ETL_RUN_LOG
        SET STATUS        = V_STATUS,
            END_TS        = V_END_TS,
            ROWS_READ     = V_ROWS_READ,
            ROWS_INSERTED = V_ROWS_INSERTED,
            ROWS_REJECTED = V_ROWS_REJECTED,
            ERROR_MESSAGE = V_ERROR_MESSAGE,
            ERROR_STACK   = V_ERROR_STACK,
            INCREMENTAL_FILTER = V_INCREMENTAL_FILTER
        WHERE RUN_ID = V_RUN_ID;

        RETURN 'FAILURE: ' || V_ERROR_MESSAGE;
END;
$$;

-- =====================================================================
-- 3. MAPPING SUMMARY (BRONZE -> SILVER)
-- =====================================================================
-- BRONZE.ORDERS_RAW -> SILVER.CUSTOMERS
--   CUSTOMER_ID      (TRIM)                    -> CUSTOMERS.CUSTOMER_ID (PK)
--   CUSTOMER_NAME    (TRIM)                    -> CUSTOMERS.CUSTOMER_NAME
--   SEGMENT          (TRIM)                    -> CUSTOMERS.SEGMENT
--   COUNTRY          (TRIM)                    -> CUSTOMERS.COUNTRY
--   CITY             (TRIM)                    -> CUSTOMERS.CITY
--   STATE            (TRIM)                    -> CUSTOMERS.STATE
--   POSTAL_CODE      (TRIM)                    -> CUSTOMERS.POSTAL_CODE
--   REGION           (TRIM)                    -> CUSTOMERS.REGION
--   _CREATED_TS / _UPDATED_TS                  -> managed automatically via DEFAULT and UPDATE

-- BRONZE.ORDERS_RAW -> SILVER.PRODUCTS
--   PRODUCT_ID       (TRIM)                    -> PRODUCTS.PRODUCT_ID (PK)
--   CATEGORY         (TRIM)                    -> PRODUCTS.CATEGORY
--   SUB_CATEGORY     (TRIM)                    -> PRODUCTS.SUB_CATEGORY
--   PRODUCT_NAME     (TRIM)                    -> PRODUCTS.PRODUCT_NAME
--   _CREATED_TS / _UPDATED_TS                  -> managed automatically via DEFAULT and UPDATE

-- BRONZE.ORDERS_RAW -> SILVER.ORDERS
--   ROW_ID           (VARCHAR)  -> ROW_ID NUMBER(38,0)  via TRY_TO_NUMBER(ROW_ID)
--   ORDER_ID         (TRIM)     -> ORDER_ID VARCHAR(30)
--   ORDER_DATE       (VARCHAR)  -> ORDER_DATE DATE via TRY_TO_DATE(ORDER_DATE,'MM/DD/YYYY')
--   SHIP_DATE        (VARCHAR)  -> SHIP_DATE DATE via TRY_TO_DATE(SHIP_DATE,'MM/DD/YYYY')
--   SHIP_MODE        (TRIM)     -> SHIP_MODE VARCHAR(50)
--   CUSTOMER_ID      (TRIM)     -> CUSTOMER_ID VARCHAR(20)
--   PRODUCT_ID       (TRIM)     -> PRODUCT_ID VARCHAR(30)
--   SALES            (VARCHAR)  -> SALES NUMBER(18,2) via TRY_TO_DECIMAL(SALES,18,2)
--   QUANTITY         (VARCHAR)  -> QUANTITY NUMBER(10,0) via TRY_TO_NUMBER(QUANTITY)
--   DISCOUNT         (VARCHAR)  -> DISCOUNT NUMBER(5,2) via TRY_TO_DECIMAL(DISCOUNT,5,2)
--   PROFIT           (VARCHAR)  -> PROFIT NUMBER(18,2) via TRY_TO_DECIMAL(PROFIT,18,2)
--   _SOURCE_FILE                  -> _SOURCE_FILE
--   _LOAD_TS                      -> _BRONZE_LOAD_TS
--   _CREATED_TS / _UPDATED_TS     -> managed automatically via DEFAULT and UPDATE
--   Deduplication: ROW_NUMBER() OVER (PARTITION BY ROW_ID ORDER BY _LOAD_TS DESC) = 1

-- BRONZE.ORDERS_RAW -> SILVER.ORDERS_REJECTED
--   Any row failing:
--      * ROW_ID cannot be converted to NUMBER
--      * ORDER_ID is NULL
--      * ORDER_DATE cannot be parsed or is NULL
--      * CUSTOMER_ID is NULL
--      * PRODUCT_ID is NULL
--      * RN <> 1 (not the latest per ROW_ID)
--   is inserted into SILVER.ORDERS_REJECTED with:
--      - REJECT_REASON (semicolon-separated reasons)
--      - RAW_RECORD    (OBJECT_CONSTRUCT of the typed fields + metadata)

-- =====================================================================
-- 4. AUDIT / LOGGING BEHAVIOR
-- =====================================================================
-- UTIL.ETL_RUN_LOG captures:
--   RUN_ID           : Surrogate key for each run
--   PROCESS_NAME     : 'SP_LOAD_SILVER_ORDERS'
--   BRONZE_TABLE     : 'BRONZE.ORDERS_RAW'
--   SILVER_TABLE     : 'SILVER.ORDERS'
--   RUN_TYPE         : 'FULL' or 'INCREMENTAL'
--   START_TS / END_TS: Run timestamps
--   STATUS           : STARTED / SUCCESS / FAILED
--   ROWS_READ        : Count from TMP_ORDERS_TYPED
--   ROWS_INSERTED    : Count of rows inserted/updated in SILVER.ORDERS for this run
--   ROWS_REJECTED    : Count of rows inserted into SILVER.ORDERS_REJECTED
--   INCREMENTAL_FILTER: Textual representation of _LOAD_TS filter (for INCREMENTAL runs)
--   ERROR_MESSAGE    : Populated on failure (from ERROR_MESSAGE())
--   ERROR_STACK      : Populated on failure (from ERROR_STACK_TRACE())

-- Error handling:
--   * Any unhandled exception in the procedure is caught by the EXCEPTION block.
--   * The log row is updated with FAILED status, error message, and stack trace.
--   * The procedure returns a FAILURE message string.

-- Idempotency:
--   * SILVER.ORDERS is loaded via MERGE on primary key ROW_ID.
--   * Re-running for the same data will update existing rows rather than duplicate.
--   * Deduplication in staging ensures only the latest _LOAD_TS per ROW_ID is used.

-- Incremental loads:
--   * When P_RUN_TYPE = 'INCREMENTAL' and P_SINCE_TS is provided,
--     only BRONZE.ORDERS_RAW rows with _LOAD_TS > P_SINCE_TS are considered.

-- =====================================================================
-- 5. MIGRATION GUIDE / HOW TO USE
-- =====================================================================
-- 1) Deploy objects
--    - Run this entire script in Snowflake (with appropriate role that can
--      create schemas, tables, and procedures in ANALYTICS_DB).
--
-- 2) Grant privileges
--    GRANT USAGE ON DATABASE ANALYTICS_DB TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT USAGE ON SCHEMA ANALYTICS_DB.BRONZE TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT USAGE ON SCHEMA ANALYTICS_DB.SILVER TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT USAGE ON SCHEMA ANALYTICS_DB.UTIL   TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT SELECT ON TABLE BRONZE.ORDERS_RAW TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT INSERT, UPDATE, SELECT ON TABLE SILVER.CUSTOMERS TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT INSERT, UPDATE, SELECT ON TABLE SILVER.PRODUCTS TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT INSERT, UPDATE, SELECT ON TABLE SILVER.ORDERS TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT INSERT, SELECT ON TABLE SILVER.ORDERS_REJECTED TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT INSERT, UPDATE, SELECT ON TABLE UTIL.ETL_RUN_LOG TO ROLE ANALYTICS_ETL_ROLE;
--    GRANT USAGE, EXECUTE ON PROCEDURE UTIL.SP_LOAD_SILVER_ORDERS(STRING, TIMESTAMP_NTZ)
--      TO ROLE ANALYTICS_ETL_ROLE;
--
-- 3) Run a FULL load manually
--    CALL UTIL.SP_LOAD_SILVER_ORDERS('FULL', NULL);
--
-- 4) Run an INCREMENTAL load
--    -- Example: load everything newer than 2024-01-01
--    CALL UTIL.SP_LOAD_SILVER_ORDERS('INCREMENTAL', '2024-01-01'::TIMESTAMP_NTZ);
--
-- 5) Schedule via Snowflake Task (example: hourly incremental load)
--    CREATE OR REPLACE TASK UTIL.TASK_LOAD_SILVER_ORDERS
--      WAREHOUSE = YOUR_WH
--      SCHEDULE  = 'USING CRON 0 * * * * America/Los_Angeles'
--      COMMENT   = 'Hourly incremental load from BRONZE.ORDERS_RAW to SILVER.*'
--    AS
--      CALL UTIL.SP_LOAD_SILVER_ORDERS('INCREMENTAL', DATEADD('HOUR', -1, CURRENT_TIMESTAMP()));
--
--    ALTER TASK UTIL.TASK_LOAD_SILVER_ORDERS RESUME;
--
-- 6) Monitoring
--    - Inspect UTIL.ETL_RUN_LOG for run history and errors:
--        SELECT *
--        FROM UTIL.ETL_RUN_LOG
--        ORDER BY RUN_ID DESC;
--
--    - Inspect SILVER.ORDERS_REJECTED for data quality issues:
--        SELECT * FROM SILVER.ORDERS_REJECTED ORDER BY _REJECTED_TS DESC;