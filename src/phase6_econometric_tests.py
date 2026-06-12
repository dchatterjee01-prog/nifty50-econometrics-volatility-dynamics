"""
Phase 6: Financial Econometrics Analysis
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Purpose:
    - Test for stationarity (Augmented Dickey-Fuller Test)
    - Test for normality of returns (Jarque-Bera Test)
    - Test for autocorrelation in returns and squared returns
      (Ljung-Box Test) - the latter is a precursor to ARCH effects

Input:
    data/processed/nifty_returns.csv

Output:
    outputs/tables/econometric_tests_summary.csv
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy.stats import jarque_bera
import os

# ------------------------------------------------------------
# 1. Setup paths
# ------------------------------------------------------------
DATA_PATH = os.path.join("data", "processed", "nifty_returns.csv")
TABLES_DIR = os.path.join("outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# ------------------------------------------------------------
# 2. Load data
# ------------------------------------------------------------
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
prices = df["Close"]
returns = df["Log_Return"].dropna()

results = {}

# ==============================================================
# A. AUGMENTED DICKEY-FULLER (ADF) TEST
# ==============================================================
"""
PURPOSE:
    Test whether a time series is stationary (i.e., its statistical
    properties - mean, variance - do not change over time).

HYPOTHESES:
    H0: The series has a unit root (i.e., it is NON-stationary)
    H1: The series is stationary

TEST EQUATION:
    The ADF test regresses the change in the series on a lagged
    level and lagged differences:

        ΔY_t = α + βt + γY_{t-1} + Σ δ_i ΔY_{t-i} + ε_t

    The test statistic is based on γ:
        - If γ = 0 -> unit root -> non-stationary
        - If γ < 0 (significantly) -> stationary

DECISION RULE:
    If p-value < 0.05 -> reject H0 -> series is stationary
    If p-value >= 0.05 -> fail to reject H0 -> non-stationary

EXPECTED RESULT FOR THIS PROJECT:
    - Price levels (Close): typically NON-stationary (trending series)
    - Log returns: typically STATIONARY (mean-reverting around 0)

    This is exactly why econometric models are applied to RETURNS,
    not raw prices.
"""

print("=" * 60)
print("A. AUGMENTED DICKEY-FULLER (ADF) TEST")
print("=" * 60)

# --- ADF on Price Levels ---
adf_price = adfuller(prices.dropna(), autolag="AIC")
print("\n--- ADF Test on Price Levels (Close) ---")
print(f"ADF Statistic: {adf_price[0]:.4f}")
print(f"p-value: {adf_price[1]:.4f}")
print(f"Critical Values: {adf_price[4]}")
if adf_price[1] < 0.05:
    print("Conclusion: Reject H0 -> Price series is STATIONARY")
else:
    print("Conclusion: Fail to reject H0 -> Price series is NON-STATIONARY")

# --- ADF on Log Returns ---
adf_returns = adfuller(returns, autolag="AIC")
print("\n--- ADF Test on Log Returns ---")
print(f"ADF Statistic: {adf_returns[0]:.4f}")
print(f"p-value: {adf_returns[1]:.4f}")
print(f"Critical Values: {adf_returns[4]}")
if adf_returns[1] < 0.05:
    print("Conclusion: Reject H0 -> Returns series is STATIONARY")
else:
    print("Conclusion: Fail to reject H0 -> Returns series is NON-STATIONARY")

results["ADF_Price_Statistic"] = adf_price[0]
results["ADF_Price_pvalue"] = adf_price[1]
results["ADF_Returns_Statistic"] = adf_returns[0]
results["ADF_Returns_pvalue"] = adf_returns[1]

# ==============================================================
# B. JARQUE-BERA TEST
# ==============================================================
"""
PURPOSE:
    Test whether a series follows a normal distribution, based on
    its sample skewness and kurtosis.

HYPOTHESES:
    H0: The series is normally distributed (skewness = 0, excess kurtosis = 0)
    H1: The series is NOT normally distributed

TEST STATISTIC:
    JB = (n/6) * [ S^2 + (1/4)*(K-3)^2 ]

    where:
        n = number of observations
        S = sample skewness
        K = sample kurtosis (not excess)

    Under H0, JB ~ Chi-squared distribution with 2 degrees of freedom.

DECISION RULE:
    If p-value < 0.05 -> reject H0 -> NOT normally distributed
    If p-value >= 0.05 -> fail to reject H0 -> normally distributed

