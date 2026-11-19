# 06_Finance Vendor Invoice Breakout — migration prompts

Source workbook: Tableau `03_Finance / 06_Finance Vendor Invoice Breakout` (~2.1k views).
Purpose: shipment-level vendor (carrier/broker) invoice data for Finance's itemization process.
Single source table: `PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__INVOICE_VENDOR_BREAKDOWN_REPORT__LAST_190D`
(holds the last 190 days only).

Paste each prompt below into the new platform's agent as-is. One prompt = one dashboard page.

---

## Prompt 1 — Itemization Dashboard (By Shipment)

```text
Build a dashboard page called "Itemization Dashboard (By Shipment)".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__INVOICE_VENDOR_BREAKDOWN_REPORT__LAST_190D.
Column names contain spaces and mixed case, so always double-quote them in SQL (e.g. "Brand Name", "3PL Name").
One row = one vendor invoice record line for one shipment. Do not deduplicate.

SUBTITLE (static text under the title)
"This dashboard view presents raw data as originally ingested (includes archived shipments and does not account
for replacement of values). Use this view only for itemization processes."

HEADER WIDGET — "Data Update Time"
Single value: MAX("DBT_UPDATED_UTC_TS"), formatted as date + time. Top-right corner.

GLOBAL FILTERS (left sidebar, apply to every widget)
1. "Invoice Ingestion Date Selection" — single-select preset on "Invoice External Parsed Date":
   Last 7 Days | Last 30 Days (DEFAULT) | Last 90 Days | Year to Date | Custom Dates.
   Last N days = parsed date between CURRENT_DATE - N and CURRENT_DATE (inclusive).
   Year to Date = YEAR(parsed date) = YEAR(CURRENT_DATE).
   Custom Dates shows two date pickers "Custom Start Date" / "Custom End Date" (inclusive); hide them otherwise.
2. "Invoice External Issuer" — single-select dropdown, default "ECMS".
3. "Invoice External ID" — multi-select, default All.
4. "Invoice External Number" — multi-select, default All.
5. "Invoice External Filename" — multi-select, default All.
6. "3PL Name" — multi-select, default All.
7. "Brand Name" — multi-select, default All.
8. "Invoice External Tracking Code Excel" — multi-select / search box, default All.
9. "Passport Tracking Code Excel" — multi-select / search box, default All.
10. "Last Mile Tracking Code Excel" — multi-select / search box, default All.
11. "Is Canada Domestic Shipment" — True / False / All, default All.
12. "Is Present in Shipment Charge" — True / False / All, default All.

MAIN WIDGET — detail table "Vendor Invoice by Shipment" (full width, scrollable, exportable to CSV/Excel)
One row per record. Columns in this exact order (numeric columns are SUMs at row grain, i.e. the raw value):
 1. Row # (running row number)
 2. "Shipment is Voided or Archived"
 3. "Invoice External ID"
 4. "Invoice External Issuer"
 5. "Invoice External Number"
 6. "Invoice External Filename"
 7. "Invoice External Parsed Status"
 8. "Invoice External Parsed Date"
 9. "3PL Name"
10. "Brand Name"
11. "Service Level Full Name"
12. "Consolidator Name"
13. "Invoice External Record Parsed Status"
14. "Invoice External Record ID"
15. "Invoice External Billable Weight Oz"
16. "Shipping Charge USD"
17. "Fuel Surcharge USD"
18. "Misc Surcharge USD"
19. "Duty Charge USD"
20. "Tax Charge USD"
21. "Total Ingested USD"
22. "Return Charge USD"
23. "Local Currency"
24. "Shipping Charge Local Currency"
25. "Fuel Surcharge Local Currency"
26. "Misc Surcharge Local Currency"
27. "Duty Charge Local Currency"
28. "Tax Charge Local Currency"
29. "Total Ingested Local Currency"
30. "Return Charge Local Currency"
31. "Misc Surcharge 1 Local Currency"
32. "Misc Surcharge 1 Description"
33. "Misc Surcharge 2 Local Currency"
34. "Misc Surcharge 2 Description"
35. "Misc Surcharge 3 Local Currency"
36. "Misc Surcharge 3 Description"
37. "Invoice External Tracking Code Excel"
38. "Passport Tracking Code Excel"
39. "Last Mile Tracking Code Excel"
40. "Is Canada Domestic Shipment"
41. "Label Print UTC Date"
42. "Passport Shipping Invoice Issue Date"
43. "Invoice External Issue Date"
44. "Passport Shipping Invoice Number"
45. "GST Amount"
46. "HST Amount"
47. "PST Amount"
48. "Sender Name"
49. "Sender Contact Name"
50. "Is Present in Shipment Charge"
51. "Quickbooks Customer ID"
52. "Quickbooks Customer Name"
Formatting: USD columns as currency with 2 decimals ($#,##0.00); local-currency columns as numbers with 2
decimals; dates as MM/DD/YYYY; tracking codes as text (never as numbers — leading zeros must be kept).
Default sort: "Invoice External ID", then "Invoice External Record ID".
```

