<!--
=============================================
Author:        Ascendion AVA+
Created on:
Description:   Zone gating validation report for the Rental Revenue to Cash Silver DQ Zone Gate (stage 8). Run halted fail-closed because the Zone_Quality_Thresholds input is missing.
=============================================
-->

# Zone Gating Validation Report — DI_Databricks_Silver_DQ_Zone_Gate

**Pipeline:** Databricks Silver Layer Data Engineering Workflow
**Domain:** Rental Revenue to Cash Reports
**Stage:** 8
**Repository:** DIAscendion/Databricks_LakeHouseInADay (branch `main`, commit `81e39d2`)

## 1. Run Status: HALTED (fail-closed). Gate result for every transition is BLOCK.

The agent requires the zone threshold file to build the gate policy. That file could not be read, so the run stopped.
The agent's rules say to stop and report the exact error, not produce partial output, and not invent thresholds.
For that reason, **no Gate Policy YAML (`*_DQ_Zone_Gate_Policy_<n>.yaml`) and no Conditional Check Blocks (`*_DQ_Zone_Gate_Checks_<n>.txt`) were generated.**

## 2. Input Read Results

| # | Input path | Result |
|---|---|---|
| 1 | `DI_Databricks_Silver_DQ_Rule_Generator/Executable_DQ_Rules.py` | READ OK (blob SHA `543066b9…`): 80 rules, DQ_001–DQ_080 |
| 2 | `Input/Zone_Quality_Thresholds.json` | **FAILED:** `Failed to get file contents. The path does not point to a file or directory, or the file does not exist in the repository.` |
| 3 | Pipeline Metrics | Not supplied as an input path for this stage |

Checks done before halting:
- The `Input/` folder only contains `Rental_Revenue_to_Cash_Reports.txt`, `bronze_sample_data.md`, `readme.md` and `rental_revenue_to_cash_bronze_schema.sql`.
- A code search of the repository for `Zone_Quality_Thresholds` found no matches.
- `main` is the only branch in the repository.

## 3. Rule Inventory Parsed (nothing dropped)

| Table | Rules | Critical | Error | Warning |
|---|---|---|---|---|
| silver.si_rental_contracts | DQ_001–DQ_018 | DQ_001, DQ_002 | DQ_003–006, 010, 012–015, 018 | DQ_007–009, 011, 016, 017 |
| silver.si_invoices | DQ_019–DQ_040 | DQ_019, DQ_020 | DQ_021–024, 028–030, 032, 033, 035, 036, 040 | DQ_025–027, 031, 034, 037–039 |
| silver.si_cash_receipts | DQ_041–DQ_057 | DQ_041, DQ_042 | DQ_043–046, 048, 051, 053, 055, 057 | DQ_047, 049, 050, 052, 054, 056 |
| silver.si_customer_master | DQ_058–DQ_068 | DQ_058, DQ_059 | DQ_060–064, 067, 068 | DQ_065, 066 |
| silver.si_branch_employee | DQ_069–DQ_077 | DQ_069, DQ_070 | DQ_071–074, 077 | DQ_075, 076 |
| silver.si_error_data | DQ_078 | – | – | DQ_078 |
| silver.si_pipeline_audit | DQ_079, DQ_080 | – | – | DQ_079, DQ_080 |
| **Total** | **80** | **10** | **43** | **27** |

Notes from the rule file that affect gating:
- The rule file uses the severities Critical, Error and Warning. The gate uses critical, major and minor. The proposed mapping (Error→major, Warning→minor) needs confirmation from the thresholds owner.
- DQ_037–039, DQ_053–055 and DQ_067 check derived columns that are not in the Silver DDL. These rules report SKIPPED, so the gate would treat them as METRIC_UNAVAILABLE. DQ_053, DQ_055 and DQ_067 are Error rules, so each would BLOCK.
- The only numeric thresholds in the rule file are rule-internal (null rate ≤ 0.05 for DQ_008, DQ_034 and DQ_056). These are not zone pass thresholds, so they were not used as gate thresholds.

## 4. Threshold Resolution

| Item | Status |
|---|---|
| Rule / table / dimension / zone-default thresholds | **MISSING_THRESHOLD for all 80 rules.** The source file is unavailable. |
| Critical rules with missing threshold (10) | Default to **BLOCK** |
| Pipeline metrics | **METRIC_UNAVAILABLE.** No metrics input was supplied. |

## 5. Gate Summary per Zone Transition

| Transition | Tables | Result | Reason |
|---|---|---|---|
| bronze_to_silver | si_rental_contracts, si_invoices, si_cash_receipts, si_customer_master, si_branch_employee (+ operational) | **BLOCK** | MISSING_THRESHOLD (input file not found) and METRIC_UNAVAILABLE |
| silver_to_gold | Same Silver tables (source zone) | **BLOCK** | MISSING_THRESHOLD (input file not found) and METRIC_UNAVAILABLE |

Promotion must not proceed until this stage is re-run successfully.

## 6. Required Actions to Unblock

1. Commit `Input/Zone_Quality_Thresholds.json` to `main`. It needs numeric pass thresholds per zone transition, plus per-dimension, severity or table thresholds where they apply. It should also set the action (BLOCK/WARN) for major/Error rules, the quarantine, audit and notification targets, and the override policy.
2. Optionally, provide pipeline run metrics (total, passed and failed rows, null and duplicate counts, freshness) for runtime evaluation.
3. Re-run stage 8. Version numbering starts at `_1`, because the output folder has no existing policy or check files.
