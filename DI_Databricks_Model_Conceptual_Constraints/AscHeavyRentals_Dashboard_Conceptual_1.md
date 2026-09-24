_____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Conceptual data model for AscHeavyRentals_Dashboard
## *Version*: 1
## *Updated on*: 
_____________________________________________

### 1. Domain Overview
AscHeavyRentals_Dashboard covers executive-level reporting for a heavy equipment rental business. The domain includes financial performance, fleet management, regional and segment analysis, and operational metrics for decision support. The dashboard is designed for CEO, CFO, and COO audiences, focusing on trailing 12-month performance, prior-period comparisons, and key business ratios.

### 2. List of Entity Names with Descriptions
1. **Company**: Represents the overall business entity, aggregating all segments and regions.
2. **Segment**: Distinguishes between General Tool and Specialty equipment categories.
3. **Region**: Geographical divisions such as Southeast, Midwest, and West.
4. **Fleet**: Collection of rental equipment, tracked by original cost and utilization.
5. **Revenue Component**: Breakdown of revenue sources (owned rental, re-rent, ancillary, equipment sales).
6. **Management P&L Line Item**: Financial line items for reporting (revenue, cost, profit, EBITDA, etc.).
7. **Fleet Transaction**: Events affecting fleet assets (additions, refurbishments, disposals).
8. **Metric Definition**: Business rules and formulas for KPIs and operational metrics.

### 3. List of Attributes for Each Entity
#### Company
1. **Company Name**: Name of the business entity.
2. **Total Revenue**: Aggregated revenue for the company.
3. **EBITDA Margin**: Earnings before interest, taxes, depreciation, and amortization as a percentage of revenue.
4. **Dollar Utilization**: Ratio of owned rental revenue to average OEC.

#### Segment
1. **Segment Name**: General Tool or Specialty.
2. **Share of Fleet OEC**: Percentage of original cost attributed to the segment.
3. **Dollar Utilization**: Utilization percentage for the segment.
4. **Design/Target Band**: Expected utilization range.
5. **Capital Stance/Recommendation**: Investment guidance for the segment.

#### Region
1. **Region Name**: Southeast, Midwest, West.
2. **Revenue**: Revenue attributed to the region.
3. **Share of Company Revenue**: Percentage of total revenue from the region.
4. **EBITDA Margin**: Margin for the region.
5. **Dollar Utilization**: Utilization for the region.

#### Fleet
1. **Month-End OEC**: Original cost at month-end.
2. **OEC-Weighted Fleet Age**: Average age of fleet, weighted by OEC.
3. **Time Utilization**: Percentage of fleet available and utilized.

#### Revenue Component
1. **Owned Rental Revenue**: Revenue from owned rentals.
2. **Re-Rent Revenue**: Revenue from re-rented equipment.
3. **Ancillary Revenue**: Revenue from ancillary services.
4. **Used Equipment Sales**: Revenue from used equipment sales.
5. **New Equipment Sales**: Revenue from new equipment sales.

#### Management P&L Line Item
1. **Line Item Name**: Name of the financial line item.
2. **Current Month Value**: Value for August.
3. **TTM Value**: Trailing 12 months value.
4. **Percent of Revenue**: Line item as percentage of revenue.

#### Fleet Transaction
1. **Transaction Type**: Addition, refurbishment, disposal.
2. **Transaction Value**: Value of the transaction.

#### Metric Definition
1. **Metric Name**: Name of the metric or KPI.
2. **Formula/Definition**: Business rule or calculation.

### 4. KPI List
1. **Revenue Growth %**: TTM vs prior TTM revenue growth.
2. **Fleet OEC Growth %**: Growth in fleet original cost.
3. **Same-Store Revenue Growth %**: Revenue growth for same stores.
4. **Fleet Productivity $**: Combined rate, time, mix effect on rental revenue.
5. **Dollar Utilization %**: Ratio of owned rental revenue to average OEC.
6. **EBITDA Margin %**: EBITDA as percentage of revenue.
7. **EBITDA $ Level and Change YoY**: Absolute EBITDA and year-over-year change.
8. **Revenue $ Change**: Change in revenue used for context.
9. **Margin Point Change YoY**: Change in margin points year-over-year.
10. **Simplified Free Cash Flow $**: EBITDA minus cash tax and net fleet capex.
11. **Net Fleet Investment $**: Capex minus disposal proceeds.
12. **Disposal Proceeds as % of OEC**: Proceeds from disposals as percentage of original cost.
13. **Days Sales Outstanding (DSO)**: Current vs prior period DSO.
14. **Ancillary Attachment %**: Ancillary revenue as percentage of owned rental revenue.
15. **Re-Rent %**: Re-rent revenue as percentage of total rental revenue.

### 5. Conceptual Data Model Diagram
| Source Entity      | Relationship Key Field   | Target Entity         | Relationship Type |
|--------------------|-------------------------|----------------------|-------------------|
| Company           | company_name             | Segment              | One-to-Many       |
| Segment           | segment_name             | Fleet                | One-to-Many       |
| Fleet             | month_end_OEC           | Fleet Transaction    | One-to-Many       |
| Segment           | segment_name             | Revenue Component    | One-to-Many       |
| Region            | region_name              | Revenue Component    | One-to-Many       |
| Company           | company_name             | Region               | One-to-Many       |
| Management P&L    | line_item_name           | Metric Definition    | One-to-Many       |

### 6. Common Data Elements in Report Requirements
1. **Revenue**
2. **EBITDA Margin**
3. **Dollar Utilization**
4. **Fleet OEC**
5. **Segment Name**
6. **Region Name**
7. **Month-End OEC**
8. **Owned Rental Revenue**
9. **Disposal Proceeds**
10. **Fleet Productivity**
11. **Days Sales Outstanding (DSO)**
