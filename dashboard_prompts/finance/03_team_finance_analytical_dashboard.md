# 03_Team Finance – Analytical Dashboard — migration prompts

Source workbook: Tableau `03_Finance / 03_Team Finance - Analytical Dashboard` (~1.5k views).
Purpose: different views into financial data for all brands and 3PLs.

Paste each prompt into the new platform's agent as-is. One prompt = one dashboard page.
Tables in `PROD_ANALYTICS_DB.FINANCE_SCHEMA` with **quoted mixed-case column names** (`"Brand Name"`) are:
SUMMARY_FINANCE_METRICS, DUTY_TAX_DISCREPANCY_REPORT, INVOICE_AND_COMPLIANCE_METRICS, BILLING_NET_TERMS,
CUSTOMERS_CHARGED_NON_DEFAULT_FEE. REVENUE_MODEL_INVOICE_BASED uses normal UPPER_SNAKE columns.

| # | Tableau page | Source table (all `NLT__FINANCE__*`) |
|---|---|---|
| 1 | Shipment Metrics by Brand/3PL (by label print date) | SUMMARY_FINANCE_METRICS |
| 2 | Shipment Metrics by Brand/3PL (by issue date) | SUMMARY_FINANCE_METRICS |
| 3 | PG Metrics by Brand/3PL (by issue date) | REVENUE_MODEL_INVOICE_BASED |
| 4 | Quarterly Board Numbers | custom SQL on SHIPMENT_LEVEL_DMT |
| 5 | Billing Net Terms | BILLING_NET_TERMS |
| 6 | Billing Inaccuracies per Month | INVOICE_AND_COMPLIANCE_METRICS |
| 7 | Duty & Tax Discrepancy per Month | DUTY_TAX_DISCREPANCY_REPORT |
| 8 | Customers Charged Non-5% Default Fee | CUSTOMERS_CHARGED_NON_DEFAULT_FEE |

---

## Prompt 1 — Shipment Metrics by Brand/3PL (by label print date)

