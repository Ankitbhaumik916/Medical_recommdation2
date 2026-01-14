import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from auth import auth_system, check_authentication

# Page configuration
st.set_page_config(
    page_title="User Profile",
    page_icon="👤",
    layout="wide"
)

# Check authentication
if not check_authentication():
    st.switch_page("pages/0_🔐_Login.py")

# Custom CSS for profile page
st.markdown("""
<style>
    .profile-header {
        background: linear-gradient(135deg, #FF6B35, #FF8B35);
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 30px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .profile-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 1%);
        background-size: 50px 50px;
        opacity: 0.3;
        animation: moveBackground 20s linear infinite;
    }
    
    @keyframes moveBackground {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    .profile-avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4A4A4A, #2D2D2D);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        border: 4px solid white;
        margin-bottom: 20px;
    }
    
    .profile-card {
        background-color: #3A3A3A;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #FF6B35;
        transition: transform 0.3s ease;
    }
    
    .profile-card:hover {
        transform: translateY(-5px);
    }
    
    .profile-section {
        margin-bottom: 30px;
    }
    
    .section-title {
        color: #FF6B35;
        font-size: 1.3rem;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #4A4A4A;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #4A4A4A;
    }
    
    .info-label {
        color: #AAAAAA;
        font-weight: 500;
    }
    
    .info-value {
        color: white;
        font-weight: bold;
    }
    
    .edit-button {
        background-color: #4A4A4A !important;
        color: white !important;
        border: 1px solid #5A5A5A !important;
        border-radius: 5px !important;
        padding: 5px 15px !important;
        font-size: 0.9rem !important;
    }
    
    .save-button {
        background: linear-gradient(135deg, #FF6B35, #FF8B35) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 5px 15px !important;
        font-size: 0.9rem !important;
    }
    
    .tab-content {
        padding: 20px 0;
    }
    
    .health-metric {
        text-align: center;
        padding: 15px;
        background-color: #4A4A4A;
        border-radius: 10px;
        margin: 5px;
    }
    
    .metric-value {
        color: #FF6B35;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #AAAAAA;
        font-size: 0.9rem;
    }
    
    .activity-item {
        padding: 10px;
        border-bottom: 1px solid #4A4A4A;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #4A4A4A;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FF6B35;
        font-size: 1.2rem;
    }
    
    .activity-details {
        flex: 1;
    }
    
    .activity-title {
        color: white;
        font-weight: 500;
        margin-bottom: 5px;
    }
    
    .activity-time {
        color: #AAAAAA;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def show_profile_header():
    """Display profile header with user info"""
    user = st.session_state.user
    
    # Get user initials for avatar
    initials = user.get('full_name', 'User')[0].upper()
    
    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar">{initials}</div>
        <h1 style="color: white; margin-bottom: 5px;">{user.get('full_name', 'User')}</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px;">
            @{user['username']} • Member since {user.get('created_at', '2024')[:10]}
        </p>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div>
                <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;">Age</div>
                <div style="color: white; font-size: 1.2rem; font-weight: bold;">{user.get('age', 'N/A')}</div>
            </div>
            <div>
                <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;">Gender</div>
                <div style="color: white; font-size: 1.2rem; font-weight: bold;">{user.get('gender', 'N/A')}</div>
            </div>
            <div>
                <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;">Blood Group</div>
                <div style="color: white; font-size: 1.2rem; font-weight: bold;">{user.get('blood_group', 'N/A')}</div>
            </div>
            <div>
                <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;">Status</div>
                <div style="color: #4CAF50; font-size: 1.2rem; font-weight: bold;">Active</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_personal_info():
    """Display and edit personal information"""
    user = st.session_state.user
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='section-title'>📋 Personal Information</div>", unsafe_allow_html=True)
        
        with st.form("personal_info_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                full_name = st.text_input(
                    "Full Name",
                    value=user.get('full_name', ''),
                    placeholder="Enter your full name"
                )
                
                email = st.text_input(
                    "Email Address",
                    value=user.get('email', ''),
                    placeholder="your.email@example.com",
                    disabled=True  # Email usually can't be changed
                )
                
                age = st.number_input(
                    "Age",
                    value=user.get('age', 25),
                    min_value=1,
                    max_value=120
                )
            
            with col_b:
                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other", "Prefer not to say"],
                    index=["Male", "Female", "Other", "Prefer not to say"].index(
                        user.get('gender', 'Male')
                    ) if user.get('gender') in ["Male", "Female", "Other", "Prefer not to say"] else 0
                )
                
                blood_group = st.selectbox(
                    "Blood Group",
                    ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
                    index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(
                        user.get('blood_group', 'Unknown')
                    ) if user.get('blood_group') in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"] else 8
                )
            
            # Submit button
            if st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary"):
                with st.spinner("Updating profile..."):
                    profile_data = {
                        'full_name': full_name,
                        'age': age,
                        'gender': gender,
                        'blood_group': blood_group
                    }
                    
                    success, message = auth_system.update_user_profile(user['id'], profile_data)
                    
                    if success:
                        # Update session state
                        st.session_state.user.update(profile_data)
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Update failed: {message}")

def show_medical_info():
    """Display medical information"""
    user = st.session_state.user
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='section-title'>🏥 Medical History</div>", unsafe_allow_html=True)
        
        # Allergies
        st.markdown("**Allergies**")
        allergies = user.get('allergies', [])
        if allergies:
            for allergy in allergies:
                st.markdown(f"• {allergy}")
        else:
            st.info("No allergies recorded")
        
        # Medical conditions
        st.markdown("**Medical Conditions**")
        conditions = user.get('medical_history', [])
        if conditions:
            for condition in conditions:
                st.markdown(f"• {condition}")
        else:
            st.info("No medical conditions recorded")
    
    with col2:
        st.markdown("<div class='section-title'>📊 Health Metrics</div>", unsafe_allow_html=True)
        
        # Get latest medical data
        medical_history = auth_system.get_user_medical_history(user['id'], limit=1)
        
        if not medical_history.empty:
            latest_data = medical_history.iloc[0]
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if pd.notna(latest_data.get('height_cm')):
                    st.metric("Height", f"{latest_data['height_cm']} cm")
                
                if pd.notna(latest_data.get('weight_kg')):
                    st.metric("Weight", f"{latest_data['weight_kg']} kg")
            
            with col_b:
                if pd.notna(latest_data.get('bmi')):
                    st.metric("BMI", f"{latest_data['bmi']:.1f}")
                
                if pd.notna(latest_data.get('glucose_level')):
                    st.metric("Glucose", f"{latest_data['glucose_level']} mg/dL")
        else:
            st.info("No health metrics recorded yet")
            
            # Add medical data form
            with st.expander("➕ Add Health Metrics"):
                with st.form("add_medical_data_form"):
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
                        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=70.0)
                        blood_pressure = st.text_input("Blood Pressure", placeholder="120/80")
                    
                    with col_y:
                        glucose = st.number_input("Glucose Level (mg/dL)", min_value=50.0, max_value=500.0, value=100.0)
                        cholesterol = st.selectbox("Cholesterol", ["Normal", "High", "Low"])
                        symptoms = st.multiselect(
                            "Current Symptoms",
                            ["Fever", "Cough", "Headache", "Fatigue", "Nausea", "Dizziness", "Other"]
                        )
                    
                    if st.form_submit_button("💾 Save Metrics", use_container_width=True):
                        bmi = weight / ((height/100) ** 2)
                        
                        medical_data = {
                            'height_cm': height,
                            'weight_kg': weight,
                            'blood_pressure': blood_pressure,
                            'glucose_level': glucose,
                            'cholesterol': cholesterol,
                            'bmi': bmi,
                            'symptoms': symptoms
                        }
                        
                        success, message = auth_system.add_medical_data(user['id'], medical_data)
                        
                        if success:
                            st.success("Medical data added successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to add medical data: {message}")

def show_activity_log():
    """Display user activity log"""
    user = st.session_state.user
    
    st.markdown("<div class='section-title'>📈 Recent Activity</div>", unsafe_allow_html=True)
    
    # Get recent activity
    activity_df = auth_system.get_recent_activity(user['id'], limit=20)
    
    if not activity_df.empty:
        # Convert timestamp to readable format
        activity_df['timestamp'] = pd.to_datetime(activity_df['timestamp'])
        activity_df['time_ago'] = activity_df['timestamp'].apply(
            lambda x: get_time_ago(x)
        )
        
        # Display activities
        for _, row in activity_df.iterrows():
            icon = get_activity_icon(row['activity_type'])
            title = get_activity_title(row['activity_type'])
            
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-icon">{icon}</div>
                <div class="activity-details">
                    <div class="activity-title">{title}</div>
                    <div class="activity-time">{row['time_ago']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity to display")

def get_time_ago(timestamp):
    """Convert timestamp to human-readable time ago"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def get_activity_icon(activity_type):
    """Get icon for activity type"""
    icons = {
        'LOGIN': '🔓',
        'LOGOUT': '🚪',
        'REGISTRATION': '👤',
        'PROFILE_UPDATE': '✏️',
        'PASSWORD_CHANGE': '🔑',
        'MEDICAL_DATA_UPDATE': '🏥',
        'PREDICTION': '🔮',
        'RECOMMENDATION': '💊',
        'DISEASE_PREDICTION': '🤒'
    }
    return icons.get(activity_type, '📝')

def get_activity_title(activity_type):
    """Get title for activity type"""
    titles = {
        'LOGIN': 'Logged into account',
        'LOGOUT': 'Logged out',
        'REGISTRATION': 'Account created',
        'PROFILE_UPDATE': 'Profile updated',
        'PASSWORD_CHANGE': 'Password changed',
        'MEDICAL_DATA_UPDATE': 'Medical data updated',
        'PREDICTION': 'Made a prediction',
        'RECOMMENDATION': 'Received recommendations',
        'DISEASE_PREDICTION': 'Predicted disease'
    }
    return titles.get(activity_type, 'Activity recorded')

def show_settings():
    """Display user settings"""
    st.markdown("<div class='section-title'>⚙️ Settings</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Preferences", "Security", "Notifications"])
    
    with tab1:
        st.markdown("**Appearance**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Theme",
                ["Dark", "Light", "Auto"],
                help="Choose your preferred theme"
            )
            
            language = st.selectbox(
                "Language",
                ["English", "Spanish", "French", "German", "Chinese", "Hindi", "Arabic"]
            )
        
        with col2:
            dashboard_layout = st.selectbox(
                "Dashboard Layout",
                ["Default", "Compact", "Detailed"],
                help="Choose how your dashboard is organized"
            )
            
            font_size = st.select_slider(
                "Font Size",
                options=["Small", "Medium", "Large"],
                value="Medium"
            )
        
        if st.button("💾 Save Preferences", use_container_width=True):
            st.success("Preferences saved!")
    
    with tab2:
        st.markdown("**Change Password**")
        
        with st.form("change_password_form"):
            current_password = st.text_input(
                "Current Password",
                type="password",
                placeholder="Enter current password"
            )
            
            new_password = st.text_input(
                "New Password",
                type="password",
                placeholder="Enter new password"
            )
            
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                placeholder="Confirm new password"
            )
            
            if st.form_submit_button("🔐 Change Password", use_container_width=True, type="primary"):
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                else:
                    success, message = auth_system.change_password(
                        st.session_state.user['id'],
                        current_password,
                        new_password
                    )
                    
                    if success:
                        st.success("Password changed successfully!")
                    else:
                        st.error(f"Password change failed: {message}")
    
    with tab3:
        st.markdown("**Notification Settings**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_notifications = st.checkbox("Email Notifications", value=True)
            push_notifications = st.checkbox("Push Notifications", value=True)
            medication_reminders = st.checkbox("Medication Reminders", value=False)
        
        with col2:
            health_tips = st.checkbox("Health Tips", value=True)
            appointment_reminders = st.checkbox("Appointment Reminders", value=True)
            emergency_alerts = st.checkbox("Emergency Alerts", value=True)
        
        if st.button("💾 Save Notification Settings", use_container_width=True):
            st.success("Notification settings saved!")

def main():
    """Main profile page"""
    st.markdown("<h1 style='color: #FF6B35;'>👤 User Profile</h1>", unsafe_allow_html=True)
    
    # Show profile header
    show_profile_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Personal Info", 
        "🏥 Medical Info", 
        "📈 Activity Log", 
        "⚙️ Settings"
    ])
    
    with tab1:
        show_personal_info()
    
    with tab2:
        show_medical_info()
    
    with tab3:
        show_activity_log()
    
    with tab4:
        show_settings()
    
    # Quick actions
    st.markdown("---")
    st.markdown("<h3 style='color: #FF6B35;'>🚀 Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Export Data", use_container_width=True):
            st.info("Data export feature coming soon!")
    
    with col2:
        if st.button("👥 Invite Friends", use_container_width=True):
            st.info("Invite feature coming soon!")
    
    with col3:
        if st.button("🆘 Emergency Info", use_container_width=True):
            st.info("Emergency info feature coming soon!")
    
    with col4:
        if st.button("🗑️ Delete Account", use_container_width=True, type="secondary"):
            st.warning("Account deletion is permanent! Are you sure?")
            confirm = st.checkbox("I understand this cannot be undone")
            if confirm and st.button("⚠️ Confirm Delete", type="primary"):
                st.error("Account deletion feature coming soon!")

if __name__ == "__main__":
    main()