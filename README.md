# Dubai Residential Real Estate — End-to-End Analytics Pipeline

> **Live API → Python ETL → MySQL Data Warehouse → Power BI Dashboard**
> A fully automated, production-grade analytics system built on Dubai Land Department (DLD) transaction data.

---

## Project Overview

This project demonstrates a complete data engineering and analytics workflow built entirely from scratch — from authenticated API extraction through to an interactive Power BI dashboard.

The data source is the **Dubai Land Department Open Data API**, which publishes residential property sales transactions across all seven emirates. The pipeline extracts, cleanses, transforms, and loads this data into a local MySQL data warehouse on a daily schedule, then surfaces it through a structured Power BI report.

---

## Architecture

```
DLD REST API  ──►  Python ETL Pipeline  ──►  MySQL Database  ──►  Power BI Dashboard
   (OAuth2)         (Pandas / SQLAlchemy)     (Star Schema)        (DAX Measures)
```

### Phase 1 — Extraction (Delta Load)
- Authenticates against the DLD API using OAuth2 client credentials flow, with token stored securely in a `.env` file
- Implements **watermark-based delta loading**: reads the maximum `instance_date` from the existing master CSV, then pulls only records newer than that date — reducing daily sync time from ~60 minutes to ~3 seconds
- Includes automatic **WAF-compliant headers** and a configurable **token lifespan guard** (50-minute safe window) to handle long-running extractions without mid-run expiry
- Paginates through results in descending date order and halts the moment an overlap with existing data is detected

### Phase 2 — Transformation (Cleansing & Feature Engineering)
- Drops Arabic-language columns, deprecated fields, and columns with >99% null rates
- Filters for residential sales transactions only; excludes commercial sub-types (shops, offices)
- Converts all ID columns to memory-efficient nullable integer types (`UInt8`, `UInt16`, `boolean`)
- Imputes missing `property_sub_type_id` values using deterministic business rules by `property_type_id`
- Imputes missing `rooms` values using **median-area proximity matching** — calculates the median `procedure_area` per known room category and assigns the nearest match to nulls (applied separately for Villas and Units)
- Converts area from square metres to square feet; derives `price_per_sqft`
- Runs a **3-step data quality pipeline** on `price_per_sqft`:
  1. Applies market-floor and market-ceiling bounds by property type (e.g. Units: AED 300–15,000/sqft)
  2. Attempts forensic recovery on flagged rows by recalculating `price_per_sqft` from raw price and area before discarding them
  3. Caps remaining statistical outliers using IQR fencing (Tukey method), per property type group

### Phase 3 — Loading (MySQL Data Warehouse)
- Connects to a local MySQL instance via **SQLAlchemy**
- Loads the cleansed fact table using `if_exists='replace'` for full daily refresh
- Conditionally loads five lookup (dimension) tables only if they do not already exist — idempotent by design, safe to re-run daily without duplication

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

| Column | Type | Description |
|---|---|---|
| `transaction_id` | VARCHAR | Unique transaction identifier |
| `transaction_date` | DATE | Date of the sale |
| `price` | DECIMAL | Total transaction value (AED) |
| `property_size_sqft` | DECIMAL | Property size in square feet |
| `price_per_sqft` | DECIMAL | Derived price per square foot |
| `price_per_sqft_capped` | DECIMAL | IQR-capped version used in visuals |
| `area_id` | UINT16 | FK → lkp_areas |
| `property_type_id` | UINT8 | FK → lkp_property_types |
| `property_sub_type_id` | UINT8 | FK → lkp_property_sub_types |
| `procedure_id` | UINT16 | FK → lkp_procedures |
| `status_id` | BOOLEAN | FK → lkp_statuses |
| `has_parking` | BOOLEAN | Parking availability flag |
| `has_nearest_metro` | BOOLEAN | Proximity to metro flag |
| `has_nearest_landmark` | BOOLEAN | Proximity to landmark flag |
| `has_nearest_mall` | BOOLEAN | Proximity to mall flag |

---

## Power BI Measures (DAX)

```dax
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
├── etl_pipeline.py              # Main ETL script (all three phases)
├── dld_transactions_2024_onwards.csv  # Master raw data file (gitignored)
├── lkp_areas.csv                # Area dimension lookup
├── lkp_property_sub_types.csv   # Property sub-type lookup
├── lkp_property_types.csv       # Property type lookup
├── lkp_statuses.csv             # Status (Off-Plan / Ready) lookup
├── lkp_procedures.csv           # Procedure type lookup
├── .env                         # Credentials (gitignored)
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
```bash
pip install pandas numpy sqlalchemy pymysql python-dotenv requests
```

**Configure credentials**

Create a `.env` file in the project root:
```
DLD_CLIENT_ID=your_client_id
DLD_CLIENT_SECRET=your_client_secret
DLD_APP_IDENTIFIER=your_app_identifier
MYSQL_PASSWORD=your_mysql_password
```

**Run the pipeline**
```bash
python etl_pipeline.py
```

The pipeline is safe to run daily. It will automatically detect the last sync date and only pull new records.

**Connect Power BI**

Open Power BI Desktop → Get Data → MySQL Database → connect to `localhost/real_estate_db` → load the fact table and all lookup tables → apply the DAX measures above.

---

## Key Engineering Decisions

**Why delta loading instead of full refresh?**
The DLD dataset grows daily. A full re-extraction on every run would be wasteful and fragile. Watermark-based delta sync keeps the daily runtime under 5 seconds regardless of total dataset size.

**Why MEDIAN instead of AVERAGE for price/sqft?**
Dubai's luxury segment produces extreme high-end outliers. MEDIAN is resistant to those extremes and gives a more representative figure for typical market participants. The IQR-capped column provides a secondary layer of protection.

**Why star schema instead of a flat table?**
Dimension tables decouple descriptive attributes from the fact table, reduce storage, and make Power BI relationship management cleaner. Adding a new area or property type requires updating one lookup table, not re-processing the entire fact table.

**Why forensic recovery before dropping rows?**
Discarding a row solely because `price_per_sqft` looks wrong — when the underlying `price` and `area` are both valid — wastes real information. The pipeline attempts to recalculate from source columns first and only drops the row if the recalculated value is also out of bounds.

---

## Data Source

Dubai Land Department (DLD) Open Data API
[https://www.dubailand.gov.ae](https://www.dubailand.gov.ae)

API access requires registration and approval through the DLD integration team. Credentials are not included in this repository.

---

## Author

**Abdullah**
Junior Data Analyst | Dubai, UAE
Open to Data Analyst opportunities in the UAE market.

[LinkedIn](www.linkedin.com/in/muhammad-abdullah-a7861a3a2l) · [GitHub](your-github-url)
