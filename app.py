import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
# --- ADDED IMPORTS ---
import requests
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Page configuration
# --- NEW UI/UX: "SOLAR FLARE" THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    /* --- Base Variables --- */
    :root {
        --solar-orange: #FF8C00;
        --solar-yellow: #FFD700;
        --dark-bg: #121212;
        --light-bg: #1E1E1E;
        --container-bg: rgba(28, 28, 28, 0.85);
        --text-color: #E0E0E0;
        --subtle-text-color: #A0A0A0;
        --border-gradient: linear-gradient(90deg, var(--solar-orange), var(--solar-yellow));
        --border-color: #333;
    }

    /* --- General Styling --- */
    html, body, [class*="st-"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background-color: var(--dark-bg);
        color: var(--text-color);
    }

    /* --- Main Header --- */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        color: white;
        background: -webkit-linear-gradient(45deg, var(--solar-orange), var(--solar-yellow));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 2px solid var(--solar-orange);
    }
    
    /* --- Sidebar Styling --- */
    [data-testid="stSidebar"] {
        background-color: var(--light-bg);
        border-right: 1px solid var(--container-bg);
    }
    
    [data-testid="stSidebar"] h3 {
        color: var(--solar-yellow);
    }

    /* --- Custom UI Card Container --- */
    .card {
        background: var(--container-bg);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }
    
    /* --- Metric Cards (Original) --- */
    .metric-card {
        background: var(--light-bg);
        border-top: 4px solid;
        border-image-source: var(--border-gradient);
        border-image-slice: 1;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: scale(1.05);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--solar-yellow);
    }
    .metric-label {
        font-size: 0.9rem;
        color: var(--subtle-text-color);
        text-transform: uppercase;
        font-weight: 600;
    }

    /* --- Tabs Styling --- */
    .stTabs [data-baseweb="tab"] {
        background-color: var(--container-bg);
        border-radius: 8px;
        color: var(--subtle-text-color);
        margin: 0 5px;
        border: 1px solid var(--border-color);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-image: var(--border-gradient);
        color: black;
        font-weight: bold;
    }

    /* --- Buttons and Inputs --- */
    .stButton > button {
        background-image: var(--border-gradient);
        color: black !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: opacity 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.8;
        border: none;
        color: black;
    }
    
    /* --- Footer --- */
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: var(--subtle-text-color);
        font-size: 0.8rem;
    }
    
    /* --- Expander Styling --- */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--solar-yellow);
        background: var(--container-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
    }
    
    .google-form-container {
        padding: 1rem;
        border-radius: 1rem;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        text-align: center;
    }
    .google-form-container iframe {
        width: 100%;
        height: 1200px;
        border: none;
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)

# Email configuration
def get_email_config():
    """Get email configuration from secrets"""
    return {
        'smtp_server': st.secrets.get('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': st.secrets.get('SMTP_PORT', 587),
        'sender_email': st.secrets.get('SENDER_EMAIL', ''),
        'sender_password': st.secrets.get('SENDER_PASSWORD', ''),
        'receiver_email': st.secrets.get('RECEIVER_EMAIL', '')
    }

# Email validation
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Send email function
def send_feedback_email(name, email, feedback_type, message, config):
    """Send feedback email"""
    if not all([config['sender_email'], config['sender_password'], config['receiver_email']]):
        st.error("Email configuration is missing in secrets. Please contact the administrator.")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = config['receiver_email']
        msg['Subject'] = f"🌬️ Wind Dashboard Feedback - {feedback_type}"
        body = f"""
        New Feedback from Wind Energy Dashboard:
        Name: {name}
        Email: {email}
        Feedback Type: {feedback_type}
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Message:
        {message}
        """
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}. Check your credentials and server settings.")
        return False

# --- UPDATED NAVIGATION ---
page = st.sidebar.selectbox(
    "Navigate",
    ["Wind Dashboard", "Tableau Dashboard", "Data Sources & Information", "AI Assistant", "Feedback & Support"]
)

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

if page == "Wind Dashboard":
    # Header
    st.markdown('<h1 class="main-header">🌬️ Wind Energy Analytics Dashboard</h1>', unsafe_allow_html=True)
    # Introduction
    
   