```text
Build a dashboard page called "Label Print / Consolidated / Invoiced Metrics by Brand or 3PL".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__SUMMARY_FINANCE_METRICS.
Column names contain spaces and mixed case — always double-quote them (e.g. "Brand Name", "3PL Name").
Grain: pre-aggregated rows by brand, 3PL, label print date and several attributes. Always SUM measures.

SUBTITLE (static text)
"- Filter date by label print date.
 - SoR from GB included in Tax/Gross Sales since September 2023 onwards only.
 - Does not hold information on PG fees and monthly minimums. To view total consolidated revenue, please refer
   to the Revenue Dashboard."
Make the title dynamic: "Label Print/Consolidated/Invoiced {Metric} by {Brand or 3PL}".

HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS") as date + time, top-right.

CONTROLS (left sidebar)
1. "Label Print Date Selection" on "Label Print Date UTC": Last 7 Days | Last 30 Days (DEFAULT) | Last 90 Days |
   Year to Date | Custom Dates. Last N days = between CURRENT_DATE - N and CURRENT_DATE inclusive; YTD = same
   calendar year as today; Custom Dates shows "Start Date"/"End Date" pickers (inclusive), hidden otherwise.
2. "Metric Selection": Gross Sales (DEFAULT) | Freight | Tax | Duty | Insurance. Row-level metric value:
     Gross Sales = COALESCE("Total Freight Invoice USD",0) + COALESCE("Total Duty Invoice USD",0)
                 + COALESCE("Total Tax Invoice USD",0) + COALESCE("Total Insurance Invoice USD",0)
     Freight     = COALESCE("Total Freight Invoice USD",0)
     Tax         = COALESCE("Total Tax Invoice USD",0)
     Duty        = COALESCE("Total Duty Invoice USD",0)
     Insurance   = COALESCE("Total Insurance Invoice USD",0)
3. "Time Interval": Year | Quarter | Month (DEFAULT) | Week | Day, bucketing "Label Print Date UTC" with labels
   YYYY | YYYY-Qn | YYYY-Mmm (e.g. 2026-M03) | YYYY-Www (zero-padded) | YYYY-MM-DD.
4. "Brand or 3PL": Brand (DEFAULT) | 3PL. Defines the grouping dimension:
     Brand → "Brand Name", with a second column "Brand's 3PL" = "3PL Name"
     3PL   → "3PL Name", and hide the "Brand's 3PL" column.
5. Multi-select filters, default All: "Brand Name", "3PL Name", "Shipment Type" (column "Duty Tax Flag"),
   "Passport Invoice Service Name", "Destination Region" (column "Destination Country EU Segmented"),
   "Destination Country", "Destination State/Province" (= UPPER(TRIM("Destination State"))).

ALWAYS-ON HIDDEN FILTER (apply to every widget)
Exclude Canadian rows with an invalid province: if "Destination Country" = 'Canada' OR
"Destination Country EU Segmented" = 'CA', keep the row only when UPPER(TRIM("Destination State")) IN
('AB','BC','MB','NB','NL','NT','NS','NU','ON','PE','QC','SK','YT'). Keep all non-Canadian rows.

KPI ROW (4 big-number tiles, same filters)
- "Number of Brands" = COUNT(DISTINCT grouping dimension from control 4). Integer.
- "{Metric}" (label print / expected value) = SUM(metric) over all rows.
- "Consolidated {Metric}" = SUM(metric) WHERE "Is Consolidated" = TRUE.
- "Invoiced {Metric}" = SUM(metric) WHERE "Is Invoiced" = TRUE.
Currency tiles as $#,##0.00.

MAIN WIDGET — pivot table (full width, scrollable, exportable)
Rows: grouping dimension, then "Brand's 3PL" (Brand mode only).
Columns: time interval bucket (oldest → newest), and under each bucket three measures:
  "Label Print Values" (SUM metric, all rows), "Consolidated Values" (SUM metric where "Is Consolidated"),
  "Invoiced Values" (SUM metric where "Is Invoiced").
Grand Total row pinned at the top. Empty cells stay blank (not 0). Currency $#,##0.00.
Default sort: grouping dimension ascending.
```

---

## Prompt 2 — Shipment Metrics by Brand/3PL (by issue date)

```text
Build a dashboard page called "Invoiced Metrics by Brand or 3PL (by Invoice Issue Date)".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__SUMMARY_FINANCE_METRICS (double-quote all
column names). Only rows with "Is Invoiced" = TRUE count toward the measures on this page.

SUBTITLE (static): "- Filter date by shipping invoice issue date.
 - SoR from GB included in Tax/Gross Sales since September 2023 onwards only."
Dynamic title: "Invoiced {Metric} by {Brand or 3PL}".
HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS").

CONTROLS (left sidebar)
1. "Invoice Issue Date" preset on "Passport Shipping Invoice Issue Date": Last 7 Days | Last 30 Days (DEFAULT) |
   Last 90 Days | Year to Date | Custom Dates (Start/End pickers only for Custom; ranges inclusive, end today).
2. "Metric Selection": Gross Sales (DEFAULT) | Freight | Tax | Duty | Insurance, defined as
     Gross Sales = COALESCE("Total Freight Invoice USD",0) + COALESCE("Total Duty Invoice USD",0)
                 + COALESCE("Total Tax Invoice USD",0) + COALESCE("Total Insurance Invoice USD",0)
     Freight = "Total Freight Invoice USD"; Tax = "Total Tax Invoice USD"; Duty = "Total Duty Invoice USD";
     Insurance = "Total Insurance Invoice USD" (each COALESCE'd to 0).
3. "Time Interval": Year | Quarter | Month (DEFAULT) | Week | Day on "Passport Shipping Invoice Issue Date",
   labels YYYY | YYYY-Qn | YYYY-MM | YYYY-Wn | YYYY-MM-DD.
4. "Brand or 3PL": Brand (DEFAULT) → rows "Brand Name" + "Brand's 3PL" ("3PL Name"); 3PL → rows "3PL Name" only.
5. Multi-select filters, default All: "Brand Name", "3PL Name", "Shipment Type" ("Duty Tax Flag"),
   "Passport Invoice Service Name", "Destination Region" ("Destination Country EU Segmented"),
   "Destination Country", "Destination State/Province" (UPPER(TRIM("Destination State"))).

ALWAYS-ON HIDDEN FILTER — same Canada rule: if "Destination Country" = 'Canada' OR
"Destination Country EU Segmented" = 'CA', keep only rows whose UPPER(TRIM("Destination State")) is one of
AB, BC, MB, NB, NL, NT, NS, NU, ON, PE, QC, SK, YT.

KPI ROW
- "Number of Brands" = COUNT(DISTINCT grouping dimension).
- "Invoiced {Metric}" = SUM(metric) WHERE "Is Invoiced" = TRUE. $#,##0.00.

MAIN WIDGET — pivot table
Rows: grouping dimension (+ "Brand's 3PL" in Brand mode). Columns: issue-date interval buckets, oldest → newest.
Value: SUM(metric) WHERE "Is Invoiced" = TRUE. Grand Total row on top. $#,##0.00. Exportable.
```

