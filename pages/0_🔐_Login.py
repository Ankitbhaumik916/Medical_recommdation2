import streamlit as st
import time
import requests
from auth import auth_system, init_session_state, check_authentication

# Page configuration
st.set_page_config(
    page_title="Login - Health AI",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

from theme import apply_theme
apply_theme()

# Custom CSS for login page
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 30px;
        background-color: #2D2D2D;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid #3A3A3A;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .login-title {
        color: #FF6B35;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .login-subtitle {
        color: #AAAAAA;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    .login-input {
        background-color: #3A3A3A !important;
        border: 1px solid #4A4A4A !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        margin-bottom: 20px !important;
    }
    
    .login-input:focus {
        border-color: #FF6B35 !important;
        box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2) !important;
    }
    
    .login-button {
        background: linear-gradient(135deg, #FF6B35, #FF8B35) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        width: 100% !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    .login-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4) !important;
    }
    
    .login-footer {
        text-align: center;
        margin-top: 25px;
        color: #888888;
        font-size: 0.9rem;
    }
    
    .login-footer a {
        color: #FF6B35;
        text-decoration: none;
        font-weight: bold;
    }
    
    .login-footer a:hover {
        text-decoration: underline;
    }
    
    .login-error {
        background-color: rgba(255, 68, 68, 0.1);
        border: 1px solid #FF4444;
        color: #FFAAAA;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .login-success {
        background-color: rgba(76, 175, 80, 0.1);
        border: 1px solid #4CAF50;
        color: #A5D6A7;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .login-card {
        background-color: #3A3A3A;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #FF6B35;
    }
    
    .social-login {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 20px 0;
    }
    
    .social-button {
        background-color: #4A4A4A;
        border: 1px solid #5A5A5A;
        border-radius: 8px;
        padding: 12px 20px;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
    }
    
    .social-button:hover {
        background-color: #5A5A5A;
        transform: translateY(-2px);
    }
    
    .forgot-password {
        text-align: right;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    
    .forgot-password a {
        color: #FF8B35;
        text-decoration: none;
        font-size: 0.9rem;
    }
    
    .forgot-password a:hover {
        text-decoration: underline;
    }
    
    .remember-me {
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

def show_login_form():
    """Display login form"""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <div class="login-title">🔐 Health AI</div>
            <div class="login-subtitle">Personalized Healthcare Intelligence</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Error/Success messages
    if 'login_error' in st.session_state and st.session_state.login_error:
        st.markdown(f"""
        <div class="login-error">
            ⚠️ {st.session_state.login_error}
        </div>
        """, unsafe_allow_html=True)
        del st.session_state.login_error
    
    if 'registration_success' in st.session_state and st.session_state.registration_success:
        st.markdown(f"""
        <div class="login-success">
            ✅ {st.session_state.registration_success}
        </div>
        """, unsafe_allow_html=True)
        del st.session_state.registration_success
    
    # Social login buttons (demo)
    st.markdown("""
    <div class="social-login">
        <div class="social-button" onclick="alert('Google login would be implemented in production')">
            <span>G</span> Google
        </div>
        <div class="social-button" onclick="alert('Microsoft login would be implemented in production')">
            <span>M</span> Microsoft
        </div>
    </div>
    
    <div style="text-align: center; margin: 20px 0; color: #666;">
        ─── OR ───
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        username = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username",
            help="Enter your registered username or email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
            help="Enter your account password"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Remember me", value=True)
        
        with col2:
            pass  # Forgot password can be added later
        
        submit_button = st.form_submit_button(
            "🔓 Login",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if not username or not password:
                st.session_state.login_error = "Please fill in all fields"
                st.rerun()
            else:
                with st.spinner("Authenticating..."):
                    success, message, auth_data = auth_system.authenticate_user(username, password)
                    
                    if success:
                        # Store authentication data in session
                        st.session_state.authenticated = True
                        st.session_state.token = auth_data['token']
                        st.session_state.user = auth_data['user']
                        
                        # Show success message
                        st.success(f"Welcome back, {auth_data['user']['username']}!")
                        
                        # Add delay for better UX
                        time.sleep(1)
                        
                        # Redirect to dashboard
                        st.switch_page("app.py")
                    else:
                        st.session_state.login_error = message
                        st.rerun()
    
    # Registration link
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Create Account", use_container_width=True):
            st.switch_page("pages/0_👤_Signup.py")
    
    with col2:
        st.markdown("""
        <div style="text-align: right; margin-top: 10px;">
            <small>By logging in, you agree to our 
            <a href="#" style="color: #FF6B35;">Terms of Service</a> and 
            <a href="#" style="color: #FF6B35;">Privacy Policy</a></small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_forgot_password_form():
    """Display forgot password form"""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <div class="login-title">🔑 Reset Password</div>
            <div class="login-subtitle">Enter your email to receive reset instructions</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("forgot_password_form"):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your registered email",
            key="forgot_email"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button(
                "📧 Send Reset Link",
                use_container_width=True,
                type="primary"
            )
        with col2:
            if st.form_submit_button("⬅️ Back to Login", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()
        
        if submit_button:
            if not email:
                st.error("Please enter your email address")
            else:
                with st.spinner("Sending reset instructions..."):
                    success, message, reset_token = auth_system.reset_password_request(email)
                    
                    if success:
                        st.success(f"Reset instructions sent to {email}")
                        st.info(f"Demo reset token: {reset_token}")
                        
                        # Show reset form
                        show_reset_password_form(reset_token)
                    else:
                        st.error(message)

def show_reset_password_form(token: str = None):
    """Display password reset form"""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <div class="login-title">🔄 Set New Password</div>
            <div class="login-subtitle">Create a new strong password</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("reset_password_form"):
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password",
            key="reset_new_password",
            help="Password must be at least 8 characters with uppercase, lowercase, number, and special character"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm new password",
            key="reset_confirm_password"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button(
                "✅ Reset Password",
                use_container_width=True,
                type="primary"
            )
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()
        
        if submit_button:
            if not new_password or not confirm_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                with st.spinner("Resetting password..."):
                    success, message = auth_system.reset_password(token or 'demo_token', new_password)
                    
                    if success:
                        st.success("Password reset successful!")
                        st.info("You can now login with your new password")
                        time.sleep(2)
                        st.session_state.current_page = 'login'
                        st.rerun()
                    else:
                        st.error(message)

def main():
    """Main login page"""
    # Initialize session state
    init_session_state()
    
    # Check if already authenticated
    if check_authentication():
        st.switch_page("pages/1_🏠_Dashboard.py")
    
    # Get query parameters
    query_params = st.query_params
    page = query_params.get("page", ["login"])[0]
    
    # Set current page based on query params
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # Show appropriate form
    if st.session_state.current_page == 'signup':
        # Redirect to signup page
        st.switch_page("pages/0_👤_Signup.py")
    elif st.session_state.current_page == 'forgot_password':
        show_forgot_password_form()
    else:
        show_login_form()
    
    # Add demo credentials info
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 0.9rem;">
        <details>
            <summary style="cursor: pointer; color: #FF6B35;">👨‍⚕️ Demo Credentials</summary>
            <div style="background-color: #3A3A3A; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <p><strong>Admin Account:</strong><br>
                Username: <code>admin</code><br>
                Password: <code>Admin@123</code></p>
                
                <p><strong>User Account:</strong><br>
                Username: <code>john_doe</code><br>
                Password: <code>User@123</code></p>
                
                <p><small>These are demo accounts for testing purposes.</small></p>
            </div>
        </details>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()