st.markdown('<div class="card">', unsafe_allow_html=True)
st.info("""
This dashboard provides wind energy potential analysis for districts in Madhya Pradesh using verified data from government sources and research institutions.
    Adjust parameters in the sidebar to simulate different project scenarios and evaluate financial viability.
""")
st.markdown('</div>', unsafe_allow_html=True)
    # Sidebar for user inputs
    with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📍 Simulation Controls")
    selected_district = st.selectbox("Select District", list(district_data.keys()), index=1)
    st.markdown('</div>', unsafe_allow_html=True)
        
        # --- DESIGN: Added icons to headers ---
        st.markdown('<h3 class="section-header">⚙️ Project Parameters</h3>', unsafe_allow_html=True)
        years = st.slider("Project Lifetime (Years)", 1, 25, 15)
        capacity_mw = st.number_input("Turbine Capacity (MW)", 0.5, 10.0, 2.5, step=0.5)
        area_km = st.number_input("Project Area (sq. km)", 1.0, 100.0, 10.0, step=1.0)
        
        st.markdown('<h3 class="section-header">💨 Wind Conditions</h3>', unsafe_allow_html=True)
        avg_wind_speed = st.slider("Average Wind Speed (m/s)", 3.0, 12.0, 
                                   district_data[selected_district]["wind_speed"], step=0.1)
        st.markdown('<div class="wind-speed-indicator"></div>', unsafe_allow_html=True)
        st.caption("Low ← Wind Speed → High")
        
        turbulence = st.slider("Turbulence Intensity (%)", 5.0, 25.0, 
                               district_data[selected_district]["turbulence"], step=0.1)
        
        st.markdown('<h3 class="section-header">💰 Financial Parameters</h3>', unsafe_allow_html=True)
        turbine_cost = st.number_input("Turbine Cost (₹ lakhs/MW)", 500, 1000, 700)
        om_cost = st.number_input("O&M Cost (₹ lakhs/MW/year)", 10, 50, 30)
        tariff_rate = st.number_input("Electricity Tariff (₹/kWh)", 3.0, 8.0, 5.2, step=0.1)
        
        st.markdown("---")
        st.info("Adjust parameters to simulate different wind project scenarios.")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # District information
        st.markdown(f'<h3 class="section-header">🗺️ District Overview: {selected_district}</h3>', unsafe_allow_html=True)
        
        # Create a map centered on the selected district
        map_center = [district_data[selected_district]["lat"], district_data[selected_district]["lon"]]
        # --- DESIGN: Changed map style ---
        m = folium.Map(location=map_center, zoom_start=9, tiles="CartoDB positron")
        
        # Add marker for the selected district
        folium.Marker(
            map_center,
            popup=f"<strong>{selected_district}</strong><br>Wind Speed: {district_data[selected_district]['wind_speed']} m/s",
            tooltip=f"Click for details",
            icon=folium.Icon(color="green", icon="wind", prefix="fa") # --- DESIGN: Changed icon color ---
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
        
        # --- DESIGN: Calculations placed inside an expander to clean up the UI ---
        with st.expander("Show Detailed Calculation Steps"):
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

        # Financial metrics (calculated outside expander to be available for charts)
        capacity_factor = max(0.087 * avg_wind_speed - (turbulence * 0.005), 0)
        estimated_annual_generation = capacity_mw * 8760 * capacity_factor
        annual_revenue = estimated_annual_generation * tariff_rate * 1000
        total_investment = capacity_mw * turbine_cost * 100000
        annual_om_cost = capacity_mw * om_cost * 100000
        annual_cash_flow = annual_revenue - annual_om_cost
        total_revenue = annual_revenue * years
        total_om_cost = annual_om_cost * years
        net_profit = total_revenue - total_investment - total_om_cost
        roi = (net_profit / total_investment) * 100 if total_investment > 0 else 0
        payback_period = total_investment / annual_cash_flow if annual_cash_flow > 0 else float('inf')
        
        years_range = np.arange(1, years + 1)
        cumulative_generation = [estimated_annual_generation * y for y in years_range]
        cumulative_revenue = [annual_revenue * y for y in years_range]
        cumulative_cash_flow = [annual_cash_flow * y - total_investment for y in years_range]
        
        # --- DESIGN: Replaced Radio Button with modern Tabs ---
        tab1, tab2, tab3 = st.tabs(["📊 Financial Performance", "⚡ Energy Output", "📈 Cash Flow Analysis (Interactive)"])
        
        with tab1:
            fig, ax = plt.subplots(figsize=(10, 6))
            plt.style.use('dark_background')
            ax.set_facecolor('#1a202c')
            fig.patch.set_facecolor('#0f1a2a')
            ax.plot(years_range, cumulative_revenue, marker="s", linewidth=2.5, color="#4fd1c5", label="Revenue", markersize=8)
            ax.axhline(y=total_investment, color="#fc8181", linestyle="--", linewidth=2, label="Initial Investment")
            ax.fill_between(years_range, cumulative_revenue, alpha=0.3, color="#4fd1c5")
            ax.set_ylabel("Amount (₹)", fontweight='bold', color='white')
            ax.set_title("Financial Performance Over Time", fontweight='bold', fontsize=14, color='white')
            ax.legend(facecolor='#2d3748', edgecolor='#4a5568', labelcolor='white')
            ax.grid(True, alpha=0.3, linestyle='--', color='#4a5568')
            ax.tick_params(colors='white')
            ax.set_xlabel("Years", fontweight='bold', color='white')
            st.pyplot(fig)
            
        with tab2:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            plt.style.use('dark_background')
            ax2.set_facecolor('#1a202c')
            fig2.patch.set_facecolor('#0f1a2a')
            ax2.plot(years_range, cumulative_generation, marker="o", linewidth=2.5, color="#4fd1c5", markersize=8)
            ax2.fill_between(years_range, cumulative_generation, alpha=0.3, color="#4fd1c5")
            ax2.set_ylabel("Cumulative Energy (MWh)", fontweight='bold', color='white')
            ax2.set_title("Projected Energy Output Over Time", fontweight='bold', fontsize=14, color='white')
            ax2.grid(True, alpha=0.3, linestyle='--', color='#4a5568')
            ax2.tick_params(colors='white')
            ax2.set_xlabel("Years", fontweight='bold', color='white')
            st.pyplot(fig2)

        with tab3:
            # --- DESIGN: Replaced Matplotlib chart with an interactive Plotly chart ---
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=list(years_range), y=cumulative_cash_flow, mode='lines+markers', name='Net Cash Flow',
                                     line=dict(color='#4fd1c5', width=3), marker=dict(size=8)))
            fig_plotly.update_layout(
                title='Interactive Project Cash Flow Over Time',
                xaxis_title='Years',
                yaxis_title='Net Cash Flow (₹)',
                plot_bgcolor='#1a202c',
                paper_bgcolor='#0f1a2a',
                font=dict(color='#e6e9f0'),
                xaxis=dict(gridcolor='#4a5568'),
                yaxis=dict(gridcolor='#4a5568'),
                hovermode='x unified'
            )
            fig_plotly.add_hline(y=0, line_dash="dash", line_color="#fc8181")
            st.plotly_chart(fig_plotly, use_container_width=True)

    with col2:
        # Key metrics display
        st.markdown('<h3 class="section-header">📊 Key Performance Indicators</h3>', unsafe_allow_html=True)
        
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

    # --- ADDED FOOTNOTE ---
    st.markdown("""
    <p class="footer">
        © 2025 Wind Energy Analytics Dashboard by PRAKARSH | Data Sources: NIWE, MNRE, IMD<br>
        For informational purposes only. Actual project feasibility requires detailed site assessment.
    </p>
    """, unsafe_allow_html=True)

