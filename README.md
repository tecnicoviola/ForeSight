# SalesPulse — Sales Trend Forecasting & Retail Analytics

A modern, production-grade analytics and weekly sales forecasting web application built using genuine historical retail transaction data from the **UCI Online Retail II Dataset**.

---

## 1. Project Title
**SalesPulse: Sales Trend Forecasting & Retail Analytics**

---

## 2. Project Overview
SalesPulse is an interactive, academic, and SaaS-grade analytics platform designed to demonstrate the practical application of multiple regression modeling and time-series feature engineering to genuine e-commerce retail data. 

The application provides executive and analytical visibility into historical retail performance through five core modules:
1. **Sales Overview**: High-level KPIs, overall revenue curves, and period-filtered breakdowns.
2. **Sales Analytics**: Multi-granularity time-series dynamics (Daily, Weekly, Monthly), period-over-period growth rates, and peak/trough identification.
3. **Product Analytics**: Catalog performance rankings, volume vs. value relationships, and Pareto (80/20 rule) cumulative revenue concentration.
4. **Geographical Analytics**: Worldwide revenue distribution across 43 export destinations and domestic UK vs. International market segmentation.
5. **Sales Forecasting & Model Comparison**: Weekly sales forecasting comparing three supervised regression architectures (**Linear Regression**, **Polynomial Regression**, and **Random Forest Regressor**) trained using chronological holdout validation with recursive multi-step future projections.

---

## 3. Problem Statement
Retail organizations generate large volumes of transactional records but often lack structured mechanisms to:
- Dissect historical revenue velocity across products, geographies, and timeframes.
- Uncover seasonal demand trends and concentration risks (e.g. over-reliance on a few key SKUs).
- Project future weekly revenue without data leakage or arbitrary heuristics.

SalesPulse bridges this gap by offering a transparent, reproducible analytical and machine learning pipeline that transforms raw transaction logs into actionable forward-looking sales intelligence.

---

## 4. Project Objectives
- Ingest and audit the complete official UCI Online Retail II dataset (1,067,371 raw records).
- Implement a documented, zero-synthetic data cleaning pipeline.
- Compute transaction-level revenue ($Q \times P$) and multi-frequency aggregations.
- Formulate leak-free weekly time-series features (calendar indices, autoregressive lags, rolling statistics).
- Implement, benchmark, and compare multiple regression models strictly on chronological holdout observations.
- Deliver an elegant, responsive, Toolfolio-inspired web interface with zero financial cost or paid API dependencies.

---

## 5. Dataset Source and Attribution
- **Dataset Name**: Online Retail II
- **Repository**: UCI Machine Learning Repository
- **Dataset ID**: 502
- **Official URL**: [https://archive.ics.uci.edu/dataset/502/online+retail+ii](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- **Academic Citation**:
  > Chen, D. (2012). *Online Retail II*. UCI Machine Learning Repository. DOI: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D).

---

## 6. Dataset License
- **License**: Creative Commons Attribution 4.0 International (**CC BY 4.0**).
- Permitted for academic, educational, and commercial analytics with appropriate citation.

---

## 7. Dataset Structure
The raw Excel workbook contains two sheets representing two consecutive operational years:
- `Year 2009-2010`: 525,461 records (01 Dec 2009 – 09 Dec 2010).
- `Year 2010-2011`: 541,910 records (01 Dec 2010 – 09 Dec 2011).
- **Total Raw Records**: **1,067,371 rows across 8 standard columns**:
  1. `Invoice`: 6-digit integer or cancellation string prefix (`C`).
  2. `StockCode`: 5-digit product code or operational code.
  3. `Description`: Product name or transaction memo.
  4. `Quantity`: Integer units of product per transaction.
  5. `InvoiceDate`: Timestamp of transaction generation.
  6. `Price`: Unit price in Sterling (£).
  7. `Customer ID`: 5-digit customer identifier (optional for guest orders).
  8. `Country`: Destination sovereign state.

---

