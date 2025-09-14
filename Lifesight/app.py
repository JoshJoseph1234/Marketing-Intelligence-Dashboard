import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Marketing Intelligence Dashboard", layout="wide")

# ---------- STEP 2: LOAD & CLEAN MARKETING DATA ----------

def load_marketing_csv(path, channel_name):
    df = pd.read_csv(path, parse_dates=['date'])
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df['channel'] = channel_name

    rename_map = {}
    if 'impression' in df.columns and 'impressions' not in df.columns:
        rename_map['impression'] = 'impressions'
    if 'attributed revenue' in df.columns and 'attributed_revenue' not in df.columns:
        rename_map['attributed revenue'] = 'attributed_revenue'
    if rename_map:
        df = df.rename(columns=rename_map)

    for col in ['impressions', 'clicks', 'spend', 'attributed_revenue']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

# ---------- STEP 3: CALCULATE METRICS ----------

def add_marketing_metrics(df):
    df = df.copy()
    df['ctr'] = np.where(df['impressions'] > 0, df['clicks'] / df['impressions'], 0)
    df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], np.nan)
    df['cpm'] = np.where(df['impressions'] > 0, df['spend'] / (df['impressions'] / 1000), np.nan)
    df['roas'] = np.where(df['spend'] > 0, df['attributed_revenue'] / df['spend'], np.nan)
    return df

# ---------- STEP 4: LOAD BUSINESS DATA & MERGE ----------

fb = load_marketing_csv("https://github.com/JoshJoseph1234/Marketing-Intelligence-Dashboard/blob/main/Lifesight/data/Facebook.csv", "Facebook")
gg = load_marketing_csv("https://github.com/JoshJoseph1234/Marketing-Intelligence-Dashboard/blob/main/Lifesight/data/Google.csv", "Google")
tt = load_marketing_csv("https://github.com/JoshJoseph1234/Marketing-Intelligence-Dashboard/blob/main/Lifesight/data/TikTok.csv", "TikTok")

marketing = pd.concat([fb, gg, tt], ignore_index=True)
marketing = add_marketing_metrics(marketing)

daily_marketing = marketing.groupby('date', as_index=False).agg({
    'impressions': 'sum',
    'clicks': 'sum',
    'spend': 'sum',
    'attributed_revenue': 'sum'
})
daily_marketing = add_marketing_metrics(daily_marketing)

business = pd.read_csv("https://github.com/JoshJoseph1234/Marketing-Intelligence-Dashboard/blob/main/Lifesight/data/business.csv", parse_dates=['date'])
business.columns = business.columns.str.strip().str.lower().str.replace(" ", "_")
for col in ['orders', 'new_orders', 'new_customers', 'total_revenue', 'gross_profit', 'cogs']:
    if col in business.columns:
        business[col] = pd.to_numeric(business[col], errors="coerce").fillna(0)

merged = pd.merge(business, daily_marketing, on="date", how="left", suffixes=("_bus", "_mkt"))
merged['attributed_rev_share_of_total'] = np.where(
    merged['total_revenue'] > 0,
    merged['attributed_revenue'] / merged['total_revenue'],
    0
)
merged['marketing_spend_share_of_gp'] = np.where(
    merged['gross_profit'] > 0,
    merged['spend'] / merged['gross_profit'],
    np.nan
)

# ---------- DASHBOARD ----------

