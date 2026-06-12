# Return and Volatility Dynamics of NIFTY 50: A Financial Econometrics Study (2023–2026)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas Version](https://img.shields.io/badge/Pandas-2.0%2B-darkblue.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Statsmodels](https://img.shields.io/badge/Statsmodels-0.14%2B-green.svg?logo=statsmodels&logoColor=white)](https://www.statsmodels.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Domain](https://img.shields.io/badge/Quantitative--Finance-Risk--Analytics-gold.svg)](https://github.com/dchatterjee01-prog)

---

## 👤 Author Information
* **Name:** Daipayan Chatterjee
* **Academic Credentials:** M.Sc. Economics (Specialization: Quantitative Financial Econometrics & Time-Series Modeling)
* **GitHub Profile:** [@dchatterjee01-prog](https://github.com/dchatterjee01-prog)


---

## 🖥️ Interactive Research Deliverables
> **Hiring Managers & Reviewers:** You can access and interact with the production slide deck built for this project directly in your web browser without downloading any files.
>
> 🌐 **[Click Here to Launch the Live Interactive Slide Presentation](https://dchatterjee01-prog.github.io/nifty50-econometrics-volatility-dynamics/presentation/)**

---
## 📈 Introduction & Research Motivation
Traditional asset valuation frameworks frequently evaluate risk under assumptions of normal distribution structures and constant variance patterns over time. However, real-world financial time-series observations consistently demonstrate asymmetric deviations, fat tails (leptokurtosis), and periods of variance clustering. 

This study develops a modular financial econometrics and quantitative risk management architecture in Python to examine the dynamic behavior of returns and conditional volatility within the **NIFTY 50 index** over a 3.5-year horizon spanning **January 1, 2023, to May 31, 2026**. By moving beyond simple exploratory metrics, this project models conditional variances, tests for stationarity properties, and isolates extreme tail risk dependencies across shifting macroeconomic regimes.

---

## 🎯 Core Research Objectives
1. **Mathematical Optimization:** Convert raw daily closing indices into additive, continuously compounded log-return distributions.
2. **Stationarity Diagnostics:** Confirm structural asset properties and test integration traits via formal statistical indicators.
3. **Volatility Clustering Quantification:** Isolate and confirm time-varying conditional variance behaviors using Lagrange Multiplier (LM) frameworks.
4. **Parametric Volatility Estimation:** Fit a parametric GARCH(1,1) engine to capture conditional variance dynamics and quantify asset risk persistence.
5. **Tail-Risk Quantification:** Compute dynamic historical and parametric Value-at-Risk (VaR) targets along with Maximum Drawdown profiles for stress-testing market cycles.

---

## 🗄️ Dataset Description
* **Asset Universe:** NIFTY 50 Index (National Stock Exchange, India)
* **Sampling Horizon:** January 01, 2023 – May 31, 2026
* **Frequency:** Daily Market Closing Ticks
* **Primary Source Ingestion:** `data/raw/NIFTY50_Daily_Data.csv`
* **Computed Elements:** Log Returns ($R_t$), 30-Day Moving Standard Deviations, GARCH Conditional Variances ($\sigma_t^2$), Parametric/Historical Value-at-Risk quantiles.

---

## 🔬 Methodology & Mathematical Formulations

### 1. Log Return Ingestion Engine
Nominal values are transformed into log space to ensure compounding additivity across time-series windows:
$$R_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$$

### 2. Stationarity Diagnostics (Augmented Dickey-Fuller Test)
Assesses integration mechanics to ensure modeling variables are non-spurious:
$$\Delta R_t = \alpha_0 + \gamma R_{t-1} + \sum_{j=1}^{p} \beta_j \Delta R_{t-j} + \varepsilon_t$$
* **$H_0$:** $\gamma = 0$ (Unit Root / Non-Stationary)
* **$H_1$:** $\gamma < 0$ (Stationary Series)

### 3. Distributional Normality Diagnostics (Jarque-Bera Test)
Measures compliance with a normal distribution by testing for skewness and excess kurtosis coefficients:
$$JB = \frac{n}{6} \left( S^2 + \frac{(K - 3)^2}{4} \right)$$
* **$H_0$:** Series is normally distributed ($S=0, K=3$).
* **$H_1$:** Series exhibits fat tails or asymmetry.

### 4. Serial Dependence Diagnostics (Ljung-Box Test)
Evaluates return dependence profiles across specified lag parameters to detect lingering serial correlation:
$$Q = n(n+2) \sum_{k=1}^{m} \frac{\rho_k^2}{n-k}$$
* **$H_0$:** Residual values represent white noise.

### 5. Volatility Modeling Framework: GARCH(1,1)
To capture time-varying, persistent shifts in financial market variance, we optimize structural parameters under an asymmetric Gaussian innovation design:
$$\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$
* **Stability Constraint:** System equilibrium requires $\omega > 0, \alpha \ge 0, \beta \ge 0,$ and $\alpha + \beta < 1$.

### 6. Quantitative Risk Analysis Techniques
* **Value-at-Risk (VaR):** Implements parametric $\text{GARCH}(1,1)$ distribution models paired with non-parametric historical simulation curves at a 95% and 99% confidence interval.
* **Maximum Drawdown (MDD):** Traces peak-to-trough capital erosions across rolling micro-cycles to evaluate maximum historical stress scenarios.
$$\text{MDD}_t = \frac{P_t - \max_{\tau \le t}(P_\tau)}{\max_{\tau \le t}(P_\tau)}$$

---

## 📊 Empirical Diagnostic Test Matrix

| Statistical Framework | Test Statistic | p-Value | Hypothesis Status | Economic Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Augmented Dickey-Fuller** | `-24.412` | `< 0.0001` | **Reject $H_0$** | Log returns are stationary $I(0)$. No unit root. |
| **Jarque-Bera** | `742.190` | `< 0.0001` | **Reject $H_0$** | Distribution exhibits fat tails and skewness. Non-Gaussian. |
| **Ljung-Box Q(10)** | `34.120` | `0.0002` | **Reject $H_0$** | Serial correlation is present in squared return windows. |
| **ARCH-LM Engine** | `112.540` | `< 0.0001` | **Reject $H_0$** | Significant conditional heteroscedasticity confirmed. |

---

## 🛠️ Complete Project Folder Hierarchy
```text
nifty50-econometrics-volatility-dynamics/
├── data/
│   ├── raw/
│   │   └── NIFTY50_Daily_Data.csv
│   └── processed/
│       └── clean_nifty_returns.csv
├── src/
│   ├── data_processor.py
│   ├── statistical_tests.py
│   ├── volatility_models.py
│   └── risk_analytics.py
├── outputs/
│   ├── graphs/
│   └── tables/
├── presentation/
│   └── NIFTY50_Econometrics_SlideDeck.pptx
├── report/
│   └── Return_and_Volatility_Dynamics_NIFTY50_Report.pdf
├── notebooks/
├── images/
├── docs/
├── tests/
└── assets/