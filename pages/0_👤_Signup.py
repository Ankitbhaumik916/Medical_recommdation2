import streamlit as st
import time
import json
import re
import sqlite3
from datetime import datetime, date
from auth import auth_system, init_session_state
from typing import Tuple

# Page configuration
st.set_page_config(
    page_title="Sign Up - Health AI",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for signup page (keeping it simple)
st.markdown("""
<style>
    .signup-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        background-color: #2D2D2D;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid #3A3A3A;
    }
    
    .signup-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .signup-title {
        color: #FF6B35;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .signup-subtitle {
        color: #AAAAAA;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    .form-section {
        background-color: #3A3A3A;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #4A4A4A;
    }
    
    .section-title {
        color: #FF6B35;
        font-size: 1.2rem;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #4A4A4A;
    }
    
    .password-strength {
        margin-top: 5px;
        font-size: 0.85rem;
    }
    
    .strength-weak {
        color: #FF4444;
    }
    
    .strength-medium {
        color: #FFA500;
    }
    
    .strength-strong {
        color: #4CAF50;
    }
    
    .progress-bar {
        height: 5px;
        background-color: #4A4A4A;
        border-radius: 3px;
        margin-top: 5px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .checkbox-group {
        background-color: #4A4A4A;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .terms-box {
        max-height: 200px;
        overflow-y: auto;
        background-color: #4A4A4A;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid #5A5A5A;
    }
    
    .terms-content {
        color: #CCCCCC;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .form-buttons {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }
    
    .back-button {
        background-color: #4A4A4A !important;
        color: white !important;
        border: 1px solid #5A5A5A !important;
    }
    
    .next-button {
        background: linear-gradient(135deg, #FF6B35, #FF8B35) !important;
        color: white !important;
        border: none !important;
    }
    
    .success-message {
        text-align: center;
        padding: 40px 20px;
    }
    
    .success-icon {
        font-size: 4rem;
        color: #4CAF50;
        margin-bottom: 20px;
    }
    
    .success-title {
        color: #4CAF50;
        font-size: 1.8rem;
        margin-bottom: 10px;
    }
    
    .success-subtitle {
        color: #AAAAAA;
        margin-bottom: 30px;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 30px;
        position: relative;
    }
    
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #4A4A4A;
        z-index: 1;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
    }
    
    .step-circle {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 5px;
        border: 2px solid;
    }
    
    .step-active {
        background-color: #FF6B35;
        color: white;
        border-color: #FF6B35;
    }
    
    .step-completed {
        background-color: #4CAF50;
        color: white;
        border-color: #4CAF50;
    }
    
    .step-pending {
        background-color: #4A4A4A;
        color: #AAAAAA;
        border-color: #5A5A5A;
    }
    
    .step-label {
        font-size: 0.8rem;
        color: #AAAAAA;
        text-align: center;
    }
    
    .step-label-active {
        color: #FF6B35;
        font-weight: bold;
    }
    
    /* BMI Calculator Styles */
    .bmi-card {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .bmi-scale {
        height: 10px;
        background: linear-gradient(90deg, #3498db 0%, #2ecc71 30%, #f39c12 60%, #e74c3c 100%);
        border-radius: 5px;
        margin: 10px 0;
        position: relative;
    }
    
    .bmi-marker {
        position: absolute;
        top: -5px;
        width: 2px;
        height: 20px;
        background-color: white;
    }
    
    .bmi-category {
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    
    .underweight {
        color: #3498db;
    }
    
    .normal {
        color: #2ecc71;
    }
    
    .overweight {
        color: #f39c12;
    }
    
    .obese {
        color: #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

def check_password_strength(password: str) -> Tuple[str, float, str, list]:
    """Check password strength and return level, score, and feedback"""
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("One uppercase letter")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("One lowercase letter")
    
    # Number check
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("One number")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("One special character")
    
    # Determine level
    if score <= 2:
        level = "Weak"
        color_class = "strength-weak"
        percentage = score / 5 * 100
    elif score <= 3:
        level = "Medium"
        color_class = "strength-medium"
        percentage = score / 5 * 100
    else:
        level = "Strong"
        color_class = "strength-strong"
        percentage = score / 5 * 100
    
    return level, percentage, color_class, feedback

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI and return value and category"""
    if height_cm <= 0 or weight_kg <= 0:
        return None, None, None
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
        color = "#3498db"
    elif 18.5 <= bmi < 25:
        category = "Normal"
        color = "#2ecc71"
    elif 25 <= bmi < 30:
        category = "Overweight"
        color = "#f39c12"
    else:
        category = "Obese"
        color = "#e74c3c"
    
    return bmi, category, color

def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    if not date_of_birth:
        return 25
    
    today = date.today()
    age = today.year - date_of_birth.year
    
    # Check if birthday hasn't occurred this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    
    return age

def show_step_indicator(current_step: int):
    """Display step indicator"""
    steps = [
        {"number": 1, "label": "Account"},
        {"number": 2, "label": "Personal & Health"},
        {"number": 3, "label": "Medical History"},
        {"number": 4, "label": "Terms"}
    ]
    
    st.markdown('<div class="step-indicator">', unsafe_allow_html=True)
    
    for step in steps:
        step_class = ""
        label_class = ""
        
        if step["number"] < current_step:
            step_class = "step-completed"
        elif step["number"] == current_step:
            step_class = "step-active"
            label_class = "step-label-active"
        else:
            step_class = "step-pending"
        
        st.markdown(f'''
        <div class="step">
            <div class="step-circle {step_class}">{step["number"]}</div>
            <div class="step-label {label_class}">{step["label"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_account_step():
    """Display account information step"""
    st.markdown("<div class='section-title'>📝 Account Information</div>", unsafe_allow_html=True)
    
    # Initialize form data in session state
    if 'signup_data' not in st.session_state:
        st.session_state.signup_data = {}
    
    with st.form("account_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Username *",
                placeholder="Choose a username",
                help="3-20 characters, letters and numbers only",
                key="signup_username",
                value=st.session_state.signup_data.get('username', '')
            )
        
        with col2:
            email = st.text_input(
                "Email Address *",
                placeholder="your.email@example.com",
                help="We'll send verification to this email",
                key="signup_email",
                value=st.session_state.signup_data.get('email', '')
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Create strong password",
                key="signup_password",
                value=st.session_state.signup_data.get('password', '')
            )
        
        with col4:
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter password",
                key="signup_confirm_password",
                value=st.session_state.signup_data.get('confirm_password', '')
            )
        
        # Password strength indicator
        if password:
            level, percentage, color_class, feedback = check_password_strength(password)
            
            st.markdown(f"""
            <div class="password-strength">
                <div style="display: flex; justify-content: space-between;">
                    <span>Password Strength: <strong class="{color_class}">{level}</strong></span>
                    <span>{int(percentage)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {percentage}%; background-color: {'#FF4444' if level == 'Weak' else ('#FFA500' if level == 'Medium' else '#4CAF50')};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if feedback:
                st.info("Requirements: " + ", ".join(feedback))
        
        # Form buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.form_submit_button("⬅️ Back to Login", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()
        
        with col_btn2:
            submit = st.form_submit_button("Next → Personal Details", 
                                         use_container_width=True, 
                                         type="primary")
        
        if submit:
            # Validation
            errors = []
            
            if not username:
                errors.append("Username is required")
            elif len(username) < 3:
                errors.append("Username must be at least 3 characters")
            elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors.append("Username can only contain letters, numbers, and underscores")
            
            if not email:
                errors.append("Email is required")
            elif not auth_system.validate_email(email):
                errors.append("Invalid email format")
            
            if not password:
                errors.append("Password is required")
            else:
                is_valid, msg = auth_system.validate_password_strength(password)
                if not is_valid:
                    errors.append(msg)
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Save data and proceed to next step
                st.session_state.signup_data.update({
                    'username': username,
                    'email': email,
                    'password': password,
                    'confirm_password': confirm_password
                })
                st.session_state.signup_step = 2
                st.rerun()

def show_personal_step():
    """Display personal details step with enhanced health metrics"""
    st.markdown("<div class='section-title'>👤 Personal Information</div>", unsafe_allow_html=True)
    
    with st.form("personal_form"):
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name *",
                placeholder="John Doe",
                help="Your full name as it should appear",
                value=st.session_state.signup_data.get('full_name', '')
            )
        
        with col2:
            # Simple age input instead of date of birth to keep it simple
            age = st.number_input(
                "Age *",
                min_value=1,
                max_value=120,
                value=st.session_state.signup_data.get('age', 25),
                help="Your age in years"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            gender = st.selectbox(
                "Gender *",
                ["Select", "Male", "Female", "Other", "Prefer not to say"],
                index=["Select", "Male", "Female", "Other", "Prefer not to say"].index(
                    st.session_state.signup_data.get('gender', 'Select')
                )
            )
        
        with col4:
            blood_group = st.selectbox(
                "Blood Group",
                ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Don't know"],
                index=["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Don't know"].index(
                    st.session_state.signup_data.get('blood_group', 'Select')
                )
            )
        
        # Contact Information
        col5, col6 = st.columns(2)
        
        with col5:
            phone = st.text_input(
                "Phone Number",
                placeholder="+1 234 567 8900",
                help="For emergency contact and notifications",
                value=st.session_state.signup_data.get('phone', '')
            )
        
        with col6:
            address = st.text_input(
                "Address",
                placeholder="City, State",
                help="Your general location",
                value=st.session_state.signup_data.get('address', '')
            )
        
        # Health Metrics Section
        st.markdown("<div style='margin-top: 20px; margin-bottom: 10px; color: #FF6B35; font-weight: bold;'>⚖️ Health Metrics</div>", unsafe_allow_html=True)
        
        col7, col8 = st.columns(2)
        
        with col7:
            height_cm = st.number_input(
                "Height (cm) *",
                min_value=50.0,
                max_value=250.0,
                value=st.session_state.signup_data.get('height_cm', 170.0),
                step=0.1,
                help="Enter your height in centimeters"
            )
        
        with col8:
            weight_kg = st.number_input(
                "Weight (kg) *",
                min_value=20.0,
                max_value=300.0,
                value=st.session_state.signup_data.get('weight_kg', 70.0),
                step=0.1,
                help="Enter your weight in kilograms"
            )
        
        # BMI Calculation and Display
        if height_cm > 0 and weight_kg > 0:
            bmi, bmi_category, bmi_color = calculate_bmi(weight_kg, height_cm)
            
            if bmi:
                # Calculate marker position (0-100%)
                marker_position = min(100, (bmi / 50) * 100)
                
                st.markdown(f"""
                <div class="bmi-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #AAAAAA; font-size: 0.9rem;">Body Mass Index</div>
                            <div style="font-size: 2rem; color: {bmi_color}; font-weight: bold;">{bmi:.1f}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; color: {bmi_color}; font-weight: bold;">{bmi_category}</div>
                            <div style="color: #AAAAAA; font-size: 0.8rem;">Healthy: 18.5-25</div>
                        </div>
                    </div>
                    <div class="bmi-scale">
                        <div class="bmi-marker" style="left: {marker_position}%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #AAAAAA;">
                        <div>Underweight<br>&lt;18.5</div>
                        <div>Normal<br>18.5-25</div>
                        <div>Overweight<br>25-30</div>
                        <div>Obese<br>&gt;30</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Simple recommendation
                if bmi_category == "Underweight":
                    recommendation = "Consider consulting a nutritionist."
                elif bmi_category == "Normal":
                    recommendation = "Great! Maintain your healthy lifestyle."
                elif bmi_category == "Overweight":
                    recommendation = "Consider regular exercise and balanced diet."
                else:
                    recommendation = "Consult a healthcare provider for guidance."
                
                st.info(f"💡 **Recommendation:** {recommendation}")
        
        # Lifestyle Information
        st.markdown("<div style='margin-top: 20px; margin-bottom: 10px; color: #FF6B35; font-weight: bold;'>🏥 Lifestyle</div>", unsafe_allow_html=True)
        
        col9, col10 = st.columns(2)
        
        with col9:
            smoking = st.selectbox(
                "Smoking Status",
                ["Never", "Former", "Current", "Occasional"],
                index=["Never", "Former", "Current", "Occasional"].index(
                    st.session_state.signup_data.get('smoking', 'Never')
                )
            )
            
            exercise = st.selectbox(
                "Exercise Frequency",
                ["Daily", "3-5 times/week", "1-2 times/week", "Rarely", "Never"],
                index=["Daily", "3-5 times/week", "1-2 times/week", "Rarely", "Never"].index(
                    st.session_state.signup_data.get('exercise', '3-5 times/week')
                )
            )
        
        with col10:
            alcohol = st.selectbox(
                "Alcohol Consumption",
                ["Never", "Occasional", "Moderate", "Heavy"],
                index=["Never", "Occasional", "Moderate", "Heavy"].index(
                    st.session_state.signup_data.get('alcohol', 'Never')
                )
            )
            
            diet = st.selectbox(
                "Diet Type",
                ["Balanced", "Vegetarian", "Vegan", "Keto", "Low-carb", "Other"],
                index=["Balanced", "Vegetarian", "Vegan", "Keto", "Low-carb", "Other"].index(
                    st.session_state.signup_data.get('diet', 'Balanced')
                )
            )
        
        # Form buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.signup_step = 1
                st.rerun()
        
        with col_btn2:
            submit = st.form_submit_button("Next → Medical History", 
                                         use_container_width=True, 
                                         type="primary")
        
        if submit:
            # Validation
            errors = []
            
            if not full_name:
                errors.append("Full name is required")
            
            if not age or age < 1:
                errors.append("Valid age is required")
            
            if gender == "Select":
                errors.append("Gender is required")
            
            if height_cm <= 0:
                errors.append("Valid height is required")
            
            if weight_kg <= 0:
                errors.append("Valid weight is required")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Calculate BMI
                bmi, bmi_category, bmi_color = calculate_bmi(weight_kg, height_cm)
                
                # Save data and proceed
                st.session_state.signup_data.update({
                    'full_name': full_name,
                    'age': age,
                    'gender': gender if gender != "Select" else "",
                    'blood_group': blood_group if blood_group != "Select" else "",
                    'phone': phone,
                    'address': address,
                    'height_cm': height_cm,
                    'weight_kg': weight_kg,
                    'bmi': bmi,
                    'bmi_category': bmi_category,
                    'smoking': smoking,
                    'alcohol': alcohol,
                    'exercise': exercise,
                    'diet': diet
                })
                st.session_state.signup_step = 3
                st.rerun()

def show_medical_step():
    """Display medical history step - SIMPLIFIED"""
    st.markdown("<div class='section-title'>🏥 Medical History</div>", unsafe_allow_html=True)
    
    st.info("This information helps us provide safe and personalized recommendations.")
    
    with st.form("medical_form"):
        # Allergies - Most important for medication safety
        allergies = st.multiselect(
            "Known Allergies *",
            [
                "Penicillin", "Sulfa Drugs", "NSAIDs", "Aspirin",
                "Codeine", "Iodine", "Latex", "Food Allergies",
                "Seasonal Allergies", "Dust", "Mold", "None"
            ],
            help="Select all that apply - CRITICAL for medication safety",
            default=st.session_state.signup_data.get('allergies', [])
        )
        
        # Medical conditions
        medical_conditions = st.multiselect(
            "Existing Medical Conditions",
            [
                "Diabetes", "Hypertension", "Asthma", "Heart Disease",
                "Arthritis", "Thyroid Disorders", "Kidney Disease",
                "Liver Disease", "Cancer", "Mental Health Conditions",
                "None"
            ],
            help="Select all that apply",
            default=st.session_state.signup_data.get('medical_conditions', [])
        )
        
        # Current medications
        current_medications = st.text_area(
            "Current Medications (Optional)",
            placeholder="List any medications you're currently taking",
            help="Include dosage if known",
            height=60,
            value=st.session_state.signup_data.get('current_medications', '')
        )
        
        # Emergency Contact
        st.markdown("<div style='margin-top: 20px; color: #FF6B35;'>🆘 Emergency Contact</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            emergency_name = st.text_input(
                "Emergency Contact Name",
                placeholder="Name of emergency contact",
                value=st.session_state.signup_data.get('emergency_name', '')
            )
        
        with col2:
            emergency_phone = st.text_input(
                "Emergency Contact Phone",
                placeholder="Emergency contact phone number",
                value=st.session_state.signup_data.get('emergency_phone', '')
            )
        
        # Form buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.signup_step = 2
                st.rerun()
        
        with col_btn2:
            submit = st.form_submit_button("Next → Terms", 
                                         use_container_width=True, 
                                         type="primary")
        
        if submit:
            # Validation
            errors = []
            
            if not allergies:
                errors.append("Please select at least 'None' for allergies")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Save data and proceed
                st.session_state.signup_data.update({
                    'allergies': allergies,
                    'medical_conditions': medical_conditions,
                    'current_medications': current_medications,
                    'emergency_name': emergency_name,
                    'emergency_phone': emergency_phone
                })
                st.session_state.signup_step = 4
                st.rerun()

def show_terms_step():
    """Display terms and conditions step - SIMPLIFIED"""
    st.markdown("<div class='section-title'>📋 Terms & Preferences</div>", unsafe_allow_html=True)
    
    with st.form("terms_form"):
        # Simple preferences
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Theme",
                ["Dark", "Light", "Auto"],
                help="Choose your preferred color theme",
                index=["Dark", "Light", "Auto"].index(
                    st.session_state.signup_data.get('theme', 'Dark')
                )
            )
        
        with col2:
            language = st.selectbox(
                "Language",
                ["English", "Spanish", "French"],
                index=["English", "Spanish", "French"].index(
                    st.session_state.signup_data.get('language', 'English')
                )
            )
        
        # Simple terms
        st.markdown("""
        <div style="background-color: #3A3A3A; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h4 style="color: #FF6B35;">Terms of Service</h4>
            <p style="color: #CCCCCC; font-size: 0.9rem;">
            By creating an account, you agree that:
            </p>
            <ul style="color: #CCCCCC; font-size: 0.9rem;">
                <li>Health AI provides informational recommendations only</li>
                <li>Always consult healthcare professionals for medical advice</li>
                <li>Your data is encrypted and protected</li>
                <li>You provide accurate health information</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        agree_terms = st.checkbox(
            "I agree to the Terms of Service *",
            value=st.session_state.signup_data.get('agree_terms', False)
        )
        
        newsletter = st.checkbox(
            "Subscribe to health tips and updates",
            value=st.session_state.signup_data.get('newsletter', True)
        )
        
        # Form buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.signup_step = 3
                st.rerun()
        
        with col_btn2:
            submit = st.form_submit_button("✅ Create Account", 
                                         use_container_width=True, 
                                         type="primary")
        
        if submit:
            if not agree_terms:
                st.error("You must agree to the Terms of Service")
            else:
                # Save preferences
                st.session_state.signup_data.update({
                    'theme': theme,
                    'language': language,
                    'newsletter': newsletter,
                    'agree_terms': agree_terms
                })
                
                # Complete registration
                complete_registration()

def complete_registration():
    """Complete the registration process - SIMPLIFIED"""
    with st.spinner("Creating your account..."):
        # Get form data
        form_data = st.session_state.signup_data
        
        # Prepare user data for registration
        user_data = {
            'username': form_data['username'],
            'email': form_data['email'],
            'password': form_data['password'],
            'full_name': form_data['full_name'],
            'age': form_data['age'],
            'gender': form_data['gender'],
            'blood_group': form_data['blood_group'],
            'phone': form_data.get('phone', ''),
            'address': form_data.get('address', ''),
            'height_cm': form_data.get('height_cm'),
            'weight_kg': form_data.get('weight_kg'),
            'bmi': form_data.get('bmi'),
            'bmi_category': form_data.get('bmi_category'),
            'allergies': form_data.get('allergies', []),
            'medical_history': form_data.get('medical_conditions', []),
            'current_medications': form_data.get('current_medications', ''),
            'smoking': form_data.get('smoking'),
            'alcohol': form_data.get('alcohol'),
            'exercise': form_data.get('exercise'),
            'diet': form_data.get('diet'),
            'emergency_name': form_data.get('emergency_name', ''),
            'emergency_phone': form_data.get('emergency_phone', '')
        }
        
        # Register user
        success, message = auth_system.register_user(user_data)
        
        if success:
            # Show success message
            st.session_state.registration_success = message
            st.session_state.signup_complete = True
            
            # Auto-login
            success, message, auth_data = auth_system.authenticate_user(
                user_data['username'], 
                user_data['password']
            )
            
            if success:
                st.session_state.authenticated = True
                st.session_state.token = auth_data['token']
                st.session_state.user = auth_data['user']
                
                # Show success animation
                st.balloons()
                
                # Success message
                bmi_info = ""
                if user_data.get('bmi'):
                    bmi_info = f"<br>BMI: <strong>{user_data['bmi']:.1f}</strong> ({user_data.get('bmi_category', '')})"
                
                st.markdown(f"""
                <div class="success-message">
                    <div class="success-icon">🎉</div>
                    <div class="success-title">Welcome to Health AI!</div>
                    <div class="success-subtitle">
                        Your account has been created successfully.<br>
                        {bmi_info}
                        <br><br>Redirecting to your dashboard...
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Redirect after delay
                time.sleep(3)
                st.switch_page("app.py")
            else:
                st.error(f"Account created but auto-login failed: {message}")
                st.info("Please login manually with your credentials")
                time.sleep(2)
                st.session_state.current_page = 'login'
                st.rerun()
        else:
            st.error(f"Registration failed: {message}")

def show_signup_form():
    """Display multi-step signup form"""
    # Initialize session state for signup
    if 'signup_step' not in st.session_state:
        st.session_state.signup_step = 1
    
    st.markdown("""
    <div class="signup-container">
        <div class="signup-header">
            <div class="signup-title">👤 Create Account</div>
            <div class="signup-subtitle">Join Health AI for personalized healthcare recommendations</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Show step indicator
    show_step_indicator(st.session_state.signup_step)
    
    # Show current step
    if st.session_state.signup_step == 1:
        show_account_step()
    elif st.session_state.signup_step == 2:
        show_personal_step()
    elif st.session_state.signup_step == 3:
        show_medical_step()
    elif st.session_state.signup_step == 4:
        show_terms_step()
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main signup page"""
    # Initialize session state
    init_session_state()
    
    # Check if already authenticated
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        st.switch_page("app.py")
    
    # Show signup form
    show_signup_form()
    
    # Simple footer
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 0.9rem;">
        <p>Already have an account? 
        <a href="/" style="color: #FF6B35; font-weight: bold;">Login here</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()