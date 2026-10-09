_____________________________________________
## *Author*: AAVA
## *Created on*: 2026-10-09
## *Description*: Conceptual data model for Rental Revenue-to-Cash Reports
## *Version*: 1
## *Updated on*: 2026-10-09
_____________________________________________

## 1. Domain Overview
The business domain covered is Rental Revenue-to-Cash analytical reporting, spanning revenue, billing, accounts receivable, collections, cash application, and customer credit risk monitoring across branches and regions. The model supports consolidated reporting for executive scorecards, billing performance, AR aging, collector performance, and customer credit exposure.

## 2. List of Entity Names with Descriptions
1. **Region**: Organizational area used to compare performance across the network.
2. **Branch**: Operating business unit used for reporting revenue, AR, collections, and risk performance.
3. **Date**: Reporting calendar reference used for daily, weekly, monthly, quarterly, and snapshot-based analysis.
4. **Customer**: Business customer whose contracts, invoices, receivables, payments, and credit exposure are monitored.
5. **Sales Rep**: Business representative associated with branch performance, contract activity, and revenue analysis.
6. **Collector**: Collections representative responsible for customer collection activity and performance monitoring.
7. **Equipment Class**: Classification used to analyze rental revenue and billing mix.
8. **Contract**: Rental agreement used to analyze contract status, revenue generation, and open exposure.
9. **Invoice**: Billing transaction used for revenue, AR aging, billing, and payment application reporting.
10. **Cash Receipt**: Payment receipt used to track cash collected, applied and unapplied cash, and payment timing.
11. **Fact Rental Revenue**: Analytical fact representing billed rental revenue, gross billings, net billings, credit memos, and related revenue measures.
12. **Fact AR Aging**: Analytical fact representing outstanding receivables by aging bucket and snapshot date.
13. **Fact Cash Application**: Analytical fact representing payment collection, application status, and collection effectiveness measures.
14. **Fact Credit Risk**: Analytical fact representing customer credit exposure, utilization, and risk conditions.
15. **Organization Hierarchy**: Hierarchical structure connecting network, region, and branch for drill-down and security use.

## 3. List of Attributes for Each Entity
### Region
1. **Region Name**: Name of the region used for aggregation and comparison.

### Branch
1. **Branch Name**: Name of the branch used in operational and performance reporting.
2. **Branch Status**: Indicates whether the branch is active for the selected reporting date.

### Date
1. **Date**: Calendar date used in daily and snapshot reporting.
2. **Period**: Reporting period reference such as week, month, or quarter.
3. **Period Type**: Indicates the reporting grain such as day or week.
4. **Number of Days in Period**: Period day count used in DSO calculations.

### Customer
1. **Customer Name**: Business name of the customer.
2. **Customer Status**: Status such as Active or Suspended.
3. **Credit Terms**: Agreed payment terms for the customer.
4. **Credit Limit**: Approved customer credit exposure limit.
5. **Customer Since Date**: Start date indicating customer tenure.

### Sales Rep
1. **Sales Rep Name**: Name of the sales representative associated with contracts and revenue.

### Collector
1. **Collector Name**: Name of the collector responsible for collections activity.

### Equipment Class
1. **Equipment Class Name**: Category used to analyze revenue and billing performance.

### Contract
1. **Contract Status**: Indicates whether a contract is open or closed.
2. **Open Contract Count**: Number of open contracts related to customer exposure.
3. **Open Contract Value**: Value of open contracts used in exposure analysis.
4. **Total Billed Rental Days**: Billed rental duration used in ADR calculation.

### Invoice
1. **Due Date**: Date when payment is expected for the invoice.
2. **Invoice Amount**: Amount billed on the invoice.
3. **Gross Billings**: Total billed amount before credit memos.
4. **Credit Memo Amount**: Reduction amount applied through credit memos.
5. **Net Billings**: Gross billings minus credit memos.
6. **Invoice Count**: Count of invoices used in billing analysis.
7. **Days Past Due**: Number of days between snapshot date and due date.
8. **Aging Bucket**: Aging classification of the invoice balance.
9. **Invoice Date**: Date the invoice was issued.

### Cash Receipt
1. **Payment Amount**: Amount collected in the receipt.
2. **Payment Method**: Method used to make the payment.
3. **Payment Date**: Date on which payment was made.
4. **Match Status**: Indicates whether payment is applied or unapplied.
5. **Days to Pay**: Time between invoice date and payment date.
6. **Unapplied Payment Amount**: Portion of payment not yet matched to invoices.

### Fact Rental Revenue
1. **Rental Revenue**: Revenue recognized from rental activity.
2. **Gross Billings**: Total billing value before adjustments.
3. **Net Billings**: Billing value after credit memo adjustments.
4. **Credit Memo Rate**: Ratio of credit memo amount to gross billings.
5. **Average Daily Rate**: Revenue per billed rental day.
6. **Revenue per Contract**: Average revenue earned per contract.
7. **Trend Value**: Period-over-period trend indicator for revenue analysis.

### Fact AR Aging
1. **Total AR Outstanding**: Total receivable balance outstanding at the snapshot date.
2. **AR 90+ Amount**: Receivable amount in the 90+ aging bucket.
3. **AR 90+ Percentage**: Proportion of total AR in the 90+ bucket.
4. **Best Possible DSO**: Best-achievable days sales outstanding measure.
5. **DSO**: Days sales outstanding measure.
6. **DSO Trend**: Period-over-period movement in DSO.
7. **AR Aging by Bucket**: Receivable amount summarized by defined aging bucket.
8. **Snapshot Date**: Date at which AR aging is measured.

