import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import re
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Medicine Recommendation",
    page_icon="💊",
    layout="wide"
)

from theme import apply_theme
apply_theme()

# Helper function to extract primary drug name
def extract_primary_drug(drug_string):
    """Extract primary drug name from complex string"""
    if pd.isna(drug_string):
        return "Unknown"
    
    drug_string = str(drug_string)
    
    # Remove dosage information (numbers and units)
    drug_string = re.sub(r'\d+\.?\d*\s*(mg|gm|ml|%|IU|mcg|Gm|Ml)', '', drug_string, flags=re.IGNORECASE)
    
    # Remove packaging info
    drug_string = re.sub(r'\d+\s*\'?S\b', '', drug_string)
    drug_string = re.sub(r'\b(\d+gm|\d+ml|\d+%)\b', '', drug_string, flags=re.IGNORECASE)
    drug_string = re.sub(r'\b\d+\s*(capsule|tablet|gel|cream|ointment|injection|syrup|soap|bar|solution|lotion)\b', 
                        '', drug_string, flags=re.IGNORECASE)
    
    # Remove common suffixes
    drug_string = re.sub(r'\([^)]*\)', '', drug_string)  # Remove anything in parentheses
    
    # Split and get first meaningful word
    words = drug_string.split()
    for word in words:
        word_clean = word.strip('(),.-_').upper()  # Convert to uppercase for consistency
        if (len(word_clean) > 2 and 
            not any(char.isdigit() for char in word_clean) and
            word_clean.lower() not in ['tablet', 'capsule', 'gel', 'cream', 'injection', 
                                     'syrup', 'soap', 'bar', 'solution', 'lotion', 'ointment',
                                     'topical', 'oral', 'kit', 'facewash', 'shampoo', 'drops',
                                     'powder', 'spray', 'wash', 'pack']):
            return word_clean
    
    # If no meaningful word found, return first word
    return words[0].upper() if words else "UNKNOWN"

# Initialize session state
def initialize_session_state():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'age': 25,
            'gender': 'Male',
            'medical_history': [],
            'medicine_preferences': [],
            'symptoms': []
        }
    
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    
    if 'drug_data' not in st.session_state:
        # Load drug data
        data_path = "C:/Users/Ankit/OneDrive/Desktop/medi_recomm/Data/Drug.csv"
        try:
            if os.path.exists(data_path):
                drug_data = pd.read_csv(data_path)
                # Clean the data
                drug_data.columns = ['Drug', 'Disease', 'Gender', 'Age']
                drug_data = drug_data.dropna()
                drug_data['Age'] = pd.to_numeric(drug_data['Age'], errors='coerce')
                drug_data = drug_data.dropna(subset=['Age'])
                
                # Create Drug_Clean column
                drug_data['Drug_Clean'] = drug_data['Drug'].apply(extract_primary_drug)
                
                st.session_state.drug_data = drug_data
            else:
                st.session_state.drug_data = pd.DataFrame()
                st.error(f"Data file not found at: {data_path}")
        except Exception as e:
            st.session_state.drug_data = pd.DataFrame()
            st.error(f"Error loading data: {str(e)}")
    
    if 'model_weights' not in st.session_state:
        st.session_state.model_weights = {
            'content_based': 0.5,
            'collaborative': 0.3,
            'user_preferences': 0.2
        }