---

## Prompt 2 — Itemization Dashboard (By Invoice)

```text
Build a dashboard page called "Itemization Dashboard (By Invoice)".

DATA SOURCE
Snowflake table PROD_ANALYTICS_DB.FINANCE_SCHEMA.NLT__FINANCE__INVOICE_VENDOR_BREAKDOWN_REPORT__LAST_190D.
Column names contain spaces and mixed case, so always double-quote them in SQL.

SUBTITLE (static text)
"This dashboard view presents raw data as originally ingested (includes archived shipments and does not account
for replacement of values). Use this view only for itemization processes."

HEADER WIDGET — "Data Update Time": MAX("DBT_UPDATED_UTC_TS") as date + time, top-right.

GLOBAL FILTERS (left sidebar)
1. "Invoice Ingestion Date Selection" on "Invoice External Parsed Date": Last 7 Days | Last 30 Days (DEFAULT) |
   Last 90 Days | Year to Date | Custom Dates (with "Custom Start Date" / "Custom End Date" pickers shown only
   when Custom Dates is selected; all ranges inclusive and end at today).
2. "Invoice External Issuer" — single-select, default "DIRECTLINK".
3. "Invoice External ID" — multi-select, default All.
4. "Invoice External Number" — multi-select, default All.
5. "Invoice External Filename" — multi-select, default All.
6. "3PL Name" — multi-select, default All.
7. "Brand Name" — multi-select, default All.

MAIN WIDGET — aggregated table "Vendor Invoice by Invoice" (full width, exportable)
Group by, in this order:
  "Invoice External ID", "Invoice External Issuer", "Invoice External Number", "Invoice External Filename",
  "Invoice External Parsed Status"
Measures, in this order:
  Shipments = COUNT(DISTINCT "Shipment ID")
  SUM("Shipping Charge USD"), SUM("Fuel Surcharge USD"), SUM("Misc Surcharge USD"), SUM("Duty Charge USD"),
  SUM("Tax Charge USD"), SUM("Total Ingested USD"), SUM("Return Charge USD"),
  SUM("Shipping Charge Local Currency"), SUM("Fuel Surcharge Local Currency"), SUM("Misc Surcharge Local Currency"),
  SUM("Duty Charge Local Currency"), SUM("Tax Charge Local Currency"), SUM("Total Ingested Local Currency"),
  SUM("Return Charge Local Currency"), SUM("Misc Surcharge 1 Local Currency"),
  SUM("Misc Surcharge 2 Local Currency"), SUM("Misc Surcharge 3 Local Currency")
Add a leading Row # column. USD as $#,##0.00, local currency as #,##0.00.
Default sort: "Invoice External ID" ascending.
```

---

### Notes for review (not part of the prompts)
- The default issuer differs per page in Tableau (ECMS on By Shipment, DIRECTLINK on By Invoice). That's a saved
  filter state, not necessarily intended — confirm with Finance which default they want.
- The By Invoice table mixes currencies when one invoice has several "Local Currency" values; same as Tableau today.
- The Tableau `Welcome Page` is only static text and was not migrated.
