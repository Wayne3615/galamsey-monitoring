# Galamsey Atmospheric Pollution Monitoring System

**AI-Based Spatiotemporal Monitoring of Illegal Artisanal Mining and Its Atmospheric Pollution Impact in Ghana**

> MSc Data Science Thesis — University of Ghana, 2026  
> Regions: Western & Ashanti | Study Period: 2019–2024 | 52 Districts

---

## Overview

Galamsey — Ghana's term for illegal artisanal and small-scale gold mining — has caused widespread environmental degradation across the Western and Ashanti regions, contaminating water bodies, destroying forest cover, and releasing harmful atmospheric pollutants. Despite government enforcement efforts, monitoring the spatial and temporal spread of galamsey activity at district scale remains a significant data challenge.

This thesis develops a machine learning pipeline that fuses **Sentinel-2 multispectral imagery** and **Sentinel-5P TROPOMI atmospheric data** extracted via **Google Earth Engine (GEE)** to construct a monthly **Pollution Risk Score (PRS)** for 52 districts from January 2019 to December 2024. Random Forest and XGBoost models are trained to identify districts at elevated risk, and results are delivered through an interactive **Streamlit dashboard**.

---

## Research Objectives

1. Characterise the spatiotemporal dynamics of galamsey-linked land degradation using remote sensing indices (NDVI, BSI, MNDWI, NDMI).
2. Quantify atmospheric pollution burdens (aerosol index, NO₂, SO₂) attributable to mining activity across districts.
3. Construct a composite Pollution Risk Score (PRS) integrating surface and atmospheric indicators.
4. Evaluate the impact of Ghana's 2021 enforcement interventions on pollution trajectories.
5. Identify and rank districts by risk tier to inform policy targeting.

---

## Data Sources

| Dataset | Satellite / Product | GEE Collection ID | Resolution | Variables |
|---|---|---|---|---|
| Surface reflectance | Sentinel-2 MSI L2A | `COPERNICUS/S2_SR` | 10–20 m | NDVI, BSI, MNDWI, NDMI |
| Aerosol index | Sentinel-5P TROPOMI | `COPERNICUS/S5P/OFFL/L3_AER_AI` | 3.5 km | UV Aerosol Index |
| Nitrogen dioxide | Sentinel-5P TROPOMI | `COPERNICUS/S5P/OFFL/L3_NO2` | 3.5 km | Tropospheric NO₂ column density |
| Sulphur dioxide | Sentinel-5P TROPOMI | `COPERNICUS/S5P/OFFL/L3_SO2` | 3.5 km | Total SO₂ column density |

Monthly district-level composites were computed in GEE by median-aggregating cloud-masked imagery over each district boundary polygon. The final master dataset spans **72 monthly observations × 52 districts = 3,744 district-month records**.

---

## Features

### Remote Sensing Indices

| Index | Formula | Interpretation |
|---|---|---|
| NDVI | (NIR − Red) / (NIR + Red) | Vegetation cover; decline signals land clearance |
| BSI | ((SWIR1 + Red) − (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue)) | Bare soil exposure; increase signals surface disturbance |
| MNDWI | (Green − SWIR1) / (Green + SWIR1) | Water body extent and turbidity proxy |
| NDMI | (NIR − SWIR1) / (NIR + SWIR1) | Moisture content; drainage disruption indicator |

### Engineered Features
- 3-month rolling means of NDVI and aerosol index
- Month-of-year cyclical encoding (sin/cos) for seasonal modelling
- Binary dry season flag (Nov–Mar)
- Mining × dry-season interaction term
- Year-on-year change features for NDVI and BSI

### Pollution Risk Score (PRS)
A composite index constructed as a weighted combination of normalised aerosol index, NO₂ column density, and SO₂ column density — scaled 0–1 across the full district-month panel. Higher PRS values indicate greater atmospheric pollution burden consistent with active mining.

---

## Methodology

```
Google Earth Engine
  ├── Sentinel-2 S2_SR  ──► Cloud masking → Band math → District median composites
  └── Sentinel-5P TROPOMI ──► Filtering → District mean composites
              │
              ▼
    Feature Engineering (NDVI, BSI, MNDWI, NDMI, rolling stats, seasonality)
              │
              ▼
    PRS Construction (normalised aerosol + NO2 + SO2 composite)
              │
              ▼
    ┌─────────────────────────────┐
    │   Machine Learning Models   │
    │  ├── Random Forest          │
    │  └── XGBoost                │
    │  Evaluation: RMSE, R², MAE  │
    └─────────────────────────────┘
              │
              ▼
    SHAP Explainability (feature importance + summary plots)
              │
              ▼
    District Risk Tiering (Critical / High / Moderate / Low)
              │
              ▼
    Streamlit Dashboard (interactive filtering, trend plots, rankings)
```