---

## Prompt 3 — PG Metrics by Brand (by issue date)

```text
Build a dashboard page called "Invoiced Passport Global Fees & Monthly Minimums by Brand".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__REVENUE_MODEL_INVOICE_BASED
(regular UPPER_SNAKE_CASE columns). Date column: DATE_VALUE (invoice issue date).
Derived row-level measure:
  PG_FEES = COALESCE(PASSPORT_GLOBAL_FEES_USD, 0) + COALESCE(PG_MONTHLY_MINIMUM_FEE_RMNANT, 0)

SUBTITLE (static): "- Filter date by invoice issue date.
 - This view only holds information on invoiced PG Fees and Monthly Minimums."
HEADER WIDGET — "Data Update Time": MAX(DBT_UPDATED_UTC_TS).

CONTROLS
1. "Invoice Issue Date" preset on DATE_VALUE: Last 7 Days | Last 30 Days (DEFAULT) | Last 90 Days |
   Year to Date | Custom Dates (Start/End pickers only for Custom; inclusive; ends today).
2. "Time Interval": Year | Quarter | Month (DEFAULT) | Week | Day on DATE_VALUE,
   labels YYYY | YYYY-Qn | YYYY-MM | YYYY-Wn | YYYY-MM-DD.
3. "Brand Name" multi-select, default All.

KPI ROW
- "Number of Brands" = COUNT(DISTINCT BRAND_NAME) over rows where PG_FEES > 0.001.
- "Invoiced PG Fees & Monthly Minimums" = SUM(PG_FEES). $#,##0.00.

MAIN WIDGET — pivot table
Rows: BRAND_NAME, SALESFORCE_ACCOUNT_ID. Columns: DATE_VALUE interval buckets, oldest → newest.
Value: SUM(PG_FEES). Only show brand rows whose SUM(PG_FEES) over the selected period is >= 0.01.
Grand Total row on top. $#,##0.00. Exportable.
```

---

## Prompt 4 — Quarterly Board Numbers

