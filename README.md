# Dubai Residential Real Estate: End-to-End Analytics Pipeline

**Bulk CSV → Python ETL → MySQL star schema → Power BI dashboard**

![Python](https://img.shields.io/badge/Python-pandas-3776AB?style=for-the-badge&logo=python&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-Star_Schema-4479A1?style=for-the-badge&logo=mysql&logoColor=white) ![Power BI](https://img.shields.io/badge/Power_BI-DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

An end-to-end analytics system built on Dubai Land Department (DLD) transaction data. The full bulk export (907,687 rows) is cleaned down to 238,267 residential sales (1 Jan 2024 to 6 Nov 2026), modelled as a star schema in MySQL and explored through a two-page Power BI dashboard.

> **Latest update (Nov 2026):** the dashboard has been redesigned and the warehouse refreshed. The report now has Status, Year and Property Type slicers, year-over-year growth cards, a dual-axis volume and price trend, an off-plan vs resale premium table, and a drill-through page for the top 10 areas. Coverage now runs to 6 November 2026. Details below.

## At a glance

| | |
|---|---|
| **Coverage** | Dubai residential sales, 1 Jan 2024 to 6 Nov 2026 |
| **Raw input** | 907,687 rows × 47 columns (full bulk export, all years) |
| **Cleaned transactions** | 238,267 |
| **Total sales value** | AED 550bn+ |
| **Market-wide median price** | About AED 1,637 / sqft |
| **Model** | 1 fact table, 5 lookup tables, 1 date table |
| **Dashboard** | 2 pages: Overview and Top 10 Areas Details (drill-through) |

## Dashboard preview

**Overview.** Slicers for Property Status, Year and Property Type with a Reset button; KPI cards (leading area, transactions, sales, median price per sqft); monthly transactions against median price per sqft; top 10 areas by transactions; transaction mix by property type; median price per sqft by number of rooms; and the off-plan vs existing premium by year.

<img width="434" height="292" alt="OVER VIEW " src="https://github.com/user-attachments/assets/b013fd4b-0ffb-4f74-b81d-f907ee5fc994" />


**Year-over-year growth.** With no year selected the KPI cards prompt for one. Once a year is chosen, each card shows its change against the prior year.

<img width="445" height="305" alt="2" src="https://github.com/user-attachments/assets/bb7030b3-5f8a-4be5-bb42-159fd7f40c83" />


**Segment recalculation.** Setting Property Type to Unit recalculates the whole page, including the premium table (the off-plan premium over resale on units falls from 44.00% in 2024 to 25.95% in 2026).

<img width="440" height="300" alt="3" src="https://github.com/user-attachments/assets/5f34566d-3ad3-4329-9e4e-46c1a539f5fc" />


**Drill-through: Top 10 Areas Details.** Right-click an area on the overview to open a matrix for that area: transactions, total sales and median price per sqft, split Existing vs Off Plan, expandable from year to quarter to month.

<img width="436" height="291" alt="4" src="https://github.com/user-attachments/assets/3abbbe0c-f119-4d68-acc5-24d09954a447" />


## Investment use case: "Where should AED 20M go?"

Most descriptive dashboards stop at reporting: total transactions, average price, month-over-month trend. This one is built so those numbers can support a decision. Given a fixed budget, where does the data point?

All price figures are median AED per sqft after IQR capping. Figures below come from the dashboard's median price comparison table with the relevant slicers applied, captured at the previous load (237.84K sales, AED 552.09bn); medians move slightly with each refresh.

### 1. Segment before looking at a single area

Off-plan and existing (resale) transactions behave like two different markets, so Property Status is the first slicer.

| Segment | 2024 | 2025 | 2026 | 2024 → 2026 |
|---|---|---|---|---|
| Existing (resale) | 1,233.84 | 1,374.89 | 1,423.53 | **+15.4%** |
| Off-plan | 1,689.08 | 1,807.21 | 1,771.61 | **+4.9%** |
| Off-plan premium over resale | 36.90% | 31.44% | 24.45% | |

Resale prices rose about three times faster than off-plan, and off-plan median price per sqft slipped about 2% from 2025 to 2026 while resale kept climbing.

One level down, the picture sharpens:

| By property type | 2024 | 2026 | Change |
|---|---|---|---|
| Resale units | 1,235.19 | 1,403.36 | **+13.6%** |
| Off-plan units | 1,778.62 | 1,767.57 | **−0.6%** |
| Resale villas | 1,211.78 | 1,465.97 | **+21.0%** |
| Off-plan villas | 1,390.51 | 1,814.77 | **+30.5%** |

Off-plan unit pricing is flat; the off-plan gain in the blended number comes from villas. For units the off-plan premium compressed from 44.00% to 25.95%, while for villas it widened from 14.75% to 23.79% (it was 7.37% in 2025, so check transaction counts before reading villa movements as a trend). A single blended number would have hidden all of this.

### 2. Find where momentum actually is

The Leading Area card is DAX-driven and responds to every slicer. Across the full window Al Barsha South Fourth leads with 21,606 transactions, and it also leads within both Existing (7,081) and Off-Plan (14,525). Set the view to Off-Plan and Year = 2026 and the lead moves to Madinat Al Mataar (6,800 transactions): newer supply is taking the volume, not just the established area.

### 3. Weigh volume against price

The Top 10 Areas chart sets volume beside price. After Al Barsha South Fourth, the next three by transactions are Madinat Al Mataar (15,487), Wadi Al Safa 5 (13,399) and Business Bay (12,983). Business Bay's median is AED 2,417 / sqft on AED 32.97bn of sales, about 48% above the market-wide median of AED 1,637, so volume and price point in different directions depending on the budget.

### 4. Pick the right configuration

Median price per sqft by number of rooms runs from AED 1,825 for penthouses and AED 1,766 for 2-bedrooms down to AED 1,022 for 6-bedrooms and AED 917 for 7-bedrooms. That chart mixes property types, so the large-bedroom end reflects the villa and building mix as well as size. Filter by Property Type before comparing configurations. Units account for 85.58% of all transactions.

## What this is and isn't

It doesn't output a single "buy here" answer, and it isn't meant to; that call belongs to the investor and their advisors, and nothing here is investment advice. What it does is compress a question that would otherwise mean pulling raw DLD data and cross-referencing it by hand into a filter-driven walkthrough, and it forces the market to be segmented properly (off-plan vs resale, unit vs villa, complete vs partial periods) before any trend line gets trusted.

Read the latest month with care. The data runs to 6 November 2026, so November holds only a few days and the final point on the monthly trend shows as a sharp drop. 2026 is also a partial year: because the growth measures use `SAMEPERIODLASTYEAR`, the 2026 cards compare against the same dates in 2025 rather than the full prior year.

## What changed in the dashboard (v1 → v2)

| | v1 (Oct 2026) | v2 (Nov 2026) |
|---|---|---|
| Layout | Light grey report, two pages | Navy and gold executive layout, two pages |
| Slicers | Status, Year | Property Status, Year, Property Type, plus a Reset button |
| KPI cards | Total transactions and sales; headline sentence | Leading area, transactions, sales and median price per sqft, each with year-over-year growth once a year is picked |
| Trend | Month-over-month transactions | Monthly transactions and median price per sqft on one dual-axis chart |
| Segment comparison | Status slicer only | Off-plan vs existing premium table by year, recalculating with the Year and Property Type slicers |
| Areas | Bing Maps visual | Top 10 bar chart plus a drill-through page (year → quarter → month, Existing vs Off Plan) |
| Measure label | "Avg Price per SqFt" (computed as a median) | "Median Price per SqFt" |
| Metro / mall comparison | On a dedicated page | Removed from the report; the `has_nearest_*` flags remain in the fact table |

## From API to bulk CSV: what changed and why

The pipeline was originally built against the DLD Open Data API (OAuth2, watermark-based delta loading). While validating 2026 coverage I profiled the date range of the extract and found that the endpoint is a test/sandbox environment: the data is valid and well-formed, but only covers January 2024 to December 2025.

Rather than stitching two partial sources together, I downloaded the entire historical transaction export as one bulk CSV from the data.dubai portal and rebuilt the warehouse from that single source. The key design choice: the file is not pre-filtered by hand. The ETL itself keeps residential sales dated 2024 onward, so the whole path from raw file to warehouse is one reproducible script. The same date filter also removes legacy rows with impossible dates (the earliest parsed date in the raw export is in the year 1416).

The CSV uses the same schema as the original API extract, so cleaning, feature engineering and loading logic stayed the same. The API extraction code (OAuth2, watermark delta-load) is still in the repo; it is the intended path for automated incremental refreshes once the account has access to a live (non-sandbox) feed.

The refresh is repeatable. Consecutive runs against re-downloaded exports:

| Run | Latest transaction date | Raw rows | Cleaned residential sales |
|---|---|---|---|
| Run 1 | 17 Sep 2026 | 892,125 | 230,038 |
| Run 2 | 2 Oct 2026 | 898,413 | 232,685 |
| Run 3 (latest) | 6 Nov 2026 | 907,687 | 238,267 |

## Architecture

<img width="1396" height="598" alt="00-architecture" src="https://github.com/user-attachments/assets/1e609b98-fc5b-481f-ab65-3d99ad997e73" />


## Pipeline walkthrough

### Phase 1: Extraction

**Current path: full bulk CSV reload**

- Reads the complete data.dubai transaction export (all years and all transaction types)
- Reports the date range it received before anything is filtered

**API path (implemented, inactive)**

- Authenticates with the OAuth2 client-credentials flow; credentials live in a `.env` file
- Watermark-based delta loading: reads the maximum `instance_date` from the existing master file and pulls only newer records, cutting sync time from ~60 minutes to under 5 seconds
- WAF-compliant headers and a 50-minute token-lifespan guard for long extractions
- Paginates in descending date order and stops the moment it overlaps with existing data

### Phase 2: Transformation

**The funnel (latest run, 6 Nov 2026)**

| Stage | Rows |
|---|---|
| Raw bulk export (all years, all usages and transaction types) | 907,687 |
| Dated 2024-01-01 or later | 336,156 |
| Residential sales only (shops and offices excluded) | 239,175 |
| Duplicate `transaction_id` rows found | 0 |
| Excluded by price/sqft market bounds | 908 (0.4%) |
| Valid rows loaded | 238,267 |
| Of those, capped to IQR fences (kept, not dropped) | 7,189 (3.0%) |

```
Raw data shape: (907687, 47)
max transaction date in raw data: 2026-11-06 00:00:00
min transaction date in raw data: 1416-07-02 00:00:00
Number of transactions from 2024-01-01 onwards: 336156
Number of transactions from 2024-01-01 onwards after Residential filter: 239175
Number of duplicate rows in raw data: 0

1. Rows Analyzed:           239175
2. Rows Forensically Saved: 0
3. Broken Rows Excluded:    908
4. Valid Rows Remaining:    238267
5. Luxury Outliers Capped:  7189
```

**Step 1: Clean and filter**

- Drops Arabic-language columns, party-count columns, `load_timestamp`, and columns that are empty for sales (`rent_value`, `meter_rent_price`)
- Drops English name columns that already live in lookup tables (area, property type and sub-type, procedure, registration type)
- Keeps Residential usage and Sales transaction group; excludes Shop and Office room types
- Parses `instance_date` and keeps 2024 onward

**Step 2: Deduplicate, type and handle nulls**

- Deduplicates on `transaction_id`
- Converts ID columns to memory-efficient nullable types (UInt8, UInt16, boolean)
- Fills structural nulls with deterministic rules by `property_type_id`, since the data is residential-only: Land → sub-type 6 (Residential Land), rooms "land", building "empty land"; Building → sub-type 5 (Residential Building), rooms "whole building", building "Independent Building"; Villa → sub-type 4, building "Villa"
- Properties outside any project get `project_number` 0 and "Independent Property" for project and master project
- Imputes missing rooms for villas and units by nearest-median-area matching: computes the median `procedure_area` for each known room category within the property type, then assigns each null row the category whose median is closest to its area

**Step 3: Standardise and engineer features**

- Cleans rooms labels (removes "B/R", maps "Single Room" to 1, title-cases)
- Turns `nearest_metro`, `nearest_landmark` and `nearest_mall` into boolean flags (`has_nearest_*`)
- Converts area from m² to sqft (× 10.7639) and derives `price_per_sqft`

**Step 4: Price-per-sqft quality gates**

- Market bounds by property type (AED/sqft): Unit 300–15,000 · Villa 400–10,000 · Land 50–5,000 · Building 300–5,000
- Recovery pass: flagged rows get `price_per_sqft` recalculated from price and area before being discarded. On this dataset it recovers 0 rows, because `price_per_sqft` is itself derived from those two columns earlier in the pipeline. It works as a guard against upstream arithmetic errors, not as a source of rescued rows.
- IQR capping: Tukey fences (1.5 × IQR) per property type clip extreme values into `price_per_sqft_capped`, which the dashboard uses

**Dimension table generation**

All five lookup tables share one normalisation pattern: select the ID and label columns, `drop_duplicates()`, reset the index. Nulls are handled deliberately rather than silently dropped: ID columns are filled with 0 (an explicit "unknown" key) and label columns with "not provided", so every foreign key in the fact table always resolves to a row in its dimension table.

```python
property_sub_type_lookup = (
    data[['property_sub_type_id', 'property_sub_type']]
    .drop_duplicates(keep='first')
    .reset_index(drop=True)
)

property_sub_type_lookup['property_sub_type_id'] = property_sub_type_lookup['property_sub_type_id'].fillna(0)
property_sub_type_lookup['property_sub_type'] = property_sub_type_lookup['property_sub_type'].fillna("not provided")

property_sub_type_lookup.to_csv('property_sub_type_lookup.csv', index=False)
```

The same pattern is reused for `lkp_areas`, `lkp_property_types`, `lkp_procedures` and `lkp_statuses`.

### Phase 3: Loading (MySQL data warehouse)

- Connects to a local MySQL instance (`real_estate_db`) through SQLAlchemy
- Loads the cleansed fact table with `if_exists='replace'` for a full refresh
- Loads the five lookup tables only if they do not already exist, so re-runs are safe and never duplicate dimensions

**Enforcing referential integrity**

`pandas.to_sql()` creates columns but doesn't enforce relationships, so the star schema is hardened with a one-time SQL pass: key columns are aligned to matching INT types, each dimension gets an explicit primary key, and the fact table gets a foreign key back to it. A bad load then fails loudly at the database level instead of surfacing weeks later as blank labels in Power BI.

```sql
-- Align dimension and fact key types
ALTER TABLE lkp_areas
MODIFY area_id INT;

ALTER TABLE cleaned_residential_real_estate_sale_data
MODIFY area_id INT;

-- Primary key on the dimension side
ALTER TABLE lkp_statuses
ADD PRIMARY KEY (status_id);

-- Foreign key on the fact side
ALTER TABLE cleaned_residential_real_estate_sale_data
ADD CONSTRAINT fk_fact_status
FOREIGN KEY (status_id) REFERENCES lkp_statuses(status_id);
```

The same pattern (type alignment → primary key → foreign key) is repeated for each of the five dimension tables. Because `replace` drops and recreates the fact table, re-run the type-alignment and foreign-key statements after every full refresh. The dimension primary keys persist; the fact-table constraints do not.

## Data model (star schema)

<img width="410" height="268" alt="05-star-schema-model" src="https://github.com/user-attachments/assets/225ac0e5-54b1-46b0-b8d3-93e35be2921b" />


One fact table (`residential real estate sale data`, loaded from the MySQL fact table) and six dimensions: `Date`, `areas`, `property types`, `property sub types`, `procedures` and `status`. Every relationship is one-to-many from the dimension to the fact table, so each dimension filters the fact table and nothing filters back. Table and column names are tidied for readability inside Power BI (for example `price_per_sqft` appears as `price per sqft`).

**Fact table key columns** (`cleaned_residential_real_estate_sale_data`)

| Column | Type | Description |
|---|---|---|
| `transaction_id` | VARCHAR | Unique transaction identifier |
| `transaction_date` | DATE | Date of the sale |
| `price` | DECIMAL | Total transaction value (AED) |
| `property_size_sqft` | DECIMAL | Property size in square feet |
| `price_per_sqft` | DECIMAL | Derived price per square foot |
| `price_per_sqft_capped` | DECIMAL | IQR-capped version used in visuals |
| `rooms` | VARCHAR | Bedroom category (Studio, 1, 2 … Penthouse, Whole Building, Land) |
| `area_id` | INT | FK → `lkp_areas` |
| `property_type_id` | UINT8 | FK → `lkp_property_types` |
| `property_sub_type_id` | UINT8 | FK → `lkp_property_sub_types` |
| `procedure_id` | UINT16 | FK → `lkp_procedures` |
| `status_id` | BOOLEAN | FK → `lkp_statuses` (Existing / Off-Plan) |
| `has_parking` | BOOLEAN | Parking availability flag |
| `has_nearest_metro` | BOOLEAN | Metro proximity flag |
| `has_nearest_landmark` | BOOLEAN | Landmark proximity flag |
| `has_nearest_mall` | BOOLEAN | Mall proximity flag |

## Power BI measures (DAX)

19 explicit measures, grouped into three display folders in the model: **Prices / SQFT measures**, **Sales Measures** and **Transactions Measures**. The year-over-year indicators return "Select year for YoY growth" unless exactly one year is selected, and compare against the same dates in the prior year using `SAMEPERIODLASTYEAR`. The `Existing Median` and `Off-plan Median` measures override the Status filter on purpose, so the premium table on the overview always shows both segments side by side.

### Prices / SQFT measures

```dax
Median Price per SqFt = MEDIAN('residential real estate sale data'[price per sqft])

Existing Median =
CALCULATE(
    [Median Price per SqFt],
    'status'[status] = "Existing"
)

Off-plan Median =
CALCULATE(
    [Median Price per SqFt],
    'status'[status] = "Off plan"
)

Off Plan vs Existing % =
VAR OffPlan = [Off-plan Median]
VAR Exist   = [Existing Median]
RETURN
    DIVIDE(OffPlan - Exist, Exist)

Previous Year Median Price =
CALCULATE(
    [Median Price per SqFt],
    SAMEPERIODLASTYEAR('Date'[Date])
)

Median Growth vs PY % =
DIVIDE(
    [Median Price per SqFt] - [Previous Year Median Price],
    [Previous Year Median Price]
)

Median Growth Indicator =
IF(
    HASONEVALUE('Date'[Year]),

    VAR Growth = [Median Growth vs PY %]

    RETURN
        SWITCH(
            TRUE(),
            ISBLANK(Growth), "No prior-year data",
            Growth > 0, UNICHAR(9650) & FORMAT(Growth, "0.00%") & " " & "VS PY",
            Growth < 0, UNICHAR(9660) & " " & FORMAT(Growth, "0.00%") & " " & "VS PY",
            UNICHAR(8212) & " 0.00%"
        ),

    "Select year for YoY growth"
)
```

### Sales Measures

```dax
Total Sales (AED) = CALCULATE(SUM('residential real estate sale data'[price]))

Previous Year Sales =
CALCULATE(
    [Total Sales (AED)],
    SAMEPERIODLASTYEAR('Date'[Date])
)

Sales Growth vs PY % =
DIVIDE(
    [Total Sales (AED)] - [Previous Year Sales],
    [Previous Year Sales]
)

Sales Growth Indicator =
IF(
    HASONEVALUE('Date'[Year]),

    VAR Growth = [Sales Growth vs PY %]

    RETURN
        SWITCH(
            TRUE(),
            ISBLANK(Growth), "No prior-year data",
            Growth > 0, UNICHAR(9650) & FORMAT(Growth, "0.00%") & " " & "VS PY",
            Growth < 0, UNICHAR(9660) & " " & FORMAT(Growth, "0.00%") & " " & "VS PY",
            UNICHAR(8212) & " 0.00%"
        ),

    "Select year for YoY growth"
)
```

### Transactions Measures

```dax
Total_Transactions = DISTINCTCOUNT('residential real estate sale data'[transaction_id])

Last Month Transactions =
CALCULATE(
    [Total_Transactions],
    DATEADD('Date'[Date], -1, MONTH)
)

MoM Transactions Growth % =
VAR TransactionsLastMonth = [Last Month Transactions]
RETURN
    DIVIDE(
        [Total_Transactions] - TransactionsLastMonth,
        TransactionsLastMonth
    )

Previous Year Transactions =
CALCULATE(
    [Total_Transactions],
    SAMEPERIODLASTYEAR('Date'[Date])
)

Transactions Growth vs PY % =
DIVIDE(
    [Total_Transactions] - [Previous Year Transactions],
    [Previous Year Transactions]
)

Transactions Growth Indicator =
IF(
    HASONEVALUE('Date'[Year]),

    VAR Growth = [Transactions Growth vs PY %]

    RETURN
        SWITCH(
            TRUE(),
            ISBLANK(Growth), "No prior-year data",
            Growth > 0, UNICHAR(9650) & FORMAT(Growth, "0.00%") & " " & "VS PY",
            Growth < 0, UNICHAR(9660) & " " & FORMAT(Growth, "0.00%") & " " & "VS PY",
            UNICHAR(8212) & " 0.00%"
        ),

    "Select year for YoY growth"
)

-- Leading area card: top area by transactions in the current filter context
-- (ties broken alphabetically so the card never returns two names)
Leading Area =
VAR AreaRanking =
    TOPN(
        1,
        ADDCOLUMNS(
            VALUES(areas[area_name]),
            "TransactionCount", [Total_Transactions]
        ),
        [TransactionCount], DESC,
        areas[area_name], ASC
    )
RETURN
    CONCATENATEX(AreaRanking, areas[area_name], ", ")

Leading Area Transactions =
VAR AreaRanking =
    TOPN(
        1,
        ADDCOLUMNS(
            VALUES(areas[area_name]),
            "TransactionCount", [Total_Transactions]
        ),
        [TransactionCount], DESC,
        areas[area_name], ASC
    )
RETURN
    MAXX(AreaRanking, [TransactionCount])
```

## Project structure

```
├── etl_pipeline.py                 # Main ETL script (extract → transform → load)
├── lkp_areas.csv                   # Area dimension lookup
├── lkp_property_sub_types.csv      # Property sub-type lookup
├── lkp_property_types.csv          # Property type lookup
├── lkp_statuses.csv                # Status (Existing / Off-Plan) lookup
├── lkp_procedures.csv              # Procedure type lookup
├── images/                         # Dashboard screenshots used in this README
├── .env                            # Credentials (gitignored)
├── .gitignore
└── README.md
```

## Setup and usage

**Prerequisites:** Python 3.9+, MySQL 8.0+ running locally, Power BI Desktop.

**1. Install dependencies**

```bash
pip install pandas numpy sqlalchemy pymysql python-dotenv requests
```

**2. Create the database and credentials**

```sql
CREATE DATABASE real_estate_db;
```

Create a `.env` file in the project root (the DLD values are only needed for the API path):

```
MYSQL_PASSWORD=your_mysql_password
DLD_CLIENT_ID=your_client_id
DLD_CLIENT_SECRET=your_client_secret
DLD_APP_IDENTIFIER=your_app_identifier
```

**3. Get the data**

Download the complete transaction export as a bulk CSV from the data.dubai open-data portal and point the script at it. No manual filtering is needed; the ETL keeps residential sales from 2024 onward.

**4. Run the pipeline**

```bash
python etl_pipeline.py
```

**5. Connect Power BI**

Power BI Desktop → Get Data → MySQL Database → `localhost` / `real_estate_db` → load the fact table and all lookup tables → apply the DAX measures above.

**Refresh runbook**

1. Download the latest full export and replace the local CSV
2. Run `python etl_pipeline.py` (rebuilds the fact table; lookups are only created if missing)
3. Re-run the type-alignment and foreign-key SQL (see Phase 3)
4. Refresh the Power BI model

## Key engineering decisions

**Why reload from a bulk CSV instead of patching in 2026?** The API turned out to be a sandbox scoped to 2024–2025, a limitation that isn't documented up front and only surfaced once I profiled the returned date ranges. Reconciling two partial, independently sourced ranges invites subtle inconsistencies. One internally consistent source beats stitching two together.

**Why filter inside the ETL instead of pre-filtering the file?** The raw export stays untouched and the whole raw-to-warehouse path lives in one script, so anyone can reproduce the warehouse from the download alone. The same date filter also drops legacy rows with impossible dates.

**Why keep the API code?** It is tested, working, and the right tool for incremental refreshes once a live feed is available. Delta loading keeps sync time under 5 seconds regardless of dataset size.

**Why MEDIAN instead of AVERAGE for price per sqft?** Dubai's luxury segment produces extreme high-end outliers. MEDIAN resists them and represents the typical market participant; the IQR-capped column is a second safety net.

**Why a star schema instead of a flat table?** Dimension tables decouple descriptive attributes from the fact table, reduce storage, and keep Power BI relationships clean. Adding a new area or property type means updating one lookup table, not reloading the fact table.

**Why add primary and foreign keys after the load?** `to_sql()` will happily create a fact table whose `area_id` doesn't match anything in `lkp_areas`. Explicit constraints turn "these columns are supposed to match" into something MySQL rejects if violated.

**Why impute instead of drop?** Many nulls are structural (land has no rooms, a villa isn't a building). Rule-based fills and nearest-median-area matching keep valid sales in the dataset instead of discarding them.

**Why explicit "unknown" members in dimensions?** Filling IDs with 0 and labels with "not provided" guarantees that every fact row joins, so nothing disappears silently from a visual.

## How this was built

I used AI assistants (Gemini, Claude and ChatGPT) every day, from my first day of learning through building this project: to explain concepts, draft and debug code, and pressure-test my reasoning. Because of that, the pipeline is built so its output never rests on trust in any single tool: row counts are reported at every stage of the funnel, the date range is profiled before filtering, and the star schema's primary and foreign keys are enforced by MySQL rather than assumed.

This project is on its fourth iteration. Each pass applies something new from my Microsoft PL-300 (Power BI Data Analyst) preparation: the star-schema model with hidden keys, a dedicated Date table, time-intelligence measures, display folders and the drill-through page.

## Known limitations and next steps

- **Latest month is partial.** Data runs to 6 November 2026; the final point on the monthly trend is incomplete.
- **Date table range.** The current-year growth cards compare like with like only while the `Date` table ends at the latest transaction date, so check it after each refresh.
- **Manual refresh.** The dashboard is a Power BI Desktop file on a local MySQL instance and is not yet published to Power BI Service. Next step: publish with a scheduled refresh.
- **Constraints after full refresh.** `if_exists='replace'` recreates the fact table, which drops its foreign keys. Switching to truncate-and-append would let the constraints survive each refresh.
- **Incremental loading.** The watermark-based API path is ready for when a live (non-sandbox) feed is available.
- **Thin segments.** The dashboard shows medians but not group sizes on every visual, so small segments (for example 6- and 7-bedroom properties, or villa premiums in a single year) need a transaction-count check before they are treated as a signal.

## Data source

- **data.dubai open-data portal:** full historical transaction export (bulk CSV), the current source for the fact table. Filtered to 2024 onward inside the ETL.
- **DLD Open Data API:** test/sandbox endpoint covering January 2024 to December 2025 only. Implemented and functional but not used for the live warehouse. Access requires registration and approval by the DLD integration team; credentials are not included in this repository.

## Author

**Muhammad Abdullah** · Data & BI Analyst · Dubai, UAE
Open to Data / BI Analyst opportunities in the UAE.

[LinkedIn](https://www.linkedin.com/in/muhammad-abdullah-a7861a3a2/) · [GitHub](https://github.com/ak786abdullah)
