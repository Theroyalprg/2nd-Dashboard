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

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #7f7f7f;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #7f7f7f;
        font-size: 0.8rem;
        padding-top: 1rem;
        border-top: 1px solid #e6e6e6;
    }
    .stSlider > div > div > div {
        background-color: #1f77b4;
    }
    .wind-speed-indicator {
        height: 10px;
        background: linear-gradient(90deg, #add8e6, #1f77b4, #000080);
        border-radius: 5px;
        margin: 10px 0;
    }
    .district-selector {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .source-info {
        font-size: 0.8rem;
        color: #7f7f7f;
        font-style: italic;
    }
    .map-container {
        border-radius: 0.5rem;
        overflow: hidden;
        margin-bottom: 1rem;
        border: 1px solid #e6e6e6;
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
    
    st.header("Project Parameters")
    years = st.slider("Project Lifetime (Years)", 1, 25, 10)
    capacity_mw = st.number_input("Turbine Capacity (MW)", 0.5, 10.0, 2.0, step=0.5)
    
    st.markdown("### Wind Conditions")
    avg_wind_speed = st.slider("Average Wind Speed (m/s)", 3.0, 12.0, 
                              district_data[selected_district]["wind_speed"], step=0.1)
    st.markdown('<div class="wind-speed-indicator"></div>', unsafe_allow_html=True)
    st.caption("Low ← Wind Speed → High")
    
    turbulence = st.slider("Turbulence Intensity (%)", 5.0, 25.0, 
                          district_data[selected_district]["turbulence"], step=0.1)
    
    st.markdown("### Financial Parameters")
    turbine_cost = st.number_input("Turbine Cost (₹ lakhs/MW)", 500, 1000, 650)
    om_cost = st.number_input("O&M Cost (₹ lakhs/MW/year)", 10, 50, 25)
    tariff_rate = st.number_input("Electricity Tariff (₹/kWh)", 3.0, 8.0, 4.5, step=0.1)
    
    st.markdown("---")
    st.info("Adjust the parameters to see how they affect your wind project's financial viability.")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # District information
    st.subheader(f"District Overview: {selected_district}")
    
    # Create a map centered on the selected district
    map_center = [district_data[selected_district]["lat"], district_data[selected_district]["lon"]]
    m = folium.Map(location=map_center, zoom_start=10)
    
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
    
    # Create charts
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_option == "Energy Output":
        ax.plot(years_range, cumulative_generation, marker="o", linewidth=2, color="#1f77b4")
        ax.fill_between(years_range, cumulative_generation, alpha=0.3, color="#1f77b4")
        ax.set_ylabel("Cumulative Energy (MWh)")
        ax.set_title("Projected Energy Output Over Time")
    elif chart_option == "Financial Performance":
        ax.plot(years_range, cumulative_revenue, marker="s", linewidth=2, color="#2ca02c", label="Revenue")
        ax.axhline(y=total_investment, color="#d62728", linestyle="--", label="Initial Investment")
        ax.fill_between(years_range, cumulative_revenue, alpha=0.3, color="#2ca02c")
        ax.set_ylabel("Amount (₹)")
        ax.set_title("Financial Performance Over Time")
        ax.legend()
    else:
        ax.plot(years_range, cumulative_cash_flow, marker="^", linewidth=2, color="#ff7f0e")
        ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) >= 0, alpha=0.3, color="#2ca02c")
        ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) < 0, alpha=0.3, color="#d62728")
        ax.axhline(y=0, color="#d62728", linestyle="--")
        ax.set_ylabel("Net Cash Flow (₹)")
        ax.set_title("Project Cash Flow Over Time")
    
    ax.set_xlabel("Years")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    # Additional charts
    st.subheader("Performance Details")
    col1b, col2b = st.columns(2)
    
    with col1b:
        # Capacity factor by wind speed
        wind_speeds = np.linspace(3, 12, 10)
        cap_factors = 0.35 * (wind_speeds/12) * (1 - (turbulence - 10)/100)
        
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.plot(wind_speeds, cap_factors, marker='o', color='#1f77b4')
        ax2.axvline(x=avg_wind_speed, color='red', linestyle='--', alpha=0.7)
        ax2.set_xlabel('Wind Speed (m/s)')
        ax2.set_ylabel('Capacity Factor')
        ax2.set_title('Capacity Factor vs. Wind Speed')
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
    
    with col2b:
        # Cost breakdown
        labels = ['Turbine Cost', 'O&M Cost']
        sizes = [total_investment, total_om_cost * years]
        colors = ['#1f77b4', '#ff7f0e']
        
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax3.axis('equal')
        ax3.set_title('Cost Breakdown')
        st.pyplot(fig3)

with col2:
    # Key metrics display
    st.subheader("Key Performance Indicators")
    
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
    st.subheader("District Comparison")
    comparison_data = []
    for district, data in district_data.items():
        comparison_data.append({
            "District": district,
            "Wind Speed (m/s)": data["wind_speed"],
            "Potential": data["potential"]
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

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
    © 2025 Wind Energy Analytics Dashboard by Prakarsh| For demonstration purposes only<br>
    Data Sources: National Institute of Wind Energy (NIWE), Ministry of New and Renewable Energy (MNRE), India Meteorological Department (IMD)<br>
    Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
</p>
""", unsafe_allow_html=True)
