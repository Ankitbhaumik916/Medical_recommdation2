# ============================================================================
# COMPLETE MEDICINE RECOMMENDATION SYSTEM - SINGLE FILE INTEGRATION
# ============================================================================
# This is a complete, production-ready Streamlit app combining:
# 1. Neural Collaborative Filtering (NCF) with TensorFlow
# 2. Context-Based Filtering (TF-IDF + Collaborative)
# 3. Your existing medicine recommendation UI
# 4. Full integration with disease prediction
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import re
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Medicine Recommendation",
    page_icon="💊",
    layout="wide"
)

# Try to apply theme if available
try:
    from theme import apply_theme
    apply_theme()
except ImportError:
    pass

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

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
    
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .ncf-badge {
        background-color: #2196F3;
        color: white;
    }
    
    .context-badge {
        background-color: #4CAF50;
        color: white;
    }
    
    .hybrid-badge {
        background-color: #FF6B35;
        color: white;
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

# ============================================================================
# PART 1: DATA HANDLER & FEATURE ENGINEERING
# ============================================================================

def extract_primary_drug(drug_string):
    """Extract primary drug name from complex string"""
    if pd.isna(drug_string):
        return "Unknown"
    
    drug_string = str(drug_string)
    
    # Remove dosage information
    drug_string = re.sub(r'\d+\.?\d*\s*(mg|gm|ml|%|IU|mcg|Gm|Ml)', '', drug_string, flags=re.IGNORECASE)
    
    # Remove packaging info
    drug_string = re.sub(r'\d+\s*\'?S\b', '', drug_string)
    drug_string = re.sub(r'\b(\d+gm|\d+ml|\d+%)\b', '', drug_string, flags=re.IGNORECASE)
    drug_string = re.sub(r'\b\d+\s*(capsule|tablet|gel|cream|ointment|injection|syrup|soap|bar|solution|lotion)\b', 
                        '', drug_string, flags=re.IGNORECASE)
    
    # Remove parentheses
    drug_string = re.sub(r'\([^)]*\)', '', drug_string)
    
    # Get first meaningful word
    words = drug_string.split()
    for word in words:
        word_clean = word.strip('(),.-_').upper()
        if (len(word_clean) > 2 and 
            not any(char.isdigit() for char in word_clean) and
            word_clean.lower() not in ['tablet', 'capsule', 'gel', 'cream', 'injection', 
                                     'syrup', 'soap', 'bar', 'solution', 'lotion', 'ointment',
                                     'topical', 'oral', 'kit', 'facewash', 'shampoo', 'drops',
                                     'powder', 'spray', 'wash', 'pack']):
            return word_clean
    
    return words[0].upper() if words else "UNKNOWN"


def load_and_prepare_data(data_path):
    """Load and prepare dataset with feature engineering"""
    try:
        # Load CSV
        drug_data = pd.read_csv(data_path)
        
        # Ensure correct column names
        drug_data.columns = ['Drug', 'Disease', 'Gender', 'Age']
        
        # Data cleaning
        drug_data = drug_data.dropna()
        drug_data['Age'] = pd.to_numeric(drug_data['Age'], errors='coerce')
        drug_data = drug_data.dropna(subset=['Age'])
        
        # Extract primary drug names
        drug_data['Drug_Clean'] = drug_data['Drug'].apply(extract_primary_drug)
        
        # Create features for content-based filtering
        drug_data['Features'] = (
            drug_data['Drug'].fillna('') + ' ' +
            drug_data['Drug_Clean'].fillna('') + ' ' +
            drug_data['Disease'].fillna('')
        )
        
        return drug_data
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


# ============================================================================
# PART 2: NEURAL COLLABORATIVE FILTERING MODEL
# ============================================================================

def build_ncf_model(num_drugs, num_diseases, num_genders, embedding_dim=64):
    """Build and return NCF model"""
    
    # Input layers
    drug_input = layers.Input(shape=(1,), dtype='int32', name='drug_input')
    disease_input = layers.Input(shape=(1,), dtype='int32', name='disease_input')
    gender_input = layers.Input(shape=(1,), dtype='int32', name='gender_input')
    age_input = layers.Input(shape=(1,), dtype='float32', name='age_input')
    
    # Embedding layers
    drug_embed = layers.Embedding(num_drugs, embedding_dim, name='drug_embedding')(drug_input)
    drug_vec = layers.Flatten(name='drug_flatten')(drug_embed)
    
    disease_embed = layers.Embedding(num_diseases, embedding_dim, name='disease_embedding')(disease_input)
    disease_vec = layers.Flatten(name='disease_flatten')(disease_embed)
    
    gender_embed = layers.Embedding(num_genders, 8, name='gender_embedding')(gender_input)
    gender_vec = layers.Flatten(name='gender_flatten')(gender_embed)
    
    # Concatenate features
    concat = layers.Concatenate(name='concat_features')([drug_vec, disease_vec, gender_vec, age_input])
    
    # Dense layers (MLP)
    dense1 = layers.Dense(256, activation='relu', name='dense1')(concat)
    dropout1 = layers.Dropout(0.3, name='dropout1')(dense1)
    
    dense2 = layers.Dense(128, activation='relu', name='dense2')(dropout1)
    dropout2 = layers.Dropout(0.3, name='dropout2')(dense2)
    
    dense3 = layers.Dense(64, activation='relu', name='dense3')(dropout2)
    dropout3 = layers.Dropout(0.2, name='dropout3')(dense3)
    
    dense4 = layers.Dense(32, activation='relu', name='dense4')(dropout3)
    
    # Output layer
    output = layers.Dense(1, activation='sigmoid', name='output')(dense4)
    
    # Create model
    model = Model(
        inputs=[drug_input, disease_input, gender_input, age_input],
        outputs=output,
        name='NCF_Medicine_Recommender'
    )
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.AUC()]
    )
    
    return model


