import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import IndigoDataLoader
from src.stat_analysis import StatisticalAnalyzer
from src.nlp_analytics import NLPTextAnalytics

# Set Page Config
st.set_page_config(
    page_title="IndiGo Executive Data Analytics Portal",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Power BI & IndiGo Visual Style
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stAppHeader { background-color: #003366; }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #003366;
        text-align: center;
    }
    .kpi-title { font-size: 14px; font-weight: 600; color: #555555; text-transform: uppercase; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #003366; margin-top: 5px; }
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #003366;
        padding-bottom: 10px;
        border-bottom: 2px solid #003366;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_dict_replace=True)

@st.cache_data
def load_data():
    loader = IndigoDataLoader()
    return loader.load_from_db()

df_raw = load_data()

# Sidebar Controls
st.sidebar.image("https://mf-careers-prod.goindigo.in/job-details/ae2fc09205d857003149.svg", width=180)
st.sidebar.title("Executive Dashboard Filters")

routes = ['All'] + list(df_raw['route'].unique())
selected_route = st.sidebar.selectbox("Filter Route", routes)

fleets = ['All'] + list(df_raw['fleet_type'].unique())
selected_fleet = st.sidebar.selectbox("Filter Fleet Type", fleets)

cabin_types = ['All'] + list(df_raw['cabin_class'].unique())
selected_cabin = st.sidebar.selectbox("Filter Cabin Class", cabin_types)

# Filter Data
df = df_raw.copy()
if selected_route != 'All':
    df = df[df['route'] == selected_route]
if selected_fleet != 'All':
    df = df[df['fleet_type'] == selected_fleet]
if selected_cabin != 'All':
    df = df[df['cabin_class'] == selected_cabin]

# App Title & Header Banner
st.title("✈️ IndiGo Executive - Data Analytics Portal")
st.markdown("**Role Scope**: Operations KPI Monitoring, Statistical Modeling (SPSS), NPS Audit, and Predictive Analytics")

# KPI Summary Section
col1, col2, col3, col4 = st.columns(4)

total_pax = len(df)
total_rev = df['total_revenue_inr'].sum()
otp_pct = (df['arrival_delay_min'] <= 15).mean() * 100
promoters = (df['nps_category'] == 'Promoter').sum()
detractors = (df['nps_category'] == 'Detractor').sum()
nps_score = ((promoters - detractors) / total_pax) * 100 if total_pax > 0 else 0

with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Passengers</div><div class="kpi-value">{total_pax:,}</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Revenue (INR)</div><div class="kpi-value">₹{total_rev:,.2f}</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">On-Time Performance (OTP)</div><div class="kpi-value">{otp_pct:.1f}%</div></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Promoter Score (NPS)</div><div class="kpi-value">{nps_score:+.1f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Flight & Financial Analytics",
    "🔬 Statistical & SPSS Modeling",
    "💬 NLP Customer Feedback",
    "📋 Data Explorer & Export"
])

with tab1:
    st.markdown('<div class="section-header">Flight Operations & Financial Performance</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Revenue by Booking Channel")
        rev_by_channel = df.groupby('booking_channel')['total_revenue_inr'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(data=rev_by_channel, x='total_revenue_inr', y='booking_channel', palette='Blues_r', ax=ax)
        ax.set_xlabel("Total Revenue (INR)")
        ax.set_ylabel("")
        st.pyplot(fig)

    with c2:
        st.subheader("Arrival Delay Reasons Distribution")
        delay_counts = df[df['is_delayed'] == 1]['delay_reason'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.pie(delay_counts, labels=delay_counts.index, autopct='%1.1f%%', colors=sns.color_palette("Set2"))
        st.pyplot(fig)

with tab2:
    st.markdown('<div class="section-header">Statistical Analysis & Predictive Modeling (SPSS Engine)</div>', unsafe_allow_html=True)
    analyzer = StatisticalAnalyzer(df)
    
    st.subheader("1. Univariate Summary Statistics")
    st.dataframe(analyzer.univariate_analysis(), use_container_width=True)
    
    st.subheader("2. Bivariate Hypothesis Testing (T-Test, ANOVA, Chi-Square)")
    st.dataframe(analyzer.bivariate_analysis(), use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("3. OLS Linear Regression (Arrival Delay Drivers)")
        lin_res = analyzer.linear_regression_model()
        st.metric("R-Squared", f"{lin_res['r_squared']:.4f}")
        st.dataframe(lin_res['summary_table'])
        
    with c2:
        st.subheader("4. Logistic Regression (Detractor Probability)")
        log_res = analyzer.logistic_regression_model()
        st.metric("AUC-ROC Score", f"{log_res['auc_roc']:.4f}")
        st.dataframe(log_res['odds_ratios'])

with tab3:
    st.markdown('<div class="section-header">NLP Customer Feedback & Sentiment Analysis</div>', unsafe_allow_html=True)
    nlp = NLPTextAnalytics(df.head(5000))  # Sample for fast interactive execution
    summary = nlp.generate_nlp_summary()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sentiment Category Distribution")
        sent_df = pd.DataFrame(list(summary['sentiment_distribution_pct'].items()), columns=['Sentiment', 'Percentage'])
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=sent_df, x='Sentiment', y='Percentage', palette=['#2ecc71', '#e74c3c', '#95a5a6'], ax=ax)
        st.pyplot(fig)
        
    with c2:
        st.subheader("Top Complaint Drivers (TF-IDF Keyword Mining)")
        st.dataframe(pd.DataFrame(summary['top_detractor_drivers']), use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">Raw Flight & Survey Dataset Explorer</div>', unsafe_allow_html=True)
    st.dataframe(df.head(500), use_container_width=True)
    
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_bytes,
        file_name="indigo_filtered_data.csv",
        mime="text/csv"
    )
