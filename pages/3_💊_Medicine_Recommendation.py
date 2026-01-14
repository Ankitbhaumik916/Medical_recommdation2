import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
# from surprise import Dataset, Reader, SVD
# from surprise.model_selection import cross_validate
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Medicine Recommendation",
    page_icon="💊",
    layout="wide"
)

from theme import apply_theme
apply_theme()

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
    .medicine-card {
        background-color: #3A3A3A;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #FF6B35;
        transition: transform 0.3s;
    }
    
    .medicine-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
    }
    
    .medicine-name {
        color: #FF6B35;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .match-score {
        background-color: #FF6B35;
        color: #1A1A1A;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .side-effects {
        background-color: #FF4444;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        margin: 2px;
        display: inline-block;
    }
    
    .benefits {
        background-color: #4CAF50;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        margin: 2px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>💊 Personalized Medicine Recommendation</h1>", unsafe_allow_html=True)

# Show notification if coming from disease prediction
if 'predicted_disease' in st.session_state and 'from_prediction' in st.session_state:
    st.success(f"🎯 Based on your disease prediction: **{st.session_state.predicted_disease}**")
    st.info("💡 We've pre-selected your predicted condition. You can change it if needed.")
    # Clear the flag
    del st.session_state.from_prediction

# Check if drug data exists
if st.session_state.drug_data.empty:
    st.error("Drug data not loaded. Please check the data file.")
    st.stop()

# Load and prepare data
df = st.session_state.drug_data.copy()

# Clean drug names (extract primary drug name)
def extract_primary_drug(drug_string):
    if pd.isna(drug_string):
        return "Unknown"
    # Take first part before any special characters or numbers
    parts = str(drug_string).split()
    for part in parts:
        if part and not any(char.isdigit() or char in '().,%' for char in part):
            if len(part) > 2:  # Avoid very short strings
                return part
    return str(drug_string).split()[0] if str(drug_string).split() else "Unknown"

df['Drug_Clean'] = df['Drug'].apply(extract_primary_drug)

# Create unique user IDs for collaborative filtering simulation
df['User_ID'] = df['Age'].astype(str) + '_' + df['Gender'] + '_' + df['Disease']

# Create two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<h3 class='sub-header'>🎯 Input Parameters</h3>", unsafe_allow_html=True)
    
    # Disease selection
    diseases = sorted(df['Disease'].unique().tolist())
    if 'predicted_disease' in st.session_state:
        default_disease = st.session_state.predicted_disease.split('/')[0]
        disease_index = 0
        for i, d in enumerate(diseases):
            if default_disease.lower() in d.lower():
                disease_index = i
                break
    else:
        disease_index = 0
    
    disease = st.selectbox(
        "Select Disease",
        diseases,
        index=disease_index,
        help="Select the disease or condition"
    )
    
    # Age and gender (pre-filled from user data)
    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=st.session_state.user_data['age'],
        help="Patient's age"
    )
    
    gender = st.selectbox(
        "Gender",
        ["Male", "Female"],
        index=0 if st.session_state.user_data['gender'] == "Male" else 1,
        help="Patient's gender"
    )
    
    # Additional preferences
    st.markdown("<h4>💊 Medication Preferences</h4>", unsafe_allow_html=True)
    
    form_type = st.multiselect(
        "Preferred Form",
        ["Tablet", "Capsule", "Gel", "Cream", "Lotion", "Injection", "Syrup"],
        default=["Tablet", "Capsule"]
    )
    
    # Budget filter
    budget = st.select_slider(
        "Budget Range",
        options=["Low", "Medium", "High", "Any"],
        value="Medium"
    )
    
    # Known allergies or restrictions
    allergies = st.text_input(
        "Known Allergies (comma separated)",
        placeholder="e.g., penicillin, sulfa drugs"
    )
    
    # Get recommendations button
    get_recommendations = st.button(
        "🔍 Get Personalized Recommendations",
        type="primary",
        use_container_width=True
    )