def train_ncf_model(model, drug_data, epochs=3):
    """Train the NCF model"""
    
    # Encode features
    drug_encoder = LabelEncoder()
    disease_encoder = LabelEncoder()
    gender_encoder = LabelEncoder()
    
    drug_data['Drug_Encoded'] = drug_encoder.fit_transform(drug_data['Drug_Clean'])
    drug_data['Disease_Encoded'] = disease_encoder.fit_transform(drug_data['Disease'])
    drug_data['Gender_Encoded'] = gender_encoder.fit_transform(drug_data['Gender'])
    
    # Normalize age
    age_min, age_max = drug_data['Age'].min(), drug_data['Age'].max()
    drug_data['Age_Normalized'] = (drug_data['Age'] - age_min) / (age_max - age_min)
    
    # Training data
    drug_ids = drug_data['Drug_Encoded'].values
    disease_ids = drug_data['Disease_Encoded'].values
    gender_ids = drug_data['Gender_Encoded'].values
    ages = drug_data['Age_Normalized'].values
    y = np.ones(len(drug_data))
    
    # Train
    history = model.fit(
        [drug_ids, disease_ids, gender_ids, ages],
        y,
        epochs=epochs,
        batch_size=32,
        validation_split=0.2,
        verbose=0
    )
    
    return model, drug_encoder, disease_encoder, gender_encoder, (age_min, age_max)


# ============================================================================
# PART 3: CONTENT & COLLABORATIVE FILTERING
# ============================================================================

def get_content_score(disease, drug_name, drug_data, tfidf_vectorizer, tfidf_matrix):
    """Calculate content-based similarity score"""
    try:
        # Create query
        query_text = f"{drug_name} {disease.lower()}"
        query_vector = tfidf_vectorizer.transform([query_text])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        # Get average for this disease
        disease_mask = drug_data['Disease'] == disease
        if disease_mask.sum() > 0:
            relevant_similarities = similarities[disease_mask]
            return float(np.mean(relevant_similarities))
        return 0.0
    except:
        return 0.5


