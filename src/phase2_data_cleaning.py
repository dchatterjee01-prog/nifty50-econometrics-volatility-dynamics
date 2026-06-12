"""
Phase 2: Data Cleaning
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Purpose:
    - Load raw NIFTY 50 data downloaded via yfinance
    - Fix the malformed header (common yfinance multi-index CSV issue)
    - Convert data types (Date -> datetime, OHLCV -> numeric)
    - Remove duplicates, handle missing values
    - Sort chronologically and verify integrity
    - Save a clean dataset for downstream analysis

Input:
    data/raw/NIFTY50_Daily_Data.csv

Output:
    data/processed/clean_nifty.csv
"""

import pandas as pd
import numpy as np
import os

# ------------------------------------------------------------
# 1. Setup paths
# ------------------------------------------------------------
RAW_PATH = os.path.join("data", "raw", "NIFTY50_Daily_Data.csv")
PROCESSED_PATH = os.path.join("data", "processed", "clean_nifty.csv")

os.makedirs(os.path.join("data", "processed"), exist_ok=True)

# ------------------------------------------------------------
# 2. Load raw data, skipping the malformed yfinance header rows
# ------------------------------------------------------------
# Rows 2 and 3 (0-indexed: 1 and 2 after the header) contain
# "Ticker" and "Date" junk rows left over from yfinance's
# multi-level column structure. We skip them on read.
df = pd.read_csv(RAW_PATH, skiprows=[1, 2])

print("Raw shape after skipping junk rows:", df.shape)
print(df.head())

# ------------------------------------------------------------
# 3. Rename 'Price' column to 'Date'
# ------------------------------------------------------------
df = df.rename(columns={"Price": "Date"})

# ------------------------------------------------------------
# 4. Convert data types
# ------------------------------------------------------------
# Convert Date column to proper datetime format
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Convert OHLCV columns to numeric (in case any are read as strings)
numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------
# 5. Inspect dataset
# ------------------------------------------------------------
print("\n--- Dataset Info ---")
print(df.info())

print("\n--- Missing Values per Column ---")
print(df.isnull().sum())

print("\n--- Date Range ---")
print("Start:", df["Date"].min())
print("End:", df["Date"].max())

# ------------------------------------------------------------
# 6. Remove duplicates
# ------------------------------------------------------------
before = df.shape[0]
df = df.drop_duplicates()
after = df.shape[0]
print(f"\nDuplicates removed: {before - after}")

# ------------------------------------------------------------
# 7. Handle missing values
# ------------------------------------------------------------
# Any row where Date is NaN (failed conversion) cannot be used
df = df.dropna(subset=["Date"])

# For OHLCV columns, if any value is missing on a trading day,
# forward-fill from the previous valid trading day. This is
# standard practice for financial time series (assumes price
# stayed constant until the next observed value).
missing_before = df[numeric_cols].isnull().sum().sum()
df[numeric_cols] = df[numeric_cols].ffill()
missing_after = df[numeric_cols].isnull().sum().sum()

print(f"\nMissing OHLCV values before fill: {missing_before}")
print(f"Missing OHLCV values after fill:  {missing_after}")

# Drop any remaining rows with missing values (e.g. if the very
# first row had no prior value to forward-fill from)
df = df.dropna(subset=numeric_cols)

# ------------------------------------------------------------
# 8. Sort data chronologically and reset index
# ------------------------------------------------------------
df = df.sort_values("Date").reset_index(drop=True)

# ------------------------------------------------------------
# 9. Verify integrity
# ------------------------------------------------------------
# Check for duplicate dates (should be none in a clean series)
duplicate_dates = df["Date"].duplicated().sum()
print(f"\nDuplicate dates remaining: {duplicate_dates}")

# Check that High >= Low, High >= Open/Close, Low <= Open/Close
# (basic sanity check on OHLC consistency)
invalid_rows = df[
    (df["High"] < df["Low"]) |
    (df["High"] < df["Open"]) |
    (df["High"] < df["Close"]) |
    (df["Low"] > df["Open"]) |
    (df["Low"] > df["Close"])
]
print(f"Rows with inconsistent OHLC values: {len(invalid_rows)}")

if len(invalid_rows) > 0:
    print(invalid_rows)

# ------------------------------------------------------------
# 10. Final checks and save
# ------------------------------------------------------------
print("\n--- Final Cleaned Dataset ---")
print("Shape:", df.shape)
print(df.head())
print(df.tail())

df.to_csv(PROCESSED_PATH, index=False)
print(f"\nClean dataset saved to: {PROCESSED_PATH}")