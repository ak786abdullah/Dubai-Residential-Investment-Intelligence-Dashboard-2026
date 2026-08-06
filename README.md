# Dubai Residential Real Estate — End-to-End Analytics Pipeline

> **Bulk CSV → Python ETL → MySQL Data Warehouse → Power BI Dashboard**
> A production-grade analytics system built on Dubai Land Department (DLD) transaction data, covering 2024–2026.

---

## Dashboard Preview
<img width="635" height="320" alt="Screenshot 2026-08-05 112117" src="https://github.com/user-attachments/assets/9cb4a4f5-15c1-4ac6-bce9-322276eeac0a" />

*KPI cards, MoM transaction trend, property type breakdown, and avg price/sqft by metro proximity — all driven by a live MySQL connection.*

<img width="624" height="344" alt="Screenshot 2026-08-05 112149" src="https://github.com/user-attachments/assets/26e90d26-c9ad-4a8c-89de-b277b33496f6" />

*Top 10 areas by transaction volume plotted on a Bing Maps visual, with avg price/sqft by property type and room count.*

---

## Project Overview

This project demonstrates a complete data engineering and analytics workflow built entirely from scratch — from data extraction through to an interactive Power BI dashboard.

The pipeline was originally built against the **Dubai Land Department (DLD) Open Data API** (OAuth2 auth, watermark-based delta loading). While validating 2026 coverage, I found that this endpoint is a **test/sandbox environment provided by data.dubai** — it returns valid, well-formed data, but only for the window **January 2024 – December 2025**. It does not expose 2026 transactions at all.

To get complete, accurate coverage across 2024–2026, I downloaded the **entire historical transaction dataset as a single bulk CSV export directly from data.dubai**, and reran the ETL pipeline against that file **instead of the API**. The CSV is normalized to the same schema as the original API extract, so it flows through the exact same cleaning, feature-engineering, and star-schema loading logic — the transform and load phases don't know or care that the input changed.

The API extraction code (OAuth2 auth, watermark delta-load) is **still in the repo and still functional** — it's just not what populated the current warehouse. It's kept as the intended path for automated incremental refreshes once the account has access to a live (non-sandbox) feed.

---

## Architecture

```
Currently used:
data.dubai Bulk CSV (2024–2026, full history)  ──►  Python ETL Pipeline  ──►  MySQL Database  ──►  Power BI Dashboard
                                                       (Pandas / SQLAlchemy)     (Star Schema)        (DAX Measures)

Implemented, not currently active:
DLD REST API (OAuth2, watermark delta-load, 2024–2025 only) ──► same ETL pipeline
```

### Phase 1 — Extraction

