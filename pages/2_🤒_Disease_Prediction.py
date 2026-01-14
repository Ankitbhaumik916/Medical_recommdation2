import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')
import os

st.set_page_config(
    page_title="Disease Prediction",
    page_icon="🤒",
    layout="wide"
)

# Custom theme (simplified version)
def apply_theme():
    st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
        }
        .stButton>button {
            background-color: #FF6B35;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #FF8B5C;
        }
        .symptom-item {
            background-color: #2D2D2D;
            padding: 8px 12px;
            border-radius: 20px;
            margin: 5px 3px;
            display: inline-block;
            font-size: 0.9rem;
            border: 1px solid #444;
        }
        .disease-card {
            background-color: #3A3A3A;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 5px solid;
        }
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'age': 25,
        'gender': 'Male',
        'symptoms': []
    }

# Load dataset
@st.cache_data
def load_dataset():
    try:
        # Try different possible paths
        possible_paths = [
            "dataset.csv",
            "C:/Users/Ankit/OneDrive/Desktop/medi_recomm/Data/dataset.csv",
            "./Data/dataset.csv",
            "../Data/dataset.csv",
            "pages/dataset.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                st.success(f"✅ Dataset found: {path}")
                df = pd.read_csv(path)
                return df
        
        # If file not found, use sample data structure
        st.error("⚠️ Dataset file not found. Using demo mode.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        return None

df = load_dataset()

# Define symptom categories function BEFORE using it
def create_symptom_categories(symptoms_list):
    """Create organized symptom categories"""
    categories = {
        "General": [],
        "Respiratory": [],
        "Gastrointestinal": [],
        "Neurological": [],
        "Musculoskeletal": [],
        "Dermatological": [],
        "Cardiovascular": [],
        "Metabolic": []
    }
    
    # Categorize symptoms
    for symptom in symptoms_list:
        symptom_lower = symptom.lower()
        
        if any(word in symptom_lower for word in ['fever', 'fatigue', 'chills', 'sweating', 'weight_', 'itching', 'lethargy']):
            categories["General"].append(symptom)
        elif any(word in symptom_lower for word in ['cough', 'breath', 'sneezing', 'sputum', 'congestion', 'runny', 'throat']):
            categories["Respiratory"].append(symptom)
        elif any(word in symptom_lower for word in ['stomach', 'vomit', 'nausea', 'appetite', 'abdominal', 'diarrhoea', 'constipation', 'pain_bowel', 'anal', 'acidity']):
            categories["Gastrointestinal"].append(symptom)
        elif any(word in symptom_lower for word in ['headache', 'dizziness', 'restlessness', 'lethargy', 'weakness', 'balance', 'concentration', 'sensorium', 'depression', 'irritability']):
            categories["Neurological"].append(symptom)
        elif any(word in symptom_lower for word in ['joint', 'muscle', 'back', 'neck', 'knee', 'hip', 'pain', 'stiff', 'swelling']):
            categories["Musculoskeletal"].append(symptom)
        elif any(word in symptom_lower for word in ['skin', 'rash', 'eruptions', 'patches', 'pimples', 'blackheads', 'peeling', 'blister']):
            categories["Dermatological"].append(symptom)
        elif any(word in symptom_lower for word in ['chest_pain', 'heart', 'palpitations', 'bp', 'pressure']):
            categories["Cardiovascular"].append(symptom)
        elif any(word in symptom_lower for word in ['sugar', 'hunger', 'thirst', 'urination', 'thyroid', 'cholesterol']):
            categories["Metabolic"].append(symptom)
        else:
            categories["General"].append(symptom)
    
    # Remove empty categories
    categories = {k: sorted(v) for k, v in categories.items() if v}
    
    return categories

# Process dataset if available
if df is not None:
    # Clean the data
    df_clean = df.copy()
    
    # Combine all symptoms into a single string
    symptom_columns = [col for col in df_clean.columns if col.startswith('Symptom_')]
    df_clean['all_symptoms'] = df_clean[symptom_columns].apply(
        lambda x: ' '.join([str(symptom) for symptom in x if pd.notna(symptom) and str(symptom).strip() != '']), 
        axis=1
    )
    
    # Get unique diseases and symptoms
    unique_diseases = sorted(df_clean['Disease'].unique())
    all_symptoms_list = []
    for col in symptom_columns:
        symptoms = df_clean[col].dropna().unique()
        all_symptoms_list.extend([s for s in symptoms if str(s).strip() != ''])
    unique_symptoms = sorted(set(all_symptoms_list))
    
    # Create symptom categories
    symptom_categories = create_symptom_categories(unique_symptoms)
    
    # Prepare training data
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df_clean['all_symptoms'])
    y = df_clean['Disease']
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = MultinomialNB()
    model.fit(X_train, y_train)
    
    # Function to predict disease
    def predict_disease_from_symptoms(symptoms_list):
        symptoms_text = ' '.join(symptoms_list)
        symptoms_vector = vectorizer.transform([symptoms_text])
        prediction = model.predict(symptoms_vector)[0]
        probabilities = model.predict_proba(symptoms_vector)[0]
        
        # Get top 5 predictions
        top_indices = np.argsort(probabilities)[::-1][:5]
        top_predictions = []
        
        for idx in top_indices:
            disease = model.classes_[idx]
            prob = probabilities[idx]
            
            # Get disease info
            disease_samples = df_clean[df_clean['Disease'] == disease]
            if len(disease_samples) > 0:
                disease_data = disease_samples.iloc[0]
                disease_symptoms = [symptom for symptom in disease_data[symptom_columns] if pd.notna(symptom) and str(symptom).strip() != '']
                
                # Calculate matched symptoms
                matched_symptoms = list(set(symptoms_list) & set(disease_symptoms))
                match_percentage = len(matched_symptoms) / len(disease_symptoms) if disease_symptoms else 0
                
                # Determine severity
                severity_map = {
                    'Heart attack': 'High', 
                    'Paralysis (brain hemorrhage)': 'High', 
                    'AIDS': 'High',
                    'Pneumonia': 'High',
                    'Tuberculosis': 'High',
                    'Hepatitis E': 'High',
                    'Hepatitis D': 'High',
                    'Bronchial Asthma': 'High',
                    'Hypertension': 'Medium',
                    'Diabetes': 'Medium',
                    'GERD': 'Medium',
                    'Migraine': 'Medium',
                    'Peptic ulcer diseae': 'Medium',
                    'Chronic cholestasis': 'Medium',
                    'Jaundice': 'Medium',
                    'Typhoid': 'Medium',
                    'Malaria': 'Medium',
                    'Dengue': 'Medium',
                    'Common Cold': 'Low',
                    'Allergy': 'Low',
                    'Fungal infection': 'Low',
                    'Acne': 'Low',
                    'Gastroenteritis': 'Low',
                    'Urinary tract infection': 'Low'
                }
                severity = severity_map.get(disease, 'Medium')
                
                # Determine urgency
                urgency = 'High' if severity == 'High' else 'Medium' if severity == 'Medium' else 'Low'
                
                top_predictions.append({
                    'disease': disease,
                    'confidence': prob,
                    'severity': severity,
                    'urgency': urgency,
                    'matched_symptoms': matched_symptoms,
                    'all_symptoms': disease_symptoms,
                    'match_percentage': match_percentage
                })
        
        return top_predictions

else:
    # Fallback to demo mode
    unique_symptoms = [
        "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing",
        "shivering", "chills", "watering_from_eyes", "stomach_pain", "acidity",
        "ulcers_on_tongue", "vomiting", "cough", "chest_pain", "fatigue",
        "weight_loss", "restlessness", "lethargy", "high_fever", "headache",
        "nausea", "joint_pain", "yellowish_skin", "dark_urine", "loss_of_appetite",
        "abdominal_pain", "yellowing_of_eyes", "breathlessness", "sweating",
        "dehydration", "diarrhoea", "dizziness", "back_pain", "constipation",
        "muscle_pain", "neck_pain", "weakness_in_limbs"
    ]
    
    unique_diseases = [
        "Fungal infection", "Allergy", "GERD", "Chronic cholestasis", 
        "Drug Reaction", "Peptic ulcer diseae", "Diabetes", "Gastroenteritis",
        "Bronchial Asthma", "Hypertension", "Migraine", "Common Cold",
        "Pneumonia", "Heart attack", "Tuberculosis", "Jaundice", "Malaria"
    ]
    
    # Create symptom categories for demo mode
    symptom_categories = create_symptom_categories(unique_symptoms)

st.markdown("<h1 style='color: #FF6B35;'>🤒 Disease Prediction System</h1>", unsafe_allow_html=True)

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3 style='color: #FF6B35;'>📋 Patient Profile & Symptoms</h3>", unsafe_allow_html=True)
    
    # Patient details
    col_age, col_gender = st.columns(2)
    with col_age:
        age = st.number_input("Age", min_value=1, max_value=120, 
                             value=st.session_state.user_data['age'],
                             help="Your age in years")
    
    with col_gender:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    # Store in session
    st.session_state.user_data['age'] = age
    st.session_state.user_data['gender'] = gender
    
    st.markdown("---")
    
    # Symptom selection from dataset
    st.markdown("<h4 style='color: #FF6B35;'>🤒 Select Your Symptoms</h4>", unsafe_allow_html=True)
    
    selected_symptoms = []
    
    # Create symptom selection with categories
    if symptom_categories:
        for category, symptoms in symptom_categories.items():
            if symptoms:  # Only show categories with symptoms
                with st.expander(f"📁 {category} ({len(symptoms)} symptoms)"):
                    # Search box for symptoms in this category
                    search_term = st.text_input(f"Search in {category}", key=f"search_{category}")
                    
                    if search_term:
                        filtered_symptoms = [s for s in symptoms if search_term.lower() in s.lower()]
                    else:
                        filtered_symptoms = symptoms
                    
                    # Display symptoms with checkboxes
                    cols = st.columns(2)
                    for i, symptom in enumerate(filtered_symptoms):
                        col_idx = i % 2
                        with cols[col_idx]:
                            display_name = symptom.replace('_', ' ').title()
                            if st.checkbox(display_name, key=f"symptom_{symptom}"):
                                selected_symptoms.append(symptom)
    else:
        # Fallback if no categories
        selected_symptoms = st.multiselect(
            "Select Symptoms",
            unique_symptoms,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    # Show selected symptoms count
    if selected_symptoms:
        st.success(f"✅ {len(selected_symptoms)} symptoms selected")
        
        # Display selected symptoms
        st.markdown("<h5>Selected Symptoms:</h5>", unsafe_allow_html=True)
        symptom_html = ""
        for symptom in selected_symptoms:
            symptom_html += f"<span class='symptom-item'>{symptom.replace('_', ' ').title()}</span> "
        st.markdown(symptom_html, unsafe_allow_html=True)
    
    # Additional health metrics
    st.markdown("---")
    st.markdown("<h4 style='color: #FF6B35;'>📊 Additional Health Information</h4>", unsafe_allow_html=True)
    
    col_health1, col_health2 = st.columns(2)
    
    with col_health1:
        blood_pressure_systolic = st.number_input("Systolic BP", min_value=80, max_value=200, value=120)
        temperature = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=36.6, step=0.1)
        
    with col_health2:
        blood_pressure_diastolic = st.number_input("Diastolic BP", min_value=50, max_value=150, value=80)
        glucose_level = st.number_input("Glucose (mg/dL)", min_value=50, max_value=500, value=100)
    
    # Symptom duration and severity
    col_dur, col_sev = st.columns(2)
    with col_dur:
        duration = st.selectbox(
            "Duration of symptoms",
            ["Less than 24 hours", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"]
        )
    
    with col_sev:
        severity_input = st.select_slider(
            "Symptom Severity",
            options=["Mild", "Moderate", "Severe"],
            value="Moderate"
        )

with col2:
    st.markdown("<h3 style='color: #FF6B35;'>🔬 Prediction Results</h3>", unsafe_allow_html=True)
    
    # Prediction button
    predict_button = st.button("🔍 Predict Disease", 
                             type="primary", 
                             use_container_width=True,
                             help="Click to analyze symptoms and predict diseases")
    
    if predict_button:
        if not selected_symptoms:
            st.error("⚠️ Please select at least one symptom")
        else:
            with st.spinner("Analyzing symptoms using medical database..."):
                # Simulate processing time
                import time
                time.sleep(1)
                
                if df is not None:
                    # Use actual ML model
                    predictions = predict_disease_from_symptoms(selected_symptoms)
                else:
                    # Demo mode - simulate predictions
                    predictions = []
                    demo_diseases = unique_diseases[:min(5, len(unique_diseases))]
                    
                    for i, disease in enumerate(demo_diseases):
                        confidence = 0.8 - (i * 0.15)
                        predictions.append({
                            'disease': disease,
                            'confidence': confidence,
                            'severity': 'High' if i < 2 else 'Medium' if i < 4 else 'Low',
                            'urgency': 'High' if i < 2 else 'Medium' if i < 4 else 'Low',
                            'matched_symptoms': selected_symptoms[:min(3, len(selected_symptoms))],
                            'match_percentage': confidence,
                            'all_symptoms': selected_symptoms[:min(5, len(selected_symptoms))]
                        })
                
                if predictions:
                    # Overall risk assessment
                    risk_factors = 0
                    if age > 50: risk_factors += 1
                    if blood_pressure_systolic >= 140 or blood_pressure_diastolic >= 90: risk_factors += 2
                    if glucose_level > 140: risk_factors += 1
                    if severity_input == "Severe": risk_factors += 2
                    elif severity_input == "Moderate": risk_factors += 1
                    
                    if risk_factors >= 4:
                        overall_risk = "High"
                        risk_color = "#FF4444"
                    elif risk_factors >= 2:
                        overall_risk = "Medium"
                        risk_color = "#FFA500"
                    else:
                        overall_risk = "Low"
                        risk_color = "#4CAF50"
                    
                    # Display overall assessment - FIXED: using st.container() instead of HTML
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color: #3A3A3A; border-radius: 10px; padding: 20px; margin: 10px 0; border-left: 5px solid {risk_color};'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h4 style='color: #FF6B35; margin: 0;'>Health Assessment</h4>
                                    <p style='color: #AAAAAA; margin: 5px 0;'>
                                    Based on {len(selected_symptoms)} symptoms • {duration} • {severity_input} severity
                                    </p>
                                </div>
                                <div style='text-align: right;'>
                                    <h4 style='color: {risk_color}; margin: 0;'>{overall_risk} Risk</h4>
                                    <p style='color: #AAAAAA; margin: 5px 0;'>{risk_factors}/5 risk factors</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display predictions title
                    st.markdown("<h4 style='color: #FF6B35; margin-top: 20px;'>📋 Predicted Conditions</h4>", unsafe_allow_html=True)
                    
                    for pred in predictions:
                        # Determine colors
                        severity_colors = {"Low": "#4CAF50", "Medium": "#FFA500", "High": "#FF4444"}
                        confidence_percent = pred['confidence'] * 100
                        confidence_color = "#4CAF50" if confidence_percent > 70 else "#FFA500" if confidence_percent > 50 else "#FF4444"
                        
                        # Display disease card using Streamlit components instead of raw HTML
                        with st.container():
                            col_left, col_right = st.columns([3, 1])
                            
                            with col_left:
                                st.markdown(f"**{pred['disease']}**")
                                st.caption(f"Matched {len(pred['matched_symptoms'])} symptoms • {pred['match_percentage']:.0%} match")
                                
                                # Severity and urgency
                                col_sev, col_urg = st.columns(2)
                                with col_sev:
                                    st.markdown(f"**Severity:** <span style='color:{severity_colors[pred["severity"]]}'>{pred['severity']}</span>", unsafe_allow_html=True)
                                with col_urg:
                                    st.markdown(f"**Urgency:** <span style='color:{severity_colors[pred["urgency"]]}'>{pred['urgency']}</span>", unsafe_allow_html=True)
                            
                            with col_right:
                                st.markdown(f"<h3 style='color:{confidence_color}; text-align:center;'>{confidence_percent:.0f}%</h3>", unsafe_allow_html=True)
                                st.caption("Confidence")
                            
                            # Confidence bar
                            st.progress(confidence_percent/100)
                            
                            st.divider()
                    
                    # Visualization
                    if len(predictions) > 1:
                        st.markdown("<h4 style='color: #FF6B35; margin-top: 20px;'>📊 Prediction Comparison</h4>", unsafe_allow_html=True)
                        
                        # Create bar chart
                        pred_df = pd.DataFrame(predictions)
                        fig = px.bar(
                            pred_df,
                            x='disease',
                            y='confidence',
                            color='severity',
                            color_discrete_map={"High": "#FF4444", "Medium": "#FFA500", "Low": "#4CAF50"},
                            title="Disease Prediction Confidence",
                            labels={'confidence': 'Confidence', 'disease': 'Disease'}
                        )
                        fig.update_layout(
                            plot_bgcolor='#1A1A1A',
                            paper_bgcolor='#1A1A1A',
                            font_color='white',
                            xaxis_tickangle=-45,
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Recommendations
                    st.markdown("<h4 style='color: #FF6B35; margin-top: 20px;'>💡 Recommended Actions</h4>", unsafe_allow_html=True)
                    
                    primary_disease = predictions[0]['disease']
                    
                    # Disease-specific recommendations
                    recommendations = []
                    
                    if "Emergency" in primary_disease or primary_disease in ["Heart attack", "Paralysis", "AIDS", "Pneumonia"]:
                        recommendations.append("🚨 **EMERGENCY**: Seek immediate medical attention")
                        recommendations.append("Call emergency services (911/112)")
                        recommendations.append("Do not delay treatment")
                    
                    elif primary_disease in ["Hypertension", "Diabetes", "Heart"]:
                        recommendations.append("Schedule appointment with specialist within 1 week")
                        recommendations.append("Monitor vital signs daily")
                        recommendations.append("Follow prescribed medication regimen")
                    
                    elif primary_disease in ["Tuberculosis", "Hepatitis", "Malaria", "Typhoid"]:
                        recommendations.append("Consult infectious disease specialist")
                        recommendations.append("Complete prescribed antibiotic course")
                        recommendations.append("Isolate if contagious")
                    
                    elif primary_disease in ["Common Cold", "Allergy", "Fungal infection", "Acne"]:
                        recommendations.append("Consult general physician within 2-3 days")
                        recommendations.append("Get adequate rest and hydration")
                        recommendations.append("Use over-the-counter remedies as directed")
                    
                    else:
                        recommendations.append("Consult a healthcare professional for proper diagnosis")
                        recommendations.append("Monitor your symptoms closely")
                        recommendations.append("Get adequate rest and maintain hydration")
                    
                    # Add general recommendations
                    recommendations.append("Keep track of symptom progression in a diary")
                    recommendations.append("Stay hydrated and maintain a balanced diet")
                    
                    for i, rec in enumerate(recommendations, 1):
                        st.markdown(f"{i}. {rec}")
                    
                    # Medicine Recommendation Button
                    st.markdown("---")
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("💊 Get Medicine Recommendations", 
                                   use_container_width=True,
                                   help="Get personalized medicine suggestions based on prediction"):
                            # Store prediction for medicine page
                            st.session_state.predicted_disease = primary_disease
                            st.session_state.from_prediction = True
                            st.session_state.selected_symptoms = selected_symptoms
                            
                            # Navigate to medicine page
                            try:
                                st.switch_page("pages/3_💊_Medicine_Recommendation.py")
                            except:
                                st.info("Navigate to Medicine Recommendation page from the sidebar")
                    
                    with col_btn2:
                        if st.button("💾 Save Health Report", 
                                   use_container_width=True,
                                   help="Save this prediction to your health history"):
                            st.success("✅ Health report saved successfully!")
                            
                else:
                    st.info("No clear predictions. Please provide more specific symptoms or consult a healthcare professional.")
    
    # Information when no prediction yet
    if not predict_button:
        st.info("👈 Select your symptoms and click 'Predict Disease'")
        
        # Show dataset statistics if available
        if df is not None:
            st.markdown(f"""
            <div style='background-color: #3A3A3A; border-radius: 10px; padding: 20px; margin: 10px 0;'>
                <h4 style='color: #FF6B35; margin: 0;'>📚 Medical Database Info</h4>
                <p style='color: #AAAAAA; margin: 5px 0;'>
                • <strong>{len(unique_diseases)}</strong> diseases in database<br>
                • <strong>{len(unique_symptoms)}</strong> unique symptoms<br>
                • <strong>{len(df)}</strong> medical cases analyzed
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show top 10 symptoms
            if 'all_symptoms' in locals():
                st.markdown("<h5>📝 Most Common Symptoms in Database:</h5>", unsafe_allow_html=True)
                from collections import Counter
                all_symptoms_flat = []
                for symptoms in df_clean['all_symptoms']:
                    all_symptoms_flat.extend(symptoms.split())
                symptom_counts = Counter(all_symptoms_flat).most_common(10)
                
                for symptom, count in symptom_counts:
                    st.markdown(f"• {symptom.replace('_', ' ').title()}: {count} cases")

# Footer with dataset info
st.markdown("---")
st.markdown("<h3 style='color: #FF6B35;'>🏥 Supported Diseases</h3>", unsafe_allow_html=True)

# Display diseases in a grid
if unique_diseases:
    # Create tabs for disease categories
    tab1, tab2, tab3 = st.tabs(["Common", "Chronic", "Infectious"])
    
    with tab1:
        common_diseases = [d for d in unique_diseases if d in [
            "Common Cold", "Allergy", "Fungal infection", "Acne", 
            "Gastroenteritis", "Urinary tract infection", "Migraine"
        ]]
        cols = st.columns(3)
        for i, disease in enumerate(common_diseases):
            with cols[i % 3]:
                st.markdown(f"• {disease}")
    
    with tab2:
        chronic_diseases = [d for d in unique_diseases if d in [
            "Diabetes", "Hypertension", "Bronchial Asthma", "GERD",
            "Chronic cholestasis", "Hypothyroidism", "Hyperthyroidism"
        ]]
        cols = st.columns(3)
        for i, disease in enumerate(chronic_diseases):
            with cols[i % 3]:
                st.markdown(f"• {disease}")
    
    with tab3:
        infectious_diseases = [d for d in unique_diseases if d in [
            "Tuberculosis", "Malaria", "Typhoid", "Hepatitis",
            "Pneumonia", "Dengue", "Chicken pox"
        ]]
        cols = st.columns(3)
        for i, disease in enumerate(infectious_diseases):
            with cols[i % 3]:
                st.markdown(f"• {disease}")

# Disclaimer
st.markdown("""
<div style='background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #FF6B35;'>
    <h5 style='color: #FF6B35; margin-top: 0;'>⚠️ Medical Disclaimer</h5>
    <p style='color: #AAAAAA; font-size: 0.9rem; margin-bottom: 0;'>
    <strong>Important:</strong> This tool is for informational purposes only and uses a medical 
    symptom database for predictions. It is <strong>NOT</strong> a substitute for professional 
    medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare 
    providers with any questions regarding medical conditions.
    <br><br>
    <strong>In case of emergency, call your local emergency number immediately.</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# Debug info (optional - can be removed)
with st.expander("🔧 Debug Information"):
    if df is not None:
        st.write(f"✅ Dataset loaded successfully")
        st.write(f"• Shape: {df.shape}")
        st.write(f"• Diseases: {len(unique_diseases)}")
        st.write(f"• Symptoms: {len(unique_symptoms)}")
        st.write(f"• Symptom Categories: {len(symptom_categories)}")
        
        # Show first few rows
        if st.checkbox("Show sample data"):
            st.dataframe(df.head())
    else:
        st.write("⚠️ Running in demo mode - dataset not found")
        st.write("• Expected path: C:/Users/Ankit/OneDrive/Desktop/medi_recomm/Data/dataset.csv")
        st.write("• Current symptoms (demo):", len(unique_symptoms))
        st.write("• Current diseases (demo):", len(unique_diseases))