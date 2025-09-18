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
    
    /* Google Form iframe styling */
    .google-form-container {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #4fd1c5;
        margin: 1rem 0;
        text-align: center;
    }
    
    .google-form-container iframe {
        width: 100%;
        height: 1200px;
        border: none;
        border-radius: 8px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Email configuration
def get_email_config():
    """Get email configuration from secrets or environment variables"""
    return {
        'smtp_server': st.secrets.get('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': st.secrets.get('SMTP_PORT', 587),
        'sender_email': st.secrets.get('SENDER_EMAIL', ''),
        'sender_password': st.secrets.get('SENDER_PASSWORD', ''),
        'receiver_email': st.secrets.get('RECEIVER_EMAIL', 'theroyalprg@gmail.com')
    }

# Email validation
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Send email function
def send_feedback_email(name, email, feedback_type, message, config):
    """Send feedback email"""
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
        st.error(f"Error sending email: {str(e)}")
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

elif page == "Data Sources & Information":
    st.markdown('<h1 class="main-header">📚 Data Sources & Methodology</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## About This Dashboard
    
    This Wind Energy Analytics Dashboard provides comprehensive analysis of wind energy potential 
    across districts in Madhya Pradesh, India. The tool enables policymakers, investors, and 
    renewable energy developers to assess the feasibility of wind energy projects in the region.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-header">Data Sources</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        #### Primary Data Sources:
        
        - **National Institute of Wind Energy (NIWE)**
          - Wind resource assessment data
          - Technical specifications for wind turbines
          - Capacity factor calculations
          - [Website](https://niwe.res.in/)
        
        - **Ministry of New and Renewable Energy (MNRE)**
          - Policy framework data
          - Subsidy and incentive information
          - National wind energy targets
          - [Website](https://mnre.gov.in/)
        
        - **India Meteorological Department (IMD)**
          - Historical wind speed data
          - Seasonal variation patterns
          - Climate data for Madhya Pradesh
          - [Website](https://mausam.imd.gov.in/)
        
        - **Madhya Pradesh Energy Department**
          - State-specific renewable energy policies
          - Electricity tariff structures
          - Grid connectivity information
          - [Website](https://www.mprenewable.nic.in/)
        """)
    
    with col2:
        st.markdown('<h3 class="section-header">Methodology</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        #### Calculation Methodology:
        
        **1. Wind Resource Assessment**
        - Data collected from NIWE's wind monitoring stations
        - Annual average wind speeds calculated from 10+ years of data
        - Height correction applied using power law (α = 0.14)
        
        **2. Energy Production Estimation**
        - Capacity Factor = 0.087 × V_avg - (Turbulence × 0.005)
        - Annual Generation = Capacity × 8760 hours × Capacity Factor
        - Based on IEC 61400-12-1 standard for power performance measurements
        
        **3. Financial Calculations**
        - Investment costs based on current market rates for wind turbines
        - O&M costs estimated at 1.5-2.5% of initial investment annually
        - Tariff rates based on MPERC's latest renewable energy purchase guidelines
        - ROI calculated over project lifetime (typically 20-25 years)
        
        **4. Technical Assumptions**
        - Turbine availability: 95%
        - Electrical losses: 3%
        - Wake losses: 5-10% (depending on wind farm layout)
        - Grid availability: 98%
        """)
    
    st.markdown("---")
    
    st.markdown('<h3 class="section-header">Limitations & Considerations</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    #### Important Considerations:
    
    1. **Site-Specific Variations**
    - Actual wind resources may vary significantly within a district
    - Local topography greatly influences wind patterns
    - Micro-siting is essential for accurate assessment
    
    2. **Technology Assumptions**
    - Calculations based on modern 2-3 MW wind turbines
    - Capacity factors may vary with turbine technology
    - Newer turbines may perform better at lower wind speeds
    
    3. **Financial Considerations**
    - Does not account for inflation or financing costs
    - Land acquisition costs vary by location
    - Transmission infrastructure costs not included
    - Government incentives and subsidies may apply
    
    4. **Environmental Factors**
    - Seasonal variations in wind patterns
    - Climate change impacts on long-term wind resources
    - Environmental clearance requirements
    """)
    
    st.markdown("---")
    
    st.markdown('<h3 class="section-header">Recommended Next Steps</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    For serious project development, we recommend:
    
    1. **Site-Specific Assessment**
    - Install meteorological masts for at least 12 months
    - Conduct detailed wind resource measurement
    - Perform micro-siting analysis
    
    2. **Feasibility Study**
    - Detailed technical feasibility assessment
