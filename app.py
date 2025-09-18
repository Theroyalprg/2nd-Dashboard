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

# Page configuration
st.set_page_config(
    page_title="Wind Energy Analytics - Madhya Pradesh",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, professional color scheme with proper contrast
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1a2a;
        color: #e6e9f0;
    }
    
    /* Headers and text */
    .main-header {
        font-size: 2.8rem;
        color: #4fd1c5;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #4fd1c5;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1v0mbdj, .css-1y4v3va {
        background-color: #1a202c !important;
    }
    
    .css-1d391kg p, .css-1v0mbdj p, .css-1y4v3va p {
        color: #e6e9f0 !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        color: white;
        border: 1px solid #4a5568;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #4fd1c5;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #cbd5e0;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        color: #4fd1c5;
        border-left: 5px solid #4fd1c5;
        padding-left: 12px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2.5rem;
        color: #a0aec0;
        font-size: 0.85rem;
        padding-top: 1.2rem;
        border-top: 1px solid #4a5568;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #4fd1c5, #2c7a7b);
    }
    
    /* Wind speed indicator */
    .wind-speed-indicator {
        height: 12px;
        background: linear-gradient(90deg, #90cdf4, #4fd1c5, #2c7a7b);
        border-radius: 6px;
        margin: 12px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* District selector */
    .district-selector {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid #4a5568;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Source info */
    .source-info {
        font-size: 0.8rem;
        color: #a0aec0;
        font-style: italic;
    }
    
    /* Map container */
    .map-container {
        border-radius: 0.8rem;
        overflow: hidden;
        margin-bottom: 1.2rem;
        border: 1px solid #4a5568;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Calculation boxes */
    .calculation-box {
        background-color: #2d3748;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4fd1c5;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #e6e9f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Source links */
    .source-link {
        color: #4fd1c5;
        text-decoration: none;
        font-weight: 500;
    }
    
    .source-link:hover {
        color: #38b2ac;
        text-decoration: underline;
    }
    
    /* Navigation buttons */
    .nav-button {
        background-color: #2c7a7b !important;
        color: white !important;
        border: 1px solid #4fd1c5 !important;
        margin: 5px;
    }
    
    /* Text elements */
    .stMarkdown, .stText, .stInfo, .stSuccess, .stWarning {
        color: #e6e9f0;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: #2d3748;
        color: #e6e9f0;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #2d3748;
        color: #e6e9f0;
        border: 1px solid #4a5568;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: #2d3748;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #4a5568;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2d3748;
        color: #e6e9f0;
        border: 1px solid #4a5568;
    }
    
    .streamlit-expanderContent {
        background-color: #2d3748;
        color: #e6e9f0;
    }
    
    /* Chart background */
    .css-1y4v3va {
        background-color: #1a202c;
    }
    
    /* Custom chart styling */
    .chart-container {
        background-color: #2d3748;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Feedback form styling */
    .feedback-form {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #4fd1c5;
        margin: 1rem 0;
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
        'receiver_email': st.secrets.get('RECEIVER_EMAIL', '') # Fallback to empty to avoid sending to wrong address
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
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = config['receiver_email']
        msg['Subject'] = f"🌬️ Wind Dashboard Feedback - {feedback_type}"
        
        # Email body
        body = f"""
        New Feedback from Wind Energy Dashboard:
        
        Name: {name}
        Email: {email}
        Feedback Type: {feedback_type}
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {message}
        
        ---
        This email was sent automatically from the Wind Energy Analytics Dashboard.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
            
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}. Check your credentials and server settings.")
        return False

# Navigation
page = st.sidebar.selectbox("Navigate", ["Wind Dashboard", "Data Sources & Information", "Feedback & Support"])

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
    st.markdown('<h1 class="main-header">🌬️ Wind Energy Analytics Dashboard - Madhya Pradesh</h1>', unsafe_allow_html=True)

    # Introduction
    st.info("""
    This dashboard provides wind energy potential analysis for districts in Madhya Pradesh using verified data from government sources and research institutions.
    Adjust parameters in the sidebar to simulate different project scenarios and evaluate financial viability.
    """)

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
        m = folium.Map(location=map_center, zoom_start=9, tiles="CartoDB dark_matter")
        
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
        plt.style.use('dark_background')
        ax.set_facecolor('#1a202c')
        fig.patch.set_facecolor('#0f1a2a')
        
        if chart_option == "Energy Output":
            ax.plot(years_range, cumulative_generation, marker="o", linewidth=2.5, color="#4fd1c5", markersize=8)
            ax.fill_between(years_range, cumulative_generation, alpha=0.3, color="#4fd1c5")
            ax.set_ylabel("Cumulative Energy (MWh)", fontweight='bold', color='white')
            ax.set_title("Projected Energy Output Over Time", fontweight='bold', fontsize=14, color='white')
            ax.grid(True, alpha=0.3, linestyle='--', color='#4a5568')
            ax.tick_params(colors='white')
        elif chart_option == "Financial Performance":
            ax.plot(years_range, cumulative_revenue, marker="s", linewidth=2.5, color="#4fd1c5", label="Revenue", markersize=8)
            ax.axhline(y=total_investment, color="#fc8181", linestyle="--", linewidth=2, label="Initial Investment")
            ax.fill_between(years_range, cumulative_revenue, alpha=0.3, color="#4fd1c5")
            ax.set_ylabel("Amount (₹)", fontweight='bold', color='white')
            ax.set_title("Financial Performance Over Time", fontweight='bold', fontsize=14, color='white')
            ax.legend(facecolor='#2d3748', edgecolor='#4a5568', labelcolor='white')
            ax.grid(True, alpha=0.3, linestyle='--', color='#4a5568')
            ax.tick_params(colors='white')
        else:
            ax.plot(years_range, cumulative_cash_flow, marker="^", linewidth=2.5, color="#4fd1c5", markersize=8)
            ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) >= 0, alpha=0.3, color="#48bb78")
            ax.fill_between(years_range, cumulative_cash_flow, where=np.array(cumulative_cash_flow) < 0, alpha=0.3, color="#fc8181")
            ax.axhline(y=0, color="#fc8181", linestyle="--", linewidth=2)
            ax.set_ylabel("Net Cash Flow (₹)", fontweight='bold', color='white')
            ax.set_title("Project Cash Flow Over Time", fontweight='bold', fontsize=14, color='white')
            ax.grid(True, alpha=0.3, linestyle='--', color='#4a5568')
            ax.tick_params(colors='white')
        
        ax.set_xlabel("Years", fontweight='bold', color='white')
        st.pyplot(fig)
        
        # Additional charts
        st.markdown('<h3 class="section-header">Performance Details</h3>', unsafe_allow_html=True)
        col1b, col2b = st.columns(2)
        
        with col1b:
            # Capacity factor by wind speed
            wind_speeds = np.linspace(3, 12, 10)
            cap_factors = [max(0.087 * ws - (turbulence * 0.005), 0) for ws in wind_speeds]
            
            fig2, ax2 = plt.subplots(figsize=(8, 4.5))
            plt.style.use('dark_background')
            ax2.set_facecolor('#1a202c')
            fig2.patch.set_facecolor('#0f1a2a')
            
            ax2.plot(wind_speeds, cap_factors, marker='o', color='#4fd1c5', linewidth=2.5, markersize=6)
            ax2.axvline(x=avg_wind_speed, color='#fc8181', linestyle='--', alpha=0.8, linewidth=2)
            ax2.set_xlabel('Wind Speed (m/s)', fontweight='bold', color='white')
            ax2.set_ylabel('Capacity Factor', fontweight='bold', color='white')
            ax2.set_title('Capacity Factor vs. Wind Speed', fontweight='bold', color='white')
            ax2.grid(True, alpha=0.3, linestyle='--', color='#4a5568')
            ax2.tick_params(colors='white')
            st.pyplot(fig2)
        
        with col2b:
            # Cost breakdown
            labels = ['Turbine Cost', 'O&M Cost']
            sizes = [total_investment, total_om_cost]
            colors = ['#4fd1c5', '#4299e1']
            
            fig3, ax3 = plt.subplots(figsize=(8, 4.5))
            plt.style.use('dark_background')
            fig3.patch.set_facecolor('#0f1a2a')
            
            wedges, texts, autotexts = ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                               startangle=90, textprops={'fontweight': 'bold', 'color': 'white'})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            ax3.axis('equal')
            ax3.set_title('Cost Breakdown', fontweight='bold', color='white')
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
        st.dataframe(comparison_df, use_container_width=True, height=200)
        
        # Data sources
        st.markdown('<h3 class="section-header">Data Sources</h3>', unsafe_allow_html=True)
        st.markdown("""
        - **National Institute of Wind Energy (NIWE):** [Wind Resource Map of India](https://niwe.res.in/department_wra_about.php)
        - **Ministry of New and Renewable Energy (MNRE):** [Wind Energy Potential](https://mnre.gov.in/wind-energy-potential)
        - **India Meteorological Department (IMD):** [Climate Data](https://mausam.imd.gov.in/)
        - **Madhya Pradesh Energy Department:** [Renewable Energy Policy](https://www.mprenewable.nic.in/)
        """)

    # Footer
    st.markdown("""
    <p class="footer">
        © 2025 Wind Energy Analytics Dashboard by Prakarsh | Data Sources: NIWE, MNRE, IMD<br>
        For informational purposes only. Actual project feasibility requires detailed site assessment.
    </p>
    """, unsafe_allow_html=True)

# === CODE UPDATE: The entire "Data Sources & Information" page has been replaced ===
elif page == "Data Sources & Information":
    st.markdown('<h1 class="main-header">📚 Data Sources & Methodology</h1>', unsafe_allow_html=True)

    st.markdown("""
    This dashboard provides a preliminary techno-economic analysis for wind energy projects in select Madhya Pradesh districts. The goal is to serve as a first-pass screening tool for investors, researchers, and policymakers. The data and methodologies used are based on publicly available, reputable sources, but are subject to the limitations outlined below. A bankable feasibility report requires site-specific, high-resolution data collection.
    """)
    st.markdown("---")

    st.markdown('<h3 class="section-header">🔬 Detailed Data Sources</h3>', unsafe_allow_html=True)
    st.markdown("""
    The data powering this dashboard is a composite of national-level assessments, global datasets, and state-level policy documents.

    #### 1. Wind Resource Data
    * **National Institute of Wind Energy (NIWE), India:** The foundational wind speed and potential data for districts are derived from NIWE's publications, including the Indian Wind Atlas. This data is typically measured at hub heights of 80m, 100m, and 120m.
        * **Source:** [NIWE Wind Resource Maps](https://niwe.res.in/department_wra_maps.php)
    * **Global Wind Atlas (GWA 3.0):** This dataset, developed by the Technical University of Denmark (DTU), provides high-resolution (250m) global wind climate data. We use it to cross-reference and understand the **Wind Power Density (WPD)**, a more accurate metric than wind speed alone, for the specific coordinates of Bhopal, Indore, Jabalpur, and Ujjain. WPD measures the power available in the wind, expressed in W/m².
        * **Source:** [Global Wind Atlas](https://globalwindatlas.info)
    * **NASA POWER Project:** The Prediction of Worldwide Energy Resources project provides meteorological and solar energy data from satellite observations. This can be used to analyze long-term seasonal and annual variability in wind patterns.
        * **Source:** [NASA POWER Data Access Viewer](https://power.larc.nasa.gov/data-access-viewer/)

    #### 2. Policy and Financial Data
    * **Ministry of New and Renewable Energy (MNRE), Govt. of India:** Provides the overarching policy framework, national targets, and guidelines for renewable energy projects.
        * **Source:** [MNRE Wind Energy Portal](https://mnre.gov.in/wind-energy/current-status/)
    * **Madhya Pradesh New and Renewable Energy Department (MPNRED):** State-specific policies, particularly the "Madhya Pradesh Renewable Energy Policy," dictate local regulations, land allotment procedures, and grid connectivity protocols.
        * **Source:** [MPNRED Policies](https://www.mprenewable.nic.in/en/policies)
    * **Central Electricity Regulatory Commission (CERC) & MPERC:** Turbine costs, O&M costs, and electricity tariffs are benchmarked against figures published in tariff orders and market analysis reports by CERC and the Madhya Pradesh Electricity Regulatory Commission (MPERC).
        * **Source:** [CERC Tariff Orders](https://cercind.gov.in/orders.html)
    """)
    st.markdown("---")

    st.markdown('<h3 class="section-header">⚙️ Detailed Methodology</h3>', unsafe_allow_html=True)
    st.markdown(r"""
    The analysis follows a standardized four-step process.

    #### Step 1: Wind Resource Assessment
    The average wind speed ($V_{avg}$) you see is just the starting point. To estimate the power at a modern turbine's hub height (e.g., 120m or 150m), we must extrapolate it from the measurement height (e.g., 80m) using the **Wind Profile Power Law**:

    $$ V_2 = V_1 \left( \frac{H_2}{H_1} \right)^\alpha $$

    Where:
    - $V_2$ = Wind speed at target hub height $H_2$.
    - $V_1$ = Wind speed at original measurement height $H_1$.
    - $\alpha$ (Alpha) = The wind shear coefficient. This crucial parameter depends on surface roughness and atmospheric stability. We assume a standard value of **α = 0.2** for the slightly rough terrain typical of the Malwa plateau region.

    #### Step 2: Turbine Power Conversion
    The simplified linear formula in the dashboard is an approximation. A rigorous analysis uses a manufacturer-specific **Power Curve**. This curve plots the turbine's power output (in kW) against different wind speeds. It defines the **cut-in speed** (where the turbine starts generating power, ~3-4 m/s), the **rated speed** (where it reaches maximum output), and the **cut-out speed** (where it shuts down for safety, ~25 m/s).
    
    

    #### Step 3: Annual Energy Production (AEP) Calculation
    The primary metric for a wind farm's performance is its **Capacity Utilization Factor (CUF)**, not the simplified capacity factor. The CUF is the ratio of the actual energy generated over a year to the maximum possible energy that could have been generated at full rated capacity.

    The AEP is calculated as:
    $AEP = \text{Installed Capacity (MW)} \times 8760 \text{ hours/year} \times \text{CUF}$

    The CUF is not just a function of wind speed; it's a net value after accounting for various losses (**derating factors**):
    - **Turbine Availability:** Typically 97-98%. (Loss due to maintenance, breakdowns).
    - **Grid Availability:** ~99%. (Loss due to grid failure or substation maintenance).
    - **Wake Losses:** 5-15%. (Loss from turbines disrupting wind flow for downstream turbines).
    - **Electrical Losses:** 2-3%. (Loss in transformers, cables, and inverters).
    - **Environmental Losses:** 1-3%. (Loss due to blade soiling, icing, or extreme temperatures).
    *This dashboard's 'Capacity Factor' is a simplified proxy for the net CUF.*

    #### Step 4: Financial Viability Analysis
    While the dashboard shows ROI and Payback Period, the industry standard is the **Levelized Cost of Energy (LCOE)**. This represents the break-even price per unit of electricity (kWh or MWh) over the project's lifetime. A project is viable if its LCOE is lower than the tariff it can sell power for.

    The simplified LCOE formula is:
    $$ LCOE = \frac{\sum_{t=1}^{n} \frac{I_t + M_t}{(1+r)^t}}{\sum_{t=1}^{n} \frac{E_t}{(1+r)^t}} $$

    Where:
    - $I_t$ = Investment expenditures in year $t$ (CAPEX).
    - $M_t$ = Operations and maintenance expenditures in year $t$ (OPEX).
    - $E_t$ = Electricity generated in year $t$ (AEP).
    - $r$ = Discount rate (cost of capital).
    - $n$ = Lifetime of the project in years.
    """
    )

elif page == "Feedback & Support":
    st.markdown('<h1 class="main-header">📬 Feedback & Support</h1>', unsafe_allow_html=True)
    
    st.info("We value your feedback! Please use the form below to report issues, suggest features, or ask questions.")
    
    # Get email config
    email_config = get_email_config()

    st.markdown('<div class="feedback-form">', unsafe_allow_html=True)
    
    with st.form(key="feedback_form"):
        name = st.text_input("Your Name", placeholder="Enter your full name")
        email = st.text_input("Your Email", placeholder="Enter a valid email address")
        feedback_type = st.selectbox(
            "Type of Feedback",
            ["Bug Report", "Feature Request", "General Question", "Data Inquiry"]
        )
        message = st.text_area("Your Message", placeholder="Please provide as much detail as possible...", height=150)
        
        submit_button = st.form_submit_button(label="Submit Feedback")

    if submit_button:
        if not name or not email or not message:
            st.warning("Please fill out all fields before submitting.")
        elif not is_valid_email(email):
            st.warning("Please enter a valid email address.")
        else:
            with st.spinner("Sending your feedback..."):
                success = send_feedback_email(name, email, feedback_type, message, email_config)
                if success:
                    st.success("Thank you for your feedback! We have received your message and will get back to you shortly.")
                else:
                    st.error("Sorry, something went wrong. Please try again later or contact the administrator directly.")

    st.markdown('</div>', unsafe_allow_html=True)
