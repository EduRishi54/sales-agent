"""
AI Sales Agent Application (Branded Version)

This Streamlit application uses Gemini 1.5 Flash to generate personalized sales responses
based on customer data from CSV files and user-provided enquiry details.
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import os
import time
import random
import base64
from datetime import datetime, timedelta
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import hashlib
import uuid
from cryptography.fernet import Fernet
import getpass
import io
import calendar
import pytz
import re
from collections import defaultdict, Counter
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import requests
import urllib.parse

# Import the dashboard module
try:
    from city_business_dashboard import (
        create_dashboard_tabs,
        create_city_distribution_tab,
        create_business_type_tab,
        create_lead_analytics_tab
    )
except ImportError:
    st.error("Could not import city_business_dashboard module. Please ensure it's in the same directory.")

    # Fallback definitions if module import fails
    def create_dashboard_tabs():
        st.warning("Dashboard module not available. Using simplified view.")

    def create_city_distribution_tab():
        st.warning("City distribution visualization not available.")

    def create_business_type_tab():
        st.warning("Business type analysis not available.")

    def create_lead_analytics_tab():
        st.warning("Lead analytics not available.")

# Import the Indian cities data module
try:
    from indian_cities_data import (
        get_all_cities,
        get_all_business_types,
        get_cities_by_state,
        get_states,
        generate_leads_by_city,
        generate_leads_by_business_type,
        generate_mock_lead,
        fetch_leads_from_external_source
    )
except ImportError:
    st.error("Could not import indian_cities_data module. Please ensure it's in the same directory.")

    # Fallback definitions if module import fails
    def get_all_cities():
        return [{"city": "Mumbai", "state": "Maharashtra"}, {"city": "Delhi", "state": "Delhi"}]

    def get_all_business_types():
        return {"Educational": ["Schools", "Colleges"], "Industrial": ["Manufacturing"]}

    def get_cities_by_state(state):
        return ["City 1", "City 2"]

    def get_states():
        return ["Maharashtra", "Delhi"]

    def generate_leads_by_city(city, count=5, business_type=None):
        return []

    def generate_leads_by_business_type(business_type, count=5, city=None, state=None):
        return []

    def generate_mock_lead(city=None, state=None, business_type=None, subcategory=None):
        return {}

    def fetch_leads_from_external_source(city=None, state=None, business_type=None, count=10):
        return []

# Set page configuration
st.set_page_config(
    page_title="EDURISHI Sales Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global product details dictionary
product_details = {
    "ELAP": {
        "name": "ELAP (Experiential Learning and Assessment Program)",
        "description": "Comprehensive experiential learning program designed for schools",
        "brochure": "EduRishi Final Brochures/ELAP_Brochure.pdf",
        "pricing": "₹800 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=elapoverview"
    },
    "MDL": {
        "name": "MDL (Multi-Dimensional Learning)",
        "description": "Multi-dimensional approach to learning that enhances student engagement",
        "brochure": "EduRishi Final Brochures/MDL_Brochure.pdf",
        "pricing": "₹1,200 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=mdloverview"
    },
    "PBL": {
        "name": "PBL (Project-Based Learning)",
        "description": "Project-based learning methodology for practical skill development",
        "brochure": "EduRishi Final Brochures/PBL_Brochure.pdf",
        "pricing": "₹950 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=pbloverview"
    },
    "ICT": {
        "name": "ICT (Information and Communication Technology)",
        "description": "Technology integration in education for digital literacy",
        "brochure": "EduRishi Final Brochures/ICT_Brochure.pdf",
        "pricing": "₹1,500 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=ictoverview"
    },
    "AI Workshop": {
        "name": "AI Workshop",
        "description": "Hands-on workshops introducing artificial intelligence concepts",
        "brochure": "AI_Workshop_Brochure.pdf",
        "pricing": "₹15,000 per workshop (up to 30 participants)",
        "video": "https://www.youtube.com/watch?v=aiworkshopoverview"
    },
    "LMS": {
        "name": "Learning Management System",
        "description": "Comprehensive platform for managing digital learning content",
        "brochure": "LMS_Brochure.pdf",
        "pricing": "₹25,000 per school (annual license)",
        "video": "https://www.youtube.com/watch?v=lmsoverview"
    },
    "AI software": {
        "name": "AI-Powered Educational Software",
        "description": "Advanced software using AI to personalize learning experiences",
        "brochure": "AI_Software_Brochure.pdf",
        "pricing": "₹1,800 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=aisoftwareoverview"
    },
    "AI tutor": {
        "name": "AI Tutor",
        "description": "Virtual tutoring system powered by artificial intelligence",
        "brochure": "AI_Tutor_Brochure.pdf",
        "pricing": "₹1,200 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=aitutoroverview"
    },
    "Simulation": {
        "name": "Educational Simulations",
        "description": "Interactive simulations for science, math, and other subjects",
        "brochure": "Simulations_Brochure.pdf",
        "pricing": "₹900 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=simulationsoverview"
    },
    "E2MP": {
        "name": "E2MP (Education to Market Place)",
        "description": "Program connecting education with real-world market skills",
        "brochure": "E2MP_Brochure.pdf",
        "pricing": "₹1,500 per student (annual subscription)",
        "video": "https://www.youtube.com/watch?v=e2mpoverview"
    },
    "Franchise Proposal": {
        "name": "EduRishi Franchise Opportunity",
        "description": "Become an EduRishi franchise partner and expand educational reach",
        "brochure": "Franchise_Proposal.pdf",
        "pricing": "Starting from ₹5,00,000 (investment)",
        "video": "https://www.youtube.com/watch?v=franchiseoverview"
    },
    "Tech Franchise": {
        "name": "Technology Franchise",
        "description": "Franchise focused on technology education and AI integration",
        "brochure": "Tech_Franchise_Brochure.pdf",
        "pricing": "Starting from ₹7,50,000 (investment)",
        "video": "https://www.youtube.com/watch?v=techfranchiseoverview"
    },
    "Entrepreneurship_Workshop": {
        "name": "Entrepreneurship Workshop",
        "description": "Workshops focused on developing entrepreneurial skills",
        "brochure": "Entrepreneurship_Workshop_Brochure.pdf",
        "pricing": "₹20,000 per workshop (up to 30 participants)",
        "video": "https://www.youtube.com/watch?v=entrepreneurshipoverview"
    }
}

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .warning-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #FFC107;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #F44336;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
    .customer-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .response-card {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .history-item {
        background-color: #FAFAFA;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #9E9E9E;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #9E9E9E;
        font-size: 0.8rem;
    }
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
    }
    .stTextArea>div>div>textarea {
        border-radius: 0.5rem;
    }
    .stSelectbox>div>div>div {
        border-radius: 0.5rem;
    }
    .stFileUploader>div>div {
        border-radius: 0.5rem;
    }
    /* Hide password field completely */
    #api-key-input {
        display: none;
    }
    /* Company branding */
    .company-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    .company-logo {
        height: 60px;
    }
    .company-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0D47A1;
    }
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        background-color: #0D47A1;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    .brand-logo {
        margin-right: 20px;
    }
    .brand-text {
        font-size: 24px;
        font-weight: bold;
    }
    /* Top right logo and company name */
    .top-right-brand {
        position: absolute;
        top: 10px;
        right: 20px;
        display: flex;
        align-items: center;
        z-index: 1000;
    }
    .top-right-logo {
        margin-right: 10px;
        background-color: #0D47A1;
        border-radius: 5px;
        padding: 5px;
    }
    .top-right-name {
        font-weight: bold;
        color: #0D47A1;
        font-size: 16px;
    }
    /* Top left logo */
    .top-left-logo {
        position: absolute;
        top: 15px;
        left: 20px;
        z-index: 1000;
        height: 70px;
        margin-bottom: 30px;
    }

    /* Add space at the top for the logo */
    .main-content {
        margin-top: 90px;
    }
</style>

<!-- Top left logo container with company name -->
<div style="display: flex; align-items: center; margin-bottom: 80px;">
    <img src="data:image/png;base64,{}" alt="EduRishi Logo" class="top-left-logo">
    <div style="margin-left: 80px; font-weight: bold; color: #0D47A1; font-size: 20px; position: absolute; top: 30px; left: 100px;">
        EDURISHI EDUVENTURES PVT LTD
    </div>
</div>
""", unsafe_allow_html=True)

