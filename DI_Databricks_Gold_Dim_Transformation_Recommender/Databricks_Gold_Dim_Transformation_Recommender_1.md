_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Transformation rules and recommendations for Gold Layer Dimension tables based on Store360 Inventory Report conceptual model and constraints.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Databricks Gold Dim Transformation Recommender

This document provides comprehensive transformation rules for Dimension tables in the Gold layer, derived from the Store360 Inventory Report conceptual model, business constraints, and Silver Layer DDL. It ensures data integrity, standardization, and alignment with reporting requirements for analytics and BI.

---

## 1. Transformation Rules for Dimension Tables

### 1.1 Store Dimension

- **Rule Name**: Store Code and Name Standardization
    - **Description**: Ensure Store Code and Store Name are consistently formatted (uppercase, trimmed, unique).
    - **Rationale**: Consistent store identifiers are critical for accurate joins and reporting.
    - **SQL Example**:
      ```sql
      SELECT DISTINCT
        UPPER(TRIM(Store_Code)) AS Store_Code,
        INITCAP(TRIM(Store_Name)) AS Store_Name,
        UPPER(TRIM(Region_Name)) AS Region_Name
      FROM silver.sv_store
      ```

- **Rule Name**: Store-Region Hierarchy Mapping
    - **Description**: Map each Store to its parent Region using Region Name.
    - **Rationale**: Enables roll-up reporting by region.
    - **SQL Example**:
      ```sql
      SELECT
        s.Store_Code,
        s.Store_Name,
        r.Region_Name,
        r.Region_Manager
      FROM silver.sv_store s
      LEFT JOIN silver.sv_region r ON s.Region_Name = r.Region_Name
      ```

### 1.2 Region Dimension

- **Rule Name**: Region Name Standardization
    - **Description**: Ensure Region Name is uppercase and unique.
    - **Rationale**: Prevents duplicate or inconsistent region records.
    - **SQL Example**:
      ```sql
      SELECT DISTINCT UPPER(TRIM(Region_Name)) AS Region_Name, INITCAP(TRIM(Region_Manager)) AS Region_Manager FROM silver.sv_region
      ```

### 1.3 Product Dimension

- **Rule Name**: Product Name and Category Normalization
    - **Description**: Standardize Product Name and Category fields (trim, proper case, unique).
    - **Rationale**: Ensures product records are not duplicated due to case or whitespace differences.
    - **SQL Example**:
      ```sql
      SELECT DISTINCT
        UPPER(TRIM(Product_Name)) AS Product_Name,
        UPPER(TRIM(Product_Category)) AS Product_Category,
        UPPER(TRIM(RFID_Tag)) AS RFID_Tag
      FROM silver.sv_product
      ```

- **Rule Name**: Product-Category Hierarchy Mapping
    - **Description**: Map each Product to its Category.
    - **Rationale**: Enables category-level analysis and reporting.
    - **SQL Example**:
      ```sql
      SELECT
        p.Product_Name,
        c.Category_Name,
        c.Category_Description
      FROM silver.sv_product p
      LEFT JOIN silver.sv_category c ON p.Product_Category = c.Category_Name
      ```

### 1.4 Category Dimension

- **Rule Name**: Category Name Standardization
    - **Description**: Ensure Category Name is uppercase and unique.
    - **Rationale**: Prevents duplicate or inconsistent category records.
    - **SQL Example**:
      ```sql
      SELECT DISTINCT UPPER(TRIM(Category_Name)) AS Category_Name, INITCAP(TRIM(Category_Description)) AS Category_Description FROM silver.sv_category
      ```

### 1.5 Date Dimension

- **Rule Name**: Date Format Standardization
    - **Description**: Ensure all date fields are in YYYY-MM-DD format and unique.
    - **Rationale**: Consistent date formats are required for time-based reporting.
    - **SQL Example**:
      ```sql
      SELECT DISTINCT DATE_FORMAT(Report_Date, 'yyyy-MM-dd') AS Report_Date FROM silver.sv_date
      ```

---

## 2. General Transformation Guidelines

- **Data Type Conversions**: Ensure all percentage fields are numeric (0-100), unit fields are integers, and dates are in standard format (YYYY-MM-DD).
- **Column Derivations**: Derive hierarchy columns (e.g., Region from Store, Category from Product) as per conceptual model relationships.
- **Normalization and Standardization**: Apply upper/lower/proper case, trim whitespace, and enforce uniqueness for business keys.
- **Hierarchy Mapping**: Implement parent-child relationships as per conceptual model (e.g., Store → Region, Product → Category).
- **Referential Integrity**: Ensure all foreign keys reference valid dimension records.
- **Uniqueness Constraints**: Enforce uniqueness on business keys (e.g., Store_Code, Product_Name + Store_Name).

---

## 3. Traceability Matrix

| Transformation Rule                | Source (Conceptual/Constraint/Silver)         | Target (Gold Layer)           |
|-------------------------------------|-----------------------------------------------|-------------------------------|
| Store Code/Name Standardization     | Conceptual 3.1, Constraints 2.1, Silver DDL   | Gold Store Dimension          |
| Store-Region Hierarchy Mapping      | Conceptual 5, Constraints 2.5                 | Gold Store/Region Dimension   |
| Region Name Standardization         | Conceptual 3.2, Constraints 2.1, Silver DDL   | Gold Region Dimension         |
| Product Name/Category Normalization | Conceptual 3.3, Constraints 2.1, Silver DDL   | Gold Product Dimension        |
| Product-Category Hierarchy Mapping  | Conceptual 5, Constraints 2.5                 | Gold Product/Category Dim     |
| Category Name Standardization       | Conceptual 3.4, Constraints 2.1, Silver DDL   | Gold Category Dimension       |
| Date Format Standardization         | Constraints 1.3, 2.3, Silver DDL              | Gold Date Dimension           |

---

## 4. API Cost

apiCost: 0.000000

---

[outputURL](https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Recommender)

pipelineID: 14669
