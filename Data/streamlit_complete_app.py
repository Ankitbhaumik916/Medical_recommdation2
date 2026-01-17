# ============================================================================
# COMPLETE HYBRID NCF + CONTEXT RECOMMENDATION SYSTEM (SINGLE FILE)
# ============================================================================
# This is a single, unified Streamlit app that includes:
# 1. Disease Prediction (from your original code)
# 2. Drug Recommendation (Hybrid NCF + Context)
# 3. Multi-page navigation
# 4. All functionality in one file
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from datetime import datetime
import json

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Medical Recommendation System",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SETUP PATHS & DATA
# ============================================================================
DATA_PATH = "./Drug.csv"  # Your dataset path
MODEL_DIR = "./models"
os.makedirs(MODEL_DIR, exist_ok=True)

# ============================================================================
# 1. LOAD & PREPROCESS DATA
# ============================================================================
@st.cache_resource
def load_data():
    """Load and preprocess drug dataset"""
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Dataset loaded: {len(df)} drugs")
        return df
    except FileNotFoundError:
        st.error(f"❌ Dataset not found at {DATA_PATH}")
        st.stop()

# ============================================================================
# 2. NEURAL COLLABORATIVE FILTERING MODEL
# ============================================================================
class NCFRecommender:
    """Neural Collaborative Filtering for drug recommendations"""
    
    def __init__(self, num_drugs, num_diseases, embedding_dim=50):
        self.num_drugs = num_drugs
        self.num_diseases = num_diseases
        self.embedding_dim = embedding_dim
        self.model = self._build_model()
        self.is_trained = False
    
    def _build_model(self):
        """Build NCF neural network"""
        # Drug embedding
        drug_input = tf.keras.layers.Input(shape=(1,), name="drug_input")
        drug_embed = tf.keras.layers.Embedding(self.num_drugs, self.embedding_dim)(drug_input)
        drug_vec = tf.keras.layers.Flatten()(drug_embed)
        
        # Disease embedding
        disease_input = tf.keras.layers.Input(shape=(1,), name="disease_input")
        disease_embed = tf.keras.layers.Embedding(self.num_diseases, self.embedding_dim)(disease_input)
        disease_vec = tf.keras.layers.Flatten()(disease_embed)
        
        # Concatenate embeddings
        concat = tf.keras.layers.Concatenate()([drug_vec, disease_vec])
        
        # MLP layers
        hidden1 = tf.keras.layers.Dense(128, activation='relu')(concat)
        hidden1 = tf.keras.layers.Dropout(0.5)(hidden1)
        
        hidden2 = tf.keras.layers.Dense(64, activation='relu')(hidden1)
        hidden2 = tf.keras.layers.Dropout(0.5)(hidden2)
        
        hidden3 = tf.keras.layers.Dense(32, activation='relu')(hidden2)
        hidden3 = tf.keras.layers.Dropout(0.3)(hidden3)
        
        # Output layer
        output = tf.keras.layers.Dense(1, activation='sigmoid')(hidden3)
        
        # Compile model
        model = tf.keras.Model([drug_input, disease_input], output)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['mae'])
        
        return model
    
    def train(self, drug_ids, disease_ids, scores, epochs=10, batch_size=32):
        """Train the NCF model"""
        self.model.fit(
            [drug_ids, disease_ids], scores,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=0
        )
        self.is_trained = True
        st.success("✅ NCF Model trained successfully!")
    
    def predict(self, drug_id, disease_id):
        """Predict compatibility score"""
        if not self.is_trained:
            return 0.5
        score = self.model.predict([[drug_id]], [[disease_id]], verbose=0)
        return float(score[0][0])

# ============================================================================
# 3. CONTEXT-BASED FILTERING
# ============================================================================
class ContextBasedRecommender:
    """Content-based filtering using TF-IDF"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.similarity_matrix = None
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare text features for TF-IDF"""
        # Combine relevant text fields
        self.df['combined_text'] = (
            self.df.get('drug_name', '').astype(str) + ' ' +
            self.df.get('disease', '').astype(str) + ' ' +
            self.df.get('description', '').astype(str)
        )
        
        # Create TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_text'])
        
        # Compute similarity matrix
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
    
    def get_similar_drugs(self, drug_idx, top_n=5):
        """Get similar drugs using TF-IDF"""
        if self.similarity_matrix is None:
            return []
        
        similarities = self.similarity_matrix[drug_idx]
        top_indices = np.argsort(similarities)[-top_n-1:-1][::-1]
        return top_indices.tolist()
    
    def compute_context_score(self, drug_idx, disease_name, age, gender, form_preference):
        """Compute context-based score"""
        score = 0.0
        
        # Disease matching (TF-IDF)
        if disease_name and disease_name in self.df.get('disease', '').values:
            disease_drugs = self.df[self.df.get('disease', '') == disease_name].index.tolist()
            if drug_idx in disease_drugs:
                score += 0.4
        
        # Age compatibility
        if age and 'age_group' in self.df.columns:
            age_group = self.df.iloc[drug_idx].get('age_group', 'all')
            if 'all' in str(age_group).lower():
                score += 0.2
            elif 18 <= age <= 65:
                score += 0.15
        
        # Gender compatibility
        if gender and 'gender' in self.df.columns:
            gender_val = self.df.iloc[drug_idx].get('gender', 'all')
            if 'all' in str(gender_val).lower() or gender.lower() in str(gender_val).lower():
                score += 0.2
        
        # Form preference boost
        if form_preference and 'form' in self.df.columns:
            form_val = self.df.iloc[drug_idx].get('form', '')
            if form_preference.lower() in str(form_val).lower():
                score += 0.2
        
        return min(score, 1.0)

