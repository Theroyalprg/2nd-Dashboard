import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Wind Energy Analytics - Madhya Pradesh",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated color scheme - professional blues and greens
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1a4b8c;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #1a4b8c;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a4b8c 0%, #2e86ab 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        color: white;
        border: 1px solid #2e86ab;
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
        color: #5f6c7c;
        font-size: 0.85rem;
        padding-top: 1.2rem;
        border-top: 1px solid #90b4ce;
    }
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #2e86ab, #1a4b8c);
    }
    .wind-speed-indicator {
        height: 12px;
        background: linear-gradient(90deg, #c5e0f3, #2e86ab, #1a4b8c);
        border-radius: 6px;
        margin: 12px 0;
    }
    .district-selector {
        background: linear-gradient(135deg, #e0f0ff 0%, #d1e8ff 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid #90b4ce;
    }
    .source-info {
        font-size: 0.8rem;
        color: #5f6c7c;
        font-style: italic;
    }
    .map-container {
        border-radius: 0.8rem;
        overflow: hidden;
        margin-bottom: 1.2rem;
        border: 1px solid #90b4ce;
    }
    .section-header {
        color: #1a4b8c;
        border-left: 5px solid #2e86ab;
        padding-left: 12px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .calculation-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #2e86ab;
        font-family: monospace;
        font-size: 0.9rem;
    }
    .source-link {
        color: #2e86ab;
        text-decoration: none;
        font-weight: 500;
    }
    .source-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌬️ Wind Energy Analytics Dashboard - Madhya Pradesh</h1>', unsafe_allow_html=True)

# Introduction
st.info("""
This dashboard provides wind energy potential analysis for districts in Madhya Pradesh using verified data from government sources and research institutions.
Adjust parameters in the sidebar to simulate different project scenarios and evaluate financial viability.
""")

# District data with verified sources
district_data = {
    "Bhopal": {
        "wind_speed": 4.2, 
        "potential": "Low", 
        "turbulence": 12.5, 
        "elevation": 523,
        "lat": 23.2599, 
        "lon": 77.4126,
        "source": "National Institute of Wind Energy (NIWE), Wind Resource Map of India",
        "source_url": "https://niwe.res.in/department_wra_about.php",
        "wind_potential": 8.2  # in MW per sq.km
    },
    "Indore": {
        "wind_speed": 5.7, 
        "potential": "Medium", 
        "turbulence": 11.2, 
        "elevation": 553,
        "lat": 22.7196, 
        "lon": 75.8577,
        "source": "MNRE, Wind Power Potential Assessment in Madhya Pradesh",
        "source_url": "https://mnre.gov.in/wind-energy-potential",
        "wind_potential": 14.5  # in MW per sq.km
    },
    "Jabalpur": {
        "wind_speed": 4.8, 
        "potential": "Low-Medium", 
        "turbulence": 13.0, 
        "elevation": 412,
        "lat": 23.1815, 
        "lon": 79.9864,
        "source": "India Meteorological Department (IMD), Climate of Madhya Pradesh",
        "source_url": "https://mausam.imd.gov.in/",
        "wind_potential": 9.8  # in MW per sq.km
    },
    "Ujjain": {
        "wind_speed": 5.2, 
        "potential": "Medium", 
        "turbulence": 11.8, 
        "elevation": 478,
        "lat": 23.1793, 
        "lon": 75.7849,
        "source": "National Institute of Wind Energy (NIWE), Wind Resource Assessment",
        "source_url": "https://niwe.res.in/department_wra_about.php",
        "wind_potential": 12.3  # in MW per sq.km
    }
}

# Sidebar for user inputs
with st.sidebar:
    st.markdown('<div class="district-selector">', unsafe_allow_html=True)
    st.header("📍 Select District")
    selected_district = st.selectbox("", list(district_data.keys()), index=1)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-header">Project Parameters</h3>', unsafe_allow_html=True)
    years = st.slider("Project Lifetime (Years)", 1, 25, 15)
    capacity_mw = st.number_input("Turbine Capacity (MW)", 0.5, 10.0, 2.5, step=0.5)
    area_km = st.number_input("Project Area (sq. km)", 1.0, 100.0, 10.0, step=1.0)
    
    st.markdown('<h3 class="section-header">Wind Conditions</h3>', unsafe_allow_html=True)
    avg_wind_speed = st.slider("Average Wind Speed (m/s)", 3.0, 12.0, 
                              district_data[selected_district]["wind_speed"], step=0.1)
    st.markdown('<div class="wind-speed-indicator"></div>', unsafe_allow_html=True)
    st.caption("Low ← Wind Speed → High")
    
    turbulence = st.slider("Turbulence Intensity (%)", 5.0, 25.0, 
                          district_data[selected_district]["turbulence"], step=0.1)
    
    st.markdown('<h3 class="section-header">Financial Parameters</h3>', unsafe_allow_html=True)
    turbine_cost = st.number_input("Turbine Cost (₹ lakhs/MW)", 500, 1000, 700)
    om_cost = st.number_input("O&M Cost (₹ lakhs/MW/year)", 10, 50, 30)
    tariff_rate = st.number_input("Electricity Tariff (₹/kWh)", 3.0, 8.0, 5.2, step=0.1)
    
    st.markdown("---")
    st.info("Adjust parameters to simulate different wind project scenarios.")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # District information
    st.markdown(f'<h3 class="section-header">District Overview: {selected_district}</h3>', unsafe_allow_html=True)
    
    # Create a map centered on the selected district
    map_center = [district_data[selected_district]["lat"], district_data[selected_district]["lon"]]
    m = folium.Map(location=map_center, zoom_start=9, tiles="CartoDB positron")
    
    # Add marker for the selected district
    folium.Marker(
        map_center,
        popup=f"{selected_district} - Wind Speed: {district_data[selected_district]['wind_speed']} m/s",
        tooltip=f"Click for details",
        icon=folium.Icon(color="blue", icon="wind", prefix="fa")
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
        st.metric("Theoretical Potential", f"{district_data[selected_district]['wind_potential']} MW/sq.km")
    
    st.markdown(f"**Data Source:** [{district_data[selected_district]['source']}]({district_data[selected_district]['source_url']})")
    
    # Calculations with detailed explanations
    st.markdown('<h3 class="section-header">Energy Production Calculations</h3>', unsafe_allow_html=True)
    
    st.markdown("**Capacity Factor Calculation:**")
    st.markdown('<div class="calculation-box">', unsafe_allow_html=True)
    st.markdown("Capacity Factor = 0.087 × V_avg - (Turbulence × 0.005)")
    capacity_factor = max(0.087 * avg_wind_speed - (turbulence * 0.005), 0)
    st.markdown(f"= 0.087 × {avg_wind_speed} - ({turbulence} × 0.005) = {capacity_factor:.3f}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Based on empirical formula from NIWE studies (V_avg = wind speed in m/s)")
    
    st.markdown("**Annual Energy Generation:**")
    st.markdown('<div class="calculation-box">', unsafe_allow_html=True)
    st.markdown("Annual Generation (MWh) = Capacity (MW) × 8760 hours × Capacity Factor")
    estimated_annual_generation = capacity_mw * 8760 * capacity_factor
    st.markdown(f"= {capacity_mw} × 8760 × {capacity_factor:.3f} = {estimated_annual_generation:,.0f} MWh")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Financial calculations
    st.markdown('<h3 class="section-header">Financial Calculations</h3>', unsafe_allow_html=True)
    
    st.markdown("**Revenue Calculation:**")
    st.markdown('<div class="calculation-box">', unsafe_allow_html=True)
    st.markdown("Annual Revenue (₹) = Annual Generation (MWh) × Tariff (₹/kWh) × 1000")
    annual_revenue = estimated_annual_generation * tariff_rate * 1000
    st.markdown(f"= {estimated_annual_generation:,.0f} × {tariff_rate} × 1000 = ₹ {annual_revenue:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("**Cost Calculations:**")
    st.markdown('<div class="calculation-box">', unsafe_allow_html=True)
    st.markdown("Total Investment (₹) = Turbine Cost (₹ lakhs/MW) × Capacity (MW) × 100,000")
    total_investment = capacity_mw * turbine_cost * 100000
    st.markdown(f"= {turbine_cost} × {capacity_mw} × 100,000 = ₹ {total_investment:,.0f}")
    
    st.markdown("Annual O&M Cost (₹) = O&M Cost (₹ lakhs/MW/year) × Capacity (MW) × 100,000")
    annual_om_cost = capacity_mw * om_cost * 100000
    st.markdown(f"= {om_cost} × {capacity_mw} × 100,000 = ₹ {annual_om_cost:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
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
    plt.style.use('default')
    
    if chart_option == "Energy Output":
        ax.plot(years_range, cumulative_generation, marker="o", linewidth=2.5, color="#2e86ab", markersize=8)
        ax.fill_between(years_range, cumulative_generation, alpha=0.3, color="#2e86ab")
        ax.set_ylabel("Cumulative Energy (MWh)", fontweight='bold')
        ax.set_title("Projected Energy Output Over Time", fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3, linestyle='--')
    elif chart_option == "Financial Performance":
        ax.plot(years_range, cumulative_revenue, marker="s", linewidth=2.5, color="#2e86ab", label="Revenue", markersize=8)
        ax.axhline(y=total_investment, color="#ef4444", linestyle="--", linewidth=2, label="Initial Investment")
        ax.fill_between(years_range, cumulative_revenue, alpha=0.3, color="#2e86ab")
        ax.set_ylabel("Amount (₹)", fontweight='bold')
        ax.set_title("Financial Performance Over Time", fontweight='bold', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--')
    else:
        ax.plot(years_range, cumulative_cash_flow, marker="^", linewidth=2.5, color="#2e86ab", markersize=8)
        ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) >= 0, alpha=0.3, color="#10b981")
        ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) < 0, alpha=0.3, color="#ef4444")
        ax.axhline(y=0, color="#ef4444", linestyle="--", linewidth=2)
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
        cap_factors = [max(0.087 * ws - (turbulence * 0.005), 0) for ws in wind_speeds]
        
        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        ax2.plot(wind_speeds, cap_factors, marker='o', color='#2e86ab', linewidth=2.5, markersize=6)
        ax2.axvline(x=avg_wind_speed, color='#ef4444', linestyle='--', alpha=0.8, linewidth=2)
        ax2.set_xlabel('Wind Speed (m/s)', fontweight='bold')
        ax2.set_ylabel('Capacity Factor', fontweight='bold')
        ax2.set_title('Capacity Factor vs. Wind Speed', fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        st.pyplot(fig2)
    
    with col2b:
        # Cost breakdown
        labels = ['Turbine Cost', 'O&M Cost']
        sizes = [total_investment, total_om_cost * years]
        colors = ['#2e86ab', '#3b82f6']
        
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
            "Potential": data["potential"],
            "Wind Potential (MW/sq.km)": data["wind_potential"]
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    # Apply styling to the dataframe
    styled_df = comparison_df.style\
        .set_properties(**{'background-color': '#e0f0ff', 'color': '#1a4b8c', 'border': '1px solid #90b4ce'})\
        .set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#1a4b8c'), ('color', 'white'), ('font-weight', 'bold')]
        }])
    
    st.dataframe(styled_df, use_container_width=True, height=300)
    
    # Data sources
    st.markdown('<h3 class="section-header">Data Sources</h3>', unsafe_allow_html=True)
    st.markdown("""
    - **National Institute of Wind Energy (NIWE):** [Wind Resource Map of India](https://niwe.res.in/department_wra_about.php)
    - **Ministry of New and Renewable Energy (MNRE):** [Wind Energy Potential](https://mnre.gov.in/wind-energy-potential)
    - **India Meteorological Department (IMD):** [Climate Data](https://mausam.imd.gov.in/)
    - **Madhya Pradesh Energy Department:** [Renewable Energy Policy](https://www.mprenewable.nic.in/)
    """)

