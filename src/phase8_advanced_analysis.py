"""
Phase 8: Advanced Analysis (Project Differentiators)
Project: Return and Volatility Dynamics of NIFTY 50 (2023-2026)

Analyses:
    1. Value at Risk (VaR) & Conditional VaR (Expected Shortfall)
       - Historical Simulation method
       - Parametric (GARCH-based) method
    2. Maximum Drawdown Analysis
    3. Volatility Regime Detection (High vs Low volatility periods)

Input:
    data/processed/nifty_returns.csv (must include Conditional_Volatility_pct
    from Phase 7)

Output:
    outputs/tables/var_cvar_summary.csv
    outputs/tables/drawdown_summary.csv
    outputs/tables/regime_summary.csv
    outputs/graphs/var_distribution.png
    outputs/graphs/drawdown_chart.png
    outputs/graphs/volatility_regimes.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
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

returns = df["Log_Return"].dropna()
returns_pct = df["Log_Return_pct"].dropna()

# ==============================================================
# ANALYSIS 1: VALUE AT RISK (VaR) AND CONDITIONAL VaR (CVaR)
# ==============================================================
"""
PURPOSE:
    Quantify the maximum expected loss over a given time horizon
    at a given confidence level - a core risk management metric
    used by banks, funds, and regulators (Basel framework).

DEFINITIONS:
    VaR at confidence level (1-α):
        P(R_t < -VaR) = α

    In words: "There is an α% chance that the loss on a given day
    will exceed VaR."

CVaR (Expected Shortfall):
    CVaR = E[R_t | R_t < -VaR]

    In words: "Given that a loss exceeds VaR, what is the AVERAGE
    size of that loss?" CVaR is considered a more informative risk
    measure because it accounts for the SEVERITY of tail losses,
    not just their probability.

METHOD 1 - HISTORICAL SIMULATION:
    VaR_hist = -percentile(returns, α)
    CVaR_hist = -mean(returns | returns < -VaR_hist)

    Makes no distributional assumption - uses actual historical
    return distribution. Limitation: assumes the past is
    representative of the future.

METHOD 2 - PARAMETRIC (GARCH-based):
    VaR_garch_t = -(μ + z_α * σ_t)

    where:
        μ     = mean return (often assumed ~0 for daily returns)
        z_α   = critical value from standard normal distribution
                (e.g., z_0.05 = -1.645 for 95% confidence)
        σ_t   = GARCH conditional volatility at time t

    KEY ADVANTAGE: This produces a TIME-VARYING VaR that responds
    to current market conditions - VaR is higher during volatile
    periods (e.g., 2024) and lower during calm periods. This is
    the modern, industry-standard approach (vs. a single static
    historical number).
"""

print("=" * 60)
print("ANALYSIS 1: VALUE AT RISK (VaR) AND CONDITIONAL VaR (CVaR)")
print("=" * 60)

confidence_levels = [0.95, 0.99]
var_results = []

for cl in confidence_levels:
    alpha = 1 - cl

    # --- Historical Simulation VaR & CVaR ---
    var_hist = -np.percentile(returns, alpha * 100)
    tail_losses = returns[returns < -var_hist]
    cvar_hist = -tail_losses.mean()

    var_results.append({
        "Method": "Historical Simulation",
        "Confidence Level": f"{int(cl*100)}%",
        "VaR (daily, %)": var_hist * 100,
        "CVaR (daily, %)": cvar_hist * 100
    })

    print(f"\n--- {int(cl*100)}% Confidence Level ---")
    print(f"Historical VaR:  {var_hist*100:.4f}%  "
          f"(on {alpha*100:.0f}% of days, expect to lose more than this)")
    print(f"Historical CVaR: {cvar_hist*100:.4f}%  "
          f"(average loss ON those worst days)")

# --- Parametric (GARCH-based) VaR - time varying ---
# Use the most recent conditional volatility from Phase 7
mu = returns.mean()
sigma_t = df["Conditional_Volatility_pct"].dropna() / 100  # convert to decimal

for cl in confidence_levels:
    alpha = 1 - cl
    z_alpha = norm.ppf(alpha)  # negative value, e.g. -1.645 for 5%

    var_garch_series = -(mu + z_alpha * sigma_t)
    latest_var_garch = var_garch_series.iloc[-1]

    var_results.append({
        "Method": "GARCH Parametric (latest)",
        "Confidence Level": f"{int(cl*100)}%",
        "VaR (daily, %)": latest_var_garch * 100,
        "CVaR (daily, %)": np.nan  # CVaR under normality shown separately below
    })

    print(f"\nGARCH-based (time-varying) {int(cl*100)}% VaR "
          f"as of {df['Date'].iloc[-1].date()}: {latest_var_garch*100:.4f}%")

var_df = pd.DataFrame(var_results)
var_df.to_csv(os.path.join(TABLES_DIR, "var_cvar_summary.csv"), index=False)

# --- Visualization: Return distribution with VaR thresholds ---
plt.figure()
sns.histplot(returns * 100, bins=60, color="#2e8b57", alpha=0.6, stat="density")
for cl in confidence_levels:
    alpha = 1 - cl
    var_hist = -np.percentile(returns, alpha * 100) * 100
    plt.axvline(-var_hist, color="#c0392b", linestyle="--",
                label=f"{int(cl*100)}% VaR = {var_hist:.2f}%")
plt.title("Return Distribution with Historical VaR Thresholds",
          fontsize=16, fontweight="bold")
plt.xlabel("Daily Log Return (%)")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "var_distribution.png"))
plt.close()
print("\nSaved: outputs/graphs/var_distribution.png")

# ==============================================================
# ANALYSIS 2: MAXIMUM DRAWDOWN ANALYSIS
# ==============================================================
"""
PURPOSE:
    Measure the largest peak-to-trough decline in cumulative value
    - i.e., "if you invested at the worst possible time, how much
    would you have lost before the index recovered?"

