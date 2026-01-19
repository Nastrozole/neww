# crypto_regulation_watch.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import base64

# Page configuration
st.set_page_config(
    page_title="Crypto Regulation Watch",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .regulation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    .regulation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .high-relevance { border-left: 4px solid #dc3545; }
    .medium-relevance { border-left: 4px solid #ffc107; }
    .low-relevance { border-left: 4px solid #28a745; }
    .stDataFrame { 
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .country-flag {
        font-size: 1.5rem;
        margin-right: 8px;
    }
    .last-updated {
        font-size: 0.85rem;
        color: #6c757d;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Country flag mapping
COUNTRY_FLAGS = {
    "USA": "🇺🇸",
    "UK": "🇬🇧",
    "EU": "🇪🇺",
    "Singapore": "🇸🇬",
    "Japan": "🇯🇵",
    "UAE": "🇦🇪",
    "Switzerland": "🇨🇭",
    "Hong Kong": "🇭🇰",
    "Australia": "🇦🇺",
    "Canada": "🇨🇦",
    "Morocco": "🇲🇦",
    "Global": "🌍"
}

# Sample data - In production, this would come from a database or API
def load_sample_data():
    """Load sample regulatory data"""
    data = [
        {
            "id": 1,
            "source": "Financial Times",
            "authority": "SEC (Securities and Exchange Commission)",
            "country": "USA",
            "type": "Guidance",
            "what_changed": "Updated rules for crypto custody by registered investment advisors",
            "neutral_description": "SEC released new guidance requiring enhanced safeguards for digital assets held by registered investment advisors.",
            "impacted": "Custodians, Investment Advisors",
            "relevance_morocco": "Medium",
            "next_action": "Monitor",
            "date": datetime.now() - timedelta(days=2),
            "status": "Active"
        },
        {
            "id": 2,
            "source": "Bloomberg",
            "authority": "FCA (Financial Conduct Authority)",
            "country": "UK",
            "type": "Consultation",
            "what_changed": "Opened consultation on cryptoasset promotion rules",
            "neutral_description": "FCA seeking feedback on proposed rules for marketing cryptoassets to UK consumers.",
            "impacted": "Exchanges, Marketing Agencies",
            "relevance_morocco": "Low",
            "next_action": "Analyze",
            "date": datetime.now() - timedelta(days=5),
            "status": "Active"
        },
        {
            "id": 3,
            "source": "Reuters",
            "authority": "MAS (Monetary Authority of Singapore)",
            "country": "Singapore",
            "type": "Law",
            "what_changed": "Digital Payment Token services now require full license",
            "neutral_description": "MAS implemented new licensing framework for all digital payment token service providers.",
            "impacted": "Exchanges, Custodians, Banks",
            "relevance_morocco": "High",
            "next_action": "Analyze",
            "date": datetime.now() - timedelta(days=1),
            "status": "Active"
        },
        {
            "id": 4,
            "source": "CoinDesk",
            "authority": "European Banking Authority",
            "country": "EU",
            "type": "Regulation",
            "what_changed": "MiCA implementation guidelines published",
            "neutral_description": "EBA published detailed guidelines for implementation of Markets in Crypto-Assets regulation.",
            "impacted": "Exchanges, Custodians, Banks, Consumers",
            "relevance_morocco": "High",
            "next_action": "Analyze",
            "date": datetime.now() - timedelta(days=3),
            "status": "Active"
        },
        {
            "id": 5,
            "source": "WSJ",
            "authority": "Bank Al-Maghrib",
            "country": "Morocco",
            "type": "Speech",
            "what_changed": "Governor announced exploratory phase for CBDC",
            "neutral_description": "Central bank governor mentioned exploring digital currency options in recent conference.",
            "impacted": "Banks, Consumers",
            "relevance_morocco": "High",
            "next_action": "Monitor",
            "date": datetime.now() - timedelta(days=4),
            "status": "Active"
        },
        {
            "id": 6,
            "source": "Forbes",
            "authority": "FINMA",
            "country": "Switzerland",
            "type": "Guidance",
            "what_changed": "Updated anti-money laundering rules for crypto firms",
            "neutral_description": "Swiss regulator clarified AML requirements for cryptocurrency businesses.",
            "impacted": "Exchanges, Custodians",
            "relevance_morocco": "Medium",
            "next_action": "Monitor",
            "date": datetime.now() - timedelta(days=7),
            "status": "Active"
        },
        {
            "id": 7,
            "source": "FT Adviser",
            "authority": "IOSCO",
            "country": "Global",
            "type": "Consultation",
            "what_changed": "Global crypto regulation standards proposal",
            "neutral_description": "International organization published consultation paper on global regulatory standards.",
            "impacted": "Exchanges, Custodians, Banks, Consumers",
            "relevance_morocco": "High",
            "next_action": "Analyze",
            "date": datetime.now() - timedelta(days=6),
            "status": "Active"
        }
    ]
    return pd.DataFrame(data)

def create_metrics(df):
    """Create metrics cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">{len(df)}</h3>
            <p style="color: #6c757d; margin: 0;">Total Updates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high_count = len(df[df['relevance_morocco'] == 'High'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #dc3545; margin: 0;">{high_count}</h3>
            <p style="color: #6c757d; margin: 0;">High Relevance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        countries = df['country'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">{countries}</h3>
            <p style="color: #6c757d; margin: 0;">Countries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        analyze_count = len(df[df['next_action'] == 'Analyze'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ffc107; margin: 0;">{analyze_count}</h3>
            <p style="color: #6c757d; margin: 0;">Require Analysis</p>
        </div>
        """, unsafe_allow_html=True)

def create_visualizations(df):
    """Create charts and visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Relevance distribution
        relevance_counts = df['relevance_morocco'].value_counts()
        fig1 = px.pie(
            values=relevance_counts.values,
            names=relevance_counts.index,
            title="Relevance for Morocco Distribution",
            color=relevance_counts.index,
            color_discrete_map={'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Regulation type distribution
        type_counts = df['type'].value_counts()
        fig2 = px.bar(
            x=type_counts.values,
            y=type_counts.index,
            orientation='h',
            title="Regulation Types",
            color=type_counts.values,
            color_continuous_scale='Blues'
        )
        fig2.update_layout(height=300, xaxis_title="Count", yaxis_title="Type")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Timeline by country
    st.subheader("Regulation Timeline by Country")
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    fig3 = px.scatter(
        df,
        x='date',
        y='country',
        color='relevance_morocco',
        size=[20]*len(df),
        hover_data=['authority', 'type', 'what_changed'],
        title="Regulation Updates Timeline",
        color_discrete_map={'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

def render_regulation_card(row):
    """Render a single regulation card"""
    relevance_class = f"{row['relevance_morocco'].lower()}-relevance"
    flag = COUNTRY_FLAGS.get(row['country'], '📍')
    
    st.markdown(f"""
    <div class="regulation-card {relevance_class}">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h4 style="margin: 0 0 8px 0;">
                    <span class="country-flag">{flag}</span>
                    {row['authority']}
                </h4>
                <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <span style="background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">
                        {row['type']}
                    </span>
                    <span style="background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">
                        {row['country']}
                    </span>
                    <span style="background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">
                        Relevance: {row['relevance_morocco']}
                    </span>
                </div>
            </div>
            <span style="color: #6c757d; font-size: 0.9rem;">
                {row['date'].strftime('%b %d, %Y')}
            </span>
        </div>
        <p style="font-weight: 600; color: #212529; margin: 12px 0 8px 0;">
            {row['what_changed']}
        </p>
        <p style="color: #495057; margin: 0 0 12px 0; font-size: 0.95rem;">
            {row['neutral_description']}
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 0.9rem; color: #6c757d;">
                    Impacted: <strong>{row['impacted']}</strong>
                </span>
            </div>
            <span style="background: {'#ffc107' if row['next_action'] == 'Analyze' else '#17a2b8'}; 
                  color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">
                {row['next_action']}
            </span>
        </div>
        <p style="margin: 8px 0 0 0; font-size: 0.85rem; color: #6c757d;">
            Source: {row['source']}
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Load data
    df = load_sample_data()
    
    # Header
    st.markdown('<h1 class="main-header">Crypto Regulation Watch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Global cryptocurrency regulatory updates and their relevance for Morocco</p>', unsafe_allow_html=True)
    
    # Last updated info
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    st.markdown(f'<p class="last-updated">Last updated: {last_updated} | Data updates daily</p>', unsafe_allow_html=True)
    
    # Metrics
    create_metrics(df)
    
    # Filters in sidebar
    st.sidebar.header("🔍 Filters")
    
    # Country filter
    all_countries = ['All'] + sorted(df['country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Country", all_countries)
    
    # Relevance filter
    relevance_options = ['All', 'High', 'Medium', 'Low']
    selected_relevance = st.sidebar.multiselect(
        "Relevance for Morocco", 
        relevance_options,
        default=['High', 'Medium']
    )
    
    # Type filter
    type_options = ['All'] + sorted(df['type'].unique().tolist())
    selected_type = st.sidebar.multiselect(
        "Regulation Type",
        type_options,
        default=['All']
    )
    
    # Next action filter
    action_options = ['All'] + sorted(df['next_action'].unique().tolist())
    selected_action = st.sidebar.multiselect(
        "Next Action",
        action_options,
        default=['All']
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    
    if 'All' not in selected_relevance:
        filtered_df = filtered_df[filtered_df['relevance_morocco'].isin(selected_relevance)]
    
    if 'All' not in selected_type:
        filtered_df = filtered_df[filtered_df['type'].isin(selected_type)]
    
    if 'All' not in selected_action:
        filtered_df = filtered_df[filtered_df['next_action'].isin(selected_action)]
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📊 Analytics", "🗂️ Data Table", "📥 Export"])
    
    with tab1:
        st.subheader(f"Recent Regulatory Updates ({len(filtered_df)} total)")
        
        # Sort options
        sort_by = st.selectbox("Sort by", 
                              ["Date (Newest First)", "Date (Oldest First)", 
                               "Relevance (High to Low)", "Country A-Z"])
        
        if sort_by == "Date (Newest First)":
            filtered_df = filtered_df.sort_values('date', ascending=False)
        elif sort_by == "Date (Oldest First)":
            filtered_df = filtered_df.sort_values('date', ascending=True)
        elif sort_by == "Relevance (High to Low)":
            relevance_order = {'High': 3, 'Medium': 2, 'Low': 1}
            filtered_df['relevance_order'] = filtered_df['relevance_morocco'].map(relevance_order)
            filtered_df = filtered_df.sort_values('relevance_order', ascending=False)
            filtered_df = filtered_df.drop('relevance_order', axis=1)
        elif sort_by == "Country A-Z":
            filtered_df = filtered_df.sort_values('country')
        
        # Display regulation cards
        for _, row in filtered_df.iterrows():
            render_regulation_card(row)
    
    with tab2:
        create_visualizations(filtered_df)
        
        # Additional statistics
        st.subheader("Key Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            most_active_country = filtered_df['country'].value_counts().index[0]
            st.metric("Most Active Country", most_active_country)
        
        with col2:
            avg_days_old = (datetime.now() - filtered_df['date'].max()).days
            st.metric("Latest Update (Days Ago)", avg_days_old)
        
        with col3:
            primary_type = filtered_df['type'].value_counts().index[0]
            st.metric("Most Common Type", primary_type)
    
    with tab3:
        st.subheader("Detailed Data View")
        
        # Enhanced dataframe display
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        # Add flags to country column
        display_df['country'] = display_df['country'].apply(
            lambda x: f"{COUNTRY_FLAGS.get(x, '📍')} {x}"
        )
        
        # Select columns to display
        columns_to_show = ['country', 'authority', 'type', 'what_changed', 
                          'relevance_morocco', 'next_action', 'date', 'source']
        st.dataframe(
            display_df[columns_to_show],
            column_config={
                "country": "Country",
                "authority": "Authority",
                "type": "Type",
                "what_changed": "What Changed",
                "relevance_morocco": "Relevance",
                "next_action": "Next Action",
                "date": "Date",
                "source": "Source"
            },
            use_container_width=True,
            height=400
        )
    
    with tab4:
        st.subheader("Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as CSV
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"crypto_regulation_watch_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export as JSON
            json_data = filtered_df.to_json(orient='records', indent=2, date_format='iso')
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name=f"crypto_regulation_watch_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        st.markdown("---")
        st.subheader("Add New Regulation")
        
        # Form for adding new entries
        with st.form("add_regulation"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_source = st.text_input("Source")
                new_authority = st.text_input("Authority / Institution")
                new_country = st.selectbox("Country", list(COUNTRY_FLAGS.keys()))
                new_type = st.selectbox("Type", ["Law", "Consultation", "Guidance", "Speech", "Regulation"])
            
            with col2:
                new_impacted = st.multiselect(
                    "Who is impacted",
                    ["Exchanges", "Custodians", "Banks", "Consumers", "Developers", "Investors"]
                )
                new_relevance = st.select_slider("Potential relevance for Morocco", ["Low", "Medium", "High"])
                new_next_action = st.selectbox("Next action", ["Monitor", "Analyze", "Ignore for now"])
            
            new_what_changed = st.text_area("What changed (3 lines max)", height=80)
            new_description = st.text_area("Neutral description only", height=100)
            
            submitted = st.form_submit_button("Add Regulation")
            
            if submitted and new_source and new_authority and new_what_changed:
                st.success("Regulation added successfully! (Note: In production, this would save to a database)")
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        <p>Crypto Regulation Watch Dashboard • Updated Daily • Neutral Information Only</p>
        <p>For internal use only. No facts asserted by this tool.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
