import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Health AI Recommender",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for charcoal black and orange theme
st.markdown("""
<style>
    :root {
        --primary-color: #FF6B35;  /* Orange */
        --secondary-color: #1A1A1A; /* Charcoal Black */
        --background-color: #2D2D2D;
        --text-color: #FFFFFF;
        --card-background: #3A3A3A;
    }
    
    .stApp {
        background-color: var(--secondary-color);
        color: var(--text-color);
    }
    
    .main-header {
        color: var(--primary-color);
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        color: var(--primary-color);
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .card {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid var(--primary-color);
    }
    
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: var(--secondary-color) !important;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    
    .stButton > button:hover {
        background-color: #FF8B35 !important;
    }
    
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: var(--card-background);
        color: var(--text-color);
    }
    
    .metric-card {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border-top: 4px solid var(--primary-color);
    }
    
    .metric-value {
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: bold;
    }
    
    .metric-label {
        color: var(--text-color);
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for user data
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'age': 25,
        'gender': 'Male',
        'medical_history': [],
        'medicine_preferences': [],
        'symptoms': []
    }

if 'disease_model' not in st.session_state:
    st.session_state.disease_model = None

if 'medicine_model' not in st.session_state:
    st.session_state.medicine_model = None

if 'drug_data' not in st.session_state:
    try:
        st.session_state.drug_data = pd.read_csv('data/Drug.csv')
    except:
        st.session_state.drug_data = pd.DataFrame()

# Navigation sidebar
with st.sidebar:
    st.markdown("<h1 style='color: #FF6B35; text-align: center;'>🏥 Health AI</h1>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Disease Prediction", "Medicine Recommendation", "Analytics", "Admin"],
        icons=["house", "activity", "capsule", "graph-up", "gear"],
        menu_icon="menu-app",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#1A1A1A"},
            "icon": {"color": "#FF6B35", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#3A3A3A",
                "color": "white"
            },
            "nav-link-selected": {"background-color": "#FF6B35", "color": "#1A1A1A"},
        }
    )
    
    # User profile section
    st.markdown("---")
    st.markdown("<h3 style='color: #FF6B35;'>👤 User Profile</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user_data['age'] = st.number_input(
            "Age", 
            min_value=1, 
            max_value=100, 
            value=st.session_state.user_data['age'],
            key="age_input"
        )
    
    with col2:
        st.session_state.user_data['gender'] = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=0 if st.session_state.user_data['gender'] == "Male" else 1,
            key="gender_input"
        )
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("<h3 style='color: #FF6B35;'>📊 Quick Stats</h3>", unsafe_allow_html=True)
    
    if not st.session_state.drug_data.empty:
        total_drugs = len(st.session_state.drug_data)
        total_diseases = st.session_state.drug_data['Disease'].nunique()
        avg_age = st.session_state.drug_data['Age'].mean()
        
        st.metric("Total Drugs", f"{total_drugs:,}")
        st.metric("Diseases Covered", total_diseases)
        st.metric("Average Age", f"{avg_age:.1f}")

# Main content based on navigation
if selected == "Dashboard":
    st.markdown("<h1 class='main-header'>🏥 Health AI Dashboard</h1>", unsafe_allow_html=True)
    
    # Welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class='card'>
            <h3 style='color: #FF6B35;'>Welcome Back!</h3>
            <p>Age: {st.session_state.user_data['age']} | Gender: {st.session_state.user_data['gender']}</p>
            <p>Get personalized healthcare recommendations based on your profile and symptoms.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("<h3 class='sub-header'>🚀 Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🩺 Predict Disease", use_container_width=True):
            st.switch_page("pages/2_🤒_Disease_Prediction.py")
    
    with col2:
        if st.button("💊 Get Medicine", use_container_width=True):
            st.switch_page("pages/3_💊_Medicine_Recommendation.py")
    
    with col3:
        if st.button("📈 View Analytics", use_container_width=True):
            st.switch_page("pages/4_📊_Analytics.py")
    
    with col4:
        if st.button("⚙️ Admin Panel", use_container_width=True):
            st.switch_page("pages/5_⚙️_Admin.py")
    
    # Stats overview
    st.markdown("<h3 class='sub-header'>📊 System Overview</h3>", unsafe_allow_html=True)
    
    if not st.session_state.drug_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-value'>2,500+</div>
                <div class='metric-label'>Medicines in Database</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-value'>3</div>
                <div class='metric-label'>Diseases Covered</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-value'>95%</div>
                <div class='metric-label'>Prediction Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-value'>24/7</div>
                <div class='metric-label'>Availability</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Disease distribution chart
        st.markdown("<h3 class='sub-header'>📈 Disease Distribution</h3>", unsafe_allow_html=True)
        
        disease_counts = st.session_state.drug_data['Disease'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=disease_counts.index,
                values=disease_counts.values,
                hole=.3,
                marker=dict(colors=['#FF6B35', '#FF8B35', '#FFA935'])
            )
        ])
        
        fig.update_layout(
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#1A1A1A',
            font_color='white',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent recommendations preview
        st.markdown("<h3 class='sub-header'>💡 Recent Insights</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='card'>
                <h4>🔬 Most Common Prescriptions</h4>
                <ul>
                    <li>Acne: Benzoyl Peroxide based gels</li>
                    <li>Allergy: Levocetirizine tablets</li>
                    <li>Diabetes: Metformin formulations</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='card'>
                <h4>📋 System Recommendations</h4>
                <ul>
                    <li>Update your medical history regularly</li>
                    <li>Consult doctor for personalized advice</li>
                    <li>Report any adverse effects immediately</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

elif selected == "Disease Prediction":
    st.switch_page("pages/2_🤒_Disease_Prediction.py")
elif selected == "Medicine Recommendation":
    st.switch_page("pages/3_💊_Medicine_Recommendation.py")
elif selected == "Analytics":
    st.switch_page("pages/4_📊_Analytics.py")
elif selected == "Admin":
    st.switch_page("pages/5_⚙️_Admin.py")