CALCULATION:
    1. Compute the cumulative return index:
           Cumulative_t = exp(cumsum(Log_Return))
    2. Compute the running maximum (peak so far):
           Peak_t = max(Cumulative_1, ..., Cumulative_t)
    3. Drawdown at time t:
           Drawdown_t = (Cumulative_t - Peak_t) / Peak_t

    Maximum Drawdown (MDD) = min(Drawdown_t) over the whole period
    (most negative value = largest decline)

INTERPRETATION:
    MDD is one of the most important metrics for risk-averse
    investors - it answers "what's the worst-case scenario I
    need to be psychologically/financially prepared for?"
    Unlike volatility, it captures SUSTAINED losses, not just
    single-day moves.
"""

print("\n" + "=" * 60)
print("ANALYSIS 2: MAXIMUM DRAWDOWN ANALYSIS")
print("=" * 60)

# Cumulative return index (starting at 1.0)
df["Cumulative_Return"] = np.exp(df["Log_Return"].fillna(0).cumsum())

# Running maximum (peak)
df["Running_Max"] = df["Cumulative_Return"].cummax()

# Drawdown series
df["Drawdown"] = (df["Cumulative_Return"] - df["Running_Max"]) / df["Running_Max"]

# Maximum drawdown
max_drawdown = df["Drawdown"].min()
max_dd_date = df.loc[df["Drawdown"].idxmin(), "Date"]

# Find the peak date before the trough, and recovery date (if any) after
trough_idx = df["Drawdown"].idxmin()
peak_idx = df.loc[:trough_idx, "Cumulative_Return"].idxmax()
peak_date = df.loc[peak_idx, "Date"]

# Recovery: first date after trough where Cumulative_Return >= peak value again
peak_value = df.loc[peak_idx, "Cumulative_Return"]
recovery_candidates = df.loc[trough_idx:][df.loc[trough_idx:, "Cumulative_Return"] >= peak_value]
recovery_date = recovery_candidates["Date"].iloc[0] if not recovery_candidates.empty else "Not yet recovered"

print(f"\nMaximum Drawdown: {max_drawdown*100:.2f}%")
print(f"Peak Date:    {peak_date.date()}")
print(f"Trough Date:  {max_dd_date.date()}")
print(f"Recovery Date: {recovery_date if isinstance(recovery_date, str) else recovery_date.date()}")
if isinstance(recovery_date, pd.Timestamp):
    drawdown_duration = (recovery_date - peak_date).days
    print(f"Total Drawdown Duration: {drawdown_duration} days")

drawdown_summary = pd.DataFrame({
    "Metric": ["Maximum Drawdown (%)", "Peak Date", "Trough Date", "Recovery Date"],
    "Value": [max_drawdown * 100, peak_date.date(), max_dd_date.date(),
              recovery_date if isinstance(recovery_date, str) else recovery_date.date()]
})
drawdown_summary.to_csv(os.path.join(TABLES_DIR, "drawdown_summary.csv"), index=False)

# --- Visualization: Drawdown chart ---
plt.figure()
plt.fill_between(df["Date"], df["Drawdown"] * 100, 0, color="#c0392b", alpha=0.5)
plt.plot(df["Date"], df["Drawdown"] * 100, color="#c0392b", linewidth=0.8)
plt.title("NIFTY 50 Drawdown from Running Peak", fontsize=16, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Drawdown (%)")
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "drawdown_chart.png"))
plt.close()
print("\nSaved: outputs/graphs/drawdown_chart.png")

# ==============================================================
# ANALYSIS 3: VOLATILITY REGIME DETECTION
# ==============================================================
"""
PURPOSE:
    Classify each trading day into a "High Volatility" or "Low
    Volatility" regime based on GARCH conditional volatility,
    and quantify how often / for how long the market was in each
    regime - a simplified, transparent alternative to a full
    Markov-Switching GARCH model.

