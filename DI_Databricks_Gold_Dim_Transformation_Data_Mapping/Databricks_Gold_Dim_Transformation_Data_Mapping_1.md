_____________________________________________
## *Author*: AAVA
## *Created on*:   
## *Description*:   Detailed data mapping for Gold Layer Dimension tables, including transformations, validations, and cleansing rules from Silver Layer, for TMS/Store360 Inventory analytics.
## *Version*: 1 
## *Updated on*: 
_____________________________________________

# Overview

This document provides a comprehensive data mapping for Dimension tables in the Gold Layer, based on the Silver Layer physical model and transformation recommendations. It details attribute-level transformations, validation, and cleansing logic to ensure high data quality, consistency, and business relevance for analytics and reporting. All rules are compatible with PySpark and Databricks best practices.

---

# Data Mapping for Dimension Tables

| Target Layer | Target Table         | Target Field         | Source Layer | Source Table         | Source Field         | Validation Rule                                                                 | Transformation Rule                                                                                       |
|--------------|---------------------|----------------------|--------------|---------------------|----------------------|---------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Gold         | dim_store           | store_code           | Silver       | sv_store            | Store_Code           | Must be unique, not null, uppercase, trimmed                                    | UPPER(TRIM(Store_Code))                                                                                  |
| Gold         | dim_store           | store_name           | Silver       | sv_store            | Store_Name           | Not null, proper case, trimmed                                                  | INITCAP(TRIM(Store_Name))                                                                                |
| Gold         | dim_store           | region_name          | Silver       | sv_store            | Region_Name           | Must reference valid region, uppercase, trimmed                                 | UPPER(TRIM(Region_Name))                                                                                 |
| Gold         | dim_store           | region_manager       | Silver       | sv_region           | Region_Manager        | Not null, proper case, trimmed                                                  | INITCAP(TRIM(Region_Manager)) (via join on Region_Name)                                                  |
| Gold         | dim_region          | region_name          | Silver       | sv_region           | Region_Name           | Must be unique, not null, uppercase, trimmed                                    | UPPER(TRIM(Region_Name))                                                                                 |
| Gold         | dim_region          | region_manager       | Silver       | sv_region           | Region_Manager        | Not null, proper case, trimmed                                                  | INITCAP(TRIM(Region_Manager))                                                                            |
| Gold         | dim_product         | product_name         | Silver       | sv_product          | Product_Name          | Must be unique, not null, uppercase, trimmed                                    | UPPER(TRIM(Product_Name))                                                                                |
| Gold         | dim_product         | product_category     | Silver       | sv_product          | Product_Category      | Must reference valid category, uppercase, trimmed                               | UPPER(TRIM(Product_Category))                                                                            |
| Gold         | dim_product         | rfid_tag             | Silver       | sv_product          | RFID_Tag              | Unique, uppercase, trimmed                                                      | UPPER(TRIM(RFID_Tag))                                                                                    |
| Gold         | dim_product         | category_name        | Silver       | sv_category         | Category_Name         | Must reference valid category, uppercase, trimmed                               | UPPER(TRIM(Category_Name)) (via join on Product_Category = Category_Name)                                 |
| Gold         | dim_product         | category_description | Silver       | sv_category         | Category_Description  | Proper case, trimmed                                                            | INITCAP(TRIM(Category_Description)) (via join on Product_Category = Category_Name)                        |
| Gold         | dim_category        | category_name        | Silver       | sv_category         | Category_Name         | Must be unique, not null, uppercase, trimmed                                    | UPPER(TRIM(Category_Name))                                                                               |
| Gold         | dim_category        | category_description | Silver       | sv_category         | Category_Description  | Proper case, trimmed                                                            | INITCAP(TRIM(Category_Description))                                                                       |
| Gold         | dim_date            | report_date          | Silver       | sv_date             | Report_Date           | Must be unique, not null, format YYYY-MM-DD                                     | DATE_FORMAT(Report_Date, 'yyyy-MM-dd')                                                                   |

---

## Explanations for Complex Transformations and Business Rules

- **Store-Region Hierarchy**: The `region_manager` in `dim_store` is populated by joining `sv_store.Region_Name` to `sv_region.Region_Name`.
- **Product-Category Hierarchy**: The `category_name` and `category_description` in `dim_product` are populated by joining `sv_product.Product_Category` to `sv_category.Category_Name`.
- **Standardization**: All business keys (store_code, region_name, product_name, category_name) are uppercased and trimmed to ensure uniqueness and prevent duplicates due to case/whitespace.
- **Proper Case**: Names and descriptions are converted to proper case for readability in reporting.
- **Date Formatting**: All dates are standardized to 'yyyy-MM-dd' for consistency in time-based analytics.
- **Validation**: Uniqueness and not-null constraints are enforced at the Gold layer for all business keys. Referential integrity is ensured via joins and lookups.
- **Cleansing**: Duplicates are removed using DISTINCT, and missing values are handled by filtering out nulls in business key columns.

---

## API Cost

apiCost: 0.000000

---

[outputURL](https://github.com/DIAscendion/Databricks_LakeHouseInADay/tree/main/DI_Databricks_Gold_Dim_Transformation_Data_Mapping)

pipelineID: 14671
