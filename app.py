"""
TRON Merchant Analytics Dashboard - Final Version
Tracking real-world USDT merchant adoption on TRON blockchain
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="TRON Merchant Analytics | Global Heatmap",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean dark theme with IBM Plex Sans font
st.markdown("""
<style>
    /* Import IBM Plex Sans */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    /* Dark theme base */
    .stApp {
        background: #0a0a0a;
        color: #e0e0e0;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 700;
    }
    
    /* Main title styling */
    .main-title {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #00ff88 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    /* Author credit */
    .author-credit {
        position: absolute;
        top: 40px;
        right: 20px;
        font-size: 0.9rem;
        color: #999;
        z-index: 9999 !important;
    }
    
    .author-credit a {
        color: #00ff88;
        text-decoration: none;
        margin-left: 1rem;
        transition: opacity 0.3s ease;
    }
    
    .author-credit a:hover {
        opacity: 0.8;
    }
    
    /* Methodology box with animated line */
    .methodology-box {
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 2rem auto;
        max-width: 900px;
        position: relative;
        overflow: hidden;
    }
    
    .methodology-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff88, transparent);
        animation: slide 3s infinite;
    }
    
    @keyframes slide {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Metric cards */
    .metric-card {
        background: #111111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        border-color: #00ff88;
        transform: translateY(-2px);
    }
    
    .metric-number {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.5rem;
        font-weight: 500;
        color: #00ff88;
        line-height: 1;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
        border-bottom: 1px solid #222;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #666;
        border: none;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 1rem 0;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #00ff88;
        border-bottom: 2px solid #00ff88;
    }
    
    /* All text elements */
    p, span, div, label {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    /* Chart description */
    .chart-description {
        color: #999;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        text-align: left;
    }
</style>

<div class="author-credit">
    Analysis by Connor DeFrain
    <a href="https://x.com/connordefrain_" target="_blank">Twitter</a>
    <a href="http://www.linkedin.com/in/connor-defrain-5a1404297" target="_blank">LinkedIn</a>
</div>
<div style="height: 100px;"></div>
""", unsafe_allow_html=True)

# Load merchant data
@st.cache_data
def load_merchant_data():
    """Load merchant data"""
    csv_path = 'output/identified_merchants.csv'
    
    if not os.path.exists(csv_path):
        st.error(f"ERROR: Could not find {csv_path}")
        st.error("Please ensure your identified_merchants.csv file is in the output folder.")
        st.stop()
    
    try:
        merchants = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"ERROR: Could not read CSV file: {str(e)}")
        st.stop()
    
    # Verify required columns
    required_columns = ['address', 'transaction_count', 'unique_customers', 
                       'total_received_usdt', 'avg_payment_size', 
                       'estimated_region', 'peak_hour_utc', 'days_active']
    
    missing_columns = [col for col in required_columns if col not in merchants.columns]
    if missing_columns:
        st.error(f"ERROR: Missing required columns: {missing_columns}")
        st.stop()
    
    # Add calculated fields
    merchants['activity_percentile'] = merchants['transaction_count'].rank(pct=True) * 100
    merchants['volume_percentile'] = merchants['total_received_usdt'].rank(pct=True) * 100
    
    return merchants

# Global crypto adoption data
GLOBAL_CRYPTO_ADOPTION = {
    'India': {'rank': 1, 'adoption_rate': 11.0},
    'Nigeria': {'rank': 2, 'adoption_rate': 22.0},
    'Indonesia': {'rank': 3, 'adoption_rate': 9.0},
    'United States': {'rank': 4, 'adoption_rate': 13.0},
    'Vietnam': {'rank': 5, 'adoption_rate': 21.0},
    'Ukraine': {'rank': 6, 'adoption_rate': 12.8},
    'Philippines': {'rank': 7, 'adoption_rate': 13.4},
    'Brazil': {'rank': 8, 'adoption_rate': 12.0},
    'Thailand': {'rank': 9, 'adoption_rate': 9.6},
    'Turkey': {'rank': 10, 'adoption_rate': 25.0},
    'Argentina': {'rank': 11, 'adoption_rate': 15.8},
    'Mexico': {'rank': 12, 'adoption_rate': 8.7},
    'Bangladesh': {'rank': 13, 'adoption_rate': 7.3},
    'Morocco': {'rank': 14, 'adoption_rate': 6.2},
    'Egypt': {'rank': 15, 'adoption_rate': 7.8},
    'Kenya': {'rank': 16, 'adoption_rate': 14.5},
    'South Africa': {'rank': 17, 'adoption_rate': 11.0},
    'Pakistan': {'rank': 18, 'adoption_rate': 6.6},
    'Venezuela': {'rank': 19, 'adoption_rate': 10.3},
    'Colombia': {'rank': 20, 'adoption_rate': 9.1},
    'Peru': {'rank': 21, 'adoption_rate': 8.5},
    'Chile': {'rank': 22, 'adoption_rate': 7.2},
    'Poland': {'rank': 23, 'adoption_rate': 5.8},
    'Malaysia': {'rank': 24, 'adoption_rate': 8.0},
    'Canada': {'rank': 25, 'adoption_rate': 7.0},
    'Singapore': {'rank': 26, 'adoption_rate': 9.5},
    'Australia': {'rank': 27, 'adoption_rate': 9.0},
    'United Kingdom': {'rank': 28, 'adoption_rate': 6.0},
    'Japan': {'rank': 29, 'adoption_rate': 4.0},
    'South Korea': {'rank': 30, 'adoption_rate': 8.0},
    'UAE': {'rank': 31, 'adoption_rate': 11.5},
    'Saudi Arabia': {'rank': 32, 'adoption_rate': 7.6},
    'Russia': {'rank': 33, 'adoption_rate': 11.4},
    'Spain': {'rank': 34, 'adoption_rate': 5.0},
    'Germany': {'rank': 35, 'adoption_rate': 4.2},
    'France': {'rank': 36, 'adoption_rate': 3.3},
    'Italy': {'rank': 37, 'adoption_rate': 3.4},
    'Netherlands': {'rank': 38, 'adoption_rate': 5.2},
    'Portugal': {'rank': 39, 'adoption_rate': 6.1},
    'Greece': {'rank': 40, 'adoption_rate': 4.5},
}

# Load data
merchants_df = load_merchant_data()

# Constants with 2.5x multiplier
MULTIPLIER = 2.5
merchant_count = int(len(merchants_df) * MULTIPLIER)
total_volume = merchants_df['total_received_usdt'].sum() * MULTIPLIER

# Header
st.markdown('<h1 class="main-title">Global Crypto Merchant Heatmap</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Tracking real-world USDT merchant adoption on TRON blockchain</p>', unsafe_allow_html=True)

# Methodology box
st.markdown("""
<div class="methodology-box">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <div style="width: 12px; height: 12px; background: #00ff88; border-radius: 50%; 
                    animation: pulse 2s infinite;"></div>
        <strong style="color: #00ff88; font-size: 1.1rem;">Geographic Estimation Methodology</strong>
    </div>
    <p style="margin: 0; color: #999; line-height: 1.6;">
        Tracking where crypto merchants actually operate show us which markets are adopting USDT for real commerce. I 
        analyzed specific wallet behavior criteria that indicate real world commerce activity as well as the peak hours for likely 
        business hours (9AM to 5PM local time) to estimate merchant like patterns. This is an educated approximation based on 
        behavioral analysis. Country distribution within regions is weighted by known crypto adoption rates from industry 
        reports.
    </p>
</div>

<style>
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.2); }
}
</style>
""", unsafe_allow_html=True)

# Key metrics - only 2
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{merchant_count:,}</div>
        <div class="metric-label">Merchants Identified</div>
        <div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">
            Approximately across all regions
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Emerging markets percentage
    emerging_regions = ['Asia-Pacific', 'Europe-Africa']
    emerging_count = merchants_df[merchants_df['estimated_region'].isin(emerging_regions)].shape[0]
    emerging_pct = (emerging_count / len(merchants_df) * 100) if len(merchants_df) > 0 else 0
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{emerging_pct:.0f}%</div>
        <div class="metric-label">Emerging Markets</div>
        <div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">
            Operating in developing economies
        </div>
    </div>
    """, unsafe_allow_html=True)

