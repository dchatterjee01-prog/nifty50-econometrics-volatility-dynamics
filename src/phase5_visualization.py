"""
Phase 5: Data Visualization
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Purpose:
    - Generate publication-quality visualizations of price and
      return series for the research report and presentation
    - All figures are saved automatically to outputs/graphs/

Input:
    data/processed/nifty_returns.csv

Output (saved to outputs/graphs/):
    1. closing_price_trend.png
    2. daily_return_trend.png
    3. return_histogram.png
    4. return_kde.png
    5. return_boxplot.png
    6. rolling_mean.png
    7. rolling_volatility.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ------------------------------------------------------------
# 1. Setup paths and styling
# ------------------------------------------------------------
DATA_PATH = os.path.join("data", "processed", "nifty_returns.csv")
GRAPH_DIR = os.path.join("outputs", "graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

# Color palette - consistent across all charts
COLOR_PRICE = "#1f4e79"     # deep blue
COLOR_RETURN = "#2e8b57"    # sea green
COLOR_NEG = "#c0392b"       # red for negative/volatility highlights
COLOR_VOL = "#8e44ad"        # purple for volatility

# ------------------------------------------------------------
# 2. Load data
# ------------------------------------------------------------
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

print("Data loaded. Shape:", df.shape)

# ------------------------------------------------------------
# 3. Chart 1: NIFTY Closing Price Trend
# ------------------------------------------------------------
plt.figure()
plt.plot(df["Date"], df["Close"], color=COLOR_PRICE, linewidth=1.5)
plt.title("NIFTY 50 Closing Price (2023-2026)", fontsize=16, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Closing Price (INR)")
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "closing_price_trend.png"))
plt.close()
print("Saved: closing_price_trend.png")

# ------------------------------------------------------------
# 4. Chart 2: Daily Log Return Trend
# ------------------------------------------------------------
plt.figure()
plt.plot(df["Date"], df["Log_Return_pct"], color=COLOR_RETURN, linewidth=0.7)
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.title("NIFTY 50 Daily Log Returns (2023-2026)", fontsize=16, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Log Return (%)")
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "daily_return_trend.png"))
plt.close()
print("Saved: daily_return_trend.png")

# ------------------------------------------------------------
# 5. Chart 3: Histogram of Returns (with Normal overlay)
# -----------------------------