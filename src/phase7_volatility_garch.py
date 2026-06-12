"""
Phase 7: Volatility Analysis
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Purpose:
    - Formally test for ARCH effects (Engle's ARCH-LM test)
    - Estimate a GARCH(1,1) model on NIFTY 50 log returns
    - Extract and plot conditional volatility
    - Interpret model parameters

Input:
    data/processed/nifty_returns.csv

Output:
    outputs/tables/arch_lm_test.csv
    outputs/tables/garch_results_summary.csv
    outputs/graphs/conditional_volatility.png
    data/processed/nifty_returns.csv (updated with conditional volatility column)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.diagnostic import het_arch
from arch import arch_model
import os

# ------------------------------------------------------------
# 1. Setup paths
# ------------------------------------------------------------
DATA_PATH = os.path.join("data", "processed", "nifty_returns.csv")
TABLES_DIR = os.path.join("outputs", "tables")
GRAPH_DIR = os.path.join("outputs", "graphs")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

# ------------------------------------------------------------
# 2. Load data
# ------------------------------------------------------------
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Use percentage log returns (standard for the arch package -
# improves numerical optimization stability)
returns_pct = df["Log_Return_pct"].dropna()

# ==============================================================
# A. ENGLE'S ARCH-LM TEST (Test for ARCH Effects)
# ==============================================================
"""
PURPOSE:
    Formally test whether a return series exhibits ARCH effects
    (i.e., whether the variance of returns is time-varying and
    predictable from past squared returns).

HYPOTHESES:
    H0: No ARCH effects (residuals are homoscedastic / constant variance)
    H1: ARCH effects present (heteroscedasticity - variance depends
        on past squared errors)

TEST PROCEDURE (Engle, 1982):
    1. Regress squared returns on their own lagged values:
           ε²_t = α0 + α1*ε²_{t-1} + α2*ε²_{t-2} + ... + αq*ε²_{t-q} + v_t
    2. Test the joint significance of α1,...,αq using an LM
       (Lagrange Multiplier) statistic:
           LM = n * R²  ~  Chi-squared(q)

DECISION RULE:
    If p-value < 0.05 -> reject H0 -> ARCH effects present ->
        GARCH-type modeling is justified
"""

print("=" * 60)
print("A. ENGLE'S ARCH-LM TEST")
print("=" * 60)

arch_test = het_arch(returns_pct, nlags=10)
lm_stat, lm_pvalue, f_stat, f_pvalue = arch_test

print(f"\nLM Statistic: {lm_stat:.4f}")
print(f"LM p-value: {lm_pvalue:.6f}")
print(f"F-Statistic: {f_stat:.4f}")
print(f"F p-value: {f_pvalue:.6f}")

if lm_pvalue < 0.05:
    print("\nConclusion: Reject H0 -> ARCH effects ARE present.")
    print("GARCH modeling is statistically justified.")
else:
    print("\nConclusion: Fail to reject H0 -> No significant ARCH effects.")

arch_lm_df = pd.DataFrame({
    "Statistic": ["LM Statistic", "LM p-value", "F Statistic", "F p-value"],
    "Value": [lm_stat, lm_pvalue, f_stat, f_pvalue]
})
arch_lm_df.to_csv(os.path.join(TABLES_DIR, "arch_lm_test.csv"), index=False)

# =====================================