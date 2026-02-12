# 🏙️ Dubai Residential Investment Intelligence Dashboard (2026 Edition)

![Status](https://img.shields.io/badge/Status-Completed-success)
![Tools](https://img.shields.io/badge/Tools-Python%20|%20Pandas%20|%20PowerBI-blue)

## 📖 Executive Summary
This project is a comprehensive end-to-end data analytics solution designed to identify undervalued real estate investment opportunities in Dubai. 

Instead of relying on aggregated reports, this project processes **raw government data** (10 million+ records) to engineer a custom **"Investment Score."** This score mathematically balances **Rental Yields** (Cash Flow) with **Sales Liquidity** (Exit Strategy) to highlight top-performing communities.

## 📊 The Output (Power BI Dashboard)
The final dashboard allows investors to:
- Compare **Off-Plan vs. Ready** price spreads per square foot.
- Visualize liquidity tiers across a geospatial map of Dubai.
- Drill down into specific communities to see historical trends (2024-2026).
- Identify high-yield areas using the "Investment Score" matrix.

## 🛠️ The Data Pipeline (Methodology)

The project was executed in **5 Technical Phases**:

### **Phase 1: Data Sourcing**
Sourced official open data from **Dubai Pulse (DLD)**:
- `Transactions.csv`: 1.5M+ historical sales records.
- `Rent_Contracts.csv`: 9M+ Ejari registration records.
- `Units.csv`: Master file for property specifications.

### **Phase 2: Handling Big Data (Memory Engineering)**
**Challenge:** The Rental dataset (4.3GB+) caused `MemoryError` on standard machines.
**Solution:**
- Implemented **Pandas Chunking**: Processed the CSV in batch sizes to filter for target years (2024-2026) without overloading RAM.
- Reduced dataset size by 70% pre-analysis by filtering irrelevant columns early.

### **Phase 3: Data Cleaning & Integrity**
**Challenge:** Inconsistent naming conventions ("Al Barsha" vs "Al Barshaa") and dirty string data in room columns.
**Solution:**
- **Regex Parsing:** Extracted integers from mixed strings (e.g., converting "3 B/R + Hall" -> `3`).
- **Probabilistic Imputation:** Filled missing room numbers using the median values of properties with similar square footage.
- **Standardization Dictionary:** Mapped variable area names to a "Single Source of Truth" to ensure successful merging.
- **Outlier Removal:** Applied the IQR (Interquartile Range) method to remove commercial outliers and non-residential bulk deals.

### **Phase 4: Feature Engineering ("The Alpha")**
Merged the Sales and Rental datasets to create new financial metrics:

1.  **Spread Percentage:**
    $$\frac{\text{OffPlan Price} - \text{Ready Price}}{\text{Ready Price}} \times 100$$
    *Identifies if an area is overvalued or undervalued.*

2.  **Gross Rental Yield:**
    $$\frac{\text{Avg Annual Rent}}{\text{Avg Sales Price}} \times 100$$

3.  **Liquidity Score:**
    Based on the monthly transaction volume (Sales Velocity).

4.  **The Investment Score (Composite Metric):**
    A weighted formula to rank areas:
    $$\text{Score} = (0.7 \times \text{Normalized Yield}) + (0.3 \times \text{Normalized Liquidity})$$

### **Phase 5: Visualization**
Exported the processed data to **Power BI** to build the interactive dashboard seen in the demo.

## 💻 Tech Stack
- **Language:** Python 3.10+
- **Libraries:** Pandas, NumPy, Matplotlib (for initial EDA), Regex.
- **Visualization:** Microsoft Power BI.

## 📂 Repository Structure

```text
├── Dashboard/
│   └── dubai_residential_dashboard.pbix       # The final Power BI Dashboard file
├── Data/
│   ├── Cleaned Data/
│   │   ├── cleaned_rent_sample.csv            # Processed rental data
│   │   └── cleaned_transactions_sample.csv    # Processed sales data
│   └── Raw_Data_sample/
│       ├── rent_2025_sample.csv               # Raw sample for testing
│       └── transactions_2024_to_2025_sample.csv
├── Notebooks/
│   ├── Analysis Code/
│   │   └── Data_analytic.ipynb                # Feature engineering & final metrics
│   ├── Data Extraction From Large File Code/
│   │   ├── rent_contracts.ipynb               # Chunking logic for 9M+ rows
│   │   └── transaction.ipynb                  # Filtering logic for sales data
│   └── Data cleaning code/
│       ├── rent_cleaning.ipynb                # Cleaning pipeline for rent
│       └── transactions_cleaning.ipynb        # Cleaning pipeline for sales
└── README.md
