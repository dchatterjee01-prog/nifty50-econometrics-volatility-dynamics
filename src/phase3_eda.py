"""
Phase 3: Exploratory Data Analysis (EDA)
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Purpose:
    - Load the cleaned NIFTY 50 dataset
    - Compute descriptive/summary statistics for price and volume series
    - Calculate distributional measures: skewness and kurtosis
    - Save a publication-quality summary table for use in the report

Input:
    data/processed/clean_nifty.csv

Output:
    outputs/tables/summary_statistics.csv
    outputs/tables/summary_statistics.xlsx
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

# ------------------------------------------------------------
# 1. Setup paths
# ------------------------------------------------------------
PROCESSED_PATH = os.path.join("data", "processed", "clean_nifty.csv")
TABLES_DIR = os.path.join("outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# ------------------------------------------------------------
# 2. Load cleaned data
# ------------------------------------------------------------
df = pd.read_csv(PROCESSED_PATH, parse_dates=["Date"])

print("Dataset loaded. Shape:", df.shape)
print("Date range:", df["Date"].min(), "to", df["Date"].max())

# ------------------------------------------------------------
# 3. Select numeric columns for analysis
# ------------------------------------------------------------
numeric_cols = ["Open", "High", "Low", "Close", "Volume"]

# ------------------------------------------------------------
# 4. Compute summary statistics
# ------------------------------------------------------------
# Basic descriptive statistics using pandas
basic_stats = df[numeric_cols].describe().T  # transpose: variables as rows

# Add additional statistics: variance, skewness, kurtosis
basic_stats["variance"] = df[numeric_cols].var()
basic_stats["skewness"] = df[numeric_cols].apply(lambda x: stats.skew(x, nan_policy="omit"))
basic_stats["kurtosis"] = df[numeric_cols].apply(lambda x: stats.kurtosis(x, nan_policy="omit"))
# Note: scipy's kurtosis() by default returns EXCESS kurtosis
# (kurtosis - 3), so 0 = normal distribution (mesokurtic).

# Rename columns for clarity
basic_stats = basic_stats.rename(columns={
    "count": "N",
    "mean": "Mean",
    "std": "Std. Dev.",
    "min": "Min",
    "25%": "25th Percentile",
    "50%": "Median",
    "75%": "75th Percentile",
    "max": "Max",
    "variance": "Variance",
    "skewness": "Skewness",
    "kurtosis": "Excess Kurtosis"
})

# Reorder columns for a clean, publication-style table
column_order = [
    "N", "Mean", "Median", "Std. Dev.", "Variance",
    "Min", "Max", "25th Percentile", "75th Percentile",
    "Skewness", "Excess Kurtosis"
]
summary_table = basic_stats[column_order]

# Round for readability (keep more precision for Volume since it's large)
summary_table = summary_table.round(4)

print("\n--- Summary Statistics Table ---")
print(summary_table)

# ------------------------------------------------------------
# 5. Save table (CSV + Excel for report use)
# ------------------------------------------------------------
csv_path = os.path.join(TABLES_DIR, "summary_statistics.csv")
xlsx_path = os.path.join(TABLES_DIR, "summary_statistics.xlsx")

summary_table.to_csv(csv_path)
summary_table.to_excel(xlsx_path, sheet_name="Summary Statistics")

print(f"\nSummary statistics saved to:\n  {csv_path}\n  {xlsx_path}")

# ------------------------------------------------------------
# 6. Quick interpretation notes (printed for your reference)
# ------------------------------------------------------------
close_skew = summary_table.loc["Close", "Skewness"]
close_kurt = summary_table.loc["Close", "Excess Kurtosis"]

print("\n--- Quick Interpretation Notes (Close Price) ---")
print(f"Skewness of Close: {close_skew:.4f}")
if close_skew > 0:
    print("  -> Positively skewed: distribution has a longer right tail "
          "(more extreme high values than low values).")
elif close_skew < 0:
    print("  -> Negatively skewed: distribution has a longer left tail.")
else:
    print("  -> Approximately symmetric.")

print(f"\nExcess Kurtosis of Close: {close_kurt:.4f}")
if close_kurt > 0:
    print("  -> Leptokurtic: heavier tails / more peaked than a normal "
          "distribution (more extreme values than normal).")
elif close_kurt < 0:
    print("  -> Platykurtic: lighter tails / flatter than normal.")
else:
    print("  -> Mesokurtic: similar to normal distribution.")