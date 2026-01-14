import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
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

st.markdown("<h1 class='main-header'>📊 Healthcare Analytics Dashboard</h1>", unsafe_allow_html=True)

# Check if data exists
if st.session_state.drug_data.empty:
    st.error("No data available for analytics.")
    st.stop()

df = st.session_state.drug_data.copy()

# Create tabs for different analytics views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎯 Disease Analysis", "💊 Drug Insights", "👥 User Patterns"])

with tab1:
    st.markdown("<h3 class='sub-header'>System Overview Analytics</h3>", unsafe_allow_html=True)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_drugs = len(df)
        st.metric("Total Drugs", f"{total_drugs:,}")
    
    with col2:
        unique_diseases = df['Disease'].nunique()
        st.metric("Diseases Covered", unique_diseases)
    
    with col3:
        avg_age = df['Age'].mean()
        st.metric("Average Patient Age", f"{avg_age:.1f}")
    
    with col4:
        gender_dist = df['Gender'].value_counts(normalize=True)
        male_percent = gender_dist.get('Male', 0) * 100
        st.metric("Male Patients", f"{male_percent:.1f}%")
    
    # Disease distribution
    st.markdown("<h4>Disease Distribution</h4>", unsafe_allow_html=True)
    
    disease_counts = df['Disease'].value_counts().reset_index()
    disease_counts.columns = ['Disease', 'Count']
    
    fig1 = px.bar(
        disease_counts,
        x='Disease',
        y='Count',
        color='Disease',
        color_discrete_sequence=['#FF6B35', '#FF8B35', '#FFA935'],
        title="Number of Drugs per Disease"
    )
    
    fig1.update_layout(
        plot_bgcolor='#1A1A1A',
        paper_bgcolor='#1A1A1A',
        font_color='white',
        showlegend=False
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Age distribution by disease
    st.markdown("<h4>Age Distribution by Disease</h4>", unsafe_allow_html=True)
    
    fig2 = px.box(
        df,
        x='Disease',
        y='Age',
        color='Disease',
        color_discrete_sequence=['#FF6B35', '#FF8B35', '#FFA935'],
        title="Age Distribution Across Diseases"
    )
    
    fig2.update_layout(
        plot_bgcolor='#1A1A1A',
        paper_bgcolor='#1A1A1A',
        font_color='white',
        showlegend=False
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("<h3 class='sub-header'>Disease-Specific Analysis</h3>", unsafe_allow_html=True)
    
    # Disease selector
    selected_disease = st.selectbox(
        "Select Disease for Detailed Analysis",
        sorted(df['Disease'].unique())
    )
    
    disease_df = df[df['Disease'] == selected_disease]
    
    if not disease_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender distribution for selected disease
            gender_counts = disease_df['Gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            
            fig3 = px.pie(
                gender_counts,
                values='Count',
                names='Gender',
                title=f"Gender Distribution for {selected_disease}",
                color_discrete_sequence=['#FF6B35', '#FF8B35']
            )
            
            fig3.update_layout(
                plot_bgcolor='#1A1A1A',
                paper_bgcolor='#1A1A1A',
                font_color='white'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Age distribution histogram
            fig4 = px.histogram(
                disease_df,
                x='Age',
                nbins=20,
                title=f"Age Distribution for {selected_disease}",
                color_discrete_sequence=['#FF6B35']
            )
            
            fig4.update_layout(
                plot_bgcolor='#1A1A1A',
                paper_bgcolor='#1A1A1A',
                font_color='white',
                xaxis_title="Age",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig4, use_container_width=True)
        
        # Top drug forms for this disease
        st.markdown("<h4>Common Drug Forms</h4>", unsafe_allow_html=True)
        
        # Extract drug forms (simplified)
        def extract_drug_form(drug_name):
            drug_lower = str(drug_name).lower()
            forms = ['tablet', 'capsule', 'gel', 'cream', 'lotion', 'injection', 'syrup', 'solution']
            for form in forms:
                if form in drug_lower:
                    return form.title()
            return 'Other'
        
        disease_df['Drug_Form'] = disease_df['Drug'].apply(extract_drug_form)
        form_counts = disease_df['Drug_Form'].value_counts().reset_index()
        form_counts.columns = ['Form', 'Count']
        
        fig5 = px.bar(
            form_counts,
            x='Form',
            y='Count',
            title=f"Drug Forms for {selected_disease}",
            color='Form',
            color_discrete_sequence=px.colors.sequential.Oranges
        )
        
        fig5.update_layout(
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#1A1A1A',
            font_color='white',
            showlegend=False
        )
        
        st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.markdown("<h3 class='sub-header'>Drug Formulation Insights</h3>", unsafe_allow_html=True)
    
    # Extract active ingredients (simplified)
    def extract_ingredient(drug_name):
        common_ingredients = [
            'retino', 'benzoyl', 'clindamycin', 'isotretinoin',
            'cetirizine', 'loratadine', 'fexofenadine',
            'metformin', 'glimepiride', 'glipizide', 'insulin'
        ]
        
        drug_lower = str(drug_name).lower()
        for ingredient in common_ingredients:
            if ingredient in drug_lower:
                return ingredient.title()
        return 'Other'
    
    df['Ingredient'] = df['Drug'].apply(extract_ingredient)
    
    # Ingredient distribution
    ingredient_counts = df['Ingredient'].value_counts().reset_index()
    ingredient_counts.columns = ['Ingredient', 'Count']
    
    fig6 = px.treemap(
        ingredient_counts,
        path=['Ingredient'],
        values='Count',
        title="Active Ingredients Distribution",
        color='Count',
        color_continuous_scale='Oranges'
    )
    
    fig6.update_layout(
        plot_bgcolor='#1A1A1A',
        paper_bgcolor='#1A1A1A',
        font_color='white'
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    
    # Age vs Drug Type heatmap
    st.markdown("<h4>Age vs Drug Type Correlation</h4>", unsafe_allow_html=True)
    
    # Create age groups
    df['Age_Group'] = pd.cut(
        df['Age'],
        bins=[0, 18, 30, 45, 60, 100],
        labels=['0-18', '19-30', '31-45', '46-60', '60+']
    )
    
    heatmap_data = pd.crosstab(df['Age_Group'], df['Ingredient'])
    
    fig7 = px.imshow(
        heatmap_data,
        title="Age Group vs Active Ingredients",
        color_continuous_scale='Oranges',
        aspect='auto'
    )
    
    fig7.update_layout(
        plot_bgcolor='#1A1A1A',
        paper_bgcolor='#1A1A1A',
        font_color='white',
        xaxis_title="Active Ingredient",
        yaxis_title="Age Group"
    )
    
    st.plotly_chart(fig7, use_container_width=True)

with tab4:
    st.markdown("<h3 class='sub-header'>User Behavior Patterns</h3>", unsafe_allow_html=True)
    
    # Create simulated user interaction data
    np.random.seed(42)
    n_users = 1000
    
    user_data = pd.DataFrame({
        'user_id': range(1, n_users + 1),
        'age': np.random.randint(15, 80, n_users),
        'gender': np.random.choice(['Male', 'Female'], n_users, p=[0.55, 0.45]),
        'disease_searched': np.random.choice(df['Disease'].unique(), n_users),
        'clicks': np.random.poisson(5, n_users),
        'time_spent_min': np.random.exponential(10, n_users),
        'conversion': np.random.binomial(1, 0.3, n_users)
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User engagement by age
        fig8 = px.scatter(
            user_data,
            x='age',
            y='time_spent_min',
            color='gender',
            size='clicks',
            title="User Engagement by Age and Gender",
            color_discrete_map={'Male': '#FF6B35', 'Female': '#FF8B35'}
        )
        
        fig8.update_layout(
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#1A1A1A',
            font_color='white'
        )
        
        st.plotly_chart(fig8, use_container_width=True)
    
    with col2:
        # Conversion rate by disease
        conversion_rates = user_data.groupby('disease_searched')['conversion'].mean().reset_index()
        
        fig9 = px.bar(
            conversion_rates,
            x='disease_searched',
            y='conversion',
            title="Conversion Rate by Disease",
            color='conversion',
            color_continuous_scale='Oranges'
        )
        
        fig9.update_layout(
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#1A1A1A',
            font_color='white',
            xaxis_title="Disease",
            yaxis_title="Conversion Rate"
        )
        
        st.plotly_chart(fig9, use_container_width=True)
    
    # Time series simulation
    st.markdown("<h4>Daily User Activity</h4>", unsafe_allow_html=True)
    
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    daily_data = pd.DataFrame({
        'date': dates,
        'active_users': np.random.randint(50, 200, 30),
        'searches': np.random.randint(100, 500, 30),
        'recommendations': np.random.randint(80, 400, 30)
    })
    
    fig10 = go.Figure()
    
    fig10.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['active_users'],
        name='Active Users',
        line=dict(color='#FF6B35', width=3)
    ))
    
    fig10.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['searches'],
        name='Searches',
        line=dict(color='#FF8B35', width=3)
    ))
    
    fig10.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['recommendations'],
        name='Recommendations',
        line=dict(color='#FFA935', width=3)
    ))
    
    fig10.update_layout(
        title="Daily System Activity",
        plot_bgcolor='#1A1A1A',
        paper_bgcolor='#1A1A1A',
        font_color='white',
        xaxis_title="Date",
        yaxis_title="Count",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig10, use_container_width=True)

# Download data option
st.markdown("---")
st.markdown("<h3 class='sub-header'>📥 Data Export</h3>", unsafe_allow_html=True)

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if st.button("📊 Export Analytics Report", use_container_width=True):
        # Create a simple report
        report = f"""
        Healthcare Analytics Report
        Generated on: {pd.Timestamp.now()}
        
        Summary Statistics:
        - Total Drugs: {len(df):,}
        - Diseases Covered: {df['Disease'].nunique()}
        - Average Age: {df['Age'].mean():.1f}
        - Gender Distribution: {df['Gender'].value_counts().to_dict()}
        
        Disease Breakdown:
        """
        
        for disease, count in df['Disease'].value_counts().items():
            report += f"- {disease}: {count} drugs\n"
        
        st.download_button(
            label="⬇️ Download Report",
            data=report,
            file_name="healthcare_analytics_report.txt",
            mime="text/plain",
            use_container_width=True
        )

with col_exp2:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📁 Download Raw Data (CSV)",
        data=csv,
        file_name="healthcare_data.csv",
        mime="text/csv",
        use_container_width=True
    )