```text
Build a dashboard page called "Quarterly Board Numbers".

CONTROL
"X Quarter Ago vs Previous Quarter" — integer selector 1..10, DEFAULT 1. Call it :q.
(1 = last completed quarter compared with the quarter before it.)

DATASET — run this SQL on Snowflake, substituting :q (keep the logic exactly):

WITH all_emerging_brands AS (
    SELECT m.id FROM prod_staging_db.aurora_passport_schema.dim__aurora_passport_merchant AS m
    WHERE client_id = 'd497a7a90a0e981a1c5011de4d8bc0191651099719003'
),
base AS (
    SELECT g.*,
        CASE WHEN g.x_3pl_id = 'a07dad8aea7c13cb49e8c6791519138c1653503783053' THEN 'SCP'
             WHEN g.brand_id IN (SELECT id FROM all_emerging_brands) THEN 'Emerging Brands'
             ELSE g.brand_name END AS brand_group
    FROM prod_analytics_db.finance_schema.nlt__finance__shipment_level_dmt g
    WHERE g.is_paid = TRUE AND g.archived = FALSE AND g.is_voided = FALSE
),
last_quarter AS (
    SELECT brand_group AS brand_name,
        CASE WHEN LAST_DAY(DATE_TRUNC('QUARTER', DATEADD('QUARTER', -:q, CURRENT_DATE)), 'QUARTER')
                  - MAX(label_print_utc_date) > 30 THEN 'Churned last quarter'
             WHEN MIN(label_print_utc_date) >= DATE_TRUNC('QUARTER', DATEADD('QUARTER', -:q, CURRENT_DATE))
                  THEN 'New brand added last quarter'
             ELSE 'Actively shipping brand last quarter' END AS status_last_quarter
    FROM base
    WHERE label_print_utc_date <= LAST_DAY(DATE_TRUNC('QUARTER', DATEADD('QUARTER', -:q, CURRENT_DATE)), 'QUARTER')
    GROUP BY 1
),
prev_quarter AS (
    SELECT brand_group AS brand_name,
        CASE WHEN LAST_DAY(DATE_TRUNC('QUARTER', DATEADD('QUARTER', -:q-1, CURRENT_DATE)), 'QUARTER')
                  - MAX(label_print_utc_date) > 30 THEN 'Churned last quarter'
             WHEN MIN(label_print_utc_date) >= DATE_TRUNC('QUARTER', DATEADD('QUARTER', -:q-1, CURRENT_DATE))
                  THEN 'New brand added last quarter'
             ELSE 'Actively shipping brand last quarter' END AS status_prev_quarter
    FROM base
    WHERE label_print_utc_date <= LAST_DAY(DATE_TRUNC('QUARTER', DATEADD('QUARTER', -:q-1, CURRENT_DATE)), 'QUARTER')
    GROUP BY 1
),
statuses AS (
    SELECT lq.brand_name, lq.status_last_quarter,
        CASE WHEN lq.status_last_quarter = 'New brand added last quarter'
                  THEN 'Brands which started shipping previous quarter'
             WHEN pq.status_prev_quarter = 'Churned last quarter'
                  AND lq.status_last_quarter = 'Actively shipping brand last quarter'
                  THEN 'Brands churned but started shipping previous quarter'
             WHEN pq.status_prev_quarter IN ('New brand added last quarter', 'Actively shipping brand last quarter')
                  AND lq.status_last_quarter = 'Actively shipping brand last quarter'
                  THEN 'Brands continued shipping into previous quarter'
             WHEN pq.status_prev_quarter = 'Churned last quarter'
                  AND lq.status_last_quarter = 'Churned last quarter' THEN 'Already churned exclude'
             WHEN pq.status_prev_quarter IS NOT NULL AND lq.status_last_quarter = 'Churned last quarter'
                  THEN 'Brands continued shipping then churned previous quarter'
             ELSE 'New brands churned previous quarter' END AS actions_status
    FROM last_quarter lq LEFT JOIN prev_quarter pq ON lq.brand_name = pq.brand_name
),
quarterly_board_numbers AS (
    SELECT status_last_quarter, actions_status, COUNT(DISTINCT brand_name) AS number_brands
    FROM statuses GROUP BY ALL
)
SELECT * FROM quarterly_board_numbers
UNION ALL
SELECT 'Brands shipping at end of quarter', 'Brands shipping at end of quarter', SUM(number_brands)
FROM quarterly_board_numbers
WHERE actions_status IN ('Brands which started shipping previous quarter',
                         'Brands continued shipping into previous quarter',
                         'Brands churned but started shipping previous quarter');

Output columns: status_last_quarter ("Status Selected Quarter"), actions_status ("Actions Status"),
number_brands ("Number Brands").

FILTERS (sidebar)
- "Status Selected Quarter" multi-select, default All.
- "Actions Status" multi-select, DEFAULT = everything except 'Already churned exclude'.

WIDGETS
1. Text tile: "You have selected to preview data for Q{quarter} {year} against the previous quarter", where
   quarter/year = the quarter of DATEADD('quarter', -:q, CURRENT_DATE).
2. "Number of Brands per Status Last Quarter and Action Status" — horizontal bar chart / bar-in-table.
   Rows: Status Selected Quarter, Actions Status. Bar length + label: SUM(number_brands).
   Sort by SUM(number_brands) descending (so "Brands shipping at end of quarter" is first).
3. "Proportion of Brands per Status Last Quarter" — one pie chart per Status Selected Quarter value, side by side
   in this order: Brands shipping at end of quarter, Actively shipping brand last quarter, Churned last quarter,
   New brand added last quarter. Slices = Actions Status, slice size and label = SUM(number_brands),
   pie size proportional to the status total. Tooltip: share of the slice within its pie, as %.
   Use one consistent color per Actions Status across both widgets, with a legend.
HEADER WIDGET — "Data Update Time": query run time.
```

