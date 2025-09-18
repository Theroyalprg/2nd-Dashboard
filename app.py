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
import requests # <-- Added for AI Assistant

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

# Navigation
page = st.sidebar.selectbox(
    "Navigate", 
    ["Wind Dashboard", "Data Sources & Information", "AI Assistant", "Feedback & Support"]
)

# District data
district_data = {
    "Bhopal": {"wind_speed": 4.2, "potential": "Low", "turbulence": 12.5, "lat": 23.2599, "lon": 77.4126, "source": "NIWE", "source_url": "https://niwe.res.in/", "wind_potential": 8.2},
    "Indore": {"wind_speed": 5.7, "potential": "Medium", "turbulence": 11.2, "lat": 22.7196, "lon": 75.8577, "source": "MNRE", "source_url": "https://mnre.gov.in/", "wind_potential": 14.5},
    "Jabalpur": {"wind_speed": 4.8, "potential": "Low-Medium", "turbulence": 13.0, "lat": 23.1815, "lon": 79.9864, "source": "IMD", "source_url": "https://mausam.imd.gov.in/", "wind_potential": 9.8},
    "Ujjain": {"wind_speed": 5.2, "potential": "Medium", "turbulence": 11.8, "lat": 23.1793, "lon": 75.7849, "source": "NIWE", "source_url": "https://niwe.res.in/", "wind_potential": 12.3}
}