def get_collaborative_score(disease, gender, age, drug_data):
    """Calculate collaborative filtering score"""
    try:
        # Find similar patients
        similar_patients = drug_data[
            (drug_data['Gender'] == gender) &
            (np.abs(drug_data['Age'] - age) <= 5) &
            (drug_data['Disease'] == disease)
        ]
        
        if len(similar_patients) == 0:
            return 0.5
        
        collab_score = len(similar_patients) / len(drug_data)
        return float(min(1.0, collab_score))
    except:
        return 0.5


# ============================================================================
# PART 4: SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize or restore session state"""
    
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
    
    if 'model_weights' not in st.session_state:
        st.session_state.model_weights = {
            'ncf': 0.6,
            'context': 0.4
        }
    
    if 'drug_data' not in st.session_state:
        st.session_state.drug_data = None
        st.session_state.ncf_model = None
        st.session_state.encoders = None
        st.session_state.tfidf_vectorizer = None
        st.session_state.tfidf_matrix = None


initialize_session_state()

# ============================================================================
# PART 5: LOAD AND CACHE MODEL
# ============================================================================

@st.cache_resource
def load_recommendation_system(data_path):
    """Load and initialize the complete recommendation system"""
    
    try:
        with st.spinner("🔄 Loading and training hybrid recommendation system..."):
            
            # Load data
            drug_data = load_and_prepare_data(data_path)
            if drug_data is None:
                return None
            
            st.write(f"✓ Data loaded: {len(drug_data)} records, {len(drug_data['Drug_Clean'].unique())} unique drugs")
            
            # Prepare TF-IDF
            tfidf_vectorizer = TfidfVectorizer(
                max_features=300,
                ngram_range=(1, 2),
                stop_words='english'
            )
            tfidf_matrix = tfidf_vectorizer.fit_transform(drug_data['Features'])
            
            # Build and train NCF model
            num_drugs = len(drug_data['Drug_Clean'].unique())
            num_diseases = len(drug_data['Disease'].unique())
            num_genders = 2
            
            ncf_model = build_ncf_model(num_drugs, num_diseases, num_genders, embedding_dim=64)
            
            st.write("Training NCF model...")
            ncf_model, drug_encoder, disease_encoder, gender_encoder, age_stats = train_ncf_model(
                ncf_model, drug_data.copy(), epochs=3
            )
            
            st.success("✓ Hybrid recommendation system initialized!")
            
            return {
                'drug_data': drug_data,
                'ncf_model': ncf_model,
                'drug_encoder': drug_encoder,
                'disease_encoder': disease_encoder,
                'gender_encoder': gender_encoder,
                'age_stats': age_stats,
                'tfidf_vectorizer': tfidf_vectorizer,
                'tfidf_matrix': tfidf_matrix
            }
            
    except Exception as e:
        st.error(f"Error loading system: {str(e)}")
        return None


# ============================================================================
# PART 6: HYBRID RECOMMENDATION LOGIC
# ============================================================================