## 8. Data Cleaning Methodology
All cleaning decisions are explicitly documented and programmatic:
1. **Deduplication**: 34,335 identical duplicate rows were removed.
2. **Cancellation Filtering**: Invoices prefixed with `C` or containing negative quantities (22,497 rows) represent returns/adjustments and were excluded from forward demand modeling.
3. **Price Validation**: Non-positive unit prices ($\le 0$, 2,626 records representing debts, fees, or system adjustments) were excluded.
4. **Missing Customer IDs**: 228,488 guest transactions were **retained**. In digital e-commerce, guest purchases represent genuine sales and excluding them would artificially understate revenue.
5. **Missing Product Descriptions**: Imputed with `'Unspecified Product [' + StockCode + ']'` to retain all genuine financial turnover.
6. **Final Cleaned Transactions**: **1,007,913 genuine transactions (94.43% retention)** representing **£20,476,260.43** in total retail revenue.

---

## 9. Revenue Calculation Methodology
Revenue is computed at the granular transaction level:
$$\text{Revenue} = \text{Quantity} \times \text{Price}$$
Calculated values are preserved with two decimal places of precision in British Pounds (£).

---

## 10. Weekly Aggregation Methodology
- Aggregated chronologically using standard ISO calendar week starts (`W-MON`).
- Continuous date range is enforced from the first observed week (`2009-11-30`) to the final week (`2011-12-05`).
- True zero-sales weeks within the historical span are preserved with 0 values rather than dropped, maintaining continuous time-series structure.

---

## 11. Feature Engineering
Time-series features are constructed with strict prevention of look-ahead target leakage:
- **Temporal Indices**:
  - `TimeIndex`: Monotonically increasing sequential integer ($0, 1, 2, \dots, N-1$).
  - `Year`: Calendar year of week start.
  - `Month`: Calendar month ($1 \dots 12$).
  - `WeekOfYear`: ISO week number ($1 \dots 53$).
- **Autoregressive Lags**:
  - `Lag_1`: Previous week sales revenue ($y_{t-1}$).
  - `Lag_2`: Sales revenue 2 weeks prior ($y_{t-2}$).
  - `Lag_4`: Sales revenue 4 weeks prior ($y_{t-4}$).
- **Rolling Historical Statistics**:
  - `Rolling_Mean_4`: 4-week historical average. Strictly calculated as `Revenue.shift(1).rolling(4).mean()`, ensuring the current period's revenue cannot leak into the rolling window.

---

## 12. Regression Models Implemented
1. **Linear Regression**: Ordinary Least Squares baseline capturing underlying secular trend and linear lag dependencies.
2. **Polynomial Regression (Pipeline)**: Degree-2 polynomial expansion with `StandardScaler` and `Ridge` regularization ($\alpha = 50.0$) to capture non-linear acceleration while preventing collinear variance inflation.
3. **Random Forest Regressor**: Non-linear ensemble model (`n_estimators=100`, `max_depth=6`, `random_state=42`) capable of capturing complex seasonal interactions.

---

## 13. Training and Testing Methodology
- **Strict Chronological Holdout Splitting**: Data is split into earlier training observations and later holdout evaluation observations (default: 12 weeks).
- **No Random Shuffling**: Time-series integrity is maintained; training set observations strictly precede test set observations.
- **Recursive Forecasting**: Future predictions across selected horizons ($H \in \{4, 8, 12\}$ weeks) are generated sequentially. At each step $t+h$, previous predictions are fed dynamically into subsequent lag and rolling feature buffers.

---

## 14. Evaluation Metrics
Evaluated strictly on held-out test data:
- **Mean Absolute Error (MAE)**:
  $$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|$$
