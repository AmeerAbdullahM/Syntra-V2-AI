import streamlit as st
from backend.database.connection import SessionLocal
from backend.services.auth.auth_service import AuthService, AuthServiceError
from backend.schemas.auth import UserLogin, UserCreate
from frontend.session import init_session, get_current_user, login_user, logout_user
from frontend.styles import SYNTRA_CSS
from frontend.universe import inject_universe
import base64
import os

def get_base64_logo():
    logo_path = os.path.join("frontend", "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return ""

def auth_page():
    b64_logo = get_base64_logo()
    img_html = f'<img src="data:image/png;base64,{b64_logo}" width="100" style="margin-bottom: 1rem;"/>' if b64_logo else ''
    
    st.markdown(f"""
        <div style="text-align: center; margin-top: 5vh; margin-bottom: 2rem;">
            {img_html}
            <h1 style="font-size: 3.5rem !important; margin-bottom: 0.5rem; margin-top: 0;">Syntra <span style="color: #6366f1;">V2</span></h1>
            <p style="font-size: 1.1rem; color: #94a3b8; max-width: 500px; margin: 0 auto;">
                Multimodal lecture reconstruction & collaborative learning workspace
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with SessionLocal() as db:
            auth_service = AuthService(db)
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    submit = st.form_submit_button("Sign In")
                    
                    if submit:
                        if not email or not password:
                            st.error("Please enter both email and password.")
                        else:
                            with st.spinner("Authenticating..."):
                                try:
                                    user = auth_service.login(UserLogin(email=email, password=password))
                                    login_user(user)
                                    st.success(f"Welcome back, {user.display_name}!")
                                    st.rerun()
                                except AuthServiceError:
                                    st.error("Invalid email or password. Please try again.")
                            
            with tab2:
                with st.form("register_form"):
                    reg_name = st.text_input("Display Name", placeholder="e.g. Alex Chen")
                    reg_email = st.text_input("Email", placeholder="you@example.com")
                    reg_password = st.text_input("Password", type="password", placeholder="At least 8 characters")
                    reg_submit = st.form_submit_button("Create Account")
                    
                    if reg_submit:
                        errors = []
                        if not reg_name: errors.append("Display Name is required.")
                        if not reg_email: errors.append("Email is required.")
                        if not reg_password or len(reg_password) < 8: errors.append("Password must be at least 8 characters.")
                        
                        if errors:
                            for e in errors: st.error(e)
                        else:
                            with st.spinner("Setting up your workspace..."):
                                try:
                                    user = auth_service.register(UserCreate(
                                        email=reg_email, 
                                        display_name=reg_name, 
                                        password=reg_password
                                    ))
                                    login_user(user)
                                    st.success("Account created successfully!")
                                    st.rerun()
                                except AuthServiceError as e:
                                    st.error(str(e))

def main():
    st.set_page_config(page_title="Syntra V2", page_icon="frontend/assets/logo.png", layout="wide", initial_sidebar_state="expanded")
    st.markdown(SYNTRA_CSS, unsafe_allow_html=True)
    inject_universe()
    init_session()
    
    user = get_current_user()
    
    if user is None:
        auth_page()
    else:
        # Define pages for logged-in users
        pages = {
            "Workspace": [
                st.Page("pages/dashboard.py", title="Dashboard"),
                st.Page("pages/dens.py", title="My Dens"),
            ],
            "Hidden": [
                st.Page("pages/den_view.py", title="Den View"),
                st.Page("pages/view_material.py", title="View Material")
            ]
        }
        
        from backend.config.settings import settings
        if user.email == settings.SUPERADMIN_EMAIL:
            pages["Administration"] = [
                st.Page("pages/superadmin.py", title="Admin Panel")
            ]
        
        pg = st.navigation(pages)
        
        with st.sidebar:
            b64_logo = get_base64_logo()
            if b64_logo:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; margin-top: 0.5rem;">
                        <img src="data:image/png;base64,{b64_logo}" width="40" />
                        <h2 style="margin: 0; font-size: 1.4rem;">Syntra <span style="color: #6366f1;">V2</span></h2>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
                
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; margin-bottom: 0.25rem;">Logged in as</div>
                    <div style="font-weight: 600; font-size: 1rem; color: #f8fafc;">{user.display_name}</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.25rem;">{user.email}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Sign Out", use_container_width=True):
                logout_user()
                
        pg.run()

if __name__ == "__main__":
    main()