# --- ADDED TABLEAU PAGE ---
elif page == "Tableau Dashboard":
    st.markdown('<h1 class="main-header">📊 Tableau Public Dashboard</h1>', unsafe_allow_html=True)
    st.info("This page displays an interactive dashboard hosted on Tableau Public.")

    tableau_url = "https://public.tableau.com/views/RenewablePowerCapacityinIndia/Dashboard1?:language=en-US&:display_count=n&:origin=viz_share_link"
    
    with st.expander("How to embed your own dashboard"):
        st.markdown("""
        1.  Go to your dashboard on [Tableau Public](https://public.tableau.com/).
        2.  Click the **Share** button at the bottom of the viz.
        3.  Copy the URL from the **Link** box.
        4.  Paste that URL into the `tableau_url` variable in the code.
        """)

    embed_code = f'<iframe src="{tableau_url}:showVizHome=no&:embed=true" width="100%" height="800px" frameBorder="0"></iframe>'
    
    components.html(embed_code, height=825, scrolling=True)

#data source page

elif page == "Data Sources & Information":
    st.markdown('<h1 class="main-header">📚 Data Sources & Detailed Methodology</h1>', unsafe_allow_html=True)
    st.info("This section provides a transparent, detailed breakdown of our data sources and the precise step-by-step calculations used in the dashboard.")
    st.markdown("---")

    st.markdown("### 🛰️ Primary Data Sources")
    st.write("The credibility of our analysis depends on the quality of our data. We use only verified, publicly available data from the following government and international agencies.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🇮🇳 National Institute of Wind Energy (NIWE)")
        st.write(
            """
            - **Data Used:** Wind speed baselines, turbulence intensity, and national potential maps from the Indian Wind Atlas.
            - **Why it's reliable:** NIWE is the primary government body in India for wind resource assessment, using data from hundreds of ground-based monitoring stations.
            - **[Direct Link: NIWE Wind Resource Maps](https://niwe.res.in/department_wra_maps.php)**
            """
        )
        st.markdown("##### 🇮🇳 Ministry of New & Renewable Energy (MNRE)")
        st.write(
            """
            - **Data Used:** Renewable energy policies, installation targets, and benchmark costs for wind projects.
            - **Why it's reliable:** MNRE is the central ministry responsible for India's renewable energy sector.
            - **[Direct Link: MNRE Wind Portal](https://mnre.gov.in/wind-energy/current-status/)**
            """
        )

    with col2:
        st.markdown("##### 🌍 Global Wind Atlas (GWA 3.0)")
        st.write(
            """
            - **Data Used:** High-resolution Wind Power Density (WPD) and mean wind speed data for specific geographic coordinates.
            - **Why it's reliable:** GWA is an international standard, developed by the Technical University of Denmark (DTU) using advanced meteorological modeling.
            - **[Direct Link: Global Wind Atlas](https://globalwindatlas.info/)**
            """
        )
        st.markdown("##### 🇮🇳 CERC & MPERC")
        st.write(
            """
            - **Data Used:** Electricity tariff rates, and benchmark Operation & Maintenance (O&M) costs.
            - **Why it's reliable:** The Central and State Electricity Regulatory Commissions determine the financial regulations for power projects.
            - **[Direct Link: CERC Tariff Orders](https://cercind.gov.in/orders.html)**
            """
        )
    
    st.markdown("---")
    st.markdown("### ⚙️ Step-by-Step Calculation Breakdown")
    st.write("Here is a detailed explanation of every calculation performed on the main dashboard.")

    with st.expander("Step 1: Capacity Factor Calculation"):
        st.markdown("#### **What is it?**")
        st.write("The Capacity Factor (CF) is a percentage that represents how much electricity a turbine *actually* produces compared to its maximum possible output. A turbine in a very windy location like Indore will have a higher CF than one in a less windy area like Bhopal.")
        
        st.markdown("#### **Why is it calculated this way?**")
        st.write("We use an **empirical formula** derived from NIWE studies specific to Indian wind conditions. It provides a realistic estimate based on two key local factors: average wind speed and turbulence.")
        
        st.markdown("#### **The Formula:**")
        st.latex(r'''
        \text{Capacity Factor} = (0.087 \times V_{avg}) - (\text{Turbulence \%} \times 0.005)
        ''')
        
        st.markdown("#### **Example Calculation (for Indore):**")
        st.write(f"Using Indore's baseline data (Wind Speed = {district_data['Indore']['wind_speed']} m/s, Turbulence = {district_data['Indore']['turbulence']}%):")
        st.code(
            f"CF = (0.087 * {district_data['Indore']['wind_speed']}) - ({district_data['Indore']['turbulence']} * 0.005)\n"
            f"CF = {0.087 * district_data['Indore']['wind_speed']:.3f} - {district_data['Indore']['turbulence'] * 0.005:.3f}\n"
            f"CF = {0.087 * district_data['Indore']['wind_speed'] - district_data['Indore']['turbulence'] * 0.005:.3f} or { (0.087 * district_data['Indore']['wind_speed'] - district_data['Indore']['turbulence'] * 0.005) * 100:.1f}%",
            language='python'
        )

    with st.expander("Step 2: Annual Energy Production (AEP) Calculation"):
        st.markdown("#### **What is it?**")
        st.write("AEP is the total amount of electricity (measured in Megawatt-hours) generated by the wind project in a full year. This is the 'product' that is sold to the grid.")
        
        st.markdown("#### **Why is it important?**")
        st.write("AEP is the foundation for all financial calculations. The more energy produced, the higher the revenue.")
        
        st.markdown("#### **The Formula:**")
        st.latex(r'''
        \text{AEP (MWh)} = \text{Turbine Capacity (MW)} \times 8760 \text{ hours/year} \times \text{Capacity Factor}
        ''')

        st.markdown("#### **Example Calculation (2.5 MW Turbine in Indore):**")
        st.write("Using the Capacity Factor of 0.439 calculated above:")
        st.code(
            # --- DEBUG: Fixed invalid syntax by removing \text{} wrapper ---
            f"AEP = 2.5 MW * 8760 hours * 0.439\n"
            f"AEP = {2.5 * 8760 * 0.439:,.0f} MWh per year",
            language='python'
        )

    with st.expander("Step 3: Financials (Revenue, Costs, Profit)"):
        st.markdown("#### **What are they?**")
        st.write("This is the breakdown of the project's income and expenses over its lifetime.")
        
        st.markdown("#### **How are they calculated?**")
        st.write("We use standard financial formulas based on the user's inputs (turbine cost, tariff rate) and the calculated AEP.")
        
        st.markdown("#### **The Formulas:**")
        st.code(
            """
# Revenue = Energy Produced * Price per unit of energy
Annual Revenue = AEP * Electricity Tariff * 1000

# Investment = Cost per MW * Number of MW
Total Investment = Turbine Cost * Turbine Capacity * 100,000

# O&M = Yearly cost per MW * Number of MW
Annual O&M Cost = O&M Cost * Turbine Capacity * 100,000

# Profit = (Total Revenue over lifetime) - (Initial Investment) - (Total O&M costs over lifetime)
Net Profit = (Annual Revenue * Lifetime) - Total Investment - (Annual O&M Cost * Lifetime)
            """,
            language='python'
        )

    with st.expander("Step 4: Key Performance Indicators (ROI & Payback Period)"):
        st.markdown("#### **What are they?**")
        st.write("ROI (Return on Investment) and Payback Period are standard metrics used to quickly assess the financial attractiveness of an investment.")
        
        st.markdown("#### **Why are they important?**")
        st.write("- **ROI** shows the total profit as a percentage of the initial investment. A higher ROI is better.")
        st.write("- **Payback Period** shows how many years it takes for the project's profits to cover the initial investment. A shorter payback period is better.")
        
        st.markdown("#### **The Formulas:**")
        st.latex(r'''
        \text{ROI} = \left( \frac{\text{Net Profit}}{\text{Total Investment}} \right) \times 100
        ''')
        st.latex(r'''
        \text{Payback Period (years)} = \frac{\text{Total Investment}}{\text{Annual Revenue} - \text{Annual O&M Cost}}
        ''')