EXPECTED RESULT FOR THIS PROJECT:
    Financial returns almost universally REJECT normality due to
    fat tails (excess kurtosis) and slight skewness - a stylized
    fact known as "leptokurtosis" in financial markets.
"""

print("\n" + "=" * 60)
print("B. JARQUE-BERA TEST")
print("=" * 60)

jb_stat, jb_pvalue = jarque_bera(returns)
print(f"\nJarque-Bera Statistic: {jb_stat:.4f}")
print(f"p-value: {jb_pvalue:.6f}")
if jb_pvalue < 0.05:
    print("Conclusion: Reject H0 -> Returns are NOT normally distributed")
else:
    print("Conclusion: Fail to reject H0 -> Returns appear normally distributed")

results["JarqueBera_Statistic"] = jb_stat
results["JarqueBera_pvalue"] = jb_pvalue

# ==============================================================
# C. LJUNG-BOX TEST
# ==============================================================
"""
PURPOSE:
    Test for the presence of autocorrelation (serial correlation)
    in a time series at multiple lags simultaneously.

HYPOTHESES:
    H0: The series shows no autocorrelation up to lag k
        (observations are independently distributed / "white noise")
    H1: The series shows autocorrelation at one or more lags

TEST STATISTIC:
    Q = n(n+2) * Σ [ ρ_k^2 / (n-k) ]   for k = 1 to h

    where:
        n = number of observations
        ρ_k = sample autocorrelation at lag k
        h = number of lags tested

    Under H0, Q ~ Chi-squared distribution with h degrees of freedom.

DECISION RULE:
    If p-value < 0.05 -> reject H0 -> series shows significant
                          autocorrelation
    If p-value >= 0.05 -> fail to reject H0 -> no significant
                          autocorrelation (white noise)

TWO APPLICATIONS HERE:
    1. Ljung-Box on RETURNS:
       Tests whether past returns help predict future returns
       (relevant for weak-form market efficiency).

    2. Ljung-Box on SQUARED RETURNS:
       Tests whether past squared returns (i.e., past volatility)
       predict future squared returns. Significant autocorrelation
       here is evidence of ARCH effects / volatility clustering -
       directly motivating Phase 7 (GARCH modeling).
"""

print("\n" + "=" * 60)
print("C. LJUNG-BOX TEST")
print("=" * 60)

# --- Ljung-Box on Returns (test for autocorrelation in mean) ---
lb_returns = acorr_ljungbox(returns, lags=[10], return_df=True)
print("\n--- Ljung-Box Test on Returns (lag=10) ---")
print(lb_returns)
lb_ret_stat = lb_returns["lb_stat"].iloc[0]
lb_ret_pvalue = lb_returns["lb_pvalue"].iloc[0]
if lb_ret_pvalue < 0.05:
    print("Conclusion: Reject H0 -> Returns show significant autocorrelation")
else:
    print("Conclusion: Fail to reject H0 -> Returns resemble white noise")

# --- Ljung-Box on Squared Returns (test for ARCH effects) ---
squared_returns = returns ** 2
lb_squared = acorr_ljungbox(squared_returns, lags=[10], return_df=True)
print("\n--- Ljung-Box Test on Squared Returns (lag=10) ---")
print(lb_squared)
lb_sq_stat = lb_squared["lb_stat"].iloc[0]
lb_sq_pvalue = lb_squared["lb_pvalue"].iloc[0]
if lb_sq_pvalue < 0.05:
    print("Conclusion: Reject H0 -> Squared returns show significant "
          "autocorrelation (evidence of ARCH effects / volatility clustering)")
else:
    print("Conclusion: Fail to reject H0 -> No significant ARCH effects detected")

results["LjungBox_Returns_Statistic"] = lb_ret_stat
results["LjungBox_Returns_pvalue"] = lb_ret_pvalue
results["LjungBox_SquaredReturns_Statistic"] = lb_sq_stat
results["LjungBox_SquaredReturns_pvalue"] = lb_sq_pvalue

# ------------------------------------------------------------
# 3. Save all results to a summary table
# ------------------------------------------------------------
results_df = pd.DataFrame(results.items(), columns=["Test", "Value"])
results_df.to_csv(os.path.join(TABLES_DIR, "econometric_tests_summary.csv"), index=False)

print("\n" + "=" * 60)
print("All test results saved to: outputs/tables/econometric_tests_summary.csv")
print("=" * 60)