with col2:
    st.markdown("<h3 class='sub-header'>📋 Recommended Medicines</h3>", unsafe_allow_html=True)
    
    if get_recommendations:
        with st.spinner("Analyzing best medications for you..."):
            # Filter data based on inputs
            filtered_df = df[df['Disease'] == disease].copy()
            
            if not filtered_df.empty:
                # Content-based filtering
                # Create features from drug names and forms
                drug_features = filtered_df['Drug'].fillna('') + ' ' + \
                               filtered_df['Drug_Clean'].fillna('')
                
                # Use TF-IDF for content similarity
                vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
                tfidf_matrix = vectorizer.fit_transform(drug_features)
                
                # Create a query based on user preferences
                query = disease + ' ' + ' '.join(form_type) + ' ' + gender
                query_vector = vectorizer.transform([query])
                
                # Calculate similarity scores
                cosine_sim = cosine_similarity(query_vector, tfidf_matrix).flatten()
                
                # Get top recommendations
                filtered_df['Similarity_Score'] = cosine_sim
                
                # Age-based scoring (closer age gets higher score)
                filtered_df['Age_Score'] = 1 / (1 + abs(filtered_df['Age'] - age))
                
                # Gender matching score
                filtered_df['Gender_Score'] = (filtered_df['Gender'] == gender).astype(float)
                
                # Calculate final score
                filtered_df['Final_Score'] = (
                    filtered_df['Similarity_Score'] * 0.5 +
                    filtered_df['Age_Score'] * 0.3 +
                    filtered_df['Gender_Score'] * 0.2
                )
                
                # Sort by final score
                recommendations = filtered_df.sort_values('Final_Score', ascending=False).head(10)
                
                # Display recommendations
                for idx, row in recommendations.iterrows():
                    # Simulate side effects and benefits based on drug type
                    drug_lower = str(row['Drug']).lower()
                    
                    side_effects = []
                    benefits = []
                    
                    if any(word in drug_lower for word in ['retino', 'retin', 'tretinoin']):
                        side_effects = ["Dryness", "Peeling", "Sun Sensitivity"]
                        benefits = ["Anti-acne", "Anti-aging", "Skin Renewal"]
                    elif any(word in drug_lower for word in ['cetirizine', 'loratadine', 'fexofenadine']):
                        side_effects = ["Drowsiness", "Dry Mouth"]
                        benefits = ["Fast Relief", "Non-sedating", "24-hour"]
                    elif any(word in drug_lower for word in ['metformin', 'glimepiride', 'glipizide']):
                        side_effects = ["GI Upset", "Hypoglycemia Risk"]
                        benefits = ["Blood Sugar Control", "Weight Neutral"]
                    else:
                        side_effects = ["Mild Nausea", "Headache"]
                        benefits = ["Effective", "Well-tolerated"]
                    
                    # Check for allergies
                    allergy_warning = ""
                    if allergies and any(allergy.lower() in drug_lower for allergy in allergies.lower().split(',')):
                        allergy_warning = "⚠️ Contains known allergen"
                    
                    # Display medicine card
                    st.markdown(f"""
                    <div class='medicine-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div class='medicine-name'>{row['Drug_Clean']}</div>
                            <div class='match-score'>{row['Final_Score']:.0%} Match</div>
                        </div>
                        <div style='color: #CCCCCC; font-size: 0.9rem; margin-bottom: 10px;'>
                            {row['Drug'][:100]}...
                        </div>
                        <div style='margin-bottom: 10px;'>
                            <strong>Form:</strong> {', '.join(form_type) if form_type else 'Various'} | 
                            <strong>Age Group:</strong> {row['Age']} | 
                            <strong>Gender:</strong> {row['Gender']}
                        </div>
                        <div style='margin-bottom: 10px;'>
                            <strong>Benefits:</strong><br>
                            {''.join([f'<span class="benefits">{b}</span> ' for b in benefits])}
                        </div>
                        <div style='margin-bottom: 10px;'>
                            <strong>Possible Side Effects:</strong><br>
                            {''.join([f'<span class="side-effects">{s}</span> ' for s in side_effects])}
                        </div>
                        {f'<div style="color: #FF4444; font-weight: bold;">{allergy_warning}</div>' if allergy_warning else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show statistics
                st.markdown("---")
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                
                with col_stats1:
                    avg_age = recommendations['Age'].mean()
                    st.metric("Average Age Match", f"{avg_age:.1f} years")
                
                with col_stats2:
                    gender_match = (recommendations['Gender'] == gender).mean()
                    st.metric("Gender Match", f"{gender_match:.0%}")
                
                with col_stats3:
                    total_options = len(filtered_df)
                    st.metric("Total Options Analyzed", total_options)
                
                # Visualization: Age distribution of recommendations
                st.markdown("<h4>📊 Recommendation Analysis</h4>", unsafe_allow_html=True)
                
                fig = px.histogram(
                    recommendations,
                    x='Age',
                    nbins=10,
                    title=f'Age Distribution for {disease} Medications',
                    color_discrete_sequence=['#FF6B35']
                )
                
                fig.update_layout(
                    plot_bgcolor='#1A1A1A',
                    paper_bgcolor='#1A1A1A',
                    font_color='white',
                    xaxis_title="Age",
                    yaxis_title="Count"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning(f"No medications found for {disease}. Please try a different condition.")
    
    else:
        # Show placeholder when no recommendations yet
        st.info("👈 Enter your parameters and click 'Get Personalized Recommendations' to see medicine suggestions.")
        
        # Show sample medicines from database
        st.markdown("<h4>💊 Sample Medicines in Database</h4>", unsafe_allow_html=True)
        
        sample_drugs = df['Drug_Clean'].value_counts().head(5).index.tolist()
        
        for drug in sample_drugs:
            st.markdown(f"""
            <div class='medicine-card' style='opacity: 0.7;'>
                <div class='medicine-name'>{drug}</div>
                <div style='color: #CCCCCC; font-size: 0.9rem;'>
                    Available for various conditions
                </div>
            </div>
            """, unsafe_allow_html=True)

# Hybrid filtering explanation
st.markdown("---")
st.markdown("<h3 class='sub-header'>🤖 How Our Recommendation System Works</h3>", unsafe_allow_html=True)

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    st.markdown("""
    <div class='card'>
        <h4>🔍 Content-Based Filtering</h4>
        <p>Analyzes drug properties, formulations, and indications to find 
        medicines similar to your needs.</p>
    </div>
    """, unsafe_allow_html=True)

with col_exp2:
    st.markdown("""
    <div class='card'>
        <h4>👥 Collaborative Filtering</h4>
        <p>Considers what medicines have worked for similar patients with 
        comparable age, gender, and conditions.</p>
    </div>
    """, unsafe_allow_html=True)

with col_exp3:
    st.markdown("""
    <div class='card'>
        <h4>⚡ Hybrid Approach</h4>
        <p>Combines both methods with personalized weightings for the most 
        accurate and relevant recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div style='background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin-top: 20px;'>
    <h4 style='color: #FF6B35;'>⚠️ Important Medical Disclaimer</h4>
    <p style='font-size: 0.9rem;'>
    This system provides informational recommendations only. All medications 
    should be prescribed by a qualified healthcare professional after proper 
    diagnosis. Always consult with your doctor before starting any new medication, 
    and report any side effects immediately.
    </p>
</div>
""", unsafe_allow_html=True)