def get_hybrid_recommendations(system, disease, gender, age, form_preferences, 
                              ncf_weight=0.6, context_weight=0.4, n_recommendations=10):
    """Get hybrid recommendations combining NCF and context"""
    
    try:
        drug_data = system['drug_data'].copy()
        ncf_model = system['ncf_model']
        drug_encoder = system['drug_encoder']
        disease_encoder = system['disease_encoder']
        gender_encoder = system['gender_encoder']
        age_min, age_max = system['age_stats']
        tfidf_vectorizer = system['tfidf_vectorizer']
        tfidf_matrix = system['tfidf_matrix']
        
        # Normalize age
        age_normalized = (age - age_min) / (age_max - age_min)
        
        # Encode disease and gender
        try:
            disease_id = disease_encoder.transform([disease])[0]
            gender_id = gender_encoder.transform([gender])[0]
        except ValueError:
            st.error(f"Unknown disease or gender")
            return pd.DataFrame()
        
        # Filter drugs for disease
        disease_drugs = drug_data[drug_data['Disease'] == disease].copy()
        
        if disease_drugs.empty:
            st.warning(f"No drugs found for {disease}")
            return pd.DataFrame()
        
        recommendations = []
        
        for _, drug_row in disease_drugs.iterrows():
            drug_name = drug_row['Drug_Clean']
            
            try:
                drug_id = drug_encoder.transform([drug_name])[0]
            except ValueError:
                continue
            
            # NCF Score
            ncf_score = float(ncf_model.predict(
                [
                    np.array([drug_id]),
                    np.array([disease_id]),
                    np.array([gender_id]),
                    np.array([age_normalized])
                ],
                verbose=0
            )[0][0])
            
            # Context Scores
            content_score = get_content_score(disease, drug_name, drug_data, tfidf_vectorizer, tfidf_matrix)
            collab_score = get_collaborative_score(disease, gender, age, drug_data)
            context_score = (content_score * 0.6) + (collab_score * 0.4)
            
            # Hybrid Score
            hybrid_score = (ncf_score * ncf_weight) + (context_score * context_weight)
            
            # Form preference boost
            form_boost = 0.0
            if form_preferences:
                drug_lower = str(drug_row['Drug']).lower()
                for form in form_preferences:
                    if form.lower() in drug_lower:
                        form_boost = 0.15
                        break
            
            final_score = min(1.0, hybrid_score + form_boost)
            
            recommendations.append({
                'Drug': drug_row['Drug'],
                'Drug_Clean': drug_name,
                'Disease': disease,
                'Age': drug_row['Age'],
                'Gender': drug_row['Gender'],
                'NCF_Score': ncf_score,
                'Content_Score': content_score,
                'Collaborative_Score': collab_score,
                'Context_Score': context_score,
                'Form_Boost': form_boost,
                'Final_Score': final_score
            })
        
        # Sort and return top N
        recommendations_df = pd.DataFrame(recommendations)
        recommendations_df = recommendations_df.sort_values('Final_Score', ascending=False)
        recommendations_df = recommendations_df.drop_duplicates(subset=['Drug_Clean'])
        
        return recommendations_df.head(n_recommendations)
        
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return pd.DataFrame()


# ============================================================================
# PART 7: MAIN UI
# ============================================================================

# Header
st.markdown("<h1 class='main-header'>💊 AI-Powered Medicine Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Hybrid NCF + Context-Based Recommendation</p>", unsafe_allow_html=True)

# Check for predicted disease
if 'predicted_disease' in st.session_state:
    st.success(f"🎯 Disease Predicted: **{st.session_state.predicted_disease}**")

# Find dataset
data_paths = [
    "Drug.csv",
    "./Data/Drug.csv",
    "Data/Drug.csv",
    os.path.expanduser("~/Desktop/medi_recomm/Data/Drug.csv"),
    os.path.expanduser("~/Downloads/Drug.csv"),
]

dataset_path = None
for path in data_paths:
    if os.path.exists(path):
        dataset_path = path
        break

if dataset_path is None:
    st.error("❌ Dataset (Drug.csv) not found!")
    st.info("""
    Please ensure Drug.csv exists in one of these locations:
    - Current directory
    - ./Data/ subdirectory
    - ~/Desktop/medi_recomm/Data/
    - ~/Downloads/
    """)
    st.stop()

st.info(f"📂 Dataset: `{dataset_path}`")

# Load system
system = load_recommendation_system(dataset_path)
if system is None:
    st.stop()