# --- ADDED AI ASSISTANT PAGE ---
elif page == "AI Assistant":
    st.markdown('<h1 class="main-header">🤖 AI Assistant for Wind Energy</h1>', unsafe_allow_html=True)
    st.info("Ask a question about wind energy, technology, or policy. Improvements are currently underway.")

    API_URL = "https://api-inference.huggingface.co/models/google/gemma-7b-it" 
    
    if 'HF_TOKEN' in st.secrets:
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
    else:
        st.error("Hugging Face API token not found. Please add it to your Streamlit secrets.")
        st.stop()

    def query_model(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response

    user_prompt = st.text_area("Your question:", placeholder="e.g., How does a wind turbine generate electricity?", height=100)

    if st.button("Get AI Answer"):
        if user_prompt:
            with st.spinner("Querying the AI model... This may take a moment on the first run."):
                try:
                    response = query_model({
                        "inputs": user_prompt,
                        "parameters": {"max_new_tokens": 250}
                    })
                    
                    if response.status_code == 200:
                        output = response.json()
                        if isinstance(output, list) and 'generated_text' in output[0]:
                            generated_text = output[0]['generated_text']
                            answer = generated_text.replace(user_prompt, "").strip()
                            st.markdown("### Answer:")
                            st.write(answer)
                        elif 'error' in output:
                            st.error(f"Model Error: {output['error']}")
                            if 'estimated_time' in output:
                                st.warning(f"The model is still loading. Please try again in about {int(output['estimated_time'])} seconds.")
                        else:
                            st.error("Received an unexpected response from the model.")
                            st.write("Raw model output for debugging:", output)
                    else:
                        st.error(f"Failed to query model. Status code: {response.status_code}")
                        st.write("Response content:", response.text)
                        st.warning("The model may be loading or unavailable. Please try again in a minute.")

                except requests.exceptions.RequestException as e:
                    st.error(f"Network error: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a question.")

# --- YOUR REQUESTED FEEDBACK PAGE ---
elif page == "Feedback & Support":
    st.markdown('<h1 class="main-header">✉️ Feedback & Support</h1>', unsafe_allow_html=True)
    
    # Create tabs for different feedback options
    tab1, tab2 = st.tabs(["Google Form Feedback", "Direct Email Support"])
    
    with tab1:
        st.info("""
        **Please use our Google Form to submit your feedback, report issues, or suggest features.**
        This form allows us to better categorize and track feedback to improve the dashboard.
        """)
        
        # Embedded Google Form
        st.markdown("""
        <div class="google-form-container">
            <h3 style="text-align: center; color: #4fd1c5; margin-bottom: 20px;">Wind Energy Dashboard Feedback Form</h3>
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLScE8gtVyIvhAbV6P4XK8JvMaPS0K4oCW0mpMgEmsTfa6tx5VA/viewform?embedded=true" 
                    frameborder="0" marginheight="0" marginwidth="0">
                Loading…
            </iframe>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        **Note:** If the form isn't loading properly, you can also 
        [open it in a new tab](https://docs.google.com/forms/d/e/1FAIpQLScE8gtVyIvhAbV6P4XK8JvMaPS0K4oCW0mpMgEmsTfa6tx5VA/viewform).
        """)
    
    with tab2:
        st.info("""
        **Alternatively, you can send us feedback directly via email.**
        This option is available if you prefer not to use the Google Form.
        """)
        
        email_config = get_email_config()

        # Check if email credentials are set
        if not email_config['sender_email'] or not email_config['sender_password']:
            st.warning("The email feedback form is currently disabled because email credentials are not configured in the application's secrets.")
        else:
            with st.form(key='feedback_form'):
                name = st.text_input("Your Name", placeholder="Enter your name")
                email = st.text_input("Your Email", placeholder="Enter your email address")
                feedback_type = st.selectbox(
                    "Type of Feedback",
                    ["Bug Report", "Feature Suggestion", "General Question", "Data Inquiry"]
                )
                message = st.text_area("Your Message", placeholder="Please provide detailed feedback here...", height=150)
                
                submit_button = st.form_submit_button(label='Submit Feedback via Email')

                if submit_button:
                    if not name or not email or not message:
                        st.warning("Please fill out all fields before submitting.")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address.")
                    else:
                        with st.spinner("Sending your feedback..."):
                            success = send_feedback_email(name, email, feedback_type, message, email_config)
                            if success:
                                st.success("Thank you! Your feedback has been sent successfully.")
                            else:
                                st.error("Sorry, something went wrong. Please try again later or use the Google Form.")
    
    st.markdown("---")
    st.markdown('<h3 class="section-header">Contact Information</h3>', unsafe_allow_html=True)
    st.markdown(f"""
    If you have any questions or need support, you can reach us at:
    - **Email:** `theroyalprg@gmail.com`
    - **Developer:** Prakarsh
    """)
    
    st.markdown("---")
    st.markdown("""
    <p class="footer">
        © 2025 Wind Energy Analytics Dashboard by Prakarsh | Data Sources: NIWE, MNRE, IMD<br>
        For informational purposes only. Actual project feasibility requires detailed site assessment.
    </p>
    """, unsafe_allow_html=True)