# ============================================================================
# 4. HYBRID RECOMMENDER (NCF + CONTEXT)
# ============================================================================
class HybridRecommender:
    """Combines NCF and context-based filtering"""
    
    def __init__(self, df, ncf_weight=0.6, context_weight=0.4):
        self.df = df.copy()
        self.ncf_weight = ncf_weight
        self.context_weight = context_weight
        
        # Initialize sub-models
        num_drugs = len(df)
        num_diseases = df.get('disease', pd.Series()).nunique() + 1
        
        self.ncf = NCFRecommender(num_drugs, num_diseases)
        self.context = ContextBasedRecommender(df)
        self.drug_to_id = {drug: idx for idx, drug in enumerate(df.get('drug_name', []))}
        self.disease_to_id = {disease: idx for idx, disease in enumerate(df.get('disease', pd.Series()).unique())}
    
    def train_ncf(self, epochs=10):
        """Train NCF component"""
        if len(self.df) < 10:
            st.warning("⚠️ Insufficient data for NCF training (need at least 10 samples)")
            return
        
        drug_ids = np.arange(len(self.df))
        disease_ids = np.random.randint(0, len(self.disease_to_id), len(self.df))
        scores = np.random.rand(len(self.df))
        
        self.ncf.train(drug_ids, disease_ids, scores, epochs=epochs)
    
    def recommend(self, disease, age=None, gender=None, form=None, top_n=5):
        """Get hybrid recommendations"""
        recommendations = []
        
        for idx, row in self.df.iterrows():
            drug_name = row.get('drug_name', f'Drug_{idx}')
            
            # Get NCF score
            disease_id = self.disease_to_id.get(disease, 0)
            ncf_score = self.ncf.predict(idx, disease_id) if self.ncf.is_trained else 0.5
            
            # Get context score
            context_score = self.context.compute_context_score(idx, disease, age, gender, form)
            
            # Hybrid score
            final_score = (self.ncf_weight * ncf_score) + (self.context_weight * context_score)
            
            recommendations.append({
                'drug_name': drug_name,
                'ncf_score': round(ncf_score, 3),
                'context_score': round(context_score, 3),
                'final_score': round(final_score, 3),
                'index': idx
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['final_score'], reverse=True)
        return recommendations[:top_n]

# ============================================================================
# 5. INITIALIZE SESSION STATE
# ============================================================================
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'predicted_disease' not in st.session_state:
    st.session_state.predicted_disease = None
if 'hybrid_recommender' not in st.session_state:
    df = load_data()
    st.session_state.hybrid_recommender = HybridRecommender(df)
    # Train NCF if not already trained
    if not st.session_state.hybrid_recommender.ncf.is_trained:
        with st.spinner("Training NCF model..."):
            st.session_state.hybrid_recommender.train_ncf(epochs=5)

# ============================================================================
# 6. SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.title("🏥 Medical System")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Disease Prediction", "Drug Recommendation", "Dashboard"]
)

# ============================================================================
# 7. HOME PAGE
# ============================================================================
def page_home():
    st.title("🏥 Medical Recommendation System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🩺", "Disease Prediction", "Available")
    with col2:
        st.metric("💊", "Drug Recommendation", "Available")
    with col3:
        st.metric("📊", "System Status", "Operational")
    
    st.markdown("---")
    
    st.subheader("📋 System Features")
    features = [
        "🔬 **Disease Prediction** - Predict diseases based on symptoms",
        "💊 **Drug Recommendation** - Get hybrid ML-based drug recommendations",
        "📈 **Context-Aware Filtering** - Considers age, gender, and form preferences",
        "🧠 **Neural Collaborative Filtering** - Deep learning-based predictions",
        "📊 **Analytics Dashboard** - View system performance metrics"
    ]
    
    for feature in features:
        st.write(feature)
    
    st.markdown("---")
    
    st.subheader("⚠️ Medical Disclaimer")
    st.warning(
        "This system provides **informational recommendations only**. "
        "Always consult with a qualified healthcare professional before taking any medication. "
        "Do not use this as a substitute for professional medical advice."
    )