if page == "Wind Dashboard":
    st.markdown('<h1 class="main-header">🌬️ Wind Energy Analytics Dashboard - Madhya Pradesh</h1>', unsafe_allow_html=True)
    st.info("This dashboard provides wind energy potential analysis. Adjust parameters in the sidebar to simulate project scenarios.")

    with st.sidebar:
        st.header("📍 Select District")
        selected_district = st.selectbox("", list(district_data.keys()), index=1)
        st.markdown('<h3 class="section-header">Project Parameters</h3>', unsafe_allow_html=True)
        years = st.slider("Project Lifetime (Years)", 1, 25, 15)
        capacity_mw = st.number_input("Turbine Capacity (MW)", 0.5, 10.0, 2.5, step=0.5)
        st.markdown('<h3 class="section-header">Wind Conditions</h3>', unsafe_allow_html=True)
        avg_wind_speed = st.slider("Average Wind Speed (m/s)", 3.0, 12.0, district_data[selected_district]["wind_speed"], step=0.1)
        turbulence = st.slider("Turbulence Intensity (%)", 5.0, 25.0, district_data[selected_district]["turbulence"], step=0.1)
        st.markdown('<h3 class="section-header">Financial Parameters</h3>', unsafe_allow_html=True)
        turbine_cost = st.number_input("Turbine Cost (₹ lakhs/MW)", 500, 1000, 700)
        om_cost = st.number_input("O&M Cost (₹ lakhs/MW/year)", 10, 50, 30)
        tariff_rate = st.number_input("Electricity Tariff (₹/kWh)", 3.0, 8.0, 5.2, step=0.1)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f'<h3 class="section-header">District Overview: {selected_district}</h3>', unsafe_allow_html=True)
        map_center = [district_data[selected_district]["lat"], district_data[selected_district]["lon"]]
        m = folium.Map(location=map_center, zoom_start=9, tiles="CartoDB dark_matter")
        folium.Marker(map_center, popup=f"{selected_district}", tooltip=f"{selected_district}").add_to(m)
        folium_static(m, width=700, height=300)
        
        st.markdown('<h3 class="section-header">Calculations</h3>', unsafe_allow_html=True)
        capacity_factor = max(0.087 * avg_wind_speed - (turbulence * 0.005), 0)
        estimated_annual_generation = capacity_mw * 8760 * capacity_factor
        annual_revenue = estimated_annual_generation * tariff_rate * 1000
        total_investment = capacity_mw * turbine_cost * 100000
        annual_om_cost = capacity_mw * om_cost * 100000
        annual_cash_flow = annual_revenue - annual_om_cost
        net_profit = (annual_revenue * years) - total_investment - (annual_om_cost * years)
        roi = (net_profit / total_investment) * 100 if total_investment > 0 else 0
        payback_period = total_investment / annual_cash_flow if annual_cash_flow > 0 else float('inf')
        
        years_range = np.arange(1, years + 1)
        cumulative_cash_flow = [annual_cash_flow * y - total_investment for y in years_range]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.style.use('dark_background')
        ax.plot(years_range, cumulative_cash_flow, marker="^", color="#4fd1c5")
        ax.axhline(y=0, color="#fc8181", linestyle="--")
        ax.set_title("Project Cash Flow Over Time", color='white')
        ax.set_xlabel("Years", color='white')
        ax.set_ylabel("Net Cash Flow (₹)", color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    with col2:
        st.markdown('<h3 class="section-header">Key Performance Indicators</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">Capacity Factor</p><p class="metric-value">{capacity_factor:.1%}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">Annual Energy (MWh)</p><p class="metric-value">{estimated_annual_generation:,.0f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">Total Investment</p><p class="metric-value">₹{total_investment:,.0f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">Net Profit</p><p class="metric-value">₹{net_profit:,.0f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">ROI</p><p class="metric-value">{roi:.1f}%</p></div>', unsafe_allow_html=True)
        payback_display = f"{payback_period:.1f} years" if payback_period != float('inf') else "> Lifetime"
        st.markdown(f'<div class="metric-card"><p class="metric-label">Payback Period</p><p class="metric-value">{payback_display}</p></div>', unsafe_allow_html=True)

elif page == "Data Sources & Information":
    st.markdown('<h1 class="main-header">📚 Data Sources & Methodology</h1>', unsafe_allow_html=True)
    st.markdown("This dashboard provides a preliminary techno-economic analysis. A bankable feasibility report requires site-specific, high-resolution data collection.")
    st.markdown("---")
    st.markdown('<h3 class="section-header">🔬 Detailed Data Sources</h3>', unsafe_allow_html=True)
    st.markdown(r"""
    - **National Institute of Wind Energy (NIWE):** Foundational wind speed and potential data. ([Source](https://niwe.res.in/department_wra_maps.php))
    - **Global Wind Atlas (GWA 3.0):** High-resolution data for Wind Power Density (WPD). ([Source](https://globalwindatlas.info))
    - **Ministry of New and Renewable Energy (MNRE):** Overarching policy framework and national targets. ([Source](https://mnre.gov.in/wind-energy/current-status/))
    """)
    st.markdown("---")
    st.markdown('<h3 class="section-header">⚙️ Detailed Methodology</h3>', unsafe_allow_html=True)
    st.markdown(r"""
    **1. Wind Resource Assessment:** Wind speed is extrapolated to hub height using the Wind Profile Power Law: $V_2 = V_1 \left( \frac{H_2}{H_1} \right)^\alpha$. We assume a wind shear coefficient ($\alpha$) of 0.2.
    **2. Annual Energy Production (AEP):** Calculated as $AEP = \text{Capacity} \times 8760 \times \text{CUF}$. The Capacity Utilization Factor (CUF) is a net value after accounting for losses (availability, wake effects, electrical, etc.).
    **3. Financial Viability:** The industry standard is the **Levelized Cost of Energy (LCOE)**, which represents the break-even price per unit of electricity over the project's lifetime.
    """)

elif page == "AI Assistant":
    st.markdown('<h1 class="main-header">🤖 AI Assistant for Wind Energy</h1>', unsafe_allow_html=True)
    st.info("Ask a question about wind energy, technology, or policy. This assistant uses a free, open-source model from Hugging Face.")

    # --- Hugging Face Configuration ---
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    if 'HF_TOKEN' in st.secrets:
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
    else:
        st.error("Hugging Face API token not found. Please add it to your Streamlit secrets.")
        st.stop()

    def query_model(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    # --- End Configuration ---

    user_prompt = st.text_area("Your question:", placeholder="e.g., How does a wind turbine generate electricity?", height=100)

    if st.button("Get AI Answer"):
        if user_prompt:
            with st.spinner("The free model is warming up... This may take 20-30 seconds on the first run."):
                try:
                    output = query_model({
                        "inputs": f"Question: {user_prompt}\n\nAnswer:",
                        "parameters": {"max_new_tokens": 250}
                    })
                    
                    if isinstance(output, list) and 'generated_text' in output[0]:
                        generated_text = output[0]['generated_text']
                        # Clean up the response
                        if "Answer:" in generated_text:
                            answer = generated_text.split("Answer:")[1].strip()
                        else:
                            answer = generated_text.replace(f"Question: {user_prompt}\n\n", "").strip()

                        st.markdown("### Answer:")
                        st.write(answer)
                    else:
                        st.error("Failed to get a valid response from the model. It might be overloaded or still loading.")
                        st.write("Raw model output for debugging:", output)

                except requests.exceptions.RequestException as e:
                    st.error(f"Network error: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a question.")

elif page == "Feedback & Support":
    st.markdown('<h1 class="main-header">📬 Feedback & Support</h1>', unsafe_allow_html=True)
    st.info("We value your feedback! Please use the form below to report issues, suggest features, or ask questions.")
    
    email_config = get_email_config()

    st.markdown('<div class="feedback-form">', unsafe_allow_html=True)
    with st.form(key="feedback_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        feedback_type = st.selectbox("Type of Feedback", ["Bug Report", "Feature Request", "General Question"])
        message = st.text_area("Your Message", height=150)
        submit_button = st.form_submit_button(label="Submit Feedback")

    if submit_button:
        if not all([name, email, message]) or not is_valid_email(email):
            st.warning("Please fill out all fields with a valid email before submitting.")
        else:
            with st.spinner("Sending..."):
                if send_feedback_email(name, email, feedback_type, message, email_config):
                    st.success("Thank you for your feedback!")
                # Error message is handled within the send_email function

    st.markdown('</div>', unsafe_allow_html=True)