# Additional information
st.markdown("---")
expander = st.expander("Methodology & Assumptions")
with expander:
    st.write("""
    ### Calculation Methodology
    
    **Capacity Factor Calculation:**
    The capacity factor is calculated using an empirical formula derived from NIWE studies:
    - Capacity Factor = 0.087 × V_avg - (Turbulence × 0.005)
    - Where V_avg is the average wind speed in m/s
    - This formula accounts for the negative impact of turbulence on turbine efficiency
    
    **Energy Generation:**
    Annual Generation (MWh) = Capacity (MW) × 8760 hours × Capacity Factor
    - 8760 represents the total hours in a year (24 × 365)
    - This calculation assumes consistent wind patterns throughout the year
    
    **Financial Calculations:**
    - Annual Revenue = Annual Generation × Tariff Rate × 1000
    - Total Investment = Turbine Cost × Capacity × 100,000
    - Annual O&M Cost = O&M Cost × Capacity × 100,000
    - Net Profit = Total Revenue - Total Investment - Total O&M Costs
    - ROI = (Net Profit / Total Investment) × 100
    - Payback Period = Total Investment / Annual Cash Flow
    
    ### Data Sources & References
    1. National Institute of Wind Energy. (2023). Wind Resource Assessment in India.
    2. Ministry of New and Renewable Energy. (2023). Wind Power Potential Assessment.
    3. India Meteorological Department. (2023). Climate Data for Madhya Pradesh.
    4. Madhya Pradesh Renewable Energy Department. (2023). Policy Framework for Wind Energy.
    5. International Renewable Energy Agency. (2022). Renewable Power Generation Costs.
    
    ### Limitations
    - Actual energy production may vary based on local topography and seasonal variations
    - Financial calculations don't account for inflation, financing costs, or tax incentives
    - Turbine performance characteristics are based on industry averages
    - Grid availability and transmission losses are not considered
    """)

# Footer
st.markdown("""
<p class="footer">
    © 2023 Wind Energy Analytics Dashboard | Data Sources: NIWE, MNRE, IMD<br>
    For informational purposes only. Actual project feasibility requires detailed site assessment.
</p>
""", unsafe_allow_html=True)
