import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Admin Panel",
    page_icon="⚙️",
    layout="wide"
)

from theme import apply_theme
apply_theme()

# Password protection (for demo purposes only)
def check_password():
    """Returns `True` if the user entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Enter Admin Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.warning("Please enter the admin password to continue.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Enter Admin Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    st.markdown("<h1 class='main-header'>⚙️ Admin Control Panel</h1>", unsafe_allow_html=True)
    
    # Admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "👥 User Management", 
        "💊 Drug Database", 
        "🤖 Model Management", 
        "⚙️ System Settings"
    ])
    
    with tab1:
        st.markdown("<h3 class='sub-header'>Admin Dashboard</h3>", unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", "1,247", "12%")
        
        with col2:
            st.metric("Active Today", "342", "5%")
        
        with col3:
            st.metric("Total Predictions", "8,942", "23%")
        
        with col4:
            st.metric("System Uptime", "99.8%", "0.1%")
        
        # System health
        st.markdown("<h4>System Health Monitor</h4>", unsafe_allow_html=True)
        
        health_data = {
            'Component': ['API Server', 'Database', 'ML Models', 'Cache', 'Storage'],
            'Status': ['Healthy', 'Healthy', 'Degraded', 'Healthy', 'Healthy'],
            'Load': [75, 60, 90, 45, 30],
            'Latency': [120, 45, 300, 15, 80]
        }
        
        health_df = pd.DataFrame(health_data)
        
        fig = go.Figure(data=[
            go.Bar(
                name='Load %',
                x=health_df['Component'],
                y=health_df['Load'],
                marker_color='#FF6B35'
            ),
            go.Bar(
                name='Latency (ms)',
                x=health_df['Component'],
                y=health_df['Latency'],
                marker_color='#FF8B35'
            )
        ])
        
        fig.update_layout(
            barmode='group',
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#1A1A1A',
            font_color='white',
            title="System Component Status"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.markdown("<h4>Recent System Activity</h4>", unsafe_allow_html=True)
        
        activity_data = pd.DataFrame({
            'Time': [datetime.now() - timedelta(minutes=x) for x in range(30, 0, -5)],
            'Event': [
                'User login - ID: 12345',
                'Disease prediction - Acne',
                'Medicine recommendation - 5 items',
                'Data export requested',
                'Model retraining started',
                'New user registered'
            ],
            'Severity': ['Info', 'Info', 'Info', 'Warning', 'Info', 'Info']
        })
        
        st.dataframe(
            activity_data,
            column_config={
                "Time": st.column_config.DatetimeColumn("Timestamp"),
                "Event": "Event Description",
                "Severity": st.column_config.SelectboxColumn(
                    "Severity",
                    options=["Info", "Warning", "Error", "Critical"]
                )
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab2:
        st.markdown("<h3 class='sub-header'>User Management</h3>", unsafe_allow_html=True)
        
        # Simulated user data
        user_data = pd.DataFrame({
            'User ID': range(1001, 1011),
            'Username': [f'user{i}' for i in range(1001, 1011)],
            'Email': [f'user{i}@example.com' for i in range(1001, 1011)],
            'Age': np.random.randint(18, 70, 10),
            'Gender': np.random.choice(['Male', 'Female'], 10),
            'Join Date': pd.date_range('2024-01-01', periods=10),
            'Last Active': pd.date_range('2024-03-20', periods=10),
            'Status': ['Active']*8 + ['Inactive']*2
        })
        
        # Search and filter
        col_search, col_filter = st.columns(2)
        
        with col_search:
            search_term = st.text_input("Search Users", placeholder="Username or Email")
        
        with col_filter:
            status_filter = st.multiselect(
                "Filter by Status",
                ['Active', 'Inactive', 'Suspended'],
                default=['Active']
            )
        
        # Display users
        filtered_users = user_data.copy()
        if search_term:
            filtered_users = filtered_users[
                filtered_users['Username'].str.contains(search_term, case=False) |
                filtered_users['Email'].str.contains(search_term, case=False)
            ]
        
        if status_filter:
            filtered_users = filtered_users[filtered_users['Status'].isin(status_filter)]
        
        st.dataframe(
            filtered_users,
            column_config={
                "User ID": st.column_config.NumberColumn("ID"),
                "Join Date": st.column_config.DateColumn("Joined"),
                "Last Active": st.column_config.DateColumn("Last Active"),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Active", "Inactive", "Suspended"]
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # User actions
        st.markdown("<h4>User Actions</h4>", unsafe_allow_html=True)
        
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            selected_user = st.selectbox("Select User", filtered_users['Username'].tolist())
        
        with col_act2:
            action = st.selectbox(
                "Select Action",
                ["View Details", "Send Message", "Reset Password", "Change Status", "Delete User"]
            )
        
        with col_act3:
            if st.button("Execute Action", use_container_width=True):
                if action == "Delete User":
                    st.error("⚠️ This action cannot be undone!")
                    confirm = st.checkbox("I confirm I want to delete this user")
                    if confirm:
                        st.success(f"User {selected_user} deleted successfully.")
                else:
                    st.success(f"Action '{action}' executed for user {selected_user}.")
    
    with tab3:
        st.markdown("<h3 class='sub-header'>Drug Database Management</h3>", unsafe_allow_html=True)
        
        if not st.session_state.drug_data.empty:
            # Show current drug data
            st.dataframe(
                st.session_state.drug_data.head(50),
                use_container_width=True,
                hide_index=True
            )
            
            # Drug management
            st.markdown("<h4>Add/Edit Drug Information</h4>", unsafe_allow_html=True)
            
            with st.form("drug_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    drug_name = st.text_input("Drug Name", placeholder="e.g., Acnetoin 20mg Capsule")
                    disease = st.selectbox("Disease", st.session_state.drug_data['Disease'].unique())
                
                with col2:
                    gender = st.selectbox("Gender", ["Male", "Female", "Both"])
                    age = st.number_input("Age", min_value=0, max_value=120, value=25)
                
                description = st.text_area("Description", placeholder="Drug description and usage instructions")
                
                submitted = st.form_submit_button("Add/Update Drug")
                
                if submitted:
                    st.success("Drug information saved successfully!")
            
            # Bulk operations
            st.markdown("<h4>Bulk Operations</h4>", unsafe_allow_html=True)
            
            col_bulk1, col_bulk2 = st.columns(2)
            
            with col_bulk1:
                uploaded_file = st.file_uploader("Upload CSV with new drugs", type=['csv'])
                if uploaded_file is not None:
                    new_data = pd.read_csv(uploaded_file)
                    st.write("Preview of uploaded data:")
                    st.dataframe(new_data.head())
                    
                    if st.button("Import Data", use_container_width=True):
                        # In real app, you would merge with existing data
                        st.success(f"Imported {len(new_data)} new records")
            
            with col_bulk2:
                export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON"])
                if st.button("Export Database", use_container_width=True):
                    st.success(f"Database exported as {export_format}")
    
    with tab4:
        st.markdown("<h3 class='sub-header'>Machine Learning Model Management</h3>", unsafe_allow_html=True)
        
        # Model status
        col_mod1, col_mod2 = st.columns(2)
        
        with col_mod1:
            st.metric("Disease Model Accuracy", "92.4%", "1.2%")
            st.progress(0.924, text="Training Progress")
        
        with col_mod2:
            st.metric("Recommendation Model Accuracy", "88.7%", "0.8%")
            st.progress(0.887, text="Training Progress")
        
        # Model controls
        st.markdown("<h4>Model Controls</h4>", unsafe_allow_html=True)
        
        col_ctl1, col_ctl2, col_ctl3 = st.columns(3)
        
        with col_ctl1:
            if st.button("🔄 Retrain Disease Model", use_container_width=True):
                with st.spinner("Retraining disease prediction model..."):
                    st.success("Disease model retrained successfully!")
        
        with col_ctl2:
            if st.button("🔄 Retrain Recommendation Model", use_container_width=True):
                with st.spinner("Retraining recommendation model..."):
                    st.success("Recommendation model retrained successfully!")
        
        with col_ctl3:
            if st.button("📊 Evaluate All Models", use_container_width=True):
                with st.spinner("Evaluating model performance..."):
                    # Simulated evaluation results
                    eval_results = pd.DataFrame({
                        'Model': ['Disease Prediction', 'Medicine Recommendation', 'Hybrid Filtering'],
                        'Accuracy': [0.924, 0.887, 0.905],
                        'Precision': [0.912, 0.876, 0.892],
                        'Recall': [0.928, 0.891, 0.910],
                        'F1-Score': [0.920, 0.883, 0.901]
                    })
                    
                    st.dataframe(eval_results, hide_index=True)
        
         # Model parameters
        st.markdown("<h4>Model Parameters</h4>", unsafe_allow_html=True)
        
        with st.expander("Disease Model Parameters"):
            col_param1, col_param2 = st.columns(2)
            
            with col_param1:
                n_estimators = st.slider("Number of Estimators", 10, 200, 100)
                max_depth = st.slider("Max Depth", 5, 50, 20)
            
            with col_param2:
                learning_rate = st.slider("Learning Rate", 0.01, 1.0, 0.1)
                min_samples_split = st.slider("Min Samples Split", 2, 20, 5)
            
            if st.button("Update Disease Model Parameters"):
                st.success("Parameters updated!")
        
        with st.expander("Recommendation Model Parameters"):
            col_param3, col_param4 = st.columns(2)
            
            with col_param3:
                factors = st.slider("Latent Factors", 10, 200, 50)
                epochs = st.slider("Training Epochs", 5, 100, 20)
            
            with col_param4:
                reg = st.slider("Regularization", 0.001, 0.1, 0.02)
                lr = st.slider("Learning Rate", 0.001, 0.1, 0.005)
            
            if st.button("Update Recommendation Model Parameters"):
                st.success("Parameters updated!")
    
    with tab5:
        st.markdown("<h3 class='sub-header'>System Settings</h3>", unsafe_allow_html=True)
        
        # General settings
        with st.form("system_settings"):
            st.markdown("### General Settings")
            
            col_set1, col_set2 = st.columns(2)
            
            with col_set1:
                site_name = st.text_input("Site Name", "Health AI Recommender")
                maintenance_mode = st.checkbox("Maintenance Mode")
                allow_registration = st.checkbox("Allow New Registrations", value=True)
            
            with col_set2:
                max_file_size = st.number_input("Max Upload Size (MB)", 1, 100, 10)
                session_timeout = st.number_input("Session Timeout (minutes)", 5, 240, 30)
                log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
            
            st.markdown("### Notification Settings")
            
            email_notifications = st.checkbox("Enable Email Notifications", value=True)
            sms_notifications = st.checkbox("Enable SMS Notifications", value=False)
            
            if st.form_submit_button("Save Settings"):
                st.success("System settings saved successfully!")
        
        # System maintenance
        st.markdown("### System Maintenance")
        
        col_maint1, col_maint2 = st.columns(2)
        
        with col_maint1:
            if st.button("🔄 Clear Cache", use_container_width=True):
                st.success("Cache cleared successfully!")
            
            if st.button("🗑️ Clear Old Logs", use_container_width=True):
                st.success("Old logs cleared successfully!")
        
        with col_maint2:
            if st.button("🔄 Restart Services", use_container_width=True, type="secondary"):
                st.warning("This will restart all system services.")
                confirm = st.checkbox("Confirm service restart")
                if confirm:
                    st.success("Services restarted successfully!")
            
            if st.button("🔒 Backup Database", use_container_width=True, type="secondary"):
                with st.spinner("Creating backup..."):
                    st.success("Database backup created successfully!")
        
        # Danger zone
        st.markdown("### ⚠️ Danger Zone")
        
        with st.expander("Dangerous Operations", icon="⚠️"):
            st.warning("These operations are irreversible!")
            
            col_danger1, col_danger2 = st.columns(2)
            
            with col_danger1:
                if st.button("🗑️ Delete All User Data", type="secondary"):
                    st.error("This will delete ALL user data!")
                    confirm1 = st.checkbox("I understand this cannot be undone")
                    confirm2 = st.text_input("Type 'DELETE ALL' to confirm")
                    if confirm1 and confirm2 == "DELETE ALL":
                        st.success("User data deleted (simulated)")
            
            with col_danger2:
                if st.button("🔄 Reset System to Defaults", type="secondary"):
                    st.error("This will reset ALL system settings!")
                    confirm1 = st.checkbox("I understand this cannot be undone")
                    confirm2 = st.text_input("Type 'RESET ALL' to confirm")
                    if confirm1 and confirm2 == "RESET ALL":
                        st.success("System reset to defaults (simulated)")

# Instructions for running the application
st.markdown("""
## Instructions for Running the Application

1. Ensure all dependencies are installed: `pip install streamlit pandas numpy plotly`
2. Run the application: `streamlit run app.py`
3. Use the admin password to access this panel
4. Monitor system health and manage users, drugs, and models from the respective tabs
""")