METHOD:
    1. Take the GARCH conditional volatility series (from Phase 7)
    2. Define a threshold = median (or a chosen percentile) of
       conditional volatility over the full sample
    3. Classify:
           Regime_t = "High Volatility" if sigma_t > threshold
           Regime_t = "Low Volatility"  if sigma_t <= threshold
    4. Report: % of days in each regime, average volatility in
       each regime, and identify the longest high-volatility
       episodes (useful for linking to real-world events in your
       discussion section)

WHY THIS MATTERS:
    This converts a continuous GARCH output into an interpretable
    narrative: "NIFTY spent X% of the 2023-2026 period in a
    high-volatility regime, with the longest such episode lasting
    Y days, from [date] to [date]" - directly useful for your
    report's discussion of market events.
"""

print("\n" + "=" * 60)
print("ANALYSIS 3: VOLATILITY REGIME DETECTION")
print("=" * 60)

vol_series = df["Conditional_Volatility_pct"]
threshold = vol_series.median()

df["Volatility_Regime"] = np.where(vol_series > threshold,
                                     "High Volatility", "Low Volatility")

regime_counts = df["Volatility_Regime"].value_counts()
regime_pct = (regime_counts / len(df)) * 100

avg_vol_by_regime = df.groupby("Volatility_Regime")["Conditional_Volatility_Annualized_pct"].mean()

print(f"\nVolatility threshold (median daily cond. vol): {threshold:.4f}%")
print("\nDays in each regime:")
print(regime_counts)
print("\nPercentage of time in each regime:")
print(regime_pct.round(2))
print("\nAverage annualized volatility by regime:")
print(avg_vol_by_regime.round(2))

# --- Identify longest High Volatility episode ---
df["Regime_Change"] = (df["Volatility_Regime"] != df["Volatility_Regime"].shift()).cumsum()
episode_lengths = df.groupby(["Regime_Change", "Volatility_Regime"]).agg(
    Start=("Date", "first"),
    End=("Date", "last"),
    Days=("Date", "count")
).reset_index()

high_vol_episodes = episode_lengths[episode_lengths["Volatility_Regime"] == "High Volatility"]
longest_episode = high_vol_episodes.loc[high_vol_episodes["Days"].idxmax()]

print(f"\nLongest High-Volatility Episode:")
print(f"  Start: {longest_episode['Start'].date()}")
print(f"  End:   {longest_episode['End'].date()}")
print(f"  Duration: {longest_episode['Days']} trading days")

regime_summary = pd.DataFrame({
    "Metric": [
        "Volatility Threshold (%)",
        "% Days High Volatility",
        "% Days Low Volatility",
        "Avg Annualized Vol - High Regime (%)",
        "Avg Annualized Vol - Low Regime (%)",
        "Longest High-Vol Episode Start",
        "Longest High-Vol Episode End",
        "Longest High-Vol Episode Duration (days)"
    ],
    "Value": [
        threshold,
        regime_pct.get("High Volatility", 0),
        regime_pct.get("Low Volatility", 0),
        avg_vol_by_regime.get("High Volatility", np.nan),
        avg_vol_by_regime.get("Low Volatility", np.nan),
        longest_episode["Start"].date(),
        longest_episode["End"].date(),
        longest_episode["Days"]
    ]
})
regime_summary.to_csv(os.path.join(TABLES_DIR, "regime_summary.csv"), index=False)

# --- Visualization: Conditional volatility with regime shading ---
plt.figure()
plt.plot(df["Date"], df["Conditional_Volatility_Annualized_pct"],
         color="#34495e", linewidth=1)

# Shade high-volatility periods
in_high = False
start_date = None
for i in range(len(df)):
    if df["Volatility_Regime"].iloc[i] == "High Volatility" and not in_high:
        start_date = df["Date"].iloc[i]
        in_high = True
    elif df["Volatility_Regime"].iloc[i] != "High Volatility" and in_high:
        plt.axvspan(start_date, df["Date"].iloc[i], color="#e74c3c", alpha=0.15)
        in_high = False
if in_high:
    plt.axvspan(start_date, df["Date"].iloc[-1], color="#e74c3c", alpha=0.15)

plt.axhline(threshold * np.sqrt(252), color="#c0392b", linestyle="--",
            linewidth=1, label="Regime Threshold")
plt.title("NIFTY 50 Volatility Regimes (Shaded = High Volatility)",
          fontsize=16, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Annualized Conditional Volatility (%)")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "volatility_regimes.png"))
plt.close()
print("\nSaved: outputs/graphs/volatility_regimes.png")

# ------------------------------------------------------------
# Save updated dataframe
# ------------------------------------------------------------
df.to_csv(DATA_PATH, index=False)

print("\n" + "=" * 60)
print("Phase 8 complete. New outputs:")
print("  - outputs/tables/var_cvar_summary.csv")
print("  - outputs/tables/drawdown_summary.csv")
print("  - outputs/tables/regime_summary.csv")
print("  - outputs/graphs/var_distribution.png")
print("  - outputs/graphs/drawdown_chart.png")
print("  - outputs/graphs/volatility_regimes.png")
print("=" * 60)