# Initialize
initialize_session_state()

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
    
    .feedback-btn {
        width: 100%;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Hybrid Recommendation System Class
class HybridRecommender:
    def __init__(self, drug_data):
        self.drug_data = drug_data
        self.tfidf_vectorizer = None
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare data for recommendation"""
        # Create features for content-based filtering
        self.drug_data['Features'] = (
            self.drug_data['Drug'].fillna('') + ' ' +
            self.drug_data['Drug_Clean'].fillna('') + ' ' +
            self.drug_data['Disease'].fillna('')
        )
    
    def content_based_filtering(self, disease, gender, age, form_preferences, n_recommendations=10):
        """Content-based filtering"""
        # Filter by disease first
        filtered_data = self.drug_data[self.drug_data['Disease'] == disease].copy()
        
        if filtered_data.empty:
            return pd.DataFrame()
        
        # Prepare features for TF-IDF
        features = filtered_data['Features'].tolist()
        
        # Add query to features for better matching
        query_text = f"{disease} {gender} {' '.join(form_preferences) if form_preferences else ''}"
        all_features = features + [query_text]
        
        # Fit TF-IDF on combined features
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=500,
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(all_features)
        
        # Separate query vector (last one) from drug vectors
        drug_vectors = tfidf_matrix[:-1]
        query_vector = tfidf_matrix[-1]
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, drug_vectors).flatten()
        
        # Ensure lengths match
        if len(similarities) != len(filtered_data):
            min_len = min(len(similarities), len(filtered_data))
            similarities = similarities[:min_len]
            filtered_data = filtered_data.iloc[:min_len]
        
        filtered_data['Content_Score'] = similarities
        
        # Age similarity (normalized)
        age_diff = np.abs(filtered_data['Age'] - age)
        filtered_data['Age_Score'] = 1 / (1 + age_diff/10)  # Scale by 10 years
        
        # Gender similarity
        filtered_data['Gender_Score'] = (filtered_data['Gender'] == gender).astype(float)
        
        # Form preference score
        def form_score(drug):
            drug_lower = str(drug).lower()
            score = 0
            for form in form_preferences:
                if form.lower() in drug_lower:
                    score += 0.3
            return min(score, 1.0)
        
        filtered_data['Form_Score'] = filtered_data['Drug'].apply(form_score)
        
        # Final content score
        filtered_data['Content_Final'] = (
            filtered_data['Content_Score'] * 0.4 +
            filtered_data['Age_Score'] * 0.3 +
            filtered_data['Gender_Score'] * 0.2 +
            filtered_data['Form_Score'] * 0.1
        )
        
        # Normalize to 0-1
        if len(filtered_data) > 0:
            min_score = filtered_data['Content_Final'].min()
            max_score = filtered_data['Content_Final'].max()
            if max_score > min_score:
                filtered_data['Content_Final'] = (filtered_data['Content_Final'] - min_score) / (max_score - min_score)
        
        return filtered_data.sort_values('Content_Final', ascending=False).head(n_recommendations)
    
    def collaborative_filtering(self, filtered_data, age, gender, disease):
        """Simple collaborative filtering"""
        if filtered_data.empty:
            return filtered_data
        
        # Create a copy to avoid modifying original
        result = filtered_data.copy()
        
        # Calculate basic collaborative scores
        # 1. Age group popularity (10-year groups)
        age_group = age // 10 * 10
        
        # Count drugs by age group and disease
        age_group_counts = {}
        gender_counts = {}
        
        # Calculate counts from full dataset
        for idx, row in self.drug_data.iterrows():
            if row['Disease'] == disease:
                drug_name = row['Drug_Clean']
                
                # Age group count
                drug_age_group = row['Age'] // 10 * 10
                if drug_age_group == age_group:
                    age_group_counts[drug_name] = age_group_counts.get(drug_name, 0) + 1
                
                # Gender count
                if row['Gender'] == gender:
                    gender_counts[drug_name] = gender_counts.get(drug_name, 0) + 1
        
        # Calculate collaborative scores
        result['Age_Popularity'] = result['Drug_Clean'].map(age_group_counts).fillna(0)
        result['Gender_Popularity'] = result['Drug_Clean'].map(gender_counts).fillna(0)
        
        # Normalize popularity scores
        if result['Age_Popularity'].max() > 0:
            result['Age_Popularity'] = result['Age_Popularity'] / result['Age_Popularity'].max()
        
        if result['Gender_Popularity'].max() > 0:
            result['Gender_Popularity'] = result['Gender_Popularity'] / result['Gender_Popularity'].max()
        
        # Combined collaborative score
        result['Collaborative_Score'] = (
            result['Age_Popularity'] * 0.5 +
            result['Gender_Popularity'] * 0.5
        )
        
        # Fill NaN values
        result['Collaborative_Score'] = result['Collaborative_Score'].fillna(0)
        
        return result
    
    def calculate_preference_score(self, recommendations, user_feedback):
        """Calculate user preference score"""
        if recommendations.empty:
            recommendations['Preference_Score'] = 0
            return recommendations
        
        # Create feedback dictionaries
        liked_drugs = {}
        disliked_drugs = {}
        
        if user_feedback:
            for feedback in user_feedback:
                drug = feedback.get('drug', '')
                if drug:
                    if feedback.get('feedback') == 'like':
                        liked_drugs[drug] = liked_drugs.get(drug, 0) + 1
                    elif feedback.get('feedback') == 'dislike':
                        disliked_drugs[drug] = disliked_drugs.get(drug, 0) + 1
        
        def get_preference_score(drug_clean):
            score = 0
            if drug_clean in liked_drugs:
                score += min(0.3, liked_drugs[drug_clean] * 0.1)
            if drug_clean in disliked_drugs:
                score -= min(0.3, disliked_drugs[drug_clean] * 0.1)
            return score
        
        recommendations['Preference_Score'] = recommendations['Drug_Clean'].apply(get_preference_score)
        
        # Update model weights based on feedback
        if user_feedback:
            feedback_count = len(user_feedback)
            if feedback_count > 3:
                weight_adjustment = min(0.15, feedback_count * 0.02)
                st.session_state.model_weights['user_preferences'] = 0.2 + weight_adjustment
                st.session_state.model_weights['content_based'] = 0.5 - weight_adjustment/2
                st.session_state.model_weights['collaborative'] = 0.3 - weight_adjustment/2
        
        return recommendations
    
    def hybrid_recommendation(self, disease, gender, age, form_preferences, 
                            user_feedback=None, n_recommendations=10):
        """Hybrid recommendation combining all methods"""
        # Step 1: Content-based filtering
        content_rec = self.content_based_filtering(
            disease, gender, age, form_preferences, 
            n_recommendations * 3
        )
        
        if content_rec.empty:
            return pd.DataFrame()
        
        # Step 2: Collaborative filtering
        collab_rec = self.collaborative_filtering(content_rec.copy(), age, gender, disease)
        
        # Step 3: Apply user preferences
        collab_rec = self.calculate_preference_score(collab_rec, user_feedback)
        
        # Step 4: Calculate final hybrid score
        weights = st.session_state.model_weights
        
        # Ensure all required columns exist
        required_columns = ['Content_Final', 'Collaborative_Score', 'Preference_Score']
        for col in required_columns:
            if col not in collab_rec.columns:
                collab_rec[col] = 0
        
        collab_rec['Hybrid_Score'] = (
            collab_rec['Content_Final'] * weights['content_based'] +
            collab_rec['Collaborative_Score'] * weights['collaborative'] +
            collab_rec['Preference_Score'] * weights['user_preferences']
        )
        
        # Normalize hybrid score to 0-1 range
        if not collab_rec.empty:
            min_score = collab_rec['Hybrid_Score'].min()
            max_score = collab_rec['Hybrid_Score'].max()
            if max_score > min_score:
                collab_rec['Hybrid_Score'] = (collab_rec['Hybrid_Score'] - min_score) / (max_score - min_score)
            else:
                collab_rec['Hybrid_Score'] = 0.5
        
        # Remove duplicates and get top recommendations
        final_rec = collab_rec.sort_values('Hybrid_Score', ascending=False)
        final_rec = final_rec.drop_duplicates(subset=['Drug_Clean']).head(n_recommendations)
        
        return final_rec

# Initialize recommender if data exists
if not st.session_state.drug_data.empty:
    recommender = HybridRecommender(st.session_state.drug_data.copy())
else:
    recommender = None

# Main UI
st.markdown("<h1 class='main-header'>💊 Personalized Medicine Recommendation</h1>", unsafe_allow_html=True)

# Show notification if coming from disease prediction
if 'predicted_disease' in st.session_state:
    st.success(f"🎯 Based on your disease prediction: **{st.session_state.predicted_disease}**")
    st.info("💡 We've pre-selected your predicted condition. You can change it if needed.")

# Check if drug data exists
if st.session_state.drug_data.empty:
    st.error("Drug data not loaded. Please check the data file.")
    st.stop()

if recommender is None:
    st.error("Recommender system could not be initialized.")
    st.stop()

# Create two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<h3 class='sub-header'>🎯 Input Parameters</h3>", unsafe_allow_html=True)
    
    # Disease selection
    diseases = sorted(st.session_state.drug_data['Disease'].unique().tolist())
    
    if 'predicted_disease' in st.session_state:
        default_disease = st.session_state.predicted_disease
        disease_index = 0
        for i, d in enumerate(diseases):
            if default_disease.lower() in d.lower():
                disease_index = i
                break
    else:
        disease_index = 0 if 'Acne' in diseases else 0
    
    disease = st.selectbox(
        "Select Disease",
        diseases,
        index=disease_index,
        help="Select the disease or condition"
    )
    
    # Age and gender
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
    
    form_options = ["Tablet", "Capsule", "Gel", "Cream", "Lotion", "Injection", "Syrup", "Soap", "Bar", "Solution"]
    form_type = st.multiselect(
        "Preferred Form",
        form_options,
        default=["Tablet", "Capsule"]
    )
    
    # Severity level
    severity = st.select_slider(
        "Condition Severity",
        options=["Mild", "Moderate", "Severe"],
        value="Moderate"
    )
    
    # Known allergies or restrictions
    allergies = st.text_input(
        "Known Allergies (comma separated)",
        placeholder="e.g., penicillin, sulfa drugs"
    )
    
    # Advanced filters
    with st.expander("Advanced Filters"):
        min_age = st.slider(
            "Minimum Age for Medication",
            min_value=0,
            max_value=100,
            value=0,
            help="Filter out medications typically for younger ages"
        )
        
        max_age = st.slider(
            "Maximum Age for Medication",
            min_value=0,
            max_value=100,
            value=100,
            help="Filter out medications typically for older ages"
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
            # Apply age filters
            filtered_drugs = st.session_state.drug_data.copy()
            filtered_drugs = filtered_drugs[
                (filtered_drugs['Age'] >= min_age) & 
                (filtered_drugs['Age'] <= max_age)
            ]
            
            if filtered_drugs.empty:
                st.warning("No medications found with the selected age filters. Please adjust the filters.")
            else:
                # Update recommender with filtered data
                recommender_filtered = HybridRecommender(filtered_drugs)
                
                # Get recommendations
                recommendations = recommender_filtered.hybrid_recommendation(
                    disease=disease,
                    gender=gender,
                    age=age,
                    form_preferences=form_type if form_type else [],
                    user_feedback=st.session_state.feedback_history,
                    n_recommendations=8
                )
                
                if not recommendations.empty:
                    # Display recommendations
                    for idx, row in recommendations.iterrows():
                        # Simulate side effects and benefits
                        drug_lower = str(row['Drug']).lower()
                        
                        # Determine drug category
                        if any(word in drug_lower for word in ['retino', 'retin', 'tretinoin', 'isotret', 'acne']):
                            category = "Acne Treatment"
                            side_effects = ["Dryness", "Peeling", "Sun Sensitivity"]
                            benefits = ["Anti-acne", "Anti-aging", "Skin Renewal"]
                        elif any(word in drug_lower for word in ['cetirizine', 'loratadine', 'fexofenadine', 'montelukast', 'allergy']):
                            category = "Allergy/Asthma"
                            side_effects = ["Drowsiness", "Dry Mouth", "Headache"]
                            benefits = ["Fast Relief", "Non-sedating", "24-hour"]
                        elif any(word in drug_lower for word in ['metformin', 'glimepiride', 'glipizide', 'insulin', 'diabetes']):
                            category = "Diabetes"
                            side_effects = ["GI Upset", "Hypoglycemia Risk"]
                            benefits = ["Blood Sugar Control", "Weight Neutral"]
                        else:
                            category = "General"
                            side_effects = ["Mild Nausea", "Headache", "Dizziness"]
                            benefits = ["Effective", "Well-tolerated", "Affordable"]
                        
                        # Check for allergies
                        allergy_warning = ""
                        if allergies:
                            allergy_list = [a.strip().lower() for a in allergies.split(',')]
                            if any(allergy in drug_lower for allergy in allergy_list):
                                allergy_warning = "⚠️ Possible allergen detected!"
                        
                        # Display medicine card
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            match_score = row['Hybrid_Score'] * 100
                            
                            st.markdown(f"""
                            <div class='medicine-card'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <div>
                                        <div class='medicine-name'>{row['Drug_Clean']}</div>
                                        <div style='color: #888; font-size: 0.8rem;'>{category}</div>
                                    </div>
                                    <div class='match-score'>{match_score:.0f}% Match</div>
                                </div>
                                <div style='color: #CCCCCC; font-size: 0.9rem; margin: 10px 0;'>
                                    {row['Drug'][:100]}...
                                </div>
                                <div style='margin-bottom: 10px; font-size: 0.9rem;'>
                                    <strong>Patient:</strong> Age {int(row['Age'])}, {row['Gender']}<br>
                                    <strong>Content:</strong> {(row['Content_Final'] * 100):.0f}% | 
                                    <strong>Collaborative:</strong> {(row['Collaborative_Score'] * 100):.0f}%
                                </div>
                                <div style='margin-bottom: 10px;'>
                                    <strong>✅ Benefits:</strong><br>
                                    {''.join([f'<span class="benefits">{b}</span> ' for b in benefits[:2]])}
                                </div>
                                <div style='margin-bottom: 10px;'>
                                    <strong>⚠️ Side Effects:</strong><br>
                                    {''.join([f'<span class="side-effects">{s}</span> ' for s in side_effects[:2]])}
                                </div>
                                {f'<div style="color: #FF4444; font-weight: bold; margin-top: 10px;">{allergy_warning}</div>' if allergy_warning else ''}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_b:
                            # Feedback buttons
                            st.markdown("<br><br>", unsafe_allow_html=True)
                            
                            # Create unique keys
                            like_key = f"like_{row['Drug_Clean']}_{idx}_{disease.replace(' ', '_')}"
                            dislike_key = f"dislike_{row['Drug_Clean']}_{idx}_{disease.replace(' ', '_')}"
                            
                            if st.button("👍 Like", key=like_key, use_container_width=True):
                                st.session_state.feedback_history.append({
                                    'drug': row['Drug_Clean'],
                                    'feedback': 'like',
                                    'timestamp': datetime.now().isoformat(),
                                    'disease': disease,
                                    'user_age': age,
                                    'user_gender': gender
                                })
                                st.success("✓ Feedback recorded! System learning...")
                                st.rerun()
                            
                            if st.button("👎 Dislike", key=dislike_key, use_container_width=True):
                                st.session_state.feedback_history.append({
                                    'drug': row['Drug_Clean'],
                                    'feedback': 'dislike',
                                    'timestamp': datetime.now().isoformat(),
                                    'disease': disease,
                                    'user_age': age,
                                    'user_gender': gender
                                })
                                st.success("✓ Feedback recorded! System learning...")
                                st.rerun()
                    
                    # Show statistics
                    st.markdown("---")
                    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                    
                    with col_stats1:
                        avg_age = recommendations['Age'].mean()
                        st.metric("Avg. Age Match", f"{avg_age:.1f} years")
                    
                    with col_stats2:
                        gender_match = (recommendations['Gender'] == gender).mean() * 100
                        st.metric("Gender Match", f"{gender_match:.0f}%")
                    
                    with col_stats3:
                        avg_score = recommendations['Hybrid_Score'].mean() * 100
                        st.metric("Avg. Match Score", f"{avg_score:.0f}%")
                    
                    with col_stats4:
                        feedback_count = len(st.session_state.feedback_history)
                        st.metric("Feedback Used", feedback_count)
                    
                    # Model weights visualization
                    st.markdown("#### 🎚️ Model Weight Distribution")
                    weights = st.session_state.model_weights
                    
                    fig_weights = go.Figure(data=[
                        go.Bar(
                            x=['Content-Based', 'Collaborative', 'User Preferences'],
                            y=[weights['content_based'], weights['collaborative'], weights['user_preferences']],
                            text=[f"{v:.0%}" for v in [weights['content_based'], weights['collaborative'], weights['user_preferences']]],
                            textposition='auto',
                            marker_color=['#FF6B35', '#4CAF50', '#2196F3']
                        )
                    ])
                    
                    fig_weights.update_layout(
                        plot_bgcolor='#1A1A1A',
                        paper_bgcolor='#1A1A1A',
                        font_color='white',
                        yaxis=dict(range=[0, 0.7], tickformat=".0%"),
                        height=300
                    )
                    
                    st.plotly_chart(fig_weights, use_container_width=True)
                    
                    # Show feedback influence if exists
                    if st.session_state.feedback_history:
                        st.markdown("#### 📝 Your Feedback Influence")
                        
                        liked = len([f for f in st.session_state.feedback_history if f['feedback'] == 'like'])
                        disliked = len([f for f in st.session_state.feedback_history if f['feedback'] == 'dislike'])
                        
                        col_fb1, col_fb2, col_fb3 = st.columns(3)
                        
                        with col_fb1:
                            st.metric("👍 Liked Medications", liked)
                        
                        with col_fb2:
                            st.metric("👎 Disliked Medications", disliked)
                        
                        with col_fb3:
                            total_fb = liked + disliked
                            st.metric("Total Feedback", total_fb)
                        
                        # Show recent feedback
                        if st.checkbox("Show detailed feedback history"):
                            if st.session_state.feedback_history:
                                feedback_df = pd.DataFrame(st.session_state.feedback_history)
                                st.dataframe(feedback_df[['drug', 'feedback', 'disease']])
                            
                            # Reset feedback button
                            if st.button("Clear All Feedback"):
                                st.session_state.feedback_history = []
                                st.session_state.model_weights = {
                                    'content_based': 0.5,
                                    'collaborative': 0.3,
                                    'user_preferences': 0.2
                                }
                                st.success("Feedback history cleared!")
                                st.rerun()
                
                else:
                    st.warning(f"No medications found for {disease} with the selected filters. Please try different parameters.")
    
    else:
        # Show placeholder when no recommendations yet
        st.info("👈 Enter your parameters and click 'Get Personalized Recommendations' to see medicine suggestions.")
        
        # Show quick stats
        col_quick1, col_quick2, col_quick3 = st.columns(3)
        
        with col_quick1:
            total_meds = len(st.session_state.drug_data)
            st.metric("Total Medicines", f"{total_meds:,}")
        
        with col_quick2:
            if 'Drug_Clean' in st.session_state.drug_data.columns:
                unique_drugs = len(st.session_state.drug_data['Drug_Clean'].unique())
                st.metric("Unique Drugs", unique_drugs)
            else:
                st.metric("Unique Drugs", "N/A")
        
        with col_quick3:
            st.metric("Feedback Count", len(st.session_state.feedback_history))

# System Explanation
st.markdown("---")
st.markdown("<h3 class='sub-header'>🤖 How Our Hybrid System Works</h3>", unsafe_allow_html=True)

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #FF6B35;'>🔍 Content-Based Filtering</h4>
        <p>Analyzes drug names, descriptions, and formulations to match 
        your specific medical condition and preferences.</p>
        <ul style='font-size: 0.9rem;'>
        <li>Drug name similarity analysis</li>
        <li>Formulation matching</li>
        <li>Disease-specific relevance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_exp2:
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #4CAF50;'>👥 Collaborative Filtering</h4>
        <p>Learns from treatment patterns of patients similar to you 
        based on age, gender, and medical history.</p>
        <ul style='font-size: 0.9rem;'>
        <li>Age group effectiveness patterns</li>
        <li>Gender-specific treatment success</li>
        <li>Popular medication choices</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_exp3:
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #2196F3;'>🎯 Personalized Learning</h4>
        <p>Adapts to your feedback to provide increasingly accurate 
        recommendations tailored to your preferences.</p>
        <ul style='font-size: 0.9rem;'>
        <li>Learn from your feedback (👍/👎)</li>
        <li>Adaptive model reweighting</li>
        <li>Continuous improvement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Medical Disclaimer
st.markdown("""
<div style='background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin-top: 30px;'>
    <h4 style='color: #FF6B35;'>⚠️ Important Medical Disclaimer</h4>
    <p style='font-size: 0.9rem;'>
    <strong>This is an AI-powered recommendation system for informational purposes only.</strong><br><br>
    
    • Always consult with a qualified healthcare professional before starting any medication<br>
    • The recommendations are based on general patterns and may not be suitable for your specific case<br>
    • Report any side effects or adverse reactions to your doctor immediately<br>
    • Never self-medicate based solely on AI recommendations<br>
    • Keep your doctor informed about all medications you're taking
    </p>
</div>
""", unsafe_allow_html=True)

# Debug section (optional)
if st.checkbox("Show Debug Information", False):
    st.write("### Debug Information")
    st.write("Drug Data Shape:", st.session_state.drug_data.shape)
    st.write("Drug Data Columns:", st.session_state.drug_data.columns.tolist())
    st.write("Sample Drug Clean Names:", st.session_state.drug_data['Drug_Clean'].head(10).tolist() if 'Drug_Clean' in st.session_state.drug_data.columns else "Column not found")
    st.write("Feedback History Length:", len(st.session_state.feedback_history))
    st.write("Model Weights:", st.session_state.model_weights)