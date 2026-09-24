____________________________________________
## *Author*: AAVA
## *Created on*: 
## *Description*: Model data constraints and business rules for AscHeavyRentals_Dashboard
## *Version*: 1
## *Updated on*: 
____________________________________________

## 1. Data Expectations

### 1.1 Data Completeness
1. All financial and operational metrics must be available for both trailing 12 months (TTM) and prior TTM periods.
2. Segment and region breakdowns must be present for all required metrics (revenue, EBITDA, dollar utilization, fleet OEC).
3. Management P&L must include all specified line items for both current month and TTM.

### 1.2 Data Accuracy
1. Dollar utilization must be calculated as ratio-of-sums, not average of period percentages.
2. Fleet productivity must be computed as the combined rate, time, and mix effect, excluding fleet-size growth.
3. All bridge calculations must reconcile exactly to the ending revenue figure.

### 1.3 Data Format
1. All monetary values must be displayed in millions, with one decimal place.
2. Percentages must be shown with one decimal place.
3. Data must be dimensioned by segment and region, as required.

### 1.4 Data Consistency
1. Definitions for KPIs and metrics must be applied consistently across all reports.
2. Prior-period comparisons must use the same calculation logic as current-period metrics.
3. All segment and region names must be consistent throughout the dashboard.

## 2. Constraints

### 2.1 Mandatory Fields
1. Segment name: Required for segment-level reporting.
2. Region name: Required for regional analysis.
3. Dollar utilization: Must be present for each segment and region.
4. Revenue: Required for all entities and breakdowns.
5. Fleet OEC: Required for fleet and segment analysis.

### 2.2 Uniqueness Requirements
1. Each segment must have a unique segment name.
2. Each region must have a unique region name.
3. Each management P&L line item must be uniquely identified by its name.

### 2.3 Data Type Limitations
1. Monetary values: Must be numeric and formatted in millions.
2. Percentages: Must be numeric and formatted to one decimal place.

### 2.4 Dependencies
1. Dollar utilization depends on owned rental revenue and average OEC.
2. Fleet productivity depends on rate, time, and mix effects, and must exclude fleet-size growth.
3. Simplified free cash flow depends on EBITDA, cash tax, and net fleet capex.

### 2.5 Referential Integrity
1. Segment names must match those in fleet and revenue tables.
2. Region names must match those in regional mix and revenue tables.
3. Fleet transactions must reference valid fleet assets.

## 3. Business Rules

### 3.1 Data Processing Rules
1. Dollar utilization must be computed as ratio-of-sums at every grain (segment, company).
2. Fleet productivity must be calculated as the subtotal of rate, time, and mix effects after removing fleet-size growth.
3. All bridge components must be calculated as isolated variance-decomposition against the prior-year base.

### 3.2 Reporting Logic Rules
1. All KPIs must be reported for both TTM and prior TTM periods.
2. Management P&L must include both current month and TTM values for each line item.
3. Regional mix table must display revenue, EBITDA margin, and dollar utilization for each region and company total.

### 3.3 Transformation Guidelines
1. Monetary values must be converted to millions and rounded to one decimal place.
2. Percentages must be calculated and rounded to one decimal place.
3. Segment and region cross-tab data must be aggregated to company totals where required.