# Main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<h3 class='sub-header'>🎯 Patient Information</h3>", unsafe_allow_html=True)
    
    # Disease selection
    diseases = sorted(system['drug_data']['Disease'].unique().tolist())
    
    disease_index = 0
    if 'predicted_disease' in st.session_state:
        for i, d in enumerate(diseases):
            if st.session_state.predicted_disease.lower() in d.lower():
                disease_index = i
                break
    
    disease = st.selectbox(
        "🦠 Select Disease/Condition",
        diseases,
        index=disease_index
    )
    
    # Demographics
    col1a, col1b = st.columns(2)
    with col1a:
        age = st.number_input(
            "👤 Age (years)",
            min_value=1,
            max_value=120,
            value=st.session_state.user_data['age']
        )
    
    with col1b:
        gender = st.selectbox(
            "⚖️ Gender",
            ["Male", "Female"],
            index=0 if st.session_state.user_data['gender'] == "Male" else 1
        )
    
    # Form preferences
    st.markdown("<h4>💊 Medication Preferences</h4>", unsafe_allow_html=True)
    form_options = ["Tablet", "Capsule", "Gel", "Cream", "Lotion", "Injection", 
                    "Syrup", "Soap", "Bar", "Solution"]
    form_type = st.multiselect(
        "Select Preferred Forms",
        form_options,
        default=["Tablet", "Capsule"]
    )
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("**Model Weights**")
        ncf_weight = st.slider(
            "NCF Weight (Collaborative)",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1
        )
        context_weight = 1.0 - ncf_weight
        st.metric("Context Weight", f"{context_weight:.1f}")
        
        st.markdown("**Filters**")
        min_age = st.slider("Min Age", 0, 100, 0)
        max_age = st.slider("Max Age", 0, 100, 100)
    
    # Get recommendations button
    get_recommendations = st.button(
        "🔍 Get Recommendations",
        type="primary",
        use_container_width=True
    )