---

## Prompt 5 — Billing Net Terms

```text
Build a dashboard page called "Billing Net Terms".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__BILLING_NET_TERMS
(columns "Customer Name", "Customer ID", "Net Term", "Last Updated" — double-quote them).
Keep only the latest record per customer: rows where "Last Updated" = MAX("Last Updated") over the same
"Customer Name". Exclude rows where "Customer Name" IS NULL.

FILTERS: "Customer Name" (multi-select, searchable, default All), "Net Term" (multi-select, default All).
HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS").

MAIN WIDGET — table
Columns: "Customer Name", "Last Updated" (MM/DD/YYYY), "Net Term" (integer, days).
Sort by "Customer Name" ascending. Exportable.
```

---

## Prompt 6 — Billing Inaccuracies per Month

```text
Build a dashboard page called "Billing Inaccuracies per Month".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__INVOICE_AND_COMPLIANCE_METRICS (double-quote
column names). One row per invoice-issue month (PST). "Ratio" is the voided-invoice ratio stored as 0–100.

FILTERS: "Invoice Issue Year PST" (multi-select, default All), "Invoice Issue Month PST" (multi-select, default All).
HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS").

MAIN WIDGET — vertical bar chart (full width)
X axis: "Invoice Issue Year Month PST", chronological.
Y axis: "Percentage of Voided Invoices" = SUM("Ratio") / 100, formatted as % with 2 decimals.
Data labels on each bar (rotated if crowded). Single color.
Tooltip: "Total Invoices" = SUM("Total Invoices"), "Total Voided Invoices" = SUM("Total Voided Invoices").
```

---

## Prompt 7 — Duty & Tax Discrepancy per Month