- **Root Mean Squared Error (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$$
- **Coefficient of Determination ($R^2$)**:
  $$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

All predictions are non-negatively bounded ($\ge 0$). The optimal model is selected via lowest holdout RMSE.

---

## 15. Technology Stack (100% Free & Open Source)
- **Programming Language**: Python 3.11+
- **Data Engineering**: Pandas, NumPy, OpenPyXL, PyArrow (Apache Parquet)
- **Machine Learning**: Scikit-learn
- **Visualization**: Plotly
- **Application Framework**: Streamlit
- **Testing**: Pytest

No paid APIs, API keys, commercial services, or synthetic data generators are required.

---

## 16. Project Structure
```text
ForeSight/
├── app.py                      # Main Streamlit application entry point
├── pages/
│   ├── sales_overview.py       # Module 1: Executive KPI overview & trend
│   ├── sales_analytics.py      # Module 2: Multi-frequency time-series dynamics
│   ├── product_analytics.py    # Module 3: Catalog rankings & Pareto curve
│   ├── geographical_analytics.py # Module 4: Global distribution & choropleth
│   └── sales_forecasting.py    # Module 5 & 6: ML regression & forecast
├── src/
│   ├── data/
│   │   ├── download.py         # Official UCI dataset download utility
│   │   ├── inspect_dataset.py  # Dataset inspection script
│   │   ├── loader.py           # Cached Parquet loaders
│   │   └── preprocessing.py    # Cleaning & aggregation pipeline
│   ├── analytics/
│   │   ├── sales_metrics.py    # KPI & growth analytics
│   │   ├── product_analysis.py # Catalog & Pareto analytics
│   │   └── country_analysis.py # Country & export analytics
│   ├── forecasting/
│   │   ├── feature_engineering.py # Leak-free lag & rolling features
│   │   ├── train.py            # Chronological splitting & model fitting
│   │   ├── evaluate.py         # MAE, RMSE, R2 benchmarking
│   │   └── predict.py          # Recursive multi-step future forecasting
│   └── utils/
│       ├── config.py           # Paths, constants, and Toolfolio theme
│       └── helpers.py          # Currency formatters & Plotly styling
├── assets/
│   └── styles.css              # Minimal Toolfolio-inspired styling
├── data/
│   ├── raw/                    # Original Excel archive
│   └── processed/              # High-speed Parquet aggregations
├── tests/
│   ├── test_pipeline.py        # ML and feature engineering unit tests
│   └── test_app_integration.py # Full application integration tests
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusions (large files excluded)
├── LICENSE                     # MIT License
└── README.md                   # Complete documentation
```

---

## 17. Installation Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/salespulse.git
   cd salespulse
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 18. How to Download the Dataset
The dataset can be automatically downloaded and verified by running:
```bash
python src/data/download.py
```
If your environment has restricted network access, manually download `online_retail_II.xlsx` from the official [UCI Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and place it in `data/raw/online_retail_II.xlsx`.

To regenerate the processed Parquet aggregations:
```bash
python src/data/preprocessing.py
```

---

## 19. How to Run the Application
Launch the Streamlit web application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 20. How to Run Tests
Execute the comprehensive Pytest suite:
```bash
pytest tests/ -v
```
All 12 unit and integration tests will execute, validating data integrity, leakage prevention, chronological splitting, regression model evaluation, and recursive prediction.

---

## 21. Deployment Instructions (Streamlit Community Cloud)
SalesPulse is fully compatible with free hosting on **Streamlit Community Cloud**:
1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
3. Click **New app**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. Click **Deploy**.
5. The processed Parquet files in `data/processed/` will load instantaneously on the cloud instance without requiring raw Excel re-parsing.

---

## 22. Known Limitations
- **Historical Period (2009–2011)**: The dataset reflects British e-commerce retail behavior from December 2009 to December 2011. Forecasts demonstrate statistical regression methodology and demand dynamics on genuine historical data rather than current macro retail conditions.
- **UK Market Concentration**: The retailer was UK-based, meaning approximately 85% of transactions and revenue originate in the United Kingdom. International projections reflect secondary export demand.
- **External Covariates**: The models rely on autoregressive temporal patterns and past demand. Exogenous factors such as macro inflation, ad spend, and exchange rate volatility are not recorded in the original transaction dataset.
