import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="NBA Evolution Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('all_seasons.csv')
    # Ensure numeric columns are correct
    df['player_height'] = pd.to_numeric(df['player_height'])
    df['player_weight'] = pd.to_numeric(df['player_weight'])
    df['age'] = pd.to_numeric(df['age'])
    
    # Create a simple "Draft Status" column
    df['draft_status'] = df['draft_year'].apply(lambda x: 'Undrafted' if x == 'Undrafted' else 'Drafted')
    return df

df = load_data()

# Identify Baseline and Modern Seasons
seasons = sorted(df['season'].unique())
baseline_season = seasons[0]  # 1996-97
modern_season = seasons[-1]   # 2022-23

# --- MAIN HEADER ---
st.title("NBA Evolution Analysis")
st.markdown(f"### Is there a correlation of the age/weight/height from the {baseline_season} season changed from modern day NBA ({modern_season})?")
st.write("Comparing the physical profiles of players across nearly 30 years of basketball history.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Data")

# Filter 1: Country
all_countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect("Select Countries", options=all_countries, default=all_countries)

# Filter 2: Draft Status
draft_options = df['draft_status'].unique()
selected_draft_status = st.sidebar.multiselect("Select Draft Status", options=draft_options, default=list(draft_options))

# Apply Filters
filtered_df = df[
    (df['country'].isin(selected_countries)) & 
    (df['draft_status'].isin(selected_draft_status))
]

# Split into Baseline and Modern for comparison
df_baseline = filtered_df[filtered_df['season'] == baseline_season]
df_modern = filtered_df[filtered_df['season'] == modern_season]

# --- KPI CALCULATION ---
def calculate_delta(col_name):
    base_avg = df_baseline[col_name].mean()
    mod_avg = df_modern[col_name].mean()
    if base_avg == 0 or pd.isna(base_avg) or pd.isna(mod_avg):
        return 0, 0
    delta_pct = ((mod_avg - base_avg) / base_avg) * 100
    return mod_avg, delta_pct

avg_age, age_delta = calculate_delta('age')
avg_height, height_delta = calculate_delta('player_height')
avg_weight, weight_delta = calculate_delta('player_weight')

# --- DISPLAY KPIs ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Modern Avg Age", value=f"{avg_age:.1f} yrs", delta=f"{age_delta:.1f}% vs {baseline_season}")

with col2:
    # Height in cm to feet/inches conversion if desired, but sticking to dataset metric for accuracy
    st.metric(label="Modern Avg Height", value=f"{avg_height:.1f} cm", delta=f"{height_delta:.1f}% vs {baseline_season}")

with col3:
    st.metric(label="Modern Avg Weight", value=f"{avg_weight:.1f} kg", delta=f"{weight_delta:.1f}% vs {baseline_season}")

st.divider()

# --- CORRELATION VISUALIZATIONS ---
st.subheader("Physical Correlations: Height vs. Weight")
st.info("Check how the relationship between height and weight has shifted. Are players leaner today?")

plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    st.markdown(f"#### {baseline_season} (Historical)")
    if not df_baseline.empty:
        fig_base = px.scatter(
            df_baseline, x="player_height", y="player_weight", 
            trendline="ols", hover_name="player_name",
            color_discrete_sequence=['#636EFA']
        )
        st.plotly_chart(fig_base, use_container_width=True)
    else:
        st.warning("No data found for the baseline season with current filters.")

with plot_col2:
    st.markdown(f"#### {modern_season} (Modern)")
    if not df_modern.empty:
        fig_mod = px.scatter(
            df_modern, x="player_height", y="player_weight", 
            trendline="ols", hover_name="player_name",
            color_discrete_sequence=['#EF553B']
        )
        st.plotly_chart(fig_mod, use_container_width=True)
    else:
        st.warning("No data found for the modern season with current filters.")

# --- INSIGHTS TABLE ---
with st.expander("View Statistical Correlation Coefficients"):
    # Calculate R values
    if not df_baseline.empty and not df_modern.empty:
        corr_base = df_baseline[['player_height', 'player_weight']].corr().iloc[0,1]
        corr_mod = df_modern[['player_height', 'player_weight']].corr().iloc[0,1]
        
        st.write(f"**{baseline_season} Correlation (H vs W):** {corr_base:.3f}")
        st.write(f"**{modern_season} Correlation (H vs W):** {corr_mod:.3f}")
    else:
        st.write("Insufficient data for correlation calculation.")