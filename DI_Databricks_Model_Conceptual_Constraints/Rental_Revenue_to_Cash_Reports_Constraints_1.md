____________________________________________
## *Author*: AAVA
## *Created on*: 2026-10-09
## *Description*: Model data constraints and business rules for Rental Revenue-to-Cash Reports
## *Version*: 1
## *Updated on*: 2026-10-09
____________________________________________

## 1. Data Expectations
### 1.1 Data Completeness
1. Branch, region, and organization hierarchy data must be available for all reported branch-level metrics.
2. Date, period, and snapshot date values must be populated for all time-based reporting views.
3. Sales rep and collector information must be available where the report requires personnel-level drill-down.
4. Customer information must be present for AR aging, cash application, and credit risk reporting.
5. Contract status, equipment class, and billing measures must be available for rental revenue and billing performance reporting.
6. Invoice detail including due date, amount, and days past due must be available for AR aging analysis.
7. Payment information including payment amount, payment method, match status, and payment date must be available for cash application reporting.
8. Credit terms, credit limit, customer status, outstanding AR, and open contract exposure must be available for customer credit risk reporting.

### 1.2 Data Accuracy
1. Health score must remain within the range of 0 to 100.
2. Net billings must reconcile to gross billings minus credit memos.
3. Aging bucket totals must reconcile to Total AR Outstanding.
4. Applied payment amounts must not exceed the related invoice amount.
5. Component domain scores must roll up to the overall health score according to configured weights.
6. Credit utilization calculations must correctly reflect outstanding AR relative to credit limit.
7. Duplicate customer records representing the same legal entity must be resolved before aggregating exposure.

### 1.3 Data Format
1. Aging buckets must use only the defined categories 0-30, 31-60, 61-90, and 90+.
2. Customer status must align to the stated report values such as Active and Suspended.
3. Contract status must align to the stated report values Open and Closed.
4. Invoice and payment reporting must distinguish applied and unapplied status explicitly.
5. Time analysis must support day, week, month, and quarter reporting where specified.

### 1.4 Data Consistency
1. Branch must exist in the organization hierarchy and be active for the selected date.
2. The same reporting period must be used consistently in rate-based calculations such as DSO and CEI.
3. Drill-through totals must reconcile to source fact totals for rental revenue and AR aging.
4. Revenue, AR, cash application, and credit risk views must use the same branch and region rollup structure.
5. Customer exposure reporting must use a single conformed customer record after deduplication.

## 2. Constraints
### 2.1 Mandatory Fields
1. **Branch Name**: Required because all reports include branch-level analysis and security access.
2. **Region**: Required for regional comparison, drill-down, and rollup reporting.
3. **Date / Snapshot Date**: Required for trend, daily, weekly, and point-in-time reporting.
4. **Customer Name**: Required for AR, cash application, and credit risk detail views.
5. **Contract Status**: Required for billing performance and open exposure analysis.
6. **Invoice Amount**: Required for billing, AR outstanding, and payment application validation.
7. **Due Date**: Required to calculate days past due and aging bucket.
8. **Payment Amount**: Required to calculate cash collected and unapplied cash.
9. **Credit Limit**: Required for customer credit utilization and over-limit analysis.
10. **Customer Status**: Required to identify suspended customers with open exposure.

### 2.2 Uniqueness Requirements
1. **Branch, Date, Period Type**: Must uniquely identify a health score record.
2. **Branch, Date, Sales Rep, Equipment Class**: Must uniquely identify a revenue aggregate.
3. **Customer, Invoice, Snapshot Date**: Must uniquely identify an AR snapshot record.
4. **Receipt ID**: Must uniquely identify a payment record.
5. **Customer, Snapshot Date**: Must uniquely identify a customer risk snapshot record.

### 2.3 Data Type Limitations
1. **Health Score**: Must be constrained to values between 0 and 100.
2. **Credit Memo Amount**: Must be negative.
3. **Standard Invoice Amount**: Must be non-negative.
4. **Payment Amount**: Must be non-negative.
5. **Credit Limit**: Must be non-negative.
6. **Aging Bucket**: Must be limited to the fixed non-overlapping bucket set.