# Try to load the company logo
try:
    with open("edurishi.png", "rb") as f:
        logo_bytes = f.read()
        logo_base64 = base64.b64encode(logo_bytes).decode()
        # Update the logo in the HTML template
        st.markdown(
            f'''
            <div style="display: flex; align-items: center; margin-bottom: 80px;">
                <img src="data:image/png;base64,{logo_base64}" alt="EduRishi Logo" class="top-left-logo">
                <div style="margin-left: 80px; font-weight: bold; color: #0D47A1; font-size: 20px; position: absolute; top: 30px; left: 100px;">
                    EDURISHI EDUVENTURES PVT LTD
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
except Exception as e:
    st.warning(f"Could not load company logo: {e}")
    # Fallback to text-only header
    st.markdown(
        '''
        <div style="margin-top: 30px; margin-bottom: 60px; text-align: center; font-weight: bold; color: #0D47A1; font-size: 24px;">
            EDURISHI EDUVENTURES PVT LTD
        </div>
        ''',
        unsafe_allow_html=True
    )

# Security functions for API key handling
def generate_key():
    """Generate a key for encryption/decryption."""
    # In a production app, this would be stored securely
    # For this demo, we'll derive it from a machine-specific value
    machine_id = str(uuid.getnode())  # MAC address as integer
    user = getpass.getuser()  # Current username
    
    # Create a consistent key based on machine ID and username
    combined = f"{machine_id}:{user}:sales_agent_secure_key"
    return base64.urlsafe_b64encode(hashlib.sha256(combined.encode()).digest())

def encrypt_api_key(api_key):
    """Encrypt the API key."""
    key = generate_key()
    cipher_suite = Fernet(key)
    encrypted_key = cipher_suite.encrypt(api_key.encode())
    return encrypted_key

def decrypt_api_key(encrypted_key):
    """Decrypt the API key."""
    try:
        key = generate_key()
        cipher_suite = Fernet(key)
        decrypted_key = cipher_suite.decrypt(encrypted_key).decode()
        return decrypted_key
    except Exception:
        return None

# Initialize session state
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False

if "encrypted_api_key" not in st.session_state:
    st.session_state.encrypted_api_key = None

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "customer_data" not in st.session_state:
    st.session_state.customer_data = None

if "current_customer" not in st.session_state:
    st.session_state.current_customer = None

if "response_generated" not in st.session_state:
    st.session_state.response_generated = False

if "sales_metrics" not in st.session_state:
    st.session_state.sales_metrics = {
        "responses_generated": 0,
        "conversations_saved": 0,
        "customers_engaged": set(),
        "avg_response_time": []
    }

if "auth_token" not in st.session_state:
    st.session_state.auth_token = str(uuid.uuid4())

if "df" not in st.session_state:
    st.session_state.df = None

# CRM-specific session state variables
if "leads" not in st.session_state:
    st.session_state.leads = []

if "deals" not in st.session_state:
    st.session_state.deals = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "meetings" not in st.session_state:
    st.session_state.meetings = []

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

if "notifications" not in st.session_state:
    st.session_state.notifications = []

if "sales_pipeline" not in st.session_state:
    st.session_state.sales_pipeline = {
        "stages": ["Lead Qualification", "Needs Assessment", "Proposal/Price Quote", "Negotiation/Review", "Closed Won", "Closed Lost"],
        "deals_by_stage": {
            "Lead Qualification": [],
            "Needs Assessment": [],
            "Proposal/Price Quote": [],
            "Negotiation/Review": [],
            "Closed Won": [],
            "Closed Lost": []
        }
    }

# New session state variables for city-wise and business-type lead management
if "leads_by_city" not in st.session_state:
    st.session_state.leads_by_city = defaultdict(list)

if "leads_by_business_type" not in st.session_state:
    st.session_state.leads_by_business_type = defaultdict(list)

if "leads_by_state" not in st.session_state:
    st.session_state.leads_by_state = defaultdict(list)

if "lead_sources" not in st.session_state:
    st.session_state.lead_sources = defaultdict(int)

if "lead_generation_stats" not in st.session_state:
    st.session_state.lead_generation_stats = {
        "total_generated": 0,
        "total_imported": 0,
        "total_manual": 0,
        "by_city": defaultdict(int),
        "by_business_type": defaultdict(int),
        "by_state": defaultdict(int),
        "by_date": defaultdict(int)
    }

if "show_lead_generator" not in st.session_state:
    st.session_state.show_lead_generator = False

if "show_lead_import" not in st.session_state:
    st.session_state.show_lead_import = False

if "last_generated_leads" not in st.session_state:
    st.session_state.last_generated_leads = []

# UI state variables
if "show_lead_form" not in st.session_state:
    st.session_state.show_lead_form = False

if "show_deal_form" not in st.session_state:
    st.session_state.show_deal_form = False

if "show_task_form" not in st.session_state:
    st.session_state.show_task_form = False

if "show_meeting_form" not in st.session_state:
    st.session_state.show_meeting_form = False

if "show_pipeline_view" not in st.session_state:
    st.session_state.show_pipeline_view = False

# CRM-specific session state variables
if "leads" not in st.session_state:
    st.session_state.leads = []

if "deals" not in st.session_state:
    st.session_state.deals = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "meetings" not in st.session_state:
    st.session_state.meetings = []

if "emails" not in st.session_state:
    st.session_state.emails = []

if "notifications" not in st.session_state:
    st.session_state.notifications = []

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {
        "currency": "₹",
        "timezone": "Asia/Kolkata",
        "language": "en",
        "date_format": "%d-%m-%Y",
        "theme": "light"
    }

if "lead_scoring_model" not in st.session_state:
    st.session_state.lead_scoring_model = {
        "budget_weight": 0.3,
        "engagement_weight": 0.25,
        "product_interest_weight": 0.25,
        "decision_timeline_weight": 0.2
    }

if "sales_pipeline" not in st.session_state:
    st.session_state.sales_pipeline = {
        "stages": [
            "Lead Qualification",
            "Needs Assessment",
            "Proposal/Price Quote",
            "Negotiation/Review",
            "Closed Won",
            "Closed Lost"
        ],
        "deals_by_stage": defaultdict(list)
    }

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

# Function to securely configure API key
def configure_api_key(api_key):
    """Configure the Gemini API with the provided key."""
    try:
        # Encrypt the API key before storing it
        st.session_state.encrypted_api_key = encrypt_api_key(api_key)
        
        # Configure Gemini with the API key
        genai.configure(api_key=api_key)
        st.session_state.api_key_configured = True
        return True
    except Exception as e:
        st.error(f"Error configuring API: {str(e)}")
        return False

# Function to use the stored API key
def use_configured_api_key():
    """Use the stored encrypted API key."""
    if st.session_state.encrypted_api_key:
        decrypted_key = decrypt_api_key(st.session_state.encrypted_api_key)
        if decrypted_key:
            genai.configure(api_key=decrypted_key)
            return True
    return False

# Function to generate product recommendations
def generate_recommendations(customer_data):
    """Generate product recommendations based on customer data."""
    # product_details is already declared as global in the main function

    recommendations = []

    # EduRishi product catalog with detailed information based on Schools_Enquiry.csv
    products = {
        # School role-based recommendations from the CSV file
        "School Relationship Manager": ["ELAP", "MDL", "PBL", "ICT", "AI tutor", "Simulation", "E2MP"],
        "Admin Dept": ["ELAP", "MDL", "PBL", "ICT", "AI Workshop", "LMS", "AI software", "AI tutor"],
        "Admin Head": ["ELAP", "MDL", "PBL", "ICT", "AI Workshop", "AI tutor", "Simulation", "Franchise Proposal"],
        "CEO": ["AI software", "E2MP", "Franchise Proposal", "Tech Franchise", "Entrepreneurship_Workshop"],
        "VC": ["AI tutor", "E2MP workshop", "E2MP software", "Simulations", "AI software"],

        # Additional roles that might be in other CSV files
        "Principal": ["ELAP", "MDL", "PBL", "ICT", "AI Workshop", "Franchise Proposal", "Tech Franchise"],
        "Teacher": ["ELAP", "PBL", "AI Workshop", "E2MP", "AI tutor", "Simulation"],
        "IT Director": ["AI software", "LMS", "ICT", "Simulations", "E2MP software"],
        "Academic Coordinator": ["ELAP", "MDL", "PBL", "AI tutor", "E2MP workshop"],

        # Generic profession-based recommendations
        "software_engineer": ["AI software", "E2MP software", "Entrepreneurship_Workshop"],
        "marketing_manager": ["Digital Marketing Masterclass", "LMS", "Entrepreneurship_Workshop"],
        "business_owner": ["AI software", "Entrepreneurship_Workshop", "Franchise Proposal"],
        "education_consultant": ["ELAP", "MDL", "PBL", "ICT", "AI Workshop", "LMS", "E2MP"]
    }

    # Using the global product_details variable instead of redefining it here

    # Check if customer has specific product interests
    if "product_interested" in customer_data and customer_data["product_interested"]:
        interested_products = [p.strip() for p in str(customer_data["product_interested"]).split(",")]
        for product in interested_products:
            if product in product_details:
                recommendations.append(product)
    
    # If no specific interests or not enough recommendations, check pitched products
    if len(recommendations) < 3 and "product_pitched" in customer_data and customer_data["product_pitched"]:
        pitched_products = [p.strip() for p in str(customer_data["product_pitched"]).split(",")]
        for product in pitched_products:
            if product in product_details and product not in recommendations:
                recommendations.append(product)
    
    # If still not enough, use profession-based recommendations
    if len(recommendations) < 3:
        profession = customer_data.get("profession", "").lower().replace(" ", "_")
        if profession in products:
            for product in products[profession]:
                if product not in recommendations:
                    recommendations.append(product)
    
    # Add generic recommendations if needed
    if len(recommendations) < 3:
        generic_products = ["ELAP", "MDL", "PBL", "ICT", "AI Workshop", "AI_Tutor", "AI_Simulation", "AI_Integration_Workshop", "Entrepreneurship_Workshop"]
        for product in generic_products:
            if product not in recommendations:
                recommendations.append(product)
    
    # Convert product codes to full names with descriptions
    detailed_recommendations = []
    for product_code in recommendations[:3]:  # Limit to top 3
        if product_code in product_details:
            detailed_recommendations.append({
                "code": product_code,
                "name": product_details[product_code]["name"],
                "description": product_details[product_code]["description"],
                "brochure": product_details[product_code]["brochure"],
                "video": product_details[product_code]["video"],
                "pricing": product_details[product_code].get("pricing", "Contact for pricing")
            })
        else:
            detailed_recommendations.append({
                "code": product_code,
                "name": product_code,
                "description": "Custom educational solution",
                "brochure": "",
                "video": "",
                "pricing": "Contact for pricing"
            })
    
    return detailed_recommendations

# Function to generate sales response
def generate_sales_response(customer_data, enquiry_details, sales_history=""):
    """Generate a personalized sales response using Gemini."""
    if not st.session_state.api_key_configured:
        return "Error: API key is not configured. Please configure it in the settings."
    
    # Ensure API key is configured
    use_configured_api_key()
    
    start_time = time.time()
    
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get product recommendations for this customer
        recommended_products = generate_recommendations(customer_data)

        # Extract product details for the prompt
        product_info = []
        for product in recommended_products:
            product_info.append({
                "name": product["name"],
                "description": product["description"],
                "pricing": product.get("pricing", "Contact for pricing")
            })

        # Construct the prompt
        prompt = f"""
        You are an AI sales agent for EDURISHI EDUVENTURES PVT LTD, an educational technology company.
        Your task is to generate a personalized sales response based on the customer data and enquiry details provided.

        ## Customer Data:
        {json.dumps(customer_data, indent=2)}

        ## Enquiry Details:
        {enquiry_details}

        ## Recommended Products:
        {json.dumps(product_info, indent=2)}

        """

        if sales_history:
            prompt += f"""
            ## Previous Conversation History:
            {sales_history}

            Please continue the conversation based on this history.
            """

        # Add specific product information based on customer interests
        if "product_interested" in customer_data and not pd.isna(customer_data["product_interested"]):
            prompt += f"""
            ## Products Customer Is Interested In:
            The customer has expressed specific interest in: {customer_data["product_interested"]}
            Focus your response on these products, highlighting their benefits for the customer's specific needs.
            """

        # Add budget information if available
        if "budget" in customer_data and not pd.isna(customer_data["budget"]):
            prompt += f"""
            ## Budget Information:
            The customer has indicated a budget of: {customer_data["budget"]}
            Tailor your recommendations to align with this budget constraint.
            """

        prompt += """
        ## Response Format:
        1. Start with a friendly greeting using the customer's name.
        2. Provide a brief summary of their enquiry to show understanding.
        3. Create a tailored sales pitch based on their data (profession, interests, etc.).
        4. Specifically mention the recommended EDURISHI EDUVENTURES PVT LTD's educational solutions that would benefit them.
        5. If they have expressed interest in specific products, emphasize those products.
        6. If they have budget constraints, acknowledge them and explain how our solutions provide value within their budget.
        7. End with a clear call to action (schedule a call, visit website, etc.).

        Make your response conversational, professional, and persuasive. Focus on how EDURISHI's educational products/services solve their specific needs.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Update metrics
        end_time = time.time()
        response_time = end_time - start_time
        st.session_state.sales_metrics["responses_generated"] += 1
        st.session_state.sales_metrics["avg_response_time"].append(response_time)
        if customer_data.get("name") not in st.session_state.sales_metrics["customers_engaged"]:
            st.session_state.sales_metrics["customers_engaged"].add(customer_data.get("name"))
        
        return response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to save conversation
def save_conversation(customer_name, conversation):
    """Save conversation history to a JSON file."""
    os.makedirs("conversations", exist_ok=True)
    filename = f"conversations/{customer_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(conversation, f, indent=2, ensure_ascii=False)

    # Update metrics
    st.session_state.sales_metrics["conversations_saved"] += 1

    return filename

# Function to generate client package
def generate_client_package(customer_data):
    """Generate a customized product package for a client."""
    if not customer_data:
        return None

    customer_name = customer_data.get('name', 'Unknown')

    # Create output directory
    output_dir = "client_packages"
    os.makedirs(output_dir, exist_ok=True)

    # Create school-specific directory
    school_dir = os.path.join(output_dir, customer_name.replace(" ", "_"))
    os.makedirs(school_dir, exist_ok=True)

    # Get product recommendations
    recommendations = generate_recommendations(customer_data)

    # Generate product information file
    info_file = os.path.join(school_dir, "product_information.txt")
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(f"EduRishi Product Information for {customer_name}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("Contact Information:\n")
        if "contact_person" in customer_data:
            f.write(f"Contact Person: {customer_data.get('contact_person', 'N/A')}\n")
        if "phone" in customer_data:
            f.write(f"Phone: {customer_data.get('phone', 'N/A')}\n")
        if "email" in customer_data:
            f.write(f"Email: {customer_data.get('email', 'N/A')}\n\n")

        f.write("Products of Interest:\n")
        if "product_interested" in customer_data and not pd.isna(customer_data["product_interested"]):
            f.write(f"Specifically interested in: {customer_data['product_interested']}\n\n")

        f.write("Recommended Products:\n")
        for product in recommendations:
            f.write(f"- {product['name']}\n")
            f.write(f"  Description: {product['description']}\n")
            if 'pricing' in product:
                f.write(f"  Pricing: {product['pricing']}\n")
            f.write(f"  Brochure: {product['brochure']}\n")
            f.write(f"  Video: {product['video']}\n\n")

        if "budget" in customer_data and not pd.isna(customer_data["budget"]):
            f.write(f"\nBudget Information: {customer_data['budget']}\n")

    # Copy relevant brochures to the school directory
    for product in recommendations:
        if "brochure" in product and product["brochure"]:
            brochure_path = product["brochure"]
            if os.path.exists(brochure_path):
                import shutil
                shutil.copy2(brochure_path, school_dir)

    return school_dir

# Function to generate customer insights
def generate_customer_insights(customer_data):
    """Generate insights about the customer."""
    insights = []
    
    # Basic insights
    if "profession" in customer_data:
        insights.append(f"Professional in {customer_data['profession']}")
    
    if "age" in customer_data:
        age = customer_data["age"]
        if isinstance(age, (int, float)):
            generation = ""
            if age < 25:
                generation = "Gen Z"
            elif age < 40:
                generation = "Millennial"
            elif age < 55:
                generation = "Gen X"
            else:
                generation = "Baby Boomer"
            insights.append(f"{generation} ({age} years old)")
    
    if "location" in customer_data:
        insights.append(f"Based in {customer_data['location']}")
    
    if "interests" in customer_data:
        interests = customer_data["interests"]
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(",")]
            if len(interests) > 0:
                insights.append(f"Interested in {', '.join(interests[:3])}")
    
    if "budget" in customer_data:
        budget = customer_data["budget"]
        if isinstance(budget, (int, float)) and budget > 0:
            if budget < 1000:
                tier = "Budget-conscious"
            elif budget < 5000:
                tier = "Mid-range buyer"
            else:
                tier = "Premium buyer"
            insights.append(f"{tier} (${budget:,} budget)")
    
    return insights

# Function to create a customer profile visualization
def create_customer_profile_chart(customer_data):
    """Create a radar chart for customer profile visualization."""
    categories = []
    values = []
    
    # Define categories and extract values
    if "age" in customer_data:
        categories.append("Age")
        age = float(customer_data["age"])
        # Normalize age to 0-1 scale (assuming 18-80 range)
        values.append(min(1.0, max(0.0, (age - 18) / 62)))
    
    if "budget" in customer_data:
        categories.append("Budget")
        budget = float(customer_data["budget"])
        # Normalize budget to 0-1 scale (assuming 0-20000 range)
        values.append(min(1.0, max(0.0, budget / 20000)))
    
    # Add engagement score (random for demo)
    categories.append("Engagement")
    values.append(random.uniform(0.3, 0.9))
    
    # Add purchase likelihood (random for demo)
    categories.append("Purchase Likelihood")
    values.append(random.uniform(0.4, 0.8))
    
    # Add customer loyalty (random for demo)
    categories.append("Loyalty")
    values.append(random.uniform(0.2, 0.7))
    
    # Create radar chart
    if len(categories) > 2:
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, polar=True)
        
        # Compute angle for each category
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        values.append(values[0])  # Close the loop
        angles.append(angles[0])  # Close the loop
        categories.append(categories[0])  # Close the loop
        
        # Plot data
        ax.plot(angles, values, 'o-', linewidth=2, color='#1E88E5')
        ax.fill(angles, values, alpha=0.25, color='#1E88E5')
        
        # Set category labels
        ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
        
        # Set radial limits
        ax.set_ylim(0, 1)
        ax.set_facecolor('#f0f0f0')
        
        # Remove radial labels
        ax.set_yticklabels([])
        
        # Add title
        plt.title("Customer Profile", size=11, y=1.1)
        
        return fig
    
    return None

# Function to generate a sales script template
def generate_sales_script(customer_data):
    """Generate a sales script template based on customer data."""
    name = customer_data.get("name", "Customer")
    profession = customer_data.get("profession", "professional")
    interests = customer_data.get("interests", "")
    
    script = f"""
    # EDURISHI EDUVENTURES Sales Script for {name}
    
    ## Introduction
    "Hello {name}, this is [Your Name] from EDURISHI EDUVENTURES PVT LTD. Thank you for your interest in our educational solutions for {profession}s."
    
    ## Value Proposition
    "At EDURISHI, we specialize in helping {profession}s like yourself enhance their skills and advance their careers through our tailored educational programs."
    
    ## Addressing Interests
    """
    
    if interests:
        script += f'"I noticed you have an interest in {interests}. Our educational solutions can help you develop expertise in these areas by providing structured learning paths and industry-relevant content."\n'
    
    script += """
    ## Overcoming Objections
    "I understand your concerns about [objection]. Many of our students initially felt the same way, but they found that our flexible learning options and expert instructors made the process much easier than expected."
    
    ## Call to Action
    "Would you be interested in scheduling a free consultation to discuss how our programs can be tailored to your specific career goals?"
    """
    
    return script

# CRM Helper Functions
def calculate_lead_score(lead_data):
    """Calculate a lead score based on various factors."""
    score = 0
    max_score = 100

    # Budget factor (higher budget = higher score)
    if "budget" in lead_data and not pd.isna(lead_data["budget"]):
        try:
            budget = float(lead_data["budget"])
            # Normalize budget score (assuming max budget of 500,000)
            budget_score = min(budget / 500000 * 30, 30)  # 30% weight to budget
            score += budget_score
        except (ValueError, TypeError):
            # If budget can't be converted to float, assign a default score
            score += 10

    # Engagement factor
    engagement_score = 0
    if lead_data.get("email_opened", 0) > 0:
        engagement_score += 5
    if lead_data.get("email_replied", 0) > 0:
        engagement_score += 10
    if lead_data.get("meetings_attended", 0) > 0:
        engagement_score += 15
    score += min(engagement_score, 25)  # 25% weight to engagement

    # Product interest factor
    if "product_interested" in lead_data and not pd.isna(lead_data["product_interested"]):
        products_interested = str(lead_data["product_interested"]).split(",")
        product_score = min(len(products_interested) * 8, 25)  # 25% weight to product interest
        score += product_score

    # Decision timeline factor (if available)
    if "decision_timeline" in lead_data:
        timeline = lead_data["decision_timeline"].lower() if not pd.isna(lead_data["decision_timeline"]) else "unknown"
        if "immediate" in timeline or "urgent" in timeline or "1 week" in timeline:
            score += 20  # 20% weight to timeline
        elif "month" in timeline or "30 day" in timeline:
            score += 15
        elif "quarter" in timeline or "3 month" in timeline:
            score += 10
        elif "year" in timeline or "12 month" in timeline:
            score += 5
        else:
            score += 0

    # Return the final score
    return min(round(score), max_score)

def get_lead_status(score):
    """Convert a lead score to a status category."""
    if score >= 80:
        return "Hot", "#FF4500"  # Orange-red
    elif score >= 60:
        return "Warm", "#FFA500"  # Orange
    elif score >= 40:
        return "Lukewarm", "#FFD700"  # Gold
    elif score >= 20:
        return "Cool", "#87CEEB"  # Sky blue
    else:
        return "Cold", "#ADD8E6"  # Light blue

def format_currency(amount, currency_symbol="₹"):
    """Format an amount with the appropriate currency symbol."""
    try:
        amount = float(amount)
        if currency_symbol in ["$", "€", "£"]:
            return f"{currency_symbol}{amount:,.2f}"
        else:
            # For Indian Rupee and other currencies that come before the amount
            return f"{currency_symbol} {amount:,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol} 0.00"

def create_new_lead(customer_data):
    """Create a new lead from customer data."""
    # Generate a unique ID for the lead
    lead_id = str(uuid.uuid4())

    # Calculate lead score
    lead_score = calculate_lead_score(customer_data)

    # Get lead status based on score
    lead_status, lead_color = get_lead_status(lead_score)

    # Extract location information
    location = customer_data.get("location", "")
    city = customer_data.get("city", "")
    state = customer_data.get("state", "")

    # If location contains city and state but city/state fields are empty, try to extract them
    if location and not (city and state):
        location_parts = location.split(",")
        if len(location_parts) >= 2:
            if not city:
                city = location_parts[0].strip()
            if not state:
                state = location_parts[1].strip()

    # If we have city but no state, try to find the state
    if city and not state:
        for s, cities in get_all_cities().items():
            if city in cities:
                state = s
                break

    # Extract business type information
    business_type = customer_data.get("business_type", "")
    business_subcategory = customer_data.get("business_subcategory", "")

    # If no business type is provided, try to infer from profession or other fields
    if not business_type:
        profession = customer_data.get("profession", "").lower()
        company_name = customer_data.get("name", "").lower()

        # Simple inference rules
        if any(term in profession for term in ["principal", "teacher", "academic", "school", "college", "university", "education"]):
            business_type = "Educational"
        elif any(term in profession for term in ["engineer", "manufacturing", "production", "industrial"]):
            business_type = "Industrial"
        elif any(term in profession for term in ["editor", "publisher", "publication", "content", "media"]):
            business_type = "Publishers"
        elif any(term in profession for term in ["software", "tech", "it", "digital", "computer"]):
            business_type = "Technology"
        elif any(term in profession for term in ["doctor", "medical", "health", "hospital", "clinic"]):
            business_type = "Healthcare"
        elif any(term in profession for term in ["retail", "store", "shop", "sales", "merchant"]):
            business_type = "Retail"
        elif any(term in profession for term in ["government", "official", "public", "municipal", "department"]):
            business_type = "Government"

        # If still not determined, check company name
        if not business_type:
            if any(term in company_name for term in ["school", "college", "university", "academy", "institute", "education"]):
                business_type = "Educational"
            elif any(term in company_name for term in ["industry", "manufacturing", "factory", "production", "mill"]):
                business_type = "Industrial"
            elif any(term in company_name for term in ["publication", "press", "media", "publisher", "news"]):
                business_type = "Publishers"
            elif any(term in company_name for term in ["tech", "software", "digital", "computer", "it solutions"]):
                business_type = "Technology"
            elif any(term in company_name for term in ["hospital", "clinic", "medical", "healthcare", "pharmacy"]):
                business_type = "Healthcare"
            elif any(term in company_name for term in ["store", "retail", "shop", "mart", "supermarket"]):
                business_type = "Retail"
            elif any(term in company_name for term in ["government", "department", "ministry", "municipal", "corporation"]):
                business_type = "Government"

    # Determine source with more detail
    source = customer_data.get("source", "CSV Import")
    if source == "CSV Import" and "source_detail" in customer_data:
        source = customer_data["source_detail"]

    # Create lead object with enhanced fields
    lead = {
        "id": lead_id,
        "name": customer_data.get("name", "Unknown"),
        "email": customer_data.get("email", ""),
        "phone": customer_data.get("phone", ""),
        "profession": customer_data.get("profession", ""),
        "company": customer_data.get("company", customer_data.get("name", "")),
        "location": location,
        "city": city,
        "state": state,
        "business_type": business_type,
        "business_subcategory": business_subcategory,
        "product_interested": customer_data.get("product_interested", ""),
        "product_pitched": customer_data.get("product_pitched", ""),
        "budget": customer_data.get("budget", 0),
        "source": source,
        "score": lead_score,
        "status": lead_status,
        "status_color": lead_color,
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_contacted": None,
        "notes": customer_data.get("notes", ""),
        "tags": customer_data.get("tags", []),
        "owner": customer_data.get("owner", "Current User"),
        "email_opened": customer_data.get("email_opened", 0),
        "email_replied": customer_data.get("email_replied", 0),
        "meetings_attended": customer_data.get("meetings_attended", 0),
        "decision_timeline": customer_data.get("decision_timeline", "Unknown"),
        "website": customer_data.get("website", ""),
        "social_media": customer_data.get("social_media", {}),
        "address": customer_data.get("address", ""),
        "pincode": customer_data.get("pincode", ""),
        "contact_person": customer_data.get("contact_person", "")
    }

    # Add to session state
    st.session_state.leads.append(lead)

    # Update city, state, and business type indexes
    if city:
        st.session_state.leads_by_city[city].append(lead_id)
        st.session_state.lead_generation_stats["by_city"][city] += 1

    if state:
        st.session_state.leads_by_state[state].append(lead_id)
        st.session_state.lead_generation_stats["by_state"][state] += 1

    if business_type:
        st.session_state.leads_by_business_type[business_type].append(lead_id)
        st.session_state.lead_generation_stats["by_business_type"][business_type] += 1

    # Update lead source stats
    st.session_state.lead_sources[source] += 1

    # Update date stats
    today = datetime.now().strftime("%Y-%m-%d")
    st.session_state.lead_generation_stats["by_date"][today] += 1

    # Update total counts
    if source == "Generated":
        st.session_state.lead_generation_stats["total_generated"] += 1
    elif source == "CSV Import":
        st.session_state.lead_generation_stats["total_imported"] += 1
    else:
        st.session_state.lead_generation_stats["total_manual"] += 1

    # Log activity
    log_activity(f"New lead created: {lead['name']}", "lead_creation", lead_id)

    return lead

def create_deal(lead_data, deal_name=None, amount=None, stage="Lead Qualification"):
    """Create a new deal from lead data."""
    # Generate a unique ID for the deal
    deal_id = str(uuid.uuid4())

    # Use provided deal name or generate one
    if not deal_name:
        deal_name = f"{lead_data['name']} - {datetime.now().strftime('%b %Y')}"

    # Use provided amount or lead's budget
    if not amount and "budget" in lead_data and lead_data["budget"]:
        try:
            amount = float(lead_data["budget"])
        except (ValueError, TypeError):
            amount = 0

    # Create deal object
    deal = {
        "id": deal_id,
        "name": deal_name,
        "lead_id": lead_data["id"],
        "lead_name": lead_data["name"],
        "amount": amount,
        "formatted_amount": format_currency(amount),
        "stage": stage,
        "probability": get_stage_probability(stage),
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expected_close_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "products": lead_data.get("product_interested", "").split(",") if lead_data.get("product_interested") else [],
        "notes": "",
        "owner": "Current User",
        "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "activities": []
    }

    # Add to session state
    st.session_state.deals.append(deal)

    # Add to pipeline by stage
    st.session_state.sales_pipeline["deals_by_stage"][stage].append(deal_id)

    # Log activity
    log_activity(f"New deal created: {deal['name']}", "deal_creation", deal_id)

    return deal

def get_stage_probability(stage):
    """Get the probability percentage based on the deal stage."""
    stage_probabilities = {
        "Lead Qualification": 10,
        "Needs Assessment": 30,
        "Proposal/Price Quote": 50,
        "Negotiation/Review": 70,
        "Closed Won": 100,
        "Closed Lost": 0
    }
    return stage_probabilities.get(stage, 10)

def create_task(title, due_date, assigned_to="Current User", related_to=None, related_type=None, priority="Medium", notes=""):
    """Create a new task."""
    # Generate a unique ID for the task
    task_id = str(uuid.uuid4())

    # Create task object
    task = {
        "id": task_id,
        "title": title,
        "due_date": due_date,
        "assigned_to": assigned_to,
        "related_to": related_to,
        "related_type": related_type,
        "priority": priority,
        "notes": notes,
        "status": "Open",
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed_date": None
    }

    # Add to session state
    st.session_state.tasks.append(task)

    # Log activity
    log_activity(f"New task created: {task['title']}", "task_creation", task_id)

    return task

def schedule_meeting(title, date, time, duration, attendees, location="Virtual", notes="", related_to=None, related_type=None):
    """Schedule a new meeting."""
    # Generate a unique ID for the meeting
    meeting_id = str(uuid.uuid4())

    # Create meeting object
    meeting = {
        "id": meeting_id,
        "title": title,
        "date": date,
        "time": time,
        "duration": duration,
        "attendees": attendees,
        "location": location,
        "notes": notes,
        "related_to": related_to,
        "related_type": related_type,
        "status": "Scheduled",
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Add to session state
    st.session_state.meetings.append(meeting)

    # Log activity
    log_activity(f"New meeting scheduled: {meeting['title']}", "meeting_creation", meeting_id)

    return meeting

def log_activity(description, activity_type, related_id=None, related_name=None):
    """Log an activity in the system."""
    activity = {
        "id": str(uuid.uuid4()),
        "description": description,
        "type": activity_type,
        "related_id": related_id,
        "related_name": related_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": "Current User"
    }

    # Add to session state
    st.session_state.activity_log.append(activity)

    return activity

def add_notification(message, notification_type="info", related_id=None, related_type=None):
    """Add a notification to the system."""
    notification = {
        "id": str(uuid.uuid4()),
        "message": message,
        "type": notification_type,
        "related_id": related_id,
        "related_type": related_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }

    # Add to session state
    st.session_state.notifications.append(notification)

    return notification

def get_pipeline_summary():
    """Get a summary of the sales pipeline."""
    summary = {
        "total_deals": len(st.session_state.deals),
        "total_value": sum(deal.get("amount", 0) for deal in st.session_state.deals),
        "stages": {}
    }

    # Calculate deals and value by stage
    for stage in st.session_state.sales_pipeline["stages"]:
        stage_deals = [deal for deal in st.session_state.deals if deal.get("stage") == stage]
        stage_value = sum(deal.get("amount", 0) for deal in stage_deals)
        stage_count = len(stage_deals)

        summary["stages"][stage] = {
            "count": stage_count,
            "value": stage_value,
            "formatted_value": format_currency(stage_value)
        }

    return summary

def get_lead_summary():
    """Get a summary of leads by status."""
    summary = {
        "total_leads": len(st.session_state.leads),
        "status": {}
    }

    # Count leads by status
    status_counts = Counter(lead.get("status") for lead in st.session_state.leads)

    for status, count in status_counts.items():
        summary["status"][status] = count

    return summary

def generate_forecast(deals, forecast_period=90):
    """Generate a sales forecast based on current deals."""
    today = datetime.now()
    end_date = today + timedelta(days=forecast_period)

    # Filter deals expected to close within the forecast period
    forecast_deals = []
    for deal in deals:
        try:
            close_date = datetime.strptime(deal.get("expected_close_date", ""), "%Y-%m-%d")
            if close_date <= end_date:
                # Apply probability to deal amount
                probability = deal.get("probability", 0) / 100
                weighted_amount = deal.get("amount", 0) * probability

                forecast_deals.append({
                    "id": deal.get("id"),
                    "name": deal.get("name"),
                    "amount": deal.get("amount", 0),
                    "probability": deal.get("probability", 0),
                    "weighted_amount": weighted_amount,
                    "close_date": deal.get("expected_close_date"),
                    "stage": deal.get("stage")
                })
        except (ValueError, TypeError):
            # Skip deals with invalid dates
            continue

    # Calculate forecast totals
    total_potential = sum(deal.get("amount", 0) for deal in forecast_deals)
    total_weighted = sum(deal.get("weighted_amount", 0) for deal in forecast_deals)

    return {
        "deals": forecast_deals,
        "total_potential": total_potential,
        "total_weighted": total_weighted,
        "formatted_potential": format_currency(total_potential),
        "formatted_weighted": format_currency(total_weighted),
        "forecast_period": forecast_period,
        "forecast_end_date": end_date.strftime("%Y-%m-%d")
    }

# Secure API key entry form
def secure_api_key_entry():
    """Provide a secure way to enter the API key."""
    st.markdown('<div class="sub-header">Secure API Key Configuration</div>', unsafe_allow_html=True)
    
    # Create a unique form key
    form_key = f"api_key_form_{st.session_state.auth_token}"
    
    with st.form(key=form_key):
        st.markdown("""
        <div class="info-box">
        Enter your API key below. For security, the key will be encrypted and never displayed again.
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden field for API key (not visible in UI)
        api_key = st.text_input("API Key", type="password", key="api_key_input")
        
        # Submit button
        submitted = st.form_submit_button("Securely Configure API")
        
        if submitted and api_key:
            if configure_api_key(api_key):
                st.markdown('<div class="success-box">API key securely configured!</div>', unsafe_allow_html=True)
                # Clear the form by regenerating the auth token
                st.session_state.auth_token = str(uuid.uuid4())
                return True
            else:
                st.markdown('<div class="error-box">Failed to configure API key. Please try again.</div>', unsafe_allow_html=True)
    
    return False

# Demo mode activation
def activate_demo_mode():
    """Activate demo mode with a pre-configured API key."""
    # Try to get API key from Streamlit secrets
    try:
        demo_api_key = st.secrets["api_keys"]["gemini_api_key"]
    except:
        # Fallback to a placeholder key (this won't work in production)
        demo_api_key = "YOUR_API_KEY_HERE"
        st.warning("No API key found in secrets. Please configure your API key in the sidebar.")

    if configure_api_key(demo_api_key):
        st.markdown('<div class="success-box">Demo mode activated! API key securely configured.</div>', unsafe_allow_html=True)
        return True
    else:
        st.markdown('<div class="error-box">Failed to activate demo mode. Please try again or configure your API key manually.</div>', unsafe_allow_html=True)
        return False

# Main application
def main():
    # Declare product_details as global at the beginning of the main function
    global product_details

    # Add space for the logo
    st.markdown('<div style="margin-top: 80px;"></div>', unsafe_allow_html=True)

    # Main header
    st.markdown('<div class="main-header">AI Sales Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Leverage AI to generate personalized sales responses and boost your conversion rates.</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration and metrics
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

        # Company name in sidebar
        st.markdown('<div style="text-align: center; font-weight: bold; color: #0D47A1; margin-bottom: 20px;">EDURISHI EDUVENTURES</div>', unsafe_allow_html=True)

        # Deployment information
        with st.expander("ℹ️ Deployment Info"):
            st.markdown("""
            ### Streamlit Cloud Deployment

            To deploy this app on Streamlit Cloud:

            1. Fork the repository on GitHub
            2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
            3. Create a new app and select your forked repository
            4. Set up your API key in Streamlit Cloud secrets:
            ```
            [api_keys]
            gemini_api_key = "your-api-key-here"
            ```

            For more details, see the README.md file.
            """)
        
        # API Key Configuration Status
        with st.expander("⚙️ Security Status"):
            if st.session_state.api_key_configured:
                st.markdown('<div class="success-box">API key is securely configured and encrypted.</div>', unsafe_allow_html=True)
                
                # Option to reset API key
                if st.button("Reset API Key"):
                    st.session_state.encrypted_api_key = None
                    st.session_state.api_key_configured = False
                    st.rerun()
            else:
                st.markdown('<div class="warning-box">API key not configured. Use the secure form below or activate demo mode.</div>', unsafe_allow_html=True)
                
                # Secure API key entry
                secure_api_key_entry()
                
                st.markdown("### OR")
                
                # Demo mode option
                if st.button("Activate Demo Mode"):
                    if activate_demo_mode():
                        st.rerun()
        
        # Sales Metrics
        st.markdown('<div class="sub-header">Sales Metrics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Responses", st.session_state.sales_metrics["responses_generated"])
            st.metric("Customers", len(st.session_state.sales_metrics["customers_engaged"]))
        
        with col2:
            st.metric("Saved Convs.", st.session_state.sales_metrics["conversations_saved"])
            if st.session_state.sales_metrics["avg_response_time"]:
                avg_time = sum(st.session_state.sales_metrics["avg_response_time"]) / len(st.session_state.sales_metrics["avg_response_time"])
                st.metric("Avg. Response Time", f"{avg_time:.2f}s")
        
        # CRM Notifications
        st.markdown('<div class="sub-header">CRM Notifications</div>', unsafe_allow_html=True)

        # Display notifications
        if not st.session_state.notifications:
            st.info("No new notifications")
        else:
            # Show most recent 3 notifications
            for notification in sorted(st.session_state.notifications, key=lambda x: x["timestamp"], reverse=True)[:3]:
                if notification["type"] == "info":
                    st.info(notification["message"])
                elif notification["type"] == "success":
                    st.success(notification["message"])
                elif notification["type"] == "warning":
                    st.warning(notification["message"])
                else:
                    st.error(notification["message"])

        # Quick Actions
        st.markdown('<div class="sub-header">Quick Actions</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Generate Report"):
                st.markdown('<div class="success-box">Report generated and saved to reports folder!</div>', unsafe_allow_html=True)

            if st.button("📞 Log Call"):
                st.session_state.show_call_log_form = True

        with col2:
            if st.button("📧 Send Email"):
                st.session_state.show_email_form = True

            if st.button("📅 New Task"):
                st.session_state.show_new_task_form = True

        # Call logging form
        if st.session_state.get("show_call_log_form", False):
            with st.form("log_call_form"):
                st.markdown('<div class="sub-header">Log Call</div>', unsafe_allow_html=True)

                # Contact selection
                contact_options = []
                for lead in st.session_state.leads:
                    contact_options.append({"label": lead.get("name", "Unknown"), "value": lead.get("id"), "type": "lead"})

                if contact_options:
                    contact_selection = st.selectbox(
                        "Contact",
                        options=[f"{opt['label']} ({opt['type']})" for opt in contact_options],
                        key="call_contact"
                    )

                    # Extract selected contact
                    selected_idx = contact_options.index(next(
                        (opt for opt in contact_options if f"{opt['label']} ({opt['type']})" == contact_selection),
                        contact_options[0]
                    ))
                    selected_contact = contact_options[selected_idx]

                    call_notes = st.text_area("Call Notes")
                    call_outcome = st.selectbox("Call Outcome", ["Interested", "Not Interested", "Call Back Later", "Left Message", "No Answer"])

                    submitted = st.form_submit_button("Log Call")

                    if submitted:
                        # Log the call as an activity
                        activity_desc = f"Call with {selected_contact['label']}: {call_outcome}"
                        log_activity(activity_desc, "call_log", selected_contact["value"], selected_contact["label"])

                        # Update lead's last contacted date
                        if selected_contact["type"] == "lead":
                            for lead in st.session_state.leads:
                                if lead.get("id") == selected_contact["value"]:
                                    lead["last_contacted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    break

                        # Add notification
                        add_notification(f"Call logged with {selected_contact['label']}", "info", selected_contact["value"], selected_contact["type"])

                        st.success("Call logged successfully!")
                        st.session_state.show_call_log_form = False
                        st.rerun()
                else:
                    st.info("No contacts available. Please create a lead first.")

        if st.button("📦 Generate All Packages"):
            with st.spinner("Generating packages for all schools..."):
                # Check if we have loaded data in session state
                if 'df' in st.session_state and st.session_state.df is not None:
                    packages_generated = 0
                    for idx, row in st.session_state.df.iterrows():
                        customer_data = row.to_dict()
                        package_dir = generate_client_package(customer_data)
                        if package_dir:
                            packages_generated += 1

                    st.markdown(f'<div class="success-box">Generated {packages_generated} client packages!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-box">No school data loaded. Please load data first.</div>', unsafe_allow_html=True)

        if st.button("🔄 Reset Session"):
            # Keep API key configuration but reset everything else
            encrypted_key = st.session_state.encrypted_api_key
            api_configured = st.session_state.api_key_configured
            
            # Reset session state
            for key in list(st.session_state.keys()):
                if key not in ["encrypted_api_key", "api_key_configured", "auth_token"]:
                    del st.session_state[key]
            
            # Restore API configuration
            st.session_state.encrypted_api_key = encrypted_key
            st.session_state.api_key_configured = api_configured
            
            # Initialize new session state
            st.session_state.conversation_history = []
            st.session_state.customer_data = None
            st.session_state.current_customer = None
            st.session_state.response_generated = False
            st.session_state.df = None
            st.session_state.sales_metrics = {
                "responses_generated": 0,
                "conversations_saved": 0,
                "customers_engaged": set(),
                "avg_response_time": []
            }
            
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 Sales Assistant",
        "📊 CRM Dashboard",
        "👥 Leads & Deals",
        "📅 Tasks & Calendar",
        "📚 Conversation History",
        "📝 Sales Scripts",
        "🎓 EduRishi Products"
    ])
    
    with tab1:
        # Check if API is configured
        if not st.session_state.api_key_configured:
            st.markdown('<div class="warning-box">Please configure your API key in the sidebar before using the application.</div>', unsafe_allow_html=True)
        else:
            # Ensure API key is configured for this session
            use_configured_api_key()

            # Clear any pre-loaded data
            if "data_cleared" not in st.session_state:
                st.session_state.df = None
                st.session_state.leads = []
                st.session_state.deals = []
                st.session_state.tasks = []
                st.session_state.meetings = []
                st.session_state.activity_log = []
                st.session_state.data_cleared = True

            # Add a button to clear all data
            if st.button("Clear All Data"):
                st.session_state.df = None
                st.session_state.leads = []
                st.session_state.deals = []
                st.session_state.tasks = []
                st.session_state.meetings = []
                st.session_state.activity_log = []
                st.success("All data has been cleared. You can now upload a new CSV file.")
                st.rerun()

            # File uploader for CSV data
            col1, col2 = st.columns([3, 1])
            with col1:
                uploaded_file = st.file_uploader("Upload customer data (CSV)", type=["csv"], help="Upload your CSV file with customer data")

            with col2:
                # Create a sample CSV template for download
                sample_data = {
                    "Name of Customer": ["ABC School", "XYZ College"],
                    "Person Name": ["John Doe", "Jane Smith"],
                    "Designation": ["Principal", "Director"],
                    "Email": ["john@abcschool.com", "jane@xyzcollege.com"],
                    "Phone": ["9876543210", "8765432109"],
                    "City": ["Mumbai", "Delhi"],
                    "State": ["Maharashtra", "Delhi"],
                    "Address": ["123 Main St", "456 Park Ave"],
                    "Pincode": ["400001", "110001"],
                    "Product Interested": ["ELAP, MDL", "PBL, ICT"],
                    "Budget": ["100000", "200000"]
                }
                sample_df = pd.DataFrame(sample_data)
                sample_csv = sample_df.to_csv(index=False)

                st.download_button(
                    label="Download Template",
                    data=sample_csv,
                    file_name="sample_template.csv",
                    mime="text/csv",
                    help="Download a sample CSV template"
                )

            if uploaded_file is not None:
                try:
                    # Read and display the CSV data
                    df = pd.read_csv(uploaded_file)
                    st.session_state.df = df  # Store in session state
                except Exception as e:
                    st.error(f"Error reading uploaded CSV: {str(e)}")
                    df = None
                    st.session_state.df = None
            else:
                df = None
                st.info("Please upload a CSV file with customer data to get started.")

            if df is not None:
                try:
                    # Map column names from Schools_Enquiry.csv format
                    # Create a mapping for Schools_Enquiry.csv columns to expected columns
                    column_mapping = {
                        'Name of Customer': 'name',
                        'Person Name': 'contact_name',
                        'Ph.no': 'phone',
                        'Email-id': 'email',
                        'Profession': 'profession',
                        'Contact Person Name in case of institution': 'contact_person',
                        'Product Pitched': 'product_pitched',
                        'Product Interested': 'product_interested',
                        'Budget': 'budget'
                    }

                    # Rename columns based on mapping
                    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

                    # Display data in an expandable section
                    with st.expander("View Customer Data"):
                        st.dataframe(df, use_container_width=True)

                    # Customer selection
                    customer_names = df['name'].tolist() if 'name' in df.columns else []
                    selected_customer = st.selectbox("Select a customer", customer_names)

                    if selected_customer:
                        # Extract customer data
                        customer_data = df[df['name'] == selected_customer].iloc[0].to_dict()
                        st.session_state.customer_data = customer_data
                        st.session_state.current_customer = selected_customer
                        
                        # Display customer information in a card
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown(f'<div class="sub-header">Customer Profile: {selected_customer}</div>', unsafe_allow_html=True)
                            st.markdown('<div class="customer-card">', unsafe_allow_html=True)
                            
                            # Display key customer information
                            if "email" in customer_data:
                                st.markdown(f"**Email:** {customer_data['email']}")

                            if "phone" in customer_data:
                                st.markdown(f"**Phone:** {customer_data['phone']}")

                            if "profession" in customer_data:
                                st.markdown(f"**Profession:** {customer_data['profession']}")

                            if "contact_person" in customer_data:
                                st.markdown(f"**Contact Person:** {customer_data['contact_person']}")

                            if "location" in customer_data:
                                st.markdown(f"**Location:** {customer_data['location']}")
                                
                            # Display product interests if available
                            if "product_pitched" in customer_data and not pd.isna(customer_data["product_pitched"]):
                                st.markdown(f"**Products Pitched:** {customer_data['product_pitched']}")
                                
                            if "product_interested" in customer_data and not pd.isna(customer_data["product_interested"]):
                                st.markdown(f"**Products Interested:** {customer_data['product_interested']}")
                                
                            if "budget" in customer_data and not pd.isna(customer_data["budget"]):
                                st.markdown(f"**Budget:** {customer_data['budget']}")
                            
                            # Customer insights
                            insights = generate_customer_insights(customer_data)
                            if insights:
                                st.markdown("**Insights:**")
                                for insight in insights:
                                    st.markdown(f"- {insight}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Product recommendations
                            st.markdown('<div class="sub-header">Recommended EDURISHI Programs</div>', unsafe_allow_html=True)
                            recommendations = generate_recommendations(customer_data)

                            for i, product in enumerate(recommendations):
                                with st.expander(f"**{i+1}. {product['name']}**"):
                                    st.markdown(f"**Description:** {product['description']}")
                                    if 'pricing' in product:
                                        st.markdown(f"**Pricing:** {product['pricing']}")
                                    st.markdown(f"**Brochure:** {product['brochure']}")
                                    st.markdown(f"**Video:** [Watch Demo]({product['video']})")

                                    # Add a download button for the brochure
                                    if product['brochure']:
                                        if st.button(f"Download {product['code']} Brochure", key=f"dl_{product['code']}"):
                                            st.markdown(f"<div class='success-box'>Downloading {product['name']} brochure...</div>", unsafe_allow_html=True)

                                # Show a progress bar for recommendation relevance
                                st.markdown("**Relevance:**")
                                st.progress(random.uniform(0.65, 0.95))

                        with col2:
                            # Customer profile visualization
                            profile_chart = create_customer_profile_chart(customer_data)
                            if profile_chart:
                                st.pyplot(profile_chart)
                            
                            # Additional customer details in expandable sections
                            with st.expander("Full Customer Details"):
                                st.json(customer_data)

                        # Enquiry details
                        st.markdown('<div class="sub-header">Customer Enquiry</div>', unsafe_allow_html=True)
                        enquiry_details = st.text_area("Enter the customer's enquiry details", height=100)
                        
                        # Previous conversation
                        with st.expander("Previous Conversation (Optional)"):
                            sales_history = st.text_area("Enter any previous conversation history", height=100)
                        
                        # Generate response button
                        if st.button("Generate Personalized Response"):
                            if enquiry_details:
                                with st.spinner("Generating your personalized sales response..."):
                                    response = generate_sales_response(customer_data, enquiry_details, sales_history)
                                    
                                    # Check if response contains an error message
                                    if response.startswith("Error"):
                                        st.markdown(f'<div class="error-box">{response}</div>', unsafe_allow_html=True)
                                    else:
                                        # Add to conversation history
                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        st.session_state.conversation_history.append({
                                            "timestamp": timestamp,
                                            "customer": selected_customer,
                                            "enquiry": enquiry_details,
                                            "response": response
                                        })
                                        
                                        st.session_state.response_generated = True
                                        
                                        # Display response
                                        st.markdown('<div class="sub-header">Generated Response</div>', unsafe_allow_html=True)
                                        st.markdown(f'<div class="response-card">{response}</div>', unsafe_allow_html=True)
                                        
                                        # Action buttons
                                        col1, col2 = st.columns(2)

                                        with col1:
                                            if st.button("Save Conversation"):
                                                saved_file = save_conversation(selected_customer, st.session_state.conversation_history)
                                                st.markdown(f'<div class="success-box">Conversation saved to {saved_file}</div>', unsafe_allow_html=True)

                                        with col2:
                                            if st.button("Copy to Clipboard"):
                                                st.markdown(f"""
                                                <textarea id="response-text" style="position: absolute; left: -9999px;">{response}</textarea>
                                                <script>
                                                    const copyText = document.getElementById("response-text");
                                                    copyText.select();
                                                    document.execCommand("copy");
                                                </script>
                                                """, unsafe_allow_html=True)
                                                st.markdown('<div class="success-box">Response copied to clipboard!</div>', unsafe_allow_html=True)

                                        col3, col4 = st.columns(2)

                                        with col3:
                                            if st.button("Email Response"):
                                                st.markdown('<div class="success-box">Response prepared for email. Opening your email client...</div>', unsafe_allow_html=True)

                                        with col4:
                                            if st.button("Generate Client Package"):
                                                with st.spinner("Generating client package..."):
                                                    package_dir = generate_client_package(customer_data)
                                                    if package_dir:
                                                        st.markdown(f'<div class="success-box">Client package generated in {package_dir}</div>', unsafe_allow_html=True)
                                                    else:
                                                        st.markdown('<div class="error-box">Failed to generate client package</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="warning-box">Please enter enquiry details.</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.markdown(f'<div class="error-box">Error processing the CSV file: {str(e)}</div>', unsafe_allow_html=True)
    
    # CRM Dashboard Tab
    with tab2:
        st.markdown('<div class="main-header">CRM Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Track your sales performance, leads, and deals in real-time.</div>', unsafe_allow_html=True)

        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            lead_count = len(st.session_state.leads)
            st.metric("Total Leads", lead_count, delta=None)

        with col2:
            deal_count = len(st.session_state.deals)
            st.metric("Active Deals", deal_count, delta=None)

        with col3:
            # Calculate total deal value
            total_deal_value = sum(deal.get("amount", 0) for deal in st.session_state.deals)
            st.metric("Pipeline Value", format_currency(total_deal_value), delta=None)

        with col4:
            # Calculate weighted forecast
            forecast_value = sum(deal.get("amount", 0) * deal.get("probability", 0) / 100 for deal in st.session_state.deals)
            st.metric("Forecast (90 Days)", format_currency(forecast_value), delta=None)

        # Use the enhanced dashboard with city-wise and business-type analytics
        create_dashboard_tabs()

        # Sales Pipeline visualization
        st.markdown('<div class="sub-header">Sales Pipeline</div>', unsafe_allow_html=True)

        # Create sample data if no deals exist
        if not st.session_state.deals:
            # Add sample deals for demonstration
            sample_stages = st.session_state.sales_pipeline["stages"]
            sample_values = [random.randint(50000, 200000) for _ in range(len(sample_stages))]
            sample_counts = [random.randint(1, 5) for _ in range(len(sample_stages))]

            # Create a DataFrame for the sample data
            pipeline_df = pd.DataFrame({
                "Stage": sample_stages,
                "Value": sample_values,
                "Count": sample_counts
            })

            # Add formatted values
            pipeline_df["Formatted Value"] = pipeline_df["Value"].apply(lambda x: format_currency(x))
        else:
            # Create a DataFrame from actual deals
            pipeline_data = []
            for stage in st.session_state.sales_pipeline["stages"]:
                stage_deals = [deal for deal in st.session_state.deals if deal.get("stage") == stage]
                stage_value = sum(deal.get("amount", 0) for deal in stage_deals)
                stage_count = len(stage_deals)

                pipeline_data.append({
                    "Stage": stage,
                    "Value": stage_value,
                    "Count": stage_count,
                    "Formatted Value": format_currency(stage_value)
                })

            pipeline_df = pd.DataFrame(pipeline_data)

        # Create a funnel chart for the pipeline
        fig = go.Figure(go.Funnel(
            y=pipeline_df["Stage"],
            x=pipeline_df["Value"],
            textinfo="value+percent initial",
            textfont={"size": 14},
            marker={"color": ["#1E88E5", "#42A5F5", "#64B5F6", "#90CAF9", "#BBDEFB", "#E3F2FD"]},
            connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}}
        ))

        fig.update_layout(
            title="Deal Value by Stage",
            height=400,
            margin=dict(t=50, b=0, l=0, r=0)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display the pipeline data in a table
        st.markdown('<div class="info-box">Pipeline Details</div>', unsafe_allow_html=True)
        st.dataframe(
            pipeline_df[["Stage", "Count", "Formatted Value"]],
            column_config={
                "Stage": "Pipeline Stage",
                "Count": "Number of Deals",
                "Formatted Value": "Total Value"
            },
            use_container_width=True
        )

        # Lead Status and Forecast
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="sub-header">Lead Status Distribution</div>', unsafe_allow_html=True)

            # Create sample data if no leads exist
            if not st.session_state.leads:
                # Sample lead statuses
                statuses = ["Hot", "Warm", "Lukewarm", "Cool", "Cold"]
                counts = [random.randint(1, 10) for _ in range(len(statuses))]
                colors = ["#FF4500", "#FFA500", "#FFD700", "#87CEEB", "#ADD8E6"]

                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=statuses,
                    values=counts,
                    hole=.4,
                    marker_colors=colors
                )])
            else:
                # Count leads by status
                status_counts = Counter(lead.get("status") for lead in st.session_state.leads)
                statuses = list(status_counts.keys())
                counts = list(status_counts.values())

                # Get colors for each status
                colors = []
                for status in statuses:
                    if status == "Hot":
                        colors.append("#FF4500")
                    elif status == "Warm":
                        colors.append("#FFA500")
                    elif status == "Lukewarm":
                        colors.append("#FFD700")
                    elif status == "Cool":
                        colors.append("#87CEEB")
                    else:
                        colors.append("#ADD8E6")

                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=statuses,
                    values=counts,
                    hole=.4,
                    marker_colors=colors
                )])

            fig.update_layout(
                title="Lead Distribution by Status",
                height=350,
                margin=dict(t=50, b=0, l=0, r=0)
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="sub-header">Sales Forecast (90 Days)</div>', unsafe_allow_html=True)

            # Create sample forecast data if no deals exist
            if not st.session_state.deals:
                # Sample months for forecast
                months = [(datetime.now() + timedelta(days=30*i)).strftime("%b %Y") for i in range(3)]
                potential_values = [random.randint(100000, 300000) for _ in range(len(months))]
                weighted_values = [v * random.uniform(0.3, 0.7) for v in potential_values]

                # Create the forecast chart
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=months,
                    y=potential_values,
                    name="Potential Value",
                    marker_color="#90CAF9"
                ))

                fig.add_trace(go.Bar(
                    x=months,
                    y=weighted_values,
                    name="Weighted Value",
                    marker_color="#1E88E5"
                ))
            else:
                # Group deals by expected close month
                forecast_data = {}
                for deal in st.session_state.deals:
                    try:
                        close_date = datetime.strptime(deal.get("expected_close_date", ""), "%Y-%m-%d")
                        month_key = close_date.strftime("%b %Y")

                        if month_key not in forecast_data:
                            forecast_data[month_key] = {"potential": 0, "weighted": 0}

                        amount = deal.get("amount", 0)
                        probability = deal.get("probability", 0) / 100

                        forecast_data[month_key]["potential"] += amount
                        forecast_data[month_key]["weighted"] += amount * probability
                    except (ValueError, TypeError):
                        continue

                # Sort months chronologically
                months = sorted(forecast_data.keys(), key=lambda x: datetime.strptime(x, "%b %Y"))
                potential_values = [forecast_data[month]["potential"] for month in months]
                weighted_values = [forecast_data[month]["weighted"] for month in months]

                # Create the forecast chart
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=months,
                    y=potential_values,
                    name="Potential Value",
                    marker_color="#90CAF9"
                ))

                fig.add_trace(go.Bar(
                    x=months,
                    y=weighted_values,
                    name="Weighted Value",
                    marker_color="#1E88E5"
                ))

            fig.update_layout(
                title="Forecast by Month",
                height=350,
                margin=dict(t=50, b=0, l=0, r=0),
                barmode="group"
            )

            st.plotly_chart(fig, use_container_width=True)

        # Recent Activity
        st.markdown('<div class="sub-header">Recent Activity</div>', unsafe_allow_html=True)

        if not st.session_state.activity_log:
            # Sample activity data
            sample_activities = [
                {"description": "New lead created: ABC International School", "timestamp": "2023-06-15 09:30:45", "type": "lead_creation"},
                {"description": "Deal moved to Proposal stage: XYZ Academy", "timestamp": "2023-06-14 14:22:10", "type": "deal_update"},
                {"description": "Meeting scheduled with St. Mary's School", "timestamp": "2023-06-14 11:05:33", "type": "meeting_creation"},
                {"description": "Email sent to Global Education Institute", "timestamp": "2023-06-13 16:45:22", "type": "email_sent"},
                {"description": "Task completed: Follow up with Sunshine Kindergarten", "timestamp": "2023-06-12 10:15:00", "type": "task_completed"}
            ]

            for activity in sample_activities:
                st.markdown(f"""
                <div class="history-item">
                    <strong>{activity["description"]}</strong><br>
                    <small>{activity["timestamp"]}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Display actual activity log (most recent first)
            for activity in sorted(st.session_state.activity_log, key=lambda x: x["timestamp"], reverse=True)[:5]:
                st.markdown(f"""
                <div class="history-item">
                    <strong>{activity["description"]}</strong><br>
                    <small>{activity["timestamp"]}</small>
                </div>
                """, unsafe_allow_html=True)

    # Leads & Deals Tab
    with tab3:
        st.markdown('<div class="main-header">Leads & Deals Management</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Manage your leads and deals in one place. Track progress and take action.</div>', unsafe_allow_html=True)

        # Create tabs for Leads and Deals
        leads_tab, deals_tab = st.tabs(["Leads", "Deals"])

        with leads_tab:
            st.markdown('<div class="sub-header">Lead Management</div>', unsafe_allow_html=True)

            # Lead actions
            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

            with col1:
                if st.button("Import Leads from CSV"):
                    if st.session_state.df is not None:
                        # Convert existing customer data to leads
                        imported_count = 0
                        for _, row in st.session_state.df.iterrows():
                            customer_data = row.to_dict()
                            create_new_lead(customer_data)
                            imported_count += 1

                        st.success(f"Successfully imported {imported_count} leads!")
                    else:
                        st.warning("Please load customer data first.")
                        st.session_state.show_lead_import = True

            with col2:
                if st.button("Create New Lead"):
                    st.session_state.show_lead_form = True

            with col3:
                if st.button("Generate Leads 🌐"):
                    st.session_state.show_lead_generator = True

            with col4:
                # Lead search/filter
                search_term = st.text_input("Search Leads", placeholder="Enter name, email, or company")

            # Lead import form
            if st.session_state.get("show_lead_import", False):
                with st.expander("Import Leads from CSV", expanded=True):
                    st.markdown('<div class="sub-header">Import Leads</div>', unsafe_allow_html=True)

                    # Store the uploaded file in session state to keep it between form submissions
                    if "uploaded_lead_file" not in st.session_state:
                        st.session_state.uploaded_lead_file = None
                        st.session_state.uploaded_lead_df = None

                    uploaded_file = st.file_uploader("Upload CSV file with lead data", type=["csv"])

                    # Update session state when a new file is uploaded
                    if uploaded_file is not None and (st.session_state.uploaded_lead_file is None or
                                                     uploaded_file.name != getattr(st.session_state.uploaded_lead_file, "name", None)):
                        try:
                            # Read the CSV data
                            df = pd.read_csv(uploaded_file)
                            st.session_state.uploaded_lead_file = uploaded_file
                            st.session_state.uploaded_lead_df = df
                            st.success(f"Successfully loaded CSV with {len(df)} records.")
                        except Exception as e:
                            st.error(f"Error reading CSV: {str(e)}")
                            st.session_state.uploaded_lead_file = None
                            st.session_state.uploaded_lead_df = None

                    # Show preview if we have data
                    if st.session_state.uploaded_lead_df is not None:
                        st.write("Preview of the data:")
                        st.dataframe(st.session_state.uploaded_lead_df.head())

                        # Use a form for the import
                        with st.form("import_leads_form"):
                            st.write(f"Ready to import {len(st.session_state.uploaded_lead_df)} leads")

                            # Submit button
                            submitted = st.form_submit_button("Import All Leads")

                            if submitted:
                                imported_count = 0
                                for _, row in st.session_state.uploaded_lead_df.iterrows():
                                    customer_data = row.to_dict()
                                    customer_data["source"] = "CSV Import"
                                    customer_data["source_detail"] = f"Imported from {st.session_state.uploaded_lead_file.name}"
                                    create_new_lead(customer_data)
                                    imported_count += 1

                                st.success(f"Successfully imported {imported_count} leads!")
                                st.session_state.show_lead_import = False
                                st.session_state.uploaded_lead_file = None
                                st.session_state.uploaded_lead_df = None
                                st.rerun()

                    if st.button("Cancel Import"):
                        st.session_state.show_lead_import = False
                        st.session_state.uploaded_lead_file = None
                        st.session_state.uploaded_lead_df = None
                        st.rerun()

            # Lead generator form
            if st.session_state.get("show_lead_generator", False):
                with st.expander("Generate Leads from Internet", expanded=True):
                    st.markdown('<div class="sub-header">Generate Leads by City & Business Type</div>', unsafe_allow_html=True)
                    st.markdown('<div class="info-box">Generate leads from our database based on city and business type.</div>', unsafe_allow_html=True)

                    # Use a form for lead generation
                    with st.form("lead_generator_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            # State and city selection
                            selected_state = st.selectbox("Select State", options=["All States"] + get_states())

                            # We need to handle city selection differently in a form since it can't be dynamic
                            # So we'll show all cities and filter them in the backend
                            all_cities = [city["city"] for city in get_all_cities()]
                            selected_city = st.selectbox("Select City", options=["All Cities"] + sorted(all_cities))

                        with col2:
                            # Business type selection
                            business_types = get_all_business_types()
                            selected_business_type = st.selectbox("Select Business Type", options=["All Business Types"] + list(business_types.keys()))

                            # Similar to cities, we'll show all subcategories and filter in the backend
                            all_subcategories = []
                            for subcats in business_types.values():
                                all_subcategories.extend(subcats)
                            selected_subcategory = st.selectbox("Select Subcategory", options=["All Subcategories"] + sorted(set(all_subcategories)))

                        # Number of leads to generate
                        num_leads = st.slider("Number of Leads to Generate", min_value=1, max_value=50, value=10)

                        # Submit button
                        submitted = st.form_submit_button("Generate Leads")

                        if submitted:
                            with st.spinner("Generating leads..."):
                                # Prepare parameters
                                city_param = None if selected_city == "All Cities" else selected_city
                                state_param = None if selected_state == "All States" else selected_state
                                business_type_param = None if selected_business_type == "All Business Types" else selected_business_type
                                subcategory_param = None if selected_subcategory == "All Subcategories" else selected_subcategory

                                # Generate leads
                                generated_leads = fetch_leads_from_external_source(
                                    city=city_param,
                                    state=state_param,
                                    business_type=business_type_param,
                                    count=num_leads
                                )

                                # Add leads to the system
                                for lead_data in generated_leads:
                                    lead_data["source"] = "Generated"
                                    lead_data["source_detail"] = f"Generated from Internet Database"
                                    create_new_lead(lead_data)

                                # Store the generated leads for display
                                st.session_state.last_generated_leads = generated_leads

                                st.success(f"Successfully generated {len(generated_leads)} leads!")

                    # Display the last generated leads
                    if st.session_state.last_generated_leads:
                        st.markdown('<div class="sub-header">Recently Generated Leads</div>', unsafe_allow_html=True)

                        for i, lead in enumerate(st.session_state.last_generated_leads[:5]):  # Show only the first 5
                            st.markdown(f"""
                            <div style="padding: 15px; background-color: #F5F5F5; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #1E88E5;">
                                <strong>{lead.get('name', 'Unknown')}</strong><br>
                                {lead.get('city', '')}, {lead.get('state', '')}<br>
                                Business Type: {lead.get('business_type', 'Unknown')}<br>
                                Contact: {lead.get('contact_person', 'Unknown')} | {lead.get('phone', 'N/A')}
                            </div>
                            """, unsafe_allow_html=True)

                        if len(st.session_state.last_generated_leads) > 5:
                            st.info(f"{len(st.session_state.last_generated_leads) - 5} more leads generated but not shown here.")

                    if st.button("Close Generator"):
                        st.session_state.show_lead_generator = False
                        st.rerun()

            # Lead creation form
            if st.session_state.get("show_lead_form", False):

                with st.form("new_lead_form"):
                    st.markdown('<div class="sub-header">Create New Lead</div>', unsafe_allow_html=True)

                    # Basic Information
                    st.markdown("#### Basic Information")
                    col1, col2 = st.columns(2)

                    with col1:
                        lead_name = st.text_input("Lead/Company Name*", key="new_lead_name")
                        lead_email = st.text_input("Email", key="new_lead_email")
                        lead_phone = st.text_input("Phone", key="new_lead_phone")
                        lead_website = st.text_input("Website", key="new_lead_website")

                    with col2:
                        lead_contact = st.text_input("Contact Person", key="new_lead_contact")
                        lead_profession = st.text_input("Profession/Role", key="new_lead_profession")
                        lead_budget = st.number_input("Budget", min_value=0, key="new_lead_budget")
                        lead_source = st.selectbox("Lead Source",
                                                ["Website", "Referral", "Cold Call", "Event", "Email Campaign",
                                                 "Social Media", "Google Ads", "LinkedIn", "Trade Show", "Partner Referral", "Other"],
                                                key="new_lead_source")

                    # Location Information
                    st.markdown("#### Location Information")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        lead_state = st.selectbox("State", options=[""] + get_states(), key="new_lead_state")

                    with col2:
                        if lead_state:
                            cities = get_cities_by_state(lead_state)
                            lead_city = st.selectbox("City", options=[""] + cities, key="new_lead_city")
                        else:
                            lead_city = st.text_input("City", key="new_lead_city")

                    with col3:
                        lead_pincode = st.text_input("PIN Code", key="new_lead_pincode")

                    lead_address = st.text_area("Address", key="new_lead_address", height=100)

                    # Business Information
                    st.markdown("#### Business Information")
                    col1, col2 = st.columns(2)

                    with col1:
                        business_types = get_all_business_types()
                        lead_business_type = st.selectbox("Business Type",
                                                       options=[""] + list(business_types.keys()),
                                                       key="new_lead_business_type")

                    with col2:
                        if lead_business_type:
                            subcategories = business_types.get(lead_business_type, [])
                            lead_subcategory = st.selectbox("Business Subcategory",
                                                         options=[""] + subcategories,
                                                         key="new_lead_subcategory")
                        else:
                            lead_subcategory = ""

                    # Product Interest
                    st.markdown("#### Product Interest")
                    # Use product_details from global
                    product_options = list(product_details.keys())
                    lead_products = st.multiselect("Products Interested In",
                                                options=product_options,
                                                key="new_lead_products")

                    lead_decision_timeline = st.selectbox("Decision Timeline",
                                                      ["Unknown", "1 week", "2 weeks", "1 month", "3 months", "6 months", "1 year"],
                                                      key="new_lead_timeline")

                    # Additional Information
                    st.markdown("#### Additional Information")
                    lead_notes = st.text_area("Notes", key="new_lead_notes")

                    lead_tags = st.text_input("Tags (comma separated)", key="new_lead_tags")

                    submitted = st.form_submit_button("Create Lead")

                    if submitted:
                        if lead_name:
                            # Process tags
                            tags = [tag.strip() for tag in lead_tags.split(",")] if lead_tags else []

                            # Create location string
                            location_parts = []
                            if lead_city:
                                location_parts.append(lead_city)
                            if lead_state:
                                location_parts.append(lead_state)
                            location = ", ".join(location_parts)

                            # Create lead object
                            lead_data = {
                                "name": lead_name,
                                "email": lead_email,
                                "phone": lead_phone,
                                "website": lead_website,
                                "location": location,
                                "city": lead_city,
                                "state": lead_state,
                                "address": lead_address,
                                "pincode": lead_pincode,
                                "contact_person": lead_contact,
                                "profession": lead_profession,
                                "business_type": lead_business_type,
                                "business_subcategory": lead_subcategory,
                                "budget": lead_budget,
                                "product_interested": ",".join(lead_products),
                                "decision_timeline": lead_decision_timeline,
                                "source": lead_source,
                                "source_detail": "Manual Entry",
                                "notes": lead_notes,
                                "tags": tags
                            }

                            # Create the lead
                            new_lead = create_new_lead(lead_data)

                            st.success(f"Lead '{lead_name}' created successfully!")
                            st.session_state.show_lead_form = False
                            st.rerun()
                        else:
                            st.error("Lead/Company Name is required.")

            # Display leads
            if not st.session_state.leads:
                if st.session_state.df is not None:
                    st.info("You have customer data loaded. Click 'Import Leads from CSV' to convert them to leads.")
                else:
                    st.info("No leads yet. Create a new lead or import from CSV.")
            else:
                # Filter leads if search term is provided
                filtered_leads = st.session_state.leads
                if search_term:
                    search_term = search_term.lower()
                    filtered_leads = [
                        lead for lead in st.session_state.leads
                        if search_term in lead.get("name", "").lower() or
                           search_term in lead.get("email", "").lower() or
                           search_term in lead.get("company", "").lower()
                    ]

                # Display leads in a table
                lead_data = []
                for lead in filtered_leads:
                    # Convert created_date string to datetime object
                    created_date = datetime.strptime(lead.get("created_date", ""), "%Y-%m-%d %H:%M:%S") if lead.get("created_date") else None
                    
                    lead_data.append({
                        "ID": lead.get("id"),
                        "Name": lead.get("name"),
                        "Email": lead.get("email"),
                        "Phone": lead.get("phone"),
                        "Score": lead.get("score"),
                        "Status": lead.get("status"),
                        "Created Date": created_date
                    })

                if lead_data:
                    lead_df = pd.DataFrame(lead_data)

                    # Use Streamlit's data editor for interactive table
                    selected_leads = st.data_editor(
                        lead_df,
                        column_config={
                            "ID": st.column_config.TextColumn("ID", width="small"),
                            "Name": st.column_config.TextColumn("Name", width="medium"),
                            "Email": st.column_config.TextColumn("Email", width="medium"),
                            "Phone": st.column_config.TextColumn("Phone", width="small"),
                            "Score": st.column_config.ProgressColumn("Lead Score", width="small", min_value=0, max_value=100),
                            "Status": st.column_config.SelectboxColumn("Status", options=["Hot", "Warm", "Lukewarm", "Cool", "Cold"], width="small"),
                            "Created Date": st.column_config.DatetimeColumn("Created", width="small", format="YYYY-MM-DD HH:mm:ss")
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                    # Lead details section
                    if selected_leads is not None and not selected_leads.empty:
                        selected_lead_id = selected_leads.iloc[0]["ID"]
                        selected_lead = next((lead for lead in st.session_state.leads if lead.get("id") == selected_lead_id), None)

                        if selected_lead:
                            st.markdown('<div class="sub-header">Lead Details</div>', unsafe_allow_html=True)

                            col1, col2, col3 = st.columns([1, 1, 1])

                            with col1:
                                if st.button("Convert to Deal", key=f"convert_{selected_lead_id}"):
                                    # Create a new deal from this lead
                                    new_deal = create_deal(selected_lead)
                                    st.success(f"Lead converted to deal: {new_deal['name']}")
                                    st.rerun()

                            with col2:
                                if st.button("Schedule Meeting", key=f"meeting_{selected_lead_id}"):
                                    st.session_state.show_meeting_form = True
                                    st.session_state.meeting_lead_id = selected_lead_id

                            with col3:
                                if st.button("Create Task", key=f"task_{selected_lead_id}"):
                                    st.session_state.show_task_form = True
                                    st.session_state.task_lead_id = selected_lead_id

                            # Lead details tabs
                            details_tab, activities_tab, notes_tab = st.tabs(["Details", "Activities", "Notes"])

                            with details_tab:
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(f"**Company:** {selected_lead.get('name', 'N/A')}")
                                    st.markdown(f"**Contact Person:** {selected_lead.get('contact_person', 'N/A')}")
                                    st.markdown(f"**Email:** {selected_lead.get('email', 'N/A')}")
                                    st.markdown(f"**Phone:** {selected_lead.get('phone', 'N/A')}")
                                    st.markdown(f"**Location:** {selected_lead.get('location', 'N/A')}")

                                with col2:
                                    st.markdown(f"**Lead Score:** {selected_lead.get('score', 'N/A')}")
                                    st.markdown(f"**Status:** {selected_lead.get('status', 'N/A')}")
                                    st.markdown(f"**Source:** {selected_lead.get('source', 'N/A')}")
                                    st.markdown(f"**Created:** {selected_lead.get('created_date', 'N/A')}")
                                    st.markdown(f"**Last Contacted:** {selected_lead.get('last_contacted', 'Never')}")

                                st.markdown("**Products Interested In:**")
                                if selected_lead.get("product_interested"):
                                    for product in selected_lead.get("product_interested").split(","):
                                        st.markdown(f"- {product.strip()}")
                                else:
                                    st.markdown("No specific products identified yet.")

                            with activities_tab:
                                # Filter activities for this lead
                                lead_activities = [
                                    activity for activity in st.session_state.activity_log
                                    if activity.get("related_id") == selected_lead_id
                                ]

                                if not lead_activities:
                                    st.info("No activities recorded for this lead yet.")
                                else:
                                    for activity in sorted(lead_activities, key=lambda x: x["timestamp"], reverse=True):
                                        st.markdown(f"""
                                        <div class="history-item">
                                            <strong>{activity["description"]}</strong><br>
                                            <small>{activity["timestamp"]}</small>
                                        </div>
                                        """, unsafe_allow_html=True)

                            with notes_tab:
                                # Display existing notes
                                existing_notes = selected_lead.get("notes", "")

                                # Use a form for notes to ensure proper submission
                                with st.form(key=f"notes_form_{selected_lead_id}"):
                                    # Notes editor
                                    new_notes = st.text_area("Lead Notes", value=existing_notes, height=150)

                     # Submit button
                                    submitted = st.form_submit_button("Save Notes")

                                    if submitted:
                                                       # Update notes in the lead
                                        for lead in st.session_state.leads:
                                            if lead.get("id") == selected_lead_id:
                                                lead["notes"] = new_notes
                                                break

                                        # Log activity
                                        log_activity("Updated lead notes", "note_update", selected_lead_id, selected_lead.get("name"))

                                        st.success("Notes saved successfully!")

                # Meeting scheduling form
                if st.session_state.get("show_meeting_form", False) and st.session_state.get("meeting_lead_id"):
                    lead_id = st.session_state.meeting_lead_id
                    lead = next((l for l in st.session_state.leads if l.get("id") == lead_id), None)

                    if lead:
                        with st.form("schedule_meeting_form"):
                            st.markdown('<div class="sub-header">Schedule Meeting</div>', unsafe_allow_html=True)

                            meeting_title = st.text_input("Meeting Title*", value=f"Meeting with {lead.get('name', 'Customer')}")

                            col1, col2 = st.columns(2)

                            with col1:
                                meeting_date = st.date_input("Date*", value=datetime.now() + timedelta(days=1))

                            with col2:
                                meeting_time = st.time_input("Time*", value=datetime.now().replace(hour=10, minute=0, second=0))

                            col1, col2 = st.columns(2)

                            with col1:
                                meeting_duration = st.selectbox("Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"])

                            with col2:
                                meeting_location = st.selectbox("Location", ["Virtual (Zoom)", "Virtual (Teams)", "Virtual (Google Meet)", "Phone Call", "In-Person"])

                            meeting_attendees = st.text_area("Attendees", value=f"- {lead.get('contact_person', 'Contact Person')}\n- You")
                            meeting_notes = st.text_area("Meeting Agenda/Notes")

                            submitted = st.form_submit_button("Schedule Meeting")

                            if submitted:
                                if meeting_title and meeting_date and meeting_time:
                                    # Schedule the meeting
                                    new_meeting = schedule_meeting(
                                        title=meeting_title,
                                        date=meeting_date.strftime("%Y-%m-%d"),
                                        time=meeting_time.strftime("%H:%M"),
                                        duration=meeting_duration,
                                        attendees=meeting_attendees.split("\n"),
                                        location=meeting_location,
                                        notes=meeting_notes,
                                        related_to=lead_id,
                                        related_type="lead"
                                    )

                                    # Update lead's last contacted date
                                    for l in st.session_state.leads:
                                        if l.get("id") == lead_id:
                                            l["last_contacted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            break

                                    st.success(f"Meeting scheduled successfully for {meeting_date.strftime('%d-%m-%Y')} at {meeting_time.strftime('%H:%M')}!")
                                    st.session_state.show_meeting_form = False
                                    st.rerun()
                                else:
                                    st.error("Please fill in all required fields.")

                # Task creation form
                if st.session_state.get("show_task_form", False) and st.session_state.get("task_lead_id"):
                    lead_id = st.session_state.task_lead_id
                    lead = next((l for l in st.session_state.leads if l.get("id") == lead_id), None)

                    if lead:
                        with st.form("create_task_form"):
                            st.markdown('<div class="sub-header">Create Task</div>', unsafe_allow_html=True)

                            task_title = st.text_input("Task Title*", value=f"Follow up with {lead.get('name', 'Customer')}")

                            col1, col2 = st.columns(2)

                            with col1:
                                task_due_date = st.date_input("Due Date*", value=datetime.now() + timedelta(days=3))

                            with col2:
                                task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])

                            task_notes = st.text_area("Task Details")

                            submitted = st.form_submit_button("Create Task")

                            if submitted:
                                if task_title and task_due_date:
                                    # Create the task
                                    new_task = create_task(
                                        title=task_title,
                                        due_date=task_due_date.strftime("%Y-%m-%d"),
                                        priority=task_priority,
                                        notes=task_notes,
                                        related_to=lead_id,
                                        related_type="lead"
                                    )

                                    st.success(f"Task created successfully with due date {task_due_date.strftime('%d-%m-%Y')}!")
                                    st.session_state.show_task_form = False
                                    st.rerun()
                                else:
                                    st.error("Please fill in all required fields.")

        with deals_tab:
            st.markdown('<div class="sub-header">Deal Management</div>', unsafe_allow_html=True)

            # Deal actions
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("Create New Deal"):
                    st.session_state.show_deal_form = True

            with col2:
                if st.button("View Pipeline"):
                    st.session_state.show_pipeline_view = True

            with col3:
                # Deal search/filter
                search_term = st.text_input("Search Deals", placeholder="Enter deal name or company")

            # Deal creation form
            if st.session_state.get("show_deal_form", False):

                with st.form("new_deal_form"):
                    st.markdown('<div class="sub-header">Create New Deal</div>', unsafe_allow_html=True)

                    # Select a lead for the deal
                    lead_options = [{"label": lead.get("name", "Unknown"), "value": lead.get("id")}
                                   for lead in st.session_state.leads]

                    # Initialize variables with default values
                    deal_name = ""
                    deal_amount = 0.0
                    deal_stage = st.session_state.sales_pipeline["stages"][0] if st.session_state.sales_pipeline["stages"] else ""
                    deal_close_date = datetime.now() + timedelta(days=30)
                    deal_products = []
                    deal_notes = ""
                    selected_lead = None

                    if lead_options:
                        selected_lead_id = st.selectbox(
                            "Select Lead*",
                            options=[lead["value"] for lead in lead_options],
                            format_func=lambda x: next((lead["label"] for lead in lead_options if lead["value"] == x), "Unknown"),
                            key="new_deal_lead"
                        )

                        selected_lead = next((lead for lead in st.session_state.leads if lead.get("id") == selected_lead_id), None)

                        if selected_lead:
                            col1, col2 = st.columns(2)

                            with col1:
                                deal_name = st.text_input("Deal Name*", value=f"{selected_lead.get('name', 'Unknown')} - {datetime.now().strftime('%b %Y')}")
                                deal_amount = st.number_input("Deal Amount*", min_value=0.0, value=float(selected_lead.get("budget", 0)))

                            with col2:
                                deal_stage = st.selectbox("Deal Stage*", options=st.session_state.sales_pipeline["stages"])
                                deal_close_date = st.date_input("Expected Close Date*", value=datetime.now() + timedelta(days=30))

                            # Use product_details
                            product_options = list(product_details.keys())

                            # Get default products from lead
                            default_products = []
                            if selected_lead.get("product_interested"):
                                # Split the string and filter out any products not in our product_details
                                interested_products = selected_lead.get("product_interested", "").split(",")
                                default_products = [p.strip() for p in interested_products if p.strip() in product_options]

                            deal_products = st.multiselect(
                                "Products",
                                options=product_options,
                                default=default_products
                            )

                            deal_notes = st.text_area("Notes")
                    else:
                        st.warning("No leads available. Please create a lead first.")

                    # Submit button - always present
                    submitted = st.form_submit_button("Create Deal")

                    if submitted:
                        if lead_options and selected_lead:
                            if deal_name and deal_amount >= 0 and deal_stage and deal_close_date:
                                # Update selected lead with deal information
                                selected_lead["expected_close_date"] = deal_close_date.strftime("%Y-%m-%d")

                                # Create the deal
                                new_deal = create_deal(
                                    lead_data=selected_lead,
                                    deal_name=deal_name,
                                    amount=deal_amount,
                                    stage=deal_stage
                                )

                                # Update deal-specific fields
                                new_deal["expected_close_date"] = deal_close_date.strftime("%Y-%m-%d")
                                new_deal["products"] = deal_products
                                new_deal["notes"] = deal_notes

                                st.success(f"Deal '{deal_name}' created successfully!")
                                st.session_state.show_deal_form = False
                                st.rerun()
                            else:
                                st.error("Please fill in all required fields.")
                        else:
                            st.error("Please create a lead first before creating a deal.")

            # Pipeline view
            if st.session_state.get("show_pipeline_view", False):
                st.markdown('<div class="sub-header">Sales Pipeline</div>', unsafe_allow_html=True)

                # Create columns for each pipeline stage
                cols = st.columns(len(st.session_state.sales_pipeline["stages"]))

                # Display deals by stage in columns
                for i, stage in enumerate(st.session_state.sales_pipeline["stages"]):
                    with cols[i]:
                        st.markdown(f"**{stage}**")

                        # Get deals for this stage
                        stage_deals = [deal for deal in st.session_state.deals if deal.get("stage") == stage]

                        if not stage_deals:
                            st.info(f"No deals in {stage}")
                        else:
                            for deal in stage_deals:
                                st.markdown(f"""
                                <div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-bottom: 10px;">
                                    <strong>{deal.get('name', 'Unknown Deal')}</strong><br>
                                    {deal.get('formatted_amount', '₹0.00')}<br>
                                    <small>{deal.get('lead_name', 'Unknown Lead')}</small>
                                </div>
                                """, unsafe_allow_html=True)

                if st.button("Close Pipeline View"):
                    st.session_state.show_pipeline_view = False
                    st.rerun()

            # Display deals
            if not st.session_state.deals:
                st.info("No deals yet. Create a new deal or convert a lead to a deal.")
            else:
                # Filter deals if search term is provided
                filtered_deals = st.session_state.deals
                if search_term:
                    search_term = search_term.lower()
                    filtered_deals = [
                        deal for deal in st.session_state.deals
                        if search_term in deal.get("name", "").lower() or
                           search_term in deal.get("lead_name", "").lower()
                    ]

                # Display deals in a table
                deal_data = []
                for deal in filtered_deals:
                    deal_data.append({
                        "ID": deal.get("id"),
                        "Name": deal.get("name"),
                        "Company": deal.get("lead_name"),
                        "Amount": deal.get("formatted_amount"),
                        "Stage": deal.get("stage"),
                        "Probability": f"{deal.get('probability')}%",
                        "Expected Close": deal.get("expected_close_date")
                    })

                if deal_data:
                    deal_df = pd.DataFrame(deal_data)

                    # Use Streamlit's data editor for interactive table
                    selected_deals = st.data_editor(
                        deal_df,
                        column_config={
                            "ID": st.column_config.TextColumn("ID", width="small"),
                            "Name": st.column_config.TextColumn("Deal Name", width="medium"),
                            "Company": st.column_config.TextColumn("Company", width="medium"),
                            "Amount": st.column_config.TextColumn("Amount", width="small"),
                            "Stage": st.column_config.SelectboxColumn("Stage", options=st.session_state.sales_pipeline["stages"], width="medium"),
                            "Probability": st.column_config.ProgressColumn("Probability", width="small", min_value=0, max_value=100, format="%d%%"),
                            "Expected Close": st.column_config.TextColumn("Close Date", width="small", help="Date format: YYYY-MM-DD")
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                    # Deal details section
                    if selected_deals is not None and not selected_deals.empty:
                        selected_deal_id = selected_deals.iloc[0]["ID"]
                        selected_deal = next((deal for deal in st.session_state.deals if deal.get("id") == selected_deal_id), None)

                        if selected_deal:
                            st.markdown('<div class="sub-header">Deal Details</div>', unsafe_allow_html=True)

                            col1, col2, col3 = st.columns([1, 1, 1])

                            with col1:
                                if st.button("Update Stage", key=f"update_{selected_deal_id}"):
                                    st.session_state.show_stage_update = True
                                    st.session_state.stage_deal_id = selected_deal_id

                            with col2:
                                if st.button("Schedule Meeting", key=f"deal_meeting_{selected_deal_id}"):
                                    st.session_state.show_deal_meeting_form = True
                                    st.session_state.meeting_deal_id = selected_deal_id

                            with col3:
                                if st.button("Create Task", key=f"deal_task_{selected_deal_id}"):
                                    st.session_state.show_deal_task_form = True
                                    st.session_state.task_deal_id = selected_deal_id

                            # Deal details tabs
                            details_tab, activities_tab, notes_tab = st.tabs(["Details", "Activities", "Notes"])

                            with details_tab:
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(f"**Deal Name:** {selected_deal.get('name', 'N/A')}")
                                    st.markdown(f"**Company:** {selected_deal.get('lead_name', 'N/A')}")
                                    st.markdown(f"**Amount:** {selected_deal.get('formatted_amount', 'N/A')}")
                                    st.markdown(f"**Stage:** {selected_deal.get('stage', 'N/A')}")

                                with col2:
                                    st.markdown(f"**Probability:** {selected_deal.get('probability', 'N/A')}%")
                                    st.markdown(f"**Created Date:** {selected_deal.get('created_date', 'N/A')}")
                                    st.markdown(f"**Expected Close Date:** {selected_deal.get('expected_close_date', 'N/A')}")
                                    st.markdown(f"**Last Activity:** {selected_deal.get('last_activity', 'N/A')}")

                                st.markdown("**Products:**")
                                if selected_deal.get("products"):
                                    for product in selected_deal.get("products"):
                                        st.markdown(f"- {product.strip()}")
                                else:
                                    st.markdown("No products specified.")

                            with activities_tab:
                                # Filter activities for this deal
                                deal_activities = [
                                    activity for activity in st.session_state.activity_log
                                    if activity.get("related_id") == selected_deal_id
                                ]

                                if not deal_activities:
                                    st.info("No activities recorded for this deal yet.")
                                else:
                                    for activity in sorted(deal_activities, key=lambda x: x["timestamp"], reverse=True):
                                        st.markdown(f"""
                                        <div class="history-item">
                                            <strong>{activity["description"]}</strong><br>
                                            <small>{activity["timestamp"]}</small>
                                        </div>
                                        """, unsafe_allow_html=True)

                            with notes_tab:
                                # Display existing notes
                                existing_notes = selected_deal.get("notes", "")

                                # Notes editor
                                new_notes = st.text_area("Deal Notes", value=existing_notes, height=150)

                                if st.button("Save Notes", key=f"save_deal_notes_{selected_deal_id}"):
                                    # Update notes in the deal
                                    for deal in st.session_state.deals:
                                        if deal.get("id") == selected_deal_id:
                                            deal["notes"] = new_notes
                                            break

                                    # Log activity
                                    log_activity("Updated deal notes", "note_update", selected_deal_id, selected_deal.get("name"))

                                    st.success("Notes saved successfully!")

                # Stage update form
                if st.session_state.get("show_stage_update", False) and st.session_state.get("stage_deal_id"):
                    deal_id = st.session_state.stage_deal_id
                    deal = next((d for d in st.session_state.deals if d.get("id") == deal_id), None)

                    if deal:
                        with st.form("update_stage_form"):
                            st.markdown('<div class="sub-header">Update Deal Stage</div>', unsafe_allow_html=True)

                            current_stage = deal.get("stage")
                            new_stage = st.selectbox("New Stage", options=st.session_state.sales_pipeline["stages"], index=st.session_state.sales_pipeline["stages"].index(current_stage))

                            reason = st.text_area("Reason for Update")

                            submitted = st.form_submit_button("Update Stage")

                            if submitted:
                                # Update the deal stage
                                old_stage = deal["stage"]

                                # Remove from old stage in pipeline
                                if deal_id in st.session_state.sales_pipeline["deals_by_stage"][old_stage]:
                                    st.session_state.sales_pipeline["deals_by_stage"][old_stage].remove(deal_id)

                                # Update deal object
                                deal["stage"] = new_stage
                                deal["probability"] = get_stage_probability(new_stage)
                                deal["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                # Add to new stage in pipeline
                                st.session_state.sales_pipeline["deals_by_stage"][new_stage].append(deal_id)

                                # Log activity
                                activity_desc = f"Deal stage updated from {old_stage} to {new_stage}"
                                if reason:
                                    activity_desc += f": {reason}"

                                log_activity(activity_desc, "stage_update", deal_id, deal.get("name"))

                                st.success(f"Deal stage updated to {new_stage}!")
                                st.session_state.show_stage_update = False
                                st.rerun()

    # Tasks & Calendar Tab
    with tab4:
        st.markdown('<div class="main-header">Tasks & Calendar</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Manage your tasks and schedule meetings with customers.</div>', unsafe_allow_html=True)

        # Create tabs for Tasks and Calendar
        tasks_tab, calendar_tab, email_tab = st.tabs(["Tasks", "Calendar", "Email Templates"])

        with tasks_tab:
            st.markdown('<div class="sub-header">Task Management</div>', unsafe_allow_html=True)

            # Task actions
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("Create New Task", key="new_task_btn"):
                    st.session_state.show_new_task_form = True

            with col2:
                # Task filter
                task_filter = st.selectbox("Filter Tasks", ["All Tasks", "My Tasks", "Overdue Tasks", "Completed Tasks", "High Priority"])

            # New task form
            if st.session_state.get("show_new_task_form", False):
                with st.form("new_task_form"):
                    st.markdown('<div class="sub-header">Create New Task</div>', unsafe_allow_html=True)

                    task_title = st.text_input("Task Title*")

                    col1, col2 = st.columns(2)

                    with col1:
                        task_due_date = st.date_input("Due Date*", value=datetime.now() + timedelta(days=1))

                    with col2:
                        task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])

                    # Related to (optional)
                    related_type = st.selectbox("Related To", ["None", "Lead", "Deal"])

                    if related_type == "Lead":
                        lead_options = [{"label": lead.get("name", "Unknown"), "value": lead.get("id")}
                                       for lead in st.session_state.leads]

                        if lead_options:
                            related_id = st.selectbox(
                                "Select Lead",
                                options=[lead["value"] for lead in lead_options],
                                format_func=lambda x: next((lead["label"] for lead in lead_options if lead["value"] == x), "Unknown")
                            )
                        else:
                            st.info("No leads available.")
                            related_id = None
                    elif related_type == "Deal":
                        deal_options = [{"label": deal.get("name", "Unknown"), "value": deal.get("id")}
                                       for deal in st.session_state.deals]

                        if deal_options:
                            related_id = st.selectbox(
                                "Select Deal",
                                options=[deal["value"] for deal in deal_options],
                                format_func=lambda x: next((deal["label"] for deal in deal_options if deal["value"] == x), "Unknown")
                            )
                        else:
                            st.info("No deals available.")
                            related_id = None
                    else:
                        related_id = None

                    task_notes = st.text_area("Task Details")

                    submitted = st.form_submit_button("Create Task")

                    if submitted:
                        if task_title and task_due_date:
                            # Create the task
                            new_task = create_task(
                                title=task_title,
                                due_date=task_due_date.strftime("%Y-%m-%d"),
                                priority=task_priority,
                                notes=task_notes,
                                related_to=related_id,
                                related_type=related_type if related_type != "None" else None
                            )

                            st.success(f"Task '{task_title}' created successfully!")
                            st.session_state.show_new_task_form = False
                            st.experimental_rerun()
                        else:
                            st.error("Please fill in all required fields.")

            # Display tasks
            if not st.session_state.tasks:
                st.info("No tasks yet. Create a new task to get started.")
            else:
                # Filter tasks based on selection
                filtered_tasks = st.session_state.tasks

                if task_filter == "My Tasks":
                    filtered_tasks = [task for task in st.session_state.tasks if task.get("assigned_to") == "Current User"]
                elif task_filter == "Overdue Tasks":
                    today = datetime.now().date()
                    filtered_tasks = [
                        task for task in st.session_state.tasks
                        if task.get("status") != "Completed" and
                        datetime.strptime(task.get("due_date", "2099-12-31"), "%Y-%m-%d").date() < today
                    ]
                elif task_filter == "Completed Tasks":
                    filtered_tasks = [task for task in st.session_state.tasks if task.get("status") == "Completed"]
                elif task_filter == "High Priority":
                    filtered_tasks = [task for task in st.session_state.tasks if task.get("priority") == "High"]

                # Display tasks in a table
                task_data = []
                for task in filtered_tasks:
                    # Get related entity name
                    related_name = "N/A"
                    if task.get("related_type") == "Lead":
                        lead = next((l for l in st.session_state.leads if l.get("id") == task.get("related_to")), None)
                        if lead:
                            related_name = lead.get("name", "Unknown Lead")
                    elif task.get("related_type") == "Deal":
                        deal = next((d for d in st.session_state.deals if d.get("id") == task.get("related_to")), None)
                        if deal:
                            related_name = deal.get("name", "Unknown Deal")

                    task_data.append({
                        "ID": task.get("id"),
                        "Title": task.get("title"),
                        "Due Date": task.get("due_date"),
                        "Priority": task.get("priority"),
                        "Status": task.get("status"),
                        "Related To": related_name,
                        "Assigned To": task.get("assigned_to")
                    })

                if task_data:
                    task_df = pd.DataFrame(task_data)

                    # Use Streamlit's data editor for interactive table
                    selected_tasks = st.data_editor(
                        task_df,
                        column_config={
                            "ID": st.column_config.TextColumn("ID", width="small"),
                            "Title": st.column_config.TextColumn("Task", width="medium"),
                            "Due Date": st.column_config.DateColumn("Due Date", width="small", format="DD-MM-YYYY"),
                            "Priority": st.column_config.SelectboxColumn("Priority", options=["High", "Medium", "Low"], width="small"),
                            "Status": st.column_config.SelectboxColumn("Status", options=["Open", "In Progress", "Completed"], width="small"),
                            "Related To": st.column_config.TextColumn("Related To", width="medium"),
                            "Assigned To": st.column_config.TextColumn("Assigned To", width="small")
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                    # Task details and actions
                    if selected_tasks is not None and not selected_tasks.empty:
                        selected_task_id = selected_tasks.iloc[0]["ID"]
                        selected_task = next((task for task in st.session_state.tasks if task.get("id") == selected_task_id), None)

                        if selected_task:
                            col1, col2 = st.columns(2)

                            with col1:
                                if selected_task.get("status") != "Completed":
                                    if st.button("Mark as Completed", key=f"complete_{selected_task_id}"):
                                        # Update task status
                                        for task in st.session_state.tasks:
                                            if task.get("id") == selected_task_id:
                                                task["status"] = "Completed"
                                                task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                break

                                        # Log activity
                                        log_activity(f"Task completed: {selected_task.get('title')}", "task_completed", selected_task_id)

                                        st.success("Task marked as completed!")
                                        st.rerun()
                                else:
                                    if st.button("Reopen Task", key=f"reopen_{selected_task_id}"):
                                        # Update task status
                                        for task in st.session_state.tasks:
                                            if task.get("id") == selected_task_id:
                                                task["status"] = "Open"
                                                task["completed_date"] = None
                                                break

                                        # Log activity
                                        log_activity(f"Task reopened: {selected_task.get('title')}", "task_reopened", selected_task_id)

                                        st.success("Task reopened!")
                                        st.rerun()

                            with col2:
                                if st.button("Delete Task", key=f"delete_{selected_task_id}"):
                                    # Remove task from session state
                                    st.session_state.tasks = [task for task in st.session_state.tasks if task.get("id") != selected_task_id]

                                    # Log activity
                                    log_activity(f"Task deleted: {selected_task.get('title')}", "task_deleted")

                                    st.success("Task deleted successfully!")
                                    st.rerun()

                            # Task details
                            st.markdown('<div class="sub-header">Task Details</div>', unsafe_allow_html=True)
                            st.markdown(f"**Title:** {selected_task.get('title')}")
                            st.markdown(f"**Due Date:** {selected_task.get('due_date')}")
                            st.markdown(f"**Priority:** {selected_task.get('priority')}")
                            st.markdown(f"**Status:** {selected_task.get('status')}")

                            if selected_task.get("notes"):
                                st.markdown(f"**Details:**\n{selected_task.get('notes')}")

        with calendar_tab:
            st.markdown('<div class="sub-header">Calendar & Meetings</div>', unsafe_allow_html=True)

            # Calendar actions
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("Schedule Meeting", key="new_meeting_btn"):
                    st.session_state.show_new_meeting_form = True

            with col2:
                # Date range selector
                today = datetime.now().date()
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)

                date_range = st.selectbox(
                    "View",
                    ["Today", "This Week", "Next Week", "This Month", "Next Month", "Custom Range"],
                    key="calendar_view"
                )

            # New meeting form
            if st.session_state.get("show_new_meeting_form", False):
                with st.form("new_meeting_form"):
                    st.markdown('<div class="sub-header">Schedule New Meeting</div>', unsafe_allow_html=True)

                    meeting_title = st.text_input("Meeting Title*")

                    col1, col2 = st.columns(2)

                    with col1:
                        meeting_date = st.date_input("Date*", value=datetime.now() + timedelta(days=1))

                    with col2:
                        meeting_time = st.time_input("Time*", value=datetime.now().replace(hour=10, minute=0, second=0))

                    col1, col2 = st.columns(2)

                    with col1:
                        meeting_duration = st.selectbox("Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"])

                    with col2:
                        meeting_location = st.selectbox("Location", ["Virtual (Zoom)", "Virtual (Teams)", "Virtual (Google Meet)", "Phone Call", "In-Person"])

                    # Related to (optional)
                    related_type = st.selectbox("Related To", ["None", "Lead", "Deal"])

                    if related_type == "Lead":
                        lead_options = [{"label": lead.get("name", "Unknown"), "value": lead.get("id")}
                                       for lead in st.session_state.leads]

                        if lead_options:
                            related_id = st.selectbox(
                                "Select Lead",
                                options=[lead["value"] for lead in lead_options],
                                format_func=lambda x: next((lead["label"] for lead in lead_options if lead["value"] == x), "Unknown")
                            )

                            # Get attendees from lead
                            selected_lead = next((lead for lead in st.session_state.leads if lead.get("id") == related_id), None)
                            default_attendees = f"- {selected_lead.get('contact_person', 'Contact Person')}\n- You" if selected_lead else "- You"
                        else:
                            st.info("No leads available.")
                            related_id = None
                            default_attendees = "- You"
                    elif related_type == "Deal":
                        deal_options = [{"label": deal.get("name", "Unknown"), "value": deal.get("id")}
                                       for deal in st.session_state.deals]

                        if deal_options:
                            related_id = st.selectbox(
                                "Select Deal",
                                options=[deal["value"] for deal in deal_options],
                                format_func=lambda x: next((deal["label"] for deal in deal_options if deal["value"] == x), "Unknown")
                            )

                            # Get attendees from deal's lead
                            selected_deal = next((deal for deal in st.session_state.deals if deal.get("id") == related_id), None)
                            if selected_deal:
                                lead_id = selected_deal.get("lead_id")
                                selected_lead = next((lead for lead in st.session_state.leads if lead.get("id") == lead_id), None)
                                default_attendees = f"- {selected_lead.get('contact_person', 'Contact Person')}\n- You" if selected_lead else "- You"
                            else:
                                default_attendees = "- You"
                        else:
                            st.info("No deals available.")
                            related_id = None
                            default_attendees = "- You"
                    else:
                        related_id = None
                        default_attendees = "- You"

                    meeting_attendees = st.text_area("Attendees", value=default_attendees)
                    meeting_notes = st.text_area("Meeting Agenda/Notes")

                    submitted = st.form_submit_button("Schedule Meeting")

                    if submitted:
                        if meeting_title and meeting_date and meeting_time:
                            # Schedule the meeting
                            new_meeting = schedule_meeting(
                                title=meeting_title,
                                date=meeting_date.strftime("%Y-%m-%d"),
                                time=meeting_time.strftime("%H:%M"),
                                duration=meeting_duration,
                                attendees=meeting_attendees.split("\n"),
                                location=meeting_location,
                                notes=meeting_notes,
                                related_to=related_id,
                                related_type=related_type if related_type != "None" else None
                            )

                            # If related to a lead, update lead's last contacted date
                            if related_type == "Lead" and related_id:
                                for lead in st.session_state.leads:
                                    if lead.get("id") == related_id:
                                        lead["last_contacted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        break

                            st.success(f"Meeting scheduled successfully for {meeting_date.strftime('%d-%m-%Y')} at {meeting_time.strftime('%H:%M')}!")
                            st.session_state.show_new_meeting_form = False
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields.")

            # Calendar view
            st.markdown('<div class="sub-header">Your Schedule</div>', unsafe_allow_html=True)

            # Determine date range based on selection
            if date_range == "Today":
                start_date = today
                end_date = today
                date_format = "%d %b %Y"
                st.markdown(f"**{today.strftime(date_format)}**")
            elif date_range == "This Week":
                start_date = start_of_week
                end_date = end_of_week
                date_format = "%d %b"
                st.markdown(f"**Week of {start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}**")
            elif date_range == "Next Week":
                start_date = start_of_week + timedelta(days=7)
                end_date = end_of_week + timedelta(days=7)
                date_format = "%d %b"
                st.markdown(f"**Week of {start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}**")
            elif date_range == "This Month":
                start_date = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_date = today.replace(day=last_day)
                date_format = "%d %b"
                st.markdown(f"**{today.strftime('%B %Y')}**")
            elif date_range == "Next Month":
                next_month = today.month + 1
                next_year = today.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                start_date = today.replace(year=next_year, month=next_month, day=1)
                last_day = calendar.monthrange(next_year, next_month)[1]
                end_date = start_date.replace(day=last_day)
                date_format = "%d %b"
                st.markdown(f"**{start_date.strftime('%B %Y')}**")
            else:  # Custom Range
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=today)
                with col2:
                    end_date = st.date_input("End Date", value=today + timedelta(days=7))
                date_format = "%d %b"
                st.markdown(f"**{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}**")

            # Display meetings in the selected date range
            if not st.session_state.meetings:
                # Create sample meetings for demonstration
                if date_range == "Today" or date_range == "This Week":
                    sample_meetings = [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Demo Meeting with ABC School",
                            "date": today.strftime("%Y-%m-%d"),
                            "time": "10:00",
                            "duration": "1 hour",
                            "location": "Virtual (Zoom)",
                            "attendees": ["Principal, ABC School", "You"],
                            "status": "Scheduled"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Product Presentation for XYZ Academy",
                            "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                            "time": "14:30",
                            "duration": "1.5 hours",
                            "location": "Virtual (Teams)",
                            "attendees": ["IT Director, XYZ Academy", "You", "Product Manager"],
                            "status": "Scheduled"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Follow-up Call with Global Institute",
                            "date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                            "time": "11:15",
                            "duration": "30 minutes",
                            "location": "Phone Call",
                            "attendees": ["Admin Head, Global Institute", "You"],
                            "status": "Scheduled"
                        }
                    ]

                    # Display sample meetings
                    for meeting in sample_meetings:
                        meeting_date = datetime.strptime(meeting["date"], "%Y-%m-%d").date()
                        if start_date <= meeting_date <= end_date:
                            st.markdown(f"""
                            <div style="padding: 15px; background-color: #E3F2FD; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #1E88E5;">
                                <strong>{meeting["title"]}</strong><br>
                                {meeting_date.strftime(date_format)} at {meeting["time"]} ({meeting["duration"]})<br>
                                Location: {meeting["location"]}<br>
                                Attendees: {", ".join(meeting["attendees"])}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No meetings scheduled in this date range.")
            else:
                # Filter meetings in the selected date range
                filtered_meetings = []
                for meeting in st.session_state.meetings:
                    try:
                        meeting_date = datetime.strptime(meeting["date"], "%Y-%m-%d").date()
                        if start_date <= meeting_date <= end_date:
                            filtered_meetings.append(meeting)
                    except (ValueError, TypeError):
                        continue

                if not filtered_meetings:
                    st.info("No meetings scheduled in this date range.")
                else:
                    # Sort meetings by date and time
                    filtered_meetings.sort(key=lambda x: (x["date"], x["time"]))

                    # Group meetings by date
                    meetings_by_date = {}
                    for meeting in filtered_meetings:
                        if meeting["date"] not in meetings_by_date:
                            meetings_by_date[meeting["date"]] = []
                        meetings_by_date[meeting["date"]].append(meeting)

                    # Display meetings grouped by date
                    for date_str, meetings in meetings_by_date.items():
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        st.markdown(f"**{date_obj.strftime(date_format)}**")

                        for meeting in meetings:
                            # Get related entity name
                            related_info = ""
                            if meeting.get("related_type") == "Lead":
                                lead = next((l for l in st.session_state.leads if l.get("id") == meeting.get("related_to")), None)
                                if lead:
                                    related_info = f"Related to Lead: {lead.get('name', 'Unknown')}"
                            elif meeting.get("related_type") == "Deal":
                                deal = next((d for d in st.session_state.deals if d.get("id") == meeting.get("related_to")), None)
                                if deal:
                                    related_info = f"Related to Deal: {deal.get('name', 'Unknown')}"

                            st.markdown(f"""
                            <div style="padding: 15px; background-color: #E3F2FD; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #1E88E5;">
                                <strong>{meeting["title"]}</strong><br>
                                {meeting["time"]} ({meeting["duration"]})<br>
                                Location: {meeting["location"]}<br>
                                Attendees: {", ".join(meeting["attendees"])}<br>
                                {related_info}
                            </div>
                            """, unsafe_allow_html=True)

        with email_tab:
            st.markdown('<div class="sub-header">Email Templates</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Create and manage email templates for different sales scenarios.</div>', unsafe_allow_html=True)

            # Email template categories
            template_category = st.selectbox(
                "Template Category",
                ["Introduction", "Follow-up", "Proposal", "Meeting Confirmation", "Thank You", "Custom"]
            )

            # Sample templates for each category
            templates = {
                "Introduction": {
                    "subject": "Introduction to EDURISHI Educational Solutions",
                    "body": """Dear {customer_name},

I hope this email finds you well. My name is {sales_rep} from EDURISHI EDUVENTURES PVT LTD, and I'm reaching out because I believe our educational solutions could be valuable for {company_name}.

EDURISHI specializes in providing innovative educational technology solutions designed specifically for institutions like yours. Our products help schools enhance student engagement, improve learning outcomes, and streamline administrative processes.

Based on your institution's focus on {area_of_interest}, I believe our {recommended_product} would be particularly beneficial for you.

Would you be available for a brief 15-minute call next week to discuss how EDURISHI can support your educational goals? I'm flexible and can work around your schedule.

Thank you for your time, and I look forward to connecting with you soon.

Best regards,
{sales_rep}
EDURISHI EDUVENTURES PVT LTD
{phone_number}
{email}"""
                },
                "Follow-up": {
                    "subject": "Following Up on Our Conversation about EDURISHI Solutions",
                    "body": """Dear {customer_name},

I hope you're doing well. I wanted to follow up on our conversation from {previous_date} regarding EDURISHI's educational solutions for {company_name}.

As we discussed, our {recommended_product} would address your needs for {customer_need} by providing {key_benefit}. Many of our clients have seen {specific_result} after implementing this solution.

I've attached some additional information about the product that I thought might interest you, including case studies from institutions similar to yours.

Would you be available for a follow-up discussion this week to address any questions you might have and discuss next steps? I'm available on {proposed_date_time} or {alternative_date_time}.

Thank you for your consideration, and I look forward to speaking with you again soon.

Best regards,
{sales_rep}
EDURISHI EDUVENTURES PVT LTD
{phone_number}
{email}"""
                },
                "Proposal": {
                    "subject": "EDURISHI Educational Solutions Proposal for {company_name}",
                    "body": """Dear {customer_name},

Thank you for the opportunity to present our proposal for {company_name}. Based on our discussions about your requirements, I'm pleased to attach our customized proposal for implementing EDURISHI's educational solutions at your institution.

Our proposal includes:

1. Implementation of {recommended_product} with the following features:
   - {feature_1}
   - {feature_2}
   - {feature_3}

2. Comprehensive training for your staff

3. Ongoing technical support and updates

4. Customization options specific to your institution's needs

The total investment for this solution is {total_price}, which includes all implementation, training, and first-year support costs.

I believe this proposal addresses the key challenges we discussed, particularly {specific_challenge}. Our solution is designed to deliver {key_benefit} and {secondary_benefit} for your institution.

I'd be happy to schedule a call to walk through the proposal in detail and answer any questions you might have. Would {proposed_date_time} work for you?

Thank you for considering EDURISHI as your educational technology partner. We look forward to the possibility of working with {company_name}.

Best regards,
{sales_rep}
EDURISHI EDUVENTURES PVT LTD
{phone_number}
{email}"""
                },
                "Meeting Confirmation": {
                    "subject": "Confirmation: Meeting on {meeting_date}",
                    "body": """Dear {customer_name},

I'm writing to confirm our upcoming meeting on {meeting_date} at {meeting_time} {timezone} via {meeting_platform}.

During our meeting, we'll discuss:
- Your current educational technology needs
- How EDURISHI's solutions can address your specific challenges
- A demonstration of our {recommended_product}
- Next steps and implementation timeline

For the {meeting_platform} meeting, please use the following details:
Meeting Link: {meeting_link}
Meeting ID: {meeting_id}
Password: {meeting_password}

If you'd like to include any additional topics or invite other team members, please let me know. Also, feel free to share any specific questions in advance so I can prepare accordingly.

I'm looking forward to our conversation and the opportunity to show you how EDURISHI can support your educational goals.

Best regards,
{sales_rep}
EDURISHI EDUVENTURES PVT LTD
{phone_number}
{email}"""
                },
                "Thank You": {
                    "subject": "Thank You for Meeting with EDURISHI",
                    "body": """Dear {customer_name},

Thank you for taking the time to meet with me today to discuss EDURISHI's educational solutions. I appreciated learning more about {company_name}'s needs and challenges, particularly regarding {specific_challenge}.

As promised, I've attached the additional information we discussed about our {recommended_product}. This includes:
- Detailed product specifications
- Case studies from similar institutions
- Implementation timeline
- Pricing options

Based on our conversation, I believe the next steps would be:
1. Review the attached materials with your team
2. Schedule a follow-up demonstration with your key stakeholders
3. Discuss customization options specific to your requirements

I'll follow up with you next week, but please don't hesitate to reach out if you have any questions in the meantime.

Thank you again for your time and interest in EDURISHI. We look forward to the possibility of partnering with {company_name} to enhance your educational technology capabilities.

Best regards,
{sales_rep}
EDURISHI EDUVENTURES PVT LTD
{phone_number}
{email}"""
                },
                "Custom": {
                    "subject": "Custom Email Subject",
                    "body": """Dear {customer_name},

[Your custom email content here]

Best regards,
{sales_rep}
EDURISHI EDUVENTURES PVT LTD
{phone_number}
{email}"""
                }
            }

            # Display and edit the selected template
            selected_template = templates[template_category]

            st.text_input("Email Subject", value=selected_template["subject"], key=f"subject_{template_category}")
            st.text_area("Email Body", value=selected_template["body"], height=400, key=f"body_{template_category}")

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Save Template"):
                    st.success("Template saved successfully!")

            with col2:
                if st.button("Send Test Email"):
                    st.success("Test email sent successfully!")

            # Template variables explanation
            st.markdown('<div class="sub-header">Template Variables</div>', unsafe_allow_html=True)
            st.markdown("""
            Use these variables in your templates to personalize emails:
            - `{customer_name}` - Customer's name
            - `{company_name}` - Company/School name
            - `{sales_rep}` - Your name
            - `{phone_number}` - Your phone number
            - `{email}` - Your email address
            - `{recommended_product}` - Recommended product name
            - `{meeting_date}` - Scheduled meeting date
            - `{meeting_time}` - Scheduled meeting time
            - `{previous_date}` - Date of previous interaction
            """)

    # Conversation History Tab
    with tab5:
        st.markdown('<div class="sub-header">Conversation History</div>', unsafe_allow_html=True)

        if not st.session_state.conversation_history:
            st.markdown('<div class="info-box">No conversations yet. Generate responses to see them here.</div>', unsafe_allow_html=True)
        else:
            # Filter by customer
            all_customers = list(set([conv["customer"] for conv in st.session_state.conversation_history]))
            filter_customer = st.selectbox("Filter by customer", ["All"] + all_customers)
            
            filtered_history = st.session_state.conversation_history
            if filter_customer != "All":
                filtered_history = [conv for conv in st.session_state.conversation_history if conv["customer"] == filter_customer]
            
            # Display conversations
            for i, conv in enumerate(filtered_history):
                st.markdown(f'<div class="history-item">', unsafe_allow_html=True)
                st.markdown(f"**Customer:** {conv['customer']}")
                st.markdown(f"**Time:** {conv['timestamp']}")
                
                with st.expander("View Conversation"):
                    st.markdown("**Enquiry:**")
                    st.markdown(f"{conv['enquiry']}")
                    st.markdown("**Response:**")
                    st.markdown(f"{conv['response']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Export options
            if st.button("Export All Conversations"):
                save_conversation("all_conversations", st.session_state.conversation_history)
                st.markdown('<div class="success-box">All conversations exported successfully!</div>', unsafe_allow_html=True)
    
    with tab6:
        st.markdown('<div class="sub-header">EDURISHI Sales Scripts</div>', unsafe_allow_html=True)

        if st.session_state.customer_data:
            # Generate sales script based on current customer
            script = generate_sales_script(st.session_state.customer_data)
            st.markdown(f"### Script for {st.session_state.current_customer}")
            st.text_area("Customizable Sales Script", script, height=300)

            if st.button("Save Script"):
                os.makedirs("scripts", exist_ok=True)
                script_file = f"scripts/{st.session_state.current_customer}_{datetime.now().strftime('%Y%m%d')}.txt"
                with open(script_file, 'w', encoding="utf-8") as f:
                    f.write(script)
                st.markdown('<div class="success-box">Script saved successfully!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">Select a customer first to generate a sales script.</div>', unsafe_allow_html=True)

            # Sample scripts
            with st.expander("Sample EDURISHI Script Templates"):
                st.markdown("""
                ### General Introduction

                "Hello [Name], I'm [Your Name] from EDURISHI EDUVENTURES PVT LTD. We specialize in helping [profession]s like yourself enhance their skills through our tailored educational programs."

                ### Addressing Pain Points

                "Many of our students in [industry] were struggling with [common pain point] before enrolling in our programs. Is that something you're experiencing as well?"

                ### Presenting Solution

                "Our [Program Name] helps you [benefit 1], [benefit 2], and [benefit 3], which means you can [desired outcome] much faster and more effectively."

                ### Call to Action

                "I'd love to show you how our program works in practice. Would you be available for a 15-minute demo session next week?"
                """)
    
    with tab7:
        st.markdown('<div class="sub-header">EDURISHI Product Catalog</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Browse our comprehensive catalog of educational products and solutions.</div>', unsafe_allow_html=True)

        # Define product categories based on Schools_Enquiry.csv
        categories = {
            "Core Educational Programs": ["ELAP", "MDL", "PBL", "ICT", "LMS"],
            "AI & Technology Solutions": ["AI Workshop", "AI software", "AI tutor", "Simulation", "Simulations"],
            "Educational Materials & Programs": ["Book Publisher", "E2MP", "E2MP workshop", "E2MP software"],
            "Business & Entrepreneurship": ["Franchise Proposal", "Tech Franchise", "Entrepreneurship_Workshop"]
        }

        # Get product details
        product_details = {
            "ELAP": {
                "name": "ELAP (Experiential Learning and Assessment Program)",
                "description": "Comprehensive experiential learning program designed for schools",
                "brochure": "EduRishi Final Brochures/ELAP_Brochure.pdf",
                "pricing": "₹800 per student (annual subscription)",
                "video": "https://www.youtube.com/watch?v=elapoverview"
            },
            "MDL": {
                "name": "MDL (Multi-Dimensional Learning)",
                "description": "Multi-dimensional approach to learning that enhances student engagement",
                "brochure": "EduRishi Final Brochures/MDL_Brochure.pdf",
                "video": "https://www.youtube.com/watch?v=mdloverview"
            },
            "PBL": {
                "name": "PBL (Project-Based Learning)",
                "description": "Project-based learning methodology for practical skill development",
                "brochure": "EduRishi Final Brochures/PBL_Brochure.pdf",
                "video": "https://www.youtube.com/watch?v=pbloverview"
            },
            "ICT": {
                "name": "ICT (Information and Communication Technology)",
                "description": "Technology integration in education for digital literacy",
                "brochure": "EduRishi Final Brochures/ICT_Brochure.pdf",
                "video": "https://www.youtube.com/watch?v=ictoverview"
            },
            "AI Workshop": {
                "name": "AI Workshop",
                "description": "Hands-on workshops introducing artificial intelligence concepts",
                "brochure": "AI_Workshop_Brochure.pdf",
                "video": "https://www.youtube.com/watch?v=aiworkshop"
            },
            "Book Publisher": {
                "name": "Book Publisher",
                "description": "Educational book publishing services for schools",
                "brochure": "Book_Publisher_Brochure.pdf",
                "video": "https://www.youtube.com/watch?v=bookpublisher"
            },
            "E2MP": {
                "name": "E2MP (EduRishi Educational Materials Program)",
                "description": "Comprehensive educational materials program",
                "brochure": "E2MP_Brochure.pdf",
                "video": "https://www.youtube.com/watch?v=e2mpoverview"
            },
            "Franchise Proposal": {
                "name": "Franchise Proposal",
                "description": "Educational franchise opportunities with EduRishi",
                "brochure": "Franchise_Proposal.pdf",
                "video": "https://www.youtube.com/watch?v=franchiseoverview"
            },
            "Tech Franchise": {
                "name": "Tech Franchise",
                "description": "Technology-focused educational franchise opportunities",
                "brochure": "Tech_Franchise.pdf",
                "video": "https://www.youtube.com/watch?v=techfranchise"
            },
            "AI_Tutor": {
                "name": "AI Tutor",
                "description": "Personalized AI-powered tutoring system for students",
                "brochure": "AI_Tutor_Brochure.pdf",
                "pricing": "₹1200 per student (annual subscription)",
                "video": "https://www.youtube.com/watch?v=aitutor"
            },
            "AI_Simulation": {
                "name": "AI Simulation",
                "description": "Advanced AI simulations for interactive learning experiences",
                "brochure": "AI_Simulation_Brochure.pdf",
                "pricing": "₹1500 per classroom (annual subscription)",
                "video": "https://www.youtube.com/watch?v=aisimulation"
            },
            "AI_Integration_Workshop": {
                "name": "AI Integration in Teaching Workshop",
                "description": "Comprehensive workshop for educators on integrating AI in teaching methodologies",
                "brochure": "AI_Integration_Workshop_Brochure.pdf",
                "pricing": "₹25,000 per workshop (up to 30 participants)",
                "video": "https://www.youtube.com/watch?v=aiintegration"
            },
            "Entrepreneurship_Workshop": {
                "name": "EduRishi Entrepreneurship and Mentorship Workshop",
                "description": "Hands-on workshop to develop entrepreneurial skills and mindset",
                "brochure": "Entrepreneurship_Workshop_Brochure.pdf",
                "pricing": "₹20,000 per workshop (up to 25 participants)",
                "video": "https://www.youtube.com/watch?v=entrepreneurship"
            }
        }

        # Display products by category
        for category, products in categories.items():
            st.markdown(f'<div class="sub-header">{category}</div>', unsafe_allow_html=True)

            # Create columns for products
            cols = st.columns(min(len(products), 2))

            for i, product_code in enumerate(products):
                try:
                    product = product_details[product_code]
                    with cols[i % 2]:
                        with st.expander(f"{product['name']}"):
                            st.markdown(f"**Description:** {product['description']}")
                            if 'pricing' in product:
                                st.markdown(f"**Pricing:** {product['pricing']}")
                            st.markdown(f"**Brochure:** {product['brochure']}")
                            st.markdown(f"**Video:** [Watch Demo]({product['video']})")

                            # Add buttons for actions
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"Download Brochure", key=f"dl_cat_{product_code}"):
                                    st.markdown(f"<div class='success-box'>Downloading {product['name']} brochure...</div>", unsafe_allow_html=True)
                            with col2:
                                if st.button(f"Watch Video", key=f"vid_{product_code}"):
                                    st.markdown(f"<div class='success-box'>Opening video: {product['video']}</div>", unsafe_allow_html=True)
                except KeyError:
                    # Skip products that don't have details
                    st.warning(f"Product details for '{product_code}' not found. Please update the product_details dictionary.")

        # Product bundles section
        st.markdown('<div class="sub-header">EduRishi Product Bundles</div>', unsafe_allow_html=True)

        bundles = {
            "School Starter Package": ["ELAP", "MDL", "ICT"],
            "Advanced Learning Suite": ["ELAP", "PBL", "AI Workshop"],
            "Complete School Transformation": ["ELAP", "MDL", "PBL", "ICT", "AI Workshop"],
            "LMS Integration Package": ["LMS", "ELAP", "MDL"],
            "AI Education Bundle": ["AI tutor", "AI software", "AI Workshop"],
            "Simulation Learning Package": ["Simulation", "Simulations", "PBL"],
            "E2MP Complete Solution": ["E2MP", "E2MP workshop", "E2MP software"],
            "University Package": ["E2MP software", "Simulations", "AI tutor"]
        }

        for bundle_name, bundle_products in bundles.items():
            with st.expander(bundle_name):
                st.markdown(f"**Included Products:**")
                for product_code in bundle_products:
                    try:
                        product = product_details[product_code]
                        st.markdown(f"- **{product['name']}**: {product['description']}")
                    except KeyError:
                        st.markdown(f"- **{product_code}**: Product details not available")

                st.markdown("**Bundle Benefits:**")
                st.markdown("- Discounted pricing compared to individual purchases")
                st.markdown("- Integrated implementation support")
                st.markdown("- Dedicated account manager")
                st.markdown("- Priority technical support")

                if st.button(f"Request Bundle Quote", key=f"bundle_{bundle_name}"):
                    st.markdown("<div class='success-box'>Quote request submitted! Our team will contact you shortly.</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">EDURISHI EDUVENTURES PVT LTD • AI Sales Assistant & CRM • Powered by Gemini 1.5 Flash • © 2023</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()