# Regional distribution section
st.markdown("### Regional Distribution")

# Get actual regional distribution
region_dist = merchants_df['estimated_region'].value_counts()
total_merchants = len(merchants_df)

cols = st.columns(3)
for i, (region, count) in enumerate(region_dist.items()):
    with cols[i % 3]:
        percentage = count / total_merchants * 100 if total_merchants > 0 else 0
        scaled_count = int(count * MULTIPLIER)
        
        # Region colors
        colors = {
            'Asia-Pacific': '#00ff88',
            'Europe-Africa': '#0099ff',
            'Americas': '#ff6b6b'
        }
        
        st.markdown(f"""
        <div style="background: #111; border: 1px solid #222; border-radius: 12px; 
                    padding: 1.5rem; text-align: center; margin-bottom: 1rem;">
            <h3 style="color: {colors.get(region, '#00ff88')}; margin: 0; font-size: 1.3rem;">
                {region}
            </h3>
            <div style="font-size: 2.5rem; font-weight: 800; color: {colors.get(region, '#00ff88')}; 
                        margin: 0.5rem 0;">
                {percentage:.1f}%
            </div>
            <div style="color: #666; font-size: 0.9rem;">
                {scaled_count:,} merchants
            </div>
        </div>
        """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Global Heatmap", "Regional Analysis", "Merchant Insights", "How I Collected This Data"])

with tab1:
    # Create country data
    country_data = []
    
    # Add all countries with adoption data
    for country, stats in GLOBAL_CRYPTO_ADOPTION.items():
        country_data.append({
            'country': country,
            'adoption_rate': stats['adoption_rate'],
            'global_rank': stats['rank'],
            'has_merchants': False,
            'merchant_count': 0,
            'estimated_merchants': 0
        })
    
    # Regional country mapping
    region_countries = {
        'Asia-Pacific': ['India', 'Indonesia', 'Vietnam', 'Philippines', 'Thailand', 
                        'Bangladesh', 'Pakistan', 'Malaysia', 'Singapore', 'Japan', 
                        'South Korea', 'Australia'],
        'Europe-Africa': ['Nigeria', 'Ukraine', 'Turkey', 'Morocco', 'Egypt', 'Kenya', 
                         'South Africa', 'Russia', 'Poland', 'Spain', 'Germany', 
                         'France', 'Italy', 'UAE', 'Saudi Arabia'],
        'Americas': ['United States', 'Brazil', 'Argentina', 'Mexico', 'Venezuela', 
                    'Colombia', 'Peru', 'Chile', 'Canada']
    }
    
    # Distribute merchants
    for region, countries in region_countries.items():
        if region in region_dist.index:
            region_merchants = region_dist[region]
            
            # Calculate weighted distribution
            region_adoption_rates = {c: GLOBAL_CRYPTO_ADOPTION.get(c, {'adoption_rate': 1.0})['adoption_rate'] 
                                   for c in countries if c in GLOBAL_CRYPTO_ADOPTION}
            total_rate = sum(region_adoption_rates.values())
            
            for country, rate in region_adoption_rates.items():
                weight = rate / total_rate if total_rate > 0 else 0
                merchant_count = int(region_merchants * weight)
                
                for i, cd in enumerate(country_data):
                    if cd['country'] == country:
                        country_data[i]['has_merchants'] = True
                        country_data[i]['merchant_count'] = merchant_count
                        country_data[i]['estimated_merchants'] = int(merchant_count * MULTIPLIER)
                        break
    
    country_df = pd.DataFrame(country_data)
    
    # Create choropleth with better hover
    fig = go.Figure()
    
    fig.add_trace(go.Choropleth(
        locations=country_df['country'],
        locationmode='country names',
        z=country_df['adoption_rate'],
        text=country_df['country'],
        customdata=country_df[['global_rank', 'adoption_rate', 'merchant_count', 'estimated_merchants']],
        colorscale=[
            [0, '#1a1a1a'],
            [0.2, '#2a3a2a'],
            [0.4, '#3a5a3a'],
            [0.6, '#4a7a4a'],
            [0.8, '#5a9a5a'],
            [1.0, '#00ff88']
        ],
        hovertemplate='<b style="font-size: 16px; font-family: IBM Plex Sans">%{text}</b><br><br>' +
                      '<span style="font-family: IBM Plex Sans">Global Crypto Rank: <b>#%{customdata[0]}</b></span><br>' +
                      '<span style="font-family: IBM Plex Sans">Adoption Rate: <b>%{customdata[1]:.1f}%</b></span><br>' +
                      '<span style="font-family: IBM Plex Sans">TRON Merchants: <b>%{customdata[3]:,}</b></span>' +
                      '<extra></extra>',
        marker=dict(
            line=dict(color='#333', width=0.5)
        ),
        colorbar=dict(
            title="Crypto<br>Adoption %",
            tickformat='.0f',
            bgcolor='#111',
            bordercolor='#333',
            borderwidth=1,
            tickfont=dict(color='#999'),
            x=1.1
        )
    ))
    
    # Update layout
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='#444',
            projection_type='natural earth',
            bgcolor='#0a0a0a',
            showcountries=True,
            countrycolor='#222',
            showocean=True,
            oceancolor='#0a0a0a',
            showlakes=False,
        ),
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#0a0a0a',
        height=700,
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(family='IBM Plex Sans', color='#999'),
        hoverlabel=dict(
            bgcolor='#111',
            bordercolor='#333',
            font=dict(family='IBM Plex Sans', size=14)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Country rankings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top Crypto Adoption Countries")
        top_countries = country_df.nlargest(10, 'adoption_rate')[['country', 'adoption_rate', 'global_rank']]
        
        for _, row in top_countries.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; 
                        border-bottom: 1px solid #222; align-items: center;">
                <span style="color: #00ff88;">#{row['global_rank']}</span>
                <span style="flex: 1; margin-left: 1rem;">{row['country']}</span>
                <span style="color: #0099ff;">{row['adoption_rate']:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### TRON Merchant Leaders")
        merchant_leaders = country_df[country_df['has_merchants']].nlargest(10, 'estimated_merchants')[
            ['country', 'estimated_merchants']
        ]
        
        for _, row in merchant_leaders.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; 
                        border-bottom: 1px solid #222; align-items: center;">
                <span style="flex: 1;">{row['country']}</span>
                <span style="color: #00ff88; font-family: 'IBM Plex Mono', monospace;">
                    {row['estimated_merchants']:,} merchants
                </span>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("### Peak Activity Hours by Region")
    st.markdown('<p class="chart-description">Merchant transaction patterns reveal business hours across time zones, confirming geographic estimates.</p>', unsafe_allow_html=True)
    
    # Create hourly distribution
    hourly_data = []
    
    for region in merchants_df['estimated_region'].unique():
        region_merchants = merchants_df[merchants_df['estimated_region'] == region]
        
        for hour in range(24):
            count = len(region_merchants[region_merchants['peak_hour_utc'] == hour])
            percentage = count / len(region_merchants) * 100 if len(region_merchants) > 0 else 0
            
            hourly_data.append({
                'Hour (UTC)': hour,
                'Region': region,
                'Percentage of Merchants': percentage,
                'Merchant Count': count
            })
    
    hourly_df = pd.DataFrame(hourly_data)
    
    # Create grouped bar chart with better formatting and thinner bars
    fig = px.bar(
        hourly_df,
        x='Hour (UTC)',
        y='Percentage of Merchants',
        color='Region',
        title='',
        color_discrete_map={
            'Asia-Pacific': '#00ff88',
            'Europe-Africa': '#0099ff',
            'Americas': '#ff6b6b'
        }
    )
    
    # Update traces for thinner bars
    fig.update_traces(
        width=0.6,  # Make bars thinner
        hovertemplate='<b style="font-family: IBM Plex Sans">Hour %{x}:00 UTC</b><br>' +
                      '<span style="font-family: IBM Plex Sans">Percentage: <b>%{y:.1f}%</b></span><br>' +
                      '<extra></extra>'
    )
    
    fig.update_layout(
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#111',
        font=dict(color='#999', family='IBM Plex Sans'),
        xaxis=dict(
            gridcolor='#222',
            tickmode='linear',
            tick0=0,
            dtick=2
        ),
        yaxis=dict(gridcolor='#222'),
        legend=dict(
            bgcolor='#111',
            bordercolor='#333',
            borderwidth=1
        ),
        height=500,
        hoverlabel=dict(
            bgcolor='#111',
            bordercolor='#333',
            font=dict(family='IBM Plex Sans', size=14)
        ),
        bargap=0.2  # Add gap between groups
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Payment size distribution
    st.markdown("### Payment Size Distribution")
    st.markdown('<p class="chart-description">Most transactions fall within retail ranges ($20-80), validating the merchant classification methodology.</p>', unsafe_allow_html=True)
    
    # Create bins for payment sizes
    bins = list(range(0, 105, 5))  # 0-5, 5-10, 10-15, ..., 95-100
    bin_labels = [f'${i}-${i+5}' for i in range(0, 100, 5)]
    
    merchants_df['payment_bin'] = pd.cut(merchants_df['avg_payment_size'], bins=bins, labels=bin_labels, include_lowest=True)
    payment_dist = merchants_df['payment_bin'].value_counts().sort_index()
    
    fig = go.Figure(data=[go.Bar(
        x=payment_dist.index,
        y=payment_dist.values,
        marker=dict(
            color='#00ff88',
            line=dict(width=0)  # Remove outline
        ),
        hovertemplate='<b style="font-family: IBM Plex Sans">%{x}</b><br>' +
                      '<span style="font-family: IBM Plex Sans">Merchants: <b>%{y}</b></span>' +
                      '<extra></extra>',
        width=0.8  # Make bars thinner
    )])
    
    fig.update_layout(
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#111',
        font=dict(color='#999', family='IBM Plex Sans'),
        xaxis=dict(
            gridcolor='#222',
            title='Average Payment Size (USDT)',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='#222',
            title='Number of Merchants'
        ),
        height=400,
        hoverlabel=dict(
            bgcolor='#111',
            bordercolor='#333',
            font=dict(family='IBM Plex Sans', size=14)
        ),
        bargap=0.1  # Thinner bars
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Customer Base vs Transaction Activity")
    st.markdown('<p class="chart-description">The logarithmic relationship between customers and transactions demonstrates consistent merchant behavior across all regions.</p>', unsafe_allow_html=True)
    
    sample_size = min(1000, len(merchants_df))
    scatter_sample = merchants_df.sample(sample_size)
    
    fig = px.scatter(
        scatter_sample,
        x='unique_customers',
        y='transaction_count',
        size='total_received_usdt',
        color='estimated_region',
        labels={
            'unique_customers': 'Unique Customers',
            'transaction_count': 'Total Transactions'
        },
        color_discrete_map={
            'Asia-Pacific': '#00ff88',
            'Europe-Africa': '#0099ff',
            'Americas': '#ff6b6b'
        },
        size_max=30,
        opacity=0.7
    )
    
    # Update hover template to include region
    fig.update_traces(
        hovertemplate='<b style="font-family: IBM Plex Sans">%{fullData.name}</b><br><br>' +
                      '<span style="font-family: IBM Plex Sans">Customers: <b>%{x:,}</b></span><br>' +
                      '<span style="font-family: IBM Plex Sans">Transactions: <b>%{y:,}</b></span><br>' +
                      '<span style="font-family: IBM Plex Sans">Volume: <b>$%{marker.size:,.0f}</b></span>' +
                      '<extra></extra>'
    )
    
    fig.update_layout(
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#111',
        font=dict(color='#999', family='IBM Plex Sans'),
        xaxis=dict(gridcolor='#222', type='log', title='Unique Customers (log scale)'),
        yaxis=dict(gridcolor='#222', type='log', title='Total Transactions (log scale)'),
        legend=dict(
            bgcolor='#111',
            bordercolor='#333',
            borderwidth=1,
            title='Region'
        ),
        height=600,
        hoverlabel=dict(
            bgcolor='#111',
            bordercolor='#333',
            font=dict(family='IBM Plex Sans', size=14)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Activity level distribution - BIGGER
    st.markdown("### Merchant Activity Distribution")
    st.markdown('<p class="chart-description">Activity levels show a healthy distribution with most merchants maintaining regular operations.</p>', unsafe_allow_html=True)
    
    activity_bins = pd.cut(
        merchants_df['activity_percentile'],
        bins=[0, 25, 50, 75, 100],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    
    activity_dist = activity_bins.value_counts().reset_index()
    activity_dist.columns = ['Activity Level', 'Count']
    activity_dist['Percentage'] = (activity_dist['Count'] / activity_dist['Count'].sum() * 100).round(1)
    
    fig = px.pie(
        activity_dist,
        values='Count',
        names='Activity Level',
        title='',
        color_discrete_sequence=['#333', '#666', '#00cc66', '#00ff88']
    )
    
    fig.update_traces(
        hovertemplate='<b style="font-family: IBM Plex Sans">%{label}</b><br>' +
                      '<span style="font-family: IBM Plex Sans">Merchants: <b>%{value:,}</b></span><br>' +
                      '<span style="font-family: IBM Plex Sans">Percentage: <b>%{percent}</b></span>' +
                      '<extra></extra>',
        textinfo='label+percent',
        textfont=dict(family='IBM Plex Sans', size=14)
    )
    
    fig.update_layout(
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#0a0a0a',
        font=dict(color='#999', family='IBM Plex Sans'),
        showlegend=True,
        legend=dict(
            bgcolor='#111',
            bordercolor='#333',
            borderwidth=1
        ),
        height=500,
        margin=dict(t=50, b=50),
        hoverlabel=dict(
            bgcolor='#111',
            bordercolor='#333',
            font=dict(family='IBM Plex Sans', size=14)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Download section
    st.markdown("---")
    st.markdown("### Export Data")
    
    # Create CSV download
    @st.cache_data
    def convert_df_to_csv(df):
        """Convert dataframe to CSV for download"""
        export_df = df[['address', 'estimated_region']].copy()
        return export_df.to_csv(index=False).encode('utf-8')
    
    csv_data = convert_df_to_csv(merchants_df)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="Download Merchant Addresses (CSV)",
            data=csv_data,
            file_name=f"tron_merchant_addresses_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            help="Download all merchant wallet addresses with their regions"
        )

with tab4:
    st.markdown("### Data Collection")
    
    st.markdown("""
    #### Overview
    Real merchants were identified by analyzing 1.1 million active receiving addresses from June 3-10, 2025. I applied behavioral filters based on patterns typical of actual businesses.
    
    #### Merchant Identification Criteria
    To qualify as a merchant, an address needed to meet ALL of the following criteria:
    - Minimum 5 transactions - Excludes one-time or rarely used wallets
    - Minimum 5 unique customers - Ensures actual business activity vs personal transfers
    - $75+ in total volume - Filters out test transactions and micro-payments
    - Average payment size between $1-100 - Typical retail transaction range
    - Maximum 80% customer concentration - Excludes personal wallets receiving from single sources
    
    #### Geographic Estimation
    I analyzed peak transaction hours for each wallet to estimate time zones:
    1. Calculated hourly transaction distribution for each merchant
    2. Identified peak activity hours (when most transactions occurred)
    3. Assumed merchants operate during typical business hours (9 AM - 5 PM local time)
    4. Mapped peak UTC hours to likely time zones and regions
    5. Distributed merchants within regions based on crypto adoption rates from industry reports
    
    #### Network Scaling
    With approximately 3 million daily active addresses on TRON as of June 2025, my analysis covered roughly one-third of all transactions. I applied a 2.5x multiplier to estimate total network activity:
    - Analyzed: ~3,400 merchants from 1.1M addresses
    - Estimated Total: ~8,500 USDT merchants on TRON globally
    
    #### Data Sources
    - Blockchain Data: TRON mainnet via Bitquery API
    - Transaction Period: June 3-10, 2025
    - Crypto Adoption Rates: Chainanalysis Global Crypto Adoption Index 2024
    - Analysis Date: June 2025
    
    #### Limitations
    - Currency Scope: Analysis limited to USDT transactions only
    - Geographic Accuracy: Time zone estimation may not reflect actual physical locations for all merchants
    - Temporal Snapshot: Data represents one week in June 2025; adoption patterns evolve rapidly
    - Exchange Exclusion: Methodology filters out centralized exchanges but may include some P2P traders
    - Payment Processors: Some identified "merchants" may be payment aggregators serving multiple businesses
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;'>
    <p>Data represents TRON blockchain USDT merchant transactions</p>
    <p style='font-size: 0.8rem;'>Geographic estimations are statistical inferences based on transaction patterns</p>
</div>
""", unsafe_allow_html=True)