import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title = "Galamsey Pollution Monitor — Ghana",
    page_icon  = "🌍",
    layout     = "wide"
)

DATA_DIR = r"C:\Users\stunn\galamsey_thesis\data"
OUT_DIR  = r"C:\Users\stunn\galamsey_thesis\outputs"

@st.cache_data
def load_data():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "galamsey_master.csv"),
        parse_dates=["date"]
    )
    rankings = pd.read_csv(
        os.path.join(OUT_DIR, "district_risk_rankings.csv")
    )
    return df, rankings

df, rankings = load_data()

st.title("🌍 Galamsey Atmospheric Pollution Monitoring System")
st.markdown(
    "**AI-Based Spatiotemporal Monitoring of Illegal Artisanal Mining "
    "and Its Atmospheric Pollution Impact in Ghana**  \n"
    "Western & Ashanti Regions | 2019–2024 | "
    "Real Sentinel-2 & Sentinel-5P Satellite Data"
)
st.divider()

col1, col2, col3, col4 = st.columns(4)
pre  = df[df["date"] < "2021-07-01"]["PRS"].mean()
post = df[df["date"] >= "2021-07-01"]["PRS"].mean()
with col1:
    st.metric("Districts Monitored", f"{df['district'].nunique()}", "52 total")
with col2:
    st.metric("Regional Mean PRS", f"{df['PRS'].mean():.3f}",
              f"{((post/pre)-1)*100:+.1f}% post-enforcement")
with col3:
    st.metric("Critical Risk Districts",
              str((rankings["risk_tier"] == "Critical").sum()))
with col4:
    st.metric("Study Period", "2019–2024", "72 monthly observations")

st.divider()

st.sidebar.header("🔍 Filters")
all_districts = sorted(df["district"].unique().tolist())
selected_districts = st.sidebar.multiselect(
    "Select Districts",
    options = all_districts,
    default = all_districts[:5]
)
year_range = st.sidebar.slider("Year Range", 2019, 2024, (2019, 2024))
metric = st.sidebar.selectbox(
    "Pollution Indicator",
    options = ["PRS", "aerosol_index", "no2_mean", "so2_mean"],
    format_func = lambda x: {
        "PRS":           "Pollution Risk Score",
        "aerosol_index": "Aerosol Index",
        "no2_mean":      "NO2 Column Density",
        "so2_mean":      "SO2 Column Density"
    }[x]
)

filtered = df[
    (df["district"].isin(selected_districts)) &
    (df["year"].between(year_range[0], year_range[1]))
]

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Pollution Trend: Selected Districts")
    if selected_districts:
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = plt.cm.tab10(np.linspace(0, 1, len(selected_districts)))
        for dist, color in zip(selected_districts, colors):
            subset = filtered[filtered["district"] == dist].set_index("date")
            ax.plot(subset.index, subset[metric],
                    label=dist, linewidth=1.8, color=color, alpha=0.85)
        ax.axvline(pd.Timestamp("2021-07-01"), color="black",
                   linestyle="--", linewidth=1.5, label="Enforcement (Jul 2021)")
        ax.set_ylabel(metric)
        ax.legend(fontsize=7, ncol=2)
        ax.set_title(f"{metric} over time", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        st.info("Select at least one district from the sidebar.")

with col_right:
    st.subheader("🏆 District Risk Rankings")
    tier_colors = {"Critical":"🔴","High":"🟠","Moderate":"🟡","Low":"🟢"}
    top20 = rankings.head(20)[["rank","district","mean_PRS","risk_tier"]].copy()
    top20["Risk"] = top20["risk_tier"].map(tier_colors)
    top20["PRS"]  = top20["mean_PRS"].round(3)
    st.dataframe(
        top20[["rank","district","PRS","Risk"]].rename(
            columns={"rank":"#","district":"District"}
        ),
        hide_index=True, height=350
    )

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📅 Seasonal Pattern")
    monthly = df.groupby("month")["PRS"].mean()
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(range(1, 13), monthly.values,
           color=["#C00000" if m in [1,2,3,11,12] else "#2E75B6"
                  for m in range(1, 13)],
           edgecolor="white")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_labels, fontsize=9)
    ax.set_ylabel("Mean PRS")
    ax.set_title("Mean PRS by Month (red = dry season)", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_b:
    st.subheader("📊 Annual Trend")
    annual = df.groupby("year")["PRS"].mean()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(annual.index, annual.values,
            color="#7030A0", linewidth=2.5, marker="o", markersize=8)
    ax.fill_between(annual.index, annual.values, alpha=0.15, color="#7030A0")
    ax.axvline(2021.5, color="black", linestyle="--",
               linewidth=1.5, label="Enforcement start")
    ax.set_xticks(annual.index)
    ax.set_ylabel("Mean PRS")
    ax.set_title("Annual Mean PRS 2019–2024", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

st.subheader("📋 Full District Summary Table")
display_cols = ["rank","district","region","mean_PRS",
                "mean_aerosol","mean_no2","risk_tier","prs_change"]
st.dataframe(
    rankings[display_cols].rename(columns={
        "rank":"Rank","district":"District","region":"Region",
        "mean_PRS":"Mean PRS","mean_aerosol":"Mean Aerosol",
        "mean_no2":"Mean NO2","risk_tier":"Risk Tier",
        "prs_change":"PRS Change 2019→2024"
    }).round(4),
    hide_index=True,
    use_container_width=True
)

st.divider()
st.caption(
    "Data: Sentinel-2 (COPERNICUS/S2_SR) and Sentinel-5P TROPOMI "
    "(COPERNICUS/S5P/OFFL) via Google Earth Engine. "
    "52 districts, Western & Ashanti Regions, Ghana. "
    "MSc Data Science Thesis — University of Ghana, 2026."
)