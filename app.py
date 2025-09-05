import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Wind Forecast & ROI Dashboard - Madhya Pradesh",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling with cool color scheme
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #0B5345;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #0B5345;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #0B5345 0%, #1ABC9C 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        color: white;
        border: 1px solid #1ABC9C;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: white;
    }
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.85);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 500;
    }
    .footer {
        text-align: center;
        margin-top: 2.5rem;
        color: #7F8C8D;
        font-size: 0.85rem;
        padding-top: 1.2rem;
        border-top: 1px solid #BDC3C7;
    }
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #1ABC9C, #0B5345);
    }
    .wind-speed-indicator {
        height: 12px;
        background: linear-gradient(90deg, #AED6F1, #3498DB, #2E86C1);
        border-radius: 6px;
        margin: 12px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .district-selector {
        background: linear-gradient(135deg, #E8F8F5 0%, #D1F2EB 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid #A3E4D7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .source-info {
        font-size: 0.8rem;
        color: #7F8C8D;
        font-style: italic;
    }
    .map-container {
        border-radius: 0.8rem;
        overflow: hidden;
        margin-bottom: 1.2rem;
        border: 1px solid #BDC3C7;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .section-header {
        color: #0B5345;
        border-left: 5px solid #1ABC9C;
        padding-left: 12px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    /* Sidebar styling */
    .css-1d391kg, .css-1v0mbdj, .css-1y4v3va {
        background-color: #E8F8F5;
    }
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #0B5345 0%, #1ABC9C 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    /* Radio button styling */
    .stRadio > div {
        background-color: #E8F8F5;
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌬️ Wind Energy Dashboard - Madhya Pradesh</h1>', unsafe_allow_html=True)

# District data with wind potential (Sources: NIWE, MNRE, and IMD)
district_data = {
    "Bhopal": {
        "wind_speed": 4.2, 
        "potential": "Low", 
        "turbulence": 12.5, 
        "elevation": 523,
        "lat": 23.2599, 
        "lon": 77.4126,
        "source": "National Institute of Wind Energy (NIWE), 2023"
    },
    "Indore": {
        "wind_speed": 4.5, 
        "potential": "Low", 
        "turbulence": 11.8, 
        "elevation": 553,
        "lat": 22.7196, 
        "lon": 75.8577,
        "source": "National Institute of Wind Energy (NIWE), 2023"
    },
    "Jabalpur": {
        "wind_speed": 4.0, 
        "potential": "Low", 
        "turbulence": 13.2, 
        "elevation": 412,
        "lat": 23.1815, 
        "lon": 79.9864,
        "source": "Ministry of New and Renewable Energy (MNRE), 2023"
    },
    "Mandsaur": {
        "wind_speed": 4.6, 
        "potential": "Low", 
        "turbulence": 11.0, 
        "elevation": 427,
        "lat": 24.0718, 
        "lon": 75.0699,
        "source": "India Meteorological Department (IMD), 2023"
    },
    "Dewas": {
        "wind_speed": 4.5, 
        "potential": "Low", 
        "turbulence": 11.7, 
        "elevation": 535,
        "lat": 22.9658, 
        "lon": 76.0553,
        "source": "National Institute of Wind Energy (NIWE), 2023"
    },
    "Ujjain": {
        "wind_speed": 4.3, 
        "potential": "Low", 
        "turbulence": 12.0, 
        "elevation": 478,
        "lat": 23.1793, 
        "lon": 75.7849,
        "source": "India Meteorological Department (IMD), 2023"
    }
}

# Sidebar for user inputs
with st.sidebar:
    st.markdown('<div class="district-selector">', unsafe_allow_html=True)
    st.header("📍 Select District")
    selected_district = st.selectbox("", list(district_data.keys()), index=0)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-header">Project Parameters</h3>', unsafe_allow_html=True)
    years = st.slider("Project Lifetime (Years)", 1, 25, 10)
    capacity_mw = st.number_input("Turbine Capacity (MW)", 0.5, 10.0, 2.0, step=0.5)
    
    st.markdown('<h3 class="section-header">Wind Conditions</h3>', unsafe_allow_html=True)
    avg_wind_speed = st.slider("Average Wind Speed (m/s)", 3.0, 12.0, 
                              district_data[selected_district]["wind_speed"], step=0.1)
    st.markdown('<div class="wind-speed-indicator"></div>', unsafe_allow_html=True)
    st.caption("Low ← Wind Speed → High")
    
    turbulence = st.slider("Turbulence Intensity (%)", 5.0, 25.0, 
                          district_data[selected_district]["turbulence"], step=0.1)
    
    st.markdown('<h3 class="section-header">Financial Parameters</h3>', unsafe_allow_html=True)
    turbine_cost = st.number_input("Turbine Cost (₹ lakhs/MW)", 500, 1000, 650)
    om_cost = st.number_input("O&M Cost (₹ lakhs/MW/year)", 10, 50, 25)
    tariff_rate = st.number_input("Electricity Tariff (₹/kWh)", 3.0, 8.0, 4.5, step=0.1)
    
    st.markdown("---")
    st.info("Adjust the parameters to see how they affect your wind project's financial viability.")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # District information
    st.markdown(f'<h3 class="section-header">District Overview: {selected_district}</h3>', unsafe_allow_html=True)
    
    # Create a map centered on the selected district
    map_center = [district_data[selected_district]["lat"], district_data[selected_district]["lon"]]
    m = folium.Map(location=map_center, zoom_start=10, tiles="CartoDB positron")
    
    # Add marker for the selected district
    folium.Marker(
        map_center,
        popup=f"{selected_district}",
        tooltip=f"Wind Speed: {district_data[selected_district]['wind_speed']} m/s",
        icon=folium.Icon(color="green", icon="wind", prefix="fa")
    ).add_to(m)
    
    # Display the map
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    folium_static(m, width=700, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # District metrics
    col1a, col2a, col3a = st.columns(3)
    with col1a:
        st.metric("Average Wind Speed", f"{district_data[selected_district]['wind_speed']} m/s")
    with col2a:
        st.metric("Wind Potential", district_data[selected_district]["potential"])
    with col3a:
        st.metric("Elevation", f"{district_data[selected_district]['elevation']} m")
    
    st.caption(f"Source: {district_data[selected_district]['source']}")
    
    # Calculations
    capacity_factor = 0.35 * (avg_wind_speed/12) * (1 - (turbulence - 10)/100)
    estimated_annual_generation = capacity_mw * 8760 * capacity_factor
    annual_revenue = estimated_annual_generation * tariff_rate * 1000  # Convert to ₹
    total_investment = capacity_mw * turbine_cost * 100000  # Convert to ₹
    annual_om_cost = capacity_mw * om_cost * 100000  # Convert to ₹
    
    # Financial metrics
    annual_cash_flow = annual_revenue - annual_om_cost
    total_revenue = annual_revenue * years
    total_om_cost = annual_om_cost * years
    net_profit = total_revenue - total_investment - total_om_cost
    roi = (net_profit / total_investment) * 100 if total_investment > 0 else 0
    payback_period = total_investment / annual_cash_flow if annual_cash_flow > 0 else float('inf')
    
    # Create data for charts
    years_range = np.arange(1, years + 1)
    cumulative_generation = [estimated_annual_generation * y for y in years_range]
    cumulative_revenue = [annual_revenue * y for y in years_range]
    cumulative_cash_flow = [annual_cash_flow * y - total_investment for y in years_range]
    
    # Chart selection
    chart_option = st.radio("Select Chart View", 
                           ["Energy Output", "Financial Performance", "Cash Flow Analysis"], 
                           horizontal=True)
    
    # Create charts with updated color scheme
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.style.use('default')  # Reset to default style
    
    if chart_option == "Energy Output":
        ax.plot(years_range, cumulative_generation, marker="o", linewidth=2.5, color="#1ABC9C", markersize=8)
        ax.fill_between(years_range, cumulative_generation, alpha=0.3, color="#1ABC9C")
        ax.set_ylabel("Cumulative Energy (MWh)", fontweight='bold')
        ax.set_title("Projected Energy Output Over Time", fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3, linestyle='--')
    elif chart_option == "Financial Performance":
        ax.plot(years_range, cumulative_revenue, marker="s", linewidth=2.5, color="#3498DB", label="Revenue", markersize=8)
        ax.axhline(y=total_investment, color="#E74C3C", linestyle="--", linewidth=2, label="Initial Investment")
        ax.fill_between(years_range, cumulative_revenue, alpha=0.3, color="#3498DB")
        ax.set_ylabel("Amount (₹)", fontweight='bold')
        ax.set_title("Financial Performance Over Time", fontweight='bold', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--')
    else:
        ax.plot(years_range, cumulative_cash_flow, marker="^", linewidth=2.5, color="#9B59B6", markersize=8)
        ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) >= 0, alpha=0.3, color="#2ECC71")
        ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) < 0, alpha=0.3, color="#E74C3C")
        ax.axhline(y=0, color="#E74C3C", linestyle="--", linewidth=2)
        ax.set_ylabel("Net Cash Flow (₹)", fontweight='bold')
        ax.set_title("Project Cash Flow Over Time", fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3, linestyle='--')
    
    ax.set_xlabel("Years", fontweight='bold')
    st.pyplot(fig)
    
    # Additional charts
    st.markdown('<h3 class="section-header">Performance Details</h3>', unsafe_allow_html=True)
    col1b, col2b = st.columns(2)
    
    with col1b:
        # Capacity factor by wind speed
        wind_speeds = np.linspace(3, 12, 10)
        cap_factors = 0.35 * (wind_speeds/12) * (1 - (turbulence - 10)/100)
        
        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        ax2.plot(wind_speeds, cap_factors, marker='o', color='#3498DB', linewidth=2.5, markersize=6)
        ax2.axvline(x=avg_wind_speed, color='#E74C3C', linestyle='--', alpha=0.8, linewidth=2)
        ax2.set_xlabel('Wind Speed (m/s)', fontweight='bold')
        ax2.set_ylabel('Capacity Factor', fontweight='bold')
        ax2.set_title('Capacity Factor vs. Wind Speed', fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        st.pyplot(fig2)
    
    with col2b:
        # Cost breakdown
        labels = ['Turbine Cost', 'O&M Cost']
        sizes = [total_investment, total_om_cost * years]
        colors = ['#3498DB', '#9B59B6']
        
        fig3, ax3 = plt.subplots(figsize=(8, 4.5))
        wedges, texts, autotexts = ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                           startangle=90, textprops={'fontweight': 'bold'})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax3.axis('equal')
        ax3.set_title('Cost Breakdown', fontweight='bold')
        st.pyplot(fig3)

with col2:
    # Key metrics display
    st.markdown('<h3 class="section-header">Key Performance Indicators</h3>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Capacity Factor</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{capacity_factor:.1%}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Annual Energy Generation</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{estimated_annual_generation:,.0f} MWh</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Total Investment</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">₹ {total_investment:,.0f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Annual Revenue</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">₹ {annual_revenue:,.0f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Net Profit</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">₹ {net_profit:,.0f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">ROI</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{roi:.1f}%</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Payback Period</p>', unsafe_allow_html=True)
    payback_display = f"{payback_period:.1f} years" if payback_period != float('inf') else "> Project Lifetime"
    st.markdown(f'<p class="metric-value">{payback_display}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # District comparison
    st.markdown('<h3 class="section-header">District Comparison</h3>', unsafe_allow_html=True)
    comparison_data = []
    for district, data in district_data.items():
        comparison_data.append({
            "District": district,
            "Wind Speed (m/s)": data["wind_speed"],
            "Potential": data["potential"]
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    # Apply styling to the dataframe
    styled_df = comparison_df.style\
        .set_properties(**{'background-color': '#E8F8F5', 'color': '#0B5345', 'border': '1px solid #BDC3C7'})\
        .set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#0B5345'), ('color', 'white'), ('font-weight', 'bold')]
        }])
    
    st.dataframe(styled_df, use_container_width=True, height=300)

# Additional information
st.markdown("---")
expander = st.expander("Assumptions & Methodology")
with expander:
    st.write("""
    ### Calculation Methodology
    
    **Capacity Factor Calculation:**
    Capacity Factor = 0.35 × (V_avg / 12) × (1 - (TI - 10)/100)
    - V_avg: Average wind speed (m/s)
    - TI: Turbulence Intensity (%)
    - 12 m/s: Rated wind speed for most commercial turbines
    - 0.35: Typical efficiency factor for wind turbines
    - Turbulence adjustment: Higher turbulence reduces efficiency
    
    **Energy Generation:**
    Annual Generation (MWh) = Capacity (MW) × 8760 hours × Capacity Factor
    
    **Financial Calculations:**
    - Annual Revenue = Annual Generation × Tariff Rate
    - Total Investment = Turbine Cost × Capacity
    - Annual O&M Cost = O&M Cost × Capacity
    - Net Profit = Total Revenue - Total Investment - Total O&M Costs
    - ROI = (Net Profit / Total Investment) × 100
    - Payback Period = Total Investment / Annual Cash Flow
    
    ### Data Sources
    - Wind speed data: National Institute of Wind Energy (NIWE), Ministry of New and Renewable Energy (MNRE)
    - Turbine costs: Based on current market rates for wind turbines in India
    - O&M costs: Industry standards for wind farm maintenance
    - Tariff rates: Madhya Pradesh Electricity Regulatory Commission (MPERC) guidelines
    """)

# Footer
st.markdown("""
<p class="footer">
    © 2025 Wind Energy Analytics Dashboard by Prakarsh | For demonstration purposes only<br>
    Data Sources: National Institute of Wind Energy (NIWE), Ministry of New and Renewable Energy (MNRE), India Meteorological Department (IMD)<br>
   
</p>
""", unsafe_allow_html=True)