with col2:
    st.markdown("<h3 class='sub-header'>📋 Personalized Recommendations</h3>", unsafe_allow_html=True)
    
    if get_recommendations:
        with st.spinner("🤖 Analyzing with Hybrid NCF + Context..."):
            # Filter by age
            filtered_data = system['drug_data'].copy()
            filtered_data = filtered_data[
                (filtered_data['Age'] >= min_age) & 
                (filtered_data['Age'] <= max_age)
            ]
            
            if filtered_data.empty:
                st.warning("No medicines found with selected age filters")
            else:
                # Get recommendations
                recommendations = get_hybrid_recommendations(
                    system,
                    disease=disease,
                    gender=gender,
                    age=age,
                    form_preferences=form_type if form_type else None,
                    ncf_weight=ncf_weight,
                    context_weight=context_weight,
                    n_recommendations=10
                )
                
                if not recommendations.empty:
                    st.success(f"✓ Found {len(recommendations)} recommendations")
                    
                    # Display recommendations
                    for idx, (_, row) in enumerate(recommendations.iterrows()):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.markdown(f"""
                            <div class='medicine-card'>
                                <div style='display: flex; justify-content: space-between; align-items: start;'>
                                    <div>
                                        <div class='medicine-name'>{row['Drug_Clean']}</div>
                                        <div style='color: #888; font-size: 0.9rem;'>{row['Drug'][:80]}...</div>
                                    </div>
                                    <div class='match-score'>{row['Final_Score']*100:.0f}% Match</div>
                                </div>
                                
                                <div style='margin-top: 12px; margin-bottom: 8px;'>
                                    <span class='score-badge ncf-badge'>NCF: {row['NCF_Score']:.2f}</span>
                                    <span class='score-badge context-badge'>Context: {row['Context_Score']:.2f}</span>
                                    <span class='score-badge hybrid-badge'>Final: {row['Final_Score']:.2f}</span>
                                </div>
                                
                                <div style='font-size: 0.85rem; color: #CCC; margin-bottom: 8px;'>
                                    <strong>Patient Match:</strong> Age {int(row['Age'])}, {row['Gender']}
                                </div>
                                
                                <div style='font-size: 0.85rem; color: #CCC;'>
                                    <strong>Score Breakdown:</strong><br>
                                    • Content: {row['Content_Score']:.2f}<br>
                                    • Collaborative: {row['Collaborative_Score']:.2f}<br>
                                    • Form Boost: +{row['Form_Boost']:.2f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_b:
                            st.markdown("<br><br><br>", unsafe_allow_html=True)
                            
                            like_key = f"like_{row['Drug_Clean']}_{idx}_{disease.replace(' ', '_')}"
                            dislike_key = f"dislike_{row['Drug_Clean']}_{idx}_{disease.replace(' ', '_')}"
                            
                            if st.button("👍", key=like_key, use_container_width=True):
                                st.session_state.feedback_history.append({
                                    'drug': row['Drug_Clean'],
                                    'feedback': 'like',
                                    'timestamp': datetime.now().isoformat(),
                                    'disease': disease,
                                    'score': float(row['Final_Score'])
                                })
                                st.success("✓ Feedback recorded!")
                                st.rerun()
                            
                            if st.button("👎", key=dislike_key, use_container_width=True):
                                st.session_state.feedback_history.append({
                                    'drug': row['Drug_Clean'],
                                    'feedback': 'dislike',
                                    'timestamp': datetime.now().isoformat(),
                                    'disease': disease,
                                    'score': float(row['Final_Score'])
                                })
                                st.success("✓ Feedback recorded!")
                                st.rerun()
                    
                    # Statistics
                    st.markdown("---")
                    st.markdown("#### 📊 Statistics")
                    
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    with col_s1:
                        st.metric("Avg Age", f"{recommendations['Age'].mean():.0f}")
                    with col_s2:
                        gender_match = (recommendations['Gender'] == gender).mean() * 100
                        st.metric("Gender Match", f"{gender_match:.0f}%")
                    with col_s3:
                        avg_score = recommendations['Final_Score'].mean() * 100
                        st.metric("Avg Score", f"{avg_score:.0f}%")
                    with col_s4:
                        st.metric("Feedback", len(st.session_state.feedback_history))
                    
                    # Visualizations
                    st.markdown("#### 📈 Score Analysis")
                    
                    fig_scores = go.Figure()
                    fig_scores.add_trace(go.Bar(
                        x=recommendations['Drug_Clean'][:8],
                        y=recommendations['NCF_Score'][:8],
                        name='NCF',
                        marker_color='#2196F3'
                    ))
                    fig_scores.add_trace(go.Bar(
                        x=recommendations['Drug_Clean'][:8],
                        y=recommendations['Context_Score'][:8],
                        name='Context',
                        marker_color='#4CAF50'
                    ))
                    fig_scores.update_layout(
                        barmode='stack',
                        plot_bgcolor='#1A1A1A',
                        paper_bgcolor='#1A1A1A',
                        font_color='white',
                        height=400,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig_scores, use_container_width=True)
                    
                    # Model weights
                    st.markdown("#### 🎚️ Model Weights")
                    fig_weights = go.Figure(data=[
                        go.Bar(
                            x=['NCF', 'Context'],
                            y=[ncf_weight, context_weight],
                            text=[f'{ncf_weight:.0%}', f'{context_weight:.0%}'],
                            textposition='auto',
                            marker_color=['#2196F3', '#4CAF50']
                        )
                    ])
                    fig_weights.update_layout(
                        plot_bgcolor='#1A1A1A',
                        paper_bgcolor='#1A1A1A',
                        font_color='white',
                        yaxis=dict(range=[0, 1]),
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_weights, use_container_width=True)
                
                else:
                    st.warning(f"No medicines found for {disease}")
    
    else:
        st.info("👈 Enter patient information and click 'Get Recommendations'")
        
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            st.metric("Total Records", f"{len(system['drug_data']):,}")
        with col_q2:
            st.metric("Unique Drugs", len(system['drug_data']['Drug_Clean'].unique()))
        with col_q3:
            st.metric("Diseases", len(system['drug_data']['Disease'].unique()))

# ============================================================================
# SYSTEM EXPLANATION
# ============================================================================

st.markdown("---")
st.markdown("<h3 class='sub-header'>🤖 How the System Works</h3>", unsafe_allow_html=True)

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #2196F3;'>🧠 Neural Collaborative Filtering</h4>
        <p style='font-size: 0.9rem;'>
        TensorFlow deep learning model that learns drug-disease relationships 
        through embeddings and neural networks.
        </p>
        <ul style='font-size: 0.85rem;'>
        <li>Drug embeddings (64-dim)</li>
        <li>Disease embeddings</li>
        <li>MLP architecture</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_exp2:
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #4CAF50;'>📚 Context-Based Filtering</h4>
        <p style='font-size: 0.9rem;'>
        TF-IDF text similarity combined with collaborative patterns 
        from similar demographic patients.
        </p>
        <ul style='font-size: 0.85rem;'>
        <li>Text similarity (TF-IDF)</li>
        <li>Demographic matching</li>
        <li>Form preferences</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_exp3:
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #FF6B35;'>🎯 Hybrid Combination</h4>
        <p style='font-size: 0.9rem;'>
        Intelligently combines both approaches with adjustable weights 
        for maximum recommendation accuracy.
        </p>
        <ul style='font-size: 0.85rem;'>
        <li>Weighted ensemble</li>
        <li>Adjustable balance</li>
        <li>Explainable scores</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FEEDBACK HISTORY
# ============================================================================

if st.session_state.feedback_history:
    st.markdown("---")
    st.markdown("<h3 class='sub-header'>📝 Feedback History</h3>", unsafe_allow_html=True)
    
    feedback_df = pd.DataFrame(st.session_state.feedback_history)
    
    col_fb1, col_fb2, col_fb3 = st.columns(3)
    with col_fb1:
        liked = len(feedback_df[feedback_df['feedback'] == 'like'])
        st.metric("👍 Liked", liked)
    with col_fb2:
        disliked = len(feedback_df[feedback_df['feedback'] == 'dislike'])
        st.metric("👎 Disliked", disliked)
    with col_fb3:
        st.metric("Total", len(feedback_df))
    
    if st.checkbox("Show detailed feedback"):
        st.dataframe(feedback_df[['drug', 'feedback', 'disease', 'score']])
    
    if st.button("Clear Feedback"):
        st.session_state.feedback_history = []
        st.rerun()

# ============================================================================
# MEDICAL DISCLAIMER
# ============================================================================

st.markdown("""
<div style='background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin-top: 30px;'>
    <h4 style='color: #FF6B35;'>⚠️ Medical Disclaimer</h4>
    <p style='font-size: 0.85rem;'>
    <strong>This is an AI-powered recommendation system for informational purposes only.</strong><br><br>
    
    ✓ Always consult with a qualified healthcare professional before starting any medication<br>
    ✓ The recommendations are based on patterns in the database and may not suit your specific case<br>
    ✓ Report any side effects or adverse reactions to your doctor immediately<br>
    ✓ Never self-medicate based solely on AI recommendations<br>
    ✓ Keep your doctor informed about all medications you're taking<br>
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# DEBUG SECTION
# ============================================================================

if st.checkbox("Show Debug Information"):
    st.write("### System Information")
    st.write(f"Dataset: `{dataset_path}`")
    st.write(f"Records: {len(system['drug_data'])}")
    st.write(f"Unique Drugs: {len(system['drug_data']['Drug_Clean'].unique())}")
    st.write(f"Diseases: {len(system['drug_data']['Disease'].unique())}")
    st.write(f"Feedback Count: {len(st.session_state.feedback_history)}")
    st.write(f"NCF Model Parameters: {system['ncf_model'].count_params():,}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888; font-size: 0.9rem;'>🎉 Complete Hybrid NCF + Context Recommendation System | Version 1.0</p>", unsafe_allow_html=True)
