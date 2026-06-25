import streamlit as st
import database as db
import json
import os
import uuid
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def check_auth():
    """Checks session state to verify login status."""
    return st.session_state.get("authenticated", False)

def login_user(username_or_email, password):
    """Authenticates user and updates session state."""
    user = db.authenticate_user(username_or_email, password)
    if user:
        st.session_state["authenticated"] = True
        st.session_state["user_info"] = user
        return True, "Login successful!"
    return False, "Invalid username/email or password."

def logout_user():
    """Logs the user out by clearing session state."""
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = None
    st.session_state["current_page"] = "login"
    # Forces re-run
    st.rerun()

def register_user(username, email, password, confirm_password):
    """Validates inputs and creates a new user in the database."""
    if not username or not email or not password or not confirm_password:
        return False, "All fields are required."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    if password != confirm_password:
        return False, "Passwords do not match."
        
    success, message = db.create_user(username, email, password)
    return success, message

def render_auth_ui():
    """Renders a beautiful centered login/signup interface."""
    # Ensure database is initialized
    db.init_db()
    
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='auth-title'>FOUNDR<span>AI</span></h1>", unsafe_allow_html=True)
        st.markdown("<p class='auth-subtitle'>Your Virtual Startup Co-Founder & Advisor</p>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab_login:
            st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
            with st.form("login_form"):
                username_input = st.text_input("Username or Email", placeholder="Enter your username or email")
                password_input = st.text_input("Password", type="password", placeholder="Enter your password")
                
                submit_login = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit_login:
                    success, msg = login_user(username_input, password_input)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_signup:
            st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
            with st.form("signup_form"):
                reg_username = st.text_input("Username", placeholder="e.g. janesmith")
                reg_email = st.text_input("Email Address", placeholder="e.g. jane@example.com")
                reg_password = st.text_input("Password (min 6 chars)", type="password", placeholder="Choose a password")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
                submit_signup = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_signup:
                    success, msg = register_user(reg_username, reg_email, reg_password, reg_confirm)
                    if success:
                        st.success("Account created successfully! Please switch to the Sign In tab.")
                    else:
                        st.error(msg)
            st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)
