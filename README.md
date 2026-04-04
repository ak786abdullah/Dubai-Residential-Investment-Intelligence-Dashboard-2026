# 🏙️ Dubai Residential Investment Intelligence Dashboard (2026 Edition)

![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Engineering-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-Analysis-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)
![Data](https://img.shields.io/badge/Records-10M+-brightgreen?style=for-the-badge)

---

## 💡 The Business Problem

> **"Dubai has 200+ residential communities. Where should a 2 Million AED investor put their money for maximum yield and a safe exit?"**

Generic market reports give you averages. This project gives you **precision** — by processing raw government data at scale to surface *exactly* which communities offer the best combination of rental cash flow and sales liquidity.

---

## 📸 Dashboard Preview

> **Market Overview — KPIs, Off-Plan vs Ready  Liquidity Tier**

[![Dashboard Overview](Dashboard/dashboard_overview.png)](https://github.com/ak786abdullah/Dubai-Residential-Investment-Intelligence-Dashboard-2026/blob/f2dd79001373f158f5856c7f5f7075cb428396c2/Dashboard/Overview.png)

> **Investment Score Matrix — Top Communities by Yield & Liquidity**

![Investment Score](Dashboard/investment_score.png)

> **Community Drill-Down — Historical Trends 2024–2026**

![Drill Down](Dashboard/community_drilldown.png)

*📥 Download the interactive `.pbix` file from the [Dashboard folder](Dashboard/) to explore filters and slicers yourself.*

---

## 🏆 Key Findings

| # | Insight | Impact |
|---|---------|--------|
| 1 | **High-yield communities** are not always in prime locations — several secondary areas outperform Downtown on gross rental yield | Unlocks undervalued investment pockets |
| 2 | **Off-Plan properties** trade at a measurable premium over ready units in fast-growing corridors | Identifies where developer pricing power exists |
| 3 | **Liquidity Score** reveals that high-yield areas often suffer from low transaction velocity — the Investment Score balances both | Prevents yield-trap investments |

---

## ⚙️ The Data Pipeline (5 Phases)

```
Raw Government Data (10M+ rows)
        │
        ▼
┌─────────────────────┐
│  Phase 1: Sourcing  │  Dubai Pulse (DLD Open Data)
│  - Transactions.csv │  1.5M+ sales records
│  - Rent_Contracts   │  9M+ Ejari registrations
│  - Units.csv        │  Master property specs
└────────┬────────────┘
         │
         ▼
┌──────────────────────────┐
│  Phase 2: Memory Engine  │  4.3GB file → Pandas Chunking
│  Chunked CSV processing  │  70% size reduction pre-analysis
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Phase 3: Data Cleaning  │  Regex • IQR Outlier Removal
│  Imputation • Mapping    │  Standardized area name dictionary
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Phase 4: Feature Eng.   │  Custom financial metrics (see below)
│  Investment Score built  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Phase 5: Power BI       │  Interactive dashboard
│  Geospatial + Drill-down │  Slicers by area, type, year
└──────────────────────────┘
```

---

## 📐 Feature Engineering — The "Alpha"

Three custom financial metrics were engineered by merging the Sales and Rental datasets:

**1. Off-Plan Spread %**

$$\text{Spread} = \frac{\text{OffPlan Price} - \text{Ready Price}}{\text{Ready Price}} \times 100$$

**2. Gross Rental Yield**

$$\text{Yield} = \frac{\text{Avg Annual Rent}}{\text{Avg Sales Price}} \times 100$$

**3. Investment Score (Composite)**

$$\text{Score} = (0.7 \times \text{Normalized Yield}) + (0.3 \times \text{Normalized Liquidity})$$

> The 70/30 weighting prioritizes cash flow (yield) over exit strategy (liquidity), reflecting a long-term investor profile. Weights are adjustable in the notebook.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core programming language |
| **Pandas** | Data cleaning, chunking, feature engineering |
| **NumPy** | Vectorized calculations, IQR method |
| **Regex** | String normalization (e.g. "3 B/R + Hall" → `3`) |
| **Microsoft Power BI** | Interactive dashboard & geospatial visuals |
| **Dubai Pulse (DLD)** | Official government data source |

---

## 📁 Repository Structure

```
Dubai-Residential-Investment-Intelligence-Dashboard-2026/
│
├── 📊 Dashboard/
│   └── dubai_residential_dashboard.pbix     ← Interactive Power BI file
│
├── 📂 Data/
│   ├── Cleaned Data/
│   │   ├── cleaned_rent_sample.csv          ← Processed rental data
│   │   └── cleaned_transactions_sample.csv  ← Processed sales data
│   └── Raw_Data_sample/
│       ├── rent_2025_sample.csv             ← Raw sample for testing
│       └── transactions_2024_to_2025_sample.csv
│
├── 📓 Notebooks/
│   ├── Analysis Code/
│   │   └── Data_analytic.ipynb              ← Feature engineering & scoring
│   ├── Data Extraction From Large File Code/
│   │   ├── rent_contracts.ipynb             ← Chunking logic for 9M+ rows
│   │   └── transaction.ipynb                ← Sales data filtering
│   └── Data Cleaning Code/
│       ├── rent_cleaning.ipynb              ← Rental cleaning pipeline
│       └── transactions_cleaning.ipynb      ← Sales cleaning pipeline
│
└── README.md
```

---

## 🚀 How to Run This Project

### Prerequisites
- Python 3.10 or higher
- Microsoft Power BI Desktop (free) — [Download here](https://powerbi.microsoft.com/en-us/downloads/)
- ~8GB RAM recommended for full dataset (samples provided for standard machines)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/ak786abdullah/Dubai-Residential-Investment-Intelligence-Dashboard-2026.git
cd Dubai-Residential-Investment-Intelligence-Dashboard-2026
```

### Step 2 — Install Python Dependencies
```bash
pip install pandas numpy matplotlib
```

### Step 3 — Run the Data Pipeline (in order)

**3a. Extract data from large files** *(skip if using provided samples)*
```bash
# Open and run:
Notebooks/Data Extraction From Large File Code/transaction.ipynb
Notebooks/Data Extraction From Large File Code/rent_contracts.ipynb
```

**3b. Clean the data**
```bash
# Open and run:
Notebooks/Data Cleaning Code/transactions_cleaning.ipynb
Notebooks/Data Cleaning Code/rent_cleaning.ipynb
```

**3c. Run the analysis & generate the Investment Score**
```bash
# Open and run:
Notebooks/Analysis Code/Data_analytic.ipynb
```

### Step 4 — Open the Dashboard
1. Open `Dashboard/dubai_residential_dashboard.pbix` in **Power BI Desktop**
2. If prompted to refresh data, point it to the `Data/Cleaned Data/` folder
3. Use the slicers to filter by community, property type, and year

---

## 🔮 Future Roadmap

- [ ] Integrate **mortgage data** to calculate Net ROI after financing costs
- [ ] Build a **2027 price forecasting model** using Time-Series (ARIMA / Prophet)
- [ ] Automate monthly data refresh via Dubai Pulse API
- [ ] Deploy dashboard to **Power BI Service** for browser-based access

---

## 👤 Author

**Muhammad Abdullah**  
*Data Analyst | Mathematician*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammad-abdullah-a7861a3a2)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ak786abdullah)

---

*Data sourced from [Dubai Pulse](https://www.dubaipulse.gov.ae/) — Dubai Land Department official open data portal.*
