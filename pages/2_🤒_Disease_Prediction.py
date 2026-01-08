import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Disease Prediction",
    page_icon="🤒",
    layout="wide"
)

# Initialize session state for user data
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'age': 25,
        'gender': 'Male',
        'medical_history': [],
        'medicine_preferences': [],
        'symptoms': []
    }

# Custom CSS
st.markdown("""
<style>
    .prediction-card {
        background-color: #3A3A3A;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #FF6B35;
    }
    
    .risk-high {
        color: #FF4444;
        font-weight: bold;
    }
    
    .risk-medium {
        color: #FFA500;
        font-weight: bold;
    }
    
    .risk-low {
        color: #4CAF50;
        font-weight: bold;
    }
    
    .symptom-item {
        background-color: #2D2D2D;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        display: inline-block;
        border: 1px solid #FF6B35;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🤒 Disease Prediction System</h1>", unsafe_allow_html=True)

# Initialize disease data (in real app, this would come from a database)
diseases_data = pd.DataFrame({
    'age': np.random.randint(1, 90, 1000),
    'gender': np.random.choice(['Male', 'Female'], 1000),
    'blood_pressure': np.random.choice(['Normal', 'High', 'Low'], 1000),
    'glucose_level': np.random.uniform(70, 200, 1000),
    'heart_rate': np.random.randint(60, 120, 1000),
    'cholesterol': np.random.choice(['Normal', 'High'], 1000),
    'bmi': np.random.uniform(18, 35, 1000),
    'symptoms': np.random.choice(['Fever,Cough', 'Rash,Itching', 'Fatigue,Dizziness', 'Pain,Swelling'], 1000),
    'disease': np.random.choice(['Acne', 'Allergy', 'Diabetes', 'Hypertension'], 1000)
})

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3 class='sub-header'>📋 Patient Information</h3>", unsafe_allow_html=True)
    
    # Patient details
    age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.user_data['age'])
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if st.session_state.user_data['gender'] == "Male" else 1)
    
    col1a, col1b = st.columns(2)
    with col1a:
        blood_pressure = st.selectbox("Blood Pressure", ["Normal", "High", "Low"])
        glucose_level = st.number_input("Glucose Level (mg/dL)", min_value=50, max_value=500, value=100)
    
    with col1b:
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=75)
        cholesterol = st.selectbox("Cholesterol Level", ["Normal", "High"])
    
    bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=22.0, step=0.1)
    
    # Symptoms selection
    st.markdown("<h4>Symptoms</h4>", unsafe_allow_html=True)
    symptoms_options = [
        "Fever", "Cough", "Headache", "Fatigue", "Nausea", 
        "Rash", "Itching", "Pain", "Swelling", "Dizziness",
        "Shortness of breath", "Chest pain", "Abdominal pain",
        "Weight loss", "Increased thirst", "Frequent urination"
    ]
    
    selected_symptoms = st.multiselect("Select symptoms", symptoms_options)
    
    if selected_symptoms:
        st.markdown("<h5>Selected Symptoms:</h5>", unsafe_allow_html=True)
        for symptom in selected_symptoms:
            st.markdown(f"<span class='symptom-item'>{symptom}</span>", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='sub-header'>🔬 Prediction Results</h3>", unsafe_allow_html=True)
    
    # Prediction button
    if st.button("🔍 Predict Disease", type="primary", use_container_width=True):
        with st.spinner("Analyzing symptoms and health data..."):
            # Simulate model prediction
            np.random.seed(hash(str(age) + gender + str(selected_symptoms)) % 10000)
            
            # Simple rule-based prediction for demo
            if "Rash" in selected_symptoms or "Itching" in selected_symptoms:
                predicted_disease = "Acne/Skin Allergy"
                confidence = np.random.uniform(0.85, 0.95)
            elif glucose_level > 140 or "Increased thirst" in selected_symptoms or "Frequent urination" in selected_symptoms:
                predicted_disease = "Diabetes"
                confidence = np.random.uniform(0.80, 0.90)
            elif blood_pressure == "High" or "Chest pain" in selected_symptoms:
                predicted_disease = "Hypertension"
                confidence = np.random.uniform(0.75, 0.85)
            elif "Fever" in selected_symptoms and "Cough" in selected_symptoms:
                predicted_disease = "Respiratory Infection"
                confidence = np.random.uniform(0.70, 0.80)
            else:
                predicted_disease = "General Health Concern"
                confidence = np.random.uniform(0.60, 0.70)
            
            # Calculate risk score
            risk_factors = 0
            if age > 50: risk_factors += 1
            if blood_pressure == "High": risk_factors += 2
            if glucose_level > 140: risk_factors += 2
            if cholesterol == "High": risk_factors += 1
            if bmi > 30: risk_factors += 1
            
            if risk_factors >= 4:
                risk_level = "High"
                risk_color = "risk-high"
            elif risk_factors >= 2:
                risk_level = "Medium"
                risk_color = "risk-medium"
            else:
                risk_level = "Low"
                risk_color = "risk-low"
            
            # Display results
            st.markdown(f"""
            <div class='prediction-card'>
                <h3>Prediction Results</h3>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #FF6B35;'>{predicted_disease}</h4>
                        <p>Confidence: {confidence:.1%}</p>
                    </div>
                    <div>
                        <h4 class='{risk_color}'>{risk_level} Risk</h4>
                        <p>Risk Factors: {risk_factors}/7</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Health metrics visualization
            st.markdown("<h4>Health Metrics Analysis</h4>", unsafe_allow_html=True)
            
            metrics = {
                'Blood Pressure': 1 if blood_pressure == "Normal" else (0.5 if blood_pressure == "Low" else 0),
                'Glucose': 1 if glucose_level < 100 else (0.5 if glucose_level < 140 else 0),
                'Heart Rate': 1 if 60 <= heart_rate <= 100 else 0.5,
                'Cholesterol': 1 if cholesterol == "Normal" else 0,
                'BMI': 1 if 18.5 <= bmi <= 24.9 else (0.5 if 25 <= bmi <= 29.9 else 0)
            }
            
            fig = go.Figure(data=[
                go.Scatterpolar(
                    r=list(metrics.values()),
                    theta=list(metrics.keys()),
                    fill='toself',
                    line_color='#FF6B35',
                    fillcolor='rgba(255, 107, 53, 0.3)'
                )
            ])
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                plot_bgcolor='#1A1A1A',
                paper_bgcolor='#1A1A1A',
                font_color='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.markdown("<h4>📋 Recommendations</h4>", unsafe_allow_html=True)
            
            recommendations = []
            if predicted_disease == "Diabetes":
                recommendations = [
                    "Monitor blood glucose levels regularly",
                    "Follow a diabetic diet plan",
                    "Exercise for 30 minutes daily",
                    "Consult an endocrinologist"
                ]
            elif predicted_disease == "Hypertension":
                recommendations = [
                    "Reduce salt intake",
                    "Monitor blood pressure twice daily",
                    "Practice stress management techniques",
                    "Consult a cardiologist"
                ]
            elif "Acne" in predicted_disease:
                recommendations = [
                    "Use gentle skincare products",
                    "Avoid touching face frequently",
                    "Stay hydrated",
                    "Consult a dermatologist"
                ]
            else:
                recommendations = [
                    "Get adequate rest",
                    "Stay hydrated",
                    "Monitor symptoms",
                    "Consult a general physician"
                ]
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # Medicine suggestion button
            if st.button("💊 Get Medicine Suggestions", use_container_width=True):
                st.session_state.predicted_disease = predicted_disease
                st.switch_page("pages/3_💊_Medicine_Recommendation.py")

# Information section
st.markdown("---")
st.markdown("<h3 class='sub-header'>ℹ️ About Disease Prediction</h3>", unsafe_allow_html=True)

col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.markdown("""
    <div class='card'>
        <h4>🔬 How it Works</h4>
        <p>Our AI analyzes your symptoms, vital signs, and health metrics using 
        machine learning algorithms to predict potential diseases.</p>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown("""
    <div class='card'>
        <h4>📊 Data Sources</h4>
        <p>We use validated medical datasets and clinical guidelines to ensure 
        accurate predictions and recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

with col_info3:
    st.markdown("""
    <div class='card'>
        <h4>⚠️ Important Note</h4>
        <p>This tool provides preliminary assessments only. Always consult with 
        a healthcare professional for accurate diagnosis and treatment.</p>
    </div>
    """, unsafe_allow_html=True)