### Fact Cash Application
1. **Cash Collected**: Total cash collected in the reporting period.
2. **Collection Effectiveness Index**: Measure of effectiveness of collections in the period.
3. **Average Days to Pay**: Average elapsed time between invoice and payment.
4. **Invoices Paid On Time Percentage**: Share of invoices paid on time.
5. **Unapplied Cash Amount**: Total payment amount not applied to invoices.
6. **Unapplied Cash Percentage**: Share of total payments that remain unapplied.

### Fact Credit Risk
1. **Outstanding AR**: Current receivable exposure for the customer.
2. **Credit Utilization Percentage**: Ratio of outstanding AR to credit limit.
3. **Customers Over Limit Count**: Count of customers exceeding credit limit.
4. **Customers Over Limit Amount**: Amount of exposure above credit limit.
5. **Suspended Customers with Open Exposure**: Indicator or count of suspended customers with AR or open contracts.
6. **AR 90+ Amount by Customer**: Past-due exposure in the 90+ bucket at customer level.

### Organization Hierarchy
1. **Organization Hierarchy Name**: Hierarchical reference supporting branch and region rollups.
2. **Network Level**: Highest rollup level used for enterprise-wide comparisons.

## 4. KPI List
1. **Overall Revenue-to-Cash Health Score**: Composite score from normalized Revenue, AR, Cash App, and Credit Risk domain scores.
2. **Rental Revenue**: Revenue generated from rental business activity.
3. **DSO**: Days Sales Outstanding calculated from AR outstanding, credit sales, and days in period.
4. **AR 90+ %**: Percentage of total outstanding AR that is aged 90 days or more.
5. **Collection Effectiveness Index (CEI)**: Measure of collection effectiveness over a reporting period.
6. **Unapplied Cash %**: Percentage of total payments that remain unapplied.
7. **Gross Billings**: Total invoiced billing amount before credits.
8. **Net Billings**: Gross billings less credit memos.
9. **Average Daily Rate (ADR)**: Rental revenue divided by total billed rental days.
10. **Revenue per Contract**: Rental revenue divided by number of contracts.
11. **Credit Memo Rate**: Credit memo dollars divided by gross billings.
12. **Total AR Outstanding**: Total open receivables balance.
13. **AR Aging by Bucket**: Outstanding AR summarized by aging bucket.
14. **Best Possible DSO**: Optimized DSO benchmark based on current AR profile.
15. **DSO Trend**: Period-over-period change in DSO.
16. **Cash Collected**: Total payment amount collected in the period.
17. **Average Days to Pay**: Average time taken by customers to pay invoices.
18. **% Invoices Paid On Time**: Percentage of invoices settled by the due date.
19. **Unapplied Cash $**: Payment dollars not applied to invoices.
20. **Credit Utilization %**: Outstanding AR as a percentage of customer credit limit.
21. **Customers Over Limit**: Count and amount of customers with exposure above credit limit.
22. **AR 90+ $ by Customer**: Customer-level exposure aged 90 days or more.
23. **Suspended Customers with Open Exposure**: Count of suspended customers with open AR or open contracts.

## 5. Conceptual Data Model Diagram
| Source Entity | Relationship Key Field | Target Entity | Relationship Type |
|---------------|------------------------|---------------|-------------------|
| Region | Region | Branch | One-to-Many |
| Branch | Branch | Contract | One-to-Many |
| Customer | Customer | Contract | One-to-Many |
| Customer | Customer | Invoice | One-to-Many |
| Sales Rep | Branch | Branch | Many-to-One |
| Collector | Branch | Branch | Many-to-One |
| Collector | Collector Assignment | Customer | One-to-Many |
| Contract | Contract | Invoice | One-to-Many |
| Invoice | Invoice to Payment Application | Cash Receipt | One-to-Many |
| Date | Date | Fact Rental Revenue | One-to-Many |
| Date | Date | Fact AR Aging | One-to-Many |
| Date | Date | Fact Cash Application | One-to-Many |
| Date | Date | Fact Credit Risk | One-to-Many |
| Customer | Customer | Fact AR Aging | One-to-Many |
| Customer | Customer | Fact Credit Risk | One-to-Many |
| Branch | Branch | Fact Rental Revenue | One-to-Many |
| Branch | Branch | Fact Cash Application | One-to-Many |
| Contract | Contract | Fact Rental Revenue | One-to-Many |
| Invoice | Invoice | Fact Cash Application | One-to-Many |
| Organization Hierarchy | Organization Hierarchy | Branch | One-to-Many |

## 6. Common Data Elements in Report Requirements
1. **Branch Name**: Appears across executive, billing, AR, cash application, and credit risk reports.
2. **Region**: Used consistently for aggregation, drill-down, and security.
3. **Date / Period / Snapshot Date**: Used across all reporting areas for trend and point-in-time analysis.
4. **Customer**: Referenced across AR, cash application, and credit risk reporting.
5. **Sales Rep**: Used in executive, billing, and AR reporting.
6. **Collector**: Used in executive, AR, and cash application reporting.
7. **Contract Status**: Used in billing and credit risk reporting.
8. **Invoice Detail**: Used in billing, AR, and cash application reporting.
9. **Rental Revenue**: Used in executive and billing reporting.
10. **DSO**: Used in executive and AR reports.
11. **AR 90+ % / AR 90+ Amount**: Used in executive, AR, and credit risk reports.
12. **Unapplied Cash**: Used in executive and cash application reporting.
13. **Credit Limit**: Used in credit risk reporting and exposure calculations.
14. **Outstanding AR**: Used in AR and credit risk reporting.
15. **Organization Hierarchy**: Used for drill paths and security across reports.