---

## Repository Structure

```
galamsey_thesis/
│
├── dashboard.py                       # Streamlit interactive dashboard
│
├── data/
│   ├── galamsey_master.csv            # Full 3,744-record panel dataset
│   ├── s5p_aerosol_v2.csv             # Sentinel-5P aerosol index extracts
│   ├── s5p_no2_v2.csv                 # Sentinel-5P NO₂ column density extracts
│   ├── s5p_so2_v2.csv                 # Sentinel-5P SO₂ column density extracts
│   └── sentinel2_ghana_2019_2024.csv  # Sentinel-2 surface reflectance indices
│
├── notebooks/
│   └── galamsey_analysis.ipynb        # Full pipeline: EDA → modelling → SHAP
│
├── outputs/
│   ├── district_risk_rankings.csv     # Final district PRS rankings and risk tiers
│   ├── 01_feature_distributions.png
│   ├── 02_district_prs_ranking.png
│   ├── 03_seasonal_patterns.png
│   ├── 04_mining_vs_nonmining.png
│   ├── 05_annual_trends.png
│   ├── 06_correlation_matrix.png
│   ├── 07_shap_importance.png
│   ├── 08_shap_summary.png
│   ├── 09_predicted_vs_actual.png
│   └── 11_regional_trend.png
│
└── README.md
```

---

## Key Findings

- **52 districts** monitored across the Western and Ashanti regions over 72 monthly time steps.
- Aerosol index is the strongest individual predictor of PRS, followed by NDVI change and BSI.
- **Dry season months (Nov–Mar)** consistently show elevated PRS, reflecting intensified mining activity during low-rainfall periods.
- A measurable post-enforcement decline in mean PRS was observed following Ghana's July 2021 crackdown, though several critical districts showed renewed increases by 2023–2024.
- The top-ranked **Critical** risk districts are concentrated in the Ashanti Region, with Asokore Mampong Municipal and KMA recording the highest mean PRS values over the study period.
- SHAP analysis confirms that the aerosol index, 3-month rolling aerosol mean, and NDVI are the dominant model drivers.

---

## Dashboard

The Streamlit dashboard provides an interactive interface for exploring results:

- **KPI metrics**: district count, mean PRS, critical-tier count, study period
- **Time-series trend viewer**: filterable by district and year range across four pollution indicators (PRS, aerosol index, NO₂, SO₂)
- **District risk rankings table**: top 20 districts with colour-coded risk tiers
- **Seasonal pattern chart**: mean PRS by month highlighting dry vs. wet season contrast
- **Annual trend chart**: year-on-year PRS trajectory with July 2021 enforcement marker
- **Full summary table**: all 52 districts with mean PRS, aerosol, NO₂, and 2019→2024 PRS change

### Running the Dashboard Locally

```bash
# 1. Clone the repository
git clone https://github.com/Wayne3615/galamsey-monitoring.git
cd galamsey-monitoring

# 2. Install dependencies
pip install streamlit pandas numpy matplotlib

# 3. Update DATA_DIR and OUT_DIR paths in dashboard.py to match your local paths

# 4. Launch the dashboard
streamlit run dashboard.py
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `pandas` | Data manipulation and time-series handling |
| `numpy` | Numerical operations |
| `matplotlib` | Static visualisation |
| `streamlit` | Interactive dashboard framework |
| `scikit-learn` | Random Forest model and evaluation metrics |
| `xgboost` | Gradient boosting model |
| `shap` | Model explainability (SHAP values) |

---

## Citation

If you reference this work, please cite:

```
Wezena, S. (2026). AI-Based Spatiotemporal Monitoring of Illegal Artisanal Mining
and Its Atmospheric Pollution Impact in Ghana. MSc Data Science Thesis,
University of Ghana, Legon.
```

---

## Acknowledgements

- **Google Earth Engine** for cloud-based satellite data extraction
- **European Space Agency (ESA) / Copernicus Programme** for open Sentinel-2 and Sentinel-5P data
- **University of Ghana, Department of Computer Science** for academic support
- Ghana's **Minerals Commission** and **Environmental Protection Agency (EPA)** for contextual reference on mining district boundaries

---

## Licence

This repository is shared for academic and research purposes. Please contact the author before reusing data or code in derivative works.

---

*Data: Sentinel-2 (COPERNICUS/S2_SR) and Sentinel-5P TROPOMI (COPERNICUS/S5P/OFFL) via Google Earth Engine. Western & Ashanti Regions, Ghana. MSc Data Science Thesis — University of Ghana, 2026.*