```text
Build a dashboard page called "Duty & Tax Discrepancy per {Time Interval}".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__DUTY_TAX_DISCREPANCY_REPORT (double-quote column
names). Always SUM the measures.
SUBTITLE (static): "Discrepancies are calculated by deducting charged values by vendors from invoiced values."
HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS").

CONTROLS
1. "Label Print Date Selection" on "Label Print Date UTC": Last 7 Days | Last 30 Days (DEFAULT) | Last 90 Days |
   Year to Date | Custom Dates (Start/End pickers only for Custom; inclusive; ends today).
2. "Time Interval": Year | Quarter | Month (DEFAULT) | Week | Day, using the precomputed columns
   "Label Print Year UTC" | "Label Print Year Quarter UTC" | "Label Print Year Month UTC" |
   "Label Print Year Week UTC" | "Label Print Date UTC".
3. "Metric" single-select (DEFAULT = Duty and Tax Wo Clearance Discrepancy):
     Invoiced Duty W Clearance            → "Invoiced Duty USD"
     Invoiced Duty Wo Clearance           → "Invoiced Duty Wo Clearance USD"
     Invoiced Tax W Clearance             → "Invoiced Tax USD"
     Invoiced Tax Wo Clearance            → "Invoiced Tax Wo Clearance USD"
     Charged Duty                         → "Charged Duty USD"
     Charged Tax                          → "Charged Tax USD"
     Duty W Clearance Discrepancy         → "Duty With Clearance Discrepancy"
     Duty Wo Clearance Discrepancy        → "Duty Wo Clearance Discrepancy"
     Tax W Clearance Discrepancy          → "Tax With Clearance Discrepancy"
     Tax Wo Clearance Discrepancy         → "Tax Wo Clearance Discrepancy"
     Duty and Tax W Clearance Discrepancy → "Duty and Tax With Clearance Discrepancy"
     Duty and Tax Wo Clearance Discrepancy→ "Duty and Tax Wo Clearance Discrepancy"
4. Multi-select filters, default All: "Brand Name", "3PL Name", "Passport Invoice Service Name",
   "Destination Country ISO".

WIDGET 1 — "Duty and Tax Summary by {Time Interval}" (table)
Rows: the 12 measures, in the order listed above (use the column names as row labels).
Columns: time-interval buckets, oldest → newest. Values: SUM. $#,##0.00.

WIDGET 2 — "{Metric} by {Time Interval}" (vertical bar chart, full width)
X: time-interval bucket. Y: SUM(selected metric). Data labels $#,##0.00.
Tooltip: "Growth Rate" = (this bucket − previous bucket) / previous bucket, as %.
```

---

## Prompt 8 — Customers Charged Non-5% Default Fee

```text
Build a dashboard page called "Customers Charged Non-5% Default Fee".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__CUSTOMERS_CHARGED_NON_DEFAULT_FEE
(columns "Clearance Type", "Brand Name", "Merchant Tax Registration Zone", "Passport Tax" — double-quote them).
"Passport Tax" is a percentage stored as 0–100.

FILTERS: "Brand Name", "Clearance Type", "Merchant Tax Registration Zone" — multi-select, default All.
HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS").

MAIN WIDGET — crosstab
Rows: "Brand Name", "Clearance Type". Columns: "Merchant Tax Registration Zone".
Cell value: SUM("Passport Tax") / 100, formatted as % with 2 decimals. Blank when no value.
Sort rows by "Brand Name" ascending. Exportable.
```

---

### Notes for review (not part of the prompts)
- **Data Update Time**: in Tableau every page shows the extract refresh time. The prompts use
  `MAX(DBT_UPDATED_UTC_TS)` instead, which is the time the dbt model last ran.
- **PG Metrics date**: in Tableau this page's date filter points at `Passport Shipping Invoice Issue Date`,
  but the revenue-model table has no such column. I used `DATE_VALUE`, which is the invoice date in an
  invoice-based model. Check the totals against Tableau.
- **Quarterly Board Numbers** reads a staging table (`PROD_STAGING_DB…dim__aurora_passport_merchant`) and
  hard-codes the Emerging Brands client ID and the SCP 3PL ID. A dbt model would be a better home for this logic.
  The SQL in the prompt is the Tableau SQL with the repeated `CASE` moved into a `base` CTE. Its results
  should be identical.
- **Pie tooltip**: in Tableau, "% of total" divides by the grand total, which includes the summary row
  "Brands shipping at end of quarter". That double-counts brands. The prompt asks for the share within each
  pie instead.
- **Billing Inaccuracies**: Tableau's saved year filter hides 2026. The prompt defaults to All.
- **Metric labels**: the Tableau metric value "Gross Revenue" is displayed as "Gross Sales". The prompts
  use "Gross Sales".
- The Tableau `Welcome Page` is only static text and was not migrated.
