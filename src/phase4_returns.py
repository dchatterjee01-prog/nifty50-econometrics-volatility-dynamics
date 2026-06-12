"""
Phase 4: Log Return Calculation
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Purpose:
    - Load cleaned NIFTY 50 price data
    - Compute daily continuously compounded (log) returns
    - Compute simple returns for comparison/reference
    - Save the returns dataset for use in EDA, visualization,
      and econometric testing (Phases 5-8)

Input:
    data/processed/clean_nifty.csv

Output:
    data/processed/nifty_returns.csv
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

# ------------------------------------------------------------
# 1. Setup paths
# ------------------------------------------------------------
PROCESSED_PATH = os.path.join("data", "processed", "clean_nifty.csv")
OUTPUT_PATH = os.path.join("data", "processed", "nifty_returns.csv")
TABLES_DIR = os.path.join("outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# ------------------------------------------------------------
# 2. Load cleaned data
# ------------------------------------------------------------
df = pd.read_csv(PROCESSED_PATH, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

print("Dataset loaded. Shape:", df.shape)

# ------------------------------------------------------------
# 3. Compute Log Returns
# ------------------------------------------------------------
# Continuously compounded (log) return:
#     R_t = ln(P_t / P_{t-1}) = ln(P_t) - ln(P_{t-1})
#
# Log returns are preferred in financial econometrics because:
#   - They are approximately additive over time (multi-period
#     return = sum of single-period log returns)
#   - They are approximately equal to simple returns for small
#     percentage changes, but behave better statistically
#     (closer to normality, no lower bound of -100%)
#   - Most time series models (ARIMA, GARCH) are built around
#     log returns

df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))

# ------------------------------------------------------------
# 4. Compute Simple Returns (for reference/comparison)
# ------------------------------------------------------------
# Simple return: R_t = (P_t - P_{t-1}) / P_{t-1}
df["Simple_Return"] = df["Close"].pct_change()

# ------------------------------------------------------------
# 5. Drop the first row (NaN return, no previous price)
# ------------------------------------------------------------
df = df.dropna(subset=["Log_Return"]).reset_index(drop=True)

print(f"\nReturns calculated. Final shape: {df.shape}")
print(df[["Date", "Close", "Simple_Return", "Log_Return"]].head())
print(df[["Date", "Close", "Simple_Return", "Log_Return"]].tail())

# ------------------------------------------------------------
# 6. Express log returns as percentages (common convention)
# ------------------------------------------------------------
# Many econometric models (e.g., GARCH in the 'arch' package)
# work better numerically with returns scaled to percentages.
df["Log_Return_pct"] = df["Log_Return"] * 100

# ------------------------------------------------------------
# 7. Basic descriptive statistics of returns
# ------------------------------------------------------------
ret_stats = pd.DataFrame({
    "Mean": [df["Log_Return"].mean()],
    "Std. Dev.": [df["Log_Return"].std()],
    "Annualized Mean (%)": [df["Log_Return"].mean() * 252 * 100],
    "Annualized Volatility (%)": [df["Log_Return"].std() * np.sqrt(252) * 100],
    "Skewness": [stats.skew(df["Log_Return"], nan_policy="omit")],
    "Excess Kurtosis": [stats.kurtosis(df["Log_Return"], nan_policy="omit")],
    "Min": [df["Log_Return"].min()],
    "Max": [df["Log_Return"].max()],
})
ret_stats = ret_stats.round(6)

print("\n--- Log Return Summary Statistics ---")
print(ret_stats.T)

# ------------------------------------------------------------
# 8. Save outputs
# ------------------------------------------------------------
df.to_csv(OUTPUT_PATH, index=False)
ret_stats.to_csv(os.path.join(TABLES_DIR, "returns_summary_statistics.csv"), index=False)

print(f"\nReturns dataset saved to: {OUTPUT_PATH}")
print(f"Returns summary stats saved to: {os.path.join(TABLES_DIR, 'returns_summary_statistics.csv')}")