**Current run: full-history CSV reload**
- The DLD API is a test/sandbox endpoint capped at December 2025; it does not surface current-year transactions
- The complete historical dataset (2024 through the present) was downloaded directly as a CSV export from the [data.dubai](https://data.dubai) open data portal
- The pipeline was rerun end-to-end against this file in place of the API call, giving a single, internally consistent 2024–2026 dataset

**API path (implemented, available for future incremental syncs)**
- Authenticates against the DLD API using OAuth2 client credentials flow, with token stored securely in a `.env` file
- Implements **watermark-based delta loading**: reads the maximum `instance_date` from the existing master CSV, then pulls only records newer than that date — reducing sync time from ~60 minutes to under 5 seconds when in use
- Includes automatic **WAF-compliant headers** and a configurable **token lifespan guard** (50-minute safe window) to handle long-running extractions without mid-run expiry
- Paginates through results in descending date order and halts the moment an overlap with existing data is detected
- Not currently used for the live warehouse, since it can't reach 2026 data — retained for when that changes

### Phase 2 — Transformation (Cleansing & Feature Engineering)

- Drops Arabic-language columns, deprecated fields, and columns with >99% null rates
- Filters for residential sales transactions only; excludes commercial sub-types (shops, offices)
- Converts all ID columns to memory-efficient nullable integer types (`UInt8`, `UInt16`, `boolean`)
- Imputes missing `property_sub_type_id` values using deterministic business rules by `property_type_id`
- Imputes missing `rooms` values using **median-area proximity matching** — calculates the median `procedure_area` per known room category and assigns the nearest match to nulls (applied separately per emirate)
- Converts area from square metres to square feet; derives `price_per_sqft`
- Runs a **3-step data quality pipeline** on `price_per_sqft`:
  1. Applies market-floor and market-ceiling bounds by property type (e.g. Units: AED 300–15,000/sqft)
  2. Attempts forensic recovery on flagged rows by recalculating `price_per_sqft` from raw price and area before discarding them
  3. Caps remaining statistical outliers using IQR fencing (Tukey method), per property type group

**Dimension table generation**

All five lookup tables share one reusable normalization pattern: select the ID + label columns, `drop_duplicates()` to get one row per unique value, then reset the index. Nulls are handled deliberately rather than silently dropped — ID columns are filled with `0` (an explicit "unknown" key) and label columns are filled with `"not provided"`, so every foreign key in the fact table always resolves to a row in its dimension table instead of failing a join.

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

The same frame is reused for `lkp_areas`, `lkp_property_types`, `lkp_procedures`, and `lkp_statuses` — swap the column names and output filename, logic stays identical.

### Phase 3 — Loading (MySQL Data Warehouse)

- Connects to a local MySQL instance via **SQLAlchemy**
- Loads the cleansed fact table using `if_exists='replace'` for a full refresh
- Conditionally loads five lookup (dimension) tables only if they do not already exist — idempotent by design, safe to re-run without duplication

**Enforcing referential integrity**

`pandas.to_sql()` creates columns but doesn't enforce relationships, so the star schema is hardened with a one-time SQL pass after the first load: dimension and fact key columns are aligned to matching `INT` types, each dimension table gets an explicit primary key, and the fact table gets a foreign key constraint back to it. This turns "these columns are supposed to match" into something MySQL actually rejects if violated.

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

The same pattern (type alignment → primary key → foreign key) is repeated for each of the five dimension tables.

---

## Data Model (Star Schema)

```
                    ┌─────────────────┐
                    │   dim_date      │
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────▼─────────────────────────────┐    ┌─────────────────────────┐
│  lkp_areas   ├───►│                                      │◄───┤  lkp_property_sub_types │
└──────────────┘    │  cleaned_residential_real_estate      │    └─────────────────────────┘
┌──────────────┐    │           _sale_data                 │    ┌─────────────────────────┐
│lkp_procedures├───►│         (Fact Table)                 │◄───┤   lkp_property_types    │
└──────────────┘    │                                      │    └─────────────────────────┘
                    └──────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  lkp_statuses   │
                    └─────────────────┘
```

**Fact table key columns:**

| Column                  | Type    | Description                        |
| ----------------------- | ------- | ----------------------------------- |
| `transaction_id`        | VARCHAR | Unique transaction identifier      |
| `transaction_date`      | DATE    | Date of the sale                   |
| `price`                 | DECIMAL | Total transaction value (AED)      |
| `property_size_sqft`    | DECIMAL | Property size in square feet       |
| `price_per_sqft`        | DECIMAL | Derived price per square foot      |
| `price_per_sqft_capped` | DECIMAL | IQR-capped version used in visuals |
| `area_id`               | INT     | FK → lkp_areas                     |
| `property_type_id`      | UINT8   | FK → lkp_property_types            |
| `property_sub_type_id`  | UINT8   | FK → lkp_property_sub_types        |
| `procedure_id`          | UINT16  | FK → lkp_procedures                |
| `status_id`             | BOOLEAN | FK → lkp_statuses                  |
| `has_parking`           | BOOLEAN | Parking availability flag          |
| `has_nearest_metro`     | BOOLEAN | Proximity to metro flag            |
| `has_nearest_landmark`  | BOOLEAN | Proximity to landmark flag         |
| `has_nearest_mall`      | BOOLEAN | Proximity to mall flag             |

---

## Power BI Measures (DAX)

```
-- Median price per sqft (robust to luxury outliers)
Avg Price per SqFt =
    MEDIAN(cleaned_residential_real_estate_sale_data[price_per_sqft_capped])

-- Dynamic headline that responds to slicer context
Market Insight Headline =
    IF(
        ISFILTERED('lkp_statuses'[status]),
        SELECTEDVALUE('lkp_statuses'[status]) & " Market Analysis: Avg Price is AED "
            & FORMAT([Avg Price per SqFt], "#,##0") & "/sqft",
        "Total Dubai Residential Market: Avg Price is AED "
            & FORMAT([Avg Price per SqFt], "#,##0") & "/sqft"
    )

-- Month-over-month transaction volume
Transactions Last Month =
    CALCULATE([Total_Transactions], DATEADD('dim_date'[Date], -1, MONTH))

MoM Transactions Growth % =
    DIVIDE(
        [Total_Transactions] - [Transactions Last Month],
        [Transactions Last Month],
        0
    )

-- Totals
Total Sales (AED)    = SUM(cleaned_residential_real_estate_sale_data[price])
Total_Transactions   = DISTINCTCOUNT(cleaned_residential_real_estate_sale_data[transaction_id])
```

---

## Project Structure

```
├── etl_pipeline.py                     # Main ETL script (extraction + transform + load)
├── dld_transactions_2024_onwards.csv   # Master raw data file — currently the full 2024–2026 bulk CSV from data.dubai (gitignored)
├── lkp_areas.csv                       # Area dimension lookup
├── lkp_property_sub_types.csv          # Property sub-type lookup
├── lkp_property_types.csv              # Property type lookup
├── lkp_statuses.csv                    # Status (Off-Plan / Ready) lookup
├── lkp_procedures.csv                  # Procedure type lookup
├── .env                                # Credentials (gitignored)
├── .gitignore
└── README.md
```

---

## Setup & Usage

**Prerequisites**

- Python 3.9+
- MySQL 8.0+ (running locally)
- Power BI Desktop

**Install dependencies**

```
pip install pandas numpy sqlalchemy pymysql python-dotenv requests
```

**Configure credentials** (only needed if you plan to use the API path)

Create a `.env` file in the project root:

```
DLD_CLIENT_ID=your_client_id
DLD_CLIENT_SECRET=your_client_secret
DLD_APP_IDENTIFIER=your_app_identifier
MYSQL_PASSWORD=your_mysql_password
```

**Get the data (current method: full CSV reload)**

Download the complete transaction history (2024–2026) as a bulk CSV export from [data.dubai](https://data.dubai) and save it as `dld_transactions_2024_onwards.csv` in the project root — the same filename the API path used to populate. No separate script needed; the transform and load phases read whatever is in that file.

**Run the pipeline**

```
python etl_pipeline.py
```

Currently this reads from the bulk CSV export rather than calling the API. Re-run it whenever you download a fresh CSV export to pick up newer transactions. The API extraction path is still in the codebase and safe to run on its own once a live (non-sandbox) endpoint is available — it will pick up automatically from the last synced date.

**Connect Power BI**

Open Power BI Desktop → Get Data → MySQL Database → connect to `localhost/real_estate_db` → load the fact table and all lookup tables → apply the DAX measures above.

---

## Key Engineering Decisions

**Why delta loading instead of full refresh (API path)?** The DLD dataset grows daily. A full re-extraction on every run would be wasteful and fragile. Watermark-based delta sync keeps sync time under 5 seconds regardless of total dataset size — this is why the logic is being kept even though it's not driving the warehouse right now.

**Why switch to a full-history CSV reload instead of patching in just 2026?** The DLD API turned out to be a test/sandbox environment scoped to 2024–2025 — a limitation that isn't documented up front and only surfaced once I profiled the returned date ranges. Rather than reconcile two partial, independently-sourced ranges against each other, I downloaded the complete 2024–2026 history as one bulk CSV from data.dubai and reran the full pipeline against it. One internally consistent source beats stitching two partial ones together.

**Why MEDIAN instead of AVERAGE for price/sqft?** Dubai's luxury segment produces extreme high-end outliers. MEDIAN is resistant to those extremes and gives a more representative figure for typical market participants. The IQR-capped column provides a second safety net.

**Why star schema instead of a flat table?** Dimension tables decouple descriptive attributes from the fact table, reduce storage, and make Power BI relationship management cleaner. Adding a new area or property type requires updating one lookup table, not re-loading the entire fact table.

**Why forensic recovery before dropping rows?** Discarding a row solely because `price_per_sqft` looks wrong — when the underlying `price` and `area` are both valid — wastes real information. The pipeline attempts to recalculate from source columns before accepting the quality flag.

**Why add primary/foreign key constraints after load instead of relying on `to_sql()`?** `to_sql()` will happily create a fact table whose `area_id` doesn't actually match anything in `lkp_areas` — it has no concept of a relationship, only column names. Adding explicit PK/FK constraints post-load means a bad load fails loudly at the database level instead of silently producing orphaned rows that only show up as blank labels in Power BI weeks later.

---

## Data Source

- **data.dubai Open Data Portal** — full historical bulk CSV export (2024–2026), the current source for the fact table: [https://data.dubai](https://data.dubai)
- **Dubai Land Department (DLD) Open Data API** — test/sandbox endpoint, 2024–2025 coverage only. Implemented and functional, but not currently used since it can't reach 2026 data. Access requires registration and approval through the DLD integration team; credentials are not included in this repository.

---

## Author

**Abdullah**
Data Analyst | Dubai, UAE
Open to Data Analyst opportunities in the UAE market.

[LinkedIn](https://www.linkedin.com/in/muhammad-abdullah-a7861a3a2/) · [GitHub](https://github.com/ak786abdullah/Dubai-Residential-Investment-Intelligence-Dashboard-2026)