### 2.4 Dependencies
1. DSO calculation depends on Total AR Outstanding, Total Credit Sales in Period, and Number of Days in Period.
2. AR 90+ % calculation depends on AR in 90+ bucket and Total AR Outstanding.
3. Net Billings depends on Gross Billings and Credit Memos.
4. ADR depends on Rental Revenue and Total Billed Rental Days.
5. Revenue per Contract depends on Rental Revenue and Number of Contracts.
6. CEI depends on Beginning AR, Credit Sales, Ending Total AR, and Ending Current AR using the same reporting window.
7. Average Days to Pay depends on Payment Date and Invoice Date across paid invoices.
8. Unapplied Cash % depends on Unapplied Payment Amount and Total Payments Amount.
9. Credit Utilization % depends on Outstanding AR and Credit Limit.
10. Suspended Customers with Open Exposure depends on Customer Status, Outstanding AR, and open contracts.

### 2.5 Referential Integrity
1. **Branch to Organization Hierarchy**: Every branch used in reporting must resolve to a valid organization hierarchy assignment.
2. **Invoice to Contract**: Invoice amounts must tie to a valid contract after conformance.
3. **Outstanding Invoice to Customer**: Every outstanding invoice must map to a valid customer.
4. **Customer to Conformed Customer Record**: Each customer must resolve to a single conformed customer record after deduplication.
5. **Contract to Customer**: Every contract used in reporting must map to a valid customer.
6. **Cash Receipt to Invoice Application**: Applied payment records must reference valid related invoices; unapplied receipts must remain identifiable as unapplied.
7. **Facts to Date**: All fact records must link to a valid reporting date.
8. **AR and Credit Risk Facts to Customer**: AR aging and credit risk records must link to valid customers.
9. **Revenue and Cash Application Facts to Branch**: Revenue and cash application records must link to valid branches.

## 3. Business Rules
### 3.1 Data Processing Rules
1. Health score must be calculated as a weighted composite of normalized domain scores using configurable weights.
2. Aging bucket must be determined by subtracting invoice due date from snapshot date and assigning the result to the fixed bucket range.
3. Net billings must be derived by subtracting credit memos from gross billings.
4. ADR must exclude zero-duration or cancelled contracts from the calculation.
5. Payments may apply to zero, one, or more invoices, and partial application must be tracked.
6. Unapplied cash must be flagged and reported separately rather than excluded.
7. Duplicate customer records for the same legal entity must be resolved before exposure aggregation.

### 3.2 Reporting Logic Rules
1. Executive scorecard reporting must support comparison across network, region, branch, and sales rep or collector levels.
2. Billing performance reporting must support analysis by branch, region, sales rep, and equipment class.
3. AR aging reporting must support aging analysis by branch, collector, customer, and invoice.
4. Cash application reporting must support collector-level performance evaluation and payment application detail.
5. Credit risk reporting must identify customers approaching or exceeding credit limits and suspended customers with open exposure.
6. Drill-through views must reconcile to the underlying fact-level data for the selected measure.
7. Rate-based calculations must only be computed when the required denominator is non-zero.
8. Executives in credit risk reporting may see aggregates only and no individual customer PII beyond name.

### 3.3 Transformation Guidelines
1. Consolidate legacy AR, dashboard, vendor, invoice detail, and rental contract reports into governed consolidated analytical views.
2. Use conformed branch, region, customer, contract, invoice, and date structures across all reporting domains.
3. Resolve duplicate customer records during Silver-layer processing before Gold-layer risk aggregation.
4. Preserve branch and region hierarchy needed for drill-down, drill-up, and security filtering.
5. Ensure period-based measures and trends align across daily, weekly, monthly, and quarterly views.
6. Maintain separate analytical facts for rental revenue, AR aging, cash application, and credit risk while enabling consistent cross-domain reporting.
7. Support source reconciliation to gold.fct_rental_revenue and gold.fct_ar_aging where specified in validations.