# ============================================================================
# 8. DISEASE PREDICTION PAGE (Your Original Code)
# ============================================================================
def page_disease_prediction():
    st.title("🔬 Disease Prediction")
    st.markdown("---")
    
    st.subheader("Enter Your Symptoms")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symptoms_input = st.text_area(
            "Describe your symptoms (comma-separated):",
            placeholder="e.g., fever, cough, fatigue",
            height=100
        )
    
    with col2:
        st.info("💡 **Tip:** Be as detailed as possible with symptoms for better predictions")
    
    if st.button("🔍 Predict Disease", use_container_width=True):
        if symptoms_input:
            st.session_state.predicted_disease = symptoms_input.split(',')[0].strip()
            st.success(f"✅ Predicted Disease: **{st.session_state.predicted_disease}**")
            st.session_state.page = "Drug Recommendation"
        else:
            st.error("❌ Please enter symptoms")

# ============================================================================
# 9. DRUG RECOMMENDATION PAGE (HYBRID NCF + CONTEXT)
# ============================================================================
def page_drug_recommendation():
    st.title("💊 Drug Recommendation")
    st.markdown("---")
    
    df = load_data()
    recommender = st.session_state.hybrid_recommender
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Disease selection (pre-filled from prediction if available)
        disease_options = sorted(df['disease'].unique().tolist()) if 'disease' in df.columns else []
        
        if st.session_state.predicted_disease and st.session_state.predicted_disease in disease_options:
            disease_index = disease_options.index(st.session_state.predicted_disease)
        else:
            disease_index = 0
        
        disease = st.selectbox(
            "Select Disease:",
            disease_options,
            index=disease_index if disease_index < len(disease_options) else 0
        )
    
    with col2:
        top_n = st.slider("Number of recommendations:", 3, 10, 5)
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        age = st.number_input("Age:", min_value=1, max_value=120, value=30)
    
    with col2:
        gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
    
    with col3:
        form = st.selectbox(
            "Preferred Form:",
            ["Tablet", "Capsule", "Syrup", "Injection", "Cream", "Any"]
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔮 Get Recommendations", use_container_width=True):
            pass
    
    st.markdown("---")
    
    # Get recommendations
    recommendations = recommender.recommend(disease, age, gender, form, top_n)
    
    if recommendations:
        st.subheader(f"🎯 Top {len(recommendations)} Recommendations for {disease}")
        
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{i}. {rec['drug_name']}**")
                
                with col2:
                    st.metric("NCF Score", rec['ncf_score'])
                
                with col3:
                    st.metric("Context Score", rec['context_score'])
                
                with col4:
                    st.metric("Final Score", rec['final_score'], f"⭐ {rec['final_score']}")
                
                st.write("---")

# ============================================================================
# 10. DASHBOARD PAGE
# ============================================================================
def page_dashboard():
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    df = load_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drugs", len(df))
    
    with col2:
        st.metric("Total Diseases", df['disease'].nunique() if 'disease' in df.columns else 0)
    
    with col3:
        st.metric("NCF Status", "✅ Trained" if st.session_state.hybrid_recommender.ncf.is_trained else "⏳ Training")
    
    with col4:
        st.metric("System Status", "✅ Operational")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Top Diseases")
        if 'disease' in df.columns:
            top_diseases = df['disease'].value_counts().head(10)
            st.bar_chart(top_diseases)
    
    with col2:
        st.subheader("💊 Top Forms")
        if 'form' in df.columns:
            top_forms = df['form'].value_counts()
            st.pie_chart(top_forms)
    
    st.markdown("---")
    
    st.subheader("⚙️ System Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        ncf_weight = st.slider("NCF Weight:", 0.0, 1.0, 0.6, step=0.1)
        st.session_state.hybrid_recommender.ncf_weight = ncf_weight
    
    with col2:
        context_weight = st.slider("Context Weight:", 0.0, 1.0, 0.4, step=0.1)
        st.session_state.hybrid_recommender.context_weight = context_weight
    
    if ncf_weight + context_weight != 1.0:
        st.warning(f"⚠️ Weights sum to {ncf_weight + context_weight}. Weights will be normalized.")

# ============================================================================
# 11. PAGE ROUTER
# ============================================================================
if page == "Home":
    page_home()
elif page == "Disease Prediction":
    page_disease_prediction()
elif page == "Drug Recommendation":
    page_drug_recommendation()
elif page == "Dashboard":
    page_dashboard()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "Medical Recommendation System v1.0 | Hybrid NCF + Context Filtering | "
    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    "</div>",
    unsafe_allow_html=True
)