st.title("📊 Marketing Intelligence Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
min_date = marketing['date'].min()
max_date = marketing['date'].max()
date_range = st.sidebar.date_input(
    "Select date range", [min_date, max_date], key="date_filter"
)

channels = st.sidebar.multiselect(
    "Select channels",
    options=marketing['channel'].unique().tolist(),
    default=marketing['channel'].unique().tolist()
)

mask = (
    (marketing['date'] >= pd.to_datetime(date_range[0])) &
    (marketing['date'] <= pd.to_datetime(date_range[1])) &
    (marketing['channel'].isin(channels))
)
filtered = marketing[mask]

merged_filtered = merged[
    (merged['date'] >= pd.to_datetime(date_range[0])) &
    (merged['date'] <= pd.to_datetime(date_range[1]))
]

# KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("💸 Total Spend", f"${filtered['spend'].sum():,.0f}")
col2.metric("💰 Attributed Revenue", f"${filtered['attributed_revenue'].sum():,.0f}")
col3.metric("📈 Avg ROAS", f"{filtered['roas'].mean():.2f}")
col4.metric("🧾 Attributed Rev Share", 
            f"{(merged_filtered['attributed_rev_share_of_total'].mean() * 100):.1f}%")

# ---------- BENCHMARKS ----------

BENCHMARKS = {"roas": 2.0, "ctr": 0.02, "cpc": 1.5, "spend_share_gp": 0.5}

avg_roas = filtered['roas'].mean()
avg_ctr = filtered['ctr'].mean()
avg_cpc = filtered['cpc'].mean()
spend_share_gp = (merged_filtered['spend'].sum() / merged_filtered['gross_profit'].sum()
                  if merged_filtered['gross_profit'].sum() > 0 else np.nan)

def status_icon(condition):
    return "🟢" if condition else "🔴"

st.subheader("🎯 Benchmarks vs Actuals")
cols = st.columns(4)
bench_metrics = [
    ("Avg ROAS", avg_roas, BENCHMARKS['roas'], lambda x, y: x >= y),
    ("Avg CTR", avg_ctr, BENCHMARKS['ctr'], lambda x, y: x >= y),
    ("Avg CPC", avg_cpc, BENCHMARKS['cpc'], lambda x, y: x <= y),
    ("Spend Share of GP", spend_share_gp, BENCHMARKS['spend_share_gp'], lambda x, y: x <= y)
]

for i, (label, actual, target, func) in enumerate(bench_metrics):
    icon = status_icon(func(actual, target))
    display_val = f"{actual:.2f}" if i != 1 and i != 3 else f"{actual:.1%}"
    display_target = f"{target:.2f}" if i != 1 and i != 3 else f"{target:.0%}"
    cols[i].metric(label, display_val, f"Target: {display_target} {icon}", delta_color="off")

# Time series chart
st.subheader("📆 Performance Over Time")
ts = merged_filtered[['date', 'spend', 'attributed_revenue', 'total_revenue']].fillna(0)
fig = px.line(ts, x='date', y=['spend', 'attributed_revenue', 'total_revenue'],
              title="Daily Spend vs Attributed Revenue vs Total Revenue",
              labels={'value': 'Amount', 'variable': 'Metric'})
st.plotly_chart(fig, use_container_width=True)

# Channel performance table with inline benchmark icons
st.subheader("📌 Channel Performance (with Benchmarks)")

channel_perf = filtered.groupby('channel', as_index=False).agg({
    'spend': 'sum',
    'attributed_revenue': 'sum',
    'impressions': 'sum',
    'clicks': 'sum'
})

# Compute metrics
channel_perf['ctr'] = np.where(channel_perf['impressions'] > 0,
                               channel_perf['clicks'] / channel_perf['impressions'], 0)
channel_perf['cpc'] = np.where(channel_perf['clicks'] > 0,
                               channel_perf['spend'] / channel_perf['clicks'], np.nan)
channel_perf['roas'] = np.where(channel_perf['spend'] > 0,
                                channel_perf['attributed_revenue'] / channel_perf['spend'], np.nan)

# Function to append emoji based on benchmark
def append_icon(value, benchmark, higher_is_better=True, fmt="{:.2f}"):
    if pd.isna(value):
        return "N/A"
    icon = "🟢" if (value >= benchmark if higher_is_better else value <= benchmark) else "🔴"
    return f"{fmt.format(value)} {icon}"

channel_perf['CTR'] = channel_perf['ctr'].apply(lambda x: append_icon(x, BENCHMARKS['ctr'], True, "{:.1%}"))
channel_perf['CPC'] = channel_perf['cpc'].apply(lambda x: append_icon(x, BENCHMARKS['cpc'], False, "${:.2f}"))
channel_perf['ROAS'] = channel_perf['roas'].apply(lambda x: append_icon(x, BENCHMARKS['roas'], True, "{:.1f}"))

# Select and reorder columns for display
display_cols = ['channel', 'spend', 'attributed_revenue', 'CTR', 'CPC', 'ROAS']
st.dataframe(channel_perf[display_cols].rename(columns={
    'channel': 'Channel',
    'spend': 'Spend',
    'attributed_revenue': 'Attributed Rev'
}), use_container_width=True)


# Top campaigns
st.subheader("🏆 Top Campaigns")
top_campaigns = filtered.groupby(['channel', 'campaign'], as_index=False).agg({
    'impressions': 'sum', 'clicks': 'sum', 'spend': 'sum', 'attributed_revenue': 'sum'
})
top_campaigns['roas'] = np.where(top_campaigns['spend'] > 0,
                                 top_campaigns['attributed_revenue'] / top_campaigns['spend'], np.nan)
st.dataframe(top_campaigns.sort_values("roas", ascending=False).head(20))

# Scatter chart
st.subheader("📊 Campaign Efficiency")
fig2 = px.scatter(top_campaigns, x='spend', y='attributed_revenue',
                  color='channel', size='impressions',
                  hover_data=['campaign'],
                  title="Spend vs Attributed Revenue by Campaign")
st.plotly_chart(fig2, use_container_width=True)

# Drill-down
st.subheader("🔎 Drill-down: Campaign Performance")
selected_campaign = st.selectbox("Choose a campaign", top_campaigns['campaign'].unique(), key="campaign_select")
if selected_campaign:
    camp_df = filtered[filtered['campaign'] == selected_campaign].sort_values('date')
    fig3 = px.line(camp_df, x='date', y=['spend', 'attributed_revenue'],
                   title=f"{selected_campaign} - Daily Spend vs Attributed Revenue")
    st.plotly_chart(fig3, use_container_width=True)

# Export button
st.subheader("⬇️ Export Filtered Data")
st.download_button("Download as CSV",
                   filtered.to_csv(index=False).encode('utf-8'),
                   "filtered_marketing.csv",
                   "text/csv")
